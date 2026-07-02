#!/usr/bin/env python3
"""Live MATCH helper — следит за Player.log Arena и отдаёт снимок игры в точке решения.

  python3 match_watch.py raw       — выгрузить сырые GRE-строки (для отладки формата)
  python3 match_watch.py once      — один снимок текущего состояния и выйти
  python3 match_watch.py watch     — ждать (блокируясь) до СЛЕДУЮЩЕЙ точки твоего решения, напечатать снимок, выйти
                                     (для фона: харнесс будит меня на выходе, я советую и перезапускаю watch)

Парсер подогнан под реальный лог SOS Premier (2026-06). Моя сторона = systemSeatIds.
Почти все сообщения — GameStateType_Diff: берём последнее вхождение каждого объекта/зоны/turnInfo.
Требует detailed logs в Arena.
"""
import json, re, os, sys, time, glob

LOG_ENV = os.environ.get("MTGA_LOG")
LOGDIR = os.path.expanduser("~/Library/Logs/Wizards Of The Coast/MTGA")
HERE = os.path.dirname(os.path.abspath(__file__))

POLL_SEC = 1.0       # как часто проверять рост лога в watch
WATCH_TIMEOUT = 180  # макс. ожидание (сек): по таймауту выходим, чтобы перезапуститься

def setcode():
    for a in sys.argv[1:]:
        if a.lower() in ("mkm", "sos", "msh"):
            return a.lower()
    return "sos"

def log_files():
    if LOG_ENV:
        return [LOG_ENV]
    return [os.path.join(LOGDIR, "Player-prev.log"), os.path.join(LOGDIR, "Player.log")]

def read_logs():
    parts = []
    for f in log_files():
        if f and os.path.exists(f):
            parts.append(open(f, encoding="utf-8", errors="ignore").read())
    return "\n".join(parts)

def log_size():
    return sum(os.path.getsize(f) for f in log_files() if f and os.path.exists(f))

def load_names():
    # grpId → имя по ВСЕМ доступным наборам (*_set.json). arena_id глобально
    # уникален на печать, поэтому объединение наборов безопасно и делает разбор
    # set-agnostic: analyze_game.py не обязан знать, из какого сета партия
    # (раньше setcode() дефолтил в "sos" и MSH-карты выходили «неопознанными»).
    out = {}
    files = sorted(glob.glob(os.path.join(HERE, "*_set.json")))
    # текущий сет грузим последним, чтобы при коллизии победило его имя
    cur = os.path.join(HERE, f"{setcode()}_set.json")
    if cur in files:
        files = [f for f in files if f != cur] + [cur]
    for f in files:
        try:
            for c in json.load(open(f)):
                aid = c.get("arena_id")
                if aid is not None:
                    out[int(aid)] = c.get("name", f"id{aid}")
        except Exception:
            continue
    return out

# ─────────────────────────────────────────────────────────────────────────────
#  РАЗБОР GRE-СОСТОЯНИЯ (формат реального лога SOS)
# ─────────────────────────────────────────────────────────────────────────────
RE_SEAT = re.compile(r'"systemSeatIds"\s*:\s*\[\s*(\d+)')
RE_ZONE = re.compile(r'"zoneId"\s*:\s*(\d+)\s*,\s*"type"\s*:\s*"(ZoneType_\w+)"(?:[^{}]*?"ownerSeatId"\s*:\s*(\d+))?')
RE_OBJ  = re.compile(r'"instanceId"\s*:\s*(\d+)\s*,\s*"grpId"\s*:\s*(\d+)[^{}]*?"zoneId"\s*:\s*(\d+)[^{}]*?"ownerSeatId"\s*:\s*(\d+)(?:[^{}]*?"controllerSeatId"\s*:\s*(\d+))?')
RE_TURNINFO = re.compile(r'"turnInfo"\s*:\s*\{([^{}]*)\}')

ZTYPE = {"ZoneType_Hand": "рука", "ZoneType_Battlefield": "стол",
         "ZoneType_Graveyard": "кладбище", "ZoneType_Stack": "стек",
         "ZoneType_Exile": "изгнание"}

