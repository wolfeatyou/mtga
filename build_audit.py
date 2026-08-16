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

Usage:  python3 build_audit.py <мой_лист.txt> [--pool pools/<set>_XXXX.txt] [--set hob]
        Лист в формате MTGA: `Deck` … `Sideboard` … — сайдборд ОБЯЗАТЕЛЕН
        (это остаток пула, без него нельзя проверить срез).

СЕТ ОПРЕДЕЛЯЕТСЯ САМ (16.08.2026). До этого рейтинги грузились как load_ratings("msh")
жёстко, и на любом другом сете скрипт молча резолвил 0 карт: часть (а) печаталась
пустой таблицей, а часть (б) отваливалась в «сайдборд пуст». Ошибка выглядела как
отсутствие данных, а не как поломка. Порядок детекта: --set → теги `(HOB)` в листе →
префикс файла пула → по числу совпавших имён карт в <set>_set.json.

РЕФЕРЕНС-ПОПУЛЯЦИЯ ТОЖЕ ПО СЕТАМ: ref_decks/<set>/*.txt; плоские ref_decks/*.txt
считаются MSH (как исторически). Нет листов по нужному сету → часть (а) НЕ печатается
вовсе. Сравнивать колоду с популяцией ЧУЖОГО сета запрещено § КАЛИБРОВКА (закон 1):
другой пул removal, другая скорость, другая доля эвейжна. Часть (б) валидна всегда —
она про мой процесс, а не про сходство с чужой популяцией.
"""
import os, re, sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sets_registry as _reg  # noqa: E402
from deck_profile import (norm, load_db, load_ratings, face, oracle,  # noqa: E402
                          parse_deck, metrics)

REF_DIR = os.path.join(HERE, "ref_decks")
LEGACY_REF_SET = "msh"   # плоские файлы в ref_decks/ — исторически листы MSH
# ⚠️ «средний GIH» УБРАН из осей аудита 16.08.2026 (указание пользователя).
# GIH нужен ТОЛЬКО для сортировки пака в живом драфте. Сравнивать по нему КОЛОДЫ — значит
# мерить сборку той самой осью, оптимизация по которой и даёт мягкую середину: разбор пяти
# трофейных листов HOB показал, что у победителей средний GIH НИЖЕ нашего во всех пяти парах,
# а карт «ниже 55» — до двенадцати на колоду. Ось показывала расхождение, но подталкивала
# к неверному выводу («подгони среднее»), тогда как чинить надо роли и кривую.
# Тест процесса ниже (мейн против жадного топ-N) GIH использует — но не как мерило качества,
# а как модель «что выбрала бы сортировка», от которой сборка обязана отклоняться.
AXES = [("cheap", "существ cmc≤2"), ("evasion", "ломателей стойки"),
        ("hard", "безусл. removal"), ("c5", "карт cmc≥5"),
        ("creatures", "существ"), ("fixers", "фикс-источников"),
        ("ncolors", "цветов")]


def detect_set(deck_path, pool_path=None, explicit=None):
    """Код сета для рейтингов. Возвращает (code, как_определили)."""
    if explicit:
        if not _reg.is_set(explicit):
            raise SystemExit(f"неизвестный сет: {explicit} (знаю: {', '.join(_reg.SETS)})")
        return explicit.lower(), "--set"

    # 1) теги вида `1 Old Thrush (HOB) 2` — самый надёжный источник
    tags = Counter()
    for p in (deck_path, pool_path):
        if not p or not os.path.exists(p):
            continue
        for line in open(p, encoding="utf-8"):
            m = re.search(r"\(([A-Za-z0-9]{3,5})\)\s+\S+\s*$", line.strip())
            if m and _reg.is_set(m.group(1)):
                tags[m.group(1).lower()] += 1
    if tags:
        return tags.most_common(1)[0][0], "теги (SET) в листе"

    # 2) префикс файла пула: pools/hob_31a78cee.txt
    if pool_path:
        pref = os.path.basename(pool_path).split("_")[0].lower()
        if _reg.is_set(pref):
            return pref, "имя файла пула"

    # 3) по числу совпавших имён карт в каждом <set>_set.json
    import json
    names = {norm(n) for _, n in sum(split_deck(deck_path), [])}
    best, hits = None, 0
    for code in _reg.SETS:
        p = os.path.join(HERE, f"{code}_set.json")
        if not os.path.exists(p):
            continue
        pool_names = set()
        for c in json.load(open(p)):
            pool_names.add(norm(c.get("name", "")))
            pool_names.add(norm(c.get("name", "").split(" //")[0]))
        k = len(names & pool_names)
        if k > hits:
            best, hits = code, k
    if best:
        return best, f"совпадение имён карт ({hits})"
    raise SystemExit("не удалось определить сет — укажи явно: --set hob")


def deck_colors(path, db):
    """Цвета колоды по пипам мейна (гибрид — половина каждому, порог четверть от ведущего)."""
    md, _ = split_deck(path)
    pips = Counter()
    for n, name in md:
        c = db.get(norm(name)) or db.get(norm(name.split(",")[0]))
        if not c or "Land" in face(c, "type_line"):
            continue
        for sym in re.findall(r"\{([^}]+)\}", face(c, "mana_cost")):
            parts = [ch for ch in sym.upper().split("/") if ch in "WUBRG"]
            for ch in parts:
                pips[ch] += n / len(parts)
    if not pips:
        return ""
    top = max(pips.values())
    return "".join(x for x in "WUBRG" if pips.get(x, 0) >= max(3, top * 0.25))


def load_refs(setcode, db, rat):
    """Референс-листы ИМЕННО этого сета. Пусто -> часть (а) не печатается."""
    files = []
    sub = os.path.join(REF_DIR, setcode)
    if os.path.isdir(sub):
        files = [os.path.join(sub, f) for f in sorted(os.listdir(sub)) if f.endswith(".txt")]
    elif setcode == LEGACY_REF_SET and os.path.isdir(REF_DIR):
        files = [os.path.join(REF_DIR, f) for f in sorted(os.listdir(REF_DIR))
                 if f.endswith(".txt")]
    # Цвета референса считаем ТОЙ ЖЕ функцией, что и для своей колоды. Поле colors из
    # metrics() построено по другому правилу (real/splash с иным порогом), и фильтр по паре
    # молча не совпадал: листов WB находилось 4 вместо 18, WU — 2 вместо 25, то есть
    # сравнение снова уезжало на весь сет. Поймано сразу после внесения фильтра, 17.08.2026.
    out = []
    for f in files:
        m = metrics(f, db, rat)
        m["pair"] = deck_colors(f, db)
        out.append(m)
    return out



def pct(vals, v):
    """Перцентиль значения в популяции: доля листов не выше моего."""
    if not vals:
        return None
    return round(100 * sum(1 for x in vals if x <= v) / len(vals))


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
            # Гибрид {W/U} — ОДИН пип, а не два: он даёт по половине каждому цвету.
            # Было `for ch in sym.split("/"): pips[ch] += n` — полная единица обоим, из-за чего
            # WB-колода с пятью {W/U}-картами (Patient Instructor ×3, Eagle's Rescue ×2)
            # набирала U=7 и считалась WUB. Последствие не косметическое: «жадный топ-N»
            # строился из ТРЁХцветного пула, и тест процесса показывал «отдано +0.72 ✅ в норме»
            # там, где на самом деле +0.36 — то есть слабее популяции. Поймано переигровкой
            # драфта 31a78cee 17.08.2026: единственная ось, где колода выглядела лучше всех,
            # оказалась артефактом измерения.
            parts = [ch for ch in sym.upper().split("/") if ch in "WUBRG"]
            for ch in parts:
                pips[ch] += n / len(parts)
    # Порог основного цвета — ОТНОСИТЕЛЬНЫЙ. Абсолютное «>=3 пипа» ловило сплеш и остаток
    # гибридов как полноценный цвет: в WB-колоде с пятью {W/U} синий набирал 3.5 и делал
    # пул трёхцветным, а «жадный топ-N» строился из карт, которые колода физически не
    # кастует. Правило то же, что в learn.py: цвет свой, если он не меньше четверти
    # ведущего. Нижняя граница 3 оставлена для очень коротких листов.
    _top = max(pips.values(), default=0)
    mains = {c for c, v in pips.items() if v >= max(3, _top * 0.25)}

    def G(nm):
        r = rat.get(norm(nm)) or rat.get(norm(nm.split(",")[0]))
        return round(r["ever_drawn_win_rate"] * 100, 1) if r and r.get("ever_drawn_win_rate") else None

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
    pool_path = setcode = None
    for flag in ("--pool", "--set"):
        if flag in sys.argv:
            i = sys.argv.index(flag)
            val = sys.argv[i + 1] if len(sys.argv) > i + 1 else None
            if flag == "--pool":
                pool_path = val
            else:
                setcode = val
            args = [a for a in args if a != val]
    path = args[0]

    setcode, how = detect_set(path, pool_path, setcode)
    db, rat = load_db(), load_ratings(setcode)
    if not rat:
        print(f"  ⚠ нет файла рейтингов 17Lands для {setcode.upper()} "
              f"({_reg.RATING_FILE.get(setcode)}) — GIH-оси и тест процесса молчат.\n"
              f"    Скачать: python3 fetch_17l.py {setcode}")

    refs = load_refs(setcode, db, rat)
    mine = metrics(path, db, rat)

    print(f"\n=== АУДИТ: {mine['name']} · сет {setcode.upper()} ({how}) ===")
    flags = []
    if not refs:
        print(f"\n  ⚠ ЧАСТЬ (а) ПРОПУЩЕНА: нет референс-листов 7-1/7-2 по {setcode.upper()}.")
        print(f"    Сравнивать с популяцией другого сета запрещено (§ КАЛИБРОВКА, закон 1):")
        print(f"    другой пул removal, другая скорость, другая доля эвейжна — это шум.")
        print(f"    Чтобы включить: класть листы 7-1/7-2 в ref_decks/{setcode}/*.txt")
    else:
        # Сравнение идёт со СВОЕЙ ПАРОЙ, а не со всем сетом (правка 17.08.2026).
        # На 298 листах диапазоны по сету настолько широки (существ 9–21, removal 0–12),
        # что «в диапазоне» получали ВСЕ колоды сразу — включая ту, которую разбор назвал
        # провальной. Прибор, который не отличает подсудимого от свидетеля, не прибор.
        # Вдобавок печатается ПЕРЦЕНТИЛЬ: «в диапазоне» на 5-м процентиле и на 50-м —
        # разные вещи, а min–max их не различает.
        my_colors = deck_colors(path, db)
        same = [r for r in refs if r.get("pair") == my_colors] if my_colors else []
        use, scope = (same, f"пара {my_colors}") if len(same) >= 6 else (refs, "весь сет")
        if len(same) < 6 and my_colors:
            print(f"    ⚠ листов пары {my_colors} всего {len(same)} — сравниваю со всем сетом,\n"
                  f"      это грубее: диапазоны сета шире, чем у любой отдельной пары.")
        print(f"    (против {len(use)} листов 7-1/7-2 · {scope})\n")
        print(f"{'ось':22} {'моё':>7}   {'победители (мин–медиана–макс)':<28} {'проц.':>6}  вердикт")
        print("-" * 92)
        for key, label in AXES:
            vals = sorted(r[key] for r in use if r[key] is not None)
            if not vals or mine[key] is None:
                continue
            lo, hi = vals[0], vals[-1]
            med = vals[len(vals) // 2]
            v = mine[key]
            q = pct(vals, v)
            if v < lo:
                verdict = f"⚠ НИЖЕ всех {len(vals)}"
                flags.append(f"{label}: {v} — ниже минимума ({lo}) у листов {scope}")
            elif q is not None and q <= 10:
                verdict = "🟡 нижние 10% популяции"
                flags.append(f"{label}: {v} — нижние 10% ({scope}), медиана {med}")
            elif v > hi:
                verdict = "↑ выше всех (не порок, но проверь зачем)"
            elif q is not None and q >= 90:
                verdict = "↑ верхние 10%"
            else:
                verdict = "в диапазоне"
            print(f"{label:22} {v:>7}   {lo:>6} – {med:^6} – {hi:<6}  {str(q) + '%':>6}  {verdict}")

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
        elif d > 1.0:
            print("\n  🔴 ОТКЛОНЕНИЕ ВЫШЕ МАКСИМУМА ПОПУЛЯЦИИ (у 23 победителей макс +0.96).")
            print("     Это зеркальная ошибка: не «нет плана», а «план дороже качества карт».")
            print("     Проверь список ниже — если там есть карты ТВОЕЙ оси, они срезаны зря.")
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
    elif refs:
        print("\n  Ни по одной оси не ниже минимума победителей.")


if __name__ == "__main__":
    main()
