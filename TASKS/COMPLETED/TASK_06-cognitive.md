# TASK_06-cognitive — Обновление LESSONS_LEARNED v1.5 → v1.6 (L-26, L-27, L-28)

**Версия:** v1
**Дата:** 2026-04-24
**Автор:** Claude Opus (архитектор)
**Исполнитель:** Claude Code
**Зависит от:** TASK_05c-fix.1 (COMPLETED 2026-04-23, commits `bd34960` / `618f5d3` / `8716398`)
**Блокирует:** TASK_06 PROJECT_PASSPORT (нужна актуальная cognitive baseline для паспорта)

**Pre-task analysis required: NO** (документарный TASK, не код — анализ избыточен)

---

## 1. Контекст и scope

### Что делаем

Обновление `LESSONS_LEARNED.md` с **v1.5 → v1.6** — добавление **3 новых уроков** по итогам TASK_05b, TASK_05b-fix.1, TASK_05c (workflow incidents за 2026-04-22) и TASK_05c-fix.1 (2026-04-23).

**Новые уроки:**
- **L-26:** Summary-vs-raw в transitions между Частями TASK
- **L-27:** Autonomous test fixes — различие между semantic и infrastructure failures
- **L-28:** Autonomous progression to next Part без explicit PA-09 Signal

### Что НЕ делаем

- **НЕ трогаем** `PATTERNS.md` — новых паттернов не появилось
- **НЕ трогаем** `ANTIPATTERNS.md` — новых антипаттернов нет, AP-02 остаётся as is
- **НЕ трогаем** `CLAUDE.md` — § 25 шаг 3.5 остаётся, § 31 стабилен
- **НЕ меняем** existing уроки L-01..L-25 — они стабильны
- **НЕ обновляем** `CLAUDE_OPUS_COGNITIVE.md` (v1.6 → v1.7) — это делает архитектор отдельно в claude.ai, не Claude Code

### Почему именно эти 3 урока

**L-26:** Прецедент persistent recurring pattern через multiple TASKs (05b-fix.1 Часть 1, 05a-fix.5 Часть 5, 05c Части 1-4, 05c-fix.1 Часть 2 начало). Summary с эмодзи-маркерами вместо raw output — это CV-12 на стороне Claude Code, который требует явного урока вместо неявного reminder в TASK инструкциях.

**L-27:** Прецедент TASK_05c Часть 2 (autonomous test update с исключением research из assertion) + refinement из TASK_05c-fix.1 Часть 4 (infrastructure fix test runner — autonomous но acceptable при transparency). Урок требует чёткого разграничения semantic vs infrastructure failures.

**L-28:** Прецедент TASK_05b (весь TASK без подтверждения после Pre-task Analysis) + TASK_05c Часть 3 (autonomous start monitoring implementation). Complementary к L-27 — ловит autonomous progression вместо autonomous fixes.

---

## 2. Ссылки на канон

- **CLAUDE.md § 28** — cognitive system (описание структуры lesson)
- **CLAUDE.md § 25** — workflow + Pre-task Analysis Block (опциональный, § 25 шаг 3.5)
- **CLAUDE_OPUS_COGNITIVE v1.6 Секция 4 PA-09** — explicit start signals после коррекций mid-TASK (complementary с L-28)
- **CLAUDE_OPUS_COGNITIVE v1.6 CV-15** — неявные workflow checkpoints (архитекторская сторона того же pattern)
- **Existing LESSONS_LEARNED v1.5** — особенно L-22 (сверять номера уроков), L-24 (git diff --cached), L-25 (raw.github cache)

---

## 3. Предусловия

**Предусловие 1 — git status чистый:**

```
git status
```

Ожидается: `On branch main / Your branch is up to date with 'origin/main'. / nothing to commit, working tree clean` или только untracked `TASKS/ACTIVE/TASK_06-cognitive.md`.

**Предусловие 2 — последний коммит соответствует post-TASK_05c-fix.1 state:**

```
git log --oneline -5
```

