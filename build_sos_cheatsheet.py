# -*- coding: utf-8 -*-
"""Генератор SOS (Secrets of Strixhaven) draft cheat sheet — по образцу msh_cheatsheet.html.
Запуск:  python3 build_sos_cheatsheet.py   (нужен sos_cards.json от Scryfall)
"""
import json, html as _h

cards = json.load(open('sos_cards.json'))
DB = {int(c['collector_number']): c for c in cards if c['collector_number'].isdigit()}

RL = {'mythic': 'M', 'rare': 'R', 'uncommon': 'U', 'common': 'C'}

def imgs(c):
    iu = c.get('image_uris')
    if iu:
        return iu['small'], iu['large']
    for f in c.get('card_faces', []):
        if f.get('image_uris'):
            return f['image_uris']['small'], f['image_uris']['large']
    return '', ''

def short_name(c):
    n = c['name'].split(' //')[0]
    n = n.split(',')[0]
    return n

def rletter(c):
    return RL.get(c['rarity'], 'C')

def card(num, short=None):
    """Карточка-плитка (.card)."""
    c = DB[num]
    sm, lg = imgs(c)
    r = rletter(c)
    nm = _h.escape(short or short_name(c))
    full = _h.escape(c['name'])
    url = c['scryfall_uri']
    return (f'<a class="card r-{r}" href="{url}" target="_blank" title="{full}">'
            f'<img loading="lazy" src="{sm}" alt="{full}">'
            f'<span class="rb">{r}</span><span class="nm">{nm}</span>'
            f'<img class="zoom" loading="lazy" src="{lg}" alt=""></a>')

def ref(num, label=None):
    """Инлайн-ссылка с ховер-зумом (.ref)."""
    c = DB[num]
    sm, lg = imgs(c)
    txt = _h.escape(label or short_name(c))
    url = c['scryfall_uri']
    return (f'<a class="ref" href="{url}" target="_blank">{txt}'
            f'<img class="zoom" loading="lazy" src="{lg}" alt=""></a>')

def grid(nums):
    return '<div class="grid">' + ''.join(card(n) for n in nums) + '</div>'

def group(h3, nums):
    return f'<div class="group"><h3>{h3}</h3>{grid(nums)}</div>'

