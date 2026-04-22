# TASK_05c — Финализация Context Orchestrator (research/monitoring/postmortem + save_session) + MDC COMPLETE

**Версия:** v1
**Дата:** 2026-04-22
**Автор:** Claude Opus (архитектор)
**Исполнитель:** Claude Code
**Зависит от:** TASK_05b (COMPLETED), TASK_05b-fix.1 (COMPLETED 2026-04-22)
**Блокирует:** **финализация MDC** (последний компонент ready) → далее TASK_06 (PROJECT_PASSPORT) и TASK_07 (comprehensive TZ analysis)

**Pre-task analysis required: YES**

**Это критически важная задача** — после её COMPLETED `component_status.json.context_orchestrator.status → "ready"` и **MDC формально завершён**. Все 4 MDC компонента готовы к первому боевому forecast.

---

## 1. Контекст и scope

### Где мы находимся

После TASK_05a + TASK_05b + TASK_05b-fix.1:
- `context_orchestrator.py` содержит полностью работающий `_build_forecast_context()` 
- 5 `_collect_*` методов с graceful degradation (P-02)
- `_invoke_axm_guard()` с 3 правильными epistemic checks
- Публичный `build_context()` делегирует в `_build_forecast_context()` при `task_type="forecast"`, для других task_types — `raise NotImplementedError`
- `save_session()` — `raise NotImplementedError`
- Тесты: 22/22 (7 skeleton + 15 forecast)
- `component_status.json.context_orchestrator.status == "not_started"` — всё ещё, потому что research/monitoring/postmortem + save_session не реализованы

### Что делаем в TASK_05c

**Scope чёткий и обозримый:**

1. Реализация `_build_research_context(symbol, timeframe) → ContextResult` — Slow Lane (research не time-critical), scope по ТЗ: "KB + hypotheses"
2. Реализация `_build_monitoring_context(symbol, timeframe) → ContextResult` — Slow Lane, scope: "health + drift + shock_score"
3. Реализация `_build_postmortem_context(symbol, timeframe) → ContextResult` — Slow Lane, scope: "audit"
4. Реализация `save_session(summary, new_items, bias) → None` — обновление `session_state.json`
5. Budget enforcement — truncation если total_tokens > MAX_TOKENS (8000), **только в Slow Lane**. Fast Lane уже обрабатывает tokens но без truncation (L-08: faster context over full context)
6. Диспетчер в `build_context()` для всех 4 task_types
7. ~12-15 новых тестов для research/monitoring/postmortem + save_session + budget truncation
8. **Финальный шаг — обновление `component_status.json.context_orchestrator.status → "ready"`** в том же commit

### Что НЕ делаем в TASK_05c (scope discipline)

- **Не реализуем full AXM Guard** (текущие 3 epistemic checks достаточны — V10+ roadmap)
- **Не реализуем real KB retrieval** для Conflict Exposure в research context — оставляем `conflict_flag = False` минимальную реализацию (как в forecast). Full KB в Task 12 (KB Manager) отдельно
- **Не реализуем Prior Manager integration** beyond current `_collect_prior_snapshot` — тот же graceful degradation через None
- **Не реализуем user_profile_manager integration** (Task 17 будущий)
- **Не трогаем** `_build_forecast_context()` — он работает, покрыт 15 тестами

### Scope комфорта

Идея — сохранить **ту же архитектуру** что в `_build_forecast_context`:
- Использовать **те же** `_collect_*` методы (reuse, not duplicate)
- Те же helpers `_count_tokens`, `is_fast_lane`
- Та же graceful degradation философия (None from collect → block dropped)
- ThreadPoolExecutor тот же паттерн для Slow Lane parallel collection
- **Но** task-specific filtering какие из 5 collected источников идут в финальный context

---

## 2. Канон из ТЗ

**Task Awareness (ТЗ Задача 3 прямая цитата):**

> `forecast → паттерны + regime + shock_score, НЕ весь KB`
> `research → KB + hypotheses`
> `monitoring → health + drift + shock_score`
> `postmortem → audit`

**save_session (ТЗ Задача 3):**

> `save_session(summary, new_items, bias) → обновляет session_state`

**Budget (ТЗ Задача 3 критерий готовности):**

> `build_context() всегда < 8000 токенов`

**Fast Lane / Slow Lane таблица (ТЗ § 1.20):**

