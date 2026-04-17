# 📋 TASK MANAGEMENT SYSTEM

## Структура папок для задач

```
TASKS/
├── ACTIVE/           # Активные задачи (файлы .md с ТЗ)
├── COMPLETED/        # Завершенные задачи (архив)
├── TEMPLATES/        # Шаблоны задач
└── README.md         # Этот файл

ENGINE/
├── scripts/          # Исполняемые скрипты задач
├── outputs/          # Результаты выполнения
└── logs/             # Логи выполнения

HISTORY/
├── task_log.json     # История всех задач
├── execution_log/    # Логи выполнения по датам
└── results/          # Архив результатов
```

## Workflow для задач

### 1. Создание задачи
```bash
# Создаем файл задачи
TASKS/ACTIVE/task_001_initialize_system.md
```

### 2. Обработка с Claude Code
```bash
# В Claude Code:
cd C:\КОДИНГ\MARKET ANALYSIS
# Передаем файл задачи
# Claude анализирует и создает:
ENGINE/scripts/task_001_initialize_system.py
```

### 3. Выполнение
```bash
# Claude запускает:
python ENGINE/scripts/task_001_initialize_system.py
```

### 4. Архивация
```bash
# После завершения:
TASKS/ACTIVE/task_001_*.md → TASKS/COMPLETED/
ENGINE/outputs/task_001_* → HISTORY/results/
```

## Преимущества такой структуры

- ✅ **История всех задач** в одном месте
- ✅ **Версионирование** через git
- ✅ **Логи выполнения** для отладки
- ✅ **Архивация результатов**
- ✅ **Шаблоны** для типовых задач
- ✅ **Интеграция с Claude Code**