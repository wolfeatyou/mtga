"""Определение цветов пула: гибрид даёт ДОСТУП, а не принадлежность (починено 20.08.2026).

Повод — живой драфт hob eba1b036: четыре `Patient Instructor` {2}{W/U}, кастуемые с одних
Островов, дали W:7 против R:6, и `pool_main_colors` весь второй и третий бустер называл
колоду WU вместо UR. Через `main` этот перекос протекал ВЕЗДЕ: ⚑ОСЬ печатала чужую пару,
«⚠ НЕ В ЭТОЙ ПАРЕ» сверялось не с той парой, а собственные красные карты (Gandalf,
Pinecone Strike, Glóin) уходили в группы `~splash` / `✗offcolor` — то есть инструмент
предлагал пивотировать из цвета, в котором мы и были.

Проверяются БОЕВЫЕ функции на реальном пуле того драфта (урок JOURNAL § 8.5 —
тест, повторяющий логику у себя, тестом не является).
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

by_id = D.load_cards()
N2I = {}
for cid, c in by_id.items():
    for k in (c.get("name", ""), c.get("name", "").split(" //")[0]):
        N2I.setdefault(re.sub(r"[^a-z0-9]", "", k.lower()), cid)


def cid(name):
    k = re.sub(r"[^a-z0-9]", "", name.lower())
    v = N2I.get(k) or N2I.get(re.sub(r"[^a-z0-9]", "", name.split(" //")[0].lower()))
    assert v is not None, f"карта не найдена в hob_set.json: {name}"
    return v


def pool(*names):
    return [cid(n) for n in names]


# ── 1. док. случай: синяя база + гибриды {W/U} не делают колоду белой ────────
# ровно каркас пула eba1b036 к началу третьего бустера
p = pool(
    "Plunder the Trollshaws", "Confusticate and Bebother", "Sound the Trumpets",
    "Uneasy Partings", "Enchanted River's Grasp", "Long Lake Nuisance",
    "Ravenhill Flock", "Elvenking's Harper", "Lake-town Mariners",
    "Patient Instructor", "Patient Instructor", "Patient Instructor", "Patient Instructor",
    "Bothersome Noisemaker", "Smaug, the Great Calamity", "Gandalf, Spark Starter",
    "Pinecone Strike",
)
main = D.pool_main_colors(p, by_id)
assert main == {"U", "R"}, (
    f"пул с четырьмя гибридами {{W/U}} прочитан как {sorted(main)}, а это UR — "
    "гибрид снова голосует за цвет, которого не требует")

# и следствие: наши красные карты обязаны быть В ЦВЕТЕ, а не в сплеше
for nm in ("Gandalf, Spark Starter", "Pinecone Strike", "Smaug, the Great Calamity"):
    assert D.cast_flag(by_id[cid(nm)], main) == "", f"{nm} помечена вне цвета в собственной паре"
# а гибрид остаётся кастуемым, он ведь и правда кастуется
assert D.cast_flag(by_id[cid("Patient Instructor")], main) == ""

# ── 2. настоящие чужие цвета не должны стать «своими» ───────────────────────
assert D.cast_flag(by_id[cid("Gollum the Abandoned")], main) == " ~splash"     # {1}{B}
assert D.cast_flag(by_id[cid("Esgaroth Garrison")], main) == " ~splash"        # {4}{W}
assert D.cast_flag(by_id[cid("Bilbo's Deadly Slice")], main) == " ✗offcolor"   # {1}{B}{B}

# ── 3. гибрид ВНЕ лидеров всё-таки заявляет свои цвета ──────────────────────
# пул почти целиком BG: гибрид {B/G} обязан подтверждать пару, а не быть проигнорированным
bg = pool("Bilbo's Deadly Slice", "Stir Up Trouble", "Ravening Warg", "Attercop",
          "Quarrel", "Wargling", "Duskwatch Hunter", "Duskwatch Hunter")
assert D.pool_main_colors(bg, by_id) == {"B", "G"}, "гибридная пара BG не опознана"

# ── 4. чисто-гибридный пул не остаётся без цветов (падение на старое поведение) ──
hyb = pool("Patient Instructor", "Patient Instructor", "Mirkwood Nurturer",
           "Nori, Teller of Tales", "Fearsome Goblin Pair")
assert D.pool_main_colors(hyb, by_id), "пул из одних гибридов потерял цвета совсем"

# ── 5. пул короче min_picks по-прежнему не коммитится ───────────────────────
assert D.pool_main_colors(p[:4], by_id) is None

print("✅ ЦВЕТА ПУЛА: гибрид даёт доступ, а не принадлежность; док. случай eba1b036 "
      "читается как UR, свои красные карты в цвете, чужие — в сплеше")
