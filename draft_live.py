#!/usr/bin/env python3
"""Live draft helper — читает Player.log Arena и показывает текущий пак.
  python3 draft_live.py mkm       — Quick Draft: Murders at Karlov Manor
  python3 draft_live.py sos       — Premier Draft: Secrets of Strixhaven
  python3 draft_live.py raw       — выгрузить сырые draft-строки лога (для отладки формата)
  (set-код можно сочетать с raw: `python3 draft_live.py mkm raw`)
Требует: detailed logs включены в Arena (Account -> Detailed Logs) + рестарт клиента.
"""
import json, re, os, sys, glob

LOG_ENV = os.environ.get("MTGA_LOG")
LOGDIR = os.path.expanduser("~/Library/Logs/Wizards Of The Coast/MTGA")
LOG = LOG_ENV or os.path.join(LOGDIR, "Player.log")
HERE = os.path.dirname(os.path.abspath(__file__))

def read_log_text():
    """Склеивает Player-prev.log + Player.log в хронологии (или один MTGA_LOG для тестов),
    чтобы обрыв связи / ротация лога не теряли ранние пики."""
    files = [LOG_ENV] if LOG_ENV else [os.path.join(LOGDIR, "Player-prev.log"),
                                       os.path.join(LOGDIR, "Player.log")]
    parts = []
    for f in files:
        if f and os.path.exists(f):
            parts.append(open(f, encoding="utf-8", errors="ignore").read())
    return "\n".join(parts)

def current_draft_id(text):
    """Последний draftId в логе = текущий драфт (для скоупа пиков). Ловит draftId и \\"DraftId\\"."""
    ids = re.findall(r'(?i)\\?"draftId\\?"\s*:\s*\\?"([0-9a-f-]{8,})\\?"', text)
    return ids[-1] if ids else None

def setcode():
    for a in sys.argv[1:]:
        if a.lower() in ("mkm", "sos", "msh"):
            return a.lower()
    return "sos"  # дефолт

def set_file():
    return os.path.join(HERE, f"{setcode()}_set.json")

RATING_FILE = {"mkm": "17l_mkm_premierdraft.json", "sos": "17l_sos_premierdraft.json", "msh": "17l_msh_premierdraft.json"}

def tier(w):
    if w >= 0.620: return "A+"
    if w >= 0.600: return "A "
    if w >= 0.580: return "B+"
    if w >= 0.560: return "B "
    if w >= 0.545: return "C+"
    if w >= 0.530: return "C "
    if w >= 0.515: return "D "
    return "F "

def stat_tag(r, cgih=None, pair=None):
    """Расширенный ярлык пика: тир + GIH + (GIH·пара) + IWD + OH-WR + ALSA.
      GIH  — ever_drawn_win_rate (винрейт игр, где карта в руке).
      IWD  — drawn_improvement_win_rate: насколько лучше идёт игра, КОГДА карту тянешь.
             IWD<0 => карту статистически вредно рисовать (низкий пол build-around) → флаг ⚠.
      OH   — opening_hand_win_rate: пол в стартовой руке (мертва ли в опенере).
    Это разводит «высокий потолок / низкий пол» (untapped-подобный сигнал) из самих 17Lands."""
    g = r.get("ever_drawn_win_rate") or 0
    iwd = r.get("drawn_improvement_win_rate")
    oh = r.get("opening_hand_win_rate")
    parts = [tier(g), f"GIH {g*100:.1f}"]
    if cgih is not None and pair:  # GIH в текущей паре цветов (17Lands, color-filtered)
        parts.append(f"{pair} {cgih*100:.1f}")
    if iwd is not None:
        parts.append(f"IWD {iwd*100:+.1f}")
    if oh:
        parts.append(f"OH {oh*100:.1f}")
    alsa_val = r.get('avg_seen', 0)
    if alsa_val is not None:
        parts.append(f"ALSA {alsa_val:.1f}")
    flag = " ⚠trap" if (iwd is not None and iwd < 0) else ""
    return "[" + "|".join(parts) + "]" + flag

