# Crypto Intelligence System — ТЗ v4.0
## Консолидированная версия с полной преемственностью v1 → v2 → v3 → v4

**Статус:** рабочая консолидированная версия  
**Дата:** Апрель 2026  
**Формат:** master-spec в Markdown  
**Принцип:** ничего не удаляется бесследно

---

# 0. Правило ведения ТЗ в V4

## 0.1 Базовый принцип

Это ТЗ ведётся по принципу **полной исторической преемственности**:

- ни один важный модуль, идея, этап, сущность или сценарий из v1, v2, v3 не исчезает без следа;
- если что-то убрано из активного объёма работ, оно **не удаляется**, а получает явную пометку:
  - **отложено**;
  - **перенесено на другой этап**;
  - **заменено другим механизмом**;
  - **сужено по объёму**;
  - **сохранено как опциональный модуль**;
- для каждого такого элемента указывается:
  - из какой версии он пришёл;
  - какой у него был исходный смысл;
  - что с ним происходит в V4.

## 0.2 Что такое V4

V4 — это не “новая версия, которая всё переписала”.  
V4 — это **собранная и инженерно нормализованная версия всех предыдущих ТЗ**, в которой:

- сохраняется философия v1;
- сохраняется двухслойная когнитивная модель v2;
- сохраняются самые сильные расширения v3;
- вводится строгая инженерная рамка:
  - схемы данных;
  - журнал экспериментов;
  - единый feature store;
  - валидация;
  - трассировка решений;
  - оркестрация контекста.

---

# 1. Эволюция проекта по версиям

## 1.1 Версия v1.0 — MARKET_MIND как когнитивная память

### Суть версии
v1 задаёт базовое ядро системы:

- Streamlit интерфейс;
- чат с Claude;
- MARKET_MIND как память между сессиями;
- контекст-загрузчик;
- автосохранение выводов;
- бэктест паттернов;
- единый запуск системы.

### Сильные стороны v1
- очень хороший MVP-контур;
- быстро даёт практическую полезность;
- уже есть замкнутый цикл:
  - гипотеза;
  - анализ;
  - сохранение;
  - тест;
  - накопление паттернов.

### Что сохраняется в V4 из v1
Сохраняется **почти всё ядро**:
- Streamlit UI;
- MARKET_MIND как центральная память;
- context loading / session continuity;
- hypotheses;
- patterns;
- backtests;
- session log;
- start script;
- работа поверх существующего проекта.

### Что в V4 меняется относительно v1
- `context_loader` развивается в **context_orchestrator**;
- свободные JSON-структуры заменяются на **схемы данных**;
- автосохранение выводов включается в более широкий **research pipeline**;
- бэктест становится не просто утилитой, а частью **validation engine**.

### Статус элементов v1 в V4
| Элемент v1 | Статус в V4 | Комментарий |
|---|---|---|
| MARKET_MIND | сохранён | остаётся ядром системы |
| Streamlit UI | сохранён и расширен | теперь UI строится вокруг research pipeline |
| ContextLoader | заменён | заменён на Context Orchestrator |
| InsightSaver | сохранён и расширен | теперь работает вместе с experiment registry |
| Backtester | сохранён и усилен | теперь связан с formal pattern logic |
| start_system.bat | сохранён | остаётся обязательным модулем запуска |

---

## 1.2 Версия v2.0 — двухслойная когнитивная система

### Суть версии
v2 делает главный концептуальный скачок:

- появляется **два слоя**:
  - MARKET_MIND — наши открытия;
  - KNOWLEDGE_BASE — классические знания;
- появляется сравнение:
  - совпадает;
  - противоречит;
  - новое;
- добавляется RAG-поиск по книгам, YouTube, research, web;
- начинает формироваться идея живой модели.

### Главный вклад v2
Именно v2 делает проект уникальным:  
система перестаёт быть просто “памятью аналитика” и становится **машиной сопоставления собственных открытий с тем, что уже знает мир**.

### Что сохраняется в V4 из v2
Сохраняется полностью:
- двухслойная архитектура;
- KNOWLEDGE_BASE;
- ingestion PDF/YouTube/web/research;
- semantic search;
- compare with classics;
- verdict layer:
  - aligned / conflicting / novel.

### Что в V4 меняется относительно v2
- сравнение с классикой **не может подтверждать паттерн само по себе**;
- novelty не трактуется как доказательство качества;
- KNOWLEDGE_BASE остаётся слоем контекста и объяснения, а не арбитром прибыльности;
- вводится **trust profile источников** вместо слишком простого единого веса.

### Статус элементов v2 в V4
| Элемент v2 | Статус в V4 | Комментарий |
|---|---|---|
| MARKET_MIND + KNOWLEDGE_BASE | сохранён | это центральная философия проекта |
| Knowledge Ingester | сохранён | входит в ENGINE |
| Knowledge Search | сохранён | используется для контекста и сравнения |
| compare_with_hypothesis | сохранён, уточнён | не подтверждает паттерн без теста |
| Живая модель | сохранена | но перенесена на поздний этап после накопления validated patterns |

