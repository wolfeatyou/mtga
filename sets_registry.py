"""Единый список поддерживаемых сетов. ОДНО место, где он живёт.

Заведено 16.08.2026. До этого whitelist был скопирован в 9 файлов (draft_live, draft_pick2,
match_live, match_watch, draft_sim, replay_moments, replay_report, deck_profile,
draft_goldfish), и SKILL.md документировал это как процедуру: «заводя сет, поправь в девяти
местах». Документировать техдолг вместо починки — тот же приём, что лечить сортировку прозой:
инструкция не выполняется, а класс ошибок («завёл сет, забыл файл») остаётся.

Порядок в SETS — приоритет автодетекта в draft_sim: сначала текущий сет.
Заводя новый сет: добавить сюда одну строку — и всё. Ничего больше править не нужно.
"""

# код сета -> файл рейтингов 17Lands (может отсутствовать на диске: сет живёт и без него,
# просто без GIH/IWD/ALSA — см. режим «сет без данных»)
RATING_FILE = {
    "hob": "17l_hob_premierdraft.json",
    "msh": "17l_msh_premierdraft.json",
    "sos": "17l_sos_premierdraft.json",
    "mkm": "17l_mkm_premierdraft.json",
}

# текущий сет первым — от этого зависит порядок автодетекта
SETS = list(RATING_FILE)

# файлы карт Scryfall в том же порядке
SET_FILES = [f"{s}_set.json" for s in SETS]


def is_set(code):
    """'HOB' / 'hob' -> True. Пустое/None -> False."""
    return bool(code) and code.lower() in RATING_FILE