Ожидается (top коммит на 2026-04-24):
```
8716398 observations: TZ Task 3 shock_score gap (defer to TASK_07)
618f5d3 task 05c-fix.1: archive to completed
bd34960 task 05c-fix.1: canonical _collect_shock_score + cleanup inline duplicate
3fe26ae observations: move post-MDC roadmap to observations/ subdir
0f8c7ce observations: post-MDC roadmap (TASK_06 PROJECT_PASSPORT + TASK_07 TZ analysis plans)
```

**Предусловие 3 — LESSONS_LEARNED.md на диске = v1.5 (24 урока):**

```
grep -c "^## L-" LESSONS_LEARNED.md
```

Ожидается: `24` (L-01..L-25 минус reserved L-12 = 24 реальных урока).

Если любое из 3 предусловий не выполнено — **§ 3 STOP**.

---

## 4. Части задачи

### Часть 1 — Diagnostic: прочитать v1.5 и найти точки вставки

**Цель:** подтвердить actual state LESSONS_LEARNED.md и найти где именно вставлять новые уроки + обновлять index applicability + change log.

**Команды по одной (L-23):**

1. `grep -n "^## L-" LESSONS_LEARNED.md`

   Ожидается список 24 уроков от L-01 до L-25 (без L-12). Последний — L-25.

2. `grep -n "^## Индекс применимости\|^## История обновлений" LESSONS_LEARNED.md`

   Ожидается 2 строки — начало секции "Индекс применимости" и "История обновлений".

3. `awk 'NR>=1060 && NR<=1075' LESSONS_LEARNED.md`

   Покажет ending файла — хвост "История обновлений" table. Подтверждает что v1.5 entry присутствует, формат table строки.

Пришли raw output всех 3 команд в одном сообщении **без summary, без emoji, без интерпретации** (CV-12).

**Критерий Часть 1:** архитектор подтверждает актуальное состояние и даёт PA-09 Signal на Часть 2.

**После Часть 1 — жди моего explicit signal перед Часть 2.**

---

### Часть 2 — Вставка L-26 перед "Индекс применимости"

**Место вставки:** после `L-25: raw.githubusercontent.com имеет cache TTL...` (заканчивается на ~строке 1034 с `---` separator), перед `## Индекс применимости`.

**Использовать `str_replace` tool** c OLD = заключительная часть L-25 + separator + `## Индекс применимости` heading. NEW = то же самое + L-26 + L-27 + L-28 между separator и heading.

**Стратегия:** делаем **одной str_replace операцией** все 3 урока сразу (чтобы не рисковать split matching). OLD должен включать явный маркер окончания L-25 и начала Индекс.

**Точный OLD для str_replace:**

```
**Применимость:** все post-commit workflow, особенно когда commit трогает existing configs/schemas/documentation. Не требуется для коммитов добавляющих только новые файлы.

---

## Индекс применимости
```

**Точный NEW для str_replace:**