| Параметр | Fast Lane (1h/4h) | Slow Lane (24h/research) |
|----------|-------------------|----------------------------|
| Контекст | Только детерминированные компоненты | Полный контекст (KB + Priors + User Profile) |
| Max latency | 30 секунд | **Не критична** |
| Использование | Live forecast короткие горизонты | Research, post-mortem, 24h прогноз |

**Важно:** `research`, `postmortem` — всегда Slow Lane (independent of timeframe). `monitoring` — также Slow Lane (аналитическая задача, не time-critical). Только `forecast` на 1h/4h — Fast Lane.

Это меняет логику `is_fast_lane()` для TASK_05c: **Fast Lane = `forecast` AND `timeframe in fast_lane_list`**. Для research/monitoring/postmortem всегда Slow Lane, независимо от timeframe.

Текущий `is_fast_lane()` helper уже так работает (`return task_type == "forecast" and timeframe in fast_lane_list`) — ничего менять не надо.

---

## 3. Предусловия

**Предусловие 1 — git status чистый.** Последний коммит `2d4d8a8 task 05b-fix.1: archive to completed`. Working tree clean. Только этот TASK файл в `TASKS/ACTIVE/` как untracked.

**Предусловие 2 — Forecast работает и тесты зелёные.**
- `python MARKET_MIND/tests/test_context_orchestrator.py` → `[PASS] 22/22 tests passed`
- `grep -n 'status = "ABORTED"' MARKET_MIND/ENGINE/context_orchestrator.py` → пусто (кроме docstring/комментариев, grep должен возвращать 4-5 совпадений всё в комментариях)

**Предусловие 3 — session_state.json готов.**
- `cat MARKET_MIND/CONFIG/session_state.json` — должен содержать поля `summary`, `new_items`, `bias` (добавлены в TASK_05a Часть 2)

**Предусловие 4 — LESSONS_LEARNED v1.5 + L-08 clarification.**
- `grep "TASK_05b-fix.1" LESSONS_LEARNED.md` — найдено (из clarification)

Если любое предусловие не выполнено — **§ 3 STOP**.

---

## 4. Pre-task Analysis (обязательно)

**До** Части 1 — пришли Pre-task Analysis Block согласно CLAUDE.md § 25.3.5.

**Особенно важно для этого TASK — ответь на эти вопросы:**

1. **Ясность:** понимаешь ли ты что `research`, `monitoring`, `postmortem` — **всегда Slow Lane** (не зависят от timeframe)?

2. **Риски:** главный риск — **budget overflow** (>8000 токенов) в Slow Lane где все источники могут быть собраны. Как планируешь truncation?

3. **Соответствие канону:** task_type mapping:
   - research → KB + hypotheses
   - monitoring → health + drift + shock_score
   - postmortem → audit
   
   ТЗ описывает словами, не конкретными источниками. Например "health" в monitoring — это что? Regime? Shock score? Оба? Или есть отдельный health-collector в будущем?
   
   Ответь честно: какое **твоё proposed mapping** от словесных описаний ТЗ к конкретным `_collect_*` методам которые у нас уже есть?

4. **Альтернативы:** 
   - Общая функция `_build_slow_context(task_type, symbol, timeframe, source_selector)` с task-specific filter vs 3 отдельных метода?
   - Reuse существующих `_collect_*` methods vs создание новых `_collect_kb`, `_collect_hypotheses`, `_collect_audit_log`?
   
   (Мой preference: отдельные методы + reuse существующих _collect_*. Твоё мнение?)

5. **Вопросы архитектору (non-blocking):** 2-3 вопроса о scope граничных случаев.

**После Pre-task Analysis — жди моего подтверждения перед Частью 1. PA-09 applied: до моего explicit "приступай к Части X" — не выполнять.**

---

## 5. Части задачи

### Часть 1 — Расширение skeleton + диспетчер в `build_context`

**Цель:** подключить диспетчер в публичном `build_context` для всех 4 task_types.

**Файл:** `MARKET_MIND/ENGINE/context_orchestrator.py`

**Текущее состояние** (из TASK_05b-fix.1):
```python
if task_type == "forecast":
    return self._build_forecast_context(symbol, timeframe)
else:
    raise NotImplementedError(f"Context building for task_type '{task_type}' implemented in TASK_05c")
```

