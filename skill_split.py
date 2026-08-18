#!/usr/bin/env python3
"""Срез по ИГРОКАМ (топ vs низ по историческому винрейту), а не по исходу драфта.

Зачем (JOURNAL § 8.11): деление трофей/провал обусловлено исходом ОДНОГО рана — в нём
сидит удача. `user_game_win_rate_bucket` считается 17Lands по всей истории игрока,
т.е. срез независим от удачи текущего драфта. Если картина совпадает с § 8.9 —
вывод «скилл = точность по качеству карт» перестаёт зависеть от способа деления.

    python3 skill_split.py msh

Пороги: ТОП wr>=0.62, НИЗ wr<=0.46, только игроки со 100+ играми (меньшие бакеты —
шумовой винрейт). На MSH: 4 580 / 5 374 драфтов, санити: 4.57 vs 2.23 победы.
"""
import argparse, gzip, json, os, sys
from collections import defaultdict
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import deck_profile as DP
import pick_quality as PQ


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("set")
    a = ap.parse_args()
    sc = a.set.lower()
    picks_raw = json.load(gzip.open(os.path.join(HERE, "games", f"{sc}_picks.json.gz"), "rt"))
    decks_raw = json.load(gzip.open(os.path.join(HERE, "games", f"{sc}_decks.json.gz"), "rt"))
    cards, pdrafts = picks_raw["cards"], picks_raw["drafts"]
    T = PQ.card_tables(cards, sc)
    GIH = T["GIH"]
    rat = DP.load_ratings(sc)

    def grp(d):
        if not d["ng"] or float(d["ng"]) < 100:
            return None
        w = float(d["wr"] or 0)
        if w >= 0.62:
            return "TOP"
        if w and w <= 0.46:
            return "BOT"
        return None

    top = [d for d in pdrafts if grp(d) == "TOP"]
    bot = [d for d in pdrafts if grp(d) == "BOT"]
    print(f"драфтов: топ {len(top):,} · низ {len(bot):,}")
    wt = np.array([d["w"] for d in top]); wb = np.array([d["w"] for d in bot])
    print(f"санити — среднее побед: топ {wt.mean():.2f} · низ {wb.mean():.2f} "
          f"(трофеев {np.mean(wt==7)*100:.0f}% vs {np.mean(wb==7)*100:.0f}%)")

    def pickstats(group):
        greedy = n = 0; lost = 0.0; g_sp = n_sp = 0
        for d in group:
            for pn, pk, pick_i, pack in d["picks"]:
                if len(pack) < 2:
                    continue
                gs = GIH[pack]
                if np.isnan(gs).all():
                    continue
                o = np.argsort(np.where(np.isnan(gs), -1, gs))[::-1]
                t1, t2 = pack[o[0]], pack[o[1]]
                gap = (GIH[t1]-GIH[t2]) if not np.isnan(GIH[t2]) else 99
                took = pick_i == t1
                n += 1; greedy += took
                lost += (GIH[t1]-GIH[pick_i]) if not np.isnan(GIH[pick_i]) else GIH[t1]-40
                if gap <= 1:
                    n_sp += 1; g_sp += took
        return greedy/n*100, lost/n, g_sp/n_sp*100, n

    gt, gb = pickstats(top), pickstats(bot)
    print(f"\nпики: топ-GIH взят — топ {gt[0]:.1f}% · низ {gb[0]:.1f}% (Δ {gt[0]-gb[0]:+.1f} п.п.)")
    print(f"      цена упущенного — {gt[1]:.2f} vs {gb[1]:.2f} GIH-пункта/пик")
    print(f"      на спорных — {gt[2]:.1f}% vs {gb[2]:.1f}%  (n пиков {gt[3]:,}/{gb[3]:,})")

    for phase in (0, 2):
        XT, cT, bT = PQ.build(top, phase, T)
        XB, cB, bB = PQ.build(bot, phase, T)
        allX = np.vstack([XT, XB]); mu, sd = allX.mean(0), allX.std(0); sd[sd == 0] = 1
        wT, wB = PQ.fit(XT, cT, bT, mu, sd), PQ.fit(XB, cB, bB, mu, sd)
        print(f"\n═══ логит, БУСТЕР {phase+1} (пиков {len(bT)-1:,}/{len(bB)-1:,}) ═══")
        for i, f in enumerate(PQ.FEATS):
            print(f"{f:>12} | топ {wT[i]:+7.3f} | низ {wB[i]:+7.3f} | Δ {wT[i]-wB[i]:+.3f}")

    deck_by_id = {}
    for d in decks_raw["decks"]:
        did, bi = d["key"]
        if bi == "0" or did not in deck_by_id:
            deck_by_id[did] = d
    db = DP.load_db()
    cur = []
    DP.parse_deck = lambda p: cur
    AXES = ["creatures", "cheap", "evasion", "hard", "c5", "fixers", "ncolors"]

    def deckrows(group):
        nonlocal cur
        rows = []
        for d in group:
            deck = deck_by_id.get(d["id"])
            if deck is None:
                continue
            cur = [(cnt, n) for n, cnt in deck["cards"].items()]
            m = DP.metrics("_", db, rat)
            rows.append([m[x] for x in AXES] + [m["gih"] or np.nan])
        return np.array(rows, float)

    def cohen_d(x, y):
        x, y = x[~np.isnan(x)], y[~np.isnan(y)]
        sp = np.sqrt(((len(x)-1)*x.std(ddof=1)**2 + (len(y)-1)*y.std(ddof=1)**2)
                     / (len(x)+len(y)-2))
        return (x.mean()-y.mean())/sp

    A, B = deckrows(top), deckrows(bot)
    print(f"\n═══ колоды (n {len(A):,}/{len(B):,}) ═══")
    for i, name in enumerate(AXES + ["средний GIH колоды"]):
        print(f"  {name:>20}: топ {np.nanmean(A[:,i]):6.2f} · низ {np.nanmean(B[:,i]):6.2f}"
              f" · d = {cohen_d(A[:,i], B[:,i]):+.3f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
