---
name: mtg-draft-helper
description: Live MTG Arena draft pick advisor + post-game replay analysis + deck building for Limited. Reads the Arena Player.log, ranks the current pack by 17Lands GIH win-rate, and recommends each pick given pool/colors/curve. Supports Secrets of Strixhaven (sos), Murders at Karlov Manor (mkm), and Marvel Super Heroes (msh). Use when the user wants help drafting in MTG Arena, live pick advice during a draft ("помоги с драфтом", "какую карту брать", "следи за паками", "start a draft"), building/comparing a Limited deck, post-game analysis ("разбери партию", "analyze my game"), or the SOS draft cheat sheet. Do NOT use for Constructed/competitive deckbuilding outside Limited or for non-MTG tasks.
---

# MTG Arena Draft Helper

Live drafting assistant for **MTG Arena Limited**. The user opens packs in Arena; you read the log, rank the pack by **17Lands GIH win-rate**, and call each pick out loud with reasoning grounded in their pool, colors, and curve. Also does post-game replay analysis and deck building.

**Supported sets:** `sos` (Secrets of Strixhaven, Premier) · `mkm` (Murders at Karlov Manor, Quick) · `msh` (Marvel Super Heroes, Premier — current).

All commands use absolute paths so they work from any working directory. Set `SKILL=~/.claude/skills/mtg-draft-helper`.

## Prerequisite (one-time, user does this)
Arena → **Settings → Account → Detailed Logs (Plugin Support)** = ON, then **restart Arena**. Without it the log has no draft/match data. Log lives at `~/Library/Logs/Wizards Of The Coast/MTGA/Player.log`.

---

## Mode 1 — Live draft (the main job)

The user does **not** type "pack" each pick. The flow is **wake → self-read → advise**: a background `wake` loop blocks until a new pack appears and just **wakes you** (one-line marker, no analysis); then **you re-read the *current* pack yourself** with a snapshot and evaluate *that*. Re-reading at advise-time means you judge the freshest pack in the log, not a stale one captured while you were thinking. Loop it.

**При старте каждого нового драфта — обязательно прочитать перед первым пиком:**
```bash
cat ~/.claude/skills/mtg-draft-helper/<set>_knowledge.md   # ДРАФТ-мета: пары open, сигналы, пик-уровень
cat ~/.claude/skills/mtg-draft-helper/<set>_insights.md    # ИНСАЙТЫ ИЗ ИГР: как наши колоды выигрывают, over/under в бою, матчапы
# + читшит сета: msh → msh_cheat.md ; sos/mkm → draft_cheat.md
cat ~/.claude/skills/mtg-draft-helper/msh_cheat.md          # (для sos/mkm: draft_cheat.md)
```
Что вынести: какие архетипы open, какой топ-1 сейчас, какие карты over/underperform свой GIH, **в какую выигрышную линию/архетип тянуть исходя из `<set>_insights.md`** (что реально побеждает в наших партиях).

**Start a NEW draft** (resets last-seen pack + history state):
```bash
python3 ~/.claude/skills/mtg-draft-helper/draft_live.py sos wake fresh
```
**Every subsequent pick** (re-arm the waker):
```bash
python3 ~/.claude/skills/mtg-draft-helper/draft_live.py sos wake
```

Run each `wake` as a **background Bash command**. When it completes:
- If output is `WAKE <pack>/<pick> — N карт …` → a new pack landed. **Now run the snapshot yourself** to read and evaluate *the current pack*:
  ```bash
  python3 ~/.claude/skills/mtg-draft-helper/draft_live.py sos
  ```
  Read it, give the pick (see below), then immediately relaunch `wake` for the next pack. The snapshot **records the pack it showed as "seen"**, so the next `wake` won't re-fire on a pack you already advised (anti-lag).
