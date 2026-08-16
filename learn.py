#!/usr/bin/env python3
"""Самообучение по референс-колодам: извлекает заметки о каждой ПАРЕ и о сете в целом.

    python3 learn.py hob            # пересобрать hob_learned.md из ref_decks/hob/
    python3 learn.py hob --print    # то же, но в stdout, файл не трогать

Что это и зачем (внесено 16.08.2026 по прямому указанию пользователя).
Раньше знания о том, КАК собирать колоду, писал я руками — и каждый раз сползал к одному и
тому же: ранжировать карты по GIH и сравнивать средние. Это давало колоды, которые «нигде не
плохи», то есть мягкую середину; разбор пяти трофейных листов HOB показал расхождение с
победителями по всем осям сразу.

**GIH здесь не используется вообще.** Он нужен только для сортировки пака в живом драфте —
это одна ось из многих, и превращать её в мерило колоды нельзя. Заметки строятся на том,
что РЕАЛЬНО играется: частота карты в колодах пары, число копий, роли, кривая, земли.

Файл `<set>_learned.md` перегенерируется целиком при каждом запуске — правки руками в нём
не живут. Хочешь добавить знание — добавь колоду в `ref_decks/<set>/` и перезапусти;
хочешь записать вывод из партии — это `<set>_insights.md`, он ведётся отдельно и вручную.
"""
import json, os, re, sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
BASIC = {"Plains", "Island", "Swamp", "Mountain", "Forest"}
PIP = re.compile(r"\{([WUBRG])(?:/([WUBRG]))?\}")

REM = re.compile(r"destroy target creature|exile target creature|"
                 r"deals \d+ damage to target creature|sacrifices a creature", re.I)
EVA = re.compile(r"\bflying\b|can't be blocked|\bmenace\b|\btrample\b", re.I)
DRAW = re.compile(r"draw a card|draw two|recruit", re.I)


def load_set(code):
    p = os.path.join(HERE, f"{code}_set.json")
    cards = {}
    for c in json.load(open(p, encoding="utf-8")):
        cards.setdefault(c["name"].split(" //")[0], c)
    return cards


def face(c, k):
    v = c.get(k)
    if v is None and c.get("card_faces"):
        v = c["card_faces"][0].get(k)
    return v or ""


def oracle(c):
    o = c.get("oracle_text") or ""
    if not o and c.get("card_faces"):
        o = " ".join(f.get("oracle_text", "") for f in c["card_faces"])
    return o


def parse(path, cards):
    """-> (spells{name:qty}, lands{name:qty}) — базовые земли и нонбейсики раздельно."""
    sp, ld = Counter(), Counter()
    for line in open(path, encoding="utf-8"):
        s = line.strip()
        if not s or s.lower() in ("deck", "sideboard"):
            continue
        m = re.match(r"(\d+)\s+(.+?)(?:\s+\([A-Z0-9]{3}\).*)?$", s)
        if not m:
            continue
        q, name = int(m.group(1)), m.group(2).split(" //")[0].strip()
        c = cards.get(name)
        tl = face(c, "type_line") if c else ""
        if name in BASIC or ("Land" in tl and "Creature" not in tl):
            ld[name] += q
        else:
            sp[name] += q
    return sp, ld


def colors_of(deck, cards):
    """Пара цветов колоды — по пипам заклинаний (гибрид считается за половину каждому)."""
    cnt = Counter()
    for name, q in deck.items():
        c = cards.get(name)
        if not c:
            continue
        for a, b in PIP.findall(face(c, "mana_cost")):
            if b:
                cnt[a] += 0.5 * q; cnt[b] += 0.5 * q
            else:
                cnt[a] += q
    top = [x for x, _ in cnt.most_common(2)]
    return "".join(x for x in "WUBRG" if x in top)


def roles(deck, cards):
    r = Counter()
    curve_cr, curve_sp = Counter(), Counter()
    for name, q in deck.items():
        c = cards.get(name)
        if not c:
            r["неопознано"] += q
            continue
        tl, o = face(c, "type_line"), oracle(c)
        cmc = int(c.get("cmc") or 0)
        if "Creature" in tl:
            r["существ"] += q
            curve_cr[cmc] += q
            if cmc <= 2:
                r["тел cmc≤2"] += q
        else:
            curve_sp[cmc] += q
        if cmc >= 5:
            r["карт cmc≥5"] += q
        if "Equipment" in tl:
            r["эквипа"] += q
        elif "Artifact" in tl:
            r["артефактов"] += q
        if REM.search(o):
            r["removal"] += q
        if EVA.search(o):
            r["ломателей стойки"] += q
        if DRAW.search(o):
            r["добора"] += q
    return r, curve_cr, curve_sp


def fmt_curve(c):
    return " · ".join(f"{k}:{c[k]}" for k in sorted(c)) or "—"


