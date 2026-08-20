"""Ось «ЧЕМ УБИВАЮ» — тела силой ≥4 (заведена 20.08.2026 по драфту eba1b036, счёт 0-3).

ПОВОД. Колода в двух доигранных партиях нанесла РОВНО НОЛЬ урона (оппонент оба раза
ушёл с 20 на 22), а все восемь осей аудита показывали «в диапазоне»: существ 14,
эвейжн 4 карты, суммарная сила 34. Ни один прибор не спрашивал, ЧЕМ колода заканчивает
партию. Эвейжн-счётчик поймать это не мог по построению — он считает КАРТЫ, и
`Old Thrush` 1/2 весит в нём столько же, сколько `Smaug` 5/5; та колода числилась
по нему в «верхних 10% популяции».

ЧТО ИЗМЕРЕНО (298 трофейных листов HOB):
  · тел силой ≥4 — норма СИЛЬНО зависит от пары: WU медиана 0, UB 2, UR 4, BR 6, RG 7;
  · корреляция «тел силой ≥4» ↔ «существ cmc≤2» = −0.28 — победители РАЗМЕНИВАЮТ
    одно на другое: листы с ≤4 дешёвыми телами держат медиану 4 крупных, листы с ≥8
    дешёвыми — медиану 2. Требовать оба порога сразу = требовать конфигурацию,
    которой у победителей нет.

КОНТРОЛЬ ОБЕИМИ СТОРОНАМИ: проваленная колода (2 тела, 8-й перцентиль) против
BR-листа того же игрока с результатом 7W-1L (8 тел, 96-й перцентиль).

⚠️ ФИКСТУРА — `hob_ur_eba1b036_fail.txt` (восстановлена 20.08.2026 из cc89970).
Тест изначально читал `hob_ur_eba1b036.txt`, но тот же коммит d84bb16 перезаписал файл
ПЕРЕСОБРАННОЙ версией (5 тел в мейне) — и тест не мог пройти с момента своего рождения:
зеркальный случай к «тесту, который не мог упасть» из § 8.5. Файл-объект теста обязан
быть фикстурой, а не рабочим файлом, который следующий шаг работы перепишет.
"""
import os
import re
import sys

os.environ["MTGA_SET"] = "hob"
os.environ["MTGA_OFFLINE"] = "1"
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.argv = ["draft_live.py", "hob"]
import draft_live as D
import deck_profile as DP

fails = []


def check(cond, msg):
    print(("   ✅ " if cond else "   ❌ ") + msg)
    if not cond:
        fails.append(msg)


# ── 1. deck_profile считает ось ──────────────────────────────────────────────
db, rat = DP.load_db(), DP.load_ratings("hob")
M = DP.metrics(os.path.join(HERE, "hob_ur_eba1b036_fail.txt"), db, rat)
check("big" in M, "deck_profile отдаёт ось big")
check(M["big"] == 2, f"проваленная колода: тел силой ≥4 = {M['big']}, ожидалось 2")
check("Smaug, the Great Calamity" in M["big_names"], "Smaug 5/5 попал в ось")
check("Old Thrush" not in M["big_names"], "Old Thrush 1/2 в ось НЕ попал")
check("Elvenking's Harper" not in M["big_names"],
      "Harper 2/2 в ось не попал (эвейжн за ману телом не делает)")

# ── 2. норма по парам взята из данных, а не назначена ────────────────────────
tbl = (D.load_traps() or {}).get("big_bodies") or {}
check(bool(tbl), "в hob_traps.json есть блок big_bodies "
                 "(иначе: python3 find_traps.py hob --write)")
check(tbl.get("UR", {}).get("med") == 4, f"медиана UR = {tbl.get('UR', {}).get('med')}, ожидалось 4")
check(tbl.get("WU", {}).get("med") == 0,
      f"медиана WU = {tbl.get('WU', {}).get('med')} — у воздушной пары крупные тела НЕ нужны, "
      "порог обязан быть по паре, а не общий")
check(tbl["BR"]["med"] > tbl["WU"]["med"], "BR требует крупных тел заметно больше, чем WU")

# ── 3. ⚑ ЧЕМ УБИВАЮ: срабатывает на бедном пуле, молчит на богатом ───────────
by, rt = D.load_cards(), D.load_ratings()
N2I = {}
for cid, c in by.items():
    for k in (c.get("name", ""), c.get("name", "").split(" //")[0]):
        N2I.setdefault(re.sub(r"[^a-z0-9]", "", k.lower()), cid)


def ids(*names):
    return [N2I[re.sub(r"[^a-z0-9]", "", n.lower())] for n in names]


thin = ids("Old Thrush", "Elvenking's Harper", "Patient Instructor",
           "Confusticate and Bebother", "Plunder the Trollshaws", "Uneasy Partings",
           "Ravenhill Flock", "Long Lake Nuisance", "Nori, Teller of Tales",
           "Mirkwood Nurturer", "Pinecone Strike", "Sound the Trumpets",
           "Enchanted River's Grasp", "Long-Bodied Grey Dog")
