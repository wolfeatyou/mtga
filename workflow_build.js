export const meta = {
  name: 'orchestrated-build',
  description: 'Оркестрированная сборка лимитед-колоды: линии из досье → веер строителей → судья',
  whenToUse: 'mode_build.md § МУЛЬТИСБОРКА: после DRAFT COMPLETE, вход — пул + досье pool_dossier.py',
  phases: [
    { title: 'Линии', detail: 'брифы линий: из args.lanes (сессия решила по досье) или агент-проектировщик' },
    { title: 'Сборка', detail: 'по строителю на линию, каждый: constraint=линия, objective=качество карт' },
    { title: 'Судья', detail: 'сам пишет кандидатов в файлы, гоняет скорборд-скрипты, решает по приору' },
  ],
}

// args: {set, draft8, pair, pool, dossier, medians, maxLanes,
//        lanes?: [{name,plan,must,avoid}]  — брифы от сессии: этап «Линии» пропускается
//                                            (в проде контроль загрязнения не нужен — финала ещё нет),
//        judge?: false                     — вернуть только кандидатов (ретро/отладка),
//        outDir?: строка                   — куда судье писать кандидатов (обязателен для судьи)}
// Ускорение 20.08.2026 (JOURNAL § 8.22): раньше судья был отдельным агентом ПОСЛЕ воркфлоу,
// скорборды и промпт судьи собирала сессия руками — медленно и с ошибкой переноса листа.
// Теперь всё в одной инвокации, судья сам гоняет скрипты, листы не перепечатываются.
// ДЕФОЛТЫ МОДЕЛЕЙ (утверждено пользователем 20.08.2026 по A/B § 8.22):
//   строители — sonnet/medium (их огрехи чинит судья; medium-судья в A/B пропустил
//   нарушение потолка и графтил против линии — судьёй его не ставить);
//   судья и проектировщик — sonnet/high (повторил opus-вердикт карта-в-карту и поймал
//   Lake-town, которую opus пропустил). args.model/effort и judgeModel/judgeEffort — оверрайды.

const B_MODEL = { model: (args && args.model) || 'sonnet', effort: (args && args.effort) || 'medium' }
const J_MODEL = { model: (args && args.judgeModel) || 'sonnet', effort: (args && args.judgeEffort) || 'high' }
const SKILL = '~/.claude/skills/mtg-draft-helper'

const LANES_SCHEMA = {
  type: 'object',
  properties: {
    mode: { type: 'string', enum: ['fan', 'single'] },
    rationale: { type: 'string' },
    lanes: {
      type: 'array', minItems: 1, maxItems: 3,
      items: {
        type: 'object',
        properties: {
          name: { type: 'string' },
          plan: { type: 'string' },
          must: { type: 'array', items: { type: 'string' } },
          avoid: { type: 'array', items: { type: 'string' } },
        },
        required: ['name', 'plan', 'must', 'avoid'],
        additionalProperties: false,
      },
    },
  },
  required: ['mode', 'rationale', 'lanes'],
  additionalProperties: false,
}

const CARD = {
  type: 'object',
  properties: { n: { type: 'integer', minimum: 1 }, name: { type: 'string' } },
  required: ['n', 'name'], additionalProperties: false,
}
const BUILD_SCHEMA = {
  type: 'object',
  properties: {
    main: { type: 'array', items: CARD },
    lands: { type: 'array', items: CARD },
    plan: { type: 'string' },
    route: { type: 'string' },
    flex: { type: 'array', items: { type: 'string' } },
  },
  required: ['main', 'lands', 'plan', 'route', 'flex'],
  additionalProperties: false,
}

const RULES = `ПРАВИЛА СБОРКИ (дистиллят mode_build.md, калиброван на 298 листах 7-1/7-2):
· ровно 23 нонленда + 17 земель (нонбейзик-земли пула считаются в 17);
· приоритет: БОМБА > СИНЕРГИЯ > РЕЙТИНГ > кривая; GIH — сортировка, не мерило колоды;
· роль (removal/закрывашка/движок) режется только за роль же, НЕ за метрику кривой;
· тело силой ≥4 режется только за тело ≥4 или removal; верх кривой cmc≥5 ≤4 и cmc≥6 ≤2 —
  это ПОТОЛКИ, а не цели (64% тел ≥4 у победителей стоят на cmc≥5);
· кривая и крупные тела — РАЗМЕН (r=−0.28): не выравнивай обе оси к медиане;
· потолки копий из досье (⚠×N>потолка) не превышать без named-причины;
· ⚠-флаги досье (ЛОВУШКА-СЕТА / НЕ-В-ЭТОЙ-ПАРЕ) — карта в мейн только с причиной;
· анти-связки досье не совмещать в мейне без причины — это измеренные конфликты планов;
· сплеш только под явную причину: 69% победителей — строго 2 цвета, медиана сплеша 1 карта;
· Premier = Bo1: сайда нет, ответ на частые угрозы должен жить в мейне.`

