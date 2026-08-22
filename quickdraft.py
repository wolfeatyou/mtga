#!/usr/bin/env python3
"""Quick Draft (bot-draft) reader — ТОЛЬКО парсер лога, весь анализ в draft_live.

Разделение обязанностей (введено 10.08.2026, чтобы не ловить дрейф):
  · РАЗНОЕ у Premier и Quick — формат события в Player.log.
        Premier: "PackCards"/"DraftPack" + отдельные MakePick-строки.
        Quick:   BotDraftDraftStatus, чей Payload держит {DraftPack, PackNumber,
                 PickNumber, PickedCards} — то есть и пак, и весь пул сразу.
  · ОБЩЕЕ — всё остальное: сортировка пака, тир/GIH/пар-GIH/IWD/OH/ALSA/тир пика,
    флаги ~splash/✗offcolor/★synergy/⚠trap, баннеры КРИВАЯ/ПЛАН/ПРОФИЛЬ/пивот/колесо,
    сводка пула и его автосохранение. Всё это — `draft_live.render_block`.

Почему так: пока рендеры были раздельные, они молча разъехались — у Quick стояли
СВОИ пороги тира (S≥60 против A≥60 у Premier), не было пар-GIH, флагов кастуемости,
⚠trap и вообще ни одного баннера, а рейтинги грузились без фильтра game_count>200.
Одна и та же карта показывалась разными буквами в двух режимах.

Usage: python3 quickdraft.py [msh]        (блокирующий цикл — quickdraft_watch.py)
Env:   MTGA_LOG to override log path.
"""
import hashlib, json, os, re, sys
from collections import Counter

SKILL = os.path.dirname(os.path.abspath(__file__))
SET = (sys.argv[1] if len(sys.argv) > 1 else "msh").lower()
sys.path.insert(0, SKILL)
import draft_live as DL          # noqa: E402  (main() под __main__-guard — импорт безопасен)

LOG = os.environ.get("MTGA_LOG") or os.path.expanduser(
    "~/Library/Logs/Wizards Of The Coast/MTGA/Player.log")


def _parse_payload(p):
    try:
        return json.loads(p.encode().decode("unicode_escape"))
    except Exception:
        try:
            return json.loads(p.replace('\\"', '"').replace('\\\\', '\\'))
        except Exception:
            return None


def chrono_picks(payloads):
    """PickedCards у Arena НЕ в порядке пиков — хронологию восстанавливаем диффом статусов.

    Пойман 22.08.2026 на живом драфте 91a4b8e8: пик №2 (Desolation Prowler) лежал в
    массиве на позиции 4, пик №9 (Key to the Side-Door) — на позиции 2. Из-за этого
    `последний элемент массива = последний пик` — ложь, и баннер ⚑ ПОСЛЕДНИЙ ПИК
    ~10 пиков подряд печатал «Desolation Prowler» с ложным «РАЗОШЁЛСЯ с ранжировкой»
    (JOURNAL § 8.32; телеметрийную половину той же болезни § 8.31 видел ещё 21.08).

    Метод: идём по статусам одного драфта; карта, чей счётчик вырос между соседними
    статусами, и есть пик этого хода. Границу драфта в логе определяем по «пул только
    растёт»: как только более ранний статус перестаёт быть под-мультимножеством
    позднего — это другой драфт. Хвост, попавший в лог не с начала (ротация), кладём
    как есть — для него порядок неизвестен, честнее массива он не станет.
    """
    seqs = []
    for p in payloads:
        st = _parse_payload(p)
        if st is not None:
            seqs.append([int(x) for x in st.get("PickedCards", [])])
    if not seqs:
        return []
    start = len(seqs) - 1
    for i in range(len(seqs) - 1, 0, -1):
        prev, cur = Counter(seqs[i - 1]), Counter(seqs[i])
        if all(cur[k] >= v for k, v in prev.items()):
            start = i - 1
        else:
            break
    chrono = list(seqs[start])           # порядок этого префикса неизвестен (ротация лога)
    have = Counter(chrono)
    for i in range(start + 1, len(seqs)):
        cur = Counter(seqs[i])
        for cid in seqs[i]:
            if have[cid] < cur[cid]:
                chrono.append(cid)
                have[cid] += 1
    return chrono


# ---- парсер: последний BotDraftDraftStatus ----
raw = open(LOG, "r", errors="ignore").read()
payloads = re.findall(r'"Payload":"(\{.*?DraftPack.*?\})"', raw)
if not payloads:
    print("Нет BotDraftDraftStatus с DraftPack в логе — открой пак в Arena.")
    sys.exit(0)

status = _parse_payload(payloads[-1])
if status is None:
    print("Не разобрал последний BotDraftDraftStatus — покажи хвост лога.")
    sys.exit(0)

pack = [int(x) for x in status.get("DraftPack", [])]
picked = chrono_picks(payloads) or [int(x) for x in status.get("PickedCards", [])]
pn = status.get("PackNumber", 0) + 1
pk = status.get("PickNumber", 0) + 1
ev = status.get("EventName", "")

# ---- всё остальное — общий рендер ----
# У Quick нет draftId, а EventName повторяется между драфтами → идентификатор выводим из
# ПЕРВОГО пака лога: стабилен внутри драфта, различает драфты между собой. Нужен для
# детекта колеса и для имени файла автосохранённого пула.
draft_tag = hashlib.md5(payloads[0].encode()).hexdigest()[:8]
by_id = DL.load_cards()          # arena_id -> карта Scryfall
ratings = DL.load_ratings()      # mtga_id  -> статы 17Lands (тот же фильтр, что у Premier)

print(DL.render_block(
    pn, pk, pack, picked, by_id, ratings, draft_tag,
    header=f"===== QUICK DRAFT [{SET.upper()}] {ev}  (Пак {pn}, пик {pk}) — {len(pack)} карт ====="))
