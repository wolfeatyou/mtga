#!/usr/bin/env python3
"""
Профиль лимитед-колоды по нашим порогам — для сравнения ЧУЖИХ (diamond/mythic) листов
с нашими сборками на одних и тех же числах.

Считает то, что у нас операционализировано как пороги/квоты, и НИЧЕГО не додумывает:
  · земли / нонленды
  · существа отдельно от спеллов, кривая по каждой группе
  · **существ cmc≤2** — квота ⚑ КРИВАЯ (4 шт ≈ 55% «существо к T2», 5 ≈ 64-65%)
  · ломатели стойки (flying / menace / unblockable / trample / reach)
  · безусловное removal (destroy|exile target) отдельно от условного
  · верх кривой: cmc≥5 (≤4) и cmc≥6 (≤2 — переоткалибровано на 298 листах HOB)
  · средний GIH (глобальный) и парный, если есть cache_17l_<set>_<PAIR>.json

Usage:  python3 deck_profile.py <decklist.txt> [PAIR]
        PAIR — пара для парного GIH, напр. UB. Необязательно.
"""
import json, os, re, sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sets_registry as _reg  # единый список сетов
SETS = _reg.SET_FILES
RATINGS = {"msh": "17l_msh_premierdraft.json", "sos": "17l_sos_premierdraft.json",
           "mkm": "17l_mkm_premierdraft.json", "hob": "17l_hob_premierdraft.json"}


def norm(s):
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def load_db():
    db = {}
    for fn in SETS:
        p = os.path.join(HERE, fn)
        if not os.path.exists(p):
            continue
        for c in json.load(open(p)):
            for key in (c.get("name", ""), c.get("name", "").split(" //")[0]):
                db.setdefault(norm(key), c)
    return db


def load_ratings(setcode="msh"):
    p = os.path.join(HERE, RATINGS.get(setcode, ""))
    if not os.path.exists(p):
        return {}
    return {norm(c["name"]): c for c in json.load(open(p)) if c.get("name")}


def load_pair(setcode, pair):
    p = os.path.join(HERE, f"cache_17l_{setcode}_{pair.upper()}.json")
    if not os.path.exists(p):
        return {}
    raw = json.load(open(p))
    rows = raw if isinstance(raw, list) else raw.get("data", raw.get("cards", []))
    out = {}
    for c in rows if isinstance(rows, list) else []:
        if isinstance(c, dict) and c.get("name"):
            out[norm(c["name"])] = c
    return out


def parse_deck(path):
    """(count, name) до строки Sideboard."""
    out = []
    for line in open(path, encoding="utf-8"):
        s = line.strip()
        if not s or s.lower().startswith("deck") or s.lower().startswith("about"):
            continue
        if s.lower().startswith("sideboard"):
            break
        m = re.match(r"^(\d+)\s+(.+?)(?:\s+\([A-Za-z0-9]+\)\s+\S+)?$", s)
        if m:
            out.append((int(m.group(1)), m.group(2).strip()))
    return out


def face(c, k):
    if "card_faces" in c and not c.get(k):
        return c["card_faces"][0].get(k, "") or ""
    return c.get(k, "") or ""


def oracle(c):
    if "card_faces" in c:
        return " // ".join((f.get("oracle_text") or "") for f in c["card_faces"])
    return c.get("oracle_text") or ""


# Reach ВЫНЕСЕН из эвейжна 17.08.2026. Он не пробивает стойку, а держит её — блокирует
# летунов. Слитая ось врала в обе стороны: колода с 3 летунами и 4 reach считалась
# «в норме по ломателям», и именно так был проигран сид 42 слепого A/B — судья написал
# «упирается в стену на земле без плана пробить», а аудит дал ей ЛУЧШЕЕ отклонение
# прогона (4.0 против 13.0 у выигравшей). По 298 трофейным листам: пробивающих медиана 4,
# reach медиана 1 — то есть слияние завышало порог примерно на одну карту.
EVASION_RE = re.compile(r"\bflying\b|\bmenace\b|can't be blocked|\btrample\b", re.I)
REACH_RE = re.compile(r"\breach\b", re.I)
# «up to one other target …» — та же безусловная убивалка, что и «destroy target …».
# Без этих групп Azog, Moria's Ruin («destroy up to one other target creature») считался
# нулём, и колода с двумя копиями получала «безусл. removal 0 — нижние 10% популяции»
# (поймано на сборке 18.08.2026, JOURNAL § 8.3 ②).
# Негативный lookahead отсекает БЛИНК своих перманентов: Elrond, Moon-Reader
# («exile up to two other target nonland permanents you control») — не removal.
# Проверено 18.08.2026: по сету правка добавляет ровно 2 карты (Azog, Moria's Ruin ·
# Celebrate the Mountain-king), не теряет ни одной, и медиана оси по 298 листам
# остаётся 1 — эталоны JOURNAL § 2.1 и базовая линия § 2.3 не сдвигаются.
HARD_RE = re.compile(
    r"(?:destroy|exile)\s+(?:up to \w+\s+)?(?:other\s+)?target\s+"
    r"(?:creature|permanent|nonland|attacking|blocking)"
    r"(?![^.]{0,60}?\byou control\b)", re.I)