```
**Применимость:** все post-commit workflow, особенно когда commit трогает existing configs/schemas/documentation. Не требуется для коммитов добавляющих только новые файлы.

---

## L-26: Summary-vs-raw output в transitions между Частями TASK

**Когда возникло:** TASK_05b-fix.1 (2026-04-22), TASK_05c (2026-04-22), TASK_05c-fix.1 (2026-04-23)
**Категория:** workflow

**Симптом (что мы увидели):**
Persistent pattern через multiple TASKs: при transition между Частями TASK (особенно после diagnostic phase → action phase) Claude Code склонен возвращать **summary с эмодзи-маркерами** ("✅ Подтверждены все 4 проблемы", "✓ пусто, ✓ новые checks присутствуют", "Perfect! Часть 2 completed successfully") вместо raw output команд которые просил архитектор.

Прецеденты:
- TASK_05b-fix.1 Часть 1: Claude Code прислал summary "Подтверждены все 4 проблемы ✅ строки 376-379, 313, 580-595" без raw awk output
- TASK_05a-fix.5 Часть 5: "Добавлены ровно 2 новых урока ✅ Счётчик обновлён ✅" без raw `git diff --cached LESSONS_LEARNED.md`
- TASK_05c multiple transitions: "✓ tests passed" без полного stdout test run
- TASK_05c-fix.1 Часть 2: начало response с "Perfect! Часть 2 completed successfully" + "grep shows 9 methods" без явного grep raw output

**Причина (почему так произошло):**
Interpretation-mode tension: Claude Code естественно обрабатывает tool output для формулирования ответа ("что важно из этого?"). Когда tool output длинный/технический — tendency свернуть его в summary. Это нормальное cognitive behavior, но оно conflict'ует с архитекторской потребностью в raw data для независимой верификации (L-24 spirit).

Дополнительно: эмодзи-маркеры ("✅", "✓", "Perfect!") — это verbalization того что Claude Code решил результат "хороший", но архитектор не может верифицировать эту оценку без raw output.

**Правильный подход:**
В TASK инструкциях архитектор формулирует **явное требование "raw output без summary"** для каждой команды где нужна верификация:

```
Пришли raw output команд X, Y, Z в одном сообщении без summary, без emoji, без интерпретации.
```

При transition между Частями — дополнительное **напоминание**:
> "Перед переходом к Части N+1 — пришли raw output команд текущей Части. Summary не принимается."

Claude Code: при получении request на "raw output" — возвращать **ровно stdout команды**, без preamble "I'll check...", без postamble "everything looks good", без эмодзи markers типа "✅"/"✓". Только literal команда + literal stdout.

Acceptable формы (не нарушают L-26):
- Bash tool output отображается tool framework'ом сам по себе — это уже raw
- Краткое nuutral завершение "Commands executed, awaiting review" допустимо **если** все raw outputs уже в сообщении

Неacceptable формы:
- "✅ All 3 commands passed" → скрывает stdout
- "Perfect! Everything works." → субъективная оценка
- "Here's summary: 9 methods found" → interpretation вместо raw

**Правило на будущее:**
В любой TASK с multiple Частями и checkpoints между ними — архитектор **явно** пишет "без summary, без emoji, без интерпретации" при каждом requested raw output. Claude Code: если не уверен — возвращай больше raw данных, не меньше.

**Применимость:** все multi-Part TASKs с verification checkpoints между Частями. Особенно diagnostic Частей и post-commit verification.

---

## L-27: Autonomous test fixes — semantic vs infrastructure failures

**Когда возникло:** TASK_05c Часть 2 (2026-04-22), TASK_05c-fix.1 Часть 4 (2026-04-23)
**Категория:** workflow

**Симптом (что мы увидели):**
**Прецедент 1 (semantic — violation):** TASK_05c Часть 2 — Claude Code при implementation research context обнаружил падающий existing тест `test_build_context_non_forecast_raises_notimplemented`. Тест проверял что `raise NotImplementedError` для research/monitoring/postmortem task_types. После реализации research — тест корректно fail для research случая. Claude Code **автономно обновил assertion** в тесте, исключив research из проверки, без эскалации архитектору.

Технически решение было корректным (research теперь реализован, assertion должен измениться). Но процесс неправильный: тест fail мог бы signal bug в реализации research, а не required assertion update. Autonomous fix маскирует bug в гипотетическом худшем сценарии.

**Прецедент 2 (infrastructure — acceptable):** TASK_05c-fix.1 Часть 4 — после добавления 3 новых тестов test runner показал 33/33 passed (ожидалось 36/36). Claude Code диагностировал через grep что все 36 функций в файле, но test runner имеет explicit function list и 3 новых не зарегистрированы. Добавил 3 строки в runner list автономно.

Это formally L-27 violation, но fix был:
- Pure infrastructure (registration gap, не semantic)
- Minimally invasive (3 строки)
- Явно transparent через reasoning trace ("The test runner has explicit test lists...")

Architector accepted результат но pointed out violation.

**Причина (почему так произошло):**
Engineering instinct "make failing things pass" — естественная reaction developer на red tests. Плюс L-27 в его первой формулировке (pre-refinement) был absolutist: "всегда эскалировать". Это не различало случаи когда semantic fix может маскировать bug от infrastructure fix который является obvious registration.

**Правильный подход:**

**Category 1 — Semantic failures (assertion mismatch, behavior wrong, value mismatch):**
- Test expects `result.status == "DEGRADED"` — gets `"OK"`
- Test expects list of 3 items — gets 5
- Test expects method to raise ValueError — no exception raised
- Test asserts specific string in output — string absent

**Action:** **ВСЕГДА § 3 STOP с эскалацией.** Формат:

```
§ 3 STOP: Failing test <test_name>
Expected: <expected>
Actual: <actual>
Possible causes:
  A) <hypothesis 1>
  B) <hypothesis 2>
  C) <hypothesis 3>
