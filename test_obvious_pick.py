"""⚑ ОЧЕВИДНЫЙ ПИК · метка ⟳в пуле ×N · сверка ⚑ ПОСЛЕДНИЙ ПИК с телеметрией.

Закрывают ошибку драфта 3657e8ab (20.08.2026, подтверждена игроком): на P1P4 ранжировка
ставила Bilbo, Luckwearer топ-1 (отрыв 3.0), а совет модели ушёл в Mirkwood Nurturer
«чтобы остаться в цветах» пула из ТРЁХ карт — при том что синий тёк весь драфт; на P3P2
взята ЧЕТВЁРТАЯ копия Nurturer над Mirkwood Pathmaker (−6.1 GIH).

Логика баннеров проверяется на СИНТЕТИЧЕСКИХ рейтингах: числа 17Lands дрейфуют
(JOURNAL § 8.2 ③), тест, привязанный к живым числам, ломался бы от дрейфа, а не от
дефекта. Интеграция — на реальном драфте 3657e8ab с ГРОМКИМ пропуском, если история
вымыта (§ 8.16 ⑤: молчаливый skip = тест, который не измеряет).
Все проверки зовут боевой код draft_live (§ 8.5: копия логики в тесте не считается).
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

fails = []


def check(cond, msg):
    print(("   ✅ " if cond else "   ❌ ") + msg)
    if not cond:
        fails.append(msg)


# ── 1. Логика ⚑ ОЧЕВИДНЫЙ ПИК на синтетике ───────────────────────────────────
print("=" * 78)
print("⚑ ОЧЕВИДНЫЙ ПИК — синтетика (боевой obvious_pick_banner + rank_score)")
print("=" * 78)


def fake(gihs):
    """ratings по списку GIH (в долях), имена Card0..N; by_id пустой — имя из ratings."""
    return {i: {"name": f"Card{i}", "ever_drawn_win_rate": g} for i, g in enumerate(gihs)}


rat = fake([0.620, 0.585, 0.555])          # отрыв 3.5 — очевидный пак
g = [(None, [0, 1, 2])]
b = b_early = D.obvious_pick_banner(g, {}, rat, {}, picks=[9] * 3)
print("\n".join("  " + x for x in b) if b else "  (молчит)")
check(bool(b) and "Card0" in b[0] and "+3.5" in b[0],
      "отрыв 3.5 → баннер горит и называет топ-карту с величиной отрыва")
check(len(b) == 2 and "НЕ цветовое обязательство" in b[1],
      "пул <5 карт → вторая строка про «не мой цвет — не причина»")

b = D.obvious_pick_banner(g, {}, rat, {}, picks=[9] * 12)
check(len(b) == 2 and "причиной-ролью" in b[1],
      "пул ≥5 карт → вторая строка требует названную причину-роль")

check(D.obvious_pick_banner([(None, [0, 1])], {}, fake([0.600, 0.571]), {}, [9] * 3) == [],
      "отрыв 2.9 → молчит (порог § 8.9 — 3.0)")
check(D.obvious_pick_banner([(None, [0])], {}, fake([0.620]), {}, []) == [],
      "одна карта с данными → молчит")
check(D.obvious_pick_banner([], {}, {}, {}, []) == [], "пустой пак → молчит")

# отрыв считается rank_score, а не голым GIH: сырой разрыв 2.0, но бомба-надбавка
# (колено 63) даёт топу +3, и суммарный отрыв 5.0 → горит. Это и есть смысл выноса
# rank_score: баннер видит пак теми же глазами, что сортировка.
b = D.obvious_pick_banner([(None, [0, 1])], {}, fake([0.650, 0.630]), {}, [9] * 3)
check(bool(b), "отрыв считается по rank_score (GIH 2.0 + бомба-надбавка) — горит")

# ── 2. Интеграция: реальный драфт 3657e8ab ───────────────────────────────────
print()
print("=" * 78)
print("Интеграция — реальные паки драфта 3657e8ab")
print("=" * 78)
by_id, rat = D.load_cards(), D.load_ratings()
hist = json.load(open(os.path.join(HERE, ".draft_hist.json")))
DID = next((k for k in hist if k.startswith("3657e8ab")), None)
tel = os.path.join(HERE, "pools", "hob_3657e8ab_telemetry.jsonl")
packs = hist.get(DID, {}) if DID else {}

if not DID or not os.path.exists(tel):
    print("  ⏭ драфт 3657e8ab не найден — интеграционная часть пропущена (история вымыта)")
else:
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

    if "3-2" not in packs:
        print("  ⏭ пак P3P2 вымыт из .draft_hist.json — кейс пропущен")
    else:
        # P3P2: Mirkwood Pathmaker 61.7 против 4-й Mirkwood Nurturer — отрыв ≥5, дрейф
        # чисел 17Lands его не съест (P1P4 с отрывом ровно 3.0 намеренно не проверяется).
        pl = pool(28)
        main = D.pool_main_colors(pl, by_id)
        grouped = D.pack_order(packs["3-2"], by_id, rat, {}, main)
        b = D.obvious_pick_banner(grouped, by_id, rat, {}, pl)
        print("\n".join("  " + x for x in b) if b else "  (молчит)")
        check(bool(b) and "Mirkwood Pathmaker" in b[0],
              "P3P2: баннер называет Mirkwood Pathmaker — реальная ошибка того драфта")

        # метка копий: в пуле к P3P2 три Mirkwood Nurturer, и в паке лежит четвёртая
        blk = D.render_block(3, 2, packs["3-2"], pl, by_id, rat, "testdraf")
        line = next((x for x in blk.splitlines()
                     if "Mirkwood Nurturer" in x and "⟳" in x), "")
        print("  " + (line.strip() or "(метки нет)"))
        check("⟳в пуле ×3" in line, "render_block печатает ⟳в пуле ×3 у 4-й копии Nurturer")
        check(any("⚑ ОЧЕВИДНЫЙ ПИК" in x for x in blk.splitlines()),
              "⚑ ОЧЕВИДНЫЙ ПИК подключён в render_block (общий путь Premier/Quick)")
        # pools/hob_testdraf.txt НЕ удалять: на регистронезависимой macOS-ФС это тот же
        # файл, что закоммиченный pools/hob_TESTDRAF.txt (поймано 20.08.2026 — клинап
        # первой редакции удалил его из рабочего дерева). Файл просто перезаписывается,
        # как это делает и test_parser_parity.

# ── 3. ⚑ ПОСЛЕДНИЙ ПИК: сверка с телеметрией ─────────────────────────────────
print()
print("=" * 78)
print("⚑ ПОСЛЕДНИЙ ПИК — расхождение с ранжировкой печатается явно")
print("=" * 78)
FID = "00000badfeedface"                     # hex → _telemetry_path его принимает
fpath = D._telemetry_path(FID)
try:
    frat = {7: {"name": "Taken Card"}, 8: {"name": "Other"}}
    with open(fpath, "w", encoding="utf-8") as f:
        f.write(json.dumps({"t": "pack", "pn": 1, "pk": 2, "i": 1, "n": 13,
                            "adv": ["Advised Card", "Other"]}) + "\n")
    b = D.last_pick_banner([8, 7], {}, frat, FID)
    print("  " + b[0])
    check("РАЗОШЁЛСЯ" in b[0] and "Advised Card" in b[0],
          "взято не то, что ставила ранжировка → баннер называет расхождение и совет")
    with open(fpath, "w", encoding="utf-8") as f:
        f.write(json.dumps({"t": "pack", "pn": 1, "pk": 2, "i": 1, "n": 13,
                            "adv": ["Taken Card", "Other"]}) + "\n")
    b = D.last_pick_banner([8, 7], {}, frat, FID)
    check("РАЗОШЁЛСЯ" not in b[0], "взят топ-1 ранжировки → обычная строка, без тревоги")
    b = D.last_pick_banner([8, 7], {}, frat, None)
    check(bool(b) and "РАЗОШЁЛСЯ" not in b[0],
          "без draft_id (нет телеметрии) деградирует в старое поведение")
finally:
    if os.path.exists(fpath):
        os.remove(fpath)

print("=" * 78)
if fails:
    print(f"❌ ПРОВАЛЕНО {len(fails)}:")
    for f in fails:
        print("   ·", f)
    sys.exit(1)
print("✅ ОЧЕВИДНЫЙ ПИК НАЗВАН В МОМЕНТ ПИКА: отрыв ≥3 печатается до совета, копии "
      "в пуле помечены у карты, расхождение с ранжировкой не тонет.")
