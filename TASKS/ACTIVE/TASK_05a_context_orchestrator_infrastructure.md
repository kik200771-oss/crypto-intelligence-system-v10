# TASK_05a — Context Orchestrator Infrastructure

**Версия:** v1
**Дата:** 2026-04-21
**Автор:** Claude Opus (архитектор)
**Исполнитель:** Claude Code
**Зависит от:** TASK_04.6 (COMPLETED, 2026-04-19)
**Блокирует:** TASK_05b (forecast logic), TASK_05c (research/monitoring/postmortem + финализация)

**Pre-task analysis required: YES**

---

## 1. Контекст и scope

### Что делаем

Создаём **infrastructure skeleton** модуля `MARKET_MIND/ENGINE/context_orchestrator.py` — четвёртого компонента MDC (Minimum Deployable Core). Это первая из трёх sub-TASK, вместе формирующих полный Context Orchestrator:

- **TASK_05a (эта)** — infrastructure: расширения configs, tiktoken, skeleton модуля и тестов. Код публичных методов — `raise NotImplementedError`. **Никакой бизнес-логики.**
- **TASK_05b (следующая)** — forecast logic + Fast Lane Invariant.
- **TASK_05c (последняя)** — research/monitoring/postmortem + финализация, перевод статуса в `ready`.

### Зачем разбивка

Context Orchestrator — большой модуль (~600-800 строк кода + ~400 строк тестов). TASK_05 "всё сразу" был бы на 2000+ строк инструкции и 1.5-2 рабочих дня Claude Code. Это превышает разумный размер и риск обрыва контекста.

TASK_05a фокусируется на **infrastructure без логики**: configs расширены, зависимости установлены, файловая структура создана, API объявлен через `raise NotImplementedError`, тесты проверяют что сигнатуры существуют. Это позволяет TASK_05b стартовать с ровной точки.

### Что НЕ делаем в TASK_05a

- **НЕ реализуем** `_build_forecast_context`, `_build_research_context`, `_build_monitoring_context`, `_build_postmortem_context` — это TASK_05b и TASK_05c
- **НЕ реализуем** `_collect_patterns`, `_collect_regime`, `_collect_features`, `_collect_shock_score`, `_collect_brake_level` — TASK_05b
- **НЕ реализуем** Fast Lane Invariant (graceful degradation, timeouts, parallel source collection) — TASK_05b
- **НЕ реализуем** `save_session` — TASK_05c (только декларация с `raise NotImplementedError`)
- **НЕ обновляем** `component_status.json` до `ready` — модуль не работает, только skeleton

### Что отличает этот TASK от TASK_03 v1

TASK_03 v1 (2026-04-17) реализовал **Input Assembler** вместо Context Orchestrator — см. L-01. Этот TASK_05a создаёт **правильный** Context Orchestrator skeleton, соответствующий ТЗ Задача 3 и ТЗ § 1.23 Adaptive Timeframe Core:

- Публичный API: `build_context(query, symbol, timeframe) → str`, лимит 8000 токенов
- Task Awareness: `forecast | research | monitoring | postmortem` (дословно из ТЗ)
- `save_session(summary, new_items, bias) → None`
- Timeframes — **config-driven** из `timeframe_core.json`, **не hardcoded**

---

## 2. Ссылки на канон

- **ТЗ Задача 3** (Context Orchestrator) — публичный API, Task Awareness, Fast Lane Invariant, Context Budget
- **ТЗ § 1.23 Adaptive Timeframe Core** — Layer 1 (15m/1h/4h/1d) + Layer 2 (3-6 пользовательских), **таймфреймы не hardcoded в коде**
- **ТЗ § 3** Fast Lane Implementation Invariant — никогда не блокировать 1h/4h прогноз
- **CLAUDE.md § 29.1** — модульный docstring обязателен
- **CLAUDE.md § 25 шаг 3.5** — Pre-task Analysis обязателен для этого TASK (флаг YES)
- **CLAUDE.md § 9** — Reflection Block обязателен в финальном отчёте

---

## 3. Предусловия

Перед началом выполнения проверь:

**Предусловие 1 — git status.** `git status` показывает **только** следующие изменения (согласно L-09, preload-сценарий):
- untracked: `TASKS/NOTES/observations/2026-04-19_spot_only_scope_clarification.md`
- untracked: `TASKS/NOTES/observations/2026-04-20_conditional_error_pattern_mining.md`
- untracked: `TASKS/ACTIVE/TASK_05a_context_orchestrator_infrastructure.md` (сам этот файл)

Других изменений быть не должно. Все эти файлы будут закоммичены в Части 6.

**Предусловие 2 — актуальная main.** `git log --oneline -5` — последний коммит должен быть `380c4a3 observations: first entries (bias correction + refinement roadmap)` или новее (если были коммиты между TASK_04.6 и этим TASK).

**Предусловие 3 — component_status.json.** Открой `MARKET_MIND/CONFIG/component_status.json`, подтверди:
- `context_orchestrator.status == "not_started"`
- `initialize_system.status == "ready"`
- `schema_layer.status == "ready"`
- `data_quality_gates.status == "ready"`

**Предусловие 4 — файл context_orchestrator.py не существует.** `ls MARKET_MIND/ENGINE/context_orchestrator.py` должен вернуть ошибку "file not found". Если файл существует — § 3 STOP (значит где-то не сработал cleanup TASK_04.6 или TASK_03 legacy не удалён).