function laneDesignerPrompt(a) {
  return `Ты проектируешь ЛИНИИ сборки для лимитед-пула MTG (сет ${a.set.toUpperCase()}, Premier Bo1, пара ${a.pair}).

Твоя единственная задача — решить по досье: есть ли в пуле НАСТОЯЩАЯ развилка планов, и если есть — написать брифы 2-3 взаимоисключающих линий. Не собирай колоду сам.

ГЕЙТ (правило из mode_build.md § МУЛЬТИСБОРКА):
· 'fan' (веер) — только если пул поддерживает ≥2 СОДЕРЖАТЕЛЬНО разных плана: разные достижимые маршруты (таблица ЛИНИИ досье) И/ИЛИ взаимоисключающие пакеты (секция анти-связок). Линии обязаны различаться ПЛАНОМ (какие 4-6 карт обязательны, какие запрещены), а не двумя флекс-слотами.
· 'single' — если план по сути один: тогда ровно одна линия с самым сильным планом.
Помни измеренный факт: три строителя с одинаковым заданием сходятся в один лист — веер без настоящей развилки это выброшенные токены.

В каждом брифе:
· name — короткое имя линии; plan — 2-3 предложения: чем колода выигрывает (маршрут) и что для этого держим;
· must — 3-6 карт пула, обязательных для этой линии (ядро плана);
· avoid — карты пула, которые в этой линии НЕ играются (например, половины анти-связок).
Линии не должны требовать карт вне пула. Маршрут линии должен быть достижим по таблице ЛИНИИ (запас ≥0).

=== МЕДИАНЫ ПОБЕДИТЕЛЕЙ ПАРЫ ${a.pair} (маршруты) ===
${a.medians}

=== ПУЛ ===
${a.pool}

=== ДОСЬЕ ===
${a.dossier}

Работай только с данными этого промпта — не читай файлы и не используй инструменты. Верни строго JSON по схеме.`
}

function builderPrompt(a, lane) {
  return `Ты собираешь лимитед-колоду MTG по НАЗНАЧЕННОЙ ЛИНИИ (сет ${a.set.toUpperCase()}, Premier Bo1, пара ${a.pair}, 40 карт).

ТВОЯ ЛИНИЯ — «${lane.name}»: ${lane.plan}
· ОБЯЗАН включить в мейн: ${lane.must.join(' · ')}
· НЕ включать: ${lane.avoid.length ? lane.avoid.join(' · ') : '—'}
· Маршрут линии должен быть ≥ медианы пары (медианы ниже).

ЦЕЛЕВАЯ ФУНКЦИЯ: внутри ограничений линии МАКСИМИЗИРУЙ качество карт (GIH в досье).
Жертвуй рейтингом только там, где этого требует линия или роль — и знай почему.
Частоты у победителей (столбец ${a.pair} N% и потолок ≤K в досье) — сильный приор:
карта с 0-7% у победителей пары попадает в мейн только с named-причиной.

${RULES}

=== МЕДИАНЫ ПОБЕДИТЕЛЕЙ ПАРЫ ${a.pair} ===
${a.medians}

=== ПУЛ (мейн собирается только из него) ===
${a.pool}

=== ДОСЬЕ ===
${a.dossier}

Перед ответом проверь арифметику: сумма main = 23, сумма lands = 17, каждая карта не
превышает число копий в пуле. В flex назови 2-4 слота мейна, в которых ты меньше всего
уверен. Работай только с данными этого промпта — не читай файлы и не используй
инструменты. Верни строго JSON по схеме.`
}

const JUDGE_SCHEMA = {
  type: 'object',
  properties: {
    winner: { type: 'string' },
    rationale: { type: 'string' },
    grafts: {
      type: 'array', maxItems: 3,
      items: {
        type: 'object',
        properties: { cut: { type: 'string' }, add: { type: 'string' }, why: { type: 'string' } },
        required: ['cut', 'add', 'why'], additionalProperties: false,
      },
    },
    final_main: { type: 'array', items: CARD },
    final_lands: { type: 'array', items: CARD },
    contested: {
      type: 'array', minItems: 2, maxItems: 4,
      items: {
        type: 'object',
        properties: { slot: { type: 'string' }, alternative: { type: 'string' }, tradeoff: { type: 'string' } },
        required: ['slot', 'alternative', 'tradeoff'], additionalProperties: false,
      },
    },
    convergence_note: { type: 'string' },
  },
  required: ['winner', 'rationale', 'grafts', 'final_main', 'final_lands', 'contested', 'convergence_note'],
  additionalProperties: false,
}

