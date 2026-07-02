#!/usr/bin/env python3
"""Красивый HTML-разбор последней партии: по ходам — касты/смерти/изгнания,
БОИ (атаки/блоки с ТЕКУЩИМИ P/T, т.е. со счётчиками-фишками), картинки карт,
и блок «совет» под каждый ход (если есть replay_advice.json: {"<turn>": "текст"}).

  python3 replay_report.py [idx] [--set sos] [--out путь.html]
      idx: -1 последняя (по умолчанию), -2 предпоследняя …
  Совет берётся из replay_advice.json рядом со скриптом (необязателен).
Текущие P/T читаются из GRE (power.value/toughness.value уже включают фишки/пампы).
"""
import json, re, sys, os
import match_watch as mw

HERE = os.path.dirname(os.path.abspath(__file__))

def setcode():
    for a in sys.argv[1:]:
        if a in ("sos", "mkm"): return a
    return "sos"

def card_index(sc):
    """grpId(arena_id) -> {name, img, pt}"""
    out = {}
    f = os.path.join(HERE, f"{sc}_set.json")
    if not os.path.exists(f): return out
    for c in json.load(open(f)):
        aid = c.get("arena_id")
        if aid is None: continue
        img = (c.get("image_uris") or {}).get("normal") or (c.get("image_uris") or {}).get("small")
        pt = ""
        if "power" in c and "toughness" in c:
            pt = f"{c['power']}/{c['toughness']}"
        out[int(aid)] = {"name": c.get("name", f"id{aid}"), "img": img, "pt": pt}
    return out

def slice_game(txt, idx):
    seen, starts = set(), []
    for m in re.finditer(r'"matchID"\s*:\s*"([0-9a-f\-]+)"\s*,\s*"gameNumber"\s*:\s*(\d+)', txt):
        k = (m.group(1), m.group(2))
        if k in seen: continue
        seen.add(k)
        p0 = m.start()
        mm = re.search(r'GREMessageType_MulliganReq', txt[p0:p0 + 120000])
        inside = p0 + (mm.start() if mm else 0)
        a = txt.rfind('GameStateType_Full', max(0, inside - 80000), inside)
        if a == -1:
            a = txt.rfind('GREMessageType_GameStateMessage', max(0, inside - 80000), inside)
        starts.append(a if a != -1 else p0)
    starts = sorted(set(starts))
    if not starts: return None, 0
    n = len(starts); i = idx if idx >= 0 else n + idx
    if i < 0 or i >= n: return None, n
    return txt[starts[i]:(starts[i + 1] if i + 1 < n else len(txt))], n

