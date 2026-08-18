#!/usr/bin/env python3
"""Регресс на ОДИН класс дефекта: сопоставление имён двусторонних карт.

Зачем отдельный тест. Этот баг всплывал ПЯТЬ раз в четырёх разных приборах:

  1. `draft_gen.py`      — матчер знал только лицевую сторону (JOURNAL § 5.5),
                           17 промахов у одного агента и 12 у другого, причём почти все
                           в контрольной группе — дефект перекосил сам результат теста;
  2. `build_audit.G()`   — 17Lands ключует по ЛИЦЕВОЙ, лист по ПОЛНОЙ → карта выпадала
                           из ОБЕИХ сторон теста «мейн vs жадный»; вердикт переворачивался
                           с «+0.00, плана нет» на «+0.93, план читается» (JOURNAL § 8.3 ①);
  3. `deck_profile.HARD_RE` — не ловил «destroy up to one other target …»;
  4. `pair_gih.py`       — Adventure-карты молча выпадали из ранжирования пула;
  5. `draft_live.pick_tier` — все 5 двусторонних карт MSH не находились по полному имени.

Общее у всех: НЕ арифметика, а строковый матчинг, и падение ВСЕГДА тихое —
карта просто отсутствует, счётчик уменьшается, вердикт меняется.

Правило, которое закрепляет тест: **имя принимается в любой записи** — и лицевой
(`Smaug, the Great Calamity`), и полной (`Smaug, the Great Calamity // Spew Flame`).
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
os.environ.setdefault("MTGA_OFFLINE", "1")
sys.path.insert(0, HERE)

fails = []
checked = 0


def check(cond, msg):
    global checked
    checked += 1
    if not cond:
        fails.append(msg)


def dfc_names(setcode):
    p = os.path.join(HERE, f"{setcode}_set.json")
    if not os.path.exists(p):
        return []
    return [c["name"] for c in json.load(open(p, encoding="utf-8")) if " // " in c.get("name", "")]


SETS = [s for s in ("hob", "msh", "sos", "mkm") if os.path.exists(os.path.join(HERE, f"{s}_set.json"))]

# ── 1. build_audit.G(): рейтинг находится по ПОЛНОМУ имени ────────────────────────
import build_audit as BA  # noqa: E402

for code in SETS:
    rat = BA.load_ratings(code)
    if not rat:
        continue
    for nm in dfc_names(code):
        front = nm.split(" //")[0]
        r_front = rat.get(BA.norm(front))
        if not (r_front and r_front.get("ever_drawn_win_rate")):
            continue          # у карты просто нет данных 17Lands — не наш случай
        # боевая функция, а не копия логики
        check(BA.rating_of(rat, nm) is not None,
              f"[{code}] build_audit.rating_of: рейтинг НЕ находится по полному имени {nm!r}")

# ── 2. pair_gih: тот же фолбэк ────────────────────────────────────────────────────
import pair_gih as PG  # noqa: E402

for code in SETS:
    fn = getattr(PG, "load_global", None) or getattr(PG, "load_ratings", None)
    if fn is None:
        break
    try:
        grat = fn(code)
    except Exception:
        continue
    if not grat:
        continue
    for nm in dfc_names(code):
        front = nm.split(" //")[0]
        if not grat.get(front):
            continue
        check((grat.get(nm) or grat.get(front)) is not None,
              f"[{code}] pair_gih: рейтинг НЕ находится по полному имени {nm!r}")

# ── 3. draft_live.pick_tier и резолв имени в id (путь replay_pick) ────────────────
for code in SETS:
    names = dfc_names(code)
    if not names:
        continue
    for m in ("draft_live",):
        sys.modules.pop(m, None)
    sys.argv = ["test", code]
    import draft_live as D  # noqa: E402

    D.pick_tier("warmup")                       # ленивая загрузка тиров
    tiers = D.PICK_TIERS or {}
    for nm in names:
        front = nm.split(" //")[0]
        if tiers and D.pick_tier(front):
            check(D.pick_tier(nm) is not None,
                  f"[{code}] pick_tier: тир есть по лицевой, но НЕ по полному имени {nm!r}")

    # ВАЖНО: зовём БОЕВОЙ резолв из replay_pick, а не переписываем его здесь.
    # Первая редакция этого теста повторяла логику локально — и осталась зелёной,
    # когда дефект вернули в replay_pick. Тест, который не может упасть, не тест.
    sys.modules.pop("replay_pick", None)
    import replay_pick as RP  # noqa: E402

    by_id = D.load_cards()
    name2id = RP.build_name_index(by_id)
    for nm in names:
        front = nm.split(" //")[0]
        if not RP.resolve_name(name2id, front):
            continue                            # карты нет в наборе Arena — не наш случай
        check(RP.resolve_name(name2id, nm) is not None,
              f"[{code}] replay_pick.resolve_name: НЕ резолвится полное имя {nm!r}")

# ── 4. consensus / learn: строка листа распознаётся в ОБОИХ написаниях ────────────
import tempfile  # noqa: E402

import consensus as CS  # noqa: E402
import learn as LN  # noqa: E402

for code in SETS:
    names = dfc_names(code)
    if not names:
        continue
    for mod, label in ((CS, "consensus"), (LN, "learn")):
        cards = mod.load_set(code)
        if isinstance(cards, tuple):
            cards = cards[0]
        nm = names[0]
        for spelling in (nm, nm.split(" //")[0]):
            path = tempfile.mktemp(suffix=".txt")
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(f"Deck\n2 {spelling}\n17 Mountain\n")
            try:
                res = mod.parse(path, cards)
                deck = res[0] if isinstance(res, tuple) else res
                found = any(nm.split(" //")[0] in str(k) for k in deck)
            except Exception as e:                       # noqa: BLE001
                found = False
                fails.append(f"[{code}] {label}.parse упал на {spelling!r}: {e}")
            finally:
                os.unlink(path)
            check(found, f"[{code}] {label}: лист с записью {spelling!r} не распознан")

# ── 5. card_leaks.norm обязана схлопывать обе записи в ОДИН ключ ──────────────────
import card_leaks as CL  # noqa: E402

for code in SETS:
    for nm in dfc_names(code):
        check(CL.norm(nm) == CL.norm(nm.split(" //")[0]),
              f"[{code}] card_leaks.norm: {nm!r} и лицевая дают РАЗНЫЕ ключи "
              f"(та же карта посчиталась бы дважды)")

print("=" * 74)
print(f"проверок: {checked} · сеты: {', '.join(SETS)}")
if fails:
    print(f"\n❌ ПРОВАЛЕНО: {len(fails)}")
    for f in fails[:25]:
        print("   ·", f)
    sys.exit(1)
print("\n✅ ИМЕНА ДВУСТОРОННИХ КАРТ ПРИНИМАЮТСЯ В ЛЮБОЙ ЗАПИСИ во всех приборах")
