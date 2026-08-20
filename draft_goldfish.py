#!/usr/bin/env python3
"""
Goldfish / draw simulator for a Limited decklist.

Reads an MTGA-format decklist (maindeck) and pulls each card's mana cost / type /
produced mana / tapland status from the set JSON (sos/mkm/msh). Simulates N games
"on the play" (London mulligan -> one land/turn) and reports opening-hand land
distribution, early-survival milestones, colour access, flood/screw, key-card draws.

Mana model: taplands enter tapped. Any-colour rocks (Trove-type) and basic-fetch
(Env-type) ARE modelled — detected generically from oracle text — so the splash
line shows lands-only "floor" vs "real" (with fixers). Mana dorks restricted to
instant/sorcery are counted for noncreature spells only.

Usage:
    python3 draft_goldfish.py <decklist.txt> [N]
        <decklist.txt>  MTGA-format list (lines before a "Sideboard" header)
        N               number of games (default 20000)
"""
import json, os, re, sys, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sets_registry as _reg  # единый список сетов
from collections import Counter

SKILL = os.path.dirname(os.path.abspath(__file__))
SETS = _reg.SET_FILES
WUBRG = set("WUBRG")

# ---------- card database ----------
def load_db():
    db = {}
    for fn in SETS:
        p = os.path.join(SKILL, fn)
        if not os.path.exists(p):
            continue
        for c in json.load(open(p)):
            for key in (c["name"], c["name"].split(" // ")[0]):
                db.setdefault(key, c)
    return db

def parse_cost(mana_cost, cmc_field):
    """Return (cmc, pip_sets). pip_sets = list of acceptable-colour sets per coloured pip."""
    cmc = float(cmc_field or 0)
    pip_sets, x = [], False
    for tok in re.findall(r"\{([^}]+)\}", mana_cost or ""):
        if tok == "X":
            x = True
        elif tok.isdigit():
            pass                                   # generic, already in cmc
        elif len(tok) == 1 and tok in WUBRG:
            pip_sets.append({tok})                 # {C}
        elif "/" in tok:
            a, b = tok.split("/", 1)
            if a in WUBRG and b in WUBRG:
                pip_sets.append({a, b})            # hybrid {C/D}
            # twobrid {2/C} or phyrexian {C/P}: always payable generically -> ignore pip
        # {C} colourless / other: generic
    if x:
        cmc += 1                                   # assume X >= 1
    return cmc, pip_sets

INTERACT = ("destroy target", "exile target creature", "exile target permanent",
            "damage to target", "damage to any target", "damage to up to",
            "target creature gets -", "fight", "counter target",
            "tap target creature", "tap enchanted creature", "stun counter", "-1/-1",
            "to its owner's hand", "on top or bottom", "owner puts it",
            "loses all abilities", "puts it into their library",
            "puts that card into its owner's library")

def card_info(name, db):
    c = db.get(name) or db.get(name.split(" // ")[0])
    if not c:
        return None
    tl = (c.get("type_line") or "").split(" // ")[0]
    txt = (c.get("oracle_text") or "").split(" // ")[0].lower()
    if "Land" in tl:
        prod = set(c.get("produced_mana") or []) & WUBRG
        tapped = "enters tapped" in txt or "enters the battlefield tapped" in txt
        return {"name": name, "land": True, "produces": prod or {"C"}, "tapped": tapped}
    cmc, pips = parse_cost(c.get("mana_cost"), c.get("cmc"))
    # generic fixer detection from oracle text
    fixer = None
    if "mana of any color" in txt or "mana of any colour" in txt:
        fixer = "is" if "instant or sorcery" in txt else "any"   # 'is' = restricted to I/S spells
    elif "search your library for a basic land" in txt and "into your hand" in txt:
        fixer = "fetch"
    # CLOCK-поля (§ 8.23): сила, печатное пробитие (та же EVASION_RE, что в deck_profile
    # и routes-медианах — общий словарь «ломателей»), haste. */X-силы считаются нулём —
    # как в оси big (deck_profile.metrics), договорённость единая.
    pw = c.get("power")
    if pw is None and c.get("card_faces"):
        pw = c["card_faces"][0].get("power")
    try:
        pw = int(pw)
    except (TypeError, ValueError):
        pw = 0
    import deck_profile as _DP
    front = (c.get("oracle_text") or "").split(" // ")[0]
    return {"name": name, "land": False, "cmc": int(round(cmc)), "pips": pips,
            "creature": "Creature" in tl,
            "removal": any(k in txt for k in INTERACT),
            "power": pw, "evasive": bool(_DP.EVASION_RE.search(front + " " + tl)),
            "haste": "haste" in txt,
            "fixer": fixer, "bomb": False}

