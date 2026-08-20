#!/usr/bin/env python3
"""
ЛИНТЕР КОЛОДЫ — «мёртвые тексты»: у каждой карты с условием должно быть то, что её включает.

    python3 deck_lint.py <deck.txt> [--set hob]

ЗАЧЕМ (§ 8.24, идея пользователя «тулы, которые быстро работают»). Класс ошибок
«условие карты не включается ЭТИМ листом» ловился то глазами, то случайно:
Thranduil при 2 эльфах (§ 4.8), «value-движок» у защитной саги (§ 8.16),
Lake-town W/U в BG-колоде (§ 8.22 — поймал только sonnet/high-судья, читая текст).
Линтер делает это скриптом за секунду. ДИАГНОСТИКА, не оценка: печатает
предупреждения с числами, тир не считает, exit всегда 0 (§ 8.4: не плодить оси).

Проверки (по оракл-текстам мейна, регексы сет-агностичные):
  A. условная сила — «you control a creature with power N or greater» → сколько тел ≥N;
  B. трайбал — «other <Type>s you control get» / «control two or more other <Type>s» /
     «Affinity for <Type>» → сколько существ этого типа (кроме самой карты);
  C. сак-кост — «sacrifice a/an … creature» как цена → сколько дешёвого фодера
     (существа cmc≤2 + тела с «when this creature dies»-выплатой);
  D. земля не цветов колоды — produced_mana ∩ цвета колоды = ∅ (кейс Lake-town);
  E. эквип-ограничение — «only … to a <Type>» → сколько носителей.
"""
import json
import os
import re
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_audit as A          # noqa: E402
import deck_profile as DP        # noqa: E402
import find_traps as FT          # noqa: E402

POWER_RE = re.compile(r"you control a creature with power (\d+) or greater", re.I)
TRIBAL_RE = re.compile(r"other (\w+) you control get", re.I)
TWO_OTHER_RE = re.compile(r"control two or more other (\w+)\b", re.I)
# «another <Type>» — единичное условие (Thranduil's Company: additional land while you
# control another Elf). Пропуск пойман 20.08.2026 на трофейном листе блоггера (§ 8.28).
ANOTHER_RE = re.compile(r"control another (\w+)\b", re.I)
AFFINITY_RE = re.compile(r"affinity for (\w+)\b", re.I)


def singular(w):
    """Wolves→Wolf, Elves→Elf, Goblins→Goblin, Armies→Army."""
    if w.lower().endswith("ves"):
        return w[:-3] + "f"
    if w.lower().endswith("ies"):
        return w[:-3] + "y"
    if w.lower().endswith("s"):
        return w[:-1]
    return w
SAC_COST_RE = re.compile(r"(additional cost[^.]*sacrifice a|sacrifice (a|an|another) "
                         r"(creature|artifact or creature))", re.I)
DIES_PAY_RE = re.compile(r"when this creature dies", re.I)
EQUIP_ONLY_RE = re.compile(r"only (?:to|onto) an? (\w+)", re.I)
BASICS = {"plains", "island", "swamp", "mountain", "forest"}


def lint(path, setcode=None):
    setcode, _ = A.detect_set(path, path, setcode)
    db = A.load_db()
    md, _sb = A.split_deck(path)
    cards = []                     # (n, name, cardobj)
    for n, name in md:
        c = db.get(A.norm(name)) or db.get(A.norm(name.split(",")[0]))
        if c is not None:
            cards.append((n, name, c))

    def subtype_count(sub, exclude_key):
        tot, names = 0, []
        for n, name, c in cards:
            tl = FT.face(c, "type_line")
            if "Creature" in tl and sub.lower() in tl.lower() and FT.norm(name) != exclude_key:
                tot += n
                names.append(f"{name}×{n}" if n > 1 else name)
        return tot, names

    def bodies_ge(x):
        tot, names = 0, []
        for n, name, c in cards:
            if "Creature" not in FT.face(c, "type_line"):
                continue
            pw = c.get("power")
            if pw is None and c.get("card_faces"):
                pw = c["card_faces"][0].get("power")
            try:
                if int(pw) >= x:
                    tot += n
                    names.append(f"{name}×{n}" if n > 1 else name)
            except (TypeError, ValueError):
                pass
        return tot, names

    deck_colors = set(A.deck_colors(path, db))
    warns = []
    for n, name, c in cards:
        ora = DP.oracle(c)
        tl = FT.face(c, "type_line")
        k = FT.norm(name)

        m = POWER_RE.search(ora)
        if m:
            need = int(m.group(1))
            tot, names = bodies_ge(need)
            own = "Creature" in tl
            eff = tot - (n if own and (c.get("power") is not None
                                       and str(c.get("power")).isdigit()
                                       and int(c["power"]) >= need) else 0)
            if eff <= 2:
                warns.append(f"{name}: условие «сила {need}+» — включателей всего {eff} "
                             f"({', '.join(names) or 'нет'})")

        for rex, what in ((TRIBAL_RE, "лорд"), (TWO_OTHER_RE, "условие"),
                          (ANOTHER_RE, "условие-another"), (AFFINITY_RE, "affinity")):
            m = rex.search(ora)
            if m:
                sub = singular(m.group(1))
                tot, names = subtype_count(sub, k)
                floor = 2 if rex is TWO_OTHER_RE else (1 if rex is ANOTHER_RE else 3)
                if tot < floor:
                    warns.append(f"{name}: {what} «{sub}» — таких существ в мейне {tot} "
                                 f"({', '.join(names) or 'нет'})")

        if SAC_COST_RE.search(ora):
            fodder, names = 0, []
            for n2, nm2, c2 in cards:
                tl2 = FT.face(c2, "type_line")
                if "Creature" not in tl2 or FT.norm(nm2) == k:
                    continue
                cheap = int(c2.get("cmc") or 9) <= 2
                pays = bool(DIES_PAY_RE.search(DP.oracle(c2)))
                if cheap or pays:
                    fodder += n2
                    if pays:
                        names.append(nm2 + "†")
            if fodder <= 3:
                warns.append(f"{name}: сак-кост — профитного/дешёвого фодера {fodder} "
                             f"(† = платит при смерти)")

        if "Land" in tl and k not in BASICS:
            pm = set(c.get("produced_mana") or [])
            if pm and deck_colors and not (pm & deck_colors) and len(pm) < 5:
                warns.append(f"{name}: земля даёт {'/'.join(sorted(pm))} — "
                             f"ни одного цвета колоды ({''.join(sorted(deck_colors))})")

        m = EQUIP_ONLY_RE.search(ora)
        if m and "Equipment" in tl:
            sub = singular(m.group(1))
            tot, names = subtype_count(sub, k)
            if tot <= 2:
                warns.append(f"{name}: цепляется только к «{sub}» — носителей {tot} "
                             f"({', '.join(names) or 'нет'})")
    return warns


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    setcode = None
    if "--set" in sys.argv:
        setcode = sys.argv[sys.argv.index("--set") + 1]
        args = [a for a in args if a != setcode]
    if not args:
        print(__doc__)
        sys.exit(1)
    warns = lint(args[0], setcode)
    print(f"=== ЛИНТ: {os.path.basename(args[0])} ===")
    if not warns:
        print("  ✅ мёртвых текстов не найдено")
    for w in warns:
        print(f"  ⚠ {w}")


if __name__ == "__main__":
    main()
