#!/usr/bin/env python3
"""card_context.py (§ 8.29) — условные частоты и улики против слепоты частоты к связкам.

Проверки структурные (конкретные числа/со-карты дрейфуют с популяцией — урок § 8.27
про хардкоды): секции A/B/C/D печатаются, условные частоты несут n, неизвестная карта
падает громко. Негативный контроль встроен кейсом 2."""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
fails = []


def check(cond, msg):
    print(("  ✅ " if cond else "  ❌ ") + msg)
    if not cond:
        fails.append(msg)


print("1) смоук: Old Thrush по всей популяции")
r = subprocess.run([sys.executable, "card_context.py", "Old Thrush", "--set", "hob"],
                   cwd=HERE, capture_output=True, text=True, timeout=600)
check(r.returncode == 0 and "КОНТЕКСТ: Old Thrush" in r.stdout, "отработал")
check("безусловно: стоит в" in r.stdout, "секция A: безусловная частота")
check("листы-улики" in r.stdout, "секция B: листы-свидетели")
check("условные частоты по фичам" in r.stdout and "сплеш есть" in r.stdout,
      "секция C: условные частоты с n")
check("со-карты" in r.stdout and "×" in r.stdout, "секция D: со-карты с lift")
check("не пороги" in r.stdout, "дисклеймер о малых n печатается")

print("2) негативный контроль: неизвестная карта — громкая ошибка")
r = subprocess.run([sys.executable, "card_context.py", "Black Lotus", "--set", "hob"],
                   cwd=HERE, capture_output=True, text=True, timeout=120)
check(r.returncode != 0 and "не найдена" in (r.stdout + r.stderr), "SystemExit с причиной")

print()
if fails:
    print(f"❌ ПРОВАЛЕНО {len(fails)}: " + " | ".join(fails))
    sys.exit(1)
print("✅ все проверки пройдены")
