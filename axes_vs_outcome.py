#!/usr/bin/env python3
"""Отличает ли что-нибудь трофейную колоду от провальной — сверх качества карт.

Продолжение JOURNAL § 8.6/8.7, оформлено скриптом 18.08.2026 (тот замер § 8.7 был
одноразовым и не сохранился — это была ошибка провенанса). Требует game-датасет:
`python3 fetch_17l_games.py <set>` → `games/<set>_decks.json.gz`.

    python3 axes_vs_outcome.py msh          # весь отчёт
    python3 axes_vs_outcome.py hob          # когда 17Lands выложит HOB (§ 9)

Четыре замера:
  A. Оси рубрикатора УСЛОВНО ВНУТРИ ПАРЫ (трофей w=7 vs провал w<=1, та же пара).
  A2. Частичный d осей hard/fixers/evasion после вычета качества карт колоды —
      дважды: по GIH (точный, но цикличен с исходами) и по ALSA (грубее, но
      независим от исходов). Правда о собственном вкладе оси — между ними.
  B. Оси маржинально в верхних рангах (diamond+mythic).
  C. Остатки по картам: веса аддитивной ridge-модели (λ по 5-fold CV) против GIH,
     сплит-половинная устойчивость, агрегат по цветам.

Оси считаются БОЕВЫМ deck_profile.metrics — подменяется только источник строк.
Единица анализа — КОЛОДА (не партия): победитель играет 7-9 партий, провал 3.
"""
import argparse
import gzip
import json
import os
import sys
from collections import Counter, defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import deck_profile as DP

AXES = ["cheap", "evasion", "hard", "c5", "creatures", "fixers", "ncolors"]
BASICS = {"Plains", "Island", "Swamp", "Mountain", "Forest"}

_cur = []
DP.parse_deck = lambda path: _cur


def deck_metrics(d, db, rat):
    global _cur
    _cur = [(cnt, name) for name, cnt in d["cards"].items()]
    return DP.metrics("_", db, rat)


def rating_of(rat, name):
    return rat.get(DP.norm(name)) or rat.get(DP.norm(name.split(",")[0]))


def deck_alsa(d, rat):
    xs = []
    for name, cnt in d["cards"].items():
        r = rating_of(rat, name)
        if r and r.get("avg_seen"):
            xs += [r["avg_seen"]] * cnt
    return sum(xs) / len(xs) if xs else None


def cohen_d(a, b):
    a, b = a[~np.isnan(a)], b[~np.isnan(b)]
    sp = np.sqrt(((len(a) - 1) * a.std(ddof=1) ** 2 + (len(b) - 1) * b.std(ddof=1) ** 2)
                 / (len(a) + len(b) - 2))
    return (a.mean() - b.mean()) / sp if sp else 0.0


def resid_on(x, q):
    A = np.vstack([q, np.ones(len(q))]).T
    coef, *_ = np.linalg.lstsq(A, x, rcond=None)
    return x - A @ coef