- If output is `WAITING` (25 min, nothing new) → just relaunch `wake`. The draft isn't open yet, or the user is thinking.
- If output is `DRAFT COMPLETE` → the draft ended; move to deck building (Mode 3). **После сборки колоды — спросить пользователя что запомнить из этого драфта и записать в `<set>_knowledge.md`.**

Why split it: the old `watch` did detection **and** printed the analysis at detection-time — so if you lagged, you'd advise on a pack the user had already moved past. The waker is now a cheap pure detector (regex only, no card/rating/network load); **you** pull the live pack the instant you actually advise. (The old combined `watch` mode still exists if ever needed — it prints the full analyzed block on detection.)

The snapshot prints cards **sorted by GIH WR**, each with `[tier|GIH xx.x|<PAIR> xx.x|IWD ±y.y|OH zz.z|ALSA a.a]` plus pool-aware flags, the booster/pick number, and the user's full **POOL** (colors + curve).
- **GIH** — win-rate of games with the card in hand (the headline number; tier is derived from it).
- **`<PAIR>` (e.g. `WR 52.8`)** — *color-filtered* GIH: the card's win-rate **in decks of your current two-color pair**, fetched live from 17Lands and cached to `cache_17l_<set>_<PAIR>.json`. Shown only once the pool commits to two colors and 17Lands has a sample. This is the real "how does it play in *my* archetype" number — compare it to global GIH (e.g. `Wander Off` GIH 55.8 but `WR 49.9` = worse in R/W than its overall rating suggests). Degrades silently offline.
- **IWD** — *improvement when drawn*: how much better games go when you draw it vs not. **IWD < 0 prints `⚠trap`** — drawing the card statistically *hurts*; it's a low-floor build-around (e.g. Dualcaster Mage: GIH 50.6 but IWD −2.2, OH 46.0). High positive IWD = real bomb/build-around (Exhibition Tidecaller IWD +9.8).
- **OH** — opening-hand win-rate: the card's *floor* (is it dead in the opener?).
- **Pool-aware flags** (after the bracket):
  - **`~splash`** — needs exactly one off-color pip vs your current colors (splashable with fixing).
  - **`✗offcolor`** — needs two+ off-color pips (not realistically castable). Operationalizes the "castability > GIH" principle automatically.
  - **`★synergy`** — a spell-matters payoff (Opus/Repartee/magecraft/"whenever you cast") **and** your pool already has ≥6 instants/sorceries to enable it. Marks when a build-around is actually supported — a `⚠trap ★synergy` together means "low global floor, but your deck pays it off."
- These signals are all **derived from 17Lands** (no second source like untapped.gg needed). The flags need a committed pool, so they appear from ~pick 5 on.
- **`─── СИГНАЛЫ ───` banner (printed ABOVE the pack by the snapshot — read and relay it first).** The snapshot auto-detects what the per-pick GIH sort can't, the exact class of mistakes that cost real drafts:
  - **`⚑ СИЛЬНЕЕ ВНЕ ЦВЕТА`** — the best off-color card beats your best in-color card by ≥3 GIH (only picks ≤9). A pivot/splash flag — the tool's `✗offcolor` demotion actively hides this, so the banner counter-balances it. Don't reflexively pass it; weigh the pivot.
  - **`⚑ ПИВОТ?`** — picks 6–10: ≥2 strong (GIH ≥56) off-color cards, or one ≥58, are flowing → that color is **open on your left**. Real signal to move.
  - **`⚑ КОЛЕСО`** — a GIH ≥54 card came back one full lap (pod=8, the pick−8 pack returned as a subset) → its color is open, lean in.
  - **`⚑ SOUP-AUDIT (пик 5/6)`** — prints your fixing count: ≥3 = take best card of any color / go soup; <3 = stay 2-color, splash only with Rule of Three.
  - **Why this exists:** the pack is sorted by *global GIH* then penalizes off-color — a "stay-the-course" optimizer with no cross-pick memory. These banners add the signal/wheel/power-gap reads the sort structurally can't. **When a banner fires, address it in your pick reasoning** — don't just take the top in-color card.

