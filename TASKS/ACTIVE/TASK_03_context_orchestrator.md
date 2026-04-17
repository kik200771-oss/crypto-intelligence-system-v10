# ЗАДАЧА 3 — CONTEXT ORCHESTRATOR [Этап 1]

## Статус предыдущих задач
- ✅ initialize_system — ready
- ✅ schema_layer — ready  
- ✅ data_quality_gates — ready

## Рабочая директория
`C:\CODE\MARKET ANALYSIS\MARKET_MIND\`

---

## Контекст

Context Orchestrator — центральный диспетчер системы. Он получает запрос на прогноз и собирает все необходимые входы для Model Core:
- Параллельно вызывает AXM Guard и Prior Manager (не последовательно)
- Управляет таймаутами для каждого входа отдельно
- При сбое любого входа активирует failover — не блокирует весь прогноз
- Возвращает собранный контекст с пометками о качестве

Без Context Orchestrator Model Core не получит правильно собранный контекст.

**Ссылки:** ТЗ V10.0-r1 раздел 1.4 (Input Assembly Contract), CONFIG/timeframe_core.json, CONFIG/stale_data_policy.json

---

## Что создать

### Файл: `ENGINE/context_orchestrator.py`

**Класс `ContextOrchestrator`** с методом `orchestrate(request)`.

**Входной объект request:**
```python
{
    "symbol": "ETHUSDT",        # торгуемая пара
    "timeframe": "4h",          # таймфрейм
    "horizon_hours": 4,         # горизонт прогноза
    "btc_context": True,        # включать BTC как macro
    "request_id": "uuid"        # уникальный ID запроса
}
```

**Что собирает оркестратор (6 входов):**

| Вход | Таймаут Fast Lane | При timeout | Описание |
|------|-------------------|-------------|----------|
| Feature Snapshot | 100ms | BLOCK → abort | Обязательный вход |
| Validated Patterns | 150ms | BLOCK → abort | Обязательный вход |
| Regime Context | 80ms | DEGRADE → default=sideways, penalty -0.05 | Желательный |
| Prior Snapshot | 200ms | SKIP → prior_snapshot_id=null, context_degraded=True | Опциональный |
| Timeframe Context | 80ms | DEGRADE → default Standard Core | Опциональный |
| change_id | 50ms | SKIP → null (baseline mode) | Опциональный |

**Правила:**
- AXM Guard и Prior Manager вызываются **параллельно** через `concurrent.futures.ThreadPoolExecutor`
- Таймаут для каждого входа — **отдельный**, не общий
- Если BLOCK-вход не пришёл в срок → `context_degraded=True`, прогноз помечается `ABORTED`
- SKIP и DEGRADE входы не блокируют старт агрегации
- BTC данные всегда добавляются как macro_context если `btc_context=True`

**Failover contract:**
```python
# При timeout любого BLOCK входа:
return {
    "status": "ABORTED",
    "reason": f"timeout_{input_name}",
    "context_degraded": True,
    "request_id": request["request_id"]
}
```

**Выходной объект при успехе:**
```python
{
    "request_id": "uuid",
    "symbol": "ETHUSDT",
    "timeframe": "4h",
    "horizon_hours": 4,
    "status": "OK",  # или "DEGRADED" если были DEGRADE/SKIP
    "context_degraded": False,
    "total_penalty": 0.0,  # сумма penalties от degraded входов
    "feature_snapshot": {...},
    "validated_patterns": [...],
    "regime_context": {"regime": "sideways", "confidence": 0.75},
    "prior_snapshot": {...},  # или null
    "timeframe_context": {...},
    "change_id": null,  # или строка
    "btc_macro": {...},  # BTC данные как macro индикатор
    "axm_guard_result": {...},
    "assembled_at": "ISO timestamp",
    "assembly_latency_ms": 145
}
```

**Заглушки для ещё не реализованных модулей:**
Поскольку Feature Store, Pattern Registry, Prior Manager ещё не реализованы — создай заглушки которые возвращают тестовые данные. Это позволит оркестратору работать сейчас и легко подключить реальные модули позже.

```python
def _get_feature_snapshot(self, symbol, timeframe):
    """Заглушка — будет заменена Feature Store (Task 13)"""
    return {
        "symbol": symbol,
        "timeframe": timeframe,
        "rsi": 45.2,
        "macd": 0.001,
        "volume_ratio": 1.2,
        "stub": True
    }

def _get_validated_patterns(self, symbol, regime):
    """Заглушка — будет заменена Pattern Registry (Task 7)"""
    return []

def _get_regime_context(self, symbol):
    """Заглушка — будет заменена Regime Detector (Task 14)"""
    return {"regime": "sideways", "confidence": 0.60, "stub": True}

def _get_prior_snapshot(self):
    """Заглушка — будет заменена Prior Manager (Task 29)"""
    return None

def _get_btc_macro(self):
    """Заглушка — будет заменена Feature Store BTC (Task 13)"""
    return {
        "symbol": "BTCUSDT",
        "trend": "neutral",
        "dominance": 52.3,
        "stub": True
    }

def _run_axm_guard(self, context):
    """Заглушка — будет заменена AXM Guard (Task 29)"""
    return {"passed": True, "violations": [], "stub": True}
```

**Логирование:**
- Каждый запрос логировать в `LAYER_H_INTERFACE/logs/orchestrator.log`
- Формат: `[timestamp] request_id | symbol | status | latency_ms | degraded_inputs`

---

## Обновить после выполнения

`CONFIG/component_status.json`:
```json
"context_orchestrator": {
    "status": "ready",
    "updated_at": "<timestamp>",
    "notes": "6 inputs, parallel AXM+Prior, failover contract"
}
```

---

## Критерии готовности

1. `ContextOrchestrator.orchestrate()` возвращает корректный объект контекста
2. AXM Guard и Prior Manager вызываются параллельно (не последовательно)
3. При симуляции timeout BLOCK-входа возвращает `status: ABORTED`
4. При симуляции timeout DEGRADE-входа — продолжает с penalty
5. BTC macro всегда присутствует в контексте
6. Латентность сборки контекста логируется

---

## Тест после выполнения

```python
import sys
sys.path.insert(0, r'C:\CODE\MARKET ANALYSIS\MARKET_MIND')

from ENGINE.context_orchestrator import ContextOrchestrator

orch = ContextOrchestrator()

# Test 1: Нормальный запрос
request = {
    "symbol": "ETHUSDT",
    "timeframe": "4h", 
    "horizon_hours": 4,
    "btc_context": True,
    "request_id": "test-001"
}
result = orch.orchestrate(request)
assert result["status"] in ["OK", "DEGRADED"]
assert result["btc_macro"] is not None
assert "assembly_latency_ms" in result
print(f"✅ Test 1 OK: status={result['status']}, latency={result['assembly_latency_ms']}ms")

# Test 2: BTC как macro всегда присутствует
assert result["btc_macro"]["symbol"] == "BTCUSDT"
print("✅ Test 2 OK: BTC macro present")

# Test 3: Параллельность — latency должна быть меньше суммы таймаутов
assert result["assembly_latency_ms"] < 1000
print(f"✅ Test 3 OK: parallel execution confirmed ({result['assembly_latency_ms']}ms)")

print("\n✅ Задача 3 выполнена. Context Orchestrator готов.")
```
