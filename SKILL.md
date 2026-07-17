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

**Model/effort: default to Sonnet 5, effort medium** for the live loop below — validated via the
`draft_sim.py` latency harness described further down this file (see also the
`mtg-draft-use-sonnet-for-speed` memory). Opus / high / xhigh effort was measured at 20–55s per
pick even in the fastest mode and made the user consistently pick faster than advice arrived.
Switch models with `/model` / `/effort` at the start of a live session if not already there;
there's no pick-clock constraint for post-game analysis or deckbuilding, so Opus/high effort is
fine for those.

The user does **not** type "pack" each pick. The flow is a **single foreground blocking call**:
run `draft_live.py <set> watch` (not `wake`) as a **foreground Bash command with `timeout: 600000`**
(10 min — it blocks until a new pack appears, no polling needed). It returns the fully analyzed
pack **as the tool result** — one inference pass gets you straight to advice, no separate snapshot
call. Give the pick (see format below), then immediately re-issue the same blocking `watch` call
for the next pick. Repeat for the whole draft.

> ### 🔴 HARD RULE — NEVER END YOUR TURN AFTER GIVING A PICK (bug caught 16.07.2026, twice in one draft)
> **The pick text and the next `watch` call MUST go out in the SAME response**: emit the advice
> block, then — with no pause and no closing question — issue the `watch` Bash call in that same
> message. If you end the turn on text, the harness stops and waits for the user, the loop dies,
> and the user has to type "пак" every pick. That is the ONLY failure mode of this loop, and it is
> yours, not the script's.
> - **Do NOT** ask "готов к следующему?", "продолжаем?", "скажи когда" — never hand the turn back.
> - **Do NOT** wait for the user to confirm the pick was made — `MTGA_SETTLE` already debounces it.
> - The loop ends ONLY on: `DRAFT COMPLETE`, a 10-min timeout with no pack, or the user interrupting.
> - Mental check before every send during a live draft: *"is there a `watch` call attached to this
>   message?"* If no → you just broke the loop.

```bash
MTGA_SETTLE=1 python3 ~/.claude/skills/mtg-draft-helper/draft_live.py <set> watch fresh   # first call of a NEW draft
MTGA_SETTLE=1 python3 ~/.claude/skills/mtg-draft-helper/draft_live.py <set> watch         # every call after
```
- `fresh` only on the very first call of a draft (clears last-seen state + pick history).
- **`MTGA_SETTLE=<seconds>`** (default 1.0) debounces rapid picks: if the user picks faster than
  you can answer, the watcher waits for N seconds of "quiet" after the newest pack before
  returning, so it always hands you the LATEST pack and silently skips stale ones instead of
  making you advise on a pick already gone. Tune to your own think time: **Sonnet medium → 1 is
  fine**; if ever running on a slow config, raise to 5–8 so you don't chase a moving target.
