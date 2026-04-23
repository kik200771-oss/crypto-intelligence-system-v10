# Observation: ТЗ Задача 3 gap — shock_score как source для monitoring context не specify

**Дата:** 2026-04-23
**Автор:** Claude Opus (архитектор)
**Категория:** observation / TZ-gap
**Тип:** фактическое наблюдение с suggested follow-up
**Defer to:** TASK_07 (Comprehensive TZ Analysis)

---

## Факты

**ТЗ Задача 3 (Context Orchestrator)** определяет 4 task_types: `forecast`, `research`, `monitoring`, `postmortem`. Для каждого описаны источники данных.

**Для `monitoring` task_type ТЗ упоминает scope как "health + drift + shock_score"** (косвенно — через описание назначения monitoring режима), но **не перечисляет явно** `shock_score` в списке источников контекста наряду с regime и drift.

**Практическая consequence:** при реализации TASK_05c Часть 3 (`_build_monitoring_context`) Claude Code интуитивно понял что monitoring без shock_score info не выполняет свою функцию — точка monitoring режима ловить аномалии состояния системы. Реализовал inline duplicate shock collector с ad-hoc выбранным путём `LAYER_H_INFRA/shock_score.json`.

**Incident:** inline duplicate — AP-02 violation (scope expansion через создание нового collection path вместо канонического паттерна других `_collect_*` методов). Path выбор (`LAYER_H_INFRA`) — ad-hoc, не соответствует layer semantics (INFRA для logs/api/backup, не для data sources).

**Resolution:** TASK_05c-fix.1 (2026-04-23) — canonical `_collect_shock_score` method + cleanup inline duplicate. Но это **не решает** underlying ТЗ gap.

---

## Что конкретно gap содержит

### Gap #1: shock_score как source в monitoring context — explicit statement отсутствует

ТЗ Задачи 3 для forecast task_type детально перечисляет обязательные и желательные источники (feature_snapshot, validated_patterns, negative_filters, regime_context, timeframe_context, prior_snapshot). Для monitoring — высокоуровневое описание без аналогичного уровня детализации.

**Вопрос:** какие источники обязательны для monitoring, какие желательны, какой degradation behavior при их отсутствии?

### Gap #2: shock_score.json path / schema / lifecycle

**ТЗ Задача 11 (Shock Score / Brake Detector)** определяет сам механизм но не определяет (либо не специфицирует с достаточной точностью):
- Где хранится output (path)
- Schema артефакта (поля, types)
- Lifecycle (когда перезаписывается, TTL, persistence)
- Trigger для Context Orchestrator чтения

**Consequence:** Claude Code в TASK_05c выбрал ad-hoc путь `LAYER_H_INFRA/shock_score.json`. Это может противоречить замыслу Task 11 когда тот будет реализован.

### Gap #3: shock_score в forecast context (Fast Lane)?

**ТЗ Задача 3 forecast-режим** shock_score **не включает** в источники. Но intuitively Fast Lane forecast мог бы benefit от brake state awareness — если система в режиме emergency brake, прогноз должен об этом знать (или пользователь должен видеть в ответе).

**Open architectural question:** должен ли Fast Lane forecast видеть shock_score? Если да — как это взаимодействует с Fast Lane Invariant (прогноз не блокируется ожиданием)?

### Gap #4: brake_level thresholds источник

В `_build_monitoring_context` hardcoded:
```python
brake_level = "MEDIUM" if shock_score_value <= 0.5 else "HIGH" if shock_score_value <= 0.75 else "CRITICAL"
```

Thresholds `0.25 / 0.5 / 0.75` — откуда? ТЗ их explicit не specify. Возможно:
- Hardcoded в Context Orchestrator (текущее)
- Config-driven через `timeframe_core.json`
- Часть `shock_score` артефакта сам (Task 11 их определяет)

---

## Почему это важно

1. **Scope discipline.** Каждая task должна соответствовать ТЗ (L-01). Gaps в ТЗ заставляют Claude Code и архитектора impровизировать, что приводит к AP-02 violations (как в TASK_05c) или architectural drift.

