# PATTERNS — Одобренные паттерны кода для CIS V10.0-r1

> **Назначение:** проверенные решения для типовых ситуаций.
> Читается Claude Code **перед началом каждой задачи** (§ 25, § 28 в CLAUDE.md).
> Пополняется **только через TASK от архитектора** — сам не добавляй.
>
> Формат одного паттерна описан в CLAUDE.md § 28.
> Текущее количество паттернов: **5** (P-01 ... P-05).

---

## P-01: Относительный путь через `Path(__file__).resolve()`

**Когда применять:** любая функция/класс которая обращается к файлам проекта
**Категория:** configuration

**Описание:**
Для определения путей внутри проекта используй `Path(__file__).resolve()` и навигацию `.parent`. Это работает независимо от того откуда запущен скрипт и где физически лежит проект.

**Пример кода:**
```python
from pathlib import Path

class SchemaValidator:
    def __init__(self, market_mind_root: str | Path | None = None):
        """
        Args:
            market_mind_root: корень MARKET_MIND. По умолчанию — родитель
                файла ENGINE/schema_validator.py, то есть MARKET_MIND/.
                Параметр нужен для тестов и нестандартных развёртываний.
        """
        if market_mind_root is None:
            # ENGINE/schema_validator.py → MARKET_MIND/
            market_mind_root = Path(__file__).resolve().parent.parent
        self.market_mind_root = Path(market_mind_root)
        self.schemas_dir = self.market_mind_root / "SCHEMAS"
```

**Почему так:**
- Код не сломается при переезде проекта (L-06)
- Код одинаково работает при запуске из любой директории
- Тесты могут передать кастомный `base_path` в fixture
- Соответствует L-03 (запрет hardcoded путей)

**Альтернативы которые НЕ подходят:**
- Hardcoded `r"C:\CODE\MARKET ANALYSIS\MARKET_MIND"` — L-03, L-06 запрещают
- `os.getcwd()` — зависит от того откуда запущен скрипт
- `sys.path[0]` — нестабильно, зависит от способа вызова

**См. также:** L-03, L-06.

---

## P-02: Data Access Layer — graceful degradation вместо stub-данных

**Когда применять:** модули которые читают данные из файлов/БД/внешних источников
**Категория:** data-access

**Описание:**
Каждый метод чтения данных возвращает **либо реальные данные, либо `None`**, плюс пишет warning в лог при отсутствии. Вызывающий код **явно проверяет** `None` и решает что делать (пропустить блок, пометить `context_degraded`, etc).

Никаких "заглушечных" значений типа `{"rsi": 45.2, "stub": True}` — это маскирует отсутствие данных и ломает вышестоящую логику.

**Пример кода:**
```python
import logging
import json
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def _load_patterns(self, symbol: str, timeframe: str) -> list[dict] | None:
    """
    Читает валидированные паттерны из LAYER_A_RESEARCH/patterns/.
    
    Returns:
        Список паттернов или None если источника нет.
    """
    patterns_dir = self.market_mind_root / "LAYER_A_RESEARCH" / "patterns"
    if not patterns_dir.exists():
        logger.warning(f"Patterns directory not found: {patterns_dir}")
        return None
    
    try:
        patterns = []
        for path in patterns_dir.glob("*.json"):
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError) as e:
                logger.warning(f"Skipping bad pattern file {path.name}: {e}")
                continue
            if data.get("symbol") == symbol and data.get("timeframe") == timeframe:
                patterns.append(data)
        return patterns if patterns else None
    except Exception as e:
        logger.error(f"Error loading patterns: {e}")
        return None


# Вызывающий код:
patterns = self._load_patterns(symbol, timeframe)
if patterns is None:
    self.blocks_dropped.append("patterns:missing")
    self.context_degraded = True
else:
    self._add_patterns_block(patterns)
```

**Почему так:**
- Честное отражение состояния системы (L-07)
- Вышестоящая логика может корректно реагировать на отсутствие данных
- Не нужен рефакторинг когда реальный модуль заменит заглушку
- Отсутствие данных не обрушивает систему

**Альтернативы которые НЕ подходят:**
- Hardcoded тестовые данные в production-коде — L-07 запрещает
- Бросать исключение — избыточно, отсутствие данных ожидаемый сценарий
- Возвращать пустой `{}` или `[]` — скрывает разницу между "нет данных" и "данных ноль"

**См. также:** L-07, P-04.

---

## P-03: Exception handling — логировать + возвращать контролируемое значение

**Когда применять:** любая функция которая делает внешние операции (файлы, сеть, парсинг)
**Категория:** error-handling

**Описание:**
Лови **конкретные типы** исключений, **всегда логируй** контекст, возвращай **документированное** значение (обычно `None` или падение через raise с дополнительным контекстом).

**Пример кода:**
```python
import logging

logger = logging.getLogger(__name__)


def _load_config(self, name: str) -> dict | None:
    """Загружает JSON-конфиг из CONFIG/. Возвращает None если не найден/битый."""
    path = self.market_mind_root / "CONFIG" / f"{name}.json"
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        logger.warning(f"Config {name}.json not found at {path}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Config {name}.json is malformed: {e}")
        return None
    except OSError as e:
        logger.error(f"Cannot read config {name}.json: {e}")
        return None
```

Плохо:
```python
try:
    data = json.loads(path.read_text())
except:           # Голый except — нарушение § 18
    pass           # Тихое проглатывание — нарушение § 18
```

