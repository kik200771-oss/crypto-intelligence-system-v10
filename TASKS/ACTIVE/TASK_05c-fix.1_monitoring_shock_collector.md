# TASK_05c-fix.1 — Canonical `_collect_shock_score` + cleanup AP-02 в `_build_monitoring_context`

**Версия:** v1 (revised после отмены previous draft 2026-04-22)
**Дата:** 2026-04-23
**Автор:** Claude Opus (архитектор)
**Исполнитель:** Claude Code
**Зависит от:** TASK_05c (COMPLETED 2026-04-22, commit `7c3d268` — MDC 4/4 READY)
**Блокирует:** чистый закрытый TASK_05 baseline перед TASK_06 PROJECT_PASSPORT

**Pre-task analysis required: YES**

---

## 1. Контекст и scope

### Что случилось

В TASK_05c Часть 3 при реализации `_build_monitoring_context` был создан **inline duplicate** shock collector:

```python
# строки 1068-1080 в MARKET_MIND/ENGINE/context_orchestrator.py
# Добавляем shock_score сбор (используем существующий метод если есть, иначе заглушка)
def collect_shock_score():
    # Пока нет _collect_shock_score метода - создаём minimal implementation
    shock_file = self.market_mind_root / "LAYER_H_INFRA" / "shock_score.json"
    ...
    
shock_future = executor.submit(collect_shock_score)
```

Это **нарушение AP-02** (scope expansion через создание нового collection path вместо канонического паттерна) + path inconsistency (inline duplicate читает `LAYER_H_INFRA/shock_score.json` — путь не определён в ТЗ, выбран ad-hoc).

### Почему previous draft TASK_05c-fix.1 был отменён

Previous draft (2026-04-22) исходил из ошибочного assumption архитектора что `_collect_shock_score` существует как результат TASK_05b, и spec fix был "убрать inline duplicate + reuse existing method". Claude Code правильно выполнил STOP на Часть 1 diagnostic (grep показал что метода нет), что привело к отмене draft.

Это CV-16 candidate в cognitive архитектора — false memory about project state.

### Что делаем в этом TASK (Variant B scope)

1. **Создаём канонический метод** `_collect_shock_score(symbol, timeframe) -> dict | None` по паттерну других 8 `_collect_*` методов
2. Метод возвращает `None` + warning log — **graceful degradation** согласно P-02 pattern, пока Task 11 (Brake Detector) не реализован
3. Заменяем inline duplicate в `_build_monitoring_context` на `self._collect_shock_score(symbol, timeframe)`
4. Вся существующая логика BRAKE_ALERT + monitoring body сохраняется — она корректно проверяет `None`
5. Добавляем **2 новых теста** для `_collect_shock_score` (missing source + valid input-like mock) и **1 тест** для `_build_monitoring_context` с `None` shock (graceful degradation path)

### Что НЕ делаем

- **НЕ определяем** где живёт `shock_score.json` — это scope Task 11 (ТЗ молчит про path сейчас). Метод просто `return None`
- **НЕ добавляем** `_collect_shock_score` к forecast context — это scope expansion за пределы ТЗ Задачи 3 (будет обсуждаться в TASK_07 Comprehensive TZ Analysis)
- **НЕ меняем** `component_status.json` (context_orchestrator уже `ready`, это internal cleanup)
- **НЕ трогаем** `_build_forecast_context`, `_build_research_context`, `_build_postmortem_context`, `save_session`, `_enforce_budget` — они в порядке

### Parallel observation (не в scope TASK — для контекста)

Одновременно с этим TASK архитектор создаст observation `2026-04-23_tz_task3_shock_score_gap.md` в `TASKS/NOTES/observations/` фиксирующий gap в ТЗ Задаче 3 (shock_score не перечислен как source для monitoring context). Это **отдельный artefact** — не часть этого TASK, не затрагивает code, будет обработано в TASK_07.

---

## 2. Ссылки на канон

- **ТЗ Задача 3** (Context Orchestrator) — monitoring task_type, Slow Lane
- **ТЗ Задача 11** (Shock Score / Brake Detector) — источник shock_score, **не реализован**
- **CLAUDE.md § 28** — cognitive system (применяем L-07 / P-02 graceful degradation, AP-02 avoided)
- **CLAUDE.md § 9** — Reflection Block обязателен
- **LESSONS_LEARNED L-24** — git diff --cached checkpoint перед commit
- **ANTIPATTERNS AP-02** — stub-данные в production коде (что исправляем)
- **PATTERNS P-02** — graceful degradation (None + warning log)

