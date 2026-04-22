# TASK_05b — Context Orchestrator Forecast Logic + Fast Lane Invariant

**Версия:** v1
**Дата:** 2026-04-22
**Автор:** Claude Opus (архитектор)
**Исполнитель:** Claude Code
**Зависит от:** TASK_05a (COMPLETED 2026-04-21 — skeleton + configs готовы), TASK_05a-fix.5 (COMPLETED 2026-04-21 — L-24, L-25 в LESSONS_LEARNED)
**Блокирует:** TASK_05c (research/monitoring/postmortem + финализация MDC)

**Pre-task analysis required: YES**

---

## 1. Контекст и scope

### Где мы находимся

После TASK_05a у нас есть:
- `MARKET_MIND/ENGINE/context_orchestrator.py` — skeleton: docstring, constants, 3 dataclasses, 3 helper функции (`_load_timeframe_core`, `_count_tokens`, `is_fast_lane`), class `ContextOrchestrator` с публичными API `build_context` и `save_session` через `raise NotImplementedError`
- `MARKET_MIND/CONFIG/timeframe_core.json` с секцией `context_orchestrator_timeouts` (fast_lane_total_ms=5000, slow_lane_total_ms=30000, per_source_ms для 6 источников)
- `MARKET_MIND/CONFIG/session_state.json` с полями `summary`, `new_items`, `bias`
- `tiktoken>=0.5.0` установлен
- `MARKET_MIND/tests/test_context_orchestrator.py` — 8 тестов skeleton (8/8 passed)
- LESSONS_LEARNED v1.5 с L-24 (git diff --cached checkpoint) и L-25 (raw.github cache TTL)

### Что делаем в TASK_05b

Реализуем **forecast logic только** — для task_type `"forecast"`. Это включает:

1. Метод `_build_forecast_context(symbol, timeframe) → ContextResult` — основная логика
2. Пять `_collect_*` методов для источников данных (все с graceful degradation — P-02, L-07)
3. `_invoke_axm_guard()` — минимальная inline реализация согласно ТЗ § 1.20
4. Conflict Exposure — детекция конфликтов между KB и patterns, пометка `conflict_flag`
5. Fast Lane Invariant compliance — никогда `ABORTED` в forecast на 1h/4h (L-08)
6. ThreadPoolExecutor для параллельного сбора источников в Slow Lane (1d)
7. ~15 новых тестов в `test_context_orchestrator.py` включая explicit Fast Lane Invariant tests

### Что НЕ делаем в TASK_05b (это TASK_05c)

- `_build_research_context`, `_build_monitoring_context`, `_build_postmortem_context` — остаются `raise NotImplementedError`
- `save_session()` — остаётся `raise NotImplementedError`
- Budget enforcement с truncation (>8000 токенов) — в TASK_05c финализация
- Обновление `component_status.json → ready` — только после TASK_05c
- Сложная логика KB retrieval — в forecast режиме KB **не входит** в обязательные/желательные входы Fast Lane (ТЗ § 1.20: Claude не вызывается в Fast Lane). KB нужен только для Conflict Exposure — отдельный минимальный путь, не полный KB ingest

### Канон из ТЗ (обязательно учесть)

**ТЗ Задача 3 + Math Model v6.3 раздел 6 (Input Assembly Contract):**

Обязательные входы Fast Lane (1h/4h):
- Feature Snapshot
- Validated Patterns  
- Negative Filters

Желательные входы Fast Lane:
- Regime Context
- Timeframe Context  
- Prior Snapshot

При отсутствии желательных → penalty + пометка `partial_inputs=True`, **агрегация продолжается**.

Обязательные входы Slow Lane (24h/1d):
- Все шесть входов плюс Prior Snapshot и change_id

Context Orchestrator вызывает AXM Guard и Prior Manager **параллельно**, timeout независимый.

**ТЗ § 1.20 AXM операциональный scope:**

AXM **не contributing factor** в scoring/aggregation ни при каких условиях. AXM применяется **только** как post-scoring epistemic check. Нарушение AXM → `epistemic_risk_flag`, `confidence_point` не меняется, score не меняется.

В TASK_05b `_invoke_axm_guard()` возвращает minimal epistemic check result — **не** модифицирует confidence/direction.

**ТЗ Задача 3 Failover Rule:**

