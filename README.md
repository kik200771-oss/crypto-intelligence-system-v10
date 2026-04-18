# Crypto Intelligence System V10.0-r1

Research Operating System для крипторынка с calibrated uncertainty и самокоррекцией.

## Канонические документы

- [ТЗ V10.0-r1](TZ/CIS_TZ_V10_0_r1.md)
- [Математическая модель v6.3](TZ/CIS_V10_Mathematical_Model_v63_COMPLETE.md)
- [Схемы V5](TZ/CIS_V10_Combined_Schematics_V5.md)

## Структура

```
MARKET_MIND/                  # канонический проект (единственный)
├── ENGINE/                   # модули системы (.py)
├── SCHEMAS/                  # JSON-схемы валидации
├── CONFIG/                   # конфиги + session_state.json
├── LAYER_A_RESEARCH/         # паттерны, гипотезы, эксперименты, негативы
├── LAYER_B_DATA/             # features, quality_logs, onchain, macro
├── LAYER_C_KNOWLEDGE/        # KB, trust_system
├── LAYER_D_MODEL/            # models, predictions, shock_log
├── LAYER_E_VALIDATION/       # backtest, validation_reports
├── LAYER_F_FEEDBACK/         # prediction_records, outcomes, drift_log
├── LAYER_G_NEWS/             # новости и sentiment
├── LAYER_H_INFRA/            # user_profile, backup, api, logs
└── meta/                     # how_to_read_me.md, index.json

TZ/                           # канонические документы
TASKS/                        # задачи от Claude Opus
├── ACTIVE/                   # активные
├── COMPLETED/                # завершённые (архив)
└── NOTES/                    # идеи, находки

scripts/                      # вспомогательные скрипты
```

## Workflow

- Задачи формирует Claude Opus (архитектор) — файлы `TASKS/ACTIVE/TASK_NN_*.md`
- Claude Code исполняет задачи строго по ТЗ (см. [CLAUDE.md](CLAUDE.md))
- Архитектор ревьюит через периодические zip-аудиты

## Статус

См. [MARKET_MIND/CONFIG/component_status.json](MARKET_MIND/CONFIG/component_status.json).

## Prerequisites

- Python 3.8+
- Git
- `pip install -r requirements.txt`

## Дисклеймер

Система для исследовательских целей. Не является финансовой рекомендацией.
Никакого автоматического трейдинга система не делает.