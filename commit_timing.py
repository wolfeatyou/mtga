#!/usr/bin/env python3
"""Момент коммита в цвета: когда драфтеры фиксируют пару и влияет ли это на исход.

Проверка гипотезы «стей-опен / поздний коммит выигрывает» (стримерский стиль) на
реальных драфтах. Требует оба датасета: `fetch_17l_picks.py <set>` и
`fetch_17l_games.py <set>` (финальная пара берётся из реального сабмиченного листа).

    python3 commit_timing.py msh

Определения:
· ЛОК-ПИК — первый пик (1-базный, 1..42), после которого топ-2 цвета пула (по числу
  пиков, гибрид дробно) строго совпадают с финальной парой колоды до конца драфта;
  43 = не залочился. Только 2-цветные колоды (в джойне MSH их 76%).
· СИЛА СИДЕНЬЯ — средний максимум GIH по 14 пакам первого бустера: свойство бустеров,
  а не решений игрока. Обязательный контроль: сильное сиденье само сдвигает лок раньше.
· ПОТЕРЯННЫЕ P1-ПИКИ — пики первого бустера, чья карта не попала в мейндек.

Результат на MSH (18.08.2026, JOURNAL § 8.10): тайминг коммита в окне P1P1–P2P14
исход НЕ меняет (кривая плоская), наказываются только патологии (не залочился к Б3);
трофей и провал теряют ОДИНАКОВО ~5.1 из 14 P1-пиков.
"""
import argparse
import gzip
import json
import os
import sys
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import deck_profile as DP


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("set")
    a = ap.parse_args()
    sc = a.set.lower()

    picks_raw = json.load(gzip.open(os.path.join(HERE, "games", f"{sc}_picks.json.gz"), "rt"))
    decks_raw = json.load(gzip.open(os.path.join(HERE, "games", f"{sc}_decks.json.gz"), "rt"))
    cards, pdrafts = picks_raw["cards"], picks_raw["drafts"]
    rat = DP.load_ratings(sc)

    GIH = np.full(len(cards), np.nan)
    CCOL = [set() for _ in cards]
    for i, c in enumerate(cards):
        r = rat.get(DP.norm(c)) or rat.get(DP.norm(c.split(",")[0]))
        if r:
            if r.get("ever_drawn_win_rate"):
                GIH[i] = r["ever_drawn_win_rate"] * 100
            for ch in (r.get("color") or ""):
                if ch in "WUBRG":
                    CCOL[i].add(ch)

    deck_by_id = {}
    for d in decks_raw["decks"]:
        did, bi = d["key"]
        if bi == "0" or did not in deck_by_id:
            deck_by_id[did] = d

    def analyze(d, pair, deck_cards):
        picks = sorted(d["picks"])
        if len(picks) != 42:
            return None
        counts = defaultdict(float)
        states, seat, offpair = [], [], []
        wasted_p1 = 0
        for pn, pk, pick_i, pack in picks:
            if pn == 0:
                g = GIH[pack]
                g = g[~np.isnan(g)]
                if len(g):
                    seat.append(g.max())
                if cards[pick_i] not in deck_cards:
                    wasted_p1 += 1
            cols = CCOL[pick_i]
            offpair.append(bool(cols - pair))
            for c in cols:
                counts[c] += 1.0 / max(len(cols), 1)
            order = sorted("WUBRG", key=lambda c: -counts[c])
            states.append(set(order[:2]) if counts[order[1]] > counts[order[2]] else None)
        lock = 43
        for i in range(41, -1, -1):
            if states[i] is not None and states[i] == pair:
                lock = i + 1
            else:
                break
        pivot = not (states[13] is not None and states[13] == pair)
        return dict(lock=lock, pivot=pivot, wasted=wasted_p1,
                    seat=np.mean(seat) if seat else np.nan,
                    off_e=sum(offpair[:5]), off_p3=sum(offpair[28:]))

    rows = []
    for d in pdrafts:
        deck = deck_by_id.get(d["id"])
        if deck is None or len(deck["colors"]) != 2:
            continue
        r = analyze(d, set(deck["colors"]), deck["cards"])
        if r is not None:
            rows.append(dict(r, w=d["w"], wr=d["wr"]))
    print(f"завершённые 2-цветные драфты: {len(rows):,}")

    W = np.array([r["w"] for r in rows], float)
    L = np.array([r["lock"] for r in rows], float)
    S = np.array([r["seat"] for r in rows], float)
    WA = np.array([r["wasted"] for r in rows], float)
    tro, fail = W == 7, W <= 1

    def cohen_d(a, b):
        sp = np.sqrt(((len(a) - 1) * a.std(ddof=1) ** 2 + (len(b) - 1) * b.std(ddof=1) ** 2)
                     / (len(a) + len(b) - 2))
        return (a.mean() - b.mean()) / sp if sp else 0.0

    print("\n══ трофей vs провал ══")
    for name, X in (("лок-пик", L), ("потерянные P1-пики", WA),
                    ("off-pair P1P1-5", np.array([r["off_e"] for r in rows], float)),
                    ("off-pair Б3", np.array([r["off_p3"] for r in rows], float))):
        print(f"  {name:>20}: Т {X[tro].mean():5.2f} · П {X[fail].mean():5.2f} · "
              f"d = {cohen_d(X[tro], X[fail]):+.3f}")
    pv = np.array([r["pivot"] for r in rows], float)
    print(f"  {'пивот после Б1':>20}: Т {pv[tro].mean()*100:.1f}% · П {pv[fail].mean()*100:.1f}%")

    print("\n══ среднее число побед по лок-пику (все завершённые) ══")
    buckets = [(1, 3), (4, 7), (8, 14), (15, 28), (29, 42), (43, 43)]
    for lo, hi in buckets:
        m = (L >= lo) & (L <= hi)
        print(f"  лок {lo:>2}-{hi:>2}: побед {W[m].mean():.2f} (n={m.sum():,}) · "
              f"сиденье {np.nanmean(S[m]):.1f}")

    print("\n══ то же внутри крайних квартилей силы сиденья ══")
    qs = np.nanpercentile(S, [25, 75])
    for lo, hi, lab in ((-1, qs[0], "слабое"), (qs[1], 99, "сильное")):
        m0 = (S > lo) & (S <= hi)
        print(f"  [{lab}, n={m0.sum():,}]")
        for blo, bhi in buckets:
            m = m0 & (L >= blo) & (L <= bhi)
            if m.sum() > 300:
                print(f"    лок {blo:>2}-{bhi:>2}: побед {W[m].mean():.2f} (n={m.sum():,})")

    print("\n══ побед по числу потерянных P1-пиков ══")
    for k in range(1, 8):
        m = (WA == k) if k < 7 else (WA >= 7)
        if m.sum() > 300:
            print(f"  {'≥7' if k >= 7 else k:>2}: побед {W[m].mean():.2f} · "
                  f"сиденье {np.nanmean(S[m]):.1f} (n={m.sum():,})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
