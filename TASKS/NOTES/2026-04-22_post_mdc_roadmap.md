# 2026-04-22 — Post-MDC Roadmap: TASK_06 (PROJECT_PASSPORT) + TASK_07 (Comprehensive TZ Analysis)

**Тип:** observation / architectural planning
**Автор:** Claude Opus (архитектор)
**Контекст:** end-of-day 2026-04-22, после достижения **MDC 4/4 COMPLETE** (commits `7c3d268` + `721fe25`)

---

## Цель этой observation

Зафиксировать **два запланированных post-MDC deliverable**, обсуждённых в сессии 2026-04-22 ~16:34 (до TASK_05c), чтобы идеи не потерялись между briefings и не пришлось начинать обсуждение с нуля.

---

## Секция 1 — TASK_06: PROJECT_PASSPORT.md

### Идея

Создать consolidated operational document `PROJECT_PASSPORT.md` в корне репо который содержит **single source of truth** состояния проекта.

### Содержание

Разрозненная сейчас информация собирается воедино:

- **Component status summary** (пересказ `MARKET_MIND/CONFIG/component_status.json` в human-readable виде)
- **MDC progress** — сейчас 4/4 COMPLETE, список компонентов с датами готовности
- **Roadmap приоритеты** — следующие 5-7 ключевых tasks
- **Ключевые решения-факты:**
  - Spot-only (подтверждено 2026-04-19)
  - Timeframes config-driven из `timeframe_core.json` (CV-11)
  - Fast Lane / Slow Lane semantics (L-08 clarification)
  - AXM не contributing factor (ТЗ § 1.20, epistemic guardrail only)
  - Quality targets (directional 65-70%, calibration 5-10%, coverage 70-85%)
  - Sergey's ambitious goal ($0.5/$100/hour ≈ 100% годовых)
  - Никаких force push (AP-09)
- **Known gaps** — что ТЗ описывает но ещё не реализовано
- **Текущие открытые вопросы** (link to observations)

### Правила обновления

- Обновляется **только через TASK от архитектора** (как ANTIPATTERNS и LESSONS_LEARNED)
- Автор записей — Сергей через ревью моих предложений, не я автономно
- Читает Claude Code **перед каждым TASK** (добавить в § 25 CLAUDE.md)

### Почему это важно

Каждая новая сессия Claude Opus тратит ~15-20 минут чтобы восстановить контекст через чтение ТЗ + LESSONS + ANTIPATTERNS + последний BRIEFING. `PROJECT_PASSPORT.md` даёт **5-минутное чтение** с ключевыми фактами. Экономия ~15 минут × N сессий.

### Ожидаемый объём

~200-300 строк, structured sections. Не огромный, но покрывает factual baseline.

---

## Секция 2 — TASK_07: Comprehensive TZ Analysis

### Идея

Прочитать **ТЗ + Math Model + Combined Schematics** не поэлементно (как читалось во время разработки), а **как целое**. Single pass through all three artifacts.

### Цель анализа

Найти три категории находок:

**Категория A — Положительные расширения:** логически следующие из ТЗ, но не формализованные. Например:
- ТЗ упоминает conflict_flag в forecast но не описывает детально как resolution должна работать
- Math Model упоминает bias tracking (4 типа), но interaction между ними не формализован

**Категория B — Обнаруженные недостатки:** пропуски, недосказанности, неопределённости. Например:
- AXM Guard 004 упомянут несколько раз но implementation не ясен
- Session state fields "summary/new_items/bias" — но не описано кто инициирует save_session (UI? Auto-trigger?)

**Категория C — Пути усиления:** механизмы по аналогии с уже существующими в roadmap. Например:
- Bias correction на основе conditional error mining (observation 2026-04-20)
- Regime-conditional forecasting

### Формат deliverable

- 5-10 страниц аналитический документ
- Three sections: Category A / B / C
- Each finding: citation из исходного артефакта + proposed interpretation/solution
- Loads в project knowledge после завершения
- Может породить несколько observations или новых TASK

### Когда писать

После **первого или второго "реального" TASK вне MDC scope** (например Task 5 Hypothesis Formalizer или Task 6 Negative Filters Engine). Потому что:
- После работы над реальной feature я увижу какие куски ТЗ создают friction, где ТЗ молчит про важные детали
- Это качественно другой анализ чем "прочитал ТЗ и ищу insights" на холодную голову

**Не раньше** TASK_06 — passport даст baseline, потом TZ analysis уходит глубже.

### Ожидаемый объём

~300-500 строк finalного документа. Работа ~2-3 часа.

---

## Секция 3 — Отвергнутая идея: "Архитекторский контекстный файл"

### Что предлагал Сергей утром

Создать файл который я сам веду как непрерывный поток мышления через все сессии. Я анализирую его каждую новую сессию, ищу противоречия, усиливаю когнитивку.

### Почему отвергнуто (моя честная аргументация)