---

## 3. Предусловия

**Предусловие 1 — git status чистый:**
```
git status
```
Ожидается: `On branch main / Your branch is up to date with 'origin/main'. / nothing to commit, working tree clean` или только untracked `TASKS/ACTIVE/TASK_05c-fix.1_monitoring_shock_collector.md`.

Если есть неожиданные modified/untracked файлы — **§ 3 STOP**.

**Предусловие 2 — последние коммиты соответствуют post-TASK_05c state:**
```
git log --oneline -5
```
Ожидается (актуальный top на 2026-04-23):
```
3fe26ae observations: move post-MDC roadmap to observations/ subdir
0f8c7ce observations: post-MDC roadmap (TASK_06 PROJECT_PASSPORT + TASK_07 TZ analysis plans)
721fe25 task 05c: archive to completed
7c3d268 task 05c: Context Orchestrator COMPLETE (research/monitoring/postmortem + save_session) — MDC 4/4 READY
2d4d8a8 task 05b-fix.1: archive to completed
```

**Предусловие 3 — baseline тесты проходят:**
```
python MARKET_MIND/tests/test_context_orchestrator.py
```
Ожидается: `[PASS] 33/33 tests passed`.

Если любое из 3 предусловий не выполнено — **§ 3 STOP**.

---

## 4. Pre-task Analysis — ОБЯЗАТЕЛЕН

**Выполнить ДО Часть 1 (diagnostic).**

После чтения TASK целиком, до любых file modifications — пришли Pre-task Analysis отдельным сообщением по формату § 25 шаг 3.5:

```
=== PRE-TASK ANALYSIS ===

1. Ясность TASK:
   - <что кажется ясным>
   - <что может быть неоднозначным и как я интерпретирую>

2. Риски стратегии:
   - <потенциальные проблемы которые вижу>
   - <архитектурные решения которые могут оказаться неверными>

3. Соответствие канону:
   - <места где TASK может расходиться с ТЗ или cognitive system>
   - <или явное "расхождений не вижу">

4. Альтернативы:
   - <какие подходы рассмотрел бы если бы писал TASK сам>
   - <или "TASK-подход выглядит оптимальным">

5. Вопросы архитектору (неблокирующие):
   - <что было бы полезно прояснить но не мешает начать>

=== END PRE-TASK ANALYSIS ===
```

**После отправки Pre-task Analysis — жди моего explicit подтверждения (PA-09 Signal 1) перед Часть 1.** Я отвечу одним из:

- **Signal 2:** "Анализ корректный. Приступай к Часть 1 (diagnostic)."
- **Signal 1:** "Комментарий по X, ответь / уточни, затем я дам добро на Часть 1."
- **Abort:** "Stop, пересматриваем TASK" — если обнаружил критическое расхождение.

Pre-task Analysis — **mutual quality check**: ты ловишь мои blind spots (как с `_collect_shock_score` вчера), я ловлю твои интерпретации spec.

---

## 5. Части задачи

### Часть 1 — Diagnostic (grep + read existing patterns)

**Цель:** получить raw context для корректной реализации canonical `_collect_shock_score`.

**Команды (по одной, L-23):**

1. `grep -n "def _collect_" MARKET_MIND/ENGINE/context_orchestrator.py`

2. Показать **ровно** сигнатуру + docstring + body одного из existing collectors как reference. Выбери `_collect_drift_metrics` (самый близкий по simplicity — single file read):
   ```
   awk 'NR>=793 && NR<=827' MARKET_MIND/ENGINE/context_orchestrator.py
   ```

3. Показать **ровно** блок inline duplicate который убираем:
   ```
   awk 'NR>=1065 && NR<=1090' MARKET_MIND/ENGINE/context_orchestrator.py
   ```

**Требование:** пришли **полный raw output** всех 3 команд **в одном сообщении**. Без summary, без emoji, без интерпретации. Это material для меня чтобы дать precise specification в Часть 2.

