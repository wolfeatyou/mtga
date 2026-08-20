#!/usr/bin/env python3
"""
ДОСЬЕ ПУЛА — вход сборки: линии (маршруты × пары) + карточка каждой карты В КОНТЕКСТЕ пула.

    python3 pool_dossier.py <pool.txt|deck.txt> [--set hob] [--pair BG[,BR]] [--lanes]

ЗАЧЕМ (заведено 20.08.2026, дизайн оркестрированной сборки — mode_build.md § МУЛЬТИСБОРКА).
Два измеренных факта:
  · системный лик советчика — «считаю карту в вакууме по GIH вместо связки в МОЁМ пуле»
    (память mtg-count-enabler-density; JOURNAL § 8.16 ③: прозовая поправка проигрывает
    сортировке — значит контекст карты должен лежать В ТОМ ЖЕ выводе, что и рейтинг);
  · данные для ответа уже добыты, но разложены по четырём местам (<set>_combos.json,
    <set>_traps.json: played/routes/traps/pair_bad, рейтинги 17Lands, оракл-тексты) —
    и на сборке систематически не сводились воедино.
Досье сводит их в один вывод: для каждой карты пула — рейтинг, роли, частота и потолок
копий у победителей ЭТОЙ пары, связки с картами ЭТОГО пула, флаги ловушек.

ЛИНИИ: для каждой пары с данными — запас пула по маршрутам § 8.17 (КРУПНЫЕ ТЕЛА · ВОЗДУХ ·
ОТВЕТЫ · ШИРИНА) против медиан победителей пары. Медианы — routes из <set>_traps.json;
пул считается ТОЙ ЖЕ функцией find_traps.sig_of, которой посчитаны сами медианы
(JOURNAL § 8.5: копия логики у потребителя не измеряет). Это детерминированная часть
гейта оркестратора: ≥2 достижимых маршрутов → веер строителей, иначе одиночная сборка.

ЧЕМ ДОСЬЕ НЕ ЯВЛЯЕТСЯ. Не скоринг и не судья. Связки как ось ОЦЕНКИ колоды отвергнуты
дважды (§ 4.4 — паритет с победителями; § 8.7 — 3160 парных признаков дают −0.030 AUC):
здесь они ВХОД для решения «зачем карта в этой колоде», а не слагаемое качества.
GIH — ось сортировки, не мерило колоды (§ КАЛИБРОВКА). Средний GIH МЕЖДУ парами несёт
перекос силы архетипа (§ 8.8 ③: на MSH ±0.4–0.8σ, на HOB не измерен — датасета нет),
поэтому колонка top23 в таблице линий информационная, решение по ней не принимается.
"""
import json
import os
import re
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sets_registry as _reg                 # noqa: E402
import build_audit as A                      # noqa: E402  (split_deck, rating_of, detect_set)
import deck_profile as DP                    # noqa: E402  (регексы ролей, oracle, face)
import find_traps as FT                      # noqa: E402  (castable, sig_of, norm)

# Тот же порог, что draft_live.MIN_LIFT (сам draft_live не импортируем: его setcode()
# читает sys.argv и молча грузит чужой сет — латентная ловушка из JOURNAL § 8.5).
MIN_LIFT = 1.5
BOMB_GIH = 63          # порог 💣 — тот же, что в draft_live.bomb_bonus (§ 8.9 правки)
CORE_SHARE = 0.5       # ★ = карта у ≥50% победителей пары (частота, не «ядро» learn.py)
BASICS = {"plains", "island", "swamp", "mountain", "forest"}
ROUTES = [("big", "тел≥4"), ("evp", "воздух"), ("rem", "ответы"), ("wide", "ширина")]


def load_json(setcode, suffix):
    p = os.path.join(HERE, f"{setcode}_{suffix}.json")
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}


def read_pool(path):
    """Пул = мейн + сайд файла, слитые по копиям. [(n, display_name)]."""
    md, sb = A.split_deck(path)
    merged, order = Counter(), []
    for n, name in md + sb:
        if name not in merged:
            order.append(name)
        merged[name] += n
    return [(merged[nm], nm) for nm in order]