def scope_current_game(text):
    """Изолируем ТЕКУЩУЮ игру. Граница — старт игры с последним (matchID, gameNumber);
    современный лог идёт на GameStateType_Diff, Full встречается редко, поэтому matchID
    надёжнее. Fallback на последний GameStateType_Full."""
    last = None
    for m in re.finditer(r'"matchID"\s*:\s*"[0-9a-f\-]+"\s*,\s*"gameNumber"\s*:\s*\d+', text):
        last = m.start()
    if last is not None:
        a = text.rfind("GameStateType_Full", 0, last)
        if a == -1 or last - a > 200000:  # Full не от этой игры — отматываем по сообщению
            a = text.rfind("GreToClientEvent", max(0, last - 8000), last)
        return text[a if a != -1 else max(0, last - 8000):]
    i = text.rfind("GameStateType_Full")
    if i == -1:
        return text
    start = text.rfind("GreToClientEvent", max(0, i - 4000), i)
    return text[start if start != -1 else i:]

def get_my_seat(text):
    # Берём ПЕРВОЕ вхождение systemSeatIds — оно всегда наше (из ConnectResp/Join),
    # а не последнее, которое может быть от соперника или повторного события.
    m = RE_SEAT.findall(text)
    return int(m[0]) if m else None

def seat_in_game(game_text):
    """Моё место В ТЕКУЩЕЙ игре: systemSeatIds в слайсе = адресат сообщений = я.
    (get_my_seat по полному логу врёт в поздних партиях, где seat сменился play/draw —
    из-за этого стороны/рука переворачивались.)"""
    from collections import Counter
    ss = RE_SEAT.findall(game_text)
    return int(Counter(ss).most_common(1)[0][0]) if ss else None

def parse_state(text):
    zones = {}
    for zid, ztype, owner in RE_ZONE.findall(text):
        zones[int(zid)] = (ztype, int(owner) if owner else None)
    objs = {}
    for iid, grp, zid, owner, ctrl in RE_OBJ.findall(text):
        objs[int(iid)] = {"grp": int(grp), "zid": int(zid),
                          "owner": int(owner), "ctrl": int(ctrl) if ctrl else int(owner)}
    # жизни (порядок полей в player-объекте бывает любой — пробуем оба)
    life = {}
    for hp, seat in re.findall(r'"lifeTotal"\s*:\s*(\d+)[^{}]*?"systemSeatNumber"\s*:\s*(\d+)', text):
        life[int(seat)] = int(hp)
    for seat, hp in re.findall(r'"systemSeatNumber"\s*:\s*(\d+)[^{}]*?"lifeTotal"\s*:\s*(\d+)', text):
        life[int(seat)] = int(hp)
    # turnInfo — последний блок (плоский, без вложенных скобок)
    turn = None
    blocks = RE_TURNINFO.findall(text)
    if blocks:
        b = blocks[-1]
        def g(k, cast=str):
            m = re.search(rf'"{k}"\s*:\s*"?(\w+)"?', b)
            return cast(m.group(1)) if m else None
        turn = {"n": g("turnNumber", int), "phase": g("phase"), "step": g("step"),
                "active": g("activePlayer", int), "priority": g("priorityPlayer", int)}
    return {"zones": zones, "objs": objs, "life": life, "turn": turn}

