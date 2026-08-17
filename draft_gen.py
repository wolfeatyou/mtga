#!/usr/bin/env python3
"""Генератор драфта с ботами — чтобы тестировать советчик не на одном реальном драфте.

    python3 draft_gen.py hob --seed 7 --pack 1 --pick 1
    python3 draft_gen.py hob --seed 7 --pack 2 --pick 5 --pool "Card A|Card B|..."
    python3 draft_gen.py hob --seed 7 --summary          # чем кончился драфт по мнению ботов

Зачем. Реальный драфт в истории ровно один (31a78cee), и переигровка на нём даёт n=1 —
эффект неотличим от случайности. Хуже: в переигровке паки зафиксированы, поэтому пивот
БЕСПЛАТЕН, сосед не может уйти в цвет вслед за тобой. Здесь боты пикают по-настоящему,
цвета пересыхают, и сигнал «цвет открыт» означает то же, что в живой игре.

Детерминизм. Один и тот же --seed даёт одни и те же бустеры и одну и ту же политику ботов,
поэтому две группы (со знанием / контроль) играют в ИДЕНТИЧНЫХ условиях — сравнивать можно.
Состояние не хранится: при каждом вызове драфт проигрывается с нуля, наш игрок берёт карты
из --pool по порядку, боты — по своей политике. Значит их решения зависят от наших, как и
должно быть.

Чего это НЕ даёт: боты не люди. Их политика — GIH со смещением в свои цвета и небольшим
шумом; они не читают сигналы, не пивотят и не строят синергии. Абсолютные числа поэтому
смещены, и «бот-мета» не равна человеческой. Для СРАВНЕНИЯ двух групп в одинаковых
условиях этого достаточно, для вывода «такая колода выигрывает на Арене» — нет.
"""
import json, os, random, re, sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

SEATS = 8
PACKS = 3
BOOSTER = dict(rare=1, uncommon=3, common=10)   # 14 карт, как в реальных паках HOB


def build_pools(cards):
    by = {"rare": [], "uncommon": [], "common": []}
    for c in cards:
        r = c.get("rarity")
        if r == "mythic":
            r = "rare"
        if r in by and not ("Basic" in (c.get("type_line") or "")):
            by[r].append(c)
    return by


def make_booster(rng, by):
    out = []
    for r, n in BOOSTER.items():
        out += rng.sample(by[r], min(n, len(by[r])))
    return out


def card_colors(c):
    cols = c.get("colors")
    if cols is None and c.get("card_faces"):
        cols = c["card_faces"][0].get("colors")
    return set(cols or [])


def bot_pick(rng, pack, pool, ratings, name2id):
    """Политика бота: GIH + смещение в свои цвета + шум.

    Смещение обязательно — без него боты берут по чистому рейтингу, цвета не пересыхают,
    и сигнал «цвет открыт» перестаёт что-либо значить: именно ради этого генератор и нужен.
    """
    col = Counter()
    for c in pool:
        for x in card_colors(c):
            col[x] += 1
    mine = {c for c, _ in col.most_common(2)} if len(pool) >= 4 else set()
    best, bs = None, -1e9
    for c in pack:
        r = ratings.get(name2id.get(c["name"].split(" //")[0].lower()))
        g = (r or {}).get("ever_drawn_win_rate") or 0.50
        s = g * 100
        cc = card_colors(c)
        if mine:
            if not cc:
                s += 1.0                      # бесцветное всегда играбельно
            elif cc <= mine:
                s += 4.0                      # в своих цветах
            elif cc & mine:
                s -= 2.0                      # частично
            else:
                s -= 6.0                      # мимо
        s += rng.uniform(-1.2, 1.2)           # шум: боты не идеальны
        if s > bs:
            best, bs = c, s
    return best


