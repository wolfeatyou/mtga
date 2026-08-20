#!/usr/bin/env python3
"""
Стрим-агрегатор replay-датасета 17Lands → games/<set>_replay.json.gz (§ 8.30).

    python3 fetch_17l_replay.py msh [--check]

Файл ~222 МБ gz (2817 колонок, партия = строка, по-ходовые метрики обеих сторон).
На диск кладётся ТОЛЬКО свёртка: партия → ~20 пилот-агрегатов (агрессия, ленд-дропы,
слитая мана 3–7, тайминг removal, блоки, риск) + мета (draft_id, won, ранг, скилл-бакет)
+ deck_gih (средний GIH мейна из deck_* колонок — контроль качества § 8.8 без джойнов).
Семантика колонок (§ 8.30, снята с сырых строк — НЕ по докам): поля существ/земель —
СПИСКИ arena-id через «|» ('105148|104936' = 2 атакера), счёт = len(split); пустая строка =
ноль/не было. Числовые — только *_mana_spent, *_life, *_combat_damage_taken. N-й СВОЙ ход
существует, если user_mana_spent != ''; чужой ход — если oppo_turn_N_eot_user_life != ''
(creatures_attacked пуст и на состоявшемся ходу без атаки — на этом сгорел первый парсер).
Анализ — pilot_vs_outcome.py. Пререгистрация вопросов — § 8.30.
"""
import csv
import gzip
import io
import json
import os
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_audit as A          # noqa: E402

URL = ("https://17lands-public.s3.amazonaws.com/analysis_data/replay_data/"
       "replay_data_public.{SET}.{EVT}.csv.gz")
MAXT = 30


def main():
    code = (sys.argv[1] if len(sys.argv) > 1 else "msh").lower()
    evt = "PremierDraft"
    url = URL.format(SET=code.upper(), EVT=evt)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    if "--check" in sys.argv:
        try:
            req.get_method = lambda: "HEAD"
            r = urllib.request.urlopen(req, timeout=30)
            print(f"✅ {code.upper()}: replay-датасет доступен, "
                  f"{int(r.headers.get('Content-Length', 0)) / 1e6:.0f} МБ")
        except Exception as e:
            print(f"❌ {code.upper()}: {e}")
        return

    rat = A.load_ratings(code)
    resp = urllib.request.urlopen(req, timeout=120)
    stream = io.TextIOWrapper(gzip.GzipFile(fileobj=resp), encoding="utf-8", newline="")
    rd = csv.reader(stream)
    hdr = next(rd)
    ix = {h: i for i, h in enumerate(hdr)}
    deck_cols = [(i, h[5:]) for i, h in enumerate(hdr) if h.startswith("deck_")]
    gih_of = {}
    for _i, nm in deck_cols:
        r = A.rating_of(rat, nm)
        gih_of[nm] = r["ever_drawn_win_rate"] * 100 if r and r.get("ever_drawn_win_rate") else None

    def I(row, col):
        v = row[ix[col]] if col in ix else ""
        try:
            return int(float(v))
        except (TypeError, ValueError):
            return None

    def C(row, col):
        """Счёт id-списка '105148|104936' → 2; '' → 0; отсутствие колонки → None."""
        if col not in ix:
            return None
        v = row[ix[col]]
        return len(v.split("|")) if v else 0

    out = []
    for row in rd:
        if not row or len(row) < len(hdr):
            continue
        g = dict(d=row[ix["draft_id"]][:8], won=row[ix["won"]] == "True",
                 turns=I(row, "num_turns") or 0, play=row[ix["on_play"]] == "True",
                 mull=I(row, "num_mulligans") or 0, rank=row[ix["rank"]],
                 wrb=row[ix["user_game_win_rate_bucket"]],
                 ngb=row[ix["user_n_games_bucket"]])
        s = w = 0.0
        for i, nm in deck_cols:
            try:
                n = int(float(row[i] or 0))
            except ValueError:
                n = 0
            if n and gih_of[nm] is not None:
                s += n * gih_of[nm]
                w += n
        g["gih"] = round(s / w, 2) if w else None

        atk_t = atk_opp = attackers = unb = dmg = 0
        spent37 = avail37 = 0
        rem_t = None
        lands5 = None
        life_min = 20
        prev_cre = 0
        my_turns = 0
        for t in range(1, MAXT + 1):
            ms = I(row, f"user_turn_{t}_user_mana_spent")
            if ms is None:
                break
            my_turns += 1
            atk = C(row, f"user_turn_{t}_creatures_attacked") or 0
            if prev_cre > 0:
                atk_opp += 1
                if atk > 0:
                    atk_t += 1
            attackers += atk
            unb += C(row, f"user_turn_{t}_creatures_unblocked") or 0
            dmg += I(row, f"user_turn_{t}_oppo_combat_damage_taken") or 0
            lands = C(row, f"user_turn_{t}_eot_user_lands_in_play") or 0
            if 3 <= t <= 7:
                spent37 += ms
                avail37 += lands
            if t == 5:
                lands5 = lands
            if rem_t is None and (C(row, f"user_turn_{t}_oppo_creatures_killed_non_combat") or 0) > 0:
                rem_t = t
            life = I(row, f"user_turn_{t}_eot_user_life")
            if life is not None:
                life_min = min(life_min, life)
            prev_cre = C(row, f"user_turn_{t}_eot_user_creatures_in_play") or 0

        ob_atk = ob_blk = blockers = 0
        for t in range(1, MAXT + 1):
            if I(row, f"oppo_turn_{t}_eot_user_life") is None:
                break
            oa = C(row, f"oppo_turn_{t}_creatures_attacked") or 0
            if oa > 0:
                ob_atk += 1
                if (C(row, f"oppo_turn_{t}_creatures_blocking") or 0) > 0:
                    ob_blk += 1
                blockers += C(row, f"oppo_turn_{t}_creatures_blocking") or 0
            life = I(row, f"oppo_turn_{t}_eot_user_life")
            if life is not None:
                life_min = min(life_min, life)

        g.update(myt=my_turns, atkt=atk_t, atko=atk_opp, natk=attackers, unb=unb, dmg=dmg,
                 sp37=spent37, av37=avail37, remt=rem_t, l5=lands5,
                 oat=ob_atk, obl=ob_blk, nbl=blockers, lmin=life_min)
        out.append(g)
        if len(out) % 50000 == 0:
            print(f"  …{len(out):,}")

    p = os.path.join(HERE, "games", f"{code}_replay.json.gz")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with gzip.open(p, "wt", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False)
    print(f"партий {len(out):,} → {p} ({os.path.getsize(p) / 1e6:.0f} МБ)")


if __name__ == "__main__":
    main()
