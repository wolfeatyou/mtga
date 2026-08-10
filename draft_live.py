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

def _norm_name(s):
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def load_pick_tiers():
    """name -> тир пика по untapped.gg (DIAMOND_TO_MYTHIC). Это ДРУГАЯ ось, чем GIH:
    как сильные драфтеры карту РЕАЛЬНО берут, а не какой у неё винрейт.
    Измерено на 196 картах (10.08.2026): ρ(тир,GIH)=+0.79, но при РАВНОМ GIH решает IWD —
    ρ(тир,IWD) внутри полосы 59-61 = +0.58, внутри 61-64 = +0.66. Поэтому тир печатается
    рядом с GIH: расхождение между ними и есть содержательная часть пика."""
    f = os.path.join(HERE, f"{setcode()}_pick_tiers.json")
    if not os.path.exists(f):
        return {}
    out = {}
    for tier, names in json.load(open(f)).items():
        if tier.startswith("_"):
            continue
        for n in names:
            out[_norm_name(n)] = tier
            out[_norm_name(n.split(",")[0])] = tier
    return out


PICK_TIERS = None


def pick_tier(name):
    global PICK_TIERS
    if PICK_TIERS is None:
        PICK_TIERS = load_pick_tiers()
    return PICK_TIERS.get(_norm_name(name)) or PICK_TIERS.get(_norm_name((name or "").split(",")[0]))


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
    pt = pick_tier(r.get("name"))
    if pt:
        parts.append(f"пик {pt}")     # как берут в Diamond→Mythic (untapped), ось ≠ GIH
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

POOL_DIR = os.path.join(HERE, "pools")


def save_pool(picks, by_id, ratings, draft_id):
    """Автосохранение ПОЛНОГО пула в MTGA-формат при каждом пике.

    Зачем автоматически, а не руками: пул физически живёт только в Player.log, а он
    **ротируется быстро** (задокументировано в § Mode 2) — после ротации остаток пула
    восстановить неоткуда, и тест «мейн ≠ жадный топ-23» (§ КАЛИБРОВКА) провести уже
    нельзя. Файл переписывается каждый пик, так что обрыв в любой момент не теряет ничего.

    Все карты кладём в Sideboard: на момент драфта мейд ещё не выбран. На сборке
    build_audit.py --pool сам вычтет мейн из пула.
    """
    if not picks:
        return None
    try:
        os.makedirs(POOL_DIR, exist_ok=True)
        tag = (draft_id or "nodraftid")[:8]
        path = os.path.join(POOL_DIR, f"{setcode()}_{tag}.txt")
        from collections import Counter
        cnt = Counter()
        for cid in picks:
            c = by_id.get(cid)
            nm = (c or {}).get("name") or (ratings.get(cid) or {}).get("name")
            if nm:
                cnt[nm.split(" //")[0]] += 1
        lines = ["Deck", "", "Sideboard"] + [f"{n} {nm}" for nm, n in sorted(cnt.items())]
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        return path
    except Exception:
        return None       # автосохранение никогда не должно ронять живой драфт


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

# ─── КРИВАЯ: счётчик дешёвых тел (операционализация порога 3) ─────────────────
# Обоснование (msh_match_log, 10 завершённых прогонов): голдфиш-метрика «существо к T2» —
# единственное, что разделило прогоны. ≥69% → 16W-8L (66.7%); ≤56% → 2W-9L (18.2%).
# Метрика почти ступенчато определяется числом существ cmc≤2: 4 шт ≈ 55%, 5 шт ≈ 64-65%.
# На сборке не чинится (взять неоткуда) → должна набираться НА ПИКЕ, значит счётчик
# обязан печататься КАЖДЫЙ пик. Прошлая версия правила была текстом в SKILL.md и
# не сработала ни разу — ничто не заставляло на неё посмотреть.
PICKS_PER_PACK = 14
CHEAP_TARGET = {1: 2, 2: 4, 3: 5}   # сколько существ cmc≤2 надо иметь к КОНЦУ пака n