def index_cards(cards):
    """FT.norm-ключ → карта сет-файла (лицевая сторона режется самим FT.norm)."""
    return {FT.norm(c["name"]): c for c in cards}


def pool_index(pool, by_key):
    """[(n, name, card|None, fkey)] — карта пула + её объект из сет-файла."""
    out = []
    for n, name in pool:
        k = FT.norm(name)
        out.append((n, name, by_key.get(k), k))
    return out


def castable_counts(pidx, pair):
    """{fkey: копий} кастуемой в паре части пула (правило find_traps.castable:
    гибриду достаточно одной половины — доступ, а не принадлежность)."""
    cnt = {}
    for n, _, c, k in pidx:
        if c is not None and FT.castable(c, pair):
            cnt[k] = cnt.get(k, 0) + n
    return cnt


def lane_rows(pidx, cards, traps, rat):
    """Таблица линий: по каждой паре из routes — запас пула против медиан победителей."""
    rows = []
    for pair, med in sorted((traps.get("routes") or {}).items()):
        cnt = castable_counts(pidx, pair)
        sig = FT.sig_of(cnt, cards)
        margins = {
            "big": sig["big"] - med["big"],
            "evp": sig["evp"] - med["evp"],
            "rem": sig["rem"] - med["rem"],
            "wide": min(sig["cre"] - med["cre"], sig["cheap"] - med["cheap"]),
        }
        gihs = []
        playables = 0
        for n, _, c, k in pidx:
            if c is None or not FT.castable(c, pair) or "Land" in FT.face(c, "type_line"):
                continue
            playables += n
            r = A.rating_of(rat, c["name"])
            if r and r.get("ever_drawn_win_rate"):
                gihs += [r["ever_drawn_win_rate"] * 100] * n
        gihs.sort(reverse=True)
        top23 = round(sum(gihs[:23]) / min(23, len(gihs)), 1) if gihs else None
        rows.append(dict(pair=pair, n=med["n"], playables=playables, top23=top23,
                         sig=sig, med=med, margins=margins,
                         feasible=sum(1 for v in margins.values() if v >= 0)))
    rows.sort(key=lambda r: (-r["playables"], -(r["top23"] or 0)))
    return rows


def roles_of(c):
    tl = FT.face(c, "type_line")
    ora = DP.oracle(c)
    mc = FT.face(c, "mana_cost")
    out = []
    if "Land" in tl:
        # Цвета земли печатаются явно (поймано 20.08.2026, § 8.22): «нонбейзик = фикс»
        # без проверки produced_mana назвал Lake-town ({T}: Add {W} or {U}, тапленная)
        # «фиксом» в BG-колоде — и оба opus-агента сыграли землю НЕ СВОИХ цветов;
        # поймал только sonnet/high-судья по полному оракл-тексту.
        pm = c.get("produced_mana") or []
        out.append("земля" + (":" + "/".join(pm) if pm else ""))
        if FT.norm(c["name"]) not in BASICS and (DP.ANYCOLOR_RE.search(ora) or len(pm) >= 5):
            out.append("фикс")
        return out
    is_cre = "Creature" in tl
    cmc = int(c.get("cmc") or 0)
    if is_cre:
        if cmc <= 2 and "{X}" not in mc:
            out.append("2дроп")
        pw = c.get("power")
        if pw is None and c.get("card_faces"):
            pw = c["card_faces"][0].get("power")
        try:
            if int(pw) >= 4:
                out.append("тело≥4")
        except (TypeError, ValueError):
            pass
        if DP.EVASION_RE.search(ora + " " + tl):
            out.append("эвейжн")
        if DP.REACH_RE.search(ora + " " + tl):
            out.append("reach")
    if DP.HARD_RE.search(ora):
        out.append("removal!")
    elif DP.SOFT_RE.search(ora):
        out.append("интеракция")
    if DP.ANYCOLOR_RE.search(ora):
        out.append("фикс")
    return out


