#!/usr/bin/env python3
"""Живой вотчер МАТЧА: блокируется до точки моего решения и печатает ПОЛНУЮ позицию.

  python3 match_live.py [msh] [fresh]

Отличия от match_watch.py (который отдаёт голые имена):
  - базовые земли резолвятся в Plains/Island/... (по subtypes из лога)
  - P/T с учётом счётчиков, ЗАТАПНУТ, «вызван в этот ход»
  - открытая мана обеих сторон (нетапнутые земли)
  - карты вне нашего сет-файла (колода бота) печатаются как [чужая N/M]
Точки решения: моя Main1 · объявление блоков в их ход · мой приоритет при их атаке.
"""
import re, os, sys, time, json
import match_watch as mw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sets_registry as _reg  # единый список сетов
SETCODE = "msh"


def load_set_cards():
    for a in sys.argv[1:]:
        if _reg.is_set(a):
            global SETCODE
            SETCODE = a.lower()
    path = os.path.join(HERE, f"{SETCODE}_set.json")
    if not os.path.exists(path):
        return {}
    data = json.load(open(path))
    cards = data["data"] if isinstance(data, dict) and "data" in data else data
    out = {}
    for c in cards:
        out[c["name"].lower()] = c
    return out
STATE = os.path.join(HERE, ".match_live.json")
POLL = 0.7
TIMEOUT = 900

BASIC = ("Plains", "Island", "Swamp", "Mountain", "Forest")


def land_map(txt):
    """grpId -> 'Plains'/... для базовых земель (у каждого арта свой grpId)."""
    out = {}
    for m in re.finditer(r'"grpId":\s*(\d+)[^{}]*?"cardTypes":\s*\[\s*"CardType_Land"\s*\]'
                         r'[^{}]*?"subtypes":\s*\[\s*"SubType_(\w+)"', txt):
        g, sub = int(m.group(1)), m.group(2)
        if sub in BASIC:
            out[g] = sub
    return out


def details(game):
    """instanceId -> {p,t,tap,sick} по последнему упоминанию объекта."""
    d = {}
    for m in re.finditer(r'"instanceId":\s*(\d+)((?:[^{}]|\{[^{}]*\})*)', game):
        iid = int(m.group(1)); b = m.group(2)
        e = d.setdefault(iid, {})
        p = re.search(r'"power":\s*\{\s*"value":\s*(-?\d+)', b)
        t = re.search(r'"toughness":\s*\{\s*"value":\s*(-?\d+)', b)
        tap = re.search(r'"isTapped":\s*(true|false)', b)
        sk = re.search(r'"hasSummoningSickness":\s*(true|false)', b)
        if p: e["p"] = int(p.group(1))
        if t: e["t"] = int(t.group(1))
        if tap: e["tap"] = tap.group(1) == "true"
        if sk: e["sick"] = sk.group(1) == "true"
    return d


def attachments(game):
    """target instanceId -> [aura/equipment instanceId, ...] — из AnnotationType_Attachment(Created).
    affectorId = прикреплённый объект (аура/эквип), affectedIds = цель(и)."""
    out = {}
    for m in re.finditer(r'"affectorId":\s*(\d+)\s*,\s*"affectedIds":\s*\[\s*(\d+)\s*\]'
                         r'[^{}]*?"type":\s*\[\s*"AnnotationType_Attachment(?:Created)?"', game):
        affector, target = int(m.group(1)), int(m.group(2))
        lst = out.setdefault(target, [])
        if affector not in lst:
            lst.append(affector)
    return out