### How to give a pick
**Output format — print exactly this short block per pick:**
```
P{pack}/P{pick} — **{Card}** · {P/T} · {Color} · {mana}
**якорь:** {anchor card + archetype}   ← from pick 3 onward; "рано" if not set
**собираем:** {our colors + plan}
**открыто:** {open colors}             ← ONLY if a СИГНАЛЫ banner fired
**не хватает:** {gap: curve / evasion / removal}
**пивот:** {pivot note}                ← ONLY if a СИГНАЛЫ banner fired
```
- Card name **bold**, ALWAYS in English. Colors as WORDS: White/Blue/Black/Red/Green (C=Colorless).
- Drop `открыто` / `пивот` entirely when no signal fired. P1P1–P2: collapse to header + `собираем: рано — беру силу`.
- **No GIH numbers or alternatives unless the user asks «почему».**

**Pick process — always in this order:**
1. **Scan** — read full pack by GIH. Flag the top in-color card, top off-color card, and any high-IWD outlier.
2. **Think** — answer exactly 3 questions (30 seconds max):
   - **Якорь + синергия:** what is our anchor/engine, and does this card feed it? A card that doubles the anchor's output beats a higher-GIH card with no hook. If no anchor yet: which card in this pack *could* become one?
   - **Дыра:** what's the one thing the deck is most missing right now? (evasion / hard removal / curve slot). The card that fills it wins even at lower GIH.
   - **Дельта:** do I already have 2+ copies of this card's role? If yes — skip it entirely, look at everything else.
3. **Pick** — priority order: **якорь-синергия > дыра > IWD-потолок > GIH**. GIH is the starting point, not the answer.

**Hard rule: max 2 copies of any common/uncommon in the 40.** At 2+ copies, that card doesn't exist in this pack — evaluate only the rest.

**Bad pack rule:** if nothing feeds the anchor, fills a gap, or has high IWD — take the card most likely to wheel or signal an open color for the next pack. Don't default to "highest GIH filler".

**Принципы — иерархия при конфликте: якорь > синергия > дыра > IWD-потолок > GIH > кривая.**
Когда принципы конфликтуют, побеждает более высокий в этой цепочке.

**Цель и философия:**
1. **Build for the trophy, not the average.** Цель — 7-0, а не 4-3. "Надёжная средняя колода" выигрывает ~55%. Нужна колода с чётким потолком: якорь-движок + финишёр + синергии. Вопрос не "эта карта всегда нормальна?" а "эта карта поднимает наш потолок?"
2. **Identify the anchor in P1–P3, draft around it.** Якорь — высокоIWD бомба или движок (Leader IWD +15, Kang IWD +9). Каждый следующий пик: "кормит ли это якорь?" Connive-карта, кормящая Leader = субъективно +2–3 GIH сверх её числа. Без якоря к P1P4 — берём карту с наибольшим потенциалом стать якорём.
3. **Draft into the format's top tier.** При старте драфта прочитать `<set>_knowledge.md` + читшит сета (msh→`msh_cheat.md`, sos/mkm→`draft_cheat.md`) — какой архетип топ-1 сейчас? Тянуться в него, а не в "любые 2 цвета". Никогда не строить 2-цветный removal-pile без якоря — это проигрышная позиция.

