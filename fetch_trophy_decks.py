#!/usr/bin/env python3
"""Скачивает трофейные колоды с untapped.gg прямо в `ref_decks/<set>/`.

    python3 fetch_trophy_decks.py hob                  # топ-10, GOLD_TO_MYTHIC, Premier
    python3 fetch_trophy_decks.py hob --n 25
    python3 fetch_trophy_decks.py hob --rank BRONZE_TO_MYTHIC
    python3 fetch_trophy_decks.py hob --sort record    # сначала 7-0, потом 7-1, потом 7-2
    python3 fetch_trophy_decks.py hob --event QUICK_DRAFT
    python3 fetch_trophy_decks.py hob --dry-run        # показать, ничего не писать

Зачем. `ref_decks/<set>/` — единственная внешняя популяция, на которой скилл калибруется
(§ КАЛИБРОВКА закон 1 в SKILL.md), и `learn.py` строит из неё `<set>_learned.md`. До этого
листы переносились руками, поэтому их было 5, потом 8, потом 31 — и каждый вывод по выборке
умирал от следующей порции данных (см. `hob_knowledge.md` § «Мой вывод был неверен ДВАЖДЫ»).
Ручной перенос и есть причина маленькой выборки.

Как это работает (чтобы чинить, когда untapped поменяет фронтенд).
1. Страница `mtga.untapped.gg/limited/draft/<slug>/trophy-decks` — Next.js; в её
   `__NEXT_DATA__` лежат (а) `minifiedMtgaJsonData` — карты сета и `localeData` вида
   titleId → название, (б) `trophyDecksByEventUrl` — путь к API списка колод.
2. Список колод: `api.mtga.untapped.gg/api/v1<путь из п.1>`. В SSR-страницу попадают только
   первые 8 колод, в API — все (на 16.08.2026 по HOB их 509), поэтому берём из API.
3. Сама колода лежит в поле `ds` — это deckstring V4 формата untapped (НЕ формат Arena).
   Декодер — `decode_deckstring()` ниже, портирован с их `fromDeckString`; формат описан
   там же в докстринге. Отдаёт titleId, названия берутся из `localeData`.
4. Ранг колоды — числовое поле `rk`: 2=bronze, 3=silver, 4=gold, 5=platinum, 6=diamond,
   7=mythic. Бесплатный эндпоинт отдаёт только bronze–platinum; diamond/mythic — платные,
   поэтому `--rank *_TO_MYTHIC` на free-выдаче фактически означает «до платины включительно».

Файлы пишутся в формате экспорта Arena (как остальные листы в `ref_decks/`), имя —
`<цвета>_<гильдия>_<рекорд>_<ник>.txt`. Провенанс (id колоды, дата, ранг, deckstring)
пишется рядом в `_source.json` — по нему же идёт дедупликация при повторных запусках,
чтобы одна и та же колода не легла в популяцию дважды и не перекосила `learn.py`.
"""
import argparse
import base64
import json
import os
import re
import sys
import urllib.request
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from learn import load_set, face, PIP, BASIC  # noqa: E402

PAGE = "https://mtga.untapped.gg/limited/{fmt}/{slug}/trophy-decks"
API = "https://api.mtga.untapped.gg/api/v1"
LOC_FULL = "https://mtgajson.untapped.gg/v1/latest/loc_en.json"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")

# Слаг сета в URL untapped. Заводя сет — добавить строку сюда (или разово дать --slug).
SLUG = {
    "hob": "the-hobbit",
    "msh": "marvel-super-heroes",
    "sos": "secrets-of-strixhaven",
    "mkm": "murders-at-karlov-manor",
}

RANKS = ["none", "spark", "bronze", "silver", "gold", "platinum", "diamond", "mythic"]

GUILD = {"WU": "azorius", "UB": "dimir", "BR": "rakdos", "RG": "gruul", "WG": "selesnya",
         "WB": "orzhov", "UR": "izzet", "BG": "golgari", "RW": "boros", "GU": "simic"}
