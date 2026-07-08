#!/usr/bin/env python3
import json, html
R = json.load(open('17l_msh_premierdraft.json'))
IMG = {r['name']: (r.get('url') or '') for r in R}
def find(name):
    if name in IMG: return IMG[name]
    for k in IMG:
        if k.split(',')[0].lower()==name.split(',')[0].lower(): return IMG[k]
    for k in IMG:
        if name.lower() in k.lower(): return IMG[k]
    return ''

# archetype data: (pair, colors, tier, theme, [key cards], plan_lines, note)
A=[
("WU","U W","60.9","Tap / темпо-контроль",
 ["Captain America, Living Legend","The Mighty Thor, Jane Foster","Quake, Agent of S.H.I.E.L.D.","Frozen in Ice"],
 ["<b>Роль:</b> контроль-темпо. Тапаешь/локаешь их атакёров (Frozen, Quake, Raft), гонишь по воздуху флаерами.",
  "Soft-removal пакет (Frozen in Ice, Super Villain Lockup) держит их угрозы; закрываешь эвейжном.",
  "Держи инстант-ответы на их ход; при лидерстве по жизни ты — контроль, не разменивай блокеры."],
 "Лучшая пара сета. White-глубина + синий tap/лок."),
("WG","W G","60.0","Heroes go-wide / counters",
 ["Black Panther, Vanguard","Okoye, Dora Milaje Leader","Borough Backup","Political Triumph"],
 ["<b>Роль:</b> го-вайд агро-мидрейндж. Заливаешь борд токенами/Heroes, пампишь всех (Cap Wings, Political Triumph).",
  "Okoye/Borough дают массу тел; +1/+1 темы усиливают альфа-страйк.",
  "Осторожно с оверэкстеншеном под свипы; держи один памп на алфу."],
 "Наш худший матчап, когда против нас. Командный памп = смертельный альфа."),
("UG","U G","58.7","Counters + «вторая карта»",
 ["Knight of Wundagore","Atlantean Cavalry","She-Hulk, Jade Defender","Beast, Erudite Aerialist"],
 ["<b>Роль:</b> темпо/грайнд на +1/+1. Растишь тела счётчиками, «draw 2nd card» триггеры (Cavalry, Roxxon) их усиливают.",
  "⚠ САМЫЙ ЧАСТЫЙ ЛИК: наземный мидрейндж БЕЗ неба/removal встаёт в стенку. Считай эвейжн≥2-3 И hard-removal≥2-3 отдельно.",
  "Финишёр — Stature (unblockable-памп) или флаер + Go Nuts/Punishing Punch (fight) как removal."],
 "Безопасная ось (counters почти всегда открыты), но требует эвейжн+removal, иначе 2:3."),
("WR","R W","58.4","Hero-агро",
 ["Agent Phil Coulson","Human Torch, Johnny Storm","Avengers Assemble!","Captain America, Wings of Freedom"],
 ["<b>Роль:</b> агрессия на Heroes. Скошенная вниз кривая, пейоффы за «attacks»/«other Heroes» (Coulson, Cap Wings).",
  "Выбери ЛИНИЮ: одиночка-вольтрон ИЛИ широкий борд — не мешай.",
  "Гони с руки, реаб мана на бёрн/памп; закрывай до их раскрутки."],
 "Быстрый Hero-агро; reach/памп добивает мимо блоков."),
("WB","W B","57.8","Equipment / вольтрон",
 ["S.H.I.E.L.D. Spy Kit","U.S.Agent, John Walker","Stolen Stark Tech","Captain America's Shield"],
 ["<b>Роль:</b> вольтрон-темпо. Одеваешь одно тело экипом (Spy Kit, Cap's Shield), пробиваешь + extort/дрейн (Kingpin).",
  "Winter Soldier/Swordsman платят за экипировку; эвейжн+экип = быстрый клок.",
  "Держи защиту носителя (Stark Tech indestructible) под их removal — вся дека на 1-2 телах."],
 "Хрупче (яйца в 1 корзине), но взрывной клок. Наша дека A — родня этой оси."),
("UB","U B","55.9","Connive / Villains / draw-контроль",
 ["Leader, Super-Genius","M.O.D.O.K.","Ghost, Spectral Saboteur","Trickster's Stratagem"],
 ["<b>Роль:</b> good-stuff темпо-контроль («be boring»). Removal + эвейжн + карт-преимущество (connive) + финишёр.",
  "Leader/M.O.D.O.K. — connive-движки (фильтр+рост); Trickster/Hour/Cruel Alliance — глубокий removal.",
  "Гони по воздуху, point-removal по их движкам, Stature/флаер закрывает. Инстанты — в ИХ ход."],
 "НАША трофейная ось (7:2). Высокий пол на фундаменте, не на хрупком движке."),
("BG","B G","54.6","Sacrifice / грайнд / яд",
 ["Killmonger, Scourge of Wakanda","The Coming of Galactus","Grim Reaper, Lethal Legionnaire","Undercover Skrull"],
 ["<b>Роль:</b> грайнд-вэлью. Sac-движки (Killmonger), реанимация (Grim Reaper), GY-value, лайфгейн, свипы (Galactus).",
  "Медленнее — выживай ранними блокерами, отвечай removal, вырывай длинную игру карт-преимуществом.",
  "Топ-энд (Galactus/Doom) закрывает; не проиграй агро до раскрутки."],
 "Грайнд-пара; при рарах (Galactus/Killmonger) потолок высокий."),
("UR","U R","53.4","Артефакты / спеллы",
 ["Iron Man, Master of Machines","HYDRA Assault Robot","Machinesmith Automaton","Vision Quest"],
 ["<b>Роль:</b> артефакт-темпо/пинг. «Artifact/Villain входит → урон» (HYDRA Robot), improvise, prowess-тела.",
  "Face-пинг (HYDRA Robot, Bullseye) добивает МИМО блоков — reach, которого нет у наземных дек.",
  "Гони + пингуй; движок-роботы — приоритет их removal против тебя."],
 "Пинг-агро; близко к нашему артефакт-комфорту (Stark Tech/Forge)."),
("RG","R G","~55","Power-up / большие тела",
 ["Wolverine, Fierce Fighter","Abomination, Terrifying Titan","Hulk, Gamma Goliath","Serpent Specialist"],
 ["<b>Роль:</b> агрессия крупными телами + power-up. Hulk удешевляет power-up; Wolverine/Abomination = fight-removal на теле.",
  "Не грузи дорогими power-up телами в чистое агро — медленно без удешевителя.",
  "Трампл/большие тела пробивают; fight-эффекты чистят блокеры."],
 "Реабилитирован (Wolverine/Hulk). Агро-мидрейндж."),
("BR","B R","50.7","Villains-агро",
 ["Avengers: Under Siege","The Ruinous Wrecking Crew","Madame Hydra","Bullseye, Death Dealer"],
 ["<b>Роль:</b> злодейский го-вайд + дрейн/бёрн. Токены 2/1 menace, «Villain входит» триггеры (Doom Reigns, Yellowjacket-лайфгейн).",
  "⚠ Слабейшая пара БЕЗ раров (50.7). Живёт только на топ-рарах (Under Siege 64!, Wrecking Crew).",
  "Пинг/дрейн (Bullseye, Yellowjacket) — reach + анти-race; но наземные menace не держат небо."],
 "Не садись без сигнпост-рара. Menace-токены проигрывают эвейжну."),
]

