#!/usr/bin/env python3
"""Draft replay feeder — латентный тест-харнесс для draft_live.py.

Проигрывает РЕАЛЬНЫЙ драфт из Arena Player.log в фейковый лог пик-за-пиком, по твоей
команде из отдельной консоли. Ассистент крутит обычный draft_live.py (через MTGA_LOG,
указывающий на фейк-лог) и советует пик — ты засекаешь, сколько думает модель/effort.

Строки лога копируются ВЕРБАТИМ из настоящего лога → формат гарантированно совместим
с парсером draft_live.py (find_packs / find_my_picks / детектор завершения).

ТЫ (из отдельной консоли) управляешь темпом:
  python3 draft_sim.py list                    — какие драфты есть в логах
  python3 draft_sim.py init [id8] [--set msh]  — извлечь драфт, обнулить фейк-лог
  python3 draft_sim.py next [N]                — подать следующий wake-пик (пик<=11), N раз
  python3 draft_sim.py step [N]                — подать ровно один pick-line (гранулярно)
  python3 draft_sim.py finish                  — досыпать хвост пака + DraftComplete
  python3 draft_sim.py status                  — где мы сейчас
  python3 draft_sim.py reset                   — обнулить лог, оставить тот же драфт

Ассистент в это время (init печатает готовые команды с нужным MTGA_LOG):
  MTGA_LOG=<sim.log> python3 draft_live.py <set> wake fresh   # ПЕРЕД первым next
  MTGA_LOG=<sim.log> python3 draft_live.py <set>              # снапшот текущего пака
  MTGA_LOG=<sim.log> python3 draft_live.py <set> wake         # переарм на следующий

Почему пик<=11: сам draft_live.py в wake-режиме будит ассистента только на пиках 1–11
(хвост 12–14 — 1–3 карты, тривиально). `next` подаёт ровно один такой wake-пик, тихо
досыпая хвостовые пики предыдущего бустера, чтобы пул оставался полным.
"""
import json, re, os, sys, glob, time

HERE = os.path.dirname(os.path.abspath(__file__))
SIMDIR = os.path.join(HERE, "sim")
SIMLOG = os.path.join(SIMDIR, "sim_player.log")
STATE = os.path.join(SIMDIR, "sim_state.json")
LOGDIR = os.path.expanduser("~/Library/Logs/Wizards Of The Coast/MTGA")
SRC_LOGS = [os.path.join(LOGDIR, "Player-prev.log"), os.path.join(LOGDIR, "Player.log")]

NOTIFY = re.compile(r'Draft\.Notify\s*(\{.*?"PackCards".*?\})')
SELFPACK = re.compile(r'"SelfPack"\s*:\s*(\d+)')
SELFPICK = re.compile(r'"SelfPick"\s*:\s*(\d+)')

def is_pack(l):   return "Draft.Notify" in l and "PackCards" in l
def is_pick(l):   return "==>" in l and "MakePick" in l

def pack_meta(l):
    """(pack, pick, ncards) из строки Draft.Notify."""
    sp = SELFPACK.search(l); si = SELFPICK.search(l)
    m = NOTIFY.search(l)
    n = 0
    if m:
        try: n = len(re.findall(r'\d+', json.loads(m.group(1)).get("PackCards", "")))
        except Exception: n = 0
    return (int(sp.group(1)) if sp else None,
            int(si.group(1)) if si else None, n)

# ─── обнаружение драфтов в логах ──────────────────────────────────────────────
def _set_ids():
    out = {}
    for s in ("msh", "sos", "mkm"):
        p = os.path.join(HERE, f"{s}_set.json")
        if not os.path.exists(p): continue
        ids = set()
        try:
            for c in json.load(open(p)):
                a = c.get("arena_id") or c.get("mtga_id")
                if a is not None: ids.add(int(a))
        except Exception: pass
        out[s] = ids
    return out