# ---------- decklist ----------
def parse_decklist(path):
    out = []
    for line in open(path):
        s = line.strip()
        if not s or s.lower() in ("deck", "maindeck", "commander"):
            continue
        if s.lower().startswith("sideboard"):
            break
        m = re.match(r"^(\d+)\s+(.+?)(?:\s+\([A-Za-z0-9]+\)\s+\S+)?$", s)
        if m:
            out.append((int(m.group(1)), m.group(2).strip()))
    return out

def build_deck(decklist, db):
    deck, missing = [], []
    for n, name in decklist:
        info = card_info(name, db)
        if not info:
            missing.append(name); continue
        deck += [dict(info) for _ in range(n)]
    return deck, missing

# ---------- mana / castability ----------
def can_match(prod_list, pip_sets):
    used = [False] * len(prod_list)
    def bt(i):
        if i == len(pip_sets): return True
        for j, p in enumerate(prod_list):
            if not used[j] and (p & pip_sets[i]):
                used[j] = True
                if bt(i + 1): return True
                used[j] = False
        return False
    return bt(0)

def castable(prod_list, cmc, pip_sets):
    return len(prod_list) >= cmc and len(pip_sets) <= len(prod_list) and can_match(prod_list, pip_sets)

def choose_land(hand_lands, in_play, turn):
    names = [l["name"] for l in hand_lands]
    taps = [i for i, l in enumerate(hand_lands) if l["tapped"]]
    if turn == 1 and taps:                         # play a tapland early (few 1-drops)
        return taps[0]
    have = Counter(c for l in in_play for c in l["produces"])
    w = {"U": 3, "G": 3, "B": 2, "W": 3, "R": 3, "C": 0}
    best, bs = 0, -1
    for i, l in enumerate(hand_lands):
        s = sum((10 * w.get(c, 1)) if have[c] == 0 else w.get(c, 1) for c in l["produces"])
        if l["tapped"]: s -= 1
        if s > bs: bs, best = s, i
    return best

# ---------- simulation ----------
def keepable(hand):
    return 2 <= sum(1 for c in hand if c["land"]) <= 5

def opening(base_deck):
    """Мулиган-политика, ВЫНЕСЕНА из simulate() без изменения порядка вызовов RNG
    (числа screw/T2 откалиброваны — сдвигать нельзя, § 8.3). Общая для simulate и clock_sim."""
    deck = [dict(c) for c in base_deck]
    random.shuffle(deck)
    raw_lands = sum(1 for c in deck[:7] if c["land"])
    mcount = 0
    while True:
        random.shuffle(deck)
        hand = deck[:7]
        if keepable(hand) or mcount >= 2:
            break
        mcount += 1
    lib = deck[7:]
    for _ in range(mcount):
        lands = [c for c in hand if c["land"]]
        if len(lands) > 4:
            victim = lands[0]
        else:
            sp = sorted([c for c in hand if not c["land"]], key=lambda c: -c.get("cmc", 0))
            victim = sp[0] if sp else hand[-1]
        hand.remove(victim); lib.append(victim)
    return deck, list(hand), lib, mcount, raw_lands