def snapshot(text, names):
    game = scope_current_game(text)     # только текущая игра
    me = seat_in_game(game) or get_my_seat(text)  # место — из слайса игры (фикс «переворота»)
    st = parse_state(game)              # состояние — только текущая игра
    if not st["objs"] and not st["turn"]:
        return None  # игры в логе нет
    seats = {o["owner"] for o in st["objs"].values()} | set(st["life"])
    opp = next((s for s in seats if s != me), None)

    def cards(seat, ztypes, by="owner"):
        out = []
        for iid, o in st["objs"].items():
            ztype, _ = st["zones"].get(o["zid"], (None, None))
            if ztype in ztypes and o[by] == seat:
                out.append(names.get(o["grp"], f"id{o['grp']}") if o["grp"] > 0 else "(скрыто)")
        return out

    L = []
    t = st["turn"]
    if t:
        who = "ТВОЙ ХОД" if t["active"] == me else "ход соперника"
        prio = "твой приоритет" if t["priority"] == me else "приоритет соперника"
        L.append(f"Ход {t['n']} · {t.get('step') or t.get('phase') or '?'} · {who} · {prio}")
    if st["life"]:
        L.append(f"Жизни: ты {st['life'].get(me,'?')} — соперник {st['life'].get(opp,'?')}")
    if me is None:
        L.append("⚠ не определил твою сторону (systemSeatIds) — пришли `raw`.")
        return st, me, "\n".join(L)
    L.append("\nТВОЯ РУКА: " + (", ".join(cards(me, ["ZoneType_Hand"])) or "—"))
    L.append("ТВОЙ СТОЛ: " + (", ".join(cards(me, ["ZoneType_Battlefield"], by="ctrl")) or "—"))
    L.append("СТОЛ СОПЕРНИКА: " + (", ".join(cards(opp, ["ZoneType_Battlefield"], by="ctrl")) or "—"))
    named, triggers = [], 0
    for iid, o in st["objs"].items():
        ztype, _ = st["zones"].get(o["zid"], (None, None))
        if ztype == "ZoneType_Stack":
            nm = names.get(o["grp"])
            if nm:
                named.append(nm)
            else:
                triggers += 1
    if named or triggers:
        extra = f" (+{triggers} триггеров/абилок)" if triggers else ""
        L.append("СТЕК: " + (", ".join(named) or "—") + extra)
    gy = cards(me, ["ZoneType_Graveyard"])
    if gy:
        L.append(f"твоё кладбище ({len(gy)}): " + ", ".join(gy[-8:]))
    return st, me, "\n".join(L)

def decision_point(st, me, scope="myturn"):
    """Срабатывание вотчера в зависимости от scope:
      myturn   — ОДИН раз в начале твоего хода (твоя главная фаза 1, твой приоритет). По умолчанию.
      oppcombat— ход соперника, шаг объявления блоков, твой приоритет (задел на будущее).
      all      — любой твой приоритет (старое поведение, спамит каждый шаг)."""
    t = st.get("turn")
    if not (t and me is not None and t.get("priority") == me):
        return False
    ph = (t.get("phase") or "") + "|" + (t.get("step") or "")
    if scope == "all":
        return True
    is_myturn   = t.get("active") == me and "Main1" in ph
    is_oppblock = t.get("active") != me and ("DeclareBlock" in ph or "Block" in ph)
    if scope == "myturn":
        return is_myturn
    if scope == "oppcombat":
        return is_oppblock
    if scope == "both":            # твой ход + блок на атаке соперника
        return is_myturn or is_oppblock
    return is_myturn

def turn_sig(st):
    # для myturn ключуем по номеру хода (а не шагу), чтобы был ровно один сигнал за ход
    t = st.get("turn")
    return (t["n"], t.get("phase"), t.get("step"), t["priority"]) if t else None

# ─────────────────────────────────────────────────────────────────────────────

def do_raw():
    text = read_logs()
    keys = ["GreToClientEvent", "GameStateMessage", "gameObjects", "turnInfo",
            "lifeTotal", "zoneId", "instanceId", "GameStateType"]
    hits = [ln for ln in text.splitlines() if any(k in ln for k in keys)]
    print(f"GRE-подобных строк: {len(hits)}")
    if not hits:
        print("Матча в логе нет (detailed logs выключены / нет рестарта / не в игре).")
        return
    print("\n--- последние GRE-строки ---")
    for ln in hits[-12:]:
        print(ln[:600])

def do_once():
    snap = snapshot(read_logs(), load_names())
    if not snap:
        print("Игры в логе не вижу. Зайди в матч, затем `once` (или `raw`).")
        return
    print("===== СНИМОК ИГРЫ =====")
    print(snap[2])

def notify(title, message):
    """macOS баннер — всплывает поверх Arena без переключения окон."""
    import subprocess
    escaped = message.replace('"', '\\"').replace("'", "'\\''")
    ttl = title.replace('"', '\\"')
    subprocess.Popen(["osascript", "-e",
        f'display notification "{escaped}" with title "{ttl}"'])

# ── Быстрый rule-based советник для W/B Silverquill (без API, <0.1 сек) ────────
LANDW = ("Island","Mountain","Swamp","Forest","Plains","Coast","Fields of Strife",
         "Forum of Amity","Titan's Grave","Skycoach Waypoint","Great Hall")
MY_REMOVAL  = {"Ajani's Response","Last Gasp","End of the Hunt","Wander Off","Foolish Fate"}
MY_TRICKS   = {"Interjection","Dig Site Inventory","Rapier Wit","Masterful Flourish"}
MY_FINISHER = {"Together as One"}

