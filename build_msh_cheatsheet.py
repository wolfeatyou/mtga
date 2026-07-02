# -*- coding: utf-8 -*-
"""Генератор MSH (Marvel Super Heroes) draft cheat sheet — полный пул (msh_set.json, 281 карта).
Структура по образцу build_sos_cheatsheet.py / старого msh_cheatsheet.html.
Запуск:  python3 build_msh_cheatsheet.py
Пишет:   msh_cheatsheet.html (в текущей папке).
"""
import json, html as _h, sys

cards = json.load(open('msh_set.json'))
DB = {int(c['collector_number']): c for c in cards if c.get('collector_number', '').isdigit()}
RL = {'mythic': 'M', 'rare': 'R', 'uncommon': 'U', 'common': 'C'}
_missing = set()

def imgs(c):
    iu = c.get('image_uris')
    if iu:
        return iu.get('small', ''), iu.get('large', '')
    for f in c.get('card_faces', []):
        if f.get('image_uris'):
            return f['image_uris'].get('small', ''), f['image_uris'].get('large', '')
    return '', ''

def short_name(c):
    n = c['name'].split(' //')[0]
    return n.split(',')[0]

def rletter(c):
    return RL.get(c['rarity'], 'C')

def card(num, short=None):
    c = DB.get(num)
    if not c:
        _missing.add(num)
        return f'<span class="card miss">#{num}?</span>'
    sm, lg = imgs(c)
    r = rletter(c)
    nm = _h.escape(short or short_name(c))
    full = _h.escape(c['name'])
    return (f'<a class="card r-{r}" href="{c["scryfall_uri"]}" target="_blank" title="{full}">'
            f'<img loading="lazy" src="{sm}" alt="{full}">'
            f'<span class="rb">{r}</span><span class="nm">{nm}</span>'
            f'<img class="zoom" loading="lazy" src="{lg}" alt=""></a>')

def ref(num, label=None):
    c = DB.get(num)
    if not c:
        _missing.add(num)
        return f'<span class="ref miss">#{num}?</span>'
    sm, lg = imgs(c)
    txt = _h.escape(label or short_name(c))
    return (f'<a class="ref" href="{c["scryfall_uri"]}" target="_blank">{txt}'
            f'<img class="zoom" loading="lazy" src="{lg}" alt=""></a>')

def grid(nums):
    return '<div class="grid">' + ''.join(card(n) for n in nums) + '</div>'

def group(h3, nums):
    return f'<div class="group"><h3>{h3}</h3>{grid(nums)}</div>'