# arena_id -> 17Lands статы
def load_ratings():
    f = os.path.join(HERE, RATING_FILE.get(setcode(), ""))
    if not os.path.exists(f):
        return {}
    out = {}
    for c in json.load(open(f)):
        mid = c.get("mtga_id")
        gw = c.get("ever_drawn_win_rate")
        if mid is not None and gw and c.get("game_count", 0) > 200:
            out[int(mid)] = c
    return out

# arena_id -> карта
def load_cards():
    cards = json.load(open(set_file()))
    by_id = {}
    for c in cards:
        aid = c.get("arena_id")
        if aid is not None:
            by_id[int(aid)] = c
    return by_id

def face(c, k):
    if "card_faces" in c and not c.get(k):
        return c["card_faces"][0].get(k, "") or ""
    return c.get(k, "") or ""

def short(c):
    R = {"common": "C", "uncommon": "U", "rare": "R", "mythic": "M"}.get(c.get("rarity"), "?")
    name = c.get("name", "?")
    cost = face(c, "mana_cost")
    tl = face(c, "type_line")
    pt = ""
    if c.get("power") is not None:
        pt = f" {c['power']}/{c['toughness']}"
    ot = face(c, "oracle_text").replace("\n", " ")
    if len(ot) > 90:
        ot = ot[:89] + "…"
    return f"[{R}] {name} {cost}{pt} — {tl}\n        {ot}"

# Вытаскиваем все возможные draft-события и их id-списки.
# Покрываем разные исторические форматы ключей Arena.
ID_LIST_KEYS = ["PackCards", "DraftPack", "CardsInPack", "draftPack"]
# Ключи номера пака/пика. SelfPack/SelfPick/CurrentPack/CurrentPick — 1-индексные;
# PackNumber/PickNumber — 0-индексные (старый бот-формат). norm_num приводит к 1-based.
PACK_KEYS_1 = ["SelfPack", "CurrentPack"]
PACK_KEYS_0 = ["PackNumber", "packNumber"]
PICK_KEYS_1 = ["SelfPick", "CurrentPick"]
PICK_KEYS_0 = ["PickNumber", "pickNumber"]

def norm_num(ctx, ones, zeros):
    """Номер 1-based: 1-индексные ключи как есть, 0-индексные +1."""
    for k in ones:
        m = re.search(rf'"{k}"\s*:\s*"?(\d+)"?', ctx)
        if m:
            return int(m.group(1))
    for k in zeros:
        m = re.search(rf'"{k}"\s*:\s*"?(\d+)"?', ctx)
        if m:
            return int(m.group(1)) + 1
    return None

def find_packs(text):
    """Список (пак 1-based, пик 1-based, [ids], pos) в порядке появления.
    Дедупликация по позиции: PackCards встречается в обоих rx, дублей нет."""
    seen_pos = set()
    out = []
    for rx in (r'"(?:PackCards|CardsInPack|draftPack)"\s*:\s*"([\d,]+)"',
               r'"(?:DraftPack|PackCards)"\s*:\s*\[([\d,\s]+)\]'):
        for m in re.finditer(rx, text):
            if m.start() in seen_pos:
                continue
            seen_pos.add(m.start())
            ids = [int(x) for x in re.findall(r'\d+', m.group(1))]
            ctx = text[max(0, m.start()-300):m.end()+300]
            out.append((norm_num(ctx, PACK_KEYS_1, PACK_KEYS_0),
                        norm_num(ctx, PICK_KEYS_1, PICK_KEYS_0), ids, m.start()))
    out.sort(key=lambda x: x[3])
    return out

# Только строка-ЗАПРОС пика игрока (в ней лежит выбранная карта), не ответ/корутина.
PICK_LINE = re.compile(r'==>.*(?:MakePick|MakeHumanDraftPick|PlayerDraftMakePick|HumanDraftPick)', re.I)
# Формат SOS: \"GrpIds\":[102517]  (массив). Плюс запасные одиночные ключи.
PICK_IDS_ARR = re.compile(r'\\?"GrpIds\\?"\s*:\s*\[([\d,\s]+)\]')
PICK_ID_ONE = re.compile(r'\\?"(?:GrpId|CardId|grpId|cardId|PickGrpId)\\?"\s*:\s*\\?"?(\d+)')
PICK_PACK = re.compile(r'\\?"Pack\\?"\s*:\s*(\d+)')
PICK_PICK = re.compile(r'\\?"Pick\\?"\s*:\s*(\d+)')

