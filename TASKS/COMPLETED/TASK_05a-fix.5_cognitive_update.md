# TASK_05a-fix.5 — Cognitive update для Claude Code

**Версия:** v1
**Дата:** 2026-04-21
**Автор:** Claude Opus (архитектор)
**Исполнитель:** Claude Code
**Тип:** cognitive update (не feature TASK)
**Зависит от:** TASK_05a (COMPLETED 2026-04-21)

**Pre-task analysis required: NO** (procedural task без архитектурных решений)

---

## 1. Контекст

### Что случилось 2026-04-21

После COMPLETED отчёта TASK_05a архитектор попытался post-commit верификацию через `web_fetch` на raw.githubusercontent.com. Через ~40 минут после push два config файла показали **старые версии** без новых секций (`context_orchestrator_timeouts` в `timeframe_core.json`, поля `summary/new_items/bias` в `session_state.json`).

Архитектор объявил "catastrophic failure Частей 1-2 TASK_05a", написал TASK_05a-fix (283 строки) для remediation. После запуска remediation в Claude Code выяснилось через независимый канал (Сергей открыл файлы в редакторе): **файлы на диске и в main commit полностью правильные с самого начала**. raw.github endpoint был закэширован — cache TTL оказался 30-40+ минут для этого репо.

TASK_05a-fix отменён. Никаких реальных проблем с TASK_05a не было. Cost: ~30 минут работы Сергея на ненужный remediation cycle.

### Почему это cognitive update

Этот incident вскрыл gap в **workflow post-commit верификации** — не было формального правила о том через какие каналы проверять commit, и что raw.github имеет non-zero TTL. L-13 в LESSONS_LEARNED предупреждал "Raw-ссылки **менее** кэшированы", но это было интерпретировано как "не кэшированы вовсе".

Главный урок — не про Claude Code (он работал корректно весь TASK_05a), а про **workflow взаимодействия архитектор ↔ Claude Code при верификации**. Нужно формализовать:

1. **L-24** — `git diff --cached` перед commit как hard checkpoint (добавляет дисциплину независимо от того был incident или нет — полезно в принципе)
2. **L-25** — raw.github / web_fetch имеет cache TTL, не является authoritative post-commit source в первые 15+ минут

Эти уроки применимы к **каждому** TASK где:
- Trогаются existing файлы (не только новые)
- Требуется подтверждение что commit содержит ожидаемые изменения

---

## 2. Scope задачи

Добавить **2 новых урока** в `LESSONS_LEARNED.md`:
- **L-24:** `git diff --cached` перед commit как обязательный checkpoint
- **L-25:** raw.github cache TTL — не полагаться как на single source post-commit верификации

**НЕ добавляем:**
- L-26 (summary vs raw) — хотя soft-версия актуальна, это overlap с L-18 (AP-10) и CV-12 для архитектора. Сейчас без формализации.
- AP-11 (ghost edit) — не подтверждено, Write tool работал корректно
- Изменения в CLAUDE.md / PATTERNS.md / ANTIPATTERNS.md — этот update только в LESSONS_LEARNED

---

## 3. Предусловия

**Предусловие 1 — working tree чист.** `git status` показывает только этот TASK файл как untracked в `TASKS/ACTIVE/`. Последний коммит `eb7de6a task 05a: archive to completed`.

**Предусловие 2 — LESSONS_LEARNED.md актуален.** Текущая версия v1.4, последний урок **L-23**, L-12 помечен `[RESERVED]`. Итого 22 урока (L-01..L-23 минус L-12).

**Предусловие 3 — знакомство со стилем LESSONS_LEARNED.** Каждый урок следует формату:
```
## L-NN: <Короткое название>

**Когда возникло:** TASK_XX (<дата>)
**Категория:** architecture | code-quality | testing | security | workflow | data

**Симптом (что мы увидели):**
<...>

**Причина (почему так произошло):**
<...>

**Правильный подход:**
<...>

**Правило на будущее:**
<одна чёткая фраза>

**Применимость:** <в каких задачах / модулях>
```

Перед редактированием файла **прочитай** последние 2-3 урока в LESSONS_LEARNED.md (L-22 и L-23), чтобы внутренне сверить стиль. Не копируй механически — адаптируй.

---

## 4. Части задачи

### Часть 1 — Добавить L-24 в LESSONS_LEARNED.md

**Цель:** добавить новый урок `L-24` после `L-23` в файле `LESSONS_LEARNED.md`.