CMAP={'W':'#f9e79f','U':'#5dade2','B':'#7d3c98','R':'#e74c3c','G':'#27ae60'}
def chip(c):
    return ''.join(f'<span class="pip" style="background:{CMAP[ch]};color:{"#111" if ch=="W" else "#fff"}">{ch}</span>' for ch in c.split())
def tclr(t):
    try: v=float(str(t).replace('~',''))
    except: v=54
    if v>=60:return '#8b5cf6'
    if v>=58:return '#3b82f6'
    if v>=56:return '#10b981'
    if v>=54:return '#eab308'
    if v>=52:return '#f97316'
    return '#ef4444'

panels=[]
for pair,cols,tier,theme,cards,plan,note in A:
    cch=''
    for cn in cards:
        img=find(cn)
        cch+=f'<span class="cc" data-img="{html.escape(img)}">{html.escape(cn.split(",")[0])}</span>'
    plh=''.join(f'<li>{p}</li>' for p in plan)
    panels.append(f'''<div class="panel">
      <div class="ph"><span class="pair">{chip(cols)} {pair}</span>
        <span class="tier" style="background:{tclr(tier)}">{tier}</span>
        <span class="theme">{html.escape(theme)}</span></div>
      <div class="cards">{cch}</div>
      <ul class="plan">{plh}</ul>
      <div class="note">💡 {html.escape(note)}</div>
    </div>''')

