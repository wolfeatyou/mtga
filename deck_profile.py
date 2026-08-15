#!/usr/bin/env python3
"""
Профиль лимитед-колоды по нашим порогам — для сравнения ЧУЖИХ (diamond/mythic) листов
с нашими сборками на одних и тех же числах.

Считает то, что у нас операционализировано как пороги/квоты, и НИЧЕГО не додумывает:
  · земли / нонленды
  · существа отдельно от спеллов, кривая по каждой группе
  · **существ cmc≤2** — квота ⚑ КРИВАЯ (4 шт ≈ 55% «существо к T2», 5 ≈ 64-65%)
  · ломатели стойки (flying / menace / unblockable / trample / reach)
  · безусловное removal (destroy|exile target) отдельно от условного
  · верх кривой: cmc≥5 и cmc≥6 (порог 5)
  · средний GIH (глобальный) и парный, если есть cache_17l_<set>_<PAIR>.json

Usage:  python3 deck_profile.py <decklist.txt> [PAIR]
        PAIR — пара для парного GIH, напр. UB. Необязательно.
"""
import json, os, re, sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sets_registry as _reg  # единый список сетов
SETS = _reg.SET_FILES
RATINGS = {"msh": "17l_msh_premierdraft.json", "sos": "17l_sos_premierdraft.json",
           "mkm": "17l_mkm_premierdraft.json", "hob": "17l_hob_premierdraft.json"}


def norm(s):
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def load_db():
    db = {}
    for fn in SETS:
        p = os.path.join(HERE, fn)
        if not os.path.exists(p):
            continue
        for c in json.load(open(p)):
            for key in (c.get("name", ""), c.get("name", "").split(" //")[0]):
                db.setdefault(norm(key), c)
    return db


def load_ratings(setcode="msh"):
    p = os.path.join(HERE, RATINGS.get(setcode, ""))
    if not os.path.exists(p):
        return {}
    return {norm(c["name"]): c for c in json.load(open(p)) if c.get("name")}


def load_pair(setcode, pair):
    p = os.path.join(HERE, f"cache_17l_{setcode}_{pair.upper()}.json")
    if not os.path.exists(p):
        return {}
    raw = json.load(open(p))
    rows = raw if isinstance(raw, list) else raw.get("data", raw.get("cards", []))
    out = {}
    for c in rows if isinstance(rows, list) else []:
        if isinstance(c, dict) and c.get("name"):
            out[norm(c["name"])] = c
    return out


def parse_deck(path):
    """(count, name) до строки Sideboard."""
    out = []
    for line in open(path, encoding="utf-8"):
        s = line.strip()
        if not s or s.lower().startswith("deck") or s.lower().startswith("about"):
            continue
        if s.lower().startswith("sideboard"):
            break
        m = re.match(r"^(\d+)\s+(.+?)(?:\s+\([A-Za-z0-9]+\)\s+\S+)?$", s)
        if m:
            out.append((int(m.group(1)), m.group(2).strip()))
    return out


def face(c, k):
    if "card_faces" in c and not c.get(k):
        return c["card_faces"][0].get(k, "") or ""
    return c.get(k, "") or ""


def oracle(c):
    if "card_faces" in c:
        return " // ".join((f.get("oracle_text") or "") for f in c["card_faces"])
    return c.get("oracle_text") or ""


EVASION_RE = re.compile(r"\bflying\b|\bmenace\b|can't be blocked|\btrample\b|\breach\b", re.I)
HARD_RE = re.compile(r"(destroy|exile) target (creature|permanent|nonland|attacking|blocking)", re.I)
SOFT_RE = re.compile(r"gets -\d|gets \-|deals \d+ damage to target|tap target|doesn't untap|"
                     r"fights|return target .* to (its owner's|their owner's) hand", re.I)