При timeout Context Orchestrator в Fast Lane (default 5000 мс из `timeframe_core.json`):
- Прогноз строится **без** prior_weight_factor (prior_snapshot_id=null)
- Пометка `context_degraded=True`
- AXM Guard продолжает на детерминированных правилах
- **Прогноз НЕ блокируется**

**ТЗ Задача 3 Conflict Exposure:**

Если KB conflicting + паттерн UP → `conflict_flag`. При shock_score > 0.25 → `brake_info` включается в контекст.

---

## 2. Предусловия

**Предусловие 1 — git status чистый.** Working tree должен быть clean (последний коммит TASK_05a-fix.5: `b3a04d7`). `git status` показывает только этот TASK файл в `TASKS/ACTIVE/`.

**Предусловие 2 — TASK_05a skeleton на месте.**
- `ls MARKET_MIND/ENGINE/context_orchestrator.py` — существует
- `python MARKET_MIND/tests/test_context_orchestrator.py` — `[PASS] 8/8 tests passed`
- `cat MARKET_MIND/CONFIG/timeframe_core.json` — содержит `context_orchestrator_timeouts`
- `python -c "from MARKET_MIND.ENGINE.context_orchestrator import is_fast_lane; print(is_fast_lane('forecast','1h'))"` — **разрешённый smoke test, часть критериев готовности TASK_05a** — возвращает `True`

**Предусловие 3 — LESSONS v1.5 в main.**
- `grep "^## L-24" LESSONS_LEARNED.md` — найдено
- `grep "^## L-25" LESSONS_LEARNED.md` — найдено

Если любое предусловие не выполнено — **§ 3 STOP**.

---

## 3. Подготовка — когнитивная система

Перед Pre-task Analysis и Частью 1 прочитай:

1. **LESSONS_LEARNED.md** — особенное внимание:
   - **L-01** (Context Orchestrator ≠ Input Assembler — главное предупреждение)
   - **L-07** (graceful degradation, no stubs)
   - **L-08** (Fast Lane Invariant — КРИТИЧНО для этого TASK)
   - **L-24** (git diff --cached checkpoint перед commit)
   - **L-18/L-19/L-21** (AP-10 все формы ad-hoc диагностики)

2. **ANTIPATTERNS.md** — AP-02 (stub data), AP-04 (ABORTED в Fast Lane — прямо запрещено), AP-07 (no scope creep), AP-10 (все три формы)

3. **PATTERNS.md** — P-01 (Path.resolve — уже в skeleton), P-02 (graceful degradation), P-03 (exception handling + logging), P-05 (ASCII markers + UTF-8)

---

## 4. Pre-task Analysis (обязательно)

**До** Части 1 — пришли Сергею Pre-task Analysis Block согласно CLAUDE.md § 25.3.5:

```
=== PRE-TASK ANALYSIS ===

1. Ясность TASK:
   - <что кажется ясным>
   - <что может быть неоднозначным и как ты интерпретируешь>

2. Риски стратегии:
   - <потенциальные проблемы которые видишь>
   - особенно: как планируешь гарантировать Fast Lane Invariant (L-08)
   - как обрабатываешь отсутствующие (ещё не реализованные) источники данных

3. Соответствие канону:
   - <расхождения с ТЗ или явное "не вижу">
   - специфично: как реализация AXM Guard будет совместима с ТЗ § 1.20 (не contributing factor)

4. Альтернативы:
   - ThreadPoolExecutor vs asyncio для параллельных таймаутов Slow Lane
   - Inline Patterns/Regime/Feature calls vs optional imports с fallback
   - Conflict Exposure detection — simple heuristic vs phased approach

5. Вопросы архитектору (неблокирующие):
   - <2-3 вопроса>

=== END PRE-TASK ANALYSIS ===

Продолжаю по TASK как написано.
```

Это **второй раз в v5 режиме с Pre-task Analysis**. После TASK_05a мы знаем что формат работает. Сегодня интересует **глубина** анализа — готов ли ты видеть архитектурные риски заранее, а не только procedural.

---

## 5. Части задачи

### Часть 1 — Подготовка imports и расширение skeleton

**Цель:** добавить новые imports и optional imports для внешних модулей (которые ещё не существуют — через try/except).

**Файл:** `MARKET_MIND/ENGINE/context_orchestrator.py`

**Шаги:**

1. Сначала покажи текущее содержимое skeleton: `cat MARKET_MIND/ENGINE/context_orchestrator.py` — полный вывод

