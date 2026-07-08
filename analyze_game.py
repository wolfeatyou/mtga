#!/usr/bin/env python3
"""Пост-гейм разбор последней игры из Player.log (зачаток пункта #6 timeline).
  python3 analyze_game.py          — последняя игра
  python3 analyze_game.py -2       — предпоследняя (индекс Full-маркера с конца)
Реконструирует: результат, таймлайн жизней, события по ходам, ключевые карты.
Оговорка: видит игру с последнего GameStateType_Full (ресинк/старт) — ранние ходы
могут быть за срезом, если лог ротировался."""
import re, sys
import match_watch as mw

def main():
    idx = -1
    for a in sys.argv[1:]:
        if re.fullmatch(r'-?\d+', a):
            idx = int(a)
    txt = mw.read_logs(); names = mw.load_names()
    id_by_name = {v: k for k, v in names.items()}
    # Игры считаем по уникальной паре (matchID, gameNumber) — это работает и для
    # современного лога, где партия идёт на GameStateType_Diff, а GameStateType_Full
    # пишется редко. Старт каждой игры якорим к её первому игровому снимку (до мулигана),
    # чтобы видеть стартовую руку: ближайший слева Full, иначе ближайший GameStateMessage.
    fulls = [m.start() for m in re.finditer('GameStateType_Full', txt)]
    seen = set(); starts = []
    for m in re.finditer(r'"matchID"\s*:\s*"([0-9a-f\-]+)"\s*,\s*"gameNumber"\s*:\s*(\d+)', txt):
        key = (m.group(1), m.group(2))
        if key in seen:
            continue
        seen.add(key)
        p0 = m.start()
        mm = re.search(r'GREMessageType_MulliganReq', txt[p0:p0 + 120000])
        inside = p0 + (mm.start() if mm else 0)
        a = txt.rfind('GameStateType_Full', max(0, inside - 80000), inside)
        if a == -1:
            a = txt.rfind('GREMessageType_GameStateMessage', max(0, inside - 80000), inside)
        starts.append(a if a != -1 else p0)
    if not starts:  # fallback на старый формат (лог только из Full-снимков)
        starts = [p for k, p in enumerate(fulls)
                  if (lambda gs: gs and int(gs.group(1)) <= 3)(
                      re.search(r'"gameStateId"\s*:\s*(\d+)',
                                txt[p:(fulls[k + 1] if k + 1 < len(fulls) else len(txt))]))]
        if not starts:
            starts = fulls
    starts.sort()
    if not starts:
        print("Игр в логе нет (детальный GRE-лог отсутствует — включи Detailed Logs)."); return
    n = len(starts)
    i = idx if idx >= 0 else n + idx
    if i < 0 or i >= n:  # явная ошибка вместо тихого схлопывания в крайнюю игру
        print(f"В логе только {n} детальн{'ая игра' if n == 1 else 'ых игр'}: "
              f"индекс {idx} вне диапазона (допустимо -{n}..{n - 1})."); return
    start = starts[i]
    end = starts[i + 1] if i + 1 < n else len(txt)
    last = txt[start:end]
    # место — ПЕР-ГЕЙМ: systemSeatIds в слайсе = адресат сообщений = я.
    # (глобальный get_my_seat берёт место из 1-й игры лога и врёт в поздних партиях,
    #  где твой seat сменился play/draw.)
    from collections import Counter
    ss = re.findall(r'"systemSeatIds"\s*:\s*\[\s*(\d+)', last)
    me = int(Counter(ss).most_common(1)[0][0]) if ss else mw.get_my_seat(txt)

    # результат
    wins = re.findall(r'"winningTeamId"\s*:\s*(\d+)', last)
    res = "?"
    if wins:
        res = "ПОБЕДА" if int(wins[-1]) == me else "ПОРАЖЕНИЕ"
    turns = [int(x) for x in re.findall(r'"turnNumber"\s*:\s*(\d+)', last)]
    print(f"Игр в логе: {len(starts)} | разбираю #{idx} | seat={me} | "
          f"результат: {res} | ходов: {max(turns) if turns else '?'}")

    # --- стартовая рука + мулиган ---
    hz = None
    for m in re.finditer(r'"zoneId":\s*(\d+),\s*"type":\s*"ZoneType_Hand",'
                         r'\s*"visibility":[^,]*,\s*"ownerSeatId":\s*(\d+)', last):
        if int(m.group(2)) == me:
            hz = int(m.group(1)); break
    objre = re.compile(r'"instanceId":\s*(\d+),\s*"grpId":\s*(\d+),[^{}]*?'
                       r'"zoneId":\s*(\d+),[^{}]*?"ownerSeatId":\s*(\d+)')
    req = re.search(r'GREMessageType_MulliganReq', last)
    win = last[:req.start()] if req else last[:40000]
    hand = {}
    for m in objre.finditer(win):
        iid, grp, zid, owner = map(int, m.groups())
        if zid == hz and owner == me and grp > 0:
            hand[iid] = grp
    from collections import Counter
    # земли (вкл. базовые) определяем по cardTypes из ЛОГА, а не по имени:
    # у базовых земель свой grpId на каждый арт, и их нет в *_set.json, поэтому
    # по имени они не находились и стартовая рука показывала «0 земель».
    SUB = {'Plains':'Plains','Island':'Island','Swamp':'Swamp',
           'Mountain':'Mountain','Forest':'Forest'}
    landgrp, landname = {}, {}
    for m in re.finditer(r'"grpId":\s*(\d+)\b((?:[^{}]|\{[^{}]*\})*?"cardTypes":\s*\[[^\]]*\])', last):
        g, blob = int(m.group(1)), m.group(2)
        if 'CardType_Land' in blob:
            landgrp[g] = True
            if g not in names:  # дать бейсику имя по subtype, иначе «Земля»
                sub = re.search(r'SubType_(\w+)', blob)
                landname[g] = SUB.get(sub.group(1), 'Земля') if sub else 'Земля'

    def hname(g):
        return names.get(g) or landname.get(g) or f'id{g}'
    hc = Counter(hname(g) for g in hand.values())
    decisions = re.findall(r'MulliganOption_(\w+)', last)
    my_dec = decisions[0] if decisions else "?"
    opp_mull = re.search(r'"mulliganCount":\s*([1-9])', last)
    print(f"\nСТАРТОВАЯ РУКА ({sum(hc.values())} карт) — решение: {my_dec}"
          + (f" | соперник мулиганил" if opp_mull else ""))
    lands = sum(1 for g in hand.values()
                if g in landgrp
                or any(w in names.get(g, '') for w in
                       ('Plains','Island','Swamp','Mountain','Forest')))
    for nm, n in sorted(hc.items(), key=lambda x: -x[1]):
        print(f"  {n}x {nm}" if n > 1 else f"  {nm}")
    if hc:
        print(f"  → земель: {lands} / спеллов: {sum(hc.values())-lands}")

    # карта зон
    zones = {int(z): zt for z, zt, _ in mw.RE_ZONE.findall(last)}
    land_words = ('Island','Mountain','Swamp','Forest','Plains','Coast','Fields of Strife')
    # типы по grpId — чтобы в exile показывать только перманенты (не flashback-инстанты/импульс)
    gtype = {}
    for m in re.finditer(r'"grpId":\s*(\d+),[^{}]*?"cardTypes":\s*\[([^\]]*)\]', last):
        gtype.setdefault(int(m.group(1)), set()).update(re.findall(r'CardType_(\w+)', m.group(2)))
    PERM = {'Creature', 'Artifact', 'Enchantment', 'Planeswalker', 'Battle'}

    # grpId → имя через overlayGrpId: токены/копии/альт-арты приходят с grpId,
    # которого нет в наборе, а реальная карта указана в overlayGrpId.
    alias = {}
    for m in re.finditer(r'"grpId":\s*(\d+)[^{}]*?"overlayGrpId":\s*(\d+)', last):
        g, ov = int(m.group(1)), int(m.group(2))
        if g not in names and ov in names:
            alias[g] = names[ov]

    def rname(grp):  # имя карты с учётом overlay-псевдонимов
        if not grp or grp <= 0:
            return None
        return names.get(grp) or alias.get(grp)

    # ОПИСАТЕЛЬНЫЙ ФОЛБЭК для карт, которых нет в *_set.json (напр. OM1 «Through the
    # Omenpaths» — Scryfall пока без arena_id). Вместо «неопознанный спелл grpN»
    # собираем тип/цвет/сет прямо из лога: грубо, но читаемо.
    COLOR = {'White': 'W', 'Blue': 'U', 'Black': 'B', 'Red': 'R', 'Green': 'G'}
    TYPE_RU = [('Creature', 'существо'), ('Planeswalker', 'планесвокер'),
               ('Enchantment', 'чары'), ('Artifact', 'артефакт'),
               ('Land', 'земля'), ('Battle', 'битва'),
               ('Instant', 'инстант'), ('Sorcery', 'колдовство')]
    gcolor, gset = {}, {}
    for m in re.finditer(r'"grpId":\s*(\d+),[^{}]{0,260}?"color":\s*\[([^\]]*)\]', last):
        gcolor.setdefault(int(m.group(1)), re.findall(r'CardColor_(\w+)', m.group(2)))
    for m in re.finditer(r'"grpId":\s*(\d+),[^{}]{0,320}?"skinCode":\s*"([A-Za-z0-9]+)_', last):
        gset.setdefault(int(m.group(1)), m.group(2))

    def dname(grp):  # имя, иначе описание из лога, иначе None (→ токен/«жетон»)
        n = rname(grp)
        if n or not grp or grp <= 0:
            return n
        st = gset.get(grp)
        if not st:               # без skinCode это реальный токен — пусть будет «жетон»
            return None
        ts = gtype.get(grp, set())
        tp = next((ru for en, ru in TYPE_RU if en in ts), 'карта')
        cl = ''.join(COLOR[c] for c in gcolor.get(grp, []) if c in COLOR)
        tag = ' · '.join(x for x in (cl, st) if x)
        return f'⟨{tp}{" · " + tag if tag else ""} · без имени⟩'

    # БАГ-ФИКС: способность, попавшая на СТЕК, получает стековый объект с grpId =
    # id СПОСОБНОСТИ (а не картой). Раньше она печаталась как «неизв. заклинание»
    # и выглядела фантомным «движком каждый ход». Распознаём её по типу объекта
    # GameObjectType_Ability и берём карту-источник из objectSourceGrpId (с тем же
    # описательным фолбэком для карт вне *_set.json, напр. OM1).
    ability = {}  # grpId способности -> имя карты-источника
    for m in re.finditer(r'"grpId":\s*(\d+),\s*"type":\s*"GameObjectType_Ability"'
                         r'.{0,400}?"objectSourceGrpId":\s*(\d+)', last):
        g, src = int(m.group(1)), int(m.group(2))
        ability[g] = dname(src) or f"id{src}"

    # события по позиции
    ev = []
    for m in re.finditer(r'"turnNumber"\s*:\s*(\d+)[^{}]*?"activePlayer"\s*:\s*(\d+)', last):
        ev.append((m.start(), 'turn', (int(m.group(1)), int(m.group(2)))))
    for m in mw.RE_OBJ.finditer(last):
        ev.append((m.start(), 'obj', (int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4)))))
    for m in re.finditer(r'"lifeTotal"\s*:\s*(\d+)[^{}]*?"systemSeatNumber"\s*:\s*(\d+)|'
                         r'"systemSeatNumber"\s*:\s*(\d+)[^{}]*?"lifeTotal"\s*:\s*(\d+)', last):
        if m.group(1): ev.append((m.start(), 'life', (int(m.group(2)), int(m.group(1)))))
        else: ev.append((m.start(), 'life', (int(m.group(3)), int(m.group(4)))))
    ev.sort(key=lambda x: x[0])

    cur = (0, None); life = {}; life_at = {}
    seen_stack=set(); seen_bf=set(); seen_gy=set(); seen_ex=set(); per_turn={}; turn_active={}
    from collections import Counter as _Counter
    ability_use = _Counter()  # (side, имя_источника) -> сколько раз способность шла на стек
    def add(t, s): per_turn.setdefault(t, []).append(s)
    for pos, kind, p in ev:
        if kind == 'turn':
            cur = p; turn_active[p[0]] = p[1]
        elif kind == 'life':
            seat, hp = p; life[seat] = hp
            if cur[0]: life_at[cur[0]] = dict(life)
        elif kind == 'obj':
            iid, grp, zid, owner = p; t, _ = cur
            if not t: continue
            zt = zones.get(zid); side = 'ты' if owner == me else 'опп'
            name = rname(grp)
            if zt == 'ZoneType_Stack' and iid not in seen_stack:
                seen_stack.add(iid)
                # БАГ-ФИКС: способность на стеке (GameObjectType_Ability) — это НЕ
                # каст карты. Показываем её как ⚡способность с источником и считаем
                # повторы (lifelink/триггер-движки), а не как «неизв. заклинание».
                if grp in ability:
                    add(t, f'  {side}: ⚡ способность — {ability[grp]}')
                    ability_use[(side, ability[grp])] += 1
                else:
                    dn = dname(grp)
                    if dn:
                        add(t, f'  {side}: кастует {dn}')
                    elif 0 < grp < 200000:
                        add(t, f'  {side}: кастует ⟨неопознанный спелл grp{grp}⟩')
            elif zt == 'ZoneType_Battlefield' and iid not in seen_bf:
                seen_bf.add(iid)
                if grp in ability: continue
                # ЗЕМЛИ не печатаем (шум): базовые земли не в *_set.json и не имеют
                # имени, поэтому фильтр по land_words их пропускал и они выпадали в
                # «жетон». landgrp (по cardTypes из лога) ловит и базовые, и нестд.
                if grp in landgrp or (name and any(w in name for w in land_words)): continue
                add(t, f'  {side}: на стол → {dname(grp) or "жетон"}')
            elif zt == 'ZoneType_Graveyard' and iid not in seen_gy:
                seen_gy.add(iid)
                if grp in ability: continue
                dn = dname(grp)
                if dn and grp not in landgrp and not any(w in dn for w in land_words):
                    add(t, f'  {side}: ✝ {dn}')
            elif zt == 'ZoneType_Exile' and iid not in seen_ex:
                seen_ex.add(iid)
                # только перманенты (существо/артефакт/чары/пв) — отсекаем flashback-инстанты/импульс/земли
                if name and (gtype.get(grp, set()) & PERM) and not any(w in name for w in land_words):
                    add(t, f'  {side}: ⊘ {name} (exile)')

    # MTGA turnNumber считает ходы ОБОИХ игроков подряд (T1 плей, T2 дро, …),
    # поэтому показываем ещё и счёт ПО СТОРОНЕ — «твой ход #k» / «ход опп #k».
    # Нумеруем по ВСЕМ ходам (включая пустые — где была только земля), иначе сбивается счёт.
    side_label = {}; my_n = opp_n = 0
    for t in sorted(turn_active):
        if turn_active[t] == me:
            my_n += 1; side_label[t] = f"твой ход #{my_n}"
        else:
            opp_n += 1; side_label[t] = f"ход опп #{opp_n}"
    # --- БОИ: атаки/блоки из GRE (attackState/blockState на объектах) ---
    # Arena пишет бой в лог: атакующий объект получает "attackState":"AttackState_Declared",
    # блокёр — "blockState":"BlockState_Declared","blockInfo":{"attackerIds":[..]}.
    # Раньше analyze их не извлекал → приходилось спрашивать игрока. Теперь видно из лога.
    iid_name = {}
    for m in re.finditer(r'"instanceId":\s*(\d+),\s*"grpId":\s*(\d+)', last):
        g = int(m.group(2))
        if g > 0: iid_name[int(m.group(1))] = names.get(g, f'id{g}')
    def cname(iid):  # имя существа или «жетон» для безымянных токенов
        nm = iid_name.get(iid)
        return nm.split(' //')[0] if nm else 'жетон'
    turn_pos = sorted((m.start(), int(m.group(1)))
                      for m in re.finditer(r'"turnNumber"\s*:\s*(\d+)', last))
    def turn_at(pos):
        t = None
        for p, tn in turn_pos:
            if p <= pos: t = tn
            else: break
        return t
    atk = {}   # turn -> set(attacker_iid)
    for m in re.finditer(r'"instanceId":\s*(\d+),\s*"grpId":\s*(\d+)'
                         r'.{0,400}?"attackState":\s*"AttackState_Declared"', last, re.S):
        atk.setdefault(turn_at(m.start()), set()).add(int(m.group(1)))
    blk = {}   # turn -> list(blocker_iid, attacker_iid)
    for m in re.finditer(r'"instanceId":\s*(\d+),\s*"grpId":\s*(\d+).{0,400}?'
                         r'"blockState":\s*"BlockState_Declared",\s*"blockInfo":\s*\{\s*'
                         r'"attackerIds":\s*\[\s*(\d+)', last, re.S):
        blk.setdefault(turn_at(m.start()), []).append((int(m.group(1)), int(m.group(3))))
    def combat_line(t):
        a = atk.get(t); b = blk.get(t)
        if not a and not b: return None
        blocked = {ai for _, ai in (b or [])}
        parts = []
        for iid in a or []:
            tag = '' if iid in blocked else ' ✓прошёл'
            parts.append(cname(iid) + tag)
        s = "  ⚔ атака: " + (", ".join(parts) if parts else "—")
        if b:
            s += "  |  🛡 блок: " + ", ".join(f"{cname(bi)}→{cname(ai)}" for bi, ai in b)
        return s

    print("\n=== ПО ХОДАМ ===  (ход N = абсолютный счётчик MTGA; в скобках — твой/опп счёт)")
    for t in sorted(set(per_turn) | set(atk) | set(blk)):
        whose = side_label.get(t, "?")
        la = life_at.get(t, {})
        opp = next((s for s in la if s != me), None)
        ls = f"  [жизни: ты {la.get(me,'?')} / опп {la.get(opp,'?')}]" if la else ""
        print(f"--- ХОД {t} ({whose}) ---{ls}")
        prev = None
        for s in per_turn.get(t, []):
            if s != prev: print(s); prev = s
        cl = combat_line(t)
        if cl: print(cl)

    # --- ДВИЖКИ: повторяющиеся способности (часто и есть причина разгрома) ---
    eng = [(s, nm, c) for (s, nm), c in ability_use.items() if c >= 2]
    if eng:
        print("\n=== ДВИЖКИ / ПОВТОРНЫЕ СПОСОБНОСТИ ===  (≥2 активаций — смотри в первую очередь)")
        for s, nm, c in sorted(eng, key=lambda x: -x[2]):
            print(f"  {s}: {nm} — способность сработала ×{c}")

    # --- ФИНАЛЬНЫЙ БОРД (надёжно: последний objectInstanceIds зоны Battlefield) ---
    mz = re.search(r'"zoneId":\s*(\d+),\s*"type":\s*"ZoneType_Battlefield"', last)
    bf = int(mz.group(1)) if mz else 28
    arrs = re.findall(r'"zoneId":\s*' + str(bf) + r',\s*"type":\s*"ZoneType_Battlefield"'
                      r'[^}]*?"objectInstanceIds":\s*\[([0-9,\s]*)\]', last)
    live = [int(x) for x in re.findall(r'\d+', arrs[-1])] if arrs else []
    oinfo = {}  # iid -> (grp, controller) по последней дефиниции объекта
    for m in re.finditer(r'"instanceId":\s*(\d+),\s*"grpId":\s*(\d+),[^{}]*?'
                         r'"ownerSeatId":\s*(\d+)(?:[^{}]*?"controllerSeatId":\s*(\d+))?', last):
        iid, grp, owner, ctrl = int(m.group(1)), int(m.group(2)), int(m.group(3)), \
            int(m.group(4)) if m.group(4) else int(m.group(3))
        oinfo[iid] = (grp, ctrl)
    # типы карт по grpId (фильтр земель — по ТИПУ, не по имени: жетоны-земли без имени)
    gtype = {}
    for m in re.finditer(r'"grpId":\s*(\d+),[^{}]*?"cardTypes":\s*\[([^\]]*)\]', last):
        gtype.setdefault(int(m.group(1)), set()).update(re.findall(r'CardType_(\w+)', m.group(2)))
    def classify(grp):
        ts = gtype.get(grp, set())
        if 'Land' in ts: return 'land'
        if 'Creature' in ts: return 'creature'
        return 'other'  # артефакт/Treasure/чары/спелл-перм
    mine_c, opp_c, mine_o, opp_o = [], [], [], []
    for iid in live:
        grp, ctrl = oinfo.get(iid, (0, None))
        nm = dname(grp) or ('жетон' if grp <= 0 else f'id{grp}')
        cls = classify(grp)
        if cls == 'land': continue
        if ctrl == me: (mine_c if cls == 'creature' else mine_o).append(nm)
        else: (opp_c if cls == 'creature' else opp_o).append(nm)
    print("\n=== ФИНАЛЬНЫЙ БОРД ===")
    print(f"  ТВОИ существа ({len(mine_c)}): " + (", ".join(mine_c) or "—")
          + (f"  | прочее: {', '.join(mine_o)}" if mine_o else ""))
    print(f"  СОПЕРНИК существа ({len(opp_c)}): " + (", ".join(opp_c) or "—")
          + (f"  | прочее: {', '.join(opp_o)}" if opp_o else ""))

    # --- ФИНАЛЬНАЯ РУКА (надёжно: ПОСЛЕДНИЙ objectInstanceIds зоны Hand игрока).
    # БАГ-ФИКС: раньше руку читали через parse_state, который АККУМУЛИРУЕТ объекты и
    # показывает по сути СТАРТОВУЮ (мулиганную) руку, а не финальную — из-за этого
    # казалось, что игрок умер с removal/блокёрами в руке, хотя там была 1 карта.
    # Берём id-зоны Hand игрока (любой порядок ключей) и последний снимок её состава.
    hz_ids = set()
    for m in re.finditer(r'"zoneId":\s*(\d+),\s*"type":\s*"ZoneType_Hand"[^}]*?'
                         r'"ownerSeatId":\s*(\d+)', last):
        if int(m.group(2)) == me: hz_ids.add(int(m.group(1)))
    for m in re.finditer(r'"ownerSeatId":\s*(\d+)[^}]*?"zoneId":\s*(\d+),\s*'
                         r'"type":\s*"ZoneType_Hand"', last):
        if int(m.group(1)) == me: hz_ids.add(int(m.group(2)))
    hand_final = []
    for m in re.finditer(r'"zoneId":\s*(\d+),\s*"type":\s*"ZoneType_Hand"[^}]*?'
                         r'"objectInstanceIds":\s*\[([0-9,\s]*)\]', last):
        if int(m.group(1)) in hz_ids:
            hand_final = [int(x) for x in re.findall(r'\d+', m.group(2))]
    hcards = [names.get(oinfo.get(i, (0, None))[0],
                        'жетон' if oinfo.get(i, (0, None))[0] <= 0 else f'id{i}')
              for i in hand_final]
    print(f"  ТВОЯ РУКА в конце ({len(hand_final)}): " + (", ".join(hcards) or "—"))

if __name__ == "__main__":
    main()