def simulate(base_deck):
    deck, hand, lib, mcount, raw_lands = opening(base_deck)
    in_play = []
    first_block = first_removal = mascot_t = 99
    lands_at, black_floor, black_real = {}, {}, {}
    fixers = []          # list of (kind, online_turn) for 'any'/'is' sources
    ALL = {"W", "U", "B", "R", "G"}
    for turn in range(1, 8):
        if turn > 1 and lib:
            hand.append(lib.pop(0))
        hl = [c for c in hand if c["land"]]
        if hl:
            land = hl[choose_land(hl, in_play, turn)]
            hand.remove(land); in_play.append({**land, "pt": turn})
        land_prod = [l["produces"] for l in in_play if l["pt"] < turn or not l["tapped"]]
        lands_at[turn] = len(in_play)

        # develop mana: cast ONE fixer this turn if affordable off lands
        for c in sorted([h for h in hand if not h["land"] and h.get("fixer")],
                        key=lambda c: {"fetch": 0, "any": 1, "is": 2}[c["fixer"]]):
            if castable(land_prod, c["cmc"], c["pips"]):
                hand.remove(c)
                if c.get("creature") and c["cmc"] <= 3:                 # fixer-creature is ALSO a blocker
                    first_block = min(first_block, turn)
                if c["fixer"] == "fetch":
                    have = Counter(x for l in in_play for x in l["produces"])
                    col = min(("B", "G", "U"), key=lambda k: have[k])   # shore up neediest (splash first)
                    hand.append({"name": col + "*", "land": True,
                                 "produces": {col}, "tapped": False})
                else:
                    fixers.append((c["fixer"], turn + 1))               # online next turn
                break

        any_n = sum(1 for k, t in fixers if k == "any" and t <= turn)
        is_n = sum(1 for k, t in fixers if k == "is" and t <= turn)
        src_cre = land_prod + [set(ALL)] * any_n              # rocks usable for creatures too
        src_non = src_cre + [set(ALL)] * is_n                 # + I/S-only sources

        for c in hand:
            if c["land"]:
                continue
            src = src_cre if c.get("creature") else src_non
            if c.get("creature") and c["cmc"] <= 3 and castable(src, c["cmc"], c["pips"]):
                first_block = min(first_block, turn)
            if c.get("removal") and castable(src, c["cmc"], c["pips"]):
                first_removal = min(first_removal, turn)
            if c.get("bomb") and castable(src, c["cmc"], c["pips"]):
                mascot_t = min(mascot_t, turn)
        black_floor[turn] = castable(land_prod, 2, [{"B"}])
        black_real[turn] = castable(src_non, 2, [{"B"}])
    return dict(raw_lands=raw_lands, mcount=mcount, first_block=first_block,
                first_removal=first_removal, mascot_t=mascot_t, lands_at=lands_at,
                black_floor=black_floor, black_real=black_real)

# ---------- CLOCK: на каком ходу колода набирает 20 урона (§ 8.23) ----------
def _alloc(sources, cmc, pips):
    """Индексы источников под каст (сначала пипы бэктреком, затем generic) или None."""
    n = int(cmc)
    if len(sources) < n or len(pips) > n:
        return None
    used = [False] * len(sources)
    def bt(i):
        if i == len(pips):
            return True
        for j, p in enumerate(sources):
            if not used[j] and (p & pips[i]):
                used[j] = True
                if bt(i + 1):
                    return True
                used[j] = False
        return False
    if not bt(0):
        return None
    picked = [j for j, u in enumerate(used) if u]
    for j in range(len(sources)):
        if len(picked) >= n:
            break
        if not used[j]:
            picked.append(j)
    return picked if len(picked) == n else None

