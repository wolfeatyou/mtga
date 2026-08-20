#!/usr/bin/env python3
"""
SWAP-ТЕСТ — дельта ОДНОГО свопа всеми приборами, одной командой.

    python3 swap_test.py <deck.txt> --cut "Card A" --add "Card B" [--set hob] [--sims 8000]

ЗАЧЕМ (§ 8.25, бэклог § 8.23). Тюнинг колоды живёт свопами, и каждый своп раньше стоил
шести команд руками (голдфиш ×2, аудит ×2, линт ×2) с ручным сравнением глазами.
Здесь печатаются только ДЕЛЬТЫ: GIH мейна · goldfish (скрю/T2/блокер/removal/муллы) ·
CLOCK (пустая/стойка) · маршруты пары · линт (что загорелось/погасло) · частоты обеих
карт у победителей пары. Числа считаются теми же боевыми функциями (simulate/clock_sim/
sig_of/lint) — не копиями (§ 8.5).
"""
import os
import random
import statistics as st
import sys
import tempfile
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_audit as A          # noqa: E402
import deck_lint as L            # noqa: E402
import draft_goldfish as G       # noqa: E402
import find_traps as FT          # noqa: E402
import pool_dossier as PD        # noqa: E402


def variant(path, cut, add):
    """Временный файл: мейн −1 cut +1 add (сайдборд не переносится)."""
    md, _sb = A.split_deck(path)
    cnt, order = Counter(), []
    for n, name in md:
        if name not in cnt:
            order.append(name)
        cnt[name] += n
    if cnt.get(cut, 0) < 1:
        raise SystemExit(f"«{cut}» нет в мейне {os.path.basename(path)}")
    cnt[cut] -= 1
    if add not in cnt:
        order.append(add)
    cnt[add] += 1
    f = tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8")
    f.write("Deck\n" + "\n".join(f"{cnt[nm]} {nm}" for nm in order if cnt[nm] > 0) + "\n")
    f.close()
    return f.name


def measure(path, setcode, sims):
    db = G.load_db()
    deck, missing = G.build_deck(G.parse_decklist(path), db)
    if missing:
        raise SystemExit(f"нет в сет-файле: {', '.join(missing)}")
    random.seed(12345)
    res = [G.simulate(deck) for _ in range(sims)]
    random.seed(12345)
    ko, kw = G.clock_sim(deck, min(sims, 4000))
    N = float(sims)
    rat = A.load_ratings(setcode)
    gihs = []
    dbA = A.load_db()
    md, _ = A.split_deck(path)
    cnt = {}
    for n, name in md:
        c = dbA.get(A.norm(name)) or dbA.get(A.norm(name.split(",")[0]))
        if c is None or "Land" in FT.face(c, "type_line"):
            continue
        cnt[FT.norm(name)] = cnt.get(FT.norm(name), 0) + n
        r = A.rating_of(rat, name)
        if r and r.get("ever_drawn_win_rate"):
            gihs += [r["ever_drawn_win_rate"] * 100] * n
    cards = A.load_ratings  # noqa: F841 (читаемость)
    import json
    setjson = json.load(open(os.path.join(HERE, f"{setcode}_set.json"), encoding="utf-8"))
    sig = FT.sig_of(cnt, setjson)
    return dict(
        gih=round(st.mean(gihs), 2) if gihs else None,
        screw=100 * sum(1 for r in res if r["lands_at"][4] <= 2) / N,
        t2=100 * sum(1 for r in res if r["first_block"] <= 2) / N,
        b3=100 * sum(1 for r in res if r["first_block"] <= 3) / N,
        rem3=100 * sum(1 for r in res if r["first_removal"] <= 3) / N,
        rem4=100 * sum(1 for r in res if r["first_removal"] <= 4) / N,
        mull=sum(r["mcount"] for r in res) / N,
        c_open=st.median(ko), c_wall=st.median(kw),
        sig=sig, lint=L.lint(path, setcode),
    )


def main():
    argv = sys.argv[1:]
    def val(flag, default=None):
        return argv[argv.index(flag) + 1] if flag in argv else default
    cut, add = val("--cut"), val("--add")
    setcode = val("--set")
    sims = int(val("--sims", 8000))
    path = next((a for a in argv if not a.startswith("--")
                 and a not in (cut, add, setcode, str(sims))), None)
    if not (path and cut and add):
        print(__doc__)
        sys.exit(1)
    setcode, _ = A.detect_set(path, path, setcode)
    vpath = variant(path, cut, add)
    try:
        base = measure(path, setcode, sims)
        new = measure(vpath, setcode, sims)
    finally:
        os.unlink(vpath)

    dbA = A.load_db()
    pair = A.deck_colors(path, dbA)
    traps = PD.load_json(setcode, "traps")
    print(f"=== SWAP: −{cut} → +{add} · {os.path.basename(path)} · пара {pair} ===")
    for name in (cut, add):
        _fl, share, cap = PD.card_flags(FT.norm(name), pair, traps)
        s = f"{int(round(share * 100))}%" if share is not None else "—"
        print(f"  {name}: у победителей {pair} {s}" + (f" · потолок ≤{cap}" if cap else ""))

    def d(a, b, suf="", inv=False):
        arrow = "" if a == b else (" ⬆" if (b > a) != inv else " ⬇")
        return f"{a:.1f}→{b:.1f}{suf}{arrow}"
    print(f"GIH мейна: {base['gih']}→{new['gih']} ({new['gih'] - base['gih']:+.2f})")
    print(f"goldfish:  скрю {d(base['screw'], new['screw'], '%', inv=True)} · "
          f"сущ-к-T2 {d(base['t2'], new['t2'], '%')} · блокер-T3 {d(base['b3'], new['b3'], '%')} · "
          f"removal-T3 {d(base['rem3'], new['rem3'], '%')} / T4 {d(base['rem4'], new['rem4'], '%')} · "
          f"муллы {d(base['mull'], new['mull'], inv=True)}")
    print(f"CLOCK:     пустая {base['c_open']}→{new['c_open']} · "
          f"стойка {base['c_wall']}→{new['c_wall']} (меньше = быстрее)")
    med = (traps.get("routes") or {}).get(pair)
    if med:
        marks = []
        for key, lab in PD.ROUTES:
            if key == "wide":
                a = min(base["sig"]["cre"] - med["cre"], base["sig"]["cheap"] - med["cheap"])
                b = min(new["sig"]["cre"] - med["cre"], new["sig"]["cheap"] - med["cheap"])
            else:
                a, b = base["sig"][key] - med[key], new["sig"][key] - med[key]
            if (a >= 0) != (b >= 0):
                marks.append(f"{lab}: {'✔→✗ УПАЛ' if a >= 0 else '✗→✔ открылся'}")
        print("маршруты:  " + ("; ".join(marks) if marks else "без изменений статуса"))
    gone = [w for w in base["lint"] if w not in new["lint"]]
    came = [w for w in new["lint"] if w not in base["lint"]]
    if not gone and not came:
        print("линт:      без изменений")
    for w in gone:
        print(f"линт:      −погасло: {w}")
    for w in came:
        print(f"линт:      +загорелось: {w}")


if __name__ == "__main__":
    main()
