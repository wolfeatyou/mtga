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

> ### 🔴 СНАЧАЛА ОПРЕДЕЛИ РЕЖИМ — у Premier и Quick РАЗНЫЕ СКРИПТЫ (иначе не увидишь ни одного пака)
> Arena пишет их разными событиями: Premier — `PackCards`/`DraftPack`, Quick (боты) — `BotDraftDraftStatus`.
> **Premier-парсер физически не видит Quick-драфт и наоборот.** Не знаешь режим — спроси одним словом.
>
> | режим | команда (блокирующая, `timeout: 600000`) |
> |---|---|
> | **Premier / Traditional** | `MTGA_SETTLE=1 python3 ~/.claude/skills/mtg-draft-helper/draft_live.py <set> watch [fresh]` |
> | **Quick Draft (боты)** | `MTGA_SETTLE=1 python3 ~/.claude/skills/mtg-draft-helper/quickdraft_watch.py <set> [fresh]` |
>
> **Вывод у них ИДЕНТИЧЕН** — оба идут через общий `draft_live.render_block`: те же тиры, GIH,
> пар-GIH, IWD, ALSA, тир пика, флаги `~splash`/`✗offcolor`/`★synergy`/`⚠trap`, те же баннеры
> (КРИВАЯ/ПЛАН/ПРОФИЛЬ/пивот/колесо/soup-audit) и то же автосохранение пула. Различается ТОЛЬКО
> парсер лога. Паритет закреплён тестом `test_parser_parity.py` (гоняет один пак через оба пути
> и сверяет построчно) — **если правишь рендер, правь в `render_block`, а не в копии**, иначе тест
> покраснеет. До 10.08.2026 копии жили раздельно и молча разъехались: у Quick стояли свои пороги
> тира (S≥60 против A≥60), не было пар-GIH, `⚠trap`, флагов кастуемости и вообще ни одного баннера.