def find_drafts():
    """draftId -> dict(picks, packs, src, set, first_id, order) в хронологии логов."""
    sets = _set_ids()
    def which(cid):
        for s, ids in sets.items():
            if cid in ids: return s
        return "?"
    drafts = {}
    order = 0
    for lf in SRC_LOGS:
        if not os.path.exists(lf): continue
        for ln in open(lf, encoding="utf-8", errors="ignore"):
            m = NOTIFY.search(ln)
            if not m: continue
            try: d = json.loads(m.group(1))
            except Exception: continue
            did = d.get("draftId")
            if not did: continue
            cards = [int(x) for x in re.findall(r'\d+', d.get("PackCards", ""))]
            e = drafts.setdefault(did, {"picks": 0, "packs": {}, "src": lf,
                                        "first_id": cards[0] if cards else None,
                                        "order": order})
            e["picks"] += 1
            e["packs"][d.get("SelfPack")] = e["packs"].get(d.get("SelfPack"), 0) + 1
            e["order"] = order  # последнее вхождение = позиция в хронологии
            order += 1
    for did, e in drafts.items():
        e["set"] = which(e["first_id"]) if e["first_id"] else "?"
    return drafts

def cmd_list(args=None):
    drafts = find_drafts()
    if not drafts:
        print("Драфтов в логах не нашёл (Player.log / Player-prev.log).")
        return
    print("Доступные драфты (самый свежий снизу):")
    for did, e in sorted(drafts.items(), key=lambda kv: kv[1]["order"]):
        packs = ",".join(f"P{k}:{v}" for k, v in sorted(e["packs"].items()) if k)
        src = os.path.basename(e["src"])
        print(f"  {did[:8]}…  set={e['set']:<3} пиков={e['picks']:<3} [{packs}]  ({src})")
    print("\ninit по умолчанию берёт самый свежий. Иначе: python3 draft_sim.py init <id8>")

# ─── извлечение строк одного драфта ───────────────────────────────────────────
def extract_lines(draft_id, src):
    """Вербатим-строки драфта (pack Notify + makepick) в порядке файла."""
    out = []
    for ln in open(src, encoding="utf-8", errors="ignore"):
        ln = ln.rstrip("\n")
        if draft_id not in ln: continue
        if is_pack(ln) or is_pick(ln):
            out.append(ln)
    return out

# ─── состояние ────────────────────────────────────────────────────────────────
def load_state():
    if not os.path.exists(STATE):
        sys.exit("Нет активного сима. Сначала: python3 draft_sim.py init")
    return json.load(open(STATE))

def save_state(st):
    json.dump(st, open(STATE, "w"))

def n_wakes_total(lines):
    return sum(1 for l in lines if is_pack(l) and (pack_meta(l)[1] or 99) <= 11)

def n_wakes_upto(lines, pos):
    return sum(1 for l in lines[:pos] if is_pack(l) and (pack_meta(l)[1] or 99) <= 11)

# ─── команды ──────────────────────────────────────────────────────────────────
def cmd_init(args):
    drafts = find_drafts()
    if not drafts:
        sys.exit("Драфтов в логах нет.")
    want = next((a for a in args if not a.startswith("-")), None)
    setarg = None
    if "--set" in args:
        setarg = args[args.index("--set") + 1]
    if want:
        cand = [d for d in drafts if d.startswith(want)]
        if not cand:
            sys.exit(f"Драфт {want} не найден. `python3 draft_sim.py list`")
        did = cand[0]
    else:
        did = max(drafts, key=lambda d: drafts[d]["order"])  # самый свежий
    e = drafts[did]
    st_set = setarg or e["set"]
    lines = extract_lines(did, e["src"])
    if not lines:
        sys.exit("Не извлёк ни одной строки — формат лога неожиданный.")
    complete = (f"<== DraftCompleteDraft({did})\n"
                f'[UnityCrossThreadLogger]Client.SceneChange '
                f'{{"fromSceneName":"Draft","toSceneName":"DeckBuilder",'
                f'"initiator":"System","context":"deck builder"}}')
    os.makedirs(SIMDIR, exist_ok=True)
    open(SIMLOG, "w").close()  # обнулить фейк-лог
    st = {"draftId": did, "src": e["src"], "set": st_set, "simlog": SIMLOG,
          "lines": lines, "pos": 0, "complete": complete, "done": False}
    save_state(st)
    total = n_wakes_total(lines)
    print(f"✔ Сим готов: draft {did[:8]}…  set={st_set}  пиков={len(lines)//2}  "
          f"wake-точек(пик<=11)={total}")
    print(f"  фейк-лог: {SIMLOG}  (пуст)")
    print("\nАссистенту — крутить draft_live.py на этом логе:")
    print(f"  export MTGA_LOG='{SIMLOG}'")
    print(f"  python3 {os.path.join(HERE,'draft_live.py')} {st_set} wake fresh   # ПЕРЕД первым next")
    print(f"  python3 {os.path.join(HERE,'draft_live.py')} {st_set}              # снапшот пака")
    print("\nТеперь подавай пики:  python3 draft_sim.py next")