TRIO = {"WUB": "esper", "UBR": "grixis", "BRG": "jund", "RGW": "naya", "GWU": "bant",
        "WBG": "abzan", "URW": "jeskai", "BGU": "sultai", "RWB": "mardu", "GUR": "temur"}


# ─────────────────────────────── deckstring V4 ───────────────────────────────

class _Reader:
    """Поток LEB128-варинтов (little-endian, 7 бит на байт, старший бит = продолжение)."""

    def __init__(self, data):
        self.d, self.i = data, 0

    def byte(self):
        self.i += 1
        return self.d[self.i - 1]

    def varint(self):
        val = shift = 0
        while True:
            b = self.byte()
            val |= (b & 0x7F) << shift
            if not b & 0x80:
                return val
            shift += 7


def _group(r, fixed):
    """Одна группа карт: N записей, у каждой дельта titleId (и число копий, если не fixed)."""
    out, tid = [], 0
    for _ in range(r.varint()):
        qty = fixed if fixed else r.varint()
        tid += r.varint()
        out.extend([tid] * qty)
    return out


def _board(r):
    """Борд = пять групп подряд: по 1 копии, по 2, по 3, по 4, затем с явным числом копий."""
    out = []
    for fixed in (1, 2, 3, 4, None):
        out.extend(_group(r, fixed))
    return out


def decode_deckstring(ds):
    """untapped deckstring V4 → {'main': [titleId…], 'side': […], 'wish': […]}.

    Байтовая раскладка: 0x00 · версия(=4) · блок командиров/компаньонов (счётчик, затем
    пары «дельта titleId, индекс группы») · далее секции, каждая = тег + борд, пока тег != 0.
    Теги: 1=main, 2=sideboard, 3=wishboard. Порт `rD`/`rk`/`ra`/`rs`/`ro` из фронтенда untapped.
    """
    raw = base64.urlsafe_b64decode(ds + "=" * (-len(ds) % 4))
    r = _Reader(raw)
    if r.byte() != 0:
        raise ValueError("не deckstring: нет ведущего нуля")
    ver = r.varint()
    if ver != 4:
        raise ValueError(f"поддержан только deckstring V4, пришёл V{ver}")
    for _ in range(r.varint()):          # командиры/компаньоны — в лимитед пусто
        r.varint(), r.varint()
    res = {"main": [], "side": [], "wish": []}
    tag = r.varint()
    while tag:
        board = _board(r)
        if tag == 1:
            res["main"] = board
        elif tag == 2:
            res["side"] = board
        elif tag == 3:
            res["wish"] = board
        tag = r.varint()
    return res


# ─────────────────────────────── источники данных ───────────────────────────────

def get(url, as_json=True):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    with urllib.request.urlopen(req, timeout=60) as f:
        data = f.read()
    return json.loads(data) if as_json else data.decode("utf-8", "replace")


def page_data(slug, fmt):
    html = get(PAGE.format(fmt=fmt, slug=slug), as_json=False)
    m = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
                  html, re.S)
    if not m:
        raise SystemExit("не нашёл __NEXT_DATA__ — untapped поменял страницу")
    ssr = json.loads(m.group(1))["props"]["pageProps"]["ssrProps"]
    names = {int(k): v for k, v in
             (row[:2] for row in ssr["minifiedMtgaJsonData"]["localeData"])}
    return names, ssr["trophyDecksByEventUrl"]


def full_names(cache=os.path.join(HERE, "cache_untapped_loc_en.json")):
    """Полный словарь titleId→строка (5 МБ). Нужен, только если карты нет в наборе сета."""
    if not os.path.exists(cache):
        sys.stderr.write("… тяну полный loc_en.json с mtgajson.untapped.gg (~5 МБ)\n")
        open(cache, "wb").write(get(LOC_FULL, as_json=False).encode("utf-8"))
    return {int(row[0]): row[1] for row in json.load(open(cache, encoding="utf-8"))}


# ─────────────────────────────── имя файла ───────────────────────────────

