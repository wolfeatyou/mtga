"""Тест телеметрии советчика (внесена 18.08.2026, JOURNAL § 8.12).

Проверяет БОЕВЫЕ функции (урок § 8.5 — тест, повторяющий логику у себя, не тест):
`draft_live.record_telemetry` пишет и дедупит, `telemetry_report.load_events` джойнит.

Негативные контроли встроены в сами проверки:
· сломается дедуп по паку → повторный вызов удвоит записи → упадёт проверка «ровно 1»;
· сломается дедуп по пику → то же для pick-записей;
· разъедется джойн pack.i == pick.i → упадёт проверка согласия.
"""
import json
import os
import sys

os.environ["MTGA_SET"] = "msh"
os.environ["MTGA_OFFLINE"] = "1"
sys.path.insert(0, os.path.expanduser("~/.claude/skills/mtg-draft-helper"))
sys.argv = ["draft_live.py", "msh"]
import draft_live as D
import telemetry_report as TR

by_id = D.load_cards()
ratings = D.load_ratings()
DRAFT = "7e1e0000cafe"        # hex-тег (гард пропускает только hex), не пересекается с реальными
path = D._telemetry_path(DRAFT)
if os.path.exists(path):
    os.remove(path)

ids = sorted(ratings.keys())[:5]
grouped = D.pack_order(ids, by_id, ratings, {}, None)
top1 = grouped[0][1][0]

def rows():
    return [json.loads(l) for l in open(path, encoding="utf-8")]

# ── 1. пак пишется один раз (дедуп по координате) ────────────────────────────
D.record_telemetry(DRAFT, 1, 1, ids, [], grouped, by_id, ratings)
D.record_telemetry(DRAFT, 1, 1, ids, [], grouped, by_id, ratings)   # повторный рендер
packs = [r for r in rows() if r["t"] == "pack"]
assert len(packs) == 1, f"дедуп пака сломан: {len(packs)} записей"
assert packs[0]["i"] == 0 and packs[0]["n"] == len(ids)
adv_name = packs[0]["adv"][0]

# ── 2. пик дописывается и тоже дедупится ─────────────────────────────────────
picks = [top1]
grouped2 = D.pack_order(ids[1:], by_id, ratings, {}, None)
D.record_telemetry(DRAFT, 1, 2, ids[1:], picks, grouped2, by_id, ratings)
D.record_telemetry(DRAFT, 1, 2, ids[1:], picks, grouped2, by_id, ratings)
rs = rows()
assert len([r for r in rs if r["t"] == "pack"]) == 2, "второй пак не записался"
pks = [r for r in rs if r["t"] == "pick"]
assert len(pks) == 1, f"дедуп пика сломан: {len(pks)}"
assert pks[0]["i"] == 0

# ── 3. джойн отчёта: пик top1 обязан читаться как согласие с советом ─────────
packs_j, picks_j = TR.load_events(path)
assert 0 in packs_j and 0 in picks_j, "джойн pack.i == pick.i разъехался"
assert packs_j[0]["adv"][0] == adv_name
assert picks_j[0] == adv_name.split(" //")[0] or picks_j[0] == adv_name, \
    f"имя пика {picks_j[0]!r} != совету {adv_name!r}"

# ── 4. телеметрия не роняет рендер при мусорных входах ───────────────────────
assert D.record_telemetry(None, 1, 3, [], [], [], by_id, ratings) is None

os.remove(path)
print("✅ ТЕЛЕМЕТРИЯ: пак и пик пишутся по разу, джойн отчёта сходится, мусор не роняет")
