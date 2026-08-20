"""Регресс-тест ⚠ ЛОВУШКА / ⚠ НЕ В ЭТОЙ ПАРЕ (внесён 17.08.2026).

ПОВОД. Замер частоты карт (`card_leaks.py`) показал `Bard, King of Dale` в 40% наших
WU-сборок и в НУЛЕ из 47 трофейных колод, где он вообще кастуем, — при ALSA 2.7, то есть
его берут третьим пиком. Ни GIH, ни ALSA этого не видят: первый говорит, насколько карта
выигрывает, второй — насколько рано её берут, и ни один не говорит, ДОШЛА ЛИ она до мейна
выигравшей колоды. Третий источник — состав 298 листов 7-1/7-2.

ДВА ЯВЛЕНИЯ, КОТОРЫЕ НЕЛЬЗЯ ПУТАТЬ (я спутал, поймано пересчётом — см. JOURNAL.md § 4.8):
  A. ЛОВУШКА СЕТА — карта не играется НИГДЕ при поправке на редкость. Их всего 3 из 187.
  B. НЕ В ЭТОЙ ПАРЕ — играется в сете, но не в текущей паре. Классика — гибрид {G/U},
     кастуемый чистой синей: флаг кастуемости пропускает его как свою карту, а текст
     («другие Эльфы +1/+1») в WU мёртв.

ЧТО ПРОВЕРЯЕТСЯ:
  · ловушка называется, когда лежит в паке;
  · «не в этой паре» срабатывает для WU и МОЛЧИТ для той пары, где карта на месте;
  · обычная карта не поднимает ни одного баннера;
  · ключи файла и ключи баннера сходятся (на этом баннер молчал при первой сборке:
    `_norm_card` оставляет пунктуацию, а `find_traps.py` её срезает);
  · без файла ловушек не падает — сет без разбора должен работать.
"""
import json, os, sys

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


def banner(names, main):
    return D.trap_banner([cid(n) for n in names], by, rat, main)


print("=" * 78)
print("0. ключи файла сходятся с ключами баннера")
t = D.load_traps()
check(bool(t.get("traps")), f"файл ловушек загружен, записей {len(t.get('traps', []))}")
first = t["traps"][0]
check(D._trap_key(first["name"]) == first["key"],
      f"нормализация совпадает: {first['name']} → {first['key']}")

print("\nA. ловушка сета лежит в паке")
out = banner(["Bard, King of Dale"], {"W", "U"})
print("\n".join("   " + x for x in out) or "   (молчит)")
check(any("ЛОВУШКА" in x and "Bard" in x for x in out), "названа поимённо")
# ALSA Барда берём из ТЕКУЩЕГО traps.json, а не хардкодом 2.7: числа 17Lands
# дважды пересобирались (§ 8.2 ③, § 8.26), захардкоженное значение сгнило за 2 дня.
_bard = next(t for t in json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "hob_traps.json")))["traps"]
             if t["key"] == "bardkingofdale")
check(any(f"{_bard['alsa']:.1f}" in x for x in out), "сказано, каким пиком её берут (ALSA из traps.json)")
check(any(f"{_bard['played']} из {_bard['seen']}" in x for x in out), "сказано, в скольких трофейных колодах стоит (played/seen из traps.json)")

print("\nB. карта не для этой пары — берётся ИЗ ТЕКУЩЕГО pair_bad, не хардкодом")
# Первая редакция хардкодила Thranduil в WU — на популяции 416 (§ 8.27) он из WU-списка
# ВЫПАЛ (set_rate упал ниже порога), и тест месяц запрещал бы карту по мёртвым данным.
_traps_all = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "hob_traps.json")))
_pb = _traps_all["pair_bad"]["WU"][0]
out = banner([_pb["name"]], {"W", "U"})
print(f"   (кандидат из данных: {_pb['name']})")
print("\n".join("   " + x for x in out) or "   (молчит)")
check(any("НЕ В ЭТОЙ ПАРЕ" in x for x in out), "в WU предупреждает")
check(any(f"{round(100*_pb['set_rate'])}%" in x and f"{round(100*_pb['here'])}%" in x for x in out),
      "названы обе доли — в сете и в паре (из traps.json)")

print("\nB2. та же карта в СВОЕЙ паре — баннер обязан молчать")
_played = _traps_all["played"][_pb["key"]]["pairs"]
_home = max(_played, key=lambda k: _played[k])
out = banner([_pb["name"]], set(_home))
print(f"   (домашняя пара по данным: {_home}, доля {round(100*_played[_home])}%)")
print("\n".join("   " + x for x in out) or "   (молчит)")
check(not out, f"в {_home} молчит — иначе баннер запрещал бы карту везде")

print("\nC. обычная карта")
out = banner(["Patient Instructor"], {"W", "U"})
print("\n".join("   " + x for x in out) or "   (молчит)")
check(not out, "молчит")

print("\nD. лимит строк")
out = banner(["Bard, King of Dale", "Orcrist, Goblin-cleaver", "Gleaming Splendor",
              "Thranduil, Sindarin Liege"], {"W", "U"})
check(len(out) <= 2, f"не больше двух строк (получено {len(out)})")

print("\nE. файла ловушек нет — сет без разбора")
_saved = D._TRAPS
D._TRAPS = {}
try:
    check(banner(["Bard, King of Dale"], {"W", "U"}) == [], "молчит, не падает")
finally:
    D._TRAPS = _saved

print("=" * 78)
if fails:
    print(f"❌ ПРОВАЛЕНО {len(fails)}:")
    for f in fails:
        print("   ·", f)
    sys.exit(1)
print("✅ ВСЕ ПРОВЕРКИ ПРОШЛИ — карта, которую берут рано и не играют, названа в момент пика.")