def quick_advice(st, me, names):
    """Одна строка совета по эвристикам W/B Silverquill (мгновенно, без API)."""
    t = st.get("turn") or {}
    my_life = st["life"].get(me, 20)
    seats = {o["owner"] for o in st["objs"].values()} | set(st["life"])
    opp = next((s for s in seats if s != me), None)
    opp_life = st["life"].get(opp, 20)

    def zone_cards(seat, ztype, by="owner"):
        out = []
        for o in st["objs"].values():
            zt, _ = st["zones"].get(o["zid"], (None, None))
            if zt == ztype and o[by] == seat and o["grp"] > 0:
                out.append(names.get(o["grp"], "жетон"))
        return out

    def noland(cards): return [c for c in cards if not any(w in c for w in LANDW)]

    my_hand   = zone_cards(me,  "ZoneType_Hand")
    my_board  = zone_cards(me,  "ZoneType_Battlefield", by="ctrl")
    opp_board = zone_cards(opp, "ZoneType_Battlefield", by="ctrl")
    my_lands  = sum(1 for c in my_board if any(w in c for w in LANDW))
    my_crea   = noland(my_board)           # прибл. твои тела
    opp_crea  = noland(opp_board)           # прибл. их тела
    step = t.get("step") or t.get("phase") or ""
    my_turn  = t.get("active") == me
    have_removal = sorted(set(my_hand) & MY_REMOVAL)
    have_trick   = sorted(set(my_hand) & MY_TRICKS)
    have_fin     = sorted(set(my_hand) & MY_FINISHER)
    behind = (opp_life - my_life >= 4) or (len(opp_crea) - len(my_crea) >= 3)
    ahead  = (my_life - opp_life >= 4) and (len(my_crea) >= len(opp_crea))

    # Короткий совет обычными словами (без сленга): глагол + максимум одна подсказка.
    # 0. Это атака соперника, твой блок
    if not my_turn:
        if my_life >= 8:
            return ("🛡 ИХ АТАКА: можешь ПРИНЯТЬ урон (жизней хватает); "
                    "не ставь много существ в одно — у них может быть усиление/трампл. Лучше пропусти или закрой одним.")
        return ("🛡 ИХ АТАКА: ты низко — считай их МАКС урон перед блоком; "
                "закрывай ровно сколько нужно, не больше (риск усиления).")
    # 1. Соперник низко — проверь, добиваешь ли
    if opp_life <= 6 and len(my_crea) >= 2:
        hint = ""
        if have_fin:     hint = f" ({have_fin[0]}: 2 урона сверху по сопернику)"
        elif have_trick: hint = " (усиль того, кого не блокируют)"
        return f"🎯 СОПЕРНИК на {opp_life} — посчитай, хватит ли атаки на победу{hint}."
    # 2. Режим
    if behind:
        head = "🛡 ЗАЩИЩАЙСЯ — выставь крупное существо, держи всех в обороне"
        hint = "; убери их сильнейшее существо" if have_removal else ""
    elif ahead or my_lands <= 3:
        head = "⚔ АТАКУЙ и выставляй существ"
        hint = "; убийство прибереги на их главную угрозу" if have_removal else ""
    else:
        head = "➕ выставляй существ, бей где выгодно"
        hint = ("; усиление прибереги для боя" if have_trick
                else ("; убийство — на их сильное существо" if have_removal else ""))
    warn = f"   ⚠ мало земель: {my_lands}" if (my_lands <= 3 and t.get("n", 0) >= 7) else ""
    return f"{head}{hint}.{warn}"

def api_advice(body, my_life, opp_life):
    """Вызов Anthropic API если есть ключ. Возвращает строку или None."""
    import os
    key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if not key:
        # попробуем .env рядом со скриптом
        env_f = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
        if os.path.exists(env_f):
            for ln in open(env_f):
                if ln.startswith("ANTHROPIC_API_KEY="):
                    key = ln.split("=",1)[1].strip().strip('"')
    if not key:
        return None
    try:
        import anthropic, textwrap
        deck = ("UR Spellslinger: 2×Matterbending Mage, Elemental Mascot, Expressive Firedancer, "
                "Sanar, Textbook Tabulator, Goblin Glasswright, Sundering Archaic, Transcendent Archaic, "
                "Mathemagics, Splatter Technique, Essence Scatter×2, Banishing Betrayal×2, "
                "Prismari Charm, Seize the Spoils, Potioner's Trove, Artistic Process, "
                "Divergent Equation, Duel Tactics, Run Behind, Stormcarved Coast+9Island+7Mountain")
        prompt = (f"MTG Arena SOS draft game. My deck: {deck}.\n"
                  f"State:\n{body}\n"
                  f"Give ONE line of advice (Russian, start with →). Be very brief.")
        c = anthropic.Anthropic(api_key=key)
        r = c.messages.create(model="claude-haiku-4-5-20251001", max_tokens=80,
                               messages=[{"role":"user","content":prompt}])
        return r.content[0].text.strip()
    except Exception:
        return None