---

## 1.3 Версия v3.0 — полная когнитивная платформа

### Суть версии
v3 превращает проект в большую интеллектуальную платформу:

- Negative Knowledge;
- Trust System;
- News Engine;
- On-chain;
- Macro;
- Market Regime;
- Pattern Decay;
- Causality Engine;
- User Profile;
- REST API;
- Backup;
- Live Model.

### Что ценного дала v3
v3 впервые делает систему не просто собирающей знания, а **оценивающей качество, контекст и срок годности знаний**.

### Главный риск v3
v3 слишком быстро расширяет область проекта:  
появляется много сильных идей, но возрастает риск:

- перегрузки архитектуры;
- расползания требований;
- неоднородных сущностей;
- невозможности стабилизировать ядро.

### Что сохраняется в V4 из v3
Сохраняется как активная часть:
- Negative Knowledge;
- Pattern Decay;
- Regime Detection;
- On-chain;
- Macro;
- Trust System;
- News Layer;
- Live Model;
- Backup;
- расширенный UI.

Сохраняется, но **сужается / откладывается**:
- Causality Engine;
- сложный User Profile Engine;
- большой REST API;
- избыточная ручная корректировка trust;
- чрезмерно широкий объём одновременной интеграции.

### Статус элементов v3 в V4
| Элемент v3 | Статус в V4 | Комментарий |
|---|---|---|
| Negative Knowledge | сохранён | одна из ключевых фишек |
| Trust System | сохранён, переработан | вместо одного общего trust — профиль пригодности |
| News Engine | сохранён, упрощён | фокус на relevance и event features |
| On-chain | сохранён | часть Data & Features |
| Macro | сохранён | часть Data & Features |
| Regime Detector | сохранён | обязательный контекстный слой |
| Pattern Decay | сохранён | обязателен |
| Causality Engine | не удалён, отложен | перенесён в поздний этап, заменён временно evidence grading |
| User Profile | не удалён, сужен | базовый профиль остаётся, глубокая аналитика позже |
| REST API | не удалён, отложен | вынесен в опциональную инфраструктуру |
| Backup | сохранён | обязателен |
| Live Model | сохранён | только после стабилизации validated knowledge |

---

# 2. Главная философия V4

Мы строим не просто торговый интерфейс, не торгового бота и не чат с памятью.  
Мы строим **Research Operating System для крипторынка**.

Система должна уметь:

1. принимать идеи;
2. формализовать гипотезы;
3. тестировать их воспроизводимо;
4. сохранять позитивные и негативные результаты;
5. сравнивать выводы с классическими знаниями;
6. отслеживать деградацию знаний;
7. строить объяснимую живую модель только на проверенной базе.

---

# 3. Обязательные инженерные принципы V4

## 3.1 Ничего не подтверждается только LLM
Claude помогает:
- формулировать;
- объяснять;
- сравнивать;
- суммировать;
- кластеризовать идеи.

Но Claude не может:
- единолично подтверждать паттерн;
- присваивать final confidence без теста;
- заменять собой бэктест или validation.

## 3.2 Knowledge Base не равен доказательству
Если идея:
- совпадает с классикой — это полезно;
- противоречит классике — это интересно;
- новая — это ценно.

Но ни одно из этих состояний **не заменяет проверку на данных**.

## 3.3 Negative knowledge так же важно, как positive knowledge
Если гипотеза системно не работает, это не мусор.  
Это защитное знание.

## 3.4 Regime matters
Паттерн без указания режима рынка — неполное знание.

## 3.5 Воспроизводимость важнее красоты
Любой вывод, который нельзя повторить на том же наборе данных тем же правилом, не считается устойчивым знанием.

---

# 4. Архитектура V4

## 4.1 Слои системы

### Слой A — Research Core
Содержит:
- session memory;
- hypotheses;
- experiments;
- patterns;
- negative knowledge;
- model versions;
- prediction tracking.

### Слой B — Data & Features
Содержит:
- OHLCV;
- индикаторы;
- BTC dominance;
- macro;
- on-chain;
- news-derived features;
- regime labels;
- event marks.

### Слой C — Knowledge & Context
Содержит:
- KNOWLEDGE_BASE;
- semantic retrieval;
- comparison with classics;
- source trust profiles.

### Слой D — Interface & Operations
Содержит:
- Streamlit;
- launcher;
- backup;
- reporting;
- позже опционально API.

---

# 5. Полная структура проекта V4

