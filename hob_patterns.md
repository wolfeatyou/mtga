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


### Дополнение: шесть пар, дописано 17.08.2026

Повод — переигровка драфта: знание молчало ровно там, куда уводит драфт (по WU было три
строки, по WB одна, при 25 и 18 листах). Разбор тот же: статистика даёт кандидатов, агенты
объясняют механизм по оракл-текстам, независимые скептики опровергают (61 связка заявлена,
31 подтверждена). Гипотеза «в каждой паре ровно две ветки» здесь ПРОВЕРЕНА И ОТВЕРГНУТА
для WU и UB — см. блоки.

### WU — recruit и «вторая карта за ход» (n=25)
**План.** Почти каждая карта делает два дела сразу: recruit («Draw a card, then discard a card. If you discarded a nonland card, create a 1/1 white Human Soldier creature token») стоит в **25 из 25** листов (медиана 5 копий, минимум 3) и одним триггером даёт тело, фильтрует руку и служит «второй картой за ход» для Lakeshore Apothecary (17/25), Bard the Bowman (14/25), Master's Councillors (12/25); токены-люди подставляются под Lake-town (20/25). Доска растёт счётчиками, добивают неблокируемый Bilbo, Luckwearer и летуны. На removal не рассчитывай: безусловных убийств медиана 2 на лист (0–4).
**Ветки.** Веток нет — проверено, отрицательный результат. ≥2 Storied-дворфа и ≥3 летающих тела лежат вместе в 3 листах при ожидании 2.8 (для сравнения UG: Weavemaster × Nuisance 1 из 45 при 5). SVD «лист × карта»: S1/S2 = 1.038 — **самое низкое из всех пар** (UG 1.170, WR 1.117, BR 1.098, UB 1.090, BG 1.063), доминирующей оси раскола нет. Дворф-эквип и птицы-эвазия — надстройки над одним recruit-скелетом.
**Ядро.** Magnificent End 21/25 (28 копий) · Lake-town 20/25 (26, шесть листов с ДВУМЯ) · Patient Instructor 19/25 (35 копий — самая многокопийная неземля) · Bilbo Baggins, Burglar 19/25 (31) · Plunder the Trollshaws 18/25 (30) · Lakeshore Apothecary 17/25 (31) · Long Lake Nuisance 17/25 (33) · Bilbo, Luckwearer 17/25 (23) · Enchanted River's Grasp 16/25 (25) · Bard the Bowman 14/25 · Uneasy Partings 14/25 · Mountain-king's Return 13/25 · Celebrate the Mountain-king 12/25 · Master's Councillors 12/25 · Eagle's Rescue 11/25.
**Связки (CONFIRMED).**
- **Patient Instructor → Lakeshore Apothecary.** Instructor не флэш, его recruit-добор всегда ПОСЛЕ шага взятия → буквально «your second card each turn» → счётчик. Механика точная, но энейблер взаимозаменяем (recruit ещё на 6 картах), лифт 0.90 — 11 листов это базовый рейт, не сигнал.
- **Bilbo, Luckwearer → Bard the Bowman.** «Can't be blocked» → урон гарантирован → draw+discard = вторая карта. Только в СВОЙ ход; если вторую карту уже взял до боя — не триггерит; лайфлинк выдаётся после урона и в этом бою мёртв, ценность = постоянный счётчик. 11 листов при 9.6.
- **Confusticate and Bebother → Bard / Apothecary.** Единственный инстант сета, который сам тянет ДВЕ карты (Plunder тянет две только из ГЯ) → пейофф в ЧУЖОЙ ход, счётчик на блокера ДО урона. Режим-контрспелл не даёт ничего. 5 при 4.8.
- **Master's Councillors + Plunder the Trollshaws.** Флэшбэк тянет две → милл 3 в чужой ход; милл наводим на СЕБЯ → своё кладбище добивается до «seven or more» → 1/3 становится 3/3. Цикл одноразовый: флэшбэк экзайлит.
**Антисинергии.** Settle the Wreckage × Fíli the Pathfinder — 0 из 25 при 2.2, самая чистая: Settle это карта того, кто НЕ атакует, и она ещё рампит оппонента базовыми · Grasp + Uneasy Partings по ОДНОЙ цели — тук уносит существо вместе с аурой, владелец выбирает верх, минус две карты · Grasp НЕ включает скидку Magnificent End: он тапает только своего носителя, которого убивать уже не надо · Lake-town целится в **Human** — не Bird (Nuisance), не Halfling (оба Bilbo), не Insect (Velvetwing), не Dwarf. Ни одно из чисел не переживает поправку на ~300 сравнений (минимальный p = 0.009).
**Правила пика.**
1. Recruit — обязательный минимум, не приятная мелочь: ниже 3 копий не опускайся. Без него мертвы пейоффы «второй карты», способность Lake-town (нужен Human), возврат Eagle's Rescue (нужен сброс) и глава II Mountain-king's Return.
2. Пейоффы «второй карты» бери РАНО и не ища включатель: источников лишнего добора на лист минимум 5, медиана 10. Это противоположность Ferocious в BG.
3. Lake-town — карта в кривой, а не фиксер: входит в 17 земель, слот спелла не занимает, бери вместо 22–23-й играбельной.
4. Держи 2 маны открытыми: Magnificent End по ТАПНУТОМУ стоит {1}{W} вместо {4}{W}; включают чужие атакующие и Gaze in Wonder.
5. Ответ на НЕсущество ровно один — Celebrate the Mountain-king (12/25); 9 из 25 листов без такого ответа вообще. Золото и гибриды (Bard the Bowman, Bard's Company, Patient Instructor, Eagle's Rescue) внутри пары — ядро, глобальный 17Lands GIH у них занижен.
**Границы.** n=25 — это 19 wu_azorius + 6 трёхцветных (2 Bant, 4 Jeskai), то есть ~24% блока не чистая Азориус: Iron Hills, Dori, Goblin Plate Mail, Dwarven Mattock и весь дворф-эквип-хвост приходят из них — в чистых 19 листах лидов «дворфы+эквип» нет вовсе. Лифты почти всех связок ≈1: механизм реален, «11 листов» — базовый рейт. **REFUTED, не использовать:** Lake-town + Patient Instructor (лифт ровно 1.00, крючок «target Human» удовлетворяет любой из пяти людей, а цена — 4 маны + жертва земли + скорость сорцери); Lake-town Toymaker + Bilbo Luckwearer (Toymaker проверяет условие «at the beginning of combat», а Билбо добирает в шаге урона — физически позже, включает Toymaker recruit). **WEAK:** Mountain-king's Return + Instructor (глава I сама делает recruit, MV≤3 подходит любому из ~10 тел); Lord of the Eagles + Nuisance (подойдёт любой флаер, n=3). Не проверялись скептиком: Eagle's Rescue + Билбо, Velvetwing + Magnificent End, Bard's Company + Instructor.

---