def find_my_picks(text, draft_id=None):
    """grpId выбранных карт — из pick-запросов текущего draftId, дедуп по (Pack,Pick).
    Дедуп защищает от повторов/авто-пиков при обрыве; склейка логов — от ротации файла."""
    by_coord = {}
    seq = []
    for ln in text.splitlines():
        if not PICK_LINE.search(ln):
            continue
        if draft_id and draft_id not in ln:
            continue
        m = PICK_IDS_ARR.search(ln)
        if m:
            nums = re.findall(r'\d+', m.group(1))
            gid = int(nums[0]) if nums else None
        else:
            m2 = PICK_ID_ONE.search(ln)
            gid = int(m2.group(1)) if m2 else None
        if gid is None:
            continue
        pk, pi = PICK_PACK.search(ln), PICK_PICK.search(ln)
        if pk and pi:
            by_coord[(int(pk.group(1)), int(pi.group(1)))] = gid  # дедуп
        else:
            seq.append(gid)
    return [by_coord[k] for k in sorted(by_coord)] + seq

def pool_summary(picks, by_id, ratings):
    """Текст: список пула, баланс цветов, кривая."""
    if not picks:
        return "  Пул пуст."
    from collections import Counter
    col = Counter(); curve = Counter(); names = []
    for cid in picks:
        c = by_id.get(cid); r = ratings.get(cid)
        nm = (c or {}).get("name") or (r or {}).get("name") or f"id{cid}"
        names.append(nm.split(",")[0].split(" //")[0])
        cl = (c or {}).get("colors")
        if cl is None and "card_faces" in (c or {}):
            cl = c["card_faces"][0].get("colors")
        if cl:
            for x in cl: col[x] += 1
        elif c is not None:
            col["C"] += 1
        cmc = (c or {}).get("cmc")
        tl = face(c, "type_line") if c else ""
        if cmc is not None and "Land" not in tl:
            curve[int(cmc)] += 1
    order = ["W", "U", "B", "R", "G", "C"]
    bal = " ".join(f"{k}:{col[k]}" for k in order if col[k])
    cv = " ".join(f"{k}cmc:{curve[k]}" for k in sorted(curve))
    out = [f"  Пул ({len(picks)}): " + ", ".join(names)]
    out.append(f"  Цвета: {bal or '—'}")
    out.append(f"  Кривая: {cv or '—'}")
    return "\n".join(out)

def full_oracle(c):
    """Полный орактекст карты, включая ОБЕ стороны //-карт (важно для prepared-половинок)."""
    if not c:
        return ""
    if "card_faces" in c:
        parts = []
        for f in c["card_faces"]:
            ot = (f.get("oracle_text", "") or "").replace("\n", " ").strip()
            if ot:
                parts.append(f"[{f.get('name','')} {f.get('mana_cost','')}] {ot}".strip())
        return " // ".join(parts)
    return (c.get("oracle_text", "") or "").replace("\n", " ").strip()

# ─── pool-aware кастуемость / синергия / color-filtered GIH ───────────────────
PIP_RE = re.compile(r'\{([^}]+)\}')
def mana_pips(cost):
    """Цветные требования из строки маны. Гибрид {W/B} -> ('W','B'); {X}/{C}/числа -> игнор."""
    out = []
    for sym in PIP_RE.findall(cost or ""):
        s = sym.upper()
        if s in ("W", "U", "B", "R", "G"):
            out.append((s,))
        elif "/" in s:
            parts = tuple(p for p in s.split("/") if p in ("W", "U", "B", "R", "G"))
            if parts:
                out.append(parts)
    return out

def pool_main_colors(picks, by_id, min_picks=5):
    """Топ-2 цвета пула как set ('W','R'). None пока пул не закоммичен (<min_picks)."""
    if len(picks) < min_picks:
        return None
    from collections import Counter
    col = Counter()
    for cid in picks:
        c = by_id.get(cid)
        cl = (c or {}).get("colors")
        if cl is None and "card_faces" in (c or {}):
            cl = c["card_faces"][0].get("colors")
        if cl:
            for x in cl:
                col[x] += 1
    if not col:
        return None
    return set(k for k, _ in col.most_common(2))