2. Добавить imports **поверх** существующих (в тот же блок imports, не разрывая его):
   - `from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError`
   - `import threading` (для lock при концорентном доступе к shared state, если понадобится)

3. Добавить **optional imports** для источников данных через try/except (после существующего try/except для tiktoken). Каждый в своём блоке — для чёткости graceful degradation:

Для каждого источника: паттерн try-except-ImportError-установить-None-боольский-flag. Источники:
- `pattern_registry` (будущий Task 8)
- `regime_detector` (будущий Task 14)
- `feature_store` (будущий Task 13)
- `shock_score_module` (будущий Task 15)
- `brake_controller` (будущий Task 16)
- `prior_manager` (будущий Task 6)
- `negative_filters` (будущий Task 5.x)
- `kb_search` (для Conflict Exposure minimal path)

Для каждого создать переменную-флаг доступности: `PATTERN_REGISTRY_AVAILABLE = True` при успешном import, `False` при ImportError. Сам объект при ImportError — `None`.

**Примечание по форме:** не пиши готовые try/except блоки здесь за Claude Code — это задача для исполнителя. Спецификация: для каждого из 8 источников создай optional import pattern. Если какой-то модуль существует в проекте (маловероятно на этом этапе) — import сработает, флаг `True`. Если нет — `False`, fallback в `_collect_*` методах вернёт `None`.

**Не импортируй** конкретные функции/классы из этих модулей — только сам модуль. Конкретные символы берутся через `getattr()` с проверкой или просто при доступности модуля — в `_collect_*` методах. Это снижает brittleness если сигнатуры будущих модулей изменятся.

4. Обновить docstring модуля (§ 29.1): в секцию "Интеграция с" можно оставить как было. В секцию "Статус" изменить: `Статус: forecast logic implemented (TASK_05b). research/monitoring/postmortem — TASK_05c.`

5. Обновить `sys, time, typing` imports — раньше были импортированы но не использовались. Теперь `time.time()` будет использоваться для measure elapsed в timeouts, `Any` / `Optional` можно удалить если нового использования нет (проверь самостоятельно).

**Критерии готовности Часть 1:**
- `cat` показывает полный файл (раз в конце Части)
- Все 8 optional imports через try/except
- 8 availability флагов определены
- `python MARKET_MIND/tests/test_context_orchestrator.py` — **все 8 тестов skeleton всё ещё проходят** (не должны сломаться)
- Нет синтаксических ошибок: `python -c "from MARKET_MIND.ENGINE import context_orchestrator; print('[OK] module loads')"` — разрешённая smoke команда

---

### Часть 2 — Реализация `_collect_*` методов

**Цель:** пять методов для сбора данных из источников, все с graceful degradation (P-02, L-07).

**Все методы — приватные методы класса `ContextOrchestrator`, возвращают либо данные, либо `None`.** При `None` вызывающий код помечает block как missing.

**Спецификация 5 методов:**

**`_collect_patterns(self, symbol: str, timeframe: str) -> list[dict] | None`**

Назначение: получить validated patterns для символа и таймфрейма.

Поведение:
- Если `PATTERN_REGISTRY_AVAILABLE` — попытаться вызвать что-то в духе `pattern_registry.load_patterns(symbol, timeframe)` (точная сигнатура будущего Task 8 неизвестна — используй hasattr + getattr pattern для защиты)
- Если модуль недоступен или вернул пусто — fallback: читать `MARKET_MIND/LAYER_A_RESEARCH/patterns/*.json` через Path(self.market_mind_root) (P-01 уже есть в `__init__`)
- Filter patterns по `symbol` и `timeframe` полям из pattern_schema
- Возвращать list of dicts (сами pattern objects) — максимум 10 последних по `last_updated`
- При любой ошибке I/O — `logger.warning()` + `None`, не raise

**`_collect_regime(self, symbol: str, timeframe: str) -> dict | None`**

Назначение: получить current regime (R1-R6 по Math Model раздел 3).

Поведение:
- Если `REGIME_DETECTOR_AVAILABLE` — вызвать модуль
- Если нет — `None`
- Возвращаемая структура: `{"regime": "R1", "confidence": 0.85, "detected_at": "<ISO timestamp>"}` — минимальная из ТЗ

**`_collect_features(self, symbol: str, timeframe: str) -> dict | None`**

Назначение: получить feature snapshot (rsi, macd, volume indicators и т.п.).