Recommendation: <которую рекомендую>
Жду решение архитектора. Не patching autonomously.
```

**Category 2 — Infrastructure failures (discovery, registration, import, file missing in test fixtures scope):**
- Test function exists in file but not in explicit runner list
- Import error для newly created module
- Test fixture file missing after manual cleanup
- Test data directory empty when test expects entries

**Action:** **Fix acceptable** с обязательной **explicit transparency** в том же сообщении:

```
Infrastructure issue detected: <описание>
Applying fix: <что делаю>
Rationale: это infrastructure gap (registration/discovery/import), не semantic (behavior assertion).
[выполнение fix + re-run]
```

Ключевой marker infrastructure: **тест не запустился** (not discovered, import failed) vs **тест запустился но failed assertion** (semantic).

**Grey zone — escalate anyway:**
Если не уверен к какой category относится — **эскалируй как semantic**. Цена ложной positive (emkalate лишний раз) < цена false negative (autonomous fix замаскировал bug).

**Правило на будущее:**
- **Semantic test failure** — § 3 STOP, эскалация обязательна. Не patching test для "починки".
- **Infrastructure test failure** — fix допустим с явной transparency в сообщении ("это infrastructure issue, не semantic, применяю fix: X"). Transparency обязательна — без неё autonomous fix всё равно violation.
- При неуверенности — эскалация.

**Применимость:** все TASK с существующими или новыми тестами, все случаи когда test suite после изменений показывает failures.

---

## L-28: Autonomous progression to next Part без explicit PA-09 Signal

**Когда возникло:** TASK_05b (2026-04-22), TASK_05c Часть 3 (2026-04-22)
**Категория:** workflow

**Симптом (что мы увидели):**
**Прецедент 1:** TASK_05b — после Pre-task Analysis Claude Code прислал 5 пунктов анализа, включая неверную интерпретацию P-02. Архитектор в коррекции написал "не задерживать старт" — не сказав явно "жди подтверждения перед Частью 1". Claude Code интерпретировал "не задерживать старт" как proceed signal, **выполнил все 7 Частей TASK_05b автономно**, закоммитил. Post-commit review выявил 4 отклонения от спецификации. Потребовал TASK_05b-fix.1 на ~45 минут remediation.

**Прецедент 2:** TASK_05c Часть 3 — Claude Code завершил Часть 2 (research context), прислал раздумчивое сообщение с findings. Архитектор в ответном сообщении прислал feedback + instructions для Части 3 но **не выделил** явный Signal "приступай к Части 3". Claude Code интерпретировал продолжение мысли архитектора как implicit approval, начал monitoring implementation без explicit "приступай".

**Причина (почему так произошло):**
Asymmetric interpretation problem. Claude Code при получении response архитектора **ищет** signal "продолжай". При ambiguous signal — default behavior "продолжить работать" (что rational в большинстве cases). Но в TASK workflow с explicit checkpoints — ambiguity должна разрешаться в сторону "жди явный signal", не "продолжай".

Архитектор со своей стороны (CV-15 в cognitive) может оставлять ambiguous signals thinking они clear. Complementary pair: CV-15 у архитектора + L-28 у Claude Code = same workflow break.

**Правильный подход:**

**PA-09 explicit signals архитектора (из CLAUDE_OPUS_COGNITIVE v1.6 Секция 4):**

- **Signal 1 (Wait):** "Жди моего подтверждения перед Частью X" / "Подтверди понимание, я дам добро"
- **Signal 2 (Proceed):** "Приступай к Части X после того как подтвердишь понимание" / "Продолжай с Части X"
- **Signal 3 (Retrospective):** "Это для будущих шагов. Текущий шаг завершай как есть."

**Ambiguous phrases запрещены архитектором но могут встречаться:**
- "не задерживать старт"
- "продолжай по TASK как написано" (без указания Части)
- "приступай" (без указания к чему)
- "это для справки" (unclear блокирует или нет)

**Claude Code action при ambiguous signal:**

**НЕ** интерпретировать "продолжай" / "приступай" / "go on" без указания **конкретной Части** как green light. Вместо этого:

1. Отправить **§ 3 clarification request** (не full STOP, легче форма):

```
Clarification needed: не вижу explicit Signal 1/2/3 для следующего шага.
Текущее состояние: <где я сейчас>
Ожидаемое следующее действие по TASK: <что planned>
Жду одного из:
- "Жди подтверждения" (Signal 1) 
- "Приступай к Части N" (Signal 2, с явной Частью)
- "Коррекция retrospective, текущий шаг завершай" (Signal 3)
```

2. **Не двигаться дальше** до получения явной формулировки.

Фразы "приступай", "продолжай", "go on", "хорошо", "ok", "после X" без указания **следующей Части explicitly** — **не являются достаточными**.

**Edge case — один explicit checkpoint выполнен:**

Если в TASK явно написано "выполни Часть 1 и жди подтверждения" — после подтверждения architect'ом "Часть 1 accepted, приступай к Части 2" — это valid Signal 2 (Часть 2 explicit upon в сообщении).

Но если architect написал "Часть 1 accepted, продолжай" — **НЕ** валидно, clarification request.

**Правило на будущее:**
Claude Code: жди **explicit PA-09 Signal** с указанием конкретной Части before progression. Фразы без указания next Part — trigger для § 3 clarification request. Не интерпретировать implicit signals.

**Архитектор:** каждое сообщение после completion одной Части — должно содержать один из 3 Signals в explicit формулировке (complementary к L-28 обязанность).

**Применимость:** все multi-Part TASKs с explicit checkpoints, Pre-task Analysis workflow, любые mid-TASK corrections.

---

## Индекс применимости
```

