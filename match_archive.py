#!/usr/bin/env python3
"""Постоянный учёт партий: реестр + архив сырых логов ДО ротации Player.log.

ЗАЧЕМ (JOURNAL § 8.13, поставлено 18.08.2026 по указанию пользователя). Player.log
ротируется быстро; всё, что не разобрано сразу, пропадало навсегда — включая сырьё
для будущих разборов и сам СЧЁТ (сколько партий, каким деком, с каким исходом).
Этот скрипт идемпотентно переносит из лога в скилл:

  matches/<set>_ledger.jsonl — одна строка = одна ПАРТИЯ: matchID, номер игры,
      результат, ходы, seat, событие (PremierDraft_HOB_…), сабмиченная колода
      ПОИМЁННО (ближайший предшествующий CourseDeck — правило § 2.4: причинные
      выводы о колоде только по реальному сабмиту), таймстамп из лога.
  logs/<match8>.log.gz — сырой сегмент лога всего матча: полноценный разбор
      (analyze_game/replay_moments) возможен и после ротации.

    python3 match_archive.py <set>            # заархивировать всё новое из логов
    python3 match_archive.py <set> --status   # счёт: W-L по событиям и колодам

Автовызов: analyze_game.py и match_watch.py дёргают run_quiet() при старте —
любая разбираемая или коучимая партия архивируется сама. После игровой сессии
без разбора запустить руками (или это сделает ближайший разбор).
Как save_pool: никогда не роняет вызывающего.
"""
import argparse
import glob
import gzip
import json
import os
import re
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import match_watch as mw

LEDGER_DIR = os.path.join(HERE, "matches")
LOGS_DIR = os.path.join(HERE, "logs")

TS_RE = re.compile(r"\b(\d{1,2}[./]\d{1,2}[./]\d{4}|\d{4}-\d{2}-\d{2})[ T]"
                   r"(\d{1,2}:\d{2}:\d{2})")


def _nearest_ts(txt, pos):
    m = None
    for m in TS_RE.finditer(txt, max(0, pos - 20000), pos + 2000):
        pass
    return f"{m.group(1)} {m.group(2)}" if m else None


def _course_decks(txt, names):
    """[(pos, event_name, [(имя, штук), ...])] по всем CourseDeck в логе."""
    out = []
    for m in re.finditer(r'"CourseDeck":\{"MainDeck":\[((?:[^\]]|\][^,}])*?)\]', txt):
        cards = [(int(a), int(b)) for a, b in
                 re.findall(r'"cardId":(\d+),"quantity":(\d+)', m.group(1))]
        ev = None
        e = None
        for e in re.finditer(r'"InternalEventName":"([^"]+)"',
                             txt[max(0, m.start() - 5000):m.start()]):
            pass
        if e:
            ev = e.group(1)
        deck = [( (names.get(cid) or f"id{cid}").split(" //")[0], q) for cid, q in cards]
        out.append((m.start(), ev, deck))
    return out


def collect(setcode):
    """Все партии из текущих логов -> [записи реестра] + сегменты матчей."""
    txt = mw.read_logs()
    names = mw.load_names()
    decks = _course_decks(txt, names)

    games = []      # (match_id, game_no, start_pos)
    seen = set()
    for m in re.finditer(r'"matchID"\s*:\s*"([0-9a-f\-]+)"\s*,\s*"gameNumber"\s*:\s*(\d+)', txt):
        key = (m.group(1), int(m.group(2)))
        if key not in seen:
            seen.add(key)
            games.append((key[0], key[1], m.start()))
    games.sort(key=lambda g: g[2])

    bounds = {}     # match_id -> (first_pos, last_pos)
    for mid, _, pos in games:
        lo, hi = bounds.get(mid, (pos, pos))
        bounds[mid] = (min(lo, pos), max(hi, pos))
    for m in re.finditer(r'"matchID"\s*:\s*"([0-9a-f\-]+)"', txt):
        mid = m.group(1)
        if mid in bounds:
            lo, hi = bounds[mid]
            bounds[mid] = (min(lo, m.start()), max(hi, m.start()))

    records, segments = [], {}
    for k, (mid, gno, pos) in enumerate(games):
        end = games[k + 1][2] if k + 1 < len(games) else len(txt)
        sl = txt[pos:end]
        ss = re.findall(r'"systemSeatIds"\s*:\s*\[\s*(\d+)', sl)
        me = int(Counter(ss).most_common(1)[0][0]) if ss else None
        wins = re.findall(r'"winningTeamId"\s*:\s*(\d+)', sl)
        res = None
        if wins and me is not None:
            res = "W" if int(wins[-1]) == me else "L"
        turns = [int(x) for x in re.findall(r'"turnNumber"\s*:\s*(\d+)', sl)]
        deck_ev, deck = None, None
        for dpos, ev, dl in decks:
            if dpos < pos:
                deck_ev, deck = ev, dl
            else:
                break
        rec = dict(match=mid, game=gno, ts=_nearest_ts(txt, pos), event=deck_ev,
                   seat=me, result=res, turns=max(turns) if turns else None,
                   deck=[f"{q} {n}" for n, q in deck] if deck else None)
        records.append(rec)
    for mid, (lo, hi) in bounds.items():
        segments[mid] = txt[max(0, lo - 30000):min(len(txt), hi + 60000)]
    return records, segments