def cast_flag(c, main):
    """' ✗offcolor' / ' ~splash' / '' по кастуемости пипов в цветах main."""
    if not main or not c:
        return ""
    off = 0
    for opt in mana_pips(face(c, "mana_cost")):
        if not any(x in main for x in opt):  # ни один вариант гибрид-пипа не в наших цветах
            off += 1
    if off == 0:
        return ""
    return " ~splash" if off == 1 else " ✗offcolor"

SPELL_PAYOFF_RE = re.compile(
    r'instant or sorcery|whenever you cast (?:a|an|your)|magecraft|opus —|repartee —', re.I)
def pool_spell_count(picks, by_id):
    n = 0
    for cid in picks:
        tl = face(by_id.get(cid), "type_line") if by_id.get(cid) else ""
        if "Instant" in tl or "Sorcery" in tl:
            n += 1
    return n

def synergy_flag(c, spell_n, thresh=6):
    """' ★synergy' если карта — spell-пэйофф и в пуле уже плотность спеллов >= thresh."""
    if not c or spell_n < thresh:
        return ""
    return " ★synergy" if SPELL_PAYOFF_RE.search(full_oracle(c)) else ""

def pair_str(main):
    if not main or len(main) != 2:
        return None
    return "".join(x for x in "WUBRG" if x in main)

def color_ratings(pair):
    """{mtga_id: GIH} для пары цветов pair ('WR'); кеш на диске; {} при ошибке/недоступности."""
    if not pair or len(pair) != 2:
        return {}
    cache = os.path.join(HERE, f"cache_17l_{setcode()}_{pair}.json")
    data = None
    if os.path.exists(cache):
        try:
            data = json.load(open(cache))
        except Exception:
            data = None
    if data is None:
        # Латентный тест / оффлайн: НИКОГДА не блокируемся на сети. Без локального кэша
        # color-filtered GIH просто отсутствует (деградирует тихо, как и при офлайне).
        if os.environ.get("MTGA_OFFLINE"):
            return {}
        import urllib.request
        url = (f"https://www.17lands.com/card_ratings/data?expansion={setcode().upper()}"
               f"&format=PremierDraft&colors={pair}")
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "mtg-draft-helper"})
            data = json.load(urllib.request.urlopen(req, timeout=6))
            json.dump(data, open(cache, "w"))
        except Exception:
            return {}
    out = {}
    for x in data:
        mid = x.get("mtga_id"); g = x.get("ever_drawn_win_rate")
        if mid is not None and g and x.get("ever_drawn_game_count", 0) > 20:
            out[int(mid)] = g
    return out

# ─── детектор сигналов: пивот / разрыв мощности / колесо / soup-audit ─────────
def _colors_of(cid, by_id, ratings):
    """Цвета карты. Из Scryfall если есть, иначе из rating['color'] (покрывает
    архив-карты, которых нет в set-файле)."""
    c = by_id.get(cid)
    if c is not None:
        cols = c.get("colors")
        if cols is None and "card_faces" in c:
            cols = c["card_faces"][0].get("colors")
        return set(cols or [])
    r = ratings.get(cid)
    if r:
        return set(x for x in (r.get("color") or "") if x in "WUBRG")
    return set()

def _gih_of(cid, ratings):
    r = ratings.get(cid)
    return round(r["ever_drawn_win_rate"] * 100, 1) if r else None

def _name_of(cid, by_id, ratings):
    nm = (by_id.get(cid) or {}).get("name") or (ratings.get(cid) or {}).get("name") or f"id{cid}"
    return nm.split(" //")[0]

FIX_RE = re.compile(r"add one mana of any|search your library for a basic land|"
                    r"create a treasure|mana of any (one )?color|any combination of colors",
                    re.I)
def _is_fixer(cid, by_id, ratings):
    c = by_id.get(cid)
    if c is None:
        return False
    tl = face(c, "type_line") or ""
    if "Land" in tl and "Basic" not in tl:
        return True
    return bool(FIX_RE.search(full_oracle(c)))

def fixing_count(picks, by_id, ratings):
    return sum(1 for cid in picks if _is_fixer(cid, by_id, ratings))