def pt_of(c):
    if "Creature" not in FT.face(c, "type_line"):
        return ""
    pw = c.get("power")
    tf = c.get("toughness")
    if pw is None and c.get("card_faces"):
        pw = c["card_faces"][0].get("power")
        tf = c["card_faces"][0].get("toughness")
    return f"{pw}/{tf}" if pw is not None else ""


def combo_edges(pidx, combos):
    """Связки, у которых ОБЕ половины лежат в этом пуле (lift ≥ MIN_LIFT), и анти-связки."""
    have = {k for _, _, c, k in pidx if c is not None}
    edges, anti = [], []
    for cb in (combos.get("combos") or []):
        ks = [FT.norm(x) for x in cb.get("cards", [])]
        if len(ks) == 2 and all(k in have for k in ks) and cb.get("lift", 0) >= MIN_LIFT:
            edges.append(cb)
    for ab in (combos.get("_anti") or []):
        ks = [FT.norm(x) for x in ab.get("cards", [])]
        if len(ks) == 2 and all(k in have for k in ks):
            anti.append(ab)
    edges.sort(key=lambda x: -x.get("lift", 0))
    return edges, anti


def card_flags(k, pair, traps):
    """(⚠-флаги, played%, потолок копий) карты в контексте пары."""
    flags = []
    pl = (traps.get("played") or {}).get(k)
    share = cap = None
    if pl:
        share = pl.get("pairs", {}).get(pair)
        cap = pl.get("max_pairs", {}).get(pair, pl.get("max"))
    if any(t.get("key") == k for t in traps.get("traps") or []):
        flags.append("⚠ЛОВУШКА-СЕТА")
    if any(x.get("key") == k for x in (traps.get("pair_bad") or {}).get(pair, [])):
        flags.append("⚠НЕ-В-ЭТОЙ-ПАРЕ")
    return flags, share, cap