Поведение:
- Если `FEATURE_STORE_AVAILABLE` — вызвать модуль  
- Если нет — `None`
- Возвращаемая структура: dict с feature_name → value

**`_collect_shock_score(self, symbol: str, timeframe: str) -> dict | None`**

Назначение: получить current shock_score + brake_level.

Поведение:
- Если `SHOCK_SCORE_MODULE_AVAILABLE` — вызвать
- Если нет — `None`
- Возвращаемая структура: `{"shock_score": 0.15, "brake_level": "none", "updated_at": "..."}`

Важно: `brake_level` один из: `"none"`, `"soft"`, `"hard"` — из Math Model v6.3 раздел 3 (modes R3/R4).

**`_collect_prior(self, symbol: str, timeframe: str) -> dict | None`**

Назначение: получить prior snapshot (для Fast Lane — желательный вход, для Slow Lane — обязательный).

Поведение:
- Если `PRIOR_MANAGER_AVAILABLE` — вызвать
- Если нет — `None`
- Возвращаемая структура: `{"prior_snapshot_id": "<uuid>", "prior_weight_factor": 0.65, "change_id": "<uuid|null>"}`

Примечание: когда prior отсутствует в Fast Lane — `prior_weight_factor` в итоговом контексте должен быть `null`, `prior_snapshot_id = null`, `context_degraded = True` (Failover Rule ТЗ).

**Общий паттерн поведения** для всех 5 методов:

1. Try фаза: доступ к модулю или файлам
2. При success: return данных
3. При любой failure (import missing, file not found, malformed data, attribute missing в модуле): `logger.warning(f"...")` + `return None`
4. Никаких raise — все exceptions ловятся локально

**НЕ создавать** для skeleton вариант (P-02 — graceful degradation это разумная стратегия, но у нас сейчас **ничего** из этих источников не существует — значит все 5 вернут `None`). Это нормально. В тестах симулируем availability через monkey-patching атрибутов модуля (см. Часть 5).

**Критерии готовности Часть 2:**
- 5 методов реализованы в классе `ContextOrchestrator`
- Каждый возвращает либо данные, либо `None` (никогда не raises)
- Docstrings для каждого публичного-выглядящего метода (короткие, 2-3 строки)
- `cat` показывает добавленный код
- Существующие тесты всё ещё проходят

---

### Часть 3 — Реализация `_invoke_axm_guard()`

**Цель:** minimal inline реализация AXM Guard согласно ТЗ § 1.20.

**Ключевое ограничение (ТЗ § 1.20):** AXM — **только post-scoring epistemic check**, не contributing factor. Не модифицирует `direction`, `confidence_point`, `score`. Возвращает `epistemic_risk_flag` (True/False) + optional reason.

**Спецификация:**

**`_invoke_axm_guard(self, patterns: list[dict] | None, features: dict | None, regime: dict | None) -> dict`**

Поведение:
- Inline minimal checks (без внешней зависимости от будущего `axiom_guard.py`)
- Проверки: простые логические sanity checks которые не требуют order flow или microstructure data (эти AXM аксиомы 001/002/004/008 — в V10+ roadmap согласно ТЗ)
- Примеры minimal checks (implement 2-3):
  - Если `regime == "R4"` (HARD brake) и `patterns` содержат UP-signals → `epistemic_risk_flag: True, reason: "patterns in hard-brake regime"`
  - Если `features.volatility > 3x median` (если доступно) + `patterns` direction противоположен — risk flag
  - Если `patterns` пусто и `regime == "R1"` (нормальный) — нет risk
- Возвращаемая структура:
  ```
  {
      "epistemic_risk_flag": bool,
      "reason": str | None,  
      "axm_guard_completed": bool  # False если произошла inner ошибка
  }
  ```
- Всегда возвращает валидный dict (не None, не raises)

**Что НЕ делать:**
- Не модифицировать confidence/direction/score — AXM строго guardrail
- Не пытаться валидировать Axiom_001/002/004/008 (требуют order flow — V10+)
- Не блокировать forecast при risk flag — это epistemic info для downstream, не блокер

**Критерии готовности Часть 3:**
- Метод реализован, возвращает dict с 3 ключами
- Никаких side effects (не правит state orchestrator)
- `cat` показывает реализацию

---

### Часть 4 — Реализация `_build_forecast_context()` — главный метод