### UB — кантрипы и эвазия, а не доска (n=23)
**План.** Выигрывает добором: в КАЖДОМ из 23 листов 7–12 копий карт с лишним дро (медиана 9, исключений нет), и одно дро делает три работы — ищет снятие (медиана 3 безусловных + эдикт Crude Bent Blade 15/23 + тук Uneasy Partings 10/23), кормит счётчики Апотекаря (17/23) и милл Советников, и через recruit ставит 1/1. Добивают эвазией (медиана 4 копии летающих/неблокируемых/менис), а не размером: тел силы 4+ медиана 2 копии, у 4 листов их ноль.
**Ветки.** Веток нет: самое сильное отрицательное — Hobbit Hole (11) × Patient Instructor (13), 3 из 23 при 6.2, и оно не даёт двух непересекающихся групп. Вместо веток — **ползунок**: чёрная доска/Армия ↔ синий пейофф/интеракция. По копиям пакеты антикоррелируют (r = −0.54), но на уровне листов пересечение равно ожиданию (9 при 9.6); чистых полюсов 6 из 23, остальные 17 — смесь. Читай как настройку крена, «зафиксируй ветку к P2» здесь применять НЕЛЬЗЯ.
**Ядро.** Plunder the Trollshaws 18/23 (36 копий) · Lakeshore Apothecary 17/23 (37 — самая копируемая неземля) · Rage into the Valley 17/23 (26) · Bilbo's Deadly Slice 17/23 (25, единственный безусловный «Destroy» за 3) · Bilbo Baggins, Burglar 16/23 (32) · Crude Bent Blade 15/23 (27) · Long Lake Nuisance 15/23 (28) · Patient Instructor 13/23 (кастуется с Островов) · Bilbo, Luckwearer 13/23 · Hobbit Hole 11/23 (внутри 17 земель).
**Связки (CONFIRMED).**
- **Confusticate and Bebother + Apothecary/Councillors.** Проверено по всему сету: из руки две карты за один каст тянет только он → включает пейофф в ЧУЖОЙ ход. Оговорка: карта модальная, режим-контра связки не даёт.
- **Thrór's Map + Lakeshore Apothecary.** «{2}, {T}: Draw a card, then discard a card» — ни «only as a sorcery», ни лимита за игру: единственный ПОВТОРЯЕМЫЙ мотор пейоффа, вторая карта каждый свой ход. В чужой ход не триггерит (это первая карта того хода). Выглядит фиксером — это мотор.
- **Mirkwood Nurturer + Crude Bent Blade.** «Return up to one other target permanent you control to its owner's hand» + рекаст {2}{B} = ВТОРОЙ эдикт, а Nurturer получает счётчик только если реально вернул (3/2 → 4/3). 6 из 6 листов с Nurturer держат Клинок при ожидании 3.9.
- **Master's Councillors + Plunder** и **Lakeshore Apothecary + Plunder** (подтверждены в WU/UR): милл на себя кладёт Plunder в ГЯ и включает флэшбэк без дотягивания; флэшбэк тянет две → пейофф в чужой ход.
**Антисинергии.** Grasp × Crude Bent Blade — эдикт выбирает ОППОНЕНТ и отдаст уже обезвреженное аурой тело: это порядок розыгрыша (сначала эдикт, потом аура), 5 из 23 при 5.9 · Grasp × Uneasy Partings — тук уносит существо вместе с твоей аурой, сам себя 2-в-1 · Ravening Warg / Nighthowl Pursuer как «пакет Ferocious» — включателей нет (медиана тел 4+ = 2, 2 из 10 листов с Warg держат ноль), бери их как тела · Hobbit Hole × Instructor — у Хоула нет мана-абилки вообще, в ход жертвы ты без маны, и трёхдропка съезжает на четвёртый · Stir Up Trouble / Thrór's Map / Great Gilded Boat — в UB артефакты это моторы, а не Treasure-корм как в BR.
**Правила пика.**
1. Plunder и Apothecary — берём вторую и третью копию: 36 и 37 копий на 23 листа, медиана 2, максимум 4. Одной не хватает.
2. Master's Councillors только когда дро уже собрано: 7 из 7 листов с ним держат Plunder, Rage И Апотекаря. Иначе это 1/3, мельчащий раз в свой ход.
3. Rage into the Valley — кантрип, а не амасс-план: 9 из 17 листов с ним не держат ни одной другой амасс-карты. Не докупай под неё Goblin Plate Mail (Equip {4}).
4. В ЧУЖОЙ ход пейоффы включают только карты, тянущие ДВЕ: Confusticate и флэшбэк Plunder. Plunder с руки в чужой ход НЕ триггерит.
5. Гибриды — СВОИ карты, а не сплэш: Instructor {2}{W/U} (13/23, из них 9 листов без единой Равнины), Nurturer {2}{G/U} (все 6 листов БЕЗ Лесов), Large Bear, Plate Mail, Duskwatch. При равном GIH бери их раньше чужого золота. Клинок вешай на эвазию (Nuisance 12 из 15 листов с Клинком).
**Границы.** n=23 — самая маленькая из «полных» пар, и 5 листов не чистые UB (сультай, гриксис, 3 эспера): «белые» и «зелёные» частоты (Celebrate 6, Bard the Bowman 3) — их сплэши. Земель 17 (15–17, 18 нет ни у кого), существ 13 (9–16, ниже 9 не опустился никто). **REFUTED:** Great Gilded Boat + Bilbo Luckwearer — «Whenever you attack» действительно не требует крюя, но это факт О ЛОДКЕ: триггер включает любой атакующий, а 1/1 при этом Crew 2 не оплачивает. **WEAK:** Councillors + Rage (Rage — сорцери, «милл 3 каждый свой ход» ложно: один триггер за игру); Apothecary + Rage (текст — «your SECOND card each turn», максимум ОДИН счётчик за ход, а не «каждое лишнее дро»); Head of the Hunt + Stir Up/Slice (статик на любую смерть, включая размен в бою; n=3); Great Ugly-Looking Goblin + Rage (2 листа при 2.3 — лифт отрицательный, и сам Гоблин амассит себе приключением). Пять связок держатся на 3–4 листах. Отдельно: сквозное правило «amass всегда требует разносчика мениса» в UB НЕ выполняется — из 14 листов с ≥2 амасс-картами разносчика держат 8.

---