**Целевое состояние** — диспетчер по всем 4 task_types:
- `"forecast"` → `self._build_forecast_context(symbol, timeframe)` (без изменений)
- `"research"` → `self._build_research_context(symbol, timeframe)` (новое, в Части 2)
- `"monitoring"` → `self._build_monitoring_context(symbol, timeframe)` (новое, Часть 3)
- `"postmortem"` → `self._build_postmortem_context(symbol, timeframe)` (новое, Часть 4)

**На этом этапе** (Часть 1) — **только диспетчер**, сами `_build_*` методы ещё raise NotImplementedError (будут реализованы в Частях 2-4). Это промежуточное состояние для того чтобы тесты на предыдущие не ломались.

**Шаги:**

1. `cat MARKET_MIND/ENGINE/context_orchestrator.py | head -30` — покажи текущее состояние модульного docstring и imports
2. str_replace диспетчера в `build_context` на новую версию с 4 branches (точный old_str/new_str — после Pre-task Analysis, уточню в отдельном сообщении)
3. Добавить skeleton `_build_research_context`, `_build_monitoring_context`, `_build_postmortem_context` в класс — каждый raises NotImplementedError с точным reason ("will be implemented in TASK_05c Part 2/3/4")
4. `python MARKET_MIND/tests/test_context_orchestrator.py` — **все 22 теста** должны всё ещё проходить, потому что диспетчер для forecast не изменился

**Критерии готовности Часть 1:**
- Диспетчер содержит 4 branches
- 3 skeleton методов `_build_*_context` добавлены с NotImplementedError
- 22/22 тесты проходят
- `cat` показывает добавленные методы

---

### Часть 2 — Реализация `_build_research_context`

**Цель:** Slow Lane method для `research` task_type. По ТЗ: "KB + hypotheses".

**Архитектурный подход:**

1. Всегда Slow Lane — используй `slow_lane_total_ms = 30000` timeout из config
2. ThreadPoolExecutor для параллельного collect (как в forecast Slow Lane)
3. **Источники данных для research:**
   - `patterns` — через `_collect_validated_patterns()` — validated patterns по symbol/timeframe (входят в scope "hypotheses" — pattern это formalized hypothesis)
   - `KB` — **нет** существующего collector. Минимальная реализация: `_collect_kb_excerpts()` — новый метод (см. ниже). Graceful degradation если KB не доступен — `None`
4. **Не включать** `features`, `shock_score`, `prior`, `negative_filters` — они не в scope research
5. AXM Guard не вызывается для research (ТЗ § 1.20: AXM применяется для forecast scoring, не для research context)
6. Conflict Exposure применим (как для forecast) — minimal implementation `conflict_flag = False` без KB access
7. Budget enforcement (см. Часть 5): если `total_tokens > MAX_TOKENS` — truncate KB excerpts first (lowest priority), затем patterns

**Новый метод `_collect_kb_excerpts(self, symbol: str, timeframe: str) -> list[dict] | None`:**

По той же P-02 философии:
- Читает из `MARKET_MIND/LAYER_A_RESEARCH/kb/*.json` (или `*.md` — разберёшься по доступным файлам, если директория пустая — return None)
- Фильтрует по `symbol` и `timeframe` если есть в metadata
- При отсутствии директории или ошибке → `logger.warning()` + `None`
- Limit: top 10 most recent by `last_updated`

**Спецификация `_build_research_context(symbol, timeframe)`:**

Структура метода следует паттерну `_build_forecast_context` Slow Lane branch, но:
- Собираются только `patterns` + `kb_excerpts`
- ThreadPoolExecutor с max_workers=2
- Context header: `=== RESEARCH CONTEXT ({symbol}/{timeframe}) ===`
- Блоки в контексте: `[PATTERNS]`, `[KB_EXCERPTS]`, `[MISSING SOURCES]`
- Status: `"OK"` или `"DEGRADED"` (никогда `"ABORTED"` — L-08 clarification)

**Критерии готовности Часть 2:**
- Метод реализован, возвращает ContextResult
- `_collect_kb_excerpts()` реализован с graceful degradation
- Документирован через docstring с ТЗ reference
- Никаких raise внутри (только validation в публичном build_context выше)
- Никаких `"ABORTED"` literal

---

