#!/usr/bin/env python3
"""Качество ПИКОВ: чем пики трофейщиков отличаются от пиков провальщиков.

Продолжение JOURNAL § 8.7 «мерить решения, а не колоду». Требует лог пиков:
`python3 fetch_17l_picks.py <set>` → `games/<set>_picks.json.gz`.

    python3 pick_quality.py msh --stage 1    # счётчики: жадный GIH, цена упущенного
    python3 pick_quality.py msh --stage 2    # условный логит: веса трофей vs провал

Этап 1 — доля пиков «взял топ пака по GIH» и средняя цена упущенного, срезы:
очевидный/спорный пак (по разрыву GIH топ-1/топ-2), средний скилл-бакет
(user_game_win_rate_bucket 0.50–0.56 — контроль «это скилл, а не трофейность»),
ALSA-вариант (ALSA не цикличен с исходами), разбивка по номерам пиков.

Этап 2 — условный логит (McFadden): P(взять карту | пак) = softmax(w·x) по картам
пака. Признаки: GIH, попадание в цвета пула, редкость, бонус-лист, removal,
существо, cmc. ОБЩИЙ скейлер для обеих групп — иначе веса несравнимы. Одна модель
на фазу (бустер) на группу; устойчивость — сплит-половины по драфтам.
"""
import argparse
import gzip
import json
import os
import re
import sys
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import deck_profile as DP

FEATS = ["GIH", "в_цвет_пула", "редкость", "бонус-лист", "removal", "существо", "cmc"]
F = len(FEATS)


def load(setcode):
    p = os.path.join(HERE, "games", f"{setcode}_picks.json.gz")
    if not os.path.exists(p):
        print(f"❌ нет {p} — сначала `python3 fetch_17l_picks.py {setcode}`")
        sys.exit(1)
    raw = json.load(gzip.open(p, "rt"))
    return raw["cards"], raw["drafts"]


def card_tables(cards, setcode):
    db, rat = DP.load_db(), DP.load_ratings(setcode)
    N = len(cards)
    GIH = np.full(N, np.nan)
    ALSA = np.full(N, np.nan)
    RARE = np.zeros(N)
    BONUS = np.zeros(N)
    REMOV = np.zeros(N)
    CRE = np.zeros(N)
    CMC = np.full(N, 3.0)
    CCOL = [set() for _ in range(N)]
    for i, c in enumerate(cards):
        r = rat.get(DP.norm(c)) or rat.get(DP.norm(c.split(",")[0]))
        d = db.get(DP.norm(c)) or db.get(DP.norm(c.split(",")[0]))
        if r:
            if r.get("ever_drawn_win_rate"):
                GIH[i] = r["ever_drawn_win_rate"] * 100
            if r.get("avg_seen"):
                ALSA[i] = r["avg_seen"]
            RARE[i] = 1.0 if r.get("rarity") in ("rare", "mythic") else 0.0
            CRE[i] = 1.0 if any("Creature" in t for t in (r.get("types") or [])) else 0.0
            for ch in (r.get("color") or ""):
                if ch in "WUBRG":
                    CCOL[i].add(ch)
        if d:
            CMC[i] = float(d.get("cmc") or 3.0)
            ot = DP.oracle(d)
            if DP.HARD_RE.search(ot) or DP.SOFT_RE.search(ot):
                REMOV[i] = 1.0
            if not CCOL[i]:
                for sym in re.findall(r"\{([^}]+)\}", DP.face(d, "mana_cost")):
                    for ch in sym.upper().split("/"):
                        if ch in "WUBRG":
                            CCOL[i].add(ch)
        else:
            BONUS[i] = 1.0
    return dict(GIH=GIH, ALSA=ALSA, RARE=RARE, BONUS=BONUS, REMOV=REMOV,
                CRE=CRE, CMC=CMC, CCOL=CCOL)


def group_of(d):
    if d["w"] == 7:
        return "T"
    if d["w"] <= 1:
        return "F"
    return None


