#!/usr/bin/env python3
"""Консенсус-лист пары: что победители этой пары играют ЧАЩЕ ВСЕГО.

    python3 consensus.py hob           # все пары
    python3 consensus.py hob UB        # одну
    python3 consensus.py hob --save    # записать листы в consensus/<set>_<пара>.txt

Метод (внесено 16.08.2026). Карты ранжируются по ЧАСТОТЕ в колодах своей пары, а не по
рейтингу: сначала те, что есть у всех, потом у большинства, потом у одного. Число копий —
медиана среди тех колод, где карта вообще играется (а не среднее по всем: карта в 2 копии
у половины колод должна попасть в лист в 2 копии, а не в 1). Земель — медиана по паре.

**GIH не участвует ни на одном шаге.** Он ось сортировки пака в живом драфте и мерилом
колоды не является: разбор 31 трофейного листа HOB показал, что у победителей средний GIH
НИЖЕ, чем у листов, которые я собирал по нему, а карт «ниже 55» — до двенадцати на колоду.

Чего этот лист НЕ делает: он не «лучшая колода пары», а **модальная** — то, что чаще всего
оказывается в выигравших листах. На парах с 2–3 колодами это ближе к пересказу одной удачной
колоды, чем к консенсусу; скрипт печатает n и предупреждает.
"""
import json, os, re, sys
from collections import Counter, defaultdict
from statistics import median

HERE = os.path.dirname(os.path.abspath(__file__))
BASIC = {"Plains", "Island", "Swamp", "Mountain", "Forest"}
PIP = re.compile(r"\{([WUBRG])(?:/([WUBRG]))?\}")
TARGET = 23           # нонлендов в листе


def load_set(code):
    cards = {}
    for c in json.load(open(os.path.join(HERE, f"{code}_set.json"), encoding="utf-8")):
        cards.setdefault(c["name"].split(" //")[0], c)
    return cards


def face(c, k):
    v = c.get(k)
    if v is None and c.get("card_faces"):
        v = c["card_faces"][0].get(k)
    return v or ""


def parse(path, cards):
    sp, ld = Counter(), Counter()
    for line in open(path, encoding="utf-8"):
        s = line.strip()
        if not s or s.lower() in ("deck", "sideboard"):
            continue
        m = re.match(r"(\d+)\s+(.+?)(?:\s+\([A-Z0-9]{3}\).*)?$", s)
        if not m:
            continue
        q, name = int(m.group(1)), m.group(2).split(" //")[0].strip()
        c = cards.get(name)
        tl = face(c, "type_line") if c else ""
        (ld if name in BASIC or ("Land" in tl and "Creature" not in tl) else sp)[name] += q
    return sp, ld


def pair_of(sp, cards):
    cnt = Counter()
    for name, q in sp.items():
        c = cards.get(name)
        if not c:
            continue
        for a, b in PIP.findall(face(c, "mana_cost")):
            if b:
                cnt[a] += 0.5 * q; cnt[b] += 0.5 * q
            else:
                cnt[a] += q
    if not cnt:
        return "C"
    top = cnt.most_common(2)
    if len(top) < 2 or top[1][1] < top[0][1] * 0.25:
        return top[0][0]
    return "".join(x for x in "WUBRG" if x in (top[0][0], top[1][0]))


