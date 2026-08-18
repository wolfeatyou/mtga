#!/usr/bin/env python3
"""Публичный draft-датасет 17Lands -> компактный лог пиков ЗАВЕРШЁННЫХ ранов.

ЗАЧЕМ (JOURNAL § 8.7/§ 9 Шаг 3 п.2). У драфта 42 решения и один исход: оценка колоды
упёрлась в потолок AUC 0.72, дальше сигнал живёт в ПИКАХ. Здесь одна строка исходника =
один пик: весь пак (`pack_card_*`), что игрок взял (`pick`), итоговый рекорд рана
(`event_match_wins/losses`) и скилл игрока (`user_game_win_rate_bucket`).

    python3 fetch_17l_picks.py msh                # -> games/msh_picks.json.gz
    python3 fetch_17l_picks.py hob --check        # только проверить, выложен ли сет

Фильтр МЯГКИЙ (18.08.2026, по решению пользователя): берём ВСЕ завершённые раны
(7 побед ИЛИ 3 поражения), а не только трофей/провал — определение «спорного пика»
само предмет исследования, резать надо по выжимке, не по стриму.

Формат выжимки:
    {"set", "event", "cards": [имена, индексируют пак и пик],
     "drafts": [{"id", "rank", "w", "l", "wr" (скилл-бакет), "ng" (игр-бакет),
                 "picks": [[pack_no, pick_no, pick_idx, [индексы карт пака]], ...]}]}

Пул на пике k НЕ хранится — это первые k элементов picks того же драфта.
`pool_*` колонки исходника по той же причине не читаются вовсе.
"""
import argparse
import csv
import gzip
import io
import json
import os
import sys
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = "https://17lands-public.s3.amazonaws.com/analysis_data"
UA = {"User-Agent": "Mozilla/5.0"}


def url_for(setcode, event):
    return f"{BASE}/draft_data/draft_data_public.{setcode.upper()}.{event}.csv.gz"


def probe(u):
    req = urllib.request.Request(u, headers=dict(UA, Range="bytes=0-1"))
    try:
        with urllib.request.urlopen(req, timeout=30) as f:
            cr = f.headers.get("Content-Range", "")
            return True, int(cr.split("/")[-1]) if "/" in cr else 0
    except urllib.error.HTTPError as e:
        return False, e.code
    except Exception:
        return False, 0


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("set")
    ap.add_argument("--event", default="PremierDraft")
    ap.add_argument("--max-rows", type=int, default=None)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    u = url_for(a.set, a.event)
    ok, info = probe(u)
    if not ok:
        print(f"❌ {a.set.upper()}/{a.event}: draft-датасет не выложен (HTTP {info})")
        print(f"   {u}")
        return 1
    print(f"✅ {a.set.upper()}/{a.event}: {info/1e6:.0f} МБ gz")
    if a.check:
        return 0

    req = urllib.request.Request(u, headers=UA)
    drafts = {}
    n_rows = n_kept = 0
    with urllib.request.urlopen(req, timeout=300) as resp:
        gz = gzip.GzipFile(fileobj=resp)
        text = io.TextIOWrapper(gz, encoding="utf-8", errors="replace", newline="")
        rd = csv.reader(text)
        header = next(rd)
        idx = {c: i for i, c in enumerate(header)}
        need = ("draft_id", "rank", "event_match_wins", "event_match_losses",
                "pack_number", "pick_number", "pick",
                "user_game_win_rate_bucket", "user_n_games_bucket")
        missing = [c for c in need if c not in idx]
        if missing:
            print(f"❌ нет колонок: {missing}")
            return 1
        pack_cols = [(i, c[len("pack_card_"):]) for c, i in idx.items()
                     if c.startswith("pack_card_")]
        pack_cols.sort(key=lambda t: t[1])
        cards = [name for _, name in pack_cols]
        cidx = {name: k for k, (_, name) in enumerate(pack_cols)}
        i_id, i_rank = idx["draft_id"], idx["rank"]
        i_w, i_l = idx["event_match_wins"], idx["event_match_losses"]
        i_pn, i_pk = idx["pack_number"], idx["pick_number"]
        i_pick = idx["pick"]
        i_wr, i_ng = idx["user_game_win_rate_bucket"], idx["user_n_games_bucket"]
        print(f"   колонок {len(header)}, карт в паковой матрице {len(cards)}")

        for row in rd:
            n_rows += 1
            if a.max_rows and n_rows > a.max_rows:
                break
            w, l = int(row[i_w]), int(row[i_l])
            if w != 7 and l != 3:      # мягкий фильтр: только завершённые раны
                continue
            pick_i = cidx.get(row[i_pick])
            if pick_i is None:         # пик не из паковой матрицы — брак строки
                continue
            n_kept += 1
            did = row[i_id]
            d = drafts.get(did)
            if d is None:
                d = drafts[did] = {"id": did, "rank": row[i_rank], "w": w, "l": l,
                                   "wr": row[i_wr], "ng": row[i_ng], "picks": []}
            pack = [k for k, (i, _) in enumerate(pack_cols) if row[i] != "0"]
            d["picks"].append([int(row[i_pn]), int(row[i_pk]), pick_i, pack])
            if n_rows % 200000 == 0:
                print(f"   … {n_rows:,} строк, взято {n_kept:,}, драфтов {len(drafts):,}",
                      flush=True)

    # целостность: полный драфт = 42 пика без дыр
    full = sum(1 for d in drafts.values() if len(d["picks"]) == 42)
    out = a.out or os.path.join(HERE, "games", f"{a.set.lower()}_picks.json.gz")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with gzip.open(out, "wt", encoding="utf-8") as f:
        json.dump({"set": a.set.lower(), "event": a.event, "cards": cards,
                   "drafts": list(drafts.values())}, f)

    tro = sum(1 for d in drafts.values() if d["w"] == 7)
    fail = sum(1 for d in drafts.values() if d["w"] <= 1)
    print(f"\nстрок {n_rows:,} · пиков взято {n_kept:,} · завершённых драфтов {len(drafts):,}"
          f" (из них полных 42/42: {full:,})")
    print(f"трофеев {tro:,} · провалов (<=1 победы) {fail:,}")
    print(f"записано: {out}  ({os.path.getsize(out)/1e6:.1f} МБ)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