**Предусловие 5 — tiktoken ещё не установлен** (это нормально для этого TASK). `pip show tiktoken` должен вернуть "Package(s) not found". Мы устанавливаем его в Части 3.

Если какое-то предусловие не выполнено — § 3 STOP, не начинай работу.

---

## 4. Подготовка — когнитивная система

Перед Частью 1 (и перед Pre-task Analysis) прочитай заново:

1. **`LESSONS_LEARNED.md`** — обрати особое внимание на: L-01 (TASK vs ТЗ), L-03 (no hardcoded paths), L-04 (no emoji), L-07 (graceful degradation, no stubs), L-08 (Fast Lane Invariant — этот TASK закладывает его для TASK_05b), L-09 (preload в предусловиях), L-18/L-19/L-20/L-21 (AP-10 все формы), L-22 (L-NN в отчётах — сверяться), L-23 (compound commands).

2. **`ANTIPATTERNS.md`** — AP-01 (hardcoded paths), AP-02 (stub data — в этом TASK `NotImplementedError`, не stub-возвращаемые значения), AP-07 (no scope creep), AP-10 (ad-hoc команды и файлы).

3. **`PATTERNS.md`** — P-01 (Path.resolve), P-03 (exception handling + logging), P-04 (config с дефолтом при отсутствии), P-05 (ASCII markers + UTF-8 reconfigure).

---

## 5. Pre-task Analysis (обязательно)

**До** начала Части 1 — пришли Сергею отдельным сообщением Pre-task Analysis Block согласно формату CLAUDE.md § 25.3.5:

```
=== PRE-TASK ANALYSIS ===

1. Ясность TASK:
   - <что кажется ясным>
   - <что может быть неоднозначным и как ты интерпретируешь>

2. Риски стратегии:
   - <потенциальные проблемы которые видишь>
   - <архитектурные решения которые могут оказаться неверными>

3. Соответствие канону:
   - <расхождения с ТЗ / когнитивной системой или явное "не вижу"> 

4. Альтернативы:
   - <подходы которые рассмотрел бы если писал TASK сам>

5. Вопросы архитектору (неблокирующие):
   - <что было бы полезно прояснить но не мешает начать>

=== END PRE-TASK ANALYSIS ===

Продолжаю по TASK как написано.
```

Это **первый раз в v5 режиме с Pre-task Analysis** — наблюдаем качество процесса. Не тормози работу из-за анализа, но и не пропускай.

---

## 6. Части задачи

### Часть 1 — Расширить `timeframe_core.json`

**Цель:** добавить секцию `context_orchestrator_timeouts` в существующий `MARKET_MIND/CONFIG/timeframe_core.json`, не ломая существующие секции.

**Текущая структура файла** (для reference — проверь `cat` перед изменением):

```json
{
  "mode": "standard_core",
  "standard_core": {
    "timeframes": ["15m", "1h", "4h", "1d"],
    "primary": "4h",
    "context": "1d",
    "fast_lane": ["1h", "4h"]
  },
  "tf_multipliers": {"1w": 1.5, "1d": 1.3, "4h": 1.0, "1h": 0.85, "15m": 0.7, "5m": 0.55, "1m": 0.4},
  "tf_conflict_penalty": -0.1,
  "tf_agreement_bonus": 0.05
}
```

**Что добавить** — новая top-level секция `context_orchestrator_timeouts`:

```json
"context_orchestrator_timeouts": {
  "fast_lane_total_ms": 5000,
  "slow_lane_total_ms": 30000,
  "per_source_ms": {
    "patterns": 150,
    "kb": 400,
    "regime": 80,
    "shock": 50,
    "prior": 200,
    "features": 100
  }
}
```

**Обоснование значений:**
- `fast_lane_total_ms: 5000` — дефолт из ТЗ § 3 ("default: 5000 мс" в FAILOVER RULE)
- `slow_lane_total_ms: 30000` — Slow Lane (24h/research) не требует жёсткого latency, 30 сек запас на полный KB context
- `per_source_ms` — эмпирические стартовые значения из ТЗ и TASK_03 v1 legacy (патерны и prior — медленнее из-за файловой IO; shock и regime — in-memory расчёт)

**Как делать:**
1. `type "MARKET_MIND\CONFIG\timeframe_core.json"` (Windows) или `cat MARKET_MIND/CONFIG/timeframe_core.json` — подтверди текущее содержимое
2. Откорректируй файл вручную (не через sed/python) — добавь новую секцию после `tf_agreement_bonus` перед закрывающей `}`
3. Убедись что JSON валидный: `python -c "import json; json.load(open('MARKET_MIND/CONFIG/timeframe_core.json','r',encoding='utf-8')); print('[OK] valid JSON')"` — **эта команда в TASK, разрешена** (валидация существующего файла, не ad-hoc диагностика модулей).

**Критерии готовности Часть 1:**
- JSON валидный после редактирования
- Существующие поля (`mode`, `standard_core`, `tf_multipliers`, `tf_conflict_penalty`, `tf_agreement_bonus`) **нетронуты** (те же значения что были)
- Добавлена секция `context_orchestrator_timeouts` с указанной структурой
- Кодировка файла UTF-8 (§ 13)

---

### Часть 2 — Расширить `session_state.json`