```text
D:\CRYPTO_INTELLIGENCE\

├── CORE\
│   ├── meta\
│   │   ├── how_to_read_me.md
│   │   ├── system_manifest.json
│   │   ├── index.json
│   │   └── session_log.json
│   │
│   ├── state\
│   │   ├── session_state.json
│   │   ├── current_context.json
│   │   └── component_status.json
│   │
│   ├── hypotheses\
│   │   ├── raw\
│   │   ├── formalized\
│   │   ├── active\
│   │   ├── archived\
│   │   └── rejected\
│   │
│   ├── experiments\
│   │   ├── registry\
│   │   ├── results\
│   │   └── reviews\
│   │
│   ├── patterns\
│   │   ├── candidate\
│   │   ├── confirmed\
│   │   ├── rejected\
│   │   ├── decayed\
│   │   └── inverted\
│   │
│   ├── negative_knowledge\
│   │   ├── raw\
│   │   ├── clusters\
│   │   └── insights\
│   │
│   └── models\
│       ├── current\
│       ├── versions\
│       └── predictions_log.json
│
├── DATA\
│   ├── raw\
│   │   ├── binance\
│   │   ├── onchain\
│   │   ├── macro\
│   │   └── news\
│   │
│   ├── processed\
│   │   ├── candles\
│   │   ├── indicators\
│   │   ├── features\
│   │   ├── regime_labels\
│   │   └── event_marks\
│   │
│   ├── cache\
│   └── feature_store\
│
├── KNOWLEDGE_BASE\
│   ├── books\
│   │   ├── raw\
│   │   └── chunks\
│   ├── youtube\
│   │   ├── raw\
│   │   └── chunks\
│   ├── research\
│   │   ├── raw\
│   │   └── chunks\
│   ├── web\
│   │   ├── raw\
│   │   └── chunks\
│   ├── index\
│   └── meta\
│       ├── sources_registry.json
│       └── ingestion_log.json
│
├── TRUST\
│   ├── sources_registry.json
│   ├── trust_history\
│   └── verification_log.json
│
├── ENGINE\
│   ├── schemas\
│   │   ├── hypothesis_schema.json
│   │   ├── pattern_schema.json
│   │   ├── experiment_schema.json
│   │   ├── prediction_schema.json
│   │   └── source_schema.json
│   │
│   ├── initialize_system.py
│   ├── schema_validator.py
│   ├── context_orchestrator.py
│   ├── hypothesis_formalizer.py
│   ├── experiment_registry.py
│   ├── insight_saver.py
│   ├── backtester.py
│   ├── validation_engine.py
│   ├── pattern_registry.py
│   ├── pattern_decay_monitor.py
│   ├── negative_knowledge_manager.py
│   ├── feature_builder.py
│   ├── regime_detector.py
│   ├── knowledge_ingester.py
│   ├── knowledge_search.py
│   ├── news_collector.py
│   ├── news_scorer.py
│   ├── trust_manager.py
│   ├── onchain_collector.py
│   ├── macro_collector.py
│   ├── model_builder.py
│   ├── prediction_tracker.py
│   ├── report_builder.py
│   └── backup_manager.py
│
├── UI\
│   └── streamlit_app.py
│
├── CONFIG\
│   ├── .env
│   ├── .env.example
│   ├── settings.yaml
│   └── source_weights.yaml
│
└── BACKUP\
    ├── daily\
    └── reports\
```

---

# 6. Новый обязательный каркас: схемы данных

## 6.1 Почему это обязательно
Во всех прошлых версиях было много хороших сущностей, но им не хватало жёсткого контрактного слоя.  
V4 делает это обязательным.

Ниже лежат обязательные схемы:
- `hypothesis_schema.json`
- `pattern_schema.json`
- `experiment_schema.json`
- `prediction_schema.json`
- `source_schema.json`

Все файлы, создаваемые системой, должны:
1. соответствовать схеме;
2. валидироваться при сохранении;
3. иметь версию схемы.

## 6.2 Статус относительно прошлых версий
| Элемент | Источник | Статус в V4 |
|---|---|---|
| свободные JSON-структуры | v1/v2/v3 | не удалены, но заменены схемами |
| ручная договорённость о структуре | v1/v2/v3 | заменена формальной валидацией |
| index.json как граф | v1/v2/v3 | сохранён |

---

# 7. Research Pipeline — главный новый стержень V4

## 7.1 Поток работы
```text
raw idea
→ formalized hypothesis
→ experiment design
→ backtest / validation
→ review
→ candidate pattern OR negative knowledge
→ confirmation / rejection / inversion / decay tracking
```

## 7.2 Что это решает
Этот слой закрывает пробел всех прошлых версий:
- не даёт гипотезам “растворяться”;
- не даёт паттернам появляться из воздуха;
- делает research traceable;
- отделяет идею от знания.

## 7.3 Статусы гипотез
- raw
- formalized
- active
- tested
- archived
- rejected