def _is_cheap_body(cid, by_id):
    c = by_id.get(cid)
    if not c:
        return False
    tl = face(c, "type_line") or ""
    if "Creature" not in tl:
        return False
    # {X}-костные существа: Scryfall считает X=0, поэтому The Ruinous Wrecking Crew {X}{B}{R}
    # приходит как cmc=2.0. Это НЕ двойка — за X=0 это 0/0. В квоту кривой не идёт.
    # (поймано 10.08.2026 на diamond-листе Grixis Skies)
    if "{X}" in (face(c, "mana_cost") or ""):
        return False
    cmc = c.get("cmc")
    return cmc is not None and cmc <= 2

def cheap_bodies(picks, by_id, ratings, main):
    """Имена существ cmc≤2 в пуле, КАСТУЕМЫХ в текущих цветах (main=None → все)."""
    out = []
    for cid in picks:
        if not _is_cheap_body(cid, by_id):
            continue
        if main and (_colors_of(cid, by_id, ratings) - set(main)):
            continue
        out.append(_name_of(cid, by_id, ratings))
    return out

def curve_banner(ids, by_id, ratings, main, pnum, pick, picks):
    """Всегда-печатаемая строка про кривую + кандидаты в ЭТОМ паке, если отстаём."""
    have = cheap_bodies(picks, by_id, ratings, main)
    n = len(have)
    prev = CHEAP_TARGET.get((pnum or 1) - 1, 0)
    tgt = CHEAP_TARGET.get(pnum or 1, 5)
    need_now = int(prev + (tgt - prev) * min(pick or 1, PICKS_PER_PACK) / PICKS_PER_PACK)
    fin = CHEAP_TARGET[3]
    if n >= need_now:
        mark = "✓" if n >= fin else "в графике"
        return [f"⚑ КРИВАЯ: существ cmc≤2 — {n} · чекпойнт {need_now} · финал ≥{fin} — {mark}"]
    cand = [(c, _gih_of(c, ratings)) for c in ids
            if _is_cheap_body(c, by_id) and not (main and (_colors_of(c, by_id, ratings) - set(main)))]
    cand = [x for x in cand if x[1] is not None]
    cand.sort(key=lambda x: -x[1])
    out = [f"⚑ КРИВАЯ — НЕДОБОР: существ cmc≤2 — {n}, к этому пику надо {need_now} "
           f"(финал ≥{fin}). Не хватает {need_now - n}."]
    if cand:
        s = " · ".join(f"{_name_of(c, by_id, ratings)} GIH {g}" for c, g in cand[:3])
        out.append(f"   дешёвые тела в цвете ЗДЕСЬ: {s}")
        out.append("   ПРАВИЛО: берём дешёвое тело. Обходится ТОЛЬКО бомбой (GIH ≥63) или "
                   "безусловным removal — не «картой повыше GIH».")
    else:
        out.append("   дешёвых тел в цвете в этом паке НЕТ — добираем в следующем, приоритет держим.")
    return out

# ─── ПЛАН: кластер воздух/земля (константы из ref_decks, n=23) ────────────────
# Флаеры бимодальны: 12 колод с ≤3, 9 с ≥6, всего 2 в середине.
# REACH — почти идеальный разделитель: из 9 воздушных reach≥2 нет НИ У ОДНОЙ;
# из 12 наземных 8 держат reach≥3. Это камень-ножницы, а не разница в силе карт.
# Константы зашиты намеренно: читать ref_decks/ в пик-цикле = лишняя латентность.
AIR_FLY, AIR_REACH_MAX = 6, 1        # воздух: флай 6–10, reach 0–1
GND_FLY_MAX, GND_REACH = 3, 3        # земля:  флай 0–3, reach медиана 3
TOTAL_PICKS = 42
REF = dict(creatures=(13, 15, 18), cheap=(1, 5, 8), hard=(0, 1, 5),
           c5=(0, 3, 5), fixers=(0, 4, 10))   # (min, медиана, max) по 23 листам

