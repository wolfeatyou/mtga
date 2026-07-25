# MSH — История партий (лог с причиной результата)

Ведётся после каждого `analyze_game.py`. **Только проверенное по логу** (см. память `mtg-analyze-game-accuracy`) — жизни/борд/GY реслайсить, не по памяти. Причина категоризирована, чтобы ловить ПАТТЕРНЫ проигрышей во времени.

**🏁 ФОРМАТ: Premier draft — ПРОГОН ДО 3 ПОРАЖЕНИЙ (или 7 побед).** Играем всегда до 3 losses. Лог кросс-прогонный (деки менялись между прогонами); отслеживать W–L ТЕКУЩЕГО прогона, при новом драфте — новый прогон.

**▶ ПРОГОН ЗАВЕРШЁН (WU Heroes tempo/мидрейндж, Premier) 17.07: 2W–3L.** Дека — Cap Living Legend / Mighty Thor / Jennifer / Wiccan якоря · 16 существ · интеракция: **3 Frozen in Ice (тап-даун, НЕ убийство)**, Red Guardian (условный kill), Depower, Helicarrier Strike, We Say Thee Nay · Futurist Forge (добор) · 17 земель (9 Island / 7 Plains / Avengers Tower). **Винкон = ВОЗДУШНАЯ гонка** (Doombot/Thor/Wiccan флаеры) vs медленное. **🔑🔑 ПАТТЕРН 5 игр ОДНОЗНАЧНЫЙ: 2W оба vs медленное durdle (RACE по воздуху) · ВСЕ 3L vs GO-WIDE+памп/лайфгейн (G1 RW-анфем Political Triumph · G4 GW токены+Doc Samson-лайфгейн · G5 GW Civil War-памп+Captain Marvel-лайфгейн, опп до 30).** Дека НЕ плохая — у неё ОДИН структурный провал: **go-wide без свипа + лайфгейн выключает воздушную гонку + наземный клок валят их фэтти.** Матчап камень-ножницы-бумага, «бумага» (go-wide) выпала 3 из 5. **Вывод для ДРАФТА:** WU-Heroes голодна на анти-ширину — тяни настойчивее hard-removal / свип / дешёвый эвейжн (гнать ДО лайфгейна), иначе этот матчап забирает прогоны на сборке. [[mtg-msh-evasion-and-removal]]
| # | Дата | На игре | Дека | Оппонент | Рез | Причина (осн. + доп.) |
|---|------|---------|------|----------|-----|------------------------|
| G5 | 17.07 | on play | WU Heroes tempo | **GW go-wide + памп + лайфгейн (РАН-ЕНДЕР)**: **The Super Hero Civil War (×3, записанный worst-matchup danger)**, Hercules, Abomination, She-Hulk Jade Defender, White Tiger/Stark Executive токены, **Captain Marvel Earth's Protector (лайфгейн → опп 12→30)** | ❌ L | **OUT-ENGINED go-wide + LIFEGAIN — 3-й проигрыш ТОГО ЖЕ класса.** Был ВПЕРЕДИ рано (We Say Thee Nay законтрил Wolverine, Cap+Jennifer чипили опп 20→12), но: (1) **Captain Marvel-лайфгейн вернул опп 12→18→24→30 = гонка мертва**; (2) **клок наземный (Cap/Jennifer/Red Guardian/Coulson) → валят их фэтти** (Hercules/Abomination/She-Hulk), единственный флаер Drone Flock пришёл T18; (3) **Frozen ×3 = тап-даун vs ширину бесполезен**; (4) Civil War пампил их борд ×3. Финал: альфа 5→2, опп 30. Mighty Thor скастована T28 — поздно. ✅ Верно: контр Wolverine, ранний чип, блоки. **НЕ пилот — записанный worst-matchup, 3-й раз.** |
| G4 | 17.07 | on draw | WU Heroes tempo | **GW go-wide + лайфгейн + движок**: Ant-Man's Army/Black Panther/White Tiger токены, **Baxter Building (×3)**, Agents of S.H.I.E.L.D. (×3), Doc Samson (лайфгейн), Titania, Guerrilla Gorilla | ❌ L | **OUT-ENGINED go-wide + LIFEGAIN — худший матчап деки.** Опп ушёл 20→22→**29** (Doc Samson) = гонка ОТКЛЮЧЕНА, а ширину грайндить нечем (0 свипа). **Бомбу убили:** Mighty Thor умерла T9 под Punishing Punch → воздушный клок исчез. **Флаеры (Doombot, Drone Flock) застряли в руке** — на столе остались наземные value-тела (Coulson/H.E.R.B.I.E./Hero in Training), которые go-wide просто перечисляет. Финал: 1 существо vs 7, ты на 2. ✅ Верно: Red Guardian убил Guerrilla Gorilla, блоки держали жизнь. **НЕ пилотный слив — это записанный worst-matchup (GW go-wide+lifegain), тот же класс что G1.** |
| G3 | 17.07 | on draw | WU Heroes tempo | UW value (A.I.M. Synthoids, Echo, Nick Fury-типаж) — **сдался на 3-м ходу** | ✅ W | **МУЛИГАН СЫГРАН ВЕРНО (сверено по грпИд).** Опенер (7): 3 земли + Doombot{U}/Bold Biochemist{1}{U}/Frozen{2}{U}/Red Guardian{2}{W} — **все 3 земли = Plains (grpId 105174=SubType_Plains), 0 Island → 3 из 4 спеллов (весь синий) НЕкастуемы, только Red Guardian живой = mono-color-mismatch → мулиган обязателен.** Оставленная 6/7 скурвилась идеально: Coulson T2 → Maria Hill+Doombot T3 (оба цвета работали), опп сдался. Классика записанной слабости WU (single-color клумпы стрендят пол-деки). |
| G2 | 17.07 | on play | WU Heroes tempo | **Медленный UW durdle/value**: Viv Vision ×2, Nick Fury + Agents of S.H.I.E.L.D., Wonder Man, Surveillance Room — всё НАЗЕМНОЕ/медленное | ✅ W | **RACE-ПОД + DISRUPT — идеальный режим деки.** Жизнь **20 всю партию**, опп 20→4→добит. Линия: Doombot T1 чипит → **We Say Thee Nay! контрит K'un-Lun Warrior** (темпо) → Mighty Thor T7, её атак-триггер (exile+return tapped, ×2) **тапал их блокера каждый раз** = воздух чист → альфа T11 Doombot(power-up 4/4)+Thor+Wiccan, все ФЛАЕРЫ, 15→4. Опп durdle'ил value-телами (все наземные) → не блокировал воздух и не успел собраться. Красногвардеец+Jennifer остались в руке (не понадобились — воздух добил). **Пилот чистый.** |
| G1 | 17.07 | on play | WU Heroes tempo | **RW Hero go-wide**: Daredevil Man Without Fear, Hawkeye Master Marksman + Young Avenger, Agent of Atlas (prowess), **Political Triumph (движок ×6 — go-wide анфем)**, Super Villain Lockup (exile), Borough Backup токены | ❌ L | **OUT-ENGINED (go-wide) + STRUCTURAL + DRAW.** Был ВПЕРЕДИ рано (Doombot T1 чипил опп до 15, ты на 20), но: (1) **клок = один 1/1 флаер** — Super Villain Lockup заэкзайлил Doombot и клок испарился; (2) **body-light + blue-heavy рука** — белое включилось поздно (Jennifer T9, Red Guardian T12, Hero in Training T15), ранняя защита тонкая; (3) **Frozen ×2 = тап-даун одного тела бесполезен vs ширина** — опп бил остальными четырьмя; (4) **Political Triumph ×6** = скрай на каждое существо + анфем +1/+1 всей команде, неинтерактивен в мейне. Финал: 2 существа vs 5, ты 6 / опп 15. ✅ Верно: Red Guardian из флеша убил Daredevil (их лучшую угрозу). **НЕ пилотный слив — дека софт к go-wide + слабая рука.** 🔑 vs go-wide: гони эвейжном ДО анфема ИЛИ ты проиграл — грайндить нечем (нет свипа). |

**▶ ПРОГОН ИДЁТ (GW Storm/Hero + U-сплеш, Traditional Draft, 2-й акк) 16.07: 1W–1L.** Дека — `msh_gw_deck.txt`: 17 существ · **всего 3 removal** (Go Nuts, Red Guardian, Trickster's-сплеш) · якоря Storm/Jennifer/Ka-Zar · 17 земель + U-сплеш (7 источников: Pym ×2, Hangar, Island, Baxter, Skrull ×2, Quinjet). Голдфиш: существо к T2 **52.8%** · **removal к T3 37.1%** (против 79–81% у наших WU/WB!) · скрю 4.1%. Оценка на сборке — **C+ ≈ 5.5/10: потолок есть (3 бомбы), пол низкий (removal вдвое хуже прошлых дек)**.
| # | Дата | На игре | Дека | Оппонент | Рез | Причина (осн. + доп.) |
|---|------|---------|------|----------|-----|------------------------|
| G2 | 16.07 | **on draw** · кип 3 земли + 0 ранней игры | GW Storm/Hero + U-сплеш | **WU tempo**: Crowd of True Believers (×3), Captain America Living Legend (×2), **Kree Commandos (2/1 флаер)**, Aerial Doombot, Patriot (×2), Spider-Man To the Rescue, Justice | ❌ L | **PILOT (removal не в флаер) + STRUCTURAL (нет ранней игры).** 🔑 **ГЛАВНАЯ ОШИБКА — Go Nuts! (T10) убил Crowd of True Believers (1/2 НАЗЕМНЫЙ support), а надо было Kree Commandos (2/1 ФЛАЕР).** Drone Flock 3/3 стоял нетапнутым и убивал Kree в fight без потерь. **Kree потом нанёс ~11 урона** (T9: 3 с prowess · T11: 2 · T13: 2 · T15: 4 с пампом Patriot) — ровно наш лайфтотал, умерли на 2. Нарушено записанное правило «чужой флаер убирай ПЕРВЫМ, не трать removal на наземку, которую и так блокируешь». **Доп. BUILD:** кип 3 земли + Drone Flock(4)/Red Guardian(3)/Ka-Zar(5)/Dinosaur(6) — **дешевейшая карта 3 маны, 0 ранней игры** vs опп на игре с T1-крипом → это те самые 52.8% существа-к-T2. **Доп. СПЛЕШ:** **Trickster's застрял в руке** на 2 жизнях (финальная рука: Royal Guard/Trickster's/Hero in Training) — документированная ловушка тонкого U-сплеша критического removal. ✅ Верно: Red Guardian из флеша снял Cap America Living Legend (их движок) |
| G1 | 16.07 | on play | GW Storm/Hero + U-сплеш | WU tempo: **Political Triumph (движок ×5)**, Raft Security Officer ×3, Ultron Drone, Kree Commandos, Mockingbird, Borough Backup | ✅ W | **ENGINE+HOSER.** 🔑 **Ant-Man, Colony Commander — способность ×5, MVP-класс токен-движок** (на сборке я оценил его как «посредственный голд GIH 53.9 / IWD +0.1» — **недооценил, в бою это двигатель**). **Storm сработал как ХОСЕР, не бита:** у оппа Kree Commandos (2/1 флаер) + Aerial Doombot — «flying не может атаковать тебя» выключил их клок полностью. **Giant Growth-блоуаут:** Ultron Drone заблокировал Undercover Skrull → памп убил блокера бесплатно. Финал: ты 17, опп 5. Storm скастован T13 и закрыл партию |