**Оценка карты:**
4. **Removal и evasion ценнее, чем кажется.** Unconditional/instant removal > conditional. Evasion (флаер, trample, unblockable) = способ заканчивать партии. Считать отдельно: hard removal ≥2–3 + evasion ≥2–3.
5. **Floor vs ceiling (IWD):** GIH = среднее. IWD = потолок. Карта GIH 58 + IWD +9 часто выигрывает больше партий чем GIH 62 + IWD +1. При наличии якоря-движка приоритизировать high-IWD карты — они реализуют потолок.
6. **Castability beats raw GIH.** ✗offcolor = карта не существует пока нет фикса. ~splash = реально только при 3+ источниках (Rule of Three). Исключение: ✗offcolor на пике ≤5 при 0 коммите = сигнал пивотировать, а не брать.
7. **Quadrant Test + Vanilla Test.** Оценить карту в 4 состояниях: Opening / Parity / Ahead / Behind. Хороша в 3–4 = премиум; в 1–2 = узкий филлер. Существо: ≥ vanilla X/X за ману? Разницу составляют keywords/ability.
8. **Кривая — считать отдельно существ и спеллы.** Removal/utility не заменяют тела в плане каста по кривой. Цель существ (WotC/Karsten): 2-дроп 4–6 · 3-дроп 3–5 · 4-дроп 2–4 · 5-дроп 1–3. Архетип диктует сдвиг: aggro — круче вниз; engine/control — removal вместо топа кривой.
9. **Deck targets:** ~17 земель · 16–18 существ · ≥2–3 hard removal · ≥2–3 evasion · 2–3 трюка. Engine-архетипы (connive/spells) подстраивают пропорции под движок.
10. **Juza tiebreaker:** при равных якорь/дыра/IWD — берём дешевле. Дешёвые карты разыгрываются больше партий.

**Сигналы и пивот:**
11. **Читать сигналы и колёса.** Сильная карта вернулась поздно (пик 6+ / 9+) = цвет открыт слева. ⚑ баннеры — обязательно адресовать в рассуждении, не игнорировать.
12. **Justified risk — когда брать:**
    - **Слабый пул (пики 1–5 все B-tier, нет якоря):** high-IWD build-around лучше надёжного B-tier — медиокрная надёжная и медиокрная рискованная колоды оба проигрывают, рискованная иногда выигрывает крупно.
    - **Сильный сигнал (⚑ПИВОТ пики 3–6):** пивот стоит 1–2 карты но открывает поток топ-архетипа. Цена пивота < цена застревания в contested цвете.
    - **Якорь уже есть:** имея бомбу-якорь, можно брать ⚠trap build-around — якорь покрывает низкий floor.
    - **Никогда:** ✗offcolor без фикса после пика 6; сплеш 4-го цвета с 0 землями; tribal тема без плотности к пику 6.

**Красные флаги:**
13. **Card-quality red flags:** симметричные эффекты; узкие/conditional карты мёртвые в руке; >2 копий одной commons/uncommons (правило максимума). При 2+ копиях — карта не существует в этом паке.

If a card shows `[нет данных]` or an unmapped name, look it up in `17l_<set>_premierdraft.json` (has `name/color/rarity/types/ever_drawn_win_rate`) or `<set>_set.json` before judging it.

### Накопленные знания о сете — ДВА файла (ЧИТАТЬ ОБА ПРИ СТАРТЕ КАЖДОГО ДРАФТА)
Два живых per-set файла с разделением ролей. Оба читать перед первым пиком — они содержат то, что глобальный GIH 17L не отражает.

**1. `<set>_knowledge.md` — ДРАФТ-мета (что происходит в пике).**
- **Архетипы (Arena meta)** — какие пары реально open/contested на Arena vs 17L
- **Карты: переоценены / недооценены** — пик-уровень over/underperform GIH
- **Сигналы** — что течёт в каком порядке, signpost-карты открытого архетипа
- **Уроки** — ошибки/правильные решения драфта с датой

**2. `<set>_insights.md` — ИНСАЙТЫ ИЗ ИГР (что происходит в партии).** Чем наши колоды реально выигрывают и проигрывают:
- **Наша колода + выигрышные линии** — какой план/финишёр работает (напр. Stature unblockable→памп)
- **Over/under-performи в БОЮ** — карты, чья игровая сила ≠ их GIH (напр. Mister Fantastic ↑, Moonstone ↓)
- **Опасные карты оппонентов** — что наказывает наш план и как играть вокруг
- **Матчапы** — кто фаворит/нет и почему
- **Уроки сборки** — структурные требования (эвейжн/removal counts и т.п.)
- Записывать ТОЛЬКО проверенное по логу (см. правило точности разбора), с датой и числом подтверждающих игр.