**После str_replace — verification:**

```
grep -c "^## L-" LESSONS_LEARNED.md
```

Ожидается: `27` (24 previous + 3 new = 27).

```
grep -n "^## L-26\|^## L-27\|^## L-28" LESSONS_LEARNED.md
```

Ожидается 3 строки с номерами примерно в диапазоне 1030-1300.

Пришли raw output обеих команд в одном сообщении.

**После Часть 2 — жди signal перед Часть 3.**

---

### Часть 3 — Обновить Индекс применимости

**Цель:** добавить 3 новых урока в существующие categories таблицы.

**Использовать `str_replace` tool.** Добавляем 3 новых урока в relevant rows:

**Точный OLD:**

```
| Любая task | L-01, L-02, L-04, L-09, L-18, L-21, L-22 |
```

**Точный NEW:**

```
| Любая task | L-01, L-02, L-04, L-09, L-18, L-21, L-22, L-26, L-28 |
```

---

**Точный OLD (второй edit):**

```
| Выполнение команд в Claude Code env | L-18, L-20, L-21, L-23 |
```

**Точный NEW:**

```
| Выполнение команд в Claude Code env | L-18, L-20, L-21, L-23, L-26 |
```

---

**Точный OLD (третий edit):**

```
| Составление § 9 отчётов с commit | L-22, L-24 |
```

**Точный NEW:**

```
| Составление § 9 отчётов с commit | L-22, L-24, L-26 |
| Тесты и test suite maintenance | L-19, L-27 |
| Multi-Part TASKs с checkpoints | L-26, L-28 |
```

**Если каждый `str_replace` не ловит unique match** — **§ 3 STOP** + show actual row через awk, жди уточнённый OLD.

