# TASK_03 — SCHEMA LAYER V2 (6 канонических схем + DSL grammar + validator)

**Тип:** содержательный компонент (первая MDC-задача)
**Приоритет:** критично — фундамент для валидации всех данных системы
**Исполнитель:** Claude Code
**Источник:** ТЗ V10.0-r1 Задача 2 + раздел 1.8 "Pattern DSL и Lifecycle" + раздел "pattern_schema.json / prediction_schema.json / experiment_schema.json"
**Статус:** ACTIVE
**Зависимости:** TASK_02 (rebuild infrastructure) — ✅, TASK_02.5 (hardening) — ✅
**Блокирует:** TASK_04 (data_quality_gates v2), множество последующих задач

---

## ⚠ Contract reminder

Соблюдай CLAUDE.md v4, все 30 параграфов. При любом сомнении — § 3 (СТОП + вопрос Сергею).

Перед началом — **прочти когнитивные файлы** (§ 25):
- `LESSONS_LEARNED.md` v1.2 (15 уроков L-01..L-16, L-12 reserved)
- `PATTERNS.md` (5 паттернов P-01..P-05)
- `ANTIPATTERNS.md` v1.2 (9 антипаттернов AP-01..AP-09)

Особенно релевантно для этой задачи:
- **L-01:** Сверь TASK с ТЗ построчно. Если что-то расходится — § 3.
- **L-02:** Статус `ready` только после полного соответствия ТЗ.
- **L-03 / P-01 / AP-01:** Pre-commit hook уже проверяет hardcoded пути — должно быть 0 нарушений.
- **L-04 / P-05 / AP-06:** ASCII маркеры в тестах.
- **L-07 / P-02 / AP-02:** Никаких stub данных в production коде.
- **§ 29:** Модульные docstrings + ссылки на уроки в коде.
- **§ 11 / AP-09:** Никакого force push в main.

Pre-commit hook установлен — он автоматически ловит AP-01/03/05/06/08 + TODO/FIXME. Полагайся на него, но ручная проверка § 24 по-прежнему обязательна.

---

## Контекст и scope

Компонент `schema_layer` по `component_status.json` имеет статус `needs_rewrite`. В репо существует `MARKET_MIND/ENGINE/schema_validator.py` и несколько файлов в `MARKET_MIND/SCHEMAS/`, но они неполные и не соответствуют V9.0 полям из ТЗ § 1.8.

**Что делаем в TASK_03:**
1. Переписать/создать 6 канонических JSON-схем в `MARKET_MIND/SCHEMAS/`
2. Создать `MARKET_MIND/SCHEMAS/dsl_grammar.md` — полный синтаксис DSL (placeholder, формализация в Task 23)
3. Переписать `MARKET_MIND/ENGINE/schema_validator.py` с правильным API
4. Реализовать `generate_snapshot_id(data) → str`
5. Написать тесты для каждой схемы
6. Обновить `component_status.json`: `schema_layer: ready`

**Что НЕ делаем в TASK_03 (зона других задач):**
- `data_quality_monitor.py` / Gates 1-6 — это **TASK_04** (отдельный файл в ENGINE)
- Полный DSL compiler — это **TASK_23** (Pattern DSL Compiler)
- Hypothesis Formalizer через Claude API — **TASK_05**
- Negative Knowledge полная логика — **TASK_17** (хоть схема создаётся сейчас)

Разделение scope с TASK_04 явное: в TASK_03 мы создаём `schema_validator.py` + 6 `.json` схем + `dsl_grammar.md`. Всё что касается Gates остаётся для TASK_04.

---

## Рабочая директория

`C:\CODE\MARKET ANALYSIS\`

---

## Предусловия

1. Текущая ветка — `main`, local = remote (после завершения TASK_02.5)
2. Последний коммит в main — `archive TASK_02.5` или свежее
3. `git status` показывает **только** следующие изменения (L-09):
   - untracked: `TASKS/ACTIVE/TASK_03_schema_layer.md` (сам файл задачи)
   - возможно modified: `.claude/settings.local.json` (permissions — нормально)
4. `python MARKET_MIND/ENGINE/initialize_system.py` выводит `[PASS]` (структура инфраструктуры правильная)
5. `python scripts/verify_infrastructure.py` выводит `[PASS]`
6. Git pre-commit hook установлен: `.git/hooks/pre-commit` существует
7. Проверка hook работоспособен: `python scripts/pre_commit_check.py` возвращает `[PASS]` или `[INFO] No staged files`
8. Локальных веток кроме `main` нет: `git branch` → только `* main`

Если любое условие не выполнено → § 3 (СТОП).

---

## Часть 1 — Создать ветку

```bash
cd "C:\CODE\MARKET ANALYSIS"
git checkout main
git pull origin main
git checkout -b task-03-schema-layer
```

---

## Часть 2 — Предварительный аудит существующих файлов

Перед тем как писать новое, посмотри что уже есть. Это **только диагностика**, ничего не меняй.

```bash
echo "=== Что в SCHEMAS/ сейчас ==="
dir MARKET_MIND\SCHEMAS\

