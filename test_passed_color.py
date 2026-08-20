"""Регресс-тест ⚑ ПАСУЕМ <цвет> — на РЕАЛЬНОМ драфте, который его породил.

HOB, драфт 31a78cee (16.08.2026). Агент закоммитился в WU и вёл её все три бустера.
Инструмент 13 раз сказал «сильнее вне цвета» (4 из них — ⚑ПИВОТ), и все 13 срабатываний
были проигнорированы ПООДИНОЧКЕ: каждое по отдельности защитимо («ну одна карта мимо»),
а вместе они означали «чёрный открыт весь драфт». Ни один пер-пак баннер этого не видит.

Замер по тому драфту: чёрный дал 6 карт GIH≥58, доступных на пиках 5+, средний GIH 55.4 —
лучший из пяти цветов, и тёк во ВТОРОМ и в ТРЕТЬЕМ бустере (то есть открыт с обеих сторон
стола). Пять из шести пропущенных бомб были ОДНОПИПОВЫЕ, то есть сплешабельные — пивот
даже не требовался.

⚠️ ДРАФТ БЕРЁТСЯ ЛЮБОЙ ДОСТУПНЫЙ (переписано 20.08.2026). Исходный 31a78cee вымыло из
`.draft_hist.json` и из Player.log, и тест месяцами молча выходил с «пропущен» — то есть
не мог ни упасть, ни пройти. Теперь источник пиков — телеметрия, и годится любой драфт,
по которому есть история + телеметрия. Числа в шапке относятся к 31a78cee и остаются
как описание ПОВОДА, а не как ожидание от текущего прогона.

ЧТО ПРОВЕРЯЕТСЯ:
  A. баннер копит через паки и загорается на 3-й отданной карте (а не на первой);
  B. считает ТОЛЬКО пройденные паки — история на диске содержит весь драфт, и без фильтра
     на P1P6 печаталось «12-й раз» (поймано при внесении);
  C. называет сплешабельные (≤1 off-пип) отдельно — это более дешёвая опция, чем пивот;
  D. печатает не больше ОДНОГО цвета: три баннера разом читаются как «открыто всё» = шум;
  E. молчит, пока пул не закоммичен в два цвета;
  F. ТЕКУЩИЙ пак не числится отданным — карта, лежащая только в нём, ещё не отдана
     (док. случай eba1b036 P3P3: «отдаём Desolation Prowler», а Prowler был в этом паке
     и мы его взяли; счётчик завышался на единицу и порог срабатывал на пик раньше).
"""
import json, os, re, sys
os.environ["MTGA_SET"] = "hob"
os.environ["MTGA_OFFLINE"] = "1"
sys.path.insert(0, os.path.expanduser("~/.claude/skills/mtg-draft-helper"))
sys.argv = ["draft_live.py", "hob"]
import draft_live as D

HERE = os.path.dirname(os.path.abspath(__file__))
by, rat = D.load_cards(), D.load_ratings()
fails = []


def check(cond, msg):
    print(("   ✅ " if cond else "   ❌ ") + msg)
    if not cond:
        fails.append(msg)


# ── ИСТОЧНИК ПИКОВ: телеметрия, а не Player.log (переписано 20.08.2026) ──────
# Прежняя версия требовала И драфт 31a78cee в .draft_hist.json, И его pick-события в
# Player.log. Оба вымываются: история перезаписывается новым драфтом, лог ротируется.
# Из-за этого тест месяцами выходил `sys.exit(0)` со словом «пропущен» — то есть
# существовал, но не мог ни упасть, ни пройти (болезнь JOURNAL § 8.5).
# Теперь пики берутся из pools/<set>_<draft8>_telemetry.jsonl, который живёт рядом с
# историей и ротацию переживает; драфт выбирается любой, по которому есть оба файла.
hist_all = json.load(open(os.path.join(HERE, ".draft_hist.json")))


