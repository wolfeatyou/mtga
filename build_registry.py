#!/usr/bin/env python3
"""
РЕЕСТР СБОРОК: дифф листов + журнал кандидатов каждой сборки.

    python3 build_registry.py diff <A.txt> <B.txt>          # расстояние мейнов
    python3 build_registry.py add  <set> <draft8> <tag> <file>   # записать кандидата
    python3 build_registry.py show <set> <draft8>           # все кандидаты + диффы до final

ЗАЧЕМ (20.08.2026, mode_build.md § МУЛЬТИСБОРКА). Цикл «моя сборка → сборка игрока →
сравнение → согласованный финал» — единственные размеченные данные о том, где советчик
систематически ошибается каркасом, и до этого файла они испарялись в чате (аналог дыры,
которую для пиков закрыла телеметрия § 8.12, а для партий — реестр § 8.13).
Метрика процесса: расстояние ПЕРВОГО кандидата до согласованного финала (карт мейна,
по копиям). Эталон 20.08: advisor→final = 4 (3657e8ab BG) и 1 (88d7d604 BR, прокси);
trio § 8.19 = 7. Финал ≠ доказанный оптимум — это консенсус; настоящий судья — раны.

Формат хранения: builds/<set>_builds.jsonl, запись = {ts, draft, tag, file, main:{имя:копий},
lands:{имя:копий}}. Теги: advisor-v1 · lane:<...> · judge · user · final. Дифф — только
нонленды мейна; земли печатаются отдельно (их разница почти всегда следствие, не решение).
"""
import json
import os
import re
import sys
from collections import Counter
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_audit as A          # noqa: E402

BASICS = {"Plains", "Island", "Swamp", "Mountain", "Forest"}
ARENA_ID = re.compile(r"^id\d+$")
_DB = None


def _db():
    global _DB
    if _DB is None:
        _DB = A.load_db()
    return _DB


def main_counts(path):
    """(нонленды мейна Counter, земли Counter) — только секция Deck.
    Земля определяется по type_line сет-файла: нонбейзик-земля (Lake-town) — это земля,
    а не карта мейна, иначе дистанция мейнов завышается (поймано на кандидатах 20.08)."""
    md, _ = A.split_deck(path)
    nl, lands = Counter(), Counter()
    for n, name in md:
        if name in BASICS or ARENA_ID.match(name):
            lands[name] += n
            continue
        c = _db().get(A.norm(name)) or _db().get(A.norm(name.split(",")[0]))
        if c is not None and "Land" in A.face(c, "type_line"):
            lands[name] += n
        else:
            nl[name] += n
    return nl, lands


def dist(a, b):
    """Расстояние по копиям: сколько карт заменить, чтобы из A получить B."""
    return sum((a - b).values())


def fmt_diff(a, b):
    da, db = a - b, b - a
    out = []
    if da:
        out.append("   − " + " · ".join(f"{k}×{v}" if v > 1 else k for k, v in sorted(da.items())))
    if db:
        out.append("   + " + " · ".join(f"{k}×{v}" if v > 1 else k for k, v in sorted(db.items())))
    return out


def reg_path(setcode):
    d = os.path.join(HERE, "builds")
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, f"{setcode}_builds.jsonl")


def add(setcode, draft8, tag, path):
    nl, lands = main_counts(path)
    if not nl:
        raise SystemExit(f"мейн пуст: {path} (нужна секция Deck)")
    rec = dict(ts=datetime.now().isoformat(timespec="minutes"), draft=draft8, tag=tag,
               file=os.path.basename(path), main=dict(nl), lands=dict(lands))
    with open(reg_path(setcode), "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"→ {setcode}/{draft8} [{tag}] {sum(nl.values())} нонлендов записано")


def show(setcode, draft8):
    p = reg_path(setcode)
    rows = []
    if os.path.exists(p):
        rows = [json.loads(l) for l in open(p, encoding="utf-8")
                if json.loads(l).get("draft") == draft8]
    if not rows:
        print(f"записей по {draft8} нет ({p})")
        return
    final = next((r for r in reversed(rows) if r["tag"] == "final"), None)
    for r in rows:
        d = ""
        if final and r is not final:
            d = f" · до final: {dist(Counter(r['main']), Counter(final['main']))}"
        print(f"{r['ts']} [{r['tag']:<12}] {sum(r['main'].values())} нонлендов ({r['file']}){d}")
    if final:
        for r in rows:
            if r is final or r["tag"] == "final":
                continue
            print(f"\n[{r['tag']}] vs final:")
            for line in fmt_diff(Counter(r["main"]), Counter(final["main"])):
                print(line)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "diff" and len(sys.argv) >= 4:
        a_nl, a_l = main_counts(sys.argv[2])
        b_nl, b_l = main_counts(sys.argv[3])
        print(f"расстояние мейнов: {dist(a_nl, b_nl)} карт "
              f"(A {sum(a_nl.values())} / B {sum(b_nl.values())} нонлендов)")
        for line in fmt_diff(a_nl, b_nl):
            print(line)
        if a_l != b_l:
            print(f"   земли: A {dict(a_l)} / B {dict(b_l)}")
    elif cmd == "add" and len(sys.argv) >= 6:
        add(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
    elif cmd == "show" and len(sys.argv) >= 4:
        show(sys.argv[2], sys.argv[3])
    else:
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
