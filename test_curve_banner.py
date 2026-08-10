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