# ── этап 1 ──────────────────────────────────────────────────────────────────
def stage1(cards, drafts, T):
    GIH, ALSA = T["GIH"], T["ALSA"]
    MID = {"0.5", "0.52", "0.54", "0.56"}

    def make():
        return {"greedy": 0, "n": 0, "lost": 0.0}

    by_pick = defaultdict(lambda: {"T": make(), "F": make()})
    slices = {k: {"T": make(), "F": make()} for k in
              ("все", "очевидный(gap>=3)", "спорный(gap<=1)", "все|midskill",
               "спорный|midskill", "все|ALSA")}
    for d in drafts:
        g = group_of(d)
        if g is None:
            continue
        mid = d["wr"] in MID
        for pn, pk, pick_i, pack in d["picks"]:
            if len(pack) < 2:
                continue
            gs = GIH[pack]
            if np.isnan(gs).all():
                continue
            order = np.argsort(np.where(np.isnan(gs), -1, gs))[::-1]
            top1, top2 = pack[order[0]], pack[order[1]]
            gap = (GIH[top1] - GIH[top2]) if not np.isnan(GIH[top2]) else 99
            took = pick_i == top1
            lost = (GIH[top1] - GIH[pick_i]) if not np.isnan(GIH[pick_i]) else GIH[top1] - 40
            bp = by_pick[pn * 14 + pk][g]
            bp["n"] += 1
            bp["greedy"] += took
            bp["lost"] += lost

            def add(k):
                s = slices[k][g]
                s["n"] += 1
                s["greedy"] += took
                s["lost"] += lost
            add("все")
            if gap >= 3:
                add("очевидный(gap>=3)")
            if gap <= 1:
                add("спорный(gap<=1)")
            if mid:
                add("все|midskill")
                if gap <= 1:
                    add("спорный|midskill")
            al = ALSA[pack]
            if not np.isnan(al).all():
                a_top = pack[int(np.argsort(np.where(np.isnan(al), 99, al))[0])]
                s = slices["все|ALSA"][g]
                s["n"] += 1
                s["greedy"] += (pick_i == a_top)

    print("═══ Этап 1: доля пиков = топ пака, средняя цена упущенного (GIH-пункты) ═══")
    for k, v in slices.items():
        t, f = v["T"], v["F"]
        if not t["n"] or not f["n"]:
            continue
        gt, gf = t["greedy"] / t["n"] * 100, f["greedy"] / f["n"] * 100
        print(f"{k:>22} | Т {gt:5.1f}% (n={t['n']:,}) | П {gf:5.1f}% (n={f['n']:,}) | "
              f"{gt-gf:+.1f} п.п. | упущено {t['lost']/t['n']:.2f} vs {f['lost']/f['n']:.2f}")
    print("\nпо номерам пиков (Δ доли топ-пиков, п.п.):")
    for pos in range(42):
        t, f = by_pick[pos]["T"], by_pick[pos]["F"]
        if t["n"] and f["n"]:
            diff = t["greedy"] / t["n"] * 100 - f["greedy"] / f["n"] * 100
            print(f"  P{pos//14+1}P{pos%14+1:>2}: {diff:+5.1f}")


# ── этап 2 ──────────────────────────────────────────────────────────────────
def build(group_drafts, phase, T):
    GIH, CCOL = T["GIH"], T["CCOL"]
    rowsX, chosen, starts = [], [], []
    pos = 0
    for d in group_drafts:
        pool_pips = defaultdict(float)
        tot = 0.0
        for pn, pk, pick_i, pack in sorted(d["picks"]):
            if pn == phase and len(pack) >= 2 and not np.isnan(GIH[pack]).all():
                starts.append(pos)
                for ci in pack:
                    cols = CCOL[ci]
                    if not cols or tot == 0:
                        inc = 1.0 if not cols else 0.0
                    else:
                        inc = min(1.0, sum(pool_pips[c] for c in cols) / tot)
                    g = GIH[ci] if not np.isnan(GIH[ci]) else 45.0
                    rowsX.append((g, inc, T["RARE"][ci], T["BONUS"][ci],
                                  T["REMOV"][ci], T["CRE"][ci], T["CMC"][ci]))
                    chosen.append(ci == pick_i)
                    pos += 1
            cols = CCOL[pick_i]
            for c in cols:
                pool_pips[c] += 1.0 / max(len(cols), 1)
            tot += 1.0 if cols else 0.0
    return (np.array(rowsX), np.array(chosen, dtype=bool),
            np.array(starts + [pos], dtype=np.int64))


