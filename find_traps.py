#!/usr/bin/env python3
"""Ловушки сета: карту берут рано, а победители её не играют.

    python3 find_traps.py hob            # показать
    python3 find_traps.py hob --write    # записать <set>_traps.json для draft_live

ЗАЧЕМ. GIH говорит, насколько карта выигрывает, ALSA — насколько рано её берут. Ни то ни
другое не говорит, ДОШЛА ЛИ она до мейна выигравшей колоды. Расхождение «берут третьим
пиком — не стоит ни в одной трофейной колоде» ловится только третьим источником: составом
298 листов 7-1/7-2.

Найдено 17.08.2026 после того, как замер частоты карт (`card_leaks.py`) показал
`Bard, King of Dale` в 40% наших WU-сборок и в НУЛЕ из 298 трофейных колод при ALSA 2.7.

ДВА РАЗНЫХ ЯВЛЕНИЯ, И ИХ НЕЛЬЗЯ ПУТАТЬ (я спутал, поймано пересчётом):
  · ЛОВУШКА СЕТА — карта не играется НИГДЕ. Лечится знанием о карте.
  · НЕ В ЭТОЙ ПАРЕ — карта играется в сете, но не в текущей паре (например гибрид {G/U},
    кастуемый чистой синей, чей текст про Эльфов в WU мёртв). Лечится знанием о паре.

ПОПРАВКА НА РЕДКОСТЬ ОБЯЗАТЕЛЬНА. Рара по определению попадает в меньшее число колод: их
медиана присутствия 8% против 30% у обычных. Без нормировки в «ловушки» уехали бы все рары
подряд. Порог — доля НИЖЕ четверти медианы своей редкости.
"""
import glob, json, os, re, statistics, sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

ALSA_EARLY = 4.5        # «берут рано» — в среднем виден к 4-5 пику
TRAP_FRACTION = 0.25    # доля от медианы своей редкости, ниже которой карта считается ловушкой
MIN_SEEN = 40           # меньше — не о чем говорить
PAIR_MIN_LISTS = 12     # пары с меньшим числом листов не судим
PAIR_SET_RATE = 0.20    # «в сете играется» для парного среза
PAIR_HERE_RATE = 0.15   # «а в этой паре почти нет»

SYM = re.compile(r"\{([^}]+)\}")


def norm(s):
    return re.sub(r"[^a-z0-9]", "", re.sub(r"\s*//.*$", "", (s or "").strip()).lower())


def face(c, k):
    if c.get("card_faces") and not c.get(k):
        return c["card_faces"][0].get(k, "") or ""
    return c.get(k, "") or ""


def castable(c, pair):
    """Каждый цветной пип покрыт парой; гибрид — достаточно одной половины."""
    for s in SYM.findall(face(c, "mana_cost") or ""):
        p = [x for x in s.upper().split("/") if x in "WUBRG"]
        if p and not (set(p) & set(pair)):
            return False
    return True


def maindeck(text):
    out = set()
    for line in text.splitlines():
        line = line.strip()
        if line == "Sideboard":
            break
        m = re.match(r"^(\d+)\s+(.+?)(?:\s+\([A-Z0-9]+\)\s+\d+)?$", line)
        if m:
            out.add(norm(m.group(2)))
    return out


