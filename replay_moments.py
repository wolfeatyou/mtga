#!/usr/bin/env python3
"""Разбор ТОП-N моментов партии: на каждый момент — ПОЗИЦИЯ (твоя рука + твой борд +
борд соперника, с текущими P/T = со счётчиками) и под ней ТЕКСТОВЫЙ разбор.

  python3 replay_moments.py [idx] --turns 7,18,19
  Тексты разбора берутся из replay_moments.json: {"7":"...", "18":"...", ...}
  Снимок позиции делается НА НАЧАЛО хода (до твоих действий) — то, что ты видел, решая.
"""
import json, re, sys, os
import match_watch as mw

HERE = os.path.dirname(os.path.abspath(__file__))

def setcode():
    for a in sys.argv[1:]:
        if a in ("sos", "mkm", "msh"): return a
    return "msh"

def card_index(sc):
    out = {}
    f = os.path.join(HERE, f"{sc}_set.json")
    if os.path.exists(f):
        for c in json.load(open(f)):
            aid = c.get("arena_id")
            if aid is None: continue
            iu = c.get("image_uris") or {}
            rec = {"name": c.get("name", f"id{aid}"),
                   "img": iu.get("normal") or iu.get("small")}
            out[int(aid)] = rec
            # also index by NAME: log grpId != set arena_id, so image lookup
            # by grpId misses; name (resolved from the log) is the reliable key.
            if c.get("name"): out[c["name"]] = rec
    return out

def slice_game(txt, idx):
    seen, starts = set(), []
    for m in re.finditer(r'"matchID"\s*:\s*"([0-9a-f\-]+)"\s*,\s*"gameNumber"\s*:\s*(\d+)', txt):
        k = (m.group(1), m.group(2))
        if k in seen: continue
        seen.add(k); p0 = m.start()
        mm = re.search(r'GREMessageType_MulliganReq', txt[p0:p0 + 120000])
        inside = p0 + (mm.start() if mm else 0)
        a = txt.rfind('GameStateType_Full', max(0, inside - 80000), inside)
        if a == -1: a = txt.rfind('GREMessageType_GameStateMessage', max(0, inside - 80000), inside)
        starts.append(a if a != -1 else p0)
    starts = sorted(set(starts))
    if not starts: return None
    n = len(starts); i = idx if idx >= 0 else n + idx
    if i < 0 or i >= n: return None
    return txt[starts[i]:(starts[i + 1] if i + 1 < n else len(txt))]

