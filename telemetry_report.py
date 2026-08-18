#!/usr/bin/env python3
"""Сводка телеметрии советчика: согласие игрока с ранжировкой по нашим драфтам.

Читает pools/<set>_*_telemetry.jsonl (пишет draft_live.record_telemetry на каждом
пике живого драфта — Premier и Quick одинаково). Джойн: pack.i == pick.i.

    python3 telemetry_report.py hob             # все драфты сета
    python3 telemetry_report.py hob 48b3ee3d    # один драфт (по draft8-тегу)

Печатает: долю пиков = топ-1 ранжировки (adv[0]), долю = топ по голому GIH
(gih_top), и список расхождений поимённо — это материал для разбора «кто был прав»
после матчей (JOURNAL § 8.12). Эталон для сравнения из § 8.9/8.11: трофейщики MSH
берут топ пака по GIH в 43.5% пиков, топ-игроки (wr>=0.62) — в 44.6%.
"""
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def load_events(path):
    """(packs: {i: pack_rec}, picks: {i: name}) одного драфта."""
    packs, picks = {}, {}
    for line in open(path, encoding="utf-8"):
        try:
            rec = json.loads(line)
        except Exception:
            continue
        if rec.get("t") == "pack":
            packs.setdefault(rec.get("i"), rec)
        elif rec.get("t") == "pick":
            picks[rec.get("i")] = rec.get("name")
    return packs, picks


def summarize(path, verbose=True):
    packs, picks = load_events(path)
    joined = [(i, p, picks[i]) for i, p in sorted(packs.items()) if i in picks]
    if not joined:
        return None
    agree_adv = sum(1 for _, p, nm in joined if p.get("adv") and p["adv"][0] == nm)
    agree_gih = sum(1 for _, p, nm in joined if p.get("gih_top") == nm)
    n = len(joined)
    tag = os.path.basename(path).replace("_telemetry.jsonl", "")
    print(f"═══ {tag}: {n} пиков с советом ═══")
    print(f"  взят топ-1 ранжировки: {agree_adv}/{n} ({agree_adv/n*100:.0f}%)")
    print(f"  взят топ по голому GIH: {agree_gih}/{n} ({agree_gih/n*100:.0f}%)")
    if verbose:
        diffs = [(i, p, nm) for i, p, nm in joined if p.get("adv") and p["adv"][0] != nm]
        if diffs:
            print("  расхождения с ранжировкой:")
            for i, p, nm in diffs:
                print(f"    P{p['pn']}P{p['pk']:>2}: совет {p['adv'][0]!r} → взято {nm!r}")
    return n, agree_adv, agree_gih


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    sc = sys.argv[1].lower()
    tag = sys.argv[2][:8] if len(sys.argv) > 2 else "*"
    paths = sorted(glob.glob(os.path.join(HERE, "pools", f"{sc}_{tag}_telemetry.jsonl")))
    if not paths:
        print(f"нет файлов pools/{sc}_{tag}_telemetry.jsonl — телеметрия пишется "
              f"живым драфтом автоматически с 18.08.2026")
        return 1
    tot = adv = gih = 0
    for p in paths:
        r = summarize(p, verbose=(len(paths) <= 3))
        if r:
            tot += r[0]; adv += r[1]; gih += r[2]
    if len(paths) > 1 and tot:
        print(f"\nИТОГО по {len(paths)} драфтам: топ-1 ранжировки {adv/tot*100:.0f}% · "
              f"голый GIH {gih/tot*100:.0f}% ({tot} пиков)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
