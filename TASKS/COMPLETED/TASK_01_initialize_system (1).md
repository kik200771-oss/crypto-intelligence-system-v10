# ЗАДАЧА 1 — ИНИЦИАЛИЗАЦИЯ СИСТЕМЫ CIS V10.0-r1

## Контекст

Ты реализуешь первый модуль **Crypto Intelligence System V10.0-r1** — системы прогнозирования направления движения цены криптовалют с calibrated uncertainty и самокоррекцией.

Система строится на Windows, рабочая директория: `D:\MARKET_MIND\`

Эта задача — фундамент. Все остальные 29 задач зависят от того что ты создашь здесь.

---

## Что создать

### Файл: `ENGINE/initialize_system.py`

Idempotent скрипт инициализации. При повторном запуске не ломается, не затирает существующие данные — только создаёт то чего нет.

---

## Структура директорий

Создать полную структуру `D:\MARKET_MIND\`:

```
D:\MARKET_MIND\
├── ENGINE\                        # Скрипты и модули системы
├── SCHEMAS\                       # JSON-схемы валидации
├── CONFIG\                        # Конфигурационные файлы
├── LAYER_A_RESEARCH\
│   ├── patterns\
│   ├── hypotheses\
│   ├── experiments\
│   ├── negatives\
│   ├── models\
│   └── audit\
├── LAYER_B_DATA\
│   ├── features\
│   │   └── snapshots\
│   ├── quality_logs\
│   ├── onchain\
│   ├── macro\
│   └── news\
├── LAYER_C_KNOWLEDGE\
│   ├── knowledge_base\
│   └── trust_system\
├── LAYER_D_MODEL\
│   ├── model_versions\
│   ├── predictions\
│   ├── weights\
│   └── shock_log\
├── LAYER_E_VALIDATION\
│   ├── backtest_results\
│   └── validation_reports\
├── LAYER_F_FEEDBACK\
│   ├── prediction_records\
│   ├── outcomes\
│   ├── drift_log\
│   ├── recalibration_log\
│   └── integral_bias_log\
├── LAYER_G_NEWS\
│   ├── raw\
│   └── scored\
├── LAYER_H_INTERFACE\
│   ├── logs\
│   └── exports\
└── meta\
```

---

## CONFIG файлы

### `CONFIG/system_manifest.json`

```json
{
  "version": "10.0",
  "revision": "r1",
  "created_at": "<ISO timestamp>",
  "canon": {
    "math_model": "v6.3-sealed",
    "schematics": "V5",
    "tz": "V10.0-r1"
  },
  "model_approximations": {
    "linear_aggregation": {
      "description": "Линейная агрегация сигналов — предполагает аддитивность",
      "review_condition": ">=50 confirmed patterns AND OOS accuracy > 0.65",
      "status": "active"
    },
    "pi_lite": {
      "description": "PI-lite вместо полного PID — нестационарный рынок",
      "review_condition": ">=200 verified forecasts",
      "status": "active"
    }
  },
  "required_modules": 30,
  "btc_as_macro_indicator": true,
  "trading_pairs_mode": "multi_pair_btc_context"
}
```

### `CONFIG/component_status.json`

30 компонентов, все в статусе `"not_started"`:

```
initialize_system, schema_layer, data_quality_gates, context_orchestrator,
streamlit_ui_basic, hypothesis_formalizer, experiment_registry,
pattern_registry, backtester, validation_engine, insight_saver,
knowledge_ingester, knowledge_search, feature_store, regime_detector,
news_engine, trust_manager, macro_onchain, negative_knowledge_manager,
pattern_decay_monitor, evidence_grading_engine, model_core,
decision_audit, pattern_dsl_compiler, feedback_system,
prediction_tracker, rest_api, backup_reports, prior_manager,
determinism_contract
```

Формат каждого:
```json
"component_name": {
  "status": "not_started",
  "updated_at": null,
  "notes": ""
}
```

### `CONFIG/triz_contradictions.json`

TRZ-001 по TRZ-020 из реестра V10.0-r1:

| ID | Противоречие | Разрешение | Статус | Версия |
|---|---|---|---|---|
| TRZ-001 | Точность ↑ vs Скорость первого прогноза ↓ | candidate status + staged approach | resolved | v7.0 |
| TRZ-002 | Полнота контекста ↑ vs Размер окна ↓ | Context Orchestrator task-aware | resolved | v7.0 |
| TRZ-003 | Чувствительность к паттернам ↑ vs Шум ↓ | Validation Engine + OOS + baseline | resolved | v7.0 |
| TRZ-004 | Адаптивность ↑ vs Стабильность весов ↓ | Control Law beta>=alpha + drift detection | resolved | v7.0 |
| TRZ-005 | Богатство KB ↑ vs Confirmation bias ↓ | KB = только контекст, Inference Boundary | resolved | v7.0 |
| TRZ-006 | Персонализация ↑ vs Объективность ↓ | bias_log + warnings (не фильтрация) | resolved | v7.1 |
| TRZ-007 | Глубина DSL ↑ vs Сложность создания ↓ | hypothesis_formalizer через Claude API | resolved | v7.1 |
| TRZ-008 | Понятность уверенности ↑ vs Честность uncertainty ↓ | conformal_intervals + calibration_bucket + UI rename | resolved | V9.0 |
| TRZ-009 | Скорость обучения ↑ vs Шум в весах ↓ | market_condition_adaptive rates | resolved | V9.0 |
| TRZ-010 | Богатство паттернов ↑ vs Мультиколлинеарность ↓ | Family Cap + Correlation Penalty + orthogonalized_weight | resolved | V9.0 |
| TRZ-011 | Детерминизм ↑ vs Адаптивность ↓ | Determinism Contract 8 параметров + H(Pi_t) hash | resolved | V10.0 |
| TRZ-012 | Calibration ↑ vs Скорость feedback ↓ | Tx_Forecast/Tx_Feedback split — две транзакции | resolved | V10.0 |
| TRZ-013 | Governance ↑ vs Operational flexibility ↓ | Config Governance Partition: Safe/Heuristic/Model-semantic | resolved | V10.0 |
| TRZ-014 | Epistemic guardrail ↑ vs Scoring speed ↓ | AXM = post-scoring guardrail only, не pre-filter | resolved | V10.0 |
| TRZ-015 | Stability ↑ vs Sensitivity к режимам ↓ | Multiple Lyapunov P_r + ADT tau=71 | resolved | V10.0 |
| TRZ-016 | Coverage guarantee ↑ vs Interval width ↓ | Conformal UQ asymmetric + conservative fallback | resolved | V10.0 |
| TRZ-017 | Feasibility check ↑ vs Latency ↓ | B_sev weighted + lightweight per-cycle check | resolved | V10.0 |
| TRZ-018 | Защита данных ↑ vs Доступность при отказе Gate ↓ | Stale Cache Policy — degrade вместо block, stale_cache_ttl | resolved | V10.0 |
| TRZ-019 | Быстрый control ↑ vs Медленный governance ↓ | Fast/Slow Feedback Split — два независимых контура | resolved | V10.0 |
| TRZ-020 | Устойчивость ↑ vs Чувствительность ↓ | Oscillation circuit breaker + dampening rule (MAX_WEIGHT_DELTA, phase lag) | resolved | V10.0 |

### `CONFIG/market_axioms.json`

AXM_001 по AXM_009 — эпистемические аксиомы системы:

| ID | Аксиома | Epistemic status | V10 proxy |
|---|---|---|---|
| AXM_001 | Цена движется только через ордера | approximate | Volume spike + price change correlation (OHLCV) |
| AXM_002 | Bid/ask — механизм ценообразования | approximate | High-Low spread proxy |
| AXM_003 | Тренд имеет инерцию | direct | MA + momentum indicators |
| AXM_004 | Ликвидность влияет на движение | approximate | Volume относительно rolling average |
| AXM_005 | Режим рынка определяет применимость паттернов | direct | Regime Detector R1-R6 |
| AXM_006 | BTC — macro-индикатор для всех альткоинов | direct | BTC OHLCV + dominance |
| AXM_007 | Множественные подтверждения снижают шум | direct | Family Cap + Correlation Penalty |
| AXM_008 | Крупные участники оставляют следы в объёме | approximate | Volume outlier detection (candles > 3sigma) |
| AXM_009 | Паттерн валиден только в своём режиме | direct | valid_in_regimes filter |

Для AXM_001, 002, 004, 008: `"axiom_proxy": true`, `"causal_confidence_penalty": -0.15`

### `CONFIG/structural_priors.json`

PRI_001 по PRI_019 — 19 структурных прайоров. Формат:
```json
{
  "id": "PRI_001",
  "description": "...",
  "default_weight": 1.0,
  "category": "...",
  "review_condition": "..."
}
```

Категории и прайоры:
- **trend**: PRI_001 (тренд продолжается чаще чем разворачивается), PRI_002 (более высокий TF доминирует)
- **regime**: PRI_003 (sideways режим снижает signal quality), PRI_004 (stress режим — все паттерны под сомнением), PRI_005 (BTC определяет направление альткоинов)
- **validation**: PRI_006 (IS accuracy > OOS accuracy = overfit), PRI_007 (confirmed_cases < 20 = ненадёжно), PRI_008 (паттерн вне valid_in_regimes = weight × 0.2)
- **uncertainty**: PRI_009 (calibration_bucket=uncalibrated = высокая неопределённость), PRI_010 (data_stale=True = расширить uncertainty interval)
- **feedback**: PRI_011 (drift_level >= 3 = recalibration), PRI_012 (I-term reset при regime shift), PRI_013 (phase_lag = 1 цикл для weight changes)
- **epistemic**: PRI_014 (AXM применяется после scoring, не до), PRI_015 (KB влияет только на контекст, не на direction), PRI_016 (GPT-критик = независимый взгляд без KB-контекста)
- **operational**: PRI_017 (Fast Feedback max 200ms Claude-free), PRI_018 (Tx_Feedback = отдельная транзакция от Tx_Forecast), PRI_019 (Silence Debt = diagnostic только, не actuator)

### `CONFIG/timeframe_core.json`

```json
{
  "mode": "standard_core",
  "description": "User-configurable. Default: Standard Core.",
  "standard_core": {
    "timeframes": ["15m", "1h", "4h", "1d"],
    "primary": "4h",
    "context": "1d",
    "fast_lane": ["1h", "4h"]
  },
  "tf_multipliers": {
    "1w": 1.5, "1d": 1.3, "4h": 1.0,
    "1h": 0.85, "15m": 0.7, "5m": 0.55, "1m": 0.4
  },
  "tf_conflict_penalty": -0.10,
  "tf_agreement_bonus": 0.05
}
```

### `CONFIG/stale_data_policy.json`

```json
{
  "stale_cache_ttl_seconds": 300,
  "uncertainty_penalty": 0.10,
  "sources": {
    "ohlcv": {"ttl_seconds": 300},
    "orderbook": {"ttl_seconds": 60},
    "funding_rate": {"ttl_seconds": 3600},
    "onchain": {"ttl_seconds": 7200},
    "macro": {"ttl_seconds": 86400}
  }
}
```

---

## Шаблонные файлы

### `LAYER_A_RESEARCH/meta/how_to_read_me.md`

```markdown
# CIS V10.0-r1 — Руководство для Claude

