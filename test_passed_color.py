"""Регресс-тест ⚑ ПАСУЕМ <цвет> — на РЕАЛЬНОМ драфте, который его породил.

HOB, драфт 31a78cee (16.08.2026). Агент закоммитился в WU и вёл её все три бустера.
Инструмент 13 раз сказал «сильнее вне цвета» (4 из них — ⚑ПИВОТ), и все 13 срабатываний
были проигнорированы ПООДИНОЧКЕ: каждое по отдельности защитимо («ну одна карта мимо»),
а вместе они означали «чёрный открыт весь драфт». Ни один пер-пак баннер этого не видит.

Замер по тому драфту: чёрный дал 6 карт GIH≥58, доступных на пиках 5+, средний GIH 55.4 —
лучший из пяти цветов, и тёк во ВТОРОМ и в ТРЕТЬЕМ бустере (то есть открыт с обеих сторон
стола). Пять из шести пропущенных бомб были ОДНОПИПОВЫЕ, то есть сплешабельные — пивот
даже не требовался.

ЧТО ПРОВЕРЯЕТСЯ:
  A. баннер копит через паки и загорается на 3-й отданной карте (а не на первой);
  B. считает ТОЛЬКО пройденные паки — история на диске содержит весь драфт, и без фильтра
     на P1P6 печаталось «12-й раз» (поймано при внесении);
  C. называет сплешабельные (≤1 off-пип) отдельно — это более дешёвая опция, чем пивот;
  D. печатает не больше ОДНОГО цвета: три баннера разом читаются как «открыто всё» = шум;
  E. молчит, пока пул не закоммичен в два цвета.
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


hist_all = json.load(open(os.path.join(HERE, ".draft_hist.json")))
DID = "31a78cee-b49b-4eb7-9ccf-924bf0092d32"
if DID not in hist_all:
    print(f"⏭  история драфта {DID[:8]} не найдена — тест пропущен "
          f"(.draft_hist.json перезаписывается каждым новым драфтом)")
    sys.exit(0)

log = D.read_log_text()
picks = {}
for m in re.finditer(r'EventPlayerDraftMakePick.*?\\"DraftId\\":\\"([0-9a-f-]+)\\"'
                     r'.*?GrpIds\\":\[(\d+)\].*?Pack\\":(\d+),\\"Pick\\":(\d+)', log):
    picks[(m.group(1), int(m.group(3)), int(m.group(4)))] = int(m.group(2))
if not picks:
    print("⏭  pick-события этого драфта уже вымыло из Player.log — тест пропущен")
    sys.exit(0)

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
print("⚑ ПАСУЕМ — прогон по реальному драфту 31a78cee")
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
check((p, k) >= (2, 1), f"не шумит в первом бустере, пока цвета не устоялись (сработал P{p}P{k})")

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
check("B" in heads[0].split(":")[0], "назван именно чёрный — он и тёк весь драфт")

# E. молчит без коммита
check(D.passed_color_banner(by, rat, None, [], DID, 1, 3) == [],
      "молчит, пока пул не закоммичен в два цвета")

print("=" * 78)
if fails:
    print(f"❌ ПРОВАЛЕНО {len(fails)}:")
    for f in fails:
        print("   ·", f)
    sys.exit(1)
print("✅ ВСЕ ПРОВЕРКИ ПРОШЛИ — пропуск открытого цвета теперь виден накопительно,")
print("   а не растворяется в тринадцати отдельных «ну одна карта мимо».")
