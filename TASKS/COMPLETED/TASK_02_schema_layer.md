# ЗАДАЧА 2 — SCHEMA LAYER + DATA QUALITY GATES [Этап 1]

## Статус задачи 1
`initialize_system` ✅ ready — инфраструктура развёрнута в `C:\КОДИНГ\MARKET ANALYSIS\MARKET_MIND\`

---

## Контекст

Ты реализуешь Задачу 2 системы **Crypto Intelligence System V10.0-r1**.

**Рабочая директория:** `C:\КОДИНГ\MARKET ANALYSIS\MARKET_MIND\`

Эта задача создаёт два фундаментальных компонента:
1. **Schema Layer** — контракты валидации всех объектов системы
2. **Data Quality Gates** — 6 проверок качества входящих данных

Без них система не может гарантировать что данные которые она анализирует — корректны. Все последующие задачи (Feature Store, Model Core, Feedback) зависят от этих двух компонентов.

**Справочные материалы:**
- `C:\КОДИНГ\MARKET ANALYSIS\MARKET_MIND\CONFIG\system_manifest.json`
- `C:\КОДИНГ\MARKET ANALYSIS\src\` — старая система, используй как reference
- ТЗ V10.0-r1, раздел 1.9 (Schema Layer) и раздел 1.4 (Data Quality Gates)

---

## Что создать

### Файл 1: `ENGINE/schema_validator.py`

Модуль валидации JSON объектов по схемам. Используется всеми модулями системы для проверки входящих и исходящих данных.

**Требования:**
- Загружает схемы из `SCHEMAS/`
- Метод `validate(obj, schema_name)` — возвращает `(bool, list[str])` — результат и список ошибок
- Кэширует загруженные схемы
- Логирует ошибки валидации в `LAYER_H_INTERFACE/logs/schema_validation.log`
- При ошибке не бросает исключение — возвращает `(False, errors)`

### Файл 2: `ENGINE/data_quality_gates.py`

6 последовательных проверок качества данных. Запускается на каждом входящем OHLCV snapshot перед попаданием в Feature Store.

**6 проверок (по порядку):**

| Gate | Название | Логика | failure_mode |
|------|----------|--------|--------------|
| 1 | Market Integrity | Нет аномальных ценовых скачков (>30% за 1 свечу) | block |
| 2 | Volume Anomaly | Объём в пределах 10× от rolling average за 20 периодов | warn |
| 3 | Price Continuity | Нет gaps — цена открытия ≈ цене закрытия предыдущей свечи (допуск 5%) | degrade |
| 4 | Timestamp Validation | Временные метки монотонно возрастают, нет дубликатов | block |
| 5 | Source Reliability | trust_score источника из trust_registry.json ≥ 0.3 | degrade |
| 6 | Staleness Check | Данные не старше stale_cache_ttl из `CONFIG/stale_data_policy.json` | block → stale_cache fallback |

**Правила обработки failure_mode:**
- `block` — данные не проходят дальше. При Gate 1 и 4: полная блокировка. При Gate 6: активируется Stale Cache Policy (данные берутся из последнего валидного snapshot с пометкой `data_stale=True`, `uncertainty_penalty=+0.10`)
- `warn` — данные проходят с пометкой `quality_flag="degraded"`, penalty -0.05 к confidence
- `degrade` — данные проходят с пометкой `quality_flag="degraded"`, penalty -0.03 к confidence

**Структура результата каждого gate:**
```python
{
    "gate_id": 1,
    "gate_name": "market_integrity",
    "passed": True/False,
    "failure_mode": "block"/"warn"/"degrade",
    "penalty": 0.0,  # применённый penalty к confidence
    "data_stale": False,
    "message": "..."
}
```

**Итоговый результат всех 6 gates:**
```python
{
    "symbol": "BTCUSDT",
    "timestamp": "...",
    "all_passed": True/False,
    "blocked": False,
    "data_stale": False,
    "total_penalty": 0.0,  # сумма всех penalties
    "quality_flag": "ok"/"degraded",
    "gates": [...]  # результаты каждого gate
}
```

Логировать каждый запуск в `LAYER_B_DATA/quality_logs/gates_YYYY-MM-DD.log`

### Файл 3: `SCHEMAS/ohlcv_candle.json`

JSON Schema для одной OHLCV свечи:
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["symbol", "timestamp", "open", "high", "low", "close", "volume"],
  "properties": {
    "symbol": {"type": "string"},
    "timestamp": {"type": "integer"},
    "open": {"type": "number", "minimum": 0},
    "high": {"type": "number", "minimum": 0},
    "low": {"type": "number", "minimum": 0},
    "close": {"type": "number", "minimum": 0},
    "volume": {"type": "number", "minimum": 0},
    "quality_flag": {"type": "string", "enum": ["ok", "degraded"]},
    "data_stale": {"type": "boolean"}
  }
}
```

### Файл 4: `SCHEMAS/forecast_output.json`

