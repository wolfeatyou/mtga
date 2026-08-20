export const meta = {
  name: 'orchestrated-build',
  description: 'Оркестрированная сборка лимитед-колоды: линии из досье → веер строителей',
  whenToUse: 'mode_build.md § МУЛЬТИСБОРКА: после DRAFT COMPLETE, вход — пул + досье pool_dossier.py',
  phases: [
    { title: 'Линии', detail: 'проектировщик читает досье, решает веер/одиночку, пишет брифы' },
    { title: 'Сборка', detail: 'по строителю на линию, каждый: constraint=линия, objective=качество карт' },
  ],
}

// args: {set, draft8, pair, pool, dossier, medians, maxLanes}
//   pool/dossier — текст файлов; medians — строка с медианами routes пары.
// Возвращает {lanes, builds}. Судья НЕ здесь: скорборды считаются скриптами между
// этапами (build_audit/goldfish/sig_of), судья — отдельный агент после них.
// Модель пришпилена к opus/high: боевая конфигурация сборки (SKILL.md хард-рул 3),
// и тест инструмента обязан идти на ней же (указание пользователя 17.08).

const MODEL = { model: 'opus', effort: 'high' }

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

const a = args
if (!a || !a.pool || !a.dossier) throw new Error('нужны args: {set, draft8, pair, pool, dossier, medians}')

phase('Линии')
log(`проектирую линии для ${a.set}/${a.draft8} (${a.pair})`)
const design = await agent(laneDesignerPrompt(a), {
  ...MODEL, label: `lanes:${a.draft8}`, phase: 'Линии', schema: LANES_SCHEMA,
})
if (!design) throw new Error('проектировщик линий не вернул результат')
const lanes = design.mode === 'single' ? design.lanes.slice(0, 1)
  : design.lanes.slice(0, a.maxLanes || 3)
log(`режим ${design.mode}: ${lanes.map(l => l.name).join(' · ')}`)

phase('Сборка')
const builds = await parallel(lanes.map(lane => () =>
  agent(builderPrompt(a, lane), {
    ...MODEL, label: `build:${lane.name.slice(0, 18)}`, phase: 'Сборка', schema: BUILD_SCHEMA,
  }).then(b => b && { lane: lane.name, ...b })))

return { design, builds: builds.filter(Boolean) }
