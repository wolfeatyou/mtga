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

SKILL = os.path.dirname(os.path.abspath(__file__))
SET = (sys.argv[1] if len(sys.argv) > 1 else "msh").lower()
sys.path.insert(0, SKILL)
import draft_live as DL          # noqa: E402  (main() под __main__-guard — импорт безопасен)

LOG = os.environ.get("MTGA_LOG") or os.path.expanduser(
    "~/Library/Logs/Wizards Of The Coast/MTGA/Player.log")

# ---- парсер: последний BotDraftDraftStatus ----
raw = open(LOG, "r", errors="ignore").read()
payloads = re.findall(r'"Payload":"(\{.*?DraftPack.*?\})"', raw)
if not payloads:
    print("Нет BotDraftDraftStatus с DraftPack в логе — открой пак в Arena.")
    sys.exit(0)

last = payloads[-1]
try:
    status = json.loads(last.encode().decode("unicode_escape"))
except Exception:
    status = json.loads(last.replace('\\"', '"').replace('\\\\', '\\'))

pack = [int(x) for x in status.get("DraftPack", [])]
picked = [int(x) for x in status.get("PickedCards", [])]
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