**Цель:** собрать контекст для forecast task_type. Fast Lane (1h/4h) — без параллелизма, всё синхронно в timeout budget. Slow Lane (1d) — через ThreadPoolExecutor с per-source timeouts.

**Спецификация:**

**`_build_forecast_context(self, symbol: str, timeframe: str) -> ContextResult`**

Шаги внутри метода (spec-level, не готовый код):

1. **Определить lane:** `is_fast = is_fast_lane("forecast", timeframe, self.config)` — используем уже существующий helper
2. **Извлечь timeouts** из `self.config["context_orchestrator_timeouts"]`:
   - `fast_lane_total_ms` или `slow_lane_total_ms`
   - `per_source_ms` dict для Slow Lane
3. **Начать elapsed timer:** `start = time.time()`
4. **Собрать обязательные входы Fast Lane** (синхронно, в любом случае):
   - `patterns = self._collect_patterns(symbol, timeframe)`
   - `features = self._collect_features(symbol, timeframe)`
   - `negative_filters = ...` (если доступен NEGATIVE_FILTERS_AVAILABLE — вызвать, иначе None)
5. **Проверить обязательные входы:**
   - Если `patterns is None or features is None` (Fast Lane) → **продолжить с graceful degradation**, не abort (L-08)
   - `context_degraded = True`, missing source помечен в `blocks_dropped`
6. **Собрать желательные/дополнительные входы:**
   - Fast Lane: `regime`, `shock_info`, `prior` — последовательно с remaining budget check
   - Slow Lane: через ThreadPoolExecutor с max_workers=5, submit все 5 `_collect_*` + `_invoke_axm_guard`, wait с timeout, собрать results
7. **Shock/brake check:** если `shock_info["shock_score"] > BRAKE_THRESHOLDS["shock_score_include"]` (0.25) — добавить brake_info block
8. **AXM Guard:** `axm_result = self._invoke_axm_guard(patterns, features, regime)` — всегда вызывается, возвращает dict
9. **Conflict Exposure:**
   - Если `patterns` содержит direction UP + (условное: `kb_search` нашёл conflicting narrative) → `conflict_flag = True`
   - Minimal implementation — если нет доступа к KB (KB_SEARCH_AVAILABLE == False) → conflict_flag = False по умолчанию
   - В TASK_05c полная реализация KB query
10. **Сборка context string:**
   - Header с metadata (symbol, timeframe, task_type, timestamp)
   - Блоки в порядке приоритета (from BlockSpec): patterns → regime → features → shock_info (if >0.25) → axm_result → prior (if present) → conflict_flag (if True)
   - Каждый блок — JSON serialized section с заголовком
11. **Подсчитать tokens через `_count_tokens()`**
12. **Если tokens > MAX_TOKENS (8000):** в TASK_05b — просто пометить overflow в `blocks_dropped = ["...:budget_exceeded"]`, НЕ truncate (truncation — TASK_05c). В test assertion проверим что в normal case < 8000 влезает.
13. **Вернуть ContextResult:**
    - `context`: финальная string
    - `total_tokens`: int
    - `blocks_included`: list[str] с именами вошедших блоков  
    - `blocks_dropped`: list[str] с именами + причиной через `:` разделитель
    - `context_degraded`: True если любой обязательный вход был None, или был timeout, или budget exceeded
    - `status`: `"OK"` если context_degraded False, `"DEGRADED"` если True — **никогда `"ABORTED"`** (L-08!)

**Важные требования реализации:**

**Fast Lane Invariant (L-08 критично):**
- **Никогда** не возвращать status `"ABORTED"` в этом методе для `is_fast_lane == True`
- При полном отсутствии данных (все 5 collect вернули None) — возвращать context с только header + query, `status="DEGRADED"`, `context_degraded=True`, `blocks_dropped=[все источники]`
- При timeout одного источника — остальные продолжают, timeout source помечен в dropped
- `raise` внутри метода запрещён — все exceptions ловятся и помечают блок как dropped с reason

**ThreadPoolExecutor для Slow Lane:**
- Использовать context manager `with ThreadPoolExecutor(max_workers=5) as executor:`
- Submit каждый `_collect_*` и `_invoke_axm_guard` как отдельный future
- Собирать results через `future.result(timeout=per_source_timeout)`
- FuturesTimeoutError для конкретного source → `None` результат + source в dropped
- Global timeout через `slow_lane_total_ms` — на уровне общего elapsed check после сбора

