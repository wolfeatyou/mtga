"""Два баннера, закрывающих дыры драфта eba1b036 (внесены 20.08.2026).

⚑ КОПИИ — за тот драфт набрано 4 `Confusticate and Bebother` при максимуме 3 у
победителей, 3 `Old Thrush` и 3 `Long-Bodied Grey Dog` при максимуме 2, и ни один
прибор не сказал об этом В МОМЕНТ ПИКА. Потолок читается из блока `played`
(`find_traps.py <set> --write`), предпочтительно максимум ВНУТРИ пары.

⚑ ПОСЛЕДНИЙ ПИК — на P2P8 советчик рекомендовал `Gollum the Abandoned`, игрок взял
`Gandalf, Wandering Wizard`, и расхождение прошло незамеченным до конца драфта: имя
было видно в хвосте сорокаэлементного списка пула, но никто его там не искал.

Прогон идёт по РЕАЛЬНЫМ пакам и пулам того драфта (урок JOURNAL § 8.5).
"""
import json
import os
import re
import sys

os.environ["MTGA_SET"] = "hob"
os.environ["MTGA_OFFLINE"] = "1"
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.argv = ["draft_live.py", "hob"]
import draft_live as D

by_id, rat = D.load_cards(), D.load_ratings()
fails = []


def check(cond, msg):
    print(("   ✅ " if cond else "   ❌ ") + msg)
    if not cond:
        fails.append(msg)


# ── данные драфта: паки из истории, пики из телеметрии ───────────────────────
hist = json.load(open(os.path.join(HERE, ".draft_hist.json")))
DID = next((k for k in hist if k.startswith("eba1b036")), None)
tel = os.path.join(HERE, "pools", f"hob_{(DID or '')[:8]}_telemetry.jsonl")
if not DID or not os.path.exists(tel):
    print("⏭  драфт eba1b036 не найден в истории/телеметрии — тест пропущен")
    sys.exit(0)

packs = hist[DID]
names = [r["name"] for r in sorted(
    (json.loads(l) for l in open(tel, encoding="utf-8")),
    key=lambda r: r.get("i", 0)) if r.get("t") == "pick"]
N2I = {}
for cid, c in by_id.items():
    for k in (c.get("name", ""), c.get("name", "").split(" //")[0]):
        N2I.setdefault(re.sub(r"[^a-z0-9]", "", k.lower()), cid)


def pool(n):
    out = []
    for x in names[:n]:
        cid = N2I.get(re.sub(r"[^a-z0-9]", "", x.lower()))
        if cid is not None:
            out.append(cid)
    return out


print("=" * 78)
print("⚑ КОПИИ — потолок копий у победителей")
print("=" * 78)
assert (D.load_traps() or {}).get("played"), \
    "нет блока played в hob_traps.json — запусти `python3 find_traps.py hob --write`"
assert "max" in next(iter(D.load_traps()["played"].values())), \
    "в блоке played нет потолка копий (`max`) — перегенерируй hob_traps.json"

cases = [
    (3, 12, 39, "Confusticate and Bebother"),   # в пуле 3, максимум у победителей 3
    (3, 2, 29, "Old Thrush"),                   # в пуле 2, максимум 2
    (3, 13, 40, "Long-Bodied Grey Dog"),        # в пуле 2, максимум в UR 1
]
for pn, pk, npool, card in cases:
    pl = pool(npool)
    main = D.pool_main_colors(pl, by_id)
    b = D.copies_banner(packs[f"{pn}-{pk}"], by_id, rat, main, pl)
    txt = " ".join(b)
    print("\n".join(f"  P{pn}P{pk}: {x}" for x in b) if b else f"  P{pn}P{pk}: (молчит)")
    check(card in txt, f"P{pn}P{pk}: назван {card} — реальный перебор того драфта")

# молчит, когда копий ещё мало
early = pool(6)
b0 = D.copies_banner(packs["1-7"], by_id, rat, D.pool_main_colors(early, by_id), early)
check(not b0, "молчит на раннем пуле, где ни одна карта потолка не достигла")
check(D.copies_banner(packs["1-1"], by_id, rat, None, []) == [], "молчит при пустом пуле")

# не больше двух строк — иначе баннер превращается в шум
big = pool(41)
b_many = D.copies_banner(packs["3-1"], by_id, rat, D.pool_main_colors(big, by_id), big)
check(len(b_many) <= 2, f"не больше двух строк за пик (получено {len(b_many)})")

print()
print("=" * 78)
print("⚑ ПОСЛЕДНИЙ ПИК — сверка «взято против совета»")
print("=" * 78)
pl = pool(22)                     # 22-й пик драфта = P2P8, где игрок ушёл от совета
b = D.last_pick_banner(pl, by_id, rat)
print("  " + (b[0] if b else "(молчит)"))
check(bool(b) and "Gandalf, Wandering Wizard" in b[0],
      "называет карту, реально ушедшую в пул на прошлом ходу")
check("№22" in b[0], "печатает НОМЕР пика — по нему видно гонку дебаунса")
check(D.last_pick_banner([], by_id, rat) == [], "молчит на первом пике, когда пул пуст")

# баннер обязан быть ПЕРВОЙ строкой блока сигналов: сверка идёт до рассуждения
sig = D.draft_signals(packs["3-2"], by_id, rat, D.pool_main_colors(pool(29), by_id),
                      3, 2, pool(29), DID)
check(sig and sig[0].startswith("⚑ ПОСЛЕДНИЙ ПИК"),
      "печатается первой строкой блока СИГНАЛЫ (сверка до рассуждения)")
check(any(x.startswith("⚑ КОПИИ") for x in sig), "⚑ КОПИИ подключён в draft_signals")

print("=" * 78)
if fails:
    print(f"❌ ПРОВАЛЕНО {len(fails)}:")
    for f in fails:
        print("   ·", f)
    sys.exit(1)
print("✅ ОБА БАННЕРА РАБОТАЮТ: перебор копий назван в момент пика, "
      "а расхождение «совет против взятого» больше не тонет в списке пула.")
