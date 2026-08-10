#!/usr/bin/env python3
"""
Анализ СРЕЗА: что попало в мейн, а что в сайд — по референс-колодам в ref_decks/.

Зачем: в драфте сайдборд = остаток пула, то есть протокол решений «что я НЕ играю».
Карта на цвете, оставленная в сайде, — это осознанный срез, и по нему видно, что
сильные драфтеры ценят иначе, чем глобальный GIH.

Считает:
  · доля сайда на цвете (насколько глубоким был пул / насколько реальны были решения)
  · карты НА ЦВЕТЕ, срезанные в сайд, отсортированные по GIH — кандидаты в «переоценённые»
  · карты в мейне с низким GIH — кандидаты в «недооценённые»
  · агрегат по всем колодам: mained/(mained+sided) для каждой карты, когда она КАСТУЕМА

Usage: python3 cut_analysis.py [ref_decks]
"""
import json, os, re, sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))


def norm(s):
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def load_db():
    db = {}
    for c in json.load(open(os.path.join(HERE, "msh_set.json"))):
        for k in (c.get("name", ""), c.get("name", "").split(" //")[0]):
            db.setdefault(norm(k), c)
    return db


def load_rat():
    out = {}
    for c in json.load(open(os.path.join(HERE, "17l_msh_premierdraft.json"))):
        if c.get("name") and c.get("ever_drawn_win_rate"):
            out[norm(c["name"])] = round(c["ever_drawn_win_rate"] * 100, 1)
    return out


def face(c, k):
    if "card_faces" in c and not c.get(k):
        return c["card_faces"][0].get(k, "") or ""
    return c.get(k, "") or ""


def parse(path):
    """(maindeck, sideboard) как списки (n, name)."""
    main, side, cur = [], [], None
    for line in open(path, encoding="utf-8"):
        s = line.strip()
        if not s:
            continue
        low = s.lower()
        if low.startswith("deck"):
            cur = main; continue
        if low.startswith("sideboard"):
            cur = side; continue
        if cur is None:
            cur = main
        m = re.match(r"^(\d+)\s+(.+?)(?:\s+\([A-Za-z0-9]+\)\s+\S+)?$", s)
        if m:
            cur.append((int(m.group(1)), m.group(2).strip()))
    return main, side


def colors_of(c):
    cols = c.get("colors")
    if cols is None and "card_faces" in c:
        cols = c["card_faces"][0].get("colors")
    return set(cols or [])


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "ref_decks")
    db, rat = load_db(), load_rat()
    # агрегат: имя -> [раз в мейне, раз в сайде НА ЦВЕТЕ]
    agg = defaultdict(lambda: [0, 0])
    per_deck = []

    for fn in sorted(os.listdir(root)):
        if not fn.endswith(".txt"):
            continue
        md, sb = parse(os.path.join(root, fn))
        pips = Counter()
        for n, name in md:
            c = db.get(norm(name)) or db.get(norm(name.split(",")[0]))
            if not c or "Land" in face(c, "type_line"):
                continue
            for sym in re.findall(r"\{([^}]+)\}", face(c, "mana_cost")):
                for ch in sym.upper().split("/"):
                    if ch in "WUBRG":
                        pips[ch] += n
        mains = {c for c, v in pips.items() if v >= 3}

        for n, name in md:
            c = db.get(norm(name)) or db.get(norm(name.split(",")[0]))
            if not c or "Land" in face(c, "type_line"):
                continue
            if not (colors_of(c) - mains):
                agg[c["name"]][0] += 1

        oncolor_cuts = []
        off = 0
        for n, name in sb:
            c = db.get(norm(name)) or db.get(norm(name.split(",")[0]))
            if not c or "Land" in face(c, "type_line"):
                continue
            if colors_of(c) - mains:
                off += n
                continue
            agg[c["name"]][1] += n
            g = rat.get(norm(c["name"]), rat.get(norm(c["name"].split(",")[0])))
            oncolor_cuts.append((g if g is not None else 0, c["name"], n))
        oncolor_cuts.sort(reverse=True)
        per_deck.append((fn, "".join(sorted(mains)), oncolor_cuts, off))

    print("=" * 78)
    print("СРЕЗЫ НА ЦВЕТЕ — что игрок МОГ сыграть, но не стал (по колодам)")
    print("=" * 78)
    for fn, mains, cuts, off in per_deck:
        top = [f"{nm} {g}" for g, nm, n in cuts[:5] if g >= 55]
        print(f"\n{fn:22} [{mains}]  вне цвета в сайде: {off}")
        if top:
            print("   срезано НА ЦВЕТЕ с GIH≥55: " + " · ".join(top))
        else:
            print("   срезов на цвете с GIH≥55 нет (пул был узкий — реального выбора не было)")

    print("\n" + "=" * 78)
    print("АГРЕГАТ: карта была КАСТУЕМА в N колодах — как часто её реально играли")
    print("=" * 78)
    rows = []
    for nm, (m, s) in agg.items():
        tot = m + s
        if tot >= 3:
            g = rat.get(norm(nm), rat.get(norm(nm.split(",")[0])))
            rows.append((m / tot, tot, m, s, g if g is not None else 0, nm))
    rows.sort()
    print("\n--- НИЗКИЙ maindeck-rate при ПРИЛИЧНОМ GIH = ПЕРЕОЦЕНЕНА рейтингом ---")
    for r, tot, m, s, g, nm in rows:
        if r <= 0.5 and g >= 55:
            print(f"  {nm:38} GIH {g:5}  мейн {m}/{tot}  ({r:.0%})")
    print("\n--- ВЫСОКИЙ maindeck-rate при НИЗКОМ GIH = НЕДООЦЕНЕНА рейтингом ---")
    for r, tot, m, s, g, nm in sorted(rows, reverse=True):
        if r >= 0.99 and 0 < g <= 56:
            print(f"  {nm:38} GIH {g:5}  мейн {m}/{tot}  (100%)")


if __name__ == "__main__":
    main()
