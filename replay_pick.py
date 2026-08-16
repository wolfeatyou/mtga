#!/usr/bin/env python3
"""Показать пак прошедшего драфта так, как его увидел бы советчик в живом драфте.

    python3 replay_pick.py <set> <draft8> <pack> <pick> [--pool "Card A|Card B|..."]
    python3 replay_pick.py hob 31a78cee 1 1
    python3 replay_pick.py hob 31a78cee 1 2 --pool "Stone by Sunlight"
    python3 replay_pick.py hob 31a78cee --list        # какие паки записаны

Зачем: пак берётся из `.draft_hist.json` (его пишет draft_live на каждом пике), а ПУЛ
задаётся аргументом — то есть можно переиграть тот же драфт с ДРУГИМИ решениями и увидеть,
как меняются баннеры. Вывод идёт через тот же `render_block`, что и живой драфт, поэтому
переигровка показывает ровно то, что показал бы инструмент: порядок пака, ⚑СВЯЗКА, ⚑ОПОРА,
⚑ПАСУЕМ, кривую, ось, профиль.

Ограничение, которое надо помнить: пул подставляется «как если бы», а история пропусков
(⚑ПАСУЕМ) считается по фактически записанным пакам — они не зависят от наших решений,
это то, что реально проплыло мимо.
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


def main():
    argv = [a for a in sys.argv[1:]]
    if not argv:
        print(__doc__); return
    code = argv[0].lower()
    os.environ["MTGA_SET"] = code
    os.environ.setdefault("MTGA_OFFLINE", "1")
    sys.argv = ["draft_live.py", code]
    import draft_live as D

    hist = json.load(open(os.path.join(HERE, ".draft_hist.json"), encoding="utf-8"))
    draft = argv[1] if len(argv) > 1 else None
    key = next((k for k in hist if k.startswith(draft or "")), None)
    if not key:
        print(f"драфт {draft} не найден. Есть: {', '.join(k[:8] for k in hist)}"); return
    packs = hist[key]

    if "--list" in argv:
        ks = sorted(packs, key=lambda k: tuple(int(x) for x in k.split("-")))
        print(f"драфт {key[:8]} — паков записано: {len(ks)}")
        print("  " + " ".join(ks))
        return

    pnum, pick = int(argv[2]), int(argv[3])
    ids = packs.get(f"{pnum}-{pick}")
    if not ids:
        print(f"пака {pnum}-{pick} нет в истории"); return

    if "--legacy" in argv:
        # Режим «как было до 16.08.2026» — для честного A/B: пак сортируется по одному GIH,
        # знание из трофейных колод отключено. Без него сравнение бессмысленно: контрольный
        # драфтер видел бы те же ⚑СВЯЗКА/⚑ОПОРА и разница измеряла бы не инструмент, а модель.
        D._COMBOS = {}                                   # гасит ⚑СВЯЗКА и ⚑ОПОРА
        D.CALIB.pop("hob", None)                         # гасит пороги ⚑ПРОФИЛЬ/⚑СТОЙКА
        _orig = D.pack_order
        def gih_order(ids, by_id, ratings, cratings, main):
            def g(cid):
                r = ratings.get(cid)
                return r.get("ever_drawn_win_rate") if r else -1
            return [(None, sorted(ids, key=lambda c: -(g(c) or 0)))]
        D.pack_order = gih_order
        D.passed_color_banner = lambda *a, **k: []       # накопительной памяти тоже не было

    by_id = D.load_cards()
    ratings = D.load_ratings()
    name2id = {}
    for cid, c in by_id.items():
        name2id.setdefault(c["name"].split(" //")[0].lower(), cid)

    pool_names = []
    if "--pool" in argv:
        raw = argv[argv.index("--pool") + 1]
        pool_names = [x.strip() for x in raw.split("|") if x.strip()]
    picks, unknown = [], []
    for n in pool_names:
        cid = name2id.get(n.lower())
        (picks.append(cid) if cid else unknown.append(n))
    if unknown:
        print(f"⚠ не нашёл в наборе: {', '.join(unknown)} — проверь написание\n")

    print(D.render_block(pnum, pick, ids, picks, by_id, ratings, key,
                         header=f"ПАК {pnum}/{pick} — {len(ids)} карт · в пуле {len(picks)}"))


if __name__ == "__main__":
    main()