**▶ ПРОГОН ЗАВЕРШЁН (WB removal-мидрейндж + эквип-клок, Premier, 2-й акк) 16.07: 2W–3L.** 🔑 **ВСЕ 3 поражения — ОДНА болезнь: ответы есть, УБИТЬ нечем** (G2: 8 существ vs 1; G4: 20→5 по воздуху; G5: загнал до 11 и встал). Оценка на сборке «B≈6.5, пол трофейный / потолка нет» **подтверждена 5 партиями — потолок и был причиной вылета**. Обе победы — эквип-клок (Yellowjacket 4/5 fly; Winter Soldier 6/4 removal-proof), обе против мулиганивших. **Корень в ДРАФТЕ:** (1) **P1P1 голд Winter Soldier {W}{B} залочил пару до сигналов** при равном моно (Agent 13 GIH 59.7 vs 59.6) — нарушено своё правило «colorless>моно>голд»; (2) **синий тёк ВЕСЬ драфт (5 ⚑-баннеров), Giant-Sized Flying Ant пасован дважды → в G4 эта дека нас и переехала**; (3) финишёр в пуле не форсился. **Следующий драфт: (а) P1P1 — гибкость, не голд; (б) пивот по 2-му U-баннеру до P1P10, пока пул ≤9 карт; (в) финишёр/потолок ВЫШЕ N-го removal.** Дека — `msh_my_deck.txt`: 12 существ + 2 Hero-токена · 7 removal (Web Up, Hour of Defeat, Murdock's ×2, Helicarrier ×2, Widow's Bite) · Spy Kit + Vibranium Daggers · Avengers Assemble (1-of) · 17 земель. Голдфиш: существо к T2 69.9% · **removal к T3 81.4%** (плотнее трофейной UB) · скрю 4% · флуд 0%. Оценка на сборке — **B ≈ 6.5/10: пол трофейный, потолка нет** (макс. тело 3/3, финишёра в пуле не было; Avengers Assemble кастуется лишь в **22% партий к T7** — измерено, планом быть не может).
| # | Дата | На игре | Дека | Оппонент | Рез | Причина (осн. + доп.) |
|---|------|---------|------|----------|-----|------------------------|
| G5 | 16.07 | on draw · **мул до 6** · опп тоже мулиганил | WB removal-мидрейндж | **WU tempo/equipment (сильная)**: Colleen Wing, Iron Lad, **Captain America Wings of Freedom**, **Luke Cage (indestructible, ×3)**, **The Mighty Thor Jane Foster**, Super Villain Lockup, **Spy Kit (×8!) + Vibranium Daggers (×2)** — НАШ ЖЕ эквип-пакет | ❌ L | **OUT-VALUED + BUILD (нет потолка). Ран-ендер 2→3.** **Пилот чист, играл хорошо:** мул верный (2 земли, **0 существ**, Murdock's ×2 мёртвые рано); **все 3 removal идеально в цель** — Web Up→Colleen Wing (их клок, вынес 7), Helicarrier→Iron Lad, **Widow's Bite→Captain America** (задокументированная гл. цель матчапа). Загнал опп **20→11**. **И встал:** опп откачал до 13 (Crowd of True Believers ×2 + Luke Cage лайфгейн), вылез **Luke Cage — indestructible** (Hour of Defeat по нему пустой, Web Up уже потрачен), затем Mighty Thor. Финал: их 4 существа + 3 эквип-перманента vs наш Whiplash. **У нас 1 безусловный эксайл (Web Up) на их 4 must-answer угрозы.** Avengers Assemble пришла T20 — поздно и в пустой борд. **Ирония: их дека гоняла НАШ эквип-пакет (Spy Kit ×8) — пакет рабочий, просто у них тела лучше** |
| G4 | 16.07 | on play (ходы 1/3/5…) · **мул до 6** · опп тоже мулиганил | WB removal-мидрейндж | **UWr tempo-ВОЗДУХ (это наши пасованные синие!)**: Aerial Doombot {U} 1/1 fly, **Giant-Sized Flying Ant** {3}{U} 3/2 flash-fly, **Thor Odinson** 4/4 fly/vig/двойной prowess, **Captain America Wings of Freedom** 3/1 fly/FS/ward, Depower, Super Suit (flash), HYDRA Assault Robot | ❌ L | **STRUCTURAL-AIR + DRAFT (скормили лейн).** 🔑 **ВСЕ их угрозы — флаеры; наш борд весь наземный** (Synthoids 1/3, Spider-Woman 1/4, Brave Brawler 2/1) → **0 блоков, 20→5 весь урон по воздуху**, опп стоял 16–20. **Пилот чист:** мул верный (2 земли + Web Up/HERBIE/Drone Flock/Avengers = 1 кастуемая карта); Helicarrier→HYDRA Robot (пинг-движок) верно; **Hour of Defeat→Thor** (бомба+флаер) верно; атака Brave Brawler 4/3 в Cap 3/1 FS была математически выиграна — перевернул **Super Suit из флеша**. **ДРАФТ-ПРИЧИНА:** их дека = синий, который колесил к нам **весь драфт** (⚑ПИВОТ/КОЛЕСО по U сработал **5 раз**: P1P7, P1P10, P2P6, P2P9, P3P6/P3P7; **Giant-Sized Flying Ant пасовали ДВАЖДЫ** — сегодня вынес ~9). Дверь закрыл **P1P1 голд Winter Soldier {W}{B}** (лочит пару до сигналов) при равном моно-варианте **Agent 13 {2}{W} GIH 59.7 vs 59.6** — нарушено своё же правило «голд P1P1 только если ЗАМЕТНО выше; colorless>моно>голд». **BUILD:** в мейне 3 флаера, на скамье ещё 3 (Unliving Legionnaire 3/2 fly, Kree Commandos ×2 2/1 fly) — против воздуха наземное тело = 0 |
| G3 | 16.07 | on draw (ходы 2/4/6…) · **опп мулиганил** | WB removal-мидрейндж | **RG/Naya removal-тяжёлая**: Lightning Strike, **Punishing Punch ×2**, Daredevil (клок, ×3), **Storm Windrider** (анти-флаер хосер), Kree Sentinel, Go Nuts! | ✅ W | **RESILIENT-CLOCK + DISRUPT.** 🔑 **Опп потратил 3 removal в наши тела (Lightning Strike→Whiplash на стеке экипа, Punishing Punch→Ronin, Punishing Punch→Winter Soldier) — и клок не умер:** Winter Soldier **вернулся из GY** ({3}{W}{B}), **Vibranium Daggers пережили смерть носителя и перевесились** → **6/4 vigilance menace** (2/2 +2/+2 от Daggers +2/+0 за эквип) → 6+6 урона, опп 18→12→6, сдался. **Подтверждено: эквип как removal-proof клок** — тезис из сборки сработал в бою. **Ключевой ход:** опп кастует **Go Nuts! (fight)** → в ответ **Widow's Bite** → **умирает Storm Windrider** (их же спелл убил их хосера, который выключал весь наш воздух). Ты 16, финал 3 существа vs 1. ⚠️ Опп мулиганил, единственный клок — Daredevil; но 4 интеракции разыграл и всё равно проиграл → **evidence реальное** |
| G2 | 16.07 | **on play** (ходы 1/3/5/7…) · **опп тоже мулиганил** | WB removal-мидрейндж | **BG/Villain go-wide-движок**: Doctor Doom (2× Doombot 3/3 + indestructible + добор в энд-степ), **Madame Masque** (×4), Titania ×2 (5/5 ward), Kree Sentinel 5/5 reach, Ninja of the Hand | ❌ L | **OUT-ENGINED (худший матчап, 5-й раз) + PILOT (мулиган) + BUILD (нет свипа).** 🔑 **Движок = Doom+Masque:** добор Doom'а в энд-степ = «вторая карта за ход» → Masque клепает 2/1 menace **каждый ход** (Masque ×4, Doom ×3) → финал **8 существ vs 1**. Не 5/5-шки убили. **PILOT-1 (главная):** сброшена кипабельная рука — **4 земли + A.I.M. Synthoids + Klaw + Hour of Defeat** (два тела + removal, на игре) → за 8 ходов скастовано **ОДНО существо** (Brave Brawler T3). **PILOT-2:** Hour of Defeat (T15) — **никто не умер**: Doom indestructible при Doombot-артефактах, destroy по нему пустой. **PILOT-3:** **Web Up (единственный exile = единственный ответ на indestructible Doom) потрачен на Titania T7** — защитимо (5/5 давила), но движок сносить стало нечем. **PILOT-4:** ward Titania оплачен **Helicarrier Strike** (живое removal) — повтор урока 02.07 (питчить землю/худшее). Avengers Assemble (T11) пустая — 1 существо на столе |
| G1 | 16.07 | **on play** (ходы 1/3/5/7/9) | WB removal-мидрейндж | Синяя дека — за всю игру появилось **1 существо** (Atlantean Cavalry, умерло т9) | ✅ W | **VARIANCE (скрю оппа) + EQUIP-CLOCK.** Опп за 5 своих ходов **не скастовал ничего**, ты **не получил урона** (20/20 все 10 ход.), финал: 0 существ у него. Выигрышная линия: **Yellowjacket (1/2 флаер) + Spy Kit + Vibranium Daggers = 4/5 флаер к T4** → 2+4+4 = 10 урона за 3 атаки (Spy Kit ×4 актив.). ⚠️ **Тезис деки НЕ проверялся: 0 removal скастовано** (Murdock's/Hour of Defeat/Helicarrier остались в руке), Avengers Assemble не пришёл. **Evidence почти нулевое** — опп не играл |

**▶ ПРОГОН ЗАВЕРШЁН (tempo-эвейжн): 6W–3L — трофей упущен на 1 победу.** Старт 0–2 мягкой серединой → рефокус в tempo-эвейжн → **6W подряд (comeback)** → проигрыш G10 (OUT-ENGINED vs UG counters + клунки-кип). **Отличный ран.** Следующий драфт = новый прогон.

**▶ ПРОГОН ЗАВЕРШЁН (Villain-tempo: Hawkeye + HYDRA Assault Robot клок, Cruel Alliance/Crimson Operative exile, Repulsor Blast/Widow's Bite removal) 15.07: 2W–3L.** Хронология L→W→W→L→L. Побед 2 (обе TEMPO+DISRUPT: HYDRA Robot+Hawkeye клок + Cruel Alliance exile пейоффа) — **обе против мула / на игре** (складывалось). Поражения 3: **G-4 MANA-скрю** (вариансный), **G-1 OUT-ENGINED/walled** (go-wide+лайфгейн, нет reach добить с 6), **G0 OUT-ENGINED+перетемплены** (глубокий UB connive/Leader-движок: их эвейжн быстрее + их движок глубже, мы посередине). 🔑 **Все 3 «настоящих» поражения (G-1,G0) = мягкая середина проигрывает и ТЕМП (эвейжн-клок), и ДВИЖОК/лайфгейн** — ни агро ПОД, ни контроль НАД. **ПЕРЕОЦЕНКА: билд-совет говорил ≈7/10, реально ~5/10 C-tier** (нет плотного 2-дроп-эвейжн-клока И нет свипа/reach/движка; выигрывает только на стамбле опп). Приоритет след. драфта — ВЫБРАТЬ ПОЛОСУ (агро-эвейжн ПОД ИЛИ движок НАД), не собирать Villain-goodstuff-середину.
| # | Дата | На игре | Дека | Оппонент | Рез | Причина (осн. + доп.) |
|---|------|---------|------|----------|-----|------------------------|
| G0 | 15.07 | on play (s1) | Villain-tempo (Hawkeye/HYDRA Robot) | **Глубокий UB connive/engine** (Aerial Doombot-флаер, Black Widow, Atlantean Cavalry, Cruel Alliance ×2, Futurist Forge, **Leader Super-Genius** якорь GIH 68.9, Red Room Recruit) | ❌ L | **OUT-ENGINED + ПЕРЕТЕМПЛЕНЫ** — на игре, но кип **4 земли+Deathlok+Ghost+Infiltration = durdle без раннего борда**; **Aerial Doombot-флаер бил КАЖДЫЙ ход (~14, ответа на флаер 0)**, опп ни разу не ниже 14; Bullseye+Ruinous эксайлены их Cruel Alliance ×2. Мы посередине: их эвейжн быстрее И Leader/Forge движок глубже. **Ран-ендер 2→3** |
| G-4 | 15.07 | on play (s1) | Villain-tempo (Hawkeye/HYDRA Robot) | UB Villain go-wide (Stark Exec, The Vision-флаер, Madame Hydra, Crossbones) — **опп мулиганил** | ❌ L | **MANA/VARIANCE** — кип 3 земли+4 спелла на игре vs мула = фаворит, но застрял: за 12 ход. скастовал только Deathlok+Crimson Op, **8 карт зависли в руке** (Hawkeye/HYDRA Robot/Masters/U.S.Agent/Repulsor некастуемы). Не пилот, не билд — скрю |
| G-3 | 15.07 | on play (s1) | Villain-tempo | GW/WU (Knight of Wundagore, Spider-Man To the Rescue, Serpent, Cap Shield, Raft Officer) | ✅ W | **TEMPO+DISRUPT** (на игре, 17 ход.) — HYDRA Assault Robot ранний движок, Ninja/Ghost клок, **Repulsor Blast+Widow's Bite** чистили Spider-Man/Serpent; грайнд 20→7 |
| G-2 | 15.07 | on draw (s2) | Villain-tempo | UB артефакт/Ultron (Ironheart, Ultron Drone, Baron Zemo, Visions of Villainy) — **оба мула** | ✅ W | **RACE+DISRUPT** (12 ход.) — HYDRA Robot+Hawkeye клок, **Cruel Alliance заэкзайлил Ironheart (их пейофф)**, Repulsor снял Ultron Drone; ты 23 (лайфгейн), опп→12. Умеренное evidence (оба мула) |
| G-1 | 15.07 | on draw (s2) | Villain-tempo | **WR teamwork/counters go-wide + лайфгейн** (War Machine, Mister Hyde-движок ×4, Hero in Training, Wakandan Royal Guard, **Knight of Wundagore+Training Regimen**, Take Up the Shield) | ❌ L | **OUT-ENGINED/WALLED + BUILD (нет reach/свипа)** — загнал опп **до 6** (т11), затем **опп 6→14** (т12 лайфгейн: Take Up the Shield + Mister Hyde ×4) + переребилд ширины/counters; **Hawkeye пингует 1/ход — нечем добить последние 6**, борд walled. Ты застрял 10. **Тот же лик что G10/N2/N4/N5** |

**▶ ПРОГОН ЗАВЕРШЁН (BG+U темпо-эвейжн-грайнд, Quick MSH, teaching-lab): 2W–3L.** Побед 2 (vs WU темпо-грайнд, vs Naya DISRUPT+bomb — благоприятные). Поражения 3: **N2 GW Civil War · N4 Jund Training Regimen (Hulk-reach walled + сплеш подвёл) · N5 GW Civil War.** 🔑 **ВСЕ 3 поражения = go-wide/pump + большие reach-блокеры, нет свипа/анти-ширины (0 пилот-панчей — N4 сначала ошибочно списал на пилота, сверил: был walled Hulk-reach + Trickster's некастуем без U).** Плюс G10 прошлого рана = то же. Под ИМ полон. Следующий драфт = новый прогон + **приоритет анти-ширины/свипа + пересмотр U-сплеша (застрял).**
| # | Дата | На игре | Дека | Оппонент | Рез | Причина (осн. + доп.) |
|---|------|---------|------|----------|-----|------------------------|
| N1 | 12.07 | on play (s1) | BG+U темпо-эвейжн-грайнд | Naya/GW go-wide (Thor Odinson, Stark Exec ×2, Guerrilla Gorilla) | ✅ W | **DISRUPT+BOMB** — Punishing Punch снял Thor (бомбу), **Ka-Zar+Zabu-токен = resilient clock** (пережил exile Crossbones), **Stolen Stark Tech ×4 = MVP** (indestructible: combat-wins+защита); ты 19 всю игру, 0 ошибок |
| N2 | 12.07 | on draw (s2) | BG+U темпо-эвейжн-грайнд | **GW go-wide + The Super Hero Civil War** (counters/pump engine) | ❌ L | **OUT-ENGINED + BUILD (нет свипа vs go-wide)** — загнал опп до 4, проиграл **5-4**; они флудили (Ant-Man's Army ×3, Wakandan Drone Flock флаеры ×3) + Civil War-памп ×3, **spot-removal не бьёт ширину**; Civil War снёс Ka-Zar, Web Up заэкзайлил Serpent; на дро. **Наш ХУДШИЙ матчап (повтор G10)** |
| N3 | 12.07 | on play (s1) | BG+U темпо-эвейжн-грайнд | WU tempo/equipment (Spy Kit ×7, Super Suit, флаеры) | ✅ W | **DISRUPT+GRIND** (24 хода) — removal (Widow's Bite снял Flying Ant, Go Nuts, Trickster's-tuck) душил их вольтрон; **Reptil скейлился в 6/6 trample = финишёр** (×2 актив.), Vision-стена + wider board; финал 3 существа vs 1 |
| N4 | 12.07 | on play (s1) | BG+U темпо-эвейжн-грайнд | BR/Jund Villains + Training Regimen ×3 (Madame Hydra, Ares, **Hulk Gamma Goliath 6/5 reach+trample ×2**, Ka-Zar) | ❌ L | **OUT-ENGINED/WALLED + BUILD (НЕ пилот — исправлено 12.07 после сверки)** — загнал опп до 2 (ты 25!) на T13, но **Hulk (6/5 REACH+trample) закрыл всю эвейжн-линию** (The Vision-флаер блокируется+умирает; Reptil 6/6 vs 6/5 = размен, 1 трампл, НЕ летал), hard-removal на Hulk НЕ было, свипа нет; **Trickster's (tuck) застрял НЕкастуемым — не было СИНЕГО источника** (сплеш подвёл; кастовал Killmonger BG = B+G был, U нет). Go-wide + Training Regimen ×3 переребилдили → альфа 25→0. Тот же лик, что N2/N5 |
| N5 | 12.07 | on play (s1) | BG+U темпо-эвейжн-грайнд | **GW go-wide + The Super Hero Civil War** (СНОВА) | ❌ L | **OUT-ENGINED (ХУДШИЙ матчап, 3-й раз) + MANA/BUILD** — GW Civil War go-wide переехал шириной+пампом (Civil War → альфа 12→4); **removal 1-в-1 не держит флуд, свипа нет**; кип 2-лендер → **HERBIE ×2 застряли + Ka-Zar замиллен → бомбы/эвейжн офлайн**; на игре, но go-wide под нас не работает. **Ран-ендер** |

## Категории причин
- **OUT-ENGINED** — грайнд проигран более глубокому движку (шли СКВОЗЬ, надо было НАД/ПОД). [[mtg-...]]
- **STRUCTURAL-AGGRO** — просели рано, нет T1–T2 борда, агро прошло ПОД.
- **MANA** — скрю / флуд / цвет.
- **PILOT** — микроошибка (придержал removal, плохой блок, racing не в ту сторону, жадный кип, зевок).
- **VARIANCE** — просто плохой розыгрыш карт при верной игре.
- **BUILD** — не хватило роли (эвейжн / свип / дешёвое removal), мёртвая карта в руке.

## Сводка
| # | Дата | На игре | Дека | Оппонент | Рез | Причина (осн. + доп.) |
|---|------|---------|------|----------|-----|------------------------|
| 1 | 11.07 | on play (s1) | UB synergy/engine | Go-wide токены | ✅ W | — (гонка эвейжном сработала: был быстрее + на игре) |
| 2 | 11.07 | on draw (s2) | UB synergy/engine | BR/UB Villain-Masque go-wide (глубокий движок) | ❌ L | **OUT-ENGINED** + PILOT (racing не в ту сторону) + BUILD (Atlantis-кирпич, нет свипа vs menace) |
| 3 | 12.07 | on draw (s2) | UB мягкая середина | UB connive-движок (2×Forge, Cosmic Cube, Cavalry×N, Baron Strucker) | ❌ L | **OUT-ENGINED** — был ВПЕРЕДИ (опп до 7), но глубокий движок перестабилизировал; Atlantis-кирпич снова |
| 4 | 12.07 | on draw (s2) | UB темпо/эвейжн | Медленный UB durdle/engine (Super Intelligence, King T'Challa) | ✅ W | **RACE-ПОД** — воздушный клок (Doombot/Drone/Falcon+токены) закрыл опп до 2 ДО сборки его движка |
| 5 | 12.07 | on play (s1) | UB темпо/эвейжн | GW go-wide/counters (Ant-Man ×9, Claim the Kingdom) | ✅ W | **RACE+DISRUPT** — Frozen ×2 лочил их пейоффы, воздушный клок догнал 19→7; заслуженно vs РЕАЛЬНЫЙ движок |
| 6 | 12.07 | on play (s1) | UB tempo-эвейжн | UB durdle — **вероятно мана-скрю** (Kid Loki→ничего 6 ходов→Kang t13) | ✅ W | чистая гонка (опп 20→1), НО опп застрял → **слабое evidence** |
| 7 | 12.07 | on play (s1) | UB tempo-эвейжн | СИЛЬНАЯ bomb-дека (Black Widow, M.O.D.O.K., The Sentry) | ✅ W | **DISRUPT+GRIND** — Cruel exile ×2 снял Black Widow+M.O.D.O.K., Masque-токены ×3 задавили; 26 ходов, опп→2. СИЛЬНОЕ evidence |
| 8 | 12.07 | on draw (s2) | UB tempo-эвейжн | GW (Viv Vision, Storm) — **опп мулиганил** | ✅ W | RACE — Justice+Doombot+Masque-токены, Frozen ×2 лочил блокеров; опп 20→1 к т11, ты на 18 |
| 9 | 12.07 | on draw (s2) | UB tempo-эвейжн | GW go-wide + бомбы (Hawkeye, Okoye) | ✅ W | **DISRUPT+BOARD** — Cruel exile снял Hawkeye, Masque ×4 токенов задавили; ты 17+ всю игру, опп→8. Солидное evidence |
| 10 | 12.07 | on draw (s2) | UB tempo-эвейжн | UG/GW +1/+1 counters engine (Knight of Wundagore, Training Regimen ×3, Civil War) | ❌ L | **OUT-ENGINED + КЛУНКИ-КИП** (2 земли, 2 реактивных Frozen, БЕЗ клока) — ни гнать, ни стабилизировать; engine over the top, ты 20→4. **Ран-ендер 6→3** |

## Партии (детали)

### G10 (последняя) — ❌ ПОРАЖЕНИЕ · on the draw · 12.07 (РАН-ЕНДЕР, 6→3)
- **Опп = committed UG/GW +1/+1 counters engine** (Knight of Wundagore, Training Regimen ×3, The Super Hero Civil War, лайфгейн). Один из сильнейших архетипов MSH — движок over the top (опп 20→22 лайфгейн, потом big/wide).
- **Причина 1 — OUT-ENGINED (как G2/G3):** counters-движок перебордил/перепампил. **Frozen (лочит 1 тело) — слабый ответ на go-wide/pump**, свипа нет.
- **Причина 2 — КЛУНКИ-КИП:** опенер 2 земли, **2 реактивных Frozen + Biochemist + Ninja + Masque — НИ ОДНОГО флаера/клока.** Не мог ГНАТЬ (нет эвейжна) и не мог СТАБИЛИЗИРОВАТЬ (Frozen не тормозит движок). Тот кип не исполнял НИ ОДИН из двух модов → мул был лучше.
- **🔑 Урок:** vs committed counters/pump (UG/GW) tempo-дека уязвима (нет свипа). **Мулиган строже: против неизвестного нужен ПРОАКТИВНЫЙ клок, а не 2 реактивных Frozen.**

### G9 — ✅ ПОБЕДА · on the draw · 12.07 (23 хода)
- **Опп = GW go-wide + бомбы** (Hawkeye Master Marksman, Okoye, Ultron, Spider-Man). Реальная дека, без скрю/мула → **солидное evidence.**
- **Как выиграл: DISRUPT + широкий борд.** **Cruel Alliance эксайлил Hawkeye (бомбу) на т5.** Дальше **Masque ×4 токенов** = устойчивый борд, Hour/Depower/Frozen чистили путь. **Ты на 17+ ВСЮ игру** (не в опасности ни разу), опп 20→8, финальный альфа 6 телами.
- **Причина: ответил на бомбу + перебордил токенами** — контролируемая доминация. Masque = MVP (×4). Forge-cantrip опять в темп, не мешал.

### G8 — ✅ ПОБЕДА · on the draw · 12.07 (13 ходов)
- **⚠️ Опп МУЛИГАНИЛ** → умеренное evidence. Опп = GW (Viv Vision, Kree Commandos, Storm Windrider).
- **Как выиграл: чистая RACE.** Doombot T1 → Justice (баунс-темпо) → Masque-токены, эвейжн-клок. **Frozen ×2 лочил их блокеров** чтобы клок проходил. Опп 20→19→15→11→**1** к т11, ты на 18. Бомба Storm опоздала.
- **Пилот: гнал, Trickster's тукнул блокера, Masque-токены — всё в темп. Верно.**

### G7 — ✅ ПОБЕДА · on the play · 12.07 (26 ходов, ГРАЙНД)
- **Опп = СИЛЬНАЯ bomb-дека** (Black Widow Super Spy, M.O.D.O.K., The Sentry Golden Guardian, Bullseye, Serpent Specialist). Реальная «супер-бомба».
- **Как выиграл: DISRUPT + resilient board, НЕ race.** Cruel Alliance (teamwork) **эксайлил Black Widow (т18) И M.O.D.O.K. (т22)** — teamwork-mode бьёт ЛЮБОЙ MV = ОТВЕТ на бомбы. Hour убил Bullseye, Frozen лочил рано. Клок — **Masque-токены ×3** + Atlantis-тело. Опп 20→2, ты 12→18.
- **Причина: ХВАТИЛО ответов на бомбы + устойчивый борд.** Играл КОНТРОЛЬ (не beatdown), out-answered их бомбы. СИЛЬНОЕ evidence (реальная дека).
- **Нюанс: value-карты (Forge ×2, Atlantis, Stark Tech) ТУТ отработали** — в 26-ходовом грайнде добор/тела = ресурс, не durdle.
- **🔑 MVP = Cruel Alliance teamwork-exile** (снял 2 бомбы). Наш ответ на «супер-бомбы».

### G6 (последняя) — ✅ ПОБЕДА · on the play · 12.07 (13 ходов)
- **⚠️ Опп почти наверняка МАНА-СКРЮ:** Kid Loki t1 → НИЧЕГО 6 ходов → Kang т13. Доминация раздута их стамблом → **слабое evidence** про силу деки. Но сыграно ВЕРНО (гнал на их спотыке — правильный плей).
- **Как выиграл: чистая tempo-эвейжн гонка (vs застрявший опп).** Курв Doombot(T1)→Drone→Ninja→Biochemist→Ant, атаки каждый ход. Опп 20→…→**1**. Ты на 19 всю игру.
- Atlantis/Cruel/Stark Tech/Falcon остались в руке — не понадобились.
- **Нюанс: Futurist Forge скастован т2 (cantrip) и НЕ замедлил гонку** — дешёвый добор безвреден, если не крадёт слот клока. Value-карты не проигрывают; выигрывает КЛОК.

### G5 — ✅ ПОБЕДА · on the play · 12.07
- **Опп = РЕАЛЬНЫЙ GW go-wide/counters движок** (Ant-Man Colony Commander **×9**, Claim the Kingdom ×6, Captain America). Коммиченная дека → «заслуженная».
- **Как выиграл: PROACTIVE + DISRUPT, не грайнд.** Был позади (15 vs 19, они шире), но: Frozen ×2 залочил их ключевые угрозы, Depower+блоки сдержали go-wide, а сам ГНАЛ — альфа т16 (опп 19→11) + воздух (Falcon/Drone/Ninja/Masque-токены) докатили 19→7.
- **Причина победы:** бил движок не в ширину, а КЛОКОМ + точечным lock-removal по пейоффам. Atlantis нашла тело в грайнде, но выиграл клок+Frozen, НЕ durdle.
- **Пилот: не паниковал будучи позади, лочил лучшее, гнал. Верно.**

### G4 — ✅ ПОБЕДА · on the draw · 12.07
- **Опп = МЕДЛЕННЫЙ UB durdle/engine** (Super Intelligence, King T'Challa DFC, Stature, Kid Loki). Не «слабый» — медленный.
- **Как выиграл: RACE ПОД движок.** Aerial Doombot T1 → Drone → Falcon + токены — весь клок ЛЕТАЕТ. Опп 20→…→**2** к т12 (альфа-страйк), ты на 11. Закрыл ДО сборки их движка. Frozen придержал их угрозу.
- **Причина победы: ты был БЕАТДАУНОМ и гнал в воздух.** Durdle/движок СОФТ к быстрому эвейжн-клоку (ровно как в G3, где опп был на 7 — тут докатил).
- **Держал Baxter/Trickster's/Helicarrier/Cavalry в руке — НЕ durdle'ил, гнал. Правильно.**

### G3 — ❌ ПОРАЖЕНИЕ · on the draw · 12.07
- **Опп = ГЛУБОКИЙ UB connive-движок (проверено по логу):** Atlantean Cavalry-триггер **×15**, Construct a Cosmic Cube **×5**, **2× Futurist Forge** (×3 актив.), A.I.M. Scientists, якорь **Baron Strucker**. Ровно «kucha Forge» — подтверждено.
- **Ход:** ты был ВПЕРЕДИ — опп до **7 жизней** (ты на 19 до т13), гнал Cavalry/Biochemist/Ant/Justice. Движок перестабилизировал и завалил бордом (финал: их 8 существ + 2 движка vs твои 3; ты на 1). Atlantis застряла в руке — **3-й раз кирпич**.
- **Причина OUT-ENGINED:** их закоммиченный движок (Cosmic Cube + 2 Forge + connive + Cavalry×N + якорь) перемолол нашу МЯГКУЮ СЕРЕДИНУ.
- **🔑 Урок:** ты почти УБИЛ движок гонкой (опп до 7) → движок СОФТ к быстрому клоку. Но добить нечем — мягкая середина выдохлась. Забрал бы: committed-агро (добить с 7) ИЛИ движок ГЛУБЖЕ их. Мягкая середина — нет. **2 Forge у них — это ПРАВИЛЬНО (в движке избыточный добор = топливо); наша ошибка — 1 Forge в НЕ-движке.**

### G2 — ❌ ПОРАЖЕНИЕ · on the draw · 11.07
- **Дека:** UB synergy/engine (в руке была Atlantis Attacks). **Опп:** BR/UB Villain-Masque go-wide.
- **Ход игры:** до т10 — 20/20 (оба дурдлят Masque'ами, раннего урона НЕТ). Кровь пошла т15→19: 21→14→9→2, вся от go-wide + **2/1 menace-токенов** (их нельзя блокировать одним телом).
- **Причина — OUT-ENGINED:** их Madame Masque сработала **×5**, твоя **×2**; их Villain-движок (Hydra + 2 Masque + Roxxon + Red Room) шире и глубже. В зеркале движков победил жирнейший — не ты.
- **Доп. PILOT:** racing на т14–16 (пропустил 7, атакуя) против БОЛЕЕ ШИРОКОЙ деки — неверная сторона гонки, надо было блокировать/чампить.
- **Доп. BUILD:** Atlantis Attacks застряла в руке (7 мана) = мёртвый кирпич в грайнде; нет свипа/массового ответа на go-wide menace.
- **Сыграно верно:** Cruel Alliance через teamwork (+3, exile их Masque), Depower придержан на их ход, убиты 2 их Masque. Пилот ~80% ок — проиграла дека/матчап.
- **Урок:** vs Villain-Masque go-wide ты КОНТРОЛЬ — бей Masque на месте, не racing, трампуй бомбой а не мелким value.

### G1 — ✅ ПОБЕДА · on the play · 11.07
- **Дека:** UB synergy/engine. **Опп:** go-wide токен-дека (много token-мейкеров).
- **Ход игры:** Kid Loki T1 → атака, Atlantean Cavalry, гонка. Опп 20→...→проигрыш; ты держал 16+.
- **Причина победы:** был **АГРЕССОРОМ** — ранний клок (Loki) + эвейжн (Falcon) обогнали более МЕДЛЕННУЮ токен-деку. Racing сработал, потому что **ты был быстрее + на игре.**

## 🔑 Паттерн (10 игр, 7W–3L) — дека умеет ДВА винконда; «кто беатдаун?» выбирает
- **МОД 1 — RACE (vs медленное/durdle): G1, G4, G6, G8.** Воздушный клок гонит ПОД, закрывает до сборки. (Оговорки: G6 опп скрю, G8 опп мулиганил, G4/G1 медленные — мод рабочий, но оппы часто споткнувшиеся.)
- **МОД 2 — DISRUPT+BOARD (vs go-wide/bomb): G5, G7, G9 — СИЛЬНОЕ evidence (реальные деки).** Cruel-teamwork-exile снимает их БОМБУ (любой MV: Black Widow, M.O.D.O.K., Hawkeye), Frozen/Hour по пейоффам, **Masque-токены (×3–4) = устойчивый борд**, который бомбы не сметают. G5 из-за спины, G7 26-ход. грайнд, G9 доминация на 17+. Дека ОТВЕЧАЕТ на бомбы + перебордивает.
- **ПРОИГРЫШИ (G2, G3, G10): OUT-ENGINED committed движками.** G2/G3 — мягкой серединой (до рефокуса). **G10 (ран-ендер) — tempo-декой vs UG +1/+1 counters-engine + клунки-кип** (2 реактивных Frozen, без клока). Урок: vs committed counters/pump (UG/GW) дека уязвима (**нет свипа**); мулиган строже — против неизвестного нужен ПРОАКТИВНЫЙ клок.
- **🎯 Вывод:** дека = **ТЕМПО-ЭВЕЙЖН с гибкой ролью.** vs медленное → RACE ПОД; vs go-wide/bomb → DISRUPT (лочь/эксайль их пейоффы-бомбы) + грайнд токенами. Value-карты (Forge/Atlantis) не проигрывают: в гонке безвредны, в грайнде (G7) — ресурс. Приоритет — клок + ответы.
- **Master-skill «кто беатдаун?»:** vs медленное/durdle → RACE; vs bomb/go-wide/агро → контроль-DISRUPT. [[mtg-commit-to-a-lane]] · [[mtg-cabs-board-foundation]]

---
## 🆕 ПРОГОН — WU темпо + Civil War splash (17–18.07.2026, идёт)

### L — ❌ ПОРАЖЕНИЕ · on the draw · 18.07 · **PILOT (Wiccan-блинк)**
- Опп = Wx go-wide/Heroes (Ka-Zar, Hulkling ×3, Super-Soldier Serum, White Widow, Cap's Shield ×4). Гонка 6-vs-4, почти выиграл.
- **Лик:** навёл Wiccan-триггер (от Take Up) на вражеского **Ka-Zar** → блинк вернул его оппу + ре-ETB (жетон), И заблокировал наш Web Up от перманентного эксайла Ka-Zar. Надо было: Web Up в Ka-Zar, Wiccan-блинк на СВОЙ Justice/Falcon. Проигрыш с окном — лик пилота, не сборки. Инсайт записан.

### W — ✅ ПОБЕДА · 17.07 · **RACE+STATURE-CLOSER / пережил вражеский Civil War**
- Опп = Wx go-wide с ИХ **The Super Hero Civil War** (свинг 19→9). Наш худший матчап — выиграли.
- **Как:** Stature неблокируемая закрыла мимо их 6-существного борда (опп 18→11→добит). Spy Kit ×6 = движок. Web Up на Colleen (removal в угрозу), Secret Invasion стабилизировал. Пережил свинг грайндом, не паниковал.

### L — ❌ ПОРАЖЕНИЕ · 17.07 · **OUT-ENGINED + PILOT (сидел на removal)**
- Опп = глубокий UB Villain-движок (Madame Masque ×5, Baron Strucker ×3, Thunderbolts-реанимация). Наш док. тяжёлый матчап (движок > goodstuff).
- **Лик:** Web Up в стартовой руке, Masque вышла т9 — эксайл только т14 (5 ходов токен-флуда). Держал premium-эксайл против движка = переезд. Клок (Justice 2 силы) слишком медленный. Проигрыш с окном (ранний Web Up на Masque + гонка = аут).

### W — ✅ ПОБЕДА · 18.07 · **RACE + DISRUPT-BOMB (Murdock's эксайл Sentry)**
- Опп = Wx go-wide/Heroes (Crowd, A.I.M. Synthoids, Kree Commandos ×2, Agent 13, Winter Soldier). Медленная ширина.
- **Как:** беатдаун по воздуху — Aerial Doombot T1 → power-up ×2 (4/4-клок) + Justice + токены, весь клок летает мимо их наземной ширины (opp 20→4). **Murdock's заэксайлил The Sentry (их бомбу) СРАЗУ (т12)** — removal в хеймейкер, не по телам, не держал.
- **✅ Применил уроки прошлых L:** removal в бомбу на месте (не сидел), верный беатдаун-рид. Контраст с сидением на Web Up (17.07) и Wiccan-блинком (18.07). Прогон 2W–2L.

### W — ✅ ПОБЕДА · on the draw · 18.07 · **RACE (Stature сквозь скрю) + DISRUPT ×2 бомбы**
- Опп = GW go-wide/Heroes (Ant-Man Colony Commander, Captain America Wings of Freedom, Tigra, Gorilla). Ты на 3 землях (скрю), выиграл 13-vs-5.
- **Как:** дешёвый кип (3 земли + Stature/Raft/Spy Kit/Web Up) — **правильный КИП, не мулл** (учёл прошлый лик). **Stature = неблокируемый клок с T1 сквозь скрю** (опп 20→5 мимо его борда). **Web Up ×2 — оба в их бомбы на месте:** Ant-Man Colony Commander (т9) + Captain America Wings of Freedom (т11, анфем-хеймейкер). Removal в движок/бомбу сразу, не держал.
- **✅ Все уроки применены:** кип низкой руки, Stature vs go-wide мимо борда, removal в бомбы на входе. Идеальное исполнение. Прогон 3W–2L.

### W — ✅ ПОБЕДА · 18.07 · дека #2 (Captain America WU) · **GO-WIDE grind vs BR-removal (Stature + ширина + Frozen-лок + Web Up бомбы)**
- Опп = BR removal/value (HULK SMASH, Dark Deed, Cruel Alliance, Crimson Operative ×4, Red Hulk, Jessica Jones). Контроль на 17, опп 20→1.
- **Как:** Stature неблокируемая понесла рано (опп→13). Затем **ГО ВАЙД** (Viv Vision, Atlantean, Aerial Doombot, Red Guardian, Bold Bio, Okoye-токен) — removal-помойка не отвечает на всё. **Frozen ×2 залочил Red Hulk/Super-Skrull**, **Web Up снёс Jessica Jones (их бомбу)**, power-up движки (Viv ×3, Atlantean ×2, Doombot) отскейлили в летальную ширину.
- **✅ Применил урок прошлого L той же BR-деке:** card adv + го вайд + лок + снос бомбы > угрозы по одной. Тот же матчап, обратный результат. Дека #2: 1W–1L.

---
## 🆕 ПРОГОН 19.07.2026 · UB темпо-контроль (Elektra ×2 / Ghost / Vision) — 1W–0L

### W — ✅ ПОБЕДА 11-vs-0 · 19.07 · **RACE-МИМО-БОРДА (Ghost неблокируемый) + SOLO-DRAIN**
- Опп = **Wx go-wide/Heroes** (Aerial Doombot, Agents of S.H.I.E.L.D., Captain America Living Legend, Agent Phil Coulson, Murdock's Crusade, Vibranium Energy Daggers). **Наш документированный ХУДШИЙ матчап — выигран чисто, жизни ни разу не упали ниже 10.**
- **Как (verified по логу):** **Ghost, Spectral Saboteur прошёл неблокированным 4 хода подряд** (т9, 11, 13, 15) — их ширина не имеет значения, он не блокируется в принципе. Добил **HYDRA Infiltration**: «атакует в одиночку → дрейн 1» сработал ×2, последний триггер и был леталом (опп 3 → Ghost 2 + дрейн 1 = 0).
- **🌟 ПОДТВЕРЖДЕНА МИКРО-СИНЕРГИЯ СБОРКИ: Ghost/Stature (неблокируемые) + HYDRA Infiltration (дрейн за соло-атаку) + Stolen Stark Tech.** Я оценивал HYDRA Infiltration как слабейшую карту мейна («чара, не тело») — **игрок был прав, она нанесла летальный урон.** Урок: считать связку, а не карту в вакууме. [[mtg-count-enabler-density]]
- **✅ Removal по верным целям (уточнено игроком, verified):** Trickster's затакнул **Captain America, Living Legend** (анфем-пампер Heroes — их главная угроза). Frozen залочил **Agent Phil Coulson**. **Aerial Doombot умер В БОЮ**, заблокировав Elektra 3/3 (не от removal). Elektra ETB снесла Agents of S.H.I.E.L.D. Ни один ответ не пролежал в руке.
- **⚠️ Нюанс Trickster's — «вторым сверху» ≠ ответ навсегда:** Cap затакнут на т11 и **переигран оппонентом на т14** (в логе два каста Captain America — т10 и т14). Здесь это не стоило партии, потому что мы закрывали (опп 4 → 0 за два хода), но правило: **против угрозы, которую надо убрать НАСОВСЕМ, выбирай «в низ библиотеки»**; «вторым сверху» — только когда гонка уже выиграна и важнее отнять у них свежий топдек.
- **Titania T3 через дискард Kingpin's Enforcers** — доплата «сбрось карту» уплачена телом, 5/5 ward на 3-м ходу нанесла 5 и стянула на себя их **Murdock's Crusade** (эксайл tough≥4, подтверждение старой заметки). Размен в нашу пользу: их premium-removal ушёл в карту, которая уже отработала.
- **⚠️ Мелкий лик (партию не стоил):** в connive от Trickster's сброшен **Frozen in Ice** — живая интеракция. Смягчение: в деке была 2-я копия, она и залочила Cap. Правило прежнее — питчить землю/худший спелл. Повтор лика 07.07 и 02.07.
- **Вывод для меты:** против go-wide+анфем работает НЕ размен в борд, а **клок, который борд игнорирует**. Третье подтверждение (17.07 Stature, 18.07 Stature, теперь Ghost).

### W — ✅ ПОБЕДА (ты 16 / опп 2) · 19.07 · **KLAW-ДИСРАПТ (сорван Web Up) + STATURE-ЗАКРЫВАШКА**
- Опп = **GW Heroes/value** (Hellcat Undying Vigilante, Mister Hyde, Agent of Atlas, Ka-Zar of the Savage Land, Web Up + неопознанный движок `id105198`, активирован ×3). Жизни не падали ниже 14.
- **🌟 КЛЮЧЕВОЙ ХОД — Klaw (т10) вырвал у оппа Web Up.** ETB «вскрой руку, ТЫ выбираешь сброс» → снят их premium-эксайл **до того**, как он изгнал наш клок. Ровно по правилу «вырывай ответ/бомбу, не землю». Дальше Stature и Elektra катались безнаказанно — отвечать было нечем.
- **✅ STATURE-ПАМП НАКОНЕЦ ПОТРАЧЕН (т14).** Прерван задокументированный лик, тянувшийся **4 партии подряд** (памп не активировался ни разу, финишёр умирал с неистраченным). Потрачен верно — на **большой НЕ-летальный** удар (опп 11 → 2), дожим командой на след. ход. Это буквально правило из заметки 10.07.
- **Elektra ETB (т8) снесла Mister Hyde.** Elektra = тело + removal, второй матч подряд отрабатывает как двойная карта.
- **Agents of HYDRA отработал как «два тела в слоте»:** разменялся в блок с Hellcat (т11) и оставил 2/1 menace-жетон. Оправдывает пик D-тира в дефицитный слот кривой.
- **Kingpin's Enforcers (т8) — агрессивная, но верная атака:** дабл-блок Hellcat+Agent of Atlas, разменялся с Agent of Atlas и вернул **+2 жизни лайфлинком** (14→16). Отдали 3-дроп за 2-дроп, но выкупили темп и жизни.
- **⚠️ Доступный апгрейд (не ошибка, партия выиграна):** 2-я Elektra осталась в руке при **Stature, проходившей неблокированной каждый ход** — идеальный энейблер для **Sneak {1}{B}{B}**. Линия «баунс неблокированного атакующего → Elektra входит атакующей + ETB-снос» закрыла бы на ход раньше и за 3 маны. Sneak за 2 матча не использован ни разу — **отработать сознательно.**
- **Итог прогона: 2W–0L.** Обе победы — клок, который игнорирует их борд (Ghost / Stature), + дисрапт их ответа до того, как он сыграл.

### W — ✅ ПОБЕДА (ты 16 / опп 0) · 19.07 · **STATURE T1 + ДИСЦИПЛИНИРОВАННЫЙ ДЕШЁВЫЙ КИП**
- Опп = **WU темпо/Heroes** (Agent 13 Sharon Carter ×3 актив., Falcon's Wing Harness, Falcon, Brave Brawler, Secret Invasion, H.E.R.B.I.E., Hero in Training), **мулиганил**. Жизни не падали ниже 16.
- **✅ КИП 2 ЗЕМЛИ — ВЕРНЫЙ, не жадный:** рука была Stature {U} / Deathlok {B} / Agents {1}{B} / Biochemist {1}{U} / Widow's Bite {1}{B} = **всё 1-2 дропы**. Дешёвая рука на 2 землях кипается, топ-тяжёлая — нет. Развернулись без запинки. Контраст с задокументированным ликом «кип с 2× Atlantis» (11.07).
- **🌟 Stature на 1-м ходу → атаковала неблокированной 5 ходов подряд** (т4, 6, 8, 10, 12). Оппонент смог ответить только **Secret Invasion на т13** — то есть весь ранний-средний гейм клок был безответным. Третья победа подряд на «клоке, который игнорирует борд».
- **✅ Вся интеракция потрачена вовремя:** Widow's Bite инстантом снёс их Bold Biochemist в бою (т10), **Frozen in Ice ×2 оба разыграны и залочили** (т8, т12). Ничего не пролежало в руке — третий матч подряд без лика «сидел на removal».
- **Agents of HYDRA снова отработал «два тела в слоте»** — разменялся в блок с их Biochemist (т8) и оставил жетон.
- **Bold Biochemist power-up (т16)** — +1/+1 и добор 2 перед летальной атакой; мана-синк в лейте, а не мёртвая 1/3.
- **⚠️ Памп Stature снова не потрачен** (5-я партия) — но **здесь это оправдано:** на т12 после Frozen оставалось ~3 маны, X=1 дал бы всего +1 урона. **Важный нюанс: качать в ГЛАВНУЮ фазу нельзя вообще** — сила >1 снимает неблокируемость и опп её чампит. Качать только ПОСЛЕ объявления блоков. Малый памп = плохой размен маны, не ошибка пропустить.
- **Итог прогона: 3W–0L.** Общий паттерн всех трёх побед: **неблокируемый/эвейжн-клок рано + дисрапт или removal в их ответ + жизни выше 14.** Ни одной гонки «в борд» не проиграно, потому что ни одной не начато.

### L — ❌ ПОРАЖЕНИЕ · 19.07 · **PILOT: removal в НЕ ту цель (Doombot вместо вражеской Stature)**
- Опп = **GU counters/value** (Stature Size Shifter, Hydraulic Helper, Guerrilla Gorilla, Aerial Doombot, Wakandan Royal Guard, Bold Biochemist, Punishing Punch, White Tiger). Оба мулиганили.
- **🔴 КОРНЕВАЯ ОШИБКА (т7, verified): ETB Elektra снёс Aerial Doombot, хотя вражеская Stature была легальной целью** (1/1, сила ≤3). Опп поставил Stature **на 1-м ходу**, она уже пробила на т4 и т6 — то есть на момент выбора цели она была очевидно главной угрозой, а Doombot только что вышел и ещё не атаковал.
- **Цена ошибки (三 удара):** (1) **т9 — опп напампил Stature и заблокировал ею Elektra → наша Elektra умерла**, размен бомбы на ничего; (2) **т10 и т14 — Stature бьёт неблокированной**; (3) она **осталась на столе к концу партии**. Одна карта, которую мы могли убить бесплатно, выиграла им игру.
- **Правило было записано и нарушено:** `msh_insights.md` — «приоритет removal в гонке: их **НЕБЛОКИРУЕМОМУ** клоку, а НЕ наземке/тому, что и так блокируется» и «**Неблокируемость > флаер > наземное тело**». Doombot 1/1 флаер **блокируется** нашими Falcon/Ant/Vision; Stature не блокируется ничем в принципе.
- **Дополнительная ирония:** это ровно та карта, которой **мы сами выиграли 3 партии подряд** в этом же прогоне. Знаем её силу изнутри — и не убили.
- **Второстепенно (т7):** Kingpin's Enforcers 2/3 атаковал в **три нетапнутых блокера** (Hydraulic Helper + Gorilla + Doombot) и умер. Crackback-чек не сделан.
- **Мулиган 7→6 спорный, но не причина:** отправлена рука 3 земли + Frozen + Elektra + Falcon + Ant (топ-тяжёлая, но с removal). Кривая после мула сложилась нормально (Deathlok т1, Kingpin's т3, Elektra т4, Titania т5) — проигрыш НЕ на мане.
- **Итог прогона: 3W–1L.**

### L — ❌ ПОРАЖЕНИЕ · 19.07 · **STRUCTURAL: REACH-фэтти закрыли воздух + бёрн разменял наши тела**
- Опп = **RG big creatures** (Reptil, Undercover Skrull, Ant-Man's Army, **Hulk Gamma Goliath 6/5 reach+trample**, **Red Hulk 6/7 reach+trample**, **Lightning Strike ×2**). Оба мулиганили. Финал: наш борд ПУСТ (0 существ) против их 3, опп на 16.
- **🔴 ДОКУМЕНТИРОВАННЫЙ ХУДШИЙ СЦЕНАРИЙ, повтор:** `msh_insights.md` прямо содержит «**БОЛЬШОЙ REACH-БЛОКЕР (Hulk Gamma Goliath) ЗАКРЫВАЕТ ВСЮ НАШУ ЭВЕЙЖН-ЛИНИЮ**» и «Reach = хищник флаер-рейса». У оппа их было **ДВА**. Весь план деки (лететь поверх) выключен одной картой, а их было две.
- **Клок был катастрофически медленным:** единственным источником урона оказался **Ghost, 2 в ход** (т8, т10 → опп 20→16). При их 6/5 и 6/7 нам нужно было ~8 ходов чистых атак. Stature ушла в мулиган и не пришла.
- **Их removal разменял наш борд 1-в-1, наш — нет:** Lightning Strike ×2 сняли **The Vision** (т11, блок Ant-Man's Army: 3 боевых + 3 бёрна = 6 ≥ 5 тафнесс) и **Scientist Supreme** (т15). Наши ответы (Widow's Bite → Reptil т4, Frozen → фэтти т8) закончились до выхода Red Hulk (т13) — на вторую 6/7 ответа уже не было.
- **⚠️ Пилот-нюанс (т15): заблокировали Undercover Skrull СВОИМ Ghost'ом** — единственным неблокируемым клоком. Инсайт гласит «**СВОЙ эвейжн береги — не размен-блокируй, лети в лицо**» (док. проигрыш с блоком The Vision об Luke Cage). Смягчение: на 11 жизнях под Red Hulk 6/7 trample выбор был скверный в любом случае — партия к т15 уже была почти проиграна.
- **Мулиган 7→6 спорный:** ушла рука 2 земли + Stature/Scientist Supreme/Widow's Bite (дешёвые) + Ant/Elektra. По критерию партии-3 (дешёвая рука на 2 землях кипается) её можно было оставить — и **Stature была бы на столе с т1**, а именно её не хватило как второго клока. **Не называю ошибкой** (3 из 5 карт дешёвые, а не 5 из 5), но это развилка.
- **Вывод: проигрыш СТРУКТУРНЫЙ, не пилотский.** Против двух reach-тримплеров с бёрном у UB-эвейжн-темпо аутов почти нет: hard-removal в деке всего 2 (Trickster's, Hour of Defeat), оба не пришли. Лечится в ДРАФТЕ (плотность безусловного removal), не в бою.
- **Итог прогона: 3W–2L.** Следующее поражение закрывает ран.

### L — ❌ ПОРАЖЕНИЕ · 19.07 · **«ЗАГНАЛ, НО НЕ ДОБИЛ» + Frozen умер в руке** (ран закрыт 3W–3L)
- Опп = **GW counters/go-wide** (Hulkling, Ka-Zar of the Savage Land, Ant-Man's Army, **Training Regimen ×2 актив.**, Hercules, Go Nuts!, Volcanic Villain). Мулиганили оба.
- **Мы ВЕЛИ всю партию:** опп 20→19→16→13→12→**11**, мы стояли на 20 до т8. Затем 20→17→14→**7**→смерть за три хода. **Это дословно наш главный задокументированный лик Платины: «загоняем оппа в низ, но НЕ добиваем, и его over-the-top переворачивает доску».**
- **🔴 ЛИК 1 — Frozen in Ice умер В РУКЕ.** Финальная рука = Frozen in Ice. На **т13 было ~7 земель**, скастован только Bold Biochemist (2 маны) — Frozen (3) влезал в тот же ход и залочил бы Ka-Zar/Hulkling до их альфы на т14. Повтор дока «сидел на removal» (3-й раз за прогон в разных формах).
- **🔴 ЛИК 2 — памп Stature снова не потрачен, и ЗДЕСЬ это была ошибка.** Она била как 1/1 на т3, т5, т11, т13 = ~4 урона за партию. На **т13 при ~7 землях** после Biochemist оставалось ~5 маны → **X=3, Stature 4/4 неблокируемая** = опп 12→8 вместо 12→11. **Отличие от партии-3 (где пропуск был верным): там X=1 при 3 манах, здесь X=3 при 5 — и мы были в режиме «обязан закрыть».** Порог: качать, когда X≥3 И опп в радиусе двух ходов.
- **✅ Klaw снова отработал** — вырвал у оппа **Hercules** (т9). Он всё равно пришёл вторым экземпляром на т14, но дисрапт был верный.
- **Training Regimen (×2) = наш док. хард-каунтер** («counters/pump go-wide бьёт темпо-мидрейндж без свипа»). Свипа в деке нет — структурная часть проигрыша реальна, но **партия была выигранной при закрытии на т11–13.**
- **Мулиган 7→6 верный:** ушла рука 2 земли + спеллы на 3/4/4/3/5 — честно топ-тяжёлая.

---
## 📊 ИТОГ ПРОГОНА 19.07.2026 · UB темпо-контроль (Elektra ×2 / Ghost / Stature / Vision) — **3W–3L**
**Чёткий раскол по цвету оппонента:**
- **3 ПОБЕДЫ — все против W/U-based** (Wx Heroes go-wide, GW Heroes value, WU темпо). Схема одна: **дешёвый неблокируемый/эвейжн-клок рано + дисрапт их ответа (Klaw/Widow's/Frozen) + жизни выше 14.** Ни одной гонки «в борд» не начато.
- **3 ПОРАЖЕНИЯ — ВСЕ против зелёных дек** (GU counters, RG reach-фэтти, GW counters/go-wide). Зелёное хосит наш план тремя способами: **reach-фэтти** (воздух мёртв), **counters/pump** (Training Regimen перерастает наши тела), **fight-спеллы** (Go Nuts! убил Ant без размена).
- **Вывод для ДРАФТА:** UB-эвейжн-темпо в MSH — фаворит против W/U и андердог против G. Нужно либо **≥4 безусловных removal** (у нас было 2: Trickster's + Hour), либо **анти-ширина/свип**, либо не идти в чистый воздух, когда зелёное за столом открыто.
- **Пилот:** 2 из 3 поражений имели ОКНО (L1 — removal в Doombot вместо Stature; L3 — Frozen в руке + непотраченный памп при опп на 11). Только L2 (два reach-тримплера + бёрн) был без аутов.

---
## 🆕 ПРОГОН 22.07.2026 · WU Heroes-темпо (Wiccan/Stature/Okoye/Viv Vision)

### W — ✅ ПОБЕДА (ты 3 / опп 0) · 22.07 · **GRIND-COMEBACK — Wiccan-блинк-движок + Web Up ×2 вытянули с 3 жизней**
- Опп = токен-движок (карты вне наших данных, grpId не резолвится — колода не читается по именам, только «жетон каждый ход» видно). Давил стабильно с хода 3, ты упал 20→16→14→10→6→**3** к ходу 19 — почти проиграна.
- **Перелом — Wiccan, Rising Magician (сработал ×5) + Raft Security Officer (×4) + Web Up ×2 (эксайл угроз) + Stature.** С хода 12 счёт пошёл в обратную сторону: опп 20→16→12→11→6→**3→0**, ты устоял на 3 и добил.
- **✅ Хорошее исполнение под давлением:** не запаниковал на низких жизнях, продолжал развивать движок (Wiccan-блинк за каждый неcуществоный спелл — заметны 5 активаций) вместо панического пуша, Web Up снимал реальные тела вовремя.
- **Итог прогона: 1W–0L** (после этой партии — до 2 поражений ниже).

### L — ❌ ПОРАЖЕНИЕ · 22.07 · **BUILD/VARIANCE: Saga-снежок (World War Hulk) не встретил ответ — не было в руке, не «сидел на нём»**
- Опп = RG/Gruff big-creature (Abomination Terrifying Titan, Savage Land Dinosaur 7/6 trample, Beast Erudite Aerialist, H.E.R.B.I.E., Hydraulic Helper, **World War Hulk** — Saga, Mister Fantastic, Wakandan Royal Guard). Кип 3 земли + Frozen/We Say Thee Nay!/Brave Brawler/Wiccan — верный (не топ-тяжёлая).
- Партия шла ровно: т14 ты 27 / опп 11 (доминация). Т16 — крупный выгодный размен в бою (потерял Viv Vision+Okoye, снял H.E.R.B.I.E.+Hydraulic Helper+Ant-Man's Army — 3 их тела за 2 твоих).
- **🔴 КОРНЕВАЯ ПРИЧИНА: World War Hulk (Saga, {3}{G}{G}) телеграфировал свою развязку, и её нечем было встретить.** Триггеры саги детерминированы: гл. I (бесплатный каст) → гл. II (+3 counters на их существо, ~т17) → гл. III (**удвоить силу/тафнесс + trample выбранному телу, потом сага сакается**). Гл. III на их следующем ходу была гарантирована — не сюрприз.
- **Т19 — гл. III ударила по Savage Land Dinosaur (7/6→14/12 trample) + Beast (флаер) прошли не заблокированными → 19 урона за один ход (ты 23→4).** Партия фактически решена этим ходом.
- **✅ Исправление (игрок поймал, verified по логу): обе копии We Say Thee Nay! разыграны ПРАВИЛЬНО, не пролежали в руке.** Т8 — законтрена Giant-Sized Flying Ant №1; т20 — законтрена Giant-Sized Flying Ant №2. Обе в реальных летающих угроз, не мимо цели. **На т15 (каст World War Hulk) второй копии в руке ещё не было** (первая уже потрачена т8, вторая пришла позже) — это нехватка ресурса в нужный момент, а не пилотская ошибка удержания карты. Также на т12 наш Frozen in Ice сам был законтрен их We Say Thee Nay! — ещё одна причина, почему ответов на угрозы объективно не хватило.
- **Правило остаётся полезным на будущее, но БЕЗ обвинения пилота этой партии:** если контрмагия ЕСТЬ в руке в момент каста Saga — контрить её на касте выгоднее, чем отвечать на payoff позже (Saga даёт предсказуемое окно). Здесь такого выбора просто не было.
- **Итог прогона: 0W–1L.**

### L — ❌ ПОРАЖЕНИЕ · 22.07 · **OUT-ENGINED go-wide (движки из нескольких источников), пилот чист**
- Опп = **BR/Villain go-wide-движок**: A.I.M. Synthoids, Kingpin's Enforcers, Hire a Crew, Crossbones, **Avengers: Under Siege** (Saga, сработала ×3 — токен каждую главу), HYDRA Troopers, **Baron Strucker, HYDRA Overlord** (якорь), The Masters of Evil.
- Кип верный: 4 земли + Okoye + Web Up ×2, некипающих карт нет.
- **✅ Пилот чист:** Web Up ×2 оба в реальные угрозы вовремя (Crossbones т11, HYDRA Troopers т15) — не пролежали. We Say Thee Nay! законтрил The Masters of Evil (т16). Okoye разменялась на Kingpin's Enforcers гэнг-блоком (т8), потеряла только Okoye — честный трейд.
- **🔴 Причина — структурная: только 2 hard removal против ГОРИЗОНТАЛЬНОГО давления из нескольких независимых источников одновременно** (сага-токены + Hire a Crew + HYDRA Troopers + постоянный чип A.I.M. Synthoids). Removal 1-в-1 не отвечает на ширину — снял 2 угрозы, а бордом задавили с других сторон. Жизни 20→17→10→3, финал 1 существо у нас против 5 у оппа.
- **Тот же класс поражения, что уже задокументирован для WU/UB-темпо этого сезона: go-wide/движок-без-свипа — наш структурный худший матчап**, не лечится пилотированием этой партии.
- **Итог прогона: 1W–2L.**

### L — ❌ ПОРАЖЕНИЕ · 22.07 · **CRACKBACK — олл-ин на 13→4 (не добил), 0 блокеров против wide-движка, снесли неблок. алфой**
- Опп = **G/B(x) go-wide через Squirrel Girl-движок**: Serpent Specialist (deathtouch), Titania Rugged Rumbler 5/5 (ward), Pet Avengers, Ant-Man's Army, Go Nuts! (fight-памп), Wolverine, Undercover Skrull, **The Unbeatable Squirrel Girl** (сработала ×5 — токен каждый ход с хода ~16).
- Кип 3 земли + 5 спеллов — верный, разворот по кривой без запинок т1-т5.
- **Т6-т12: Titania 5/5 + Go Nuts! (убил King T'Challa через fight, т10) продавили доску.** Т12 при жизнях 4 — вынужденный экстренный блок ВСЕМ (в т.ч. Aerial Doombot в deathtouch-Serpent) — **правильно по правилу «на низких жизнях блокируй всё блокируемое»**, не лик. Оба Giant-Sized Flying Ant погибли тем же/следующим блоком (т12, т16) — тоже вынужденно, не пилотская ошибка.
- **✅ Super Suit (т21) отработал штатно, НЕ потрачен зря** (проверено по raw-логу): flash+attach на A.I.M. Scientists → 6/7, пережил дабл-блок 2 токенов Squirrel Girl, убил ОБА (assignedDamage 1+5). Прямой вклад в алфа-страйк т21: опп 13→4, ты 10→14.
- **🔴 КОРНЕВАЯ ПРИЧИНА: алфа т21 не добила (опп остался на 4), после нее — 0 блокеров, а Squirrel Girl уже 5 ходов копила токены.** Т22 — их crackback **16 атакующих**, все ✓прошёл (блоков не было физически возможно достаточно). Это crackback-check из pilot §4 навыворот: пошли ва-банк БЕЗ летального счёта против ИЗВЕСТНОГО (видимого 5 активациями) растущего wide-движка.
- **Урок:** против видимого token-engine (≥3 активации до твоего решающего хода) — считай их потенциальный крэкбэк ПЕРЕД алфой явно, не только «мы после атаки живы», а «если не убиваем — сколько блокеров у нас останется против ИХ следующего хода». Karta-уровня решение (Super Suit) может быть безупречным и всё равно проиграть партию, если решение об алфе выше него было неверным.
- **Итог прогона: 1W–3L.**

### W — ✅ ПОБЕДА (ты 6 / опп 8, 20 ходов) · 22.07 · **EVASION-CLOSED — план Б донёс, хотя движок (Leader) сняли removal'ом**
- Опп = **чёрный Villain/эквип-деструктив**: Swordsman, Sharp Scoundrel (сработал ×5, attach equipment на Villain ETB), Black Widow Double Agent, Grim Reaper Lethal Legionnaire, Thor God of Thunder, Baron Helmut Zemo, Red Room Recruit, **Cruel Alliance ×2** (exile-removal).
- **Потеряли и Leader (т9), и Hero in Training (т15) под Cruel Alliance** — обе копии их removal ушли в наши лучшие карты, движок снят рано. Kid Loki умер т5 почти без пользы (снова минус к его и так отрицательному IWD).
- **✅ Партия выиграна НЕ движком, а голым эвейжн-планом**: с т14 по т20 два Giant-Sized Flying Ant + Aerial Doombot заходили в лицо без блока (✓прошёл каждый ход) и закрыли игру, пока жизни качались 20↔6-8.
- **Инсайт для `msh_insights.md`: неблокируемый/летающий клок — реальный план Б, не зависящий от бомб.** Потеря главного движка (Leader) removal'ом на 9-м ходу не помешала выиграть — плотность эвейжн (2+ флаера) сама по себе закрывает партию. Контраст с прошлыми поражениями этого же архетипа (17.07, 22.07 L1-L3), где эвейжн вытаптывали вынужденными блоками при недостатке removal — здесь плотность оказалась достаточной, чтобы план сработал даже под давлением.
- **Итог прогона: 2W–3L.**

### L — ❌ ПОРАЖЕНИЕ (13 ходов) · 22.07 · **OUT-ENGINED — War Machine репитинг-памп ×4 без ответа, добит all-flying алфой**
- Опп = **почти зеркальный WU/WR-артефакт-эвейжн** (свой Aerial Doombot, S.H.I.E.L.D. Deployment Drone, Wakandan Drone Flock, **War Machine, Legacy of Iron** — {2}{R/W} 1/3 flying, начало боя пампит другое существо на +X/+0, сработал **×4** за игру, **Vision Quest** тьюторнул Wakandan Drone Flock прямо на стол с бонус-counters на решающем ходу).
- **Финальная атака т13 — все три атакующих летающие, у нас на столе только Kid Loki + Stature (оба наземные) — блокировать физически нечем.**
- **⚠️ Web Up был в стартовой руке и не разыгран НИ РАЗУ за 13 ходов**, пока War Machine копил памп 4 активациями. Leader тоже пролежал в руке весь матч. Причина (мана vs. пропущенный момент) НЕ верифицирована по логу — не считать подтверждённым ликом, но держать в голове: репитинг-движок оппонента — приоритетная цель по правилу «движок важнее тела».
- **Итог прогона: 2W–4L.**

### L — ❌ ПОРАЖЕНИЕ (19 ходов, доминирующая позиция) · 22.07 · **DECK-OUT — свой King T'Challa+Leader выел библиотеку раньше победы**
- Игра была выиграна по борду: опп 21→5, у нас 6 существ на столе, Web Up эксайлнул их бомбу (Jennifer Walters // She-Hulk), лучшая позиция за весь прогон — и всё равно поражение.
- **Подтверждено по логу (прямой трекинг зоны библиотеки): к т19 своя библиотека упала до 1 карты, дальше draw-from-empty = проигрыш по правилам.** Не текстовый баг парсера — независимо подтверждено счётчиком объектов зоны + отчётом игрока.
- **🔴 КОРНЕВАЯ ПРИЧИНА — механика связки Leader+King T'Challa, не невезение.** Leader — replacement-эффект: коннайв под ним = draw + (draw+discard) = **2 добора за одно срабатывание**, не 1. King T'Challa триггерится на «второй добор за ход» — часто сам этот двойной коннайв его и заводит (ещё +1 добор). За игру: King T'Challa ×7, Leader ×6 (~12 доборов только оттуда), плюс connive A.I.M. Scientists/Bold Biochemist сверху — 40-карточная колода физически не тянет такой темп изъятия за 19 ходов.
- **Урок для `msh_knowledge.md`: связка Leader+King T'Challa способна выесть свою же библиотеку раньше победы, даже при явном игровом преимуществе.** В затяжных партиях с обеими картами на столе — следить за счётчиком своей библиотеки; при явном превосходстве и низком остатке (≤10-12 карт) — придерживать активации Leader вместо автоматического нажатия по инерции.
- **Итог прогона: 2W–5L.**

### Партия — 2026-07-24 (проигрыш, VARIANCE — баг клиента)
Украдено существо через The Super Hero Civil War (chapter I, ход 11). На ходах 11 и 13 карта не отвечала на управление — Arena лагнула, существо застряло без возможности атаковать/активировать, хотя summoning sickness уже не должно было действовать на ходу 13. Пользователь подтвердил: это не ошибка розыгрыша, а сбой клиента (не смог управлять украденной картой).
Категория: VARIANCE (баг Arena, не пилотирование/сборка).

---
## 🆕 ПРОГОН 24.07.2026 · WU темпо-эвейжн (Spy Kit ×2 / 2× Drone Flock / Political Triumph) — новая колода после вылета 0:3

### W — ✅ ПОБЕДА (ты 24 / опп 0, 17 ходов) · 24.07 · **EQUIP-CLOCK: 3 их removal не остановили эквип-клок**
- Опп = **чёрно-белый мидрейндж/value**: Project Deathlok Soldier, свой Wakandan Drone Flock 3/3, Moonstone Harsh Mistress 2/4 fly, **Web Up**, **Hour of Defeat ×2**.
- Кип 3 земли + Spy Kit / Ant / Political Triumph / Drone Flock — верный (дешёвая рука, топ-тяжёлого нет).
- **Линия победы (verified по логу): урон ровно по 4 каждый ход, опп 20→16→12→8→4→0, НИ ОДНА наша атака не заблокирована.** Мы не опускались ниже 19 (одна ранняя атака Deathlok'а).
- **🌟 S.H.I.E.L.D. Spy Kit сработал ×7 — 3-е подтверждение инсайта «ЭКВИП = REMOVAL-PROOF КЛОК», теперь в WU-воздухе.** Опп разыграл **ТРИ removal** (Web Up → Political Triumph т11; Hour of Defeat → Wakandan Drone Flock т13; Hour of Defeat → Giant-Sized Flying Ant т15) и всё равно проиграл: **эквип оставался на столе и перевешивался на следующее тело** (активации т14, т16 — уже на новых носителях). Их 1-в-1 removal против эквип-клока = не размены.
- **✅ Кривая-ускорение отработала как спланировано:** T1 Political Triumph → T2 Hydraulic Helper → **T3 Wakandan Drone Flock, оплаченный маной Helper'а** (Drone Flock — артефактное существо, ограничение Helper'а «только артефакты» его пропускает). 3/3 флаер на ход раньше = весь темп партии.
- **✅ Murdock's Crusade приберёгся правильно:** Moonstone 2/4 была ЕДИНСТВЕННОЙ легальной целью на столе (тафнесс ≥4; их Drone Flock 3/3 под него не подходит). Потрачен т16, когда она осталась последним летающим блокером → эксайл → добивание.
- **✅ Solo-attack режим:** каждая атака — одним флаером, Spy Kit untap+scry, тело возвращалось в блок. Грайнд-режим работает именно так, как расписан в пилот-плане.
- **📌 Political Triumph = магнит их эксайла.** Дала 3 скрая за {W}, но 4-й счётчик не успела — снята Web Up'ом. Это приемлемый размен: она стянула их лучший ответ, который иначе ушёл бы в клок. Не считать потерей.
- **📌 Murdock's НЕ вернёт свои карты из-под их Web Up:** второй режим (Legal Justice) требует чару **mv ≥4**, а Web Up стоит {2}{W} = mv 3.
- **Итог прогона: 1W–0L.**

### W — ✅ ПОБЕДА (ты 11 / опп 0, 24 хода) · 24.07 · **UNBLOCKABLE-CLOSE — Stature 6 атак без единого блока; опп слил removal в наши ФЛАЕРЫ**
- Опп = **WB Hero/Villain goodstuff-мидрейндж**: Brave Brawler, Hero in Training ×2, Elektra Daughter of the Hand, Crowd of True Believers, Kingpin's Enforcers, Mockingbird, HYDRA Troopers, Black Widow Super Spy, Agent Maria Hill, **Stolen Stark Tech + свой S.H.I.E.L.D. Spy Kit (×5 активаций) + Robot Domination**. Removal: Hour of Defeat, Web Up.
- **Линия победы: Stature, Size Shifter прошла НЕЗАБЛОКИРОВАННОЙ 6 раз подряд** (т12, 14, 16, 18, 20, 22). Решающий удар т22: опп **9 → 1**.
- **⚙️ ТОЧНАЯ МЕХАНИКА (проверено по сырому логу, grpId 104970 / instanceId 261 — первая формулировка была неточной): P/T во времени 1/1 → 7/7, power-up потрачен ОДИН раз** (в финальном состоянии лога он уже в `inactiveActions`; «×2» в сводке движков — артефакт парсера). Рабочая линия: **атака как 1/1 → блоки объявить нельзя («не может быть заблокирована, пока сила ≤1») → ПОСЛЕ объявления блоков активировать power-up → урон наносит уже 7/7.** Power-up — активируемая способность без ограничения по таймингу, поэтому это легально. Арифметика сходится: опп 9 − 7 = 1–2 (расхождение в 1 — известное запаздывание лайфтоталов в логе).
- **📌 Это прямое подтверждение правила `msh_pilot.md` §8 «Stature: качать ТОЛЬКО после объявления блоков».** Памп в главную фазу поднял бы силу >1 ДО блоков → её зачампили бы токеном за 1 ману вместо 7 урона в лицо. «7/7» и «неблокируемая» не противоречат друг другу: она 1/1 на шаге блоков и 7/7 на шаге урона.
- **🔑 Ошибка оппонента, из которой надо учиться (это НАШ же задокументированный лик, увиденный со стороны): оба его removal ушли в наши ЛЕТАЮЩИЕ тела** — Hour of Defeat → Giant-Sized Flying Ant (т13), Web Up → Kree Commandos (т15) — **а неблокируемую Stature он не тронул ни разу.** Наши флаеры он мог заблокировать своим воздухом; Stature — не мог ничем. Прямое подтверждение иерархии `msh_pilot.md` §2 **«сначала то, что я НЕ могу заблокировать»**.
- **Лайфгейн + широкая доска против неблокируемого клока не работают:** в финале у оппа **6 существ против наших 3**, он лечился ≥5 раз (Brave Brawler lifelink, Crowd ×3, Hero in Training, Kingpin's lifelink), отлечился с 1 обратно до 5 — и всё равно умер. Наземная стена не блокирует неблокируемое, лайфгейн лишь оттягивает.
- **⚠️ ПОДТВЕРДИЛАСЬ НАЗВАННАЯ ПРИ СБОРКЕ СЛАБОСТЬ: обе Murdock's Crusade умерли в руке — у оппа НЕ БЫЛО легальных целей.** Murdock's требует тафнесс ≥4, вся его доска ≤3 (2/2, 1/2, 2/1, 3/2, 2/3). Партию вытащил клок, а не интеракция. **Вывод: против низко-тафнесовых WB/агро-колод Murdock's = мёртвая карта, план строить на неблокируемом/воздушном клоке.**
- **✅ Political Triumph сработала ×5** и на этот раз дошла до payoff (т10, сакнулась → добор + +1/+1 на команду) — в отличие от прошлой партии, где её сняли Web Up'ом.
- **Итог прогона: 2W–0L.**

### L — ❌ ПОРАЖЕНИЕ · 24.07 · **OUT-ENGINED — Madame Masque токен-флуд + Yellowjacket lifelink, Murdock's condition не берёт мелкие тела**
- Опп = **UB Villain go-wide/lifegain**: Yellowjacket Heartless Marauder (⚡×5, +1/+0 + lifelink на каждый Villain), Atlantean Cavalry, Madame Masque (токен-фабрика, ⚡×3), Futurist Forge, Klaw Sonic Subjugator, Leader Super-Genius.
- Кип на грани (3 земли + Political Triumph T1 + три тела на 4-4-5, без 2-дропа) — приемлемый, не топ-тяжёлый.
- **🔴 КОРНЕВАЯ ПРИЧИНА: Madame Masque вышла т9, наштамповала токен, ЕЩЁ токен т11 — единственный точечный removal (Murdock's, condition тафнесс≥4) физически не мог её взять.** Ушёл в Atlantean Cavalry вместо неё (т10). Повтор задокументированного паттерна `msh_pilot.md` §2 («Masque вышла т9, заэксайлена т14 — 5 ходов флуда = переезд») — здесь ответа вообще не нашлось, не «поздно взяли».
- **🔴 Yellowjacket (их лайфгейн-мотор) не тронут НИ РАЗУ за 5 активаций.** Каждый их Villain-каст = +1/+0 + lifelink → жизни 20→23 на т9, пока мы падали 20→9. Depower — не removal (-4/-0), реального ответа на него в колоде не было (Web Up не пришёл).
- **✅ Political Triumph сработала ×5**, выполнила свою работу (scry+counters), не в ней проблема.
- **Вывод — СТРУКТУРНЫЙ, не пилотский:** Murdock's Crusade condition (тафнесс≥4) не бьёт токен-рои/мелких Villain-движков (Masque, Yellowjacket) — только Web Up бьёт что угодно, и он один на весь мейн. Против UB Villain go-wide/lifegain это узкое место колоды, не ошибка розыгрыша.
- **Итог прогона: 2W–1L.**

### L — ❌ ПОРАЖЕНИЕ · 24.07 · **OUT-TEMPO — их Tigra+Spy Kit дважды пробили по 5-6 рано, играли вдогонку до конца**
- Опп = **GW Hero-темпо**: Tigra Feline Fury (под их S.H.I.E.L.D. Spy Kit, ⚡×3, росла 2/1→5/4→6/5), Hero in Training ×3, Agent Phil Coulson (движок +1/+1 на Heroes), Wakandan Drone Flock, Borough Backup, Web Up. Их Spy Kit сработал ×5.
- Кип 3 земли + 4 играбельных — верный.
- **🔴 Корень: их Tigra+эквип дважды пробила по большому куску (т8: 20→15, т10: 15→9), пока у нас не было ответа на столе.** Web Up ушёл в свежевышедшую Wiccan (т10, до value) вместо их клока — размен по таймингу невыгодный, но не ошибка (Tigra тогда ещё не подходила под условия наших removal).
- **✅ Murdock's сработал точно (т11, эксайл Tigra)** — убрал угрозу, как только тафнесс подошла. Но к этому моменту счёт уже 9 vs 22 — инициатива потеряна безвозвратно.
- **Финал т16: их альфа 4 атакующими (Coulson, Drone Flock, Hero in Training, токен) с 14 жизней — смертельна**, у нас на столе только 2 тела (Ant свежевышедший, Kree Commandos), заблокировать всё физически нечем.
- **Вывод — структурный проигрыш темпу**, не пилотская ошибка: ранний разрыв 6-7 жизней под их эквип-клоком определил всю партию, дальше играли вдогонку.
- **Итог прогона: 2W–2L.**

### W — ✅ ПОБЕДА (ты 17 / опп 10, 19 ходов) · 24.07 · **GRIND-OUT — 4 тела давят стабильно, Murdock's точно в их движок**
- Опп = **UB Hero-темпо/копир**: Echo Perceptive Prodigy (копирует триггеры), The Wondrous Wasp (flash flying, tap-strip), Stolen Stark Tech ×2, Ghost Spectral Saboteur, We Say Thee Nay!, Dark Deed. Соперник мулиганил.
- Кип 4 земли + Depower/Forge/Helper — верный.
- **✅ Murdock's Crusade сработал точно (т12): эксайл Echo, Perceptive Prodigy** — снял их копи-движок в момент, когда тафнесс подошла; сразу же счёт выровнялся 17 vs 17 → преимущество перешло к нам.
- **Наш Captain Mar-Vell законтрен их We Say Thee Nay! (т10)** — небольшая потеря темпа, партию не переломила: на столе оставалось ещё 2 тела.
- **Движки: Political Triumph ×5, S.H.I.E.L.D. Spy Kit ×4** — грайнд-режим отработал как задумано, Brave Brawler+Hydraulic Helper давили почти каждый ход (21→17→13→10).
- **Не разгром, а устойчивый грайнд:** после раннего давления Wasp+Echo (20→17) стабилизировались и медленно выдавили — ровно та роль (плотный грайнд + точечный removal), под которую колода собрана.
- **Итог прогона: 3W–2L.**

### W — ✅ ПОБЕДА (ты 5 / опп 3, 20 ходов) · 24.07 · **RACE-ПОД — почти зеркальный WU/WR, Murdock's ×2 в их движок решил темп**
- Опп = **WR темпо** (почти зеркало): своя Political Triumph (⚡×6), War Machine Legacy of Iron (репитинг-памп, ⚡×4), Super-Soldier Serum, Thor Odinson, Hero in Training, HYDRA Infiltration. Соперник мулиганил.
- Кип 3 земли + 4 играбельных, оба игрока разыграли Political Triumph уже на т1-2.
- **✅ Web Up снял их Super-Soldier Serum (т10)** — движок/эквип, не тело, правильный приоритет.
- **✅ Murdock's Crusade сработал ДВАЖДЫ точно по цели:** т14 эксайл Thor Odinson, **т18 эксайл War Machine, Legacy of Iron** (их репитинг-памп-движок, ×4 активации до этого) — без него их темп рухнул с 5 жизней до 3 без ответа, решающий момент партии.
- **Партия была чистой гонкой, не грайндом** — оба игрока падали параллельно (23→17→16→11→6→5 vs 20→17→10→5→3→0), темп решил на 1-2 хода раньше.
- **Т16-17 — обмен в лоб на грани смерти** (мы 11→6, опп 10→5→2), их Repulsor Blast срубил Captain Mar-Vell в ответ на атаку — но темп уже был впереди.
- **Итог прогона: 4W–2L.**

### L — ❌ ПОРАЖЕНИЕ (22 хода) · 24.07 · **OUT-ENGINED — HYDRA Assault Robot ×7 пингов, точечный removal не успевает за конвейером артефактов**
- Опп = **BR HYDRA Villain/артефакт go-wide**: HYDRA Assault Robot (⚡×7 — 1 урон за каждый вход Villain/артефакт), Super-Adaptoid, Machinesmith Automaton, Red Room Recruit, Crimson Operative (⚡×4), Kree Sentinel, Red Hulk, Ares God of War.
- Кип на 2 землях с дешёвой рукой (Helper/Brawler на 2) — по правилу приемлемый, но не повезло: застряли на 2-3 землях половину партии.
- **🔴 КОРНЕВАЯ ПРИЧИНА: HYDRA Assault Robot сработал ×7 — постоянный конвейер их артефактов/Villain-ов запускал пинг с каждым выходом.** Урон 20→19→18→17→**8**→7→6→3: один ход (т16) снял 9 жизней разом (накопленный пинг + атака).
- **✅ Оба removal сработали ТОЧНО по цели** (Web Up → Red Hulk т15, Murdock's → Kree Sentinel т19) — но ни один не пошёл в сам Assault Robot: тафнесс 3 не подходила под Murdock's, а Web Up был потрачен раньше на более крупную угрозу.
- **Вывод — прямое подтверждение `msh_insights.md`: «HYDRA Assault Robot + go-wide = точечный removal слишком медленный, нужен масс-эффект/бланк ширины, которого у деки нет».** Не пилотская ошибка — у колоды физически 2 removal-слота на партию против непрерывного потока их существ.
- **Итог прогона: 4W–3L.**

## 🆕 ПРОГОН 25.07.2026 · WU темпо (Depower ×2 / Ghost / Mockingbird+Colleen Wing target-pump / I Am Iron Man) — новая колода, 43 карты

### W — ✅ ПОБЕДА (ты 17 / опп 0, ~27 ходов) · 25.07 · **RACE-ПОД, тягучая — эвейжн (Ghost+Ant) закрыл раньше их движков**
- Опп = **GU Villain/counters-снежок**: Undercover Skrull, The Astonishing Ant-Man (токен-фабрика от +1/+1 счётчиков), Falcon Winged Wonder+Redwing, Atlantean Cavalry, **Savage Land Dinosaur 7/6 trample**, Ant-Man's Army, Construct a Cosmic Cube.
- Кип 3 земли (2 Island/1 Plains) + 4 играбельных — верный, не топ-тяжёлый.
- **✅ Движки сняты ВОВРЕМЯ, оба точно по приоритету:** Trickster's Stratagem → **The Astonishing Ant-Man** (ход 12, токен-фабрика убрана до разгона), Super Villain Lockup → **Savage Land Dinosaur** (ход 16, эксайлен ПОКА ТАПНУТ — правильное окно, самая крупная угроза партии снята без размена).
- **Оба Depower ушли на Falcon** (закрывали его атаки temp-ответом) — постоянного removal на него так и не пришло (Murdock's Crusade добрался в руку уже позже, когда Depower были потрачены — не выбор, а порядок добора).
- **Линия победы: Ghost (неблокируемый) + Giant-Sized Flying Ant (flying) утилизировали план — опп 21→18→14→9→7→2→0**, пока наши блокеры (Raft Security Officer, Agents of S.H.I.E.L.D., A.I.M. Scientists) держали фронт от их наземной ширины.
- **Разбор на ошибки (по запросу) — ничего не найдено.** Проверены обе спорные точки: Captain Mar-Vell экзайлен их Cruel Alliance (т11) — легальный безусловный ответ через teamwork-режим, непредотвратимо; H.E.R.B.I.E. разменян на токен Redwing (т9) — уже отработал ETB-добор, не потеря ценности.
- **Итог прогона: 1W–0L.**

### W — ✅ ПОБЕДА (~ты 10 / опп 0, 16 ходов) · 25.07 · **RACE-ПОД под давлением — Mar-Vell добил ровно на 4, пока их флаер был тапнут**
- Опп = **BR HYDRA Villain-снежок**: Loki Laufeyson (спелл-копи движок), **Crossbones, Malicious Mercenary** (deathtouch + пинг 2 на каждый входящий Villain, вырос до 5/5), **Fin Fang Foom 3/5 flying** (спелл-копи + счётчики), Kingpin's Enforcers (sac-аутлет), Agents of HYDRA, **Thunderbolts Conspiracy** (возвращает погибших Villain с finality counter).
- Кип 3 земли (1 Plains/2 Island) + дешёвая рука — верный; Captain America, Super-Soldier {W}{W} временно некастуем (1 Plains), но остальное играбельно на синем.
- **⚠️ Frozen in Ice на Crossbones обнулён их же комбо:** Kingpin's Enforcers сакнул Crossbones → Thunderbolts Conspiracy вернул его с finality counter — новый объект, наш Frozen ушёл в GY вместе со старым. Не пилотская ошибка (нельзя было предвидеть их sac-connection), но фиксирует, что **лок уязвим к sac-based recursion** в BR Villain-матчапе.
- **Оба игрока обменивались тяжёлыми ударами** (ты 20→18→14→12→10, опп 21→18→16→10→4) — партия шла ноздря в ноздрю, не грайндом.
- **✅ Закрывающий удар точный: Captain Mar-Vell (4/4 flying vigilance) атаковал в одиночку на опп с 4 жизнями, пока их ЕДИНСТВЕННЫЙ летающий блокер (Fin Fang Foom) стоял тапнутым** — ровно летально, чисто прочитанное окно.
- **Итог прогона: 2W–0L.**

### L — ❌ ПОРАЖЕНИЕ (19 ходов) · 25.07 · **OUT-ENGINED — Crimson Operative ×4 (движок сработал ×15!) + Thor, God of Thunder бёрн, в колоде нет ответа на артефакт-снежок**
- Опп = **UR artifact/spellslinger Villain**: Shuri, Wakandan Inventor (артефакты дешевле + копи-движок), **Crimson Operative ×4** (prowess + impulse-draw при входе, суммарно активировалась **×15** за партию), **Thor, God of Thunder 5/5 flying** (урон = mv их некриатур-спелла в любую цель, при входе возвращает Equipment/instant/sorcery из GY), Ms. Marvel Kamala Khan, Justice, Vance Astrovik, Frozen in Ice.
- Кип 3 земли (верный сплит, 4 играбельных спелла) — не топ-тяжёлая, мулиган не требовался.
- **🔴 КОРНЕВАЯ ПРИЧИНА: 4 копии Crimson Operative дали 15 активаций импульс-драва/prowess — постоянный поток карт и растущих тел, с которым точечный removal физически не мог сравняться.** У нас не было ни одной карты, отвечающей на артефактных существ массово или на сам card-advantage-движок.
- **Thor, God of Thunder добавил урон поверх** — каждый их некреатур-спелл (Trickster's Stratagem ×2 и т.д.) бил напрямую в лицо/существо помимо обычного урона в боях. Жизни падали синхронно с их спеллами: 20→18→12→8→5→2→6(частично отыграли)→2→0.
- **Наш план (эвейжн-гонка) не успел собраться:** Colleen Wing и оба Captain America умерли/застряли под давлением рано, Captain Mar-Vell (закрывашка) вышел только на ходу 18 — на 5+ ходов позже, чем нужно было против такого темпа.
- **Вывод — структурный, не пилотский:** против UR artifact-снежка (много дешёвых артефактных тел + card advantage engine) колоде нечем ответить массово — только точечный removal (Frozen/Murdock's/Lockup/Trickster's), которого не хватает на 4+ копии одной угрозы. Отмечать в knowledge как контр-матчап архетипа.
- **Итог прогона: 2W–1L.**

### W — ✅ ПОБЕДА (ты 14 / опп 7→0, 23 хода) · 25.07 · **GRIND-OUT — Living Legend untap-движок ×6 + точный removal, добито I Am Iron Man**
- Опп = **GW-ish Villain/Hero микс**: Serpent Specialist, Undercover Skrull, Kingpin's Enforcers, Brave Brawler, Knight of Wundagore, Tigra Feline Fury, Mockingbird Ace Agent, Fisk Tower.
- Кип 3 земли (верный сплит W/U) + 4 играбельных — не топ-тяжёлая.
- **✅ Точный removal по приоритету:** Murdock's Crusade → **Kingpin's Enforcers** (ход 7, снят сразу как вышел), Frozen in Ice (ход 13) залочил их растущую угрозу.
- **🌟 Captain America, Living Legend untap-движок сработал ×6** — весь грайнд держался на нём: тапал Patriot/Agents повторно за ход, не жертвуя атакой ради активаций.
- **Добивающий удар: I Am Iron Man на ходу 21** (превратил своё тело в 4/4 flying + добор) пробил опп с 15 до 7 за один ход — решающий момент, дальше Captain Mar-Vell и Super Villain Lockup дожимали.
- **Партия была именно грайндом, не гонкой:** жизни держались стабильно (мы 12-14 всю вторую половину, опп плавно падал 21→18→17→15→7→0) — план колоды (тела+точечный removal+untap-движок) отработал так, как задуман для полосы CABS/мидрейндж, не воздушной гонки.
- **Итог прогона: 3W–1L.**

### L — ❌ ПОРАЖЕНИЕ (15 ходов) · 25.07 · **OUT-ENGINED — Killmonger sac-removal съел наш борд, Titania (ward) продавила, Cruel Alliance закрыл дверь перед альфой**
- Опп = **BG мидрейндж removal/value**: Red Room Recruit ×2 (connive, recurring), **Titania, Rugged Rumbler 5/5 ward** (discard/pay {2} — дорого доставать), **Killmonger, Scourge of Wakanda** (sac-a-creature → destroy nonland permanent, растёт +2/+1 от 2+ существ в своём GY), Powerful Broker (counter-doubler), Agents of HYDRA, Cruel Alliance (teamwork-эксайл).
- Кип 3 земли + 4 играбельных — верный, не топ-тяжёлая.
- **🔴 КОРНЕВАЯ ПРИЧИНА: каждое наше существо умирало 1-в-1, а собственного removal в этой партии не пришло вообще.** Justice пал в бою (т8), Bold Biochemist и Giant-Sized Flying Ant — оба на ходу 10 (Ant, вероятно, под sac-destroy Killmonger), Agents of S.H.I.E.L.D. чампнул Titania (т12, вынужденно — 5/5 без блока было ещё хуже), Brave Brawler эксайлен Cruel Alliance ровно как разыгран (т14). Ни разу за 15 ходов мы не сыграли ни Frozen, ни Murdock's, ни Lockup, ни Trickster's — все четыре карты removal не пришли в руку.
- **✅ Блок Agents of S.H.I.E.L.D. на Titania (т12) — правильный вынужденный чамп**, не ошибка: 5/5 ward стоит дорого доставать точечным removal, блокировать дешевле, чем терять 5 жизней за раз.
- **Добивающая альфа т14: Powerful Broker + Agents of HYDRA + Killmonger все прошли не заблокированными — 10→1 за один ход**, борд к этому моменту у нас — пусто (последнее тело умерло тем же ходом от Cruel Alliance).
- **Вывод — структурный, не пилотский:** матчап решило отсутствие removal в руке всю партию (variance), не ошибки в блоках/атаках. BG с sac-based removal + ward-бомбой — тяжёлый матчап для колоды без ответа на растущего Killmonger.
- **Итог прогона: 3W–2L.**

### W — ✅ ПОБЕДА (ты 17 / опп 5→0, 20 ходов) · 25.07 · **ЗЕРКАЛО WU vs WU — плотность мелких тел передавила, removal точно по эвейжну**
- Опп = **почти зеркальная WU-темпо**: Ghost Spectral Saboteur (неблокируемый), Captain America Living Legend (untap-движок), Spider-Woman Secret Agent, Knight of Wundagore, Frozen in Ice ×2, Giant-Sized Flying Ant, Restorative Technique.
- Кип 4 земли + 3 дешёвых спелла (1-2-2) — не флуд, играбельно с первого хода.
- **✅ Removal точно по приоритету эвейжна:** Murdock's Crusade → **Spider-Woman, Secret Agent** (т12), Super Villain Lockup → **Ghost, Spectral Saboteur** (т14, их неблокируемый клок снят на месте) — ровно та иерархия «неблокируемое > летающее > наземное».
- **Опп дважды заморозил нам тела (Frozen in Ice ×2 в финальном борде у них)**, но это не остановило план — план победил не одним клоком, а ШИРИНОЙ дешёвых тел: Crowd of True Believers, H.E.R.B.I.E., Hero in Training, Colleen Wing атаковали КАЖДЫЙ ход параллельно, опп не успевал блокировать/лочить всё сразу (16→15→10→5→0).
- **Captain Mar-Vell (т10) не был центральным клоком в этой партии** — вошёл рано, но победу сделала именно плотность мелких тел, не он один.
- **Показательный зеркальный матчап:** обе колоды играли одинаковый план (тела+точечный removal+Ghost/эвейжн) — победила та сторона, что раньше и точнее сняла ключевую эвейжн-угрозу оппонента (наш Lockup на их Ghost решил партию раньше, чем их Frozen — на нас).
- **Итог прогона: 4W–2L.**

### L — ❌ ПОРАЖЕНИЕ (25 ходов) · 25.07 · **OUT-ENGINED — Human Torch ×12 + Mister Fantastic ×8 + Stark Industries Executive ×6 токенов, точечный removal физически не успевает**
- Опп = **UR artifact/spellslinger go-wide**: Speed Young Avenger, Shuri Wakandan Inventor, **Mister Fantastic, Reed Richards** (⚡×8), Jessica Jones Private Eye, **Stark Industries Executive** (⚡×6 — токен на каждую активацию), **Human Torch, Johnny Storm** (⚡×12!), Aerial Doombot ×2, Armor Wars, Ultron Drone, Super Suit, The Scarlet Witch, Frozen in Ice.
- Кип пограничный (4 земли, все 3 спелла требуют {U} при 1 Island) — но заявленно честно, не топ-тяжёлый; риск реализовался как медленный старт (первый спелл сыгран т4), не решающий фактор проигрыша.
- **🔴 КОРНЕВАЯ ПРИЧИНА: суммарный движковый вывод оппонента (Torch ×12 + Fantastic ×8 + Executive ×6 токенов) на порядок превысил объём removal колоды.** Единственный permanent removal (Super Villain Lockup → Jessica Jones, т11) снял одну угрозу — против непрерывного потока токенов/value это капля.
- **Финальный борд: у нас 3 существа, у оппа 8** — плавное выдавливание, не один блоу-аут-ход: жизни падали устойчиво т17→25 (22→14→13→11→6→8) под давлением растущей ширины.
- **Trickster's Stratagem и Depower ушли реактивно**, но не по движкам (Executive/Torch/Fantastic) — целей на сам движок не нашлось или не подошли по условиям.
- **Вывод — структурный, прямое повторение паттерна 24.07 (HYDRA Assault Robot) и 25.07 (Crimson Operative ×4):** третий проигрыш ПОДРЯД в knowledge-паттерне «движковый go-wide/артефакт-снежок превосходит точечный removal колоды». Колоде физически не хватает массового ответа (свипера/анти-ширина) против этого класса архетипов — драфт-приоритет на будущее.
- **🏁 ПРОГОН ЗАВЕРШЁН: 4W–3L** (3-е поражение, лимит прогона достигнут).