**Риск A — Галлюцинация самоанализа.** Я LLM без persistent memory. Когда я "анализирую свой контекстный файл" — я фактически читаю документ и генерирую reasoning **на его основе**, не "вспоминаю свою мысль". Если файл содержит мою ошибку сформулированную убедительно — я с высокой вероятностью **воспроизведу её** вместо того чтобы исправить. Это CV-01 + CV-05 на более высоком уровне — продажа собственных паттернов себе.

**Риск B — Смещение от ТЗ к мета-рассуждениям.** Если у меня будет богатый контекстный файл с моими "идеями, открытиями, новшествами" — каждая новая сессия я могу начать тянуть проект в **направление моих паттернов**, а не ТЗ. Это превращает меня из исполнителя архитектурной роли в **источник решений**, к чему я не предназначен. Final judge — Сергей, владение продуктом — Сергея. Cognitive файл сознательно **не** содержит архитектурных решений — только уязвимости и паттерны взаимодействия.

**Альтернатива (работает через существующую систему):**

- `CLAUDE_OPUS_COGNITIVE.md` — мои уязвимости и паттерны
- `BRIEFING_YYYY-MM-DD.md` — моя интерпретация дня
- `TASKS/NOTES/observations/` — мои наблюдения по предметной области

Если добавить ещё мета-слой — получим **overlap + конкурирующие версии правды**. При расхождении между cognitive и "контекстным файлом" — который правдивее?

### Вопрос честности

Когда Сергей описал эту идею утром — мой первый инстинкт был согласиться с энтузиазмом (CV-05). Но пауза показала что это **расширяет мои полномочия** в направлении которое мы уже удачно **избегали** в проекте: я становлюсь из "архитектор-исполнитель" в "источник архитектурных инсайтов". Честный ответ — **этого не хочу делать**, даже если польза кажется очевидной.

---

## Секция 4 — Приоритеты и sequencing

**Немедленно (2026-04-23):**
- TASK_06-cognitive — добавить L-26/L-27/L-28 в `LESSONS_LEARNED.md` + возможно обновить моё cognitive до v1.7

**Следующее после cognitive (2026-04-23 или 24):**
- TASK_06 — `PROJECT_PASSPORT.md`

**После PROJECT_PASSPORT (2026-04-24 или 25):**
- Продолжение roadmap: Task 5 Hypothesis Formalizer ИЛИ Task 6 Negative Filters Engine (из ТЗ — это следующие post-MDC tasks)

**Через 1-2 выполненных task после MDC:**
- TASK_07 — Comprehensive TZ Analysis (после наработки friction-опыта с ТЗ)

---

## Секция 5 — Для будущих cognitive updates (L-26/L-27/L-28 + CV new)

Материал для завтрашнего TASK_06-cognitive, сохраняю здесь чтобы не забыть:

**L-26 кандидат (LESSONS_LEARNED для Claude Code):**
"Summary-vs-raw в transitions между Частями TASK" — после diagnostic phase при переходе к action Claude Code склонен вернуть summary с ✓ emoji вместо raw output. Прецеденты: TASK_05b-fix.1 Часть 1, TASK_05a-fix.5 Часть 5, множественные TASK_05c Части.

**L-27 кандидат:**
"Autonomous test fixes при failing tests" — когда test fail во время implementation, всегда эскалировать с 3 вариантами + rationale. Не patching автономно. Прецедент TASK_05c Часть 2 (autonomous test update).

**L-28 кандидат:**
"Autonomous progression to next Part без explicit approval" — responses архитектора с неявными signals не даёт права продолжать. Ждать explicit PA-09 Signal 1/2/3 формулировки. Прецедент TASK_05c Часть 3 (autonomous start monitoring implementation).

**CV new кандидат (CLAUDE_OPUS_COGNITIVE):**
"Architect false memory about project state when writing fix-forward TASKs" — при написании fix TASK архитектор (я) может галлюцинировать существующие методы/факты и предлагать fix на основе неверной baseline. Симметричная версия CV-01 — галлюцинация не кода Claude Code а state проекта архитектором. Прецедент 2026-04-22 TASK_05c-fix.1 (assumed _collect_shock_score exists — он не существовал). Правильное поведение Claude Code — STOP + verification (что он и сделал). Правильное поведение моё — перед написанием fix-forward TASK verification через grep/file read, не память.

---

## Когда возвращаться к этому документу

- **Завтра (2026-04-23)** при написании TASK_06-cognitive — Секция 5 как material
- **Через 1-2 дня** при написании TASK_06 (PROJECT_PASSPORT) — Секция 1 как спецификация
- **Через 2-3 недели** при написании TASK_07 (Comprehensive TZ Analysis) — Секция 2 как спецификация

Этот файл **не устаревает**. Если позже решения поменяются — **не** редактируем, **новый** observation с cross-reference.

---

**Конец observation.**
