#!/usr/bin/env python3
"""Частота КАРТ у нас против победителей — самый прямой способ увидеть лик отбора.

    python3 card_leaks.py [--set hob] [--min-ours 3] [--top 20]

ЗАЧЕМ. Два дня спорили про оси (связки, пробитие, removal) и почти ничего не выспорили:
по осям мы попадаем в диапазон победителей. А расхождение по КОНКРЕТНОЙ карте видно
мгновенно и лечится одной строкой. Найдено 17.08.2026: `Old Thrush` стоит в 83% наших
WU-сборок и в 5% трофейных WU-листов. Такое не спрячется ни в одной агрегированной оси.

ГЛАВНОЕ ПРО МЕТОД — СРАВНИВАТЬ ВНУТРИ ПАРЫ. Карта {W}{U} редка по всему сету просто потому,
что большинство колод не WU: сравнение с общесетовой частотой порождает «лики» из ничего.
Поэтому каждая наша колода сравнивается только с трофейными листами СВОЕЙ пары, и пары, где
листов меньше порога, выбрасываются, а не сравниваются грубее.

Частота считается ПО ПРИСУТСТВИЮ (в скольких колодах карта есть), а не по числу копий:
присутствие устойчиво к тому, что одну и ту же карту кто-то играет в двух копиях.

Значимость — точный тест Фишера (двусторонний). При наших n (5-15 колод на пару) без него
любая карта «2 из 3 против 1 из 19» выглядит открытием.
"""
import glob, json, math, os, re, sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

SCRATCH = ("/private/tmp/claude-501/-Users-wolfeatyou/"
           "f1b79ede-89ba-4f2b-9896-2a448c3cde54/scratchpad")


def norm(s):
    return re.sub(r"[^a-z0-9]", "", re.sub(r"\s*//.*$", "", (s or "").strip()).lower())


BASICS = {norm(x) for x in ("Plains", "Island", "Swamp", "Mountain", "Forest", "Wastes")}


def maindeck_names(text):
    """Немля́ные имена мейна. Строка Sideboard обрывает — сайдборд это остаток пула."""
    out = set()
    for line in text.splitlines():
        line = line.strip()
        if line == "Sideboard":
            break
        if not line or line == "Deck":
            continue
        m = re.match(r"^(\d+)\s+(.+?)(?:\s+\([A-Z0-9]+\)\s+\d+)?$", line)
        if m and norm(m.group(2)) not in BASICS:
            out.add(norm(m.group(2)))
    return out


def fisher_two_sided(a, b, c, d):
    """p для таблицы [[a,b],[c,d]]. a — наши с картой, b — наши без, c/d — то же у трофеек."""
    n = a + b + c + d
    def p_of(x):
        return (math.comb(a + b, x) * math.comb(c + d, a + c - x) / math.comb(n, a + c)
                if 0 <= a + c - x <= c + d else 0.0)
    obs = p_of(a)
    return min(1.0, sum(p_of(x) for x in range(0, a + b + 1) if p_of(x) <= obs + 1e-12))


def our_decks(code):
    """Наши колоды: A/B-прогоны + реальные листы рядом со скиллом."""
    out = []
    for fn in ("ab2.json", "ab3.json"):
        p = os.path.join(SCRATCH, fn)
        if not os.path.exists(p):
            continue
        for x in json.load(open(p, encoding="utf-8"))["drafts"]:
            out.append(dict(group=x["group"], src=f"{fn}:{x['seed']}", text=x["deck"],
                            pool=[norm(n) for n in x.get("pool", "").split("|") if n.strip()]))
    for p, tag in ((f"{code}_my_deck.txt", "реальный драфт"),
                   (f"{code}_sealed_deck.txt", "sealed")):
        f = os.path.join(HERE, p)
        if os.path.exists(f):
            pool = []
            for cand in glob.glob(os.path.join(HERE, "pools", f"{code}_*.txt")):
                pool += [norm(l.split(" ", 1)[-1]) for l in open(cand, encoding="utf-8")
                         if l.strip()]
            out.append(dict(group="real", src=tag, pool=pool,
                            text=open(f, encoding="utf-8").read()))
    return out


