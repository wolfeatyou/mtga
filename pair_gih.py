#!/usr/bin/env python3
"""Пересчёт списка карт по ПАР-ФИЛЬТРОВАННОМУ 17Lands GIH (как карта играет в ТВОЕЙ паре).

Зачем: глобальный GIH усреднён по всем колодам. В паре числа сдвигаются на +2..+4,
и сдвиг НЕРАВНОМЕРНЫЙ — порядок карт меняется, а IWD может поменять ЗНАК
(док. случай 10.08.2026: Shuri глоб +1.2 → WU −2.1; Kree Commandos глоб −1.2 → WU +0.3).
Строить колоду по глобальному GIH, когда пара уже известна, — ошибка.

Usage:
    python3 pair_gih.py <set> <PAIR> <decklist.txt>     # разобрать лист
    python3 pair_gih.py msh WU my_deck.txt
    python3 pair_gih.py msh WU --pool                   # весь пул из лога (Premier)
    python3 pair_gih.py msh WU --pool --quick           # весь пул из лога (Quick Draft)

Env: MTGA_OFFLINE=1 — не ходить в сеть (нужен готовый cache_17l_<set>_<PAIR>.json).
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))


def load_pair(setcode, pair):
    """[{name, gih, iwd, n}] для пары; кеш на диске, иначе тянем с 17Lands."""
    pair = "".join(x for x in "WUBRG" if x in pair.upper())
    cache = os.path.join(HERE, f"cache_17l_{setcode}_{pair}.json")
    data = None
    if os.path.exists(cache):
        try:
            data = json.load(open(cache))
        except Exception:
            data = None
    if data is None:
        if os.environ.get("MTGA_OFFLINE"):
            sys.exit(f"нет кэша {os.path.basename(cache)} и MTGA_OFFLINE=1")
        import urllib.request
        url = (f"https://www.17lands.com/card_ratings/data?expansion={setcode.upper()}"
               f"&format=PremierDraft&colors={pair}")
        req = urllib.request.Request(url, headers={"User-Agent": "mtg-draft-helper"})
        data = json.load(urllib.request.urlopen(req, timeout=15))
        json.dump(data, open(cache, "w"))
        print(f"(скачал и закэшировал {os.path.basename(cache)})")
    out = {}
    for x in data:
        n = x.get("name")
        if not n:
            continue
        out[n] = {"gih": x.get("ever_drawn_win_rate"),
                  "iwd": x.get("drawn_improvement_win_rate"),
                  "n": x.get("ever_drawn_game_count") or x.get("game_count") or 0}
    return out, pair


def load_global(setcode):
    rows = json.load(open(os.path.join(HERE, f"17l_{setcode}_premierdraft.json")))
    return {r["name"]: r for r in rows}


def load_set(setcode):
    d = json.load(open(os.path.join(HERE, f"{setcode}_set.json")))
    d = d["data"] if isinstance(d, dict) and "data" in d else d
    by_name, by_arena = {}, {}
    for c in d:
        by_name[c["name"]] = c
        if c.get("arena_id"):
            by_arena[int(c["arena_id"])] = c
    return by_name, by_arena


def names_from_decklist(path):
    """MTGA-формат; мейндек до Sideboard. -> [(name, qty)]"""
    out, stop = [], False
    for line in open(path, encoding="utf-8"):
        s = line.strip()
        if not s or s.lower() == "deck":
            continue
        if s.lower().startswith("sideboard"):
            break
        m = re.match(r"^(\d+)\s+(.*?)\s*\((\w+)\)\s*\d+\s*$", s) or re.match(r"^(\d+)\s+(.+)$", s)
        if m:
            out.append((m.group(2).strip(), int(m.group(1))))
    return out


def names_from_log(setcode, quick):
    log = os.environ.get("MTGA_LOG") or os.path.expanduser(
        "~/Library/Logs/Wizards Of The Coast/MTGA/Player.log")
    txt = open(log, encoding="utf-8", errors="ignore").read()
    _, by_arena = load_set(setcode)
    if quick:
        pays = re.findall(r'"Payload":"(\{.*?DraftPack.*?\})"', txt)
        if not pays:
            sys.exit("BotDraftDraftStatus в логе не найден")
        picked = json.loads(pays[-1].replace('\\"', '"')).get("PickedCards") or []
    else:
        picked = []
        for m in re.finditer(r'"PickedCards"\s*:\s*\[([^\]]*)\]', txt):
            picked = [int(x) for x in re.findall(r"\d+", m.group(1))]
    from collections import Counter
    cnt = Counter(int(g) for g in picked)
    return [(by_arena[g]["name"], q) for g, q in cnt.items() if g in by_arena]


def main():
    args = [a for a in sys.argv[1:]]
    if len(args) < 2:
        sys.exit(__doc__)
    setcode, pair = args[0].lower(), args[1]
    quick = "--quick" in args
    rest = [a for a in args[2:] if not a.startswith("--")]
    if "--pool" in args:
        cards = names_from_log(setcode, quick)
    elif rest:
        cards = names_from_decklist(rest[0])
    else:
        sys.exit(__doc__)

    prat, pair = load_pair(setcode, pair)
    grat = load_global(setcode)
    by_name, _ = load_set(setcode)

    # 17Lands ключует двусторонние карты по ЛИЦЕВОЙ стороне ("Smaug, the Great Calamity"),
    # а листы и <set>_set.json — полным именем ("Smaug, the Great Calamity // Spew Flame").
    # Без этого фолбэка такая карта получала GIH/пар-GIH = None и выпадала из ранжирования
    # пула — то есть § Шаг 0 сборки молча не видел Adventure-карты.
    # Третий прибор с этим же багом за один вечер (JOURNAL § 8.3 ①, там же список
    # непроверенных). 18.08.2026.
    def _rat(d, nm):
        return d.get(nm) or d.get(nm.split(" //")[0])

    rows = []
    for name, qty in cards:
        c = by_name.get(name)
        if c and "Land" in (c.get("type_line") or "") and "Creature" not in (c.get("type_line") or ""):
            if not _rat(grat, name):
                continue
        g = _rat(grat, name); p = _rat(prat, name)
        gg = round(g["ever_drawn_win_rate"] * 100, 1) if g and g.get("ever_drawn_win_rate") else None
        pg = round(p["gih"] * 100, 1) if p and p.get("gih") else None
        pi = round(p["iwd"] * 100, 1) if p and p.get("iwd") is not None else None
        gi = round(g["drawn_improvement_win_rate"] * 100, 1) if g and g.get("drawn_improvement_win_rate") is not None else None
        n = p["n"] if p else 0
        cmc = int(c["cmc"]) if c and c.get("cmc") is not None else None
        rows.append((name, qty, cmc, gg, pg, pi, gi, n))

    rows.sort(key=lambda r: -(r[4] or r[3] or 0))
    print(f"\n=== {setcode.upper()} · пара {pair} · пар-фильтрованный GIH ===")
    print(f"{'карта':<34}{'cmc':>4}{'глоб':>7}{'ПАРА':>7}{'Δ':>7}{'IWD':>7}{'ΔIWD':>7}{'n':>8}")
    lowsample, flip = [], []
    for name, qty, cmc, gg, pg, pi, gi, n in rows:
        d = f"{pg-gg:+.1f}" if (pg and gg) else "  -"
        di = f"{pi-gi:+.1f}" if (pi is not None and gi is not None) else "  -"
        mark = ""
        if n and n < 500:
            mark = "  ⚠мало данных"; lowsample.append(name)
        if pi is not None and gi is not None and (pi < 0) != (gi < 0):
            mark += "  🔄IWD сменил знак"; flip.append(name)
        print(f"{str(qty)+'x '+name[:30]:<34}{cmc if cmc is not None else '-':>4}"
              f"{gg if gg else '-':>7}{pg if pg else '-':>7}{d:>7}"
              f"{pi if pi is not None else '-':>7}{di:>7}{n:>8}{mark}")
    if flip:
        print(f"\n🔄 IWD сменил знак в паре — читать по ПАРНОМУ числу: {', '.join(flip)}")
    if lowsample:
        print(f"⚠ выборка <500 игр (парному числу верить осторожно): {', '.join(lowsample)}")
    good = [r for r in rows if r[4]]
    if good:
        avg = sum(r[4] * r[1] for r in good) / sum(r[1] for r in good)
        print(f"\nсредний ПАРНЫЙ GIH (взвешенный по копиям): {avg:.1f}")


if __name__ == "__main__":
    main()