HIST_PATH = os.path.join(HERE, ".draft_hist.json")
def _load_hist():
    try:
        return json.load(open(HIST_PATH))
    except Exception:
        return {}
def _record_hist(draft_id, pnum, pick, ids):
    if not draft_id or pnum is None or pick is None:
        return
    h = _load_hist()
    h.setdefault(draft_id, {})[f"{pnum}-{pick}"] = list(ids)
    try:
        json.dump(h, open(HIST_PATH, "w"))
    except Exception:
        pass

def draft_signals(ids, by_id, ratings, main, pnum, pick, picks, draft_id):
    """Список баннеров-предупреждений (пивот/сплеш/колесо/audit). Печатаются ПЕРЕД паком."""
    out = []
    main = set(main or [])
    def offcolor(cid):
        cols = _colors_of(cid, by_id, ratings)
        return bool(cols and (cols - main))
    if len(main) >= 2:
        ins = [_gih_of(c, ratings) for c in ids if not offcolor(c) and _gih_of(c, ratings) is not None]
        off = [(c, _gih_of(c, ratings)) for c in ids if offcolor(c) and _gih_of(c, ratings) is not None]
        best_in = max(ins) if ins else None
        # (2) разрыв мощности — только на ранних/средних пиках, где решение о пивоте/сплеше
        # реально (после ~9 пика берёшь лучшую карту и так).
        if off and pick <= 9:
            cid_b, g_b = max(off, key=lambda x: x[1])
            if best_in is not None and g_b - best_in >= 3:
                cs = "".join(x for x in "WUBRG" if x in _colors_of(cid_b, by_id, ratings))
                out.append(f"⚑ СИЛЬНЕЕ ВНЕ ЦВЕТА: {_name_of(cid_b, by_id, ratings)} [{cs}] GIH {g_b} "
                           f"— на +{round(g_b - best_in, 1)} выше лучшей в-цвете ({best_in}). Взвесь сплеш/пивот.")
        # (1a) плотность сильных вне цвета на поздних пиках = цвет открыт
        strong = [(c, g) for c, g in off if g >= 56]
        if 6 <= pick <= 10 and strong and (len(strong) >= 2 or any(g >= 58 for _, g in strong)):
            from collections import Counter
            cc = Counter()
            for c, g in strong:
                for x in _colors_of(c, by_id, ratings) - main:
                    cc[x] += 1
            colstr = " ".join(f"{k}×{v}" for k, v in cc.most_common())
            nm = ", ".join(f"{_name_of(c, by_id, ratings)} {g}"
                           for c, g in sorted(strong, key=lambda x: -x[1])[:3])
            out.append(f"⚑ ПИВОТ? пик {pick}: текут сильные вне цвета ({colstr}) — {nm}. Цвет открыт слева.")
    # (1b) колесо — тот же физический пак возвращается через один круг (под=8): пик P
    # есть подмножество пака с пика P-8. Сообщаем, только если вернулась СИЛЬНАЯ карта
    # (GIH>=54) — значит её цвет открыт (соседи слева её не берут).
    POD = 8
    prev_pack = _load_hist().get(draft_id or "", {}).get(f"{pnum}-{pick - POD}")
    if prev_pack:
        wheeled = set(ids) & set(prev_pack)
        cand = [(c, _gih_of(c, ratings)) for c in wheeled if (_gih_of(c, ratings) or 0) >= 54]
        if cand:
            cid_w, g_w = max(cand, key=lambda x: x[1])
            cs = "".join(x for x in "WUBRG" if x in _colors_of(cid_w, by_id, ratings)) or "C"
            out.append(f"⚑ КОЛЕСО: {_name_of(cid_w, by_id, ratings)} [{cs}] GIH {g_w} вернулась по кругу "
                       f"(пик {pick}) — её цвет открыт, греби туда.")
    # (4) soup-audit на пике ~5 первого пака
    if pnum == 1 and pick in (5, 6):
        fx = fixing_count(picks, by_id, ratings)
        if fx >= 3:
            out.append(f"⚑ SOUP-AUDIT (пик {pick}): фикс={fx} — достаточно. Бери лучшую карту ЛЮБОГО "
                       f"цвета, соус/сплеши открыты.")
        else:
            out.append(f"⚑ SOUP-AUDIT (пик {pick}): фикс={fx} — мало. Держись 2 цветов; "
                       f"сплеш только при 3+ источниках (Rule of Three).")
    return out

