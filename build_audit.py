#!/usr/bin/env python3
"""
АУДИТ СБОРКИ ПРОТИВ РЕФЕРЕНС-ПОПУЛЯЦИИ (23 листа 7-1/7-2 в ref_decks/).

Заменяет выдуманные пороги на вопрос «где моя колода в распределении победителей».
Порог, выведенный из трёх наших трофеек, отбраковывал 16 из 23 реально выигрывающих
колод (проверено 10.08.2026) — поэтому калибровка берётся из популяции, а не из головы.

Плюс ГЛАВНЫЙ тест процесса:
    Ни одна из 23 победивших колод не равна «жадному» топ-23 по GIH — все отдают
    в среднем 0.49 GIH на карту, все 23 из 23 в одну сторону. Если МОЙ мейн совпал
    с жадным списком, это признак, что план не выбран, а пул просто отсортирован.
    Этот тест — про мой процесс, поэтому он не страдает от survivorship-bias выборки.

Usage:  python3 build_audit.py <мой_лист.txt> [--pool pools/msh_XXXX.txt]
        Лист в формате MTGA: `Deck` … `Sideboard` … — сайдборд ОБЯЗАТЕЛЕН
        (это остаток пула, без него нельзя проверить срез).
"""
import os, re, sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from deck_profile import (norm, load_db, load_ratings, face, oracle,  # noqa: E402
                          parse_deck, metrics)

REF_DIR = os.path.join(HERE, "ref_decks")
AXES = [("cheap", "существ cmc≤2"), ("evasion", "ломателей стойки"),
        ("hard", "безусл. removal"), ("c5", "карт cmc≥5"),
        ("creatures", "существ"), ("fixers", "фикс-источников"),
        ("ncolors", "цветов"), ("gih", "средний GIH")]


def colors_of(c):
    cols = c.get("colors")
    if cols is None and "card_faces" in c:
        cols = c["card_faces"][0].get("colors")
    return set(cols or [])


def split_deck(path):
    """(maindeck, sideboard) как списки (n, name) — parse_deck читает только мейн."""
    main, side, cur = [], [], None
    for line in open(path, encoding="utf-8"):
        s = line.strip()
        if not s:
            continue
        if s.lower().startswith("deck"):
            cur = main; continue
        if s.lower().startswith("sideboard"):
            cur = side; continue
        if cur is None:
            cur = main
        m = re.match(r"^(\d+)\s+(.+?)(?:\s+\([A-Za-z0-9]+\)\s+\S+)?$", s)
        if m:
            cur.append((int(m.group(1)), m.group(2).strip()))
    return main, side


def load_pool_file(p):
    """Пул, автосохранённый draft_live.py (pools/<set>_<draft8>.txt). Принимает
    и голое имя файла, и путь."""
    for cand in (p, os.path.join(HERE, "pools", p), os.path.join(HERE, p)):
        if os.path.exists(cand):
            md, sb = split_deck(cand)
            return md + sb          # там всё в Sideboard, но берём обе секции
    raise SystemExit(f"пул не найден: {p} (ищу в ./ и в pools/)")


def merge_pool(md, pool):
    """Сайдборд = пул МИНУС мейн (по количеству копий)."""
    from collections import Counter
    have = Counter()
    for n, name in md:
        have[name] += n
    out = []
    for n, name in pool:
        left = n - have.get(name, 0)
        have[name] = max(0, have.get(name, 0) - n)
        if left > 0:
            out.append((left, name))
    return out