echo ""
echo "=== Что в schema_validator.py сейчас ==="
type MARKET_MIND\ENGINE\schema_validator.py
```

**Ожидания:**
- В `SCHEMAS/` может быть 3-5 файлов (неполный набор от прежних попыток)
- `schema_validator.py` существует, но API/реализация не соответствуют ТЗ

**Не удаляй существующие файлы сейчас.** В Части 3 мы их перезапишем. TASK явно разрешает переписывание:
- `MARKET_MIND/SCHEMAS/*.json` — полностью переписываем по V9.0
- `MARKET_MIND/ENGINE/schema_validator.py` — полностью переписываем

---

## Часть 3 — Создать 6 JSON-схем в `MARKET_MIND/SCHEMAS/`

Все схемы — **JSON Schema draft 2020-12** (используем `jsonschema>=4.0` библиотеку, уже в requirements.txt).

Создать следующие файлы (перезаписать существующие):

### 3.1 — `MARKET_MIND/SCHEMAS/pattern_schema.json`

По ТЗ § 1.8 (pattern_schema.json все поля V9.0).

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "pattern_schema.json",
  "title": "Pattern Schema V9.0",
  "description": "Схема торгового паттерна с полным набором полей V9.0 (6 статусов, epistemic_status, pattern_family, emergency, orthogonalized weight).",
  "type": "object",
  "required": [
    "id", "name", "logic_dsl", "symbol", "timeframe",
    "status", "confidence_point", "evidence_grade",
    "created_at", "last_updated"
  ],
  "properties": {
    "id": {"type": "string", "pattern": "^[A-Za-z0-9_-]+$", "description": "Уникальный ID паттерна"},
    "name": {"type": "string", "minLength": 1, "description": "Человекочитаемое имя"},
    "logic_dsl": {"type": "string", "description": "Логика паттерна на DSL (см. dsl_grammar.md)"},
    "logic_human": {"type": "string", "description": "Человекочитаемое описание логики"},
    "symbol": {"type": "string", "pattern": "^[A-Z0-9]+$", "description": "Торговый символ, например BTCUSDT"},
    "timeframe": {"type": "string", "enum": ["1m", "5m", "15m", "30m", "1h", "4h", "12h", "1d", "1w"]},
    "window_hours": {"type": "number", "exclusiveMinimum": 0, "description": "Размер окна анализа в часах"},
    "lag_hours_min": {"type": "number", "minimum": 0},
    "lag_hours_max": {"type": "number", "minimum": 0},

    "status": {
      "type": "string",
      "enum": ["testing", "candidate", "confirmed", "unstable", "decayed", "rejected"],
      "description": "Lifecycle status (ровно 6 значений по ТЗ § 1.8)"
    },

    "confidence_point": {"type": "number", "minimum": 0.0, "maximum": 1.0},
    "confirmed_cases": {"type": "integer", "minimum": 0},
    "total_cases": {"type": "integer", "minimum": 0},
    "is_performance": {"type": "number", "description": "In-sample performance"},
    "oos_performance": {"type": "number", "description": "Out-of-sample performance"},
    "recent_performance": {"type": "number", "description": "Recent rolling performance"},

    "valid_in_regimes": {
      "type": "array",
      "items": {"type": "string"},
      "description": "Список режимов рынка где паттерн валиден"
    },
    "exceptions": {
      "type": "array",
      "items": {"type": "string"}
    },

    "evidence_grade": {"type": "string", "enum": ["A", "B", "C", "D"]},
    "evidence_grade_breakdown": {
      "type": "object",
      "properties": {
        "temporal_precedence": {"type": "number", "minimum": 0.0, "maximum": 1.0},
        "period_stability": {"type": "number", "minimum": 0.0, "maximum": 1.0},
        "asset_robustness": {"type": "number", "minimum": 0.0, "maximum": 1.0},
        "regime_sensitivity": {"type": "number", "minimum": 0.0, "maximum": 1.0},
        "confounder_sensitivity": {"type": "number", "minimum": 0.0, "maximum": 1.0}
      },
      "additionalProperties": false
    },
    "evidence_grade_method": {
      "type": "string",
      "enum": ["deterministic", "claude_assisted"],
      "description": "Способ получения evidence_grade (по ТЗ: детерминированный предпочтителен)"
    },

    "pattern_family_id": {"type": ["string", "null"], "description": "ID семейства паттернов для Family Cap"},
    "correlation_cluster_id": {"type": ["string", "null"]},
    "orthogonalized_weight": {"type": ["number", "null"], "description": "Вес с учётом корреляции внутри family"},

    "canonical_id": {"type": ["string", "null"]},
    "duplicate_of": {"type": ["string", "null"]},

    "emergency_flag": {"type": "boolean", "default": false},
    "emergency_reason": {"type": ["string", "null"]},
    "emergency_at": {"type": ["string", "null"], "format": "date-time"},
    "recovery_eligible_at": {"type": ["string", "null"], "format": "date-time"},

    "epistemic_status": {
      "type": "string",
      "enum": ["validated", "validated_partial", "validated_negative"]
    },

    "linked_patterns": {"type": "array", "items": {"type": "string"}},
    "linked_negatives": {"type": "array", "items": {"type": "string"}},
    "source_hypothesis": {"type": ["string", "null"]},

    "market_regime_at_discovery": {"type": ["string", "null"]},
    "btc_price_at_discovery": {"type": ["number", "null"]},

    "created_at": {"type": "string", "format": "date-time"},
    "last_updated": {"type": "string", "format": "date-time"},
    "decay_check_at": {"type": ["string", "null"], "format": "date-time"}
  },
  "additionalProperties": false
}
```

### 3.2 — `MARKET_MIND/SCHEMAS/prediction_schema.json`

По ТЗ § 1.8.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "prediction_schema.json",
  "title": "Prediction Schema V9.0",
  "description": "Схема прогноза. Включает uncertainty_band, shock_score, Fast Lane поля, verification_policy.",
  "type": "object",
  "required": [
    "id", "model_version", "symbol", "timeframe", "direction",
    "confidence_point", "uncertainty_band_low", "uncertainty_band_high",
    "shock_score", "horizon_hours", "verify_at", "created_at"
  ],
  "properties": {
    "id": {"type": "string", "pattern": "^[A-Za-z0-9_-]+$"},
    "model_version": {"type": "string"},
    "symbol": {"type": "string", "pattern": "^[A-Z0-9]+$"},
    "timeframe": {"type": "string", "enum": ["1m", "5m", "15m", "30m", "1h", "4h", "12h", "1d", "1w"]},

    "direction": {"type": "string", "enum": ["UP", "DOWN", "NEUTRAL"]},
    "confidence_point": {"type": "number", "minimum": 0.0, "maximum": 1.0},
    "uncertainty_band_low": {"type": "number", "minimum": 0.0, "maximum": 1.0},
    "uncertainty_band_high": {"type": "number", "minimum": 0.0, "maximum": 1.0},

    "dominant_uncertainty": {
      "type": ["string", "null"],
      "enum": ["small_sample", "regime_instability", "signal_conflict", "data_quality", null]
    },
    "calibration_bucket": {
      "type": "string",
      "enum": ["uncalibrated", "low", "moderate", "high"]
    },

    "strength": {"type": "number", "minimum": 0.0, "maximum": 1.0},
    "final_score": {"type": "number"},
    "bull_score": {"type": "number"},
    "bear_score": {"type": "number"},

    "shock_score": {"type": "number", "minimum": 0.0, "maximum": 1.0},
    "brake_level": {"type": "string", "enum": ["none", "soft", "hard"]},
    "brake_reason": {"type": ["string", "null"]},

    "suppressed": {"type": "boolean", "default": false},

    "horizon_hours": {"type": "number", "exclusiveMinimum": 0},
    "verify_at": {"type": "string", "format": "date-time"},

    "verification_policy": {
      "type": "string",
      "enum": ["horizon_end", "any_within_horizon", "terminal_direction", "max_favorable_excursion"]
    },

    "tf_alignment": {
      "type": "object",
      "properties": {
        "senior_tf": {"type": ["string", "null"]},
        "junior_tf": {"type": ["string", "null"]},
        "aligned": {"type": "boolean"},
        "conflict": {"type": "boolean"}
      },
      "additionalProperties": false
    },

    "triggered_patterns": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "weight", "epistemic_status"],
        "properties": {
          "id": {"type": "string"},
          "weight": {"type": "number"},
          "epistemic_status": {"type": "string", "enum": ["validated", "validated_partial", "validated_negative"]}
        },
        "additionalProperties": false
      }
    },

    "blocked_by_anti": {"type": "array", "items": {"type": "string"}},
    "regime_at_prediction": {"type": ["string", "null"]},

    "context_snapshot_id": {"type": ["string", "null"]},
    "context_degraded": {"type": "boolean", "default": false},
    "prior_snapshot_id": {"type": ["string", "null"]},

    "actual_direction": {"type": ["string", "null"], "enum": ["UP", "DOWN", "NEUTRAL", null]},
    "correct": {"type": ["boolean", "null"]},
    "verified_at": {"type": ["string", "null"], "format": "date-time"},
    "created_at": {"type": "string", "format": "date-time"}
  },
  "additionalProperties": false
}
```

### 3.3 — `MARKET_MIND/SCHEMAS/experiment_schema.json`

По ТЗ § 1.8.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "experiment_schema.json",
  "title": "Experiment Schema V9.0",
  "description": "Схема эксперимента с pre-registration (V9.0: preregistered + data_cutoff_date).",
  "type": "object",
  "required": [
    "id", "hypothesis_id", "test_method", "symbol", "timeframe",
    "data_snapshot_id", "preregistered", "verdict", "created_at"
  ],
  "properties": {
    "id": {"type": "string", "pattern": "^[A-Za-z0-9_-]+$"},
    "hypothesis_id": {"type": "string"},
    "test_method": {"type": "string", "description": "Метод теста (backtest, walk-forward, OOS и т.п.)"},
    "symbol": {"type": "string", "pattern": "^[A-Z0-9]+$"},
    "timeframe": {"type": "string", "enum": ["1m", "5m", "15m", "30m", "1h", "4h", "12h", "1d", "1w"]},

    "data_snapshot_id": {"type": "string", "description": "ID снапшота данных (воспроизводимость)"},

    "preregistered": {"type": "boolean"},
    "data_cutoff_date": {"type": "string", "format": "date-time", "description": "Дата отсечки данных (до которой smoke test не смотрит)"},
    "preregistered_at": {"type": ["string", "null"], "format": "date-time"},

    "train_period": {
      "type": "object",
      "properties": {
        "start": {"type": "string", "format": "date-time"},
        "end": {"type": "string", "format": "date-time"}
      },
      "additionalProperties": false
    },
    "test_period": {
      "type": "object",
      "properties": {
        "start": {"type": "string", "format": "date-time"},
        "end": {"type": "string", "format": "date-time"}
      },
      "additionalProperties": false
    },
    "sample_size": {"type": "integer", "minimum": 0},

    "metrics": {
      "type": "object",
      "properties": {
        "accuracy": {"type": "number"},
        "sharpe": {"type": "number"},
        "drawdown": {"type": "number"},
        "baseline_delta": {"type": "number"}
      },
      "additionalProperties": true
    },
    "oos_metrics": {
      "type": "object",
      "additionalProperties": true
    },

    "verdict": {
      "type": "string",
      "enum": ["confirmed", "rejected", "inconclusive", "overfit", "unstable"]
    },
    "epistemic_status": {
      "type": "string",
      "enum": ["validated", "hypothetical"]
    },

    "created_at": {"type": "string", "format": "date-time"}
  },
  "additionalProperties": false
}
```

### 3.4 — `MARKET_MIND/SCHEMAS/hypothesis_schema.json`

ТЗ не даёт полной формализации схемы hypothesis (детали в Task 5 Hypothesis Formalizer). Создаём canonical minimum который будет расширяться:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "hypothesis_schema.json",
  "title": "Hypothesis Schema V10.0",
  "description": "Схема гипотезы (pre-registered перед тестированием). Расширяется Task 5 Hypothesis Formalizer.",
  "type": "object",
  "required": ["id", "statement", "symbol", "timeframe", "status", "created_at"],
  "properties": {
    "id": {"type": "string", "pattern": "^[A-Za-z0-9_-]+$"},
    "statement": {"type": "string", "minLength": 10, "description": "Формальное утверждение гипотезы"},

    "symbol": {"type": "string", "pattern": "^[A-Z0-9]+$"},
    "timeframe": {"type": "string", "enum": ["1m", "5m", "15m", "30m", "1h", "4h", "12h", "1d", "1w"]},

    "predicted_direction": {"type": ["string", "null"], "enum": ["UP", "DOWN", "NEUTRAL", null]},
    "predicted_effect_size": {"type": ["number", "null"]},

    "status": {
      "type": "string",
      "enum": ["draft", "formalized", "preregistered", "tested", "archived"],
      "description": "Lifecycle гипотезы (Task 5 определит полную логику переходов)"
    },

    "preregistered_at": {"type": ["string", "null"], "format": "date-time"},
    "data_cutoff_date": {"type": ["string", "null"], "format": "date-time"},

    "linked_experiments": {"type": "array", "items": {"type": "string"}},
    "linked_patterns": {"type": "array", "items": {"type": "string"}},

    "source": {"type": ["string", "null"], "description": "KB source id / paper / user input"},

    "created_at": {"type": "string", "format": "date-time"},
    "last_updated": {"type": ["string", "null"], "format": "date-time"}
  },
  "additionalProperties": false
}
```

### 3.5 — `MARKET_MIND/SCHEMAS/negative_schema.json`

Полная семантика в Task 17 Negative Knowledge. Canonical minimum:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "negative_schema.json",
  "title": "Negative Knowledge Schema V10.0",
  "description": "Схема negative knowledge entry (debunked pattern / failed hypothesis). Расширяется Task 17.",
  "type": "object",
  "required": ["id", "debunked_claim", "reason", "evidence_grade", "created_at"],
  "properties": {
    "id": {"type": "string", "pattern": "^[A-Za-z0-9_-]+$"},
    "debunked_claim": {"type": "string", "minLength": 10, "description": "Что именно опровергнуто"},
    "reason": {"type": "string", "description": "Причина опровержения (failed OOS, overfit, regime-specific, etc.)"},

    "linked_pattern": {"type": ["string", "null"], "description": "ID паттерна который стал negative"},
    "linked_hypothesis": {"type": ["string", "null"]},
    "linked_experiment": {"type": ["string", "null"], "description": "ID эксперимента который привёл к rejection"},

    "evidence_grade": {"type": "string", "enum": ["A", "B", "C", "D"]},
    "applies_to_symbols": {"type": "array", "items": {"type": "string"}},
    "applies_to_regimes": {"type": "array", "items": {"type": "string"}},

    "created_at": {"type": "string", "format": "date-time"},
    "last_verified_at": {"type": ["string", "null"], "format": "date-time"}
  },
  "additionalProperties": false
}
```

### 3.6 — `MARKET_MIND/SCHEMAS/source_schema.json`

Для Knowledge Base / Trust Manager (Task 18). Canonical minimum:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "source_schema.json",
  "title": "Source Schema V10.0",
  "description": "Схема источника знаний (KB entry, news source, reference). Расширяется Task 18 Trust Manager.",
  "type": "object",
  "required": ["id", "source_type", "title", "trust_score", "created_at"],
  "properties": {
    "id": {"type": "string", "pattern": "^[A-Za-z0-9_-]+$"},
    "source_type": {
      "type": "string",
      "enum": ["classic_book", "paper", "news_feed", "user_note", "web_article", "internal"]
    },
    "title": {"type": "string", "minLength": 1},
    "author": {"type": ["string", "null"]},
    "url": {"type": ["string", "null"], "format": "uri"},
    "publication_date": {"type": ["string", "null"], "format": "date-time"},

    "trust_score": {"type": "number", "minimum": 0.0, "maximum": 1.0, "description": "4-контурный trust score (детали — Task 18)"},
    "trust_contours": {
      "type": "object",
      "properties": {
        "authority": {"type": "number", "minimum": 0.0, "maximum": 1.0},
        "track_record": {"type": "number", "minimum": 0.0, "maximum": 1.0},
        "methodology": {"type": "number", "minimum": 0.0, "maximum": 1.0},
        "recency": {"type": "number", "minimum": 0.0, "maximum": 1.0}
      },
      "additionalProperties": false
    },

    "tags": {"type": "array", "items": {"type": "string"}},
    "summary": {"type": ["string", "null"]},

    "created_at": {"type": "string", "format": "date-time"},
    "last_reviewed_at": {"type": ["string", "null"], "format": "date-time"}
  },
  "additionalProperties": false
}
```

---

## Часть 4 — Создать `MARKET_MIND/SCHEMAS/dsl_grammar.md`

Это **placeholder документ** описывающий текущее состояние DSL. Полная грамматика будет в TASK_23 (Pattern DSL Compiler). Но canonical описание нужно уже сейчас.

```markdown
# Pattern DSL Grammar V10.0-r1 (Initial Draft)

> **Статус документа:** initial draft. Полная формализация грамматики — в Task 23 (Pattern DSL Compiler).
> Этот файл — canonical minimum для обеспечения валидности pattern_schema.logic_dsl.

## Назначение

DSL (Domain Specific Language) позволяет описать логику торгового паттерна в структурированном, машинно-читаемом виде. Каждый паттерн в `pattern_schema.json` имеет поле `logic_dsl` — строку на этом DSL.

## Базовый синтаксис (draft)

```
WHEN <condition> THEN <signal>
```

Где:
- `<condition>` — логическое выражение над рыночными данными
- `<signal>` — сигнал паттерна (UP/DOWN/NEUTRAL)

## Примеры

```
WHEN rsi(14) < 30 AND volume > sma(volume, 20) * 1.5 THEN UP
```

```
WHEN macd_line > macd_signal AND price > ema(50) THEN UP
```

```
WHEN bb_lower > price AND rsi(14) < 25 THEN UP
```

## Операторы (draft)

| Оператор | Семантика |
|---|---|
| `<`, `>`, `<=`, `>=`, `==`, `!=` | Сравнение |
| `AND`, `OR`, `NOT` | Логические |
| `+`, `-`, `*`, `/` | Арифметика |

## Функции индикаторов (draft)

| Функция | Описание |
|---|---|
| `rsi(period)` | Relative Strength Index |
| `sma(series, period)` | Simple Moving Average |
| `ema(period)` | Exponential Moving Average |
| `macd_line`, `macd_signal`, `macd_hist` | MACD компоненты |
| `bb_upper`, `bb_middle`, `bb_lower` | Bollinger Bands |
| `volume` | Объём |
| `price` | Текущая цена (close) |

## Валидация на уровне schema_validator

В TASK_03 (текущий этап) поле `logic_dsl` валидируется как `string` без syntactic проверки DSL. Полный parser/validator появится в Task 23.

## Связь с pattern_schema

Поле `pattern_schema.logic_dsl` содержит DSL-строку. Поле `pattern_schema.logic_human` — человекочитаемое описание той же логики (пишется автором паттерна).

Пример:
```json
{
  "logic_dsl": "WHEN rsi(14) < 30 AND volume > sma(volume, 20) * 1.5 THEN UP",
  "logic_human": "Перепроданность по RSI с аномально высоким объёмом предсказывает рост"
}
```

## Развитие

Task 23 (Pattern DSL Compiler) добавит:
- Формальную BNF-грамматику
- Lexer/parser
- Type checking (numeric vs boolean)
- Оптимизация выражений
- Конвертацию в Python callable для Feature Store

## История

| Дата | Версия | Изменения |
|---|---|---|
| 2026-04-XX | initial | Draft grammar для TASK_03 schema layer v2 |
```

---

## Часть 5 — Переписать `MARKET_MIND/ENGINE/schema_validator.py`

**Перезапиши файл полностью** (существующий `needs_rewrite` — см. `component_status.json`).

Применяем:
- **P-01** (относительные пути через `Path(__file__).resolve()`)
- **P-03** (конкретные exception + логирование)
- **P-04** (graceful при отсутствии схемы — ошибка, не возврат None)
- **L-03, L-06** (никаких hardcoded `C:\`)
- **L-04** (UTF-8 явно)
- **§ 13, § 16, § 29** (docstrings модуля, функций, ссылки на уроки в комментариях)
- **AP-02** (никаких stub данных — реальная реализация)

```python
"""
schema_validator — JSON Schema валидатор для 6 канонических схем CIS V10.0-r1.

Загружает схемы из MARKET_MIND/SCHEMAS/ и предоставляет публичный API
для валидации объектов. Используется всеми компонентами системы для
проверки данных перед записью в файловое хранилище.

Задача 2 из ТЗ V10.0-r1 (первая часть — schema layer).
Компонент: schema_layer.

Используемые паттерны: P-01 (relative paths), P-03 (exception handling),
P-04 (graceful config).

Соответствует CLAUDE.md § 16 (docstrings + type hints), § 29 (стандарт
комментирования), § 13 (UTF-8).
"""
from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# jsonschema library — добавлена в requirements.txt в TASK_00
# applies P-03: import ошибка будет явной если jsonschema не установлен
from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError as _JsonSchemaValidationError

logger = logging.getLogger(__name__)

# Канонические имена схем согласно ТЗ V10.0-r1 Задача 2
# Список фиксирован — любая схема за пределами списка считается неизвестной
CANONICAL_SCHEMAS: tuple[str, ...] = (
    "pattern",
    "prediction",
    "experiment",
    "hypothesis",
    "negative",
    "source",
)


class SchemaValidationError(Exception):
    """
    Исключение при неуспешной валидации объекта по схеме.

    Содержит список ошибок валидации (каждая строка — одна проблема).
    Используется публичным API validate() в strict-режиме.
    """

    def __init__(self, schema_name: str, errors: list[str]) -> None:
        self.schema_name = schema_name
        self.errors = errors
        message = f"Validation failed for schema '{schema_name}': {len(errors)} error(s)"
        super().__init__(message)


@dataclass(frozen=True)
class ValidationResult:
    """
    Результат валидации объекта по схеме.

    Атрибуты:
        ok: True если валидация прошла, False иначе
        schema_name: имя схемы по которой валидировали
        errors: список сообщений об ошибках (пустой если ok=True)
    """
    ok: bool
    schema_name: str
    errors: list[str] = field(default_factory=list)


class SchemaValidator:
    """
    Валидатор объектов по каноническим JSON-схемам.

    Публичный контракт:
      - validate(data, schema_name) -> ValidationResult: non-throwing, возвращает результат
      - validate_strict(data, schema_name) -> None: поднимает SchemaValidationError при ошибках
      - list_schemas() -> tuple[str, ...]: список известных схем
      - generate_snapshot_id(data) -> str: детерминированный ID объекта для reproducibility

    Инвариант:
      - Схемы загружаются лениво (при первом обращении) и кэшируются в памяти.
      - Базовая директория — MARKET_MIND/SCHEMAS/ относительно корня проекта (P-01).
      - Поддерживается опциональный параметр base_path для тестов.

    Пример использования:
      >>> v = SchemaValidator()
      >>> result = v.validate(my_pattern_dict, "pattern")
      >>> if not result.ok:
      ...     for err in result.errors:
      ...         print(err)
    """

    def __init__(self, schemas_dir: Path | str | None = None) -> None:
        """
        Инициализация валидатора.

        Args:
            schemas_dir: путь к директории со схемами. По умолчанию —
                MARKET_MIND/SCHEMAS/ относительно этого файла (P-01, L-03).
                Параметр для тестов и нестандартных развёртываний.
        """
        if schemas_dir is None:
            # applies P-01: ENGINE/schema_validator.py -> MARKET_MIND -> SCHEMAS/
            # Никакого hardcoded C:\CODE — L-03, L-06, AP-01
            schemas_dir = Path(__file__).resolve().parent.parent / "SCHEMAS"
        self.schemas_dir: Path = Path(schemas_dir)
        # Кэш валидаторов: schema_name -> Draft202012Validator
        self._validators: dict[str, Draft202012Validator] = {}
        # Кэш сырых схем: schema_name -> dict
        self._schemas: dict[str, dict[str, Any]] = {}

    def list_schemas(self) -> tuple[str, ...]:
        """
        Возвращает кортеж имён всех канонических схем.

        Returns:
            Кортеж из 6 имён в порядке из CANONICAL_SCHEMAS.
        """
        return CANONICAL_SCHEMAS

    def _load_schema(self, schema_name: str) -> Draft202012Validator:
        """
        Загружает схему с диска и кэширует её валидатор.

        Args:
            schema_name: имя схемы без расширения (например "pattern")

        Returns:
            Draft202012Validator инстанс

        Raises:
            ValueError: если schema_name не канонический
            FileNotFoundError: если файл схемы не найден
            json.JSONDecodeError: если файл не валидный JSON
        """
        if schema_name in self._validators:
            return self._validators[schema_name]

        # L-01: сверяем имя с каноном из ТЗ
        if schema_name not in CANONICAL_SCHEMAS:
            raise ValueError(
                f"Unknown schema '{schema_name}'. "
                f"Canonical: {', '.join(CANONICAL_SCHEMAS)}"
            )

        schema_path = self.schemas_dir / f"{schema_name}_schema.json"
        try:
            # § 13: UTF-8 explicit (L-04)
            raw = schema_path.read_text(encoding="utf-8")
        except FileNotFoundError:
            # P-03: конкретный exception + логирование, потом re-raise
            logger.error(f"Schema file not found: {schema_path}")
            raise
        except OSError as e:
            logger.error(f"Cannot read schema file {schema_path}: {e}")
            raise

        try:
            schema = json.loads(raw)
        except json.JSONDecodeError as e:
            logger.error(f"Schema {schema_name} is malformed JSON: {e}")
            raise

        # Validate schema itself (meta-validation)
        try:
            Draft202012Validator.check_schema(schema)
        except Exception as e:
            logger.error(f"Schema {schema_name} is not a valid JSON Schema: {e}")
            raise

        validator = Draft202012Validator(schema)
        self._schemas[schema_name] = schema
        self._validators[schema_name] = validator
        logger.debug(f"Loaded schema: {schema_name}")
        return validator

    def validate(self, data: Any, schema_name: str) -> ValidationResult:
        """
        Валидирует объект по указанной схеме (non-throwing).

        Применяет P-02 (graceful): возвращает структурированный результат,
        не бросает исключение на невалидные данные (бросает только на
        системные проблемы — нет схемы, нет файла).

        Args:
            data: объект для валидации (обычно dict)
            schema_name: имя канонической схемы (см. list_schemas())

        Returns:
            ValidationResult(ok, schema_name, errors)

        Raises:
            ValueError: если schema_name не канонический
            FileNotFoundError: если файл схемы отсутствует
        """
        validator = self._load_schema(schema_name)
        # iter_errors возвращает генератор всех ошибок (не только первой)
        errors_list: list[str] = []
        for err in validator.iter_errors(data):
            errors_list.append(self._format_error(err))

        ok = len(errors_list) == 0
        return ValidationResult(ok=ok, schema_name=schema_name, errors=errors_list)

    def validate_strict(self, data: Any, schema_name: str) -> None:
        """
        Валидирует объект и бросает SchemaValidationError при ошибках.

        Для случаев когда "нельзя продолжать с невалидными данными".

        Args:
            data: объект для валидации
            schema_name: имя канонической схемы

        Raises:
            SchemaValidationError: если валидация не прошла
            ValueError/FileNotFoundError: как в validate()
        """
        result = self.validate(data, schema_name)
        if not result.ok:
            raise SchemaValidationError(schema_name, result.errors)

    @staticmethod
    def _format_error(err: _JsonSchemaValidationError) -> str:
        """
        Форматирует jsonschema ValidationError в читаемую строку.

        Приватный helper — не часть публичного API.
        """
        # Путь до поля (если есть) + сообщение
        if err.absolute_path:
            path = ".".join(str(p) for p in err.absolute_path)
            return f"{path}: {err.message}"
        return err.message

    def generate_snapshot_id(self, data: Any) -> str:
        """
        Генерирует детерминированный ID для объекта (для reproducibility).

        Использует SHA-256 от canonical JSON представления. Одинаковый объект
        всегда даст одинаковый ID. Используется experiment_schema.data_snapshot_id
        и context_snapshot_id в prediction_schema.

        Args:
            data: любой JSON-сериализуемый объект

        Returns:
            Строка вида "sha256:<hex>", фиксированная длина.
        """
        # sort_keys=True обеспечивает детерминизм при одинаковых данных
        # ensure_ascii=False сохраняет не-ASCII (безопасно, hash от utf-8 bytes)
        canonical = json.dumps(data, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
        digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        return f"sha256:{digest}"


# Удобная функция модуля — для случаев когда не нужен класс
_default_validator: SchemaValidator | None = None


def get_default_validator() -> SchemaValidator:
    """
    Возвращает singleton-экземпляр SchemaValidator с дефолтным путём.

    Для удобства в простых случаях. Для тестов / кастомных путей —
    создавай SchemaValidator(schemas_dir=...) напрямую.
    """
    global _default_validator
    if _default_validator is None:
        _default_validator = SchemaValidator()
    return _default_validator


def validate(data: Any, schema_name: str) -> ValidationResult:
    """
    Функция-обёртка — валидирует через default validator.

    Args:
        data: объект для валидации
        schema_name: имя канонической схемы

    Returns:
        ValidationResult
    """
    return get_default_validator().validate(data, schema_name)


def generate_snapshot_id(data: Any) -> str:
    """
    Функция-обёртка — generate_snapshot_id через default validator.

    Args:
        data: JSON-сериализуемый объект

    Returns:
        "sha256:<hex>" строка
    """
    return get_default_validator().generate_snapshot_id(data)
```

**Критически важно:**
- **Нет hardcoded путей** (AP-01). Pre-commit hook это проверит.
- **Нет emoji в print** — у нас вообще нет print, только logger.
- **Нет bare except** — все exception handling конкретные (FileNotFoundError, OSError, JSONDecodeError).
- **Нет TODO/FIXME** в коде — всё либо реализовано, либо отсылает к будущей задаче в docstring (что допустимо).

---

## Часть 6 — Написать тесты

Создать файл `MARKET_MIND/tests/test_schema_validator.py`.

Это **первый тестовый файл в проекте**. Поэтому:
1. Создать директорию `MARKET_MIND/tests/` с `__init__.py` и `.gitkeep`-ом уже есть? Проверь; если нет — создай
2. Добавить `tests/fixtures/` для тестовых данных

Содержимое `MARKET_MIND/tests/test_schema_validator.py`:

```python
"""
test_schema_validator — тесты для SchemaValidator (TASK_03).

Применяет P-05 (ASCII markers, UTF-8 reconfigure).
Использует только standard library + jsonschema, без pytest (чтобы работало
автономно без дополнительных зависимостей).

Запуск:
    python MARKET_MIND/tests/test_schema_validator.py
"""
from __future__ import annotations

import sys
from pathlib import Path

# L-04 / P-05: защита Windows cp1251 (AP-06 avoidance)
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

# applies P-01: относительный путь до корня проекта для sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Теперь можем импортировать
from MARKET_MIND.ENGINE.schema_validator import (
    SchemaValidator,
    SchemaValidationError,
    ValidationResult,
    CANONICAL_SCHEMAS,
    generate_snapshot_id,
    validate,
)


# === Helper-функции для тестов ===

def _valid_pattern() -> dict:
    """Минимальный валидный объект pattern."""
    return {
        "id": "pattern_001",
        "name": "RSI Oversold",
        "logic_dsl": "WHEN rsi(14) < 30 THEN UP",
        "symbol": "BTCUSDT",
        "timeframe": "4h",
        "status": "candidate",
        "confidence_point": 0.65,
        "evidence_grade": "B",
        "created_at": "2026-04-18T10:00:00Z",
        "last_updated": "2026-04-18T10:00:00Z"
    }


def _valid_prediction() -> dict:
    """Минимальный валидный объект prediction."""
    return {
        "id": "pred_001",
        "model_version": "v1.0.0",
        "symbol": "BTCUSDT",
        "timeframe": "4h",
        "direction": "UP",
        "confidence_point": 0.7,
        "uncertainty_band_low": 0.55,
        "uncertainty_band_high": 0.85,
        "calibration_bucket": "moderate",
        "shock_score": 0.15,
        "brake_level": "none",
        "horizon_hours": 4.0,
        "verify_at": "2026-04-18T14:00:00Z",
        "verification_policy": "horizon_end",
        "created_at": "2026-04-18T10:00:00Z"
    }


def _valid_experiment() -> dict:
    """Минимальный валидный объект experiment."""
    return {
        "id": "exp_001",
        "hypothesis_id": "hyp_001",
        "test_method": "walk_forward_OOS",
        "symbol": "BTCUSDT",
        "timeframe": "4h",
        "data_snapshot_id": "sha256:abc123",
        "preregistered": True,
        "data_cutoff_date": "2026-04-01T00:00:00Z",
        "verdict": "confirmed",
        "created_at": "2026-04-18T10:00:00Z"
    }


# === Тесты ===

def test_list_schemas_returns_six() -> None:
    """list_schemas() возвращает ровно 6 канонических имён."""
    v = SchemaValidator()
    schemas = v.list_schemas()
    assert len(schemas) == 6, f"Expected 6 schemas, got {len(schemas)}"
    assert set(schemas) == {"pattern", "prediction", "experiment", "hypothesis", "negative", "source"}, \
        f"Schema names mismatch: {schemas}"
    print("[OK] test_list_schemas_returns_six")


def test_canonical_schemas_constant() -> None:
    """CANONICAL_SCHEMAS константа содержит 6 имён."""
    assert len(CANONICAL_SCHEMAS) == 6
    assert "pattern" in CANONICAL_SCHEMAS
    assert "prediction" in CANONICAL_SCHEMAS
    assert "experiment" in CANONICAL_SCHEMAS
    print("[OK] test_canonical_schemas_constant")


def test_valid_pattern_passes() -> None:
    """Валидный pattern проходит validate."""
    v = SchemaValidator()
    result = v.validate(_valid_pattern(), "pattern")
    assert result.ok, f"Expected ok=True, got errors: {result.errors}"
    assert result.errors == []
    assert result.schema_name == "pattern"
    print("[OK] test_valid_pattern_passes")


def test_pattern_status_enum_strict() -> None:
    """pattern_schema.status enum — ровно 6 значений по ТЗ § 1.8."""
    v = SchemaValidator()
    expected_statuses = {"testing", "candidate", "confirmed", "unstable", "decayed", "rejected"}
    for st in expected_statuses:
        obj = _valid_pattern()
        obj["status"] = st
        result = v.validate(obj, "pattern")
        assert result.ok, f"Status '{st}' should be valid, errors: {result.errors}"
    # Недопустимый status
    obj = _valid_pattern()
    obj["status"] = "unknown_status"
    result = v.validate(obj, "pattern")
    assert not result.ok, "Invalid status should fail"
    print("[OK] test_pattern_status_enum_strict (6 values)")


def test_invalid_pattern_missing_required() -> None:
    """Pattern без required поля не проходит."""
    v = SchemaValidator()
    obj = _valid_pattern()
    del obj["id"]
    result = v.validate(obj, "pattern")
    assert not result.ok
    assert len(result.errors) > 0
    print("[OK] test_invalid_pattern_missing_required")


def test_prediction_uncertainty_band_required() -> None:
    """prediction_schema требует uncertainty_band_low и _high (ТЗ критерий 7)."""
    v = SchemaValidator()
    obj = _valid_prediction()
    del obj["uncertainty_band_low"]
    result = v.validate(obj, "prediction")
    assert not result.ok, "Prediction without uncertainty_band_low should fail"
    print("[OK] test_prediction_uncertainty_band_required")


def test_prediction_shock_score_required() -> None:
    """prediction_schema требует shock_score (ТЗ критерий 7)."""
    v = SchemaValidator()
    obj = _valid_prediction()
    del obj["shock_score"]
    result = v.validate(obj, "prediction")
    assert not result.ok, "Prediction without shock_score should fail"
    print("[OK] test_prediction_shock_score_required")


def test_experiment_preregistered_required() -> None:
    """experiment_schema требует preregistered и data_cutoff_date (ТЗ критерий 8)."""
    v = SchemaValidator()
    obj = _valid_experiment()
    del obj["preregistered"]
    result = v.validate(obj, "experiment")
    assert not result.ok, "Experiment without preregistered should fail"

    obj = _valid_experiment()
    del obj["data_cutoff_date"]
    result = v.validate(obj, "experiment")
    assert not result.ok, "Experiment without data_cutoff_date should fail"
    print("[OK] test_experiment_preregistered_required")


def test_validate_strict_raises_on_invalid() -> None:
    """validate_strict поднимает SchemaValidationError на невалидном объекте (ТЗ критерий 10)."""
    v = SchemaValidator()
    obj = _valid_pattern()
    del obj["name"]  # убрать required
    raised = False
    try:
        v.validate_strict(obj, "pattern")
    except SchemaValidationError as e:
        raised = True
        assert e.schema_name == "pattern"
        assert len(e.errors) > 0
    assert raised, "SchemaValidationError must be raised"
    print("[OK] test_validate_strict_raises_on_invalid")


def test_validate_strict_silent_on_valid() -> None:
    """validate_strict не поднимает исключение на валидном объекте."""
    v = SchemaValidator()
    try:
        v.validate_strict(_valid_pattern(), "pattern")
    except Exception as e:
        raise AssertionError(f"Should not raise on valid data, got: {e}")
    print("[OK] test_validate_strict_silent_on_valid")


def test_unknown_schema_raises_valueerror() -> None:
    """Неизвестная схема → ValueError."""
    v = SchemaValidator()
    raised = False
    try:
        v.validate({}, "nonexistent")
    except ValueError as e:
        raised = True
        assert "nonexistent" in str(e)
    assert raised, "Unknown schema must raise ValueError"
    print("[OK] test_unknown_schema_raises_valueerror")


def test_generate_snapshot_id_deterministic() -> None:
    """generate_snapshot_id одинаково для одинаковых данных."""
    v = SchemaValidator()
    data1 = {"a": 1, "b": 2}
    data2 = {"b": 2, "a": 1}  # другой порядок ключей
    id1 = v.generate_snapshot_id(data1)
    id2 = v.generate_snapshot_id(data2)
    assert id1 == id2, f"Hash must be deterministic, got {id1} vs {id2}"
    assert id1.startswith("sha256:"), f"Expected sha256: prefix, got {id1}"
    print("[OK] test_generate_snapshot_id_deterministic")


def test_generate_snapshot_id_differs_for_different_data() -> None:
    """Разные данные → разные snapshot_id."""
    v = SchemaValidator()
    id1 = v.generate_snapshot_id({"a": 1})
    id2 = v.generate_snapshot_id({"a": 2})
    assert id1 != id2
    print("[OK] test_generate_snapshot_id_differs_for_different_data")


def test_module_level_functions() -> None:
    """Модульные wrappers validate() и generate_snapshot_id() работают."""
    result = validate(_valid_pattern(), "pattern")
    assert result.ok
    snap = generate_snapshot_id({"test": True})
    assert snap.startswith("sha256:")
    print("[OK] test_module_level_functions")


def test_hypothesis_schema_minimal() -> None:
    """hypothesis minimal valid object passes."""
    v = SchemaValidator()
    obj = {
        "id": "hyp_001",
        "statement": "RSI oversold predicts upward move in BTC 4h",
        "symbol": "BTCUSDT",
        "timeframe": "4h",
        "status": "draft",
        "created_at": "2026-04-18T10:00:00Z"
    }
    result = v.validate(obj, "hypothesis")
    assert result.ok, f"Valid hypothesis should pass, errors: {result.errors}"
    print("[OK] test_hypothesis_schema_minimal")


def test_negative_schema_minimal() -> None:
    """negative minimal valid object passes."""
    v = SchemaValidator()
    obj = {
        "id": "neg_001",
        "debunked_claim": "High-volume RSI oversold always means UP reversal",
        "reason": "Fails in bearish regimes (OOS test 2024-Q2)",
        "evidence_grade": "B",
        "created_at": "2026-04-18T10:00:00Z"
    }
    result = v.validate(obj, "negative")
    assert result.ok, f"Valid negative should pass, errors: {result.errors}"
    print("[OK] test_negative_schema_minimal")


def test_source_schema_minimal() -> None:
    """source minimal valid object passes."""
    v = SchemaValidator()
    obj = {
        "id": "src_001",
        "source_type": "classic_book",
        "title": "Technical Analysis of the Financial Markets",
        "trust_score": 0.85,
        "created_at": "2026-04-18T10:00:00Z"
    }
    result = v.validate(obj, "source")
    assert result.ok, f"Valid source should pass, errors: {result.errors}"
    print("[OK] test_source_schema_minimal")


# === Runner ===

def run_all_tests() -> int:
    """Запускает все тесты, возвращает количество ошибок."""
    tests = [
        test_list_schemas_returns_six,
        test_canonical_schemas_constant,
        test_valid_pattern_passes,
        test_pattern_status_enum_strict,
        test_invalid_pattern_missing_required,
        test_prediction_uncertainty_band_required,
        test_prediction_shock_score_required,
        test_experiment_preregistered_required,
        test_validate_strict_raises_on_invalid,
        test_validate_strict_silent_on_valid,
        test_unknown_schema_raises_valueerror,
        test_generate_snapshot_id_deterministic,
        test_generate_snapshot_id_differs_for_different_data,
        test_module_level_functions,
        test_hypothesis_schema_minimal,
        test_negative_schema_minimal,
        test_source_schema_minimal,
    ]

    failures: list[tuple[str, str]] = []
    for test in tests:
        try:
            test()
        except AssertionError as e:
            failures.append((test.__name__, str(e)))
        except Exception as e:
            # Неожиданное исключение — тоже failure, но другого типа
            failures.append((test.__name__, f"UNEXPECTED: {type(e).__name__}: {e}"))

    total = len(tests)
    passed = total - len(failures)
    print()
    print(f"=== Results: {passed}/{total} passed ===")
    if failures:
        print("[FAIL]")
        for name, msg in failures:
            print(f"  - {name}: {msg}")
        return 1
    print("[PASS]")
    return 0


if __name__ == "__main__":
    sys.exit(run_all_tests())
```

Также создать `MARKET_MIND/tests/__init__.py` (пустой — для импорта):
```python
```

---

## Часть 7 — Запустить тесты

```bash
cd "C:\CODE\MARKET ANALYSIS"
python MARKET_MIND/tests/test_schema_validator.py
```

Ожидается:
```
[OK] test_list_schemas_returns_six
[OK] test_canonical_schemas_constant
[OK] test_valid_pattern_passes
...
[OK] test_source_schema_minimal

=== Results: 17/17 passed ===
[PASS]
```

Если любой `[OK]` отсутствует или `[FAIL]` — **не коммитить**. Разбирайся по списку (§ 3).

---

## Часть 8 — Обновить `component_status.json`

```bash
# Прочитать текущий статус
type MARKET_MIND\CONFIG\component_status.json
```

Найти запись `schema_layer` и заменить её на:

```json
"schema_layer": {
    "status": "ready",
    "updated_at": "2026-04-18",
    "notes": "Task 03: 6 canonical schemas (pattern, prediction, experiment, hypothesis, negative, source) with V9.0 fields per TZ § 1.8. SchemaValidator with validate/validate_strict/generate_snapshot_id. 17/17 tests pass. dsl_grammar.md placeholder for Task 23."
}
```

**Не трогай другие компоненты** (AP-07).

---

## Часть 9 — Коммит и merge

### 9.1 Проверка перед коммитом

```bash
git status
```

Ожидаемые изменения:
- `M MARKET_MIND/CONFIG/component_status.json`
- `M MARKET_MIND/ENGINE/schema_validator.py` (перезаписан)
- `A MARKET_MIND/SCHEMAS/pattern_schema.json` (возможно M если был)
- `A MARKET_MIND/SCHEMAS/prediction_schema.json`
- `A MARKET_MIND/SCHEMAS/experiment_schema.json`
- `A MARKET_MIND/SCHEMAS/hypothesis_schema.json`
- `A MARKET_MIND/SCHEMAS/negative_schema.json`
- `A MARKET_MIND/SCHEMAS/source_schema.json`
- `A MARKET_MIND/SCHEMAS/dsl_grammar.md`
- `A MARKET_MIND/tests/__init__.py`
- `A MARKET_MIND/tests/test_schema_validator.py`

Никаких других файлов не должно быть.

### 9.2 Pre-commit checklist (§ 24)

Пройди весь checklist. Особенно:
- Тесты 17/17 PASS
- В schema_validator.py нет hardcoded путей (hook проверит)
- Нет реальных секретов
- UTF-8 без BOM
- Docstrings + type hints на публичных функциях/классах (§ 16, § 29)
- Ссылки на уроки (P-01, L-03) присутствуют в комментариях (§ 29.3)

### 9.3 Коммит

```bash
git add MARKET_MIND/
git commit -m "task 03: schema layer v2 (6 canonical schemas V9.0 + validator + dsl_grammar placeholder)"
# Pre-commit hook должен вывести [PASS]
```

### 9.4 Merge

```bash
git checkout main
git merge task-03-schema-layer
git push origin main
git branch -d task-03-schema-layer
```

**Не force push** (AP-09). Обычный push.

### 9.5 Проверка синхронизации

```bash
git fetch origin
git log --oneline origin/main..main   # должен быть пуст
git log --oneline main..origin/main   # должен быть пуст
```

### 9.6 Архивация TASK

```bash
git mv TASKS/ACTIVE/TASK_03_schema_layer.md TASKS/COMPLETED/TASK_03_schema_layer.md
git commit -m "archive TASK_03"
git push origin main
```

---

## Часть 10 — Финальный отчёт

Пришли Сергею отчёт в формате § 9:

```
TASK_03 [schema_layer_v2] — COMPLETED

Файлы созданы:
  - MARKET_MIND/SCHEMAS/pattern_schema.json (V9.0 полные поля)
  - MARKET_MIND/SCHEMAS/prediction_schema.json (V9.0)
  - MARKET_MIND/SCHEMAS/experiment_schema.json (V9.0)
  - MARKET_MIND/SCHEMAS/hypothesis_schema.json (minimal V10.0)
  - MARKET_MIND/SCHEMAS/negative_schema.json (minimal V10.0)
  - MARKET_MIND/SCHEMAS/source_schema.json (minimal V10.0)
  - MARKET_MIND/SCHEMAS/dsl_grammar.md (placeholder, полное в Task 23)
  - MARKET_MIND/tests/__init__.py
  - MARKET_MIND/tests/test_schema_validator.py (17 тестов)

Файлы изменены:
  - MARKET_MIND/ENGINE/schema_validator.py (полностью переписан)
  - MARKET_MIND/CONFIG/component_status.json (schema_layer → ready)

Файлы удалены: none

Тесты: 17/17 passed
Commit: <hash> task 03: schema layer v2 (...)
Archive commit: <hash> archive TASK_03
Push в origin/main: успешный (без push protection блокировок)

Время работы: <минуты>

ТЗ соответствие (критерии готовности Задачи 2 в части schema):
  - [6] pattern_schema enum статусов = 6 значений ✓
  - [7] prediction_schema содержит uncertainty_band_low, uncertainty_band_high, shock_score ✓
  - [8] experiment_schema содержит preregistered и data_cutoff_date ✓
  - [10] validate() с невалидным объектом → SchemaValidationError ✓ (через validate_strict)

Lessons applied:
  - L-01 (сверил поля схем с ТЗ § 1.8 построчно)
  - L-02 (статус ready только после 17/17 тестов PASS)
  - L-03 / AP-01 (relative paths через Path(__file__).resolve())
  - L-04 / AP-06 (ASCII маркеры в тестах, UTF-8 reconfigure)
  - L-07 / AP-02 (никаких stub данных в schema_validator)

Patterns applied:
  - P-01 (Path(__file__).resolve() в __init__)
  - P-03 (конкретные exception FileNotFoundError/OSError/JSONDecodeError)
  - P-05 (структура теста с ASCII маркерами)

Antipatterns avoided:
  - AP-01 (0 hardcoded путей, hook confirmed)
  - AP-02 (0 stub данных, real implementation)
  - AP-03 (нет bare except, AST-checker confirmed)
  - AP-06 (ASCII в print)
  - AP-07 (только файлы из TASK, ничего лишнего)
  - AP-08 (нет реальных секретов в коде/тестах)
  - AP-09 (обычный push в main, без force)

Component status updates:
  - schema_layer: needs_rewrite → ready (ВТОРОЙ честный ready статус за проект)

Ideas logged: <N>
Warnings/issues: none (или описать)

Готов к TASK_04 (data_quality_gates v2).
```

---

## Критерии готовности (acceptance criteria)

- [ ] 6 JSON-схем созданы в `MARKET_MIND/SCHEMAS/` с полями V9.0 по ТЗ § 1.8
- [ ] `MARKET_MIND/SCHEMAS/dsl_grammar.md` создан (placeholder, явно помечен)
- [ ] `MARKET_MIND/ENGINE/schema_validator.py` полностью переписан согласно § 16, § 29, применяет P-01/P-03
- [ ] `MARKET_MIND/tests/test_schema_validator.py` содержит 17+ тестов, все PASS
- [ ] `generate_snapshot_id(data)` работает детерминированно
- [ ] Pre-commit hook пропустил коммит без нарушений
- [ ] `component_status.json`: `schema_layer: ready` с корректными notes
- [ ] TZ критерии 6, 7, 8, 10 проверены тестами
- [ ] TASK в COMPLETED, main синхронизирован с origin

---

## Важные предупреждения

- ⚠ **Не добавляй полей в схемы сверх ТЗ** (AP-07). Если кажется что какое-то поле "хорошо бы иметь" — § 3.
- ⚠ **Не трогай `TZ/`**. Это канон.
- ⚠ **Не меняй другие компоненты** в `component_status.json` кроме `schema_layer`. Их задача — последующие TASK.
- ⚠ **Не реализуй DSL parser в schema_validator.py** — это Task 23. В TASK_03 `logic_dsl` валидируется как обычная строка.
- ⚠ **Не реализуй Data Quality Gates** — это TASK_04. Ни под каким предлогом.
- ⚠ При смоук-тесте pre-commit hook, если вдруг что-то блокирует — § 3, не обходи через `--no-verify`.
- ⚠ **Никакого force push** (AP-09). Обычные push через main, force только через soft reset если надо откатить smoke commits (L-16).

---

**После успешного TASK_03 — готовимся к TASK_04 (data_quality_gates v2) и далее TASK_05 (context_orchestrator v2). Это завершит MDC-тройку.**
