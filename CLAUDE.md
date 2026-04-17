# CRYPTO INTELLIGENCE SYSTEM V10.0-r1

**Система прогнозирования движения криптовалют с объяснением, calibrated uncertainty и самокоррекцией**

## Архитектура проекта

Это профессиональная Research Operating System для криптовалютного рынка с 8-слойной архитектурой:

### 🏗️ Структура MARKET_MIND
```
MARKET_MIND/
├── ENGINE/                     # Ядро системы
├── SCHEMAS/                    # JSON схемы валидации
├── CONFIG/                     # Конфигурационные файлы
├── LAYER_A_RESEARCH/          # Исследования и эксперименты
├── LAYER_B_DATA/              # Данные и feature store
├── LAYER_C_KNOWLEDGE/         # База знаний и доверие
├── LAYER_D_MODEL/             # ML модели и предсказания
├── LAYER_E_VALIDATION/        # Бэктестинг и валидация
├── LAYER_F_FEEDBACK/          # Обратная связь и коррекция
├── LAYER_G_NEWS/              # Новости и sentiment
└── LAYER_H_INTERFACE/         # API и логи
```

## Ключевые компоненты (3/30 готовы)

### ✅ Готовые компоненты
- **initialize_system** - инициализация всей структуры
- **schema_layer** - валидация JSON объектов (3 схемы + validator)
- **data_quality_gates** - 6 проверок качества данных

### 🔧 В разработке
27 компонентов ожидают реализации согласно техническому заданию V10.0-r1

## Технические особенности

### Data Quality Gates (6 проверок)
1. **Market Integrity** - блокирует скачки >30%
2. **Volume Anomaly** - предупреждает об аномалиях объёма
3. **Price Continuity** - проверяет gaps >5%
4. **Timestamp Validation** - монотонность временных меток
5. **Source Reliability** - доверие к источнику ≥0.3
6. **Staleness Check** - активирует stale cache при устаревших данных

### Математическая модель
- **Two-transaction model** (Tx_Forecast / Tx_Feedback)
- **Conformal UQ** - uncertainty quantification
- **6 режимов работы** (R1-R6): Normal, Degraded, Soft/Hard Brake, Recovery, Stale
- **Shock Score + Emergency Brake**
- **Fast Lane** ≤200ms для критических операций

### Система доверия
- Trust registry с источниками данных
- Evidence Grading (детерминированный)
- 4-контурный Trust Manager

## Конфигурация

### MCP Integration (Claude Desktop)
Система интегрирована с Claude через MCP серверы:
- `filesystem` - доступ к файловой системе
- `crypto-intelligence-system` - кастомные инструменты CIS

### Разрешения Claude
```json
{
  "permissions": {
    "allow": [
      "Bash(pip install:*)",
      "Bash(python -c:*)"
    ]
  }
}
```

## Стек технологий
- **Python 3.8+** (основной язык)
- **jsonschema** - валидация данных
- **Node.js** - MCP сервер
- **JSON** - конфигурация и схемы
- **Git** - версионирование

## Принципы разработки
- **Детерминизм** - воспроизводимые результаты
- **Idempotency** - безопасное повторное выполнение
- **Fail-safe** - graceful degradation при ошибках
- **Stale cache fallback** - работа с устаревшими данными
- **Uncertainty quantification** - калиброванная неопределённость

## Задачи и статус

### Активные задачи
- TASKS/ACTIVE/ - пуста (все выполнены)

### Завершённые задачи  
- TASKS/COMPLETED/ - 3 задачи выполнены

### Следующие этапы
Реализация оставшихся 27 компонентов согласно приоритетам ТЗ V10.0-r1

---

**Версия:** V10.0-r1  
**Статус:** 3 из 30 компонентов готовы  
**Последнее обновление:** 2026-04-17