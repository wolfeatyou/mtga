#!/usr/bin/env python3
"""
ПИЛОТИРОВАНИЕ против исхода: трофей-раны vs провал-раны по replay-агрегатам (§ 8.30).

    python3 pilot_vs_outcome.py msh

Вход — games/<set>_replay.json.gz (fetch_17l_replay.py). Единица анализа — ДРАФТ
(метрики усреднены по его партиям). Вопросы пререгистрированы ДО анализа (§ 8.30):
Q1 агрессия · Q2 ленд-дропы · Q3 слитая мана 3–7 · Q4 тайминг removal · Q5 блоки ·
Q6 риск (минимум жизней). Контроли обязательны и печатаются рядом с каждым d:
· d|GIH — частичный d после вычета качества колоды (методика § 8.8 ①);
· d(lost) — только ПРОИГРАННЫЕ партии обеих групп (ломает цикличность «выигрывающий
  атакует больше, потому что уже выигрывает»);
· скилл-срез § 8.11 (top wr≥0.62 vs bottom ≤0.46) — деление, независимое от удачи рана.
Прибор-чек: партий ≈ 377 514 (§ 8.6) и d по deck-GIH ≈ +0.67 — не сошлось → анализу
не верить, чинить агрегатор.
"""
import gzip
import json
import os
import statistics as st
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from clock_vs_outcome import cohen_d, residuals   # noqa: E402  (§ 8.5: боевые, не копии)


def draft_metrics(games):
    """Средние пилот-метрики одного драфта по списку его партий."""
    def agg(f, pred=lambda g: True):
        vals = [f(g) for g in games if pred(g)]
        vals = [v for v in vals if v is not None]
        return st.mean(vals) if vals else None
    m = dict(
        gih=agg(lambda g: g["gih"]),
        atk_share=agg(lambda g: g["atkt"] / g["atko"] if g["atko"] else None),
        attackers=agg(lambda g: g["natk"] / g["atkt"] if g["atkt"] else None),
        dmg_turn=agg(lambda g: g["dmg"] / g["myt"] if g["myt"] else None),
        lands5=agg(lambda g: g["l5"]),
        eff37=agg(lambda g: g["sp37"] / g["av37"] if g["av37"] else None),
        rem_t=agg(lambda g: g["remt"]),
        rem5=agg(lambda g: (1 if g["remt"] and g["remt"] <= 5 else 0)
                 if g["remt"] is not None or True else None),
        block_share=agg(lambda g: g["obl"] / g["oat"] if g["oat"] else None),
        life_min=agg(lambda g: g["lmin"]),
    )
    return m


LABELS = [("atk_share", "Q1 доля ходов с атакой (есть кем)"),
          ("attackers", "Q1 атакующих за атаку"),
          ("dmg_turn", "Q1 комбат-урон за свой ход"),
          ("lands5", "Q2 земель к своему 5-му ходу"),
          ("eff37", "Q3 потрачено/доступно, ходы 3–7"),
          ("rem_t", "Q4 первый removal, ход"),
          ("rem5", "Q4 removal был к T5, доля партий"),
          ("block_share", "Q5 доля чужих атак с блоком"),
          ("life_min", "Q6 минимум своих жизней")]


def dtable(T, F, tag):
    print(f"\n— {tag}: трофеев {len(T)} · провалов {len(F)}")
    gT = [m["gih"] for m in T if m["gih"] is not None]
    gF = [m["gih"] for m in F if m["gih"] is not None]
    print(f"{'метрика':<34}{'трофей':>8}{'провал':>8}{'d':>7}{'d|GIH':>7}")
    print(f"{'deck-GIH (прибор-чек)':<34}{st.mean(gT):>8.2f}{st.mean(gF):>8.2f}"
          f"{cohen_d(gT, gF):>+7.2f}")
    for key, lab in LABELS:
        a = [(m[key], m["gih"]) for m in T if m[key] is not None and m["gih"] is not None]
        b = [(m[key], m["gih"]) for m in F if m[key] is not None and m["gih"] is not None]
        if len(a) < 50 or len(b) < 50:
            continue
        d = cohen_d([x for x, _ in a], [x for x, _ in b])
        res = residuals([x for x, _ in a + b], [g for _, g in a + b])
        dg = cohen_d(res[:len(a)], res[len(a):])
        print(f"{lab:<34}{st.mean([x for x, _ in a]):>8.2f}"
              f"{st.mean([x for x, _ in b]):>8.2f}{d:>+7.2f}{dg:>+7.2f}")


def main():
    code = (sys.argv[1] if len(sys.argv) > 1 else "msh").lower()
    with gzip.open(os.path.join(HERE, "games", f"{code}_replay.json.gz"), "rt") as f:
        rows = json.load(f)
    print(f"партий {len(rows):,} · доля побед по партиям "
          f"{100 * sum(r['won'] for r in rows) / len(rows):.1f}% (артефакт — § 8.6)")

    by_draft = {}
    for r in rows:
        by_draft.setdefault(r["d"], []).append(r)
    trophy_g, fail_g = {}, {}
    for d, gs in by_draft.items():
        w = sum(g["won"] for g in gs)
        losses = len(gs) - w
        if w == 7:
            trophy_g[d] = gs
        elif w <= 1 and losses >= 3:
            fail_g[d] = gs
    print(f"драфтов: {len(by_draft):,} · трофеев {len(trophy_g):,} · провалов {len(fail_g):,}")

    T = [draft_metrics(gs) for gs in trophy_g.values()]
    F = [draft_metrics(gs) for gs in fail_g.values()]
    dtable(T, F, "ВСЕ партии рана")

    Tl = [draft_metrics([g for g in gs if not g["won"]]) for gs in trophy_g.values()]
    Tl = [m for m in Tl if m["gih"] is not None]
    Fl = [draft_metrics([g for g in gs if not g["won"]]) for gs in fail_g.values()]
    Fl = [m for m in Fl if m["gih"] is not None]
    dtable(Tl, Fl, "только ПРОИГРАННЫЕ партии (анти-цикличность)")

    def wr(g):
        try:
            return float(g[0]["wrb"])
        except (TypeError, ValueError):
            return None
    top = [draft_metrics(gs) for gs in by_draft.values() if (wr(gs) or 0) >= 0.62]
    bot = [draft_metrics(gs) for gs in by_draft.values()
           if wr(gs) is not None and wr(gs) <= 0.46]
    if len(top) > 200 and len(bot) > 200:
        dtable(top, bot, "скилл-срез § 8.11 (top wr≥0.62 vs bottom ≤0.46, независим от удачи рана)")


if __name__ == "__main__":
    main()