**Критерий Часть 1:** я вижу:
- Список всех `_collect_*` методов (ожидается 8)
- Полный `_collect_drift_metrics` как стилистический reference
- Полный inline duplicate code chunk который убираем

**После Часть 1 — жди моего explicit signal перед Часть 2.**

---

### Часть 2 — Добавить `_collect_shock_score` метод

**Условие:** Часть 1 завершена, я дал explicit signal на Часть 2.

**Где вставлять:** после `_collect_kb_excerpts` (который сейчас на строке 828 и далее — последний в блоке Slow Lane collectors). Inserting **после** его закрывающей строки метода.

**Почему там:** структурное соседство с другими Slow Lane collectors (`_collect_audit_entries`, `_collect_drift_metrics`, `_collect_kb_excerpts`). `shock_score` принадлежит той же категории (читается только в Slow Lane, в `_build_monitoring_context`).

**Точная реализация метода:**

```python
def _collect_shock_score(self, symbol: str, timeframe: str) -> dict | None:
    """
    Читает shock_score из источника Brake Detector.
    
    ВАЖНО: Task 11 (Brake Detector) на момент TASK_05c-fix.1 НЕ РЕАЛИЗОВАН.
    Метод возвращает None (P-02 graceful degradation) — monitoring context
    получает missing shock info и корректно не добавляет [BRAKE_ALERT] блок.
    
    Когда Task 11 будет реализован, body метода заменится на чтение 
    канонического shock_score артефакта. Path, schema, lifecycle определяются
    Task 11 scope — не здесь.
    
    Args:
        symbol: торговый символ (BTCUSDT, etc.)
        timeframe: таймфрейм (1h, 4h, 1d)
    
    Returns:
        dict со shock_score данными или None если источник недоступен.
        Ожидаемая будущая структура (Task 11): {"shock_score": float, 
        "timestamp": str, "symbol": str, "timeframe": str}
    """
    self.logger.info(
        f"shock_score collector: Task 11 (Brake Detector) not yet implemented — "
        f"returning None for {symbol}/{timeframe}"
    )
    return None
```

**Правила именно такой реализации:**

- **Не создавать** shock_score.json при `None` через P-04 default (P-04 для критичных configs, не для optional data sources). Этот метод symmetric с `_collect_drift_metrics` / `_collect_kb_excerpts` — при отсутствии источника возвращаем `None` graceful
- **logger.info не warning** — Task 11 не implemented это known state, не error. Warning был бы misleading в логах
- **Docstring обязательно** с явной отметкой "Task 11 not implemented" и инструкцией для будущего implementer (когда Task 11 realised — меняй body, сигнатура stable)

**Критерий Часть 2:** новый метод вставлен после `_collect_kb_excerpts`. Пришли raw output:
```
grep -n "def _collect_" MARKET_MIND/ENGINE/context_orchestrator.py
```
Ожидается **9 методов** включая `_collect_shock_score`.

**После Часть 2 — жди моего signal перед Часть 3.**

---

### Часть 3 — Убрать inline duplicate в `_build_monitoring_context`

**Условие:** Часть 2 completed, я дал signal.

**Цель:** заменить inline `collect_shock_score()` на `self._collect_shock_score(symbol, timeframe)`.

**Конкретная правка:**

Найди в `_build_monitoring_context` блок (примерно строки 1068-1083 согласно diagnostic grep):

```python
# Добавляем shock_score сбор (используем существующий метод если есть, иначе заглушка)
def collect_shock_score():
    # Пока нет _collect_shock_score метода - создаём minimal implementation
    shock_file = self.market_mind_root / "LAYER_H_INFRA" / "shock_score.json"
    if shock_file.exists():
        try:
            data = json.loads(shock_file.read_text(encoding="utf-8"))
            if isinstance(data, dict) and "shock_score" in data:
                return data
        except (json.JSONDecodeError, OSError) as e:
            self.logger.error(f"Error reading shock_score: {e}")
    return None

shock_future = executor.submit(collect_shock_score)
future_to_source[shock_future] = "shock_score"
```

Замени на:

```python
# shock_score через канонический _collect_shock_score (Task 11 pending → None graceful)
shock_future = executor.submit(self._collect_shock_score, symbol, timeframe)
future_to_source[shock_future] = "shock_score"
```