**Цель:** добавить поля `summary`, `new_items`, `bias` в существующий `MARKET_MIND/CONFIG/session_state.json` — для будущего метода `save_session()`.

**Текущая структура** (для reference):

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

**Что добавить** — три новых поля после существующих:

```json
"summary": null,
"new_items": [],
"bias": null
```

**Семантика:**
- `summary: str | null` — краткое текстовое описание последней сессии (результат `save_session()`)
- `new_items: list[str]` — новые элементы обнаруженные в сессии (паттерны, гипотезы, observations)
- `bias: str | null` — bias-маркер (directional / asset / indicator / timeframe concentration — см. ТЗ § 4 types of bias)

**Как делать:**
1. `type "MARKET_MIND\CONFIG\session_state.json"` — подтверди текущее содержимое
2. Отредактируй файл вручную — добавь три поля
3. Валидация: тот же `python -c "import json; json.load(...)"` что в Части 1

**Критерии готовности Часть 2:**
- JSON валидный
- Существующие 7 полей нетронуты
- Добавлены 3 новых поля с дефолтами `null / [] / null`
- UTF-8

---

### Часть 3 — Добавить `tiktoken` в requirements.txt и установить

**Цель:** `tiktoken` понадобится в Части 4 для constant `TIKTOKEN_ENCODING` и вспомогательной функции `_count_tokens()` (в skeleton — с fallback к `len // 4` при ImportError).

**Шаги:**

1. Открой `requirements.txt`, добавь строку (в алфавитном порядке если в файле есть сортировка, иначе в конец):
   ```
   tiktoken>=0.5.0
   ```

2. Установи через pip:
   ```
   pip install tiktoken>=0.5.0
   ```

3. Проверь установку:
   ```
   python -c "import tiktoken; enc = tiktoken.get_encoding('cl100k_base'); print(f'[OK] tiktoken {tiktoken.__version__} with cl100k_base')"
   ```

**Критерии готовности Часть 3:**
- `requirements.txt` содержит строку `tiktoken>=0.5.0`
- `import tiktoken` работает без ошибок
- Encoding `cl100k_base` доступен (это кодировка для GPT-4 / Claude-совместимых моделей)

**Важно (L-09 в `requirements.txt`):** если в файле уже были другие зависимости помимо stdlib — не трогай их. Добавляем только одну строку.

---

### Часть 4 — Skeleton `context_orchestrator.py`

**Файл:** `MARKET_MIND/ENGINE/context_orchestrator.py`

Это **skeleton**. Все публичные методы — `raise NotImplementedError("implemented in TASK_05b")` или `NotImplementedError("implemented in TASK_05c")`. Вспомогательные функции `_load_timeframe_core`, `_count_tokens`, `is_fast_lane` — **реализованы** (они нужны тестам в Части 5).

#### 4.1 Спецификация модульного docstring (§ 29.1)

Модуль начинается с docstring в формате:

```
"""
context_orchestrator — Context Orchestrator для CIS V10.0-r1.

Собирает контекст для модели прогноза с учётом Task Awareness
(forecast/research/monitoring/postmortem), таймфрейма и
Fast Lane Implementation Invariant.

Публичный API:
    build_context(query, symbol, timeframe) -> str
    save_session(summary, new_items, bias) -> None
    is_fast_lane(task_type, timeframe, config) -> bool

Интеграция с:
    - MARKET_MIND/CONFIG/timeframe_core.json (таймфреймы + timeouts)
    - MARKET_MIND/CONFIG/session_state.json (save_session target)
    - Pattern Registry (Task 8) — через LAYER_A_RESEARCH/patterns/
    - Regime Detector (Task 14) — через LAYER_B_DATA/
    - Feature Store (Task 13) — через LAYER_B_DATA/features/
    - Shock Score / Brake Level — через LAYER_H_INFRA/

ТЗ-источник:
    - Задача 3 (Context Orchestrator)
    - § 1.23 Adaptive Timeframe Core (Layer 1 + Layer 2 support)
    - § 3 Fast Lane Implementation Invariant

Уроки:
    - L-01 (Context Orchestrator != Input Assembler)
    - L-03 (no hardcoded paths — P-01 через Path(__file__).resolve())
    - L-07 (graceful degradation, no stub data)
    - L-08 (Fast Lane Invariant — никогда ABORTED в Fast Lane)

Компонент: MDC, Layer D_MODEL (по Combined Schematics V5)
Статус: skeleton (TASK_05a). Логика в TASK_05b/05c.
"""
```

#### 4.2 Imports

Порядок imports (PEP 8):
1. Stdlib: `json`, `logging`, `sys`, `time`, `dataclasses`, `pathlib.Path`, `typing.Any/Optional/List/Dict`
2. Third-party optional (через try/except): `tiktoken` — при ImportError переменная `tiktoken = None`, будем использовать fallback в `_count_tokens`

Логгер модуля: `logger = logging.getLogger(__name__)`.

**Не импортируй** в этом skeleton:
- Pattern Registry, Regime Detector, Feature Store — они ещё не реализованы, будут через try/except Optional imports в TASK_05b
- AXM Guard — в TASK_05b (минимальная inline реализация)

#### 4.3 Constants (на уровне модуля, после imports)

Объяви следующие константы:

- `TASK_TYPES: frozenset[str]` — дословно 4 значения из ТЗ: `frozenset({"forecast", "research", "monitoring", "postmortem"})`. **Комментарий обязателен:** `# ТЗ Задача 3: Task Awareness taxonomy. НЕ расширять без обновления ТЗ.`