2. **Task 11 integration.** Когда Brake Detector будет реализован, текущий `_collect_shock_score` placeholder должен быть заменён на реальное чтение. Без explicit ТЗ спецификации path/schema/lifecycle — риск что Task 11 реализация создаст файл в **другом** месте относительно того что ожидает Context Orchestrator.

3. **Consistency с другими monitoring источниками.** `_collect_regime_context` читает из канонического path по ТЗ. `_collect_drift_metrics` — тоже. `_collect_shock_score` пока не имеет канонического path — это anomaly.

---

## Suggested resolution в TASK_07 scope

TASK_07 (Comprehensive TZ Analysis) — батч-review ТЗ на consistency / completeness. Предлагаемые точки для этого observation:

### Resolution 1: Явно дополнить ТЗ Задача 3 monitoring section

Добавить в ТЗ Задачу 3 для monitoring task_type:

```markdown
Обязательные источники monitoring context:
- regime_context (health proxy)
- drift_metrics
- shock_score

Degradation behavior: любой из 3 источников отсутствует → partial_inputs=True, 
missing источники помечаются в context_degraded, monitoring продолжается 
с доступными данными. BRAKE_ALERT блок формируется только при shock_score 
valid + > threshold.
```

### Resolution 2: Дополнить ТЗ Задача 11 контрактом output артефакта

Добавить в ТЗ Задачу 11:

```markdown
Output артефакт shock_score:
- Path: <TBD — обсудить в TASK_07, варианты: LAYER_D_MODEL/shock/, LAYER_B_DATA/shock/, etc.>
- Schema:
  - shock_score: float [0.0, 1.0]
  - timestamp: ISO 8601
  - symbol: string
  - timeframe: string
  - trigger_factors: list[string] (что вызвало shock)
  - thresholds: {"medium": 0.25, "high": 0.5, "critical": 0.75}
- Lifecycle: перезаписывается на каждый Brake Detector run (per symbol/timeframe)
- TTL: N/A (всегда актуальное состояние)
- Trigger: Brake Detector run — по расписанию или по событию
```

### Resolution 3: Явный архитектурный decision по shock_score в forecast

Отдельный вопрос для TASK_07: **должен ли Fast Lane forecast видеть shock_score?**

- **Вариант A (current):** нет, shock_score только в monitoring. Forecast не зависит от brake state.
- **Вариант B:** да, shock_score как желательный источник forecast. При valid shock > threshold — добавляется в context с пометкой но не блокирует.
- **Вариант C:** shock_score affects confidence_point/uncertainty_band в forecast (не как source контекста, а как post-processing signal).

Требует отдельного обсуждения в свете Fast Lane Invariant и Math Model v6.3.

### Resolution 4: Config-driven thresholds

Перенести `brake_level` thresholds (0.25 / 0.5 / 0.75) из hardcoded в `timeframe_core.json` или сделать их частью shock_score артефакта (resolution 2 schema).

---

## Связь с другими observations

Этот observation дополняет briefing `BRIEFING_2026-04-22.md` — секция "Open questions / не решено" уже упоминала:
- **shock_score.json path** — где должен жить?
- **ТЗ Task 11** — когда реализуется?

Этот файл фиксирует вопрос более систематически для TASK_07 batch обработки.

---

## Что я (архитектор) не делаю сейчас

- **Не меняю ТЗ.** ТЗ изменяется только через deliberate process в TASK_07, не реактивно
- **Не расширяю TASK_05c-fix.1 scope.** Fix остаётся minimal: canonical collector + cleanup AP-02
- **Не навязываю resolution.** Suggested resolutions выше — starting points для обсуждения в TASK_07, не финальные решения

---

**Конец observation.**

---

**File status:** draft для commit в `TASKS/NOTES/observations/` — commit возможен отдельно от TASK_05c-fix.1 или после него (по удобству Сергея).

**Applicability:** TASK_07 (Comprehensive TZ Analysis) — primary consumer. TASK_06 (PROJECT_PASSPORT) — secondary (open questions index).