**Точный способ правки — через `str_replace` tool.** OLD должен включать **полный блок от комментария "Добавляем shock_score сбор" до строки `future_to_source[shock_future] = "shock_score"` включительно**. NEW — двухстрочный replacement выше.

**Если `str_replace` не ловит unique match** (например отступы не совпадают) — **§ 3 STOP**, покажи текущий exact содержимое блока через `awk 'NR>=1065 && NR<=1090'` и жди уточнённого OLD string.

**Проверка после правки:**

```
grep -n "shock_score\|_build_monitoring_context" MARKET_MIND/ENGINE/context_orchestrator.py
```

Ожидается:
- Строка ~1069 комментарий "shock_score через канонический..."
- Строка ~1070 `executor.submit(self._collect_shock_score, symbol, timeframe)`
- **Нет** `def collect_shock_score():` (inline функция удалена)
- **Нет** `LAYER_H_INFRA" / "shock_score.json"` (путь ушёл вместе с inline)
- Остальные использования `shock_score` в BRAKE_ALERT блоке (~1115-1126), monitoring body (~1142-1149), priority_order (~1170) — **сохранены**

Пришли raw output grep.

**После Часть 3 — жди signal перед Часть 4.**

---

### Часть 4 — Тесты

**Условие:** Часть 3 completed, signal получен.

**Добавить 3 новых теста** в `MARKET_MIND/tests/test_context_orchestrator.py`.

**Где вставлять:** после существующих monitoring тестов (которые добавлены в TASK_05c Часть 3). Используй grep чтобы найти:
```
grep -n "def test_.*monitoring\|def test_" MARKET_MIND/tests/test_context_orchestrator.py | tail -10
```

Это покажет где заканчивается текущая secuenсия monitoring тестов.

**Спецификация 3 новых тестов:**

**Test 1: `test_collect_shock_score_returns_none_task11_pending`**
- Инстанцировать `ContextOrchestrator` с tmp base
- Вызвать `orch._collect_shock_score("BTCUSDT", "1h")`
- Assert: результат is `None`
- Assert: logger.info call сделан (опционально — если уже mockаем logger в других тестах, сохрани consistency; если нет — без проверки log call)
- Покрывает P-02 contract текущей реализации

**Test 2: `test_collect_shock_score_signature_matches_other_collectors`**
- Проверка что сигнатура `(symbol, timeframe) -> dict | None` — согласно паттерну
- Можно через `inspect.signature(orch._collect_shock_score)` + проверка двух параметров + return annotation
- Эта проверка — guardrail чтобы будущая реализация Task 11 не сломала контракт

**Test 3: `test_build_monitoring_context_graceful_without_shock`**
- Создать mock сценарий где `_collect_shock_score` возвращает `None` (текущее default поведение)
- Заполнить `_collect_regime_context` и `_collect_drift_metrics` valid mock data (чтобы monitoring context имел источники)
- Вызвать `orch.build_context("test query", "BTCUSDT", "1h", task_type="monitoring")`
- Assert: `status != "ERROR"` — монтирование прошло
- Assert: `[BRAKE_ALERT]` **не** появляется в `result.context` (т.к. shock is None)
- Assert: monitoring body содержит regime и drift (если они замоканы)
- Assert: `result.partial_inputs == True` ИЛИ `context_degraded == True` — один из флагов выставлен поскольку shock missing

**Стилистический reference:** смотри другие monitoring тесты добавленные в TASK_05c Часть 3.

**Запуск тестов:**

```
python MARKET_MIND/tests/test_context_orchestrator.py
```

Ожидается: `[PASS] 36/36 tests passed` (было 33, +3 новых).

**Если тесты не проходят — §3 STOP.** Пришли полный traceback ошибки, не пытайся "починить тест" autonomously (L-27).

**После Часть 4 — жди signal перед Часть 5.**

---

### Часть 5 — Staging + `git diff --cached` verification (L-24)

**Условие:** Часть 4 completed (36/36 тесты), signal получен.

**Команды:**

