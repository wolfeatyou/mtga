#!/usr/bin/env python3
"""Standalone Quick Draft (bot-draft) reader for MSH.

Premier draft is handled by draft_live.py (DO NOT TOUCH that parser).
Quick Draft logs a different event: `BotDraftDraftStatus` whose Payload holds
{DraftPack, PackNumber, PickNumber, PickedCards}. This script reads the LAST
such status from Player.log, maps grpIds -> name/GIH via the same data files,
and prints the pack sorted by GIH plus the running pool. No blocking/watch —
just a snapshot, since we're drafting in manual discussion mode.

Usage: python3 quickdraft.py [msh]
Env:   MTGA_LOG to override log path.
"""
import json, os, re, sys

SKILL = os.path.dirname(os.path.abspath(__file__))
SET = (sys.argv[1] if len(sys.argv) > 1 else "msh").lower()
LOG = os.environ.get("MTGA_LOG") or os.path.expanduser(
    "~/Library/Logs/Wizards Of The Coast/MTGA/Player.log")

# ---- load data ----
ratings = json.load(open(os.path.join(SKILL, f"17l_{SET}_premierdraft.json")))
setcards = json.load(open(os.path.join(SKILL, f"{SET}_set.json")))

by_id = {}
for r in ratings:
    mid = r.get("mtga_id")
    if mid is not None:
        by_id[int(mid)] = r
set_by_id = {}
for c in setcards:
    aid = c.get("arena_id")
    if aid is not None:
        set_by_id[int(aid)] = c

def gih(r):
    v = r.get("ever_drawn_win_rate")
    return (v * 100 if v and v < 1.5 else v) if v else None

def tier(g):
    if g is None: return "?"
    if g >= 60: return "S"
    if g >= 57.5: return "A"
    if g >= 55: return "B"
    if g >= 52.5: return "C"
    if g >= 50: return "D"
    return "F"

def info(cid):
    cid = int(cid)
    r = by_id.get(cid); s = set_by_id.get(cid)
    name = (r or {}).get("name") or (s or {}).get("name") or f"id{cid}"
    color = (r or {}).get("color") or "".join((s or {}).get("colors") or []) or "C"
    mana = (s or {}).get("mana_cost", "")
    pt = ""
    if s and s.get("power") is not None:
        pt = f"{s.get('power')}/{s.get('toughness')}"
    g = gih(r) if r else None
    iwd = (r or {}).get("drawn_improvement_win_rate")
    if iwd is not None and abs(iwd) < 1.5: iwd *= 100
    oh = (r or {}).get("opening_hand_win_rate")
    if oh is not None and oh < 1.5: oh *= 100
    alsa = (r or {}).get("avg_seen")
    text = (s or {}).get("oracle_text", "").replace("\n", " | ")
    tl = (s or {}).get("type_line", "")
    return dict(id=cid, name=name, color=color, mana=mana, pt=pt,
                gih=g, iwd=iwd, oh=oh, alsa=alsa, text=text, tl=tl)

# ---- find last BotDraftDraftStatus payload ----
raw = open(LOG, "r", errors="ignore").read()
# payloads look like: "Payload":"{...escaped json...}" containing "DraftPack"
payloads = re.findall(r'"Payload":"(\{.*?DraftPack.*?\})"', raw)
if not payloads:
    print("Нет BotDraftDraftStatus с DraftPack в логе — открой пак в Arena.")
    sys.exit(0)
# also capture standalone (non-Payload-wrapped) statuses if any
last = payloads[-1]
# the captured group is escaped JSON (\" for quotes); unescape
decoded = json.loads('"' + last.replace('"', '\\"').replace('\\\\"', '\\"') + '"') \
    if False else json.loads(last.encode().decode("unicode_escape"))
# robust decode fallback
try:
    status = json.loads(last.encode().decode("unicode_escape"))
except Exception:
    status = json.loads(last.replace('\\"', '"').replace('\\\\', '\\'))

pack = [int(x) for x in status.get("DraftPack", [])]
picked = [int(x) for x in status.get("PickedCards", [])]
pn = status.get("PackNumber", 0) + 1
pk = status.get("PickNumber", 0) + 1
ev = status.get("EventName", "")

# ---- print pack sorted by GIH ----
print(f"===== QUICK DRAFT [{SET.upper()}] {ev}  (Пак {pn}, пик {pk}) — {len(pack)} карт =====\n")
rows = [info(c) for c in pack]
rows.sort(key=lambda x: (x["gih"] is None, -(x["gih"] or 0)))
for x in rows:
    g = f"{x['gih']:.1f}" if x["gih"] is not None else "  ? "
    iwd = f"{x['iwd']:+.1f}" if x["iwd"] is not None else "  ? "
    oh = f"{x['oh']:.1f}" if x["oh"] is not None else "  ? "
    alsa = f"{x['alsa']:.1f}" if x["alsa"] is not None else " ? "
    print(f"  [{tier(x['gih'])}|GIH {g}|IWD {iwd}|OH {oh}|ALSA {alsa}]  "
          f"{x['name']}  ·  {x['pt']:>4}  ·  {x['color']:<3}  ·  {x['mana']}")
    tl = x.get("tl", "")
    typ = tl.split("—")[0].strip() if tl else ""
    if x.get("text"):
        print(f"        └ {typ}: {x['text']}")
    elif typ:
        print(f"        └ {typ}")

# ---- pool ----
if picked:
    prows = [info(c) for c in picked]
    from collections import Counter
    cc = Counter()
    curve = Counter()
    for x in prows:
        for ch in (x["color"] or "C"):
            cc[ch] += 1
    names = [x["name"] for x in prows]
    print(f"\n----- ПУЛ ({len(picked)}) -----")
    print("  " + ", ".join(names))
    print("  Цвета:", " ".join(f"{k}:{v}" for k, v in cc.most_common()))
else:
    print("\n----- ПУЛ (0) -----  (первый пик)")