### WB — плотное убийство с довеском (n=18)
**План.** Размянивает один-в-один (медиана 5 копий ремувала на лист, 2–9) и выигрывает тем, что сам ремувал оставляет на столе: Crude Bent Blade (эдикт при выходе + эквип + артефакт под Storied) и Stir Up Trouble («Destroy target creature» за {B}) убивают и одновременно включают Dreaded Bat-Cloud. Добивает Армия под менисом (медиана 3 источника amass, разносчик в 14/18) либо Gollum, Silent Slinker — 4/3 menace за {3}{B} в 15 листах из 18.
**Ветки.** Есть, но мягкие. **A — белые легенды + эквип + Storied** (6 листов): Ori 10/18, Bofur 7, Fíli 6, Dáin Lord 5, Dwarven Shortsword 8, Esgaroth Garrison 5; дворфов медиана 5, эквипов 4. **B — дешёвая чёрная ширина** (8 листов): Front Porch Sentries 9, Rage 9, Stony-Voiced 8, Ravening Warg 7, Duskwatch 7, Desolation Prowler 7, Great Ugly 6, Bat-Cloud 6; Storied-карт НОЛЬ в 5 из 8, зато по 3–5 копий одной дешёвой двойки. 4 листа посередине. Разделение доказано **агрегатом**: 56 клеток «маркер A × маркер B» дают 101 совстречание при ожидании 161.5 (−37%), 7 клеток нулевые; PC1 объясняет 17.6% дисперсии против 13.7% в перестановочной нуль-модели, p=0.007 — выше, чем у любой другой пары. Отдельной пары уровня UG нет.
**Ядро.** Gollum, Silent Slinker 15/18 (22 копии) · Bilbo's Deadly Slice 12/18 (18) · Crude Bent Blade 12/18 (21) · Stir Up Trouble 11/18 (16) · Ori, Keeper of Songs 10/18 · The Mountain-king's Return 10/18 · Iron Hills Blacksmith 10/18 · Dwarven Provisioner 10/18 · Front Porch Sentries 9/18 · Goblin Plate Mail 9/18.
**Связки (CONFIRMED).**
- **Great Ugly-Looking Goblin + Duskwatch Hunter.** Ключевое чтение: «Each creature you control **with a +1/+1 counter on it** has menace» — никакого ограничения на Army, хотя карта подана как amass-пейофф. Duskwatch кладёт ETB-счётчик на кого угодно, включая себя: 3/1 → 4/2 с менисом. Данные слабые (3 листа при 2.31), текст точный.
- **Stir Up Trouble + Dreaded Bat-Cloud** (подтверждено в моно-B). Stir Up даёт смерть ДВАЖДЫ — доп-стоимостью «sacrifice an artifact or creature» и эффектом «Destroy target creature», обе в свой ход до каста Тучи: {B} + {1}{B} = снятие плюс 4/2 flying deathtouch. Оговорка: условие включает ЛЮБАЯ смерть, в том числе размен в бою, — Stir Up не обязателен.
**Антисинергии.** Down, Down to Goblin-town × The Mountain-king's Return — 1 из 18 при 4.4 (лучший p пары, 0.0019): обе саги за 3 маны, обе пасуют ход выхода, слот один · An Unexpected Party × Fíli — 0 из 18 при 2.3, два белых четырёхдропа-анкема (повторяет вердикт WR) · Dáin, Lord of the Iron Hills × Front Porch Sentries / Great Ugly / Bat-Cloud — по 0 из 18: его Storied это налог на ЧУЖУЮ атаку, карта играет от обороны · Bat-Cloud × Gnashing of Teeth / Head of the Hunt / Celebrate — все три ИЗГОНЯЮТ, существо не умирает, скидка {3} не включается · **ложная связка** Dwarven Shortsword × Fíli: Меч делает 2/2 **токен**, а Fíli триггерит на «another **NONTOKEN** Dwarf».
**Правила пика.**
1. Gollum (15/18) — первый пик пары в ЛЮБОЙ ветке: 4/3 menace за {3}{B}, adventure Meager Meal {B} даёт счётчик и 2 жизни, он же халфлинг-цель Hobbit Hole.
2. Ветку фиксируй по первой дорогой белой. Взял Dáin Lord / Bofur / Shortsword — дальше НЕ берём Front Porch Sentries, Duskwatch, Nighthowl, Bat-Cloud: все четыре пары дают 0 из 18.
3. Взял ≥2 источника amass — обязателен разносчик мениса (Goblin Plate Mail 9/18 или Great Ugly 6/18); так сделали 13 из 18. Great Ugly бери РАНЬШЕ второго amass — менис он даёт любому телу со счётчиком.
4. Bat-Cloud считай за {1}{B} только при УБИВАЮЩЕМ ремувале (Stir Up, Deadly Slice, Клинок, Stone by Sunlight, Magnificent End) — изгоняющие скидку не дают.
5. Ferocious не строим и Storied не собираем: у листов с Ravening Warg источников силы 4+ МЕНЬШЕ (медиана 4 против 6 у листов без него), а квалифицирующих под Storied и так 5–12 при пороге 3 — пик решает выплата. Дворфы в WB не трайб: медиана 4 копии против 10 в WR.
**Границы.** n=18 (16 чистых). Ветки доказаны только агрегатом, а маркеры выбраны из PC1 ЭТИХ ЖЕ листов — post-hoc, на новых данных разделение будет слабее, −37% это верхняя оценка. Большинство проверок «X из X листов» здесь неинформативны: источник счётчиков 18/18, убивающий ремувал 18/18, тело силы 4+ 18/18, recruit 16/18 — проверять надо КОЛИЧЕСТВО. Ключевые карты веток лежат в 5–7 листах. **REFUTED:** Goblin Plate Mail + Down, Down to Goblin-town (второй амасс — требование к архетипу, общее для всех 14 амасс-карт; 3 листа при 3.1); Gathering of Darkness + Patient Instructor (лифт ровно 1.0, ГЯ наполняется боевыми разменами, сброс-аутлет не нужен; подпорка «amass 3 — самый большой в паре» ложна — Fearsome Goblin Pair амассит 4). **WEAK:** Mountain-king's Return + Instructor; Nighthowl + Gollum (порог берёт любое тело 4+, дешевле — Desolation Prowler за 2 жизни); Iron Hills Blacksmith + Crude Bent Blade (7 при 6.7 — роль, а не драйвер пика). Земель 17 (11/18), 16 (6/18), 15 (1/18); база почти всегда 8/8 или 7/9.

---