def _pick_source():
    """(draft_id, {(pack,pick): arena_id}) для любого драфта, где есть история И телеметрия."""
    name2id = {}
    for cid, c in by.items():
        for k in (c.get("name", ""), c.get("name", "").split(" //")[0]):
            name2id.setdefault(re.sub(r"[^a-z0-9]", "", k.lower()), cid)
    for did in hist_all:
        tel = os.path.join(HERE, "pools", f"{D.setcode()}_{did[:8]}_telemetry.jsonl")
        if not os.path.exists(tel):
            continue
        # Телеметрии мало: баннер считает ОТДАННЫЕ карты по пакам из .draft_hist.json,
        # а история вымывается следующими драфтами (20.08.2026: от eba1b036 остался
        # 1 пак из 42, тест выбирал его и падал «баннер не сработал ни разу»).
        if len(hist_all[did]) < 20:
            continue
        size = max((len(v) for k, v in hist_all[did].items() if k.endswith("-1")), default=14)
        got = {}
        for line in open(tel, encoding="utf-8"):
            try:
                r = json.loads(line)
            except Exception:
                continue
            if r.get("t") != "pick":
                continue
            cid = name2id.get(re.sub(r"[^a-z0-9]", "", (r.get("name") or "").lower()))
            if cid is not None:
                got[(r["i"] // size + 1, r["i"] % size + 1)] = cid
        if len(got) >= 20:
            return did, got
    return None, {}


DID, picks_by_coord = _pick_source()
if not DID:
    print("⏭  нет ни одного драфта, где есть И .draft_hist.json, И телеметрия с пиками — "
          "тест пропущен (запусти любой живой драфт)")
    sys.exit(0)
print(f"источник: драфт {DID[:8]}, пиков {len(picks_by_coord)}")
picks = {(DID, p, k): cid for (p, k), cid in picks_by_coord.items()}

pool, fired = [], []
for p in (1, 2, 3):
    for k in range(1, 15):
        main = D.pool_main_colors(pool, by)
        b = D.passed_color_banner(by, rat, main, pool, DID, p, k)
        if b:
            fired.append((p, k, b))
        g = picks.get((DID, p, k))
        if g:
            pool.append(g)

print("=" * 78)
print(f"⚑ ПАСУЕМ — прогон по реальному драфту {DID[:8]}")
print("=" * 78)
assert fired, "баннер не сработал ни разу — это провал сам по себе"
p, k, first = fired[0]
print(f"первое срабатывание: P{p}P{k}")
for l in first:
    print("   ", l)
print()

# A. копит, а не срабатывает на первой же карте
n_first = int(re.search(r"уже (\d+)-й раз", first[0]).group(1))
check(n_first >= 3, f"загорается накопительно, на {n_first}-й отданной карте (порог 3)")
# Инвариант — «не раньше P1P6»: pool_main_colors коммитится с 5 пиков, раньше баннер
# физически молчит. Прежний чек «не раньше P2P1» был наблюдением за eba1b036, а не
# правилом: на 3657e8ab баннер честно загорелся на P1P7 («ПАСУЕМ U», первым назван
# Bilbo, Luckwearer) — и это ИСТИННОЕ срабатывание, подтверждённое разбором (§ 8.18:
# синий тёк весь драфт, 13 сильных отдано). Требовать от него молчать в Б1 значило бы
# требовать пропустить ровно ту ошибку, ради которой он существует.
check((p, k) >= (1, 6), f"не раньше P1P6 — до коммита цветов молчит (сработал P{p}P{k})")

# B. считает только пройденные паки
counts = [int(re.search(r"уже (\d+)-й раз", b[0]).group(1)) for _, _, b in fired]
check(counts == sorted(counts), "счётчик монотонно растёт по ходу драфта")
check(max(counts) <= 42, f"счётчик не заглядывает в будущее (макс {max(counts)} ≤ 42 пиков)")
for (pp, kk, b) in fired:
    n = int(re.search(r"уже (\d+)-й раз", b[0]).group(1))
    seen = (pp - 1) * 14 + kk
    if n > seen:
        check(False, f"P{pp}P{kk}: счётчик {n} > просмотренных паков {seen} — считает будущее")
        break
else:
    check(True, "ни на одном пике счётчик не превысил число просмотренных паков")

# C. сплешабельные названы отдельно
check(any("СПЛЕШАБЕЛЬНЫ" in l for l in first),
      "однопиповые карты названы отдельной строкой (сплеш дешевле пивота)")

# D. один цвет за раз
heads = [l for l in first if l.startswith("⚑ ПАСУЕМ")]
check(len(heads) == 1, f"печатается ровно один цвет, не {len(heads)} (иначе «открыто всё» = шум)")
# Ожидаемый цвет — знание О КОНКРЕТНОМ драфте (из его разбора), а не инвариант:
# вычислять его здесь заново значило бы повторить логику баннера в тесте (§ 8.5).
KNOWN_OPEN = {"eba1b036": "B",     # § 8.16: чёрный — самый глубокий и дорогой из отданных
              "3657e8ab": "U"}     # § 8.18: 13 сильных моносиних отдано, включая 2× Bilbo
exp = KNOWN_OPEN.get(DID[:8])
if exp is None:
    print(f"  ⏭ драфт {DID[:8]} не разбирался — проверка «назван правильный цвет» пропущена")
else:
    check(exp in heads[0].split(":")[0],
          f"назван именно {exp} — по разбору этого драфта тёк он")

# E. молчит без коммита
check(D.passed_color_banner(by, rat, None, [], DID, 1, 3) == [],
      "молчит, пока пул не закоммичен в два цвета")

# F. ТЕКУЩИЙ пак не считается отданным (починено 20.08.2026)
# Док. случай eba1b036 P3P3: баннер написал «уже 4-й раз отдаём … Desolation Prowler 60.4»,
# пока Prowler лежал В ЭТОМ ЖЕ паке — и мы его взяли. Счётчик завышался на единицу.
hist_d = hist_all[DID]
bad_now = []
for (pp, kk, b) in fired:
    txt = " ".join(b)
    earlier = set()
    for key, ids in hist_d.items():
        try:
            a, c = (int(x) for x in key.split("-"))
        except ValueError:
            continue
        if (a, c) < (pp, kk):
            earlier |= set(ids)
    earlier_names = {D._name_of(c, by, rat) for c in earlier}
    # карта в тексте баннера обязана лежать хотя бы в одном СТРОГО БОЛЕЕ РАННЕМ паке;
    # экземпляр из текущего пака ещё не отдан — решение по нему принимается прямо сейчас
    for cid in hist_d.get(f"{pp}-{kk}", []):
        nm = D._name_of(cid, by, rat)
        if nm and nm in txt and nm not in earlier_names:
            bad_now.append((pp, kk, nm))
check(not bad_now,
      "ни одно срабатывание не называет отданной карту, которая лежит ТОЛЬКО в текущем паке"
      + (f" — нарушения: {bad_now[:3]}" if bad_now else ""))

print("=" * 78)
if fails:
    print(f"❌ ПРОВАЛЕНО {len(fails)}:")
    for f in fails:
        print("   ·", f)
    sys.exit(1)
print("✅ ВСЕ ПРОВЕРКИ ПРОШЛИ — пропуск открытого цвета теперь виден накопительно,")
print("   а не растворяется в тринадцати отдельных «ну одна карта мимо».")