**Содержание L-24:**

```
## L-24: `git diff --cached` перед commit — обязательный checkpoint

**Когда возникло:** TASK_05a review (2026-04-21)
**Категория:** workflow

**Симптом (что мы увидели):**
Финальный § 9 отчёт Claude Code по TASK_05a содержал summary "COMPLETED ✅" с правильными хешами коммитов, но БЕЗ raw output команд промежуточных проверок (pre_commit_check, git diff --cached, git push output). Это создало ситуацию где архитектор не мог независимо подтвердить что именно попало в commit, и вынужден был полагаться на external channels (raw.github) для верификации — что привело к ложной тревоге из-за cache TTL (L-25).

**Причина (почему так произошло):**
В CLAUDE.md § 24 (Pre-commit checklist) упоминается `pre_commit_check.py` и ручная проверка, но нет явного требования **показать** содержимое staging архитектору перед commit. Claude Code добросовестно выполнял checks, но результаты не оказывались в отчёте как verifiable raw data.

**Правильный подход:**
Перед каждым `git commit` в multi-file TASK — обязательно выполнить и **включить в отчёт** raw output следующих команд:

1. `git status` — показать список staged/unstaged/untracked
2. `git diff --cached --stat` — сводка изменений по файлам (какие файлы и на сколько строк)
3. `git diff --cached <path>` для КАЖДОГО critical config/code файла — полный diff, не fragment

Особенно для configs (JSON, YAML) и schemas (которые могут быть "изменены но кажутся нетронутыми" если правки были в отдельной части файла).

Эти выводы включаются в § 9 отчёт в секции "Commit verification" перед строкой `Commit: <hash>`.

**Правило на будущее:**
В multi-file TASK, особенно трогающих existing configs/schemas: перед `git commit` выполнить `git diff --cached --stat` + `git diff --cached <file>` для каждого critical файла. Эти raw outputs включить в финальный § 9 отчёт. Это позволяет архитектору **независимо подтвердить** содержимое staging до того как commit попадёт в main.

**Применимость:** все multi-file TASK, особенно с правками existing configs или schemas. Не требуется для TASK которые только создают новые файлы (их содержимое показывается через `cat` после создания — P-05 style).
```

**Как делать:**

1. `type "LESSONS_LEARNED.md"` (или `cat`) — проверь что последний урок действительно `L-23` и что финальная секция "Индекс применимости" + "История обновлений" присутствуют в конце файла

2. Добавь L-24 **между** L-23 и секцией "---" перед "## Индекс применимости". Новый урок должен стоять **после** L-23, **до** индексной таблицы.

3. В таблице "Индекс применимости" добавь соответствующую строку:
```
| Составление § 9 отчётов с commit | L-22, L-24 |
```
(Предыдущая строка была `| Составление § 9 отчётов | L-22 |` — обнови на новую версию).

**Критерий готовности Часть 1:**
- L-24 добавлен в правильном месте (после L-23, до "Индекс применимости")
- Индекс применимости обновлён
- Файл по-прежнему валидный markdown
- Кодировка UTF-8 (§ 13)

---

### Часть 2 — Добавить L-25 в LESSONS_LEARNED.md

**Содержание L-25:**