### UR — синее темпо + красный ремувал и топ-энд (n=16)
**План.** 14 из 16 листов держат пейофф «второй карты» (Apothecary 13, Councillors 10, Ravenhill Flock 5) при медиане 9 добор-энейблеров (5–11); каждый лишний добор — постоянный счётчик или милл 3, добивают летуны. Красное здесь не сплэш, а второй цвет ради того, чего у синего нет: жёсткого ремувала (Pinecone Strike 14/16, медиана 4 хардремувала) и {R}{R}-топэнда (Smaug 10/16, Gandalf 10/16) — поэтому Гор 6–9 при 8–9 Островах.
**Ветки.** Веток нет — проверено. Синий пакет «вторая карта» и красный amass не расходятся, а складываются: ≥1 карта из ОБОИХ пакетов в 11 листах из 16, листов без синего пакета — 0 из 16; главный маркер amass (Misty Mountains Raider) лежит с Апотекарём 5 раз при 4.88. Перебор всех 2^15 разбиений даёт лучшее деление 5/11 без единой эксклюзивной карты. Реальная ось — градиент манабазы (10 листов U−R ≥ +6, 6 листов ≤ +3), но и он пул не режет. Фиксируй базовый цвет (синий), а не ветку.
**Ядро.** Bilbo Baggins, Burglar 15/16 · Pinecone Strike 14/16 (1.9 копии) · Lakeshore Apothecary 13/16 (2.3 копии, один лист с 5) · Plunder the Trollshaws 13/16 · Long Lake Nuisance 11/16 · Master's Councillors 10/16 · Enchanted River's Grasp 10/16 · Smaug, the Great Calamity 10/16 · Gandalf, Spark Starter 10/16 · Óin the Brave 10/16 · Patient Instructor 9/16 · Uneasy Partings 9/16 · Ragged Short Spear 8/16.
**Связки (CONFIRMED).**
- **Lakeshore Apothecary + Plunder the Trollshaws.** Из руки в свой ход — счётчик; из ГЯ «draw two cards instead» — счётчик даже в ЧУЖОЙ ход, и это единственный способ включить Апотекаря на ходу оппонента в UR. Один картон = два каста и два счётчика, но за каст ровно ОДИН (триггер «second card», не «each card»).
- **Master's Councillors + Plunder.** Замкнутый цикл: милл на себя кладёт Plunder в ГЯ → флэшбэк тянет две → ещё милл 3 → своё кладбище добивается до «seven or more» под «+2/+0 for each graveyard» (1/3 → 3/3). Цикл одноразовый — флэшбэк экзайлит.
**Антисинергии.** Confusticate × Patient Instructor 0 из 16 при 2.25 — конкуренция за слот «лишняя карта», и все 4 листа с Confusticate стоят ровно на 13 существах при медиане 15–16 · Ragged Short Spear × Sound the Trumpets 0 при 2.0: Equip {3} «only as a sorcery» против трёх открытых на контру · Burn, Burn, Tree and Fern × Misty Mountains Raider 0 при 2.25 — сага играет от сидения, Raider окупается только атакой каждый ход · Hobbit Hole × Smaug 1 при 3.12: у Хоула нет «{T}: Add» вообще, а топ-энд стоит {5}{R}{R} · **не путать:** Councillors × Tidings of War 1 при 3.12 механической несовместимости НЕ имеет (милл сам кладёт Tidings в ГЯ под «amass 3») — расхождение цветовое, пик по этому числу не двигать · Bothersome Noisemaker в существовой паре почти не триггерит: медиана некреатурных 8.5 из 23.
**Правила пика.**
1. **UR-земли в сете НЕТ.** Дуалы есть только у GU, BR, RW, WU, BG — значит сквозное правило «утилитарная земля пары = карта в кривой» к UR не применяется, фикса не будет, третий цвет не открываем (8 из 16 листов вообще без небазовых).
2. Синий — база, красный — полноценный второй цвет: планируй 7–8 Гор (медиана 7, минимум 5), потому что 14 листов держат 1–3 карты с {R}{R}. Не «доливай пару Гор под сплэш».
3. Пейофф «второй карты» обязателен (14/16; оба листа без него — трёхцветные), Апотекаря бери в любом количестве. Энейблеров ≥7 (медиана 9) — считаются только доборы ВНЕ шага взятия. Ravenhill Flock — ДРУГОЙ пейофф: «Whenever you draw a card» ловит и шаг взятия, при 5–6 энейблерах она надёжнее.
4. Считай адвенчуры двумя картами: Smaug = Spew Flame {4}{R} на 5 урона плюс 5/5 летун за {5}{R}{R} из изгнания; Bilbo Burglar = Take a Glance {U} плюс тело с ETB-добором.
5. Pinecone Strike — 3 урона, тафнесс 4 он НЕ убивает; вторая мода бьёт по Treasure и по Axe от Iron Hills Blacksmith. Grasp (10/16) держи 1–2 копии как ответ и на бомбу, и на Армию (токен базово 0/0, аура снимает все счётчики). Amass в UR — приложение: внутри пакета работает одна связка, Goblin Plate Mail + Tidings of War (3/16).
**Границы.** n=16 — самая маленькая из расписанных пар, и 2 листа трёхцветные (гриксис, джескай), именно они единственные без пейоффа, то есть чистых Izzet фактически 14. При таком n «0 из 16 при ожидании 2» даёт p≈0.02–0.06 — раздел АНТИ здесь **предупреждения, а не запреты**, и «веток нет» читай как «на 16 листах разделения не видно». Ни одна связка блока не проходила отдельный цикл опровержения. **WEAK:** Smaug the Magnificent + Dori (Treasure при использовании ЖЕРТВУЕТСЯ — либо мана, либо +1 урона, не оба; Смауг генерит их сам; n=3); Apothecary + Long Lake Nuisance (один из десяти взаимозаменяемых recruit-энейблеров, лифт ноль); Ragged Short Spear + Councillors (эффект разовый, ETB эквипа). Скелет: 17 земель (14/16), 15–16 существ, горб на двойках (медиана 9 карт с MV 2). Utверждение «Grasp убивает Армию» выведено из текста, матчапных данных нет.

---

