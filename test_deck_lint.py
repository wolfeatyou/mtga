#!/usr/bin/env python3
"""Линтер мёртвых текстов (`deck_lint.py`, § 8.24).

Каждая проверка — ПАРА: предупреждение загорается на листе без включателей и ГАСНЕТ,
когда включатели добавлены (вторая половина пары = встроенный негативный контроль
самой проверки). Дополнительный ручной негативный контроль проведён 20.08.2026:
подмена subtype_count на «всегда 99» гасит трайбал/эквип-предупреждения — кейсы 1 и 4
падают.

Фикстуры — синтетические листы из реальных карт HOB (по 40 карт не требуется:
линтер читает мейн как есть)."""
import os
import sys
import tempfile

os.environ["MTGA_SET"] = "hob"
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import deck_lint as L            # noqa: E402

fails = []


def check(cond, msg):
    print(("  ✅ " if cond else "  ❌ ") + msg)
    if not cond:
        fails.append(msg)


def lint_of(*lines):
    f = tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8")
    f.write("Deck\n" + "\n".join(lines) + "\n")
    f.close()
    try:
        return L.lint(f.name, "hob")
    finally:
        os.unlink(f.name)


BASE = ["8 Forest", "8 Swamp"]

print("1) трайбал-лорд: Thranduil без эльфов / с эльфами")
w = lint_of("1 Thranduil, Sindarin Liege", "3 Ordinary Bear", *BASE)
check(any("Thranduil" in x and "Elf" in x for x in w), "без эльфов — предупреждение горит")
w = lint_of("1 Thranduil, Sindarin Liege", "3 Mirkwood Nurturer", "1 Wood Elves", *BASE)
check(not any(x.startswith("Thranduil") for x in w), "с 4 эльфами — гаснет")

print("2) земля не цветов колоды: Lake-town в BG")
w = lint_of("1 Lake-town", "3 Ordinary Bear", "3 Stir Up Trouble", *BASE)
check(any("Lake-town" in x and "ни одного цвета" in x for x in w), "W/U-земля в BG — горит")
w = lint_of("3 Ordinary Bear", "3 Stir Up Trouble", *BASE)
check(not any("Lake-town" in x for x in w), "без Lake-town — тишина")

print("3) сак-кост: Stir Up Trouble без фодера / с фодером")
w = lint_of("2 Stir Up Trouble", "3 Ordinary Bear", "1 Large Bear", *BASE)
check(any("Stir Up" in x and "фодера" in x for x in w), "только толстяки — горит")
w = lint_of("2 Stir Up Trouble", "2 Attercop", "2 Nasty Little Rabbit",
            "1 Front Porch Sentries", *BASE)
check(not any(x.startswith("Stir Up") for x in w), "5 дешёвых тел (Sentries платит при смерти) — гаснет")

print("4) условная сила: Wargling (Ferocious) без тел 4+ / с телами")
w = lint_of("1 Wargling", "3 Attercop", "2 Nasty Little Rabbit", *BASE)
check(any("Wargling" in x and "сила 4+" in x for x in w), "без тел 4+ — горит")
w = lint_of("1 Wargling", "3 Ordinary Bear", "1 Large Bear", *BASE)
check(not any(x.startswith("Wargling") for x in w), "с 4 телами 4+ — гаснет")

print("5) условие «two or more other»: Chief Warg's Company")
w = lint_of("1 Chief Warg's Company", "3 Ordinary Bear", *BASE)
check(any("Chief Warg" in x and "Wolf" in x for x in w), "без Волков — горит")
w = lint_of("1 Chief Warg's Company", "1 Wargling", "2 Duskwatch Hunter", *BASE)
check(not any(x.startswith("Chief Warg") for x in w), "с 3 Волками — гаснет")

print()
if fails:
    print(f"❌ ПРОВАЛЕНО {len(fails)}: " + " | ".join(fails))
    sys.exit(1)
print("✅ все проверки пройдены")