def deck_colors(main, cards):
    """Цвета колоды по пипам заклинаний; гибрид — половина каждому.

    Порог второго и последующих цветов — четверть от главного, как в `learn.py.colors_of`
    (без него моночёрная 7-2 из-за одного {B/R} на эквипе уезжала в чужую пару). Отличие
    одно: здесь не обрезается на двух цветах, иначе трёхцветный Mardu 7-2 назывался бы
    двухцветным.
    """
    cnt = Counter()
    for name, q in main.items():
        c = cards.get(name)
        if not c or name in BASIC:
            continue
        for a, b in PIP.findall(face(c, "mana_cost")):
            if b:
                cnt[a] += 0.5 * q
                cnt[b] += 0.5 * q
            else:
                cnt[a] += q
    if not cnt:
        return "C"
    top = cnt.most_common(1)[0][1]
    keep = {c for c, n in cnt.items() if n >= top * 0.25}
    return "".join(c for c in "WUBRG" if c in keep)


def archetype(colors):
    if len(colors) == 1:
        return colors.lower() + "_mono"
    if len(colors) == 2:
        for code, name in GUILD.items():
            if set(code) == set(colors):
                return code.lower() + "_" + name
    if len(colors) == 3:
        for code, name in TRIO.items():
            if set(code) == set(colors):
                return colors.lower() + "_" + name
    return colors.lower() + f"_{len(colors)}c"


def deck_key(path):
    """Отпечаток колоды — мультимножество «карта×количество», независимо от порядка строк."""
    c = Counter()
    for line in open(path, encoding="utf-8"):
        m = re.match(r"(\d+)\s+(.+?)(?:\s+\([A-Z0-9]{3}\).*)?$", line.strip())
        if m:
            c[m.group(2)] += int(m.group(1))
    return tuple(sorted(c.items()))


def filename(deck, main, cards):
    who = re.sub(r"[^a-z0-9]", "", (deck.get("pn") or "anon").lower()) or "anon"
    return f"{archetype(deck_colors(main, cards))}_{deck['wi']}{deck['lo']}_{who}.txt"


# ─────────────────────────────── main ───────────────────────────────

def rank_range(spec):
    """'GOLD_TO_MYTHIC' → {4,5,6,7}. Так же, как untapped строит фильтр из URL."""
    parts = spec.lower().split("_to_")
    if len(parts) != 2 or any(p not in RANKS for p in parts):
        raise SystemExit(f"не понял --rank {spec!r}; ранги: {', '.join(RANKS[2:])}")
    lo, hi = (RANKS.index(p) for p in parts)
    return set(range(min(lo, hi), max(lo, hi) + 1))


