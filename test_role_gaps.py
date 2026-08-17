"""Регресс-тест ⚠ РОЛЬ ВПЕРЁД (внесён 17.08.2026 после проигранного A/B).

ПОВОД. Слепой судья на 8 сгенерированных драфтах отдал старому скиллу 6 из 8 (3 из 4 на
сидах, чистых по целостности) и трижды назвал одну и ту же причину:
  · сид 42 — «летунов у B всего 3 против 7 — упирается в стену на земле без плана пробить»;
  · сид 11 — «удаления почти нет: единственный инструмент — 2× Stone by Sunlight»;
  · сид 58 — «Thranduil даёт +1/+1 Эльфам, а Эльфов в колоде всего 2 — мёртвый текст».
Правка «роль вперёд связки» в тот момент УЖЕ стояла в коде и не сработала ни разу. Разбор
нашёл два дефекта, каждый из которых этот файл и стережёт:

  A. REACH СЧИТАЛСЯ ПРОБИТИЕМ. Сумма fly+reach сравнивалась с медианой 5. Reach не
     пробивает — он блокирует летунов, то есть держит стойку; в скилле с времён MSH
     записано, что он анти-коррелирует с воздушным планом. Колода с 3 флаерами и 4 reach
     проходила проверку как здоровая — это ровно сид 42. Пересчёт по 298 трофейным листам:
     пробивающих (flying/menace/unblockable/trample) медиана 4, reach отдельно медиана 1.

  B. ПРЕДУПРЕЖДЕНИЕ О REMOVAL НЕ МОГЛО СРАБОТАТЬ РАНЬШЕ 32-го ПИКА. Порог был
     «медиана × доля драфта ≥ 1.5», у removal медиана 2 → 1.5 набегает только к P3P4.
     Заменено проекцией собственного темпа: have/доля против медианы, с пика 8.
"""
import os, sys

os.environ["MTGA_SET"] = "hob"
os.environ["MTGA_OFFLINE"] = "1"
sys.path.insert(0, os.path.expanduser("~/.claude/skills/mtg-draft-helper"))
sys.argv = ["draft_live.py", "hob"]
import draft_live as D  # noqa: E402

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


def gaps(names, pnum, pick, main={"W", "U"}):
    return D.role_gaps([cid(n) for n in names], by, rat, main, pnum, pick)


def has(g, role):
    return any(role in x[0] for x in g)


print("=" * 78)
print("A. reach не засчитывается как пробитие (сид 42)")
# 3 летающих тела + опора на reach: раньше 3+4=7 при медиане 5 → «в норме».
air3_reach = ["Long Lake Nuisance", "Old Thrush", "Ravenhill Flock",
              "Bard the Bowman", "Mirkwood Nurturer", "Boughside Wanderers",
              "Patient Instructor", "Lakeshore Apothecary", "Bilbo Baggins, Burglar",
              "Iron Hills Blacksmith", "Elrond, Moon-Reader", "Uneasy Partings",
              "Magnificent End", "Vow to Erebor", "Esgaroth Garrison",
              "Mirkwood Meditator", "Lake-town Lookout", "Ori, Keeper of Songs",
              "Sound the Trumpets", "Elvenking's Harper"]
r = D._pool_roles([cid(n) for n in air3_reach], by, rat, {"W", "U"})
print(f"   пул: пробивающих {r['brk']}, reach {r['reach']}, летающих {r['fly']}")
# Прямая проверка семантики: чистый reach-крип (Bard the Bowman, Long-Bodied Grey Dog)
# не должен попадать в пробитие ни при каких условиях.
pure_reach = D._pool_roles([cid("Bard the Bowman"), cid("Long-Bodied Grey Dog")],
                           by, rat, {"W", "U"})
print(f"   два чистых reach-крипа: reach {pure_reach['reach']}, пробивающих {pure_reach['brk']}")
check(pure_reach["reach"] == 2 and pure_reach["brk"] == 0,
      "reach считается reach-ом и НЕ считается пробитием")

print("\n   контроль: тот же размер пула, но пробития почти нет")
ground = ["Iron Hills Blacksmith", "Dwarven Provisioner", "Lake-town Lookout",
          "Patient Instructor", "Lakeshore Apothecary", "Bilbo Baggins, Burglar",
          "Elrond, Moon-Reader", "Ori, Keeper of Songs", "Mirkwood Meditator",
          "Elvenking's Harper", "Uneasy Partings", "Vow to Erebor",
          "Sound the Trumpets", "Esgaroth Garrison", "Master's Councillors",
          "Bard the Bowman", "Thorin's Last Stand", "Wizard's Staff",
          "Reverent Howl", "Moment of Glory"]
