"""Регресс-тест pack_order — порядка печати пака (внесён 16.08.2026).

ЗАЧЕМ. До этой правки пак печатался как sorted(GIH, reverse=True). Один отсортированный
столбец создаёт якорь: рассуждение начинается с верхней строки и дальше её рационализирует.
SKILL.md документирует два промаха подряд в одном драфте по этой причине и сам ставит
диагноз — «сортировка сильнее любой прозы». Лечить прозой уже пробовали (запрет на
«выше по GIH» в ЛОГИКА, баннер ⚑ТАЙБРЕЙК) — промахи продолжились, потому что источник
якоря — сам порядок строк.

ЧТО ПРОВЕРЯЕТСЯ (ось обновлена 18.08.2026 — IWD снят, JOURNAL § 8.9):
  A. при равном GIH выше встаёт карта, чей цвет глобальный GIH ЗАНИЖАЕТ (§ 8.8: на MSH
     W −1.2 / B +1.2) — док. случай Take Up the Shield {W} / Super-Skrull {B}, P1P2
     10.08.2026, решается в ту же сторону, что и раньше, но по подтверждённой причине;
  B. некастуемые уходят в отдельную группу ВНИЗ, а не стоят первыми по GIH;
  C. GIH остаётся ведущей осью — цветовая поправка (±1-2 пункта) не переворачивает
     заметный разрыв GIH;
  D. без коммита цветов (main=None) группа ровно одна — ранняя раскладка не меняется.
"""
import os, sys
os.environ["MTGA_SET"] = "msh"
os.environ["MTGA_OFFLINE"] = "1"
sys.path.insert(0, os.path.expanduser("~/.claude/skills/mtg-draft-helper"))
sys.argv = ["draft_live.py", "msh"]
import draft_live as D

by_id = D.load_cards()
ratings = D.load_ratings()
fails = []


def find(name):
    for aid, c in by_id.items():
        if c.get("name", "").split(" //")[0].lower() == name.lower():
            return aid
    raise SystemExit("нет карты " + name)


def flat(grouped):
    return [c for _, g in grouped for c in g]


def show(label, grouped):
    print("=" * 78)
    print(label)
    print("=" * 78)
    for glabel, gids in grouped:
        if glabel:
            print(f"  ── {glabel} ──")
        for cid in gids:
            r = ratings.get(cid, {})
            g = (r.get("ever_drawn_win_rate") or 0) * 100
            i = (r.get("drawn_improvement_win_rate") or 0) * 100
            print(f"     GIH {g:5.1f}  IWD {i:+5.1f}   {by_id[cid].get('name')}")
    print()


def check(cond, msg):
    print(("   ✅ " if cond else "   ❌ ") + msg)
    if not cond:
        fails.append(msg)


# ── A. равный GIH, разный IWD ────────────────────────────────────────────────
shield, skrull = find("Take Up the Shield"), find("Super-Skrull")
main = {"W", "B"}                      # оба кастуемы → одна группа, решает только ранг
g = D.pack_order([shield, skrull], by_id, ratings, {}, main)
show("A. Равный GIH (59.9 обе): цвет W −1.2 против B +1.2 — MSH P1P2, 10.08.2026", g)
check(flat(g)[0] == skrull,
      "Super-Skrull выше Take Up the Shield (старая сортировка ставила наоборот)")

# ── B. некастуемая с высоким GIH не должна быть первой ───────────────────────
# Web Up {2}{W} GIH 60.8 — в цвете; Super-Skrull {1}{B}{B}{B} — два+ off-color пипа в WU.
webup = find("Web Up")
g = D.pack_order([skrull, webup], by_id, ratings, {}, {"W", "U"})
show("B. Пул в WU: Super-Skrull (GIH 59.9, ✗offcolor) против Web Up (GIH 60.8, в цвете)", g)
check(len(g) == 2 and g[0][1] == [webup],
      "некастуемая вынесена в отдельную группу ниже, а не в общий GIH-список")
check(g[1][0] and "ВНЕ ЦВЕТА" in g[1][0], "группа подписана явно")

# ── C. GIH остаётся ведущей осью ─────────────────────────────────────────────
# Крайний случай: карта заметно лучше по GIH и хуже по IWD не должна проваливаться вниз.
pairs = [(find("Web Up"), find("Crowd of True Believers"))]
for hi, lo in pairs:
    g = D.pack_order([lo, hi], by_id, ratings, {}, {"W", "U"})
    rh, rl = ratings[hi], ratings[lo]
    show(f"C. {by_id[hi]['name']} (GIH {rh['ever_drawn_win_rate']*100:.1f}) против "
         f"{by_id[lo]['name']} (GIH {rl['ever_drawn_win_rate']*100:.1f}, IWD отрицательный)", g)
    check(flat(g)[0] == hi, "заметно лучший GIH побеждает — поправки не переворачивают явный разрыв")

# ── D. до коммита цветов группа одна ─────────────────────────────────────────
g = D.pack_order([shield, skrull, webup], by_id, ratings, {}, None)
show("D. main=None (пул < 5 пиков) — кастуемость ещё не считается", g)
check(len(g) == 1 and g[0][0] is None, "ровно одна группа без заголовка")

print("=" * 78)
if fails:
    print(f"❌ ПРОВАЛЕНО {len(fails)}:")
    for f in fails:
        print("   ·", f)
    sys.exit(1)
print("✅ ВСЕ ПРОВЕРКИ ПРОШЛИ:")
print("   · равный GIH разрешается цветовой поправкой § 8.8 (промах P1P2 всё так же невозможен)")
print("   · некастуемые в своей группе внизу, а не наверху по GIH")
print("   · GIH остаётся ведущей осью — поправки не переворачивают явный разрыв")
print("   · до коммита цветов раскладка не меняется")