def pack_sig(text):
    """Дешёвая подпись текущего пака (только regex, без карт/рейтингов/сети) — для wake-режима.
    Возвращает (sig, pnum, pick, ncards) или (None, None, None, None), если пака нет."""
    packs = find_packs(text)
    if not packs:
        return None, None, None, None
    pnum, pick, ids, _ = packs[-1]
    return f"{pnum}-{pick}-{len(ids)}-{sum(ids)}", pnum, pick, len(ids)

def current_block(text, by_id, ratings, draft_id):
    """Возвращает (sig, текст-блок) текущего пака: подпись для детекта изменений +
    кандидаты по убыванию GIH WR с тиром, и сводку пула. sig=None если пака нет."""
    packs = find_packs(text)
    if not packs:
        return None, "NOPACK"
    pnum, pick, ids, _ = packs[-1]
    sig = f"{pnum}-{pick}-{len(ids)}-{sum(ids)}"

    def gw(cid):
        r = ratings.get(cid)
        return r["ever_drawn_win_rate"] if r else -1
    order = sorted(ids, key=gw, reverse=True)
    # контекст пула: цвета (кастуемость), плотность спеллов (синергия), color-filtered GIH
    picks = find_my_picks(text, draft_id)
    main = pool_main_colors(picks, by_id)
    pair = pair_str(main)
    cratings = color_ratings(pair) if pair else {}
    spell_n = pool_spell_count(picks, by_id)
    _record_hist(draft_id, pnum, pick, ids)
    lines = []
    sigs = draft_signals(ids, by_id, ratings, main, pnum, pick, picks, draft_id)
    if sigs:
        lines.append("─── СИГНАЛЫ ───")
        lines += sigs
        lines.append("───────────────")
    lines.append(f"PACK {pnum}/{pick} — {len(ids)} карт")
    for cid in order:
        c = by_id.get(cid)
        r = ratings.get(cid)
        if r:
            tag = stat_tag(r, cratings.get(cid), pair if cid in cratings else None)
        else:
            tag = "[нет данных]"
        flags = cast_flag(c, main) + synergy_flag(c, spell_n)
        nm = (c or {}).get("name") or (r or {}).get("name") or f"id{cid}"
        cost = face(c, "mana_cost") if c else ""
        tl = face(c, "type_line") if c else (r or {}).get("types", "")
        pt = f" {c['power']}/{c['toughness']}" if c and c.get("power") is not None else ""
        lines.append(f"  {tag}{flags} {nm} {cost}{pt} — {tl}")
        ot = full_oracle(c)
        if ot:
            if len(ot) > 280:
                ot = ot[:279] + "…"
            lines.append(f"        {ot}")
    lines.append("POOL:")
    lines.append(pool_summary(picks, by_id, ratings))
    return sig, "\n".join(lines)