_FLY_RE = re.compile(r"\bflying\b", re.I)
_REACH_RE = re.compile(r"\breach\b", re.I)


def _pool_roles(picks, by_id, ratings, main):
    """Счётчики ролей по КАСТУЕМОЙ части пула."""
    r = {"fly": 0, "reach": 0, "creatures": 0, "cheap": 0, "c5": 0, "fixers": 0, "n": 0}
    for cid in picks:
        c = by_id.get(cid)
        if not c:
            continue
        tl = face(c, "type_line") or ""
        if "Land" in tl:
            if "Basic" not in tl:
                r["fixers"] += 1
            continue
        if main and (_colors_of(cid, by_id, ratings) - set(main)):
            continue
        r["n"] += 1
        txt = full_oracle(c) + " " + tl
        if _FLY_RE.search(txt):
            r["fly"] += 1
        if _REACH_RE.search(txt):
            r["reach"] += 1
        cmc = c.get("cmc") or 0
        if "Creature" in tl:
            r["creatures"] += 1
            if cmc <= 2 and "{X}" not in (face(c, "mana_cost") or ""):
                r["cheap"] += 1
        if cmc >= 5:
            r["c5"] += 1
    return r


# ─── ОСЬ / АРХЕТИП: лейн называется механикой сета, а не статистикой ──────────
# Внесено 11.08.2026. До этого ⚑ПЛАН делил колоды на воздух/землю — это ось
# «чем ломаю стойку», выведенная из 23 победителей, и она измеряет НЕ архетип.
# Архетипов в MSH десять (msh_cheat.md), плюс сквозные механики. Лейн обязан
# называться ими: «UB connive/Villains», а не «воздух».
ARCH = None


def load_arch():
    global ARCH
    if ARCH is None:
        f = os.path.join(HERE, f"{setcode()}_archetypes.json")
        ARCH = json.load(open(f)) if os.path.exists(f) else {"axes": {}, "pairs": {}}
    return ARCH


def _axes_of(cid, by_id):
    """Какие оси сета трогает карта."""
    c = by_id.get(cid)
    if not c:
        return []
    tl = face(c, "type_line") or ""
    ot = full_oracle(c) or ""
    out = []
    for name, spec in load_arch().get("axes", {}).items():
        if "type" in spec and spec["type"] in tl:
            out.append(name)
        elif "re" in spec and re.search(spec["re"], ot, re.I):
            out.append(name)
    return out


def axis_banner(ids, by_id, ratings, main, picks):
    """Ось пула + что её кормит в ЭТОМ паке. Заменяет «архетип» в баннере ПЛАН."""
    from collections import Counter
    cnt = Counter()
    for cid in picks:
        for a in _axes_of(cid, by_id):
            cnt[a] += 1
    if not cnt:
        return []
    pair = pair_str(main) if main else None
    # ключ пары ищем в ЛЮБОМ порядке букв: pair_str даёт WUBRG-порядок, а в JSON
    # пары могли быть записаны иначе. Зависеть от написания нельзя.
    pairs = load_arch().get("pairs", {})
    arch = None
    if pair:
        for k, v in pairs.items():
            if sorted(k) == sorted(pair):
                arch, pair = v, k if False else pair
                break
    out = []
    top = " · ".join(f"{a} {n}" for a, n in cnt.most_common(5))
    if arch:
        want = arch["axes"]
        have = {a: cnt.get(a, 0) for a in want}
        thin = [a for a, n in have.items() if n <= 1]
        out.append(f"⚑ ОСЬ: {pair} = {arch['name']} · нужно [{', '.join(want)}] → "
                   + " · ".join(f"{a} {n}" for a, n in have.items()))
        if thin:
            out.append(f"   ⚠ ТОНКО: {', '.join(thin)} — либо добирать детали оси, "
                       f"либо честно признать goodstuff и не притворяться архетипом")
        # что в паке кормит ось
        feed = []
        for cid in ids:
            if main and (_colors_of(cid, by_id, ratings) - set(main)):
                continue
            hit = [a for a in _axes_of(cid, by_id) if a in want]
            if hit:
                feed.append(f"{_name_of(cid, by_id, ratings)} ({'+'.join(hit)})")
        if feed:
            out.append("   кормят ось ЗДЕСЬ: " + " · ".join(feed[:4]))
    else:
        out.append(f"⚑ ОСЬ: пара не закоммичена · оси пула: {top}")
    return out