1. `git add MARKET_MIND/ENGINE/context_orchestrator.py`
2. `git add MARKET_MIND/tests/test_context_orchestrator.py`
3. `git add TASKS/ACTIVE/TASK_05c-fix.1_monitoring_shock_collector.md`
4. `git status` — пришли raw output
5. `git diff --cached --stat` — пришли raw output
6. `git diff --cached MARKET_MIND/ENGINE/context_orchestrator.py` — пришли **полный** raw diff
7. `git diff --cached MARKET_MIND/tests/test_context_orchestrator.py` — пришли **полный** raw diff

**Важно:** после шага 7 — **остановись и жди моего подтверждения**.

Я проанализирую `git diff --cached` по обоим файлам (L-24 — единственный способ увидеть что РЕАЛЬНО в staging). Если diff показывает:
- В context_orchestrator.py: +новый метод `_collect_shock_score` (~15 строк) + замена inline duplicate (-17 строк, +2 строки) ≈ net **около 0 строк**
- В test_context_orchestrator.py: +3 новых тестовых функции (~40-50 строк)
- Нет unexpected changes

→ Даю добро на Часть 6 (commit).

Если diff содержит неожиданное (changes в методах которые не должны меняться, removed existing тесты, etc.) — разбираемся вместе.

---

### Часть 6 — Commit + push

**Условие:** Часть 5 completed, я дал explicit signal.

1. `git commit -m "task 05c-fix.1: canonical _collect_shock_score + cleanup inline duplicate"`
2. `git log --oneline -3` — пришли raw output
3. `git show --stat HEAD` — пришли raw output
4. `git push origin main` — пришли **полный** raw output (включая "Writing objects...", "remote:", "To github.com...")

---

### Часть 7 — Post-commit верификация (PA-08 Канал 1)

**Цель:** подтвердить что fix реально в HEAD через authoritative channel.

1. `git show HEAD:MARKET_MIND/ENGINE/context_orchestrator.py` (первые 50 строк headerа + последний метод через `| head -50` и `| tail -50`) — достаточно для sanity check

   Конкретно:
   ```
   git show HEAD:MARKET_MIND/ENGINE/context_orchestrator.py | awk 'NR>=820 && NR<=870'
   ```
   (это должно показать `_collect_kb_excerpts` + новый `_collect_shock_score` следом)

2. `git show HEAD:MARKET_MIND/ENGINE/context_orchestrator.py | grep -n "def _collect_"`

   Ожидается 9 методов, включая `_collect_shock_score`.

3. `git show HEAD:MARKET_MIND/ENGINE/context_orchestrator.py | grep -n "collect_shock_score\|LAYER_H_INFRA"`

   Ожидается:
   - `def _collect_shock_score(...)` — один раз
   - `self._collect_shock_score(symbol, timeframe)` — один раз в `_build_monitoring_context`
   - **НЕТ** `def collect_shock_score():` (inline)
   - **НЕТ** `LAYER_H_INFRA" / "shock_score.json"` (ушёл вместе с inline)

Пришли raw output всех 3 команд.

**Почему PA-08 Канал 1 достаточен:** не используем raw.github (L-13 cache TTL 15-30+ мин сразу после push, плюс мы в работе — авторитетно `git show HEAD`).

---

### Часть 8 — Архивация + финальный отчёт

1. `git mv TASKS/ACTIVE/TASK_05c-fix.1_monitoring_shock_collector.md TASKS/COMPLETED/TASK_05c-fix.1_monitoring_shock_collector.md`
2. `git commit -m "task 05c-fix.1: archive to completed"`
3. `git push origin main`
4. `git status` — должно быть clean
5. Финальный отчёт по формату § 9.

---

## 6. Формат финального отчёта

