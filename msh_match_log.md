# MSH — История партий (лог с причиной результата)

Ведётся после каждого `analyze_game.py`. **Только проверенное по логу** (см. память `mtg-analyze-game-accuracy`) — жизни/борд/GY реслайсить, не по памяти. Причина категоризирована, чтобы ловить ПАТТЕРНЫ проигрышей во времени.

**🏁 ФОРМАТ: Premier draft — ПРОГОН ДО 3 ПОРАЖЕНИЙ (или 7 побед).** Играем всегда до 3 losses. Лог кросс-прогонный (деки менялись между прогонами); отслеживать W–L ТЕКУЩЕГО прогона, при новом драфте — новый прогон.

**▶ ПРОГОН ЗАВЕРШЁН (tempo-эвейжн): 6W–3L — трофей упущен на 1 победу.** Старт 0–2 мягкой серединой → рефокус в tempo-эвейжн → **6W подряд (comeback)** → проигрыш G10 (OUT-ENGINED vs UG counters + клунки-кип). **Отличный ран.** Следующий драфт = новый прогон.

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