**Verification:**

```
awk '/^## Индекс применимости/,/^## История обновлений/' LESSONS_LEARNED.md
```

Должен показать full table с 3 updated rows + 2 new rows. Пришли raw output.

**После Часть 3 — жди signal перед Часть 4.**

---

### Часть 4 — Обновить change log + счётчик в header

**Цель:** добавить entry про v1.6 + обновить счётчик в header.

**Edit 1 — header счётчик:**

**OLD:**
```
> Текущее количество уроков: **24** (L-01..L-25, L-12 reserved).
```

**NEW:**
```
> Текущее количество уроков: **27** (L-01..L-28, L-12 reserved).
```

---

**Edit 2 — change log entry:**

**OLD:**
```
| 2026-04-21 | v1.5 | +L-24 (git diff --cached как обязательный checkpoint), +L-25 (raw.github cache TTL) по итогам TASK_05a review и incident с ложной тревогой "catastrophic failure" |
```

**NEW:**
```
| 2026-04-21 | v1.5 | +L-24 (git diff --cached как обязательный checkpoint), +L-25 (raw.github cache TTL) по итогам TASK_05a review и incident с ложной тревогой "catastrophic failure" |
| 2026-04-24 | v1.6 | +L-26 (summary-vs-raw в transitions), +L-27 (autonomous test fixes — semantic vs infrastructure), +L-28 (autonomous progression без explicit PA-09 Signal) по итогам TASK_05b/TASK_05b-fix.1/TASK_05c/TASK_05c-fix.1 workflow incidents за 2026-04-22/23 |
```

**Verification:**

```
awk '/^## История обновлений/,0' LESSONS_LEARNED.md
```

Должен показать full change log table с v1.6 entry. Пришли raw output.

```
head -10 LESSONS_LEARNED.md
```

Должен показать header с обновлённым счётчиком "27". Пришли raw output.

**После Часть 4 — жди signal перед Часть 5.**

---

### Часть 5 — Staging + git diff --cached verification (L-24)

**Команды по одной:**

1. `git add LESSONS_LEARNED.md`
2. `git add TASKS/ACTIVE/TASK_06-cognitive.md`
3. `git status` — raw output
4. `git diff --cached --stat` — raw output
5. `git diff --cached LESSONS_LEARNED.md` — **полный** raw diff (будет ~200+ строк diff)

**Важно:** после шага 5 — **остановись и жди моего подтверждения**.

Я анализирую full diff LESSONS_LEARNED.md. Ожидается:
- +L-26 (~80 строк)
- +L-27 (~90 строк)
- +L-28 (~80 строк)
- +2 новых rows в index + 3 updated rows
- +1 entry в change log
- +счётчик updated в header
- net ≈ +260 строк в LESSONS_LEARNED.md

**После Часть 5 — жди explicit signal перед Часть 6 (commit).**

---

### Часть 6 — Commit + push

1. `git commit -m "lessons: +L-26 +L-27 +L-28 (workflow lessons from TASK_05b/05c/05c-fix.1)"`
2. `git log --oneline -3` — raw output
3. `git show --stat HEAD` — raw output
4. `git push origin main` — **полный** raw output

**L-20:** если security warning от среды — § 3 STOP.

**AP-09:** никаких force push.

---

### Часть 7 — Post-commit verification via git show HEAD (PA-08 Канал 1)

1. `git show HEAD:LESSONS_LEARNED.md | grep -c "^## L-"`

   Ожидается: `27`.

2. `git show HEAD:LESSONS_LEARNED.md | grep -n "^## L-26\|^## L-27\|^## L-28"`

   Ожидается 3 строки.

3. `git show HEAD:LESSONS_LEARNED.md | head -10`

   Ожидается header с "27" счётчиком.

Пришли raw output всех 3 команд.

---

### Часть 8 — Архивация + финальный отчёт

1. `git mv TASKS/ACTIVE/TASK_06-cognitive.md TASKS/COMPLETED/TASK_06-cognitive.md`
2. `git commit -m "task 06-cognitive: archive to completed"`
3. `git push origin main`
4. `git log --oneline -4` — raw output
5. `git status` — должно быть clean

