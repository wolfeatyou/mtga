# SOS Draft #1 — UR Spellslinger (контроль/темп)

draftId 689b0ddf · пул восстановлен по логам (34 карты; ~5-8 пиков потеряны на обрыве связи в буст.3)

## Основа (40 карт)

### Существа (10)
- Sanar, Unfinished Genius {U}{R} — 0/4 + спелл
- Expressive Firedancer {1}{R} — opus-пейофф 2/2
- Goblin Glasswright {R}… — 2-дроп
- Page, Loose Leaf {2} — 0/2 стена
- Matterbending Mage {2}{U} ×2 — баунс-ETB
- Elemental Mascot {1}{U}{R} — 1/4
- Textbook Tabulator {2}{U} — 0/3 стена
- Sundering Archaic {6} — 3/3, exile-removal на входе
- Transcendent Archaic {7} — 6/6, добор (финишер)

### Не-существа (13)
- Divergent Equation {X}{X}{U} — возврат спеллов
- Mathemagics {X}{X}{U}{U} — движок добора ⭐
- Essence Scatter {1}{U} ×2 — контрспелл
- Banishing Betrayal {1}{U} ×2 — баунс+surveil
- Prismari Charm {U}{R} — гибкий инстант ⭐
- Seize the Spoils {2}{R} — добор+треже
- Potioner's Trove {3} — рамп/фикс
- Artistic Process {3}{R}{R} — 6 урона / removal ⭐
- Splatter Technique {1}{U}{U}{R}{R} — свип+добор, бомба ⭐⭐
- Duel Tactics {R} — дешёвое removal + flashback (2 триггера)
- Run Behind {3}{U} — темп/псевдо-removal

### Земли (17)
- Stormcarved Coast (UR-дуал)
- 9 Island · 7 Mountain
+ Potioner's Trove как 18-й источник (фикс любой)

## Сайдборд (не в основе)
Run Behind ×2, Essence Scatter ×2, Spell Pierce, Stargaze,
Ancestral Anger, Encouraging Aviator, Borrowed Knowledge (вне цвета — RW).

## Честная оценка: B-/C+
- **Сила:** карточное преимущество (Mathemagics, Splatter, Divergent), Splatter как свип,
  два «архаика»-финишера, плотная синяя интеракция.
- **Слабость:** мало проактивных тел (реальных угроз ~7, остальное — стены 0/x),
  удаление по существам жидковатое (Artistic, Splatter, Duel, Run Behind, баунс — темп, не чистый kill).
  Уязвимы к быстрому агро.
- **План на игру:** доживать стенами/баунсом/контрами → Splatter ровняет борд →
  Mathemagics/Divergent закапывают в картах → Transcendent/Sundering добивают.

## Урок драфта (по моей же критике)
Перебрал реактив (4× Essence Scatter, 3× Run Behind) в погоне за on-color GIH,
недобрал существа. В след. раз: при равном GIH — тело важнее N-го контрспелла.

---

# SOS Draft #2 — WB Silverquill (агро-мидрейндж)

draftId 7acfadc9 · полный драфт (42 карты), пул трекался вживую через `draft_live.py watch`.

## Основа (40 карт)

### Существа (14)
- Elite Interceptor ×3 `{W}` — 1-дроп + flashback-сорсери, темпо-каркас ⭐
- Inkling Mascot `{W}{B}` — летун (evasion)
- Soaring Stoneglider `{2}{W}` — летун
- Owlin Historian `{2}{W}`
- Rehearsed Debater ×2 `{2}{W}`
- Abigale, Poet Laureate `{1}{W}{B}` — легендарка-вэлью, сигнпост Silverquill ⭐
- Grave Researcher `{2}{B}` — 3/3, surveil + реанимация
- Eager Glyphmage `{3}{W}` — топ-W коммон
- Inkshape Demonstrator `{3}{W}`
- Honorbound Page ×2 `{3}{W}` — first strike + гибкий {W}-спелл (Forum's Favor)

### Не-существа (9)
- **Moment of Reckoning** `{3}{W}{W}{B}{B}` — бомба, A+ (GIH 63.4) ⭐⭐
- End of the Hunt `{1}{B}` — removal ⭐
- Wander Off `{3}{B}` — removal
- Dissection Practice `{B}` — removal
- Cost of Brilliance `{2}{B}` — removal + добор
- Hop to It `{W}` — делает тела, GIH 55.4
- Dig Site Inventory `{W}` — дешёвое вэлью
- Group Project `{1}{W}` — токены/вэлью
- Interjection `{W}` — единственный трюк/интеракция (55.8)

### Земли (17)
- Forum of Amity (дуал-фикс)
- 9 Plains · 7 Swamp
  (белый — основной цвет; 7 Swamp + Forum держат BB под Moment of Reckoning)

## Правки после сверки с Untapped (90% совпало, та же мана-база)
Untapped независимо собрал ту же базу; честно поймал 2 мои переоценки — внёс:
- **Arcane Omens → в сайд.** Это **Converge**: дискард = число цветов маны. В 2-цветном WB X=2 («дискард 2 за 5») — слабо; GIH 59.7 раздут converge-супами. Я повёлся на голый рейтинг.
- **Page, Loose Leaf → Hop to It.** У Page мёртв Grandeur (нужна 2-я копия); Hop to It в цвет и делает тела (55.4 > 52.7).
- **Держу оборону:** 2-й Honorbound Page (тело + first strike) вместо Rapier Wit (2-й трюк). По уроку #1: тело > N-го реактива; Untapped гонял Rapier Wit *и* Interjection — перебор реактива. Оставил один Interjection.

## Сайдборд / флекс
- Arcane Omens `{4}{B}` — главный SB-ин против контроля/гриндовых матчапов (дискард-2)
- Rapier Wit `{1}{W}`, Page, Loose Leaf `{2}`, Primary Research `{4}{W}`, Biblioplex Tomekeeper `{4}` — флекс-подмены
- **Red-сплеш** (если найдёшь фикс): Wilt in the Heat ×2 `{2}{R}{W}` (removal), Pursue the Past `{R}{W}`, Kirol `{R}{W}` — мини-сплеш на доп. removal/вэлью
- Вне цвета (не в составе): Rapturous Moment, Pterafractyl, Sleight of Hand, Rearing Embermare, Maelstrom Artisan, Zombify, Duty Beyond Death

## Честная оценка: B+/A-
- **Сила:** проактивный темпо-каркас (3× Elite Interceptor), **5 removal** (End of the Hunt, Wander Off, Dissection, Cost of Brilliance + свип Moment), evasion (2 летуна), A+ бомба, вэлью-хвост (Arcane Omens, Dig Site, Abigale).
- **Слабость:** кривая верхотяжёлая (много 3-4 cmc), существ всего ~15 (на грани, можно добить 16-м). Moment of Reckoning по пипам тяжёлый (WWBB) — без аккуратной маны застрянет.
- **План на игру:** ранний прессинг 1-2-дропами и летунами → removal расчищает блокеров → Moment of Reckoning ровняет/ломает борд при стопоре → Arcane Omens/Abigale закапывают в вэлью.

## Урок учтён (из #1)
Прошлый дек перебрал реактив и недобрал тел. Здесь сознательно: на P1P5 взял
Soaring Stoneglider (летун) вместо 4-го removal — тело важнее N-го реактива.
Сигналы прочитаны верно: **чёрное removal текло весь драфт** (End of the Hunt,
Dissection, Wander Off, Cost of Brilliance закрутились) — B был открыт, не ушёл из пары.