```bash
MTGA_SETTLE=1 python3 ~/.claude/skills/mtg-draft-helper/draft_live.py <set> watch fresh   # Premier, первый вызов
MTGA_SETTLE=1 python3 ~/.claude/skills/mtg-draft-helper/draft_live.py <set> watch         # Premier, дальше
MTGA_SETTLE=1 python3 ~/.claude/skills/mtg-draft-helper/quickdraft_watch.py msh fresh     # Quick, первый вызов
MTGA_SETTLE=1 python3 ~/.claude/skills/mtg-draft-helper/quickdraft_watch.py msh           # Quick, дальше
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
- **🆕 `пик <тир>` — КАК КАРТУ РЕАЛЬНО БЕРУТ в Diamond→Mythic** (untapped.gg pick order, `msh_pick_tiers.json`, 196 карт, снято 10.08.2026). **Это ортогональная GIH ось: не «сколько выигрывает», а «сколько за неё дают».** Расхождение между `GIH` и `пик` — и есть содержательная часть пика.
  - **Измерено (n=196):** ρ(тир пика, GIH) = **+0.79** — GIH остаётся лучшим одиночным предиктором, спорить с ним не надо. НО при примерно РАВНОМ GIH решает **IWD**, и тем сильнее, чем выше полоса: ρ(тир, IWD) внутри GIH 57–59 = **+0.42**, внутри 59–61 = **+0.58**, внутри 61–64 = **+0.66**. То есть ровно там, где живут ранние пики, тайбрейк — IWD, а не второй знак GIH.
  - **Практическое правило (заменяет «при равном GIH — дешевле» на верхних пиках):** две карты в пределах ~1 GIH и обе ≥59 → **бери ту, у которой IWD выше**. Док. пример из той же полосы 59–61: Ka-Zar `пик A` IWD +5.0 против Brave Brawler `пик C` IWD +0.7 — четыре тира разницы при одинаковом GIH.
  - **Типовые расхождения в MSH** (высокий GIH, но берут поздно — мы их систематически переоцениваем): Political Triumph 61.0 `C+` · Web Up 60.8 `C+` · Agent Maria Hill 60.3 `C+` · Take Up the Shield 59.9 `C+` · Red Guardian 59.9 `C` · Brave Brawler 59.2 `C` · Borough Backup 59.1 `C` · Raft Security Officer 58.7 `C-`. И наоборот (берут рано при среднем GIH): Thanos 55.6 `B+` (IWD +7.8) · Tony Stark 60.7 `B+` (+8.0) · Cosmic Cube 60.7 `A-` (+6.2) · Killmonger 60.8 `B+` (+6.9).
  - ⚠️ Тиры перенесены со скриншотов вручную — возможны пропуски отдельных карт; отсутствие тира у карты ничего не значит.
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
  - **⚖️ `⚑ ТАЙБРЕЙК` — срабатывает, когда GIH-сортировка ставит наверх НЕ ту карту (внесено 11.08.2026).** Молчит, пока верх по GIH и есть лучший выбор. Говорит, когда в пределах **1.5 GIH** есть карта заметно лучше по **IWD** (≥2.0) или по **пик-тиру** (≥2 ступени) — и называет её поимённо. Некастуемые в тайбрейке не участвуют.
    - **Повод — задокументированный промах (Quick MSH, 10.08.2026, P1P2):** в паке лежали `Take Up the Shield` GIH 59.9 / IWD +3.0 / пик C+ и `Super-Skrull` GIH **59.9** / IWD **+8.6** / пик **B**, 4/5 flying. **GIH совпал до десятой**, советчик взял верхнюю строку списка. Игрок взял Super-Skrull вопреки совету и был прав: колода уехала в воздух (флай 8), а Take Up the Shield стоит поимённо в списке «высокий GIH, берут поздно» выше по этому же файлу.
    - **Почему баннером, а не правилом:** правило «floor vs ceiling, IWD — потолок» стояло в § Оценка карты давно и не сработало ни разу. **Сортировка по GIH сильнее любой прозы** — ровно как было с квотой кривой. Третий раз наступать не будем.
  - **🛩️ `⚑ ПЛАН` — печатается КАЖДЫЙ пик (внесено 10.08.2026, n=23).** Классифицирует пул в кластер по флаерам и рича: 🟦 **ВОЗДУХ** (проекция флаеров ≥6 — так у 9 колод) · 🟫 **ЗЕМЛЯ** (≤3 — у 12 колод) · ⬜ **не определился** (4–5 — там всего 2 из 23). До пика 10 вердикт не выносится. **Reach — почти идеальный разделитель кластеров:** из 9 воздушных победителей reach≥2 не держит НИ ОДНА; из 12 наземных 8 держат reach≥3.
    - **⚠ КОНФЛИКТ** — reach ≥2 при воздушном плане: карты работают против собственной колоды. Раньше это не ловилось ничем.
    - **⚠ REACH МАЛО** — наземный план без рича проигрывает воздушному кластеру автоматически; рич здесь не филлер, а приоритетная роль.
    - Счётчики +1/+1 в детектор НЕ входят: они универсальны (6–9 в обоих кластерах) — это язык формата, а не признак архетипа.
  - **📊 `⚑ ПРОФИЛЬ` — только на границе бустера (P2P1/P3P1).** Существа / cmc≤2 / cmc≥5 / фикс в формате «моё/ожидаемо-к-этому-пику» против диапазонов 23 победителей. **Сравнение ТЕМПОВОЕ**, а не с финальными числами — иначе на P2P1 всегда «всего мало». `!` = ниже темпа минимума, `↑` = выше максимума.
  - **🔴 `⚑ КРИВАЯ` — печатается КАЖДЫЙ пик — ИНФОРМАЦИЯ, НЕ ПРИКАЗ (статус понижен 10.08.2026, см. ниже).** Показывает `существ cmc≤2 — N · чекпойнт K · финал ≥5`, считая только тела, **кастуемые в текущих цветах**. При `— НЕДОБОР` баннер сам называет дешёвые тела в цвете **в этом паке** — и это и есть пик, если в паке нет бомбы (GIH ≥63) или безусловного removal. **Что это НЕ значит (проверено и опровергнуто 10.08.2026):** число не является порогом качества колоды. На 14 листах diamond/mythic медиана «существо к T2» = **54.3%**, десять из четырнадцати ниже 60%, и метрика чувствительна к таплендам (−5.1 пункта на 3 тапленда) и к числу земель не меньше, чем к числу дешёвых тел. Читать как **дескриптор полосы**: агро-полоса C без 5–6 дешёвых тел не работает, а бомбовая/соуп-колода спокойно живёт на 40–50%. Печатает `draft_live.py` (§ `curve_banner`). Исходная корреляция (7 наших прогонов) не воспроизвелась на внешней выборке — см. § РЕФЕРЕНС-ВЫБОРКА в `msh_knowledge.md`.
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
- **🚫 «Выше по GIH» / «топ по GIH среди доступных» — ЗАПРЕЩЁННОЕ обоснование в `ЛОГИКА` (внесено 11.08.2026).** GIH — стартовая сортировка, а не аргумент; в строке карты рядом с ним стоят **IWD** и **`пик <тир>`**, и пик решается их расхождением. Два задокументированных промаха подряд в одном драфте: P1P2 — взята карта с равным GIH, но втрое меньшим IWD и худшим пик-тиром; P3P1 — `ЛОГИКА` дословно «топ по GIH среди истинно доступных карт» при `пик C-` в той же строке. **Обосновывай ролью, планом полосы, квадрантами или дырой.** Берёшь карту с низким пик-тиром — скажи, почему ЗДЕСЬ она лучше, чем её берут в среднем. Если сработал `⚑ ТАЙБРЕЙК`, адресуй его явно, как ⚑-баннеры.
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
     - **➕ КВАДРАНТНЫЙ ПРОФИЛЬ ПУЛА — 4 числа по 5** (Develop / Parity / Ahead / Behind, § Quadrant Theory). Это главная точка вставки квадрантов: на границе бустера есть минута, в пике её нет. Вердикт одной строкой:
       · слабый квадрант **совпал со сданным у моей полосы** (C→Behind, B→время в Ahead) → норма, идём дальше;
       · слабый квадрант **не тот** → это дыра, следующий бустер добираем в неё;
       · **все четыре ≈3/5 → это и есть мягкая середина** — диагноз ставится ЧИСЛАМИ, а не ощущением постфактум. Раньше у мягкой середины детектора не было вообще. Реакция: заострять в полосу, а не добирать ещё один «ровный» голдстафф.
     - **➕ Прогони РУБРИКАТОР «8+» (§ Mode 3) прямо здесь, а не на финале.** Цель — **6/7 порогов без проваленных стоп-кранов.** Пороги 1 (двуролевых ≥15), **3 (≥5 существ cmc≤2)** и 5 (ноль карт cmc≥6) **на сборке уже не чинятся** — только пиками. **➕ КВОТА ДЕШЁВЫХ ТЕЛ — сверь с баннером `⚑ КРИВАЯ` (он печатается каждый пик, здесь только фиксируешь итог бустера).** Чекпойнты: **конец P1 ≥2 · конец P2 ≥4 · финал ≥5** существ cmc≤2 в своих цветах. **Статус — ориентир полосы, не квота (понижен 10.08.2026, § РЕФЕРЕНС-ВЫБОРКА).** Для полосы C (агро) 5–6 дешёвых тел обязательны, без них полоса не работает. Для полос A/B — это просто число: на 14 листах diamond/mythic медиана дешёвых тел **4.5**, а у обеих наших лучших колод 6–7, т.е. мы по этой оси уже выше нормы победителей и дожимать её нечего. **❌ Именной урок про Crowd of True Believers СНЯТ (10.08.2026).** Он был выведен из одной партии («пасован трижды, добирай его»). Проверка по 14 листам 7-1/7-2: из трёх драфтеров, кому эта карта была НА ЦВЕТЕ, её оставили в сайде **все трое** (мейн 0/3 при GIH 57.1). Одна наша партия против трёх независимых срезов победителей — урок снимается. Назови, какие пороги провалены СЕЙЧАС, реши **какой ОДИН готов отдать осознанно**, и следующий бустер добирай под остальные: не хватает двуролевых → приоритет токен-мейкерам/модальным/циклерам/телам-с-removal; нет закрывашки (порог 6, стоп-кран) → ищи финишёр, а не N-й ответ.
   - **(b) Креативный пересмотр — ищи ЛУЧШУЮ колоду в пуле, а не только латай дыры текущего плана.** Спроси себя:
     · Открылась ли более **ОТКРЫТАЯ и мощная полоса**, в которую стоит доломиться (цвет течёт/колесит сильнее нашего)? Цена пивота на границе пака ниже — впереди ещё целый бустер.
     · Есть ли **бомба/хеймейкер**, под которую пора НАЧАТЬ тянуть фикс (сплеш-опцион по Rule of Three)? Ранняя бомба = обязательство строить под неё, а не «фри-карта».
     · Тянет ли пул **теперь** build-around/движок, которого не было на P1 (набралась плотность энейблеров — counters-снежок, connive-движок, go-wide+памп, эвейжн-рейс с неблокируемым финишёром)? Плотность могла перевалить порог.
     · Не собираем ли мы **мягкую середину**? Если да — можно ли ЗАОСТРИТЬ в одну полосу (глубже агро / глубже движок / чище контроль-с-потолком)? И **где wincon** — если его нет, ищи закрывашку СЕЙЧАС.
   - **Выбери самую ВЫСОКОПОТОЛОЧНУЮ из КОГЕРЕНТНЫХ версий**, потом возвращайся к латанию дыр. Изменения озвучь в `собираем`/`не хватает`/`пивот` этого пика (напр. «цвет X пересох — не пивотим» или «набралось 6 counters-энейблеров → тянемся в snowball, а не goodstuff»). Не сбрасывай состояние молча.
> ### 🧪 АКТИВНЫЙ ЭКСПЕРИМЕНТ — «ОДИН ПРОГОН В ПОЛОСУ B» (заведён 08.08.2026, статус: ИДЁТ, площадка — Quick Draft)
> **Зачем:** попытка собрать движок у нас ровно ОДНА (07.07, shallow, 0:3), и из неё сделан вывод «движки — ловушка», который с тех пор фильтрует каждый драфт. Один провал — не выборка. Эксперимент нужен, чтобы проверить полосу B **при честном исполнении**, а не отменять её по памяти о единственной неудаче.
> - **Триггер входа:** к **P1P5** в пуле набралось **≥2 детали одной движковой полосы** (connive-фидеры · артефакт-каунт · Villain-каунт · counters-снежок) **ИЛИ** взят якорь полосы B на P1P1–P1P3 (Leader / Tony Stark / Madame Masque / Baron Strucker / Cosmic Cube — см. § ЯКОРЬ ПОЛОСЫ).
> - **Что делаем при срабатывании:** коммитим и **ведём до конца**, даже когда на пике 8 предлагают флаер 58 против детали 52. Цель по плотности — **≥5 карт движка** (ниже = shallow = заведомый повтор 07.07, тогда честнее откатиться в A).
> - **Что НЕ делаем:** не переобуваемся на P3P1 обратно в good-stuff «потому что рубрикатор показывает 7». **Пороги 3 и 6 для полосы B читаются по своей колонке** (§ Пороги 3 и 6 по полосе) — если по ним 6/7, это восьмёрка, а не семёрка.
> - **Триггер отмены (честный):** якорь не пришёл к P1P3 И к P1P5 нет двух деталей → полоса B не открывается, драфтим как обычно. Отмена — не провал эксперимента, а его корректное отрицательное срабатывание; записать это тоже.
> - **Что фиксируем в `msh_match_log.md` по итогу прогона:** плотность движка (сколько карт) · число ⚡-активаций за партию из `analyze_game.py` · рубрикатор по колонке B · W–L. Сравнивать надо с нашими эвейжн-прогонами (6W–3L, 6W–3L, 4W–3L, 3W–3L), а не с абсолютным нулём.
> - **Снять этот блок**, когда прогон закрыт и вывод записан в `msh_knowledge.md`.

1. **Scan** — read full pack by GIH. Flag the top in-color card, top off-color card, and any high-IWD outlier.
2. **Think** — ответь на 4 вопроса (План полосы · Дыра · Дельта · **Квадранты**). Тайминг по правилу [[mtg-conditional-think-time]]: условные +5с ТОЛЬКО на спорных пиках и на P1 каждого пака (эти секунды идут на синергию/полосу — кормит ли карта ось, есть ли фундамент); на очевидных пиках (один явный бомб/removal) и поздних пиках пака (P10–P13) — не тормозить.
   - **План полосы:** двигает ли карта план ТВОЕЙ полосы? (A/C: board-affecting тело/removal в кривую; B: движок-деталь/пейофф, кормящий якорь.) Карта, усиливающая план полосы, бьёт более-высокий-GIH без роли. Полосы/якоря ещё нет — что ЗДЕСЬ может ими стать?
   - **Дыра:** what's the one thing the deck is most missing right now? (evasion / hard removal / curve slot). The card that fills it wins even at lower GIH.
   - **Дельта:** do I already have 2+ copies of this card's role? If yes — skip it entirely, look at everything else.
   - **➕ КВАДРАНТЫ — 4-й вопрос, обязательный на КАЖДОМ пике (§ Quadrant Theory). Считать не весь пак, а 2–3 ФИНАЛИСТОВ** — тех, что реально борются за пик после первых трёх вопросов. По всему паку это и не нужно (там 15 карт, а решают две), и слишком долго; по двум финалистам это несколько секунд, которые на Sonnet у нас есть.
     - **(а) Пометь каждому финалисту буквы живых квадрантов** — D/P/A/B. «Живой» = карта делает в этом состоянии что-то РЕАЛЬНОЕ, а не «её можно сыграть». 2/2 тело за 2 = **D**, оно не спасает Behind и не добивает Ahead. Безусловное removal = **D P A B**. Боевой трюк = **P A**. Добор/движок = **P B**. Флаер 3/2 = **D P A**. Лайфгейн-стена = **B**. Памп на всю команду = **A**.
     - **(б) Правило сравнения (это ОТВЕТ, а не подсказка): карта, живая в 2+ квадрантах, бьёт карту с более высоким GIH, живую в одном.** GIH — среднее по чужим колодам; число квадрантов — насколько карта не бывает мёртвой в МОЕЙ. Это тот же принцип, что «двуролевых ≥15» (порог 1), только применённый в моменте пика, а не постфактум на сборке.
     - **(в) Штраф за сданный квадрант.** Финалист, чья ценность лежит ТОЛЬКО в квадранте, который моя полоса сдала (агро+стабилизатор/лайфгейн, движок+памп-на-Ahead) — **опускается на ступень**, даже при высоком GIH. Это не «закрытие дыры», это размывание фокуса.
     - **(г) Штраф за тонкий квадрант пула.** Держи в голове, какой квадрант у пула сейчас самый тонкий (полный профиль считается на границе бустера, между границами — грубая прикидка). **При прочих равных берётся финалист, оживляющий самый тонкий НЕ-сданный квадрант.** Типовые тонкие места по нашей истории: Develop (нет 2-дропов) и Ahead (нечем добить).
     - **(д) Два вопроса-детектора против нашего bias** — задавать, когда финалист попадает в класс: трюк/условное removal/−X/−0/памп → **«что она делает, когда я ПОЗАДИ?»**; движок/добор/durdle → **«что она делает, когда я ВПЕРЕДИ?»**. Ответ «ничего» = минус буква, роль не засчитывать. LTL ставит первый вопрос отдельно именно потому, что человек систематически оценивает карту по best-case.
     - **Тайминг:** пункты (а)+(б) — всегда, это буквально пара букв на карту. (в)+(г)+(д) — на спорных пиках, на P1 каждого пака и когда финалисты близки по GIH; на очевидном пике (один бомб/премиум-removal) и на P10–P13 не тормозить.
3. **Pick** — по иерархии ТВОЕЙ полосы (§ КОММИТ В ПОЛОСУ): **якорь/бомба-закрывашка > карта, двигающая план полосы (тело для A/C; движок-деталь для B) > дыра-роль > БОЛЬШЕ ЖИВЫХ КВАДРАНТОВ > при равных дешевле**. GIH — старт, не ответ. «Синергия» высоко ТОЛЬКО в полосе B.
   - **⚠️ `⚑ КРИВАЯ` — это ИНФОРМАЦИЯ, НЕ ПРИКАЗ (статус понижен 10.08.2026 после проверки на 23 чужих листах 7-1/7-2).** Сутки этот пункт стоял здесь как жёсткий override («квота бьёт всю иерархию») на основании корреляции по 7 нашим прогонам. **Выборка из 14 колод diamond/mythic его опровергла: большинство имеет «существо к T2» НИЖЕ 60%** (медиана 54.3%, минимум 36.4%), а обе наши лучшие колоды — 77.2% и 70.4% — стоят в топ-3 распределения. То есть по этой оси мы не отстаём, а лидируем, и override отбраковывал бы большинство реально выигрывающих колод. Счётчик оставлен: знать число полезно, особенно для агро-полосы C. **Но пик им больше не решается** — работает обычная иерархия ниже. Детали и таблица — § РЕФЕРЕНС-ВЫБОРКА в `msh_knowledge.md`.
   - **Квадранты стоят выше Juza-тайбрейка («при равных дешевле») и ниже плана полосы/дыры** — то есть решают ровно те пики, где раньше решал GIH за неимением аргумента. Именно там мы и теряли: «обе карты нормальные, беру которая выше в списке».
   - **В `ЛОГИКА` формулировать квадрантами, когда именно они решили пик** — «живёт в D+P+A, альтернатива только в A» информативнее, чем «выше GIH». Отдельной строки в блоке вывода НЕ заводить.
   - **В `альтернатива` причина проигрыша тоже может быть квадрантной** — «только Ahead, а мы сейчас проваливаем Develop».

**Hard rule: max 2 copies of any common/uncommon in the 40.** At 2+ copies, that card doesn't exist in this pack — evaluate only the rest.

**Bad pack rule:** if nothing feeds the anchor, fills a gap, or has high IWD — take the card most likely to wheel or signal an open color for the next pack. Don't default to "highest GIH filler".

## 🏛️ КАЛИБРОВКА — ЗАКОН НАД ВСЕМИ ПРАВИЛАМИ НИЖЕ (внесено 10.08.2026)

> **Все пороги, квоты и стоп-краны в этом файле выведены из НАШИХ ПОРАЖЕНИЙ. Это модель, обученная на собственных провалах, и она никогда не проходила отрицательный контроль.** Первая же проверка на внешней выборке показала цену: **наш рубрикатор отбраковал бы 10 из 14 реальных колод 7-1/7-2 (на выборке n=23 — 16 из 23)** — по стоп-крану «существо к T2 ≥60%» (у них медиана 54.3%) и по порогу «removal ≥4» (у них медиана 1, у пяти колод ноль). Мы измеряли «похоже ли это на нашу колоду», а не «выигрывает ли это.

**Отсюда три закона, приоритетных над любым конкретным порогом ниже:**

**1. Источник калибровки — популяция победителей, а не наши сливы.** `ref_decks/` (23 листа 7-1/7-2, растёт). Фиксированные пороги заменяются вопросом «где моя колода в распределении». Дефект — только **выход ниже ВСЕЙ популяции**, не отклонение от выдуманного числа.
```bash
python3 ~/.claude/skills/mtg-draft-helper/build_audit.py <мой_лист.txt>   # лист ОБЯЗАН содержать Sideboard
python3 ~/.claude/skills/mtg-draft-helper/deck_profile.py <лист> [--brief]
python3 ~/.claude/skills/mtg-draft-helper/cut_analysis.py                  # что победители режут на цвете
```
**Пул сохраняется САМ (внесено 10.08.2026) — руками ничего делать не надо.** `draft_live.py` пишет полный пул в `pools/<set>_<draft8>.txt` (MTGA-формат, всё в `Sideboard`) **на КАЖДОМ пике** и печатает строку `💾 пул сохранён: …`. Автоматически — потому что пул физически живёт только в `Player.log`, а он **ротируется быстро** (§ Mode 2): после ротации остаток пула восстановить неоткуда, и тест на жадность провести уже нельзя. Перезапись каждый пик означает, что обрыв в любой момент ничего не теряет.
На сборке: `python3 build_audit.py <мой_лист.txt> --pool <файл_пула>` — сайдборд вычисляется как **пул минус мейн**, отдельный лист с `Sideboard` больше не нужен. (Проверено: лист без сайда + `--pool` даёт тот же результат, что лист со встроенным сайдом.)

**2. Тест процесса: наш мейн не должен совпадать с «жадным» топ-23 по GIH.** Ни одна из 23 победивших колод не равна жадному списку — все отдают **+0.49 GIH на карту, 23 из 23 в одну сторону** (минимум +0.03) (случайно — 1 шанс из 16 000). Совпадение с жадным = «план не выбран, пул отсортирован». Печатает `build_audit.py`. **Этот тест про НАШ процесс, поэтому он не страдает от survivorship-bias референс-выборки** — в отличие от любых выводов вида «4 цвета выигрывают», которые из выборки только победителей делать НЕЛЬЗЯ.

**3. Почему отклонение от GIH обязано быть — и куда именно.** GIH это **среднее по всем колодам**, где карта встретилась, то есть маргинальная величина, а не условная на моей сборке. Поэтому он систематически:
   - **завышает** карты, одинаково приличные везде (дженерик-тела, трюки, дженерик-добор): по срезам победителей — Agent Maria Hill 60.3, Take Up the Shield 59.9, Brave Brawler 59.2, H.E.R.B.I.E. 58.5, Futurist Forge 58.4, Crowd of True Believers 57.1 (мейн 0/3), Depower 56.5 (0/3), Attuma 55.4 (0/3);
   - **занижает** карты, ценность которых условна на плане: пейоффы движка/трайбала (Machinesmith 51.3, Training Regimen 52.4, Knight of Wundagore 52.9, Madame Hydra 49.0, Armor Wars 48.7, Invisible Woman **46.4**) и **фикс** (Restorative Technique 52.1 — в двухцветной колоде он мёртв, оттого и среднее низкое).
   **Драфт по GIH строит колоду, которая нигде не плоха — то есть буквально мягкую середину**, которую наш же матч-лог называет главным диагнозом (10 из 17 поражений OUT-ENGINED). Величина поправки мала (≈0.5 на карту), направление — всегда в сторону пейоффа собственного плана.

**4. Правила ОБЯЗАНЫ устаревать.** Каждое новое правило здесь пишется с **n и датой**. Правило, выведенное из 1–7 наших партий, имеет статус гипотезы и проверяется на `ref_decks/` при первой возможности; **противоречит популяции — понижается или удаляется, а не остаётся «на всякий случай»**. За 10.08 так сняты: override квоты кривой, стоп-кран порога 3, именной урок про Crowd of True Believers. Это норма работы файла, а не авария. Файл рос 2 месяца, не удалив ни одного правила — именно так и получается переобучение.

---

## 🧭 ГЛАВНЫЙ ПРИНЦИП = КОММИТ В ПОЛОСУ (обновлено 12.07.2026 — заменяет «CABS-универсален»)
**Верхний закон драфта: выбери ОДНУ полосу и коммить в неё. Мягкая середина проигрывает ВСЕМ закоммиченным декам.** (Лог: 2 из 3 — проигрыш глубокому движку; наша дека = 1 Forge + полу-движок + 13–14 существ, закоммичена ни во что.) [[mtg-commit-to-a-lane]] [[mtg-maintain-match-log]]

**Три полосы — у КАЖДОЙ свои правила (камень-ножницы-бумага):**

| Полоса | Правила сборки | Квадранты: держит / **сдаёт** | Бьёт | Слаба к |
|---|---|---|---|---|
| **A. CABS-мидрейндж** | board-only: существа+кривая+removal, БЕЗ добора/движков | **все четыре, не сдаёт ничего** | агро | глубокий движок |
| **B. Глубокий движок/контроль** | добор+движок+connive+ЯКОРЬ; **избыточный добор ПРАВИЛЬНЫЙ (2 Forge — да)** | Behind + Parity / **сдаёт ВРЕМЯ в Ahead** | мидрейндж/goodstuff (грайнд) | быстрое агро |
| **C. Агро** | низкая кривая (2-дропы!)+эвейжн+reach, иди ПОД | Develop + Ahead / **сдаёт Behind** | движок (не даёт собраться) | нужен пул с 2-дропами |

**🧩 Квадранты полосы — это ПИК-ПРАВИЛО, а не украшение (внесено 22.07.2026, § Quadrant Theory ниже).** Сданный квадрант — это обязательство НЕ добирать под него карты: они не «закрывают дыру», они размывают фокус.
- **C (агро) сдал Behind → стабилизаторы / лайфгейн / «отыграться с пустой доски» НЕ БРАТЬ.** *«When you truly commit to building an aggressive deck, you're effectively conceding the 'behind' quadrant»* (LTL Part 2).
- **B (движок) сдал ВРЕМЯ в Ahead, но НЕ закрывашку** (наш порог 6 — стоп-кран, выведен из проигрыша 16.07 «ответы были, убить нечем»; здесь мы сознательно расходимся с LTL, у которого финишёр контроля вторичен). Практика: движку нужны **1–2 закрывашки, а не плотность**; Ahead-пампы не брать, Behind-карты (стабилизатор, стена-с-value) брать ВЫШЕ их GIH.
- **A (CABS) не сдаёт ничего — поэтому она самая ДОРОГАЯ полоса, а не самая безопасная.** Мидрейндж обязан быть компетентен во всех четырёх квадрантах (*«midrange decks have to be competent in all of them»*). Отсюда механизм нашей мягкой середины: мы по умолчанию садимся в A и собираем её по остаточному принципу.

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

> ### 🔴 ЯКОРЬ ПОЛОСЫ ≠ «ПРОСТО СИЛЬНАЯ КАРТА» — развилка, которую мы 8 драфтов подряд не замечали (внесено 08.08.2026)
> **Механизм лика:** правило «на P1P1–P5 бери СИЛУ» на практике = «бери верхний GIH», а верхний GIH в MSH — это белый темпо/эвейжн good-stuff (58–62). К пику 6 в пуле уже 5 таких карт, и **вход в полосу B закрыт навсегда**, потому что она требовала коммита на P1–P2. Два правила в этом файле несовместимы, и по умолчанию всегда выигрывало первое. Результат — **8–9 из 11 задокументированных прогонов темпо/эвейжн, из них 6 буквально «WU воздух», и ровно ОДНА попытка движка (07.07, собрана shallow, 0:3)**.
> - **Разводить два класса ранних пиков явно:**
>   - **«Сильная карта»** — высокий GIH, работает в любой оболочке (Web Up, Murdock's, флаер 58+). Не создаёт обязательств.
>   - **«ЯКОРЬ ПОЛОСЫ»** — карта, вокруг которой архетип существует. Её GIH раздут именно тем, что она стоит в закоммиченных колодах; взять её = **обязательство с P1P4 брать детали по 51–55 GIH над флаером на 58**.
> - **Якоря полосы B в MSH (проверено по 17L):** **Leader, Super-Genius** {2}{U}{U} — GIH 68.7 / **IWD +16.0** / ALSA 1.7 · **Tony Stark // The Invincible Iron Man** — 60.7 / **IWD +8.0** / ALSA 2.1 · **Madame Masque** {4}{B} — 59.1 / **IWD +6.4** / ALSA 3.6 (в паре 61.1) · Baron Strucker · Cosmic Cube. **Маркер якоря — не GIH, а IWD ≥+6 при ALSA ≤3.6:** карта, которая настолько меняет игру при доборе, что её забирают почти сразу.
> - **Правило пика:** якорь полосы B на **P1P1–P1P3** → это НЕ «фри-бомба», это **выбор полосы**. Дальше весь драфт: детали движка > дженерик-эвейжн, даже при разнице −5 GIH. Если брать якорь и потом драфтить good-stuff — получится ровно 07.07 (shallow, 0:3), худший из возможных исходов.
> - **Обратное тоже верно:** якорь НЕ пришёл к P1P3 → полосу B не открывать вообще. Она не собирается «по остаточному принципу», в отличие от A.
> - **Почему детали движка выглядят непикабельными (главное):** 17L усредняет их по всем колодам, включая те, где движка нет. Карты, которые нас реально били: Machinesmith Automaton **51.3**, Training Regimen **52.4**, Crossbones **52.9**, HYDRA Assault Robot **52.9**, Knight of Wundagore **52.9 (наш инструмент печатает ⚠trap!)**, Atlantean Cavalry **53.0**, Super Intelligence **53.1**, Kingpin's Enforcers 53.9. Медиана ≈53. **Средний GIH НАШИХ колод 57.7–58.6 — мы стабильно собираем более высокорейтинговые колоды и проигрываем им.** Флаг `⚠trap` (IWD<0) означает «плохо БЕЗ полосы», а читается нами как «не бери никогда» — для полосы B его надо инвертировать. [[mtg-count-enabler-density]]
- **Голд P1P1 лочит 2 цвета** — бери только если хеймейкер заметно выше гибкой карты. Иерархия гибкости: **colorless > моно > голд.**
  - **⚠️ Тройной пип одного цвета ({B}{B}{B}) — это МОНО, а не голд (уточнено 11.08.2026).** Он коммитит в ОДИН цвет, а не в пару, и на ранних пиках это нормальная цена за силу. Не приравнивай его к голду: голд закрывает дверь в оба цвета сразу, тяжёлое моно — только в один, второй остаётся полностью открытым.
  - **И проверяй альтернативу на ТОТ ЖЕ вопрос.** «Не лочусь рано» — аргумент только если в паке есть **colorless / фикс / карта с одним пипом**. Если весь верх пака цветной, выбор идёт между моно-W и моно-B, и гибкость не выигрывается ничем — тогда решают сила, IWD и пик-тир. Док. промах (Quick MSH, 10.08.2026, P1P2): `Super-Skrull` {1}{B}{B}{B} 4/5 flying (GIH 59.9 / IWD **+8.6** / пик **B**) пасован «чтобы не лочиться в чёрный», а взятая альтернатива `Take Up the Shield` {1}{W} (59.9 / +3.0 / C+) лочила ровно так же — в белый. Пул при этом уехал в B:14/U:8, то есть чёрный и был лейном. Пивотируй В ЦВЕТ БОМБЫ при сильном сигнале (иначе «убивают картами, которых не взял»).
- **Кастуемая бомба-закрывашка** (on-color, ~on-curve) — бери в любой полосе (Bo1 её оправдывает); off-color / off-curve / durdle-«потолок» — НЕ бери (делает body-light).
- **Якорь определи к P1–P3:** в полосе B якорь = движок / бомба-закрывашка; в A/C = сильнейшая board-карта. Каждый пик: **«двигает ли это ПЛАН моей полосы?»**

**Оценка карты (принципы — не последовательность, а чек-лист):**
- **Removal и evasion ценнее, чем кажутся.** Unconditional/instant removal > conditional. Evasion (флаер, trample, unblockable) = способ заканчивать партии в creature-heavy грайнде. Считать **отдельно**: hard removal ≥2–3 + evasion ≥2–3 (−X/−0 и боевые трюки — НЕ removal).
- **Floor vs ceiling (IWD).** GIH = среднее, IWD = потолок. Карта GIH 58 + IWD +9 часто выигрывает больше партий, чем GIH 62 + IWD +1. При наличии якоря-движка приоритизируй high-IWD — они реализуют потолок.
- **Castability beats raw GIH — но НЕ смешивай single-pip и double-pip off-color (баг, пойманный 13.07.2026).** `~splash` (ОДИН off-color пип, напр. {3}{R}) — реально живая опция при 3+ источниках (Rule of Three), а **на пике ≤~15 из ~33 времени добрать фикс ещё достаточно** — высокий IWD/бомба здесь заслуживает статуса реальной альтернативы, а не «нереалистично», особенно если полоса ещё не жёстко законтрена. `✗offcolor` (ДВА+ off-color пипа, напр. {B}{B}) — вот это реально **не сплешится никогда**, дабл-пип сжирает мана-базу. Не приравнивай эти два случая — ошибка была списать одинарный-пип бомбу как «нереалистичный сплеш» той же фразой, что и дабл-пип. Исключение: `✗offcolor` на пике ≤5 при 0 коммите = сигнал ПИВОТИТЬ, а не брать.
- **Vanilla Test.** Существо: бьёт ли vanilla X/X за свою ману? Разницу делают keywords/ability.
- **Quadrant Theory — см. отдельный раздел ниже.** Карта хороша в 3–4 квадрантах = премиум, в 1–2 = узкий филлер; **бомба = работает во всех четырёх, ОСОБЕННО Behind** (а не «карта с максимальным GIH» — это уточняет наш ранний пик «бери силу» на P1P1–P5).

### 🎲 QUADRANT THEORY — общий словарь под наши пороги (внесено 22.07.2026)
Источники: Brian Wong / Marshall Sutcliffe (оригинал) · [LTL Part 1 — card evaluation](https://letstalklimited.wordpress.com/2020/09/11/quadrant-theory-part-1-card-evaluation/) · [LTL Part 2 — deckbuilding](https://letstalklimited.wordpress.com/2020/09/25/quadrant-theory-part-2-deckbuilding-and-planning/) · [Crushing Limited — Extended](https://crushinglimitedmtg.wordpress.com/2017/11/09/quadrant-theory-extended/). LTL — тот же автор, что «Be Boring», на котором стоит полоса A.

**Четыре состояния партии:** **Develop** (первые ходы, роли только устанавливаются) · **Parity** (атаковать невыгодно никому, стойка) · **Ahead** (выигрываем, если ничего не изменится) · **Behind** (потеряли доску, чампблочим).

**🔑 Это НЕ второй фреймворк — это объяснение того, что у нас уже есть.** Наши четыре главных порога рубрикатора = ровно четыре квадранта, выведенные эмпирически из наших сливов:

| Квадрант | Наш инструмент |
|---|---|
| **Develop** | порог 3 «существо к T2 ≥60%» — **СТОП-КРАН** |
| **Parity** | порог 7 «план ≥4 картами» + **ломатели стойки (эвейжн/неблокируемое)** |
| **Ahead** | порог 6 «закрывашка» — **СТОП-КРАН** |
| **Behind** | порог 4 «hard removal ≥4, ответ на тело ≥5» |

**Где это работает в пике:** квадранты — **4-й вопрос Think-шага и тайбрейк выше «при равных дешевле»** (§ Pick process, шаг 2). Считаются **не все 15 карт пака, а 2–3 финалиста**: помечаем каждому живые квадранты буквами (D/P/A/B), и **карта, живая в 2+, бьёт карту с более высоким GIH, живую в одном**. Это применение порога 1 («двуролевых ≥15») в моменте пика, а не постфактум на сборке.

Два вопроса-детектора против нашего задокументированного bias:
- **Трюк / условное removal / −X/−0 / памп → «что она делает, когда я ПОЗАДИ?»** Ничего → это не removal и не ответ, это Ahead-карта. (LTL ставит этот вопрос отдельно именно против уклона в best-case. Лечит наш лик «трюки посчитаны за removal», стоивший партии против Hulk 6/5.)
- **Движок / добор / durdle → «что она делает, когда я ВПЕРЕДИ?»** Не приближает конец партии → это не закрывашка. (Лечит «загнал, но не добил».)

**Шпаргалка по типовым картам:** ванильное тело в кривую = **D** · безусловное removal = **D P A B** · условное removal (сила ≤N) = **D P** · боевой трюк = **P A** · добор/движок = **P B** · эвейжн-тело = **D P A** · лайфгейн/стабилизатор = **B** · командный памп = **A** · бомба = **D P A B**.

**Ещё два тезиса из LTL, применимых прямо в пике:**
- **Racing — не отдельный квадрант, а симптом непонимания роли** (кто здесь беатдаун). Совпадает с нашим правилом «кто беатдаун — каждую игру».
- **Три класса карт:** *Specialists* (условные — ценны ТОЛЬКО в правильной оболочке) · *Bombs* (работают везде) · **«Ricks»** — узкие карты, запомнившиеся одной яркой игрой и создающие ложное впечатление. Ярлык «Rick» использовать в `<set>_knowledge.md` для наших переоценённых карт: он называет МЕХАНИЗМ ошибки, а не только факт.
- **Кривая — считать существ и спеллы ОТДЕЛЬНО.** Removal/utility не заменяют тела в плане каста по кривой. Цель тел (Karsten): 2-дроп 4–6 · 3-дроп 3–5 · 4-дроп 2–4 · 5-дроп 1–3. Архетип сдвигает: агро — круче вниз; движок/контроль — removal вместо топа кривой.
- **Deck targets (все полосы):** ~17 земель · **15–17 существ** (не ниже 15 — формат creature-heavy) · ≥2–3 hard removal · ≥2–3 evasion · 2–3 трюка · **≥1 источник ПОВТОРЯЕМОГО преимущества** (см. ниже). Engine-архетипы (connive/spells) подстраивают пропорции под движок; CABS-полоса A хочет плотнее (16–18 тел).
- **🆕 РОЛЬ «ДВИЖОК / ИНЭВИТАБИЛИТИ» — считать наравне с removal и эвейжном (внесено 08.08.2026).** Вопрос на аудите: **«чем я генерирую преимущество КАЖДЫЙ ход, без новых карт из руки?»** До этой правки в Deck targets и в 7 порогах была инструментирована только *разовая* интеракция и *фиксированный* клок — поэтому мы систематически собирали колоды, которые бьют на 2–3 в ход, и проигрывали тем, кто каждый ход получает карту/тело/счётчик.
  - **Что считается:** повторяемая активация (⚡ по матч-логу — Machinesmith ×5, Yellowjacket ×8, HYDRA Assault Robot ×7) · фабрика токенов (Madame Masque, Okoye, Stark Executive) · добор-мотор (Super Intelligence, Political Triumph, Futurist Forge, connive-якорь) · мана-синк на теле (power-up) · снежок от счётчиков.
  - **Не считается:** разовый ETB-value, добор одной картой, трюк.
  - **Минимум по полосам:** A/C — **≥1** (обычно мана-синк/power-up, чтобы лишняя мана не простаивала в лейте) · B — **≥5** (порог плотности, см. § Пороги 3 и 6 по полосе).
  - **⚠️ Роль дефицитна ровно потому, что её карты дешёвые по GIH.** Не ждать, что она закроется «сама собой» верхними пиками — её надо закрывать осознанно, как removal.
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

**3. `<set>_pilot.md` — ПИЛОТ-ЧЕКЛИСТ (как ИГРАТЬ). Читается НЕ перед драфтом, а ПЕРЕД МАТЧЕМ / при живом коучинге.** Задокументированные по логам лики розыгрыша, отсортированные по числу проигранных партий: когда тратить removal и в кого (иерархия «неблокируемое > летающее > наземное» + движок важнее тела), чтение роли «кто беатдаун», крэкбэк-чек, что нельзя питчить, мулиган-пороги, карточные ловушки сета (indestructible vs exile, тайминг пампа Stature, Wiccan = блинк). Обновлять после разбора партии, когда лик подтверждён по логу.

**Зачем три:** `knowledge` отвечает «кого ПИКать», `insights` — «во ЧТО собирать», `pilot` — «как РАЗЫГРЫВАТЬ». В драфте тянись в линию, которая по `insights` реально берёт трофеи, а не в «любые 2 цвета». **Причина разделения:** прогон рубрикатора 19.07 показал, что сборка у нас уже уровня 8, а партии сливаются в розыгрыше — значит пилот-лики нужны отдельным файлом, читаемым в ДРУГОЙ момент, иначе они тонут в драфт-заметках и не применяются.

**Когда обновлять:**
- После `analyze_game.py` / разбора партии — новый проверенный паттерн (карта over/under, рабочая линия, опасный матчап) → дописать в `<set>_insights.md`.
- После `DRAFT COMPLETE` — драфт-наблюдения (сигналы, открытые пары) → в `<set>_knowledge.md`.
- В любой момент — "запомни: ..." → немедленно записать в нужный из двух (геймплей → insights, драфт → knowledge).

**Как использовать в пике:**
- При старте драфта: `cat <set>_knowledge.md` И `cat <set>_insights.md`.
- В Think-шаге: «что знаем об этой карте/архетипе из прошлых драфтов (knowledge) И как это играет/выигрывает (insights)?»

**Файлы:** knowledge — `msh_knowledge.md` · `sos_knowledge.md` · `mkm_knowledge.md` ; insights — `msh_insights.md` ; pilot — `msh_pilot.md` (заводить `<set>_insights.md` / `<set>_pilot.md` по мере накопления партий в сете).

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

## Mode 1.5 — Live match coaching (добавлено 19–20.07.2026)

Живая помощь ВО ВРЕМЯ партии (не пика драфта) — на тренировочных играх (в т.ч. vs бот) или на реальном матче, когда нужны рассуждения по ходу, а не только пик-советы. Отдельный скрипт от `draft_live.py`.

**Инструмент — `match_live.py`:**
```bash
python3 ~/.claude/skills/mtg-draft-helper/match_live.py msh fresh   # первый вызов новой партии
python3 ~/.claude/skills/mtg-draft-helper/match_live.py msh         # последующие — блокирующий вызов
```
Блокируется до точки решения, печатает: жизни, оба стола (P/T со счётчиками, тапнутость, привязанные ауры/эквип — `⚠ПОД: <карта>`), руку, стек, GY, **и принудительную секцию `=== СПРАВКА ===` с ПОЛНЫМ оракл-текстом каждого уникального объекта в игре** (не по памяти — read это не опционально, это напечатано).

**Точки пробуждения (настроено под текущий тренировочный режим — не менять без явного запроса):**
- мулиган ещё не решён (стартовая рука, `MulliganReq` без ответа)
- **ТОЛЬКО моя главная фаза** (Main1/Main2) — их атака/боевые шаги НЕ триггерят (сузили по запросу 19.07; было — их атака тоже будила)
- debounce 0.3с на каждое срабатывание — сырой лог даёт транзитные turnInfo-блоки (Main1→BeginCombat→DeclareAttack за доли секунды), без него ловятся ложные срабатывания на их ходу

**Известные потолки данных (не чинятся, это факт лога, не баг):**
- **Объявленные атакующие не разбираются** парсером — спрашивать состав у игрока перед советом по блокам. TODO на будущее.
- **Карты вне наших `*_set.json` (msh/sos/mkm) — способности нельзя узнать из сырого лога вообще.** Arena не хранит keyword-абилки текстом, только числовые id. Это относится к тренировочным ботовским колодам вне сета; в настоящем драфте (Premier/Quick/Pick-Two) колода оппонента из того же сета и почти всегда резолвится.

**Правила рассуждения — читать `live_advice_rules.md` (мои лики как советчика, не лики игрока — те в `<set>_pilot.md`).** Ядро: пятишаговая процедура (читать тексты → выписать линии → посчитать состояние ПОСЛЕ каждой → сравнить → **черновик/самокритика/финал** → писать) + конкретные пойманные провалы (flash в главную фазу, аура-копирование на уникальное тело, crew≠участие в бою, владение аурой ≠ на чьём теле висит, кэш вывода вместо пересчёта).

**Формат ответа (директива игрока 19.07, отличается от `mtg-live-advice-ultra-short` для конкурентных матчей под часами):** для тренировочных игр — **два блока, не ультракоротко**: `# ДЕЙСТВИЯ` (нумерованный список) и `# РАЗМЫШЛЕНИЯ` (кратко, но с реальным рассуждением). Важное — жирным. Не объяснять очевидное («какую землю играть и почему», если выбор тривиален).