def watch(mode="full"):
    """Блокируется, поллит лог раз в 0.2с. Как только появляется НОВЫЙ пак (другая
    координата/состав) — выходит (exit 0). Если за 25 мин ничего нового — печатает WAITING.
    Состояние (последняя показанная подпись) в .draft_watch.json; `fresh` сбрасывает его.

    mode="full" — печатает полный проанализированный блок пака (старое поведение).
    mode="wake" — БУДИЛЬНИК: печатает одну строку-маркер `WAKE пак/пик — N карт` и выходит,
                  НЕ грузя карты/рейтинги/сеть. Ассистент сам перечитывает пак снапшотом
                  `draft_live.py <set>` в момент совета (свежий пак, без лага от его задержки)."""
    import time
    state_path = os.path.join(HERE, ".draft_watch.json")
    # Debounce: при детекте нового пака не возвращаемся мгновенно, а ждём SETTLE секунд
    # «тишины». Если за это время появился ещё более новый пак (юзер быстро пикает пак-за-
    # паком) — следуем к нему и сбрасываем таймер. Возвращаем ТОЛЬКО последний устоявшийся
    # пак → ассистент никогда не советует пик, который юзер уже пролистал. 0 = выключить.
    SETTLE = float(os.environ.get("MTGA_SETTLE", "1.0"))
    last_sig = None
    if "fresh" in sys.argv[1:]:
        for p in (state_path, HIST_PATH):
            try:
                os.remove(p)
            except OSError:
                pass
    elif os.path.exists(state_path):
        try:
            last_sig = json.load(open(state_path)).get("sig")
        except Exception:
            last_sig = None
    # wake-режим — чистый детектор: карты/рейтинги/сеть не нужны (это делает снапшот).
    by_id = ratings = None
    if mode == "full":
        by_id = load_cards()    # карты и рейтинги за драфт не меняются — грузим один раз
        ratings = load_ratings()
    # Baseline: длина лога на момент старта вотчера. Завершение ПРОШЛОГО драфта (DeckBuilder/
    # Complete от уже закрытого ивента) висит в логе ДО этой точки — его игнорируем, иначе
    # вотчер мгновенно выскакивает «DRAFT COMPLETE» и не дожидается нового драфта. Только
    # завершение, появившееся ПОСЛЕ baseline (>= start_len), относится к текущему драфту.
    start_len = len(read_log_text())
    # Блокируемся до РЕАЛЬНО нового пака (а не таймаутим каждые ~2 мин и будим зря на тот же
    # пак). 25 мин — потолок на случай, если игрок отошёл; выход мгновенный при появлении пака.
    deadline = time.time() + 1500
    while time.time() < deadline:
        text = read_log_text()
        # Завершение драфта: DraftCompleteDraft / переход в DeckBuilder ПОСЛЕ последнего пака
        # И появившееся после старта вотчера (>= start_len) — иначе это старый, закрытый драфт.
        done_pos = max(text.rfind("DraftCompleteDraft"),
                       text.rfind('"toSceneName":"DeckBuilder"'))
        pack_pos = max(text.rfind("Draft.Notify"), text.rfind("PackCards"),
                       text.rfind("DraftPack"))
        if done_pos != -1 and done_pos > pack_pos and done_pos >= start_len:
            print("DRAFT COMPLETE — драфт окончен, переходи к сборке колоды.")
            return
        if mode == "wake":
            sig, pnum, pick, ncards = pack_sig(text)
            if sig and sig != last_sig:
                if pick >= 12:
                    last_sig = sig
                    json.dump({"sig": sig, "set": setcode()}, open(state_path, "w"))
                else:
                    ts = time.strftime("%H:%M:%S") + f".{int((time.time()%1)*1000):03d}"
                    print(f"WAKE [{ts}] {pnum}/{pick} — {ncards} карт. Перечитай текущий пак: "
                          f"python3 {os.path.basename(__file__)} {setcode()}")
                    json.dump({"sig": sig, "set": setcode()}, open(state_path, "w"))
                    return
        else:
            sig, pnum, pick, ncards = pack_sig(text)  # дешёвый детект (без карт/блока)
            if sig and sig != last_sig:
                # debounce: следуем за быстрыми пиками к самому свежему паку, блок считаем
                # ОДИН раз — по устоявшемуся последнему (промежуточные пропускаем целиком).
                if SETTLE > 0:
                    stable_since = time.time()
                    while time.time() - stable_since < SETTLE:
                        time.sleep(0.15)
                        t2 = read_log_text()
                        s2, _, _, _ = pack_sig(t2)
                        if s2 and s2 != sig:
                            sig, text = s2, t2
                            stable_since = time.time()
                # Финальный ре-рид: пак мог смениться, пока крутился debounce/рендер (или юзер
                # успел подать ещё next). Всегда печатаем АБСОЛЮТНО последний пак в логе, чтобы
                # никогда не отставать на пик. Пересчитываем и sig из этого же свежего text.
                text = read_log_text()
                sig, _, _, _ = pack_sig(text)
                draft_id = current_draft_id(text)
                _, block = current_block(text, by_id, ratings, draft_id)
                print(block)
                json.dump({"sig": sig, "set": setcode()}, open(state_path, "w"))
                return
        time.sleep(0.2)
    print("WAITING")

