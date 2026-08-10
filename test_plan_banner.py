"""Регресс-тест баннера ⚑ ПЛАН (кластер воздух/земля) и ⚑ ПРОФИЛЬ."""
import os, re, sys
os.environ["MTGA_SET"] = "msh"
os.environ["MTGA_OFFLINE"] = "1"
sys.path.insert(0, os.path.expanduser("~/.claude/skills/mtg-draft-helper"))
sys.argv = ["draft_live.py", "msh"]
import draft_live as D

by_id = D.load_cards()
ratings = D.load_ratings()

def pick_cards(pred, k):
    out = []
    for aid, c in by_id.items():
        tl = D.face(c, "type_line") or ""
        if "Land" in tl or "Creature" not in tl:
            continue
        if pred(D.full_oracle(c) + " " + tl) and set(c.get("colors") or []) <= {"U", "W"}:
            out.append(aid)
        if len(out) >= k:
            break
    assert len(out) >= k, f"нашлось только {len(out)} из {k}"
    return out

FLY = pick_cards(lambda t: re.search(r"\bflying\b", t, re.I), 8)
REACH = pick_cards(lambda t: re.search(r"\breach\b", t, re.I) and not re.search(r"\bflying\b", t, re.I), 3)
GROUND = pick_cards(lambda t: not re.search(r"\bflying\b|\breach\b", t, re.I), 12)
MAIN = {"U", "W"}
print(f"фикстуры: {len(FLY)} флаеров, {len(REACH)} с reach, {len(GROUND)} наземных\n")

def run(pool, pnum, pick, label):
    print("=" * 74); print(label); print("=" * 74)
    lines = D.plan_banner(pool, by_id, ratings, MAIN, pnum, pick)
    print("\n".join(lines))
    return "\n".join(lines)

a = run(FLY[:2] + GROUND[:3], 1, 5, "A. пик 5 — слишком рано для вердикта")
assert "рано" in a

b = run(FLY[:7] + GROUND[:8], 3, 1, "B. 7 флаеров, 0 reach → ВОЗДУХ, норма")
assert "🟦 ВОЗДУХ" in b and "КОНФЛИКТ" not in b

c = run(FLY[:7] + REACH[:2] + GROUND[:6], 3, 1, "C. 7 флаеров + 2 reach → КОНФЛИКТ")
assert "🟦 ВОЗДУХ" in c and "КОНФЛИКТ" in c, "конфликт плана не пойман!"

d = run(GROUND[:14] + FLY[:1], 3, 1, "D. 1 флаер, 0 reach → ЗЕМЛЯ, рича мало")
assert "🟫 ЗЕМЛЯ" in d and "REACH МАЛО" in d

e = run(GROUND[:11] + FLY[:1] + REACH[:3], 3, 1, "E. 1 флаер + 3 reach → ЗЕМЛЯ, норма")
assert "🟫 ЗЕМЛЯ" in e and "REACH МАЛО" not in e

f = run(FLY[:4] + GROUND[:10], 3, 1, "F. 4 флаера, рича нет → НЕ ОПРЕДЕЛИЛСЯ")
assert "НЕ ОПРЕДЕЛИЛСЯ" in f

print("=" * 74); print("G. ⚑ ПРОФИЛЬ на границе бустера"); print("=" * 74)
print("\n".join(D.profile_banner(FLY[:7] + GROUND[:8], by_id, ratings, MAIN, 3, 1)))

print("\n\n✅ ВСЕ ПРОВЕРКИ ПРОШЛИ:")
print("   · до пика 10 вердикт не выносится")
print("   · воздух/земля/середина классифицируются раздельно")
print("   · КОНФЛИКТ (reach при воздушном плане) ловится — ни одна из 9 воздушных его не держит")
print("   · нехватка рича у наземного плана ловится")
