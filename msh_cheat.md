# MSH — Marvel Super Heroes · драфт-référence (полный пул)

Arena **23.06.2026** / бумага **26.06.2026** — **полноценный драфтируемый сет в MTG Arena**.
**17Lands LIVE с 25.06** — `17l_msh_premierdraft.json` залит (≈320 карт, выборки 0.3–3k, ранние но directional), `msh` в RATING_FILE → `draft_live.py msh` РАБОТАЕТ. Освежать периодически: `curl ".../card_ratings/data?expansion=MSH&format=PremierDraft"`.
Полные данные: `msh_set.json` (281 карта).

## Тир пар цветов (17L, 25.06, ≥800 игр) — White лучший
🥇 WU 60.9 · WG 60.0 · UG 58.7 · WR 58.4 · WB 57.8 · 🟡 UB 55.9 · BG 54.6 · UR 53.4 · 🚫 BR 50.7.
Все 4 белые пары ≥57.8 — **при сомнении тянись в White.** BR (Villains-агро) недодаёт несмотря на хайп.
Визуальный чит: `msh_cheatsheet.html` (`python3 build_msh_cheatsheet.py`).

## Сквозные оси сета
- **+1/+1 counters (74 карты!)** — доминирующая механика. Почти каждый зелёный/синий архетип её трогает.
- **Villain трайбал (29)** — чёрно-красный костяк; «whenever a Villain enters» + токены 2/1 menace.
- **Hero трайбал (18)** — бело-красно-зелёный; «other Heroes»/«attacks» баффы.
- **Power-up (24)** — активируемая абилка (раз на способность): мана → большие +1/+1. Дорого без удешевления.
- **Teamwork N (13)** — доп. стоимость: тапни существ с суммарной силой N → бонус. N=1–2 легко, 4+ хочет стол.
- **Connive (11)** — возьми-сбрось; нелэнд-сброс → +1/+1. Фильтр, не чистый добор.
- **Plan (9)** — чары копят plan-счётчики (≈1/ход), отдают на X. Медленные как саги.
- **Landfall (3)** — Ka-Zar, Mole Man, Claim the Kingdom.

## REMOVAL — цени высоко, формат на него СВЕТЛЫЙ
Приоритет пика. По цветам (имя — что делает):
- **W:** Helicarrier Strike (teamwork removal), Red Guardian (destroy attacker, flash), Super Villain Lockup (exile tapped), Web Up (exile nonland), Frozen in Ice-аналог нет (это U).
- **U:** Depower (−4/−X, дешевле на атакующего), Frozen in Ice (pacifism+tap), Secret Invasion (exile-aura), Wiccan (exile при noncreature-касте), Wondrous Wasp (tap+shrink), S.H.I.E.L.D. Flying Car (blink).
- **B:** Hour of Defeat (destroy + surveil — лучший чёрный), Dark Deed (−4/−4), Cruel Alliance (teamwork EXILE — топ), Widow's Bite (teamwork −X−X), Ninja of the Hand.
- **R:** Lightning Strike (3 any — премиум), Truck Toss (4 dmg, дешевле с Vehicle), Avengers Disassembled (3 ко всем ИЛИ destroy — свип!), Mjölnir (4 dmg, equipment), Photon Blast Barrage (XRR копия-бёрн), Repulsor Blast (teamwork dmg).
- **G:** Epic Fight (fight), Punishing Punch (fight, дешевле с GY), She-Hulk (destroy art/ench, power-up), Guerrilla Gorilla (sac → destroy art/ench).
- **Multi:** Killmonger (sac→destroy nonland), Wolverine (ETB fight), Abomination (power-up fight), Serpent Society (deathtouch+ward-яд), Galactus (свип-сага).
- **Бесцветное удаление почти нет** → removal привязан к цвету, тяни в своих цветах рано.