def main():
    if "wake" in sys.argv[1:]:
        return watch(mode="wake")
    if "watch" in sys.argv[1:]:
        return watch()
    text = read_log_text()
    if not text:
        print("Нет логов Arena — Arena запускалась? (ищу Player.log / Player-prev.log)")
        return
    draft_id = current_draft_id(text)
    by_id = load_cards()

    if "raw" in sys.argv[1:]:
        # печатаем строки, где встречаются draft-ключи — чтобы увидеть реальный формат
        hits = [ln for ln in text.splitlines()
                if any(k in ln for k in ["Draft", "PackCards", "DraftPack", "PickGrpId", "draftId", "MakePick"])]
        picks = [ln for ln in text.splitlines() if PICK_LINE.search(ln)]
        print(f"draft-подобных строк: {len(hits)} | pick-строк: {len(picks)}\n")
        print("--- последние pick-строки (для проверки формата трекинга) ---")
        for ln in picks[-6:]:
            print(ln[:400])
        print("\n--- последние draft-строки ---")
        for ln in hits[-20:]:
            print(ln[:400])
        return

    packs = find_packs(text)
    if not packs:
        print("Паков в логе не нашёл. Проверь:")
        print(" 1) Settings -> Account -> Detailed Logs (Plugin Support) включены")
        print(" 2) Arena перезапущена ПОСЛЕ включения")
        print(" 3) Драфт реально открыт и виден первый пак")
        print("\nЗапусти `python3 draft_live.py raw` и пришли вывод — подстрою парсер.")
        return

    ratings = load_ratings()
    pnum, pick, ids, _ = packs[-1]
    # Снапшот — авторитетный источник «что я уже видел»: пишем подпись текущего пака, чтобы
    # следующий `wake` не сработал повторно на пак, который я только что оценил (анти-лаг).
    try:
        sig = f"{pnum}-{pick}-{len(ids)}-{sum(ids)}"
        json.dump({"sig": sig, "set": setcode()},
                  open(os.path.join(HERE, ".draft_watch.json"), "w"))
    except Exception:
        pass
    label = ""
    if pnum is not None:
        label = f"  (Бустер {pnum}, пик {pick})"
    print(f"\n===== ТЕКУЩИЙ ПАК [{setcode().upper()}]{label} — {len(ids)} карт =====\n")
    # сортируем по GIH WR, чтобы лучший пик был сверху
    def gw(cid):
        r = ratings.get(cid)
        return r["ever_drawn_win_rate"] if r else -1
    order = sorted(ids, key=gw, reverse=True)
    # контекст пула: цвета / спелл-плотность / color-filtered GIH
    picks = find_my_picks(text, draft_id)
    main = pool_main_colors(picks, by_id)
    pair = pair_str(main)
    cratings = color_ratings(pair) if pair else {}
    spell_n = pool_spell_count(picks, by_id)
    _record_hist(draft_id, pnum, pick, ids)
    for s in draft_signals(ids, by_id, ratings, main, pnum, pick, picks, draft_id):
        print("  " + s)
    if main:
        print()
    unknown = []
    for cid in order:
        c = by_id.get(cid)
        r = ratings.get(cid)
        tag = ""
        if r:
            tag = stat_tag(r, cratings.get(cid), pair if cid in cratings else None) + " "
        else:
            tag = "[нет данных] "
        flags = (cast_flag(c, main) + synergy_flag(c, spell_n)).strip()
        flags = (" " + flags) if flags else ""
        if c:
            print(f"  {tag}{short(c)}{flags}")
        elif r:
            # карты нет в Scryfall-мапе, но 17Lands знает имя/тип — показываем хоть это
            print(f"  {tag}{r.get('name','?')} — {r.get('types','?')} ({r.get('color') or 'C'}/{r.get('rarity','?')[0].upper()})")
        else:
            unknown.append(cid)
            print(f"  {tag}<id {cid} — нет ни в {setcode()}_set.json, ни в рейтингах>")
    if unknown:
        print(f"\n  ⚠ неизвестных id: {len(unknown)} — возможно, не тот сет или мап неполный")
    print("\n----- ПУЛ -----")
    if draft_id:
        print(f"  (draftId {draft_id[:8]}…)")
    print(pool_summary(picks, by_id, ratings))

if __name__ == "__main__":
    main()
