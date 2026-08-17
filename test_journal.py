"""Сверка JOURNAL.md с живыми приборами (внесён 17.08.2026).

ЗАЧЕМ. Журнал — компас: по нему решают, что менять дальше. Но числа в нём привязаны к
состоянию приборов, а приборы правятся. За один день 17.08 две правки (`reach` отделён от
пробития, гибрид перестал создавать цвет) сдвинули две оси из семи, и все записи, сделанные
до них, стали неверными молча. Ровно так рождаются выводы, которые потом приходится
отзывать — этот файл ловит расхождение раньше, чем оно попадёт в решение.

ЧТО ПРОВЕРЯЕТСЯ:
  · все коммиты, упомянутые в журнале, существуют в истории;
  · медианы и квартили семи осей § 2.1 совпадают с тем, что сейчас считает build_audit;
  · доли цветов и сплеша § 2.2 совпадают с тем, что сейчас считает deck_profile;
  · размер выборки в журнале равен реальному числу листов в ref_decks/<set>/.

ЧТО НЕ ПРОВЕРЯЕТСЯ: выводы и интерпретации. Их проверяют экспериментом, а не тестом.
"""
import os, re, subprocess, sys, glob, statistics

HERE = os.path.expanduser("~/.claude/skills/mtg-draft-helper")
sys.path.insert(0, HERE)
os.environ["MTGA_SET"] = "hob"
os.environ.setdefault("MTGA_OFFLINE", "1")

import build_audit as A  # noqa: E402
import deck_profile as P  # noqa: E402

J = open(os.path.join(HERE, "JOURNAL.md"), encoding="utf-8").read()
fails = []


def check(cond, msg):
    print(("   ✅ " if cond else "   ❌ ") + msg)
    if not cond:
        fails.append(msg)


def row(label):
    """Строка таблицы журнала: «| ось | медиана | q1–q3 | ...». Жирное начертание не мешает."""
    m = re.search(rf"^\|\s*\*{{0,2}}{re.escape(label)}\*{{0,2}}[^|]*\|\s*\*{{0,2}}(\d+)\*{{0,2}}\s*"
                  rf"\|\s*(\d+)–(\d+)", J, re.M)
    return (m.group(1), m.group(2), m.group(3)) if m else None


print("=" * 76)
print("A. коммиты, упомянутые в журнале, существуют")
hashes = set(re.findall(r"`([0-9a-f]{7})`", J))
real = set(subprocess.run(["git", "-C", HERE, "log", "--format=%h", "-200"],
                          capture_output=True, text=True).stdout.split())
missing = hashes - real
check(not missing, f"{len(hashes)} коммитов на месте" + (f" — потерялись: {missing}" if missing else ""))

print("\nB. оси § 2.1 совпадают с build_audit")
db, rat = A.load_db(), A.load_ratings("hob")
refs = A.load_refs("hob", db, rat)
JOURNAL_LABEL = {"ломателей стойки": "пробивающих стойку"}
for key, lab in A.AXES:
    v = sorted(r[key] for r in refs if r[key] is not None)
    if not v:
        continue
    live = (f"{statistics.median(v):.0f}", str(v[len(v) // 4]), str(v[3 * len(v) // 4]))
    got = row(JOURNAL_LABEL.get(lab, lab))
    check(got == live, f"{JOURNAL_LABEL.get(lab, lab):<20} журнал {got} · прибор {live}")

print("\nC. цвета и сплеш § 2.2 совпадают с deck_profile")
files = sorted(glob.glob(os.path.join(HERE, "ref_decks", "hob", "*.txt")))
ms = [P.metrics(f, db, rat) for f in files]
tot = len(ms)
two = round(100 * sum(1 for m in ms if len(m["colors"]) == 2) / tot)
three = round(100 * sum(1 for m in ms if len(m["colors"]) == 3) / tot)
spl = round(100 * sum(1 for m in ms if m["splash"]) / tot)
check(f"{two}%" in J, f"строго 2 цвета: {two}%")
check(f"{three}%" in J, f"3 цвета: {three}%")
check(f"{spl}%" in J, f"со сплешем: {spl}%")
check(str(tot) in J, f"размер выборки: {tot} листов")

print("=" * 76)
if fails:
    print(f"❌ ЖУРНАЛ РАЗОШЁЛСЯ С ПРИБОРАМИ ({len(fails)}):")
    for f in fails:
        print("   ·", f)
    print("\n   Не «поправь тест». Числа в JOURNAL.md § 2 устарели после правки приборов —")
    print("   пересчитай их и обнови журнал, иначе решения будут приниматься по мёртвым числам.")
    sys.exit(1)
print("✅ ЖУРНАЛ СОГЛАСОВАН С ПРИБОРАМИ — числам § 2 можно верить.")