def clock_sim(base_deck, N=4000, blockers=2, max_turn=14):
    """ЧАСЫ КОЛОДЫ: медианный ход, на котором суммарный урон достигает 20.

    ВЕРХНЯЯ ГРАНИЦА ТЕМПА, не винрейт: оппонент не мешает (removal/блоков по нам нет).
    Два режима: пустая доска (бьют все) и «стойка» из K блокеров — каждый ход блокеры
    съедают урон K самых крупных НЕпробивающих атакеров; пробивающие = та же
    EVASION_RE, что ось «воздух» в routes (flying/menace/unblockable/trample).
    Ограничения v1 (задокументированы в § 8.23): некреатуры урона не дают (эквип,
    бёрн, Армии-токены amass — мимо), саммон-сикнесс учтён, haste учтён, счётчики/
    пампы не растят силу. Каст — жадный (дорогие существа вперёд) на реальной
    манабазе через ту же модель источников, что и остальной голдфиш."""
    kills_open, kills_wall = [], []
    for _ in range(N):
        _deck, hand, lib, _mc, _rl = opening(base_deck)
        lands_ip, board = [], []          # board: (power, evasive, cast_turn, haste)
        dmg_o = dmg_w = 0
        ko = kw = 99
        for turn in range(1, max_turn + 1):
            if turn > 1 and lib:
                hand.append(lib.pop(0))
            hl = [c for c in hand if c["land"]]
            if hl:
                land = hl[choose_land(hl, lands_ip, turn)]
                hand.remove(land)
                lands_ip.append({**land, "pt": turn})
            avail = [l["produces"] for l in lands_ip if l["pt"] < turn or not l["tapped"]]
            for c in sorted([h for h in hand if not h["land"] and h.get("creature")],
                            key=lambda c: -c["cmc"]):
                pick = _alloc(avail, c["cmc"], c["pips"])
                if pick is not None:
                    avail = [s for j, s in enumerate(avail) if j not in pick]
                    hand.remove(c)
                    board.append((c["power"], c["evasive"], turn, c["haste"]))
            attackers = [(p, e) for p, e, t, h in board if t < turn or h]
            dmg_o += sum(p for p, _e in attackers)
            ground = sorted((p for p, e in attackers if not e), reverse=True)
            dmg_w += sum(p for p, e in attackers if e) + sum(ground[blockers:])
            if ko == 99 and dmg_o >= 20:
                ko = turn
            if kw == 99 and dmg_w >= 20:
                kw = turn
            if ko < 99 and kw < 99:
                break
        kills_open.append(ko)
        kills_wall.append(kw)
    return kills_open, kills_wall

