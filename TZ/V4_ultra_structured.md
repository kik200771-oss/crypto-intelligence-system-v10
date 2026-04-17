# Crypto Intelligence System — V4 Ultra-Structured (Claude Code)

## Формат: task-driven execution spec

---

## ЗАДАЧА 1 — ИНИЦИАЛИЗАЦИЯ СИСТЕМЫ

**Файл:** ENGINE/initialize_system.py  

**Что создать:**
- Полную структуру директорий V4
- Все базовые JSON шаблоны:
  - session_state.json
  - system_manifest.json
  - index.json
  - component_status.json
- Папки CORE, DATA, KNOWLEDGE_BASE, TRUST, ENGINE, UI, CONFIG, BACKUP

**Критерии готовности:**
- Все папки существуют
- Все JSON валидны
- Скрипт можно запускать повторно без ошибок (idempotent)

**Зависимости:**
- pathlib
- json
- os

**Статус наследия:**
- ОСНОВА из v1 (initialize_mind.py)
- РАСШИРЕНО до полной системы из v3
- СТРУКТУРИРОВАНО в V4

---

## ЗАДАЧА 2 — SCHEMA LAYER

**Файл:** ENGINE/schema_validator.py  

**Что создать:**
- Валидатор JSON по схемам
- Схемы:
  - hypothesis_schema.json
  - pattern_schema.json
  - experiment_schema.json
  - prediction_schema.json

**Критерии готовности:**
- Любой объект проходит validate() перед сохранением
- Ошибка выбрасывается при несоответствии

**Зависимости:**
- jsonschema

**Статус наследия:**
- НОВОЕ в V4
- ЗАМЕНЯЕТ свободные JSON из v1-v3

---

## ЗАДАЧА 3 — CONTEXT ORCHESTRATOR

**Файл:** ENGINE/context_orchestrator.py  

**Что создать:**
- build_task_context()
- Логика выбора релевантного контекста

**Критерии готовности:**
- Контекст < 8000 токенов
- Включает только релевантные данные

**Зависимости:**
- session_state
- patterns
- hypotheses

**Статус наследия:**
- ЗАМЕНА ContextLoader (v1-v3)

---

## ЗАДАЧА 4 — HYPOTHESIS FORMALIZER

**Файл:** ENGINE/hypothesis_formalizer.py  

**Что создать:**
- Преобразование текста в формальную гипотезу
- Выделение:
  - условия
  - инструмента
  - таймфрейма
  - expected outcome

**Критерии готовности:**
- Каждая гипотеза имеет formal_statement

**Зависимости:**
- Claude API

**Статус наследия:**
- РАСШИРЕНИЕ save_hypothesis (v1)

---

## ЗАДАЧА 5 — EXPERIMENT REGISTRY

**Файл:** ENGINE/experiment_registry.py  

**Что создать:**
- Реестр экспериментов
- CRUD операции

**Критерии готовности:**
- Любая гипотеза связана с экспериментами

**Зависимости:**
- schema_validator

**Статус наследия:**
- НОВОЕ в V4

---

## ЗАДАЧА 6 — BACKTESTER

**Файл:** ENGINE/backtester.py  

**Что создать:**
- run_backtest()
- calculate metrics

**Критерии готовности:**
- Возвращает:
  - hit_rate
  - sharpe
  - drawdown

**Зависимости:**
- feature_store

**Статус наследия:**
- СОХРАНЁН из v1/v3

---

## ЗАДАЧА 7 — VALIDATION ENGINE

**Файл:** ENGINE/validation_engine.py  

**Что создать:**
- Проверка паттернов:
  - sample size
  - out-of-sample
  - baseline comparison

**Критерии готовности:**
- pattern не может стать confirmed без validate()

**Зависимости:**
- backtester
- experiment_registry

**Статус наследия:**
- НОВОЕ в V4

---

## ЗАДАЧА 8 — FEATURE STORE

**Файл:** ENGINE/feature_builder.py  

**Что создать:**
- единый набор признаков
- сохранение snapshot

**Критерии готовности:**
- все модули используют один источник данных

**Зависимости:**
- pandas
- binance API

**Статус наследия:**
- НОВОЕ в V4
- ОБЪЕДИНЯЕТ data_cache (v1) + data (v3)

---

## ЗАДАЧА 9 — KNOWLEDGE BASE

**Файл:** ENGINE/knowledge_ingester.py  
**Файл:** ENGINE/knowledge_search.py  

**Что создать:**
- ingestion PDF, YouTube, web
- semantic search

**Критерии готовности:**
- поиск возвращает релевантные chunks

**Зависимости:**
- chromadb
- sentence-transformers

**Статус наследия:**
- СОХРАНЁН из v2/v3

---

## ЗАДАЧА 10 — NEGATIVE KNOWLEDGE

**Файл:** ENGINE/negative_knowledge_manager.py  

**Что создать:**
- сохранение негативных гипотез
- кластеризация

**Критерии готовности:**
- негативные идеи не теряются

**Зависимости:**
- insight_saver

**Статус наследия:**
- СОХРАНЁН из v3

---

## ЗАДАЧА 11 — PATTERN DECAY

**Файл:** ENGINE/pattern_decay_monitor.py  

**Что создать:**
- мониторинг деградации

**Критерии готовности:**
- паттерны переходят в decayed при ухудшении

**Зависимости:**
- backtester

**Статус наследия:**
- СОХРАНЁН из v3

---

## ЗАДАЧА 12 — MODEL BUILDER

**Файл:** ENGINE/model_builder.py  

**Что создать:**
- rule-based ensemble model

**Критерии готовности:**
- predict() возвращает направление и объяснение

**Зависимости:**
- patterns
- negative knowledge
- regime

**Статус наследия:**
- СОХРАНЁН из v2/v3
- ОТЛОЖЕН запуск до накопления данных

---

## ЗАДАЧА 13 — STREAMLIT UI

**Файл:** UI/streamlit_app.py  

**Что создать:**
- 8 вкладок:
  - Market
  - Chat
  - Experiments
  - Patterns
  - KB
  - News
  - Model
  - Decay

**Критерии готовности:**
- полный workflow доступен через UI

**Зависимости:**
- streamlit
- plotly

**Статус наследия:**
- СОХРАНЁН из v1-v3
- ПЕРЕСТРОЕН под pipeline

---

## ЗАДАЧА 14 — BACKUP

**Файл:** ENGINE/backup_manager.py  

**Что создать:**
- daily backup
- export report

**Критерии готовности:**
- создаётся архив системы

**Зависимости:**
- zipfile

**Статус наследия:**
- СОХРАНЁН из v3

---

## ЗАДАЧА 15 — OPTIONAL API

**Файл:** ENGINE/api_server.py  

**Что создать:**
- FastAPI endpoints

**Критерии готовности:**
- GET /predict работает

**Зависимости:**
- fastapi

**Статус наследия:**
- НЕ УДАЛЁН
- ПЕРЕНЕСЁН на поздний этап

---

# ИТОГ

Это execution-версия V4 для Claude Code:
- каждая задача изолирована
- есть критерии готовности
- есть связь с предыдущими версиями