def run(setcode, quiet=False):
    os.makedirs(LEDGER_DIR, exist_ok=True)
    os.makedirs(LOGS_DIR, exist_ok=True)
    ledger = os.path.join(LEDGER_DIR, f"{setcode}_ledger.jsonl")
    known = set()
    if os.path.exists(ledger):
        for line in open(ledger, encoding="utf-8"):
            try:
                r = json.loads(line)
                known.add((r.get("match"), r.get("game")))
            except Exception:
                continue
    records, segments = collect(setcode)
    sc_up = setcode.upper()
    new = [r for r in records if (r["match"], r["game"]) not in known
           and (r["event"] is None or sc_up in (r["event"] or "").upper())]
    if new:
        with open(ledger, "a", encoding="utf-8") as f:
            for r in new:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
    archived = 0
    for mid, seg in segments.items():
        if not any(r["match"] == mid for r in new + []) and \
           not any(r["match"] == mid and (r["match"], r["game"]) in known for r in records):
            continue
        p = os.path.join(LOGS_DIR, f"{mid[:8]}.log.gz")
        if not os.path.exists(p):
            with gzip.open(p, "wt", encoding="utf-8") as f:
                f.write(seg)
            archived += 1
    if not quiet:
        print(f"реестр: +{len(new)} партий (всего в логе видно {len(records)}), "
              f"архив: +{archived} матчей → matches/{os.path.basename(ledger)}, logs/")
    return len(new), archived


def run_quiet(setcode):
    """Для автовызова из analyze_game/match_watch: молча и никогда не падает."""
    try:
        return run(setcode, quiet=True)
    except Exception:
        return None


def status(setcode):
    ledger = os.path.join(LEDGER_DIR, f"{setcode}_ledger.jsonl")
    if not os.path.exists(ledger):
        print(f"реестра ещё нет: {ledger}")
        return
    rows = []
    for line in open(ledger, encoding="utf-8"):
        try:
            rows.append(json.loads(line))
        except Exception:
            continue
    print(f"═══ {setcode.upper()}: {len(rows)} партий в реестре ═══")
    by_ev = {}
    for r in rows:
        by_ev.setdefault(r.get("event") or "?", []).append(r)
    for ev, rs in sorted(by_ev.items()):
        w = sum(1 for r in rs if r["result"] == "W")
        l = sum(1 for r in rs if r["result"] == "L")
        u = sum(1 for r in rs if r["result"] is None)
        print(f"  {ev}: {w}W-{l}L" + (f" (+{u} без результата)" if u else ""))
        by_deck = {}
        for r in rs:
            key = tuple(r["deck"]) if r.get("deck") else ("<колода неизвестна>",)
            by_deck.setdefault(key, []).append(r)
        for deck, drs in by_deck.items():
            w = sum(1 for r in drs if r["result"] == "W")
            l = sum(1 for r in drs if r["result"] == "L")
            head = ", ".join(d.split(" ", 1)[1] for d in list(deck)[:4])
            print(f"    {w}W-{l}L · {len(deck)} карт · {head}…"
                  if deck[0] != "<колода неизвестна>" else f"    {w}W-{l}L · колода неизвестна")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("set")
    ap.add_argument("--status", action="store_true")
    a = ap.parse_args()
    if a.status:
        status(a.set.lower())
    else:
        run(a.set.lower())
        status(a.set.lower())
    return 0


if __name__ == "__main__":
    sys.exit(main())