## 7.4 Статусы паттернов
- candidate
- confirmed
- rejected
- decayed
- inverted

---

# 8. Hypothesis Layer

## 8.1 Роль слоя
Каждая идея сначала существует как гипотеза, а не как паттерн.

## 8.2 Форматы хранения
- `CORE/hypotheses/raw/`
- `CORE/hypotheses/formalized/`
- `CORE/hypotheses/active/`
- `CORE/hypotheses/archived/`
- `CORE/hypotheses/rejected/`

## 8.3 Новый модуль
`hypothesis_formalizer.py`

### Назначение
Преобразует сырую идею в формальную гипотезу:
- определяет инструмент;
- определяет таймфрейм;
- выделяет условие;
- выделяет expected outcome;
- помогает перевести мысль в Pattern DSL-совместимую форму.

## 8.4 Статус относительно прошлых версий
| Элемент | Статус |
|---|---|
| save_hypothesis из v1/v3 | сохранён |
| сырая гипотеза как текст из чата | сохранена |
| формализация как отдельный этап | добавлена в V4 |

---

# 9. Experiment Registry

## 9.1 Новый обязательный слой
Это один из ключевых модулей V4.

Модуль: `experiment_registry.py`

## 9.2 Что хранит эксперимент
- какая гипотеза проверялась;
- каким методом;
- на какой версии данных;
- на каком feature snapshot;
- какие были train / test периоды;
- какие метрики получены;
- кто и когда запускал;
- какой итог review.

## 9.3 Зачем он нужен
Без этого система не является research OS.  
Она лишь набор утилит.

## 9.4 Статус относительно прошлых версий
| Элемент | Статус |
|---|---|
| session_log | сохранён |
| backtest_results | сохранён |
| formal experiment registry | новый обязательный слой V4 |

---

# 10. Pattern Layer

## 10.1 Роль паттерна
Паттерн — это не просто идея из чата.  
Паттерн — это формально выраженная закономерность, прошедшая тестирование.

## 10.2 Статусы паттернов
- candidate;
- confirmed;
- rejected;
- decayed;
- inverted.

## 10.3 Pattern DSL
V4 официально вводит исполнимую логику паттернов.

Примеры:

```text
RSI_14(ETHBTC,4h) cross_above 30 -> RETURN(24h) > 0
```

```text
BTC_DOM[-4h] <= -2% & ETHUSDT.prev_4h > 0 => ETHUSDT.next_6h > 0
```

## 10.4 Что это даёт
- устраняет двусмысленность;
- делает паттерн исполнимым;
- позволяет одинаково тестировать;
- позволяет строить модель не по текстам, а по правилам.

## 10.5 Статус относительно прошлых версий
| Элемент | Статус |
|---|---|
| компактная нотация паттернов из v1/v2/v3 | сохранена как источник идеи |
| полуформальная нотация | не удалена, но нормализована |
| executable DSL | новый слой V4 |

---

# 11. Backtesting Layer

## 11.1 Бэктест остаётся обязательным
Модуль: `backtester.py`

Сохраняется из v1 и v3, но теперь интегрируется с:
- Pattern DSL;
- experiment registry;
- validation engine;
- feature store.

## 11.2 Основные функции
- `run_backtest(...)`
- `compare_patterns(...)`
- `visualize_backtest(...)`

## 11.3 Что меняется в V4
Бэктест больше не является изолированной утилитой.  
Теперь это стандартный шаг research pipeline.

---

# 12. Validation Engine

## 12.1 Новый обязательный модуль
`validation_engine.py`

Это главная защита от:
- false discovery;
- переобучения;
- красивых, но ложных паттернов.

## 12.2 Минимальные правила подтверждения
Паттерн не может стать confirmed, если нет:
1. минимального sample size;
2. out-of-sample проверки;
3. воспроизводимой логики;
4. метрик лучше наивного baseline;
5. проверки недавнего окна;
6. regime-aware интерпретации.

## 12.3 Уровни evidence
- low
- medium
- high
- strong

## 12.4 Статус относительно прошлых версий
| Элемент | Статус |
|---|---|
| confidence через backtest | сохранён |
| автоматическое подтверждение по одной проверке | не удалено бесследно, но от этого отказались в V4 |
| полноценная validation discipline | новый обязательный слой V4 |

---

# 13. Context Continuity: от ContextLoader к Context Orchestrator

## 13.1 Что было раньше
Во всех версиях была очень сильная идея “эффекта моргания”:
система должна помнить, где остановились.

## 13.2 Почему этого стало недостаточно
Когда слоёв мало — можно грузить почти всё.  
Когда слоёв много — это приводит к шуму и перегрузке prompt.

## 13.3 Что вводит V4
Модуль: `context_orchestrator.py`

### Основная функция
`build_task_context(task_type, symbol, timeframe, user_query) -> dict`