g2 = gaps(ground, 2, 6)
r2 = D._pool_roles([cid(n) for n in ground], by, rat, {"W", "U"})
print(f"   пул: пробивающих {r2['brk']}")
print("   " + ("; ".join(f"{n} {h}→{p:g}" for n, h, p, _ in g2) or "(молчит)"))
check(has(g2, "пробивающих"), "пул без пробития получает предупреждение")

print("\n" + "=" * 78)
print("B. дефицит ОТВЕТОВ предупреждается в середине драфта, а не на 32-м пике")
# Ни одна из этих карт не убирает тело — ни destroy/exile, ни -X/-X, ни файт, ни баунс.
no_removal = ["Patient Instructor", "Lakeshore Apothecary", "Bilbo Baggins, Burglar",
              "Long Lake Nuisance", "Old Thrush", "Bard the Bowman",
              "Mirkwood Meditator", "Lake-town Lookout"]
g3 = gaps(no_removal, 1, 8)
print(f"   P1P8, ноль removal в пуле: "
      + ("; ".join(f"{n} {h}→{p:g}" for n, h, p, _ in g3) or "(молчит)"))
check(has(g3, "ответов"), "на пике 8 уже говорит про removal (раньше молчал до пика 32)")

g4 = gaps(no_removal[:6], 1, 6)
print(f"   P1P6 (раньше порога проекции): "
      + ("; ".join(f"{n} {h}→{p:g}" for n, h, p, _ in g4) or "(молчит)"))
check(not g4, "до пика 8 молчит — проекция от 5 карт это шум")

print("\n   контроль: removal в пуле есть — молчит")
with_removal = no_removal + ["Magnificent End", "Stone by Sunlight"]
# Расширение определения ответа (17.08): условный эффект, убивающий мелкое тело, засчитывается.
# Повод — реальная партия: проигрыш Bilbo, Luckwearer (1/1) со словами «убрать её было нечем»,
# при том что -1/-1 её убивает. В HOB 54% существ у победителей имеют выносливость ≤2.
g5 = gaps(with_removal, 1, 10)
print("   " + ("; ".join(f"{n} {h}→{p:g}" for n, h, p, _ in g5) or "(молчит про removal)"))
check(not has(g5, "ответов"), "два removal к пику 10 — вопросов нет")

print("\nB3. ПОЛ: ноль ответов на входе во второй бустер — говорит независимо от проекции")
# Пул из 14 карт, НИ ОДНА не убирает тело (проверено фильтром по _HARD_RE/_SOFT_RE).
# Раньше `Vow to Erebor` незаметно засчитывался ответом и портил этот кейс.
none_at_all = ["Old Thrush", "Troop of Ponies", "Belladonna Took", "Bofur, Reliable Guardian",
               "Celebrate the Mountain-king", "Dáin, Lord of the Iron Hills",
               "Dwarven Provisioner", "Dwarven Shortsword", "Eagle of the Great Shelf",
               "The Eagles Are Coming!", "Esgaroth Garrison", "Fíli the Pathfinder",
               "Iron Hills Blacksmith", "Lake-town Lookout"]
ids = [cid(n) for n in none_at_all]
real = sum(1 for i in ids
           if D._HARD_RE.search(D.full_oracle(by[i]) or "")
           or D._SOFT_RE.search(D.full_oracle(by[i]) or ""))
check(real == 0, f"контрольный пул действительно без ответов (насчитано {real})")
g6 = D.role_gaps(ids, by, rat, {"W", "U"}, 2, 1)
print("   " + ("; ".join(f"{n} {h}→{p:g}" for n, h, p, _ in g6) or "(молчит)"))
check(any(x[0] == "ответов на тело" and x[1] == 0 for x in g6),
      "на P2P1 при нуле ответов баннер говорит")

print("\n" + "=" * 78)
print("C. без калибровки сета не падает")
_saved = D.CALIB.pop("hob", None)
try:
    check(D.role_gaps([cid("Patient Instructor")], by, rat, {"W", "U"}, 2, 6) == [],
          "молчит без CALIB, не падает")
finally:
    if _saved:
        D.CALIB["hob"] = _saved

print("=" * 78)
if fails:
    print(f"❌ ПРОВАЛЕНО {len(fails)}:")
    for f in fails:
        print("   ·", f)
    sys.exit(1)
print("✅ ВСЕ ПРОВЕРКИ ПРОШЛИ — роль меряется тем, что действительно пробивает,")
print("   и дефицит называется тогда, когда его ещё можно закрыть.")