```
## L-25: raw.githubusercontent.com имеет cache TTL — не authoritative source в первые 15-30 минут после push

**Когда возникло:** TASK_05a post-commit verification (2026-04-21)
**Категория:** workflow

**Симптом (что мы увидели):**
Через ~40 минут после `git push origin main` с двумя коммитами TASK_05a, архитектор выполнил `web_fetch` на 5 raw.githubusercontent.com URL для независимой верификации содержимого main. Для двух config файлов (`timeframe_core.json`, `session_state.json`) raw.github показал **старое содержимое** без новых секций, которые реально были добавлены в коммит `e07e6a2`. Через несколько минут после остановки diagnostic cycle те же URL показали правильное содержимое — endpoint обновился.

Архитектор на основе stale output объявил "catastrophic failure TASK_05a — Части 1-2 не попали в main", написал TASK_05a-fix (283 строки) с remediation planом. Часть 0 TASK_05a-fix (diagnostic `cat` на локальном диске) показала что файлы там правильные. Далее — противоречие `cat ok` + `git diff --cached empty` подтвердило что файлы УЖЕ в HEAD commit. Сергей открыл файлы в редакторе напрямую — абсолютный ground truth, полностью правильное содержимое.

TASK_05a-fix отменён. Никаких реальных проблем с TASK_05a не было — `cat` и git show HEAD всё время показывали правильные файлы.

**Причина (почему так произошло):**
L-13 в LESSONS_LEARNED предупреждал:
> "Raw-ссылки **менее** кэшированы чем рендер страницы GitHub UI (L-13) — обновляются в течение минут после push."

Ключевое слово — **"менее"**, не **"не"**. Cache TTL для raw.githubusercontent.com endpoint может составлять 15-30+ минут для low-activity репо. "Менее кэшированы" было интерпретировано архитектором как "обновляются моментально", что неверно.

Дополнительно: формирование catastrophic failure conclusion на основе **одного external channel** — антипаттерн. Должен быть cross-check через independent channel до remediation action.

**Правильный подход:**
Post-commit верификация commit через multiple channels в правильном приоритете:

**Channel 1 (most authoritative — git local):**
`git show HEAD:<path>` — показывает содержимое файла в последнем коммите. Независимо от working tree, независимо от remote cache. Single source of truth для "что именно в последнем коммите".

**Channel 2 (absolute ground truth — Сергей):**
Сергей открывает файл локально в редакторе и присылает содержимое. Полный bypass всех cache/interface/interpretation problems. Используется когда Channel 1 даёт противоречивые данные.

**Channel 3 (supplementary — remote):**
`web_fetch` на raw.githubusercontent.com. **НЕ использовать** как primary или single source в первые 15+ минут после push. Используется для cross-verification после паузы (TTL expiration).

**При противоречии между Channel 1 и Channel 3:**
- Это **ожидаемое** поведение в первые 15-30 минут после push
- НЕ объявлять catastrophic failure
- Подождать + повторить через 15-30 минут, или cross-check через Channel 2

**Правило на будущее:**
При post-commit верификации существующих файлов (а не просто новых) — **всегда сначала `git show HEAD:<path>`**, затем при желании cross-check через raw.github только через 15+ минут после push. Никогда не объявлять commit failure только на основании raw.github / web_fetch single channel в первые 30 минут после push.

Для финального § 9 отчёта полезно включать `git show HEAD:<path>` для 1-2 critical файлов — это Canonical post-commit state который позже не зависит от cache.

**Применимость:** все post-commit workflow, особенно когда commit трогает existing configs/schemas/documentation. Не требуется для коммитов добавляющих только новые файлы.
```

**Как делать:**

1. Добавь L-25 сразу после L-24 (которое было в Части 1).

2. Обнови таблицу "Индекс применимости" — добавь строку:
```
| Post-commit verification | L-13, L-25 |
```

3. Обнови таблицу "История обновлений" в конце файла — добавь строку:
```
| 2026-04-21 | v1.5 | +L-24 (git diff --cached как обязательный checkpoint), +L-25 (raw.github cache TTL) по итогам TASK_05a review и incident с ложной тревогой "catastrophic failure" |
```

**Критерий готовности Часть 2:**
- L-25 добавлен сразу после L-24
- Индекс применимости обновлён (2 строки: одна из Часть 1, одна из Часть 2)
- История обновлений содержит строку v1.5
- Файл валидный markdown, UTF-8

---

### Часть 3 — Обновление счётчика уроков в header

В самом начале `LESSONS_LEARNED.md` есть строка:
```
> Текущее количество уроков: **22** (L-01..L-23, L-12 skipped).
```

После добавления L-24 и L-25 количество будет 24 (L-01..L-25 минус L-12 reserved).

**Что делать:**
Обнови эту строку на:
```
> Текущее количество уроков: **24** (L-01..L-25, L-12 reserved).
```

**Критерий готовности Часть 3:**
- Счётчик обновлён на 24
- Диапазон обновлён на L-01..L-25

---

### Часть 4 — Верификация + pre-commit check

1. `type LESSONS_LEARNED.md | find "L-24"` (Windows) или `grep "^## L-24" LESSONS_LEARNED.md` — должно найти строку заголовка L-24
2. `type LESSONS_LEARNED.md | find "L-25"` — должно найти L-25
3. `type LESSONS_LEARNED.md | find "24 (L-01..L-25"` — должно найти обновлённый счётчик
4. `python scripts/pre_commit_check.py` — должен вернуть `[PASS]`

**Критерий готовности Часть 4:**
- Все 4 verification commands дают ожидаемые результаты
- pre_commit_check PASS

---

### Часть 5 — Staging + git diff --cached + commit (применяем L-24!)

