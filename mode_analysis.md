# MODE 2 — РАЗБОР ПАРТИИ  ·  MODE 1.5 — ЖИВОЙ КОУЧИНГ В МАТЧЕ

> **Читается ПОСЛЕ матча (разбор) или ПЕРЕД матчем (коучинг), не во время драфта.**
> Перед матчем и при живом коучинге сначала читать `<set>_pilot.md` — там «как РАЗЫГРЫВАТЬ»,
> здесь только инструменты и формат.
> Лог Arena ротируется быстро — разбор и HTML делать сразу после матча.

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