def build(pair, decks, cards):
    """-> (спеллы [(qty,name)], земли {name:qty}, диагностика)"""
    seen = Counter()            # в скольких колодах карта есть
    copies = defaultdict(list)  # сколько копий там, где есть
    for d in decks:
        for name, q in d["sp"].items():
            seen[name] += 1
            copies[name].append(q)
    # частота важнее числа копий: карта у всех в 1 копии выше карты у одного в 3
    order = sorted(seen, key=lambda n: (-seen[n], -median(copies[n]), n))
    out, total = [], 0
    for name in order:
        if total >= TARGET:
            break
        q = int(round(median(copies[name])))
        q = min(q, TARGET - total)
        out.append((q, name))
        total += q
    nland = int(round(median([sum(d["ld"].values()) for d in decks])))
    # сплит земель по пипам получившегося листа
    pips = Counter()
    for q, name in out:
        c = cards.get(name)
        if not c:
            continue
        for a, b in PIP.findall(face(c, "mana_cost")):
            if b:
                pips[a] += 0.5 * q; pips[b] += 0.5 * q
            else:
                pips[a] += q
    # нонбейсики, которые пара реально играет (медиана по колодам)
    nb = Counter()
    for d in decks:
        for name, q in d["ld"].items():
            if name not in BASIC:
                nb[name] += q
    nb_keep = {n: max(1, round(v / len(decks))) for n, v in nb.items() if v >= len(decks)}
    nb_total = sum(nb_keep.values())
    basics_left = max(0, nland - nb_total)
    NAME = {"W": "Plains", "U": "Island", "B": "Swamp", "R": "Mountain", "G": "Forest"}
    lands = dict(nb_keep)
    # Базовые земли — ТОЛЬКО в цветах пары. Иначе сплеш одной колоды (WR со сплешем чёрного,
    # UR со сплешем белого) протекает в консенсус и делает мана-базу трёхцветной, хотя
    # сплешевая карта в лист не попала — она по определению редка и отсеялась по частоте.
    own = [c for c in pips if c in pair] or list(pips)
    tot_p = sum(pips[c] for c in own) or 1
    for col in own:
        v = round(basics_left * pips[col] / tot_p)
        if v:
            lands[NAME[col]] = v
    # добиваем/срезаем округление
    while sum(lands.values()) < nland:
        best = max(own, key=lambda c: pips[c])
        lands[NAME[best]] = lands.get(NAME[best], 0) + 1
    while sum(lands.values()) > nland:
        k = max((n for n in lands if n in BASIC), key=lambda n: lands[n])
        lands[k] -= 1
        if not lands[k]:
            del lands[k]
    lands = {k: v for k, v in lands.items() if v > 0}
    return out, lands, seen, copies


def main():
    code = (sys.argv[1] if len(sys.argv) > 1 else "hob").lower()
    only = next((a.upper() for a in sys.argv[2:] if not a.startswith("--")), None)
    save = "--save" in sys.argv
    cards = load_set(code)
    d = os.path.join(HERE, "ref_decks", code)
    decks = []
    for f in sorted(os.listdir(d)):
        if not f.endswith(".txt"):
            continue
        sp, ld = parse(os.path.join(d, f), cards)
        decks.append(dict(file=f, sp=sp, ld=ld, pair=pair_of(sp, cards)))
    bypair = defaultdict(list)
    for x in decks:
        bypair[x["pair"]].append(x)

    outdir = os.path.join(HERE, "consensus")
    if save:
        os.makedirs(outdir, exist_ok=True)
    for pair in sorted(bypair, key=lambda p: (-len(bypair[p]), p)):
        if only and pair != only:
            continue
        grp = bypair[pair]
        spells, lands, seen, copies = build(pair, grp, cards)
        n = len(grp)
        warn = "  ⚠️ n мал — это пересказ одной-двух колод, а не консенсус" if n <= 2 else ""
        print(f"\n{'='*76}\n{pair} — по {n} колодам{warn}\n{'='*76}")
        for q, name in spells:
            mark = "●" * seen[name]
            print(f"  {q}× {name:34s} {mark}")
        print(f"  земли ({sum(lands.values())}): " + " · ".join(f"{v} {k}" for k, v in lands.items()))
        if save:
            p = os.path.join(outdir, f"{code}_{pair}.txt")
            with open(p, "w", encoding="utf-8") as fh:
                fh.write("Deck\n")
                for q, name in spells:
                    fh.write(f"{q} {name}\n")
                for k, v in lands.items():
                    fh.write(f"{v} {k}\n")
            print(f"  → {os.path.relpath(p, HERE)}")


if __name__ == "__main__":
    main()
