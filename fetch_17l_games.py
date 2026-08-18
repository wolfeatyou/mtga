#!/usr/bin/env python3
"""Публичный game-датасет 17Lands -> таблица колод С ПОБЕДАМИ И ПОРАЖЕНИЯМИ.

ЗАЧЕМ. До сих пор вся калибровка скилла стояла на `ref_decks/` — 298 трофейных
листов с untapped. Это выборка ТОЛЬКО победителей: проверено 18.08.2026, выдача
отдаёт 545 колод HOB и все до одной 7-0/7-1/7-2. На такой выборке любая ось
отвечает на вопрос «что есть у победителей» и НИ ОДНА не может ответить
«отделяет ли это победителей от проигравших» (JOURNAL § 8.4).

Здесь берётся контрольная группа. В game-датасете одна строка = одна ПАРТИЯ,
`won` = True/False примерно 50/50, а `deck_<карта>` даёт полный мейндек. Группируем
партии по (draft_id, build_index) — получаем колоду с её реальным счётом.

    python3 fetch_17l_games.py msh                 # -> games/msh_decks.json.gz
    python3 fetch_17l_games.py msh --max-games 50000   # быстрый прогон
    python3 fetch_17l_games.py hob --check         # только проверить, выложен ли сет

ЗАМЕЧАНИЯ ПО ДАННЫМ (читать до выводов):
· Сет появляется в датасете НЕ сразу. На 18.08.2026: MSH есть (31 МБ), HOB — 403,
  вышел 11.08. Проверять `--check`.
· Файл ~30-240 МБ gz и до ~1.3 ГБ текста — он СТРИМИТСЯ, на диск не кладётся.
· В датасете только PremierDraft (Bo1) по умолчанию; `--event` меняет.
· У одного драфта бывает НЕСКОЛЬКО сборок (`build_index`) — это разные колоды,
  и группировать надо по паре, иначе смешаются разные листы одного пула.
· `rank` — ранг игрока на момент партии, не сила колоды. Фильтровать им можно,
  но это меняет популяцию: сравнивать надо внутри одного фильтра.
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
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = "https://17lands-public.s3.amazonaws.com/analysis_data"
UA = {"User-Agent": "Mozilla/5.0"}


def url_for(setcode, event, kind="game_data"):
    return f"{BASE}/{kind}/{kind}_public.{setcode.upper()}.{event}.csv.gz"


def probe(u):
    """(есть ли файл, размер в байтах)."""
    req = urllib.request.Request(u, headers=dict(UA, Range="bytes=0-1"))
    try:
        with urllib.request.urlopen(req, timeout=30) as f:
            cr = f.headers.get("Content-Range", "")
            return True, int(cr.split("/")[-1]) if "/" in cr else 0
    except urllib.error.HTTPError as e:
        return False, e.code
    except Exception:
        return False, 0


def stream_rows(u, max_games=None):
    """Ленивая построчная выдача (header, row) без материализации файла."""
    req = urllib.request.Request(u, headers=UA)
    with urllib.request.urlopen(req, timeout=120) as resp:
        gz = gzip.GzipFile(fileobj=resp)
        text = io.TextIOWrapper(gz, encoding="utf-8", errors="replace", newline="")
        rd = csv.reader(text)
        header = next(rd)
        yield header, None
        for i, row in enumerate(rd):
            if max_games and i >= max_games:
                return
            yield None, row


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("set")
    ap.add_argument("--event", default="PremierDraft")
    ap.add_argument("--max-games", type=int, default=None)
    ap.add_argument("--check", action="store_true", help="только проверить наличие")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    u = url_for(a.set, a.event)
    ok, info = probe(u)
    if not ok:
        print(f"❌ {a.set.upper()}/{a.event}: датасет не выложен (HTTP {info})")
        print(f"   {u}")
        print("   17Lands публикует набор не сразу после релиза сета — проверить позже.")
        return 1
    print(f"✅ {a.set.upper()}/{a.event}: {info/1e6:.0f} МБ gz")
    print(f"   {u}")
    if a.check:
        return 0

    decks = {}          # (draft_id, build_index) -> {"w":int,"l":int,"cards":{...},...}
    n_games = 0
    deck_cols = None
    idx = {}
    for header, row in stream_rows(u, a.max_games):
        if header is not None:
            idx = {c: i for i, c in enumerate(header)}
            deck_cols = [(i, c[5:]) for c, i in idx.items() if False]  # placeholder
            deck_cols = [(i, c[len("deck_"):]) for c, i in idx.items() if c.startswith("deck_")]
            need = ("draft_id", "build_index", "won", "rank", "main_colors")
            missing = [c for c in need if c not in idx]
            if missing:
                print(f"❌ в датасете нет колонок: {missing}")
                return 1
            print(f"   колонок {len(header)}, из них deck_* — {len(deck_cols)}")
            continue
        n_games += 1
        key = (row[idx["draft_id"]], row[idx["build_index"]])
        d = decks.get(key)
        if d is None:
            cards = {name: int(row[i]) for i, name in deck_cols if row[i] not in ("0", "")}
            d = decks[key] = {"w": 0, "l": 0, "rank": row[idx["rank"]],
                              "colors": row[idx["main_colors"]], "cards": cards}
        if row[idx["won"]] == "True":
            d["w"] += 1
        else:
            d["l"] += 1
        if n_games % 50000 == 0:
            print(f"   … {n_games:,} партий, {len(decks):,} колод", flush=True)

    out = a.out or os.path.join(HERE, "games", f"{a.set.lower()}_decks.json.gz")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with gzip.open(out, "wt", encoding="utf-8") as f:
        json.dump({"set": a.set.lower(), "event": a.event, "games": n_games,
                   "decks": [dict(v, key=list(k)) for k, v in decks.items()]}, f)

    wins = sum(d["w"] for d in decks.values())
    losses = sum(d["l"] for d in decks.values())
    full = [d for d in decks.values() if d["w"] + d["l"] >= 3]
    print(f"\nпартий {n_games:,} · колод {len(decks):,} · побед {wins:,} / поражений {losses:,}"
          f" ({wins/(wins+losses)*100:.1f}%)")
    print(f"колод с >=3 партиями: {len(full):,}  (на них и считать винрейт)")
    print(f"записано: {out}  ({os.path.getsize(out)/1e6:.1f} МБ)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