### RG — наземный размен на печатной силе 4 (n=14)
**План.** Валюта пары — тело силы 4: в листах 12–20 существ (медиана 17) и 4–9 тел с силой 4+ (медиана 7, минимум 4), а почти весь «ремувал» эту силу пересчитывает в убийство — Quarrel «deals damage equal to its power» без ответки, Ferocious-пейоффы при теле 4+ раздают трампл ВСЕЙ команде. Эвазии нет (медиана 1 летун на лист, 13 из 16 копий летающих — это Смауг), поэтому проходят размером и трамплом, а красный докладывает урон по кривой: Pinecone Strike 12/14, Burn, Burn, Tree and Fern (6 урона) 8/14, Spew Flame (5 урона) 8/14.
**Ветки.** Веток нет — проверено, отрицательный результат. Красный amass-пакет: ≥1 карта в 11 листах из 14. Зелёные landfall-пейоффы: ≥1 в 12 из 14. ОБА сразу — 9 из 14; только amass 2 листа, только landfall 3. На пороге «≥2 карты пакета»: amass 7, landfall 8, оба 3 при ожидании 4.0. Самые жёсткие антипары (Smaug × Troll Negotiations 0 при 2.3, Attercop × Mirkwood 0 при 2.1) на таком n получаются случайно с вероятностью ~10–20%. **RG — контрпример к сквозному правилу №7 файла «у каждой пары ровно две ветки»:** здесь фиксировать надо не ветку, а счёт тел силы 4+.
**Ядро.** Pinecone Strike 12/14 (22 копии; 10 из 12 держат ровно 2) · Quarrel 11/14 (17) · Gundabad Opportunist 10/14 (19 — самая частая неземля и базовое тело силы 4) · Smaug, the Great Calamity 8/14 (13) · Beorn, Reluctant Host 8/14 (10) · Burn, Burn, Tree and Fern 8/14 (10) · Dori, Bearer of Friends 8/14 (11) · Wargling 8/14 (11) · Hobbit Hole 7/14 (9) · Wood Elves, Misty Mountains Raider, Óin the Brave, Beorn's Hospitality, Goblin Plate Mail, Attercop, Warg Tactics — по 6/14.
**Связки (CONFIRMED).**
- **Duskwatch Hunter + Wargling.** ETB-счётчик Дускуотч кладёт на себя: 3/1 → 4/2, и порог «creature with power 4 or greater» взят ОДНОЙ картой на третий ход и **навсегда** (счётчик, а не «until end of turn»). 5 листов из 14 при 2.86. Оговорка: 4/2 умирает от любых 2 урона, порог держится, пока Дускуотч жив.
- **Bothersome Noisemaker + Tidings of War.** Tidings — некреатурный спелл под «Whenever you cast a noncreature spell, amass Goblins 1», а флэшбэк означает ВТОРОЙ каст: из руки {R} даёт 1+1, из ГЯ {3}{R} — «amass Goblins 3 instead» + 1, итого до 6 счётчиков на ОДНУ Армию с одной карты. 4 из 14 при 1.79. Шумелка триггерится от любого некреатурного и сама 2/2 — должна дожить.
- **Quarrel + Attercop.** Единственный дэтчтач вне чёрного во всём HOB → Quarrel за {1}{G} убивает ЛЮБОЕ тело, и ответного урона нет (это не fight). 4 из 14 при 4.71 — стата нулевая, механика card-specific.
**Антисинергии.** Quarrel и Warg Tactics — не ремувал в вакууме: первому нужно СВОЁ крупное тело, второй убивает «target creature **with flying**», а летунов у соперника-зеркала почти нет · Smaug × Troll Negotiations 0 из 14 при 2.29 — два дорогих ответа на один слот (Spew Flame {4}{R} и файт за {2}{G}{G}) · Gundabad Opportunist × Mirkwood 1 при 3.57 и Dori × Hobbit Hole 2 при 4.0 — тапленые и жертвенные земли против кривой 2–4, а у Гундабада «play that card until the end of your next turn» требует маны сразу · Óin × Duskwatch 0 при 2.14 — механизма в текстах нет, как правило не использовать · Ferocious-выплаты неравноценны: Nasty Little Rabbit растёт только при ЧУЖОМ теле 4+, Wargling даёт трампл всей команде, Wilderland Scrounger — счётчик каждому · антисинергия UR «Hobbit Hole × {R}{R}-топэнд» в RG НЕ повторяется: 4 из 14 при 4.0.
**Правила пика.**
1. Считай тела силы 4+ (медиана 7 копий, минимум 4) — это включатель, а не бонус. Дешевле всего порог берёт Duskwatch Hunter: 3 маны, 4/2 навсегда.
2. Quarrel (11/14) — главный ответ пары, но он платит СВОЕЙ силой: без тела 4+ это 2 урона. Pinecone Strike (12/14) — ровно 3 урона, тафнесс 4 не убивает.
3. Смауг — две карты в одной и ЕДИНСТВЕННАЯ эвазия пары: Spew Flame {4}{R} на 5 урона, потом 5/5 летун из изгнания.
4. Amass — приложение, а не план: 4 листа из 14 держат НОЛЬ амасс-карт, и внутри пакета работает только Noisemaker + Tidings.
5. Скелет: 17 земель (12/14; 16 у двух), ~8 Гор и ~7 Лесов. **RG-дуала в сете нет**; единственные небазовые — Hobbit Hole (7/14) и Mirkwood (5/14), обе тапленые/жертвенные и при кривой 2–4 стоят темпа, так что «земля вместо 23-й играбельной» здесь работает хуже, чем в UG/BR/WR/BG.
**Границы.** Исходный разбор RG пришёл обрезанным: план, ветки, ядро и две связки — из него, антисинергии и правила я досчитал по тем же 14 листам (сверка совпала точно: Pinecone 12/14 ×22, Quarrel 11/14 ×17, Смауг 8/14 ×13, Wargling×Duskwatch 5 при 2.86, Noisemaker×Tidings 4 при 1.79). n=14, один лист трёхцветный (urg_temur). При таком n «0 при ожидании 2» не доказывает ничего — все антисинергии здесь читаются по тексту, а не по числу. **WEAK:** Óin the Brave + Dori как Storied-связка (у всех листов с Óin квалифицирующих 7–12, порог включается сам и одноразово — Dori просто ещё одна легендарка); Quarrel + Gundabad Opportunist (по логике вердикта [MONO-G] Pathmaker+Quarrel: подойдёт любое крупное тело, взаимной настройки текстов нет). Всё остальное скептиком не проверялось.

---