def render(path, setcode=None, pairs=None, lanes_only=False):
    setcode, how = A.detect_set(path, path, setcode)
    cards = json.load(open(os.path.join(HERE, f"{setcode}_set.json"), encoding="utf-8"))
    rat = A.load_ratings(setcode)
    traps = load_json(setcode, "traps")
    combos = load_json(setcode, "combos")
    by_key = index_cards(cards)
    pool = read_pool(path)
    pidx = pool_index(pool, by_key)

    out = []
    nl = sum(n for n, _, c, _ in pidx if c is not None and "Land" not in FT.face(c, "type_line"))
    meta = traps.get("meta") or {}
    out.append(f"=== ДОСЬЕ ПУЛА: {os.path.basename(path)} · сет {setcode.upper()} ({how}) ===")
    out.append(f"карт: {sum(n for n, *_ in pidx)} (нонлендов {nl}) · "
               f"референс: {meta.get('lists', '?')} листов 7-1/7-2 · связок в базе: "
               f"{len(combos.get('combos') or [])}")
    miss = [name for _, name, c, _ in pidx if c is None]
    if miss:
        out.append(f"⚠ не найдены в {setcode}_set.json: {', '.join(miss)}")

    rows = lane_rows(pidx, cards, traps, rat)
    if rows:
        out.append("")
        out.append("── ЛИНИИ: запас пула против медиан победителей пары "
                   "(маршрут достижим при запасе ≥0) ──")
        out.append(f"{'пара':<5}{'n':>4} {'плей':>5} {'top23':>6}  "
                   + "".join(f"{lab:>9}" for _, lab in ROUTES) + "  достижимо")
        for r in rows:
            if r["playables"] < 15:
                continue
            cells = "".join(f"{r['margins'][key]:>+8}{'✔' if r['margins'][key] >= 0 else ' '}"
                            for key, _ in ROUTES)
            out.append(f"{r['pair']:<5}{r['n']:>4} {r['playables']:>5} "
                       f"{r['top23'] if r['top23'] is not None else '—':>6}  {cells}  "
                       f"{r['feasible']}/4")
        out.append("   top23 = средний GIH лучших 23 кастуемых — ИНФОРМАЦИЯ, не решение: "
                   "между парами GIH перекошен силой архетипа (§ 8.8 ③, на HOB не измерен).")
        out.append("   воздух/ширина считаются в единицах маршрута (сумм. сила эвейжна / "
                   "мин(существа, дешёвые) − медиана).")
    if lanes_only:
        print("\n".join(out))
        return rows

    sel = pairs or [r["pair"] for r in rows[:2] if r["playables"] >= 18]
    edges, anti = combo_edges(pidx, combos)
    partner = {}
    for cb in edges:
        a, b = (FT.norm(x) for x in cb["cards"])
        partner.setdefault(a, []).append((cb["cards"][1], cb["lift"]))
        partner.setdefault(b, []).append((cb["cards"][0], cb["lift"]))

    for pair in sel:
        out.append("")
        out.append(f"── КАРТЫ ПУЛА · пара {pair} (частота/потолок — по {pair}-листам "
                   f"победителей, ★ = у ≥{int(CORE_SHARE*100)}%) ──")
        rows_c, off = [], []
        for n, name, c, k in pidx:
            if c is None:
                continue
            r = A.rating_of(rat, c["name"])
            gih = round(r["ever_drawn_win_rate"] * 100, 1) if r and r.get("ever_drawn_win_rate") else None
            alsa = round(r["avg_seen"], 1) if r and r.get("avg_seen") else None
            (rows_c if FT.castable(c, pair) else off).append((gih, alsa, n, name, c, k))
        rows_c.sort(key=lambda x: (x[0] is None, -(x[0] or 0)))
        for gih, alsa, n, name, c, k in rows_c:
            flags, share, cap = card_flags(k, pair, traps)
            if "Land" in FT.face(c, "type_line"):
                pm = set(c.get("produced_mana") or [])
                if pm and not (pm & set(pair)) and len(pm) < 5:
                    flags.append("⚠НЕ-ДАЁТ-ЦВЕТОВ-ПАРЫ")
            rl = ",".join(roles_of(c)) or "—"
            pt = pt_of(c)
            core = "★" if share is not None and share >= CORE_SHARE else ""
            stat = (f"{pair} {int(round(share*100))}%{core}" if share is not None else f"{pair} —")
            if cap:
                stat += f" ≤{cap}"
                if n > cap:
                    flags.append(f"⚠×{n}>потолка")
            ed = ""
            if k in partner:
                ed = " · ↔" + "; ".join(f"{pn[:22]}(×{lf:.1f})" for pn, lf in partner[k][:3])
            bomb = " 💣" if gih is not None and gih >= BOMB_GIH else ""
            fl = (" " + " ".join(flags)) if flags else ""
            g = f"{gih:.1f}" if gih is not None else "  — "
            a_ = f"A{alsa}" if alsa is not None else ""
            out.append(f" {g:>5} {a_:>5} ×{n} {name[:34]:<34} {pt:<5} {rl:<28} {stat}{ed}{bomb}{fl}")
            # ПОЛНЫЙ оракл-текст (внесено 20.08.2026, запрос «всегда читай текст»).
            # Сет может быть новее кат-оффа модели — строители/судья/советчик обязаны
            # брать механику из напечатанного, а не из памяти (§ 8.16: «value-движок
            # приписан защитной саге без чтения текста»). Ремайндеры в скобках срезаны.
            ora = re.sub(r"\s*\([^()]*\)", "", DP.oracle(c)).replace("\n", " · ").strip()
            if ora and "Land" not in FT.face(c, "type_line"):
                out.append(f"          {ora}")
        if off:
            names = ", ".join(f"{name}×{n}" if n > 1 else name for _, _, n, name, _, _ in off)
            out.append(f"   вне пары {pair}: {names}")

    if edges or anti:
        out.append("")
        out.append("── СВЯЗКИ, ОБЕ ПОЛОВИНЫ КОТОРЫХ В ПУЛЕ (механизм подтверждён текстом + "
                   f"lift≥{MIN_LIFT} по {meta.get('lists', '?')} листам) ──")
        for cb in edges:
            out.append(f" ↔ {cb['cards'][0]} + {cb['cards'][1]} · lift {cb['lift']:.1f} "
                       f"({cb.get('decks', '?')} колод, {cb.get('pair', '?')}): {cb.get('why', '')}")
        for ab in anti:
            out.append(f" ⚡АНТИ {ab['cards'][0]} + {ab['cards'][1]}: {ab.get('why', '')}")

    print("\n".join(out))
    return rows