### Поддерживаемые типы задач
- chart_analysis
- hypothesis_review
- backtest_review
- compare_with_classics
- prediction_explanation
- session_resume

### Что делает
Подгружает только релевантные блоки:
- похожие паттерны;
- близкие негативные знания;
- режим рынка;
- нужные новости;
- нужные chunks из KB;
- текущее состояние сессии.

## 13.4 Статус относительно прошлых версий
| Элемент | Статус |
|---|---|
| ContextLoader | не удалён, заменён |
| “эффект моргания” | сохранён полностью |
| подход “грузить всё подряд” | в V4 заменён оркестрацией контекста |

---

# 14. Feature Store

## 14.1 Новый обязательный фундамент
Модуль: `feature_builder.py`

## 14.2 Что хранит
Для каждого timestamp:
- OHLCV;
- RSI, MACD, BB, EMA, ATR, Volume signals;
- BTC dominance;
- funding rate;
- open interest;
- macro summary;
- onchain summary;
- news event flags;
- regime label.

## 14.3 Почему это критично
Чтобы:
- бэктестер;
- regime detector;
- model builder;
- prediction tracker;
- UI

работали на одних и тех же данных.

## 14.4 Статус относительно прошлых версий
| Элемент | Статус |
|---|---|
| data_cache из v1 | сохранён |
| raw market / macro / onchain data из v3 | сохранены |
| unified feature store | новый обязательный слой V4 |

---

# 15. Knowledge Base

## 15.1 Роль слоя
KNOWLEDGE_BASE сохраняется как полноценный слой системы.

Он нужен чтобы:
- искать классические аналоги;
- находить противоречия;
- подсвечивать novelty;
- объяснять выводы;
- помогать ориентироваться в накопленном “внешнем знании”.

## 15.2 Источники
Сохраняются из v2/v3:
- books;
- youtube;
- research;
- web.

## 15.3 Приоритеты источников в V4
1. книги;
2. research papers;
3. long-form аналитические статьи;
4. YouTube;
5. web explainers / glossaries.

## 15.4 Что меняется
Knowledge Base:
- не подтверждает паттерн;
- не заменяет тестирование;
- используется как внешний слой контекста и сравнения.

## 15.5 Модули
- `knowledge_ingester.py`
- `knowledge_search.py`

## 15.6 Статус относительно прошлых версий
| Элемент | Статус |
|---|---|
| PDF ingestion | сохранён |
| YouTube ingestion | сохранён |
| URL ingestion | сохранён |
| compare_with_hypothesis | сохранён |
| KB как доказательство эффективности | в V4 от этого отказались |

---

# 16. Trust System

## 16.1 Что сохраняется из v3
Идея Trust System сохраняется полностью:
источники должны оцениваться не только по популярности, а по полезности и надёжности.

## 16.2 Что меняется в V4
Вместо одного универсального trust score вводится **профиль пригодности источника**.

### Основные измерения
- factual_reliability
- predictive_usefulness
- market_relevance
- crypto_specificity

### Дополнительно для news
- speed
- noise_risk

### Дополнительно для books/research
- conceptual_reliability
- transferability_to_crypto

## 16.3 Модуль
`trust_manager.py`

## 16.4 Статус относительно прошлых версий
| Элемент | Статус |
|---|---|
| sources_registry.json | сохранён |
| trust history | сохранён |
| overall trust как одно магическое число | не удалён бесследно, но заменён trust profile в V4 |
| ручная корректировка trust в UI | не удалена, но перенесена в опциональный функционал |

---

# 17. News Layer

## 17.1 Что сохраняется
Из v3 сохраняется полноценная идея новостного слоя:
- сбор;
- дедупликация;
- классификация;
- оценка важности;
- связь новости с рынком.

## 17.2 Что меняется в V4
News Layer упрощается и становится практичнее:

- меньше претензии на полноценный intelligence engine на старте;
- больше фокуса на:
  - event relevance;
  - news-derived features;
  - источники;
  - маркировку на графике;
  - влияние на контекст.

## 17.3 Модули
- `news_collector.py`
- `news_scorer.py`

## 17.4 Статус относительно прошлых версий
| Элемент | Статус |
|---|---|
| сбор новостей | сохранён |
| классификация новостей | сохранена |
| трекинг влияния | сохранён |
| слишком широкий news intelligence объём | сужен в V4 |

---

# 18. On-chain и Macro

## 18.1 Статус
Полностью сохраняются из v3.

## 18.2 Роль в V4
Они входят не как “отдельная красивая надстройка”, а как часть:
- DATA;
- feature store;
- regime detection;
- model signals;
- context orchestration.

## 18.3 Модули
- `onchain_collector.py`
- `macro_collector.py`

## 18.4 Статус относительно прошлых версий
| Элемент | Статус |
|---|---|
| on-chain metrics | сохранены |
| macro context | сохранён |
| использование в regime/model | сохранено и усилено |