**Зачем два:** `knowledge` отвечает «кого ПИКать», `insights` — «во ЧТО собирать и как этим играть». В драфте тянись в линию, которая по `insights` реально берёт трофеи, а не в «любые 2 цвета».

**Когда обновлять:**
- После `analyze_game.py` / разбора партии — новый проверенный паттерн (карта over/under, рабочая линия, опасный матчап) → дописать в `<set>_insights.md`.
- После `DRAFT COMPLETE` — драфт-наблюдения (сигналы, открытые пары) → в `<set>_knowledge.md`.
- В любой момент — "запомни: ..." → немедленно записать в нужный из двух (геймплей → insights, драфт → knowledge).

**Как использовать в пике:**
- При старте драфта: `cat <set>_knowledge.md` И `cat <set>_insights.md`.
- В Think-шаге: «что знаем об этой карте/архетипе из прошлых драфтов (knowledge) И как это играет/выигрывает (insights)?»

**Файлы:** knowledge — `msh_knowledge.md` · `sos_knowledge.md` · `mkm_knowledge.md` ; insights — `msh_insights.md` (заводить `<set>_insights.md` по мере накопления партий в сете).

### Reference while drafting
- `draft_cheat.md` — set mechanics + the 5 SOS college archetypes (Lorehold/Silverquill/Prismari/Quandrix/Witherbloom) and MKM pairs.
- `sos_tier.md` / `mkm_tier.md` / `msh_tier.md` — GIH tier lists.
- `sos_cheatsheet.html` / `msh_cheatsheet.html` — visual draft cheat sheets (open in browser).
- **MSH (Marvel Super Heroes)** — Arena 23.06.2026. 17L live с 25.06. Advise from `msh_cheat.md` + `msh_tier.md` + `msh_knowledge.md`. Core axes: +1/+1 counters (74), Villain/Hero tribal, Power-up, Teamwork, Connive, Plan.
- `mtg_readme.md` — full setup notes + **§6 match lessons** (read these; они encode реальные ошибки из партий).

---

## Mode 2 — Post-game analysis

After a match, run:
```bash
python3 ~/.claude/skills/mtg-draft-helper/analyze_game.py        # last game
python3 ~/.claude/skills/mtg-draft-helper/analyze_game.py -2     # game before last
```
Prints: result, opening hand + keep/mull decision, turn-by-turn casts/deaths, life swings, **combat** (attackers with `✓прошёл`=unblocked, plus blocks shown `blocker→attacker`, parsed from GRE `attackState`/`blockState`), an **abilities/engine** summary, and final board. **Combat is now read straight from the log** — don't guess attacks/blocks or ask the player; if a turn shows no `⚔` line, none was declared (or it predates the log slice). Life swings can still lag/include lifegain, so trust the `⚔`/`🛡` lines over inferring from life alone.

**Abilities ≠ spells (parser fix — read the engine summary).** When an *ability* goes on the stack, Arena logs a stack object whose `grpId` is the **ability id**, not a card — these used to print as `⟨неизв. заклинание grpNNNNN⟩` and looked like a phantom "spell cast every turn." They're now resolved via `GameObjectType_Ability` + `objectSourceGrpId`/`overlayGrpId` and shown as `⚡ способность — <карта>`, with repeated activations (≥2) collected into a **`=== ДВИЖКИ / ПОВТОРНЫЕ СПОСОБНОСТИ ===`** block. **Read that block first** — a recurring lifelink/combat trigger (e.g. Startled Relic Sloth, Muse Seeker) is usually the real reason for a lopsided life swing, *not* a mystery spell. Don't attribute unexplained life loss to guesses; check the ⚡/engine lines and the `⊘ overlay`-resolved names. A residual `⟨неопознанный спелл grpNNNNN⟩` (in the card grpId range) is a real card we lack data for — usually an adventure/split *back face* — so name it cautiously, but it is a spell, not an ability.