**Это first TASK применяющий L-24 (который сам только что добавлен).** Соответственно, verification чуть более строгая:

1. `git add LESSONS_LEARNED.md`
2. `git add TASKS/ACTIVE/TASK_05a-fix.5_cognitive_update.md` (сам TASK файл)
3. `git status` — пришли raw output
4. `git diff --cached --stat` — пришли raw output
5. `git diff --cached LESSONS_LEARNED.md` — пришли **полный** raw diff (это критический файл обновления)

**Остановись после шага 5 и жди моего подтверждения.**

Я проверю что:
- Diff добавляет ровно 2 новых урока (L-24, L-25)
- Диапазон updates в header корректный
- Таблицы индекса и истории обновлены
- Существующие уроки L-01..L-23 нетронуты

---

### Часть 6 — Commit + push + архивация

Только после моего подтверждения Части 5.

1. `git commit -m "lessons: +L-24 (git diff --cached checkpoint) +L-25 (raw.github cache TTL)"`
2. `git show --stat HEAD` — raw output (применяем PA-08 Channel 1 самопроверки)
3. `git push origin main` — полный output
4. `git mv TASKS/ACTIVE/TASK_05a-fix.5_*.md TASKS/COMPLETED/TASK_05a-fix.5_cognitive_update.md`
5. `git commit -m "task 05a-fix.5: archive to completed"`
6. `git push origin main`
7. `git status` — должно быть clean

Финальный § 9 отчёт (короткий):

```
TASK_05a-fix.5 [Cognitive Update L-24 L-25] — COMPLETED

Файлы изменены:
  - LESSONS_LEARNED.md (добавлены L-24, L-25; обновлены индекс применимости и история)

Файлы перемещены:
  - TASKS/ACTIVE/TASK_05a-fix.5_*.md → TASKS/COMPLETED/

Commit (main): <hash> lessons: +L-24 (git diff --cached checkpoint) +L-25 (raw.github cache TTL)
Commit (archive): <hash> task 05a-fix.5: archive to completed
Время работы: <минуты>

Git show HEAD verification (применение L-24 + PA-08 для этого самого update):
<первые несколько строк git show --stat HEAD>

=== REFLECTION BLOCK (короткий) ===

## Observations from this task
<2-3 пункта про процесс: применение L-24 в этом самом TASK, чувствовалось ли полезным; стиль уроков хорошо удалось скопировать или были трудности>

## Self-critique
<1-2 пункта>

=== END REFLECTION BLOCK ===

Готов к TASK_05b.
```

---

## 5. Важные предупреждения

### 5.1 Это cognitive update, не feature task

Scope узкий: **только** добавить 2 урока в LESSONS_LEARNED.md. Не добавлять:
- Новые антипаттерны
- Новые паттерны
- Правки CLAUDE.md
- Новые тесты

Если кажется что "а не стоит ли ещё <X>" — § 3 STOP, не расширяй scope.

### 5.2 Стилистическая консистентность с existing уроками

L-24 и L-25 должны читаться "как родные" в LESSONS_LEARNED.md. Заимствуй структуру, терминологию, тональность из L-22 и L-23 (последние уроки — наиболее свежие по стилю).

**Не**:
- Добавлять emoji в текст уроков (§ 13, L-04)
- Писать слишком короткие уроки без "Правило на будущее"
- Использовать "мы" — уроки пишутся безлично или "архитектор / Claude Code"

### 5.3 AP-10 все три формы по-прежнему применимы

Для этого TASK: никаких ad-hoc diagnostic commands / debug файлов. Единственные команды — те что явно в TASK. Если нужно "проверить как выглядит файл" — `cat` или `type` как в Части 4 verification.

### 5.4 L-23 commands по одной

Все git команды одной строкой, не compound.

### 5.5 Post-commit верификация этого самого update

В Части 6 применяем `git show --stat HEAD` (Channel 1 из PA-08). **Не** используем raw.github для верификации в отчёте — нам TTL всё ещё может помешать. Если архитектор захочет cross-check — сделает это через 20+ минут после push.

---

## 6. Формат финального отчёта

См. Часть 6 выше — короткий § 9 с git show HEAD verification block.

---

**Конец TASK_05a-fix.5.**

**Ожидаемое время:** 25-35 минут чистой работы Claude Code + approvals.

**Это первый TASK формально применяющий L-24 + PA-08 (от архитектора), так что — момент truth для процесса. Если будет неясно что-то в инструкциях — § 3 STOP, не импровизируй.**