---

## Mode 2 — Post-game analysis

> **⚡ ПЕРЕД МАТЧЕМ / при живом коучинге — читать `<set>_pilot.md`** (`msh_pilot.md`). Минимум — блок «четыре вопроса каждый ход» + раздел под матчап. Это не то же, что `insights`: там «во что собирать», здесь «как разыгрывать». Обоснование приоритета: прогон 19.07 показал сборку уровня 8 при счёте 3W–3L, где 2 из 3 поражений имели окно — **узкое место в розыгрыше, не в билде.**
> **После разбора — дописывать туда новый лик** (только подтверждённый по логу, с датой и ценой), а не хоронить его в тексте `insights`.

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
- **🚫 ЗАПРЕЩЁННЫЙ ВЫВОД ИЗ `OUT-ENGINED`: «на следующем драфте добрать ещё один ответ / карту против движка» (внесено 10.08.2026).** Мы записали этот вывод **8 раз подряд разными сборками** (24.07 · 25.07 · 29.07 · 02.08 · 08.08×2 · 10.08-2) — и он не сработал ни разу, потому что неисполним по построению: движок делает N угроз с одной карты, спот-removal отвечает на одну. Размен 1-в-N нельзя выиграть плотностью ответов — их пришлось бы взять 8.
  - **Легальных ответов на OUT-ENGINED ровно два:** **ПОД** (клок быстрее их сборки — см. квоту `⚑ КРИВАЯ`) или **НАД** (свой движок, полоса B, порог входа ≥5 карт). «Темпо + 4 ответа» — это между, и оно проигрывает обоим.
  - **Прежде чем писать `OUT-ENGINED`, назови метрику `существо к T2` этой колоды.** По нашим данным поражения этого класса кучкуются у сборок с ≤56% — то есть диагноз часто не «у них движок глубже», а **«мы не успели начать»**, и лечится он квотой на пике, а не ещё одним removal.
  - Если после этой проверки вывод всё равно «нужен ответ» — он допустим, но обязан назвать **конкретный класс карты** (массовый ответ / exile перманента-источника), а не «ещё removal».

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