def main():
    code = (sys.argv[1] if len(sys.argv) > 1 else "hob").lower()
    os.environ["MTGA_SET"] = code
    os.environ.setdefault("MTGA_OFFLINE", "1")
    import build_audit as A
    db, rat = A.load_db(), A.load_ratings(code)
    cards = json.load(open(os.path.join(HERE, f"{code}_set.json"), encoding="utf-8"))

    by_pair = defaultdict(list)
    for f in sorted(glob.glob(os.path.join(HERE, "ref_decks", code, "*.txt"))):
        by_pair[A.deck_colors(f, db)].append(maindeck(open(f, encoding="utf-8").read()))
    total = sum(len(v) for v in by_pair.values())
    if total < 50:
        print(f"трофейных листов всего {total} — мало для этого разбора, нужно ≥50")
        return

    rows = []
    for c in cards:
        if "Basic" in face(c, "type_line"):
            continue
        k = norm(c["name"])
        rar = "rare" if c.get("rarity") in ("rare", "mythic") else c.get("rarity", "?")
        played = seen = 0
        for pair, decks in by_pair.items():
            if not castable(c, pair):
                continue
            seen += len(decks)
            played += sum(1 for d in decks if k in d)
        if seen < MIN_SEEN:
            continue
        r = rat.get(A.norm(c["name"])) or {}
        alsa = r.get("avg_seen")
        rows.append(dict(key=k, name=c["name"].split(" //")[0], rar=rar,
                         rate=played / seen, played=played, seen=seen, alsa=alsa))

    med = {}
    for rar in ("common", "uncommon", "rare"):
        v = [r["rate"] for r in rows if r["rar"] == rar]
        if v:
            med[rar] = statistics.median(v)

    print("=" * 92)
    print(f"ЛОВУШКИ СЕТА {code.upper()} · {total} трофейных листов")
    print("=" * 92)
    print("медиана присутствия по редкости: "
          + " · ".join(f"{k} {100*v:.0f}%" for k, v in med.items()))

    traps = [r for r in rows
             if r["alsa"] and r["alsa"] <= ALSA_EARLY
             and r["rar"] in med and r["rate"] < med[r["rar"]] * TRAP_FRACTION]
    traps.sort(key=lambda r: r["alsa"])
    print(f"\n⚠ БЕРУТ РАНО (ALSA ≤ {ALSA_EARLY}), ПОБЕДИТЕЛИ НЕ ИГРАЮТ:")
    print(f"{'карта':<30} {'ред.':<9} {'ALSA':>5} {'в трофейных':>16} {'медиана ред.':>13}")
    print("-" * 78)
    for r in traps:
        print(f"{r['name'][:29]:<30} {r['rar']:<9} {r['alsa']:>5.1f} "
              f"{r['played']:>4}/{r['seen']:<5} ({100*r['rate']:>3.0f}%) {100*med[r['rar']]:>11.0f}%")
    print(f"  итого {len(traps)} из {len(rows)} карт с данными")

    # ── парный срез: играется в сете, но не в этой паре ──
    pair_bad = defaultdict(list)
    idx = {r["key"]: r for r in rows}
    for pair, decks in sorted(by_pair.items()):
        if len(decks) < PAIR_MIN_LISTS:
            continue
        for c in cards:
            k = norm(c["name"])
            r = idx.get(k)
            if not r or not castable(c, pair) or r["rate"] < PAIR_SET_RATE:
                continue
            here = sum(1 for d in decks if k in d) / len(decks)
            if here <= PAIR_HERE_RATE:
                pair_bad[pair].append(dict(name=r["name"], key=k, here=round(here, 3),
                                           set_rate=round(r["rate"], 3), n=len(decks)))
    print(f"\n⚠ ИГРАЕТСЯ В СЕТЕ (≥{100*PAIR_SET_RATE:.0f}%), НО НЕ В ЭТОЙ ПАРЕ "
          f"(≤{100*PAIR_HERE_RATE:.0f}%):")
    for pair in sorted(pair_bad):
        items = sorted(pair_bad[pair], key=lambda x: -x["set_rate"])[:6]
        print(f"  {pair:<5} (n={items[0]['n']:>3}) " +
              " · ".join(f"{x['name'][:22]} {100*x['here']:.0f}%/{100*x['set_rate']:.0f}%"
                         for x in items))
    if not pair_bad:
        print("  (ничего выше порога)")

    if "--write" in sys.argv:
        out = dict(
            traps=[dict(name=r["name"], key=r["key"], alsa=r["alsa"], rar=r["rar"],
                        played=r["played"], seen=r["seen"], rate=round(r["rate"], 3))
                   for r in traps],
            pair_bad={k: v for k, v in pair_bad.items()},
            meta=dict(lists=total, alsa_early=ALSA_EARLY, trap_fraction=TRAP_FRACTION,
                      rarity_median={k: round(v, 3) for k, v in med.items()}),
        )
        p = os.path.join(HERE, f"{code}_traps.json")
        json.dump(out, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(f"\n→ записано {p}")


if __name__ == "__main__":
    main()