# ----------------------------------------------------------------------------
# Архетипы (5 колледжей Стриксхейвена)
# ----------------------------------------------------------------------------
ARCHES = [
    dict(
        cls='wb', title='WB — Silverquill (Repartee / Инклинги-дрейн)',
        tag='⚪⚫ Заклинания в существ · летучие Инклинги · дрейн',
        plan=(f'<b>План:</b> разверни летучих Инклингов, кидай дешёвые инстанты/сорсери '
              f'<b>в свои существа</b> ради {ref(196,"Repartee")}-триггеров (+1/+1, полёт, '
              f'непроходимость, дрейн), добивай эвейжном и сливом жизней.'),
        win=dict(wc='🏆 <b>Победа:</b> темп + эвейжн, постепенный дрейн добивает стабилизировавшегося оппонента.',
            bullets=[
                f'<b>Раннее (1–3):</b> дешёвые тела и токены — {ref(11,"Eager Glyphmage")}, '
                f'{ref(196,"Inkling Mascot")}, {ref(224,"Scolding Administrator")}; начинай бить.',
                f'<b>Среднее (3–5):</b> заклинания в свои существа включают Repartee — '
                f'{ref(20,"Informed Inkwright")} делает Инклингов, {ref(227,"Snooping Page")} '
                f'тянет карты сквозь блок.',
                f'<b>Добивание:</b> {ref(225,"Silverquill Charm")} (дрейн 3) и '
                f'{ref(101,"Sneering Shadewriter")} дожимают; {ref(226,"Silverquill, the Disputant")} '
                f'удваивает каждый твой спелл через casualty.']),
        groups=[
            ('🎯 Сигналы / Пайоффы', [225, 196, 224, 227, 20, 35]),
            ('💫 Repartee-энейблеры (спеллы в существ)', [22, 28, 79, 89, 197]),
            ('💀 Removal', [18, 34, 86, 104, 83, 228]),
            ('👥 Инклинги / value', [11, 82, 195, 234]),
            ('👑 Топ / бомбы', [226, 13, 80, 78]),
        ],
        traps=(f'⚠️ <b>Ловушки:</b> Repartee срабатывает только от спеллов, которые <b>таргетят '
               f'существо</b> — чистый добор ({ref(65,"Quick Study")}) его НЕ включает. Не перебирай '
               f'Инклингов без финишера; держи 4–5 дешёвых таргет-спеллов.'),
    ),
    dict(
        cls='ur', title='UR — Prismari (Opus / спеллслингер-бёрн)',
        tag='🔵🔴 Плотность инстантов/сорсери · Opus · бёрн + Элементали',
        plan=(f'<b>План:</b> залей колоду дешёвыми инстантами/сорсери, {ref(229,"Opus")}-существа '
              f'растут и пингуют с каждого спелла; добивай бёрном и летучими Элементалями. '
              f'Спеллы за <b>5+ маны</b> открывают усиленный режим Opus.'),
        win=dict(wc='🏆 <b>Победа:</b> темп + прямой урон — Opus-тела и бёрн сводят оппонента в 0.',
            bullets=[
                f'<b>Раннее (1–3):</b> поставь Opus-двигатель — {ref(42,"Deluge Virtuoso")}, '
                f'{ref(134,"Thunderdrum Soloist")}, {ref(125,"Molten-Core Maestro")}.',
                f'<b>Среднее (3–5):</b> сжигай блокеров ({ref(136,"Unsubtle Mockery")}, '
                f'{ref(235,"Stress Dream")}) — каждый спелл качает все Opus-тела сразу.',
                f'<b>Добивание:</b> {ref(229,"Spectacular Skywhale")} (+3/+0 за спелл) и бёрн в лицо; '
                f'{ref(212,"Prismari, the Inspiration")} даёт спеллам storm → летальный ход.']),
        groups=[
            ('🎯 Сигналы / Пайоффы', [211, 240, 229, 180, 185, 223]),
            ('🔥 Opus-тела (моно)', [42, 60, 114, 134, 133, 125]),
            ('💀 Removal / бёрн', [240, 235, 239, 136, 118, 119]),
            ('📚 Карты / топливо', [65, 129, 219, 231]),
            ('👑 Топ / бомбы', [212, 120, 44, 45, 58]),
        ],
        traps=(f'⚠️ <b>Ловушки:</b> Opus считает только <b>инстанты/сорсери</b> — существа и '
               f'артефакты не триггерят. Нужно ~9–11 спеллов; не перегружай существами. Усиленный '
               f'режим требует <b>5+ маны, потраченной на один спелл</b> (X-спеллы это легко добивают).'),
    ),
    dict(
        cls='ug', title='GU — Quandrix (Increment / счётчики + Фракталы)',
        tag='🟢🔵 +1/+1 счётчики · рамп · большие X-спеллы',
        plan=(f'<b>План:</b> рампи, ставь {ref(190,"Increment")}-существ, кидай дорогие X-спеллы — '
              f'они грузят счётчики и Фракталы. Перерасти стол через размер.'),
        win=dict(wc='🏆 <b>Победа:</b> мидрейндж по счётчикам — большие Фракталы и Increment-тела перебивают по статам.',
            bullets=[
                f'<b>Раннее (1–3):</b> фикс и рамп ({ref(162,"Studious First-Year")}, '
                f'{ref(147,"Environmental Scientist")}, {ref(155,"Noxious Newt")}) + дешёвый Increment.',
                f'<b>Среднее (3–6):</b> {ref(50,"Fractal Anomaly")}/{ref(167,"Wild Hypothesis")} делают '
                f'Фракталов; каждый крупный спелл вешает +1/+1 на Increment-тела.',
                f'<b>Добивание:</b> {ref(193,"Growth Curve")} удваивает счётчики, '
                f'{ref(218,"Quandrix, the Proof")} (cascade, полёт, трампл) закрывает игру.']),
        groups=[
            ('🎯 Сигналы / Пайоффы', [217, 193, 190, 183, 175, 218]),
            ('📈 Increment / счётчики (моно)', [140, 69, 70, 151, 165, 63]),
            ('🌀 Фракталы / X-спеллы', [50, 51, 167, 55, 215, 139]),
            ('🌱 Рамп / фикс', [162, 147, 169, 186, 146]),
            ('👑 Топ / бомбы', [218, 149, 202, 145, 58]),
        ],
        traps=(f'⚠️ <b>Ловушки:</b> Increment вешает счётчик, только если <b>потрачено маны больше '
               f'текущей силы ИЛИ выносливости</b> существа — раскачанное тело перестаёт расти. '
               f'Сначала качай дешёвыми существами, потом дорогими спеллами. Removal в паре скудный — '
               f'добери {ref(244,"Witherbloom Charm")}/бёрн на сплеше.'),
    ),
    dict(
        cls='bg', title='BG — Witherbloom (Infusion / лайфгейн + сак-гринд)',
        tag='⚫🟢 Набор жизней · Пести · жертвы + дрейн',
        plan=(f'<b>План:</b> набирай жизни <b>каждый ход</b> (Пести, дрейн), это включает '
              f'{ref(83,"Infusion")} на removal/баффах; гринди через жертвы, реанимацию и слив жизней.'),
        win=dict(wc='🏆 <b>Победа:</b> гринд — лайфгейн+дрейн истощает оппонента, ты переигрываешь по картам и борде.',
            bullets=[
                f'<b>Раннее (1–3):</b> заведи лайфгейн-двигатель — {ref(238,"Teacher’s Pest")}, '
                f'{ref(177,"Bogwater Lumaret")}, {ref(100,"Send in the Pest")}.',
                f'<b>Среднее (3–5):</b> с набранной жизнью Infusion бьёт сильнее — '
                f'{ref(83,"Foolish Fate")} (убей + слив 3), {ref(92,"Poisoner’s Apprentice")} (-4/-4).',
                f'<b>Добивание:</b> {ref(105,"Withering Curse")} (вайп при лайфгейне), '
                f'{ref(214,"Professor Dellian Fel")} и {ref(245,"Witherbloom, the Balancer")} закрывают.']),
        groups=[
            ('🎯 Сигналы / Пайоффы', [244, 238, 187, 207, 199, 176]),
            ('🩸 Infusion-пайоффы (моно)', [83, 92, 105, 91, 102, 144]),
            ('💚 Лайфгейн / Пести (энейблеры)', [177, 100, 101, 157, 90, 143]),
            ('💀 Removal / sac', [86, 104, 192, 241, 81, 179]),
            ('👑 Топ / бомбы', [245, 214, 80, 105, 78]),
        ],
        traps=(f'⚠️ <b>Ловушки:</b> почти все Infusion-эффекты проверяют, набрал ли ты жизнь '
               f'<b>уже в этот ход</b> — сначала лайфгейн, потом Infusion-спелл. '
               f'{ref(102,"Tragedy Feaster")} заставляет жертвовать, если жизнь не набрана. '
               f'Не клади removal вслепую — копи дрейн-движок.'),
    ),
    dict(
        cls='rw', title='RW — Lorehold (Flashback / кладбище + Духи)',
        tag='🔴⚪ Flashback · «карты ушли с кладбища» · Духи + реликвии',
        plan=(f'<b>План:</b> дешёвые тела и токены-Духи, разыгрывай спеллы <b>из кладбища</b> '
              f'({ref(115,"Flashback")}), триггеря пайоффы «когда карты покидают кладбище». '
              f'Агро + reach от реликвий.'),
        win=dict(wc='🏆 <b>Победа:</b> агро по value — Духи и flashback-спеллы дают двойную отдачу, бёрн добивает.',
            bullets=[
                f'<b>Раннее (1–3):</b> {ref(230,"Spirit Mascot")}, {ref(17,"Group Project")}, '
                f'{ref(7,"Antiquities on the Loose")} наполняют борд Духами.',
                f'<b>Среднее (3–5):</b> flashback даёт вторую отдачу, а {ref(194,"Hardened Academic")} / '
                f'{ref(116,"Garrison Excavator")} ловят триггер «карта ушла с кладбища».',
                f'<b>Добивание:</b> {ref(204,"Molten Note")} (урон + развал) и '
                f'{ref(201,"Lorehold, the Historian")} (miracle, полёт, haste) закрывают.']),
        groups=[
            ('🎯 Сигналы / Пайоффы', [200, 230, 198, 194, 174, 233]),
            ('♻️ Flashback / «ушли с GY»', [7, 17, 216, 10, 121, 116]),
            ('💀 Removal / бёрн', [243, 204, 118, 236, 135, 136]),
            ('🏺 Реликвии / артефакты', [173, 210, 250, 132]),
            ('👑 Топ / бомбы', [201, 113, 30, 120, 13]),
        ],
        traps=(f'⚠️ <b>Ловушки:</b> Flashback после розыгрыша <b>изгоняет</b> карту — это разовая '
               f'отдача. Пайоффы «когда карты покидают кладбище» требуют реального наполнения GY; '
               f'не вычерпывай кладбище зря ({ref(36,"Stone Docent")}, {ref(56,"Soaring Stoneglider")} '
               f'едят его как ресурс).'),
    ),
]

