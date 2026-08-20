#!/usr/bin/env python3
"""CLOCK-симуляция голдфиша (`draft_goldfish.clock_sim`, § 8.23) — часы колоды.

ЗАЧЕМ. «Чем колода заканчивает партию» до § 8.17 не спрашивал ни один прибор (колода 0-3
с нулём нанесённого урона прошла все оси «в диапазоне»); ось big сделала это статикой,
clock_sim делает динамикой: медианный ход, на котором суммарный урон достигает 20 —
на реальной манабазе, с мулиганами, саммон-сикнесс и haste. Это ВЕРХНЯЯ ГРАНИЦА темпа
(оппонент не мешает), сравнивать ей можно кандидатов одного пула и колоду с медианой
своей пары (<set>_clocks.json из --calibrate).

Проверки — ИНВАРИАНТЫ на синтетических колодах (не снапшоты чисел: модель может
уточняться, инварианты обязаны выживать):
  1. пустая доска ≤ стойка — поточечно (урон через блокеров не может прийти раньше);
  2. полностью пробивающая колода: оба режима совпадают поточечно (блокерам нечего есть);
  3. монотонность по силе: тела 4/х при том же cmc убивают раньше тел 2/х;
  4. негативный контроль: колода с силой 0 не убивает никогда (все 99).

НЕГАТИВНЫЙ КОНТРОЛЬ ПРОВЕДЁН 20.08.2026 (правило § 1): обнуление силы в кейсе 4 — это
он и есть, встроенный; дополнительно вручную ломали суммирование урона (dmg_o -= вместо
+=) — падают кейсы 1 и 3.
"""
import os
import random
import sys

os.environ["MTGA_SET"] = "hob"
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from draft_goldfish import clock_sim  # noqa: E402

fails = []


def check(cond, msg):
    print(("  ✅ " if cond else "  ❌ ") + msg)
    if not cond:
        fails.append(msg)


def synth_deck(power, n=23, cmc=2, evasive=False, lands=17):
    cre = {"name": f"c{power}", "land": False, "cmc": cmc, "pips": [], "creature": True,
           "power": power, "evasive": evasive, "haste": False, "removal": False,
           "fixer": None, "bomb": False}
    land = {"name": "Forest", "land": True, "produces": {"G"}, "tapped": False}
    return [dict(cre) for _ in range(n)] + [dict(land) for _ in range(lands)]


def med(v):
    return sorted(v)[len(v) // 2]


N = 800

print("1) пустая доска ≤ стойка (поточечно)")
random.seed(7)
ko, kw = clock_sim(synth_deck(2), N)
check(all(o <= w for o, w in zip(ko, kw)), "урон через блокеров никогда не раньше пустой доски")
check(med(kw) > med(ko), f"2 блокера замедляют наземную колоду (медианы {med(ko)} → {med(kw)})")

print("2) полностью пробивающая колода — режимы совпадают")
random.seed(7)
ko_e, kw_e = clock_sim(synth_deck(3, evasive=True), N)
check(ko_e == kw_e, "у колоды из одних пробивающих блокеры ничего не съедают")

print("3) монотонность по силе (тот же cmc)")
random.seed(7)
ko4, _ = clock_sim(synth_deck(4), N)
check(med(ko4) < med(ko), f"тела 4/x убивают раньше тел 2/x (медианы {med(ko4)} < {med(ko)})")

print("4) негативный контроль: сила 0 → убийств нет")
random.seed(7)
ko0, kw0 = clock_sim(synth_deck(0), 200)
check(all(x == 99 for x in ko0 + kw0), "колода без силы не набирает 20 никогда")

print()
if fails:
    print(f"❌ ПРОВАЛЕНО {len(fails)}: " + " | ".join(fails))
    sys.exit(1)
print("✅ все проверки пройдены")
