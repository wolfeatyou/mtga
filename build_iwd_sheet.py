#!/usr/bin/env python3
import json, html

R = json.load(open('17l_msh_premierdraft.json'))
MIN_GAMES = 400  # sample threshold to kill noise

def pct(v): return v*100 if v is not None and v < 1.5 else v
rows=[]
for r in R:
    n = r.get('ever_drawn_game_count') or 0
    if n < MIN_GAMES: continue
    iwd = r.get('drawn_improvement_win_rate')
    gih = r.get('ever_drawn_win_rate')
    oh  = r.get('opening_hand_win_rate')
    if iwd is None or gih is None: continue
    rows.append({
        'name': r['name'],
        'color': r.get('color') or '',
        'rarity': (r.get('rarity') or '')[:1].upper(),
        'type': (r.get('types') or [''])[0],
        'iwd': iwd*100,
        'gih': pct(gih),
        'oh': pct(oh) if oh else None,
        'alsa': r.get('avg_seen'),
        'img': r.get('url') or '',
        'n': n,
    })
rows.sort(key=lambda x:-x['iwd'])
rows = rows[:80]

def tier(g):
    if g>=60:return('S','#8b5cf6')
    if g>=57.5:return('A','#3b82f6')
    if g>=55:return('B','#10b981')
    if g>=52.5:return('C','#eab308')
    if g>=50:return('D','#f97316')
    return('F','#ef4444')

CMAP={'W':'#f9e79f','U':'#5dade2','B':'#7d3c98','R':'#e74c3c','G':'#27ae60','':'#95a5a6'}
def colorchip(c):
    if not c: return '<span class="pip" style="background:#95a5a6">C</span>'
    return ''.join(f'<span class="pip" style="background:{CMAP.get(ch,"#95a5a6")};color:{"#111" if ch in "W" else "#fff"}">{ch}</span>' for ch in c)

def iwd_bg(v):
    # green scale for positive, red for negative
    if v>=8: return '#166534'
    if v>=5: return '#15803d'
    if v>=3: return '#3f6212'
    if v>=1: return '#4d5218'
    if v>=0: return '#57534e'
    return '#7f1d1d'

trs=[]
for i,r in enumerate(rows,1):
    t,tc=tier(r['gih'])
    oh = f"{r['oh']:.1f}" if r['oh'] is not None else '—'
    alsa = f"{r['alsa']:.1f}" if r['alsa'] is not None else '—'
    trs.append(f'''<tr data-img="{html.escape(r['img'])}">
      <td class="rank">{i}</td>
      <td class="name">{html.escape(r['name'])}<span class="type">{html.escape(r['type'])}</span></td>
      <td class="ci">{colorchip(r['color'])}</td>
      <td><span class="rar rar{r['rarity']}">{r['rarity']}</span></td>
      <td class="iwd" style="background:{iwd_bg(r['iwd'])}">{'+' if r['iwd']>=0 else ''}{r['iwd']:.1f}</td>
      <td><span class="tier" style="background:{tc}">{t}</span> {r['gih']:.1f}</td>
      <td class="dim">{oh}</td>
      <td class="dim">{alsa}</td>
    </tr>''')

HTML=f'''<!doctype html><html><head><meta charset="utf-8"><title>MSH — Top by IWD</title>
<style>
:root{{--bg:#0f1115;--card:#171a21;--line:#262b36;--txt:#e7e9ee;--dim:#9aa3b2}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--txt);font:14px/1.4 -apple-system,Segoe UI,Roboto,sans-serif;padding:24px}}
h1{{font-size:22px;margin:0 0 4px}}
.sub{{color:var(--dim);margin:0 0 16px;font-size:13px}}
.legend{{display:flex;gap:18px;flex-wrap:wrap;background:var(--card);border:1px solid var(--line);border-radius:10px;padding:10px 14px;margin-bottom:16px;font-size:12px;color:var(--dim)}}
.legend b{{color:var(--txt)}}
table{{border-collapse:collapse;width:100%;max-width:900px}}
th,td{{padding:7px 10px;text-align:left;border-bottom:1px solid var(--line)}}
th{{position:sticky;top:0;background:var(--bg);color:var(--dim);font-weight:600;font-size:11px;text-transform:uppercase;letter-spacing:.04em;z-index:2}}
tr:hover{{background:#1d222c}}
.rank{{color:var(--dim);width:34px;text-align:right;font-variant-numeric:tabular-nums}}
.name{{font-weight:600}}
.type{{display:block;color:var(--dim);font-weight:400;font-size:11px}}
.iwd{{font-weight:700;text-align:center;color:#fff;border-radius:6px;font-variant-numeric:tabular-nums;min-width:52px}}
.tier{{display:inline-block;width:20px;text-align:center;color:#fff;border-radius:5px;font-weight:700;font-size:12px}}
.dim{{color:var(--dim);font-variant-numeric:tabular-nums}}
.pip{{display:inline-block;width:18px;height:18px;line-height:18px;text-align:center;border-radius:50%;font-size:11px;font-weight:700;margin-right:2px}}
.rar{{display:inline-block;width:18px;text-align:center;border-radius:4px;font-size:11px;font-weight:700;color:#111}}
.rarM{{background:#e07b39}}.rarR{{background:#e9c46a}}.rarU{{background:#c0c7d1}}.rarC{{background:#8d99ae;color:#fff}}
#pv{{position:fixed;pointer-events:none;z-index:99;width:244px;border-radius:14px;box-shadow:0 10px 40px rgba(0,0,0,.6);display:none}}
</style></head><body>
<h1>MSH — Top-80 карт по IWD</h1>
<p class="sub">Marvel Super Heroes · Premier Draft · 17Lands (выборка ≥{MIN_GAMES} игр) · наведи на строку → картинка</p>
<div class="legend">
<span><b>IWD</b> — improvement when drawn: насколько лучше идёт партия, когда карту ВЫТЯНУЛ (потолок/импакт). Сортировка по нему.</span>
<span><b>GIH</b> — win% с картой в руке (+ тир).</span>
<span><b>OH</b> — win% в стартовой руке (пол).</span>
<span><b>ALSA</b> — средний пик, где её берут (чем ниже — тем раньше уходит).</span>
</div>
<table><thead><tr><th>#</th><th>Карта</th><th>Цвет</th><th>R</th><th>IWD</th><th>GIH·тир</th><th>OH</th><th>ALSA</th></tr></thead>
<tbody>{''.join(trs)}</tbody></table>
<img id="pv">
<script>
const pv=document.getElementById('pv');
document.querySelectorAll('tr[data-img]').forEach(tr=>{{
  tr.addEventListener('mouseenter',()=>{{const s=tr.dataset.img;if(s){{pv.src=s;pv.style.display='block'}}}});
  tr.addEventListener('mouseleave',()=>{{pv.style.display='none'}});
  tr.addEventListener('mousemove',e=>{{
    let x=e.clientX+22,y=e.clientY-120;
    if(x+250>innerWidth)x=e.clientX-266;
    if(y<8)y=8; if(y+340>innerHeight)y=innerHeight-346;
    pv.style.left=x+'px';pv.style.top=y+'px';
  }});
}});
</script></body></html>'''
open('msh_iwd_cheatsheet.html','w').write(HTML)
print(f'wrote msh_iwd_cheatsheet.html — {len(rows)} cards, top IWD: {rows[0]["name"]} {rows[0]["iwd"]:+.1f}')
