<!-- Автогенерация: мультиагентный разбор 298 трофейных колод HOB (17.08.2026).
     Порядок: статистика нашла кандидатов (пары карт с повышенной совстречаемостью),
     10 агентов объяснили механизм по оракл-текстам, 4 скептика опровергали.
     221 заявлено → 110 подтверждено. Машиночитаемые связки — hob_combos.json,
     их печатает ⚑СВЯЗКА и ⚑ОПОРА в живом драфте. -->

# HOB — что делают победители (298 трофейных колод)

> Источник: разбор трофейных колод (gold+platinum, untapped). Проверено скептиком 64 утверждения: 31 CONFIRMED, 24 WEAK, 9 REFUTED (выброшены). Всё ниже — из данных; противоречия названы прямо.
> **Как читать в пике:** сначала «Сквозные закономерности» → потом блок своей пары → таблицу связок использовать как проверку, а не как план.

---

## Сквозные закономерности

Только то, что видно минимум в двух парах.

1. **Утилитарная земля пары = карта в кривой, а не фиксер.** Elvenking's Halls 32/44 (UG), Iron Hills 30/39 (WR), Goblin-town 27/43 (BR, из них 12 листов с ДВУМЯ копиями), Mirkwood 25/35 (BG). Все четыре: сак земли → **два +1/+1 счётчика** на трайб пары (Эльф / Дворф / Гоблин-Орк / Медведь-Паук-Волк). Входит в 17 земель, слот спелла не занимает → бери вместо 22–23-й играбельной.
2. **17 земель — норма, 18 не встретилось ни разу.** BG: 29/35 листов по 17, 6/35 по 16. UG-медиана 17 (~7 Forest, ~6 Island, ~4 небазовых). Утилитарные земли считаются ВНУТРИ этих 17 (BG: 32/35 держат минимум одну).
3. **Amass всегда складывается в ОДНУ Армию и требует разносчика.** Пары BR, WR, BG, UR. Goblin Plate Mail сам амассит и сам цепляется к получившейся Армии (+1/+0, menace) без оплаты Equip {4}. BG: 12 из 13 листов с Plate Mail держат второй источник amass. Куча счётчиков без menace не выигрывает.
4. **Ferocious — это два разных требования: пейоффы и включатели.** BG: 34/35 листов держат ≥1 пейофф (медиана 3), и у ВСЕХ 25 листов с 3+ пейоффами есть ≥5 тел силы 4+ (медиана 7, исключений нет). BR: в листах с Ferocious тел 4+ в среднем 5.8, без — 4.8. Самый дешёвый подтверждённый включатель во всех парах — **Duskwatch Hunter** (счётчик на себя = 4/2 за 3 маны, CONFIRMED в BR и моно-B).
5. **Storied включается сам.** В 9 UR-листах с Óin квалифицирующих артефактов/легенд/саг 6, 6, 7, 8, 9, 9, 9, 11, 12; медиана WR — 14. Пик строй вокруг ВЫПЛАТЫ (Bifur, Bombur, Fíli), а не вокруг «наберу три перманента». Порог ~10 из правил WR данные подтверждают только для WR-листов.
6. **Hobbit Hole — общий тьютор халфлинга и общая ловушка.** Тип-замок подтверждён в WU (7/7 листов с Hobbit Hole держат Bilbo, Luckwearer), WB (5/6 держат халфлинга, в 4 — Gollum), моно; в BR лежит с Gollum'ом в 13 листах. Но карта **не даёт маны вообще** (нет «{T}: Add») и попадает в антисинергии: с Nori (WR, 2 при ожидании 5.3), с Wood Elves (BG, 2/35 при 3.6).
7. **У каждой пары ровно две ветки, и они не смешиваются.** UG эльфы/синий темп (Weavemaster+Nuisance 1 из 45 при ожидании 5), WR белый эквип-го-вайд 22 листа / красный амасс-топэнд 17 (Blacksmith+Raider 1/39 при 4.5), BR чёрный ремувал / красный сак (Gnashing+Snowslope 0 при 12 и 12 листах по отдельности), BG зелёные медведи / чёрное амасс-темпо (Beorn+Stony-Voiced 1/35 при 3.4). **Ветку фиксируй к P2.**
8. **Сплэш ровно один и взаимоисключающий.** BR: Forest 16 листов, Plains 10, вместе — 1 (lift 0.28).
9. **Существ минимум 10, медиана 14–16.** BR: медиана 14, min 10 («ниже 10 amass-план не работает — некого экипировать и нечего сакать»). UG-скелет: 16 существ.
10. **Removal-медиана 4–5 карт, но UG — исключение: безусловного removal в паре нет вообще.** BR медиана 5 (min 2, max 10), WR 4–5 (Magnificent End 28/39, Pinecone Strike 24, Stone by Sunlight 19), BG безусловные — Bilbo's Deadly Slice 19/35 + Stir Up Trouble. В UG единственный ответ на бомбу — аура Enchanted River's Grasp (33/44).

---

## Связки, которые меняют пик

Только CONFIRMED, по убыванию числа колод.