def main():
    code = (sys.argv[1] if len(sys.argv) > 1 else "hob").lower()
    cards = load_set(code)
    d = os.path.join(HERE, "ref_decks", code)
    files = sorted(f for f in os.listdir(d) if f.endswith(".txt")) if os.path.isdir(d) else []
    if not files:
        print(f"нет колод в ref_decks/{code}/ — учиться не на чем"); return

    decks = []
    for f in files:
        sp, ld = parse(os.path.join(d, f), cards)
        pair = colors_of(sp, cards)
        r, ccr, csp = roles(sp, cards)
        decks.append(dict(file=f, pair=pair, spells=sp, lands=ld, roles=r, ccr=ccr, csp=csp,
                          nland=sum(ld.values()), n=sum(sp.values())))

    bypair = defaultdict(list)
    for x in decks:
        bypair[x["pair"]].append(x)

    L = []
    L.append(f"# {code.upper()} — извлечённые заметки (автогенерация)\n")
    L.append(f"**Сгенерировано `learn.py` из {len(decks)} колод в `ref_decks/{code}/`. "
             f"Файл перезаписывается целиком — не править руками.**\n")
    L.append("> Заметки строятся на том, что РЕАЛЬНО играется: частота карты, число копий, роли,\n"
             "> кривая, земли. **GIH здесь не используется** — он нужен только для сортировки пака\n"
             "> в живом драфте и мерилом колоды не является.\n"
             "> Выводы из партий — отдельно и вручную, в `<set>_insights.md`.\n")

    # ── общее по сету ───────────────────────────────────────────────
    L.append("\n## Общее по сету\n")
    keys = ["существ", "тел cmc≤2", "removal", "ломателей стойки", "эквипа",
            "артефактов", "добора", "карт cmc≥5"]
    L.append("| ось | мин | медиана | макс |")
    L.append("|---|---|---|---|")
    for k in keys:
        v = sorted(x["roles"].get(k, 0) for x in decks)
        L.append(f"| {k} | {v[0]} | {v[len(v)//2]} | {v[-1]} |")
    lands = sorted(x["nland"] for x in decks)
    L.append(f"| земель | {lands[0]} | {lands[len(lands)//2]} | {lands[-1]} |")

    maxcopy = Counter()
    for x in decks:
        for nm, q in x["spells"].items():
            maxcopy[nm] = max(maxcopy[nm], q)
    over2 = [f"{nm} ×{q}" for nm, q in maxcopy.items() if q > 2]
    L.append(f"\n**Максимум копий одной карты:** {max(maxcopy.values())}"
             + (f" — {', '.join(sorted(over2))}" if over2 else ""))

    # карты, встречающиеся в РАЗНЫХ парах = универсальные
    inpairs = defaultdict(set)
    for x in decks:
        for nm in x["spells"]:
            inpairs[nm].add(x["pair"])
    univ = sorted((len(p), nm) for nm, p in inpairs.items() if len(p) >= 2)
    if univ:
        L.append("\n**Играются в разных парах** (универсальные, брать можно до коммита в цвет):")
        L.append("  " + " · ".join(f"{nm} ({n} пары)" for n, nm in sorted(univ, reverse=True)[:12]))

    # ── по парам ────────────────────────────────────────────────────
    L.append("\n---\n\n## По парам\n")
    for pair in sorted(bypair, key=lambda p: -len(bypair[p])):
        grp = bypair[pair]
        L.append(f"\n### {pair} — {len(grp)} колод"
                 + ("  ⚠️ одна колода: это наблюдение, а не статистика" if len(grp) == 1 else ""))
        for x in grp:
            L.append(f"- `{x['file']}` — {x['n']} нонлендов + {x['nland']} земель · "
                     f"кривая существ {fmt_curve(x['ccr'])} · спеллов {fmt_curve(x['csp'])}")
        agg = Counter()
        for x in grp:
            agg.update(x["roles"])
        L.append("\n  **Роли** (сумма по колодам пары): "
                 + " · ".join(f"{k} {agg.get(k,0)}" for k in keys if agg.get(k)))
        # ядро пары: что играется в каждой колоде этой пары
        common = set(grp[0]["spells"])
        for x in grp[1:]:
            common &= set(x["spells"])
        if common:
            core = sorted(common, key=lambda nm: -max(x["spells"].get(nm, 0) for x in grp))
            L.append(f"\n  **Ядро пары** (есть во всех {len(grp)} колодах): "
                     + " · ".join(f"{nm}"
                                  + (f" ×{max(x['spells'].get(nm,0) for x in grp)}"
                                     if max(x["spells"].get(nm, 0) for x in grp) > 1 else "")
                                  for nm in core[:14]))
        rest = Counter()
        for x in grp:
            for nm, q in x["spells"].items():
                if nm not in common:
                    rest[nm] += q
        if rest:
            L.append("\n  **Остальное:** " + " · ".join(f"{nm}" + (f" ×{q}" if q > 1 else "")
                                                        for nm, q in rest.most_common(18)))

    L.append("\n---\n\n## Как этим пользоваться\n")
    L.append("- **Ядро пары** — то, что стоит тянуть, если пара открыта. Это не рейтинг, "
             "а факт: карта оказалась в каждой выигравшей колоде своей пары.")
    L.append("- **Диапазоны ролей** — проверка своей сборки: чинить надо то, что ниже ВСЕЙ "
             "популяции, а не то, что ниже медианы.")
    L.append("- **Одна колода на пару = наблюдение, не норма.** Пополнять `ref_decks/` при каждой "
             "встреченной трофейной колоде и перезапускать `learn.py`.")
    out = "\n".join(L) + "\n"

    if "--print" in sys.argv:
        print(out); return
    path = os.path.join(HERE, f"{code}_learned.md")
    open(path, "w", encoding="utf-8").write(out)
    print(f"→ {path}  ({len(decks)} колод, {len(bypair)} пар)")


if __name__ == "__main__":
    main()