- `MAX_TOKENS: int = 8000` — ТЗ Задача 3: Context Budget. **Комментарий:** `# ТЗ Задача 3: лимит context в токенах для build_context()`

- `TIKTOKEN_ENCODING: str = "cl100k_base"` — стандарт для GPT-4 / Claude-совместимых токенизаторов.

- `BRAKE_THRESHOLDS: dict[str, float]` — словарь:
  ```
  {
      "shock_score_include": 0.25,  # ТЗ Задача 3: при shock_score > 0.25 — brake_info в контекст
      "conflict_flag": 0.5,          # exposure threshold для conflict_flag (будет использоваться в TASK_05b)
  }
  ```

**Критично (CV-11):** НЕ объявляй `TIMEFRAMES = frozenset({...})` или аналогичный hardcoded список таймфреймов. Поддерживаемые таймфреймы читаются из `timeframe_core.json` через `_load_timeframe_core()`. Layer 2 extensibility ТЗ § 1.23 требует чтобы система поддерживала 3-6 пользовательских таймфреймов.

#### 4.4 Dataclasses

Три dataclass, все `@dataclass(frozen=True)`:

**`BlockSpec`** — спецификация одного блока контекста (какие данные, какой приоритет, какой budget limit).

Поля:
- `name: str` — имя блока (например "patterns", "regime", "shock_info")
- `priority: int` — приоритет (меньше = выше, 1-10)
- `required: bool` — обязателен ли блок (Fast Lane обязательные входы vs желательные)
- `max_tokens: int | None` — лимит на размер блока (None = неограничен пока есть общий budget)

**`ContextBlock`** — один собранный блок с контентом.

Поля:
- `name: str`
- `content: str` — текстовое представление блока (готовое для inclusion в итоговый context)
- `token_count: int` — посчитанное количество токенов
- `source_available: bool` — успешно ли собрались данные (для graceful degradation — P-02)

**`ContextResult`** — результат `build_context`.

Поля:
- `context: str` — финальный текст контекста
- `total_tokens: int`
- `blocks_included: list[str]` — имена включённых блоков
- `blocks_dropped: list[str]` — имена пропущенных (с причиной через `":"` разделитель, например "patterns:source_missing", "kb:budget_exceeded")
- `context_degraded: bool` — True если пропущены обязательные блоки или был timeout
- `status: str` — `"OK"` | `"DEGRADED"` (**никогда `"ABORTED"` в Fast Lane** — L-08)

#### 4.5 Вспомогательные функции (реализовать в этом TASK)

Эти функции **реализованы в skeleton** (не `NotImplementedError`) — они нужны тестам в Части 5 и используются публичными методами в TASK_05b/05c.

**`_load_timeframe_core() -> dict`**

Назначение: читает `MARKET_MIND/CONFIG/timeframe_core.json` через P-01 (Path.resolve) + P-03 (exception handling + logging) + P-04 (config с дефолтом при отсутствии — но тут файл ДОЛЖЕН существовать после Части 1).

Поведение:
- Читает файл через `Path(__file__).resolve().parent.parent / "CONFIG" / "timeframe_core.json"`
- При `FileNotFoundError` — logger.error + raise (не fallback, этот файл критичен)
- При `JSONDecodeError` — logger.error + raise
- Возвращает распарсенный dict

Длина тела: ~10-15 строк.

**`_count_tokens(text: str, encoding_name: str = TIKTOKEN_ENCODING) -> int`**

Назначение: считает количество токенов в тексте.

Поведение:
- Если `tiktoken is not None` — использует `tiktoken.get_encoding(encoding_name).encode(text)` и возвращает len
- Если `tiktoken is None` (ImportError при imports) — fallback: `return len(text) // 4` (грубая оценка: ~4 символа на токен для английского)
- При любой ошибке tiktoken — logger.warning + fallback к `len // 4`

Длина тела: ~10 строк.

**`is_fast_lane(task_type: str, timeframe: str, config: dict | None = None) -> bool`**

Назначение: определяет принадлежит ли (task_type, timeframe) к Fast Lane. Используется всеми `_build_*_context` методами в TASK_05b для выбора ветки.

Правило из ТЗ Задача 3:
- Fast Lane = `task_type == "forecast"` AND `timeframe` in fast_lane списке из config
- Во всех других случаях — Slow Lane или не применимо (research/monitoring/postmortem — не Fast Lane)

Поведение:
- Если `config is None` — загружает через `_load_timeframe_core()`
- Извлекает `fast_lane_list = config["standard_core"]["fast_lane"]` (по умолчанию `["1h", "4h"]`, но **читаем из config**, не hardcoded — CV-11)
- Возвращает `task_type == "forecast" and timeframe in fast_lane_list`
- При отсутствии ключей в config (malformed) — logger.warning + return False (безопасный дефолт — при сомнении Slow Lane)

Длина тела: ~10 строк.

#### 4.6 Класс `ContextOrchestrator`

**`__init__(self, market_mind_root: str | Path | None = None)`**

Поведение:
- Применяет P-01: если `market_mind_root is None` — `market_mind_root = Path(__file__).resolve().parent.parent`
- Сохраняет `self.market_mind_root = Path(market_mind_root)`
- Инициализирует `self.config = _load_timeframe_core()` (один раз при создании)
- Сохраняет `self.logger = logging.getLogger(self.__class__.__name__)`
- **НЕ** инициализирует connections к Pattern Registry / Feature Store / etc. — это делается lazy в TASK_05b

