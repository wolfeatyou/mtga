"""АНТИ-ДРЕЙФ: Premier и Quick обязаны рендерить один и тот же пак ОДИНАКОВО.

Парсеры лога у них разные (PackCards vs BotDraftDraftStatus) — и это нормально.
Но всё, что ниже парсера (тир, GIH, пар-GIH, IWD, ALSA, тир пика, флаги кастуемости,
баннеры, пул), обязано идти через общий draft_live.render_block. Этот тест собирает
два синтетических лога с ОДНИМ И ТЕМ ЖЕ паком и пулом, гоняет оба пути и сверяет вывод
построчно. Разъехалось — тест красный.

Появился после того, как у quickdraft.py нашлись СВОИ пороги тира (S≥60 против A≥60),
отсутствие пар-GIH/⚠trap/флагов и рейтинги без фильтра game_count — то есть одна карта
показывалась в двух режимах по-разному, и заметить это можно было только глазами.
"""
import json, os, subprocess, sys, tempfile

SKILL = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SKILL)
os.environ["MTGA_SET"] = "msh"
os.environ["MTGA_OFFLINE"] = "1"
sys.argv = ["x", "msh"]
import draft_live as DL

by_id = DL.load_cards()


def find(name):
    for aid, c in by_id.items():
        if c.get("name", "").split(" //")[0].lower() == name.lower():
            return aid
    raise SystemExit("нет карты " + name)


PACK = [find(n) for n in ["Web Up", "Bold Biochemist", "Crowd of True Believers",
                          "Atlantis Attacks", "Aerial Doombot"]]
POOL = [find(n) for n in ["Aerial Doombot", "Bold Biochemist", "Web Up",
                          "Kree Commandos", "Justice, Vance Astrovik",
                          "Brave Brawler", "Frozen in Ice", "Stature, Size Shifter",
                          "Falcon, Winged Wonder", "Colleen Wing, Street Samurai",
                          "Agent of Atlas", "Raft Security Officer"]]
PN, PK = 2, 3

# ── лог Premier: PackCards + MakePick-строки ──────────────────────────────────
prem = [f'[UnityCrossThreadLogger]Draft.Notify {{"draftId":"PARITYTEST0001",'
        f'"SelfPack":{PN},"SelfPick":{PK},"PackCards":"{",".join(map(str, PACK))}"}}']
for i, cid in enumerate(POOL):
    prem.append(f'==> MakeHumanDraftPick(1) {{\\"draftId\\":\\"PARITYTEST0001\\",'
                f'\\"Pack\\":{i // 14 + 1},\\"Pick\\":{i % 14 + 1},\\"GrpIds\\":[{cid}]}}')

# ── лог Quick: один BotDraftDraftStatus, где пак и пул лежат вместе ───────────
payload = json.dumps({"DraftPack": [str(c) for c in PACK],
                      "PickedCards": [str(c) for c in POOL],
                      "PackNumber": PN - 1, "PickNumber": PK - 1,
                      "EventName": "QuickDraft_MSH_Parity"})
quick = ['[UnityCrossThreadLogger]BotDraftDraftStatus {"Payload":"'
         + payload.replace('"', '\\"') + '"}']


def run(script, lines, args):
    with tempfile.NamedTemporaryFile("w", suffix=".log", delete=False, encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
        path = f.name
    env = dict(os.environ, MTGA_LOG=path, MTGA_OFFLINE="1")
    out = subprocess.run([sys.executable, os.path.join(SKILL, script)] + args,
                         capture_output=True, text=True, env=env)
    os.unlink(path)
    if out.returncode != 0:
        raise SystemExit(f"{script} упал:\n{out.stderr[:800]}")
    return out.stdout


a = run("draft_live.py", prem, ["msh"])
b = run("quickdraft.py", quick, ["msh"])


def cards(txt):
    """Строки карт — то, что должно совпасть до символа."""
    return [l.rstrip() for l in txt.splitlines() if l.lstrip().startswith("[")]


def banners(txt):
    return [l.rstrip() for l in txt.splitlines() if l.lstrip().startswith("⚑")]


ca, cb = cards(a), cards(b)
ba, bb = banners(a), banners(b)

print("PREMIER — строки карт:")
for l in ca:
    print("  " + l[:120])
print("\nQUICK — строки карт:")
for l in cb:
    print("  " + l[:120])

assert ca, "Premier не отрендерил ни одной карты — сломался парсер или фикстура"
assert cb, "Quick не отрендерил ни одной карты"
assert ca == cb, ("РАСХОЖДЕНИЕ рендера карт!\nPremier: %s\nQuick:   %s"
                  % ("\n".join(ca), "\n".join(cb)))
assert ba == bb, ("РАСХОЖДЕНИЕ баннеров!\nPremier: %s\nQuick:   %s"
                  % ("\n".join(ba), "\n".join(bb)))

print("\nБАННЕРЫ (совпадают в обоих режимах):")
for l in ba:
    print("  " + l[:120])

print(f"\n✅ ПАРИТЕТ ПОДТВЕРЖДЁН: {len(ca)} строк карт и {len(ba)} баннеров идентичны")
print("   Premier и Quick идут через один render_block — дрейф невозможен без падения теста.")