def arch_html(a):
    head = (f'<section class="arch {a["cls"]}"><div class="arch-head">'
            f'<h2>{a["title"]}</h2><p class="tag">{a["tag"]}</p>'
            f'<p class="plan">{a["plan"]}</p></div>')
    w = a['win']
    win = ('<div class="win"><div class="wc">' + w['wc'] + '</div><ul>'
           + ''.join(f'<li>{b}</li>' for b in w['bullets']) + '</ul></div>')
    grps = ''.join(group(h, n) for h, n in a['groups'])
    traps = f'<div class="traps">{a["traps"]}</div>'
    return head + win + grps + traps + '</section>'

ARCH_BLOCK = '<div class="wrap">' + ''.join(arch_html(a) for a in ARCHES) + '</div>'

# ----------------------------------------------------------------------------
# Панель: Prepare (гибкие двусторонние пики) — incl. Emeritus // reprint цикл
# ----------------------------------------------------------------------------
PREP_ROWS = [
    (13, '{1}{W}{W} существо // {W} <b>Swords to Plowshares</b> — лучший removal сета держится «наготове»', 'ядро WB'),
    (45, '{3}{U}{U} летун // {U} <b>Ancestral Recall</b> — добор 3 карт, пока тело давит', 'ядро UR/GU'),
    (80, '{3}{B} существо // {1}{B} <b>Demonic Tutor</b> — тутор любой карты, не теряя тело', 'ядро BG'),
    (113, '{1}{R} ферст-страйк // {R} <b>Lightning Bolt</b> — готовится с 3-го спелла за ход', 'ядро UR/RW'),
    (145, '{2}{G} вижил // {1}{G} <b>Regrowth</b> — возврат любой карты при 8 землях', 'ядро GU/BG'),
]
def prep_row(num, desc, pair):
    c = DB[num]
    return (f'<div class="dfcrow">{card(num)}'
            f'<div class="dfctext">{desc} &nbsp;•&nbsp; <span class="pair">{pair}</span></div></div>')

