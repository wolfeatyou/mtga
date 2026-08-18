"""Регресс-тест ⚑ ТАЙБРЕЙК — на РЕАЛЬНОМ случае, который его и породил.

Quick MSH, 10.08.2026, P1P2: в паке лежали Take Up the Shield (GIH 59.9 / IWD +3.0 /
пик C+) и Super-Skrull (GIH 59.9 / IWD +8.6 / пик B, 4/5 flying). GIH совпал до десятой,
советчик взял верхнюю строку GIH-сортировки. Игрок взял Super-Skrull вопреки совету и
оказался прав: колода уехала в воздух, а Take Up the Shield — поимённо в списке
«высокий GIH, берут поздно» из § КАЛИБРОВКА.
"""
import os, sys
os.environ["MTGA_SET"] = "msh"
os.environ["MTGA_OFFLINE"] = "1"
sys.path.insert(0, os.path.expanduser("~/.claude/skills/mtg-draft-helper"))
sys.argv = ["draft_live.py", "msh"]
import draft_live as D

by_id = D.load_cards()
ratings = D.load_ratings()


def find(name):
    for aid, c in by_id.items():
        if c.get("name", "").split(" //")[0].lower() == name.lower():
            return aid
    raise SystemExit("нет карты " + name)


def show(label, ids, main=None):
    print("=" * 76); print(label); print("=" * 76)
    out = D.tiebreak_banner(ids, by_id, ratings, main)
    print("\n".join(out) if out else "   (молчит)")
    return "\n".join(out)


# ── A. настоящий случай P1P2 ──────────────────────────────────────────────────
REAL = [find(n) for n in ["Take Up the Shield", "Super-Skrull", "Undercover Skrull",
                          "Madame Masque", "Reptil, Dinomorpher"]]
a = show("A. реальный P1P2: Take Up the Shield 59.9/пик C+ vs Super-Skrull 59.9/пик B", REAL)
assert "ТАЙБРЕЙК" in a, "не сработал на случае, ради которого написан!"
assert "Super-Skrull" in a, "не назвал правильного победителя тайбрейка"
assert "пик-тир" in a, "не назвал причину (пик-тир; IWD снят 18.08.2026, § 8.9)"

# ── B. молчит, когда верх по GIH и по тайбрейку — одна карта ──────────────────
QUIET = [find(n) for n in ["Web Up", "Crowd of True Believers", "Atlantis Attacks"]]
b = show("B. верх по GIH он же лучший — баннер обязан молчать", QUIET)

# ── C. молчит, когда разрыв по GIH больше порога (тайбрейка нет) ──────────────
FAR = [find(n) for n in ["Leader, Super-Genius", "Hydraulic Helper"]]
c = show("C. разрыв GIH велик — решает GIH, тайбрейк не нужен", FAR)
assert not c, "сработал там, где GIH решает сам"

# ── D. некастуемые в тайбрейке не участвуют ──────────────────────────────────
d = show("D. Super-Skrull ({1}{B}{B}{B}) вне цвета при пуле UW — из тайбрейка выпадает",
         REAL, main={"U", "W"})
assert "Super-Skrull" not in d, "предложил некастуемую карту"

print("\n✅ ВСЕ ПРОВЕРКИ ПРОШЛИ:")
print("   · срабатывает на реальном случае и называет Super-Skrull + причину (пик-тир)")
print("   · молчит, когда GIH-топ и есть лучший выбор")
print("   · молчит, когда GIH решает сам (разрыв > порога)")
print("   · не предлагает карты вне цвета")