## Inference Boundary
KB влияет только на explanation и context quality.
Не на direction прогноза. Это защита от KB-bias.

## TF Hierarchy
1w > 1d > 4h > 1h > 15m > 5m > 1m
При конфликте: junior TF weight × 0.3, confidence -= 0.10
При согласованности: confidence += 0.05

## Epistemic Status
- direct: данные напрямую измеряют явление
- approximate: OHLCV-proxy, causal_confidence_penalty = -0.15
- uncertain: недостаточно данных

## Три правила канона
1. Stability proof ≠ predictive validity
2. Determinism ≠ correctness
3. Conformal coverage ≠ trading edge

## Операциональный сценарий
Трейдер → гипотеза → Claude анализирует → Система считает →
Claude интерпретирует → GPT (опционально) критикует →
Трейдер принимает решение
```

### `LAYER_A_RESEARCH/meta/index.json`

Пустой индекс с полями: `patterns_count`, `hypotheses_count`, `experiments_count`, `last_updated`.

### `LAYER_C_KNOWLEDGE/trust_system/trust_registry.json`

Начальные источники:
```json
{
  "sources": {
    "CoinDesk": {"trust": 0.5, "category": "news"},
    "CoinTelegraph": {"trust": 0.5, "category": "news"},
    "Decrypt": {"trust": 0.5, "category": "news"},
    "Glassnode": {"trust": 0.5, "category": "onchain"},
    "Binance": {"trust": 0.8, "category": "exchange_data"}
  }
}
```

### `LAYER_D_MODEL/session_state.json`

```json
{
  "current_session": null,
  "active_pair": null,
  "active_timeframe": null,
  "last_forecast": null,
  "regime": "unknown",
  "silence_debt": 0,
  "shock_score": 0.0
}
```

---

## Критерии готовности

1. Все директории 8 слоёв существуют
2. `CONFIG/system_manifest.json` содержит `"version": "10.0"` и `model_approximations` с двумя approximations
3. `CONFIG/component_status.json` содержит ровно 30 компонентов все в `"not_started"`
4. `CONFIG/triz_contradictions.json` содержит TRZ-001..TRZ-020
5. `CONFIG/market_axioms.json` содержит AXM_001..AXM_009
6. `CONFIG/structural_priors.json` содержит PRI_001..PRI_019
7. Повторный запуск скрипта не выдаёт ошибок и не затирает существующие данные

---

## Проверка после выполнения

```python
# Запусти этот код для проверки
import json, os