| Связка | Механизм (из текста карт) | Колод | Тип |
|---|---|---|---|
| Attercop + Quarrel | Quarrel бьёт «урон = сила», без ответки; Attercop — **единственный deathtouch в G/U** сета → убийство любого тела за {1}{G} | UG 22, BG 17, RG ✓ | механика |
| Wood Elves + Thranduil, Sindarin Liege | Forest выходит НА ПОЛЕ = вторая земля за ход → landfall-токен; Wood Elves сам Elf Scout под анкем | UG 19 | механика |
| Hobbit Hole + халфлинг (Gollum / Bilbo, Luckwearer) | Halflingcycling {4} тьюторит «a Halfling card»; лишняя земля → тело | BR 13, WU 7/7, WB 5/6, моно ✓ | роль |
| Goblin Plate Mail + Rage into the Valley | Plate Mail цепляется к амассенной Армии; Rage кладёт на неё же +2 → menace-угроза без Equip {4} | BR 14 | механика |
| Thranduil, Sindarin Liege + Woodland Weavemaster | Анкем делает Weavemaster 2/3 (мана = сила); landfall-токен — тоже Elf → ещё +1/+1 до конца хода | UG 14 | механика |
| Lakeshore Apothecary + Plunder the Trollshaws | Plunder — инстант: добор = вторая карта за ход → счётчик; flashback тянет ДВЕ и триггерит в чужой ход | UG 12 | механика |
| Duskwatch Hunter + Ravening Warg | ETB-счётчик на СЕБЯ → перманентные 4/2 на 3-м ходу = включатель Ferocious без карты и без пампа | BR 11 | механика |
| Dwarven Mattock + Iron Hills Stalwart | ETB Stalwart бесплатно вешает Mattock (Equip {3}): 4/5 reach trample → 6/7 ward {1} | WR 9 | механика |
| Lakeshore Apothecary + Bilbo, Luckwearer | «Bilbo can't be blocked» → каждый бой лут = вторая карта за ход → +1/+1. Обе по {1}{U} | UG 8, WU ✓ | механика |
| Cantankerous Keepers + Woodland Weavemaster | Keepers — Elf Soldier: мана Weavemaster'а его законно кастует, и сам Weavemaster режет Affinity на {1}. Реальный ход выхода — 4-й, не 3-й | UG 7 | мана |
| Kíli the Resourceful + Iron Hills Blacksmith | Blacksmith — Дворф, чей ETB делает Axe-эквип; «{0} вместо equip cost» оплачивает equip {2}. **Кили тянет ОДНУ карту, не две** («triggers only once each turn») | WR 7 | механика |
| Attercop + Boughside Wanderers + Hobbit Hole | Сак Hobbit Hole в инстант-скорость = landfall в бою: 3/2 deathtouch + 6/6 одной землёй | UG 7 | механика |
| Stir Up Trouble + Part in Friendship | Доп-стоимость «sacrifice a creature» буквально триггерит «whenever a nontoken creature you control dies» → минус превращается в тело с верха. Жертвовать надо НЕТОКЕН; тело выходит, только если MV ≤ числа земель; раз в ход | BG 3 | механика |
| Master's Councillors + Plunder the Trollshaws | «Draw a card» = вторая карта за ход → милл 3; flashback {3}{U} = второй такой триггер той же картой; самомилл набивает порог «seven or more cards» | UB ✓, UR ✓ | механика |
| Long Lake Nuisance + Master's Councillors | ETB recruit: дро (вторая карта) + сброс + милл 3 = 4 карты в ГЯ за один ETB; милить можно и себя, и оппонента | UB ✓ | механика |
| Desolation Prowler + Ravening Warg | «Pay 2 life: +2/+2» (раз в ход) = 4/4 в инстант-скорость до объявления атак → Ferocious возвращает ровно эти 2 жизни. Ноль маны, повтор каждый ход | UB ✓ | механика |
| Goblin Plate Mail + Tidings of War | Тот же замок «одна Армия»: Tidings амассит её дважды за карту (флэшбэк {3}{R}) при уже висящем menace | UR ✓ | механика |
| Bothersome Noisemaker + Tidings of War | Sorcery → триггер Noisemaker (amass 1) + собственный amass 1 = 2 счётчика за {R}; флэшбэк даёт ещё 4 | RG ✓ | механика |
| Galion, Elvenking's Butler + Wargling | Galion задаёт базовые 4/4 и сам включает Ferocious → Wargling 5/4 + **трампл всей команде**, и сам становится включателем для других | RG ✓ | механика |
| The Lonely Mountain + любой эквип | Земля выходит РАЗВЯЗАННОЙ при эквипе и дешевеет на {1} за каждый: при 3 эквипах {4}{R} → {1}{R}. Оговорка: три эквипа на столе редки (в листах их 1–3 в КОЛОДЕ) | RG ✓ | механика |
| Óin the Brave + артефакты/легенды/саги | Storied буквально называет типы → +1/+0 и haste; основная ценность карты всё равно луталка | UR 9 листов | роль |
| Stir Up Trouble + Dreaded Bat-Cloud | Stir Up за {B} гарантирует смерть в этот ход → Bat-Cloud 4/2 flying deathtouch за {1}{B} | моно ✓, BR 8 | механика |
| Duskwatch Hunter + Nighthowl Pursuer | 3/1 → 4/2 счётчиком на себя → Pursuer 3/3 menace за {B}. Самый дешёвый включатель в моно-B (остальные 4+ силы: Gollum 4, Head of the Hunt 4, Bat-Cloud 5, Great Ugly 6) | моно ✓ | механика |
| Beorn the Fierce + Attercop | Trample-счётчик + «становится Bear» + анкем «Other Bears +2/+2» → 4/3 reach + deathtouch + trample (по 1 урона блокерам, остальное в игрока) | моно ✓ | механика |
| Great Gilded Boat + Master's Councillors | «Whenever you attack» — триггер перманента: срабатывает **даже без крюя**; recruit = вторая карта → милл 3 каждый ход | моно ✓ | механика |
| Eagle's Rescue + Patient Instructor | Recruit даёт и дискард-аутлет, и 1/1 Soldier — единственного законного носителя под возврат «attached to target creature with power 1 or less»; токен становится 3/3 летуном. Возврат в скорости сорцери | моно ✓ | механика |
| The Lord of the Eagles + Long Lake Nuisance | «Costs {X} less, X = суммарная сила летающих»: Nuisance 3/1 → −3 генерики. Все 3 WU-листа с Лордом играют Nuisance (2–4 копии) | WU 3/3 | мана |

### WEAK — знать, но пик не двигать

| Связка | Пара | Почему не решает |
|---|---|---|
| Hobbit Hole + Attercop (одиночный) | UG/RG | +1/+1 на один ход ценой сака земли; при deathtouch лишняя СИЛА почти бесполезна. С ДВУМЯ landfall-телами — уже CONFIRMED |
| Beorn's Hospitality + Woodland Weavemaster | UG | Мана Weavemaster'а только на Elf-спеллы; «+1 мана навсегда» оверселл |
| Silvan Reveler + Plunder | UG | ETB сбрасывает РОВНО ОДНУ карту: земля-из-ГЯ и сброс Plunder взаимоисключающи |
| Lakeshore Apothecary + Long Lake Nuisance / Patient Instructor | UG | Один ETB = один счётчик; счётчик ложится на самого Apothecary (1/2, без полёта) |
| Mirkwood Nurturer + Thranduil's Company | UG | Лишний лендроп тратится на переигранную землю вместо земли с руки |
| Gollum + Ravening Warg | BR | Подходит любое тело 4+; выплата Warg — «gain 2 life» |
| Dori + Stir Up Trouble | BR | Корм — ЛЮБОЙ артефакт или существо, они есть в каждой чёрной колоде |
| Burn, Burn, Tree and Fern + Óin | BR | Один из 6–12 квалифицирующих перманентов; мана раз в ход |
| Iron Hills + Dwarven Shortsword | WR | Цель-Дворф есть всегда; {2}{R}{W} + сак = поздний мана-синк, не причина брать Shortsword |
| Crude Bent Blade + Ravening Warg | BG | 5 маны до первой атаки ({2}{B} + Equip {2}) против 3 у Duskwatch Hunter |
| Great Ugly-Looking Goblin + Nasty Little Rabbit | BG | 6 маны; menace носит собственная Армия Гоблина от Clap! Snap! |
| Dreaded Bat-Cloud + Nasty Little Rabbit | BG | Включатель — любое 4-силовое тело; скидка требует уже случившейся смерти |
| Stir Up Trouble + Stony-Voiced Goblins / Iron Hills Blacksmith / «токены и эквипы» | UB/WB | Доп-стоимость платится ЛЮБЫМ артефактом или существом — признак выполняется в 100% листов |
| Bofur + Dáin, Lord of the Iron Hills | WU | Storied считает любые артефакты/легенды/саги; защита — любому своему перманенту |
| Dáin, Lord of the Iron Hills + Stone by Sunlight | WB | Трюк законен (тип «артефакт» защёлкивает Storied навсегда), но нужен ровно счёт 2 и трата ремувала |
| Nori + Rhovanion Rampager / Óin | WB/RG | First strike даётся ЛЮБОМУ атакующему; на 2/3 Óin прибавка почти нулевая |
| Great Gilded Boat + Patient Instructor | UR | **1/1 не крюит Crew 2**; Лодка триггерит и без крюя — рамка «крюй» лишняя |
| Enchanted River's Grasp + Mirkwood Nurturer | UR | Одноразовая тактическая опция, перевес стоит ещё {2}{U} |
| Thranduil's Company + Gigantic Big Bear | моно | Родовой рамп, выигрыш максимум один ход |

### Не проверялись скептиком (держать как гипотезы, не как правила)

Частые в данных, но без вердикта: Bothersome Noisemaker + Rage into the Valley (BR 18), Iron Hills + Dwarven Shortsword-пакет (WR 18), Goblin-town + Goblin Plate Mail (BR 16), Mirkwood + Ravening Warg (BG 13), Elvenking's Halls + Weavemaster (UG 11), Bifur + Fíli + Glóin (WR 6 при ожидании 1.5), Gandalf + Smaug (WR 10), Dwarven Mauler + Crude Bent Blade (BR 8/8 листов), Dáin Ironfoot + Dáin's Company (WR 8).

