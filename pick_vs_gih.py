#!/usr/bin/env python3
"""
РАСХОЖДЕНИЕ «КАК ПИКАЮТ» vs «КАКОЙ GIH» — две ортогональные оси.

  pick order (untapped.gg, DIAMOND_TO_MYTHIC) = revealed preference сильных драфтеров
  GIH (17Lands)                                = винрейт игр, где карта была в руке

Их расхождение — это ровно тот сигнал, который в § КАЛИБРОВКА выведен из сайдбордов
23 победителей, только измеренный на несравнимо большей выборке и напрямую.

  · GIH высокий, пикают низко  → карта «нигде не плоха», но план ею не строится.
    Мы её переоцениваем, потому что сортируем пак по GIH.
  · GIH низкий, пикают высоко  → пейофф/бомба, чей средний GIH размазан колодами,
    которые её не поддерживают. Мы её систематически пасуем.

Usage: python3 pick_vs_gih.py [N]     N — сколько строк в каждую сторону (по умолч. 20)
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
TIERS = ["S", "A+", "A", "A-", "B+", "B", "B-", "C+", "C", "C-", "D+", "D"]
# ранг тира → числовая шкала 0..1 (S = 1.0)
TIER_VAL = {t: 1.0 - i / (len(TIERS) - 1) for i, t in enumerate(TIERS)}


def norm(s):
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def main():
    topn = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    tiers = json.load(open(os.path.join(HERE, "msh_pick_tiers.json")))
    rat = {}
    for c in json.load(open(os.path.join(HERE, "17l_msh_premierdraft.json"))):
        if c.get("name") and c.get("ever_drawn_win_rate"):
            rat[norm(c["name"])] = c
    # шкала GIH → 0..1 по фактическому диапазону сета
    vals = [c["ever_drawn_win_rate"] for c in rat.values()]
    lo, hi = min(vals), max(vals)

    rows, missing = [], []
    for t in TIERS:
        for name in tiers.get(t, []):
            r = rat.get(norm(name)) or rat.get(norm(name.split(",")[0]))
            if not r:
                missing.append(name)
                continue
            rows.append(dict(name=name, tier=t, gih=round(r["ever_drawn_win_rate"] * 100, 1),
                             alsa=r.get("avg_seen"),
                             iwd=round((r.get("drawn_improvement_win_rate") or 0) * 100, 1)))
    # ОСТАТОК ОТ ТРЕНДА: тир пика и GIH связаны монотонно (см. таблицу внизу), поэтому
    # сравнивать их «в лоб» бессмысленно — так наверх всплывут просто бомбы. Сигнал —
    # насколько карта отклоняется от СРЕДНЕГО GIH СВОЕГО ЖЕ тира.
    for t in TIERS:
        sub = [r for r in rows if r["tier"] == t]
        if not sub:
            continue
        m = sum(r["gih"] for r in sub) / len(sub)
        for r in sub:
            r["delta"] = round(r["gih"] - m, 1)   # + = GIH выше сверстников по тиру

    print(f"\nсопоставлено {len(rows)} карт; без данных 17L: {len(missing)}")
    if missing:
        print("  (" + ", ".join(missing[:8]) + ("…" if len(missing) > 8 else "") + ")")

    # Прямой срез понятнее остатков: берём НИЗКИЕ тиры с высоким GIH и наоборот.
    # (Остаток внутри S-тира не значит «переоценена» — там просто лучшие из лучших.)
    LOW = {"C+", "C", "C-", "D+", "D"}
    HIGH = {"S", "A+", "A", "A-", "B+"}

    def show(title, sel, key, note):
        print("\n" + "=" * 92); print(title); print("=" * 92)
        print(f"{'карта':38} {'тир':>4} {'GIH':>6} {'IWD':>6} {'ALSA':>5}")
        for r in sorted([x for x in rows if x["tier"] in sel], key=key)[:topn]:
            print(f"{r['name'][:38]:38} {r['tier']:>4} {r['gih']:>6} {r['iwd']:>+6} {r['alsa'] or 0:>5.1f}")
        print("  " + note)

    show("🔻 ВЫСОКИЙ GIH, но пикают ПОЗДНО (тир C+ и ниже) — мы их переоцениваем",
         LOW, lambda x: -x["gih"],
         "GIH-сортировка пака поднимет их наверх, сильные драфтеры — пасуют.")
    show("🔺 НИЗКИЙ GIH, но пикают РАНО (тир B+ и выше) — мы их пасуем",
         HIGH, lambda x: x["gih"],
         "Средний GIH размазан колодами без поддержки; в своей колоде карта сильнее числа.")

    # сводка по тирам: средний GIH внутри тира — насколько вообще оси связаны
    print("\n" + "=" * 92)
    print("СРЕДНИЙ GIH ПО ТИРУ ПИКА (если бы оси совпадали, шло бы строго вниз)")
    print("=" * 92)
    for t in TIERS:
        sub = [r["gih"] for r in rows if r["tier"] == t]
        if sub:
            bar = "█" * int((sum(sub) / len(sub) - 48) * 1.6)
            print(f"  {t:>3} n={len(sub):>3}  средний GIH {sum(sub)/len(sub):5.1f}  {bar}")


if __name__ == "__main__":
    main()