### 🔴 ШАГ 0 СБОРКИ — ПЕРЕСЧИТАТЬ ПУЛ ПО ПАР-ФИЛЬТРОВАННОМУ GIH (внесено 10.08.2026, ошибка поймана пользователем)
> **Цвета на сборке уже ИЗВЕСТНЫ. Значит глобальный GIH здесь — заведомо худшие данные из доступных, и строить по нему нельзя.** Пар-фильтрованные числа лежат в `cache_17l_<set>_<PAIR>.json` (их пишет `draft_live.py` во время драфта) — в драфте я их читаю, а на сборке систематически забывал и ранжировал пул по глобальному GIH.

```bash
cd ~/.claude/skills/mtg-draft-helper
python3 pair_gih.py <set> <PAIR> <deck.txt>    # разобрать конкретный лист
python3 pair_gih.py msh WU --pool [--quick]    # весь пул из лога
```
Печатает `глоб · ПАРА · Δ · IWD в паре · ΔIWD · n`, взвешенный средний парный GIH, и сам помечает **🔄 смену знака IWD** и **⚠ выборку <500 игр**.

**Почему это не косметика — сдвиг НЕРАВНОМЕРНЫЙ, поэтому МЕНЯЕТСЯ ПОРЯДОК КАРТ:**
- Типичный сдвиг в паре **+1.3…+4.2 GIH**, но у разных карт разный: U.S.Agent +4.2, Captain America Wings +1.3. Две карты, «равные» по глобальному числу, в паре расходятся на 3 пункта.
- **IWD может поменять ЗНАК** — а IWD у нас управляет флагом `⚠trap`. Док. случай (MSH/WU, 10.08): **Shuri** глоб IWD **+1.2** → в WU **−2.1**; **Kree Commandos** глоб **−1.2** → в WU **+0.3**. То есть глобальные данные говорили «бери Shuri, режь Kree», а парные — ровно наоборот. Я предложил замену по глобальному числу, пользователь возразил («меняем летающего с prowess на Shuri, которая ничего не умеет?») и оказался прав.
- В том же прогоне по глобальным числам я недооценил **Helicarrier Strike** (58.0 → в WU **60.3**, n=13k) и **Iron Lad** (55.1 → **58.0**) и зря вырезал их из листа.