---

# 19. Market Regime

## 19.1 Статус
Сохраняется как обязательный слой.

## 19.2 Модуль
`regime_detector.py`

## 19.3 Почему это важно
Regime используется при:
- сохранении гипотез;
- подтверждении паттернов;
- decay monitoring;
- построении модели;
- объяснении сигналов.

## 19.4 Формат
```json
{
  "primary_regime": "bull|bear|sideways|capitulation|euphoria",
  "cycle_phase": "early|mid|late|transition",
  "risk_level": "low|medium|high",
  "confidence": 0.78,
  "reasoning": "..."
}
```

---

# 20. Negative Knowledge

## 20.1 Статус
Сохраняется как одна из важнейших особенностей всей системы.

## 20.2 Модуль
`negative_knowledge_manager.py`

## 20.3 Назначение
Сохранять системные неудачи:
- какие идеи не работают;
- в каком режиме не работают;
- какие кластеры ошибок повторяются;
- какие идеи можно инвертировать.

## 20.4 Основные функции
- `save_negative_result(...)`
- `cluster_negatives()`
- `suggest_inversion_candidates()`
- `promote_inversion_to_pattern()`

## 20.5 Статус относительно прошлых версий
| Элемент | Статус |
|---|---|
| negative knowledge | сохранён |
| negative clusters | сохранены |
| inversion testing | сохранён |
| “never revisit” как жёсткое правило | не удалено, но ослаблено — V4 предпочитает revisit_condition |

---

# 21. Pattern Decay

## 21.1 Статус
Сохраняется как обязательный аналитический слой.

## 21.2 Модуль
`pattern_decay_monitor.py`

## 21.3 Статусы
- stable
- weakening
- degrading
- decayed

## 21.4 Логика
Для каждого confirmed pattern:
- historical performance;
- recent performance;
- regime-specific recent performance.

Если паттерн начал ухудшаться:
- сначала warning;
- затем понижение веса;
- затем перенос в decayed.

## 21.5 Важное правило
Паттерн не удаляется — он переносится в decayed с историческим контекстом.

---

# 22. Causality Engine

## 22.1 Статус в V4
Не удалён.  
Но **отложен на поздний этап**.

## 22.2 Почему не включён в раннее ядро
Идея очень сильная, но это один из самых сложных исследовательских модулей.  
Если включить его слишком рано, он может создать иллюзию строгости без достаточной базы.

## 22.3 Чем временно заменяется в V4
Вместо полноценного causality engine сначала вводится **evidence grading**:
- temporal precedence;
- stability;
- robustness;
- regime dependence;
- confounder awareness.

## 22.4 Статус относительно прошлых версий
| Элемент | Статус |
|---|---|
| Causality Engine из v3 | не удалён |
| ранняя обязательная реализация causality | перенесена на поздний этап |
| evidence grading | введён как замещающий этап V4 |

---

# 23. User Profile

## 23.1 Статус в V4
Не удалён.  
Сужен до базового слоя.

## 23.2 Что остаётся
- preferred timeframes;
- basic analytical style;
- known recurring biases;
- session count;
- hypothesis success statistics.

## 23.3 Что перенесено на поздний этап
- глубокий поведенческий профиль;
- автоматическая сложная адаптация ответов;
- развитый bias mining engine.

## 23.4 Причина
Сначала нужно стабилизировать ядро системы и качество данных.

---

# 24. Live Model

## 24.1 Статус
Сохраняется полностью как стратегическая цель.

## 24.2 Но важное правило V4
Модель не строится “впереди знаний”.

Она запускается только если:
- накоплено минимум 20 confirmed patterns;
- есть out-of-sample validation;
- есть prediction tracking;
- feature store стабилен;
- есть regime-aware performance data.

## 24.3 Модуль
`model_builder.py`

## 24.4 Подход V4
Не “магический ML”, а **объяснимая rule-based ensemble model**.

Источники сигнала:
- confirmed patterns;
- negative filters;
- regime alignment;
- on-chain alignment;
- macro alignment.

## 24.5 Статус относительно прошлых версий
| Элемент | Статус |
|---|---|
| живая модель | сохранена |
| ранний запуск модели | отложен |
| объяснимый rule-based ensemble | выбран как основной вариант V4 |

---

# 25. Prediction Tracking

## 25.1 Новый обязательный модуль
`prediction_tracker.py`

## 25.2 Назначение
Каждый прогноз должен логироваться с:
- timestamp;
- входным контекстом;
- triggered patterns;
- blocked negatives;
- regime;
- horizon;
- actual result.

## 25.3 Почему это важно
Без prediction tracking невозможно:
- реально сравнивать версии модели;
- понимать качество сигналов;
- оценивать drift.

---

# 26. UI V4

## 26.1 Основной принцип
Интерфейс строится не вокруг набора независимых вкладок, а вокруг research workflow.

