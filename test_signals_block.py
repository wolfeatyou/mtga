"""Интеграционный тест: баннер ⚑ КРИВАЯ должен попадать в блок, который возвращает watch."""
import os, sys
os.environ["MTGA_SET"] = "msh"
os.environ["MTGA_OFFLINE"] = "1"
sys.path.insert(0, os.path.expanduser("~/.claude/skills/mtg-draft-helper"))
sys.argv = ["draft_live.py", "msh"]
import draft_live as D

by_id = D.load_cards()
ratings = D.load_ratings()

def find(name):
    for aid, c in by_id.items():
        if c.get("name", "").split(" //")[0].lower() == name.lower():
            return aid
    raise SystemExit("нет карты " + name)

PACK = [find(n) for n in ["Crowd of True Believers", "Atlantis Attacks",
                          "Kree Commandos", "Web Up", "Bold Biochemist"]]
POOL_THIN = [find(n) for n in ["Web Up", "Kree Commandos", "Atlantis Attacks",
                               "Political Triumph", "Captain America, Living Legend"]]
POOL_OK = POOL_THIN + [find(n) for n in ["Crowd of True Believers", "Bold Biochemist",
                                         "Aerial Doombot", "Brave Brawler", "Colleen Wing, Street Samurai"]]

def run(pool, pnum, pick, label):
    D.find_packs = lambda text: [(pnum, pick, PACK, None)]
    D.find_my_picks = lambda text, did=None: pool
    D._record_hist = lambda *a, **k: None
    sig, block = D.current_block("FAKE", by_id, ratings, "testdraft")
    print(f"\n{'='*70}\n{label}\n{'='*70}")
    print(block[:900])
    return block

b1 = run(POOL_THIN, 2, 1, "A. P2P1, пул без дешёвых тел → ожидаем НЕДОБОР + кандидаты")
assert "⚑ КРИВАЯ — НЕДОБОР" in b1, "баннер недобора НЕ попал в блок!"
assert "Crowd of True Believers" in b1.split("PACK")[0], "кандидат не назван в баннере!"
assert b1.index("КРИВАЯ") < b1.index("PACK"), "баннер должен быть ВЫШЕ пака!"

b2 = run(POOL_OK, 3, 1, "B. P3P1, 5 дешёвых тел → ожидаем ✓, без директивы")
assert "⚑ КРИВАЯ:" in b2 and "НЕДОБОР" not in b2, "ложное срабатывание на полном пуле!"

print("\n\n✅ ВСЕ ПРОВЕРКИ ПРОШЛИ:")
print("   · баннер печатается ВЫШЕ пака (виден до карт)")
print("   · при недоборе называет конкретных кандидатов из ЭТОГО пака")
print("   · при закрытой квоте не шумит")