def metrics(path, db, rat, prat=None):
    """Все метрики листа одним словарём. Используется и CLI, и build_audit.py."""
    prat = prat or {}
    entries = parse_deck(path)
    lands = nonlands = fixers = 0
    cre_curve, spell_curve, pips = Counter(), Counter(), Counter()
    cheap_bodies, evasion, hard, soft, topend, missing = [], [], [], [], [], []
    gih_g, gih_p = [], []
    BASICS = {"plains", "island", "swamp", "mountain", "forest"}
    ANYCOLOR = re.compile(r"mana of any (one )?color|create a treasure", re.I)

    for n, name in entries:
        c = db.get(norm(name)) or db.get(norm(name.split(",")[0]))
        if not c:
            missing.append(name)
            continue
        tl = face(c, "type_line")
        if "Land" in tl:
            lands += n
            if norm(name) not in BASICS:
                fixers += n          # нонбейзик = источник фикса (дуал/утилити)
            continue
        for sym in re.findall(r"\{([^}]+)\}", face(c, "mana_cost")):
            for ch in sym.upper().split("/"):
                if ch in "WUBRG":
                    pips[ch] += n
        if ANYCOLOR.search(oracle(c)):
            fixers += n
        nonlands += n
        cmc = int(c.get("cmc") or 0)
        is_cre = "Creature" in tl
        (cre_curve if is_cre else spell_curve)[cmc] += n
        # {X}-костные не считаем двойками: Scryfall берёт X=0 (Ruinous Wrecking Crew {X}{B}{R} → cmc 2)
        if is_cre and cmc <= 2 and "{X}" not in face(c, "mana_cost"):
            cheap_bodies += [name] * n
        if is_cre and EVASION_RE.search(oracle(c) + " " + tl):
            evasion += [name] * n
        ot = oracle(c)
        if HARD_RE.search(ot):
            hard += [name] * n
        elif SOFT_RE.search(ot):
            soft += [name] * n
        if cmc >= 5:
            topend += [f"{name}({cmc})"] * n
        r = rat.get(norm(name)) or rat.get(norm(name.split(",")[0]))
        if r and r.get("ever_drawn_win_rate"):
            gih_g += [round(r["ever_drawn_win_rate"] * 100, 1)] * n
        pr = prat.get(norm(name)) or prat.get(norm(name.split(",")[0]))
        if pr and pr.get("ever_drawn_win_rate"):
            gih_p += [round(pr["ever_drawn_win_rate"] * 100, 1)] * n

    def avg(xs):
        return round(sum(xs) / len(xs), 2) if xs else None

    ncre = sum(cre_curve.values())
    # цвета: считаем ПИПЫ нонлендов. Цвет «настоящий» если пипов ≥3, иначе сплеш.
    real = sorted([c for c, v in pips.items() if v >= 3], key=lambda x: -pips[x])
    splash = sorted([c for c, v in pips.items() if 0 < v < 3], key=lambda x: -pips[x])
    return dict(
        name=os.path.basename(path), lands=lands, nonlands=nonlands, creatures=ncre,
        cheap=len(cheap_bodies), cheap_names=cheap_bodies, evasion=len(evasion),
        evasion_names=evasion, hard=len(hard), hard_names=hard, soft=len(soft),
        soft_names=soft, fixers=fixers, colors="".join(real), splash="".join(splash),
        ncolors=len(real) + len(splash), gih=avg(gih_g), gih_pair=avg(gih_p),
        cre_curve=cre_curve, spell_curve=spell_curve, missing=missing,
        c5=sum(v for k, v in list(cre_curve.items()) + list(spell_curve.items()) if k >= 5),
        c6=sum(v for k, v in list(cre_curve.items()) + list(spell_curve.items()) if k >= 6),
    )


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    args = [a for a in sys.argv[1:] if a != "--brief"]
    BRIEF = "--brief" in sys.argv
    path = args[0]
    pair = args[1].upper() if len(args) > 1 else None
    db, rat = load_db(), load_ratings("msh")
    prat = load_pair("msh", pair) if pair else {}
    M = metrics(path, db, rat, prat)
    lands, nonlands, fixers = M["lands"], M["nonlands"], M["fixers"]
    cheap_bodies, evasion = M["cheap_names"], M["evasion_names"]
    hard, soft, missing = M["hard_names"], M["soft_names"], M["missing"]
    cre_curve, spell_curve = M["cre_curve"], M["spell_curve"]
    ncre, real, splash = M["creatures"], M["colors"], M["splash"]

    def avg_of(k):
        return M[k]
    if BRIEF:
        print(f"{M['name']:22} | {lands:2} | {ncre:2} | {M['cheap']:2} | "
              f"{M['evasion']:2} | {M['hard']:2} | {M['c5']:2} | "
              f"{real}{'+' + splash if splash else '':6} | {fixers:2} | {M['gih']}")
        return
    print(f"\n=== {os.path.basename(path)} ===")
    print(f"земель {lands} · нонлендов {nonlands} · всего {lands + nonlands}")
    print(f"существ {ncre} · спеллов {sum(spell_curve.values())}")
    print(f"\nкривая СУЩЕСТВ : " + "  ".join(f"{k}:{cre_curve[k]}" for k in sorted(cre_curve)))
    print(f"кривая СПЕЛЛОВ : " + "  ".join(f"{k}:{spell_curve[k]}" for k in sorted(spell_curve)))
    print(f"\n🔴 СУЩЕСТВ cmc≤2 : {len(cheap_bodies)}   (квота ⚑КРИВАЯ: ≥5)")
    for b in sorted(set(cheap_bodies)):
        print(f"     · {b}" + (f" ×{cheap_bodies.count(b)}" if cheap_bodies.count(b) > 1 else ""))
    print(f"\nломателей стойки (эвейжн/reach) : {len(evasion)}")
    for b in sorted(set(evasion)):
        print(f"     · {b}" + (f" ×{evasion.count(b)}" if evasion.count(b) > 1 else ""))
    print(f"\nбезусловное removal : {len(hard)}   " + (", ".join(sorted(set(hard))) or "—"))
    print(f"условная интеракция : {len(soft)}   " + (", ".join(sorted(set(soft))) or "—"))
    c5 = sum(v for k, v in list(cre_curve.items()) + list(spell_curve.items()) if k >= 5)
    c6 = sum(v for k, v in list(cre_curve.items()) + list(spell_curve.items()) if k >= 6)
    print(f"\nверх кривой : cmc≥5 — {c5} (порог ≤4) · cmc≥6 — {c6} (порог 0)")
    print(f"средний GIH глоб : {M['gih']}")
    if pair:
        print(f"средний GIH {pair}   : {M['gih_pair']}")
    if missing:
        print(f"\n⚠ не найдены в set-файле: {', '.join(missing)}")


if __name__ == "__main__":
    main()