Длина тела: ~6-8 строк.

**`build_context(self, query: str, symbol: str, timeframe: str, task_type: str = "forecast") -> ContextResult`**

Назначение: публичный API ТЗ Задача 3.

В skeleton (TASK_05a):
- Валидация входов: `task_type in TASK_TYPES` — иначе `ValueError(f"Invalid task_type: {task_type}. Expected one of {TASK_TYPES}")`
- Валидация: `symbol` — непустая строка, `timeframe` — непустая строка (минимальная проверка)
- Тело: `raise NotImplementedError("Context building logic implemented in TASK_05b (forecast) and TASK_05c (research/monitoring/postmortem)")`

Длина тела: ~6-8 строк (включая валидацию, до `NotImplementedError`).

**`save_session(self, summary: str, new_items: list[str], bias: str | None = None) -> None`**

Назначение: публичный API из ТЗ Задача 3.

В skeleton:
- Валидация: `summary` — строка (может быть пустой), `new_items` — list of str, `bias` — str или None
- Тело: `raise NotImplementedError("save_session logic implemented in TASK_05c")`

Длина тела: ~4-6 строк.

**Другие методы (приватные) — НЕ объявлять в этом TASK.** Они появятся в TASK_05b/05c. Skeleton должен иметь **только** публичные API методы + `__init__`.

#### 4.7 Module-level wrappers

Для удобства импорта (ТЗ Задача 3 объявляет функции, не только класс):

- `def build_context(query: str, symbol: str, timeframe: str, task_type: str = "forecast") -> ContextResult:` — создаёт `ContextOrchestrator()` и вызывает метод

- `def save_session(summary: str, new_items: list[str], bias: str | None = None) -> None:` — создаёт `ContextOrchestrator()` и вызывает метод

Длина каждой функции: 2-3 строки (создание экземпляра + делегация).

**Важно:** эти wrappers тоже будут кидать `NotImplementedError` через экземпляр класса. Это корректно.

#### 4.8 Общая структура файла (порядок секций)

1. Модульный docstring (§ 29.1, пункт 4.1)
2. Imports (4.2)
3. Logger: `logger = logging.getLogger(__name__)`
4. Constants (4.3): `TASK_TYPES`, `MAX_TOKENS`, `TIKTOKEN_ENCODING`, `BRAKE_THRESHOLDS`
5. Dataclasses (4.4): `BlockSpec`, `ContextBlock`, `ContextResult`
6. Вспомогательные функции (4.5): `_load_timeframe_core`, `_count_tokens`, `is_fast_lane`
7. Класс `ContextOrchestrator` (4.6): `__init__`, `build_context`, `save_session`
8. Module-level wrappers (4.7): `build_context`, `save_session`

**Никаких дополнительных методов, утилит, helpers в этом TASK.** Если по ходу работы кажется что нужна ещё одна функция — § 3 STOP + вопрос архитектору.

#### 4.9 Что НЕ должно быть в файле (профилактика AP-02 и AP-10)

- Никаких `"stub": True` полей — мы используем `raise NotImplementedError`, не возвращаем заглушечные значения
- Никаких `# TODO` / `# FIXME` — § 29.3 запрещает TODO в production. Вместо TODO — `raise NotImplementedError("...implemented in TASK_05b...")`
- Никаких `debug_*.py`, `check_*.py` в корне или где-либо (AP-10 форма B)
- Никаких `python -c "..."` команд при реализации (AP-10 форма A) — для проверки используй `python MARKET_MIND/tests/test_context_orchestrator.py` из Части 5

**Критерии готовности Часть 4:**
- Файл `MARKET_MIND/ENGINE/context_orchestrator.py` существует
- UTF-8 без BOM (§ 13)
- `python -c "from MARKET_MIND.ENGINE import context_orchestrator; print('[OK] import')"` — **команда разрешена** (smoke import test skeleton, обозначена в TASK)
- `python -c "from MARKET_MIND.ENGINE.context_orchestrator import ContextOrchestrator, build_context, save_session, BlockSpec, ContextBlock, ContextResult, TASK_TYPES, MAX_TOKENS, is_fast_lane; print('[OK] symbols')"` — **команда разрешена**, проверяет что все expected symbols экспортируются
- `grep -n "TODO\|FIXME" MARKET_MIND/ENGINE/context_orchestrator.py` — пусто
- `grep -n "stub" MARKET_MIND/ENGINE/context_orchestrator.py` — пусто (тесты AP-02)
- `grep -n "ABORTED" MARKET_MIND/ENGINE/context_orchestrator.py` — пусто (skeleton не должен содержать ABORTED, Fast Lane Invariant — L-08)

**НЕ нужно** (явно):
- Запускать тесты из Части 5 (они ещё не созданы)
- Проверять что `build_context("test", "BTCUSDT", "4h")` работает — он `raise NotImplementedError`, это ожидаемо

---

### Часть 5 — Skeleton `test_context_orchestrator.py`

**Файл:** `MARKET_MIND/tests/test_context_orchestrator.py`

**Стиль:** function-based, stdlib only, как в `test_data_quality_monitor.py` (не unittest.TestCase). Используй P-05 (ASCII маркеры + UTF-8 reconfigure).