### Часть 3 — Реализация `_build_monitoring_context`

**Цель:** Slow Lane method для `monitoring` task_type. По ТЗ: "health + drift + shock_score".

**Mapping ТЗ → наши collectors:**
- "shock_score" → `_collect_shock_score()` — уже есть
- "health" → ~`_collect_regime_context()` — текущий regime как proxy для market health (R1=healthy, R4=hard-brake etc.)
- "drift" → **новый** `_collect_drift_metrics(symbol, timeframe)` — читает из `MARKET_MIND/LAYER_F_FEEDBACK/drift_log.json` если есть. Graceful degradation

**Спецификация `_build_monitoring_context(symbol, timeframe)`:**

Структура:
- Всегда Slow Lane
- ThreadPoolExecutor, max_workers=3
- Источники: regime, shock_score, drift_metrics
- Header: `=== MONITORING CONTEXT ({symbol}/{timeframe}) ===`
- Блоки: `[REGIME_HEALTH]`, `[SHOCK_SCORE]`, `[DRIFT]`, `[MISSING SOURCES]`
- **Важно для monitoring:** при `shock_score > 0.25` → блок `[BRAKE_ALERT]` в начало context (после header), с `brake_level` и rationale
- AXM Guard **не** вызывается (monitoring — не forecast, не нужно epistemic check)
- Conflict Exposure тоже неприменимо (пропускаем)
- Budget: если >8000 → truncate drift_metrics (самый низкий priority), затем regime, затем shock_score (highest priority — всегда сохраняется)

**Новый метод `_collect_drift_metrics()`:**

Читает из `MARKET_MIND/LAYER_F_FEEDBACK/drift_log.json`. Этого файла пока скорее всего нет на диске (будущий Task). Graceful degradation → `None`.

**Критерии готовности Часть 3:**
- Метод реализован
- `_collect_drift_metrics()` с graceful degradation
- При отсутствии всех источников → status = "DEGRADED", context_degraded=True, context содержит только header
- Blocks order: brake_alert → regime_health → shock_score → drift (если shock > 0.25)

---

### Часть 4 — Реализация `_build_postmortem_context`

**Цель:** Slow Lane method для `postmortem` task_type. По ТЗ: "audit".

**Mapping ТЗ → collectors:**
- "audit" — аудит какого типа? Predictions audit? Session audit? 
  
  По контексту ТЗ раздел 28 (Postmortem) — это **анализ past forecasts**. Значит источник: past predictions log + их verification results.
  
- Новый collector `_collect_audit_entries(symbol, timeframe)` — читает из `MARKET_MIND/LAYER_H_INTERFACE/audit/*.json` или `LAYER_F_FEEDBACK/predictions_history.json` — зависит от актуальной архитектуры (скорее всего ни того ни другого нет пока, так что N/A)

**Спецификация `_build_postmortem_context(symbol, timeframe)`:**

Минималистичная реализация:
- Всегда Slow Lane
- Один collector: `_collect_audit_entries()`
- Header: `=== POSTMORTEM CONTEXT ({symbol}/{timeframe}) ===`
- Блоки: `[AUDIT_ENTRIES]`, `[MISSING SOURCES]`
- AXM не вызывается, Conflict Exposure неприменим
- Budget: truncate audit_entries если превышение (keep most recent)

При отсутствии audit директории — `_collect_audit_entries()` → None → status "DEGRADED" + context с только header.

**Критерии готовности Часть 4:**
- Метод реализован
- `_collect_audit_entries()` с graceful degradation
- Никаких стубов / placeholder данных если audit пустой

---

### Часть 5 — Budget enforcement (truncation)

**Цель:** если `total_tokens > MAX_TOKENS` (8000) — truncate low-priority blocks до fit в budget.

**Важно:** это применимо **только к Slow Lane** (research/monitoring/postmortem). Fast Lane forecast **не truncate** — L-08 Fast Lane Invariant: faster context over fuller context. Если Fast Lane контекст получился > 8000 токенов (маловероятно но возможно) — `blocks_dropped` помечается `"budget_exceeded"`, но контекст **возвращается as-is** без truncation.

**Подход для Slow Lane:**