def plan_banner(picks, by_id, ratings, main, pnum, pick):
    """ЧЕМ ЛОМАЮ СТОЙКУ (воздух/земля) — это НЕ архетип, архетип печатает axis_banner."""
    done = (pnum - 1) * 14 + pick if pnum else pick
    r = _pool_roles(picks, by_id, ratings, main)
    if done < 10:
        return [f"⚑ СТОЙКА: рано (пик {done}/{TOTAL_PICKS}) — флай {r['fly']}, reach {r['reach']}"]
    scale = TOTAL_PICKS / max(done, 1)
    pf, pr = r["fly"] * scale, r["reach"] * scale      # проекция на конец драфта
    # одна десятая, а не целое: округление 5.8→«6» рядом с вердиктом «не определился»
    # (порог воздуха ровно 6) читается как противоречие
    head = f"⚑ СТОЙКА: флай {r['fly']} · reach {r['reach']} (пик {done}/{TOTAL_PICKS} → к финалу ~{pf:.1f}/{pr:.1f})"
    out = []
    if pf >= AIR_FLY:
        out.append(head + " = 🟦 ВОЗДУХ")
        if r["reach"] >= 2:
            out.append(f"   ⚠ КОНФЛИКТ: reach {r['reach']} при воздушном плане — из 9 воздушных "
                       f"победителей reach≥2 НЕ ДЕРЖИТ НИ ОДНА. Рич больше не брать.")
        else:
            out.append("   норма кластера (n=9): флай 6–10, reach 0–1. Рич не брать вообще, добирать флаеров.")
    elif pf <= GND_FLY_MAX:
        out.append(head + " = 🟫 ЗЕМЛЯ")
        if pr < 2:
            out.append(f"   ⚠ REACH МАЛО: у 8 из 12 наземных победителей reach≥3 — иначе воздушный "
                       f"кластер (9 из 23 колод) обыгрывает автоматически. Рич сейчас = приоритетная роль.")
        else:
            out.append("   норма кластера (n=12): флай 0–3, reach медиана 3. Держим рич, флаеров не ищем.")
    else:
        out.append(head + " = ⬜ НЕ ОПРЕДЕЛИЛСЯ")
        out.append("   в зоне 4–5 флаеров всего 2 победителя из 23 (там же наша трофейка — это не "
                   "брак, но и не план). Решай: добирать флаеров до 6 ИЛИ рич до 3.")
    return out


def profile_banner(picks, by_id, ratings, main, pnum, pick):
    """Профиль пула против диапазонов 23 победителей. Только на границе бустера.

    ВАЖНО: диапазоны REF — это ФИНАЛЬНЫЕ колоды (23 карты). Пул на середине драфта
    меньше по определению, поэтому сравнивать в лоб нельзя — иначе на P2P1 всегда
    «существ мало». Сравниваем ТЕМП: сколько должно быть к этому пику.
    """
    done = (pnum - 1) * 14 + pick
    frac = min(done / TOTAL_PICKS, 1.0)
    r = _pool_roles(picks, by_id, ratings, main)
    parts = []
    for key, lab in (("creatures", "существ"), ("cheap", "cmc≤2"),
                     ("c5", "cmc≥5"), ("fixers", "фикс")):
        lo, med, hi = REF[key]
        elo, ehi = lo * frac, hi * frac
        v = r[key]
        mark = "↑" if v > ehi else ("!" if v < elo else "")
        parts.append(f"{lab} {v}{mark}/{med * frac:.0f}")
    return [f"⚑ ПРОФИЛЬ (пик {done}/{TOTAL_PICKS}, темп к медиане 23 победителей): "
            + " · ".join(parts),
            "   формат «моё/ожидаемо-к-этому-пику». ! = ниже темпа минимума, ↑ = выше максимума. "
            "Это диапазоны, а не пороги."]