def deck_check(path, setcode, pair):
    """Скорборд ГОТОВОГО мейна для судьи (mode_build.md § МУЛЬТИСБОРКА): достигнутые
    маршруты против медиан пары, потолки копий, ⚠-флаги в мейне, средний GIH мейна.
    Считает те же sig_of/played, что и досье пула, — судья и строитель смотрят в один прибор."""
    setcode, _ = A.detect_set(path, path, setcode)
    cards = json.load(open(os.path.join(HERE, f"{setcode}_set.json"), encoding="utf-8"))
    rat = A.load_ratings(setcode)
    traps = load_json(setcode, "traps")
    by_key = index_cards(cards)
    md, _sb = A.split_deck(path)
    pidx = pool_index([(n, nm) for n, nm in md], by_key)
    cnt = {}
    gihs = []
    for n, name, c, k in pidx:
        if c is None or "Land" in FT.face(c, "type_line"):
            continue
        cnt[k] = cnt.get(k, 0) + n
        r = A.rating_of(rat, c["name"])
        if r and r.get("ever_drawn_win_rate"):
            gihs += [r["ever_drawn_win_rate"] * 100] * n
    sig = FT.sig_of(cnt, cards)
    med = (traps.get("routes") or {}).get(pair)
    out = [f"=== СКОРБОРД МЕЙНА: {os.path.basename(path)} · пара {pair} ==="]
    out.append(f"нонлендов {sum(cnt.values())} · средний GIH мейна "
               f"{round(sum(gihs)/len(gihs), 2) if gihs else '—'} (карт с данными {len(gihs)})")
    if med:
        marks = []
        for key, lab in ROUTES:
            have = (min(sig["cre"] - med["cre"], sig["cheap"] - med["cheap"]) + 0
                    if key == "wide" else sig[key] - med[key])
            val = (f"{sig['cre']}сущ/{sig['cheap']}дёш" if key == "wide"
                   else str(sig[key]))
            marks.append(f"{lab} {val} ({'✔' if have >= 0 else '✗'} медиана "
                         + (f"{med['cre']}/{med['cheap']}" if key == "wide" else str(med[key])) + ")")
        out.append("маршруты: " + " · ".join(marks))
    warn = []
    for n, name, c, k in pidx:
        if c is None:
            continue
        flags, share, cap = card_flags(k, pair, traps)
        if "Land" in FT.face(c, "type_line"):
            pm = set(c.get("produced_mana") or [])
            if pm and not (pm & set(pair)) and len(pm) < 5:
                flags.append("⚠НЕ-ДАЁТ-ЦВЕТОВ-ПАРЫ")
        if cap and n > cap:
            flags.append(f"⚠×{n}>потолка(≤{cap})")
        if share is not None and share < 0.08 and "Land" not in FT.face(c, "type_line"):
            flags.append(f"у победителей {pair} {int(round(share*100))}%")
        if flags:
            warn.append(f"   · {name}: " + " ".join(flags))
    out.append("флаги мейна:" if warn else "флаги мейна: нет")
    out += warn
    print("\n".join(out))


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print(__doc__)
        sys.exit(1)
    setcode = pairs = deck_pair = None
    if "--set" in sys.argv:
        setcode = sys.argv[sys.argv.index("--set") + 1]
        args = [a for a in args if a != setcode]
    if "--pair" in sys.argv:
        raw = sys.argv[sys.argv.index("--pair") + 1]
        pairs = [p.strip().upper() for p in raw.split(",") if p.strip()]
        args = [a for a in args if a != raw]
    if "--deck" in sys.argv:
        deck_pair = sys.argv[sys.argv.index("--deck") + 1].upper()
        args = [a for a in args if a.upper() != deck_pair]
    if deck_pair:
        deck_check(args[0], setcode, deck_pair)
        return
    render(args[0], setcode, pairs, lanes_only="--lanes" in sys.argv)


if __name__ == "__main__":
    main()
