#!/usr/bin/env python3
"""Досье пула (`pool_dossier.py`) — линии, связки в пуле, флаги частоты/потолка/ловушек.

ЗАЧЕМ ТЕСТ (20.08.2026, вместе с самим прибором — mode_build.md § МУЛЬТИСБОРКА).
Досье — вход строителей оркестрированной сборки и деталь гейта (веер/одиночка), то есть
его ошибка тиражируется во ВСЕ кандидаты сразу. Классы багов, которые здесь стерегутся,
уже случались в других приборах:
  · копия логики у потребителя (§ 8.5) — досье обязано звать find_traps.sig_of/castable
    и регексы deck_profile, и тест проверяет СОВПАДЕНИЕ с их прямым вызовом;
  · сопоставление имён (§ 5.5, § 8.3, § 8.5 — четыре случая одного бага);
  · гибридный пип как принадлежность, а не доступ (§ 5.3, § 8.16 ②).

ФИКСТУРА — `fixture_hob_pool_3657e8ab.txt` (копия пула BG-драфта 20.08). Рабочий файл
pools/… ротируется/затирается — файл-объект теста обязан быть фикстурой (§ 8.18).

РУЧНЫЕ ОЖИДАНИЯ сняты по составу фикстуры и hob_traps.json от 20.08.2026:
  · тел силой ≥4, кастуемых в BG: Chief Warg's Company 5/3 · Gollum Silent Slinker 4/3 ·
    Large Bear 5/5 · Ordinary Bear 4/5 ×3 · Boughside Wanderers 4/4 · Cantankerous
    Keepers 4/3 = 8 при медиане пары 4 → запас +4;
  · связка Wood Elves + Thranduil (lift 3.3) — обе половины в пуле;
  · анти-связка Stir Up Trouble + Large Bear — обе половины в пуле;
  · Mirkwood Nurturer: в пуле ×4, у BG-победителей потолок 3, частота 30%.

НЕГАТИВНЫЙ КОНТРОЛЬ ПРОВЕДЁН 20.08.2026 (правило § 1: зелёный тест без него ничего
не доказывает): (а) подмена sig_of на нулевую сигнатуру роняет проверки линий;
(б) выкидывание Wood Elves из пула роняет проверку связки (кейс 5 сам это и делает —
он встроенный негативный контроль индексации рёбер).
"""
import json
import os
import sys
from collections import Counter

os.environ["MTGA_SET"] = "hob"
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import find_traps as FT          # noqa: E402
import pool_dossier as PD        # noqa: E402

FIX = os.path.join(HERE, "fixture_hob_pool_3657e8ab.txt")
fails = []


def check(cond, msg):
    print(("  ✅ " if cond else "  ❌ ") + msg)
    if not cond:
        fails.append(msg)


cards = json.load(open(os.path.join(HERE, "hob_set.json"), encoding="utf-8"))
traps = json.load(open(os.path.join(HERE, "hob_traps.json"), encoding="utf-8"))
combos = json.load(open(os.path.join(HERE, "hob_combos.json"), encoding="utf-8"))
by_key = PD.index_cards(cards)
pool = PD.read_pool(FIX)
pidx = PD.pool_index(pool, by_key)

print("1) пул прочитан и карты сопоставлены")
check(sum(n for n, *_ in pidx) == 42, "42 карты в пуле (мейн+сайд слиты)")
check(all(c is not None for _, _, c, _ in pidx), "все имена нашлись в hob_set.json")

print("2) линии: пул считается ТЕМ ЖЕ sig_of, которым посчитаны медианы routes")
bg_cnt = PD.castable_counts(pidx, "BG")
sig = FT.sig_of(bg_cnt, cards)
check(sig["big"] == 8, f"тел ≥4 в BG-кастуемой части = 8 (ручной пересчёт), получил {sig['big']}")
rows = {r["pair"]: r for r in PD.lane_rows(pidx, cards, traps, PD.A.load_ratings("hob"))}
bg = rows["BG"]
check(bg["margins"]["big"] == sig["big"] - traps["routes"]["BG"]["big"] == 4,
      f"запас маршрута тел≥4 = сигнатура − медиана пары = +4, получил {bg['margins']['big']}")