# ─── ТАЙБРЕЙК: когда GIH-сортировка ставит наверх НЕ ту карту ─────────────────
# Док. случай (Quick MSH, 10.08.2026, P1P2): Take Up the Shield GIH 59.9 / IWD +3.0 /
# пик C+ против Super-Skrull GIH 59.9 / IWD +8.6 / пик B, 4/5 flying. GIH совпал до
# десятой, советчик взял верхнюю строку списка. Измерено (n=196): при GIH в пределах
# ~1 тир пика определяется IWD — ро=+0.58 в полосе 59-61, +0.66 в 61-64.
# Правило текстом в SKILL.md уже стояло («floor vs ceiling») и не сработало ни разу:
# сортировка по GIH сильнее любой прозы. Поэтому — баннером.
GIH_TIE = 1.5        # в пределах этого GIH считаем «равным»
IWD_GAP = 2.0        # разница IWD, с которой она решает
TIER_GAP = 2         # ступеней пик-тира, с которых он решает
_TIER_ORDER = ["S", "A+", "A", "A-", "B+", "B", "B-", "C+", "C", "C-", "D+", "D"]


def _tier_idx(name):
    t = pick_tier(name)
    return _TIER_ORDER.index(t) if t in _TIER_ORDER else None


def tiebreak_banner(ids, by_id, ratings, main):
    """Молчит, пока верх по GIH и верх по тайбрейку — одна карта. Говорит, когда разошлись."""
    cand = []
    for cid in ids:
        r = ratings.get(cid)
        if not r or r.get("ever_drawn_win_rate") is None:
            continue
        if main and (_colors_of(cid, by_id, ratings) - set(main)):
            continue                       # некастуемые в тайбрейке не участвуют
        nm = _name_of(cid, by_id, ratings)
        cand.append(dict(name=nm, gih=round(r["ever_drawn_win_rate"] * 100, 1),
                         iwd=round((r.get("drawn_improvement_win_rate") or 0) * 100, 1),
                         tier=pick_tier(nm), ti=_tier_idx(nm)))
    if len(cand) < 2:
        return []
    top = max(cand, key=lambda x: x["gih"])
    near = [c for c in cand if top["gih"] - c["gih"] <= GIH_TIE]
    if len(near) < 2:
        return []
    by_iwd = max(near, key=lambda x: x["iwd"])
    tiered = [c for c in near if c["ti"] is not None]
    by_tier = min(tiered, key=lambda x: x["ti"]) if tiered else None

    reasons = []
    if by_iwd["name"] != top["name"] and by_iwd["iwd"] - top["iwd"] >= IWD_GAP:
        reasons.append(f"IWD {top['iwd']:+.1f} → {by_iwd['iwd']:+.1f}")
    if (by_tier and by_tier["name"] != top["name"] and top["ti"] is not None
            and top["ti"] - by_tier["ti"] >= TIER_GAP):
        reasons.append(f"пик-тир {top['tier']} → {by_tier['tier']}")
    if not reasons:
        return []
    win = by_iwd if by_iwd["name"] != top["name"] else by_tier
    return [f"⚑ ТАЙБРЕЙК: сверху по GIH {top['name']} ({top['gih']}), но в пределах "
            f"{GIH_TIE} GIH есть {win['name']} ({win['gih']}) — и он лучше по: "
            + " · ".join(reasons),
            "   GIH тут не решает (разница в шуме). Берёшь верхнюю строку — назови ПОЧЕМУ "
            "именно её, а не «она выше по GIH»."]