## 26.2 Вкладки

### 1. 📊 Market
- свечной график;
- индикаторы;
- news markers;
- regime summary;
- key context.

### 2. 💬 Research Chat
- чат;
- формализация гипотезы;
- compare with classics;
- save negative;
- run test.

### 3. 🧪 Experiments
- реестр экспериментов;
- статусы;
- результаты;
- review.

### 4. 🧩 Patterns
- candidate / confirmed / decayed / inverted;
- evidence level;
- recent performance.

### 5. 📚 Knowledge Base
- поиск;
- aligned / conflicting / novel;
- источники.

### 6. 📰 News & Context
- лента;
- relevance;
- source profile;
- влияние.

### 7. 🎯 Model
- текущий прогноз;
- triggered patterns;
- blocked negatives;
- recent tracking stats.

### 8. 📉 Decay & Negatives
- деградация;
- негативные кластеры;
- inversion candidates.

## 26.3 Статус относительно прошлых версий
| Элемент | Статус |
|---|---|
| Streamlit UI | сохранён |
| 2 вкладки из v1 | не удалены, а расширены |
| 4 вкладки из v2 | сохранены как основа |
| 7 вкладок из v3 | не удалены, а реорганизованы в 8 workflow-oriented вкладок |

---

# 27. Backup и отчётность

## 27.1 Статус
Сохраняется из v3 как обязательный слой.

## 27.2 Модули
- `backup_manager.py`
- `report_builder.py`

## 27.3 Что делают
- ежедневный backup;
- хранение последних архивов;
- экспорт Markdown-отчётов по знаниям, паттернам, модели и негативным кластерам.

---

# 28. REST API

## 28.1 Статус в V4
Не удалён.  
Но перенесён в **опциональный этап инфраструктуры**.

## 28.2 Почему
До стабилизации внутренних сущностей API только закрепит нестабильные контракты.

## 28.3 Что остаётся
- идея внешнего доступа;
- использование для Telegram / mobile / alerts в будущем.

---

# 29. Полная карта преемственности: что сохранили, что отложили, что заменили

## 29.1 Сохранено без принципиальных потерь
- MARKET_MIND
- Streamlit
- Session continuity
- Hypotheses
- Patterns
- Backtesting
- Knowledge Base
- Compare with classics
- News
- Trust
- On-chain
- Macro
- Regime
- Negative knowledge
- Pattern decay
- Live model
- Backup

## 29.2 Заменено более строгим вариантом
- ContextLoader → Context Orchestrator
- свободные JSON-структуры → schema layer
- разрозненные проверки → validation engine
- текстовые паттерны → Pattern DSL
- общий trust score → trust profile
- ручное накопление выводов → research pipeline + experiment registry

## 29.3 Перенесено на более поздний этап
- Causality Engine
- глубокий User Profile engine
- широкий REST API
- тяжёлая ручная trust-админка
- расширенная инфраструктура внешнего доступа

## 29.4 Сужено по стартовому объёму, но не удалено
- News intelligence
- trust manual control
- сложная причинность
- behavioural profiling
- full platform infra

---

# 30. Этапы реализации V4

## Этап 1 — Foundation
### Цель
Стабилизировать каркас и структуру.

### Делается
- `initialize_system.py`
- папки и шаблоны;
- схемы данных;
- `schema_validator.py`
- базовый `streamlit_app.py`
- `session_state.json`
- `system_manifest.json`
- `component_status.json`

### Результат
Система умеет жить структурно и проверять свои данные.

---

## Этап 2 — Research Core
### Цель
Построить замкнутый цикл исследования.

### Делается
- `hypothesis_formalizer.py`
- `experiment_registry.py`
- `insight_saver.py`
- `backtester.py`
- `validation_engine.py`
- `pattern_registry.py`

### Результат
Идея → гипотеза → эксперимент → review → паттерн / negative knowledge

---

## Этап 3 — Knowledge Layer
### Цель
Подключить классическое знание.

### Делается
- `knowledge_ingester.py`
- `knowledge_search.py`
- Chroma / vector index
- compare with classics

### Результат
Система умеет понимать, где идея совпадает с классикой, где спорит, где нова.

---

## Этап 4 — Data & Context Expansion
### Цель
Собрать единый data backbone.

### Делается
- `feature_builder.py`
- `regime_detector.py`
- `macro_collector.py`
- `onchain_collector.py`
- `news_collector.py`
- `news_scorer.py`
- `trust_manager.py`

### Результат
Появляется полноценный context-aware data layer.

---

## Этап 5 — Negatives & Decay
### Цель
Система должна уметь защищать себя от ложных знаний.

### Делается
- `negative_knowledge_manager.py`
- `pattern_decay_monitor.py`

### Результат
Система умеет:
- сохранять системные ошибки;
- кластеризовать неудачи;
- отслеживать деградацию.