check(bg["feasible"] == 4, f"BG: достижимы 4/4 маршрута, получил {bg['feasible']}")
check(bg["margins"]["wide"] == min(sig["cre"] - traps["routes"]["BG"]["cre"],
                                   sig["cheap"] - traps["routes"]["BG"]["cheap"]),
      "ширина = min(существа, дешёвые) против медиан")

print("3) гибрид даёт ДОСТУП, а не принадлежность (§ 5.3 / § 8.16 ②)")
check("thranduilsindarinliege" in bg_cnt, "Thranduil {G/U} кастуем в BG (зелёная половина)")
check("thranduilsindarinliege" not in PD.castable_counts(pidx, "BR"),
      "…и НЕ кастуем в BR (ни одной половины)")

print("4) частота/потолок/ловушки из played-блока")
flags, share, cap = PD.card_flags("mirkwoodnurturer", "BG", traps)
check(share == traps["played"]["mirkwoodnurturer"]["pairs"]["BG"],
      f"частота Nurturer в BG из таблицы победителей ({share})")
check(cap == 3, f"потолок копий Nurturer в BG = 3, получил {cap}")
tflags, _, _ = PD.card_flags("bardkingofdale", "WU", traps)
check("⚠ЛОВУШКА-СЕТА" in tflags, "Bard, King of Dale помечен ловушкой сета (0/298)")

print("5) связки: ребро живёт только когда ОБЕ половины в пуле")
edges, anti = PD.combo_edges(pidx, combos)
names = {tuple(sorted(FT.norm(x) for x in e["cards"])) for e in edges}
check(("thranduilsindarinliege", "woodelves") in {tuple(sorted(t)) for t in names},
      "ребро Wood Elves ↔ Thranduil найдено (lift 3.3)")
anti_names = {tuple(sorted(FT.norm(x) for x in a["cards"])) for a in anti}
check(("largebear", "stiruptrouble") in anti_names, "анти-ребро Stir Up Trouble + Large Bear найдено")
pool_wo = [(n, nm) for n, nm in pool if nm != "Wood Elves"]
edges_wo, _ = PD.combo_edges(PD.pool_index(pool_wo, by_key), combos)
check(all("woodelves" not in {FT.norm(x) for x in e["cards"]} for e in edges_wo),
      "негативный контроль: без Wood Elves ребро исчезает")

print("6) рендер: потолок копий печатается на карте с перебором")
import io
from contextlib import redirect_stdout
buf = io.StringIO()
with redirect_stdout(buf):
    PD.render(FIX, "hob", ["BG"])
text = buf.getvalue()
check("⚠×4>потолка" in text and "Mirkwood Nurturer" in text,
      "⚠×4>потолка у Mirkwood Nurturer (ошибка P3P2 § 8.18 была бы видна в досье)")
check("Reach, deathtouch" in text,
      "полный оракл-текст печатается под картой (Attercop; сет новее кат-оффа модели)")
check("It's an artifact with" not in text,
      "ремайндеры в скобках срезаны из оракл-текстов")
check("⚠ЛОВУШКА" not in text.split("КАРТЫ ПУЛА")[1].split("СВЯЗКИ")[0].replace("⚠НЕ-В-ЭТОЙ-ПАРЕ", "")
      if "КАРТЫ ПУЛА" in text else True,
      "ловушек сета в этом пуле нет — флаг не печатается зря")

print("7) режим --deck: скорборд готового мейна (вход судьи § МУЛЬТИСБОРКА)")
import tempfile
_deck = tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8")
# мини-мейн из фикстуры: 3 тела ≥4 (медиана BG 4 → маршрут закрыт быть не должен) + перебор копий
_deck.write("Deck\n3 Ordinary Bear\n1 Large Bear\n2 Nasty Little Rabbit\n8 Forest\n")
_deck.close()
buf2 = io.StringIO()
with redirect_stdout(buf2):
    PD.deck_check(_deck.name, "hob", "BG")
t2 = buf2.getvalue()
check("тел≥4 4 (✔" in t2, "deck_check считает тела ≥4 тем же sig_of (3 Bear + Large = 4, медиана 4 ✔)")
check("⚠×3>потолка(≤2)" in t2, "deck_check ловит перебор копий (Ordinary Bear ×3 при потолке 2)")
os.unlink(_deck.name)

print()
if fails:
    print(f"❌ ПРОВАЛЕНО {len(fails)}: " + " | ".join(fails))
    sys.exit(1)
print("✅ все проверки пройдены")