1. Подсчитать tokens after context_lines assembly
2. Если > 8000:
   - Определить priority order блоков (task-specific, из BlockSpec)
   - Удалять блоки с **highest priority number** (= lowest priority) пока не fit
   - При удалении — добавлять в `blocks_dropped` с reason `":budget_exceeded"`
   - Rebuild context string без удалённых блоков
   - Recount tokens
3. `context_degraded = True` если хотя бы один блок был удалён из-за budget

**Реализация:**

Вспомогательный приватный метод `_enforce_budget(context_lines, blocks_included, blocks_dropped, priority_order) -> tuple[list[str], int]`:
- Returns: modified context_lines + final token count
- Удаляет блоки из context_lines по priority (которые после токенизации превышают budget)
- Обновляет blocks_included и blocks_dropped

**Критерии готовности Часть 5:**
- Метод `_enforce_budget()` реализован
- Применяется в `_build_research_context`, `_build_monitoring_context`, `_build_postmortem_context` (не в forecast)
- Тесты (Часть 7) покрывают сценарий budget overflow

---

### Часть 6 — `save_session()` реализация

**Цель:** обновлять `MARKET_MIND/CONFIG/session_state.json` с `summary`, `new_items`, `bias`.

**Текущее состояние:** `save_session()` делает input validation и `raise NotImplementedError`. Надо убрать raise и добавить логику.

**Спецификация `save_session(summary: str, new_items: list[str], bias: str | None = None) -> None`:**

1. Validation (уже есть): summary is str, new_items is list[str], bias is str|None
2. Читать current state из `self.market_mind_root / "CONFIG" / "session_state.json"`
3. Обновить поля:
   - `summary = <summary>`
   - `new_items = <new_items>` (replace, not append — ТЗ не specifies, чётко заменяем)
   - `bias = <bias>`
4. Atomically записать назад (write to temp + rename — AP-05 compliance если применим)
5. `logger.info(f"Session state saved: summary length {len(summary)}, {len(new_items)} new items, bias={bias}")`
6. No return value (None)

**Поведение на ошибки:**
- Если `session_state.json` не существует или malformed JSON — `logger.error()` + **re-raise** (в отличие от _collect_ методов, save_session должен сигнализировать ошибку)
- `save_session` **может** raise (OSError, PermissionError, json.JSONDecodeError) — документировать в docstring

**Critical review:** проверь что в ТЗ написано про остальные поля session_state (`current_session`, `active_pair`, `active_timeframe` и т.д.). Если `save_session` трогает только 3 поля — остальные сохраняются как есть.

**Критерии готовности Часть 6:**
- `save_session()` реализован, не raises NotImplementedError
- Validation сохранена (summary str, new_items list[str], bias str|None)
- Existing fields (`current_session`, `active_pair` etc.) сохраняются при обновлении
- Тест проверяет round-trip (save → read → verify)

---

### Часть 7 — Расширение тестов

**Цель:** добавить ~12-15 новых тестов для покрытия research/monitoring/postmortem + save_session + budget truncation.

**Новые тесты (группы):**

**Research context tests (3-4):**
- `test_research_context_returns_result()` — research 1d/4h возвращает ContextResult
- `test_research_context_status_never_aborted()` — никогда ABORTED
- `test_research_context_includes_patterns_and_kb_blocks()` — блоки названы правильно
- `test_research_context_no_forecast_specific_blocks()` — нет [SHOCK_SCORE], [AXM_GUARD] etc. в research

**Monitoring context tests (3-4):**
- `test_monitoring_context_returns_result()`
- `test_monitoring_context_status_never_aborted()`
- `test_monitoring_context_includes_brake_alert_when_high_shock()` — при mock shock_score > 0.25 → [BRAKE_ALERT] в context
- `test_monitoring_context_blocks()` — правильные блоки

**Postmortem context tests (2):**
- `test_postmortem_context_returns_result()`
- `test_postmortem_context_degraded_when_no_audit()`

**save_session tests (3):**
- `test_save_session_updates_fields()` — round-trip test
- `test_save_session_preserves_other_fields()` — existing `current_session` etc. не затерты
- `test_save_session_validates_types()` — ValueError на неверные типы

**Budget tests (2):**
- `test_budget_not_enforced_in_fast_lane()` — Fast Lane over-budget context возвращается as-is с blocks_dropped=["...:budget_exceeded"]
- `test_budget_enforced_in_slow_lane()` — Slow Lane over-budget → truncated