# ----------------------------------------------------------------------------
# 10 архетипов (пары цветов). Темы Marvel: Villain/Hero трайбал, +1/+1 counters,
# Power-up, Teamwork, Connive, Plan, Equipment, Artifacts.
# ----------------------------------------------------------------------------
ARCHES = [
 dict(cls='br', title='BR — Villains-агро (трайбал + токены)',
   tag='⚫🔴 Злодеи · «whenever a Villain enters» · токены 2/1 menace · бёрн',
   plan=(f'<b>План:</b> наводни стол злодеями и 2/1-menace токенами, триггеря '
         f'{ref(91,"Crossbones")}/{ref(96,"Doom Reigns Supreme")} с каждого Villain-ETB; '
         f'добивай бёрном и menace-уроном.'),
   win=dict(wc='🏆 <b>Победа:</b> темп-агро — широкий злодейский борд + дрейн/бёрн закрывают до стабилизации.',
     bullets=[f'<b>Раннее (1–3):</b> дешёвые злодеи и токен-мейкеры — {ref(85,"Agents of HYDRA")}, '
              f'{ref(101,"HYDRA Troopers")}, {ref(123,"Yellowjacket")}.',
              f'<b>Среднее:</b> {ref(221,"Madame Hydra")} и {ref(88,"Baron Strucker")} превращают каждого '
              f'злодея в карты/токены; {ref(91,"Crossbones")} растёт неудержимо.',
              f'<b>Добивание:</b> {ref(105,"The Masters of Evil")} (+2/+1 команде) + бёрн '
              f'({ref(157,"Truck Toss")}, {ref(147,"Photon Blast Barrage")}).']),
   groups=[('🎯 Сигнпосты / пайоффы', [221, 91, 96, 88, 105, 202]),
           ('👿 Злодеи / токены (энейблеры)', [85, 101, 123, 86, 134, 137]),
           ('🔥 Removal / бёрн', [142, 157, 124, 146, 150, 122]),
           ('🃏 Value', [104, 120, 113, 119, 98]),
           ('👑 Топ / бомбы', [233, 95, 202, 89, 224])],
   traps=(f'⚠️ <b>Ловушки:</b> токены 2/1 хрупкие — нужен payoff, который превращает их в урон/карты '
          f'({ref(96,"Doom Reigns")}, {ref(105,"Masters of Evil")}), иначе просто рассыпаются о блок. '
          f'Не зевай свипы ({ref(124,"Avengers Disassembled")} — твой же, бойся зеркала).')),

 dict(cls='ug', title='UG — Счётчики + «вторая карта» (value)',
   tag='🟢🔵 +1/+1 counters · «draw your second card» · Ant-Man / Beast',
   plan=(f'<b>План:</b> качай +1/+1 счётчики и добирай по <b>2 карты за ход</b> — '
         f'{ref(204,"Astonishing Ant-Man")} и {ref(175,"Knight of Wundagore")} запускают цепную реакцию; '
         f'перерасти стол по статам.'),
   win=dict(wc='🏆 <b>Победа:</b> мидрейндж по счётчикам — раскачанные тела + добор перебивают по картам и размеру.',
     bullets=[f'<b>Раннее:</b> постав движок — {ref(204,"Astonishing Ant-Man")}, {ref(175,"Knight of Wundagore")}, '
              f'{ref(201,"Ant-Man, Colony Commander")}.',
              f'<b>Среднее:</b> {ref(164,"Doc Samson")} удваивает все счётчики; {ref(223,"Moon Girl")} и '
              f'{ref(45,"Atlantean Cavalry")} награждают за 2-ю карту за ход.',
              f'<b>Добивание:</b> {ref(192,"Training Regimen")} (трампл всем со счётчиками) + '
              f'{ref(193,"Squirrel Girl")}/{ref(196,"White Tiger")}.']),
   groups=[('🎯 Сигнпосты / пайоффы', [204, 201, 223, 206, 199, 241]),
           ('📈 Счётчики (моно-энейблеры)', [175, 164, 173, 192, 63, 196]),
           ('🃏 «Вторая карта за ход»', [45, 47, 113, 90, 67]),
           ('🌱 Value / фикс', [174, 247, 66, 84, 81]),
           ('👑 Топ / бомбы', [193, 187, 188, 215, 230])],
   traps=(f'⚠️ <b>Ловушки:</b> {ref(204,"Astonishing Ant-Man")} и «draw your second card» хотят '
          f'<b>дешёвый добор</b> — держи 4–6 источников второй карты. Счётчики без эвейжна '
          f'упираются в блок: добери трампл ({ref(192,"Training Regimen")}) или летунов.')),

 dict(cls='rg', title='RG — Power-up / большие тела',
   tag='🔴🟢 Power-up (активируемые счётчики) · трампл · gamma-громилы',
   plan=(f'<b>План:</b> ставь дешёвые power-up тела, {ref(215,"Hulk")} удешевляет их активацию на {3}, '
         f'и за ход взрываешь стол в счётчиках; трампл-урон пробивает.'),
   win=dict(wc='🏆 <b>Победа:</b> мидрейндж-громилы — power-up превращает ману в +1/+1, трампл сводит в 0.',
     bullets=[f'<b>Раннее:</b> power-up тела — {ref(186,"Serpent Specialist")}, {ref(159,"Volcanic Villain")}, '
              f'{ref(171,"Hercules")}.',
              f'<b>Среднее:</b> {ref(215,"Hulk, Gamma Goliath")} (−3 к power-up) + {ref(149,"Red Hulk")} (enrage) '
              f'делают активации почти бесплатными.',
              f'<b>Добивание:</b> {ref(240,"Wolverine")}/{ref(198,"Abomination")} (fight) расчищают, '
              f'{ref(190,"The Thing")} и большие трамплеры закрывают.']),
   groups=[('🎯 Сигнпосты / пайоффы', [215, 198, 240, 200, 160]),
           ('💪 Power-up тела (моно)', [186, 159, 171, 178, 188, 196]),
           ('🌋 Большие тела / landcycle', [185, 141, 149, 178, 195]),
           ('⚔️ Removal / fight / бёрн', [166, 180, 142, 169, 157]),
           ('👑 Топ / бомбы', [149, 156, 190, 215, 233])],
   traps=(f'⚠️ <b>Ловушки:</b> power-up активируется <b>раз на способность</b> и стоит много маны — без '
          f'{ref(215,"Hulk")}/{ref(160,"Wonder Man")} (доп. активации / −стоимость) это медленно. '
          f'Не перегружай дорогими телами без раннего давления.')),

 dict(cls='rw', title='RW — Hero-агро (атака + трайбал)',
   tag='🔴⚪ Герои · «attacks alone»/«other Heroes» · вид-агро + бёрн',
   plan=(f'<b>План:</b> быстрый героический борд, бей рано; {ref(10,"Captain America")} и '
         f'{ref(4,"Agent Phil Coulson")} вешают счётчики на «других героев», {ref(6,"Avengers Assemble!")} '
         f'добивает анфема.'),
   win=dict(wc='🏆 <b>Победа:</b> агро — герои растут от атак, бёрн и анфем добивают по жизни.',
     bullets=[f'<b>Раннее:</b> {ref(148,"Quicksilver")}, {ref(130,"Hawkeye")}, {ref(5,"Agents of S.H.I.E.L.D.")} '
              f'начинают давление.',
              f'<b>Среднее:</b> {ref(10,"Cap, Wings of Freedom")} и {ref(4,"Coulson")} качают команду героев; '
              f'{ref(136,"Human Torch")} пингует.',
              f'<b>Добивание:</b> {ref(234,"Thor Odinson")}, {ref(6,"Avengers Assemble!")} (+2/+2 + анфем) + бёрн.']),
   groups=[('🎯 Сигнпосты / пайоффы', [213, 234, 238, 231, 6]),
           ('🦸 Hero-пайоффы (моно)', [4, 10, 28, 136, 190, 35]),
           ('⚔️ «Attack alone» / агро', [5, 20, 14, 130, 7]),
           ('🔥 Removal / бёрн', [142, 157, 34, 150, 15]),
           ('👑 Топ / бомбы', [156, 9, 35, 213, 11])],
   traps=(f'⚠️ <b>Ловушки:</b> «attacks alone»-бонусы ({ref(20,"Luke Cage")}, {ref(5,"Agents of SHIELD")}) '
          f'конфликтуют с вид-агро — реши, ты <b>одиночка-вольтрон</b> или <b>широкий</b>. Не оба сразу. '
          f'Держи 2–3 бёрна, чтобы пробить стабилизацию.')),

 dict(cls='bg', title='BG — Sacrifice / гринд / counters-poison',
   tag='⚫🟢 Жертвы + кладбище · дрейн · яд (Serpent Society) · большие финишеры',
   plan=(f'<b>План:</b> размени мелочь через {ref(218,"Killmonger")}, возвращай угрозы из кладбища '
         f'({ref(98,"Grim Reaper")}), дрейни и закрывай большими бомбами ({ref(212,"Galactus")}).'),
   win=dict(wc='🏆 <b>Победа:</b> гринд — value из жертв/кладбища истощает, бомба или яд закрывают.',
     bullets=[f'<b>Раннее:</b> заведи лайфгейн/дрейн — {ref(96,"Doom Reigns Supreme")}, {ref(100,"HYDRA Infiltration")}, '
              f'{ref(181,"Rapid Rescue")}.',
              f'<b>Среднее:</b> {ref(218,"Killmonger")} (sac → destroy) и {ref(98,"Grim Reaper")} '
              f'(реанимация на атаке) грайндят; {ref(194,"Undercover Skrull")} растёт от GY.',
              f'<b>Добивание:</b> {ref(212,"The Coming of Galactus")} (свип+финиш) или яд '
              f'{ref(226,"The Serpent Society")}.']),
   groups=[('🎯 Сигнпосты / пайоффы', [218, 226, 212, 235, 96]),
           ('💀 Sac / кладбище (моно)', [98, 119, 194, 109, 184]),
           ('💚 Лайфгейн / дрейн', [100, 181, 172, 161, 96]),
           ('🩸 Removal', [99, 93, 122, 92, 188]),
           ('👑 Топ / бомбы', [212, 95, 193, 226, 235])],
   traps=(f'⚠️ <b>Ловушки:</b> жертвенные карты ({ref(218,"Killmonger")}) хотят <b>дешёвых тел/токенов</b> '
          f'как топливо — не оставайся без жертвы. Яд {ref(226,"Serpent Society")} — план B, не основной; '
          f'не строй колоду вокруг ward-яда.')),

 dict(cls='ur', title='UR — Артефакты / спеллы (Iron Man)',
   tag='🔵🔴 Артефакты + improvise · prowess/noncreature · Stark-tech',
   plan=(f'<b>План:</b> залей колоду дешёвыми артефактами и спеллами — {ref(216,"Iron Man")} и '
         f'{ref(144,"Machinesmith Automaton")} растут с каждого артефакта, prowess-тела бьют, '
         f'improvise удешевляет верх кривой.'),
   win=dict(wc='🏆 <b>Победа:</b> темп+бёрн — артефакт-тела и спелл-пайоффы давят, бёрн добивает.',
     bullets=[f'<b>Раннее:</b> артефакты-движок — {ref(153,"Stark Industries Exec")}, {ref(75,"Shuri")}, '
              f'{ref(55,"Futurist Forge")}.',
              f'<b>Среднее:</b> {ref(216,"Iron Man")}/{ref(144,"Machinesmith")} масштабируются от артефактов; '
              f'{ref(151,"Scarlet Witch")} удешевляет спеллы.',
              f'<b>Добивание:</b> {ref(80,"Tony Stark // Iron Man")} и {ref(252,"Ultron")} закрывают; '
              f'бёрн в лицо.']),
   groups=[('🎯 Сигнпосты / пайоффы', [216, 203, 237, 227, 60]),
           ('⚙️ Артефакты-движок', [153, 75, 55, 144, 252, 246]),
           ('✨ Спеллы / prowess', [3, 19, 126, 151, 152, 84]),
           ('🔥 Removal / бёрн', [142, 147, 50, 157, 83]),
           ('👑 Топ / бомбы', [80, 156, 245, 252, 129])],
   traps=(f'⚠️ <b>Ловушки:</b> improvise/артефакт-пайоффы хотят <b>массы дешёвых артефактов</b> '
          f'(Treasure, Clue, токены) — без плотности {ref(216,"Iron Man")} мелкий. Не бери дорогие '
          f'артефакты ради «синергии», если они не двигают борд.')),

 dict(cls='wu', title='WU — Tap / темп-контроль (Heroes)',
   tag='⚪🔵 Tap-matters · флеш/флай · «creature becomes tapped» · мягкое removal',
   plan=(f'<b>План:</b> тэмпо-контроль — тапай/морозь угрозы, держи флай-блокеров и флеш, '
         f'{ref(210,"Captain America")} награждает за каждое тап-событие; добивай эвейжном.'),
   win=dict(wc='🏆 <b>Победа:</b> темп — мягкое removal + флай-давление, ты всегда на ход впереди.',
     bullets=[f'<b>Раннее:</b> {ref(33,"Raft Security Officer")}, {ref(73,"S.H.I.E.L.D. Deployment Drone")}, '
              f'{ref(32,"Quake")} тормозят и развивают.',
              f'<b>Среднее:</b> {ref(210,"Captain America, Living Legend")} и {ref(71,"Rewrite History")} '
              f'превращают tap-события в карты/счётчики.',
              f'<b>Добивание:</b> летуны ({ref(12,"Mar-Vell")}, {ref(40,"Wakandan Drone")}) + '
              f'{ref(11,"Captain Marvel")}.']),
   groups=[('🎯 Сигнпосты / пайоффы', [210, 229, 222, 219, 2]),
           ('🔁 Tap / темп', [32, 33, 84, 56, 71]),
           ('🕊️ Флай / value', [40, 73, 12, 66, 67]),
           ('❄️ Removal / pacify', [54, 37, 41, 74, 50]),
           ('👑 Топ / бомбы', [11, 222, 9, 210, 219])],
   traps=(f'⚠️ <b>Ловушки:</b> «soft removal» ({ref(54,"Frozen in Ice")}, {ref(37,"Super Villain Lockup")}) '
          f'не убивает — против больших тел нужен реальный exile/бёрн на сплеше. Не будь чисто реактивным: '
          f'держи 3–4 флай-угрозы, чтобы закрывать игру.')),

 dict(cls='wb', title='WB — Equipment / вольтрон',
   tag='⚪⚫ Экипировка · «equipped»-пайоффы · одна большая угроза + дрейн',
   plan=(f'<b>План:</b> навесь экипировку на ключевое тело — {ref(239,"Winter Soldier")} растёт +2/+0 за каждую, '
         f'{ref(121,"Whiplash")} дрейнит; добивай защищённым вольтроном + extort.'),
   win=dict(wc='🏆 <b>Победа:</b> одна неубиваемая угроза в экипировке + дрейн перебивают по урону.',
     bullets=[f'<b>Раннее:</b> дешёвые тела-носители + {ref(36,"S.H.I.E.L.D. Spy Kit")}, '
              f'{ref(78,"Super Suit")}, {ref(254,"Vibranium Daggers")}.',
              f'<b>Среднее:</b> {ref(239,"Winter Soldier")}/{ref(116,"Swordsman")} превращают экипировку в статы; '
              f'{ref(25,"Nick Fury")} и {ref(248,"Iron Man Armor")} закрывают.',
              f'<b>Добивание:</b> {ref(220,"Kingpin")} (extort-дрейн) + защищённый вольтрон.']),
   groups=[('🎯 Сигнпосты / пайоффы', [239, 236, 220, 211, 121]),
           ('🛡️ Equipment-пайоффы', [116, 112, 25, 248, 121]),
           ('⚙️ Экипировка (предметы)', [36, 244, 254, 78, 114, 38]),
           ('🩸 Removal', [34, 99, 93, 92, 37]),
           ('👑 Топ / бомбы', [89, 220, 233, 239, 211])],
   traps=(f'⚠️ <b>Ловушки:</b> вольтрон умирает от removal — держи защиту ({ref(39,"Take Up the Shield")}, '
          f'ward/indestructible) и <b>2-ю угрозу</b>, чтобы экипировка не легла зря. Не клади экипировку без '
          f'тел, которые её носят.')),

 dict(cls='gw', title='GW — Heroes go-wide / counters',
   tag='🟢⚪ Широкий героический борд · токены + анфем · +1/+1 раздача',
   plan=(f'<b>План:</b> наводни стол героями/токенами, раздавай +1/+1 ({ref(207,"Black Panther")}, '
         f'{ref(195,"Wakandan Royal Guard")}) и бей широко с анфемом ({ref(192,"Training Regimen")}).'),
   win=dict(wc='🏆 <b>Победа:</b> go-wide — широкий борд + командные баффы перекатывают по доске.',
     bullets=[f'<b>Раннее:</b> токен-мейкеры — {ref(27,"Okoye")}, {ref(7,"Borough Backup")}, '
              f'{ref(195,"Wakandan Royal Guard")}.',
              f'<b>Среднее:</b> {ref(207,"Black Panther, Vanguard")} и {ref(31,"Political Triumph")} '
              f'раздают счётчики/токены; {ref(17,"Invisible Woman")} гейнит.',
              f'<b>Добивание:</b> {ref(230,"Storm, Windrider")} (анти-флай лок) + {ref(193,"Squirrel Girl")} / '
              f'массовый анфем.']),
   groups=[('🎯 Сигнпосты / пайоффы', [207, 228, 230, 31, 173]),
           ('👥 Go-wide / токены', [27, 7, 249, 178, 195, 17]),
           ('🦸 Hero / counter-пайоффы', [4, 28, 190, 11, 196]),
           ('⚔️ Removal / pump', [15, 39, 168, 169, 188]),
           ('👑 Топ / бомбы', [230, 11, 193, 207, 156])],
   traps=(f'⚠️ <b>Ловушки:</b> go-wide рассыпается о свипы ({ref(124,"Avengers Disassembled")}, '
          f'{ref(212,"Galactus")}) — держи анфем/добор как backup. Не перегружай токенами без payoff, '
          f'который превращает ширину в урон.')),

 dict(cls='ub', title='UB — Connive / Villains / draw-контроль',
   tag='🔵⚫ Connive + «draw second card» · злодеи-value · отложенный контроль',
   plan=(f'<b>План:</b> фильтруй connive’ом, набирай карты, контроль removal’ом и закрывай '
         f'злодейскими бомбами ({ref(62,"Kang the Conqueror")}, {ref(95,"Doctor Doom")}).'),
   win=dict(wc='🏆 <b>Победа:</b> контроль по картам — connive-фильтр + removal, бомба закрывает поздно.',
     bullets=[f'<b>Раннее:</b> connive-тела — {ref(110,"Red Room Recruit")}, {ref(44,"A.I.M. Scientists")}, '
              f'{ref(88,"Baron Strucker")}.',
              f'<b>Среднее:</b> {ref(217,"Kang, Temporal Tyrant")} и {ref(104,"Madame Masque")} '
              f'грайндят картами; {ref(64,"Leader")} усиливает connive в добор.',
              f'<b>Добивание:</b> {ref(62,"Kang the Conqueror")} (extra turn) или {ref(232,"Taskmaster")}.']),
   groups=[('🎯 Сигнпосты / пайоффы', [217, 232, 225, 214, 65]),
           ('🔮 Connive / draw-2', [44, 104, 110, 88, 64]),
           ('👿 Villain-value', [86, 103, 107, 250, 252]),
           ('🩸 Removal', [99, 93, 50, 54, 122]),
           ('👑 Топ / бомбы', [62, 233, 95, 217, 106])],
   traps=(f'⚠️ <b>Ловушки:</b> connive — это фильтр, не чистый добор: не утони в дискарде без пайоффов '
          f'({ref(64,"Leader")}, {ref(88,"Baron Strucker")}). Контролю нужен реальный финишер — не остановись '
          f'на value без бомбы.')),
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
# Панель: двусторонние мифики (DFC) — гибкие ранние пики
# ----------------------------------------------------------------------------
DFC_ROWS = [
 (80,  'Tony Stark // The Invincible Iron Man — артефактор флипается в бомбу-финишер', 'ядро UR'),
 (49,  'Bruce Banner // The Incredible Hulk — мирная сторона → 7/7 трампл-громила', 'ядро RG/любой G'),
 (18,  'Jennifer Walters // The Sensational She-Hulk — value-героиня → крупный финишер', 'ядро GW/RW'),
 (23,  'Monica Rambeau // Photon — флай-value, гибкая в любой Hero-деке', 'ядро WU/GW'),
 (219, 'King T’Challa // Black Panther — двойной удар/флеш, топ-сигнпост WU/GW', 'ядро WU/GW'),
]
def dfc_row(num, desc, pair):
    return (f'<div class="dfcrow">{card(num)}'
            f'<div class="dfctext">{desc} &nbsp;•&nbsp; <span class="pair">{pair}</span></div></div>')
PANEL_DFC = (
 '<section class="panel dfc"><h2>🔁 Двусторонние мифики (DFC) — гибкие ранние пики</h2>'
 '<p class="ptext"><b>Пять мифик-DFC:</b> вход слабой/гибкой стороной, флип в бомбу-финишер. '
 'Спекулятивный P1 — закрывают верх кривой почти любой деки. Бери высоко, цвет коммить не обязан.</p>'
 + ''.join(dfc_row(*r) for r in DFC_ROWS) + '</section>')

# ----------------------------------------------------------------------------
# Панель: «вторая карта/спелл за ход»
# ----------------------------------------------------------------------------
PANEL_SECOND = (
 '<section class="panel second"><h2>🃏 Паутина «второй карты за ход»</h2>'
 '<p class="ptext">Сквозная ось UG/UB: множество карт награждают за то, что ты '
 '<b>добрал вторую карту</b> (или скастил 2-й спелл) за ход. Считай «вторую карту» отдельным ресурсом — '
 'держи 4–6 дешёвых каунтрипов/добора, тогда движок (Ant-Man, Moon Girl, Roxxon) работает каждый ход.</p>'
 '<div class="scols">'
 '<div class="scol"><h4>⚡ Платят за 2-ю карту (пайоффы)</h4>'
 + grid([204, 45, 223, 47, 113, 90]) + '</div>'
 '<div class="scol"><h4>⚙️ Дешёвый добор / фильтр (энейблеры)</h4>'
 + grid([55, 79, 70, 110, 44, 158]) + '</div>'
 '</div></section>')

# ----------------------------------------------------------------------------
# Панель: keyword-математика
# ----------------------------------------------------------------------------
KW_ROWS = [
 ('+1/+1', 'Counters', 'Доминирующая ось сета (74 карты!). {ref0} удваивает раздачу, {ref1} ловит цепочку. Целься в плотность каунтер-синергии.', [164, 175, 192]),
 ('Villain', 'Трайбал', 'Триггеры «whenever a Villain enters». Токены 2/1 menace — топливо. {ref2} растёт, {ref3} дрейнит.', [91, 96, 221]),
 ('Hero', 'Трайбал', '«Other Heroes»/«attacks» баффы. Широкий или одиночка-вольтрон — выбери одно.', [4, 10, 207]),
 ('Power-up', 'Активация', 'Раз на способность: мана → большие +1/+1. Дорого без {ref4} (−стоимость / доп. активация).', [215, 159, 171]),
 ('Teamwork N', 'Доп. стоимость', 'Тапни существ с суммарной силой N → бонус. N=1–2 легко, 4+ хочет стол. Тёмп-окно.', [92, 122, 15]),
 ('Connive', 'Фильтр', 'Возьми-сбрось; нелэнд-сброс → +1/+1. Это фильтр, не чистый добор — нужен пайофф.', [217, 104, 64]),
 ('Plan', 'Чары-движок', 'Копят plan-счётчики (≈1/ход), отдают на X. Медленные как саги — нужен паффер/время.', [90, 127, 96]),
]
def kw_row(n, name, mean, ex):
    mean = (mean.replace('{ref0}', ref(164,'Doc Samson')).replace('{ref1}', ref(175,'Knight of Wundagore'))
            .replace('{ref2}', ref(91,'Crossbones')).replace('{ref3}', ref(96,'Doom Reigns'))
            .replace('{ref4}', ref(215,'Hulk')))
    return (f'<div class="kwrow"><div class="kwhead"><span class="kwn">{n}</span> <b>{name}</b></div>'
            f'<div class="kwmean">{mean}</div><div class="kwex">{"".join(card(x) for x in ex)}</div></div>')
PANEL_KW = ('<section class="panel kw"><h2>⚔️ Keyword-математика</h2>'
            + ''.join(kw_row(*r) for r in KW_ROWS) + '</section>')

# ----------------------------------------------------------------------------
# Панель: порядок пика / процесс
# ----------------------------------------------------------------------------
PROC = [
 ('🥇 P1–P4 (старт)', 'Бери СИЛУ: бомба/removal > всё. DFC-мифики и rare-легенды — спекулятивный 1-й пик. Цвет не коммить.'),
 ('🔀 P5–P9 (сигналы)', 'Поздний золотой сигнпост (BR Madame Hydra, UG Ant-Man) = пара <b>открыта</b>. Wheel (9+) = железный сигнал. К концу пака 1 — гипотеза по паре.'),
 ('📦 Бустер 2 (коммит)', 'Коммить пару в <b>середине пака 2</b> (стримерский тайминг): максимум сигналов, ещё ~20 пиков на глубину. Добирай кривую/фикс.'),
 ('📊 Приоритет', 'Bombs > Removal (его МАЛО) > Evasion/трампл > Engine (трайбал/counters/артефакты) > filler. Removal цени высоко — формат светлый на него.'),
 ('🎴 Состав', '~17 земель + 23 нонленда. Агро (BR/RW) скошен к 2–3 дропам. Counters/Power-up (UG/RG) — больше существ. Минимум 2–3 removal.'),
 ('🌈 Фикс / сплеш', f'Лайфгейн-тапленды (тип {ref(265,"Fisk Tower")}) и {ref(246,"Dependable Quinjet")}/{ref(153,"Stark Industries Exec")} (Treasure) дают 3-й цвет. Бомбы окупают сплеш.'),
 ('✋ Мулиган', 'Держи 2–4 земли + игру на 2–3 ход. Агро без дешёвых тел и Power-up/Counters без дешёвого старта — слабые руки.'),
]
def pcard(h, p):
    return f'<div class="pcard"><h4>{h}</h4><p>{p}</p></div>'
PANEL_PROC = ('<section class="panel proc"><h2>🧭 Порядок пика и процесс драфта</h2>'
              '<div class="pgrid">' + ''.join(pcard(*x) for x in PROC) + '</div></section>')

# ----------------------------------------------------------------------------
# Панель: комбо
# ----------------------------------------------------------------------------
COMBOS = [
 (164, 175, 'Doc Samson +1 ко всем счётчикам → Knight ловит каждый → цепная лавина +1/+1.'),
 (215, 159, 'Hulk даёт −3 к power-up: Volcanic/любое power-up тело качается почти даром.'),
 (91, 221, 'Madame Hydra делает Villain-токен с каждого Villain-спелла → Crossbones растёт каждый ход.'),
 (218, 85, 'Killmonger жертвует токен HYDRA → destroy nonland; токен заранее от Agents of HYDRA.'),
 (239, 36, 'Winter Soldier +2/+0 за каждую экипировку → S.H.I.E.L.D. Spy Kit/Super Suit = быстрый вольтрон.'),
 (204, 45, 'Astonishing Ant-Man +1/+1 за каждый добор; Atlantean Cavalry — за 2-ю карту → двойной рост.'),
 (216, 153, 'Iron Man +1/+0 за артефакт; Stark Exec штампует Treasure → растёт и фиксит ману.'),
 (210, 32, 'Cap Living Legend ловит каждый tap; Quake тапает на каждый noncreature → карты/value.'),
 (193, 192, 'Squirrel Girl плодит белок; Training Regimen даёт всем со счётчиками трампл → альфа.'),
 (207, 27, 'Black Panther на Hero-ETB; Okoye делает 2 солдат → ширина + раздача счётчиков.'),
]
def combo(a, b, desc):
    return (f'<div class="combo">{card(a)}<span class="plus">+</span>{card(b)}'
            f'<p class="cdesc">{desc}</p></div>')
PANEL_COMBOS = ('<section class="panel combos"><h2>🔗 Комбо-связки (знать наизусть)</h2>'
                '<div class="cgrid">' + ''.join(combo(*c) for c in COMBOS) + '</div></section>')

# ----------------------------------------------------------------------------
# Стиль (общий с SOS — set-agnostic)
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
.arch.br{border-top:4px solid #b5483a} .arch.ug{border-top:4px solid #4aa564}
.arch.rg{border-top:4px solid #c9772e} .arch.rw{border-top:4px solid #e0b04a}
.arch.bg{border-top:4px solid #6b8f4e} .arch.ur{border-top:4px solid #8a6fc7}
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
.card.miss{width:auto;color:#e07a7a;font-size:11px;border:1px dashed #7a3a3a;border-radius:6px;padding:2px 6px}
.card>img:first-of-type{width:76px;border-radius:6px;display:block;box-shadow:0 2px 6px rgba(0,0,0,.5);border:1px solid #2c3140;transition:border-color .15s}
.card:hover>img:first-of-type{border-color:#5b6bce}
.card .nm{display:block;font-size:10px;color:var(--mut);text-align:center;margin-top:3px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:76px}
.card .rb{position:absolute;top:3px;right:3px;background:#000a;border-radius:4px;font-size:9px;padding:1px 4px;font-weight:700}
.r-M .rb{color:#f5a623} .r-R .rb{color:#e8d27a} .r-U .rb{color:#cfd6e4} .r-C .rb{color:#9aa3b2}
.zoom{position:fixed;top:50%;right:24px;left:auto;transform:translateY(-50%);height:84vh;max-height:680px;width:auto;border-radius:18px;z-index:999;display:none;box-shadow:0 18px 60px rgba(0,0,0,.85);pointer-events:none}
.card:hover .zoom,.ref:hover .zoom{display:block}
.ref{color:#bcd0ff;text-decoration:none;border-bottom:1px dashed #4a5a80;cursor:help;position:relative;white-space:nowrap}
.ref.miss{color:#e07a7a;border-bottom-color:#7a3a3a} .ref:hover{color:#e8f0ff}
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
.dfctext{flex-basis:100%;font-size:12px;color:#c7cdda;margin-top:4px} .dfctext .pair{color:#bfe7e2;font-weight:600}
.scols{display:grid;grid-template-columns:1fr 1fr;gap:16px} @media(max-width:700px){.scols{grid-template-columns:1fr}}
.scol h4{margin:0 0 8px;font-size:14px;color:#cdd4e2}
.kwrow{display:grid;grid-template-columns:130px 1fr auto;gap:12px;align-items:center;background:#15181f;border:1px solid #262a34;border-radius:10px;padding:8px 10px;margin-bottom:8px}
@media(max-width:800px){.kwrow{grid-template-columns:1fr}}
.kwhead .kwn{display:inline-block;min-width:26px;text-align:center;background:#2a2410;color:#f0d28a;border-radius:6px;padding:1px 6px;font-weight:700;margin-right:4px}
.kwmean{font-size:12.5px;color:#c7cdda} .kwex{display:flex;gap:6px}
</style>"""
H1 = ('<h1>🦸 MSH Draft Cheat Sheet — 10 архетипов · DFC · counters/Villain/Hero · '
      'keyword-математика · комбо · порядок пика</h1>')
DISC = ('<div class="disc">📚 <b>Marvel Super Heroes · Arena 23.06.2026 / бумага 26.06.2026 · полный пул '
        f'(данные Scryfall, {len([c for c in DB.values() if "Land" not in c.get("type_line","")])} нонленд-карт + земли).</b> '
        'Драфтируемый сет в MTG Arena. Тексты карт точные. <b>17Lands GIH LIVE с 25.06</b> — '
        'актуальные тиры/числа в <code>msh_tier.md</code>, пары цветов в <code>msh_cheat.md</code>; этот лист — архетипы/механики/порядок пика. '
        'Обнови картинки: <code>python3 build_msh_cheatsheet.py</code>.</div>')
LEGEND = ('<p class="legend"><b>10 пар цветов = 10 архетипов.</b> Сквозные оси: '
          '🟦 <b>+1/+1 counters</b> (74 карты) · 👿 <b>Villain</b> / 🦸 <b>Hero</b> трайбал · '
          '💪 <b>Power-up</b> · 🤝 <b>Teamwork</b> · 🔮 <b>Connive</b> · 📜 <b>Plan</b>. '
          '<b>Наведи на карту</b> → увеличенный скан.</p>')

DOC = ('<!doctype html><html lang="ru"><head><meta charset="utf-8">'
       '<meta name="viewport" content="width=device-width,initial-scale=1">'
       '<title>MSH Draft Cheat Sheet</title>' + STYLE + '</head><body>'
       + H1 + DISC + LEGEND + ARCH_BLOCK
       + PANEL_DFC + PANEL_SECOND + PANEL_KW + PANEL_PROC + PANEL_COMBOS
       + '</body></html>')

open('msh_cheatsheet.html', 'w').write(DOC)
print('written msh_cheatsheet.html', len(DOC), 'bytes')
if _missing:
    print('!! MISSING collector numbers (нет в msh_set.json):', sorted(_missing))
else:
    print('OK — все ссылки на карты резолвятся')