#### 5.1 Структура файла

1. Модульный docstring: `"""Skeleton tests для context_orchestrator (TASK_05a). Тесты API сигнатур и constants, не бизнес-логики."""`
2. UTF-8 reconfigure block (P-05, L-04)
3. Добавление sys.path для импорта:
   ```
   BASE = Path(__file__).resolve().parent.parent.parent
   sys.path.insert(0, str(BASE))
   ```
4. Импорты из модуля
5. Test functions (см. 5.2)
6. `if __name__ == "__main__":` runner с try/except AssertionError + exit code (как в `test_data_quality_monitor.py`)

#### 5.2 Test functions (примерно 8 тестов)

**`test_module_imports()`** — все публичные символы импортируются без ошибок. Проверяет: `ContextOrchestrator`, `build_context`, `save_session`, `BlockSpec`, `ContextBlock`, `ContextResult`, `TASK_TYPES`, `MAX_TOKENS`, `is_fast_lane`. `print("[OK] test_module_imports")` на успех.

**`test_task_types_constant()`** — `TASK_TYPES` — frozenset ровно из 4 значений, дословно дословно из ТЗ:
```
assert TASK_TYPES == frozenset({"forecast", "research", "monitoring", "postmortem"})
assert isinstance(TASK_TYPES, frozenset)
assert len(TASK_TYPES) == 4
```

**`test_max_tokens_constant()`** — `MAX_TOKENS == 8000`. Проверяет int type.

**`test_is_fast_lane_correctness()`** — комплексный тест вспомогательной функции:
- `is_fast_lane("forecast", "1h")` → `True`
- `is_fast_lane("forecast", "4h")` → `True`
- `is_fast_lane("forecast", "1d")` → `False` (1d не в fast_lane)
- `is_fast_lane("forecast", "15m")` → `False`
- `is_fast_lane("research", "1h")` → `False` (research — не Fast Lane независимо от tf)
- `is_fast_lane("monitoring", "4h")` → `False`
- `is_fast_lane("postmortem", "1h")` → `False`

**`test_context_orchestrator_instantiates()`** — `ContextOrchestrator()` создаётся без ошибок, имеет атрибуты `market_mind_root` (Path) и `config` (dict).

**`test_build_context_raises_notimplemented()`** — вызов `ContextOrchestrator().build_context("test", "BTCUSDT", "4h")` поднимает `NotImplementedError`. Используй try/except, не pytest.raises (stdlib only).

**`test_build_context_validates_task_type()`** — вызов `ContextOrchestrator().build_context("test", "BTCUSDT", "4h", task_type="invalid_type")` поднимает `ValueError` (валидация task_type происходит ДО `NotImplementedError`).

**`test_save_session_raises_notimplemented()`** — вызов `ContextOrchestrator().save_session("test summary", [], None)` поднимает `NotImplementedError`.

#### 5.3 Runner формат

В конце файла:

```
if __name__ == "__main__":
    tests = [
        test_module_imports,
        test_task_types_constant,
        test_max_tokens_constant,
        test_is_fast_lane_correctness,
        test_context_orchestrator_instantiates,
        test_build_context_raises_notimplemented,
        test_build_context_validates_task_type,
        test_save_session_raises_notimplemented,
    ]
    failures = []
    for t in tests:
        try:
            t()
        except AssertionError as e:
            failures.append((t.__name__, str(e)))
            print(f"[FAIL] {t.__name__}: {e}")
    if failures:
        print(f"\n[FAIL] {len(failures)}/{len(tests)} tests failed")
        sys.exit(1)
    else:
        print(f"\n[PASS] {len(tests)}/{len(tests)} tests passed")
```

**Критерии готовности Часть 5:**
- Файл `MARKET_MIND/tests/test_context_orchestrator.py` существует
- UTF-8 без BOM, `sys.stdout.reconfigure(encoding="utf-8")` в начале
- `python MARKET_MIND/tests/test_context_orchestrator.py` → `[PASS] 8/8 tests passed` (точное число может быть 7-9 в зависимости от того сколько подтестов в `test_is_fast_lane_correctness` — главное все `[OK]`)
- Exit code 0 при успехе, 1 при failure
- Никаких emoji в print (L-04, AP-06)

**НЕ делай:**
- Тесты реальной логики `_build_forecast_context` — её нет в skeleton
- Mock Pattern Registry / Feature Store — не нужны для skeleton
- Performance тесты / benchmarks — преждевременно

---

### Часть 6 — Pre-commit check + коммит

**Цель:** закоммитить всю infrastructure включая 2 untracked observation файла (L-09, соблюдение CV-07 по briefing).

**Шаги:**

1. **Pre-commit check (обязательно, § 24):**
   ```
   python scripts/pre_commit_check.py
   ```
   Должен вернуть `[PASS]`. При `[FAIL]` — **§ 3 STOP**, не коммить, сообщи Сергею что сработало и почему.

2. **Git add:**
   ```
   git add MARKET_MIND/CONFIG/timeframe_core.json
   git add MARKET_MIND/CONFIG/session_state.json
   git add requirements.txt
   git add MARKET_MIND/ENGINE/context_orchestrator.py
   git add MARKET_MIND/tests/test_context_orchestrator.py
   git add TASKS/NOTES/observations/2026-04-19_spot_only_scope_clarification.md
   git add TASKS/NOTES/observations/2026-04-20_conditional_error_pattern_mining.md
   git add TASKS/ACTIVE/TASK_05a_context_orchestrator_infrastructure.md
   ```

   **Важно:** команды по одной, не compound (L-23 профилактика). Если Claude Code интерфейс позволяет одобрить всё одной группой — ок, но каждая команда отдельной строкой.