def card_facts(card):
    """Одна строка фактов + полный оракл-текст — принудительно перед советом."""
    if not card:
        return None
    cost = card.get("mana_cost") or ""
    tl = card.get("type_line") or ""
    ot = card.get("oracle_text") or ""
    if not cost and card.get("card_faces"):
        f0 = card["card_faces"][0]
        cost = f0.get("mana_cost", "")
        tl = f0.get("type_line", tl)
        ot = f0.get("oracle_text", ot)
    pt = f" {card['power']}/{card['toughness']}" if card.get("power") is not None else ""
    tags = []
    if "Flash" in ot: tags.append("⚡FLASH")
    if re.search(r'\{T\}', ot): tags.append("🔧{T}-абилка")
    if "attacks alone" in ot: tags.append("🎯solo-attack триггер")
    if "Aura" in tl or "becomes a copy" in ot: tags.append("⚠копирование/аура")
    tagstr = " " + " ".join(tags) if tags else ""
    return f"  • {card['name']} {cost}{pt} — {tl}{tagstr}\n      {ot.replace(chr(10), ' / ')[:280]}"


def render(txt, names):
    game = mw.scope_current_game(txt)
    me = mw.seat_in_game(game) or mw.get_my_seat(txt)
    st = mw.parse_state(game)
    if not st["objs"] or me is None:
        return None, None
    lm = land_map(txt)
    det = details(game)
    atk = attachments(game)
    setcards = load_set_cards()
    seats = {o["owner"] for o in st["objs"].values()} | set(st["life"])
    opp = next((s for s in seats if s != me), None)
    t = st["turn"] or {}

    def nm(o, d):
        n = names.get(o["grp"]) or lm.get(o["grp"])
        if n:
            return n
        pt = f" {d['p']}/{d['t']}" if "p" in d else ""
        return f"[чужая{pt}]"

    def zone(seat, ztype, by):
        rows = []
        for iid, o in sorted(st["objs"].items()):
            z = st["zones"].get(o["zid"], (None, None))[0]
            if z != ztype or o[by] != seat:
                continue
            rows.append((iid, o, det.get(iid, {})))
        return rows

    def fmt_board(rows):
        out, mana = [], 0
        for iid, o, d in rows:
            n = nm(o, d)
            island = n in BASIC or (names.get(o["grp"]) and "Land" in str(names.get(o["grp"])))
            if n in BASIC and not d.get("tap"):
                mana += 1
            pt = f" {d['p']}/{d['t']}" if "p" in d and n not in BASIC else ""
            fl = []
            if d.get("tap"): fl.append("Т")
            if d.get("sick"): fl.append("вызван")
            # ⚠ ауры/эквип, привязанные К этому объекту — не пропустить лок/бафф на теле
            attached = atk.get(iid, [])
            if attached:
                anames = []
                for aid in attached:
                    ao = st["objs"].get(aid)
                    an = names.get(ao["grp"]) if ao else None
                    anames.append(an or f"чужая-аура/id{aid}")
                fl.append("⚠ПОД: " + ",".join(anames))
            out.append(f"{n}{pt}" + (f"({','.join(fl)})" if fl else ""))
        return out, mana

    L = []
    who = "ТВОЙ ХОД" if t.get("active") == me else "ХОД ОППА"
    L.append(f"=== ход {t.get('n')} · {t.get('step') or t.get('phase')} · {who} ===")
    L.append(f"ЖИЗНИ: ты {st['life'].get(me,'?')} / опп {st['life'].get(opp,'?')}")
    mb, mymana = fmt_board(zone(me, "ZoneType_Battlefield", "ctrl"))
    ob, oppmana = fmt_board(zone(opp, "ZoneType_Battlefield", "ctrl"))
    hand = [nm(o, d) for _, o, d in zone(me, "ZoneType_Hand", "owner")]
    L.append(f"ТВОЙ СТОЛ ({mymana} откр. маны): " + (", ".join(mb) or "—"))
    L.append(f"СТОЛ ОППА ({oppmana} откр. маны): " + (", ".join(ob) or "—"))
    L.append("РУКА: " + (", ".join(hand) or "—"))
    stack = [nm(o, det.get(i, {})) for i, o, d in zone(me, "ZoneType_Stack", "owner")] + \
            [nm(o, det.get(i, {})) for i, o, d in zone(opp, "ZoneType_Stack", "owner")]
    if stack:
        L.append("СТЕК: " + ", ".join(stack))
    gy = [nm(o, d) for _, o, d in zone(me, "ZoneType_Graveyard", "owner")]
    if gy:
        L.append(f"твоё GY ({len(gy)}): " + ", ".join(gy[-8:]))

    # === ПРИНУДИТЕЛЬНАЯ СПРАВКА: полный оракл каждого уникального объекта в игре ===
    # Не полагаться на память — тексты печатаются здесь всегда, шаг 1 процедуры
    # (live_advice_rules.md) пропустить физически нельзя, если это прочитано.
    all_rows = (zone(me, "ZoneType_Battlefield", "ctrl") + zone(opp, "ZoneType_Battlefield", "ctrl")
                + zone(me, "ZoneType_Hand", "owner"))
    seen, facts = set(), []
    for iid, o, d in all_rows:
        n = nm(o, d)
        if n in BASIC or n.startswith("[чужая") or n in seen:
            continue
        seen.add(n)
        card = setcards.get(n.lower())
        f = card_facts(card)
        if f:
            facts.append(f)
        else:
            facts.append(f"  • {n} — [нет данных в {SETCODE}_set.json]")
    if facts:
        L.append("\n=== СПРАВКА (читать ПЕРЕД советом, шаг 1) ===")
        L.extend(facts)
        unresolved = [nm(o, d) for _, o, d in
                      (zone(me, "ZoneType_Battlefield", "ctrl") + zone(opp, "ZoneType_Battlefield", "ctrl"))
                      if nm(o, d).startswith("[чужая")]
        if unresolved:
            L.append(f"  ⚠ БЕЗ ДАННЫХ (вне сета): {', '.join(sorted(set(unresolved)))} — спроси у игрока способность.")

    sig = (t.get("n"), t.get("step"), t.get("phase"), len(st["objs"]),
           st["life"].get(me), st["life"].get(opp))
    return sig, "\n".join(L)


