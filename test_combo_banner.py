"""Регресс-тест ⚑ СВЯЗКА (внесён 16.08.2026).

ЗАЧЕМ БАННЕР. 31 трофейный лист использовался на сборке (build_audit) и в подготовке
(learn.py), но в момент пика не участвовал вообще — прямая претензия пользователя.
При этом главного знания нет ни в GIH, ни в частотной статистике: ЗАЧЕМ карта в колоде,
с чем она работает. Частота говорит «эту играют 4 из 4»; связка говорит «она достраивает
то, что у тебя уже есть» — и только второе можно применить в конкретном паке.

ЧТО ПРОВЕРЯЕТСЯ:
  A. горит, когда часть связки в пуле, а недостающая — в паке;
  B. молчит, когда в паке нет недостающей детали (нечего советовать);
  C. молчит, когда связка целиком уже собрана в пуле (совет бессмысленен);
  D. ранжирует по числу трофейных колод и не заваливает вывод (максимум 3 строки);
  E. молчит без файла связок — сет без разбора не должен падать.
"""
import os, sys
os.environ["MTGA_SET"] = "hob"
os.environ["MTGA_OFFLINE"] = "1"
sys.path.insert(0, os.path.expanduser("~/.claude/skills/mtg-draft-helper"))
sys.argv = ["draft_live.py", "hob"]
import draft_live as D

by, rat = D.load_cards(), D.load_ratings()
fails = []


def cid(name):
    for i, c in by.items():
        if c["name"].split(" //")[0].lower() == name.lower():
            return i
    raise SystemExit("нет карты: " + name)


def check(cond, msg):
    print(("   ✅ " if cond else "   ❌ ") + msg)
    if not cond:
        fails.append(msg)


A, B, C = "Bilbo Baggins, Burglar", "Enchanted River's Grasp", "Quarrel"
D._COMBOS = {"combos": [
    {"cards": [A, B], "why": "фильтрация ищет ответ на большое тело", "decks": 4, "pair": "UG"},
    {"cards": [A, C], "why": "тестовая слабая связка", "decks": 1, "pair": "UG"},
]}

print("=" * 74)
print("A. часть связки в пуле, недостающая — в паке")
out = D.combo_banner([cid(B), cid(C)], by, rat, [cid(A)])
print("\n".join("   " + x for x in out) or "   (молчит)")
check(any(B in x for x in out), "советует взять недостающую деталь")
check(any("4 троф" in x for x in out), "называет, в скольких трофейных колодах связка встречалась")

print("\nB. недостающей детали в паке нет")
out = D.combo_banner([cid("Attercop"), cid("Wargling")], by, rat, [cid(A)])
print("\n".join("   " + x for x in out) or "   (молчит)")
check(not out, "молчит — советовать нечего")

print("\nC. связка уже собрана в пуле целиком")
out = D.combo_banner([cid("Attercop")], by, rat, [cid(A), cid(B), cid(C)])
print("\n".join("   " + x for x in out) or "   (молчит)")
check(not out, "молчит — связка уже есть")

print("\nD. порядок и лимит строк")
D._COMBOS = {"combos": [
    {"cards": [A, B], "why": "редкая", "decks": 1, "pair": "UG"},
    {"cards": [A, C], "why": "частая", "decks": 9, "pair": "UG"},
    {"cards": [A, "Attercop"], "why": "средняя", "decks": 5, "pair": "UG"},
    {"cards": [A, "Wargling"], "why": "ещё", "decks": 3, "pair": "UG"},
]}
out = D.combo_banner([cid(B), cid(C), cid("Attercop"), cid("Wargling")], by, rat, [cid(A)])
print("\n".join("   " + x for x in out))
check(len(out) <= 3, f"не больше трёх строк (получено {len(out)})")
check(out and "частая" in out[0], "самая частая связка — первой")

print("\nE. слабый lift не советуется")
D._COMBOS = {"combos": [
    {"cards": [A, B], "why": "совместность объясняется частотой", "decks": 40, "lift": 1.2},
    {"cards": [A, C], "why": "настоящая связка", "decks": 9, "lift": 2.6},
]}
out = D.combo_banner([cid(B), cid(C)], by, rat, [cid(A)])
print("\n".join("   " + x for x in out) or "   (молчит)")
check(out and all(B not in x for x in out), "связка с lift 1.2 не показана (порог 1.5)")
check(any(C in x for x in out), "связка с lift 2.6 показана")

print("\nF. связка без поля lift — показывается (нет данных ≠ слабая)")
D._COMBOS = {"combos": [{"cards": [A, B], "why": "не мерили", "decks": 5}]}
check(D.combo_banner([cid(B)], by, rat, [cid(A)]), "показана")

print("\nG. файла связок нет")
D._COMBOS = {}
check(D.combo_banner([cid(B)], by, rat, [cid(A)]) == [], "молчит без данных, не падает")

print("=" * 74)
if fails:
    print(f"❌ ПРОВАЛЕНО {len(fails)}:")
    for f in fails:
        print("   ·", f)
    sys.exit(1)
print("✅ ВСЕ ПРОВЕРКИ ПРОШЛИ — знание из трофейных колод работает в момент пика,")
print("   а не только на сборке.")
