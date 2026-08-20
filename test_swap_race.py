#!/usr/bin/env python3
"""swap_test.py и race_card.py (§ 8.25) — смоук + негативные контроли.

Оба тула — обвязка над уже тестированными приборами (simulate/clock_sim/lint/sig_of),
поэтому здесь проверяется ПРОВОДКА: дельта считается и имеет правильный знак, вердикты
печатаются, ошибки входа громкие. Фикстура — hob_ur_eba1b036_fail.txt (стабильна, § 8.18).

Негативные контроли встроены кейсами 2 и 4 (неверный вход обязан падать громко);
дополнительно 20.08.2026 вручную: подмена rating_of на константу зануляет GIH-дельту —
кейс 1 падает."""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FIX = os.path.join(HERE, "hob_ur_eba1b036_fail.txt")
fails = []


def check(cond, msg):
    print(("  ✅ " if cond else "  ❌ ") + msg)
    if not cond:
        fails.append(msg)


def run(*args):
    return subprocess.run([sys.executable] + list(args), cwd=HERE,
                          capture_output=True, text=True, timeout=300)

print("1) swap_test: замена слабой карты на сильную даёт положительную GIH-дельту")
r = run("swap_test.py", FIX, "--cut", "Old Thrush", "--add", "Smaug, the Great Calamity",
        "--set", "hob", "--sims", "400")
check(r.returncode == 0 and "SWAP:" in r.stdout, "отработал и напечатал шапку")
gl = next((l for l in r.stdout.splitlines() if l.startswith("GIH мейна")), "")
import re as _re
_m = _re.search(r"\(([+-][\d.]+)\)", gl)
check(_m is not None and float(_m.group(1)) > 0.05,
      f"дельта GIH положительная и ненулевая ({gl.split(':')[-1].strip()})")
check("CLOCK:" in r.stdout and "линт:" in r.stdout, "clock и линт в отчёте")

print("2) swap_test: карта, которой нет в мейне, — громкая ошибка")
r = run("swap_test.py", FIX, "--cut", "Bilbo, Luckwearer", "--add", "Old Thrush", "--set", "hob")
check(r.returncode != 0 and "нет в мейне" in (r.stdout + r.stderr), "SystemExit с причиной")

print("3) race_card: вердикт по каждой паре меты")
r = run("race_card.py", FIX, "--set", "hob", "--sims", "400")
check(r.returncode == 0 and "RACE-КАРТОЧКА" in r.stdout, "отработал")
rows = [l for l in r.stdout.splitlines()
        if ("ГОНЩИК" in l or "ЗАЩИТНИК" in l or "ровня" in l)]
check(len(rows) >= 12, f"вердикты по ≥12 парам ({len(rows)})")
check("эквип/бёрн/amass" in r.stdout, "ограничение § 8.23 напечатано")

print("4) race_card: без калибровки сета — громкая ошибка")
r = run("race_card.py", FIX, "--set", "msh")
check(r.returncode != 0 and "msh_clocks.json" in (r.stdout + r.stderr),
      "нет msh_clocks.json → SystemExit с подсказкой --calibrate")

print()
if fails:
    print(f"❌ ПРОВАЛЕНО {len(fails)}: " + " | ".join(fails))
    sys.exit(1)
print("✅ все проверки пройдены")