3. **Verify staging через `git status` и `git diff --cached --stat`:**
   - `git status` — ничего untracked не должно остаться (кроме возможно новых файлов от тестов, если такие — см. ниже)
   - `git diff --cached --stat` — в staging ровно 8 файлов (или меньше если тесты в `MARKET_MIND/tests/` не генерируют новых `__pycache__` — он в `.gitignore`)

4. **Commit:**
   ```
   git commit -m "task 05a: context_orchestrator infrastructure skeleton"
   ```

   Сообщение коммита — **одной строкой**, без extended description (одна логическая работа — skeleton с расширениями configs).

5. **Verify commit:**
   ```
   git log --oneline -3
   git show --stat HEAD
   ```

   В `git show HEAD` должны быть изменения всех 8 файлов. Если какой-то отсутствует — § 3 STOP.

6. **Push в main:**
   ```
   git push origin main
   ```

   Обычный push, без force (AP-09). Если push отклонён push protection — **§ 3 STOP**, разбираем по L-11/L-14/L-16.

7. **Перемещение TASK из ACTIVE в COMPLETED:**
   ```
   git mv TASKS/ACTIVE/TASK_05a_context_orchestrator_infrastructure.md TASKS/COMPLETED/TASK_05a_context_orchestrator_infrastructure.md
   git commit -m "task 05a: archive to completed"
   git push origin main
   ```

**Критерии готовности Часть 6:**
- Pre-commit check PASSED
- Один основной коммит `task 05a: context_orchestrator infrastructure skeleton` в main
- Один финальный коммит `task 05a: archive to completed` в main (как в предыдущих TASK)
- Push прошёл без force, без push protection блокировок
- `git status` — чисто, рабочая директория без uncommitted changes

**НЕ делай:**
- **НЕ обновляй** `MARKET_MIND/CONFIG/component_status.json` — `context_orchestrator.status` остаётся `not_started` (модуль не работает, только skeleton; статус меняется только после TASK_05c)
- **НЕ пиши** WIP коммиты в main — всё одним коммитом (Часть 6 — single atomic commit)
- **НЕ используй** `--force` или `--force-with-lease` в push в main (AP-09)

---

## 7. Общие критерии готовности TASK_05a

Перед финальным отчётом прогони этот финальный чеклист:

**Files state:**
- [ ] `MARKET_MIND/CONFIG/timeframe_core.json` содержит новую секцию `context_orchestrator_timeouts`, JSON валидный, existing секции нетронуты
- [ ] `MARKET_MIND/CONFIG/session_state.json` содержит 3 новых поля (`summary`, `new_items`, `bias`), existing поля нетронуты
- [ ] `requirements.txt` содержит `tiktoken>=0.5.0`
- [ ] `tiktoken` установлен в активном Python environment
- [ ] `MARKET_MIND/ENGINE/context_orchestrator.py` создан, соответствует спецификации 4.1-4.9
- [ ] `MARKET_MIND/tests/test_context_orchestrator.py` создан, все тесты проходят с `[PASS]`

**Git state:**
- [ ] `git log --oneline -3` показывает 2 коммита этого TASK (main + archive)
- [ ] `git status` — чисто
- [ ] Нет файлов `debug_*.py`, `check_*.py`, `try_*.py` в корне или где-либо (AP-10 форма B)
- [ ] Нет `__pycache__/` закоммиченных (они в .gitignore)

**Cognitive compliance:**
- [ ] Pre-task Analysis был прислан до Части 1 (§ 25 шаг 3.5, флаг YES)
- [ ] Reflection Block будет включён в § 9 отчёт
- [ ] `component_status.json` НЕ обновлялся (context_orchestrator остаётся not_started)

---

## 8. Важные предупреждения

### 8.1 Context Orchestrator ≠ Input Assembler (L-01)

Предыдущий TASK_03 v1 (2026-04-17) по ошибке реализовал Input Assembler (Task 21 по ТЗ) вместо Context Orchestrator (Task 3). Этот TASK_05a создаёт **правильный** Context Orchestrator:

- Правильно: `build_context(query, symbol, timeframe) → str` с Task Awareness
- Неправильно: `orchestrate(request)` с per-input timeout matrix BLOCK/DEGRADE/SKIP

Если по ходу работы видишь что-то про `orchestrate()`, BLOCK/DEGRADE/SKIP статусы, per-input timeout matrix — **§ 3 STOP**, это признак что TASK понят неверно.

### 8.2 Timeframes config-driven (CV-11, ТЗ § 1.23)

ТЗ § 1.23 Adaptive Timeframe Core требует поддержки Layer 1 (default 15m/1h/4h/1d) + Layer 2 (3-6 пользовательских таймфреймов). 

**Запрещено в коде (даже в skeleton):**
- `TIMEFRAMES = frozenset({"1h", "4h", "1d"})` или аналогичный hardcoded список
- `if timeframe in ("1h", "4h")` — читай fast_lane из config

**Разрешено:**
- `fast_lane_list = config["standard_core"]["fast_lane"]`
- `if timeframe in fast_lane_list`