def draft_signals(ids, by_id, ratings, main, pnum, pick, picks, draft_id):
    """Список баннеров-предупреждений (кривая/план/пивот/сплеш/колесо/audit). Печатаются ПЕРЕД паком."""
    out = curve_banner(ids, by_id, ratings, main, pnum, pick, picks)
    out += tiebreak_banner(ids, by_id, ratings, main)
    out += axis_banner(ids, by_id, ratings, main, picks)
    out += plan_banner(picks, by_id, ratings, main, pnum or 1, pick or 1)
    if (pnum or 1) > 1 and (pick or 1) == 1:
        out += profile_banner(picks, by_id, ratings, main, pnum or 1, pick or 1)
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

def render_block(pnum, pick, ids, picks, by_id, ratings, draft_id, header=None):
    """ЕДИНЫЙ рендер пака+пула для ВСЕХ режимов драфта.

    Парсеры лога у Premier и Quick разные (PackCards vs BotDraftDraftStatus) — а вот
    анализ обязан быть один. Пока рендеры были раздельные, они разъехались молча:
    у Quick были СВОИ пороги тира (S≥60 против A≥60), не было пар-GIH, флагов
    ~splash/✗offcolor/★synergy, ⚠trap и баннеров. Одна и та же карта показывалась
    разными буквами в двух режимах. Дублировать этот код нельзя — только вызывать.
    """
    def gw(cid):
        r = ratings.get(cid)
        return r["ever_drawn_win_rate"] if r else -1
    order = sorted(ids, key=gw, reverse=True)
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
    lines.append(header or f"PACK {pnum}/{pick} — {len(ids)} карт")
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
    # Карты, которых нет в <set>_set.json, МОЛЧА выпадали из всех счётчиков (кривая,
    # существа, цвета, ПЛАН, ПРОФИЛЬ) — то есть баннеры врали на их число, не сообщая
    # об этом. Поймано 11.08.2026 живым драфтом: id105262 (артефакт с симметричным
    # добором) и id105178 в пуле. Сами данные добрать нельзя, но врать молча нельзя тем более.
    unk_pool = [c for c in picks if c not in by_id]
    unk_pack = [c for c in ids if c not in by_id]
    if unk_pool or unk_pack:
        lines.append(f"  ⚠ НЕ РАСПОЗНАНО: в пуле {len(unk_pool)}, в паке {len(unk_pack)} "
                     f"(id: {', '.join(str(c) for c in (unk_pool + unk_pack)[:6])}) — "
                     f"их НЕТ в {setcode()}_set.json, поэтому они не учтены ни в одном "
                     f"счётчике выше. Спроси у игрока текст и оцени вручную.")
    saved = save_pool(picks, by_id, ratings, draft_id)
    if saved:
        lines.append(f"  💾 пул сохранён: pools/{os.path.basename(saved)} ({len(picks)} карт)")
    return "\n".join(lines)


def current_block(text, by_id, ratings, draft_id):
    """Premier: разбирает лог и отдаёт (sig, блок). Весь рендер — в render_block."""
    packs = find_packs(text)
    if not packs:
        return None, "NOPACK"
    pnum, pick, ids, _ = packs[-1]
    sig = f"{pnum}-{pick}-{len(ids)}-{sum(ids)}"
    picks = find_my_picks(text, draft_id)
    return sig, render_block(pnum, pick, ids, picks, by_id, ratings, draft_id)


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
    label = f"  (Бустер {pnum}, пик {pick})" if pnum is not None else ""
    picks = find_my_picks(text, draft_id)
    # ЕДИНЫЙ рендер — тот же, что в watch и в quickdraft.py. Своей копии тут больше нет.
    print(render_block(pnum, pick, ids, picks, by_id, ratings, draft_id,
                       header=f"===== ТЕКУЩИЙ ПАК [{setcode().upper()}]{label} — {len(ids)} карт ====="))
    if draft_id:
        print(f"  (draftId {draft_id[:8]}…)")


if __name__ == "__main__":
    main()