def main():
    ap = argparse.ArgumentParser(description="трофейные колоды untapped.gg → ref_decks/<set>/")
    ap.add_argument("set", help="код сета, например hob")
    ap.add_argument("--n", type=int, default=10, help="сколько колод взять (по умолчанию 10)")
    ap.add_argument("--rank", default="GOLD_TO_MYTHIC",
                    help="диапазон рангов, как в URL untapped (GOLD_TO_MYTHIC)")
    ap.add_argument("--event", default="PREMIER_DRAFT", help="EventTypeFilter untapped")
    ap.add_argument("--sort", choices=("site", "record"), default="site",
                    help="site = как на странице (сначала свежие); record = сначала 7-0")
    ap.add_argument("--slug", help="слаг сета в URL untapped, если его нет в SLUG")
    ap.add_argument("--out", help="каталог назначения (по умолчанию ref_decks/<set>/)")
    ap.add_argument("--dry-run", action="store_true", help="показать и ничего не писать")
    ap.add_argument("--force", action="store_true", help="перекачать уже скачанные колоды")
    a = ap.parse_args()

    code = a.set.lower()
    slug = a.slug or SLUG.get(code)
    if not slug:
        raise SystemExit(f"не знаю слаг для {code!r} — передай --slug (см. URL на untapped)")
    fmt = "sealed" if "SEALED" in a.event.upper() else "draft"

    names, list_url = page_data(slug, fmt)
    decks = get(API + list_url)["data"]
    keep = rank_range(a.rank)
    decks = [d for d in decks if d["rk"] in keep]
    decks.sort(key=lambda d: d["dt"], reverse=True)          # site: сначала свежие
    if a.sort == "record":                                   # стабильно: внутри рекорда — свежие
        decks.sort(key=lambda d: (d["lo"], -d["wi"]))
    if not decks:
        raise SystemExit(f"по фильтру {a.rank}/{a.event} колод нет")
    top = max(d["rk"] for d in decks)
    if top < max(keep):
        sys.stderr.write(f"… выше {RANKS[top]} на бесплатной выдаче колод нет "
                         f"(diamond/mythic — платные), фильтр {a.rank} этого не меняет\n")

    out_dir = a.out or os.path.join(HERE, "ref_decks", code)
    src_path = os.path.join(out_dir, "_source.json")
    src = json.load(open(src_path, encoding="utf-8")) if os.path.exists(src_path) else {}
    seen = {v["id"] for v in src.values()}

    # Дедуп по СОДЕРЖИМОМУ, а не только по id: 31 лист лежал в ref_decks/ ещё до этого
    # скрипта и id у них нет, а один и тот же 40-карточник, попавший в популяцию дважды,
    # тихо удваивает свой вес в `learn.py` — то есть портит ровно то, ради чего его качали.
    have = {}
    for fn in os.listdir(out_dir) if os.path.isdir(out_dir) else []:
        if fn.endswith(".txt"):
            have[deck_key(os.path.join(out_dir, fn))] = fn

    cards = load_set(code)
    written = skipped = 0
    # Окно режется ДО цикла, а не счётчиком записей внутри него: иначе повторный запуск
    # пропускает уже скачанные и добирает следующие — то есть «топ-10» на второй раз молча
    # означает «ещё 10», и популяция растёт от каждого лишнего вызова.
    for deck in decks[:a.n]:
        if deck["di"] in seen and not a.force:
            skipped += 1
            continue
        try:
            title_ids = decode_deckstring(deck["ds"])["main"]
        except Exception as e:                                    # noqa: BLE001
            sys.stderr.write(f"!! {deck.get('pn')}: {e}\n")
            continue
        if any(t not in names for t in title_ids):
            names.update(full_names())                            # карта не из этого сета
        counts = Counter(names.get(t, f"<titleId {t}>") for t in title_ids)
        unknown = [n for n in counts if n not in cards and n not in BASIC]
        key = tuple(sorted(counts.items()))
        if key in have and not a.force:
            skipped += 1
            continue

        lines = ["Deck"] + [f"{q} {n}" for n, q in counts.most_common()]
        text = "\n".join(lines) + "\n"
        fn = filename(deck, counts, cards)
        rank = RANKS[deck["rk"]] if deck["rk"] < len(RANKS) else str(deck["rk"])
        note = f"  ⚠ не опознаны: {', '.join(unknown)}" if unknown else ""
        print(f"{'[dry] ' if a.dry_run else ''}{fn:<44} "
              f"{sum(counts.values())} карт · {rank} · {deck['dt'][:10]}{note}")
        if a.dry_run:
            written += 1
            continue
        os.makedirs(out_dir, exist_ok=True)
        open(os.path.join(out_dir, fn), "w", encoding="utf-8").write(text)
        have[key] = fn
        src[fn] = {"id": deck["di"], "player": deck.get("pn"), "rank": rank,
                   "wins": deck["wi"], "losses": deck["lo"], "date": deck["dt"],
                   "event": a.event, "ds": deck["ds"]}
        written += 1

    if not a.dry_run and written:
        os.makedirs(out_dir, exist_ok=True)
        json.dump(src, open(src_path, "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1, sort_keys=True)
    print(f"\n{written} колод записано, {skipped} из топ-{a.n} уже были, "
          f"всего по фильтру {a.rank} доступно {len(decks)}")
    if written and not a.dry_run:
        print(f"→ {out_dir}\n   дальше: python3 {os.path.join(HERE, 'learn.py')} {code}")


if __name__ == "__main__":
    main()