**Итого +~14 тестов. Target: 22 + 14 = 36 тестов.** Фактически может быть 34-36, не критично.

**Runner:** обновить `forecast_tests` в runner + добавить новые группы (возможно новые lists: `research_tests`, `monitoring_tests`, `postmortem_tests`, `session_tests`, `budget_tests` или все в общий `task_05c_tests`).

**Критерии готовности Часть 7:**
- Все тесты проходят
- Runner обновлён
- `python MARKET_MIND/tests/test_context_orchestrator.py` → `[PASS] ~36/36 tests passed`

---

### Часть 8 — Обновление `component_status.json` → ready + MDC COMPLETE commit

**Это критический шаг.** Трогает **самый важный** json в проекте.

**Цель:** обновить `context_orchestrator` компонент в `component_status.json`:
- `status: "not_started"` → `status: "ready"`
- Обновить `last_updated` на текущую ISO дату
- Обновить `ready_for_mdc: true` если раньше было false

**Шаги:**

1. `cat MARKET_MIND/CONFIG/component_status.json` — показать текущее состояние ВСЕХ компонентов (для контекста что MDC 3/4 → 4/4)

2. str_replace того конкретного блока `context_orchestrator`. Точный old_str / new_str после получения cat (будет в отдельном сообщении после подтверждения Части 7).

3. Валидация JSON: `python -c "import json; json.load(open('MARKET_MIND/CONFIG/component_status.json','r',encoding='utf-8'))"` — должно пройти без ошибок

4. Дополнительно посмотреть `system_health_score` — возможно он тоже требует обновления (MDC complete = higher health). Это **второстепенно**, уточним по ходу.

**Критерии готовности Часть 8:**
- `context_orchestrator.status` == `"ready"` в JSON
- JSON валиден
- `cat` подтверждает изменение

---

### Часть 9 — Pre-commit check + L-24 checkpoint + commit

Применение L-24 уже привычно.

1. `python scripts/pre_commit_check.py` — raw output
2. `git status` — raw output
3. `git add` для каждого изменённого файла:
   - `MARKET_MIND/ENGINE/context_orchestrator.py`
   - `MARKET_MIND/tests/test_context_orchestrator.py`
   - `MARKET_MIND/CONFIG/component_status.json`
   - `TASKS/ACTIVE/TASK_05c_*.md`
4. `git status` — все 4 в staged
5. `git diff --cached --stat` — raw output
6. `git diff --cached MARKET_MIND/ENGINE/context_orchestrator.py` — **полный** diff (самый большой файл)
7. `git diff --cached MARKET_MIND/CONFIG/component_status.json` — **полный** diff (critical change)
8. `git diff --cached MARKET_MIND/tests/test_context_orchestrator.py` — полный diff

**ОСТАНОВИСЬ после шага 8 и жди моего подтверждения.**

Я особенно проверю:
- В component_status.json: только `context_orchestrator` изменён, другие компоненты нетронуты
- В context_orchestrator.py: 4 новых метода (`_build_research_context`, `_build_monitoring_context`, `_build_postmortem_context`, `save_session`-переписан, плюс опционально `_enforce_budget`)
- В тестах: +14 тестов
- Никаких `"ABORTED"` literal в новом коде

Только после моего explicit добро — Часть 10.

---

### Часть 10 — Commit + push + PA-08 + archive + MDC CELEBRATION

Финальный commit message должен отражать MDC завершение.

1. `git commit -m "task 05c: Context Orchestrator COMPLETE (research/monitoring/postmortem + save_session) — MDC 4/4 READY"`
2. `git show --stat HEAD` — Channel 1 verification
3. `git push origin main`
4. `git mv TASKS/ACTIVE/TASK_05c_*.md TASKS/COMPLETED/TASK_05c_*.md`
5. `git commit -m "task 05c: archive to completed"`
6. `git push origin main`
7. `git status` → clean

---

## 6. Формат финального отчёта

