# Crypto Intelligence System — FINAL SPEC (V5)

## Статус
Финальная версия ТЗ после интеграции:
- TRIZ
- Systems Thinking
- First Principles
- Scientific Method
- OODA Loop
- Control Theory

---

# 1. Главная функция системы

Система предназначена для:

**Прогнозирования движения цены выбранной пользователем криптовалюты**
с указанием:
- направления (up / down / neutral)
- горизонта (1h / 4h / 24h / etc)
- силы движения (weak / moderate / strong)
- confidence (0–1)
- типа движения (trend / reversal / pullback / consolidation)
- объяснения (explanation)
- основания (audit trail)

---

# 2. Полный цикл системы (OODA)

Observe → Orient → Decide → Act → Feedback

## Реализация:

1. Observe
- market data
- on-chain
- macro
- news

2. Orient
- context_orchestrator
- knowledge_base
- regime_detector
- trust system

3. Decide
- model_builder (агрегация сигналов)

4. Act
- forecast generation

5. Feedback
- prediction_tracker
- validation_engine
- pattern_decay

---

# 3. Архитектура

## Layer 1 — Data
- feature_store
- raw/processed data

## Layer 2 — Context
- context_orchestrator
- knowledge_base
- trust

## Layer 3 — Signals
- patterns
- negative knowledge
- features

## Layer 4 — Model
- signal aggregation
- weighting
- filtering

## Layer 5 — Output
- forecast
- explanation

## Layer 6 — Feedback
- tracking
- validation
- learning

---

# 4. Forecast Pipeline

User selects asset →  
Context built →  
Signals extracted →  
Model aggregates →  
Forecast generated →  
Result tracked →  
System updated

---

# 5. Основные модули

## Core
- hypothesis_formalizer
- experiment_registry
- pattern_registry
- negative_knowledge_manager

## Data
- feature_builder
- data_quality_monitor

## Intelligence
- knowledge_search
- news_scorer
- trust_manager

## Model
- model_builder
- baseline_engine

## Validation
- validation_engine
- pattern_decay_monitor

## Feedback
- prediction_tracker
- decision_audit

---

# 6. Научные правила

Обязательно:

- OOS validation
- minimum sample size
- baseline comparison
- reproducibility
- evidence grading

---

# 7. TRIZ слой

## contradictions_registry
фиксирует противоречия системы

## resource_map
используем:
- ошибки
- данные
- негативные паттерны

---

# 8. Control System

## Метрики:
- prediction error
- model drift
- pattern performance

## Реакция:
- изменение весов
- удаление слабых паттернов
- усиление сильных

---

# 9. Model Logic (First Principles)

Forecast = f(
  patterns,
  negative_filters,
  regime,
  macro,
  onchain,
  news
)

---

# 10. UI

Главная вкладка:
🎯 Forecast

Остальные:
- Patterns
- Experiments
- Knowledge
- News
- Model
- Audit

---

# 11. Критерии готовности системы

Система считается работающей если:

1. Делает прогноз по выбранному активу  
2. Прогноз имеет explanation  
3. Есть tracking результатов  
4. Есть обновление модели  
5. Есть защита от ложных паттернов  

---

# 12. Финальная оценка

Архитектура: 10/10  
Реализуемость: 7.5/10  
Уникальность: 10/10  

---

# 13. Итог

Это:

- не бот  
- не чат  
- не анализатор  

Это:

**адаптивная система прогнозирования цены с научной валидацией и самообучением**