**Правила чтения:**
1. **Ранжируй пул по ПАРНОМУ GIH, глобальный оставляй только как фон.** Средний парный GIH листа — та цифра, которую называешь в блоке «Сила» (не глобальный).
2. **`⚠trap` (IWD<0) пересчитывай по парному IWD.** Флаг из снапшота драфта построен на глобальном числе и в паре может быть ложным.
3. **n < 500 → парному числу не верить**, откатываться на глобальное (скрипт помечает сам). Особенно у редких/нишевых карт.
4. **Пара может быть не закэширована** — тогда скрипт скачает её сам (в оффлайне откажется). Проверь наличие кэша ДО того, как начнёшь резать пул.

### ⚠️ GIH ДОРОГИХ КАРТ РАЗДУТ ВЫЖИВАНИЕМ — сверяй IWD и РЕАЛЬНУЮ кастуемость (внесено 10.08.2026)
Высокий GIH у карты с cmc≥6 частично означает «я дожил до 7-го хода и потому выиграл», а не «карта выиграла». Не отменяй порог 5 из-за красивого парного числа.
- Док. случай: **Atlantis Attacks** cmc 7 — парный GIH в WU **60.2** (выглядит как топ-половина листа!), но **IWD всего +1.2** против **+3.3** у второго Trickster's Stratagem, а замеренная кастуемость на реальной мана-базе — **9.9% к 8-му ходу**, 20.1% к 10-му.
- **Что делать вместо «посмотреть на GIH»:** сравнивать **IWD** (он не награждает карту за то, что ты дожил) и **мерить кастуемость симуляцией на СВОЕЙ мана-базе**, а не на глаз.
- То же смещение работает и в обратную сторону: у дешёвых карт GIH занижен, потому что их тянут ранние проигранные партии.

