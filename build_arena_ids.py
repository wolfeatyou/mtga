#!/usr/bin/env python3
"""Проставить arena_id в <set>_set.json из ЛОКАЛЬНОЙ базы карт MTG Arena.

Зачем: Scryfall и MTGJSON присваивают arena_id с задержкой в несколько дней после
релиза сета, а `draft_live.py` резолвит содержимое пака ИСКЛЮЧИТЕЛЬНО по arena_id.
То есть свежий сет физически недрафтуем, пока публичные источники не догонят.
Клиент Arena при этом уже знает все id — они лежат в его собственной SQLite-базе.
(Пойманo на HOB 11.08.2026: Scryfall 0/193 arena_id, MTGJSON 0/193, база Arena — все 280.)

Использование:
    python3 build_arena_ids.py hob            # проставить и записать
    python3 build_arena_ids.py hob --dry-run  # только отчёт о покрытии

Имена в базе Arena лежат в Localizations_enUS под тремя значениями Formatted:
0 = plain, 1 = с HTML-разметкой (<nobr> и т.п.), 2 = альтернативный plain.
У большинства карт свежего сета есть ТОЛЬКО Formatted=1, поэтому берём любой
доступный в порядке 0 → 2 → 1 и чистим теги. (На HOB: Formatted=0 покрывает 26
карт из 280 — джойн только по нему молча теряет 90% сета.)
"""
import glob
import html
import json
import os
import re
import sqlite3
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
DB_GLOB = os.path.expanduser(
    "~/Library/Application Support/com.wizards.mtga/Downloads/Raw/Raw_CardDatabase_*.mtga"
)


def find_db():
    files = glob.glob(DB_GLOB)
    if not files:
        sys.exit(
            "Не найдена база карт Arena.\nОжидалась здесь: " + DB_GLOB +
            "\nЗапусти Arena хотя бы раз, чтобы она скачала Raw_CardDatabase_*.mtga."
        )
    return max(files, key=os.path.getmtime)


def norm(s):
    """Ключ сравнения имён: только ASCII-буквы/цифры в нижнем регистре.

    Диакритику РАЗБИРАЕМ, а не выбрасываем: Scryfall пишет "Dáin", Arena — "Dain",
    и без NFKD ключи расходятся ("din" против "dain"). На HOB это 7 карт из 193
    (весь дом Дурина: Dáin, Fíli, Kíli, Óin, Thrór).
    """
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    return re.sub(r"[^a-z0-9]", "", s.lower())


def clean(loc):
    """Formatted=1 приходит с HTML — вычистить теги и сущности."""
    return html.unescape(re.sub(r"<[^>]+>", "", loc or "")).strip()


def arena_names(setcode):
    """ExpansionCode -> {norm(name): [grpid, ...]} + список сырых записей.

    Один и тот же карточный титул может иметь несколько GrpId (базовая печать +
    альт-арты/showcase). В драфте прийти может ЛЮБОЙ из них, поэтому собираем ВСЕ,
    а не только IsPrimaryCard.
    """
    con = sqlite3.connect(f"file:{find_db()}?mode=ro", uri=True)
    loc = {}
    for locid, fmt, text in con.execute(
        "SELECT LocId, Formatted, Loc FROM Localizations_enUS"
    ):
        # приоритет 0 > 2 > 1: меньший ранг не перетирается большим
        rank = {0: 0, 2: 1, 1: 2}.get(fmt, 3)
        cur = loc.get(locid)
        if cur is None or rank < cur[0]:
            loc[locid] = (rank, clean(text))

    rows = con.execute(
        "SELECT GrpId, TitleId, CollectorNumber, IsPrimaryCard "
        "FROM Cards WHERE ExpansionCode=? AND IsToken=0 ORDER BY GrpId",
        (setcode.upper(),),
    ).fetchall()
    con.close()

    by_name = {}
    recs = []
    for grpid, titleid, cnum, primary in rows:
        entry = loc.get(titleid)
        if not entry or not entry[1]:
            continue
        name = entry[1]
        by_name.setdefault(norm(name), []).append(grpid)
        recs.append({"grpid": grpid, "name": name, "collector": cnum, "primary": primary})
    return by_name, recs


def scryfall_keys(card):
    """Все имена, под которыми карта может лежать в базе Arena.

    У adventure/split/DFC Scryfall хранит склейку "Front // Back", а Arena —
    только лицевую сторону, поэтому отдаём оба варианта.
    """
    keys = [card.get("name", "")]
    full = card.get("name", "")
    if " // " in full:
        keys += full.split(" // ")
    for f in card.get("card_faces", []) or []:
        keys.append(f.get("name", ""))
    return [norm(k) for k in keys if k]


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    dry = "--dry-run" in sys.argv
    if not args:
        sys.exit("Укажи код сета, например: python3 build_arena_ids.py hob")
    code = args[0].lower()

    path = os.path.join(HERE, f"{code}_set.json")
    if not os.path.exists(path):
        sys.exit(f"Нет {path} — сначала скачай карты сета со Scryfall.")
    cards = json.load(open(path))

    by_name, recs = arena_names(code)
    print(f"База Arena: {len(recs)} нетокенных карт {code.upper()}, "
          f"{len(by_name)} уникальных имён")

    hit = miss = 0
    unmatched = []
    for c in cards:
        ids = []
        for k in scryfall_keys(c):
            ids += by_name.get(k, [])
        ids = sorted(set(ids))
        if ids:
            c["arena_id"] = ids[0]          # базовая печать — минимальный GrpId
            if len(ids) > 1:
                c["arena_ids"] = ids        # альт-арты: пак может отдать любой
            hit += 1
        else:
            miss += 1
            unmatched.append(c.get("name", "?"))

    print(f"Сопоставлено: {hit}/{len(cards)}  (без arena_id: {miss})")
    if unmatched:
        print("Не найдены в базе Arena:")
        for n in unmatched[:25]:
            print("   ", n)
        if len(unmatched) > 25:
            print(f"    … ещё {len(unmatched) - 25}")

    if dry:
        print("--dry-run: файл не изменён")
        return
    json.dump(cards, open(path, "w"), ensure_ascii=False)
    print(f"Записано: {path}")


if __name__ == "__main__":
    main()
