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
from collections import Counter

SKILL = os.path.dirname(os.path.abspath(__file__))
SETS = ["sos_set.json", "mkm_set.json", "msh_set.json"]
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
            "tap target creature", "stun counter", "-1/-1",
            "to its owner's hand", "on top or bottom", "owner puts it")

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
    return {"name": name, "land": False, "cmc": int(round(cmc)), "pips": pips,
            "creature": "Creature" in tl,
            "removal": any(k in txt for k in INTERACT),
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

def simulate(base_deck):
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

    in_play, hand = [], list(hand)
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

def main():
    args = [a for a in sys.argv[1:]]
    path = next((a for a in args if not a.isdigit()), None)
    N = next((int(a) for a in args if a.isdigit()), 20000)
    if not path or not os.path.exists(path):
        print("usage: python3 draft_goldfish.py <decklist.txt> [N]"); sys.exit(1)

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

if __name__ == "__main__":
    main()