Give a step-by-step breakdown: correct decisions, mistakes (ranked), and 2–3 takeaways. Honesty rules:
- A slow start from a tapland-only hand is **variance/decklist, not a misplay** — fix it in the draft, not in sequencing.
- Hold **instant-speed interaction for the opponent's turn/combat** (pump toughness vs burn, shrink an attacker) — don't dump it in your main phase.
- vs **go-wide + team pump** (e.g. Root Manipulation): when ahead on life you're the control — keep blockers, count their max alpha before tapping out.
- vs **burn/control (UR Opus):** be the aggressor, overload their answers with redundant threats, don't durdle; one pump can't beat two burn spells.

When the analysis surfaces a durable new lesson, append it to `mtg_readme.md` §6 (general piloting lessons across sets) И/ИЛИ к **`<set>_insights.md`** (per-set: карта over/under в бою, выигрышная линия, опасный матчап) — последнее читается перед каждым драфтом сета. Писать только проверенное по логу, с датой и числом подтверждающих игр.

### Visual HTML replay reports (картинки карт + P/T со счётчиками)
Two renderers turn the parsed game into a styled HTML page with **card images** (hover = zoom ×2.6) and **current P/T including +1/+1 counters/фишки** (read from GRE `power.value`/`toughness.value`, not base stats). On macOS `open <file>` launches it.

- **`replay_moments.py`** — the preferred format. Renders an HTML page with a **header** (📖 overview + 🔑 key moments) then **top-N mistake moments**, each = **position** (rows in table order: 🟥 opp board → 🟦 your board → 🃏 your hand, with P/T + life + your land count) then a **text analysis** of what was wrong. Trigger phrases: «разбери партию» / «разбери топ-3 момента».
  ```bash
  python3 replay_moments.py -2 --turns 9,11,19   # game -2, these turns
  ```
  All text comes from `replay_moments.json`, authored before rendering:
  - `"_overview"`: 1-paragraph arc of the game (HTML-ok: `<b>`).
  - `"_keymoments"`: list of bullet strings (turning points by turn).
  - `"<turn>"`: per-moment mistake analysis (one entry per `--turns` value).
  Position is snapshotted at each turn's start (parse_state on the log slice). Card images + P/T-with-counters are automatic.
  - **Always give a CONCRETE "что надо было сделать", not just a principle** (user feedback). If a turn has no clean better play (e.g. their 4/4 walls your 3/3), say so and name the real, actionable error instead.
  - **Own my own coaching errors** in the analysis when a live call I gave was wrong (the user values the honesty).
- **`replay_report.py`** — full turn-by-turn timeline (every turn, casts/deaths/combat + optional per-turn advice from `replay_advice.json`). Heavier; use only if the user wants the whole game, not the highlights.

Workflow for «разбери партию»: run `analyze_game.py [-N]` → pick the key turns → write `replay_moments.json` → `replay_moments.py [-N] --turns ...` → `open replay_moments.html`.

---

## Mode 3 — Deck building / cheat sheet

- Compare/tune lists by GIH + curve + the principles above. SOS sample decks: `sos_draft_deck.md`.
- Output decklists in **MTGA import format**: `Deck` header, then `<count> <Name> (<SET>) <collector#>`, optional `Sideboard`. Keep within the user's pool unless they say they'll craft missing cards.
- **Premier Draft = Bo1 (одна игра на матч) — сайдбординга НЕТ.** Никаких «подмен по матчапам» / «против агро занеси X». Колода строится один раз и играет single-game матчи. «Sideboard» — это просто карты пула вне 40 (пригодятся только если переосмыслить мейн перед СЛЕДУЮЩИМ драфт-матчем, не внутри текущего). Не советовать in-match свопы. (Traditional Draft — Bo3 со сайдом, но это отдельный режим; по умолчанию Premier = Bo1.)

