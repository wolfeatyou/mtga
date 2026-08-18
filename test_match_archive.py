"""Тест учёта партий (внесён 18.08.2026, JOURNAL § 8.13).

Боевой код (`match_archive.collect` / `run`) на синтетическом логе-фикстуре:
сборка записи (результат, seat, событие, колода из ближайшего CourseDeck),
фильтр чужих событий, идемпотентность (повторный run → +0), архив сегмента.

Негативный контроль встроен: сломается дедуп → второй run() допишет строки →
упадёт проверка «+0»; разъедется ассоциация CourseDeck → упадёт проверка колоды.
"""
import gzip
import json
import os
import shutil
import sys
import tempfile

os.environ["MTGA_SET"] = "msh"
sys.path.insert(0, os.path.expanduser("~/.claude/skills/mtg-draft-helper"))
import match_archive as MA
import match_watch as mw

MID1 = "aaaa1111-0000-0000-0000-000000000001"
MID2 = "bbbb2222-0000-0000-0000-000000000002"
FIXTURE = (
    '8/18/2026 10:00:00 blah\n'
    '"InternalEventName":"PremierDraft_MSH_20260601"\n'
    '"CourseDeck":{"MainDeck":[{"cardId":92070,"quantity":2},{"cardId":92203,"quantity":1}]}\n'
    f'"matchID":"{MID1}","gameNumber":1\n'
    '"systemSeatIds":[1] "turnNumber":5 "turnNumber":9\n'
    '"winningTeamId":1\n'
    f'"matchID":"{MID1}","gameNumber":2\n'
    '"systemSeatIds":[1] "turnNumber":7\n'
    '"winningTeamId":2\n'
    '"InternalEventName":"Ladder"\n'
    '"CourseDeck":{"MainDeck":[{"cardId":11111,"quantity":4}]}\n'
    f'"matchID":"{MID2}","gameNumber":1\n'
    '"systemSeatIds":[2]\n'
    '"winningTeamId":2\n'
)

tmp = tempfile.mkdtemp(prefix="ma_test_")
orig_read, orig_ledger, orig_logs = mw.read_logs, MA.LEDGER_DIR, MA.LOGS_DIR
mw.read_logs = lambda: FIXTURE
MA.LEDGER_DIR = os.path.join(tmp, "matches")
MA.LOGS_DIR = os.path.join(tmp, "logs")
try:
    new, arch = MA.run("msh", quiet=True)
    assert new == 2, f"ожидались 2 MSH-партии, взято {new} (Ladder-матч обязан отсечься)"
    rows = [json.loads(l) for l in open(os.path.join(MA.LEDGER_DIR, "msh_ledger.jsonl"))]
    assert [r["result"] for r in rows] == ["W", "L"], rows
    assert rows[0]["seat"] == 1 and rows[0]["turns"] == 9
    assert rows[0]["event"] == "PremierDraft_MSH_20260601"
    assert rows[0]["deck"] and rows[0]["deck"][0].startswith("2 "), rows[0]["deck"]
    assert rows[0]["ts"] and "2026" in rows[0]["ts"]
    # идемпотентность = дедуп (негативный контроль: сломай known-набор — тут упадёт)
    new2, _ = MA.run("msh", quiet=True)
    assert new2 == 0, f"повторный run добавил {new2} — дедуп сломан"
    # архив сегмента существует и содержит матч
    p = os.path.join(MA.LOGS_DIR, MID1[:8] + ".log.gz")
    assert os.path.exists(p) and MID1 in gzip.open(p, "rt").read()
finally:
    mw.read_logs = orig_read
    MA.LEDGER_DIR, MA.LOGS_DIR = orig_ledger, orig_logs
    shutil.rmtree(tmp, ignore_errors=True)
print("✅ УЧЁТ ПАРТИЙ: запись/результат/колода/фильтр событий/дедуп/архив — всё сходится")