PANEL_PREP = (
    '<section class="panel dfc"><h2>🔁 Prepare — гибкие двусторонние пики</h2>'
    '<p class="ptext"><b>Prepare:</b> существо входит «<b>наготове</b>» (prepared) — пока оно наготове, '
    'можно разыграть <b>копию его заклинания</b> (нижняя половина), и существо при этом остаётся на столе. '
    'Это встроенное 2-в-1: ранний пик гибок (тело ИЛИ спелл по ситуации). Топ-цикл — '
    '<b>Emeritus // классические перепечатки</b>: одни из сильнейших бомб формата.</p>'
    + ''.join(prep_row(*r) for r in PREP_ROWS) +
    '<p class="ptext" style="margin-top:6px">Прочие сильные prepare-тела: '
    + ' · '.join(ref(n) for n in [55, 67, 99, 170, 223, 237, 166]) + '.</p>'
    '</section>'
)

# ----------------------------------------------------------------------------
# Панель: плотность спеллов («магия каждый ход») — мост Repartee/Opus/Increment
# ----------------------------------------------------------------------------
PANEL_SPELL = (
    '<section class="panel second"><h2>🃏 Двигатель плотности спеллов</h2>'
    '<p class="ptext">Сквозная ось сета: множество карт награждают за <b>розыгрыш инстанта/сорсери</b> '
    '(а часто — за <b>каждый</b> спелл за ход). {ref_opus} (UR), {ref_rep} (WB), Increment (GU) и flashback (RW) '
    'питаются от одного и того же — <b>высокой плотности заклинаний</b>. Считай спеллы как отдельный ресурс: '
    'цель ~10+ инстантов/сорсери + дешёвый источник «маны только под спеллы».</p>'
    .replace('{ref_opus}', ref(42, 'Opus')).replace('{ref_rep}', ref(196, 'Repartee')) +
    '<div class="scols">'
    '<div class="scol"><h4>⚡ Платят за каждый спелл (пайоффы)</h4>'
    + grid([229, 134, 125, 114, 133, 250, 248, 169, 123]) + '</div>'
    '<div class="scol"><h4>⚙️ Дешёвые спеллы + мана-фикс под них</h4>'
    + grid([240, 136, 79, 22, 65, 54, 251, 257]) + '</div>'
    '</div></section>'
)