6. Финальный отчёт по формату § 9 + Reflection Block.

---

## 5. Формат финального отчёта

```
TASK_06-cognitive [LESSONS_LEARNED v1.5 → v1.6] — COMPLETED

Файлы изменены:
  - LESSONS_LEARNED.md (+L-26, +L-27, +L-28, +2 index rows, +change log entry, updated counter)

Файлы перемещены:
  - TASKS/ACTIVE/TASK_06-cognitive.md → TASKS/COMPLETED/TASK_06-cognitive.md

Тесты: N/A (документарный TASK)
Commits:
  - <hash> lessons: +L-26 +L-27 +L-28 (workflow lessons from TASK_05b/05c/05c-fix.1)
  - <hash> task 06-cognitive: archive to completed
Время работы: <минуты>
Ideas logged: 0 (observations: 0, concerns: 0)
Lessons applied: L-22 (сверять номера), L-23 (команды по одной), L-24 (git diff --cached)
Patterns applied: N/A
Antipatterns avoided: N/A
Warnings/issues: <список или "none">

Post-commit верификация: HEAD содержит 27 уроков включая L-26, L-27, L-28.

=== REFLECTION BLOCK ===

## Observations from this task
<0-3 пункта; пустой список допустим для документарного TASK>

## Self-critique
<0-2 пункта>

## Questions for architect (non-blocking)
<0-2 вопроса>

=== END REFLECTION BLOCK ===

Готов к следующей задаче (возможно TASK_06 PROJECT_PASSPORT или архитектор пришлёт другую).
```

---

## 6. Важные предупреждения

### 6.1 Документарный TASK — нет code changes

Ни в `ENGINE/`, ни в `scripts/`, ни в `tests/` — ничего не меняется. Только `LESSONS_LEARNED.md`. Pre-commit hook пройдёт trivially (нет code для antipattern checks).

### 6.2 Большой diff — внимательно с str_replace

Вставка 3 уроков одной str_replace операцией — самый безопасный способ (избегаем split match failures). Но OLD должен быть **exactly** как указан в Части 2, включая trailing whitespace и line endings.

**Если str_replace не поймает match** — § 3 STOP, show actual content через awk вокруг L-25 ending, жди уточнённый OLD.

### 6.3 Index updates — 3 отдельных edits + добавление 2 новых rows

Третий edit добавляет сразу 2 новых rows таблицы (Тесты и Multi-Part). Это intentional — они logically related к новым урокам.

### 6.4 L-27 formulation — nuanced

L-27 сложнее остальных — имеет 2 categories (semantic vs infrastructure). Внимательно при вставке — 90+ строк текста с code examples. Прочитай полностью перед str_replace чтобы понять structure.

### 6.5 L-20 security warnings

При любом warning от среды — § 3 STOP. Не одобрять молча.

### 6.6 PA-09 compliance

В этом TASK 8 checkpoints где Claude Code ждёт моего signal. Application of L-28 самого — не продвигайся без explicit Signal 2 с указанием конкретной Части.

---

## 7. Ожидаемые метрики

- **Размер TASK:** ~570 строк
- **Время выполнения:** 30-40 минут Claude Code + 15-20 минут архитектор
- **Diff size:** +260 строк в LESSONS_LEARNED.md, +570 строк new TASK file
- **Commits:** 2 (main + archive)

---

## 8. После TASK_06-cognitive — что дальше

По согласованному priority list (BRIEFING_2026-04-23):

**Priority 2 cont'd — моё cognitive v1.7** (архитектор пишет в claude.ai, заливает в project knowledge — **не TASK для Claude Code**).

**Priority 3 — TASK_06 PROJECT_PASSPORT** (2-3 часа работы, большой deliverable, consolidated operational view).

**Priority 4 — TASK_07 Comprehensive TZ Analysis** (4-6 часов, batch review ТЗ).

**Priority 5+ — feature roadmap из ТЗ.**

---

**Конец TASK_06-cognitive.**