SOFT_RE = re.compile(r"gets -\d|gets \-|deals \d+ damage to target|tap target|doesn't untap|"
                     r"fights|return target .* to (its owner's|their owner's) hand", re.I)
# Вынесен из metrics() на уровень модуля 20.08.2026 — pool_dossier.py помечает фикс той же
# регуляркой, а не копией (JOURNAL § 8.5: копия логики у потребителя не измеряет).
ANYCOLOR_RE = re.compile(r"mana of any (one )?color|create a treasure", re.I)


def metrics(path, db, rat, prat=None):
    """Все метрики листа одним словарём. Используется и CLI, и build_audit.py."""
    prat = prat or {}
    entries = parse_deck(path)
    lands = nonlands = fixers = 0
    cre_curve, spell_curve, pips = Counter(), Counter(), Counter()
    pure_pips = Counter()
    cheap_bodies, evasion, hard, soft, topend, missing = [], [], [], [], [], []
    reach = []
    # 🔴 «ЧЕМ Я УБИВАЮ» — тела силой ≥4 (ось заведена 20.08.2026 по разбору драфта eba1b036).
    # Повод: колода 0-3, в двух доигранных партиях нанесла РОВНО НОЛЬ урона (оппонент 20→22
    # оба раза), а аудит не показал ни одного дефекта: существ 14, эвейжн 4 карты, суммарная
    # сила 34 — всё «в диапазоне». Ни одна ось не спрашивала «чем эта колода заканчивает
    # партию». Замер по 298 листам: тел силы ≥4 медиана 3 (UR — 4, минимум 1); у той колоды
    # было 2 = 7-й перцентиль своей пары. Это единственная ось, которая её отбраковывает.
    big_bodies = []
    gih_g, gih_p = [], []
    BASICS = {"plains", "island", "swamp", "mountain", "forest"}
    ANYCOLOR = ANYCOLOR_RE

    for n, name in entries:
        c = db.get(norm(name)) or db.get(norm(name.split(",")[0]))
        if not c:
            missing.append(name)
            continue
        tl = face(c, "type_line")
        if "Land" in tl:
            lands += n
            if norm(name) not in BASICS:
                fixers += n          # нонбейзик = источник фикса (дуал/утилити)
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
            if len(parts) == 1:
                pure_pips[parts[0]] += n
        if ANYCOLOR.search(oracle(c)):
            fixers += n
        nonlands += n
        cmc = int(c.get("cmc") or 0)
        is_cre = "Creature" in tl
        (cre_curve if is_cre else spell_curve)[cmc] += n
        # {X}-костные не считаем двойками: Scryfall берёт X=0 (Ruinous Wrecking Crew {X}{B}{R} → cmc 2)
        if is_cre and cmc <= 2 and "{X}" not in face(c, "mana_cost"):
            cheap_bodies += [name] * n
        if is_cre and EVASION_RE.search(oracle(c) + " " + tl):
            evasion += [name] * n
        if is_cre and REACH_RE.search(oracle(c) + " " + tl):
            reach += [name] * n
        if is_cre:
            pw = c.get("power") if c.get("power") is not None else face(c, "power")
            try:
                if int(pw) >= 4:
                    big_bodies += [name] * n
            except (TypeError, ValueError):
                pass          # */X и прочие нечисловые силы в ось не идут
        ot = oracle(c)
        if HARD_RE.search(ot):
            hard += [name] * n
        elif SOFT_RE.search(ot):
            soft += [name] * n
        if cmc >= 5:
            topend += [f"{name}({cmc})"] * n
        r = rat.get(norm(name)) or rat.get(norm(name.split(",")[0]))
        if r and r.get("ever_drawn_win_rate"):
            gih_g += [round(r["ever_drawn_win_rate"] * 100, 1)] * n
        pr = prat.get(norm(name)) or prat.get(norm(name.split(",")[0]))
        if pr and pr.get("ever_drawn_win_rate"):
            gih_p += [round(pr["ever_drawn_win_rate"] * 100, 1)] * n

    def avg(xs):
        return round(sum(xs) / len(xs), 2) if xs else None

    ncre = sum(cre_curve.values())
    # ЦВЕТА СЧИТАЮТСЯ ТОЛЬКО ПО ЧИСТЫМ ПИПАМ (17.08.2026). Гибрид {W/U} кастуется любой
    # из половин, то есть НЕ требует второго цвета и не создаёт нужды в фиксинге. Раньше он
    # шёл по половине пипа в каждый цвет и порождал фантомные «сплеши»: из 251 сплеша в 298
    # трофейных листах 202 (80%) не имели НИ ОДНОГО чистого пипа своего цвета, а медиана
    # источников под такой «сплеш» была 0 — то есть его нечем было кастовать, потому что его
    # и не было. Доля колод со сплешем падает с 61% до 15%, и вывод переворачивается:
    # победители в основном НЕ сплешат.
    real = sorted([c for c, v in pure_pips.items() if v >= 3], key=lambda x: -pure_pips[x])
    splash = sorted([c for c, v in pure_pips.items() if 0 < v < 3], key=lambda x: -pure_pips[x])
    # Гибридные цвета, доступные колоде «бесплатно» — не цвет колоды, но знать полезно.
    hybrid_only = sorted(c for c, v in pips.items()
                         if v > 0 and pure_pips.get(c, 0) == 0)
    return dict(
        name=os.path.basename(path), lands=lands, nonlands=nonlands, creatures=ncre,
        cheap=len(cheap_bodies), cheap_names=cheap_bodies, evasion=len(evasion),
        big=len(big_bodies), big_names=big_bodies,
        reach=len(reach), reach_names=reach,
        evasion_names=evasion, hard=len(hard), hard_names=hard, soft=len(soft),
        soft_names=soft, fixers=fixers, colors="".join(real), splash="".join(splash),
        ncolors=len(real) + len(splash), hybrid_only="".join(hybrid_only), gih=avg(gih_g), gih_pair=avg(gih_p),
        cre_curve=cre_curve, spell_curve=spell_curve, missing=missing,
        c5=sum(v for k, v in list(cre_curve.items()) + list(spell_curve.items()) if k >= 5),
        c6=sum(v for k, v in list(cre_curve.items()) + list(spell_curve.items()) if k >= 6),
    )


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    args = [a for a in sys.argv[1:] if a != "--brief"]
    BRIEF = "--brief" in sys.argv
    path = args[0]
    pair = args[1].upper() if len(args) > 1 else None
    db, rat = load_db(), load_ratings("msh")
    prat = load_pair("msh", pair) if pair else {}
    M = metrics(path, db, rat, prat)
    lands, nonlands, fixers = M["lands"], M["nonlands"], M["fixers"]
    cheap_bodies, evasion = M["cheap_names"], M["evasion_names"]
    hard, soft, missing = M["hard_names"], M["soft_names"], M["missing"]
    cre_curve, spell_curve = M["cre_curve"], M["spell_curve"]
    ncre, real, splash = M["creatures"], M["colors"], M["splash"]

    def avg_of(k):
        return M[k]
    if BRIEF:
        print(f"{M['name']:22} | {lands:2} | {ncre:2} | {M['cheap']:2} | "
              f"{M['evasion']:2} | {M['hard']:2} | {M['c5']:2} | "
              f"{real}{'+' + splash if splash else '':6} | {fixers:2} | {M['gih']}")
        return
    print(f"\n=== {os.path.basename(path)} ===")
    print(f"земель {lands} · нонлендов {nonlands} · всего {lands + nonlands}")
    print(f"существ {ncre} · спеллов {sum(spell_curve.values())}")
    print(f"\nкривая СУЩЕСТВ : " + "  ".join(f"{k}:{cre_curve[k]}" for k in sorted(cre_curve)))
    print(f"кривая СПЕЛЛОВ : " + "  ".join(f"{k}:{spell_curve[k]}" for k in sorted(spell_curve)))
    print(f"\n🔴 СУЩЕСТВ cmc≤2 : {len(cheap_bodies)}   (квота ⚑КРИВАЯ: ≥5)")
    for b in sorted(set(cheap_bodies)):
        print(f"     · {b}" + (f" ×{cheap_bodies.count(b)}" if cheap_bodies.count(b) > 1 else ""))
    print(f"\nПРОБИВАЮЩИХ стойку (flying/menace/unblockable/trample) : {len(evasion)}")
    for b in sorted(set(evasion)):
        print(f"     · {b}" + (f" ×{evasion.count(b)}" if evasion.count(b) > 1 else ""))
    print(f"reach (ДЕРЖИТ стойку, не пробивает) : {M['reach']}   "
          + (", ".join(sorted(set(M['reach_names']))) or "—"))
    print(f"\nбезусловное removal : {len(hard)}   " + (", ".join(sorted(set(hard))) or "—"))
    print(f"условная интеракция : {len(soft)}   " + (", ".join(sorted(set(soft))) or "—"))
    c5 = sum(v for k, v in list(cre_curve.items()) + list(spell_curve.items()) if k >= 5)
    c6 = sum(v for k, v in list(cre_curve.items()) + list(spell_curve.items()) if k >= 6)
    # Порог по cmc≥6 переоткалиброван 17.08.2026: «0» приехало из MSH и на HOB не держится —
    # 194 из 298 трофейных листов (65%) несут хотя бы одну такую карту, медиана 1, ≤2 у 87%.
    print(f"\nверх кривой : cmc≥5 — {c5} (порог ≤4) · cmc≥6 — {c6} (порог ≤2, медиана победителей 1)")
    print(f"средний GIH глоб : {M['gih']}")
    if pair:
        print(f"средний GIH {pair}   : {M['gih_pair']}")
    if missing:
        print(f"\n⚠ не найдены в set-файле: {', '.join(missing)}")


if __name__ == "__main__":
    main()
