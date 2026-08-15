#!/usr/bin/env python3
"""Скачать рейтинги 17Lands в 17l_<set>_premierdraft.json + отчёт о ГОТОВНОСТИ данных.

Зачем отдельный скрипт: у свежего сета 17Lands отдаёт пустой массив или числа на
крошечной выборке, и по ним нельзя драфтить — но понять это по самому файлу нельзя,
советчик просто начнёт печатать шум как факты. Здесь готовность измеряется явно:
сколько карт перешагнуло порог game_count>200, который `draft_live.load_ratings()`
использует как фильтр. Пока таких карт мало — рейтингам верить нельзя.

Использование:
    python3 fetch_17l.py hob              # скачать и записать (если данные есть)
    python3 fetch_17l.py hob --check      # только отчёт, ничего не писать
    python3 fetch_17l.py hob --force      # записать даже сырую выборку
    python3 fetch_17l.py hob --format PickTwoDraft
"""
import json
import os
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
UA = {"User-Agent": "mtg-draft-helper/1.0", "Accept": "application/json"}
MIN_GAMES = 200      # тот же порог, что в draft_live.load_ratings()
READY_CARDS = 100    # ниже этого числа карт сет считаем непрогретым


def get(url):
    return json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA)))


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        sys.exit("Укажи код сета: python3 fetch_17l.py hob")
    code = args[0].lower()
    fmt = "PremierDraft"
    if "--format" in sys.argv:
        fmt = sys.argv[sys.argv.index("--format") + 1]
    check_only = "--check" in sys.argv
    force = "--force" in sys.argv

    data = get(f"https://www.17lands.com/card_ratings/data?"
               f"expansion={code.upper()}&format={fmt}")

    rated = [c for c in data if c.get("ever_drawn_win_rate")]
    solid = [c for c in rated if (c.get("game_count") or 0) > MIN_GAMES]
    print(f"17Lands {code.upper()}/{fmt}: карт в ответе {len(data)}, "
          f"с GIH {len(rated)}, с выборкой >{MIN_GAMES} игр — {len(solid)}")

    if len(solid) < READY_CARDS:
        try:
            f = get("https://www.17lands.com/data/filters")
            start = f.get("start_dates", {}).get(code.upper())
            if start:
                print(f"Формат стартовал: {start}")
        except Exception:
            pass
        print(f"\n⚠ ДАННЫЕ ЕЩЁ НЕ ПРОГРЕЛИСЬ — драфтить по ним нельзя.")
        print("  Обычно рейтинги стабилизируются через 2-3 дня после релиза.")
        print(f"  Проверяй: python3 fetch_17l.py {code} --check")
        if not force:
            print("  Файл НЕ перезаписан (--force чтобы всё равно записать).")
            return

    if check_only:
        print("--check: файл не изменён")
        return

    path = os.path.join(HERE, f"17l_{code}_premierdraft.json")
    json.dump(data, open(path, "w"), ensure_ascii=False)
    print(f"Записано: {path}")
    if solid:
        top = sorted(solid, key=lambda c: -c["ever_drawn_win_rate"])[:5]
        print("Топ-5 по GIH:")
        for c in top:
            print(f"   {c['ever_drawn_win_rate']*100:5.1f}  {c['name']}")


if __name__ == "__main__":
    main()