def fit(X, chosen, bounds, mu, sd, lam=1e-3, iters=400):
    Xz = (X - mu) / sd
    starts = bounds[:-1]
    seg = np.repeat(np.arange(len(starts)), np.diff(bounds))
    w = np.zeros(F)
    m = np.zeros(F)
    v = np.zeros(F)
    for t in range(1, iters + 1):
        s = Xz @ w
        e = np.exp(s - np.maximum.reduceat(s, starts)[seg])
        p = e / np.add.reduceat(e, starts)[seg]
        grad = Xz[chosen].sum(0) - (p[:, None] * Xz).sum(0) - lam * len(starts) * w
        m = 0.9 * m + 0.1 * grad
        v = 0.999 * v + 0.001 * grad ** 2
        w += 0.05 * (m / (1 - 0.9 ** t)) / (np.sqrt(v / (1 - 0.999 ** t)) + 1e-8)
    return w


def stage2(cards, drafts, T):
    tro = [d for d in drafts if d["w"] == 7]
    fail = [d for d in drafts if d["w"] <= 1]
    rng = np.random.default_rng(7)
    for phase, label in ((0, "БУСТЕР 1"), (1, "БУСТЕР 2"), (2, "БУСТЕР 3")):
        XT, cT, bT = build(tro, phase, T)
        XF, cF, bF = build(fail, phase, T)
        allX = np.vstack([XT, XF])
        mu, sd = allX.mean(0), allX.std(0)
        sd[sd == 0] = 1
        wT, wF = fit(XT, cT, bT, mu, sd), fit(XF, cF, bF, mu, sd)

        def halves(group):
            idx = rng.permutation(len(group))
            return [build([group[i] for i in sorted(h)], phase, T)
                    for h in (idx[:len(idx)//2], idx[len(idx)//2:])]
        (XT1, cT1, bT1), (XT2, cT2, bT2) = halves(tro)
        (XF1, cF1, bF1), (XF2, cF2, bF2) = halves(fail)
        wT1, wT2 = fit(XT1, cT1, bT1, mu, sd), fit(XT2, cT2, bT2, mu, sd)
        wF1, wF2 = fit(XF1, cF1, bF1, mu, sd), fit(XF2, cF2, bF2, mu, sd)
        print(f"\n═══ {label}  (пиков: трофей {len(bT)-1:,} · провал {len(bF)-1:,}) ═══")
        print(f"{'признак':>12} | {'ТРОФЕЙ':>20} | {'ПРОВАЛ':>20} | Δ(Т−П)")
        for i, f in enumerate(FEATS):
            print(f"{f:>12} | {wT[i]:+6.3f} ({wT1[i]:+.2f}/{wT2[i]:+.2f}) | "
                  f"{wF[i]:+6.3f} ({wF1[i]:+.2f}/{wF2[i]:+.2f}) | {wT[i]-wF[i]:+.3f}")


# ── этап 3: инкрементальный AUC пиков сверх колоды ─────────────────────────
PICK_F = ["упущено/пик", "доля топ-пиков", "упущ.Б1", "упущ.Б2", "упущ.Б3",
          "упущ.очевидные", "упущ.спорные"]


def pick_feats(d, GIH):
    lost_all, lost_ob, lost_sp, greedy, n = 0.0, [], [], 0, 0
    lost_by_pack = [0.0, 0.0, 0.0]
    n_by_pack = [0, 0, 0]
    for pn, pk, pick_i, pack in d["picks"]:
        if len(pack) < 2:
            continue
        gs = GIH[pack]
        if np.isnan(gs).all():
            continue
        order = np.argsort(np.where(np.isnan(gs), -1, gs))[::-1]
        top1, top2 = pack[order[0]], pack[order[1]]
        gap = (GIH[top1] - GIH[top2]) if not np.isnan(GIH[top2]) else 99
        lost = (GIH[top1] - GIH[pick_i]) if not np.isnan(GIH[pick_i]) else GIH[top1] - 40
        n += 1
        lost_all += lost
        greedy += (pick_i == top1)
        lost_by_pack[pn] += lost
        n_by_pack[pn] += 1
        (lost_ob if gap >= 3 else lost_sp if gap <= 1 else []).append(lost)
    if n < 30:
        return None
    return [lost_all / n, greedy / n,
            *(lost_by_pack[p] / max(n_by_pack[p], 1) for p in range(3)),
            (sum(lost_ob) / len(lost_ob)) if lost_ob else 0.0,
            (sum(lost_sp) / len(lost_sp)) if lost_sp else 0.0]


def stage3(cards, drafts, T, setcode):
    GIH = T["GIH"]
    dp = os.path.join(HERE, "games", f"{setcode}_decks.json.gz")
    decks_raw = json.load(gzip.open(dp, "rt"))
    deck_by_id = {}
    for d in decks_raw["decks"]:
        did, bi = d["key"]
        if bi == "0" or did not in deck_by_id:
            deck_by_id[did] = d
    rows = []
    for d in drafts:
        if d["w"] == 7:
            y = 1.0
        elif d["w"] <= 1:
            y = 0.0
        else:
            continue
        deck = deck_by_id.get(d["id"])
        pf = pick_feats(d, GIH)
        if deck is None or pf is None:
            continue
        rows.append((y, deck["cards"], pf))
    print(f"джойн пики+колоды: {len(rows):,} драфтов")
    from collections import Counter
    BASICS = {"Plains", "Island", "Swamp", "Mountain", "Forest"}
    freq = Counter()
    for _, cds, _ in rows:
        for name in cds:
            if name not in BASICS:
                freq[name] += 1
    feat_cards = sorted(c for c, n in freq.items() if n >= 200)
    ci = {c: i for i, c in enumerate(feat_cards)}
    Xc = np.zeros((len(rows), len(feat_cards)))
    Xp = np.zeros((len(rows), len(PICK_F)))
    y = np.array([r[0] for r in rows])
    for k, (_, cds, pf) in enumerate(rows):
        for name, cnt in cds.items():
            i = ci.get(name)
            if i is not None:
                Xc[k, i] = cnt
        Xp[k] = pf
    Xp = (Xp - Xp.mean(0)) / Xp.std(0)

    def auc(yt, s):
        o = np.argsort(s)
        rk = np.empty(len(s))
        rk[o] = np.arange(1, len(s) + 1)
        n1 = yt.sum()
        return (rk[yt == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * (len(yt) - n1))

    rng = np.random.default_rng(42)
    folds = np.array_split(rng.permutation(len(rows)), 5)

    def cv_auc(X):
        best = None
        for lam in [1, 10, 30, 100, 300, 1000]:
            aucs = []
            for k in range(5):
                te = folds[k]
                tr = np.concatenate([folds[j] for j in range(5) if j != k])
                mu = X[tr].mean(0)
                Xt = X[tr] - mu
                w = np.linalg.solve(Xt.T @ Xt + lam * np.eye(X.shape[1]),
                                    Xt.T @ (y[tr] - y[tr].mean()))
                aucs.append(auc(y[te], (X[te] - mu) @ w))
            m = np.mean(aucs)
            if best is None or m > best[1]:
                best = (lam, m, np.std(aucs) / np.sqrt(5))
        return best

    for name, X in (("колода (карты)", Xc),
                    ("колода + пик-признаки", np.hstack([Xc, Xp])),
                    ("только пик-признаки", Xp)):
        lam, m, se = cv_auc(X)
        print(f"  {name:>24}: AUC {m:.4f} ± {se:.4f} (λ={lam})")


# ── этап 4: экзамен ранжировщиков на пиках людей ───────────────────────────
def stage4(cards, drafts, T):
    """Три ранжировщика (GIH · 2GIH+IWD · логит-трофейщика) против пиков людей,
    плюс точечный тест тайбрейка IWD на GIH-ничьих. Веса логита — из stage2."""
    GIH, CCOL = T["GIH"], T["CCOL"]
    rat = DP.load_ratings("msh")
    IWD = np.full(len(cards), np.nan)
    for i, c in enumerate(cards):
        r = rat.get(DP.norm(c)) or rat.get(DP.norm(c.split(",")[0]))
        if r and r.get("drawn_improvement_win_rate") is not None:
            IWD[i] = r["drawn_improvement_win_rate"] * 100
    W_LOGIT = {0: [1.464, 0.502, 0.298, 0.138, 0.171, 0.280, 0.100],
               1: [1.255, 0.619, 0.191, 0.144, 0.150, 0.267, 0.062],
               2: [1.161, 0.620, 0.180, 0.136, 0.142, 0.230, 0.060]}

    def feat_row(ci2, pool_pips, tot):
        cols = CCOL[ci2]
        if not cols or tot == 0:
            inc = 1.0 if not cols else 0.0
        else:
            inc = min(1.0, sum(pool_pips[c] for c in cols) / tot)
        g = GIH[ci2] if not np.isnan(GIH[ci2]) else 45.0
        return (g, inc, T["RARE"][ci2], T["BONUS"][ci2], T["REMOV"][ci2],
                T["CRE"][ci2], T["CMC"][ci2])

    sums = {p: [np.zeros(F), np.zeros(F), 0] for p in range(3)}
    for d in drafts:
        if d["w"] != 7 and d["w"] > 1:
            continue
        pool_pips = defaultdict(float)
        tot = 0.0
        for pn, pk, pick_i, pack in sorted(d["picks"]):
            if len(pack) >= 2 and not np.isnan(GIH[pack]).all():
                for ci2 in pack:
                    x = np.array(feat_row(ci2, pool_pips, tot))
                    s = sums[pn]
                    s[0] += x
                    s[1] += x * x
                    s[2] += 1
            cols = CCOL[pick_i]
            for c in cols:
                pool_pips[c] += 1.0 / max(len(cols), 1)
            tot += 1.0 if cols else 0.0
    MUSD = {p: ((s1 / n), np.sqrt(np.maximum(s2 / n - (s1 / n) ** 2, 1e-9)))
            for p, (s1, s2, n) in sums.items()}

    def make():
        return {"GIH": 0, "2GIH+IWD": 0, "логит-Т": 0, "n": 0}
    res = {g: {"все": make(), "спорные": make()} for g in "TF"}
    tie = {"T": [0, 0], "F": [0, 0]}
    for d in drafts:
        if d["w"] == 7:
            g = "T"
        elif d["w"] <= 1:
            g = "F"
        else:
            continue
        pool_pips = defaultdict(float)
        tot = 0.0
        for pn, pk, pick_i, pack in sorted(d["picks"]):
            if len(pack) >= 2 and not np.isnan(GIH[pack]).all():
                gs = np.where(np.isnan(GIH[pack]), -1, GIH[pack])
                o = np.argsort(gs)[::-1]
                top_gih = pack[o[0]]
                gap = gs[o[0]] - gs[o[1]]
                top_b = pack[int(np.argmax(2 * gs + np.where(np.isnan(IWD[pack]), 0, IWD[pack])))]
                X = np.array([feat_row(ci2, pool_pips, tot) for ci2 in pack])
                mu, sd = MUSD[pn]
                top_l = pack[int(np.argmax(((X - mu) / sd) @ np.array(W_LOGIT[pn])))]
                for key in (("все",) if gap > 1 else ("все", "спорные")):
                    r = res[g][key]
                    r["n"] += 1
                    r["GIH"] += (pick_i == top_gih)
                    r["2GIH+IWD"] += (pick_i == top_b)
                    r["логит-Т"] += (pick_i == top_l)
                # тест тайбрейка: GIH-ничья топ-2, IWD различает, взято одно из двух
                a, b = pack[o[0]], pack[o[1]]
                if (gap <= 0.5 and len(pack) >= 3 and not np.isnan(IWD[a])
                        and not np.isnan(IWD[b]) and abs(IWD[a] - IWD[b]) >= 1.5
                        and pick_i in (a, b)):
                    hi = a if IWD[a] > IWD[b] else b
                    tie[g][1] += 1
                    tie[g][0] += (pick_i == hi)
            cols = CCOL[pick_i]
            for c in cols:
                pool_pips[c] += 1.0 / max(len(cols), 1)
            tot += 1.0 if cols else 0.0

    print("═══ Этап 4: доля пиков игрока = топ ранжировщика ═══")
    for key in ("все", "спорные"):
        print(f"  [{key}] (nТ={res['T'][key]['n']:,} · nП={res['F'][key]['n']:,})")
        for rk in ("GIH", "2GIH+IWD", "логит-Т"):
            t = res["T"][key][rk] / res["T"][key]["n"] * 100
            f = res["F"][key][rk] / res["F"][key]["n"] * 100
            print(f"    {rk:>10}: трофейщики {t:5.1f}% · провальщики {f:5.1f}% · Δ {t-f:+.1f}")
    print("  тайбрейк IWD на GIH-ничьих (взял высокий IWD):")
    for g, lab in (("T", "трофейщики"), ("F", "провальщики")):
        k, n = tie[g]
        print(f"    {lab}: {k/n*100:.1f}% (n={n:,})")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("set")
    ap.add_argument("--stage", type=int, choices=(1, 2, 3, 4), required=True)
    a = ap.parse_args()
    cards, drafts = load(a.set.lower())
    T = card_tables(cards, a.set.lower())
    if a.stage == 1:
        stage1(cards, drafts, T)
    elif a.stage == 2:
        stage2(cards, drafts, T)
    elif a.stage == 3:
        stage3(cards, drafts, T, a.set.lower())
    else:
        stage4(cards, drafts, T)
    return 0


if __name__ == "__main__":
    sys.exit(main())