### 🚫 НЕ ЗАТЫКАТЬ ПРОВАЛЕННЫЙ ПОРОГ ПЛОХОЙ КАРТОЙ (внесено 10.08.2026)
Порог — это **диагностика, а не мандат впихнуть любую карту, которая его удовлетворяет.** Если единственный кандидат под порог имеет **отрицательный IWD в паре** — честнее провалить порог, назвать слабость вслух и играть вокруг неё, чем ухудшать колоду ради метрики.
- Док. случай: порог 3 (существо к T2) провален на 54.8%. Единственный оставшийся 2-дроп в пуле — Shuri с WU-IWD **−2.1**. Взять её = поднять метрику до 63% картой, которая статистически ухудшает партии, где её добрал. Правильный ответ — **оставить провал, записать его как ограничение ПУЛА (а не ошибку сборки) и компенсировать пилотированием.**
- **🔴 НО НЕ «жёстче мулиган» — ЭТО ОШИБКА, ПРОВЕРЕННАЯ НА ПРОГОНЕ (WU 1W–3L, 10.08.2026).** Я написал сюда «рука без действия до 3-го хода — сброс», и оба мулигана прогона стали поражениями. **Нельзя замулиганить в кривую, которой в колоде нет:** при 4 существах cmc≤2 шанс раннего действия падает **55.2% → 49.3%** на шести картах (функциональность руки 87.8% → 82.1%). Мулиган ищет плотность — если плотности нет, он просто отнимает карту.
- **Правильная политика для колоды с тонким Develop — МЯГЧЕ обычного:** держи любую руку 2–5 земель с двумя кастуемыми заклинаниями и **прими пустой 2-й ход как норму**. Сбрасывай только 0–1 / 6+ земель или руку, где всё дороже 4.
- **Калибровка порога 3 (измерено на 6 прогонах голдфиша, MSH):** число существ **cmc≤2** переводится в метрику почти ступенькой — **4 дешёвых существа ≈ 55%, 5 ≈ 64–65%**. То есть порог 3 фактически = «в колоде ≥5 существ на 1–2 маны». Если пул их не дал — метрику не вытянуть ничем, кроме плохих карт.
- **Смягчающее обстоятельство, требующее проверки (гипотеза, не правило):** порог 3 выведен из мидрейнджа. Темпо-колода с **блокером к T3 ≥90%** может переживать пустой 2-й ход. Не отменять порог, но при провале печатать рядом «блокер к T3» и отмечать прогон в `<set>_match_log.md`, чтобы набрать выборку.

### Креативный проход ПЕРЕД финалом (не собирай мягкую середину по умолчанию)
Прежде чем механически резать пул до 40 по ролям — спроси, какая **самая высокопотолочная КОГЕРЕНТНАЯ** версия этого пула:
- Стоит ли **сплеш ради бомбы/хеймейкера** (проверь по Rule of Three + `draft_goldfish.py`, а не на глаз)?
- Есть ли **build-around-линия** (counters-снежок, connive-движок, go-wide+памп, эвейжн-рейс с неблокируемым финишёром), которую пул реально тянет и которая бьёт СИЛЬНЕЕ, чем goodstuff-мидрейндж?
- В какую из трёх полос (A/B/C) пул заострён естественно — и не размываем ли мы это, добирая «безопасные одиночки» в мягкую середину?
- **Где wincon?** Нет закрывашки → durdle-пул проигрывает на Платине (документированные 0:3). Найди финишёр или собери самый агрессивный клок из возможного.

Выбери полосу с самым высоким потолком, который пул **реально поддерживает** (плотностью, не одной картой), затем добери пол (removal / эвейжн / кривую). Творческий, но КОГЕРЕНТНЫЙ билд > безопасный и мягкий. Это тот же вопрос, что в Pn/P1-пересмотре (§ Pick process, шаг 0b) — на финале он последний раз.

### 🎯 РУБРИКАТОР «8+» — считать ПОРОГАМИ, а не ощущением (добавлено 19.07.2026)
> **🎯 ЦЕЛЬ = 8+ КАЖДЫЙ ДРАФТ (директива пользователя 19.07.2026), то есть минимум 6 порогов из 7 и НИ ОДНОГО проваленного стоп-крана.**
> Почему именно 8, а не 9: **9 (7/7) требует, чтобы пул дал закрывашку и ось — это уже раздача** (открытый лейн, пришедшая бомба). **8 (6/7) достигается одной дисциплиной, почти из любого пула.** Цель, которая зависит от везения, не цель — 8 это ПОЛ, который держим всегда, 9 это апсайд, когда пул позволил.
> **Практический вопрос на аудите:** не «дотянем ли до 9», а **«какой ОДИН порог я осознанно готов провалить — и это точно не стоп-кран?»** Явно выбранная слабость даёт 8; дрейф без выбора даёт три проваленных порога и 6.
Причина: я систематически завышаю свои сборки ([[mtg-dont-overrate-soft-middle]]) — «7/10» ставилось и трофейным, и вылетевшим 0:3 колодам. Ощущение не калибруется, пороги калибруются. Выведены из наших трофеек (UB 7:2, GU 6:3, BR) и двух листов финала Pro Tour (`msh_knowledge.md` § PRO TOUR).