## 10 архетипов (пара → тема → ключевое)
- **BR — Villains-агро.** Сигнпост: Madame Hydra, Ares, Wrecking Crew. Движок: Crossbones, Baron Strucker, Doom Reigns Supreme, токены HYDRA. План: широкий злодейский борд + дрейн/бёрн. Топ: Thanos, Doctor Doom, Black Widow Super Spy.
- **UG — Счётчики + «вторая карта».** Сигнпост: Astonishing Ant-Man, Ant-Man Colony Cmdr, Moon Girl, Beast. Движок: Knight of Wundagore, Doc Samson (удвоение), Training Regimen. «Draw 2nd card»: Atlantean Cavalry, Attuma, Roxxon. Топ: Squirrel Girl, Shang-Chi, She-Hulk.
- **RG — Power-up / большие тела.** Сигнпост: Hulk Gamma Goliath (−3 к power-up), Abomination, Wolverine. Тела: Serpent Specialist, Volcanic Villain, Hercules, Wonder Man (доп. активации). Топ: Red Hulk, Thor God of Thunder, The Thing.
- **RW — Hero-агро.** Сигнпост: Daredevil, Thor Odinson, War Machine. Пайоффы: Phil Coulson, Cap Wings of Freedom, Human Torch, Avengers Assemble! Топ: Thor, Cap Super-Soldier, The Sentry. ⚠ выбери одиночка-вольтрон ИЛИ широкий.
- **BG — Sacrifice / гринд / яд.** Сигнпост: Killmonger, Serpent Society, Galactus. Движок: Grim Reaper (реанимация), Undercover Skrull (GY), Doom Reigns, лайфгейн. Топ: Galactus, Doctor Doom, Squirrel Girl.
- **UR — Артефакты / спеллы.** Сигнпост: Iron Man Master of Machines, Armor Wars, Vision Quest. Движок: Machinesmith, Stark Industries Exec (Treasure), Shuri, Ironheart (improvise), prowess-тела. Топ: Tony Stark//Iron Man, Cosmic Cube, Ultron.
- **WU — Tap / темп-контроль.** Сигнпост: Cap Living Legend, Spider-Woman, Mighty Thor Jane, King T'Challa. Движок: Quake, Raft Security, Rewrite History, soft-removal (Frozen in Ice, Lockup). Топ: Captain Marvel, Cap Super-Soldier.
- **WB — Equipment / вольтрон.** Сигнпост: Winter Soldier (+2/+0 за экипировку), U.S.Agent, Kingpin (extort). Пайоффы: Swordsman, Ronin, Nick Fury, Iron Man Armor. Предметы: Spy Kit, Cap's Shield, Vibranium Daggers. Топ: Black Widow Super Spy, Kingpin, Thanos.
- **GW — Heroes go-wide / counters.** Сигнпост: Black Panther Vanguard, Spider-Man To the Rescue, Storm Windrider. Движок: Okoye, Borough Backup, SHIELD Helicarrier (токены), Political Triumph, Training Regimen. Топ: Storm, Captain Marvel, Squirrel Girl.
- **UB — Connive / Villains / draw-контроль.** Сигнпост: Kang Temporal Tyrant, Taskmaster, Scientist Supreme, Ghost. Движок: connive-тела (Red Room Recruit, AIM Scientists, Madame Masque), Leader, Baron Strucker. Топ: Kang the Conqueror, Doctor Doom, Thanos.

## DFC-мифики — ⚠ ОЦЕНИВАЙ ПО КАСТУЕМОЙ СТОРОНЕ (flip требует КОНКРЕТНЫХ цветов!)
**Правило (не «бери высоко, цвет не коммить»!):** DFC — бомба-финишёр ТОЛЬКО если можешь скастовать ОБЕ стороны в своих цветах. Иначе играешь ЛИЦО (обычно скромный value-крип), а полный GIH **раздут** деками, которые флипают в off-color финишёр. Перед пиком DFC — сверь transform-кост по `msh_set.json`, не бери «на GIH».

| DFC | Лицо | Flip-кост | Флипается (нужны цвета) |
|---|---|---|---|
| **King T'Challa // Black Panther** | {1}{W}{U} | {4}{W}{U} | **WU — в своих же цветах! реальная бомба в WU/UW** |
| Tony Stark // Iron Man | {1}{U} | {4}{U}{R} | UR (нужен **R**); в UB — только лицо (value-крип) |
| Bruce Banner // Hulk | {U} | {2}{R}{R}{G}{G} | RG (нужен **RRGG**); в UB — {U} draw-движок, **НЕ бомба** |
| Jennifer Walters // She-Hulk | {1}{W} | {3}{G}{W}{W} | GW (нужен **G**); в WB/WU — 2-дроп-дисраптор, не финишёр |
| Monica Rambeau // Photon | {2}{W} | {2}{R}{W}{W} | RW (нужен **R**); в WU/WB — только лицо |