base = r"D:\MARKET_MIND"

# 1. Директории
layers = ["LAYER_A_RESEARCH", "LAYER_B_DATA", "LAYER_C_KNOWLEDGE",
          "LAYER_D_MODEL", "LAYER_E_VALIDATION", "LAYER_F_FEEDBACK",
          "LAYER_G_NEWS", "LAYER_H_INTERFACE"]
for layer in layers:
    assert os.path.exists(os.path.join(base, layer)), f"Missing: {layer}"

# 2. Manifest
with open(os.path.join(base, "CONFIG", "system_manifest.json")) as f:
    m = json.load(f)
assert m["version"] == "10.0"
assert "model_approximations" in m
assert len(m["model_approximations"]) == 2

# 3. Component status
with open(os.path.join(base, "CONFIG", "component_status.json")) as f:
    cs = json.load(f)
assert len(cs) == 30, f"Expected 30 components, got {len(cs)}"

# 4. TRIZ
with open(os.path.join(base, "CONFIG", "triz_contradictions.json")) as f:
    triz = json.load(f)
assert len(triz) == 20

# 5. AXM
with open(os.path.join(base, "CONFIG", "market_axioms.json")) as f:
    axm = json.load(f)
assert len(axm) == 9

# 6. PRI
with open(os.path.join(base, "CONFIG", "structural_priors.json")) as f:
    pri = json.load(f)
assert len(pri) == 19

print("✅ Все проверки пройдены. Задача 1 выполнена.")
```

---

## Примечания

- Путь `D:\MARKET_MIND\` — основная рабочая директория на Windows
- Скрипт должен работать как `python ENGINE/initialize_system.py` из директории `D:\MARKET_MIND\`
- Логировать каждое созданное/пропущенное действие в stdout
- После успешного запуска обновить `component_status.json`: `initialize_system → "ready"`