Это обеспечивает Layer 2 extensibility: пользователь добавляет таймфреймы в config, код продолжает работать.

### 8.3 Никаких stub values (AP-02, L-07)

Все публичные методы — `raise NotImplementedError`, **не** возвращают заглушечные значения типа `{"context": "TODO", "stub": True}`. Raise явно сигнализирует "not implemented yet" — stub маскирует отсутствие.

### 8.4 AP-10 все три формы запрещены

**Форма A** — inline команды `python -c "..."`, `echo | python`, `grep` для ad-hoc анализа кода модулей. Разрешены **только** три команды перечисленные в TASK (JSON validation + import smoke test + symbols check) — они часть критериев готовности.

**Форма B** — отдельные файлы `debug_*.py`, `check_*.py`, `explore_*.py`, `try_*.py` в любой локации. Запрещены.

**Форма C** — файлы в `MARKET_MIND/tests/`, `scripts/` не упомянутые в TASK. Разрешены **только** `context_orchestrator.py` в ENGINE и `test_context_orchestrator.py` в tests.

Если возникло желание "быстро проверить" что-то вне TASK scope — § 3 STOP.

### 8.5 Команды bash — по одной, не compound (L-23)

В Части 6 все git команды одной строкой — одна команда на одну одобренную операцию. Никаких:
- `git add X && git commit -m "..."` — разбить на 2
- `command 2>/dev/null || echo "fallback"` — не нужны redirections
- `cd path && git status` — cd отдельно, git отдельно

Если среда выдала security warning (L-20) — § 3 STOP, не одобряй молча.

### 8.6 L-NN в § 9 отчёте — сверяться с LESSONS_LEARNED.md (L-22)

Перед написанием финального отчёта (§ 9) — открой `LESSONS_LEARNED.md` и проверь что каждый упомянутый L-NN соответствует применённому подходу. В случае сомнений — "L-??" или описательная форма.

Типично применимые в TASK_05a:
- **L-01** — Context Orchestrator != Input Assembler (критично на всём TASK)
- **L-03** — P-01 в `__init__` через `Path(__file__).resolve()`
- **L-04** — ASCII маркеры в тестах, UTF-8 reconfigure
- **L-07** — `raise NotImplementedError` вместо stub values
- **L-09** — учёт preload observations в git status (Предусловие 1)
- **L-23** — команды git по одной (Часть 6)

Если применил урок которого нет в этом списке — добавляй. Если не уверен — "L-??" placeholder.

---

## 9. Формат финального отчёта (§ 9)

После выполнения всех 6 Частей + финального чеклиста (Часть 7) — пришли Сергею отчёт в формате:

```
TASK_05a [Context Orchestrator Infrastructure] — COMPLETED

Файлы изменены: 
  - MARKET_MIND/CONFIG/timeframe_core.json (расширен секцией context_orchestrator_timeouts)
  - MARKET_MIND/CONFIG/session_state.json (добавлены поля summary, new_items, bias)
  - requirements.txt (добавлен tiktoken>=0.5.0)

Файлы созданы:
  - MARKET_MIND/ENGINE/context_orchestrator.py (~N строк, skeleton)
  - MARKET_MIND/tests/test_context_orchestrator.py (~N строк, 8 тестов)

Файлы перемещены:
  - TASKS/ACTIVE/TASK_05a_*.md → TASKS/COMPLETED/TASK_05a_*.md

Файлы закоммичены дополнительно (preload-observations из L-09):
  - TASKS/NOTES/observations/2026-04-19_spot_only_scope_clarification.md
  - TASKS/NOTES/observations/2026-04-20_conditional_error_pattern_mining.md

Тесты: 8/8 passed (test_context_orchestrator.py)
Commit (main): <hash> task 05a: context_orchestrator infrastructure skeleton
Commit (archive): <hash> task 05a: archive to completed
Время работы: <минуты>
Ideas logged: 0 (или N если были)
Lessons applied: L-01 (Context Orchestrator != Input Assembler), L-03 (P-01), L-04 (ASCII markers), L-07 (no stubs), L-09 (preload in preconditions), L-23 (commands per-line)
Patterns applied: P-01 (Path.resolve), P-03 (exception handling + logging), P-04 (config с дефолтом), P-05 (ASCII markers + UTF-8)
Antipatterns avoided: AP-01 (no hardcoded paths), AP-02 (no stubs, raise NotImplementedError), AP-06 (no emoji in print), AP-07 (strict TASK scope), AP-10 (no ad-hoc commands / debug files)
Warnings/issues: <список или "none">

=== REFLECTION BLOCK (v5 — обязательный) ===

## Observations from this task
<1-5 пунктов>

## Self-critique
<1-3 пункта>

## Questions for architect (non-blocking)
<0-3 вопроса / идеи>

=== END REFLECTION BLOCK ===

Готов к следующей задаче (TASK_05b — forecast logic + Fast Lane Invariant).
```

Особые темы для Reflection Block в этом TASK (первая в v5 с Pre-task Analysis):
- Как прошёл процесс Pre-task Analysis — был ли полезен, что улучшить
- Были ли моменты желания написать `python -c` или `debug_*.py` (честно отметить)
- Есть ли места в TASK где инструкция была неясна / требовала интерпретации (для будущих TASK_05b/05c)

---

**Конец TASK_05a. Удачи!**
