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
# Оси маршрутов (§ 8.17): эвейжн — только ПЕЧАТНЫЙ (строка со стоимостью активации не считается).
EV_RE = re.compile(r"\bflying\b|\bmenace\b|can't be blocked|\btrample\b", re.I)
ACT_RE = re.compile(r"\{[^}]+\}\s*:")


def sig_of(cnt, cards):
    """Сигнатура {big, evp, cre, cheap, rem} для набора карт {norm-имя: копий}.

    Вынесена из main() на уровень модуля 20.08.2026, чтобы pool_dossier.py и тесты
    звали ТУ ЖЕ функцию, которой посчитаны медианы `routes` в <set>_traps.json —
    копия логики у потребителя не измеряет (JOURNAL § 8.5). Поведение не менялось.
    """
    import deck_profile as _DP
    big = evp = cre = cheap = rem = 0
    for c in cards:
        k = norm(c["name"])
        if k not in cnt:
            continue
        n_ = cnt[k]; tl = face(c, "type_line"); ora = _DP.oracle(c)
        if _DP.HARD_RE.search(ora) or _DP.SOFT_RE.search(ora):
            rem += n_
        if "Creature" not in tl:
            continue
        cre += n_
        if int(c.get("cmc") or 0) <= 2:
            cheap += n_
        pw = c.get("power")
        if pw is None and c.get("card_faces"):
            pw = c["card_faces"][0].get("power")
        try:
            pw = int(pw)
        except (TypeError, ValueError):
            pw = 0
        if pw >= 4:
            big += n_
        if any(EV_RE.search(l) and not ACT_RE.search(l) for l in ora.split("\n")):
            evp += pw * n_
    return dict(big=big, evp=evp, cre=cre, cheap=cheap, rem=rem)


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
    return set(maindeck_counts(text))


def maindeck_counts(text):
    """{имя: число копий} мейна. Нужно для потолка копий (см. блок `played`)."""
    out = {}
    for line in text.splitlines():
        line = line.strip()
        if line == "Sideboard":
            break
        m = re.match(r"^(\d+)\s+(.+?)(?:\s+\([A-Z0-9]+\)\s+\d+)?$", line)
        if m:
            k = norm(m.group(2))
            out[k] = max(out.get(k, 0), int(m.group(1)))
    return out