HTML=f'''<!doctype html><html><head><meta charset="utf-8"><title>MSH — Архетипы</title><style>
:root{{--bg:#0f1115;--card:#171a21;--line:#262b36;--txt:#e7e9ee;--dim:#9aa3b2}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--txt);font:14px/1.45 -apple-system,Segoe UI,Roboto,sans-serif;padding:24px}}
h1{{font-size:23px;margin:0 0 4px}}.sub{{color:var(--dim);margin:0 0 18px;font-size:13px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(420px,1fr));gap:16px;max-width:1300px}}
.panel{{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:16px 18px}}
.ph{{display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin-bottom:10px}}
.pair{{font-size:18px;font-weight:800}}
.tier{{color:#fff;font-weight:800;border-radius:6px;padding:2px 9px;font-size:13px}}
.theme{{color:var(--dim);font-size:13px;font-weight:600}}
.cards{{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:10px}}
.cc{{background:#20252f;border:1px solid var(--line);border-radius:7px;padding:4px 9px;font-size:12px;font-weight:600;cursor:pointer;transition:.1s}}
.cc:hover{{background:#2b3240;border-color:#3b82f6}}
.plan{{margin:0 0 10px;padding-left:18px}}.plan li{{margin:4px 0;font-size:13px}}
.plan b{{color:#fff}}
.note{{color:var(--dim);font-size:12.5px;border-top:1px solid var(--line);padding-top:8px}}
.pip{{display:inline-block;width:20px;height:20px;line-height:20px;text-align:center;border-radius:50%;font-size:12px;font-weight:800;margin-right:1px}}
#pv{{position:fixed;pointer-events:none;z-index:99;width:250px;border-radius:14px;box-shadow:0 12px 44px rgba(0,0,0,.7);display:none}}
.tl{{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:10px 14px;margin-bottom:18px;font-size:12.5px;color:var(--dim);max-width:1300px}}
.tl b{{color:var(--txt)}}
</style></head><body>
<h1>MSH — Топ архетипов: карты + как играть</h1>
<p class="sub">Marvel Super Heroes · пары по тиру (17L pair-WR) · наведи на карту → картинка</p>
<div class="tl"><b>Тир пар (17L):</b> 🥇 WU 60.9 · WG 60.0 · UG 58.7 · WR 58.4 · WB 57.8 · UB 55.9 · BG 54.6 · UR 53.4 · 🚫 BR 50.7.
&nbsp;<b>При сомнении — тянись в White</b> (все 4 белые пары ≥57.8). <b>Removal цени высоко</b> (формат светлый на removal). <b>Counters (UG/GW/RG)</b> — самая безопасная/открытая ось.</div>
<div class="grid">{''.join(panels)}</div><img id="pv">
<script>
const pv=document.getElementById('pv');
document.querySelectorAll('.cc[data-img]').forEach(el=>{{
  el.addEventListener('mouseenter',()=>{{if(el.dataset.img){{pv.src=el.dataset.img;pv.style.display='block'}}}});
  el.addEventListener('mouseleave',()=>pv.style.display='none');
  el.addEventListener('mousemove',e=>{{let x=e.clientX+20,y=e.clientY-140;if(x+256>innerWidth)x=e.clientX-272;if(y<8)y=8;if(y+348>innerHeight)y=innerHeight-354;pv.style.left=x+'px';pv.style.top=y+'px';}});
}});
</script></body></html>'''
open('msh_archetypes.html','w').write(HTML)
miss=[cn for _,_,_,_,cards,_,_ in A for cn in cards if not find(cn)]
print('wrote msh_archetypes.html — 10 archetypes')
if miss: print('no image for:', miss)