- On real Arena logs (not the sim), 17Lands color-pair fetches (`cache_17l_<set>_<PAIR>.json`) hit
  the network the first time a pair isn't cached — usually fine live, but if it ever stalls, set
  `MTGA_OFFLINE=1` to skip the fetch entirely (color-filtered GIH just won't show that pick).
- If the call times out with no pack (10 min of silence) or returns `DRAFT COMPLETE`, stop looping
  — the latter means move to deck building (Mode 3). **После сборки колоды — спросить пользователя
  что запомнить из этого драфта и записать в `<set>_knowledge.md`.**

**При старте каждого нового драфта — обязательно прочитать перед первым пиком:**
```bash
cat ~/.claude/skills/mtg-draft-helper/<set>_knowledge.md   # ДРАФТ-мета: пары open, сигналы, пик-уровень
cat ~/.claude/skills/mtg-draft-helper/<set>_insights.md    # ИНСАЙТЫ ИЗ ИГР: как наши колоды выигрывают, over/under в бою, матчапы
# + читшит сета: msh → msh_cheat.md ; sos/mkm → draft_cheat.md
cat ~/.claude/skills/mtg-draft-helper/msh_cheat.md          # (для sos/mkm: draft_cheat.md)
```
Что вынести: какие архетипы open, какой топ-1 сейчас, какие карты over/underperform свой GIH, **в какую выигрышную линию/архетип тянуть исходя из `<set>_insights.md`** (что реально побеждает в наших партиях).

**Older 2-pass modes (kept for reference, not the default):** a background `wake` loop that only
prints a one-line marker (`WAKE <pack>/<pick> — N карт`), requiring a *separate* snapshot call
(`draft_live.py <set>`) to actually read the pack — this costs a second inference pass per pick
(waking on the notification is itself a pass) and was measured at ~2× slower than the blocking
single-pass call above. Use it only if a foreground blocking call is impossible in your harness.

The snapshot prints cards **sorted by GIH WR**, each with `[tier|GIH xx.x|<PAIR> xx.x|IWD ±y.y|OH zz.z|ALSA a.a]` plus pool-aware flags, the booster/pick number, and the user's full **POOL** (colors + curve).
- **GIH** — win-rate of games with the card in hand (the headline number; tier is derived from it).
- **`<PAIR>` (e.g. `UG 59.8`)** — *color-filtered* GIH: the card's win-rate **in decks of your current two-color pair**, fetched live from 17Lands and cached to `cache_17l_<set>_<PAIR>.json`. Shown only once the pool commits to two colors and 17Lands has a sample. This is the real "how does it play in *my* archetype" number — compare it to global GIH: `Atlantean Cavalry` GIH 53.0 but `UG 50.5` = **worse** in G/U than its global rating suggests; conversely `Ant-Man's Army` GIH 56.9 but `UG 59.8` = **better** in-pair. Degrades silently offline.
- **IWD** — *improvement when drawn*: how much better games go when you draw it vs not. **IWD < 0 prints `⚠trap`** — drawing the card statistically *hurts*; it's a low-floor build-around (e.g. `Knight of Wundagore` GIH 52.9 but IWD −1.7 — looks playable, but drawing it hurts without counter support). High positive IWD = real bomb/build-around (`Leader, Super-Genius` GIH 68.9, IWD +15.6).
- **OH** — opening-hand win-rate: the card's *floor* (is it dead in the opener?).
- **Pool-aware flags** (after the bracket):
  - **`~splash`** — needs exactly one off-color pip vs your current colors (splashable with fixing).
  - **`✗offcolor`** — needs two+ off-color pips (not realistically castable). Operationalizes the "castability > GIH" principle automatically.
  - **`★synergy`** — a spell-matters payoff (prowess / magecraft / "whenever you cast a noncreature spell") **and** your pool already has ≥6 instants/sorceries to enable it. Marks when a build-around is actually supported — a `⚠trap ★synergy` together means "low global floor, but your deck pays it off."
- These signals are all **derived from 17Lands** (no second source like untapped.gg needed). The flags need a committed pool, so they appear from ~pick 5 on.
- **`─── СИГНАЛЫ ───` banner (printed ABOVE the pack by the snapshot — read and relay it first).** The snapshot auto-detects what the per-pick GIH sort can't, the exact class of mistakes that cost real drafts:
  - **`⚑ СИЛЬНЕЕ ВНЕ ЦВЕТА`** — the best off-color card beats your best in-color card by ≥3 GIH (only picks ≤9). A pivot/splash flag — the tool's `✗offcolor` demotion actively hides this, so the banner counter-balances it. Don't reflexively pass it; weigh the pivot.
  - **`⚑ ПИВОТ?`** — picks 6–10: ≥2 strong (GIH ≥56) off-color cards, or one ≥58, are flowing → that color is **open on your left**. Real signal to move.
  - **`⚑ КОЛЕСО`** — a GIH ≥54 card came back one full lap (pod=8, the pick−8 pack returned as a subset) → its color is open, lean in.
  - **`⚑ SOUP-AUDIT (пик 5/6)`** — prints your fixing count: ≥3 = take best card of any color / go soup; <3 = stay 2-color, splash only with Rule of Three.
  - **Why this exists:** the pack is sorted by *global GIH* then penalizes off-color — a "stay-the-course" optimizer with no cross-pick memory. These banners add the signal/wheel/power-gap reads the sort structurally can't. **When a banner fires, address it in your pick reasoning** — don't just take the top in-color card.

### How to give a pick
**Output format — print exactly this block per pick, groups separated by a BLANK LINE (readability — a wall of consecutive label lines was flagged as hard to read):**
```
P{pack}/P{pick} — {Card} · {P/T} · {Color} · {mana}

СОБИРАЕМ: {colors} — {what this MEANS for the deck, one clause, not just a color code}
КАК ПОБЕЖДАЕМ: {win-condition in one clause}   ← ONLY when the pool's density actually supports it (see rule below); otherwise say so honestly

НЕ ХВАТАЕТ: {gap: curve / evasion / removal}
ОТКРЫТО: {open colors}                          ← ONLY if a СИГНАЛЫ banner fired
ПИВОТ: {pivot note}                             ← ONLY if a СИГНАЛЫ banner fired
ЯКОРЬ: {anchor card + archetype}                ← from pick 3 onward; omit if not set yet ("рано")
СОСЕД: {left/right neighbor read}               ← ONLY on a real negative-signal inference (a color that never shows up = neighbor is eating it), not on every pick
ПЛАН: {what to prioritize next booster}         ← ONLY on the LAST pick of a booster (P1P14/P2P14/etc.)
МЫСЛИ: {fork / hypothesis / forward-looking note}  ← ONLY when there's a genuine one worth flagging

  альтернатива (N/10): {card} — {short reason}  ← 0+ lines, own paragraph, indented; N/10 where 10 = this pick's own strength (i.e. rate alternatives RELATIVE to the pick, not an absolute score)

ЛОГИКА: {which gap this plugs + the 1-2 thoughts that actually drove the decision}
```
- **Label style — UPPERCASE word + colon, NO markdown bold, NO `>>` marker (13.07.2026): markdown `**bold**` and raw ANSI escapes were tried in this session's actual host and neither rendered** (asterisks/escape codes showed up literally as text); a leading `>>` was tried too and dropped per user feedback as visual clutter. Plain `LABEL:` in caps is enough to separate the label from body text without any rendering dependency. Card name stays plain (no ** wrapping) for the same reason — verify once at session start whether the host DOES support markdown (some do); if so, bold is a nicer fallback, but default to plain caps unless confirmed otherwise.
- **`логика` is MANDATORY, always last.** Name the specific gap being plugged (curve slot / evasion / removal / fixing / anchor-feed) AND the concrete reasoning that got you there this pick — e.g. "куда ни глянь, кривая тройками забита, а тут наконец 2-дроп-тело + растёт от counters-подтемы уже в пуле" or "removal дефицитно (1 штука), это премиум fight в цвете — очевидный пик, альтернатив не смотрел". This is the "why", not a restatement of `не хватает` — it's the actual chain of thought, one or two sentences, not a GIH dump.
- Card name plain text, ALWAYS in English. Colors as WORDS: White/Blue/Black/Red/Green (C=Colorless).
- Drop `открыто` / `пивот` entirely when no signal fired. P1P1–P2: collapse to header + `собираем: рано — беру силу`.
- **`как побеждаем` — DERIVE from actual pool density every time, never template it.** Don't default to "воздух добивает" (or any other stock phrase) unless evasion/removal/engine counts in the pool genuinely support that plan (§ Оценка карты: evasion ≥2–3, hard removal ≥2–3, or a real engine anchor). Early picks / thin pools with e.g. exactly one flyer → say the plan is undetermined ("план не определён — собираем тела+ответы, ищем финишёр"), don't dress up a hope as a plan. This was a caught mistake (13.07.2026): repeating "воздух добивает" every pick with only 1 flyer in the pool.
- `якорь` / `сосед` / `план` / `мысли` are OPTIONAL and ONE line each — print only on picks where there's a genuine, non-manufactured thing to say. Most picks print none of these; don't pad every pick to look thorough. Added once Sonnet 5 + effort medium proved fast enough to afford them (see `mtg-draft-use-sonnet-for-speed` memory) — don't let them erode the block's terseness or slow the pick below the live pace that justified adding them.
- `альтернатива`: name + a short phrase why it lost (not a GIH number dump), rated N/10 relative to the actual pick (which is implicitly 10/10) — can list more than one, each its own line, only when genuinely worth flagging (not "here's everything I passed" on every pick).
- `сосед`: an inference from what's conspicuously ABSENT across packs (not from a СИГНАЛЫ banner — that's `открыто`/`пивот`'s job) — e.g. "красный вообще не идёт с P1P3 — сосед слева, видимо, в красном".
- `план`: booster-boundary only — 1 line on what to prioritize (curve slot / removal / evasion) walking into the next booster, based on current pool gaps.
- **No GIH numbers unless the user asks «почему».**

**Pick process — always in this order:**
0. **Booster-boundary review — ОБЯЗАТЕЛЬНО на P2/P1 и P3/P1 (первый пик каждого нового бустера).** На границе бустера есть естественная пауза (~минута) — потрать её на ПОЛНЫЙ пересмотр колоды и стратегии, а не на один пик. Два прохода:
   - **(a) Аудит-подсчёт.** Перечитай ВЕСЬ пул покарточно — **полный oracle-текст, не только имена/GIH.** Пересчитай числами: цвета; кривую (существа по CMC **отдельно** от спеллов); роли (hard removal / эвейжн / 2-дропы); в какой ПОЛОСЕ (A/B/C) реально сидим.
   - **(b) Креативный пересмотр — ищи ЛУЧШУЮ колоду в пуле, а не только латай дыры текущего плана.** Спроси себя:
     · Открылась ли более **ОТКРЫТАЯ и мощная полоса**, в которую стоит доломиться (цвет течёт/колесит сильнее нашего)? Цена пивота на границе пака ниже — впереди ещё целый бустер.
     · Есть ли **бомба/хеймейкер**, под которую пора НАЧАТЬ тянуть фикс (сплеш-опцион по Rule of Three)? Ранняя бомба = обязательство строить под неё, а не «фри-карта».
     · Тянет ли пул **теперь** build-around/движок, которого не было на P1 (набралась плотность энейблеров — counters-снежок, connive-движок, go-wide+памп, эвейжн-рейс с неблокируемым финишёром)? Плотность могла перевалить порог.
     · Не собираем ли мы **мягкую середину**? Если да — можно ли ЗАОСТРИТЬ в одну полосу (глубже агро / глубже движок / чище контроль-с-потолком)? И **где wincon** — если его нет, ищи закрывашку СЕЙЧАС.
   - **Выбери самую ВЫСОКОПОТОЛОЧНУЮ из КОГЕРЕНТНЫХ версий**, потом возвращайся к латанию дыр. Изменения озвучь в `собираем`/`не хватает`/`пивот` этого пика (напр. «цвет X пересох — не пивотим» или «набралось 6 counters-энейблеров → тянемся в snowball, а не goodstuff»). Не сбрасывай состояние молча.
1. **Scan** — read full pack by GIH. Flag the top in-color card, top off-color card, and any high-IWD outlier.
2. **Think** — ответь на 3 вопроса. Тайминг по правилу [[mtg-conditional-think-time]]: условные +5с ТОЛЬКО на спорных пиках и на P1 каждого пака (эти секунды идут на синергию/полосу — кормит ли карта ось, есть ли фундамент); на очевидных пиках (один явный бомб/removal) и поздних пиках пака (P10–P13) — не тормозить.
   - **План полосы:** двигает ли карта план ТВОЕЙ полосы? (A/C: board-affecting тело/removal в кривую; B: движок-деталь/пейофф, кормящий якорь.) Карта, усиливающая план полосы, бьёт более-высокий-GIH без роли. Полосы/якоря ещё нет — что ЗДЕСЬ может ими стать?
   - **Дыра:** what's the one thing the deck is most missing right now? (evasion / hard removal / curve slot). The card that fills it wins even at lower GIH.
   - **Дельта:** do I already have 2+ copies of this card's role? If yes — skip it entirely, look at everything else.
3. **Pick** — по иерархии ТВОЕЙ полосы (§ КОММИТ В ПОЛОСУ): **якорь/бомба-закрывашка > карта, двигающая план полосы (тело для A/C; движок-деталь для B) > дыра-роль > при равных дешевле**. GIH — старт, не ответ. «Синергия» высоко ТОЛЬКО в полосе B.

**Hard rule: max 2 copies of any common/uncommon in the 40.** At 2+ copies, that card doesn't exist in this pack — evaluate only the rest.

**Bad pack rule:** if nothing feeds the anchor, fills a gap, or has high IWD — take the card most likely to wheel or signal an open color for the next pack. Don't default to "highest GIH filler".

## 🧭 ГЛАВНЫЙ ПРИНЦИП = КОММИТ В ПОЛОСУ (обновлено 12.07.2026 — заменяет «CABS-универсален»)
**Верхний закон драфта: выбери ОДНУ полосу и коммить в неё. Мягкая середина проигрывает ВСЕМ закоммиченным декам.** (Лог: 2 из 3 — проигрыш глубокому движку; наша дека = 1 Forge + полу-движок + 13–14 существ, закоммичена ни во что.) [[mtg-commit-to-a-lane]] [[mtg-maintain-match-log]]

**Три полосы — у КАЖДОЙ свои правила (камень-ножницы-бумага):**

| Полоса | Правила сборки | Бьёт | Слаба к |
|---|---|---|---|
| **A. CABS-мидрейндж** | board-only: существа+кривая+removal, БЕЗ добора/движков | агро | глубокий движок |
| **B. Глубокий движок/контроль** | добор+движок+connive+ЯКОРЬ; **избыточный добор ПРАВИЛЬНЫЙ (2 Forge — да)** | мидрейндж/goodstuff (грайнд) | быстрое агро |
| **C. Агро** | низкая кривая (2-дропы!)+эвейжн+reach, иди ПОД | движок (не даёт собраться) | нужен пул с 2-дропами |

**⚠️ Правила ОДНОЙ полосы НЕ переносятся на другую.** Наша ошибка: взять CABS-правило «no card draw» и применить к движку (2-я Forge в движке — ПРАВИЛЬНО, а не «у нас уже есть добор»); ИЛИ наоборот — засунуть 1 Forge в не-движок. И то, и то = мягкая середина.

### Полоса A — CABS-мидрейндж (дефолт, если движок не открыт; первоисточник Be Boring)
**CABS = Cards Affecting the Board State** (letstalklimited.wordpress.com/2021/05/19/be-boring-a-guide-to-building-better-draft-decks). Бери ТОЛЬКО board-affecting (существа/removal/трюки); добор/чары/контр/симметрия — НЕ бери (*«just creatures, tricks, and removal»*). Консистентность > бомбы (*«over 10k games wildly incorrect to choose the bomb over casting on curve»*). Числа: **17 земель · 16–18 существ · 3–4 removal · 2–3 трюка**, упор на **2-дропы**, трать ману T2–5, all-equal → дешевле, fill roles, избегай сплешей. (Строгий CABS учит «decide colors early» — но тайминг коммита у нас по единому правилу ниже: для A/C late-commit по сигналам, ранний коммит только для движка B.)

### Полоса B — Глубокий движок/контроль (коммить РАНО, P1–P2, когда полоса открыта)
CABS-правила здесь ПЕРЕВЁРНУТЫ: **добор и движки — это ПЛАН, не мусор.** Бери избыточный card advantage (2+ Forge), engine-детали (Cosmic Cube), connive-фидеры, пейоффы (Cavalry/Masque), **ЯКОРЬ-закрывашку** (Baron Strucker/Leader). MSH deep lane = UB connive/Villain. Требует ПЛОТНОСТИ: half-движок на goodstuff-базе = мягкая середина. Либо ГЛУБОКО, либо не трогай. Слабость: софт к агро → не зевай ранние ходы.

### Полоса C — Агро (иди ПОД движки; только если пул даёт низкую кривую)
Низкая кривая (**плотность 2-дропов** обязательна) + эвейжн + reach/burn: убей движок ДО сборки. MSH-пулы часто не дают 2-дропов → эта полоса реже доступна.

**Иерархия пика ЗАВИСИТ от полосы. Скелет: якорь/бомба-закрывашка > карта, двигающая ПЛАН полосы (тело для A/C; движок-деталь для B) > дыра-роль > при равных ДЕШЕВЛЕ.** Board/кривая-тело НЕ в хвосте ([[mtg-draft-bodies-over-engine]]).

**Выбор полосы и цвета — ОДНО правило коммита (снимает конфликт «decide early» vs late-commit):**

> ### 🧭 ЦВЕТ ВЫБИРАЮТ СИГНАЛЫ, А НЕ ТЫ (директива пользователя 16.07.2026 — приоритет над «взять сильнейшую карту»)
> **Ориентир №1 в драфте — цвета, которые ТЕКУТ.** Не рейтинг пары, не GIH одной карты, не «мы уже вложились».
> **Цена нарушения задокументирована (ран 2W–3L, 16.07):** ⚑-баннер по синему сработал **5 раз**
> (P1P7, P1P10, P2P6, P2P9, P3P6/P3P7), Giant-Sized Flying Ant пасован **дважды** — и в G4 нас
> переехала колода, собранная **ровно из наших пасов** (Aerial Doombot, Flying Ant, Depower, Super Suit).
> **Пасуя открытый лейн, ты его КОРМИШЬ:** за столом 8 человек, он сядет рядом и ты с ним сыграешь.
> - **Порог действия:** **2-й баннер одного цвета до ~P1P10 при пуле ≤9 карт → пивот рассматривать ВСЕРЬЁЗ**,
>   а не отвечать «поздно». «Поздно» на пике 7–10 — это почти всегда отговорка: 9 карт ≠ колода.
> - **«Мы глубоко» — проверяй ЧИСЛОМ, не ощущением:** сколько карт реально теряем? Colorless и
>   вторые копии не теряются. Обычно цена пивота = 2–4 карты, цена застревания в contested цвете = весь драфт.
> - **Сильная карта в НЕ текущем цвете = ловушка.** Сигнал важнее +2 GIH: в открытом цвете ты
>   получишь 10 карт уровня B+, в закрытом — 3 карты уровня A и 10 кусков мусора.
> - **Отсюда и P1P1:** голд лочит цвет ДО появления сигналов → на первых пиках ценность гибкости
>   (colorless > моно > голд) выше, чем разница в IWD. Ошибка 16.07: взят голд Winter Soldier {W}{B}
>   над моно Agent 13 {2}{W} при **GIH 59.7 vs 59.6** — обосновано «IWD выше», а по факту закрыло дверь в синий.
> - В каждом пике с ⚑-баннером **адресуй его явно** в строке `открыто`/`пивот` — «игнорируем, потому что X»
>   должно быть осознанным решением с ценой, а не рефлексом.

- **Когда коммитить 2 цвета.** P1P1–P5 сигналов об открытости ещё нет (паки свежие) → бери **СИЛУ / гибкость / colorless / фикс, НЕ лочь 2 цвета.** С пика 6 читай, что течёт и колесит → коммить в лейн, который **одновременно ОТКРЫТ и МОЩНЫЙ**, к ~пику 6–8. **Исключение — Полоса B (движок): коммить РАНО, P1–P2** (плотность нужна с первых пиков, иначе выйдет shallow = мягкая середина). Строгий CABS учит «decide colors early» — на Arena это верно **только для движка**; для A/C late-commit по сигналам сильнее (реагируешь на то, что реально раздают).
- **Голд P1P1 лочит 2 цвета** — бери только если хеймейкер заметно выше гибкой карты. Иерархия гибкости: **colorless > моно > голд.** Пивотируй В ЦВЕТ БОМБЫ при сильном сигнале (иначе «убивают картами, которых не взял»).
- **Кастуемая бомба-закрывашка** (on-color, ~on-curve) — бери в любой полосе (Bo1 её оправдывает); off-color / off-curve / durdle-«потолок» — НЕ бери (делает body-light).
- **Якорь определи к P1–P3:** в полосе B якорь = движок / бомба-закрывашка; в A/C = сильнейшая board-карта. Каждый пик: **«двигает ли это ПЛАН моей полосы?»**

**Оценка карты (принципы — не последовательность, а чек-лист):**
- **Removal и evasion ценнее, чем кажутся.** Unconditional/instant removal > conditional. Evasion (флаер, trample, unblockable) = способ заканчивать партии в creature-heavy грайнде. Считать **отдельно**: hard removal ≥2–3 + evasion ≥2–3 (−X/−0 и боевые трюки — НЕ removal).
- **Floor vs ceiling (IWD).** GIH = среднее, IWD = потолок. Карта GIH 58 + IWD +9 часто выигрывает больше партий, чем GIH 62 + IWD +1. При наличии якоря-движка приоритизируй high-IWD — они реализуют потолок.
- **Castability beats raw GIH — но НЕ смешивай single-pip и double-pip off-color (баг, пойманный 13.07.2026).** `~splash` (ОДИН off-color пип, напр. {3}{R}) — реально живая опция при 3+ источниках (Rule of Three), а **на пике ≤~15 из ~33 времени добрать фикс ещё достаточно** — высокий IWD/бомба здесь заслуживает статуса реальной альтернативы, а не «нереалистично», особенно если полоса ещё не жёстко законтрена. `✗offcolor` (ДВА+ off-color пипа, напр. {B}{B}) — вот это реально **не сплешится никогда**, дабл-пип сжирает мана-базу. Не приравнивай эти два случая — ошибка была списать одинарный-пип бомбу как «нереалистичный сплеш» той же фразой, что и дабл-пип. Исключение: `✗offcolor` на пике ≤5 при 0 коммите = сигнал ПИВОТИТЬ, а не брать.
- **Quadrant + Vanilla Test.** Карта в 4 состояниях: Opening / Parity / Ahead / Behind — хороша в 3–4 = премиум, в 1–2 = узкий филлер. Существо: бьёт ли vanilla X/X за свою ману? Разницу делают keywords/ability.
- **Кривая — считать существ и спеллы ОТДЕЛЬНО.** Removal/utility не заменяют тела в плане каста по кривой. Цель тел (Karsten): 2-дроп 4–6 · 3-дроп 3–5 · 4-дроп 2–4 · 5-дроп 1–3. Архетип сдвигает: агро — круче вниз; движок/контроль — removal вместо топа кривой.
- **Deck targets (все полосы):** ~17 земель · **15–17 существ** (не ниже 15 — формат creature-heavy) · ≥2–3 hard removal · ≥2–3 evasion · 2–3 трюка. Engine-архетипы (connive/spells) подстраивают пропорции под движок; CABS-полоса A хочет плотнее (16–18 тел).
- **Juza tiebreaker:** при равных якорь/дыра/IWD — бери ДЕШЕВЛЕ (разыгрывается в большем числе партий).

**Сигналы и пивот:**
- **Читай сигналы и колёса.** Сильная карта вернулась поздно (пик 6+ = цвет открыт слева; пик 9+ = полное колесо — круг пода = 8 пиков) → лейн открыт. ⚑ баннеры адресовать в рассуждении **обязательно**, не игнорировать.
- **Justified risk — когда оправдан риск:**
  - **Слабый пул (пики 1–5 все B-tier, нет якоря):** high-IWD build-around > надёжный B-tier (обе медиокрные колоды проигрывают — но рискованная хоть иногда выигрывает крупно).
  - **Сильный сигнал (⚑ПИВОТ, пики 6–10):** пивот стоит 1–2 карты, но открывает поток топ-архетипа. Цена пивота < цена застревания в contested цвете.
  - **Якорь уже есть:** с бомбой-якорем можно брать ⚠trap build-around — якорь покрывает низкий floor.
  - **Никогда:** `✗offcolor` без фикса после пика 6; сплеш 4-го цвета с 0 фикса; трайбал без плотности к пику 6.

**Красные флаги карты:** симметричные эффекты; узкие/conditional карты, мёртвые в руке; >2 копий одной common/uncommon — при 2+ копиях карта «не существует» в паке (оценивай только остальное).

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
- **MSH (Marvel Super Heroes)** — Arena 23.06.2026. 17L live с 25.06. Advise from `msh_knowledge.md` + `msh_insights.md` + `msh_cheat.md` (+ `msh_tier.md` для тир-справки). Core axes: +1/+1 counters (74), Villain/Hero tribal, Power-up, Teamwork, Connive, Plan.
- `mtg_readme.md` — full setup notes + **§6 match lessons** (read these; они encode реальные ошибки из партий).

### Latency practice / model tuning — `draft_sim.py`
Not for real drafts — a **replay test-harness** to practice the live-draft workflow above and/or
A/B advice speed across models/effort without waiting for a real Arena draft. It replays a REAL
past draft's log lines verbatim from `Player.log`/`Player-prev.log` into `sim/sim_player.log`,
pick-by-pick, driven by the **user from a separate console** (not you):
```bash
cd ~/.claude/skills/mtg-draft-helper
python3 draft_sim.py list            # drafts found in the real logs, newest last
python3 draft_sim.py init [id8]      # extract one (default: newest), reset the fake log
python3 draft_sim.py next [N]        # feed the next wake-pick (pick<=11), N times
python3 draft_sim.py status          # where the replay currently is
python3 draft_sim.py reset           # rewind the same draft to pick 1
```
Your side: point the Mode 1 blocking `watch` loop at the fake log instead of the real one —
```bash
MTGA_SETTLE=1 MTGA_LOG=~/.claude/skills/mtg-draft-helper/sim/sim_player.log \
  python3 draft_live.py <set> watch fresh   # first call; drop `fresh` on subsequent calls
```
Same draft replays identically every run, so it's a fair, deterministic comparison across models
and effort levels. Because it's a pre-recorded historical draft, **the pool reflects the real
historical picks, not your advice** — you're practicing/timing the advice, not steering the draft.
`MTGA_OFFLINE=1` is worth setting for pure latency tests so a first-time 17Lands fetch never
pollutes the timing. See the `mtg-latency-test-harness` memory for the validated result (Sonnet 5 +
effort medium is the live-draft default) and iteration history (why blocking single-pass + debounce
won over the older two-pass wake/watch modes).

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

### ⚑ ОБЯЗАТЕЛЬНО после КАЖДОЙ партии — писать лог в `<set>_match_log.md` (причина ПОБЕДЫ И поражения)
После каждого `analyze_game.py` / разбора — **допиши партию в `~/.claude/skills/mtg-draft-helper/<set>_match_log.md`** (`msh_match_log.md` уже есть). Не только проигрыши — **логируй причину и для WIN, и для LOSS** (пользователь, 12.07.2026: «записывай лог партий с причиной победы/поражения»), чтобы лог показывал и выигрышные линии деки, и её failure-modes, а не только провалы. Формат: **строка в сводной таблице ТЕКУЩЕГО прогона + короткая деталь-запись**. Новый драфт = новый прогон (отслеживать W–L прогона; играем до 3 losses или 7 wins).
- **Категория-тег причины (осн. + доп.):** проигрыши — **OUT-ENGINED · STRUCTURAL-AGGRO · MANA · PILOT · VARIANCE · BUILD**; победы — короткая выигрышная линия (напр. **DISRUPT+BOMB · RACE-ПОД · MVP-карта · DISRUPT+BOARD**).
- **Только проверенное по логу** (реслайс жизни/борд/GY, не по памяти; forced plays ≠ misplays; отмечать и то, что сыграно ВЕРНО). См. правило точности разбора.
- Обновлять «Паттерн»-заметку внизу лога, когда across-games проявляется тренд (что стабильно ВЫИГРЫВАЕТ и что проигрывает). Лог MSH ротируется быстро → писать СРАЗУ после матча.

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

### Креативный проход ПЕРЕД финалом (не собирай мягкую середину по умолчанию)
Прежде чем механически резать пул до 40 по ролям — спроси, какая **самая высокопотолочная КОГЕРЕНТНАЯ** версия этого пула:
- Стоит ли **сплеш ради бомбы/хеймейкера** (проверь по Rule of Three + `draft_goldfish.py`, а не на глаз)?
- Есть ли **build-around-линия** (counters-снежок, connive-движок, go-wide+памп, эвейжн-рейс с неблокируемым финишёром), которую пул реально тянет и которая бьёт СИЛЬНЕЕ, чем goodstuff-мидрейндж?
- В какую из трёх полос (A/B/C) пул заострён естественно — и не размываем ли мы это, добирая «безопасные одиночки» в мягкую середину?
- **Где wincon?** Нет закрывашки → durdle-пул проигрывает на Платине (документированные 0:3). Найди финишёр или собери самый агрессивный клок из возможного.

Выбери полосу с самым высоким потолком, который пул **реально поддерживает** (плотностью, не одной картой), затем добери пол (removal / эвейжн / кривую). Творческий, но КОГЕРЕНТНЫЙ билд > безопасный и мягкий. Это тот же вопрос, что в Pn/P1-пересмотре (§ Pick process, шаг 0b) — на финале он последний раз.

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
4. **Файлы знаний (иначе драфтишь вслепую по одному GIH):** заведи `<set>_knowledge.md` (драфт-мета) и `<set>_insights.md` (инсайты из игр) — оба читаются перед КАЖДЫМ драфтом (§ Накопленные знания). Плюс справка: `<set>_cheat.md` (или строки в `draft_cheat.md`) и `<set>_tier.md`. Первый драфт сета — стартуй с пустых knowledge/insights и наполняй после каждого драфта/разбора.