def do_watch(scope="myturn"):
    names = load_names()
    snap0 = snapshot(read_logs(), names)
    sig0 = turn_sig(snap0[0]) if snap0 else None
    deadline = time.time() + WATCH_TIMEOUT
    last_size = log_size()
    while time.time() < deadline:
        time.sleep(POLL_SEC)
        sz = log_size()
        if sz == last_size:
            continue
        last_size = sz
        text = read_logs()
        snap = snapshot(text, names)
        if not snap:
            continue
        st, me, body = snap
        if turn_sig(st) != sig0 and decision_point(st, me, scope):
            t = st.get("turn") or {}
            step = t.get("step") or t.get("phase") or "?"
            my_life  = st["life"].get(me,  20)
            opp_life = st["life"].get(next((s for s in
                       ({o["owner"] for o in st["objs"].values()}|set(st["life"])) if s!=me), None), 20)
            # 1. Мгновенный rule-based совет
            advice = quick_advice(st, me, names)
            notify("⚔ MTG", f"→ {advice}  [{my_life}v{opp_life}]")
            print("===== ТОЧКА РЕШЕНИЯ =====")
            print(body)
            print(f"\n→ СОВЕТ: {advice}")
            # 2. Попробуем уточнить через API (async, не блокируем)
            import threading
            def _api():
                a = api_advice(body, my_life, opp_life)
                if a:
                    notify("⚔ MTG (AI)", a)
                    print(f"→ AI СОВЕТ: {a}")
            threading.Thread(target=_api, daemon=True).start()
            return
    print("(watch: таймаут — точки решения не было; перезапусти watch)")

def do_loop(scope="myturn"):
    """Бесконечная лента в ТВОЙ терминал: печатает совет на каждом твоём ходу.
    Запускать в своём окне Terminal: python3 match_watch.py sos loop [myturn|oppcombat|all]
    Ctrl+C — выход. Баннер НЕ шлёт (всё в stdout)."""
    names = load_names()
    print("═" * 64)
    print("  MTG live advisor — лента в терминал (W/B Silverquill)")
    print(f"  scope={scope}   ·   Ctrl+C для выхода")
    print("═" * 64, flush=True)
    last_sig = None
    last_size = log_size()
    while True:
        try:
            time.sleep(POLL_SEC)
            sz = log_size()
            if sz == last_size:
                continue
            last_size = sz
            snap = snapshot(read_logs(), names)
            if not snap:
                continue
            st, me, body = snap
            sig = turn_sig(st)
            if sig != last_sig and decision_point(st, me, scope):
                last_sig = sig
                advice = quick_advice(st, me, names)
                tt = st.get("turn") or {}
                opp = next((s for s in st["life"] if s != me), None)
                ml, ol = st["life"].get(me, "?"), st["life"].get(opp, "?")
                print("\n" + "─" * 40)
                print(f"  ХОД {tt.get('n','?')}   ·   ты {ml} — опп {ol}")
                print(f"  → {advice}", flush=True)
        except KeyboardInterrupt:
            print("\n(выход)")
            return
        except Exception as e:
            print(f"(ошибка: {e})", flush=True)
            time.sleep(1)

if __name__ == "__main__":
    mode = "watch"; scope = "myturn"
    for a in sys.argv[1:]:
        if a in ("raw", "once", "watch", "loop"):
            mode = a
        if a in ("myturn", "oppcombat", "both", "all"):
            scope = a
    if mode == "watch":
        do_watch(scope)
    elif mode == "loop":
        do_loop(scope)
    else:
        {"raw": do_raw, "once": do_once}[mode]()