def simulate(code, seed, my_pool_names, upto_pack, upto_pick):
    import draft_live as D
    cards = json.load(open(os.path.join(HERE, f"{code}_set.json"), encoding="utf-8"))
    ratings = D.load_ratings()
    by_id = D.load_cards()
    name2id = {}
    for cid, c in by_id.items():
        name2id.setdefault(c["name"].split(" //")[0].lower(), cid)

    rng = random.Random(seed)
    by = build_pools(cards)
    boosters = [[make_booster(rng, by) for _ in range(SEATS)] for _ in range(PACKS)]

    pools = [[] for _ in range(SEATS)]        # 0 — наше место
    taken_names = [n.strip().lower() for n in my_pool_names]
    misses = []                                # карты из --pool, которых не было в паке
    bot_rng = random.Random(seed * 977 + 13)

    for p in range(PACKS):
        packs = [list(b) for b in boosters[p]]
        for pick in range(1, 15):
            # чей пак у какого места: пас влево в 1 и 3 бустере, вправо во втором
            idx = [(s + (pick - 1) * (1 if p % 2 == 0 else -1)) % SEATS for s in range(SEATS)]
            mine_pack = packs[idx[0]]
            if not mine_pack:
                continue
            if (p + 1, pick) == (upto_pack, upto_pick):
                return mine_pack, pools[0], None, misses
            # наш пик
            want = taken_names[len(pools[0])] if len(pools[0]) < len(taken_names) else None
            chosen = None
            if want:
                for c in mine_pack:
                    if c["name"].split(" //")[0].lower() == want:
                        chosen = c
                        break
            if chosen is None:
                # Карта из --pool не найдена в паке: пул уехал. Раньше здесь молча пикал бот,
                # и весь дальнейший драфт шёл по чужим решениям — пул выглядел полным, а ось
                # показывала не тот архетип. Теперь промах фиксируется и печатается.
                if want:
                    misses.append((p + 1, pick, want))
                chosen = bot_pick(bot_rng, mine_pack, pools[0], ratings, name2id)
            mine_pack.remove(chosen)
            pools[0].append(chosen)
            # боты
            for s in range(1, SEATS):
                pk = packs[idx[s]]
                if not pk:
                    continue
                c = bot_pick(bot_rng, pk, pools[s], ratings, name2id)
                pk.remove(c)
                pools[s].append(c)
    return None, pools[0], pools, misses


def main():
    a = sys.argv[1:]
    if not a:
        print(__doc__); return
    code = a[0].lower()
    os.environ["MTGA_SET"] = code
    os.environ.setdefault("MTGA_OFFLINE", "1")
    sys.argv = ["draft_live.py", code]
    import draft_live as D

    def opt(k, d=None):
        return a[a.index(k) + 1] if k in a else d

    seed = int(opt("--seed", "1"))
    pool = [x for x in (opt("--pool", "") or "").split("|") if x.strip()]

    if "--summary" in a:
        _, mine, pools, misses = simulate(code, seed, pool, 99, 99)
        print(f"seed {seed} · наш пул {len(mine)} карт")
        for i, p in enumerate(pools or []):
            col = Counter()
            for c in p:
                for x in card_colors(c):
                    col[x] += 1
            print(f"  место {i}: " + " ".join(f"{k}{v}" for k, v in col.most_common(3)))
        return

    pk, mine, _, misses = simulate(code, seed, pool, int(opt("--pack", "1")), int(opt("--pick", "1")))
    if misses:
        # ФАТАЛЬНО, а не предупреждением (ужесточено 17.08.2026). Раньше здесь печаталось
        # предупреждение и пак выдавался дальше — и в A/B-прогоне ЕГО ПРОИГНОРИРОВАЛИ все
        # 16 агентов, хотя инструкция прямо велела остановиться. Хуже, что промах каскадный:
        # подменённый пик меняет выбор ботов, следующие паки расходятся, и уже сделанные
        # пики перестают сходиться. Одна опечатка портила 2–5 пиков из 42 и тихо.
        # Теперь пак не выдаётся вовсе: продолжить можно, только починив --pool.
        print("❌ ОСТАНОВКА: карты из --pool не оказалось в её паке. Пак НЕ выдан.")
        for pp, pk_, nm in misses[:6]:
            print(f"    P{pp}P{pk_}: «{nm}» — этой карты в том паке не было")
        print("\n    Причина почти всегда одна из двух:")
        print("      · порядок в --pool не совпадает с порядком, в каком ты брал карты;")
        print("      · карта названа по памяти, а не скопирована из вывода пака.")
        print("    Восстанови --pool до последнего пика, который прошёл без ошибки, "
              "и продолжай оттуда.")
        sys.exit(2)
    if pk is None:
        print("драфт окончен (42 пика сделано)"); return
    by_id = D.load_cards()
    ratings = D.load_ratings()
    n2i = {}
    for cid, c in by_id.items():
        n2i.setdefault(c["name"].split(" //")[0].lower(), cid)
    ids = [n2i[c["name"].split(" //")[0].lower()] for c in pk
           if c["name"].split(" //")[0].lower() in n2i]
    picks = [n2i[c["name"].split(" //")[0].lower()] for c in mine
             if c["name"].split(" //")[0].lower() in n2i]
    if "--legacy" in a:
        D._COMBOS = {}
        D.CALIB.pop(code, None)
        D.passed_color_banner = lambda *x, **k: []
        def gih_order(ids_, by, rat, cr, main):
            def g(i):
                r = rat.get(i)
                return r.get("ever_drawn_win_rate") if r else -1
            return [(None, sorted(ids_, key=lambda c: -(g(c) or 0)))]
        D.pack_order = gih_order
    print(D.render_block(int(opt("--pack", "1")), int(opt("--pick", "1")), ids, picks,
                         by_id, ratings, f"GEN{seed}",
                         header=f"ПАК {opt('--pack','1')}/{opt('--pick','1')} — "
                                f"{len(ids)} карт · в пуле {len(picks)} · seed {seed}"))


if __name__ == "__main__":
    main()
