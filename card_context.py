#!/usr/bin/env python3
"""
КОНТЕКСТ КАРТЫ — лечение слепоты частоты к связкам (§ 8.29).

    python3 card_context.py "Old Thrush" [--set hob] [--pair UB]

Безусловная частота («0% у победителей UB») не видит, С ЧЕМ карта работает: мана-пакет
из четырёх разных карт частотой не ловится (док. случай — трофейный UB-лист блоггера,
§ 8.28). Полное лечение невозможно — условные частоты на подвыборках имеют крошечные n
(из 140 ТРОЕК связок значимость не прошла ни одна, hob_combos._note) — поэтому здесь
не скоринг, а ПОКАЗ УЛИК с n на виду:
  A. безусловная частота по парам (как в досье);
  B. каждый трофейный лист, где карта стоит: пара · цвета · сплеш · фикс — читаешь
     контексты глазами;
  C. условные частоты по ФИЧАМ листа (сплеш есть/нет · фикс ≥3) — фичи агрегируют
     через пары, n здоровее, чем у пар карт;
  D. со-карты: с чем она реально стоит в этих листах чаще случайного (lift, co≥3 —
     наблюдение, не правило).
Все числа печатаются с n; ничего из этого не является осью оценки (§ 8.7: парные
признаки предсказания не добавляют — это ДИАГНОСТИКА приора, не предиктор).
"""
import glob
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_audit as A          # noqa: E402
import deck_profile as DP        # noqa: E402
import find_traps as FT          # noqa: E402


def main():
    argv = sys.argv[1:]
    def val(flag, default=None):
        return argv[argv.index(flag) + 1] if flag in argv else default
    setcode = (val("--set") or "hob").lower()
    only_pair = val("--pair")
    name = next((a for a in argv if not a.startswith("--")
                 and a not in (setcode, only_pair, val("--set"), val("--pair"))), None)
    if not name:
        print(__doc__)
        sys.exit(1)
    key = FT.norm(name)
    db, rat = DP.load_db(), DP.load_ratings(setcode)
    if not (db.get(A.norm(name)) or db.get(A.norm(name.split(",")[0]))):
        raise SystemExit(f"карта «{name}» не найдена в {setcode}_set.json")

    files = sorted(glob.glob(os.path.join(HERE, "ref_decks", setcode, "*.txt")))
    rows = []
    for f in files:
        cnt = FT.maindeck_counts(open(f, encoding="utf-8").read())
        m = DP.metrics(f, db, rat)
        pair = A.deck_colors(f, db)
        rows.append(dict(f=os.path.basename(f), pair=pair, cnt=cnt,
                         splash=bool(m["splash"]), fixers=m["fixers"],
                         colors=len(m["colors"]) + len(m["splash"])))
    if only_pair:
        pop = [r for r in rows if r["pair"] == only_pair.upper()]
    else:
        pop = rows
    have = [r for r in pop if key in r["cnt"]]

    print(f"=== КОНТЕКСТ: {name} · сет {setcode.upper()} · "
          f"популяция {len(pop)} листов" + (f" (пара {only_pair.upper()})" if only_pair else "") + " ===")

    print(f"\nA. безусловно: стоит в {len(have)}/{len(pop)} "
          f"({100 * len(have) / max(1, len(pop)):.0f}%)")

    if have:
        print("\nB. листы-улики (читать контекст глазами):")
        for r in have[:12]:
            print(f"   · {r['f']:<38} {r['pair']:<4} цветов {r['colors']} · "
                  f"{'сплеш' if r['splash'] else 'без сплеша'} · фикс {r['fixers']}")
        if len(have) > 12:
            print(f"   … и ещё {len(have) - 12}")

    print("\nC. условные частоты по фичам листа (n на виду):")
    for label, pred in (("сплеш есть", lambda r: r["splash"]),
                        ("сплеша нет", lambda r: not r["splash"]),
                        ("фикс ≥3", lambda r: r["fixers"] >= 3),
                        ("фикс ≤1", lambda r: r["fixers"] <= 1)):
        sub = [r for r in pop if pred(r)]
        k = sum(1 for r in sub if key in r["cnt"])
        base = 100 * len(have) / max(1, len(pop))
        rate = 100 * k / max(1, len(sub))
        mark = " ←" if sub and abs(rate - base) >= max(5, base) and k >= 2 else ""
        print(f"   {label:<12} {k:>3}/{len(sub):<4} ({rate:4.1f}%){mark}")

    if have:
        others = Counter()
        for r in have:
            for k2 in r["cnt"]:
                if k2 != key:
                    others[k2] += 1
        base_freq = Counter()
        for r in pop:
            for k2 in r["cnt"]:
                base_freq[k2] += 1
        scored = []
        for k2, co in others.items():
            if co < 3:
                continue
            exp = base_freq[k2] * len(have) / max(1, len(pop))
            if exp > 0:
                scored.append((co / exp, co, k2))
        scored.sort(reverse=True)
        if scored:
            print(f"\nD. со-карты (в листах с «{name}» чаще случайного; co≥3 — наблюдение):")
            for lift, co, k2 in scored[:8]:
                print(f"   ×{lift:.1f}  {k2:<28} вместе в {co}/{len(have)}")
    print("\n⚠ Условные n малы по построению — это улики для глаз, не пороги (§ 8.29).")


if __name__ == "__main__":
    main()