def main():
    idx = -1; turns = []
    args = sys.argv[1:]
    for j, a in enumerate(args):
        if re.fullmatch(r'-?\d+', a): idx = int(a)
        if a == "--turns" and j + 1 < len(args):
            turns = [int(x) for x in re.findall(r'\d+', args[j + 1])]
    sc = setcode()
    txt = mw.read_logs(); names = mw.load_names(); CARDS = card_index(sc)
    last = slice_game(txt, idx)
    if not last: print("Игра не найдена."); return
    from collections import Counter
    ss = re.findall(r'"systemSeatIds"\s*:\s*\[\s*(\d+)', last)
    me = int(Counter(ss).most_common(1)[0][0]) if ss else 1

    # позиция начала хода T: cut по маркеру turnNumber==T (твой ход)
    def turn_cut(T):
        for m in re.finditer(r'"turnNumber"\s*:\s*' + str(T) + r'\b', last):
            return m.start()
        return None
    # текущие P/T по позиции
    ptlog = {}
    for m in re.finditer(r'"instanceId":\s*(\d+),\s*"grpId":\s*\d+.{0,400}?'
                         r'"power":\s*\{\s*"value":\s*(\d+)\s*\}[^{}]{0,80}?'
                         r'"toughness":\s*\{\s*"value":\s*(\d+)', last, re.S):
        ptlog.setdefault(int(m.group(1)), []).append((m.start(), int(m.group(2)), int(m.group(3))))
    def cur_pt(iid, pos):
        best = None
        for p, pw, tu in ptlog.get(iid, []):
            if p <= pos: best = (pw, tu)
        return best
    gtype = {}
    for m in re.finditer(r'"grpId":\s*(\d+),[^{}]*?"cardTypes":\s*\[([^\]]*)\]', last):
        gtype.setdefault(int(m.group(1)), set()).update(re.findall(r'CardType_(\w+)', m.group(2)))
    def is_land(grp): return 'Land' in gtype.get(grp, set())
    def is_creature(grp): return 'Creature' in gtype.get(grp, set())
    def gname(grp): return names.get(grp) or CARDS.get(grp, {}).get("name") or "жетон"
    def gimg(grp):  return CARDS.get(grp, {}).get("img") or CARDS.get(gname(grp), {}).get("img")

    moments = json.load(open(os.path.join(HERE, "replay_moments.json"))) \
        if os.path.exists(os.path.join(HERE, "replay_moments.json")) else {}

    def chip(grp, iid, pos):
        nm = gname(grp); img = gimg(grp); pt = cur_pt(iid, pos)
        ptb = f'<span class="pt">{pt[0]}/{pt[1]}</span>' if pt else ''
        inner = (f'<img src="{img}" loading="lazy">' if img
                 else f'<div class="tok">{nm}</div>')
        return f'<span class="card" title="{nm}">{inner}{ptb}<span class="cn">{nm}</span></span>'

    blocks = []
    for T in turns:
        cut = turn_cut(T)
        if cut is None: continue
        # позиция = состояние НА начало твоего хода (после untap/draw). Берём срез до
        # первого каста/боя этого хода, чтобы рука была ДО твоих действий.
        nxt = re.search(r'"attackState"|"instanceId":\s*\d+,\s*"grpId":\s*\d+[^{}]*?'
                        r'"zoneId":\s*\d+[^{}]*?ZoneType_Stack', last[cut:cut + 60000])
        win_end = cut + 12000  # окно после старта хода
        st = mw.parse_state(last[:win_end])
        z = st["zones"]; objs = st["objs"]; life = st["life"]
        opp = next((s for s in (set(life) | {o['owner'] for o in objs.values()}) if s != me), None)
        def zone_cards(seat, ztype, by='owner'):
            r = []
            for iid, o in objs.items():
                zt, _ = z.get(o['zid'], (None, None))
                if zt == ztype and o[by] == seat and o['grp'] > 0:
                    r.append((iid, o['grp']))
            return r
        hand = zone_cards(me, 'ZoneType_Hand')
        my_bf = [(i, g) for i, g in zone_cards(me, 'ZoneType_Battlefield', 'ctrl') if not is_land(g)]
        op_bf = [(i, g) for i, g in zone_cards(opp, 'ZoneType_Battlefield', 'ctrl') if not is_land(g)]
        my_lands = sum(1 for i, g in zone_cards(me, 'ZoneType_Battlefield', 'ctrl') if is_land(g))

        def render(cards):
            return "".join(chip(g, i, win_end) for i, g in cards) or '<span class="empty">—</span>'
        adv = moments.get(str(T), "(нет разбора)")
        blocks.append(f'''<section class="moment">
  <header><span class="mt">Ход {T}</span>
    <span class="life">❤ ты {life.get(me,'?')} — опп {life.get(opp,'?')}</span>
    <span class="lands">земель у тебя: {my_lands}</span></header>
  <div class="pos">
    <div class="row"><div class="lab">🟥 Борд соперника</div><div class="cards">{render(op_bf)}</div></div>
    <div class="row"><div class="lab">🟦 Твой борд</div><div class="cards">{render(my_bf)}</div></div>
    <div class="row opp"><div class="lab">🃏 Твоя рука</div><div class="cards">{render(hand)}</div></div>
  </div>
  <div class="analysis"><b>📝 Разбор:</b><br>{adv}</div>
</section>''')

    css = """
*{box-sizing:border-box}body{font-family:-apple-system,Segoe UI,Roboto,sans-serif;background:#13151b;color:#e7e9ee;margin:0;padding:26px;max-width:1000px;margin:auto}
h1{font-size:22px;margin:0 0 18px}
.moment{background:#1b1e27;border:1px solid #2b3140;border-radius:14px;margin:0 0 20px;overflow:hidden}
.moment>header{display:flex;gap:16px;align-items:center;background:#232838;padding:11px 16px;font-weight:700}
.life{margin-left:auto;color:#ffd479;font-weight:600}.lands{color:#9aa3b2;font-size:13px;font-weight:400}
.pos{padding:10px 16px}.row{display:flex;align-items:flex-start;gap:12px;padding:8px 0;border-bottom:1px dashed #262c3a}
.row.opp{border-bottom:none}.lab{min-width:130px;color:#aab2c2;font-size:13px;padding-top:14px}
.cards{display:flex;flex-wrap:wrap;gap:8px}
.card{display:inline-flex;flex-direction:column;align-items:center;position:relative}
.card img{height:128px;border-radius:7px;box-shadow:0 2px 7px #0009;transition:transform .15s}
.card:hover img{transform:scale(2.6);z-index:60;position:relative}
.card .cn{font-size:12px;color:#c2c9d6;max-width:120px;text-align:center;line-height:1.15;margin-top:3px}
.pt{position:absolute;bottom:22px;right:-6px;background:#000b;border:1px solid #ffd479;color:#ffd479;border-radius:7px;font-size:13px;padding:1px 6px;font-weight:700}
.tok{height:128px;width:92px;display:flex;align-items:center;justify-content:center;text-align:center;background:#333a4d;border:1px dashed #5a627a;border-radius:7px;font-size:12px;padding:6px}
.empty{color:#6b7280;padding-top:20px}
.analysis{margin:6px 16px 16px;background:#1d2a1f;border-left:3px solid #6ee787;border-radius:8px;padding:12px 14px;font-size:15px;line-height:1.5;color:#dcf5e2}
"""
    # --- ШАПКА: обзор + ключевые моменты (из replay_moments.json спецключей) ---
    overview = moments.get("_overview", "")
    keys = moments.get("_keymoments", [])
    if isinstance(keys, str): keys = [keys]
    header = ""
    if overview or keys:
        kitems = "".join(f"<li>{k}</li>" for k in keys)
        header = f'''<section class="overview">
  {f'<div class="ov-text"><b>📖 Обзор партии:</b> {overview}</div>' if overview else ''}
  {f'<div class="ov-key"><b>🔑 Ключевые моменты:</b><ul>{kitems}</ul></div>' if kitems else ''}
</section>'''
    css_extra = """
.overview{background:#1a2230;border:1px solid #33415a;border-radius:14px;padding:16px 18px;margin:0 0 20px;line-height:1.55}
.ov-text{font-size:15px;color:#dbe6f5;margin-bottom:10px}
.ov-key{font-size:14px;color:#c2cdde}.ov-key ul{margin:6px 0 0;padding-left:22px}.ov-key li{margin:3px 0}
"""
    html = f"""<!doctype html><html lang="ru"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Разбор партии</title>
<style>{css}{css_extra}</style></head><body><h1>Разбор партии</h1>
{header}
<h2 style="font-size:18px;margin:22px 0 12px;color:#ff9d6e">⚠ Топ-{len(blocks)} ошибки</h2>
<p style="color:#9aa3b2;margin:-6px 0 16px">Наведи на карту — увеличится. P/T со счётчиками (фишками).</p>
{''.join(blocks)}</body></html>"""
    out = os.path.join(HERE, "replay_moments.html")
    open(out, "w", encoding="utf-8").write(html)
    print(f"OK → {out}  (моментов: {len(blocks)})")

if __name__ == "__main__":
    main()
