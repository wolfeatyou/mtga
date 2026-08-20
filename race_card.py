#!/usr/bin/env python3
"""
RACE-КАРТОЧКА К МАТЧУ — «кто beatdown?» до первой земли (§ 8.25, бэклог § 8.23).

    python3 race_card.py <deck.txt> [--set hob] [--sims 4000]

Наши часы (clock_sim § 8.23) против медианных часов ПОБЕДИТЕЛЕЙ каждой пары меты
(<set>_clocks.json, пересчёт: draft_goldfish.py --calibrate <set>). Отвечает на
задокументированный пилотский вопрос «who's the beatdown?» (§ КОММИТ В ПОЛОСУ,
mtg-commit-a-lane) числом, а не ощущением.

Чтение вердикта: ГОНЩИК — мы быстрее их типичного листа: не разменивайся без нужды,
removal только в блокеров и их клок; ЗАЩИТНИК — они быстрее: держи блоки, стабилизируйся,
твоё окно — их медианный ход летального. Ограничение § 8.23 в силе: эквип/бёрн/amass
в clock не бьют — против таких пар их реальные часы БЫСТРЕЕ показанных.
"""
import json
import os
import random
import statistics as st
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_audit as A          # noqa: E402
import draft_goldfish as G       # noqa: E402


def main():
    argv = sys.argv[1:]
    def val(flag, default=None):
        return argv[argv.index(flag) + 1] if flag in argv else default
    setcode = val("--set")
    sims = int(val("--sims", 4000))
    path = next((a for a in argv if not a.startswith("--") and a not in (setcode, str(sims))), None)
    if not path or not os.path.exists(path):
        print(__doc__)
        sys.exit(1)
    setcode, _ = A.detect_set(path, path, setcode)
    cp = os.path.join(HERE, f"{setcode}_clocks.json")
    if not os.path.exists(cp):
        raise SystemExit(f"нет {setcode}_clocks.json — сначала: "
                         f"python3 draft_goldfish.py --calibrate {setcode}")
    clocks = json.load(open(cp, encoding="utf-8"))

    db = G.load_db()
    deck, missing = G.build_deck(G.parse_decklist(path), db)
    if missing:
        print("⚠ нет в сет-файле (пропущены):", ", ".join(missing))
    random.seed(12345)
    ko, kw = G.clock_sim(deck, sims)
    our_o, our_w = st.median(ko), st.median(kw)
    pair = A.deck_colors(path, A.load_db())

    print(f"=== RACE-КАРТОЧКА: {os.path.basename(path)} · пара {pair} ===")
    ref = clocks.get(pair)
    print(f"наши часы: пустая доска {our_o} · через стойку {our_w}"
          + (f"   (медиана победителей {pair}: {ref['open']}/{ref['wall']})" if ref else ""))
    print(f"\n{'пара':<5}{'n':>4} {'их часы':>9}   вердикт")
    for p in sorted(clocks, key=lambda x: -clocks[x]["n"]):
        r = clocks[p]
        diff = our_o - r["open"]
        if diff <= -0.5:
            verdict = f"МЫ ГОНЩИК (быстрее на {-diff:.1f}) — не трать removal на нестрашное"
        elif diff >= 0.5:
            verdict = f"МЫ ЗАЩИТНИК (медленнее на {diff:.1f}) — блоки, окно к их ходу {r['open']:.0f}"
        else:
            verdict = "ровня — решают темп-размены и «кто первым моргнул»"
        print(f"{p:<5}{r['n']:>4} {r['open']:>5.1f}/{r['wall']:<5.1f} {verdict}")
    print("\n⚠ эквип/бёрн/amass в clock не бьют: против BR/WR-эквип их реальные часы "
          "быстрее показанных — вердикт «мы гонщик» там читать осторожнее.")


if __name__ == "__main__":
    main()