Мораль: лицо кастуется → карта играбельна; но **потолок-бомба доступен только при доступе к flip-цветам**. King T'Challa — единственный, кто флипается внутри своей пары.

## Дуальные земли (фикс под сплеш)
- **Лайфгейн-тапленды (common, входят тапнутыми, +1 жизнь):** A.I.M. Labs (UB), Asgardian Citadel (RW), Avengers Hangar (WU), Birnin Zana Plaza (GW), Fisk Tower (WB), Hell's Kitchen (BR), Los Diablos Missile Base (RG), Pym Technologies (GU), Stark Industries (UR), Subterranean Cavern (BG).
- **Rare «painless» дуалы** (Gleaming Bastion WU, Hidden Lair UB, Gathering Place GW, Training Compound RG, Dark Fortress BR).
- **Any-color:** Dependable Quinjet (Vehicle, {T} any), Avengers Tower / Villainous Hideout (Hero/Villain-mana), Stark Industries Exec + Treasure-мейкеры.

## Пик-эвристики MSH
1. **Removal > всё** после бомб — формат светлый на removal, тяни рано в цвете.
2. **Counters — самая безопасная ось:** UG/GW/RG почти всегда открыты, синергия глубокая.
3. **Villain/Hero трайбал** требуют плотности — коммить, только если сигнпост + поток.
4. **Power-up медленный без удешевителя** (Hulk/Wonder Man) — не грузи дорогими power-up телами в агро.
5. **Teamwork N — не хардлок:** N=1–2 кастуй смело, 4+ только при борде.
6. **Коммит пары — середина пака 2** (стримерский late-commit); якорь + 2 кандидата → 2 цвета (+ сплэш по фиксу).
7. **Кривая:** агро (BR/RW) скошен к 2–3; counters/power-up (UG/RG) — больше тел; ~17 земель / 23 нонленда / 2–3+ removal.

## УРОК СБОРКИ: эвейжн + жёсткое удаление считай ОТДЕЛЬНО (UG 2:3, 25.06, data-backed)
Колода UG проиграла матч 2:3 при **нормальной паре** (UG 58.7%, 3-я из 9) и **нормальных картах** (средний GIH 58.3, премиум-двойки Bold Biochemist 61.7 / She-Hulk 61.0). Слита НЕ по качеству карт, а по структуре: **наземный мидрейндж без неба и без жёсткого удаления.** Обе партии — ровно по этим дырам: (1) Black Villain ping-движок (HYDRA Assault Robot — урон **мимо борда**, блок не спасает), (2) UG темпо-флаеры (S.H.I.E.L.D. Flying Car и Ко — **over the top**, наземные тела не блокируют). 17L подтверждает: топ UG-карты, что реально выигрывают, — это **эвейжн** (Falcon 60.9, Falcon's Wing Harness 59.3 *даёт полёт*, Stature 61.6) и **hard removal** (Punishing Punch 62.0 fight, Frozen in Ice 59.1 lock) — ровно чего в колоде не было.

**Правило — при сборке посчитай ДВЕ вещи как жёсткие требования, отдельно от creature-count/curve:**
1. **Hard removal ≥ 2–3** — карта, которая **УБИВАЕТ или ЛОКАЕТ** существо (destroy/exile/fight/Frozen-in-Ice-pacifism). **−X/−0 (Depower) и боевые трюки (Giant Growth) НЕ считаются removal** — они не отвечают ни на движок, ни на уже-вышедшего эвейжн-атакера.
2. **Evasion ≥ 2–3** — флаер / reach / trample / unblockable, **или эквип, дающий полёт** (Falcon's Wing Harness). Стопка ровных наземных тел встаёт в стенку и умирает по воздуху — нужен способ И добивать, И держать небо.
3. **Близкий пик «4-е ровное наземное тело / дорогой Power-up» vs «флаер/removal схожего GIH» → бери флаер/removal.** Дельта-над-заменой у counters-мидрейнджа — это эвейжн+ответы, а не ещё одно тело. (Не противоречит «bodies > non-board engine»: эвейжн и removal — это board/answer, а не durdle-движок.)
4. **Тактика-следствие (в партии):** instant-удаление/Depower держи на атакующего (дешевле, гасит урон когда больно); Wasp (флаер+тап+снятие способностей) — твой ответ на чужой флаер, не выкатывай ванилью под кривую.