**Порядок блоков в context:**
По приоритету (low priority number = high priority):
1. `patterns` (priority 1, required)
2. `features` (priority 2, required)
3. `regime` (priority 3)
4. `shock_info` (priority 4, только если shock > 0.25)
5. `axm_result` (priority 5)
6. `prior` (priority 6, если доступен)
7. `conflict_flag` (priority 7, только если True)

**Docstring метода:** полный с Args/Returns/Raises (raises: none в forecast), ссылка на L-08, ТЗ Задача 3 Failover Rule.

**Не пиши** готовый код метода целиком в TASK — это спецификация. Метод получится ~80-120 строк. Разделяй на приватные helper methods если становится длинным.

**Критерии готовности Часть 4:**
- `_build_forecast_context` реализован
- Использует ThreadPoolExecutor для Slow Lane (ищу `ThreadPoolExecutor` в cat выводе)
- Использует `_collect_*` методы из Части 2 и `_invoke_axm_guard` из Части 3
- **Никаких** `return ContextResult(status="ABORTED"...)` в коде — это архитектурная ошибка (grep в Части 6 verification должен вернуть пусто)
- **Никаких** `raise` внутри метода (только validation в начале если нужно)
- `build_context` method (публичный) вызывает `_build_forecast_context` при `task_type == "forecast"`, для других task_types сохраняется `raise NotImplementedError`

**В методе `build_context` (класс):**
```
if task_type == "forecast":
    return self._build_forecast_context(symbol, timeframe)
else:
    raise NotImplementedError(f"{task_type} context building in TASK_05c")
```

---

### Часть 5 — Расширить тесты

**Цель:** добавить ~15 новых тестов в `test_context_orchestrator.py` для forecast logic.

**Спецификация новых тестов (имена + краткое assertion):**

**Базовые forecast тесты (5):**

1. `test_forecast_1h_returns_result()` — forecast 1h возвращает ContextResult, status не ABORTED
2. `test_forecast_4h_returns_result()` — forecast 4h возвращает ContextResult
3. `test_forecast_1d_returns_result()` — forecast 1d (Slow Lane) возвращает ContextResult
4. `test_forecast_context_has_header()` — поле `context` непустое, содержит symbol и timeframe
5. `test_forecast_returns_context_result_instance()` — isinstance check

**Fast Lane Invariant тесты (критично! 4):**

6. `test_fast_lane_invariant_1h_no_aborted_status()` — forecast 1h, даже при всех источниках None, `status != "ABORTED"`. Должен быть `"OK"` или `"DEGRADED"`.
7. `test_fast_lane_invariant_4h_no_aborted_status()` — то же для 4h
8. `test_fast_lane_all_sources_missing_returns_degraded()` — при всех None → status = "DEGRADED", context_degraded = True
9. `test_fast_lane_partial_sources_still_succeeds()` — при 2-3 из 5 источников доступных → OK с partial_inputs пометкой в blocks_dropped

**Валидация входов (3):**

10. `test_forecast_invalid_symbol_empty_raises()` — пустой symbol → ValueError в публичном build_context
11. `test_forecast_invalid_timeframe_empty_raises()` — пустой timeframe → ValueError
12. `test_forecast_invalid_task_type_research_raises_notimplemented()` — research → NotImplementedError (пока)

**AXM Guard тесты (2):**

13. `test_axm_guard_returns_dict_with_required_keys()` — `_invoke_axm_guard(None, None, None)` возвращает dict с ключами `epistemic_risk_flag`, `reason`, `axm_guard_completed`
14. `test_axm_guard_never_raises()` — вызов с любыми входами (включая malformed) не бросает exception

**Budget / tokens (1):**

15. `test_forecast_context_tokens_counted()` — `total_tokens` > 0 после build_context

**Полная 15-тест suite, все через stdlib (L-24/L-22 напоминания для Claude Code):**
- Имена тестов должны соответствовать актуальной behavior (L-22 применяется)
- Function-based стиль как в skeleton
- Никаких mock libraries — используем monkey-patching через `setattr(context_orchestrator, 'PATTERN_REGISTRY_AVAILABLE', False)` где нужно

**Вспомогательный helper:**

Добавь в test файл функцию:
```
def _patch_availability(**kwargs):
    """Контекст-менеджер-подобный helper для патча availability flags."""
```