def main():
    idx = -1; out_path = os.path.join(HERE, "replay_report.html")
    args = sys.argv[1:]
    for j, a in enumerate(args):
        if re.fullmatch(r'-?\d+', a): idx = int(a)
        if a == "--out" and j + 1 < len(args): out_path = args[j + 1]
    sc = setcode()
    txt = mw.read_logs(); names = mw.load_names(); CARDS = card_index(sc)
    last, n = slice_game(txt, idx)
    if not last:
        print(f"Игра не найдена (в логе {n})."); return

    from collections import Counter
    ss = re.findall(r'"systemSeatIds"\s*:\s*\[\s*(\d+)', last)
    me = int(Counter(ss).most_common(1)[0][0]) if ss else 1
    wins = re.findall(r'"winningTeamId"\s*:\s*(\d+)', last)
    res = ("ПОБЕДА" if int(wins[-1]) == me else "ПОРАЖЕНИЕ") if wins else "?"

    # grpId/iid helpers
    def gname(grp): return names.get(grp) or (CARDS.get(grp, {}).get("name")) or "жетон"
    def gimg(grp):  return CARDS.get(grp, {}).get("img")
    iid_grp = {}
    for m in re.finditer(r'"instanceId":\s*(\d+),\s*"grpId":\s*(\d+)', last):
        iid_grp[int(m.group(1))] = int(m.group(2))
    # текущие P/T по позиции: iid -> [(pos,pow,tou)]
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

    # ходы и жизни
    turn_pos = sorted((m.start(), int(m.group(1)), int(m.group(2)))
                      for m in re.finditer(r'"turnNumber"\s*:\s*(\d+)[^{}]*?"activePlayer"\s*:\s*(\d+)', last))
    def turn_at(pos):
        t = None
        for p, tn, _ in turn_pos:
            if p <= pos: t = tn
            else: break
        return t
    active = {tn: ap for _, tn, ap in turn_pos}
    life = {}; life_at = {}
    for m in re.finditer(r'"lifeTotal"\s*:\s*(\d+)[^{}]*?"systemSeatNumber"\s*:\s*(\d+)|'
                         r'"systemSeatNumber"\s*:\s*(\d+)[^{}]*?"lifeTotal"\s*:\s*(\d+)', last):
        if m.group(1): seat, hp = int(m.group(2)), int(m.group(1))
        else: seat, hp = int(m.group(3)), int(m.group(4))
        life[seat] = hp; t = turn_at(m.start())
        if t: life_at[t] = dict(life)

    # зоны/события
    zones = {int(z): zt for z, zt, _ in mw.RE_ZONE.findall(last)}
    gtype = {}
    for m in re.finditer(r'"grpId":\s*(\d+),[^{}]*?"cardTypes":\s*\[([^\]]*)\]', last):
        gtype.setdefault(int(m.group(1)), set()).update(re.findall(r'CardType_(\w+)', m.group(2)))
    LANDW = ('Island','Mountain','Swamp','Forest','Plains','Coast','Fields of Strife')
    PERM = {'Creature','Artifact','Enchantment','Planeswalker','Battle'}
    seen_stack=set(); seen_gy=set(); seen_ex=set(); per_turn={}
    for m in mw.RE_OBJ.finditer(last):
        iid, grp, zid, owner = int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4))
        t = turn_at(m.start());  zt = zones.get(zid)
        if not t or grp <= 0: continue
        nm = gname(grp); side = 'you' if owner == me else 'opp'
        ev = None
        if zt == 'ZoneType_Stack' and iid not in seen_stack:
            seen_stack.add(iid); ev = ('cast', side, grp, nm)
        elif zt == 'ZoneType_Graveyard' and iid not in seen_gy:
            seen_gy.add(iid)
            if not any(w in nm for w in LANDW): ev = ('die', side, grp, nm)
        elif zt == 'ZoneType_Exile' and iid not in seen_ex:
            seen_ex.add(iid)
            if (gtype.get(grp, set()) & PERM) and not any(w in nm for w in LANDW):
                ev = ('exile', side, grp, nm)
        if ev: per_turn.setdefault(t, []).append(ev)

    # бои
    atk = {}
    for m in re.finditer(r'"instanceId":\s*(\d+),\s*"grpId":\s*(\d+)'
                         r'.{0,400}?"attackState":\s*"AttackState_Declared"', last, re.S):
        atk.setdefault(turn_at(m.start()), {})[int(m.group(1))] = m.start()
    blk = {}
    for m in re.finditer(r'"instanceId":\s*(\d+),\s*"grpId":\s*(\d+).{0,400}?'
                         r'"blockState":\s*"BlockState_Declared",\s*"blockInfo":\s*\{\s*'
                         r'"attackerIds":\s*\[\s*(\d+)', last, re.S):
        blk.setdefault(turn_at(m.start()), []).append((int(m.group(1)), int(m.group(3)), m.start()))

    # ---- side label ----
    my_n = opp_n = 0; label = {}
    for t in sorted(active):
        if active[t] == me: my_n += 1; label[t] = f"твой ход #{my_n}"
        else: opp_n += 1; label[t] = f"ход соперника #{opp_n}"

    advice = {}
    af = os.path.join(HERE, "replay_advice.json")
    if os.path.exists(af):
        try: advice = json.load(open(af))
        except Exception: advice = {}

    # ---------- HTML ----------
    def chip(grp, iid=None, pos=None, extra=""):
        nm = gname(grp); img = gimg(grp)
        pt = cur_pt(iid, pos) if (iid and pos) else None
        ptbadge = f'<span class="pt">{pt[0]}/{pt[1]}</span>' if pt else ''
        inner = (f'<img src="{img}" loading="lazy">' if img
                 else f'<div class="token">{nm}<br><small>жетон</small></div>')
        return (f'<span class="card" title="{nm}">{inner}{ptbadge}'
                f'<span class="cname">{nm}{extra}</span></span>')

    rows = []
    allturns = sorted(set(per_turn) | set(atk) | set(blk) | set(life_at))
    for t in allturns:
        la = life_at.get(t, {}); opp = next((s for s in la if s != me), None)
        ev_html = []
        ICON = {'cast': '🪄', 'die': '✝', 'exile': '⊘'}
        for kind, side, grp, nm in per_turn.get(t, []):
            cls = 'you' if side == 'you' else 'opp'
            ev_html.append(f'<div class="ev {cls}">{ICON[kind]} <b>{"ты" if side=="you" else "опп"}</b> '
                           f'{ {"cast":"кастует","die":"умирает","exile":"изгнан"}[kind] } {chip(grp)}</div>')
        # combat
        combat_html = ""
        if atk.get(t) or blk.get(t):
            blocked = {ai for _, ai, _ in blk.get(t, [])}
            bmap = {}
            for bi, ai, bp in blk.get(t, []): bmap.setdefault(ai, []).append((bi, bp))
            atk_rows = []
            for aiid, apos in atk.get(t, {}).items():
                agrp = iid_grp.get(aiid, 0)
                got = aiid not in blocked
                tag = ' <span class="ok">✓ прошёл</span>' if got else ' <span class="blkd">заблокирован</span>'
                blockers = ''.join(chip(iid_grp.get(bi,0), bi, bp) for bi, bp in bmap.get(aiid, []))
                arrow = f'<span class="vs">⟶ блок:</span>{blockers}' if blockers else ''
                atk_rows.append(f'<div class="atkrow">{chip(agrp, aiid, apos, tag)}{arrow}</div>')
            combat_html = f'<div class="combat"><div class="ctitle">⚔ Бой</div>{"".join(atk_rows)}</div>'
        adv = advice.get(str(t))
        adv_html = f'<div class="advice"><b>💡 Совет:</b> {adv}</div>' if adv else ''
        youL = la.get(me, '?'); oppL = la.get(opp, '?')
        rows.append(f'''<section class="turn">
  <header><span class="tnum">Ход {t}</span><span class="tside">{label.get(t,"")}</span>
    <span class="life">❤ ты {youL} — опп {oppL}</span></header>
  <div class="body">{''.join(ev_html)}{combat_html}{adv_html}</div>
</section>''')

    css = """
*{box-sizing:border-box} body{font-family:-apple-system,Segoe UI,Roboto,sans-serif;background:#14161c;color:#e6e8ec;margin:0;padding:24px}
h1{font-size:22px;margin:0 0 4px} .sub{color:#9aa3b2;margin-bottom:20px}
.turn{background:#1c1f28;border:1px solid #2a2f3c;border-radius:12px;margin:0 0 14px;overflow:hidden}
.turn>header{display:flex;gap:14px;align-items:center;background:#222633;padding:10px 14px;border-bottom:1px solid #2a2f3c}
.tnum{font-weight:700} .tside{color:#9aa3b2;font-size:13px} .life{margin-left:auto;font-size:14px;color:#ffd479}
.body{padding:12px 14px} .ev{margin:4px 0;font-size:14px;display:flex;align-items:center;gap:6px}
.ev.opp{color:#ff9d9d} .ev.you{color:#9dd1ff}
.card{display:inline-flex;flex-direction:column;align-items:center;position:relative;margin:0 4px;vertical-align:middle}
.card img{height:46px;border-radius:4px;transition:transform .15s;box-shadow:0 1px 4px #0007}
.card:hover img{transform:scale(5.2);z-index:50;position:relative}
.card .cname{font-size:11px;color:#c7cdd8;max-width:90px;text-align:center;line-height:1.1;margin-top:2px}
.pt{position:absolute;bottom:16px;right:-4px;background:#000a;border:1px solid #ffd479;color:#ffd479;border-radius:6px;font-size:11px;padding:0 4px;font-weight:700}
.token{height:46px;width:38px;display:flex;flex-direction:column;justify-content:center;background:#33384a;border:1px dashed #5a627a;border-radius:4px;font-size:9px;text-align:center;padding:2px}
.combat{margin:10px 0;background:#191d27;border:1px solid #313748;border-radius:8px;padding:8px 10px}
.ctitle{font-weight:700;color:#ff8a5b;margin-bottom:6px} .atkrow{display:flex;align-items:center;flex-wrap:wrap;gap:6px;margin:6px 0;padding:4px;border-bottom:1px dashed #262b38}
.vs{color:#9aa3b2;font-size:12px;margin:0 4px} .ok{color:#6ee787;font-weight:700;font-size:12px} .blkd{color:#ff8f8f;font-size:12px}
.advice{margin-top:10px;background:#1b2a1e;border-left:3px solid #6ee787;border-radius:6px;padding:8px 10px;font-size:14px;color:#d7f5dd}
"""
    title = f"Разбор партии — {res}"
    html = f"""<!doctype html><html lang="ru"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title><style>{css}</style></head><body>
<h1>{title}</h1><div class="sub">Наведи на карту — увеличится. P/T показаны со счётчиками (фишками). ⚔ = бой, ✓ прошёл = без блока.</div>
{''.join(rows)}
</body></html>"""
    open(out_path, "w", encoding="utf-8").write(html)
    print(f"OK → {out_path}  ({len(allturns)} ходов, результат: {res})")

if __name__ == "__main__":
    main()