### ALWAYS describe the deck after building it (обязательный формат)
**После сборки/тюнинга любой колоды — всегда выдать два блока, не только лист + голдфиш:**

**1. Сила: <буква-тир ≈X/10>**
- **Что даёт силу** — якорь/бомба, плотность и качество removal, эвейжн, карт-преимущество (конкретные карты).
- **Что ограничивает (честно)** — сила пары на Arena (из `<set>_knowledge.md`), проблемы кривой, реактивность/уязвимость к топ-архетипам, зависимость от 1 карты. Не приукрашивать.
- **Реалистичный итог** — пол и потолок словами («уверенные 4–5 побед с апсайдом на трофей»), не обещать 7-0.

**2. Как играть**
- **Роль:** ты контроль / агро / темпо? Одной фразой — и из неё следует всё остальное.
- **Ключевые правила пилотирования:** что держать на инстант-скорости, чем выживать рано, как собрать движок-якорь (сиквенсинг синергий), win condition.
- **Mulligan:** что оставлять / что сбрасывать.
- **Матчапы:** хороший и плохой, и как играть каждый (vs агро — стабилизируйся/не дёргайся; vs контроль — карт-преимущество/flash вокруг removal). Помнить: Premier = Bo1, это план НА ИГРУ, не сайд.

Тон — как у тренера: честно про слабости, конкретные действия, не общие принципы. (Согласовано с пользователем 25.06.2026.)

### ALWAYS goldfish a deck you build — `draft_goldfish.py`
**Whenever you build, tune, or compare a Limited deck, run the goldfish sim and report the numbers as part of the answer** (not just the list). It quantifies the things GIH/curve can't: mulligan rate, early-survival, colour/splash reliability, flood/screw, top-end castability.

```bash
# write the maindeck to an MTGA-format .txt, then:
cd ~/.claude/skills/mtg-draft-helper && python3 draft_goldfish.py <deck.txt> [N]
```
- Generic: parses any MTGA decklist (maindeck only, stops at `Sideboard`) and pulls cmc / pips / type / produced-mana / tapland status from `sos_set.json` (+ `mkm`/`msh`). Handles hybrid `{C/D}`, twobrid `{n/C}` (→ generic), and `{X}` (→ cmc+1). Auto-tags the highest-cmc creature as the tracked "bomb".
- Mana model: taplands enter tapped; any-colour rocks (Trove-type) + basic-fetch (Env-type) are auto-detected from oracle text and modelled, so the splash line shows **lands-only "floor" vs "real" (with fixers)** — relay both. I/S-only dorks count for noncreature spells only.
- Default `N=20000`. Re-run on each candidate list to A/B a swap (e.g. the deck-defining tension is usually early-removal/early-blocker % vs card-quality).
- When tuning, lead the recommendation with the metric that moved (e.g. "−1 5-drop draw → +1 cheap removal lifts removal-by-T3 from 33%→45% at 0 cost to screw"). A swap that doesn't move a goldfish metric or curve is probably not worth it.
- Save the list the user lands on as `sos_my_deck.txt` (or `<set>_my_deck.txt`) so it's re-runnable.

### Cheat sheet
- Regenerate the SOS cheat sheet (run from the skill dir so it finds `sos_cards.json`):
  ```bash
  cd ~/.claude/skills/mtg-draft-helper && python3 build_sos_cheatsheet.py
  ```

---

## Adding a new set
1. `<set>_set.json` — Scryfall cards (`https://api.scryfall.com/cards/search?q=set:<code>&unique=cards`, send a User-Agent header).
2. `17l_<set>_premierdraft.json` — 17Lands card ratings (GIH WR, ALSA).
3. Add the set to `RATING_FILE` in `draft_live.py`. Then `draft_live.py <set> watch` works.