def clock_stats(kills):
    s = sorted(kills)
    med = s[len(s) // 2]
    return med, (lambda t: sum(1 for x in kills if x <= t) / len(kills))

def calibrate(setcode, N=1200):
    """Голдфиш-калибровка по парам на ref_decks/<set>/ → <set>_clocks.json.

    Расширена 20.08.2026 (JOURNAL § 8.27, закрытие долга «числа n=23 старой MSH-выборки»):
    кроме часов пишутся медианы ранней игры победителей КАЖДОЙ пары — screw% · существо-к-T2%
    · блокер-к-T3% · removal-к-T3/T4% · муллиганы. Это те же метрики, которыми mode_build
    меряет НАШУ колоду, посчитанные тем же simulate() — сравнение прибор-в-прибор.
    Описательная популяция победителей, не предикторы (§ 8.6)."""
    import glob
    import build_audit as A
    import statistics as st
    dbA = A.load_db()
    db = load_db()
    rows = {}
    files = sorted(glob.glob(os.path.join(SKILL, "ref_decks", setcode, "*.txt")))
    Ne = max(400, N // 2)          # ранние метрики: отдельный прогон simulate()
    print(f"калибровка: {len(files)} листов · clock {N} + early {Ne} игр на лист")
    for i, f in enumerate(files):
        deck, missing = build_deck(parse_decklist(f), db)
        if len(deck) < 38:
            continue
        pair = A.deck_colors(f, dbA)
        ko, kw = clock_sim(deck, N)
        res = [simulate(deck) for _ in range(Ne)]
        e = dict(
            screw=100 * sum(1 for r in res if r["lands_at"][4] <= 2) / Ne,
            t2=100 * sum(1 for r in res if r["first_block"] <= 2) / Ne,
            b3=100 * sum(1 for r in res if r["first_block"] <= 3) / Ne,
            rem3=100 * sum(1 for r in res if r["first_removal"] <= 3) / Ne,
            rem4=100 * sum(1 for r in res if r["first_removal"] <= 4) / Ne,
            mull=sum(r["mcount"] for r in res) / Ne,
        )
        rows.setdefault(pair, []).append(
            (sorted(ko)[len(ko) // 2], sorted(kw)[len(kw) // 2], e))
        if (i + 1) % 50 == 0:
            print(f"  …{i + 1}/{len(files)}")
    out = {}
    for pair, v in rows.items():
        if len(v) < 12:
            continue
        rec = dict(open=st.median([a for a, _, _ in v]), wall=st.median([b for _, b, _ in v]),
                   n=len(v))
        for k in ("screw", "t2", "b3", "rem3", "rem4", "mull"):
            vals = [e[k] for _, _, e in v]
            rec[k] = round(st.median(vals), 1)
            rec[k + "_q"] = [round(sorted(vals)[len(vals) // 4], 1),
                             round(sorted(vals)[3 * len(vals) // 4], 1)]
        out[pair] = rec
    p = os.path.join(SKILL, f"{setcode}_clocks.json")
    json.dump(out, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"{'пара':<5}{'n':>4} {'пустая':>7} {'стойка':>7} {'T2%':>6} {'блкT3%':>7} "
          f"{'remT4%':>7} {'скрю%':>6}")
    for pair in sorted(out, key=lambda x: -out[x]["n"]):
        r = out[pair]
        print(f"{pair:<5}{r['n']:>4} {r['open']:>7} {r['wall']:>7} {r['t2']:>6} "
              f"{r['b3']:>7} {r['rem4']:>7} {r['screw']:>6}")
    print(f"→ записано {p}")

def main():
    args = [a for a in sys.argv[1:]]
    if "--calibrate" in args:
        i = args.index("--calibrate")
        code = args[i + 1] if len(args) > i + 1 else "hob"
        random.seed(12345)
        calibrate(code, next((int(a) for a in args if a.isdigit()), 1200))
        return
    path = next((a for a in args if not a.isdigit()), None)
    N = next((int(a) for a in args if a.isdigit()), 20000)
    if not path or not os.path.exists(path):
        print("usage: python3 draft_goldfish.py <decklist.txt> [N] | --calibrate <set> [N]"); sys.exit(1)

    db = load_db()
    decklist = parse_decklist(path)
    deck, missing = build_deck(decklist, db)
    nonland = [c for c in deck if not c["land"]]
    # tag the single highest-cmc creature as the 'bomb' to track
    cre = [c for c in deck if not c["land"] and c.get("creature")]
    if cre:
        top = max(c["cmc"] for c in cre)
        bomb_name = next(c["name"] for c in cre if c["cmc"] == top)
        for c in deck:
            if c["name"] == bomb_name: c["bomb"] = True
    else:
        bomb_name = None

    if missing:
        print("WARNING — not found in set JSON (skipped):", ", ".join(sorted(set(missing))))
    if len(deck) < 40:
        print(f"WARNING — only {len(deck)} cards parsed (expected >=40)")

    random.seed(12345)
    res = [simulate(deck) for _ in range(N)]
    P = lambda x: f"{100*x/N:5.1f}%"
    lands = sum(1 for c in deck if c["land"])
    rem = sum(1 for c in nonland if c.get("removal"))

    print(f"\n=== GOLDFISH  ({N:,} games, on the play) ===")
    print(f"{len(deck)} cards | {lands} lands | {len(cre)} creatures | ~{rem} removal/interaction"
          f"{' | bomb tracked: '+bomb_name if bomb_name else ''}")
    print("model: 'floor' = land mana only; 'real' also taps any-colour rocks + fetched basics\n")

    lh = Counter(r["raw_lands"] for r in res)
    print("OPENING 7 — lands:")
    for k in range(8):
        print(f"  {k} land: {P(lh.get(k,0))}  {'#'*round(60*lh.get(k,0)/N)}")
    keep = sum(v for k, v in lh.items() if 2 <= k <= 5)
    print(f"  keepable (2-5): {P(keep)}   mulligan first hand: {P(N-keep)}\n")

    print("EARLY SURVIVAL:")
    print(f"  creature castable by turn 2: {P(sum(1 for r in res if r['first_block']<=2))}")
    print(f"  blocker  castable by turn 3: {P(sum(1 for r in res if r['first_block']<=3))}")
    print(f"  removal available by turn 3: {P(sum(1 for r in res if r['first_removal']<=3))}")
    print(f"  removal available by turn 4: {P(sum(1 for r in res if r['first_removal']<=4))}\n")

    has_fix = any(c.get("fixer") for c in nonland)
    print("COLOUR — can cast a {1}{B}-style splash card:")
    print("  turn |  lands-only (floor) | with fixers (real)")
    for t in (3, 4, 5):
        fl = P(sum(1 for r in res if r["black_floor"][t]))
        rl = P(sum(1 for r in res if r["black_real"][t]))
        print(f"   {t}   |   {fl}            | {rl}")
    if has_fix:
        print("  (fixers modelled: Trove-type any-colour + Env-type basic-fetch in this deck)")
    print()

    print("MANA CONSISTENCY:")
    print(f"  screwed (<=2 lands through turn 4): {P(sum(1 for r in res if r['lands_at'][4]<=2))}")
    print(f"  flooded (>=7 lands by turn 6):      {P(sum(1 for r in res if r['lands_at'][6]>=7))}\n")

    if bomb_name:
        print(f"TOP-END ({bomb_name}):")
        print(f"  castable by turn 6: {P(sum(1 for r in res if r['mascot_t']<=6))}")
        print(f"  castable by turn 7: {P(sum(1 for r in res if r['mascot_t']<=7))}")
    print(f"avg mulligans/game: {sum(r['mcount'] for r in res)/N:.2f}\n")

    ko, kw = clock_sim(deck, min(N, 4000))
    mo, po = clock_stats(ko)
    mw, pw_ = clock_stats(kw)
    fmt = lambda m: (f"ход {m}" if m < 99 else ">14")
    print("CLOCK — на каком ходу набрано 20 урона (оппонент НЕ мешает — верхняя граница темпа):")
    print(f"  пустая доска:     медиана {fmt(mo)} · к 8-му {100*po(8):.0f}% · к 10-му {100*po(10):.0f}%")
    print(f"  через 2 блокеров: медиана {fmt(mw)} · к 8-му {100*pw_(8):.0f}% · к 10-му {100*pw_(10):.0f}%")
    print("  (некреатуры урона не дают: эквип/бёрн/amass-Армии мимо — см. JOURNAL § 8.23)")
    try:
        import build_audit as A
        code, _how = A.detect_set(path, path, None)
        cp = os.path.join(SKILL, f"{code}_clocks.json")
        if os.path.exists(cp):
            pair = A.deck_colors(path, A.load_db())
            ref = json.load(open(cp)).get(pair)
            if ref:
                print(f"  победители пары {pair} (n={ref['n']}): пустая {ref['open']} · "
                      f"стойка {ref['wall']}")
    except SystemExit:
        pass
    print()

if __name__ == "__main__":
    main()