# ----------------------------------------------------------------------------
# Панель: keyword-математика
# ----------------------------------------------------------------------------
KW_ROWS = [
    ('38', 'Prepared', 'Самая частая механика. Существо «наготове» → можно скастить копию его спелла, тело остаётся = 2-в-1. Снимает/ставит наготове {ref0}.', [13, 80, 45]),
    ('12', 'Repartee', 'Триггер от инстанта/сорсери, который <b>таргетит существо</b>. Держи дешёвые таргет-спеллы.', [196, 20, 35]),
    ('10', 'Opus', 'Бонус за каждый инстант/сорсери; усиление при <b>5+ маны</b> на один спелл (X-спеллы).', [229, 125, 42]),
    ('9', 'Increment', 'Спелл с маной > силы ИЛИ выносливости тела → +1/+1. Раскачанное тело растёт хуже.', [190, 175, 69]),
    ('12', 'Infusion', 'Срабатывает, если ты <b>набрал жизнь в этот ход</b>. Сначала лайфгейн — потом спелл.', [83, 105, 92]),
    ('9', 'Converge', '+1/+1 (или X) за <b>каждый цвет маны</b>, потраченный на каст. Награда за 3+ цвета / сплеш.', [123, 4, 5]),
    ('24', 'Flying', 'Главная ось эвейжна. Элементали 3/3 и Инклинги летают — целься в ≥3–4 летуна/reach.', [229, 226, 201]),
]
def kw_row(n, name, mean, ex):
    mean = mean.replace('{ref0}', ref(247, 'Biblioplex Tomekeeper'))
    return (f'<div class="kwrow"><div class="kwhead"><span class="kwn">{n}</span> <b>{name}</b></div>'
            f'<div class="kwmean">{mean}</div><div class="kwex">{"".join(card(x) for x in ex)}</div></div>')
PANEL_KW = ('<section class="panel kw"><h2>⚔️ Keyword-математика</h2>'
            + ''.join(kw_row(*r) for r in KW_ROWS) + '</section>')