def mulligan_pending(txt):
    """True, если последний MulliganReq в текущей игре ещё БЕЗ ответа —
    то есть после него в логе не появилось turnInfo (игра ещё не началась)."""
    game = mw.scope_current_game(txt)
    idxs = [m.start() for m in re.finditer("MulliganReq", game)]
    if not idxs:
        return False
    after = game[idxs[-1]:]
    return not re.search(r'"turnInfo"', after)


def is_decision(txt, me_prio_only=True):
    if mulligan_pending(txt):
        return True
    game = mw.scope_current_game(txt)
    me = mw.seat_in_game(game) or mw.get_my_seat(txt)
    st = mw.parse_state(game)
    t = st.get("turn") or {}
    if me is None or t.get("priority") != me:
        return False
    ph = f"{t.get('phase') or ''}|{t.get('step') or ''}"
    mine = t.get("active") == me
    # ТОЛЬКО моя главная фаза (Main1/Main2) — режим тестирования, их атака НЕ триггерит
    return mine and "Main" in ph


def main():
    if "fresh" in sys.argv[1:]:
        try: os.remove(STATE)
        except OSError: pass
    last = None
    if os.path.exists(STATE):
        try: last = tuple(json.load(open(STATE))["sig"])
        except Exception: last = None
    names = mw.load_names()
    deadline = time.time() + TIMEOUT
    while time.time() < deadline:
        txt = mw.read_logs()
        if is_decision(txt):
            # debounce: turnInfo может мелькнуть транзитным блоком (Main1->BeginCombat
            # за доли секунды) — перепроверяем ЕЩЁ РАЗ через паузу, прежде чем верить.
            time.sleep(0.3)
            txt2 = mw.read_logs()
            if not is_decision(txt2):
                time.sleep(POLL)
                continue
            sig, block = render(txt2, names)
            if sig and list(sig) != list(last or ()):
                print(block)
                json.dump({"sig": list(sig)}, open(STATE, "w"))
                return
        time.sleep(POLL)
    print("WAITING — за 15 мин точки решения не было")


if __name__ == "__main__":
    main()