Реализация через `try/finally` с restore оригинальных значений. Но **не пиши** готовый код — специфицируй требования и позволь Claude Code реализовать.

**Runner нужно обновить:** существующий inline runner (с 8 тестами) расширить до 23 тестов (8 старых + 15 новых). Лучший подход — переписать runner в стиле функции `run_all_tests()` как в `test_data_quality_monitor.py` (референс style). Это также адресует self-critique из TASK_05a Reflection Block ("runner не вынесен в функцию").

**Критерии готовности Часть 5:**
- `python MARKET_MIND/tests/test_context_orchestrator.py` → `[PASS] 23/23 tests passed`
- Runner в стиле функции `run_all_tests()` (не inline в `if __name__`)
- Все 15 новых тестов имеют smysl assertions (не `assert True`)
- Fast Lane Invariant tests (6-9) — явно проверяют отсутствие "ABORTED" статуса

---

### Часть 6 — Pre-commit check + commit (применяем L-24!)

**Обязательно** применить L-24 которое мы сами добавили вчера.

**Шаги:**

1. `python scripts/pre_commit_check.py` — пришли полный stdout
2. `git status` — raw output
3. `git add MARKET_MIND/ENGINE/context_orchestrator.py`
4. `git add MARKET_MIND/tests/test_context_orchestrator.py`  
5. `git add TASKS/ACTIVE/TASK_05b_forecast_logic.md`
6. `git status` — raw output (все 3 файла в staged)
7. `git diff --cached --stat` — raw output
8. `git diff --cached MARKET_MIND/ENGINE/context_orchestrator.py` — **полный** diff (это самый critical файл TASK)
9. `git diff --cached MARKET_MIND/tests/test_context_orchestrator.py` — **полный** diff

**Остановись после шага 9 и жди моего подтверждения** (L-24 workflow). Я проверю diffs:
- В `context_orchestrator.py`: отсутствие "ABORTED" literal, присутствие "ThreadPoolExecutor", все 5 `_collect_*` + `_invoke_axm_guard` + `_build_forecast_context`
- В tests: 15 новых тестов, Fast Lane Invariant tests явно проверяют non-ABORTED статус

**После моего подтверждения — Часть 7 (commit + push).**

---

### Часть 7 — Commit + push + post-commit verification + архивация

Только после моего подтверждения Части 6.

1. `git commit -m "task 05b: context_orchestrator forecast logic + Fast Lane Invariant"` — raw output
2. `git show --stat HEAD` — raw output (PA-08 Channel 1 verification, применение L-25)
3. `git push origin main` — **полный** raw output
4. `git mv TASKS/ACTIVE/TASK_05b_forecast_logic.md TASKS/COMPLETED/TASK_05b_forecast_logic.md`
5. `git commit -m "task 05b: archive to completed"`
6. `git push origin main`
7. `git status` — должно быть clean

**НЕ делать:**
- **НЕ обновлять** `component_status.json → ready` (всё ещё not_started — forecast работает, но research/monitoring/postmortem не имплементированы)
- **НЕ делать web_fetch на raw.github** в финальном отчёте для верификации (L-25: минимум 15 минут TTL, а мы только что закоммитили — бессмысленно)

---

## 6. Формат финального отчёта

Включает стандартные § 9 блоки + **git verification section** (L-24 + PA-08):

```
TASK_05b [Context Orchestrator Forecast Logic] — COMPLETED

Файлы изменены:
  - MARKET_MIND/ENGINE/context_orchestrator.py (+~XXX строк, forecast logic)
  - MARKET_MIND/tests/test_context_orchestrator.py (+~XXX строк, 15 новых тестов)

Файлы перемещены:
  - TASKS/ACTIVE/TASK_05b_*.md → TASKS/COMPLETED/TASK_05b_*.md

Тесты: 23/23 passed (8 skeleton + 15 forecast)
Commit (main): <hash> task 05b: context_orchestrator forecast logic + Fast Lane Invariant
Commit (archive): <hash> task 05b: archive to completed
Время работы: <минуты>

Git verification (L-24 + PA-08 Channel 1):
<первые 20 строк git show --stat HEAD>

Lessons applied: L-01 (Context Orchestrator != Input Assembler), L-03 (relative paths), L-07 (graceful degradation), L-08 (Fast Lane Invariant — CRITICAL для этого TASK), L-24 (git diff --cached checkpoint — применён в Части 6)
Patterns applied: P-01 (Path.resolve), P-02 (graceful degradation с None vs stub), P-03 (exception handling + logging)
Antipatterns avoided: AP-02 (no stubs — все пропущенные источники возвращают None, не fake data), AP-04 (no ABORTED в Fast Lane — критично), AP-07 (no scope creep — research/monitoring/postmortem не трогал), AP-10 (no ad-hoc diagnostic commands)

=== REFLECTION BLOCK (v5 — обязательный) ===

## Observations from this task
<2-5 пунктов>

## Self-critique
<1-3 пункта>

## Questions for architect (non-blocking)
<0-3 вопроса>

=== END REFLECTION BLOCK ===

Готов к TASK_05c (research/monitoring/postmortem + финализация MDC).
```