# ----------------------------------------------------------------------------
# Панель: порядок пика / процесс
# ----------------------------------------------------------------------------
PROC = [
    ('🥇 P1–P4 (старт)', 'Бери СИЛУ: бомба/removal > всё. Цвет не коммить — формируй гипотезу. Emeritus-цикл и Elder Dragon’ы — спекулятивный 1-й пик.'),
    ('🔀 P5–P9 (сигналы)', 'Колледж = пара цветов. Поздний золотой signpost-анкоммон (charm, mascot) = этот колледж <b>открыт</b>. Wheel (9+) = железный сигнал. К этому моменту закоммить колледж.'),
    ('📦 Бустер 2–3', 'Колледж ясен. Добирай кривую, плотность спеллов (под Opus/Repartee), фикс — двойные земли с surveil. Поздние сигналы игнорируй.'),
    ('📊 BREAD-приоритет', 'Bombs > Removal > Evasion (летуны) > Engine (спелл-пайоффы) > filler. Спеллы считай как отдельный must.'),
    ('🎴 Состав колоды', '~17 земель + 23 нонленда. UR/WB хотят ~10+ инстантов/сорсери. GU/BG — больше существ и рампа. Минимум 2–3 removal.'),
    ('🌈 Сплеш / Converge', 'Двойные земли + {ref_terra} легко дают 3-й цвет. Converge ({ref_arch}) и многоцветные бомбы окупают сплеш.'),
    ('✋ Мулиган', 'Держи 2–4 земли + игру на 2–3 ход. UR без дешёвых спеллов и GU без рампа — слабые руки.'),
]
def pcard(h, p):
    p = p.replace('{ref_terra}', ref(265, 'Terramorphic Expanse')).replace('{ref_arch}', ref(2, 'Rancorous Archaic'))
    return f'<div class="pcard"><h4>{h}</h4><p>{p}</p></div>'
PANEL_PROC = ('<section class="panel proc"><h2>🧭 Порядок пика и процесс драфта</h2>'
              '<div class="pgrid">' + ''.join(pcard(*x) for x in PROC) + '</div></section>')

# ----------------------------------------------------------------------------
# Панель: комбо
# ----------------------------------------------------------------------------
COMBOS = [
    (174, 240, 'Тапни 3 существа → скопируй свой бёрн/removal. Удвоенный {ref}.'),
    (193, 215, 'Поставь счётчик и удвой все → Pterafractyl/любой Фрактал взрывается.'),
    (179, 100, 'Жертвуй Пестов → дрейн + реанимация существа из кладбища каждый ход.'),
    (226, 11, 'Casualty на каждом спелле: жертвуй Инклинга → копия спелла бесплатно.'),
    (201, 113, 'Miracle на инстантах в руке: Lightning Bolt/Swords за {2} с верха.'),
    (123, 136, 'Каждый спелл даёт команде +1/+0 — Magmablood превращает бёрн в альфа-страйк.'),
    (212, 65, 'Storm: цепочка дешёвых спеллов копирует Quick Study/бёрн → летально.'),
    (175, 193, 'Growth Curve удваивает счётчики Berta, та триггерит добор от +1/+1.'),
    (146, 167, 'Emil даёт трампл телам со счётчиками; Wild Hypothesis грузит Фракталов.'),
    (245, 100, 'Affinity for creatures: широкий борд Пестов делает дракона почти бесплатным.'),
]
def combo(a, b, desc):
    desc = desc.replace('{ref}', ref(240, 'Vibrant Outburst'))
    return (f'<div class="combo">{card(a)}<span class="plus">+</span>{card(b)}'
            f'<p class="cdesc">{desc}</p></div>')
PANEL_COMBOS = ('<section class="panel combos"><h2>🔗 Комбо-связки (знать наизусть)</h2>'
                '<div class="cgrid">' + ''.join(combo(*c) for c in COMBOS) + '</div></section>')