JSON Schema для выходного объекта прогноза (используется в Tasks 21+):
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["forecast_id", "symbol", "direction", "confidence", "u_low", "u_high", "horizon_hours", "created_at"],
  "properties": {
    "forecast_id": {"type": "string"},
    "symbol": {"type": "string"},
    "direction": {"type": "string", "enum": ["UP", "DOWN", "NEUTRAL"]},
    "confidence": {"type": "number", "minimum": 0, "maximum": 1},
    "u_low": {"type": "number", "minimum": 0, "maximum": 1},
    "u_high": {"type": "number", "minimum": 0, "maximum": 1},
    "horizon_hours": {"type": "integer", "enum": [1, 4, 24]},
    "regime": {"type": "string", "enum": ["R1", "R2", "R3", "R4", "R5", "R6"]},
    "shock_score": {"type": "number", "minimum": 0, "maximum": 1},
    "data_stale": {"type": "boolean"},
    "quality_flag": {"type": "string", "enum": ["ok", "degraded"]},
    "created_at": {"type": "string"},
    "determinism_hash": {"type": "string"}
  }
}
```

### Файл 5: `SCHEMAS/pattern.json`

JSON Schema для торгового паттерна:
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["pattern_id", "name", "status", "valid_in_regimes", "confirmed_cases"],
  "properties": {
    "pattern_id": {"type": "string"},
    "name": {"type": "string"},
    "status": {"type": "string", "enum": ["testing", "candidate", "confirmed", "rejected", "overfit", "unstable"]},
    "valid_in_regimes": {"type": "array", "items": {"type": "string"}},
    "confirmed_cases": {"type": "integer", "minimum": 0},
    "total_cases": {"type": "integer", "minimum": 0},
    "oos_performance": {"type": "number"},
    "base_weight": {"type": "number", "minimum": 0, "maximum": 1},
    "orthogonalized_weight": {"type": "number", "minimum": 0, "maximum": 1},
    "pattern_family_id": {"type": "string"},
    "axiom_proxy": {"type": "boolean"},
    "epistemic_status": {"type": "string", "enum": ["direct", "approximate", "uncertain"]}
  }
}
```

---

## Обновить после выполнения

В `CONFIG/component_status.json` обновить:
```json
"schema_layer": {"status": "ready", "updated_at": "<timestamp>", "notes": "6 schemas + validator"},
"data_quality_gates": {"status": "ready", "updated_at": "<timestamp>", "notes": "6 gates, stale cache fallback"}
```

---

## Критерии готовности

1. `ENGINE/schema_validator.py` загружает схемы и валидирует объекты
2. `ENGINE/data_quality_gates.py` прогоняет все 6 gates на тестовом OHLCV наборе
3. Gate 6 при stale данных активирует fallback (не блокирует, а помечает `data_stale=True`)
4. Повторный прогон тех же данных даёт идентичный результат (детерминизм)
5. Все 3+ схемы в `SCHEMAS/` валидируют корректные объекты без ошибок

---

## Тест после выполнения

```python
import sys
sys.path.insert(0, r'C:\КОДИНГ\MARKET ANALYSIS\MARKET_MIND')

from ENGINE.schema_validator import SchemaValidator
from ENGINE.data_quality_gates import DataQualityGates

# Test 1: Schema validation
validator = SchemaValidator()
candle = {
    "symbol": "BTCUSDT", "timestamp": 1700000000000,
    "open": 45000.0, "high": 45500.0, "low": 44800.0,
    "close": 45200.0, "volume": 1234.5
}
ok, errors = validator.validate(candle, "ohlcv_candle")
assert ok, f"Schema validation failed: {errors}"
print("✅ Schema validator OK")

# Test 2: Quality gates — clean data
gates = DataQualityGates()
candles = [
    {"symbol": "BTCUSDT", "timestamp": 1700000000, "open": 45000, "high": 45500,
     "low": 44800, "close": 45200, "volume": 1234, "source": "Binance"},
    {"symbol": "BTCUSDT", "timestamp": 1700003600, "open": 45200, "high": 45600,
     "low": 45100, "close": 45400, "volume": 1100, "source": "Binance"},
]
result = gates.run(candles, symbol="BTCUSDT")
assert result["all_passed"] == True
assert result["blocked"] == False
print("✅ Quality gates OK — clean data passes")

# Test 3: Gate 1 — price spike detection
bad_candles = [
    {"symbol": "BTCUSDT", "timestamp": 1700000000, "open": 45000, "high": 45500,
     "low": 44800, "close": 45200, "volume": 1234, "source": "Binance"},
    {"symbol": "BTCUSDT", "timestamp": 1700003600, "open": 45200, "high": 90000,
     "low": 45100, "close": 88000, "volume": 1100, "source": "Binance"},  # +95% spike
]
result = gates.run(bad_candles, symbol="BTCUSDT")
assert result["blocked"] == True
print("✅ Gate 1 correctly blocks price spike")

print("\n✅ Задача 2 выполнена. Schema Layer + Data Quality Gates готовы.")
```

---

## Примечания

- Используй `jsonschema` библиотеку для валидации (`pip install jsonschema`)
- Stale Cache Policy параметры читай из `CONFIG/stale_data_policy.json`
- Trust registry читай из `LAYER_C_KNOWLEDGE/trust_system/trust_registry.json`
- Все пути относительно `C:\КОДИНГ\MARKET ANALYSIS\MARKET_MIND\`
- Совместимость с Python 3.8+