---

## Этап 6 — Live Model
### Цель
Построить объяснимую модель поверх validated knowledge.

### Делается
- `model_builder.py`
- `prediction_tracker.py`
- model UI tab

### Результат
Рабочая модель, которая объясняет свои сигналы и отслеживает качество.

---

## Этап 7 — Optional Infra
### Цель
Внешний доступ и сервисные функции.

### Делается
- API;
- alerting;
- расширенный export;
- внешние интеграции.

### Статус
Не удалено.  
Осознанно вынесено за пределы стартового обязательного ядра.

---

# 31. Первый стартовый комплект файлов V4

Обязательные стартовые файлы:

- `ENGINE/initialize_system.py`
- `ENGINE/schema_validator.py`
- `ENGINE/context_orchestrator.py`
- `ENGINE/hypothesis_formalizer.py`
- `ENGINE/experiment_registry.py`
- `ENGINE/insight_saver.py`
- `ENGINE/backtester.py`
- `ENGINE/validation_engine.py`
- `ENGINE/pattern_registry.py`
- `ENGINE/feature_builder.py`
- `ENGINE/regime_detector.py`
- `UI/streamlit_app.py`
- `CONFIG/.env.example`

---

# 32. Что не должно потеряться при дальнейших версиях

Это обязательное правило развития после V4.

При создании V5+ запрещено:
- удалять старые идеи без следа;
- переписывать архитектуру без migration map;
- убирать модули без пометки причин;
- терять связь между версиями ТЗ.

Каждая следующая версия должна иметь раздел:

## Migration Map
- что перенесли;
- что заменили;
- что свернули;
- почему;
- чем это компенсируется;
- где теперь это живёт в системе.

---

# 33. Итоговый вердикт V4

V4 — это версия, где:
- ничего не теряется из прошлых ТЗ;
- лучшие идеи v1, v2, v3 сохраняются;
- перегрузка v3 приводится к инженерно устойчивой форме;
- проект становится не просто “системой модулей”, а **исследовательской операционной системой с дисциплиной знаний**.

Если кратко:

- v1 дал ядро;
- v2 дал уникальную идею;
- v3 дал масштаб;
- v4 даёт устойчивость, порядок и реалистичный путь реализации.

---

# 34. Приложение A — Статусный реестр наследия по крупным блокам

| Блок | Был в версиях | Статус в V4 |
|---|---|---|
| MARKET_MIND | v1, v2, v3 | сохранён |
| KNOWLEDGE_BASE | v2, v3 | сохранён |
| Streamlit UI | v1, v2, v3 | сохранён и переработан |
| Context continuity | v1, v2, v3 | сохранён, механизм заменён |
| Insight saving | v1, v2, v3 | сохранён и встроен в pipeline |
| Backtesting | v1, v2, v3 | сохранён и усилен |
| Live Model | v2, v3 | сохранён, этап смещён позже |
| Trust System | v3 | сохранён, переработан |
| News Engine | v3 | сохранён, сужен |
| Macro | v3 | сохранён |
| On-chain | v3 | сохранён |
| Market Regime | v3 | сохранён |
| Negative Knowledge | v3 | сохранён |
| Pattern Decay | v3 | сохранён |
| Causality Engine | v3 | сохранён как future module |
| User Profile | v3 | сохранён в базовой версии |
| REST API | v3 | сохранён как optional stage |
| Backup | v3 | сохранён |
| Schema Layer | V4 | новый обязательный |
| Experiment Registry | V4 | новый обязательный |
| Validation Engine | V4 | новый обязательный |
| Feature Store | V4 | новый обязательный |
| Context Orchestrator | V4 | новый обязательный |
| Pattern DSL | V4 | новый обязательный |

---

# 35. Приложение B — Формулировка правила изменений для будущих ТЗ

Любой элемент системы при изменении обязан иметь одну из пометок:

- **СОХРАНЁН** — элемент остаётся без принципиальной смены роли;
- **РАСШИРЕН** — элемент остаётся, но получает новые функции;
- **СУЖЕН** — элемент остаётся, но уменьшается стартовый объём;
- **ЗАМЕНЁН** — старый способ остаётся в истории, но его роль переходит новому механизму;
- **ПЕРЕНЕСЁН** — элемент не удалён, а сдвинут на другой этап реализации;
- **ОТЛОЖЕН** — элемент признан важным, но временно не входит в обязательный scope;
- **ОПЦИОНАЛЬНЫЙ** — элемент не обязателен для запуска ядра, но остаётся частью системы;
- **ОТКАЗ ОТ РЕАЛИЗАЦИИ В ЭТОЙ ФОРМЕ** — старая формулировка явно сохраняется в истории, но заменяется новым вариантом.

Это правило является частью V4 и обязательно для всех следующих версий.