# ----------------------------------------------------------------------------
# Сборка
# ----------------------------------------------------------------------------
STYLE = r"""<style>
:root{--card:#1a1d24;--ink:#e8eaf0;--mut:#9aa3b2}
*{box-sizing:border-box}
body{margin:0;background:linear-gradient(135deg,#0d0f14,#141823);color:var(--ink);font:15px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;padding:24px}
h1{font-size:22px;margin:0 0 4px} .sub{color:var(--mut);margin:0 0 12px;font-size:13px}
.disc{max-width:1500px;margin:0 auto 14px;background:#3a2410;border:1px solid #7a531c;border-radius:10px;padding:11px 14px;font-size:13px;color:#f2d9a6}
.disc b{color:#ffe9be}
.legend{color:var(--mut);font-size:12px;margin:0 auto 16px;max-width:1500px;background:#161a22;border:1px solid #262a34;border-radius:10px;padding:10px 12px}
.legend b{color:#cdd4e2} .legend code{color:#9fc7ff}
.wrap{display:grid;grid-template-columns:1fr 1fr;gap:22px;max-width:1500px;margin:0 auto}
@media(max-width:1100px){.wrap{grid-template-columns:1fr}}
.arch{background:var(--card);border-radius:16px;padding:18px;border:1px solid #262a34}
.arch.br{border-top:4px solid #d8553b} .arch.ug{border-top:4px solid #4aa564}
.arch.rg{border-top:4px solid #c9772e} .arch.rw{border-top:4px solid #e0b04a}
.arch.bg{border-top:4px solid #6b8f4e} .arch.ur{border-top:4px solid #5a8fc7}
.arch.wu{border-top:4px solid #9fb6d6} .arch.wb{border-top:4px solid #9aa0ad}
.arch.gw{border-top:4px solid #9ac06a} .arch.ub{border-top:4px solid #6c6f9c}
.arch-head h2{margin:0 0 2px;font-size:19px} .tag{margin:0;color:var(--mut);font-size:12px;font-weight:600}
.plan{margin:8px 0 12px;font-size:13px;color:#c7cdda}
.win{background:#12161d;border:1px solid #2b3340;border-left:3px solid #c79b3a;border-radius:10px;padding:10px 12px;margin-bottom:14px}
.win .wc{font-size:13px;color:#f0e2bf;margin-bottom:6px} .win ul{margin:0;padding-left:18px}
.win li{font-size:12.5px;color:#c7cdda;margin-bottom:4px} .win b{color:#e8eaf0}
.group{margin-bottom:14px} .group h3{font-size:13px;margin:0 0 8px;color:#cdd4e2}
.grid{display:flex;flex-wrap:wrap;gap:8px}
.card{position:relative;width:76px;text-decoration:none;color:var(--ink)}
.card>img:first-of-type{width:76px;border-radius:6px;display:block;box-shadow:0 2px 6px rgba(0,0,0,.5);border:1px solid #2c3140;transition:border-color .15s}
.card:hover>img:first-of-type{border-color:#5b6bce}
.card .nm{display:block;font-size:10px;color:var(--mut);text-align:center;margin-top:3px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:76px}
.card .rb{position:absolute;top:3px;right:3px;background:#000a;border-radius:4px;font-size:9px;padding:1px 4px;font-weight:700}
.r-M .rb{color:#f5a623} .r-R .rb{color:#e8d27a} .r-U .rb{color:#cfd6e4} .r-C .rb{color:#9aa3b2}
.zoom{position:fixed;top:50%;right:24px;left:auto;transform:translateY(-50%);height:84vh;max-height:680px;width:auto;border-radius:18px;z-index:999;display:none;box-shadow:0 18px 60px rgba(0,0,0,.85);pointer-events:none}
.card:hover .zoom,.ref:hover .zoom{display:block}
.ref{color:#bcd0ff;text-decoration:none;border-bottom:1px dashed #4a5a80;cursor:help;position:relative;white-space:nowrap}
.ref:hover{color:#e8f0ff}
.traps{font-size:12px;color:#e3b7a0;background:#2a1c18;border-radius:10px;padding:10px 12px;margin-top:8px;border:1px solid #3a2620}
.panel{max-width:1500px;margin:22px auto 0;background:var(--card);border:1px solid #262a34;border-radius:16px;padding:18px}
.panel.combos{border-top:4px solid #9b6dd6} .panel.proc{border-top:4px solid #3aa9a0}
.panel.dfc{border-top:4px solid #c77fd6} .panel.second{border-top:4px solid #4aa564} .panel.kw{border-top:4px solid #d8973b}
.panel h2{margin:0 0 12px;font-size:19px}
.ptext{font-size:13px;color:#c7cdda;margin:0 0 12px} .ptext b{color:#e8eaf0}
.cgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:16px}
.combo{display:flex;flex-wrap:wrap;align-items:flex-start;gap:6px;background:#15181f;border:1px solid #262a34;border-radius:12px;padding:10px}
.plus{font-size:22px;color:#9b6dd6;font-weight:700;align-self:center;margin:0 2px}
.cdesc{flex-basis:100%;margin:6px 0 0;font-size:12px;color:#c7cdda}
.pgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:14px}
.pcard{background:#13171e;border:1px solid #262a34;border-radius:12px;padding:12px}
.pcard h4{margin:0 0 6px;font-size:14px;color:#bfe7e2} .pcard p{margin:0;font-size:12.5px;color:#c7cdda}
.dfcrow{display:flex;flex-wrap:wrap;align-items:flex-start;gap:8px;background:#15181f;border:1px solid #262a34;border-radius:12px;padding:10px;margin-bottom:10px}
.arrow{align-self:center;color:#c77fd6;font-weight:700;font-size:12px;white-space:nowrap}
.dfctext{flex-basis:100%;font-size:12px;color:#c7cdda;margin-top:4px} .dfctext .pair{color:#bfe7e2;font-weight:600}
.scols{display:grid;grid-template-columns:1fr 1fr;gap:16px} @media(max-width:700px){.scols{grid-template-columns:1fr}}
.scol h4{margin:0 0 8px;font-size:14px;color:#cdd4e2}
.kwrow{display:grid;grid-template-columns:130px 1fr auto;gap:12px;align-items:center;background:#15181f;border:1px solid #262a34;border-radius:10px;padding:8px 10px;margin-bottom:8px}
@media(max-width:800px){.kwrow{grid-template-columns:1fr}}
.kwhead .kwn{display:inline-block;min-width:26px;text-align:center;background:#2a2410;color:#f0d28a;border-radius:6px;padding:1px 6px;font-weight:700;margin-right:4px}
.kwmean{font-size:12.5px;color:#c7cdda} .kwex{display:flex;gap:6px}
</style>"""
H1 = ('<h1>🎓 SOS Draft Cheat Sheet — 5 колледжей · Prepare · плотность спеллов · '
      'keyword-математика · комбо · порядок пика</h1>')