---

## Антисинергии

Раздел, которого не было в прошлом разборе. Числа — «листов вместе / ожидание».

**Тип 1. Разные ветки одной пары (самые жёсткие числа).**
- Woodland Weavemaster ↔ Long Lake Nuisance / Patient Instructor — **1 из 45 при ожидании 5** (UG). Листы с Weavemaster держат ~12 эльфов, с Nuisance ~4.
- Iron Hills Blacksmith ↔ Misty Mountains Raider — **1 из 39 при 4.5** (WR). Raider — Гоблин, эквип-пейоффы (Кили, Mattock «target Dwarf», Iron Hills) его физически не видят.
- Gnashing of Teeth ↔ Snowslope Hunter — по 12 листов каждая, **вместе 0** (BR). {B}{B}-ремувальный список против красной сак-ветки.
- Beorn, Reluctant Host ↔ Stony-Voiced Goblins — 1 из 35 при 3.4 (BG).
- Gandalf, Spark Starter ↔ Dáin Ironfoot — 1 из ~4 (WR). Гэндальф бежит от всего белого пакета: с Shortsword 4 при 8, с Blacksmith 3 при 5.3, с Mattock 4 при 5.7 — и склеивается со Smaug (10 при 6).

**Тип 2. Два чистых пейоффа без включателя.**
- Wargling ↔ Wilderland Scrounger — 4 из 35 при 6.9 (BG): 2/2 и 3/6, ни один сам не даёт силу 4.
- Nasty Little Rabbit ↔ Thranduil — 2 из 45 при 7 (UG): токены 1/1 (2/2 под анкемом) не включают Ferocious.
- Great Ugly-Looking Goblin ↔ Tidings of War — 2 из 33 при 3.5 (BR): один и тот же слот «дешёвый спелл, дающий только счётчики и ни одного тела».

**Тип 3. Дублирование эффекта.**
- Elvenking's Harper ↔ Old Fat Spider — 2 из 45 при 5 (UG): у паука уже «can't be blocked by creatures with power 2 or less».
- Old Fat Spider ↔ Goblin Plate Mail — 1 из 35 при 3.3 (BG): menace ему не нужен, Equip {4} конкурирует с кастом шестидропки.
- Hobbit Hole ↔ Wood Elves — 2 из 35 при 3.6 (BG): обе тащат бэйсик в игру.
- An Unexpected Party ↔ Fíli the Pathfinder — 1 из ~3 (WR): два белых четырёхдроп-анкема.

**Тип 4. План против плана.**
- Stir Up Trouble ↔ Large Bear — **0 из 35 при 2.8** (BG; с Boughside Wanderers тоже 0, с Ordinary Bear 2 при 4.4): жертва толстяка выключает собственный Ferocious.
- Galion ↔ Ordinary Bear — **0 из 45 при 2** (UG): Galion ставит БАЗОВЫЕ 4/4, то есть 4/5 он уменьшает.
- Dwarven Provisioner ↔ Dáin, Lord of the Iron Hills — 5 из ~8.6 (WR): оба {1}{W} 2/2, но один — слив маны в атаку, второй — оборонительный тэкс.
- Bothersome Noisemaker ↔ Front Porch Sentries — 1 при 22 и 10 листах (BR): существо не даёт Noisemaker ни одного триггера, и обе дерутся за слот двойки.

**Тип 5. Мана.**
- Forest ↔ Plains в BR — 1 при 16 и 10 (сплэш ровно один).
- Nori ↔ Hobbit Hole — 2 при 5.3 (WR): гибридная двойка не может позволить землю, которая не кастует ничего.
- Ordinary Bear ↔ Thranduil — 1 из 45 при 6 (UG): ванильный не-эльф пролетает мимо анкема, маны Weavemaster'а, счётчиков Halls и affinity Keepers.

---

## Движки по цветам

**Бесплатные (не требуют маны на срабатывание) — приоритетнее при равном GIH:**

| Пара | Карта | Что делает |
|---|---|---|
| UG | Thranduil, Sindarin Liege | Каждая земля = 1/1 Elf, под собственным анкемом сразу 2/2 |
| UG | Thranduil's Company | Лишний лендроп КАЖДЫЙ ход (при другом эльфе) → два landfall-триггера за ход |
| UG | Beorn's Hospitality | Каждая земля = ПОСТОЯННЫЙ +1/+1 на любое своё существо |
| UG | Lakeshore Apothecary | Растёт на каждой второй карте за ход; vigilance |
| UG | Bilbo, Luckwearer | Неблокируем; каждый боевой урон = draw+discard |
| UG/UR | Great Gilded Boat | «Whenever you attack, recruit» — триггер перманента, **работает без крюя** |
| UG | Down in the Valley / Old Fat Spider | Сага на 4 главы; ремувал по Spider всегда размен на карту |
| BR/WR | Misty Mountains Raider | Amass 2 при каждой атаке в ту же Армию |
| BR/WR | Bothersome Noisemaker | Amass 1 на каждый НЕкреатурный спелл (эквип, ремувал, саги — да; существа — нет) |
| BR | Head of the Hunt | Каждая смерть существа оппонента → изгнание + твой 2/2 Волк |
| BR/BG | Chief Warg's Company | 2/2 Волк каждый апкип; сама набирает себе «двух других Волков» |
| BR | The Great Goblin | Любые счётчики на Гоблина/Орка/Армию = 2 урона оппоненту |
| BR/BG | Down, Down to Goblin-town | Сага: дискард → amass 1 → 2× дрейн |
| BR | Snowslope Hunter | Сак существа/артефакта → изгнать топ и сыграть; активация без маны |
| BR | The Misty Mountains Cold | Treasure каждый ход, на четвёртом — 6/6 дракон |
| WR | Bifur, Melodic Rider | С историей УДВАИВАЕТ любой триггер Дворфа (токены Фили, Treasure Дори, Axe, мана Глоина) |
| WR | Glóin the Mighty | {R}{R} в начале первой главной = оплаченный эквип каждый ход (эквип — скорость сорцери) |
| WR | Kíli the Resourceful | Карта за выход Дворфа ИЛИ эквипа — **раз в ход**; с историей первый эквип за {0} |
| WR | Fíli the Pathfinder | 2/2 Дворф на каждый нетокеновый Дворф + анкем +1/+1 с историей |
| WR | Dáin Ironfoot | Каждая его атака = двойной удар ВСЕМ экипированным атакующим |
| WR | Dwalin, Weaponmaster | Выход и каждая атака = постоянный hone-счётчик на КАЖДЫЙ эквип |
| BG | The Chief Warg (19/35) | При ЛЮБОЙ атаке при теле 4+ — карта за 1 жизнь. Главный мотор пары |
| BG | Wilderland Scrounger (16/35) | При атаке (при теле 4+) — +1/+1 счётчик на КАЖДОЕ своё существо |
| BG/UB | Desolation Prowler | «Pay 2 life: +2/+2», раз в ход, ноль маны — дешевейший повторяемый доступ к силе 4 |
| BG | Bejeweled Warg | Урон игроку → счётчик на Волка ИЛИ Treasure |
| BG | Part in Friendship | Смерть нетокенного существа → существо с верха в игру (раз в ход, MV ≤ числу земель) |

**С затратами маны (мана-синки, не бесплатные движки):** Óin the Brave ({1},{T}, сброс: карта — BR/WR/UR), Goblin-town / Elvenking's Halls / Iron Hills / Mirkwood (сак земли), The Lonely Mountain ({4}{R} минус {1} за эквип), Dwarven Provisioner ({3}{W} команде +1/+1), Guardian of the Halls ({5}{G}{G} три счётчика), Silvan Reveler ({1}{G}{U} выкуп из ГЯ), Tom, Bert, and William ({1} + сак).