def _append(st, lo, hi):
    chunk = st["lines"][lo:hi]
    with open(st["simlog"], "a", encoding="utf-8") as f:
        f.write("\n".join(chunk) + "\n")
    return chunk

def _advance(st, stop_pred):
    """Аппендит строки от pos до включительно первого pack-line, где stop_pred(pick).
    Хвостовые pack-и (не удовлетворяющие pred) досыпаются тихо. Возвращает последний pack."""
    lines = st["lines"]; pos = st["pos"]; start = pos
    last = None
    while pos < len(lines):
        l = lines[pos]; pos += 1
        if is_pack(l):
            pk, pi, nc = pack_meta(l)
            last = (pk, pi, nc)
            if stop_pred(pi):
                break
    _append(st, start, pos)
    st["pos"] = pos
    return last

def _report(st, last, tag):
    total = n_wakes_total(st["lines"])
    done_w = n_wakes_upto(st["lines"], st["pos"])
    ts = time.strftime("%H:%M:%S") + f".{int((time.time()%1)*1000):03d}"
    if last:
        pk, pi, nc = last
        print(f"▶ [{ts}] подан P{pk}/P{pi} — {nc} карт   ({tag}: wake {done_w}/{total})  ⏱ старт клока")
    if st["pos"] >= len(st["lines"]):
        print("  (все пики поданы — заверши: python3 draft_sim.py finish)")

def cmd_next(args):
    st = load_state()
    n = int(args[0]) if args and args[0].isdigit() else 1
    for _ in range(n):
        if st["pos"] >= len(st["lines"]):
            print("Все пики уже поданы. python3 draft_sim.py finish"); break
        last = _advance(st, lambda pi: (pi or 99) <= 11)
        _report(st, last, "next")
    save_state(st)

def cmd_step(args):
    st = load_state()
    n = int(args[0]) if args and args[0].isdigit() else 1
    for _ in range(n):
        if st["pos"] >= len(st["lines"]):
            print("Все пики уже поданы. python3 draft_sim.py finish"); break
        last = _advance(st, lambda pi: True)  # стоп на первом же pack
        _report(st, last, "step")
    save_state(st)

def cmd_finish(args):
    st = load_state()
    lines = st["lines"]
    if st["pos"] < len(lines):
        _append(st, st["pos"], len(lines))
        st["pos"] = len(lines)
    with open(st["simlog"], "a", encoding="utf-8") as f:
        f.write(st["complete"] + "\n")
    st["done"] = True
    save_state(st)
    print("✔ Досыпан хвост + DraftCompleteDraft. wake напечатает DRAFT COMPLETE.")

def cmd_status(args):
    st = load_state()
    lines = st["lines"]; pos = st["pos"]
    total = n_wakes_total(lines); done_w = n_wakes_upto(lines, pos)
    # последний поданный pack
    last = None
    for l in lines[:pos]:
        if is_pack(l): last = pack_meta(l)
    cur = f"P{last[0]}/P{last[1]} ({last[2]} карт)" if last else "— (лог пуст)"
    print(f"draft {st['draftId'][:8]}…  set={st['set']}")
    print(f"  фейк-лог: {st['simlog']}")
    print(f"  подано строк: {pos}/{len(lines)}   wake-точек: {done_w}/{total}")
    print(f"  последний поданный пак: {cur}   done={st.get('done')}")

def cmd_reset(args):
    st = load_state()
    open(st["simlog"], "w").close()
    st["pos"] = 0; st["done"] = False
    save_state(st)
    print(f"✔ Фейк-лог обнулён, драфт {st['draftId'][:8]}… с начала. "
          f"Не забудь: draft_live.py {st['set']} wake fresh")

CMDS = {"list": cmd_list, "init": cmd_init, "next": cmd_next, "step": cmd_step,
        "finish": cmd_finish, "status": cmd_status, "reset": cmd_reset}

def main():
    if len(sys.argv) < 2 or sys.argv[1] not in CMDS:
        print(__doc__); return
    CMDS[sys.argv[1]](sys.argv[2:])

if __name__ == "__main__":
    main()