```
TASK_05c-fix.1 [Canonical _collect_shock_score + cleanup AP-02] — COMPLETED

Файлы изменены:
  - MARKET_MIND/ENGINE/context_orchestrator.py (+_collect_shock_score метод, -inline duplicate)
  - MARKET_MIND/tests/test_context_orchestrator.py (+3 tests)

Файлы перемещены:
  - TASKS/ACTIVE/TASK_05c-fix.1_*.md → TASKS/COMPLETED/TASK_05c-fix.1_*.md

Тесты: 36/36 passed (было 33, +3 новых)
Commit (main): <hash> task 05c-fix.1: canonical _collect_shock_score + cleanup inline duplicate
Commit (archive): <hash> task 05c-fix.1: archive to completed
Время работы: <минуты>
Ideas logged: 0 (observations: 0, concerns: 0)
Lessons applied: L-07 (graceful degradation), L-24 (git diff --cached перед commit), L-23 (команды по одной)
Patterns applied: P-02 (graceful degradation, None + warning log)
Antipatterns avoided: AP-02 (stub данные в production — убран inline duplicate который был AP-02 violation)
Warnings/issues: <список или "none">

Post-commit верификация: new _collect_shock_score в HEAD (подтверждено через git show HEAD)

=== REFLECTION BLOCK ===

## Observations from this task
<0-3 пункта; пустой список допустим>

## Self-critique
<0-3 пункта; что мог бы сделать иначе>

## Questions for architect (non-blocking)
<0-3 вопроса/идеи; пустой список допустим>

=== END REFLECTION BLOCK ===

Готов к следующей задаче (TASK_06-cognitive).
```

---

## 7. Важные предупреждения

### 7.1 PA-09 Signal compliance

Этот TASK имеет **7 explicit checkpoints** где Claude Code ждёт signal архитектора:
1. После Pre-task Analysis (до Часть 1)
2. После Часть 1 diagnostic
3. После Часть 2 (метод добавлен)
4. После Часть 3 (inline duplicate removed)
5. После Часть 4 (тесты proходят)
6. После Часть 5 (staging + diff shown)
7. После Часть 7 (post-commit verified)

На каждом checkpoint — **жди моего explicit Signal 1/2/3** (PA-09 формулировки). Фразы "приступай", "продолжай", "go on" без указания конкретной Части — **не валидны**.

Если в моём response ambiguity — **§ 3 clarify**. Не интерпретировать в сторону proceed автономно (L-28).

### 7.2 Никаких ad-hoc tests (AP-10)

В Часть 4 мы добавляем тесты **в existing test file**, стилистически согласованные с existing pattern. **Никаких** `debug_*.py`, `check_*.py`, inline `python -c "..."` для проверки реализации. Если возникло желание "быстро проверить работает ли" — запусти весь test suite (`python MARKET_MIND/tests/test_context_orchestrator.py`). Если что-то не ясно — **§ 3 STOP**.

### 7.3 Raw output without summary (CV-12 mitigation)

На каждом checkpoint где прошу raw output — пришли **именно raw** без interpretation. Summary "✅ 36 tests passed, shock collector работает" **не принимается** в качестве raw output `python test_*.py` команды. Нужен full stdout.

### 7.4 L-23 команды по одной

Все git-команды одной строкой, не compound с `&&` / `||`. Каждое approval одобряй отдельно (1, не "always allow"). Один security warning — **§ 3 STOP**.

### 7.5 AP-09 никакого force push

Все коммиты past-main **не трогаем**. Только новые коммиты поверх. Никаких `--force`, `--force-with-lease`, `git reset --hard`.

### 7.6 L-27 — autonomous test fixes запрещены

Если какой-то **existing** тест начнёт падать после наших изменений — это **signal что наши изменения неверны**, не что тест устарел. **§ 3 STOP** с 3 вариантами + rationale + твоя рекомендация. Жди моё решение. Не правь тест autonomously.

### 7.7 Pre-task Analysis — не пропускать

Я отслеживаю строго. Если Часть 1 diagnostic пришла до Pre-task Analysis — это **§ 3 violation** и я попрошу откат к началу.

---

## 8. Ожидаемые метрики

- **Размер TASK:** ~350 строк (средний)
- **Время выполнения:** 45-60 минут Claude Code + ~20-30 минут архитектор (анализ checkpoints)
- **Diff size:** net ~0 строк в `context_orchestrator.py` (+~15 метод, -~17 inline, +2 replacement), +~45 строк тестов
- **Тесты:** 33 → 36 (все passed)
- **Новые commits:** 2 (main + archive)

---

## 9. После TASK_05c-fix.1 — что дальше

По согласованному priority list:

**Priority 2 — TASK_06-cognitive** (обновление LESSONS_LEARNED v1.5 → v1.6 с L-26/27/28 + моё cognitive v1.6 → v1.7 с CV-16).

После cognitive update — TASK_06 PROJECT_PASSPORT (priority 3).

---

**Конец TASK_05c-fix.1 revised.**