**🔑 ГЛАВНАЯ МЕТРИКА, которую мы раньше не считали — РОЛЕЙ НА КАРТУ.**
> **Ценность добирается ролями на карту, а не картами в руку.** Наш рефлекс при нехватке value — доложить добор (Futurist Forge). Ответ про — взять карту, которая УЖЕ делает два дела: это то же карт-преимущество, но **без потери темпа и без слота**.
> Считается так: карта = «двуролевая», если делает 2+ вещи ИЛИ масштабируется от плана деки. Тело+removal (Red Guardian) · тело+токены (Okoye) · земля ИЛИ заклинание (Borough Backup, циклеры) · модальная (Murdock's) · эквип на пейофф (Spy Kit) · flash-тело · тело+ETB-value (Hero in Training) · тело+мана-синк (power-up).
> **Эталон: у Штойера (PT-финал) двуролевых — практически все 24 из 24.** У наших вылетевших сборок — примерно треть (Atlantis ×2, Forge, реактивный removal 1-в-1 = по одной роли каждая). Подтверждается и нашей историей: трофейка UB 7:2 состояла из многоролевых (Leader движок+добор, Stature финишёр+неблокируемость, Mister Fantastic стена+reach+добор).

**7 порогов — считать ЧИСЛАМИ перед выдачей тира:**
| # | Порог | Откуда |
|---|---|---|
| 1 | **Двуролевых ≥15 из 23** | PT-эталон ~24/24; наши провалы ~треть |
| 2 | **Тел ≥15** (токен-мейкер считается своими телами) | гайд «15+ crips», Штойер 21 |
| 3 | **Существо к T2 ≥60%** (goldfish) | трофейка 77%, PT 64/85%, вылет 11.07 — **40%** |
| 4 | ~~Hard removal ≥4~~ → **ПОНИЖЕН 10.08.2026 до «разбери по категориям и назови число»**. Порог ≥4 опровергнут: у 23 листа 7-1/7-2 медиана безусловного removal **1**, у пяти колод **ноль**. Разбивка по категориям (см. ниже) остаётся полезной, само число «≥4» — нет | было: трофейки 7, PT 6 (n=5, только наши) |
| 5 | **Верх кривой: ≤4 карт с cmc≥5, НОЛЬ с cmc≥6** | оба PT-листа кончаются на 5; наш вылет — 2× Atlantis (7) |
| 6 | **Закрывашка есть** — карта, которая реально УБИВАЕТ (≥4 силы / неблокируемое / бомба-финишёр) | вылет 16.07: «ответы были, убить нечем», макс. тело 3/3 |
| 7 | **Когерентный ПЛАН, выраженный ≥4 картами** — синергия-ось ИЛИ параллельная линия — **И ≥2 ломателя Parity** (ЛЮБЫЕ: эвейжн/неблокируемое · reach/burn · solo-attack+раз-тап · ширина+first strike · инэвитабилити-движок) | Штойер: solo-attack ×4 · трофейка UB: эвейжн-рейс ×5 |

**Тир по числу взятых порогов:** 7/7 → **9+** (апсайд, если пул дал) · 6/7 → **8 ← ЦЕЛЬ, ПОЛ КАЖДОГО ДРАФТА** · 5/7 → **7** · ≤4 → **6 и ниже (мягкая середина)**.
**🚨 ДВА СТОП-КРАНА (перекрывают счёт):** провален порог **6 (закрывашка)** ИЛИ порог **3 (существо к T2)** → **потолок 7, как бы ни было остальное.** Это ровно два наших документированных failure-mode: «загнал, но не добил» и «переехали до того, как я развернулся».

### 🔁 ПОРОГИ 3 и 6 — ЧИТАТЬ ПО ПОЛОСЕ (внесено 08.08.2026, разбор «почему мы никогда не собираем движок»)
**Проблема, которую это чинит:** оба стоп-крана выведены из мидрейнджа/темпо (полосы A и C) и **структурно недостижимы для полосы B**. Настоящая движковая колода (Leader 1/3 за 4, connive, добор) проваливает «существо к T2 ≥60%» по построению, а её закрывашка — часто инэвитабилити, а не тело ≥4 силы. В той же § КОММИТ В ПОЛОСУ мы сами пишем, что B **сдаёт время в Ahead**, и тут же наказываем её порогом, выведенным из полосы, которая не сдаёт ничего. Итог до этой правки: **рубрикатор не мог поставить движковой колоде выше 7 ни при каком исполнении** — то есть запрещал архетип, который нас регулярно обыгрывает (6 задокументированных OUT-ENGINED подряд).

**СНАЧАЛА назови полосу вслух, ПОТОМ считай стоп-краны.** Полоса объявляется на аудите P3P1 и не меняется задним числом под удобный счёт.

| Стоп-кран | Полосы **A / C** (как было) | Полоса **B** (движок/контроль) |
|---|---|---|
| **3 — Develop** | существо к T2 **≥60%** (goldfish) | **«не умираю до онлайна»:** ранний интерактор/блокер к T3 **≥75%** (goldfish `блокер к T3` + дешёвое removal ≤3 маны) **И движок онлайн к T5** (якорь/добор-мотор кастуем к T5 ≥60%) |
| **6 — Ahead** | закрывашка: ≥4 силы / неблокируемое / бомба-финишёр | **инэвитабилити ИЛИ закрывашка:** повторяемый источник преимущества, который оппонент не может отыграть (движок-якорь + ≥1 способ конвертировать в победу). **1–2 конвертера, а не плотность** |

- **Порог 6 для B НЕ отменяется, а переформулируется.** Урок 07.07 («движок без закрывашки = durdle-лоссы») остаётся в силе — но он про **отсутствие способа выиграть**, а не про отсутствие тела 4/4. Инэвитабилити засчитывается только если названо, ЧЕМ именно партия заканчивается.
- **Полоса B обязана предъявить ПЛОТНОСТЬ, иначе считается по A/C.** Порог входа: **≥5 карт движка** (якорь + детали, кормящие друг друга). 3–4 карты = shallow = мягкая середина, и тогда стоп-краны читаются по A/C без поблажек. Это ровно диагноз 07.07 — обобщать его в «движки — ловушка» было ошибкой, ловушка это **половина** движка.
- **Модификатор качества (средний GIH) для полосы B не применять как минус.** Детали движка стоят 51–55 GIH в вакууме (Machinesmith 51.3, Super Intelligence 53.1, Atlantean Cavalry 53.0, HYDRA Assault Robot 52.9) — это цена архетипа, а не слабость сборки. Считать вместо этого **число активаций за партию**, если есть данные из матч-лога.
**Модификатор качества (±0.5):** средний GIH пула ≥58 и мало карт <54 — плюс; несколько карт <54 — минус (Детечник на PT: структурно 7/7, но 4 карты <54 → 8.5, а не 9).
> **⚠️ ЭТИ ПОРОГИ (≥58 / <54) ОТКАЛИБРОВАНЫ НА ГЛОБАЛЬНОМ GIH.** Парные числа идут на **+1.3…+4.2** выше (§ Шаг 0 сборки), поэтому подставлять их сюда напрямую нельзя — иначе плюс получит вообще каждая колода. Либо считай модификатор по глобальным числам, либо сдвинь порог на наблюдённую дельту пары (для MSH/WU это ≈ **+2.5**, т.е. парный ≥60.5 / карты <56.5) — и **явно скажи, по какой шкале посчитал.** Смешивать две шкалы в одном выводе — прямой путь к завышению, к которому я и так склонен ([[mtg-dont-overrate-soft-middle]]).

**🎲 КВАДРАНТНЫЙ ПРОФИЛЬ — печатать РЯДОМ со счётом (диагностика, НЕ 8-й порог).** Восьмой порог сделал бы цель 8+ недостижимой и сломал калибровку; профиль вместо этого объясняет счёт и ловит то, что пороги пропускают. Формат: `6/7, профиль D4/P3/A2/B4 — провален Ahead, это стоп-кран`.
- Пороги 3/7/6/4 = Develop/Parity/Ahead/Behind (§ Quadrant Theory) — профиль это их пересказ в понятном виде, а не отдельный подсчёт.
- **Плоский профиль ≈3/3/3/3 при формально взятых порогах → модификатор −0.5 и ОБЯЗАН назвать полосу вслух.** Это ровно портрет мягкой середины: нигде не провалено, нигде и не сильно. Бьёт по моему задокументированному завышению ([[mtg-dont-overrate-soft-middle]]).
- **Слабый квадрант ≠ провал, если он СДАН полосой осознанно** (C сдаёт Behind, B сдаёт время в Ahead). Агро с B2/5 — это агро, а не дырявая колода. Агро с D2/5 — дырявая колода.

**⚠️ Уточнения порогов 4 и 7 — внесены 19.07.2026 после тестового прогона на нашей UB-темпо (3W–3L), оба бага вскрылись именно там:**
- **Порог 4 — считать removal ПО КАТЕГОРИЯМ и называть числа отдельно** (правило уже было в `msh_knowledge.md`, рубрикатор его игнорировал): **безусловное** (destroy/exile/tuck любого) · **условное по размеру** (сила ≤N / тафнесс ≥N) · **лок** (Frozen-класс) · **fight** (нужно своё тело) · **−X/−X** (НЕ removal). **Обязательно назвать, сколько отвечает на БОЛЬШОЕ тело (сила или тафнесс ≥5).** Док. случай: рубрикатор насчитал «6 removal», а матч-лог честно писал «hard-removal всего 2» — обе Elektra (сила ≤3) мертвы против Hulk 6/5 и Red Hulk 6/7, и это решило партию. **«6 интеракции» ≠ «6 ответов на их лучшее тело».**
- **Порог 7 — ПЛАН, а не обязательно синергия.** Первая формулировка («≥3 карты, кормящие друг друга») **заваливала нашу собственную трофейную UB 7:2** — там параллельный эвейжн-рейс, карты не разговаривают друг с другом, и колода взяла трофей. Порог, отвергающий трофейку, откалиброван неверно. Засчитывается и **синергия-ось** (Штойер: solo-attack ×4), и **параллельная линия** (эвейжн/неблокируемый рейс ×5), если она выражена ≥4 картами. Не засчитывается пайл хороших карт без общего плана.
- **➕ Порог 7 расширен 22.07.2026 — «≥2 ломателя Parity».** Дыру нашли через Quadrant Theory: **эвейжн был в «Deck targets» (≥2–3) и в памяти по MSH, но НИ В ОДИН из 7 порогов не входил** — то есть квадрант Parity был у нас единственным неинструментированным. При этом наша трофейка UB 7:2 выиграла ровно эвейжн-рейсом. **Формулировка НАРОЧНО шире, чем «эвейжн»** — иначе порог противоречил бы нашей же заметке `msh_knowledge.md` §7 (n=2): Штойер и Детечник ломали стойку solo-attack+раз-тапом и шириной+first strike, имея 1–2 флаера. Считается любой механизм, который РЕАЛЬНО пробивает стойло; не считаются голые наземные тела. Порог 7 стал строже — осознанно, оба PT-листа и обе наши трофейки его проходят.
- **📌 Что прогон ПОДТВЕРДИЛ:** наша сборка от 19.07 взяла 6/7 (двуролевых **20/23**, существо к T2 **69.2%**, верх кривой — 1 карта на 5, лучше обоих PT-листов). Гипотеза «наши колоды бедны ролями на карту» на ней **НЕ подтвердилась**. Счёт 3W–3L просел на пилотировании (2 из 3 поражений с задокументированными окнами), а не на сборке. **Вывод: на сборке цель 8 мы уже примерно берём — прирост винрейта теперь в пилотировании** (совпадает с выводом `msh_insights.md` «bottleneck на плато = ПИЛОТИРОВАНИЕ, не сборка»). Не искать проблему в билде, когда она в розыгрыше.

**Как этим пользоваться (важно — это НЕ финальный чек):**
- Порог 1, **3** и 5 **нельзя починить на сборке** — они решаются НА ПИКЕ. **Порог 3 добавлен сюда 10.08.2026:** он фактически равен «в колоде ≥5 существ cmc≤2», а дешёвые существа в пуле либо есть, либо нет — на финале взять их неоткуда. Поэтому прогонять рубрикатор **на аудите P2/P1 и P3/P1** (§ Pick process, шаг 0), пока есть ещё бустер, чтобы добрать недостающее. На финале он только фиксирует результат.
- **При равном GIH бери двуролевую карту.** Это прямое пик-правило, вытекающее из порога 1: токен-мейкеры, модальные, циклеры/земли-заклинания, тела-с-removal, flash-тела — систематически недооценены нашим GIH-рефлексом.
- **Называть провалённые пороги вслух** в блоке «Сила» ниже. «B≈6.5, провалены пороги 1 и 6» информативнее, чем «крепкая колода с небольшими проблемами».

### ALWAYS describe the deck after building it (обязательный формат)
**После сборки/тюнинга любой колоды — всегда выдать два блока, не только лист + голдфиш:**

**1. Сила: <буква-тир ≈X/10>**
- **Что даёт силу** — якорь/бомба, плотность и качество removal, эвейжн, карт-преимущество (конкретные карты).
- **Что ограничивает (честно)** — сила пары на Arena (из `<set>_knowledge.md`), проблемы кривой, реактивность/уязвимость к топ-архетипам, зависимость от 1 карты. Не приукрашивать.
- **Реалистичный итог** — пол и потолок словами («уверенные 4–5 побед с апсайдом на трофей»), не обещать 7-0.

**1b. ВТОРОЙ рейтинг (Draftsim-стиль, добавлено 29.07.2026 по запросу пользователя) — считать ПАРАЛЛЕЛЬНО с рубрикатором, не вместо.**
Пользователь сравнивает две методики между собой на практике (кросс-прогонный трек-рекорд), чтобы понять, какая лучше предсказывает реальный результат — поэтому обе должны выводиться каждый раз, без исключений.
Реконструировано из одного скриншота Draftsim (см. `mtg-draftsim-deck-score-reverse-engineered`): **Deck Score = простое (невзвешенное) среднее шести осей 0–10**: Power Level, Mana Curve, Bombs, Synergy, Removal, Mana Base. Точной формулы Draftsim для отдельных осей у нас нет — это прокси-реконструкция по смыслу названий и по данным, которые уже считаются в этом воркфлоу (17Lands GIH/WU-GIH, `draft_goldfish.py`). Явно говорить пользователю, что это оценка по аналогии, а не официальный алгоритм Draftsim.
- **Power Level** — средний GIH нонлендов относительно центра формата (~55); ориентир: GIH 59.8 ≈ 7.0/10. **Считать по ГЛОБАЛЬНОМУ GIH** — шкала-ориентир построена на нём; парный подставлять только вместе со сдвинутым ориентиром (§ Шаг 0 сборки), иначе ось ломается вверх у всех.
- **Bombs** — здесь же ловится систематическая слепота обеих методик: когда в пуле нет карты, выигрывающей партию в одиночку, Draftsim роняет эту ось (5.5–6.0), а рубрикатор берёт порог 6 «через плотность/рой» и разрыв между оценками растёт. Если методики разошлись ≥1 балла — назвать причину вслух, это и есть полезная информация, а не шум.
- **Mana Curve** — форма кривой существ (пик на 2–3, малый верх cmc≥5) → выше балл при кривой, близкой к Karsten-таргетам.
- **Bombs** — число карт A+/A tier (GIH ≥63) в 23 нонлендах; 0 бомб ≈ низкий балл, 1 бомба на 23 карты ≈ середина (6.0), 2+ — выше.
- **Synergy** — связность плана: число ломателей стойки (эвейжн/неблокируемое/first strike и т.п.) + наличие движка (Political Triumph-класс), НЕ то же самое, что порог 7 рубрикатора, но пересекается.
- **Removal** — количество БЕЗУСЛОВНОГО removal (то же множество карт, что и порог 4 рубрикатора) — 3 карты ≈ 4.0/10, 4+ ≈ 6–7/10.
- **Mana Base** — из `draft_goldfish.py`: кип/скрю/существо-к-T2 напрямую переводятся в балл (образцовая мана ≈ 9.0, скрю >6-7% или существо-к-T2 <60% резко роняет).
- **Итог = среднее шести чисел** (не средневзвешенное — так ведёт себя эталонный пример, где Mana Base=0 линейно тянул общий счёт вниз несмотря на Synergy=10).
- **Показывать оба числа рядом в блоке «Сила»**, например: `Рубрикатор: 6/7 (провален removal≥4) → тир ~8/10 · Draftsim-прокси: 6.8/10 (Power 7.0 · Curve 8.5 · Bombs 6.0 · Synergy 6.5 · Removal 4.0 · Mana 9.0)`. Явно называть, где методики СХОДЯТСЯ (обычно на слабом removal — оба метода его ловят независимо, это усиливает диагноз) и где РАСХОДЯТСЯ (у рубрикатора два порога — стоп-краны, обнуляющие тир целиком; у Draftsim-среднего слабая ось топит счёт линейно, а не катастрофически, если остальное сильное).
- Со временем, когда накопится больше прогонов (`msh_match_log.md`), сверять — какой рейтинг точнее предсказывал реальный W/L этой колоды — и фиксировать вывод в `msh_knowledge.md`.

**2. Как играть**
- **Роль:** ты контроль / агро / темпо? Одной фразой — и из неё следует всё остальное.
- **Ключевые правила пилотирования:** что держать на инстант-скорости, чем выживать рано, как собрать движок-якорь (сиквенсинг синергий), win condition.
- **Mulligan:** что оставлять / что сбрасывать.
- **Матчапы:** хороший и плохой, и как играть каждый (vs агро — стабилизируйся/не дёргайся; vs контроль — карт-преимущество/flash вокруг removal). Помнить: Premier = Bo1, это план НА ИГРУ, не сайд.

Тон — как у тренера: честно про слабости, конкретные действия, не общие принципы. (Согласовано с пользователем 25.06.2026.)

### Порядок сборки (четыре инструмента, все четыре обязательны)
1. **`pair_gih.py <set> <PAIR> --pool`** — пересчитать пул по паре (§ Шаг 0). Ранжирование и `⚠trap` — по ПАРНЫМ числам.
2. Собрать 23+17 по ролям и порогам (§ Креативный проход, § Рубрикатор).
3. **`draft_goldfish.py`** — проверить МАНУ и раннюю игру; при спорном топ-энде домерить кастуемость симуляцией на своей мана-базе, а не по GIH.
4. **`build_audit.py <лист.txt> --pool pools/<set>_<draft8>.txt` — ГЛАВНАЯ проверка (§ КАЛИБРОВКА).** Пул `draft_live.py` сохранил сам на каждом пике; `--pool` вычтет мейн и получит сайд. (Если лист уже содержит `Sideboard`, флаг не нужен.) Даёт (а) положение по каждой оси в распределении 14 победителей — чинить только то, что ниже ВСЕЙ популяции; (б) тест «мейн ≠ жадный топ-23». **Совпадение с жадным = плана нет, вернуться к § Креативный проход.**
5. `pair_gih.py <set> <PAIR> <deck.txt>` на финальном листе — средний парный GIH для блока «Сила».

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