function judgePrompt(a, builds) {
  const cands = builds.map((b, i) => {
    const list = b.main.map(c => `${c.n} ${c.name}`).join('\n')
    const lands = b.lands.map(c => `${c.n} ${c.name}`).join('\n')
    return `=== КАНДИДАТ ${i + 1} «${b.lane}» ===\nПлан строителя: ${b.plan}\nФлекс строителя: ${(b.flex || []).join(' · ')}\nМейн:\n${list}\nЗемли:\n${lands}`
  }).join('\n\n')
  return `Ты — судья оркестрированной сборки лимитед-колоды MTG Arena (сет ${a.set.toUpperCase()}, Premier Bo1, пара ${a.pair}). Кандидаты собраны строителями по взаимоисключающим линиям.

ПРИОР РЕШЕНИЯ (зашит, не обсуждается):
1. При прочих равных побеждает КАЧЕСТВО КАРТ: средний GIH мейна и тест «отдано к жадному» (норма победителей +0.49/карту, максимум популяции +0.96; больше — «план дороже качества карт», меньше +0.2 — «плана нет»).
2. Жертва качества допустима только за (а) ось НИЖЕ ВСЕЙ популяции пары в аудите или (б) явное обязательство линии; размер — в норме популяции.
3. Роль (removal/закрывашка) не режется ради метрики; тело силой ≥4 меняется только на тело ≥4 или removal.
4. Запрещено ссылаться на правила, которых нет в этих материалах и в выводах скриптов.
5. Гибрид = каркас ПОБЕДИТЕЛЯ + 0–3 графта слот-в-слот с причиной; графт не роняет маршруты победителя и не тащит в мейн половину анти-связки его плана. Смешивать планы нельзя.
6. Кандидаты сошлись — сказать прямо.

ПОРЯДОК РАБОТЫ — ОБЯЗАТЕЛЬНЫЙ, числа только из выводов команд (не по памяти):
1. Запиши каждый мейн+земли в файл ${a.outDir}/cand_<номер>.txt в формате MTGA («Deck», затем «N Имя» построчно, земли в конце).
2. По каждому файлу прогони и прочитай вывод:
   cd ${SKILL} && python3 build_audit.py <файл> --pool pools/${a.set}_${a.draft8}.txt --set ${a.set}
   python3 ${SKILL}/pool_dossier.py <файл> --set ${a.set} --deck ${a.pair}
   python3 ${SKILL}/draft_goldfish.py <файл> 8000 | tail -14
3. Сравни по приору, примени 0–3 графта (после графта — перепрогони скорборд финала), выдай финальные 23+17 и 2–4 реально спорных слота с ценой альтернативы.
Другие файлы скилла (журнал, матч-логи, чужие листы) НЕ читай.

=== МЕДИАНЫ ПОБЕДИТЕЛЕЙ ПАРЫ ${a.pair} ===
${a.medians}

=== ДОСЬЕ ПУЛА ===
${a.dossier}

${cands}

Верни строго JSON по схеме.`
}

const a = args
if (!a || !a.pool || !a.dossier) throw new Error('нужны args: {set, draft8, pair, pool, dossier, medians}')

let design
if (a.lanes && a.lanes.length) {
  design = { mode: a.lanes.length > 1 ? 'fan' : 'single', rationale: 'линии заданы сессией по досье', lanes: a.lanes }
  log(`линии от сессии: ${a.lanes.map(l => l.name).join(' · ')}`)
} else {
  phase('Линии')
  log(`проектирую линии для ${a.set}/${a.draft8} (${a.pair})`)
  design = await agent(laneDesignerPrompt(a), {
    ...J_MODEL, label: `lanes:${a.draft8}`, phase: 'Линии', schema: LANES_SCHEMA,
  })
  if (!design) throw new Error('проектировщик линий не вернул результат')
}
const lanes = design.mode === 'single' ? design.lanes.slice(0, 1)
  : design.lanes.slice(0, a.maxLanes || 3)
log(`режим ${design.mode}: ${lanes.map(l => l.name).join(' · ')}`)

phase('Сборка')
const builds = (await parallel(lanes.map(lane => () =>
  agent(builderPrompt(a, lane), {
    ...B_MODEL, label: `build:${lane.name.slice(0, 18)}`, phase: 'Сборка', schema: BUILD_SCHEMA,
  }).then(b => b && { lane: lane.name, ...b })))).filter(Boolean)

if (a.judge === false || !builds.length) return { design, builds }
if (!a.outDir) throw new Error('для судьи нужен args.outDir (куда писать кандидатов)')

phase('Судья')
const verdict = await agent(judgePrompt(a, builds), {
  ...J_MODEL, label: `judge:${a.draft8}`, phase: 'Судья', schema: JUDGE_SCHEMA,
})
return { design, builds, verdict }