def main():
    a = sys.argv[1:]
    def opt(k, d):
        return a[a.index(k) + 1] if k in a else d
    code = opt("--set", "hob")
    min_ours = int(opt("--min-ours", "3"))
    top = int(opt("--top", "20"))
    min_ref = int(opt("--min-ref", "6"))

    os.environ["MTGA_SET"] = code
    os.environ.setdefault("MTGA_OFFLINE", "1")
    import build_audit as A
    import deck_profile as P
    db, rat = A.load_db(), A.load_ratings(code)

    # трофейные листы, сгруппированные по паре — той же функцией, что и наши
    ref = defaultdict(list)
    for f in sorted(glob.glob(os.path.join(HERE, "ref_decks", code, "*.txt"))):
        ref[A.deck_colors(f, db)].append(maindeck_names(open(f, encoding="utf-8").read()))

    import tempfile
    ours = defaultdict(list)
    for d in our_decks(code):
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False,
                                         encoding="utf-8") as fh:
            fh.write(d["text"] if "Sideboard" in d["text"] else d["text"] + "\nSideboard\n")
            p = fh.name
        try:
            pair = A.deck_colors(p, db)
        finally:
            os.unlink(p)
        ours[pair].append(dict(names=maindeck_names(d["text"]), **d))

    pairs = [k for k in ours if len(ref.get(k, [])) >= min_ref]
    skipped = [(k, len(ours[k]), len(ref.get(k, []))) for k in ours if k not in pairs]

    print("=" * 96)
    print(f"ЧАСТОТА КАРТ: наши колоды против трофейных, ВНУТРИ СВОЕЙ ПАРЫ · сет {code.upper()}")
    print("=" * 96)
    print(f"наших колод {sum(len(v) for v in ours.values())} · "
          f"трофейных {sum(len(v) for v in ref.values())}")
    print(f"пары в сравнении: " + ", ".join(f"{k}(наших {len(ours[k])}/троф {len(ref[k])})"
                                            for k in sorted(pairs)))
    if skipped:
        print(f"⚠ пропущены (трофейных листов < {min_ref}, сравнивать не с чем): "
              + ", ".join(f"{k} наших {a_}/троф {b_}" for k, a_, b_ in sorted(skipped)))

    rows = []
    for pair in pairs:
        on, rn = ours[pair], ref[pair]
        cards = {c for d in on for c in d["names"]} | {c for d in rn for c in d}
        for c in cards:
            oa = sum(1 for d in on if c in d["names"])
            ra = sum(1 for d in rn if c in d)
            if oa < min_ours and ra < min_ours:
                continue
            p = fisher_two_sided(oa, len(on) - oa, ra, len(rn) - ra)
            rows.append(dict(pair=pair, card=c, oa=oa, on=len(on), ra=ra, rn=len(rn),
                             d=oa / len(on) - ra / len(rn), p=p))

    # Печатное имя резолвим ТОЙ ЖЕ норм-функцией, что и частоты. load_db ключует по своей
    # нормализации полного имени, а у двусторонних карт оно включает обратную сторону —
    # ключи бы не сошлись и в отчёте печатались бы «bilboluckwearer» вместо имени.
    name_of = {}
    for c in json.load(open(os.path.join(HERE, f"{code}_set.json"), encoding="utf-8")):
        name_of.setdefault(norm(c["name"]), c["name"].split(" //")[0])

    def show(title, sel, note):
        print("\n" + "=" * 96)
        print(title)
        print("=" * 96)
        print(note)
        print(f"\n{'карта':<34} {'пара':<5} {'у нас':>10} {'у победителей':>15} {'разрыв':>8} {'p':>8}")
        print("-" * 96)
        for r in sel[:top]:
            nm = name_of.get(r["card"], r["card"])
            print(f"{nm[:33]:<34} {r['pair']:<5} {r['oa']}/{r['on']} ({100*r['oa']/r['on']:>3.0f}%)".ljust(62)
                  + f"{r['ra']}/{r['rn']} ({100*r['ra']/r['rn']:>3.0f}%)".rjust(14)
                  + f"{100*r['d']:>+8.0f}pp{r['p']:>9.3f}")
        if not sel:
            print("   (ничего выше порога)")

    over = sorted([r for r in rows if r["d"] > 0], key=lambda r: (r["p"], -r["d"]))
    under = sorted([r for r in rows if r["d"] < 0], key=lambda r: (r["p"], r["d"]))
    show("ПЕРЕИГРЫВАЕМ — ставим чаще, чем победители",
         over, "Кандидаты в лики отбора: карта кажется нам нужной, а выигрывающие её не берут.")
    # ДОСТУПНОСТЬ ОТДЕЛЬНО ОТ ВЫБОРА. Карты может не быть в мейне просто потому, что её не
    # открыли — это не лик отбора, а бустер. Пул каждого драфта записан, поэтому «недоигрываем»
    # делится на две разные вещи: карта БЫЛА в пуле и не поставлена (наш выбор) против
    # карты не было вовсе (нечего обсуждать).
    for r in under:
        on = ours[r["pair"]]
        had = [d for d in on if d.get("pool") and r["card"] in d["pool"]]
        r["had"] = len(had)
        r["had_played"] = sum(1 for d in had if r["card"] in d["names"])
        r["pooled"] = sum(1 for d in on if d.get("pool"))
    show("НЕДОИГРЫВАЕМ — победители ставят, а мы нет",
         under, "Обратная сторона: что регулярно есть в выигрышных листах и проходит мимо нас.")
    print("\n  РАЗДЕЛЕНИЕ «не открыли» и «открыли и не поставили» (по записанным пулам):")
    print(f"  {'карта':<34} {'был в пуле':>12} {'из них в мейн':>15}  вердикт")
    print("  " + "-" * 78)
    for r in under[:top]:
        if not r.get("pooled"):
            continue
        nm = name_of.get(r["card"], r["card"])
        if r["had"] == 0:
            v = "НЕ ОТКРЫВАЛИ — доступность, не выбор"
        elif r["had_played"] < r["had"]:
            v = f"ОТКРЫВАЛИ и не ставили {r['had'] - r['had_played']} раз — ЭТО ВЫБОР"
        else:
            v = "ставили всегда, когда была"
        print(f"  {nm[:33]:<34} {r['had']}/{r['pooled']:<11} {r['had_played']:>15}  {v}")

    print("\n" + "=" * 96)
    print("ЛИК ОБЩИЙ ИЛИ ВЕРСИОННЫЙ?")
    print("=" * 96)
    print("Если карту переигрывают ОБЕ версии скилла — это непонимание сета, лечится знанием.")
    print("Если только новая — её туда загнал баннер, лечится кодом.\n")
    for r in over[:10]:
        if r["p"] > 0.1:
            continue
        on = ours[r["pair"]]
        by = Counter(d["group"] for d in on if r["card"] in d["names"])
        tot = Counter(d["group"] for d in on)
        parts = []
        for g, ru in (("new", "новая"), ("old", "старая"), ("real", "реальные")):
            if tot.get(g):
                parts.append(f"{ru} {by.get(g, 0)}/{tot[g]}")
        print(f"  {name_of.get(r['card'], r['card'])[:32]:<33} " + " · ".join(parts))

    print("\nПорог: карта показывается, если встречается ≥%d раз хотя бы у одной стороны." % min_ours)
    print("p — точный тест Фишера, двусторонний. При наших n значимым считать p<0.05,")
    print("остальное — направление, а не факт.")


if __name__ == "__main__":
    main()