DISC = ('<div class="disc">📚 <b>Secrets of Strixhaven · релиз 24.04.2026 · 271 карта основного сета '
        '(данные Scryfall, полный сет).</b> Тексты карт точные; оценки силы/тир-листа и форса — '
        '<b>аналитика по картам и механикам</b> (ранний прочтённый формат), не финальный мета-тир-лист. '
        'Обнови картинки/цены: <code>python3 build_sos_cheatsheet.py</code>.</div>')
LEGEND = ('<p class="legend"><b>5 колледжей = 5 пар цветов:</b> '
          '⚪⚫ Silverquill · 🔵🔴 Prismari · 🟢🔵 Quandrix · ⚫🟢 Witherbloom · 🔴⚪ Lorehold. '
          'Каждый — свой архетип и механика. <b>Наведи на карту</b> → увеличенный скан. '
          'Бесцветные Archaic-существа и Converge награждают за <b>сплеш в 3+ цвета</b>.</p>')

DOC = ('<!doctype html><html lang="ru"><head><meta charset="utf-8">'
       '<meta name="viewport" content="width=device-width,initial-scale=1">'
       '<title>SOS Draft Cheat Sheet</title>' + STYLE + '</head><body>'
       + H1 + DISC + LEGEND + ARCH_BLOCK
       + PANEL_PREP + PANEL_SPELL + PANEL_KW + PANEL_PROC + PANEL_COMBOS
       + '</body></html>')

open('sos_cheatsheet.html', 'w').write(DOC)
print('written sos_cheatsheet.html', len(DOC), 'bytes')