b = D.kill_banner(thin, by, rt, {"U", "R"}, 3, 1)
print("\n".join("   " + x for x in b) if b else "   (молчит)")
check(bool(b) and "ЧЕМ УБИВАЮ" in b[0], "бедный на крупные тела пул UR — баннер горит")
check(any("🔴" in x for x in b), "проекция ниже минимума пары помечена красным")

rich = thin + ids("Smaug, the Great Calamity", "Gandalf, Spark Starter",
                  "Lake-town Mariners", "The Lord of the Eagles", "Gandalf, Wandering Wizard")
check(D.kill_banner(rich, by, rt, {"U", "R"}, 3, 1) == [],
      "пул с пятью крупными телами (выше медианы UR) — баннер молчит")
check(D.kill_banner(thin, by, rt, {"W", "U"}, 3, 1) == [],
      "в WU (медиана 0) тот же пул баннер НЕ ругает — норма берётся по паре")
check(D.kill_banner(thin, by, rt, {"U", "R"}, 1, 3) == [],
      "на раннем пике молчит: проекция по трём пикам — шум")

# ── 4. квота кривой уступает полосе крупных тел ──────────────────────────────
big_pool = ids("Smaug, the Great Calamity", "Gandalf, Spark Starter", "Lake-town Mariners",
               "The Lord of the Eagles", "Plunder the Trollshaws")
cb = D.curve_banner(ids("Old Thrush"), by, rt, {"U", "R"}, 3, 2, big_pool)
print("\n".join("   " + x for x in cb))
check(any("полосе КРУПНЫХ ТЕЛ" in x for x in cb),
      "при 4 телах силы ≥4 квота кривой отменяется, а не требует дешёвых тел вдобавок")
check(not any("НЕДОБОР" in x for x in cb), "слово НЕДОБОР на этой полосе не печатается")

# а на пуле БЕЗ крупных тел квота работает как раньше
cb2 = D.curve_banner(ids("Old Thrush"), by, rt, {"U", "R"},
                     3, 2, ids("Plunder the Trollshaws") * 6)
check(any("НЕДОБОР" in x for x in cb2), "без крупных тел квота кривой по-прежнему считается")

# ── 5. ⚑ ПЛАН ПОБЕДЫ: пул против собранной из него колоды ────────────────────
# Ключевая демонстрация: ПУЛ давал три маршрута, СБОРКА не оставила ни одного.
import json as _json
pool_names = []
for ln in open(os.path.join(HERE, "pools", "hob_eba1b036.txt"), encoding="utf-8"):
    m = re.match(r"^\s*(\d+)\s+(.+?)\s*$", ln.strip())
    if m:
        k = re.sub(r"[^a-z0-9]", "", m.group(2).lower())
        if k in N2I:
            pool_names += [N2I[k]] * int(m.group(1))
pb = D.plan_banner_v2(pool_names, by, rt, {"U", "R"}, 3, 14)
print("\n".join("   " + x for x in pb))
check(bool(pb) and "✔" in pb[0], "на реальном ПУЛЕ маршруты открыты — драфт дал материал")
check("КРУПНЫЕ ТЕЛА" in pb[0], "пул давал маршрут крупных тел (их было 5 при норме 4)")

deck_names = []
for ln in open(os.path.join(HERE, "hob_ur_eba1b036_fail.txt"), encoding="utf-8"):
    if ln.strip() == "Sideboard":
        break
    m = re.match(r"^\s*(\d+)\s+(.+?)\s*$", ln.strip())
    if m:
        k = re.sub(r"[^a-z0-9]", "", m.group(2).lower())
        if k in N2I:
            deck_names += [N2I[k]] * int(m.group(1))
db_ = D.plan_banner_v2(deck_names, by, rt, {"U", "R"}, 3, 14)
print("\n".join("   " + x for x in db_))
check(bool(db_) and ("🔴" in db_[0] or "⚠" in db_[0]),
      "СОБРАННАЯ из того же пула колода (0-3) маршрута не имеет — баннер это называет")

# молчит в первом бустере (проекция по 5 пикам — шум)
check(D.plan_banner_v2(pool_names[:5], by, rt, {"U", "R"}, 1, 5) == [],
      "в первом бустере молчит")
# в паре без референса молчит
check(D.plan_banner_v2(pool_names, by, rt, {"W", "B", "G"}, 3, 14) == [],
      "по паре без референс-выборки молчит, а не выдумывает норму")

print("=" * 78)
if fails:
    print(f"❌ ПРОВАЛЕНО {len(fails)}:")
    for f in fails:
        print("   ·", f)
    sys.exit(1)
print("✅ ОСЬ «ЧЕМ УБИВАЮ» РАБОТАЕТ: норма по паре из данных, баннер горит в драфте "
      "(на сборке тела не добрать),\n   и квота кривой ей уступает — у победителей это "
      "размен, а не два порога сразу.")
