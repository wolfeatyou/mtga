#!/usr/bin/env python3
"""CLOCK против исхода: различает ли скорость колоды трофей (7 побед) от провала (≤1).

    python3 clock_vs_outcome.py msh [--sample 1200] [--sims 500]

ЗАЧЕМ (§ 8.24). clock_sim (§ 8.23) различает кандидатов одного пула — но даёт ли он
СИГНАЛ ИСХОДА? Все 7 осей рубрикатора на этой же контрольной группе дали |d| ≤ 0.11
(§ 8.6), связки −0.030 AUC (§ 8.7). Методика та же: трофей vs провал, Cohen's d,
плюс частичный d после вычета качества карт (среднего GIH колоды) — § 8.8 ①.

ПРИБОР-ПРОВЕРКА ВСТРОЕНА: сэмпл обязан воспроизводить известный d по среднему GIH
(эталон § 8.6: +0.67). Не воспроизвёл — замеру не верить, чинить сэмплер.

Требует games/<set>_decks.json.gz (fetch_17l_games.py). Готов к HOB по § 9.
"""
import gzip
import json
import os
import random
import statistics as st
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_audit as A          # noqa: E402
import draft_goldfish as G       # noqa: E402

CAP = 15                          # 99 («не убил») капится сюда для среднего


def cohen_d(a, b):
    na, nb = len(a), len(b)
    va, vb = st.pvariance(a), st.pvariance(b)
    sp = ((na * va + nb * vb) / (na + nb)) ** 0.5
    return (st.mean(a) - st.mean(b)) / sp if sp else 0.0


def residuals(y, x):
    """Остатки линейной регрессии y~x (для частичного d после вычета GIH)."""
    mx, my = st.mean(x), st.mean(y)
    sxx = sum((xi - mx) ** 2 for xi in x)
    b = sum((xi - mx) * (yi - my) for xi, yi in zip(x, y)) / sxx if sxx else 0.0
    return [yi - (my + b * (xi - mx)) for xi, yi in zip(x, y)]


def main():
    code = next((a for a in sys.argv[1:] if not a.startswith("--")), "msh")
    getv = lambda k, d: int(sys.argv[sys.argv.index(k) + 1]) if k in sys.argv else d
    SAMPLE, SIMS = getv("--sample", 1200), getv("--sims", 500)

    with gzip.open(os.path.join(HERE, "games", f"{code}_decks.json.gz"), "rt") as f:
        data = json.load(f)
    decks = data["decks"]
    trophy = [r for r in decks if r["w"] == 7]
    fail = [r for r in decks if r["w"] <= 1 and r["l"] == 3]
    random.seed(42)
    trophy = random.sample(trophy, min(SAMPLE, len(trophy)))
    fail = random.sample(fail, min(SAMPLE, len(fail)))
    print(f"{code.upper()}: трофеев {len(trophy)} · провалов {len(fail)} · "
          f"{SIMS} игр/колоду (seed 42)")

    db = G.load_db()
    rat = A.load_ratings(code)

    def measure(rows, tag):
        out, skipped = [], 0
        for i, r in enumerate(rows):
            dl = list(r["cards"].items())
            deck, _missing = G.build_deck([(n, nm) for nm, n in dl], db)
            lands = sum(1 for c in deck if c["land"])
            if len(deck) < 36 or lands < 12:
                skipped += 1
                continue
            gihs = []
            for nm, n in dl:
                rr = A.rating_of(rat, nm)
                if rr and rr.get("ever_drawn_win_rate"):
                    gihs += [rr["ever_drawn_win_rate"] * 100] * n
            ko, kw = G.clock_sim(deck, SIMS)
            out.append(dict(gih=st.mean(gihs) if gihs else None,
                            open=st.mean([min(x, CAP) for x in ko]),
                            wall=st.mean([min(x, CAP) for x in kw])))
            if (i + 1) % 300 == 0:
                print(f"  {tag}: …{i + 1}/{len(rows)}")
        return [r for r in out if r["gih"] is not None], skipped

    T, st1 = measure(trophy, "трофеи")
    F, st2 = measure(fail, "провалы")
    print(f"измерено: {len(T)} / {len(F)} (пропущено {st1}/{st2} — не распарсились)")

    print(f"\n{'метрика':<26}{'трофей':>9}{'провал':>9}{'d':>8}")
    d_gih = cohen_d([r["gih"] for r in T], [r["gih"] for r in F])
    print(f"{'средний GIH (прибор-чек)':<26}{st.mean([r['gih'] for r in T]):>9.2f}"
          f"{st.mean([r['gih'] for r in F]):>9.2f}{d_gih:>+8.2f}   (эталон § 8.6: +0.67)")
    for key, lab in (("open", "clock: пустая доска"), ("wall", "clock: через 2 блокеров")):
        d = cohen_d([r[key] for r in T], [r[key] for r in F])
        print(f"{lab:<26}{st.mean([r[key] for r in T]):>9.2f}"
              f"{st.mean([r[key] for r in F]):>9.2f}{d:>+8.2f}")
    # частичный d: clock после вычета качества карт (методика § 8.8 ①)
    allr = T + F
    for key, lab in (("open", "…после вычета GIH"), ("wall", "…после вычета GIH (wall)")):
        res = residuals([r[key] for r in allr], [r["gih"] for r in allr])
        d = cohen_d(res[:len(T)], res[len(T):])
        print(f"{lab:<26}{'':>18}{d:>+8.2f}")
    print("\nЗнак: clock — это ХОД убийства, меньше = быстрее; отрицательный d = трофеи быстрее.")


if __name__ == "__main__":
    main()