**Почему так:**
- § 18 запрещает голый `except:` и тихое проглатывание
- Stack trace поиск работает когда есть конкретное сообщение в логе
- Вызывающий код получает предсказуемый `None` вместо случайного эффекта
- Разные типы ошибок могут требовать разной реакции (missing ≠ malformed)

**Альтернативы которые НЕ подходят:**
- `except Exception: pass` — скрывает баги
- `except: pass` — ловит даже KeyboardInterrupt и SystemExit
- `raise` без контекста — теряется информация где именно упало

**См. также:** CLAUDE.md § 18.

---

## P-04: Чтение конфига с созданием дефолта при отсутствии

**Когда применять:** модуль использует JSON-конфиг который **обязательно должен существовать** для работы
**Категория:** configuration

**Описание:**
Если конфиг критически нужен модулю — при первом запуске создавай его с дефолтными значениями. Это делает модуль bootstrap-friendly (работает из коробки) и явно документирует что за конфиг ожидается.

**Пример кода:**
```python
import json
from pathlib import Path

DEFAULT_TIMEFRAME_CORE = {
    "context_orchestrator_timeout_ms": 5000,
    "fast_lane_timeframes": ["1h", "4h"],
    "slow_lane_timeframes": ["24h"],
    "per_source_timeout_ms": {
        "patterns": 150,
        "kb": 400,
        "regime": 80,
        "shock": 50,
        "prior": 200,
    },
    "schema_version": "1.0.0",
}


def _load_timeframe_config(self) -> dict:
    """Читает timeframe_core.json, создаёт дефолт при отсутствии."""
    path = self.market_mind_root / "CONFIG" / "timeframe_core.json"
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(DEFAULT_TIMEFRAME_CORE, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        logger.info(f"Created default timeframe_core.json at {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        logger.error(f"Malformed timeframe_core.json, using defaults")
        return DEFAULT_TIMEFRAME_CORE.copy()
```

**Почему так:**
- Модуль работает из коробки без ручной настройки
- Дефолт в коде = документация ожидаемой структуры конфига
- Не падает при malformed JSON, возвращает безопасный дефолт с логом
- Соответствует P-03 (контролируемое поведение при ошибках)

**Альтернативы которые НЕ подходят:**
- Падать с `FileNotFoundError` — нарушает bootstrap
- Молча возвращать пустой `{}` — вызывающий код не будет знать какие ключи ждать
- Хранить дефолт в отдельном файле `.default.json` — два источника правды

**См. также:** P-03, CLAUDE.md § 18.

---

## P-05: Тест-скрипт — ASCII маркеры + UTF-8 reconfigure

**Когда применять:** любой test_*.py или verify_*.py скрипт который будет запускаться на Windows
**Категория:** testing

**Описание:**
Тестовые скрипты используют только ASCII-маркеры (`[OK]`, `[FAIL]`, `[PASS]`) в `print()`. Кодировка устанавливается в начале скрипта на UTF-8 для случаев когда в выводе есть русский текст.

**Пример кода:**
```python
#!/usr/bin/env python3
"""Тест модуля XXX."""
import sys
from pathlib import Path

# Защита от cp1251 на Windows — Lesson L-04
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

BASE = Path(__file__).resolve().parent.parent  # применяем P-01
sys.path.insert(0, str(BASE))

from MARKET_MIND.ENGINE.schema_validator import SchemaValidator


def test_valid_pattern():
    validator = SchemaValidator()
    pattern = {
        "id": "test_pattern_001",
        "name": "Test RSI Pattern",
        "logic_dsl": "RSI(14) < 30",
        "symbol": "BTCUSDT",
        "timeframe": "1h",
        "status": "testing",
        "confidence_point": 0.75,
        "evidence_grade": "B",
        "created_at": "2026-04-18T23:00:00Z",
        "last_updated": "2026-04-18T23:00:00Z"
    }
    result = validator.validate(pattern, "pattern")
    assert result.success, f"Expected valid, got errors: {result.errors}"
    print("[OK] test_valid_pattern")


def test_invalid_pattern():
    validator = SchemaValidator()
    bad = {"id": "test_bad", "status": "invalid_status"}  # missing required fields
    result = validator.validate(bad, "pattern")
    assert not result.success, "Expected invalid pattern to fail"
    assert len(result.errors) > 0, "Expected non-empty errors list"
    print("[OK] test_invalid_pattern")


if __name__ == "__main__":
    try:
        test_valid_pattern()
        test_invalid_pattern()
        print("\n[PASS] all tests")
    except AssertionError as e:
        print(f"\n[FAIL] {e}")
        sys.exit(1)
```

**Почему так:**
- Не падает на Windows cp1251 (L-04)
- Чёткий визуальный статус через `[OK]` / `[FAIL]` / `[PASS]`
- Возвращает exit code 1 при падении → работает в CI и `verify_*.py` цепочках
- Использует относительные пути (P-01)

**Альтернативы которые НЕ подходят:**
- Emoji (`✅ ❌ ⚠️`) — L-04 запрещает
- `pytest` без ASCII-маркеров — усложняет настройку, для простых verify-скриптов избыточно
- `print("OK")` без скобок — труднее грепать в выводе

**См. также:** L-04, P-01, CLAUDE.md § 13.

---

## Индекс по категориям

| Категория | Паттерны |
|---|---|
| configuration | P-01, P-04 |
| data-access | P-02 |
| error-handling | P-03 |
| testing | P-05 |

---

## История обновлений

| Дата | Версия | Что добавлено |
|---|---|---|
| 2026-04-18 | v1.0 | Initial — 5 паттернов P-01..P-05 |