```
TASK_05c [Context Orchestrator COMPLETE — MDC 4/4 READY] — COMPLETED

Файлы изменены:
  - MARKET_MIND/ENGINE/context_orchestrator.py (+~XXX строк: research/monitoring/postmortem + save_session + _enforce_budget + 2-4 новых _collect_*)
  - MARKET_MIND/tests/test_context_orchestrator.py (+~XXX строк, +14 тестов)
  - MARKET_MIND/CONFIG/component_status.json (context_orchestrator: not_started → ready)

Файлы перемещены:
  - TASKS/ACTIVE/TASK_05c_*.md → TASKS/COMPLETED/

Тесты: XX/XX passed (7 skeleton + 15 forecast + ~14 task_05c)
Commit (main): <hash> task 05c: Context Orchestrator COMPLETE — MDC 4/4 READY
Commit (archive): <hash> task 05c: archive to completed
Время работы: <минуты>

Git verification (L-24 + PA-08 Channel 1):
<первые 25 строк git show --stat HEAD>

MDC STATUS: ████ 4/4 COMPONENTS READY
  ✓ initialize_system
  ✓ schema_layer  
  ✓ data_quality_gates
  ✓ context_orchestrator

Lessons applied: L-01, L-07, L-08 (clarified), L-22, L-24, L-25
Patterns applied: PA-08 (Channel 1 post-commit verification)
Antipatterns avoided: AP-02 (no stubs), AP-04 (no ABORTED anywhere), AP-07 (scope discipline)

=== REFLECTION BLOCK (v5) ===

## Observations from this task
<особенно интересно: восприятие TASK с YES Pre-task Analysis после incident в TASK_05b — чувствовалось ли разница?>

## Self-critique
<1-3 пункта>

## Questions for architect (non-blocking)
<0-3 вопроса>

=== END REFLECTION BLOCK ===

Готов к TASK_06 (PROJECT_PASSPORT) или TASK_07 (comprehensive TZ analysis).
```

---

## 7. Важные предупреждения

### 7.1 PA-09 applied — explicit checkpoints

Этот TASK критически важный (MDC COMPLETE = финал). **После Pre-task Analysis ждёшь моего подтверждения.** После Части 8 (перед commit) ждёшь моего подтверждения. **Явно указаны** два checkpoint — не пропускать, это не формальность после TASK_05b incident.

### 7.2 Scope discipline (AP-07)

Соблазн будет "а заодно расширить AXM Guard" или "добавить ещё один _collect_" — STOP. Scope чёткий: 4 task_types + save_session + budget + ready status. Всё остальное — future TASK.

### 7.3 L-08 clarification — никогда ABORTED

В **ВСЕХ** новых методах (`_build_research_context`, `_build_monitoring_context`, `_build_postmortem_context`) — status всегда `"OK"` или `"DEGRADED"`. **Никогда** `"ABORTED"`. TASK_05b-fix.1 clarified L-08: ABORT только для Model Core aggregation.

### 7.4 P-02 / AP-02 — никаких placeholder данных

Во **всех** новых `_collect_*` (kb, drift, audit) — при недоступности **return None**, не fake data. Даже если соблазн написать `return [{"id": "placeholder", "stub": True}]` чтобы тесты проходили — это AP-02 violation.

### 7.5 L-24 + PA-08

Часть 9 — обязательный `git diff --cached` checkpoint перед commit. Часть 10 — `git show --stat HEAD` после commit (PA-08 Channel 1). **НЕ** web_fetch на raw.github (L-25 cache TTL).

### 7.6 CV-12 предупреждение

В Частях где делаешь diagnostic (cat / git diff) перед transition к action — **raw outputs обязательны**, не summary с ✓. Это специфическая рекомендация после сегодняшнего дня где CV-12 pattern возник multiple times.

### 7.7 L-23 команды по одной

Как обычно.

---

## 8. Ожидаемые метрики

- **Размер изменений в `context_orchestrator.py`:** +200-300 строк
- **Размер изменений в `test_context_orchestrator.py`:** +150-200 строк (14 тестов + helpers)
- **Размер изменений в `component_status.json`:** ~3 строки (status change)
- **Время Claude Code:** 60-90 минут (Pre-task Analysis + 10 Частей, много мелких checkpoints)
- **Approvals:** ~20-30 (много git/grep/cat operations)
- **Commits:** 2 (main + archive)

---

**Конец TASK_05c.**

**После завершения — MDC будет COMPLETE.** Это **первая major milestone проекта** — система готова к первому боевому forecast. Далее TASK_06 (PROJECT_PASSPORT) консолидирует состояние проекта, TASK_07 (comprehensive TZ analysis) начнёт поиск расширений.