def main():
    code = (sys.argv[1] if len(sys.argv) > 1 else "hob").lower()
    os.environ["MTGA_SET"] = code
    os.environ.setdefault("MTGA_OFFLINE", "1")
    import build_audit as A
    db, rat = A.load_db(), A.load_ratings(code)
    cards = json.load(open(os.path.join(HERE, f"{code}_set.json"), encoding="utf-8"))

    by_pair = defaultdict(list)
    counts_by_pair = defaultdict(list)      # то же, но с числом копий — для потолка копий
    for f in sorted(glob.glob(os.path.join(HERE, "ref_decks", code, "*.txt"))):
        cnt = maindeck_counts(open(f, encoding="utf-8").read())
        pair = A.deck_colors(f, db)
        by_pair[pair].append(set(cnt))
        counts_by_pair[pair].append(cnt)
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

    # ── ЧАСТОТА КАЖДОЙ КАРТЫ: по сету и по каждой паре ────────────────────────
    # Нужна баннеру ⚑КРИВАЯ: «квоту дешёвых тел закрывает только тело ИЗ ЯДРА ПАРЫ»
    # (hob_insights.md 17.08). Без этой таблицы баннер называл кандидатом любое тело за 2
    # и трижды за драфт eba1b036 указал на Old Thrush — 0 из 14 UR-листов победителей.
    # pair_bad для этого не годится: там только карты выше порога «играется в сете ≥20%»,
    # а тела вроде Old Thrush (8% по сету) в него не попадают вовсе.
    big_pairs = sorted(p for p, d in by_pair.items() if len(d) >= PAIR_MIN_LISTS)
    played_tbl = {}
    for c in cards:
        if "Basic" in face(c, "type_line"):
            continue
        k = norm(c["name"])
        pl = sn = 0
        pairs = {}
        for pair, decks in by_pair.items():
            if not castable(c, pair):
                continue
            hits = sum(1 for d in decks if k in d)
            sn += len(decks)
            pl += hits
            if pair in big_pairs:
                pairs[pair] = round(hits / len(decks), 3)
        if sn:
            # ПОТОЛОК КОПИЙ: максимум, встреченный у победителей, и максимум ВНУТРИ пары.
            # Нужен баннеру ⚑ КОПИИ: за драфт eba1b036 набрано 4 Confusticate при
            # максимуме 3 и 3 Old Thrush / 3 Long-Bodied Grey Dog при максимуме 2,
            # и ни один прибор этого не назвал в момент пика.
            mx = 0
            mx_pairs = {}
            for pair, decks in counts_by_pair.items():
                if not castable(c, pair):
                    continue
                here = max((d.get(k, 0) for d in decks), default=0)
                mx = max(mx, here)
                if pair in big_pairs and here:
                    mx_pairs[pair] = here
            played_tbl[k] = dict(set=round(pl / sn, 3), n=sn, pairs=pairs,
                                 max=mx, max_pairs=mx_pairs)

    # ── РОЛЬ «ЧЕМ УБИВАЮ»: распределение тел силой ≥4 по парам ───────────────
    # Заведено 20.08.2026 по разбору драфта eba1b036 (UR, 0-3). В обеих доигранных
    # партиях колода нанесла РОВНО НОЛЬ урона, а все восемь осей аудита показывали
    # «в диапазоне»: ни одна не спрашивала, чем колода заканчивает партию. Эвейжн-ось
    # не ловит этого по построению — она считает КАРТЫ, и 1/2-флаер весит в ней
    # столько же, сколько 5/5. Контроль: у той же колоды 2 тела силы ≥4 (8-й перцентиль),
    # у BR-листа того же игрока с результатом 7W-1L — восемь (96-й).
    import statistics as _st
    big_by_pair = {}
    for pair, decks in by_pair.items():
        vals = []
        for cnt in counts_by_pair[pair]:
            tot = 0
            for c in cards:
                k = norm(c["name"])
                if k not in cnt or "Creature" not in face(c, "type_line"):
                    continue
                pw = c.get("power")
                if pw is None and c.get("card_faces"):
                    pw = c["card_faces"][0].get("power")
                try:
                    if int(pw) >= 4:
                        tot += cnt[k]
                except (TypeError, ValueError):
                    pass
            vals.append(tot)
        if vals:
            big_by_pair[pair] = dict(n=len(vals), min=min(vals),
                                     med=round(_st.median(vals)), max=max(vals))
    print("\n⚔ ТЕЛ СИЛОЙ ≥4 ПО ПАРАМ (чем колода заканчивает партию):")
    for pair in sorted(big_by_pair, key=lambda x: -big_by_pair[x]["n"]):
        d = big_by_pair[pair]
        if d["n"] >= PAIR_MIN_LISTS:
            print(f"  {pair:<5} n={d['n']:>3}  мин {d['min']} · медиана {d['med']} · макс {d['max']}")

    # ── МАРШРУТЫ ПОБЕДЫ по парам (заведено 20.08.2026) ───────────────────────
    # Замер: 93.3% трофейных листов вытягивают ХОТЯ БЫ ОДНУ ось победы до медианы
    # своей популяции; листов «ни одной оси» всего 20 из 298 (6.7%). Проигравшая
    # колода драфта eba1b036 (0-3) была ниже медианы по ВСЕМ четырём — мягкая
    # середина как измеримое состояние, а не как метафора.
    routes = {}
    for pair, cnts in counts_by_pair.items():
        if len(cnts) < PAIR_MIN_LISTS: continue
        sigs = [sig_of(c, cards) for c in cnts]
        routes[pair] = {k: round(_st.median([x[k] for x in sigs]))
                        for k in ("big", "evp", "cre", "cheap", "rem")}
        routes[pair]["n"] = len(sigs)
    print("\n🏁 МАРШРУТЫ ПОБЕДЫ — медианы по парам (ось на медиане = маршрут открыт):")
    print(f"  {'пара':<6}{'n':>4}  {'тел≥4':>6} {'воздух':>7} {'существ':>8} {'дешёвых':>8} {'ответов':>8}")
    for pair in sorted(routes, key=lambda x: -routes[x]["n"]):
        r = routes[pair]
        print(f"  {pair:<6}{r['n']:>4}  {r['big']:>6} {r['evp']:>7} {r['cre']:>8} "
              f"{r['cheap']:>8} {r['rem']:>8}")

    if "--write" in sys.argv:
        out = dict(
            big_bodies=big_by_pair,
            routes=routes,
            traps=[dict(name=r["name"], key=r["key"], alsa=r["alsa"], rar=r["rar"],
                        played=r["played"], seen=r["seen"], rate=round(r["rate"], 3))
                   for r in traps],
            pair_bad={k: v for k, v in pair_bad.items()},
            played=played_tbl,
            meta=dict(lists=total, alsa_early=ALSA_EARLY, trap_fraction=TRAP_FRACTION,
                      pair_min_lists=PAIR_MIN_LISTS, big_pairs=big_pairs,
                      pair_lists={p: len(d) for p, d in sorted(by_pair.items())},
                      rarity_median={k: round(v, 3) for k, v in med.items()}),
        )
        p = os.path.join(HERE, f"{code}_traps.json")
        json.dump(out, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(f"\n→ записано {p}")


if __name__ == "__main__":
    main()