---

## 7. Важные предупреждения

### 7.1 Fast Lane Invariant — критически важно (L-08, AP-04)

**Самое важное** в этом TASK: никогда не возвращать статус `"ABORTED"` в `_build_forecast_context()` для 1h/4h.

Цитата ТЗ:
> Fast Lane (1h/4h) numeric forecast path must NEVER wait for Claude response. Context Orchestrator обязан: (1) отдавать Fast Lane прогноз детерминированно без вызова Claude API, (2) запускать Claude slow path асинхронно post-forecast, (3) никогда не блокировать 1h/4h прогноз ожиданием KB / explainability / prior review. Нарушение этого инварианта является архитектурной ошибкой.

Конкретная реализация:
- При всех источниках None → `status="DEGRADED"`, `context_degraded=True`, минимальный context (header + query)
- При timeout одного источника → другие продолжают, timeout помечается в `blocks_dropped`
- При exception в коде метода — **не raise**, ловить и пометить блок dropped

Test #6-9 именно это проверяют. **Они обязаны проходить.**

### 7.2 AXM — не contributing factor (ТЗ § 1.20)

`_invoke_axm_guard()` **не модифицирует** `direction`, `confidence_point`, `score`. Возвращает только `epistemic_risk_flag + reason`. Это guardrail, не контролер.

### 7.3 CV-13 у архитектора (не тебя) — но и тебе полезно

Я (архитектор) старался НЕ писать код за тебя в этом TASK. Спецификации описывают **что** и **как** должно вести себя, не готовые реализации. Если какая-то деталь выглядит неясной — § 3 STOP, уточни вместо того чтобы "импровизировать по аналогии".

### 7.4 AP-10 все формы — критично

Никаких ad-hoc `python -c "..."` (кроме 2 smoke test команд явно в TASK), никаких `debug_*.py`, никаких файлов вне tests/engine которые не указаны в TASK. Если хочется "проверить что logic работает" — запусти **существующий test suite** через `python MARKET_MIND/tests/test_context_orchestrator.py`.

### 7.5 L-24 применение — обязательно

В Части 6 и финальном отчёте — **обязательно** полный `git diff --cached` до commit, `git show --stat HEAD` после. Это первое полноценное применение L-24 на feature TASK. Посмотрим работает ли эта дисциплина в бою.

### 7.6 Post-commit verification — не через web_fetch

L-25 применение: в финальном отчёте **не** делаем web_fetch на raw.github. Используем `git show --stat HEAD` (Channel 1) как post-commit verification. raw.github TTL означает что первые 15-30 минут он будет stale anyway.

### 7.7 L-22 — сверяться с LESSONS перед отчётом

Перед § 9 отчётом — открой LESSONS_LEARNED.md, сверь каждый упомянутый L-NN с реальным уроком. Если не уверен — "L-??" placeholder лучше чем неверный номер.

### 7.8 L-23 commands по одной

Все git команды в Частях 6-7 одной строкой, не compound. Каждое approval одобряй отдельно (1, не "always allow").

---

## 8. Ожидаемые метрики TASK_05b

- **Размер изменений в `context_orchestrator.py`:** +150-250 строк (forecast logic + 5 collect + AXM + helpers)
- **Размер изменений в `test_context_orchestrator.py`:** +150-200 строк (15 тестов + helpers + обновлённый runner)
- **Время Claude Code:** 60-90 минут (Pre-task Analysis + 7 Частей)
- **Approvals ожидается:** ~15-20 (git commands, pip checks, etc.)
- **Commits:** 2 (main commit + archive)

---

**Конец TASK_05b. Удачи с Fast Lane Invariant!**