def auc(y_true, score):
    order = np.argsort(score)
    ranks = np.empty(len(score))
    ranks[order] = np.arange(1, len(score) + 1)
    n1 = y_true.sum()
    n0 = len(y_true) - n1
    return (ranks[y_true == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("set")
    a = ap.parse_args()

    path = os.path.join(HERE, "games", f"{a.set.lower()}_decks.json.gz")
    if not os.path.exists(path):
        print(f"❌ нет {path} — сначала `python3 fetch_17l_games.py {a.set}`")
        return 1
    raw = json.load(gzip.open(path, "rt"))
    decks = raw["decks"]
    trophy = [d for d in decks if d["w"] == 7]
    fail = [d for d in decks if d["w"] <= 1 and d["l"] == 3]
    print(f"{a.set.upper()}: колод {len(decks)} · трофей {len(trophy)} · провал {len(fail)}")

    db = DP.load_db()
    rat = DP.load_ratings(a.set.lower())
    if not rat:
        print("❌ нет файла рейтингов 17l для этого сета")
        return 1

    # проверка прибора ДО выводов (§ 1 правило 2)
    miss = Counter()
    for d in trophy[:500] + fail[:500]:
        miss.update(deck_metrics(d, db, rat)["missing"])
    print(f"нераспознанных имён на 1000 колод: {sum(miss.values())} "
          f"{miss.most_common(5)}")

    def profile(group):
        rows = []
        for d in group:
            m = deck_metrics(d, db, rat)
            rows.append([m[ax] for ax in AXES] + [m["gih"] or np.nan])
        return np.array(rows, dtype=float)

    # ── A + A2 ──────────────────────────────────────────────────────────
    print("\n══ A. Внутри пары: трофей vs провал (d по осям; hard|GIH и hard|ALSA) ══")
    tro_by, fail_by = defaultdict(list), defaultdict(list)
    for d in trophy:
        tro_by[d["colors"]].append(d)
    for d in fail:
        fail_by[d["colors"]].append(d)
    pairs = sorted((p for p in tro_by
                    if len(tro_by[p]) >= 100 and len(fail_by.get(p, [])) >= 100),
                   key=lambda p: -len(tro_by[p]))
    print("  " + " | ".join(f"{h:>9}" for h in
                            ["пара", "nT"] + AXES + ["gih", "hard|GIH", "hard|ALSA"]))
    tot = 0
    acc = defaultdict(float)
    for p in pairs:
        A, B = profile(tro_by[p]), profile(fail_by[p])
        nT = len(A)
        ds = [cohen_d(A[:, i], B[:, i]) for i in range(len(AXES) + 1)]
        # частичные d для hard
        rows = []
        for d in tro_by[p] + fail_by[p]:
            m = deck_metrics(d, db, rat)
            al = deck_alsa(d, rat)
            if m["gih"] is None or al is None:
                continue
            rows.append((m["gih"], al, m["hard"], 1.0 if d["w"] == 7 else 0.0))
        arr = np.array(rows)
        g, al, h, lab = arr[:, 0], arr[:, 1], arr[:, 2], arr[:, 3]
        rg, ra = resid_on(h, g), resid_on(h, al)
        d_hg = cohen_d(rg[lab == 1], rg[lab == 0])
        d_ha = cohen_d(ra[lab == 1], ra[lab == 0])
        for i, name in enumerate(AXES + ["gih"]):
            acc[name] += ds[i] * nT
        acc["hard|GIH"] += d_hg * nT
        acc["hard|ALSA"] += d_ha * nT
        tot += nT
        print("  " + " | ".join([f"{p:>9}", f"{nT:>9}"] +
                                [f"{v:>+9.2f}" for v in ds + [d_hg, d_ha]]))
    print("  взвешенно (вес = nT): " +
          " · ".join(f"{k} {acc[k]/tot:+.3f}"
                     for k in AXES + ["gih", "hard|GIH", "hard|ALSA"]))

    # ── B ───────────────────────────────────────────────────────────────
    print("\n══ B. Маржинально в diamond+mythic ══")
    TOP = {"diamond", "mythic"}
    At = profile([d for d in trophy if d["rank"] in TOP])
    Bt = profile([d for d in fail if d["rank"] in TOP])
    print(f"  трофей {len(At)} · провал {len(Bt)}")
    for i, name in enumerate(AXES + ["gih"]):
        print(f"    {name:>10}: трофей {np.nanmean(At[:, i]):6.2f} · "
              f"провал {np.nanmean(Bt[:, i]):6.2f} · d = {cohen_d(At[:, i], Bt[:, i]):+.3f}")

    # ── C ───────────────────────────────────────────────────────────────
    print("\n══ C. Ridge-веса против GIH: остатки по картам ══")
    sample = trophy + fail
    y = np.array([1.0] * len(trophy) + [0.0] * len(fail))
    freq = Counter()
    for d in sample:
        for name in d["cards"]:
            if name not in BASICS:
                freq[name] += 1
    cards = sorted(c for c, n in freq.items() if n >= 200)
    cidx = {c: i for i, c in enumerate(cards)}
    X = np.zeros((len(sample), len(cards)))
    for r, d in enumerate(sample):
        for name, cnt in d["cards"].items():
            i = cidx.get(name)
            if i is not None:
                X[r, i] = cnt
    gih = {}
    for c in cards:
        r = rating_of(rat, c)
        if r and r.get("ever_drawn_win_rate"):
            gih[c] = r["ever_drawn_win_rate"] * 100
    have = [c for c in cards if c in gih]
    print(f"  признаков {len(cards)} (>=200 колод), с GIH {len(have)}")

    rng = np.random.default_rng(42)
    perm = rng.permutation(len(sample))
    folds = np.array_split(perm, 5)
    best = None
    for lam in [1, 10, 30, 100, 300, 1000]:
        aucs = []
        for k in range(5):
            te = folds[k]
            tr = np.concatenate([folds[j] for j in range(5) if j != k])
            mu = X[tr].mean(0)
            Xtr = X[tr] - mu
            w = np.linalg.solve(Xtr.T @ Xtr + lam * np.eye(len(cards)),
                                Xtr.T @ (y[tr] - y[tr].mean()))
            aucs.append(auc(y[te], (X[te] - mu) @ w))
        m = np.mean(aucs)
        if best is None or m > best[1]:
            best = (lam, m)
    lam, cv = best
    print(f"  λ={lam}, CV AUC={cv:.4f} (эталон MSH § 8.7: 0.719)")

    def residuals(rows):
        Xs, ys = X[rows], y[rows]
        Xc = Xs - Xs.mean(0)
        w = np.linalg.solve(Xc.T @ Xc + lam * np.eye(len(cards)),
                            Xc.T @ (ys - ys.mean()))
        wv = np.array([w[cidx[c]] for c in have])
        return resid_on(wv, np.array([gih[c] for c in have]))

    full = residuals(np.arange(len(sample)))
    rng2 = np.random.default_rng(7)
    perm2 = rng2.permutation(len(sample))
    r1 = residuals(perm2[: len(perm2) // 2])
    r2 = residuals(perm2[len(perm2) // 2:])
    print(f"  сплит-половины: corr={np.corrcoef(r1, r2)[0, 1]:.3f}")
    t_full = set(np.argsort(full)[::-1][:15])
    b_full = set(np.argsort(full)[:15])
    t_st = t_full & set(np.argsort(r1)[::-1][:15]) & set(np.argsort(r2)[::-1][:15])
    b_st = b_full & set(np.argsort(r1)[:15]) & set(np.argsort(r2)[:15])
    sd = full.std()
    print("  УСТОЙЧИВО недооценены GIH (в топ-15 полного прогона и ОБЕИХ половин):")
    for i in sorted(t_st, key=lambda i: -full[i]):
        print(f"    {full[i]/sd:+5.2f}σ  GIH {gih[have[i]]:5.1f}  n={freq[have[i]]:>5}  {have[i]}")
    print("  УСТОЙЧИВО переоценены:")
    for i in sorted(b_st, key=lambda i: full[i]):
        print(f"    {full[i]/sd:+5.2f}σ  GIH {gih[have[i]]:5.1f}  n={freq[have[i]]:>5}  {have[i]}")

    def color_of(name):
        c = db.get(DP.norm(name)) or db.get(DP.norm(name.split(",")[0]))
        if not c:
            return "?"
        ci = c.get("color_identity") or c.get("colors") or []
        return "".join(sorted(ci)) or "C"

    print("  агрегат по моноцвету карты (средний остаток, σ; полный / половины):")
    for col in "WUBRG":
        idx = [i for i, c in enumerate(have) if color_of(c) == col]
        if not idx:
            continue
        print(f"    {col}: {np.mean(full[idx])/sd:+.2f}σ · "
              f"{np.mean(r1[idx])/sd:+.2f}σ / {np.mean(r2[idx])/sd:+.2f}σ · карт {len(idx)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