⚠️ **Nasty Little Rabbit числится в разборе BG «бесплатным движком, растущим каждый бой» — это ошибка разбора.** Полный текст: «Ferocious — At the beginning of combat on your turn, **if you control a creature with power 4 or greater**, put a +1/+1 counter on this creature». Без стороннего тела 4+ он не растёт вообще.

⚠️ **Woodland Weavemaster — не рамп.** «Spend this mana only to cast Elf spells and activate abilities of Elf sources»: Beorn, Old Fat Spider, Ordinary Bear, Large Bear она не кастует.

---

## По парам

### UG — landfall + эльфы (n=44)
**План:** лишние выходы земель (Wood Elves, Hobbit Hole, Thranduil's Company, Till and Tend) конвертируются в эльфов-токены, постоянные счётчики и ману; хардремувала нет — бомбу выключает Enchanted River's Grasp, добивает эвазия.
1. Скелет: 17 земель (~7 Forest, ~6 Island, ~4 небазовых), 16 существ, 5 landfall-пейоффов, 3 источника лишней земли.
2. **К P2 выбери ветку:** ЭЛЬФЫ (10–12 эльфов: Weavemaster, Thranduil, Keepers, Galion, Elvenking's Halls) ИЛИ СИНИЙ ТЕМП (~5 эльфов: Apothecary, Nuisance, Instructor, Bilbo). Смешанных листов практически нет.
3. **Grasp — бери два** (33/44): единственный ответ на бомбу. Quarrel и Troll Negotiations — файт (нужны тела), Warg Tactics — только по летающим, Uneasy Partings — tuck.
4. Attercop ↔ Quarrel: взял одно — приоритет второму (22 листа). Attercop — единственный deathtouch в G/U.
5. Wood Elves ищет именно «Forest card»: Halls и Mirkwood не подходят, держи ≥6 базовых лесов. Cantankerous Keepers без ~10 эльфов не берём (все 8 листов с ним — эльфовые, в среднем 12 эльфов).

### BR — amass + дешёвые тела (n=43)
**План:** дешёвая кривая + amass в одну Армию, menace от Goblin Plate Mail / Great Ugly-Looking Goblin, плотный removal расчищает атаку.
1. **Crude Bent Blade — топ-приоритет пары: 32/43, самая частая неземля.** Эдикт на входе + сила до 4 (то есть ещё и включатель Ferocious). Но как включатель он стоит 5 маны суммарно.
2. Amass-пакет БЕЗ разносчика menace не берём. Goblin-town 27/43 (12 листов с двумя копиями) — бери 1–2 всегда.
3. Ferocious не берём без 4–5 тел силы ≥4. Взял Bothersome Noisemaker — приоритет НЕкреатурным (Rage, Tidings, Pinecone Strike, Deadly Slice); Gandalf его НЕ триггерит.
4. Óin/Bombur (Storied): Dori закрывает два слота сразу (легендарка + Treasure), Crude Bent Blade — третий. Dwarven Mauler без эквипа — ванильный 2/1 (8/8 листов с Mauler держат Blade).
5. Существ ≥10 (медиана 14), removal медиана 5. Pinecone Strike / Gnashing / Head of the Hunt ИЗГОНЯЮТ убитое → скидку Dreaded Bat-Cloud они **не** включают: под неё нужен Stir Up Trouble, Crude Bent Blade или Bilbo's Deadly Slice.

### WR — дворфы, эквип, Storied (n=39)
**План:** плотная кривая дворфов (медиана 10) + эквип; три квалифицирующих перманента навсегда включают Storied. Две ветки: белая эквип-го-вайд (22 листа) и красная амасс-топэнд (17).
1. **Ветку выбери к P2:** Blacksmith + Raider = 1 лист из 39.
2. Iron Hills (30/39) — первый нон-плеябл: RW-фиксер + два счётчика на любого Дворфа, включая токены.
3. Дворфов цель 10+: на них завязаны Iron Hills, Mattock («attach it to target Dwarf»), Vow to Erebor, лайфлинк Dáin's Company, Кили.
4. Mattock (Equip {3}) без бесплатного перевешивания (Stalwart 9 листов, Vow to Erebor 6, Mauler 6) — разовый +2/+2. Glóin оценивай как ритуал: {R}{R} именно в первую главную = оплаченный эквип.
5. Держи 2 маны открытыми: Magnificent End по ТАПНУТОМУ стоит {1}{W}. Stone by Sunlight убивает **только силу 4+** — не универсальный ремувал.

### BG — ферошес-агро на волках (n=35)
**План:** дешёвые волки + одно тело силы 4+ → вся команда растёт, добирает (The Chief Warg 19/35) и проходит menace+трамплом; чёрное даёт безусловный removal.
1. Пейофф без тела 4+ — ванильный медведь. **3+ пейоффа ⇒ ≥5 источников силы 4** (медиана 7; исключений среди 25 листов нет).
2. Дешёвые включатели по приоритету: Duskwatch Hunter (3 маны, 4/2) → Desolation Prowler (2 жизни) → Mirkwood (сак земли, +2 счётчика навсегда) → Mirkwood Pathmaker (с 4-й земли) → Crude Bent Blade (дороже всех: 5 маны).
3. Attercop (24/35) бери РАНЬШЕ Quarrel: 22 из 23 листов с Quarrel держат дэтчтачера.
4. Mirkwood (25/35, 36 копий, во всех 25 есть Медведь/Паук/Волк) — почти бесплатный слот, бери вместо 23-й играбельной. Земель 17 (29/35) или 16 (6/35).
5. Stir Up Trouble без артефакта (13 из 14 листов держат) съедает собственное тело силы 4 и выключает ферошес: с Large Bear 0/35, с Boughside 0/35.

### Пары без полного разбора (только вердикты по связкам)
Плана, n и правил в данных нет — используй как локальные проверки.
- **WU:** Bilbo, Luckwearer + Lakeshore Apothecary; Hobbit Hole + Bilbo (7/7 листов); The Lord of the Eagles дешевеет на суммарную силу летающих (Long Lake Nuisance 3/1 = −3, все 3 листа с Лордом играют Nuisance).
- **UB:** Master's Councillors — ось «вторая карта за ход → милл 3»: Plunder (флэшбэк = второй триггер), Long Lake Nuisance (4 карты в ГЯ за один ETB); Desolation Prowler + Ravening Warg.
- **UR:** Master's Councillors + Plunder; Goblin Plate Mail + Tidings of War; Óin + 6–12 квалифицирующих перманентов (9 листов).
- **WB:** Hobbit Hole + Gollum (5 из 6 листов; суммарно 8 маны — тьютор {4} + каст {3}{B}).
- **RG:** Quarrel + Attercop; Galion + Wargling; Noisemaker + Tidings; The Lonely Mountain + эквип.
- **Моно:** Stir Up → Bat-Cloud за {1}{B}; Duskwatch → Nighthowl 3/3 menace за {B}; Beorn the Fierce + Attercop; Great Gilded Boat + Master's Councillors; Eagle's Rescue + Patient Instructor.

---

## Что противоречит интуиции

1. **Земля бывает лучшим пиком, чем 22-я играбельная.** Iron Hills 30/39, Elvenking's Halls 32/44, Goblin-town 27/43, Mirkwood 25/35 — они входят в 17 земель и не занимают слот спелла, при этом дают два +1/+1 счётчика по трайбу. Обычная статистика карт этого не показывает.
2. **Самая играемая карта пары ≠ лучший исполнитель роли.** Crude Bent Blade (32/43 BR, 23/35 BG) как включатель Ferocious стоит {2}{B} + Equip {2} = 5 маны до первой атаки; Duskwatch Hunter делает то же за 3, Gollum — за 4.
3. **Hobbit Hole не даёт маны вообще.** Это Evolving Wilds с halflingcycling {4}. В агро-кривой (Nori, WR) и рядом с Wood Elves (BG) она — антисинергия, а не фикс.
4. **Один landfall-триггер не окупает сак земли, два — окупают.** Скептик пометил Hobbit Hole + Attercop как WEAK, но Hobbit Hole + Attercop + Boughside Wanderers — CONFIRMED. Порог реального боевого трика = **два landfall-тела на столе**.
5. **Ferocious-выплаты не равноценны, хотя лежат в одном «пакете».** Ravening Warg даёт «gain 2 life», Wargling — трампл ВСЕЙ команде, Wilderland Scrounger — счётчик на каждое существо. Считать их одинаковыми пейоффами нельзя.
6. **Корм под сакрифайс — не сигнал.** Stir Up Trouble берёт любой артефакт ИЛИ существо; в 100% листов это есть. Ценность создают карты, которым нужна СМЕРТЬ: Dreaded Bat-Cloud (скидка {3}), Part in Friendship, Head of the Hunt.
7. **Storied не нужно «собирать».** В реальных листах 6–12 квалифицирующих перманентов; условие включается само. Пик решает выплата, а не счёт.
8. **Ванильный толстяк в подстройке — минус, а не плюс.** Galion + Ordinary Bear 0 из 45 (Galion ставит БАЗОВЫЕ 4/4 и 4/5 уменьшает); Ordinary Bear + Thranduil 1 из 45; Stir Up + Large Bear 0 из 35.
9. **Высокий lift ≠ механика.** Из 64 проверенных утверждений 9 выброшены именно как «две карты одной колоды» (в т.ч. Chief Warg's Company + Forest — это цветовая идентичность {1}{B}{G}, а не связка; Misty Mountains Raider + Stone by Sunlight; Guardian of the Halls + Troll Negotiations; Thranduil's Company + Troll Negotiations). Сам разбор WR прямо перечисляет частые пары без текстового стыка: Gundabad+Raider, Dáin Lord+Kíli, An Unexpected Party+Óin/Ori, Dwalin+Ori, Fíli+Glóin, Bombur+Mauler.
10. **18 земель не сыграл никто** (BG: 35 из 35 листов на 17 или 16), при том что утилитарные земли считаются внутри этих 17.
11. **Пара может вообще не иметь безусловного removal.** UG: только аура Grasp и tuck Uneasy Partings. Значит бомбы соперника в UG решаются позицией, а не пиком ремувала.
12. **«Whenever you attack» у Great Gilded Boat срабатывает без крюя** — Лодка приносит карту и токен, даже не будучи существом; Crew 2 при этом требует силы 2, один 1/1 токен её не крюит.
13. **Ключевые тексты в разборе бывают обрезаны ровно там, где живёт аргумент** (Nasty Little Rabbit без условия «if you control a creature with power 4 or greater»; Кили без «triggers only once each turn»; Weavemaster без «only to cast Elf spells»). Проверяй полный текст, прежде чем двигать пик.

---

## Границы данных

- **Расписаны только 4 пары из 161 колоды: UG 44, BR 43, WR 39, BG 35.** Остальные ~137 трофейных колод (WU, UB, WB, UR, RG, моно) присутствуют лишь отдельными вердиктами по связкам — **ни плана, ни n, ни правил, ни антисинергий**. Для этих пар шпаргалка неполная.
- **Gold + Platinum.** Mythic в бесплатной выдаче untapped отсутствует — верхний срез игроков в выборку не попал.
- **Только победившие колоды, базы проигравших нет.** «X в 30 из 39 листов» **не** означает высокий винрейт: карта может быть просто частой или поздно уходящей. Пик-порядок (ALSA/GIH) отсюда не выводится — шпаргалка дополняет 17Lands, а не заменяет.
- **Антисинергии измерены как со-встречаемость против ожидания ВНУТРИ трофейных колод.** «1 из 45 при ожидании 5» означает «победители их не собирают вместе» — это может быть раздел веток или доступность в паках, а не качество карт.
- **Трофейная колода — это готовые 40 карт, а не запись драфта.** Порядка пиков в данных нет; всё, что здесь названо «приоритетом», — вывод из состава, а не наблюдение.
- **Малые n у части CONFIRMED-связок:** Stir Up + Part in Friendship — 3 листа, Lord of the Eagles + Nuisance — 3, Wilderland + Great Ugly — 4, Chief Warg's Company-тройка — 5. На таких числах связка неотличима от совпадения.
- **Непроверенных связок больше, чем проверенных.** Из 88 связок по четырём парам вердикт получила лишь часть; раздел «не проверялись» — гипотезы, не правила.
- **Исходный разбор BG обрывается** на списке ролей removal — часть правил пары в данных отсутствует.
- **Текст Goblin-town в данных приведён только сак-способностью**; обычная мана-абилка не подтверждена цитатой (для Iron Hills и Mirkwood — подтверждена «{T}: Add»), хотя правило BR называет её фиксером {B}{R}.
- **Нет ни винрейтов, ни данных по играм, ни сайдборда** (Premier — Bo1). Всё «сколько removal / сколько существ» — медианы по победившим спискам, а не оптимум."
  },
  "workflowProgress": [
    {
      "type": "workflow_phase",
      "index": 1,
      "title": "Механизмы"
    },
    {
      "type": "workflow_phase",
      "index": 2,
      "title": "Опровержение"
    },
    {
      "type": "workflow_phase",
      "index": 3,
      "title": "Синтез"
    },
    {
      "type": "workflow_agent",
      "index": 1,
      "label": "механизм:UG",
      "phaseIndex": 1,
      "phaseTitle": "Механизмы",
      "agentId": "ae9252392be973f2d",
      "model": "claude-opus-5[1m]",
      "state": "done",
      "startedAt": 1786912049625,
      "queuedAt": 1786912049613,
      "attempt": 1,
      "lastToolName": "StructuredOutput",
      "lastToolSummary": "UG",
      "promptPreview": "Разбор трофейных колод MTG-сета The Hobbit (HOB), группа UG. Выборка — 298 листов
победителей (7-0…7-2), это вся доступная популяция формата, а не образец.

ДАННЫЕ:
- Колоды: /Users/wolfeatyou/.claude/skills/mtg-draft-helper/ref_decks/hob/*.txt. Тебе нужны листы пары UG: имя файла начинается с цветов в нижнем регистре, порядок букв может быть любым (ug или gu). Их несколько десятков.
- Тексты карт…",
      "lastProgressAt": 1786912807347,
      "tokens": 73997,
      "toolCalls": 22,
      "durationMs": 757721,
      "resultPreview": "{"pair":"UG","n":44,"plan":"UG — landfall + эльфы: лишние выходы земель (Wood Elves, Hobbit Hole, Thranduil's Company, Till and Tend) конвертируются в токены-эльфов, постоянные +1/+1 счётчики и ману Weavemaster'а. Хардремувала в паре нет — убивают Quarrel через deathtouch Attercop'а, а бомбу выключает Enchanted River's Grasp (33/44 листов); добивают эвазией Elvenking's Harper.","combos":[{"cards":…"
    },
    {
      "type": "workflow_agent",
      "index": 2,
      "label": "механизм:BR",
      "phaseIndex": 1,
      "phaseTitle": "Механизмы",
      "agentId": "a5e3c09c126b90fba",
      "model": "claude-opus-5[1m]",
      "state": "done",
      "startedAt": 1786912049625,
      "queuedAt": 1786912049613,
      "attempt": 1,
      "lastToolName": "StructuredOutput",
      "lastToolSummary": "BR",
      "promptPreview": "Разбор трофейных колод MTG-сета The Hobbit (HOB), группа BR. Выборка — 298 листов
победителей (7-0…7-2), это вся доступная популяция формата, а не образец.

ДАННЫЕ:
- Колоды: /Users/wolfeatyou/.claude/skills/mtg-draft-helper/ref_decks/hob/*.txt. Тебе нужны листы пары BR: имя файла начинается с цветов в нижнем регистре, порядок букв может быть любым (br или rb). Их несколько десятков.
- Тексты карт…",
      "lastProgressAt": 1786912763521,
      "tokens": 102091,
      "toolCalls": 23,
      "durationMs": 712393,
      "resultPreview": "{"pair":"BR","n":43,"plan":"Дешёвые тела + amass копят счётчики на ОДНОЙ Армии, а Goblin Plate Mail / Great Ugly-Looking Goblin дают ей менис, чтобы куча counters реально проходила. Плотный removal (Crude Bent Blade 32/43, Stir Up Trouble, Bilbo's Deadly Slice) расчищает атаку, а Ferocious-пакет (Ravening Warg) добивает по жизням.","combos":[{"cards":["Gollum, Silent Slinker","Ravening Warg"],"dec…"
    },
    {
      "type": "workflow_agent",
      "index": 3,
      "label": "механизм:WR",
      "phaseIndex": 1,
      "phaseTitle": "Механизмы",
      "agentId": "aea4d82fc441d916b",
      "model": "claude-opus-5[1m]",
      "state": "done",
      "startedAt": 1786912049625,
      "queuedAt": 1786912049613,
      "attempt": 1,
      "lastToolName": "StructuredOutput",
      "lastToolSummary": "WR (Boros — Дворфы/Эквип, Storied)",
      "promptPreview": "Разбор трофейных колод MTG-сета The Hobbit (HOB), группа WR. Выборка — 298 листов
победителей (7-0…7-2), это вся доступная популяция формата, а не образец.

ДАННЫЕ:
- Колоды: /Users/wolfeatyou/.claude/skills/mtg-draft-helper/ref_decks/hob/*.txt. Тебе нужны листы пары WR: имя файла начинается с цветов в нижнем регистре, порядок букв может быть любым (wr или rw). Их несколько десятков.
- Тексты карт…",
      "lastProgressAt": 1786912922996,
      "tokens": 109618,
      "toolCalls": 23,
      "durationMs": 871866,
      "resultPreview": "{"pair":"WR (Boros — Дворфы/Эквип, Storied)","n":39,"plan":"Плотная кривая Дворфов (медиана 10 дворфов на лист) плюс Эквип; тремя перманентами из «артефакты/легенды/Саги» навсегда включаешь Storied, и все легенды становятся крупнее, а ремувал (медиана 4-5 карт) сносит блокеров. Внутри пары две ветки: бело-тяжёлая эквип-го-вайд (Shortsword/Blacksmith/Stalwart/Mattock, 22 листа) и красно-тяжёлая ама…"
    },
    {
      "type": "workflow_agent",
      "index": 4,
      "label": "механизм:BG",
      "phaseIndex": 1,
      "phaseTitle": "Механизмы",
      "agentId": "abd63537091c08ebc",
      "model": "claude-opus-5[1m]",
      "state": "done",
      "startedAt": 1786912049625,
      "queuedAt": 1786912049614,
      "attempt": 1,
      "lastToolName": "StructuredOutput",
      "lastToolSummary": "BG",
      "promptPreview": "Разбор трофейных колод MTG-сета The Hobbit (HOB), группа BG. Выборка — 298 листов
победителей (7-0…7-2), это вся доступная популяция формата, а не образец.

ДАННЫЕ:
- Колоды: /Users/wolfeatyou/.claude/skills/mtg-draft-helper/ref_decks/hob/*.txt. Тебе нужны листы пары BG: имя файла начинается с цветов в нижнем регистре, порядок букв может быть любым (bg или gb). Их несколько десятков.
- Тексты карт…",
      "lastProgressAt": 1786912842085,
      "tokens": 108545,
      "toolCalls": 38,
      "durationMs": 790956,
      "resultPreview": "{"pair":"BG","n":35,"plan":"BG — ферошес-агро на дешёвых Волках: держишь на столе одно тело силы 4+, и вся команда бесплатно растёт счётчиками, добирает карты (The Chief Warg) и лезет сквозь блок менасом с трамплом. Чёрное докладывает безусловный removal (Bilbo's Deadly Slice, Stir Up Trouble) и эдикт на Crude Bent Blade, зелёное — Quarrel с дэтчтачем как второй removal.","combos":[{"cards":["Crud…"
    },
    {
      "type": "workflow_agent",
      "index": 5,
      "label": "механизм:WU",
      "phaseIndex": 1,
      "phaseTitle": "Механизмы",
      "agentId": "a23d0678a656ff548",
      "model": "claude-opus-5[1m]",
      "state": "done",
      "startedAt": 1786912049626,
      "queuedAt": 1786912049614,
      "attempt": 1,
      "lastToolName": "StructuredOutput",
      "lastToolSummary": "WU",
      "promptPreview": "Разбор трофейных колод MTG-сета The Hobbit (HOB), группа WU. Выборка — 298 листов
победителей (7-0…7-2), это вся доступная популяция формата, а не образец.

ДАННЫЕ:
- Колоды: /Users/wolfeatyou/.claude/skills/mtg-draft-helper/ref_decks/hob/*.txt. Тебе нужны листы пары WU: имя файла начинается с цветов в нижнем регистре, порядок букв может быть любым (wu или uw). Их несколько десятков.
- Тексты карт…",
      "lastProgressAt": 1786912885686,
      "tokens": 109846,
      "toolCalls": 29,
      "durationMs": 834557,
      "resultPreview": "{"pair":"WU","n":25,"plan":"Плоская кривая Human-тел с vigilance + recruit-карты, которые дают токен И «вторую карту за ход»; пейоффы (Апотекарь, Бард, Toymaker) конвертируют эти дро в счётчики и урон. Убивает пара дёшево: таппер (Grasp / Gaze in Wonder) превращает Magnificent End в заклинание за {W}.","combos":[{"cards":["Enchanted River's Grasp","Magnificent End"],"kind":"механика","decks":13,"w…"
    },
    {
      "type": "workflow_agent",
      "index": 6,
      "label": "механизм:UB",
      "phaseIndex": 1,
      "phaseTitle": "Механизмы",
      "agentId": "ad655fcc27982427c",
      "model": "claude-opus-5[1m]",
      "state": "done",
      "startedAt": 1786912049626,
      "queuedAt": 1786912049614,
      "attempt": 1,
      "lastToolName": "StructuredOutput",
      "lastToolSummary": "UB",
      "promptPreview": "Разбор трофейных колод MTG-сета The Hobbit (HOB), группа UB. Выборка — 298 листов
победителей (7-0…7-2), это вся доступная популяция формата, а не образец.

ДАННЫЕ:
- Колоды: /Users/wolfeatyou/.claude/skills/mtg-draft-helper/ref_decks/hob/*.txt. Тебе нужны листы пары UB: имя файла начинается с цветов в нижнем регистре, порядок букв может быть любым (ub или bu). Их несколько десятков.
- Тексты карт…",
      "lastProgressAt": 1786912821443,
      "tokens": 91048,
      "toolCalls": 22,
      "durationMs": 770313,
      "resultPreview": "{"pair":"UB","n":23,"plan":"Пара выигрывает на триггере «вторая карта за ход»: 7-12 дешёвых доборов (Plunder, Rage, recruit-карты, Билбо) превращают Lakeshore Apothecary и Master's Councillors в растущие угрозы. Чёрное removal (Slice/Stir Up/Gnashing) держит доску, а добивают непроходимый Bilbo, Luckwearer, Great Gilded Boat и Army-токены.","combos":[{"cards":["Head of the Hunt","Stir Up Trouble"]…"
    },
    {
      "type": "workflow_agent",
      "index": 7,
      "label": "механизм:WB",
      "phaseIndex": 1,
      "phaseTitle": "Механизмы",
      "agentId": "a45939bb668640010",
      "model": "claude-opus-5[1m]",
      "state": "done",
      "startedAt": 1786912049626,
      "queuedAt": 1786912049614,
      "attempt": 1,
      "lastToolName": "StructuredOutput",
      "lastToolSummary": "WB",
      "promptPreview": "Разбор трофейных колод MTG-сета The Hobbit (HOB), группа WB. Выборка — 298 листов
победителей (7-0…7-2), это вся доступная популяция формата, а не образец.

ДАННЫЕ:
- Колоды: /Users/wolfeatyou/.claude/skills/mtg-draft-helper/ref_decks/hob/*.txt. Тебе нужны листы пары WB: имя файла начинается с цветов в нижнем регистре, порядок букв может быть любым (wb или bw). Их несколько десятков.
- Тексты карт…",
      "lastProgressAt": 1786912859800,
      "tokens": 103380,
      "toolCalls": 27,
      "durationMs": 808670,
      "resultPreview": "{"pair":"WB","n":18,"plan":"WB выигрывает широкой доской дворфов/солдат/Армии, поверх которой ложатся эквипы и Storied-анемоны (Ori/Fíli/Dáin), а чёрная половина даёт Голлума 4/3 и медиану 5 снятий на лист — размен один-в-один плюс перевес в размере. Второй мотор — кладбище: recruit сбрасывает существо, а The Mountain-king's Return II и Gathering of Darkness его возвращают.","combos":[{"cards":["I…"
    },
    {
      "type": "workflow_agent",
      "index": 8,
      "label": "механизм:UR",
      "phaseIndex": 1,
      "phaseTitle": "Механизмы",
      "agentId": "ac17d1b577571e179",
      "model": "claude-opus-5[1m]",
      "state": "done",
      "startedAt": 1786912049626,
      "queuedAt": 1786912049614,
      "attempt": 1,
      "lastToolName": "StructuredOutput",
      "lastToolSummary": "UR",
      "promptPreview": "Разбор трофейных колод MTG-сета The Hobbit (HOB), группа UR. Выборка — 298 листов
победителей (7-0…7-2), это вся доступная популяция формата, а не образец.

ДАННЫЕ:
- Колоды: /Users/wolfeatyou/.claude/skills/mtg-draft-helper/ref_decks/hob/*.txt. Тебе нужны листы пары UR: имя файла начинается с цветов в нижнем регистре, порядок букв может быть любым (ur или ru). Их несколько десятков.
- Тексты карт…",
      "lastProgressAt": 1786912694204,
      "tokens": 82800,
      "toolCalls": 23,
      "durationMs": 643074,
      "resultPreview": "{"pair":"UR","n":16,"plan":"UR — темпо-вэлью на «второй карте за ход»: дешёвые синие тела (Lakeshore Apothecary 13/16, Master's Councillors 10/16) растут и мельчат от плотного пакета кантрипов/recruit (Bilbo Burglar 15/16, Plunder 13/16, Long Lake Nuisance 11/16), красный держит доску удалением (Pinecone Strike 14/16) и закрывает топ-эндом (Gandalf Spark Starter и Smaug the Great Calamity по 10/16…"
    },
    {
      "type": "workflow_agent",
      "index": 9,
      "label": "механизм:RG",
      "phaseIndex": 1,
      "phaseTitle": "Механизмы",
      "agentId": "ab1a8002cd13d43fb",
      "model": "claude-opus-5[1m]",
      "state": "done",
      "startedAt": 1786912694206,
      "queuedAt": 1786912049614,
      "attempt": 1,
      "lastToolName": "StructuredOutput",
      "lastToolSummary": "RG",
      "promptPreview": "Разбор трофейных колод MTG-сета The Hobbit (HOB), группа RG. Выборка — 298 листов
победителей (7-0…7-2), это вся доступная популяция формата, а не образец.

ДАННЫЕ:
- Колоды: /Users/wolfeatyou/.claude/skills/mtg-draft-helper/ref_decks/hob/*.txt. Тебе нужны листы пары RG: имя файла начинается с цветов в нижнем регистре, порядок букв может быть любым (rg или gr). Их несколько десятков.
- Тексты карт…",
      "lastProgressAt": 1786913463329,
      "tokens": 90658,
      "toolCalls": 22,
      "durationMs": 769123,
      "resultPreview": "{"pair":"RG","n":14,"plan":"RG — наземный бит: 14–16 существ, из них 5–10 с силой 4+ (среднее 7.6), плюс дешёвый removal (Pinecone Strike 12/14, Quarrel 11/14). Сила 4 — общая валюта: она превращает Quarrel в убийство любого существа за {1}{G} и включает Ferocious (Wargling / Nasty Little Rabbit / Wilderland Scrounger), который даёт всей команде трампл. Внутри пары две ветки: зелёный landfall/земл…"
    },
    {
      "type": "workflow_agent",
      "index": 10,
      "label": "механизм:MONO",
      "phaseIndex": 1,
      "phaseTitle": "Механизмы",
      "agentId": "a61801bd2e1748129",
      "model": "claude-opus-5[1m]",
      "state": "done",
      "startedAt": 1786912763521,
      "queuedAt": 1786912049614,
      "attempt": 1,
      "lastToolName": "StructuredOutput",
      "lastToolSummary": "MONO",
      "promptPreview": "Разбор трофейных колод MTG-сета The Hobbit (HOB), группа MONO. Выборка — 298 листов
победителей (7-0…7-2), это вся доступная популяция формата, а не образец.

ДАННЫЕ:
- Колоды: /Users/wolfeatyou/.claude/skills/mtg-draft-helper/ref_decks/hob/*.txt. Тебе нужны МОНОЦВЕТНЫЕ: файлы b_mono_*, g_mono_*, u_mono_*, w_mono_*, r_mono_* (всего ~31).
- Тексты карт: /Users/wolfeatyou/.claude/skills/mtg-draft-he…",
      "lastProgressAt": 1786913654583,
      "tokens": 129660,
      "toolCalls": 15,
      "durationMs": 891062,
      "resultPreview": "{"pair":"MONO","n":34,"plan":"Каждая моно-колода HOB — одна вертикаль, где карта либо КЛАДЁТ счётчик/триггер, либо его СЧИТАЕТ: B растит одну Армию через amass и включает Ferocious-волков телом с силой 4+; G копит landfall-счётчики и эльфов; U ловит «вторую карту за ход» бесплатными recruit-триггерами; W собирает 3 артефакта/легенды/саги на Storied вокруг гномов и эквипа. Выигрывают темпом одной м…"
    },
    {
      "type": "workflow_agent",
      "index": 11,
      "label": "скептик:1",
      "phaseIndex": 2,
      "phaseTitle": "Опровержение",
      "agentId": "a716c49d95806f3ce",
      "model": "claude-opus-5[1m]",
      "state": "done",
      "startedAt": 1786913654595,
      "queuedAt": 1786913654586,
      "attempt": 1,
      "lastToolName": "StructuredOutput",
      "promptPreview": "Ты СКЕПТИК. Проверяешь заявленные связки в сете HOB. Задача — ОПРОВЕРГНУТЬ.

Тексты: /Users/wolfeatyou/.claude/skills/mtg-draft-helper/hob_set.json (через python3/grep). Колоды: /Users/wolfeatyou/.claude/skills/mtg-draft-helper/ref_decks/hob/*.txt (298 шт).

Для каждого пункта:
- Есть ли в текстах карт реальное взаимодействие? Или это две карты одного архетипа, которые
  просто часто вместе? Второ…",
      "lastProgressAt": 1786914473451,
      "tokens": 95116,
      "toolCalls": 18,
      "durationMs": 818855,
      "resultPreview": "{"results":[{"claim":"1. [UG] Attercop + Quarrel","verdict":"CONFIRMED","reason":"Цитаты дословны. Attercop: «Reach, deathtouch»; Quarrel: «Target creature you control deals damage equal to its power to target creature an opponent controls.» Deathtouch превращает любой ненулевой урон в убийство, а Quarrel (в отличие от fight) не даёт ответки. Проверил грепом: deathtouch в сете только у Dreaded Bat…"
    },
    {
      "type": "workflow_agent",
      "index": 12,
      "label": "скептик:2",
      "phaseIndex": 2,
      "phaseTitle": "Опровержение",
      "agentId": "a0b6c38a474807424",
      "model": "claude-opus-5[1m]",
      "state": "done",
      "startedAt": 1786913654596,
      "queuedAt": 1786913654587,
      "attempt": 1,
      "lastToolName": "StructuredOutput",
      "promptPreview": "Ты СКЕПТИК. Проверяешь заявленные связки в сете HOB. Задача — ОПРОВЕРГНУТЬ.

Тексты: /Users/wolfeatyou/.claude/skills/mtg-draft-helper/hob_set.json (через python3/grep). Колоды: /Users/wolfeatyou/.claude/skills/mtg-draft-helper/ref_decks/hob/*.txt (298 шт).

Для каждого пункта:
- Есть ли в текстах карт реальное взаимодействие? Или это две карты одного архетипа, которые
  просто часто вместе? Второ…",
      "lastProgressAt": 1786914572881,
      "tokens": 114010,
      "toolCalls": 12,
      "durationMs": 916601,
      "resultPreview": "{"results":[{"claim":"1. [UG] Thranduil, Sindarin Liege + Woodland Weavemaster","verdict":"CONFIRMED","reason":"Цитаты дословны. Weavemaster — Creature — Elf Druid, значит анфем «Other Elves you control get +1/+1» его буквально задевает: 1/2 → 2/3, а «Add X mana… where X is this creature's power» читает эту силу. Токен от landfall — тоже Elf, т.е. «Whenever another Elf you control enters» срабатыв…"
    },
    {
      "type": "workflow_agent",
      "index": 13,
      "label": "скептик:3",
      "phaseIndex": 2,
      "phaseTitle": "Опровержение",
      "agentId": "ac777a3a85221e252",
      "model": "claude-opus-5[1m]",
      "state": "done",
      "startedAt": 1786913654596,
      "queuedAt": 1786913654587,
      "attempt": 1,
      "lastToolName": "StructuredOutput",
      "promptPreview": "Ты СКЕПТИК. Проверяешь заявленные связки в сете HOB. Задача — ОПРОВЕРГНУТЬ.

Тексты: /Users/wolfeatyou/.claude/skills/mtg-draft-helper/hob_set.json (через python3/grep). Колоды: /Users/wolfeatyou/.claude/skills/mtg-draft-helper/ref_decks/hob/*.txt (298 шт).

Для каждого пункта:
- Есть ли в текстах карт реальное взаимодействие? Или это две карты одного архетипа, которые
  просто часто вместе? Второ…",
      "lastProgressAt": 1786914510615,
      "tokens": 90260,
      "toolCalls": 16,
      "durationMs": 854334,
      "resultPreview": "{"results":[{"claim":"1. [UG] Woodland Weavemaster + Elvenking's Harper — мана Weavemaster легально платит {4}{U} Harper'а, а приход Harper'а пампит Weavemaster","verdict":"WEAK","reason":"Обе цитаты точны. Weavemaster: «Spend this mana only to cast Elf spells and activate abilities of Elf sources», Harper — Creature — Elf Bard, значит его {4}{U} действительно легальный слив для этой маны, и он же…"
    },
    {
      "type": "workflow_agent",
      "index": 14,
      "label": "скептик:4",
      "phaseIndex": 2,
      "phaseTitle": "Опровержение",
      "agentId": "af74ed5826c5c1ae7",
      "model": "claude-opus-5[1m]",
      "state": "done",
      "startedAt": 1786913654596,
      "queuedAt": 1786913654587,
      "attempt": 1,
      "lastToolName": "StructuredOutput",
      "promptPreview": "Ты СКЕПТИК. Проверяешь заявленные связки в сете HOB. Задача — ОПРОВЕРГНУТЬ.

Тексты: /Users/wolfeatyou/.claude/skills/mtg-draft-helper/hob_set.json (через python3/grep). Колоды: /Users/wolfeatyou/.claude/skills/mtg-draft-helper/ref_decks/hob/*.txt (298 шт).

Для каждого пункта:
- Есть ли в текстах карт реальное взаимодействие? Или это две карты одного архетипа, которые
  просто часто вместе? Второ…",
      "lastProgressAt": 1786914406157,
      "tokens": 79239,
      "toolCalls": 14,
      "durationMs": 749876,
      "resultPreview": "{"results":[{"claim":"1. [UG] Woodland Weavemaster + Guardian of the Halls","verdict":"WEAK","reason":"Цитаты верны: Guardian — Elf Soldier, {5}{G}{G} — ability of an Elf source, мана Weavemaster ей платится. Но масштаб: Weavemaster 1/2, X = сила = 1 мана (2-3 если вошли эльфы, и то до конца хода). Он срезает с 7-маны один-два, а не «делает недостижимое достижимым». Тезис «без него почти недостижи…"
    },
    {
      "type": "workflow_agent",
      "index": 15,
      "label": "синтез",
      "phaseIndex": 3,
      "phaseTitle": "Синтез",
      "agentId": "ae3c1f27e471bd0fb",
      "model": "claude-opus-5[1m]",
      "state": "done",
      "startedAt": 1786914572886,
      "queuedAt": 1786914572883,
      "attempt": 1,
      "promptPreview": "Собери шпаргалку по HOB для ЖИВОГО ДРАФТА на основе разбора 298 трофейных колод —
всей доступной популяции формата. Читать будет советчик в момент пика: короткие
проверяемые правила, не эссе. Markdown, по-русски.

РАЗБОР ПО ПАРАМ:
[
 {
  "pair": "UG",
  "n": 44,
  "plan": "UG — landfall + эльфы: лишние выходы земель (Wood Elves, Hobbit Hole, Thranduil's Company, Till and Tend) конвертируются в ток…",
      "lastProgressAt": 1786915027335,
      "tokens": 66883,
      "toolCalls": 0,
      "durationMs": 454448,
      "resultPreview": "# HOB — что делают победители (298 трофейных колод)

> Источник: разбор трофейных колод (gold+platinum, untapped). Проверено скептиком 64 утверждения: 31 CONFIRMED, 24 WEAK, 9 REFUTED (выброшены). Всё ниже — из данных; противоречия названы прямо.
> **Как читать в пике:** сначала «Сквозные закономерности» → потом блок своей пары → таблицу связок использовать как проверку, а не как план.

---

## Ск…"
    }
  ],
  "totalTokens": 1447151,
  "totalToolCalls": 304
}