def greedy_check(path, db, rat, pool_path=None):
    """Сравнить мейн с топ-N по GIH из пула (мейн + сайд НА ЦВЕТЕ)."""
    md, sb = split_deck(path)
    if pool_path:
        sb = merge_pool(md, load_pool_file(pool_path))
    pips = Counter()
    for n, name in md:
        c = db.get(norm(name)) or db.get(norm(name.split(",")[0]))
        if not c or "Land" in face(c, "type_line"):
            continue
        for sym in re.findall(r"\{([^}]+)\}", face(c, "mana_cost")):
            for ch in sym.upper().split("/"):
                if ch in "WUBRG":
                    pips[ch] += n
    mains = {c for c, v in pips.items() if v >= 3}

    def G(nm):
        r = rat.get(norm(nm)) or rat.get(norm(nm.split(",")[0]))
        return round(r["ever_drawn_win_rate"] * 100, 1) if r else None

    real, pool = [], []
    for lst, is_md in ((md, True), (sb, False)):
        for n, name in lst:
            c = db.get(norm(name)) or db.get(norm(name.split(",")[0]))
            if not c or "Land" in face(c, "type_line") or (colors_of(c) - mains):
                continue
            g = G(c["name"])
            if g is None:
                continue
            for _ in range(n):
                pool.append((g, c["name"]))
                if is_md:
                    real.append((g, c["name"]))
    if not real or len(pool) <= len(real):
        return None
    N = len(real)
    greedy = sorted(pool, reverse=True)[:N]
    a = sum(g for g, _ in real) / N
    b = sum(g for g, _ in greedy) / N
    return b - a, sorted(set(n for _, n in greedy) - set(n for _, n in real)), a, b


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    pool_path = None
    if "--pool" in sys.argv:
        i = sys.argv.index("--pool")
        pool_path = sys.argv[i + 1] if len(sys.argv) > i + 1 else None
        args = [a for a in args if a != pool_path]
    path = args[0]
    db, rat = load_db(), load_ratings("msh")

    refs = []
    for fn in sorted(os.listdir(REF_DIR)):
        if fn.endswith(".txt"):
            refs.append(metrics(os.path.join(REF_DIR, fn), db, rat))
    mine = metrics(path, db, rat)

    print(f"\n=== АУДИТ: {mine['name']} против {len(refs)} листов 7-1/7-2 ===\n")
    print(f"{'ось':22} {'моё':>7}   {'победители (мин–медиана–макс)':<28} вердикт")
    print("-" * 82)
    flags = []
    for key, label in AXES:
        vals = sorted(r[key] for r in refs if r[key] is not None)
        if not vals or mine[key] is None:
            continue
        lo, hi = vals[0], vals[-1]
        med = vals[len(vals) // 2]
        v = mine[key]
        if v < lo:
            verdict = f"⚠ НИЖЕ всех {len(vals)}"
            flags.append(f"{label}: {v} — ниже минимума победителей ({lo})")
        elif v > hi:
            verdict = "↑ выше всех (не порок, но проверь зачем)"
        else:
            verdict = "в диапазоне"
        print(f"{label:22} {v:>7}   {lo:>6} – {med:^6} – {hi:<6}       {verdict}")

    g = greedy_check(path, db, rat, pool_path)
    print("\n" + "=" * 82)
    print("ТЕСТ ПРОЦЕССА: мой мейн vs «жадный» топ-N по GIH из моего же пула")
    print("=" * 82)
    if g is None:
        print("  ⚠ Сайдборд пуст и --pool не указан — тест невозможен.")
        print("    draft_live.py сохраняет пул сам: pools/<set>_<draft8>.txt")
        print("    Запусти: python3 build_audit.py <лист.txt> --pool <файл_пула>")
    else:
        d, swapped, a, b = g
        print(f"  мой мейн {a:.2f} · жадный {b:.2f} · ОТДАНО {d:+.2f} GIH на карту")
        print(f"  (у 23 победителей: отдано +0.49 в среднем, все 23 положительные)")
        if d <= 0.02:
            print("\n  🔴 МОЙ МЕЙН = ЖАДНЫЙ СПИСОК. Ни одна из 23 победивших колод так не собрана.")
            print("     Это не «я взял лучшие карты» — это «я не выбрал план, а отсортировал пул».")
            print("     Вернись и ответь: какая карта здесь пейофф, и что я играю РАДИ неё?")
        elif d < 0.2:
            print("\n  🟡 Отклонение от жадного есть, но слабее нормы победителей (0.49).")
            print("     Проверь, не срезаны ли пейоффы сборки ради «ровных» карт.")
        else:
            print("\n  ✅ Отклонение в норме популяции — план в колоде читается.")
        if swapped:
            print(f"\n  жадный взял бы вместо моих: {', '.join(swapped[:6])}")
            print("  (если среди них нет НИ ОДНОГО пейоффа моей оси — это и есть подтверждение)")

    if flags:
        print("\n" + "=" * 82)
        print("НИЖЕ ВСЕЙ ПОПУЛЯЦИИ ПОБЕДИТЕЛЕЙ (единственное, что стоит чинить):")
        for f in flags:
            print("  · " + f)
    else:
        print("\n  Ни по одной оси не ниже минимума победителей.")


if __name__ == "__main__":
    main()
