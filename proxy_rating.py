#!/usr/bin/env python3
"""ОЦ — эвристическая оценка карты 0–10 по механике, когда 17Lands ещё пуст.

⚠️ ЭТО НЕ GIH И НЕ ЕГО ЗАМЕНА. Другая шкала (0–10), другое имя, другая точность.
Печатается только пока у сета НЕТ данных 17Lands, и гаснет сама, как только они появятся.
Смешивать ОЦ с GIH в одном рассуждении запрещено: GIH — измеренный винрейт, ОЦ — правила,
записанные человеком по текстам карт.

Зачем вообще: на старте сета пак приходит НЕОТСОРТИРОВАННЫМ, и глазами сканировать 14 карт
дольше, чем есть времени на пик. ОЦ даёт грубый порядок, чтобы не пропустить removal/бомбу.
Решает пик по-прежнему рассуждение (роль, ось, дыра, квадранты), а не это число.

🔴 ИЗМЕРЕННОЕ КАЧЕСТВО (11.08.2026) — СЛАБОЕ, читать до использования:
    ручные веса:  MSH ρ=+0.08 · SOS ρ=+0.26 · MKM ρ=+0.39
    регрессия, обученная на двух сетах и проверенная на ТРЕТЬЕМ (честный holdout):
                  MSH ρ=+0.26 · SOS ρ=+0.28 · MKM ρ=+0.37
Для сравнения: ось «пик-тир» (untapped) коррелирует с GIH на ρ=+0.79.
ВЫВОД: ОЦ годится максимум на то, чтобы не пропустить removal/бомбу при беглом скане пака.
Ранжировать ею пик НЕЛЬЗЯ — на MSH ручная версия не предсказывала вообще ничего.
Пока сет без данных, решают роль, ось (⚑ОСЬ), дыра и квадранты, а не это число.

    python3 proxy_rating.py --validate msh     # перепроверить самому

    python3 proxy_rating.py hob                # топ карт сета по ОЦ
    python3 proxy_rating.py hob --all          # весь сет
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def _txt(c):
    t = c.get("oracle_text", "") or ""
    for f in c.get("card_faces", []) or []:
        t += " " + (f.get("oracle_text", "") or "")
    return t


def _tl(c):
    t = c.get("type_line", "") or ""
    for f in c.get("card_faces", []) or []:
        t += " " + (f.get("type_line", "") or "")
    return t


def _num(v):
    try:
        return int(str(v).replace("*", "") or 0)
    except ValueError:
        return 0


def score(c):
    """0–10. Веса подобраны по общим принципам Limited, затем сверены на сетах с GIH."""
    tl, ot, cmc = _tl(c), _txt(c), c.get("cmc") or 0
    low = ot.lower()
    s = 5.0

    is_creature = "Creature" in tl
    if is_creature:
        p, t = _num(c.get("power")), _num(c.get("toughness"))
        # ванильный тест: тело «по кривой» ≈ P+T = 2*cmc+1
        s = 5.0 + (p + t - (2 * cmc + 1)) * 0.55
        for kw, w in (("flying", 1.3), ("deathtouch", 0.8), ("lifelink", 0.5),
                      ("double strike", 1.0), ("first strike", 0.5), ("menace", 0.45),
                      ("trample", 0.4), ("vigilance", 0.25), ("reach", 0.25),
                      ("haste", 0.2), ("ward", 0.4), ("hexproof", 0.4)):
            if re.search(r"\b" + kw + r"\b", low):
                s += w
        if re.search(r"when this creature enters|when .{0,24} enters", low):
            s += 0.7                                    # ETB-value = 2-в-1
        if re.search(r"\bwhenever\b", low):
            s += 0.5                                    # повторяемый триггер
        if "defender" in low or "can't attack" in low:
            s -= 1.0
        if "can't block" in low:
            s -= 0.5
        if "doesn't untap" in low:
            s -= 0.6
    else:
        # removal — главный неткриче-класс, различаем по безусловности
        hard = re.search(r"destroy target creature|exile target creature(?! card)", low)
        cond = re.search(r"destroy target creature|exile target creature", low)
        dmg = re.search(r"deals? (\d+) damage to target (creature|any target)", low)
        if hard and not re.search(r"with (power|mana value|toughness)|that is tapped|with flying", low):
            s = 8.4
        elif cond or dmg:
            s = 6.3 + (0.25 * min(_num(dmg.group(1)), 6) if dmg else 0)
        elif re.search(r"counter target", low):
            s = 5.6
        elif re.search(r"draw (a|two|three) card", low):
            s = 5.8
        elif re.search(r"create .{0,30}token", low):
            s = 5.6
        elif "Equipment" in tl:
            s = 5.2
        elif re.search(r"\+\d/\+\d until end of turn", low):
            s = 4.8                                     # боевой трюк
        elif "Land" in tl:
            s = 4.2 if "Basic" not in tl else 0.5
        if re.search(r"\binstant\b", tl.lower()):
            s += 0.3
        s -= max(0, cmc - 4) * 0.35                     # дорогие неткриче дешевеют

    # общие поправки
    if cmc <= 2 and is_creature:
        s += 0.25                                       # Juza: дешёвое разыгрывается чаще
    if re.search(r"each player|all creatures|all players", low) and "you control" not in low:
        s -= 0.4                                        # симметрия
    s += {"mythic": 0.9, "rare": 0.55, "uncommon": 0.15}.get(c.get("rarity"), 0.0)
    return max(0.0, min(10.0, round(s, 1)))


def load(setcode):
    return json.load(open(os.path.join(HERE, f"{setcode}_set.json"), encoding="utf-8"))


def validate(setcode):
    """Корреляция ОЦ с настоящим GIH. Без этого числа ОЦ доверять нельзя."""
    rf = os.path.join(HERE, f"17l_{setcode}_premierdraft.json")
    if not os.path.exists(rf):
        sys.exit(f"нет {rf} — не на чем проверять")
    gih = {}
    for c in json.load(open(rf, encoding="utf-8")):
        g = c.get("ever_drawn_win_rate")
        if g and (c.get("game_count") or 0) > 200:
            gih[c["name"].split(" //")[0].lower()] = g * 100
    pairs = []
    for c in load(setcode):
        n = c["name"].split(" //")[0].lower()
        if n in gih and "Basic" not in _tl(c):
            pairs.append((score(c), gih[n]))
    if len(pairs) < 20:
        sys.exit("мало пересечений")
    n = len(pairs)
    mx = sum(p[0] for p in pairs) / n
    my = sum(p[1] for p in pairs) / n
    cov = sum((a - mx) * (b - my) for a, b in pairs)
    vx = sum((a - mx) ** 2 for a, b in pairs) ** 0.5
    vy = sum((b - my) ** 2 for a, b in pairs) ** 0.5
    r = cov / (vx * vy) if vx and vy else 0
    # ранговая (Спирмен) — устойчивее к шкале
    rx = {v: i for i, v in enumerate(sorted(set(p[0] for p in pairs)))}
    ry = {v: i for i, v in enumerate(sorted(set(p[1] for p in pairs)))}
    rp = [(rx[a], ry[b]) for a, b in pairs]
    mrx = sum(p[0] for p in rp) / n
    mry = sum(p[1] for p in rp) / n
    rc = sum((a - mrx) * (b - mry) for a, b in rp)
    rvx = sum((a - mrx) ** 2 for a, b in rp) ** 0.5
    rvy = sum((b - mry) ** 2 for a, b in rp) ** 0.5
    rs = rc / (rvx * rvy) if rvx and rvy else 0
    # насколько ОЦ ловит верх формата
    top = sorted(pairs, key=lambda p: -p[1])[:max(10, n // 8)]
    hit = sum(1 for a, b in top if a >= sorted((p[0] for p in pairs), reverse=True)[len(top) - 1])
    print(f"{setcode.upper()}: карт {n} · Пирсон r={r:+.2f} · Спирмен ρ={rs:+.2f} · "
          f"верх формата пойман {hit}/{len(top)}")
    return rs


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if "--validate" in sys.argv:
        for s in (args or ["msh", "sos", "mkm"]):
            validate(s)
        return
    if not args:
        sys.exit(__doc__)
    code = args[0].lower()
    cards = [(score(c), c) for c in load(code) if "Basic" not in _tl(c)]
    cards.sort(key=lambda x: -x[0])
    lim = len(cards) if "--all" in sys.argv else 30
    print(f"ОЦ — ЭВРИСТИКА, НЕ GIH. Проверь качество: python3 proxy_rating.py --validate msh\n")
    for s, c in cards[:lim]:
        col = "".join(c.get("colors") or []) or "C"
        print(f"  ОЦ {s:4.1f}  {c['rarity'][0].upper()} {col:2} {c['name'][:34]:34} {c.get('mana_cost','')}")


if __name__ == "__main__":
    main()