### WG — белый ремувал плюс зелёные тела (n=7)
**План.** WG — не архетип, а остаточная пара: во всём сете **ноль золотых и гибридных карт с W и G**, WG-земли тоже нет, и на неё приходится 7 листов из 263 двухцветных трофеев (2.7%) — самая редкая пара сета. Что реально лежит в листах: белый ремувал + зелёные тела. Ответов 5–7 копий на лист (медиана 7), и это единственная пара без листа с менее чем 3 безусловными снятиями (в WU, UB, UG, BR, WR, BG такие листы есть). Эвазии нет вообще (0–1 летун), тел силы 4+ медиана 2 — выигрывают не размером и не эвазией, а тем, что каждый размен выигран, плюс мана-синками на длинной игре.
**Ветки.** Не измеримы: на n=7 все «нули» стоят при ожидании 1.3–1.7 (p > 0.15). Видно два несмешивающихся хвоста — дворф-эквип-Storied (abigscarybear 8 копий, lukash 10; у остальных пяти 1–2) и landfall-зелень (raguzzoni, silee, hotsauce по 4–5 копий; у lukash и mistersmiths по 1). Это гипотеза о двух хвостах, а не ветка: фиксировать к P2 нечего.
**Ядро.** Magnificent End 6/7 (12 копий) · Wood Elves 5/7 (11, один лист с ЧЕТЫРЬМЯ) · Hobbit Hole 5/7 (9) · Stone by Sunlight 5/7 (7) · Mirkwood Pathmaker 5/7 (6) · The Mountain-king's Return 4/7 (8) · Mirkwood Nurturer 4/7 · Guardian of the Halls 4/7 · Troll Negotiations 4/7 · Celebrate the Mountain-king 4/7 · Dwarven Provisioner 4/7 · Quarrel 3/7 · Settle the Wreckage 3/7 · Attercop 3/7 · Ori, Keeper of Songs 3/7.
**Связки.** CONFIRMED-вердиктов по WG нет ни одного — блок скептиком не проверялся, ниже механизмы по оракл-тексту, держать как гипотезы:
- **Wood Elves → Attercop / Beorn's Hospitality / Boughside Wanderers.** «Search your library for a Forest card, put that card onto the battlefield» — без «tapped» и ВНЕ ленддропа, то есть отдельный landfall-триггер плюс рамп (механизм подтверждён вердиктом [MONO-G] Thranduil's Company + Wood Elves). Ищет именно **Forest card**: Elvenking's Halls и Mirkwood не подходят.
- **Stone by Sunlight + Troll Negotiations.** Вторая мода за {1}{W} инстантом («becomes an artifact in addition to its other types and gains indestructible») превращает файт в односторонний, а «This effect doesn't end» оставляет твоё существо артефактом навсегда — ещё один квалификатор Storied. 3 из 7 при 2.9.
- **Kíli the Resourceful + Dwarven Shortsword.** Меч «create a 2/2 red Dwarf creature token, then attach this Equipment to it» — одной картой входят и Дворф, и Эквип, Кили добирает (но «only once each turn»), а при включённом Storied первый эквип за {0}. 2 листа при 0.57 — n мал.
- **Beorn's Hospitality как мана-синк.** Пока не активирована — энчант, creature-ремувал её не берёт; {5}{G}{G} превращает её в тело размером с манабазу. Тот же слот у Guardian of the Halls ({5}{G}{G}: три счётчика) — в паре без топ-энда это и есть «дорогие карты».
**Антисинергии.** Проверять по тексту, чисел здесь нет. Три «ремувала» пары стреляют не во всё: Stone by Sunlight убивает **только силу 4+**, Warg Tactics — **только летающих**, Magnificent End дёшево ({1}{W}) — **только по тапнутому**, а таппера (Gaze in Wonder) нет ни в одном листе, то есть скидку включает исключительно чужая атака. В зеркале WG (медиана 2 тела силы 4+, ноль летунов) первые два не убивают ничего. Settle the Wreckage (3/7) — карта того, кто НЕ атакует, и она рампит оппонента базовыми: в агро-лист не берём. Hobbit Hole (5/7, 9 копий) не даёт маны вообще и выводит землю ТАПНУТОЙ — при инстантах {2}{W}{W} (Settle, Thorin's Last Stand) это пропущенное окно ответа; Hobbit Hole × Settle 1 из 7 при 2.14, направление то же, но число ничего не доказывает.
**Правила пика.**
1. **В WG не идут — в неё попадают.** Ни одной золотой карты, ни одной WG-земли, 2.7% трофеев: это сигнал «оба цвета открыты», а не архетип. Оказался тут к P2 — режь план до «белый ремувал + лучшие зелёные тела» и не ищи механику.
2. Ремувал и есть план: ни один лист не опустился ниже 3 безусловных снятий, медиана 7 копий ответов. Magnificent End и Stone by Sunlight бери выше любого зелёного четырёхдропа.
3. Перед пиком ответа проверь, во что он стреляет (см. Антисинергии). Ответ на НЕсущество ровно один — Celebrate the Mountain-king (4/7).
4. Wood Elves (5/7, 11 копий) берём при ≥6 базовых Лесов (в листах 6–9) и ≥2 landfall-телах, иначе это 1/1 за три маны.
5. Скелет: 17 земель (5 из 7), существ 13–17 (медиана 14), тел силы 4+ 1–4, летунов 0–1. Топ-энда в паре нет — его заменяют мана-синки ({5}{G}{G} у Guardian of the Halls и Beorn's Hospitality, {3}{W} у Dwarven Provisioner); держи хотя бы один.
**Границы.** n=7 — это 6 wg_selesnya плюс один бант (mistersmiths), фактически по одному листу на каждую гипотезу; два листа (abigscarybear, lukash) тянут на себя всю дворф-статистику. Любое число в блоке — иллюстрация к тексту карт: самые «жёсткие» нули лежат при ожидании 1.3–1.7. Вердиктов скептика по WG нет вообще, так что раздел «Связки» — это чтение оракл-текстов, а не проверенные утверждения; статистикой не подтверждена ни одна. Доля 2.7% смешивает популярность и винрейт: правильное чтение — «в WG почти никто не финиширует 7 побед», базы проигравших и не-трофейных колод в данных нет. Отдельная поправка к сквозному тезису файла «18 земель не сыграл никто»: по всем 298 листам 18 земель встречаются 5 раз, и один из них — WG hotsauce (18 земель на 43 картах, то есть та же плотность, что 17/40)."
  },
  "workflowProgress": [
    {
      "type": "workflow_phase",
      "index": 1,
      "title": "Разбор пар"
    },
    {
      "type": "workflow_phase",
      "index": 2,
      "title": "Опровержение"
    },
    {
      "type": "workflow_phase",
      "index": 3,
      "title": "Дописать"
    },
    {
      "type": "workflow_agent",
      "index": 1,
      "label": "пара:WU",
      "phaseIndex": 1,
      "phaseTitle": "Разбор пар",
      "agentId": "a75bbc35ac7800369",
      "model": "claude-opus-5[1m]",
      "state": "done",
      "startedAt": 1786918081601,
      "queuedAt": 1786918081592,
      "attempt": 1,
      "lastToolName": "StructuredOutput",
      "lastToolSummary": "ГЛАВНОЕ: n=25 — это 19 листов wu_azorius_* ПЛЮС 6 трёхцветн…",
      "promptPreview": "Допиши разбор пары WU для сета The Hobbit (HOB). Эта пара НЕДОКРЫТА: в hob_patterns.md
про неё одна-три строки, хотя трофейных листов достаточно. Из-за этого живой драфт, уходя
в эту пару, остаётся без знания — это выявила переигровка драфта 17.08.2026.

ДАННЫЕ:
- Статистика по парам: /private/tmp/claude-501/-Users-wolfeatyou/f1b79ede-89ba-4f2b-9896-2a448c3cde54/scratchpad/pairs6.json (ключ "WU").…",
      "lastProgressAt": 1786919048206,
      "tokens": 159372,
      "toolCalls": 40,
      "durationMs": 966604,
      "resultPreview": "{"anti":[{"cards":["Enchanted River's Grasp","Magnificent End"],"why":"НЕ связка, а ложный кандидат. Grasp тапает ТОЛЬКО собственного носителя («When this Aura enters, tap enchanted creature»), а тот уже «loses all abilities and doesn't untap during its controller's untap step» — то есть выключен. Скидка Magnificent End («costs {3} less to cast if it targets a tapped creature») применима лишь к су…"
    },
    {
      "type": "workflow_agent",
      "index": 2,
      "label": "пара:UB",
      "phaseIndex": 1,
      "phaseTitle": "Разбор пар",
      "agentId": "a9cfc58c67b0bb271",
      "model": "claude-opus-5[1m]",
      "state": "done",
      "startedAt": 1786918081601,
      "queuedAt": 1786918081592,
      "attempt": 1,
      "lastToolName": "StructuredOutput",
      "lastToolSummary": "UB",
      "promptPreview": "Допиши разбор пары UB для сета The Hobbit (HOB). Эта пара НЕДОКРЫТА: в hob_patterns.md
про неё одна-три строки, хотя трофейных листов достаточно. Из-за этого живой драфт, уходя
в эту пару, остаётся без знания — это выявила переигровка драфта 17.08.2026.

ДАННЫЕ:
- Статистика по парам: /private/tmp/claude-501/-Users-wolfeatyou/f1b79ede-89ba-4f2b-9896-2a448c3cde54/scratchpad/pairs6.json (ключ "UB").…",
      "lastProgressAt": 1786919095415,
      "tokens": 161783,
      "toolCalls": 33,
      "durationMs": 1011847,
      "resultPreview": "{"pair":"UB","n":23,"plan":"Пара выигрывает кантрипами, а не доской: в КАЖДОМ из 23 листов 7–12 копий карт, дающих лишнее дро (медиана 9, минимум 7 — исключений нет), и одно и то же дро делает три работы сразу — находит снятие (медиана 3 безусловных + эдикт Crude Bent Blade в 15/23 + тук Uneasy Partings в 10/23), кормит счётчики Lakeshore Apothecary (17/23) и милл Master's Councillors, и через rec…"
    },
    {
      "type": "workflow_agent",
      "index": 3,
      "label": "пара:WB",
      "phaseIndex": 1,
      "phaseTitle": "Разбор пар",
      "agentId": "aaaea953953ca4c3e",
      "model": "claude-opus-5[1m]",
      "state": "done",
      "startedAt": 1786918081601,
      "queuedAt": 1786918081592,
      "attempt": 1,
      "lastToolName": "StructuredOutput",
      "lastToolSummary": "WB",
      "promptPreview": "Допиши разбор пары WB для сета The Hobbit (HOB). Эта пара НЕДОКРЫТА: в hob_patterns.md
про неё одна-три строки, хотя трофейных листов достаточно. Из-за этого живой драфт, уходя
в эту пару, остаётся без знания — это выявила переигровка драфта 17.08.2026.

ДАННЫЕ:
- Статистика по парам: /private/tmp/claude-501/-Users-wolfeatyou/f1b79ede-89ba-4f2b-9896-2a448c3cde54/scratchpad/pairs6.json (ключ "WB").…",
      "lastProgressAt": 1786919237784,
      "tokens": 167362,
      "toolCalls": 40,
      "durationMs": 1154216,
      "resultPreview": "{"pair":"WB","n":18,"plan":"Пара размянивает один-в-один плотным убийством (медиана 5 копий ремувала на лист, min 2, max 9) и выигрывает довеском, который этот ремувал сам оставляет на столе: Crude Bent Blade 12/18 (эдикт при выходе + эквип +2/+1 + артефакт под Storied) и Stir Up Trouble 11/18 («Destroy target creature» за {B}) убивают и одновременно включают Dreaded Bat-Cloud и кормят Stir Up. До…"
    },
    {
      "type": "workflow_agent",
      "index": 4,
      "label": "пара:UR",
      "phaseIndex": 1,
      "phaseTitle": "Разбор пар",
      "agentId": "a18ca4c9b63259f06",
      "model": "claude-opus-5[1m]",
      "state": "done",
      "startedAt": 1786918081601,
      "queuedAt": 1786918081592,
      "attempt": 1,
      "lastToolName": "StructuredOutput",
      "lastToolSummary": "UR",
      "promptPreview": "Допиши разбор пары UR для сета The Hobbit (HOB). Эта пара НЕДОКРЫТА: в hob_patterns.md
про неё одна-три строки, хотя трофейных листов достаточно. Из-за этого живой драфт, уходя
в эту пару, остаётся без знания — это выявила переигровка драфта 17.08.2026.

ДАННЫЕ:
- Статистика по парам: /private/tmp/claude-501/-Users-wolfeatyou/f1b79ede-89ba-4f2b-9896-2a448c3cde54/scratchpad/pairs6.json (ключ "UR").…",
      "lastProgressAt": 1786918924570,
      "tokens": 143384,
      "toolCalls": 34,
      "durationMs": 841002,
      "resultPreview": "{"pair":"UR","n":16,"plan":"UR — синебазовое темпо-вэлью на «второй карте за ход»: 14 из 16 листов держат хотя бы один пейофф (Lakeshore Apothecary 13, Master's Councillors 10, Ravenhill Flock 5) при медиане 9 добор-энейблеров на лист (min 5, max 11), и каждый лишний добор превращается в постоянный +1/+1 счётчик или милл 3, а летуны (Long Lake Nuisance 11/16) добивают. Красное здесь не сплэш, а по…"
    },
    {
      "type": "workflow_agent",
      "index": 5,
      "label": "пара:RG",
      "phaseIndex": 1,
      "phaseTitle": "Разбор пар",
      "agentId": "a98b60c8c32c5b5c0",
      "model": "claude-opus-5[1m]",
      "state": "done",
      "startedAt": 1786918081602,
      "queuedAt": 1786918081593,
      "attempt": 1,
      "lastToolName": "StructuredOutput",
      "lastToolSummary": "RG",
      "promptPreview": "Допиши разбор пары RG для сета The Hobbit (HOB). Эта пара НЕДОКРЫТА: в hob_patterns.md
про неё одна-три строки, хотя трофейных листов достаточно. Из-за этого живой драфт, уходя
в эту пару, остаётся без знания — это выявила переигровка драфта 17.08.2026.

ДАННЫЕ:
- Статистика по парам: /private/tmp/claude-501/-Users-wolfeatyou/f1b79ede-89ba-4f2b-9896-2a448c3cde54/scratchpad/pairs6.json (ключ "RG").…",
      "lastProgressAt": 1786918994592,
      "tokens": 137409,
      "toolCalls": 32,
      "durationMs": 911022,
      "resultPreview": "{"pair":"RG","n":14,"plan":"RG — наземный размен, где валюта это печатная сила 4: в листах 12–20 существ (медиана 17 копий) и 4–9 тел с силой 4+ (медиана 7, минимум 4), а почти весь ремувал пары пересчитывает эту силу в убийство — Quarrel «deals damage equal to its power» без ответки, Ferocious-пейоффы (Wargling) при теле 4+ раздают трампл ВСЕЙ команде. Эвазии у пары нет (летунов в корпусе всего т…"
    },
    {
      "type": "workflow_agent",
      "index": 6,
      "label": "пара:MONO",
      "phaseIndex": 1,
      "phaseTitle": "Разбор пар",
      "agentId": "a781721741a0351d6",
      "model": "claude-opus-5[1m]",
      "state": "done",
      "startedAt": 1786918081602,
      "queuedAt": 1786918081593,
      "attempt": 1,
      "lastToolName": "StructuredOutput",
      "lastToolSummary": "n=34 по pairs6.json против 35 файлов на диске: из статистик…",
      "promptPreview": "Допиши разбор пары MONO для сета The Hobbit (HOB). Эта пара НЕДОКРЫТА: в hob_patterns.md
про неё одна-три строки, хотя трофейных листов достаточно. Из-за этого живой драфт, уходя
в эту пару, остаётся без знания — это выявила переигровка драфта 17.08.2026.

ДАННЫЕ:
- Статистика по парам: /private/tmp/claude-501/-Users-wolfeatyou/f1b79ede-89ba-4f2b-9896-2a448c3cde54/scratchpad/pairs6.json (ключи "W"…",
      "lastProgressAt": 1786919009616,
      "tokens": 159160,
      "toolCalls": 39,
      "durationMs": 926047,
      "resultPreview": "{"anti":[{"cards":["Down, Down to Goblin-town","Mirkwood","Gnashing of Teeth","Duskwatch Hunter","The Chief Warg","Azog, Moria's Ruin"],"why":"Раздел веток моно-B, самые жёсткие числа группы. Down, Down to Goblin-town (7 листов) × Mirkwood (4) = 0 при ожидании 2.2; × The Chief Warg (3) = 0 при 1.6; × Duskwatch Hunter (7) = 1 при 3.8. Gnashing of Teeth (6) × Mirkwood = 0 при 1.8; × Duskwatch = 1 пр…"
    },
    {
      "type": "workflow_agent",
      "index": 7,
      "label": "скептик:1",
      "phaseIndex": 2,
      "phaseTitle": "Опровержение",
      "agentId": "a284e358602ba9070",
      "model": "claude-opus-5[1m]",
      "state": "done",
      "startedAt": 1786919237799,
      "queuedAt": 1786919237791,
      "attempt": 1,
      "lastToolName": "StructuredOutput",
      "promptPreview": "Ты СКЕПТИК. Опровергни заявленные связки сета HOB по текстам карт.
Тексты: /Users/wolfeatyou/.claude/skills/mtg-draft-helper/hob_set.json (python3/grep). Листы: /Users/wolfeatyou/.claude/skills/mtg-draft-helper/ref_decks/hob/*.txt.

Для каждой: есть ли в оракл-текстах РЕАЛЬНОЕ взаимодействие, или это две карты одного
архетипа, часто стоящие рядом? Второе — REFUTED, каким бы ни был lift. Цитаты про…",
      "lastProgressAt": 1786919774951,
      "tokens": 64739,
      "toolCalls": 16,
      "durationMs": 537143,
      "resultPreview": "{"results":[{"claim":"[WU] Patient Instructor + Lakeshore Apothecary — recruit как источник второй карты за ход","verdict":"CONFIRMED","reason":"Тексты процитированы дословно. Взаимодействие настоящее и точное: recruit = «Draw a card, then discard a card», Instructor — не-флэш 3-дроп, значит его добор всегда идёт ПОСЛЕ шага взятия → это буквально «your second card each turn» → счётчик на Апотекаря…"
    },
    {
      "type": "workflow_agent",
      "index": 8,
      "label": "скептик:2",
      "phaseIndex": 2,
      "phaseTitle": "Опровержение",
      "agentId": "ab13523e826b110cc",
      "model": "claude-opus-5[1m]",
      "state": "done",
      "startedAt": 1786919237804,
      "queuedAt": 1786919237791,
      "attempt": 1,
      "lastToolName": "StructuredOutput",
      "promptPreview": "Ты СКЕПТИК. Опровергни заявленные связки сета HOB по текстам карт.
Тексты: /Users/wolfeatyou/.claude/skills/mtg-draft-helper/hob_set.json (python3/grep). Листы: /Users/wolfeatyou/.claude/skills/mtg-draft-helper/ref_decks/hob/*.txt.

Для каждой: есть ли в оракл-текстах РЕАЛЬНОЕ взаимодействие, или это две карты одного
архетипа, часто стоящие рядом? Второе — REFUTED, каким бы ни был lift. Цитаты про…",
      "lastProgressAt": 1786919839278,
      "tokens": 72810,
      "toolCalls": 17,
      "durationMs": 599992,
      "resultPreview": "{"results":[{"claim":"[WU] Bilbo, Luckwearer + Bard the Bowman — неблокируемый Билбо даёт вторую карту каждый ход, Бард кладёт счётчик + лайфлинк","verdict":"CONFIRMED","reason":"Цитаты дословны. Связь текстовая и причинная: «Bilbo can't be blocked» → боевой урон гарантирован → «draw a card, then discard a card»; в свой ход это ровно ВТОРАЯ карта (первая — из шага взятия), что и есть условие Барда…"
    },
    {
      "type": "workflow_agent",
      "index": 9,
      "label": "скептик:3",
      "phaseIndex": 2,
      "phaseTitle": "Опровержение",
      "agentId": "ae073fdad2083e856",
      "model": "claude-opus-5[1m]",
      "state": "done",
      "startedAt": 1786919237808,
      "queuedAt": 1786919237791,
      "attempt": 1,
      "lastToolName": "StructuredOutput",
      "promptPreview": "Ты СКЕПТИК. Опровергни заявленные связки сета HOB по текстам карт.
Тексты: /Users/wolfeatyou/.claude/skills/mtg-draft-helper/hob_set.json (python3/grep). Листы: /Users/wolfeatyou/.claude/skills/mtg-draft-helper/ref_decks/hob/*.txt.

Для каждой: есть ли в оракл-текстах РЕАЛЬНОЕ взаимодействие, или это две карты одного
архетипа, часто стоящие рядом? Второе — REFUTED, каким бы ни был lift. Цитаты про…",
      "lastProgressAt": 1786919768433,
      "tokens": 68012,
      "toolCalls": 17,
      "durationMs": 529146,
      "resultPreview": "{"results":[{"claim":"1. [WU] Bilbo, Luckwearer + Eagle's Rescue","verdict":"CONFIRMED","reason":"Тексты дословно верны: Eagle's Rescue — «Enchanted creature gets +2/+2 and has flying» + «{2}{W/U}{W/U}: Return this card from your graveyard to the battlefield attached to target creature you control with power 1 or less»; Bilbo, Luckwearer — 1/1, «Bilbo can't be blocked», «Whenever Bilbo deals comba…"
    },
    {
      "type": "workflow_agent",
      "index": 10,
      "label": "блоки",
      "phaseIndex": 3,
      "phaseTitle": "Дописать",
      "agentId": "ae1337d3f2d4f7852",
      "model": "claude-opus-5[1m]",
      "state": "done",
      "startedAt": 1786919839287,
      "queuedAt": 1786919839286,
      "attempt": 1,
      "lastToolName": "Bash",
      "lastToolSummary": "cd /private/tmp/claude-501/-Users-wolfeatyou/f1b79ede-89ba-…",
      "promptPreview": "Собери markdown-блоки для шести пар HOB, чтобы дописать их в hob_patterns.md рядом с
уже готовыми UG/BR/WR/BG. Формат ровно как у существующих блоков — посмотри
/Users/wolfeatyou/.claude/skills/mtg-draft-helper/hob_patterns.md, раздел «## По парам».

ВХОД:
[
 {
  "anti": [
   {
    "cards": [
     "Enchanted River's Grasp",
     "Magnificent End"
    ],
    "why": "НЕ связка, а ложный кандидат. Gr…",
      "lastProgressAt": 1786920722492,
      "tokens": 157669,
      "toolCalls": 35,
      "durationMs": 883205,
      "resultPreview": "### WU — recruit и «вторая карта за ход» (n=25)
**План.** Почти каждая карта делает два дела сразу: recruit («Draw a card, then discard a card. If you discarded a nonland card, create a 1/1 white Human Soldier creature token») стоит в **25 из 25** листов (медиана 5 копий, минимум 3) и одним триггером даёт тело, фильтрует руку и служит «второй картой за ход» для Lakeshore Apothecary (17/25), Bard t…"
    }
  ],
  "totalTokens": 1291700,
  "totalToolCalls": 303
}

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