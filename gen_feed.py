#!/usr/bin/env python3
"""Генератор-фидер: сгенерённый ботами драфт → фейк-лог Arena, пик-за-пиком.

Зачем отдельно от draft_sim.py. `draft_sim` переигрывает РЕАЛЬНЫЙ драфт из Player.log —
а по HOB реального драфта в логах не осталось (Player.log/prev без драфтов, `.draft_hist.json`
перезатёрт GEN-прогонами). `draft_gen.py` умеет генерить HOB с ботами, но печатает пак в
stdout и в лог не пишет, то есть блокирующий `draft_live.py … watch` им не покормить.
Этот скрипт закрывает ровно этот стык: тот же движок `draft_gen.simulate`, но результат
кладётся в фейк-лог строками ВЕРБАТИМНОГО формата Arena (скопированы из реального лога
драфта a56fb024) → парсер `draft_live` не отличает их от настоящих.

    python3 gen_feed.py hob init [--seed 7]   — новый драфт, обнулить лог, подать P1P1
    python3 gen_feed.py hob next [N]          — авто-пик (за нас пикает бот) + следующий пак, N раз
    python3 gen_feed.py hob pick "Card Name"  — записать НАШ пик + подать следующий пак
    python3 gen_feed.py hob status            — где мы сейчас
    python3 gen_feed.py hob finish            — досыпать DraftComplete

Ассистент в это время крутит НАСТОЯЩИЙ блокирующий вотчер (init печатает готовую команду):

    MTGA_SETTLE=1 MTGA_LOG=<sim.log> python3 draft_live.py hob watch [fresh]

`next` против `pick`. Для замера ЛАТЕНТНОСТИ хватает `next`: пул всё равно растёт и
баннеры считаются по-настоящему, просто наш пик делает бот, а совет ассистента ни на что
не влияет. `pick "Имя"` нужен, когда проверяется КАЧЕСТВО советов: тогда боты реагируют
на реальные наши решения — цвета пересыхают, сигнал «цвет открыт» значит то же, что живьём.
Режимы смешиваются свободно: авто-пик тоже записывается в состояние поимённо.

Детерминизм. Один seed = одни бустеры и одна политика ботов. Состояние — только список
НАШИХ пиков по именам (`sim/gen_state.json`); драфт при каждом вызове переигрывается с нуля
до нужной координаты, поэтому решения ботов всегда зависят от наших, как и должно быть.
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
SIMDIR = os.path.join(HERE, "sim")
STATE = os.path.join(SIMDIR, "gen_state.json")


def simlog(code):
    return os.path.join(SIMDIR, f"{code}_gen.log")


def draft_id(seed):
    """Фейковый draftId. Только hex — `current_draft_id` ловит [0-9a-f-]{8,}, буква 'g'
    из «gen…» уже не прошла бы, и пикам стало бы не с чем сопоставляться."""
    return f"{seed:08x}-0000-4000-8000-{seed:012x}"


def first_face(name):
    return re.split(r"\s*//\s*", (name or "").strip())[0].strip().lower()


def load_engine(code):
    """draft_gen тянет draft_live; обоим нужен сет в окружении и argv как у живого запуска."""
    os.environ["MTGA_SET"] = code
    os.environ.setdefault("MTGA_OFFLINE", "1")
    sys.argv = ["draft_live.py", code]
    import draft_gen as G
    import draft_live as D
    return G, D


def name2id(D):
    n2i = {}
    for cid, c in D.load_cards().items():
        n2i.setdefault(first_face(c["name"]), cid)
    return n2i


def nxt(p, pick):
    if pick < 14:
        return (p, pick + 1)
    if p < 3:
        return (p + 1, 1)
    return None


# ── строки лога: формат скопирован вербатим из настоящего Player.log ────────────────────
def line_pack(did, p, pick, ids):
    return ('[UnityCrossThreadLogger]Draft.Notify '
            f'{{"draftId":"{did}","SelfPick":{pick},"SelfPack":{p},'
            f'"PackCards":"{",".join(str(i) for i in ids)}"}}')


def line_pick(did, seed, p, pick, gid):
    rid = f"{seed:08x}-{p:04x}-4{pick:03x}-8000-000000000000"
    return ('[UnityCrossThreadLogger]==> EventPlayerDraftMakePick '
            f'{{"id":"{rid}","request":"{{\\"DraftId\\":\\"{did}\\",'
            f'\\"GrpIds\\":[{gid}],\\"Pack\\":{p},\\"Pick\\":{pick}}}"}}')


def lines_done(did):
    return [f"<== DraftCompleteDraft({did})",
            '[UnityCrossThreadLogger]Client.SceneChange {"fromSceneName":"Draft",'
            '"toSceneName":"DeckBuilder","initiator":"System","context":"deck builder"}']


def append(code, lines):
    with open(simlog(code), "a", encoding="utf-8") as f:
        for ln in lines:
            f.write(ln + "\n")


# ── состояние ──────────────────────────────────────────────────────────────────────────
def load_state():
    if not os.path.exists(STATE):
        sys.exit("состояния нет — сначала `gen_feed.py <set> init`")
    return json.load(open(STATE, encoding="utf-8"))


def save_state(st):
    os.makedirs(SIMDIR, exist_ok=True)
    json.dump(st, open(STATE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def sim_at(G, code, seed, names, p, pick):
    """Пак и наш пул на координате (p,pick) — ДО нашего пика на ней."""
    pack, mine, _, misses = G.simulate(code, seed, names, p, pick)
    if misses:
        for pp, pk, nm in misses[:5]:
            print(f"❌ P{pp}P{pk}: «{nm}» — этой карты в том паке не было")
        sys.exit("состояние разъехалось с генератором; `init` заново")
    return pack, mine


def emit_pack(G, D, code, st):
    """Подать в лог пак текущей координаты. Возвращает число карт."""
    p, pick = st["coord"]
    pack, _ = sim_at(G, code, st["seed"], st["names"], p, pick)
    if pack is None:
        return 0
    n2i = name2id(D)
    ids = [n2i[first_face(c["name"])] for c in pack if first_face(c["name"]) in n2i]
    append(code, [line_pack(draft_id(st["seed"]), p, pick, ids)])
    return len(ids)


def advance(G, D, code, st, choice=None):
    """Сделать пик на текущей координате, записать его и подать следующий пак."""
    p, pick = st["coord"]
    pack, _ = sim_at(G, code, st["seed"], st["names"], p, pick)
    if pack is None:
        print("драфт окончен — `finish`")
        return False

    if choice:
        want = first_face(choice)
        card = next((c for c in pack if first_face(c["name"]) == want), None)
        if card is None:
            print(f"❌ «{choice}» в паке P{p}P{pick} нет. В паке:")
            print("   " + " · ".join(c["name"] for c in pack))
            return False
    else:
        # авто-пик: за нас пикает бот. Кто именно — спрашиваем у самого движка, доиграв
        # до следующей координаты: его пул на ней длиннее нашего ровно на этот пик.
        nc = nxt(p, pick)
        _, mine2 = sim_at(G, code, st["seed"], st["names"], *(nc if nc else (99, 99)))
        card = mine2[len(st["names"])]

    n2i = name2id(D)
    gid = n2i[first_face(card["name"])]
    st["names"].append(card["name"])
    append(code, [line_pick(draft_id(st["seed"]), st["seed"], p, pick, gid)])

    st["coord"] = list(nxt(p, pick) or (0, 0))
    if st["coord"] == [0, 0]:
        append(code, lines_done(draft_id(st["seed"])))
        st["done"] = True
        print(f"P{p}P{pick}: {card['name']} — 42/42, DRAFT COMPLETE подан")
        return False
    n = emit_pack(G, D, code, st)
    print(f"P{p}P{pick}: {card['name']}"
          f"{' (бот за нас)' if not choice else ''} → подан пак "
          f"P{st['coord'][0]}P{st['coord'][1]} ({n} карт)")
    return True


def main():
    a = sys.argv[1:]
    if not a:
        print(__doc__)
        return
    code = a[0].lower()
    cmd = a[1] if len(a) > 1 else "status"
    G, D = load_engine(code)
    os.makedirs(SIMDIR, exist_ok=True)

    if cmd == "init":
        seed = int(a[a.index("--seed") + 1]) if "--seed" in a else 7
        open(simlog(code), "w").close()
        st = {"set": code, "seed": seed, "names": [], "coord": [1, 1], "done": False}
        n = emit_pack(G, D, code, st)
        save_state(st)
        for p in (os.path.join(HERE, ".draft_watch.json"), os.path.join(HERE, ".draft_hist.json")):
            try:
                os.remove(p)
            except OSError:
                pass
        print(f"драфт {draft_id(seed)[:8]} · сет {code} · seed {seed} — подан P1P1 ({n} карт)")
        print(f"фейк-лог: {simlog(code)}\n")
        print("ассистенту (блокирующий вотчер, из папки скилла):")
        print(f"  MTGA_SETTLE=1 MTGA_LOG={simlog(code)} python3 draft_live.py {code} watch fresh")
        print(f"тебе после каждого совета:  python3 gen_feed.py {code} next")
        return

    st = load_state()
    if st["set"] != code:
        sys.exit(f"в состоянии сет {st['set']}, а запрошен {code} — сделай `init`")

    if cmd == "status":
        p, pick = st["coord"]
        print(f"драфт {draft_id(st['seed'])[:8]} · сет {code} · seed {st['seed']}")
        print(f"  фейк-лог: {simlog(code)}")
        print(f"  наших пиков: {len(st['names'])}/42 · текущий пак: P{p}P{pick} · done={st.get('done')}")
        if st["names"]:
            print("  пул: " + " · ".join(st["names"][-6:]))
        return

    if cmd == "next":
        n = int(a[2]) if len(a) > 2 and a[2].isdigit() else 1
        for _ in range(n):
            if not advance(G, D, code, st):
                break
        save_state(st)
        return

    if cmd == "pick":
        name = a[2] if len(a) > 2 else ""
        if not name:
            sys.exit('нужно имя: gen_feed.py hob pick "Card Name"')
        if advance(G, D, code, st, name):
            save_state(st)
        return

    if cmd == "finish":
        append(code, lines_done(draft_id(st["seed"])))
        st["done"] = True
        save_state(st)
        print("DraftComplete подан")
        return

    print(__doc__)


if __name__ == "__main__":
    main()
