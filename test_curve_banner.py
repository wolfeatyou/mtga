import os, sys
os.environ["MTGA_SET"] = "msh"
os.environ["MTGA_OFFLINE"] = "1"
sys.path.insert(0, os.path.expanduser("~/.claude/skills/mtg-draft-helper"))
sys.argv = ["draft_live.py", "msh"]
import draft_live as D

by_id = D.load_cards()
ratings = D.load_ratings()
print(f"карт: {len(by_id)}  рейтингов: {len(ratings)}")

def find(name):
    for aid, c in by_id.items():
        if c.get("name", "").split(" //")[0].lower() == name.lower():
            return aid
    for aid, c in by_id.items():
        if name.lower() in c.get("name", "").lower():
            return aid
    raise SystemExit(f"НЕ НАЙДЕНА: {name}")

def show(cid):
    c = by_id[cid]
    return f"{c['name']} cmc={c.get('cmc')} {D.face(c,'type_line')[:28]}"

# реальные MSH-карты: дешёвые тела и дорогие/нетела
cheap  = ["Crowd of True Believers", "Bold Biochemist", "Aerial Doombot", "A.I.M. Synthoids",
          "Brave Brawler", "Colleen Wing"]
# ловушки: Kree Commandos — существо, но cmc 3; Political Triumph — cmc 1, но НЕ существо
expens = ["Atlantis Attacks", "Kree Commandos", "Web Up", "Political Triumph"]
ids_cheap  = [find(n) for n in cheap]
ids_expens = [find(n) for n in expens]
print("\n-- дешёвые кандидаты --")
for i in ids_cheap:  print("  ", show(i))
print("-- дорогие/нонкрит --")
for i in ids_expens: print("  ", show(i))

# санити: _is_cheap_body
print("\n-- _is_cheap_body --")
for i in ids_cheap:
    assert D._is_cheap_body(i, by_id), f"должно быть дешёвым: {show(i)}"
for i in ids_expens:
    assert not D._is_cheap_body(i, by_id), f"НЕ должно быть дешёвым: {show(i)}"
print("   OK: 6 дешёвых распознаны, 4 дорогих/нонкрита отброшены")

pack = ids_cheap[:2] + ids_expens          # пак, где ЕСТЬ дешёвые тела
pack_nocheap = ids_expens                  # пак без дешёвых тел

print("\n=== A. пул пуст, P1P1 (чекпойнт 0) ===")
print("\n".join(D.curve_banner(pack, by_id, ratings, None, 1, 1, [])))

print("\n=== B. P2P1, в пуле 1 дешёвое тело — НЕДОБОР, в паке есть кандидаты ===")
pool = [ids_cheap[0]] + ids_expens * 3
print("\n".join(D.curve_banner(pack, by_id, ratings, {"W", "U"}, 2, 1, pool)))

print("\n=== C. P3P1, в пуле 5 дешёвых — норма набрана ===")
pool5 = ids_cheap[:5] + ids_expens
print("\n".join(D.curve_banner(pack, by_id, ratings, {"W", "U"}, 3, 1, pool5)))

print("\n=== D. P2P14, недобор, в паке дешёвых НЕТ ===")
print("\n".join(D.curve_banner(pack_nocheap, by_id, ratings, {"W", "U"}, 2, 14, pool)))

print("\n=== E. off-color НЕ засчитывается (пул те же карты, но цвета B/R) ===")
print("   в цветах WU:", len(D.cheap_bodies(pool5, by_id, ratings, {"W", "U"})))
print("   в цветах BR:", len(D.cheap_bodies(pool5, by_id, ratings, {"B", "R"})))

print("\n=== F. рампа чекпойнта по пикам ===")
for pn in (1, 2, 3):
    row = []
    for pk in (1, 7, 14):
        prev = D.CHEAP_TARGET.get(pn - 1, 0); tgt = D.CHEAP_TARGET.get(pn, 5)
        row.append(f"P{pn}P{pk}:{int(prev + (tgt - prev) * pk / D.PICKS_PER_PACK)}")
    print("   " + "  ".join(row))

# сет без таблицы `played` не должен получать ложных обвинений: нет данных — не наказываем
b = D.curve_banner(pack, by_id, ratings, {"W", "U"}, 2, 1, pool)
assert not any("не входит в ядро" in x for x in b), "сет без частот получил обвинение в не-ядре"
assert not any("ПРАВИЛО" in x for x in b), "слово ПРАВИЛО вернулось в баннер (порог снят 10.08)"

# ── G. HOB, ДОК. СЛУЧАЙ P3P2 драфта eba1b036 (починка 20.08.2026) ────────────
# Баннер трижды за драфт назвал кандидатом Old Thrush (GIH 50.9) и печатал
# «ПРАВИЛО: берём дешёвое тело» — карту взяли все три раза. Old Thrush стоит в
# 0 из 14 UR-листов победителей и 23 из 298 по сету. Цена: 19.3 GIH-пункта,
# треть всей упущенной ценности драфта.
print("\n=== G. HOB: тело вне ядра пары не закрывает квоту ===")
import importlib
os.environ["MTGA_SET"] = "hob"
sys.argv = ["draft_live.py", "hob"]
importlib.reload(D)
H_by_id, H_rat = D.load_cards(), D.load_ratings()


def hid(name):
    for aid, c in H_by_id.items():
        if c.get("name", "").split(" //")[0].lower() == name.lower():
            return aid
    raise SystemExit(f"НЕ НАЙДЕНА в hob: {name}")


assert D.load_traps().get("played"), "в hob_traps.json нет блока played — запусти find_traps.py hob --write"
r_ot, sc_ot = D.played_rate("Old Thrush", {"U", "R"})
r_pi, _ = D.played_rate("Patient Instructor", {"U", "R"})
assert sc_ot == "UR" and r_ot == 0.0, f"частота Old Thrush в UR: {r_ot} ({sc_ot}), ожидалось 0.0"
assert r_pi and r_pi > D.CORE_MIN_RATE, f"Patient Instructor выпал из ядра UR: {r_pi}"

pack_ot = [hid("Old Thrush"), hid("Velvetwing Butterflies")]
pool_thin = [hid("Plunder the Trollshaws")] * 6          # ни одного тела cmc≤2 → НЕДОБОР
b = D.curve_banner(pack_ot, H_by_id, H_rat, {"U", "R"}, 3, 2, pool_thin)
print("\n".join(b))
assert any("НЕДОБОР" in x for x in b), "недобор не сработал — сценарий собран неверно"
assert any("не входит в ядро UR" in x for x in b), \
    "Old Thrush снова предлагается как закрывающий квоту — починка 20.08 откатилась"
assert any("✗Old Thrush" in x for x in b), "нет пометки ✗ у карты вне ядра"
assert not any("ПРАВИЛО: берём дешёвое тело" in x for x in b), "приказ вернулся"

# а карта ИЗ ядра пары квоту закрывает и печатается с ✔ впереди
pack_mix = [hid("Old Thrush"), hid("Elvenking's Harper")]
b2 = D.curve_banner(pack_mix, H_by_id, H_rat, {"U", "R"}, 3, 2, pool_thin)
print("\n".join(b2))
assert any("✔Elvenking's Harper" in x for x in b2), "карта ядра не помечена ✔"
assert b2[1].index("✔") < b2[1].index("✗"), "ядро должно печататься ПЕРВЫМ, а не по GIH"
assert any("роль закрывает ✔-карта" in x for x in b2)

print("\n✅ КРИВАЯ: квоту закрывает только тело из ядра пары; слово ПРАВИЛО снято; "
      "сет без частот деградирует молча")
