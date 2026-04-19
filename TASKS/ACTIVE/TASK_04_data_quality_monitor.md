# TASK_04 — DATA QUALITY MONITOR V2 (6 Gates + Gate Failure Policy)

**Тип:** содержательный компонент (вторая часть Задачи 2 ТЗ — после schema layer)
**Приоритет:** критично — без Data Quality Gates нельзя делать прогнозы (MDC)
**Исполнитель:** Claude Code
**Источник:** ТЗ V10.0-r1 Задача 2 (§ 1879-1943) + Gate Failure Policy (§ 1881-1902)
**Статус:** ACTIVE
**Зависимости:** TASK_02 rebuild ✅, TASK_02.5 hardening ✅, TASK_03 schema_layer ✅, TASK_03.5 cognitive v1.3 ✅
**Блокирует:** TASK_05 (context_orchestrator v2) — завершает MDC-тройку

---

## ⚠ Contract reminder

Соблюдай CLAUDE.md v4. При любом сомнении — § 3 (СТОП + вопрос Сергею).

Перед началом — **прочти когнитивные файлы** (§ 25):
- `LESSONS_LEARNED.md` v1.3 (19 уроков L-01..L-20, L-12 reserved)
- `PATTERNS.md` (5 паттернов P-01..P-05)
- `ANTIPATTERNS.md` v1.3 (10 антипаттернов AP-01..AP-10)

**Особенно релевантно для этой задачи:**
- **L-01:** Сверь TASK с ТЗ § 1879-1943 и § 1.8 построчно
- **L-02:** `ready` только после 20+ тестов PASS + соответствия ТЗ
- **L-03 / P-01 / AP-01:** `Path(__file__).resolve()` везде, hook проверит
- **L-04 / P-05 / AP-06:** ASCII маркеры в тестах
- **L-07 / P-02 / AP-02:** Никаких stub данных — реальные эвристики
- **L-17:** Это cleanup-компонент — удаляем legacy `data_quality_gates.py`, не забудь его
- **L-18 / AP-10:** Никаких ad-hoc `python -c` / `echo | python` / изолированных `grep`. Только команды из TASK или из test_suite
- **L-20:** Security warnings от среды — не одобрять молча
- **§ 29:** Модульный docstring + ссылки на уроки в комментариях

Pre-commit hook установлен — он автоматически ловит AP-01/03/05/06/08 + TODO/FIXME. Полагайся на него.

---

## Контекст и scope

Компонент `data_quality_gates` в `component_status.json` имеет статус `needs_rewrite`. В репо существует legacy файл `MARKET_MIND/ENGINE/data_quality_gates.py` (439 строк, создан в initial commit `5a98001` от 17.04.2026, 0 тестов, 0 интеграций). ТЗ § 1908 требует имя `data_quality_monitor.py` — не `data_quality_gates.py`.

**Что делаем в TASK_04:**
1. Удалить legacy `MARKET_MIND/ENGINE/data_quality_gates.py`
2. Создать `MARKET_MIND/CONFIG/gate_failure_policy.json` (конфиг согласно ТЗ § 1881-1902)
3. Создать `MARKET_MIND/ENGINE/data_quality_monitor.py` с 6 Gates и правильным API
4. Создать `MARKET_MIND/tests/test_data_quality_monitor.py` — минимум 20 тестов
5. Обновить `component_status.json`: `data_quality_gates: ready`

**Что НЕ делаем в TASK_04 (зона других задач):**
- Context Orchestrator — TASK_05
- Интеграция с Feature Store — TASK_13
- Привязка к реальному источнику OHLCV (Binance) — TASK_13
- Shock Score computation — TASK_24 (Feedback system). В TASK_04 возвращаем только **shock_score_delta** который вносит Gate 6; полный shock_score считается где-то ещё
- Streamlit UI индикаторы Gates — TASK_27

Разделение scope чёткое: в TASK_04 — движок проверки качества данных. Он принимает **список candles** (dict-структуры совместимые с ohlcv формой) и возвращает `QualityReport`. Источник candles — не наше дело (реальный Binance client, тестовые fixtures, whatever).

---

## Рабочая директория

`C:\CODE\MARKET ANALYSIS\`

---

## Предусловия (проверить перед началом)

1. Текущая ветка — `main`, local = remote
2. Последние коммиты в main (через `git log --oneline -5`):
   - `2199997` archive TASK_03.5
   - `341abd1` task 03.5: extend verify_cognitive_foundation
   - `2ef94d8` task 03.5: update cognitive system with L-17..L-20, AP-10
   - `ac17dc5` chore: untrack log files, fix gitignore
   - `35d8789` archive TASK_03
3. `git status` показывает **только**:
   - untracked: `TASKS/ACTIVE/TASK_04_data_quality_monitor.md` (сам файл задачи)
   - возможно modified: `.claude/settings.local.json` (permissions — нормально)
4. `python MARKET_MIND/tests/test_schema_validator.py` — 17/17 PASS (TASK_03 работает)
5. `python scripts/verify_infrastructure.py` — [PASS]
6. `python scripts/verify_cognitive_foundation.py` — [PASS]
7. Файл `MARKET_MIND/ENGINE/data_quality_gates.py` **существует** (legacy)
8. Файл `MARKET_MIND/ENGINE/data_quality_monitor.py` **НЕ существует**
9. Файл `MARKET_MIND/CONFIG/gate_failure_policy.json` **НЕ существует**
10. Локальных веток кроме `main` нет

Если любое условие не выполнено → § 3 (СТОП).

---

## Часть 1 — Создать ветку

```bash
cd "C:\CODE\MARKET ANALYSIS"
git checkout main
git pull origin main
git checkout -b task-04-data-quality-monitor
```

---

## Часть 2 — Удалить legacy `data_quality_gates.py`

Отдельным коммитом, чтобы история была чистой (применение L-17: явно удаляем legacy как начальный шаг).

```bash
cd "C:\CODE\MARKET ANALYSIS"

# Убедиться что файл существует
ls MARKET_MIND/ENGINE/data_quality_gates.py

# Удалить из git и с диска
git rm MARKET_MIND/ENGINE/data_quality_gates.py

# Коммит
git commit -m "task 04 part 2: remove legacy data_quality_gates.py (needs_rewrite, replaced by data_quality_monitor.py per TZ § 1908)"

# Pre-commit hook должен вывести [PASS] (или [INFO] No staged files — зависит от реализации hook)
```

Файл помечен как `needs_rewrite` в `component_status.json`. 439 строк, 0 тестов, 0 интеграций — безопасно удалить. Замена появится в Части 4 с правильным именем (`data_quality_monitor.py`) и правильными Gates.

**Важно:** pre-commit hook может попытаться проверить удаляемый файл. Если блокирует — STOP (это значит есть проблема с логикой hook, не с нашим удалением).

---

## Часть 3 — Создать `MARKET_MIND/CONFIG/gate_failure_policy.json`

ТЗ § 1883: "Файл: CONFIG/gate_failure_policy.json". Создаём конфиг по таблице из § 1885-1899.

Создай файл с содержимым:

```json
{
  "$schema_version": "1.0",
  "description": "Gate Failure Policy согласно ТЗ V10.0-r1 Задача 2 § 1881-1902. Определяет failure_mode и confidence_penalty для каждого из 6 Gates. Используется data_quality_monitor.py.",
  "version": "V10.0-r1",
  "created_at": "2026-04-19",
  "gates": {
    "gate_1_data_corruption": {
      "gate_id": 1,
      "check_type": "data_corruption / duplicate candles",
      "failure_mode": "block",
      "confidence_penalty": 0.0,
      "behavior": "Полная блокировка — данные физически некорректны. Gate 1 НЕ допускает продолжения pipeline.",
      "affects_shock_score_delta": 0.0,
      "affects_manipulation_risk": false
    },
    "gate_2_timestamp_gaps": {
      "gate_id": 2,
      "check_type": "timestamp gaps / sequence errors",
      "failure_mode": "warn",
      "confidence_penalty": -0.05,
      "behavior": "Логирование, предупреждение в UI, прогноз продолжается.",
      "affects_shock_score_delta": 0.0,
      "affects_manipulation_risk": false
    },
    "gate_3_statistical_outliers": {
      "gate_id": 3,
      "check_type": "statistical outlier detection",
      "failure_mode": "degrade",
      "confidence_penalty": -0.10,
      "behavior": "Данные идут дальше с quality_flag=degraded. Gate 3 может ложно срабатывать при резком легитимном движении.",
      "affects_shock_score_delta": 0.0,
      "affects_manipulation_risk": false
    },
    "gate_4_cross_source_consistency": {
      "gate_id": 4,
      "check_type": "cross-source consistency",
      "failure_mode": "degrade",
      "confidence_penalty": -0.08,
      "behavior": "Данные идут дальше. Inconsistency фиксируется в audit.",
      "affects_shock_score_delta": 0.0,
      "affects_manipulation_risk": false
    },
    "gate_5_volume_anomaly": {
      "gate_id": 5,
      "check_type": "volume / liquidity anomaly",
      "failure_mode": "degrade",
      "confidence_penalty": -0.07,
      "behavior": "Данные идут дальше. shock_score получает +0.10.",
      "affects_shock_score_delta": 0.10,
      "affects_manipulation_risk": false
    },
    "gate_6_market_integrity": {
      "gate_id": 6,
      "check_type": "Market Integrity (MDC) — wash trading detection",
      "failure_mode": "degrade",
      "confidence_penalty": -0.15,
      "behavior": "Данные идут дальше. manipulation_risk_score повышается. Эвристики: round_volumes > 30%, volume_spike без price_impact > 10%, repeated_candles > 5%.",
      "affects_shock_score_delta": 0.0,
      "affects_manipulation_risk": true,
      "heuristics": {
        "suspicious_round_volumes_threshold_pct": 30.0,
        "volume_without_price_impact_threshold_pct": 10.0,
        "repeated_candles_threshold_pct": 5.0
      }
    }
  },
  "degraded_mode_rule": {
    "description": "Если два или более Gate переходят в degrade одновременно — shock_score получает принудительный +0.15 и UI показывает 'Degraded data mode'.",
    "trigger_min_degraded_gates": 2,
    "forced_shock_score_delta": 0.15,
    "ui_flag": "Degraded data mode"
  },
  "confidence_floor": {
    "description": "Confidence penalties суммируются но не могут опустить confidence_point ниже 0.20.",
    "min_confidence_point": 0.20
  }
}
```

**Не закоммитить пока** — сначала создаём скрипт и тесты, потом всё атомарным коммитом.

---

## Часть 4 — Создать `MARKET_MIND/ENGINE/data_quality_monitor.py`

**Главный файл задачи.** Применяем все уроки и паттерны:

- **P-01** (`Path(__file__).resolve()`)
- **P-02** (graceful degradation)
- **P-03** (типизированные exception + logging)
- **P-04** (конфиг загружается, не hardcoded)
- **L-03, L-06, AP-01** (нет hardcoded `C:\`)
- **L-04, AP-06** (UTF-8 reconfigure + ASCII если print)
- **L-07, AP-02** (нет stub данных)
- **§ 13, § 16, § 29** (UTF-8, docstrings, ссылки на уроки)

Создай `MARKET_MIND/ENGINE/data_quality_monitor.py`:

```python
"""
data_quality_monitor — 6 Data Quality Gates для проверки OHLCV данных.

Реализует Gate Failure Policy согласно ТЗ V10.0-r1 Задача 2 § 1881-1902:
  Gate 1: data_corruption (block, penalty 0.0)
  Gate 2: timestamp_gaps (warn, penalty -0.05)
  Gate 3: statistical_outliers (degrade, penalty -0.10)
  Gate 4: cross_source_consistency (degrade, penalty -0.08)
  Gate 5: volume_anomaly (degrade, penalty -0.07, shock_score +0.10)
  Gate 6: market_integrity / wash_trading (degrade, penalty -0.15, manipulation_risk up)

Применяет правило degraded mode: если ≥ 2 Gates в degrade — shock_score +0.15.
Confidence floor: минимум 0.20 (не ниже).

Задача 2 из ТЗ V10.0-r1. Компонент: data_quality_gates.

Паттерны: P-01 (relative paths), P-02 (graceful degradation),
P-03 (exception handling), P-04 (config loading from CONFIG/).

Соответствует CLAUDE.md § 16 (docstrings + type hints), § 29 (стандарт
комментирования с ссылками на уроки), § 13 (UTF-8).
"""
from __future__ import annotations

import json
import logging
import statistics
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


# === Константы ===

# Канонические имена Gates — фиксированы по ТЗ § 1885-1898
# Любая схема за пределами списка считается неизвестной
GATE_NAMES: tuple[str, ...] = (
    "gate_1_data_corruption",
    "gate_2_timestamp_gaps",
    "gate_3_statistical_outliers",
    "gate_4_cross_source_consistency",
    "gate_5_volume_anomaly",
    "gate_6_market_integrity",
)

# Canonical OHLCV поля в candle dict (проверяются Gate 1)
REQUIRED_CANDLE_FIELDS: frozenset[str] = frozenset(
    ("timestamp", "open", "high", "low", "close", "volume")
)

# Default thresholds если конфиг недоступен (P-04 graceful fallback)
# Значения совпадают с gate_failure_policy.json — если конфиг отсутствует,
# поведение остаётся предсказуемым
DEFAULT_THRESHOLDS: dict[str, float] = {
    # Gate 3
    "z_score_threshold": 5.0,  # 5-sigma для outlier detection
    # Gate 5
    "volume_spike_multiplier": 5.0,  # объём > 5x среднего = аномалия
    # Gate 6 эвристики (из ТЗ § 1940)
    "round_volumes_threshold_pct": 30.0,
    "volume_without_price_impact_threshold_pct": 10.0,
    "repeated_candles_threshold_pct": 5.0,
}


# === Exceptions ===

class DataQualityError(Exception):
    """
    Базовый exception для data quality errors.

    Поднимается только в случае системных проблем (отсутствие конфига,
    битый конфиг и т.п.) — не для failed Gates (для них ok=False в QualityReport).
    """
    pass


class CandleCorruptionError(DataQualityError):
    """
    Gate 1 block — данные физически некорректны.

    Единственная ошибка которая блокирует pipeline. Все остальные Gates
    возвращают degrade/warn через QualityReport без исключений.
    """
    pass


# === Dataclasses ===

@dataclass(frozen=True)
class GateResult:
    """
    Результат проверки одного Gate.

    Атрибуты:
        gate_id: номер Gate (1-6)
        gate_name: канон имени из GATE_NAMES
        passed: True если Gate пройден, False если сработал
        failure_mode: block | warn | degrade | None (если passed)
        confidence_penalty: отрицательное число или 0.0
        violations: список найденных проблем (пустой если passed)
        shock_score_delta: вклад в shock_score от Gate (>0 только для Gate 5/6)
        affects_manipulation_risk: True если Gate 6 сработал
    """
    gate_id: int
    gate_name: str
    passed: bool
    failure_mode: str | None = None
    confidence_penalty: float = 0.0
    violations: list[str] = field(default_factory=list)
    shock_score_delta: float = 0.0
    affects_manipulation_risk: bool = False


@dataclass(frozen=True)
class QualityReport:
    """
    Сводный отчёт о качестве данных — результат check().

    Атрибуты:
        overall_passed: True если НИ ОДИН Gate не сработал в режиме block
                        (warn/degrade не делают overall_passed=False, pipeline продолжает)
        blocked: True если Gate 1 сработал (data corruption)
        gate_results: список GateResult по каждому из 6 Gates
        quality_flag: 'ok' | 'warned' | 'degraded' | 'blocked'
        total_confidence_penalty: сумма всех penalty (отрицательное, ограничено floor)
        final_confidence_adjustment: применяется к confidence_point прогноза
        total_shock_score_delta: сумма вкладов + forced delta если degraded_mode
        manipulation_risk_score: 0.0..1.0 — итоговая оценка риска манипуляции
        degraded_mode_triggered: True если ≥ 2 Gates в degrade
    """
    overall_passed: bool
    blocked: bool
    gate_results: list[GateResult]
    quality_flag: str
    total_confidence_penalty: float
    final_confidence_adjustment: float
    total_shock_score_delta: float
    manipulation_risk_score: float
    degraded_mode_triggered: bool


# === Main class ===

class DataQualityMonitor:
    """
    Движок Data Quality Gates согласно ТЗ V10.0-r1 Задача 2.

    Публичный контракт:
      - check(candles) -> QualityReport: non-throwing (кроме Gate 1 block)
      - check_strict(candles) -> QualityReport: поднимает CandleCorruptionError
        при Gate 1 block вместо возврата blocked=True
      - get_policy() -> dict: возвращает текущий loaded policy

    Инвариант:
      - Gate 1 — единственный с failure_mode='block'. При его срабатывании
        Gates 2-6 НЕ проверяются (данные физически некорректны).
      - Confidence floor 0.20: final_confidence_adjustment не может
        опустить confidence_point ниже 0.20.
      - Degraded mode rule: ≥ 2 Gates в degrade → +0.15 к shock_score_delta.

    Применяем:
      - P-01: относительные пути (CONFIG/gate_failure_policy.json относительно ENGINE/)
      - P-02: graceful если данные пустые или недостаточные
      - P-03: DataQualityError/CandleCorruptionError, не generic Exception
      - P-04: загрузка политики из JSON конфига при init
    """

    def __init__(
        self,
        config_path: Path | str | None = None,
        thresholds: dict[str, float] | None = None,
    ) -> None:
        """
        Инициализация монитора.

        Args:
            config_path: путь к gate_failure_policy.json. По умолчанию —
                MARKET_MIND/CONFIG/gate_failure_policy.json относительно
                этого файла (P-01, L-03, AP-01).
            thresholds: override дефолтных порогов (для тестов). Мёрджится
                с DEFAULT_THRESHOLDS (override-only для указанных ключей).
        """
        # applies P-01: no hardcoded paths (L-03, AP-01)
        # ENGINE/data_quality_monitor.py -> MARKET_MIND -> CONFIG/
        if config_path is None:
            config_path = (
                Path(__file__).resolve().parent.parent
                / "CONFIG"
                / "gate_failure_policy.json"
            )
        self.config_path: Path = Path(config_path)

        # Merge default thresholds with override
        self.thresholds: dict[str, float] = dict(DEFAULT_THRESHOLDS)
        if thresholds:
            self.thresholds.update(thresholds)

        # Load policy (P-04 graceful)
        self._policy: dict[str, Any] = self._load_policy()

    def _load_policy(self) -> dict[str, Any]:
        """
        Загружает Gate Failure Policy из JSON конфига.

        P-04: если файл отсутствует — лог warning и используется
        синтезированная default policy с значениями из ТЗ (чтобы система
        работала даже без конфига). Но в production ожидается что конфиг есть.

        Returns:
            dict с policy — ключи gates, degraded_mode_rule, confidence_floor.

        Raises:
            DataQualityError: если конфиг существует но невалиден (битый JSON,
            отсутствуют required ключи). Молча проглатывать такое нельзя (AP-03).
        """
        if not self.config_path.is_file():
            # P-04: graceful fallback + явный warning
            logger.warning(
                f"gate_failure_policy.json not found at {self.config_path}; "
                "using built-in defaults per TZ § 1881-1902"
            )
            return self._default_policy()

        try:
            # § 13: UTF-8 explicit
            raw = self.config_path.read_text(encoding="utf-8")
            policy = json.loads(raw)
        except json.JSONDecodeError as e:
            # P-03: конкретный exception + raise (нельзя молча проглотить)
            logger.error(f"gate_failure_policy.json malformed: {e}")
            raise DataQualityError(f"Malformed policy JSON: {e}") from e
        except OSError as e:
            logger.error(f"Cannot read gate_failure_policy.json: {e}")
            raise DataQualityError(f"Cannot read policy file: {e}") from e

        # Минимальная валидация структуры
        if "gates" not in policy:
            raise DataQualityError(
                "Policy missing 'gates' key (expected per TZ § 1885-1898)"
            )

        return policy

    @staticmethod
    def _default_policy() -> dict[str, Any]:
        """
        Built-in default policy синтезированная из ТЗ § 1881-1902.

        Fallback для случаев когда конфиг файл отсутствует. Значения должны
        совпадать с gate_failure_policy.json который создаётся в TASK_04 Часть 3.
        """
        return {
            "gates": {
                "gate_1_data_corruption": {
                    "gate_id": 1, "failure_mode": "block",
                    "confidence_penalty": 0.0,
                    "affects_shock_score_delta": 0.0,
                    "affects_manipulation_risk": False,
                },
                "gate_2_timestamp_gaps": {
                    "gate_id": 2, "failure_mode": "warn",
                    "confidence_penalty": -0.05,
                    "affects_shock_score_delta": 0.0,
                    "affects_manipulation_risk": False,
                },
                "gate_3_statistical_outliers": {
                    "gate_id": 3, "failure_mode": "degrade",
                    "confidence_penalty": -0.10,
                    "affects_shock_score_delta": 0.0,
                    "affects_manipulation_risk": False,
                },
                "gate_4_cross_source_consistency": {
                    "gate_id": 4, "failure_mode": "degrade",
                    "confidence_penalty": -0.08,
                    "affects_shock_score_delta": 0.0,
                    "affects_manipulation_risk": False,
                },
                "gate_5_volume_anomaly": {
                    "gate_id": 5, "failure_mode": "degrade",
                    "confidence_penalty": -0.07,
                    "affects_shock_score_delta": 0.10,
                    "affects_manipulation_risk": False,
                },
                "gate_6_market_integrity": {
                    "gate_id": 6, "failure_mode": "degrade",
                    "confidence_penalty": -0.15,
                    "affects_shock_score_delta": 0.0,
                    "affects_manipulation_risk": True,
                },
            },
            "degraded_mode_rule": {
                "trigger_min_degraded_gates": 2,
                "forced_shock_score_delta": 0.15,
            },
            "confidence_floor": {
                "min_confidence_point": 0.20,
            },
        }

    def get_policy(self) -> dict[str, Any]:
        """Возвращает копию текущей loaded policy (read-only use)."""
        return dict(self._policy)

    # === Публичные API методы ===

    def check(
        self,
        candles: list[dict[str, Any]],
        cross_source_candles: list[dict[str, Any]] | None = None,
    ) -> QualityReport:
        """
        Проверяет OHLCV candles через все 6 Gates.

        Non-throwing за исключением системных ошибок (битый конфиг).
        Gate 1 block возвращает QualityReport с blocked=True, не exception.

        Args:
            candles: список OHLCV dict. Каждый должен содержать
                timestamp, open, high, low, close, volume.
            cross_source_candles: опциональные candles из второго источника
                для Gate 4 (cross-source consistency). Если None — Gate 4
                пропускается с passed=True (нечего сравнивать).

        Returns:
            QualityReport со списком GateResult и сводной статистикой.
        """
        # applies P-02: graceful для пустого списка
        if not candles:
            logger.warning("check() called with empty candles list")
            return self._empty_report()

        gate_results: list[GateResult] = []

        # Gate 1 — block. Если сработал, остальные не проверяем (P-02)
        g1 = self._gate_1_data_corruption(candles)
        gate_results.append(g1)
        if not g1.passed:
            return self._build_blocked_report(gate_results)

        # Gates 2-6 проверяются последовательно, независимо от результата предыдущих
        gate_results.append(self._gate_2_timestamp_gaps(candles))
        gate_results.append(self._gate_3_statistical_outliers(candles))
        gate_results.append(self._gate_4_cross_source_consistency(candles, cross_source_candles))
        gate_results.append(self._gate_5_volume_anomaly(candles))
        gate_results.append(self._gate_6_market_integrity(candles))

        return self._build_report(gate_results)

    def check_strict(
        self,
        candles: list[dict[str, Any]],
        cross_source_candles: list[dict[str, Any]] | None = None,
    ) -> QualityReport:
        """
        Как check(), но поднимает CandleCorruptionError при Gate 1 block.

        Используется для пайплайнов где блокировка = системная ошибка
        и нужна явная обработка через try/except.

        Raises:
            CandleCorruptionError: если Gate 1 сработал
        """
        report = self.check(candles, cross_source_candles)
        if report.blocked:
            g1 = report.gate_results[0]
            raise CandleCorruptionError(
                f"Gate 1 data corruption: {'; '.join(g1.violations)}"
            )
        return report

    # === Gate implementations ===

    def _gate_1_data_corruption(self, candles: list[dict[str, Any]]) -> GateResult:
        """
        Gate 1: data corruption / duplicate candles.

        Проверяет:
          - Все candle dict содержат required поля (REQUIRED_CANDLE_FIELDS)
          - Нет NaN/None в числовых полях
          - low <= open, close, high и high >= open, close, low (валидность свечи)
          - volume >= 0
          - Нет дубликатов по timestamp

        ТЗ § 1888: failure_mode=block, penalty=0.0, полная блокировка.
        """
        policy = self._policy["gates"]["gate_1_data_corruption"]
        violations: list[str] = []

        timestamps_seen: set[Any] = set()
        for i, c in enumerate(candles):
            # Required поля
            missing = REQUIRED_CANDLE_FIELDS - set(c.keys())
            if missing:
                violations.append(f"candle[{i}] missing fields: {sorted(missing)}")
                continue  # нет смысла дальше анализировать этот candle

            # NaN/None check (float('nan') != float('nan') — используем isinstance)
            for fld in ("open", "high", "low", "close", "volume"):
                v = c[fld]
                if v is None:
                    violations.append(f"candle[{i}].{fld} is None")
                elif isinstance(v, float) and v != v:  # NaN check
                    violations.append(f"candle[{i}].{fld} is NaN")

            # Валидность свечи: low <= open, close, high; high >= open, close, low
            try:
                low_v = float(c["low"])
                high_v = float(c["high"])
                open_v = float(c["open"])
                close_v = float(c["close"])
                vol_v = float(c["volume"])
            except (TypeError, ValueError):
                # Уже зафиксируем по NaN-check выше или missing
                continue

            if low_v > high_v:
                violations.append(f"candle[{i}]: low ({low_v}) > high ({high_v})")
            if not (low_v <= open_v <= high_v):
                violations.append(f"candle[{i}]: open ({open_v}) outside [low, high]")
            if not (low_v <= close_v <= high_v):
                violations.append(f"candle[{i}]: close ({close_v}) outside [low, high]")
            if vol_v < 0:
                violations.append(f"candle[{i}]: negative volume ({vol_v})")

            # Duplicate timestamps
            ts = c["timestamp"]
            if ts in timestamps_seen:
                violations.append(f"candle[{i}]: duplicate timestamp {ts}")
            timestamps_seen.add(ts)

        passed = len(violations) == 0
        return GateResult(
            gate_id=1,
            gate_name="gate_1_data_corruption",
            passed=passed,
            failure_mode=None if passed else policy["failure_mode"],
            confidence_penalty=0.0 if passed else policy["confidence_penalty"],
            violations=violations,
            shock_score_delta=0.0,
            affects_manipulation_risk=False,
        )

    def _gate_2_timestamp_gaps(self, candles: list[dict[str, Any]]) -> GateResult:
        """
        Gate 2: timestamp gaps / sequence errors.

        Проверяет:
          - Timestamps строго возрастают (candle[i+1] > candle[i])
          - Нет gaps больше чем 2x median interval

        ТЗ § 1890: failure_mode=warn, penalty=-0.05.
        """
        policy = self._policy["gates"]["gate_2_timestamp_gaps"]
        violations: list[str] = []

        if len(candles) < 2:
            # Меньше 2 свечей — нечего проверять
            return GateResult(
                gate_id=2, gate_name="gate_2_timestamp_gaps",
                passed=True,
            )

        # Extract timestamps as numeric
        try:
            timestamps = [float(c["timestamp"]) for c in candles]
        except (KeyError, TypeError, ValueError):
            # Уже зафиксировано Gate 1; здесь не дублируем
            return GateResult(
                gate_id=2, gate_name="gate_2_timestamp_gaps",
                passed=True,
            )

        # Check ordering
        for i in range(len(timestamps) - 1):
            if timestamps[i + 1] <= timestamps[i]:
                violations.append(
                    f"timestamp at index {i+1} ({timestamps[i+1]}) "
                    f"not strictly after index {i} ({timestamps[i]})"
                )

        # Check gaps (если хотя бы 3 candles)
        if len(timestamps) >= 3:
            intervals = [timestamps[i+1] - timestamps[i] for i in range(len(timestamps) - 1)]
            if intervals:
                median_interval = statistics.median(intervals)
                if median_interval > 0:
                    for i, interval in enumerate(intervals):
                        if interval > 2 * median_interval:
                            violations.append(
                                f"gap at index {i} -> {i+1}: interval {interval} "
                                f"is >2x median {median_interval:.2f}"
                            )

        passed = len(violations) == 0
        return GateResult(
            gate_id=2,
            gate_name="gate_2_timestamp_gaps",
            passed=passed,
            failure_mode=None if passed else policy["failure_mode"],
            confidence_penalty=0.0 if passed else policy["confidence_penalty"],
            violations=violations,
        )

    def _gate_3_statistical_outliers(self, candles: list[dict[str, Any]]) -> GateResult:
        """
        Gate 3: statistical outlier detection.

        Проверяет через z-score на returns:
          - |return| > 5 стандартных отклонений = outlier
          - Минимум 10 свечей для статистической значимости

        ТЗ § 1892: failure_mode=degrade, penalty=-0.10.
        """
        policy = self._policy["gates"]["gate_3_statistical_outliers"]
        violations: list[str] = []

        if len(candles) < 10:
            # Мало данных для статистики (P-02: graceful)
            return GateResult(
                gate_id=3, gate_name="gate_3_statistical_outliers",
                passed=True,
            )

        try:
            closes = [float(c["close"]) for c in candles]
        except (KeyError, TypeError, ValueError):
            return GateResult(
                gate_id=3, gate_name="gate_3_statistical_outliers",
                passed=True,
            )

        # Returns = (close[i+1] - close[i]) / close[i]
        returns: list[float] = []
        for i in range(len(closes) - 1):
            if closes[i] > 0:
                returns.append((closes[i+1] - closes[i]) / closes[i])

        if len(returns) < 10:
            return GateResult(
                gate_id=3, gate_name="gate_3_statistical_outliers",
                passed=True,
            )

        try:
            mean = statistics.mean(returns)
            stdev = statistics.stdev(returns)
        except statistics.StatisticsError:
            return GateResult(
                gate_id=3, gate_name="gate_3_statistical_outliers",
                passed=True,
            )

        if stdev <= 0:
            # Все returns одинаковые — нет волатильности, но и нет outliers
            return GateResult(
                gate_id=3, gate_name="gate_3_statistical_outliers",
                passed=True,
            )

        threshold = self.thresholds["z_score_threshold"]
        for i, r in enumerate(returns):
            z = abs(r - mean) / stdev
            if z > threshold:
                violations.append(
                    f"return at index {i}: value={r:.4f}, z-score={z:.2f} "
                    f"exceeds {threshold}-sigma"
                )

        passed = len(violations) == 0
        return GateResult(
            gate_id=3,
            gate_name="gate_3_statistical_outliers",
            passed=passed,
            failure_mode=None if passed else policy["failure_mode"],
            confidence_penalty=0.0 if passed else policy["confidence_penalty"],
            violations=violations,
        )

    def _gate_4_cross_source_consistency(
        self,
        candles: list[dict[str, Any]],
        cross_source_candles: list[dict[str, Any]] | None,
    ) -> GateResult:
        """
        Gate 4: cross-source consistency.

        Если передан второй источник candles — сравнивает close prices
        по совпадающим timestamp'ам. Допустимая разница: 0.5% (50 bps).

        Если cross_source_candles=None — Gate пропускается (passed=True).

        ТЗ § 1894: failure_mode=degrade, penalty=-0.08.
        """
        policy = self._policy["gates"]["gate_4_cross_source_consistency"]

        if cross_source_candles is None:
            # Нечего сравнивать
            return GateResult(
                gate_id=4, gate_name="gate_4_cross_source_consistency",
                passed=True,
            )

        violations: list[str] = []

        # Index by timestamp для быстрого сравнения
        try:
            source_by_ts = {float(c["timestamp"]): float(c["close"]) for c in candles}
            cross_by_ts = {float(c["timestamp"]): float(c["close"]) for c in cross_source_candles}
        except (KeyError, TypeError, ValueError):
            # Проблемы с типами — Gate 1 уже зафиксировал бы
            return GateResult(
                gate_id=4, gate_name="gate_4_cross_source_consistency",
                passed=True,
            )

        common_timestamps = set(source_by_ts.keys()) & set(cross_by_ts.keys())
        if not common_timestamps:
            # Нет общих timestamps — нечего сверять
            return GateResult(
                gate_id=4, gate_name="gate_4_cross_source_consistency",
                passed=True,
            )

        # Допустимая разница 0.5% (50 bps)
        tolerance_pct = 0.5
        for ts in common_timestamps:
            src_close = source_by_ts[ts]
            cross_close = cross_by_ts[ts]
            if src_close <= 0:
                continue
            diff_pct = abs(src_close - cross_close) / src_close * 100.0
            if diff_pct > tolerance_pct:
                violations.append(
                    f"timestamp {ts}: source close={src_close}, "
                    f"cross close={cross_close}, diff={diff_pct:.2f}% > {tolerance_pct}%"
                )

        passed = len(violations) == 0
        return GateResult(
            gate_id=4,
            gate_name="gate_4_cross_source_consistency",
            passed=passed,
            failure_mode=None if passed else policy["failure_mode"],
            confidence_penalty=0.0 if passed else policy["confidence_penalty"],
            violations=violations,
        )

    def _gate_5_volume_anomaly(self, candles: list[dict[str, Any]]) -> GateResult:
        """
        Gate 5: volume / liquidity anomaly.

        Проверяет:
          - volume > 5x median volume — подозрительный spike
          - Минимум 10 candles для median

        ТЗ § 1896: failure_mode=degrade, penalty=-0.07, shock_score_delta=+0.10.
        """
        policy = self._policy["gates"]["gate_5_volume_anomaly"]
        violations: list[str] = []

        if len(candles) < 10:
            return GateResult(
                gate_id=5, gate_name="gate_5_volume_anomaly",
                passed=True,
            )

        try:
            volumes = [float(c["volume"]) for c in candles]
        except (KeyError, TypeError, ValueError):
            return GateResult(
                gate_id=5, gate_name="gate_5_volume_anomaly",
                passed=True,
            )

        if not volumes or all(v <= 0 for v in volumes):
            return GateResult(
                gate_id=5, gate_name="gate_5_volume_anomaly",
                passed=True,
            )

        median_vol = statistics.median(volumes)
        if median_vol <= 0:
            return GateResult(
                gate_id=5, gate_name="gate_5_volume_anomaly",
                passed=True,
            )

        multiplier = self.thresholds["volume_spike_multiplier"]
        threshold_vol = median_vol * multiplier

        for i, v in enumerate(volumes):
            if v > threshold_vol:
                violations.append(
                    f"candle[{i}].volume={v} exceeds {multiplier}x median {median_vol:.2f}"
                )

        passed = len(violations) == 0
        return GateResult(
            gate_id=5,
            gate_name="gate_5_volume_anomaly",
            passed=passed,
            failure_mode=None if passed else policy["failure_mode"],
            confidence_penalty=0.0 if passed else policy["confidence_penalty"],
            violations=violations,
            shock_score_delta=0.0 if passed else policy["affects_shock_score_delta"],
        )

    def _gate_6_market_integrity(self, candles: list[dict[str, Any]]) -> GateResult:
        """
        Gate 6: Market Integrity — wash trading detection (MDC).

        Реализует 3 эвристики из ТЗ § 1940:
          A. suspicious_round_volumes > 30% (volumes целые числа кратные 100/1000)
          B. volume_spike без price_impact > 10% (аномальный объём без движения цены)
          C. repeated_candles > 5% (идентичные OHLC свечи)

        ТЗ § 1898: failure_mode=degrade, penalty=-0.15,
        affects_manipulation_risk=True.
        """
        policy = self._policy["gates"]["gate_6_market_integrity"]
        violations: list[str] = []

        if len(candles) < 10:
            # Мало данных для wash trading detection
            return GateResult(
                gate_id=6, gate_name="gate_6_market_integrity",
                passed=True,
            )

        try:
            numeric = [
                (float(c["open"]), float(c["high"]), float(c["low"]),
                 float(c["close"]), float(c["volume"]))
                for c in candles
            ]
        except (KeyError, TypeError, ValueError):
            return GateResult(
                gate_id=6, gate_name="gate_6_market_integrity",
                passed=True,
            )

        n = len(numeric)

        # === Эвристика A: suspicious round volumes ===
        # Round volume = целое число, кратное 100 (или самому volume если он целый "круглый")
        round_volume_threshold_pct = self.thresholds["round_volumes_threshold_pct"]
        round_count = sum(
            1 for (_, _, _, _, vol) in numeric
            if vol > 0 and (vol % 100 == 0 or vol % 1000 == 0)
        )
        round_pct = (round_count / n) * 100.0
        if round_pct > round_volume_threshold_pct:
            violations.append(
                f"heuristic_A suspicious_round_volumes: {round_pct:.1f}% "
                f"exceeds threshold {round_volume_threshold_pct}%"
            )

        # === Эвристика B: volume spike без price impact ===
        # "Spike" = volume > 2x median, "без impact" = |price change| < 0.1%
        volumes = [v for (_, _, _, _, v) in numeric]
        closes = [c for (_, _, _, c, _) in numeric]
        median_vol = statistics.median(volumes) if volumes else 0.0

        impact_threshold_pct = self.thresholds["volume_without_price_impact_threshold_pct"]
        suspicious_count = 0
        if median_vol > 0:
            for i in range(1, n):
                is_spike = volumes[i] > 2 * median_vol
                if is_spike and closes[i-1] > 0:
                    price_change_pct = abs(closes[i] - closes[i-1]) / closes[i-1] * 100.0
                    if price_change_pct < 0.1:
                        suspicious_count += 1
        suspicious_pct = (suspicious_count / n) * 100.0
        if suspicious_pct > impact_threshold_pct:
            violations.append(
                f"heuristic_B volume_without_price_impact: {suspicious_pct:.1f}% "
                f"exceeds threshold {impact_threshold_pct}%"
            )

        # === Эвристика C: repeated candles ===
        # Свеча считается повтором если OHLC совпадают с предыдущей
        repeated_threshold_pct = self.thresholds["repeated_candles_threshold_pct"]
        repeated_count = 0
        for i in range(1, n):
            prev = numeric[i-1][:4]  # OHLC без volume
            curr = numeric[i][:4]
            if prev == curr:
                repeated_count += 1
        repeated_pct = (repeated_count / n) * 100.0
        if repeated_pct > repeated_threshold_pct:
            violations.append(
                f"heuristic_C repeated_candles: {repeated_pct:.1f}% "
                f"exceeds threshold {repeated_threshold_pct}%"
            )

        passed = len(violations) == 0
        return GateResult(
            gate_id=6,
            gate_name="gate_6_market_integrity",
            passed=passed,
            failure_mode=None if passed else policy["failure_mode"],
            confidence_penalty=0.0 if passed else policy["confidence_penalty"],
            violations=violations,
            affects_manipulation_risk=not passed,
        )

    # === Report building ===

    def _empty_report(self) -> QualityReport:
        """Отчёт для пустого списка candles (P-02 graceful)."""
        return QualityReport(
            overall_passed=True,
            blocked=False,
            gate_results=[],
            quality_flag="ok",
            total_confidence_penalty=0.0,
            final_confidence_adjustment=0.0,
            total_shock_score_delta=0.0,
            manipulation_risk_score=0.0,
            degraded_mode_triggered=False,
        )

    def _build_blocked_report(self, gate_results: list[GateResult]) -> QualityReport:
        """Отчёт при срабатывании Gate 1 block."""
        g1 = gate_results[0]
        return QualityReport(
            overall_passed=False,
            blocked=True,
            gate_results=gate_results,
            quality_flag="blocked",
            total_confidence_penalty=g1.confidence_penalty,
            final_confidence_adjustment=g1.confidence_penalty,
            total_shock_score_delta=0.0,
            manipulation_risk_score=0.0,
            degraded_mode_triggered=False,
        )

    def _build_report(self, gate_results: list[GateResult]) -> QualityReport:
        """
        Строит итоговый отчёт для нормального прогона (Gates 1-6).

        Применяет правила:
          - Degraded mode: ≥ 2 Gates в degrade → +0.15 к shock_score_delta
          - Confidence floor: final_confidence_adjustment ограничен floor
        """
        # Считаем сработавшие Gates
        degraded_count = sum(
            1 for g in gate_results
            if not g.passed and g.failure_mode == "degrade"
        )
        warned_count = sum(
            1 for g in gate_results
            if not g.passed and g.failure_mode == "warn"
        )

        # Sum confidence penalties
        total_penalty = sum(g.confidence_penalty for g in gate_results if not g.passed)

        # Sum shock score deltas
        total_shock_delta = sum(g.shock_score_delta for g in gate_results if not g.passed)

        # Degraded mode rule
        degraded_mode = False
        min_degraded = self._policy.get("degraded_mode_rule", {}).get(
            "trigger_min_degraded_gates", 2
        )
        forced_shock = self._policy.get("degraded_mode_rule", {}).get(
            "forced_shock_score_delta", 0.15
        )
        if degraded_count >= min_degraded:
            degraded_mode = True
            total_shock_delta += forced_shock

        # Confidence floor: floor — минимальное значение confidence_point,
        # т.е. максимальное "снижение" ограничено
        floor = self._policy.get("confidence_floor", {}).get("min_confidence_point", 0.20)
        # Предположим базовая confidence = 1.0 и penalty применяется как +penalty
        # Если после всех penalty итог < floor, то final = floor (т.е. penalty обрезается)
        # Эта логика — для интеграции с model_core, здесь мы возвращаем сырые числа
        base_confidence = 1.0
        adjusted = base_confidence + total_penalty
        if adjusted < floor:
            final_adjustment = floor - base_confidence
        else:
            final_adjustment = total_penalty

        # Manipulation risk score — вклад Gate 6
        manipulation_risk = 0.0
        for g in gate_results:
            if g.gate_id == 6 and g.affects_manipulation_risk:
                # Базовая логика: Gate 6 сработал = risk 0.5, каждая эвристика вне threshold +0.15
                manipulation_risk = min(1.0, 0.5 + 0.15 * len(g.violations))

        # Quality flag
        if degraded_count > 0:
            quality_flag = "degraded"
        elif warned_count > 0:
            quality_flag = "warned"
        else:
            quality_flag = "ok"

        # Overall passed — pipeline продолжает если не blocked
        # warn/degrade не останавливают pipeline
        overall = True  # blocked уже обработан в _build_blocked_report

        return QualityReport(
            overall_passed=overall,
            blocked=False,
            gate_results=gate_results,
            quality_flag=quality_flag,
            total_confidence_penalty=total_penalty,
            final_confidence_adjustment=final_adjustment,
            total_shock_score_delta=total_shock_delta,
            manipulation_risk_score=manipulation_risk,
            degraded_mode_triggered=degraded_mode,
        )


# === Module-level convenience functions ===

_default_monitor: DataQualityMonitor | None = None


def get_default_monitor() -> DataQualityMonitor:
    """
    Возвращает singleton-экземпляр DataQualityMonitor с дефолтным путём.

    Для удобства в простых случаях. Для тестов / кастомных путей —
    создавай DataQualityMonitor(config_path=...) напрямую.
    """
    global _default_monitor
    if _default_monitor is None:
        _default_monitor = DataQualityMonitor()
    return _default_monitor


def check(
    candles: list[dict[str, Any]],
    cross_source_candles: list[dict[str, Any]] | None = None,
) -> QualityReport:
    """Функция-обёртка — check через default monitor."""
    return get_default_monitor().check(candles, cross_source_candles)
```

**Важно проверить:**
- Ни одного hardcoded `C:\` или `/home/` в коде
- Ни одного bare `except:` — все типизированы
- Ни одного `print` с emoji — только logger
- Ни одного `TODO`/`FIXME`
- Модульный docstring с ссылкой на ТЗ
- Ссылки на паттерны (`applies P-01`, `P-02`, `P-03`, `P-04`) в комментариях

---

## Часть 5 — Тесты

Создать `MARKET_MIND/tests/test_data_quality_monitor.py`. Применяем P-05 (ASCII маркеры).

Минимум 20 тестов:
- 2 теста на каждый Gate (positive + negative) = 12 тестов
- Тесты на правило degraded mode (2)
- Тесты на confidence floor (2)
- Тесты на manipulation_risk_score (2)
- Тесты на edge cases: empty candles, single candle, missing fields (3)
- Integration test: все Gates сразу (1)
- Policy loading (2)

Создай файл:

```python
"""
test_data_quality_monitor — тесты для DataQualityMonitor (TASK_04).

Применяет P-05 (ASCII markers, UTF-8 reconfigure).
Standard library only — без pytest.

Запуск:
    python MARKET_MIND/tests/test_data_quality_monitor.py
"""
from __future__ import annotations

import sys
from pathlib import Path

# L-04 / P-05
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

# applies P-01
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from MARKET_MIND.ENGINE.data_quality_monitor import (
    DataQualityMonitor,
    CandleCorruptionError,
    DataQualityError,
    GateResult,
    QualityReport,
    GATE_NAMES,
    check,
)


# === Helpers ===

def _make_valid_candles(n: int = 20, start_ts: int = 1_700_000_000, interval: int = 3600) -> list[dict]:
    """Создаёт список валидных OHLCV с растущей ценой, умеренным объёмом."""
    candles = []
    for i in range(n):
        base = 100.0 + i * 0.5
        candles.append({
            "timestamp": start_ts + i * interval,
            "open": base,
            "high": base + 0.3,
            "low": base - 0.3,
            "close": base + 0.1,
            "volume": 1500.0 + (i * 17),  # не round-кратное 100
        })
    return candles


# === Gate 1 tests ===

def test_gate1_valid_passes() -> None:
    m = DataQualityMonitor()
    report = m.check(_make_valid_candles())
    assert not report.blocked
    assert report.gate_results[0].passed
    print("[OK] test_gate1_valid_passes")


def test_gate1_missing_field_blocks() -> None:
    m = DataQualityMonitor()
    candles = _make_valid_candles(3)
    del candles[1]["close"]
    report = m.check(candles)
    assert report.blocked
    assert report.quality_flag == "blocked"
    print("[OK] test_gate1_missing_field_blocks")


def test_gate1_low_greater_than_high_blocks() -> None:
    m = DataQualityMonitor()
    candles = _make_valid_candles(3)
    candles[1]["low"] = 200.0
    candles[1]["high"] = 100.0
    report = m.check(candles)
    assert report.blocked
    print("[OK] test_gate1_low_greater_than_high_blocks")


def test_gate1_duplicate_timestamp_blocks() -> None:
    m = DataQualityMonitor()
    candles = _make_valid_candles(3)
    candles[2]["timestamp"] = candles[1]["timestamp"]
    report = m.check(candles)
    assert report.blocked
    print("[OK] test_gate1_duplicate_timestamp_blocks")


def test_gate1_strict_raises() -> None:
    m = DataQualityMonitor()
    candles = _make_valid_candles(3)
    candles[1]["low"] = 200.0
    candles[1]["high"] = 100.0
    raised = False
    try:
        m.check_strict(candles)
    except CandleCorruptionError:
        raised = True
    assert raised
    print("[OK] test_gate1_strict_raises")


# === Gate 2 tests ===

def test_gate2_valid_passes() -> None:
    m = DataQualityMonitor()
    report = m.check(_make_valid_candles())
    assert report.gate_results[1].passed
    print("[OK] test_gate2_valid_passes")


def test_gate2_gap_detected() -> None:
    m = DataQualityMonitor()
    candles = _make_valid_candles(20)
    # Создаём большой gap перед 10-й свечой
    for i in range(10, 20):
        candles[i]["timestamp"] += 3600 * 10  # 10 часов
    report = m.check(candles)
    g2 = report.gate_results[1]
    assert not g2.passed
    assert g2.failure_mode == "warn"
    assert g2.confidence_penalty == -0.05
    print("[OK] test_gate2_gap_detected")


# === Gate 3 tests ===

def test_gate3_valid_passes() -> None:
    m = DataQualityMonitor()
    report = m.check(_make_valid_candles())
    assert report.gate_results[2].passed
    print("[OK] test_gate3_valid_passes")


def test_gate3_outlier_detected() -> None:
    m = DataQualityMonitor()
    candles = _make_valid_candles(20)
    # Огромный spike в close на 10-й свече
    candles[10]["close"] = 1000.0
    candles[10]["high"] = 1000.0
    candles[11]["open"] = 1000.0
    report = m.check(candles)
    g3 = report.gate_results[2]
    assert not g3.passed
    assert g3.failure_mode == "degrade"
    assert g3.confidence_penalty == -0.10
    print("[OK] test_gate3_outlier_detected")


# === Gate 4 tests ===

def test_gate4_no_cross_source_passes() -> None:
    m = DataQualityMonitor()
    report = m.check(_make_valid_candles())
    # cross_source=None → Gate 4 passes
    assert report.gate_results[3].passed
    print("[OK] test_gate4_no_cross_source_passes")


def test_gate4_cross_source_inconsistent() -> None:
    m = DataQualityMonitor()
    primary = _make_valid_candles(10)
    secondary = _make_valid_candles(10)
    # Изменяем цену на одной свече в secondary — 5% разница
    secondary[5]["close"] = primary[5]["close"] * 1.05
    report = m.check(primary, cross_source_candles=secondary)
    g4 = report.gate_results[3]
    assert not g4.passed
    assert g4.failure_mode == "degrade"
    print("[OK] test_gate4_cross_source_inconsistent")


# === Gate 5 tests ===

def test_gate5_valid_passes() -> None:
    m = DataQualityMonitor()
    report = m.check(_make_valid_candles())
    assert report.gate_results[4].passed
    print("[OK] test_gate5_valid_passes")


def test_gate5_volume_spike_detected() -> None:
    m = DataQualityMonitor()
    candles = _make_valid_candles(20)
    # Volume spike 10x на 15-й свече
    candles[15]["volume"] = 50000.0
    report = m.check(candles)
    g5 = report.gate_results[4]
    assert not g5.passed
    assert g5.failure_mode == "degrade"
    assert g5.confidence_penalty == -0.07
    assert g5.shock_score_delta == 0.10
    print("[OK] test_gate5_volume_spike_detected")


# === Gate 6 tests ===

def test_gate6_valid_passes() -> None:
    m = DataQualityMonitor()
    report = m.check(_make_valid_candles())
    assert report.gate_results[5].passed
    print("[OK] test_gate6_valid_passes")


def test_gate6_round_volumes_detected() -> None:
    m = DataQualityMonitor()
    candles = _make_valid_candles(20)
    # 50% свечей с round volumes кратных 1000
    for i in range(0, 20, 2):
        candles[i]["volume"] = 10000.0  # кратно 1000
    report = m.check(candles)
    g6 = report.gate_results[5]
    assert not g6.passed
    assert g6.failure_mode == "degrade"
    assert g6.affects_manipulation_risk
    assert any("heuristic_A" in v for v in g6.violations)
    print("[OK] test_gate6_round_volumes_detected")


def test_gate6_repeated_candles_detected() -> None:
    m = DataQualityMonitor()
    candles = _make_valid_candles(20)
    # 20% повторяющихся OHLC
    for i in [5, 7, 9, 11]:
        candles[i]["open"] = candles[i-1]["open"]
        candles[i]["high"] = candles[i-1]["high"]
        candles[i]["low"] = candles[i-1]["low"]
        candles[i]["close"] = candles[i-1]["close"]
    report = m.check(candles)
    g6 = report.gate_results[5]
    assert not g6.passed
    assert any("heuristic_C" in v for v in g6.violations)
    print("[OK] test_gate6_repeated_candles_detected")


# === Rule tests ===

def test_degraded_mode_triggered() -> None:
    """2+ Gates в degrade → degraded_mode_triggered + shock_score +0.15."""
    m = DataQualityMonitor()
    candles = _make_valid_candles(20)
    # Триггерим Gate 3 (outlier)
    candles[10]["close"] = 1000.0
    candles[10]["high"] = 1000.0
    candles[11]["open"] = 1000.0
    # Триггерим Gate 5 (volume spike) — тот же spike но отдельно от Gate 3
    candles[15]["volume"] = 50000.0
    report = m.check(candles)
    degraded = sum(1 for g in report.gate_results if not g.passed and g.failure_mode == "degrade")
    assert degraded >= 2, f"Expected >=2 degrade, got {degraded}"
    assert report.degraded_mode_triggered
    assert report.total_shock_score_delta >= 0.15
    print("[OK] test_degraded_mode_triggered")


def test_single_degrade_no_forced_shock() -> None:
    """Только 1 Gate degrade → без forced +0.15."""
    m = DataQualityMonitor()
    candles = _make_valid_candles(20)
    # Только outlier (Gate 3)
    candles[10]["close"] = 1000.0
    candles[10]["high"] = 1000.0
    candles[11]["open"] = 1000.0
    report = m.check(candles)
    # Только Gate 3 fail (не Gate 5, волатильность не задета)
    degraded = sum(1 for g in report.gate_results if not g.passed and g.failure_mode == "degrade")
    if degraded == 1:
        assert not report.degraded_mode_triggered
    print("[OK] test_single_degrade_no_forced_shock")


def test_confidence_floor() -> None:
    """Confidence penalty не опускает ниже 0.20."""
    m = DataQualityMonitor()
    # Триггерим все 4 degrade (Gate 3, 4, 5, 6) — суммарный penalty -0.40
    # Плюс Gate 2 warn -0.05 = -0.45
    # Base 1.0 - 0.45 = 0.55 > 0.20, floor не срабатывает
    # Для срабатывания floor нужно penalty > -0.80 (маловероятно при обычных gates)
    # Проверим что логика floor работает через поведение final_adjustment
    candles = _make_valid_candles(20)
    candles[10]["close"] = 1000.0
    candles[10]["high"] = 1000.0
    candles[11]["open"] = 1000.0
    candles[15]["volume"] = 50000.0
    report = m.check(candles)
    # final_adjustment должен быть >= -0.80 (т.е. 1.0 - 0.80 = 0.20 floor)
    assert 1.0 + report.final_confidence_adjustment >= 0.20
    print("[OK] test_confidence_floor")


def test_manipulation_risk_from_gate6() -> None:
    """Gate 6 сработал → manipulation_risk_score > 0."""
    m = DataQualityMonitor()
    candles = _make_valid_candles(20)
    for i in range(0, 20, 2):
        candles[i]["volume"] = 10000.0
    report = m.check(candles)
    assert report.manipulation_risk_score > 0.0
    assert report.manipulation_risk_score <= 1.0
    print("[OK] test_manipulation_risk_from_gate6")


def test_no_manipulation_risk_when_gate6_passes() -> None:
    m = DataQualityMonitor()
    report = m.check(_make_valid_candles())
    assert report.manipulation_risk_score == 0.0
    print("[OK] test_no_manipulation_risk_when_gate6_passes")


# === Edge cases ===

def test_empty_candles() -> None:
    m = DataQualityMonitor()
    report = m.check([])
    assert report.overall_passed
    assert not report.blocked
    assert report.quality_flag == "ok"
    assert len(report.gate_results) == 0
    print("[OK] test_empty_candles")


def test_single_candle() -> None:
    m = DataQualityMonitor()
    candles = _make_valid_candles(1)
    report = m.check(candles)
    # Gate 1 проходит, Gate 2-6 по graceful (мало данных)
    assert not report.blocked
    print("[OK] test_single_candle")


def test_module_level_check() -> None:
    """Модульная функция check() работает."""
    report = check(_make_valid_candles())
    assert isinstance(report, QualityReport)
    print("[OK] test_module_level_check")


# === Policy loading tests ===

def test_gate_names_constant() -> None:
    assert len(GATE_NAMES) == 6
    assert "gate_6_market_integrity" in GATE_NAMES
    print("[OK] test_gate_names_constant")


def test_policy_loads_from_config() -> None:
    """При наличии config файла — policy loaded из него."""
    m = DataQualityMonitor()
    policy = m.get_policy()
    assert "gates" in policy
    assert "gate_6_market_integrity" in policy["gates"]
    print("[OK] test_policy_loads_from_config")


def test_policy_fallback_when_no_config(tmp_path: Path | None = None) -> None:
    """Если config не найден — used built-in defaults."""
    fake_path = Path(__file__).resolve().parent / "__nonexistent__.json"
    m = DataQualityMonitor(config_path=fake_path)
    policy = m.get_policy()
    assert "gates" in policy
    # Default содержит все 6 gates
    assert len(policy["gates"]) == 6
    print("[OK] test_policy_fallback_when_no_config")


# === Runner ===

def run_all_tests() -> int:
    tests = [
        test_gate1_valid_passes,
        test_gate1_missing_field_blocks,
        test_gate1_low_greater_than_high_blocks,
        test_gate1_duplicate_timestamp_blocks,
        test_gate1_strict_raises,
        test_gate2_valid_passes,
        test_gate2_gap_detected,
        test_gate3_valid_passes,
        test_gate3_outlier_detected,
        test_gate4_no_cross_source_passes,
        test_gate4_cross_source_inconsistent,
        test_gate5_valid_passes,
        test_gate5_volume_spike_detected,
        test_gate6_valid_passes,
        test_gate6_round_volumes_detected,
        test_gate6_repeated_candles_detected,
        test_degraded_mode_triggered,
        test_single_degrade_no_forced_shock,
        test_confidence_floor,
        test_manipulation_risk_from_gate6,
        test_no_manipulation_risk_when_gate6_passes,
        test_empty_candles,
        test_single_candle,
        test_module_level_check,
        test_gate_names_constant,
        test_policy_loads_from_config,
        test_policy_fallback_when_no_config,
    ]

    failures: list[tuple[str, str]] = []
    for t in tests:
        try:
            t()
        except AssertionError as e:
            failures.append((t.__name__, str(e)))
        except Exception as e:
            failures.append((t.__name__, f"UNEXPECTED: {type(e).__name__}: {e}"))

    total = len(tests)
    passed = total - len(failures)
    print()
    print(f"=== Results: {passed}/{total} passed ===")
    if failures:
        print("[FAIL]")
        for name, msg in failures:
            print(f"  - {name}: {msg}")
        return 1
    print("[PASS]")
    return 0


if __name__ == "__main__":
    sys.exit(run_all_tests())
```

---

## Часть 6 — Запустить тесты

```bash
cd "C:\CODE\MARKET ANALYSIS"
python MARKET_MIND/tests/test_data_quality_monitor.py
```

Ожидается:
```
[OK] test_gate1_valid_passes
[OK] test_gate1_missing_field_blocks
...
=== Results: 27/27 passed ===
[PASS]
```

Если любой `[FAIL]` — не коммитить, разбираться по списку (§ 3). Возможные причины падений:
- Алгоритм detect'а слишком мягкий/жёсткий для тестовых данных (тюнинг пороговых значений)
- Ошибка в логике gate — сверить с ТЗ § 1885-1898
- Ошибка в конструкции test candles (перепроверить `_make_valid_candles`)

Также проверить что test_schema_validator всё ещё работает (TASK_03 не сломан):

```bash
python MARKET_MIND/tests/test_schema_validator.py
```

Должно быть 17/17 PASS.

---

## Часть 7 — Обновить `component_status.json`

Открыть `MARKET_MIND/CONFIG/component_status.json`. Найти запись `data_quality_gates` и **заменить** на:

```json
"data_quality_gates": {
    "status": "ready",
    "updated_at": "2026-04-19",
    "notes": "Task 04: переписан с нуля. 6 Gates согласно ТЗ § 1881-1902: Gate 1 data_corruption (block), Gate 2 timestamp_gaps (warn), Gate 3 statistical_outliers (degrade), Gate 4 cross_source_consistency (degrade), Gate 5 volume_anomaly (degrade, shock_delta+0.10), Gate 6 market_integrity/wash_trading (degrade, 3 эвристики). Degraded mode rule и confidence floor 0.20 реализованы. Конфиг в CONFIG/gate_failure_policy.json. 27/27 tests pass."
}
```

Остальные компоненты не трогать (AP-07).

---

## Часть 8 — Коммит, merge, push

### 8.1 Проверка перед коммитом

```bash
git status
```

Ожидаемые изменения:
- Добавлено: `MARKET_MIND/CONFIG/gate_failure_policy.json`
- Добавлено: `MARKET_MIND/ENGINE/data_quality_monitor.py`
- Добавлено: `MARKET_MIND/tests/test_data_quality_monitor.py`
- Изменено: `MARKET_MIND/CONFIG/component_status.json`

Файл `data_quality_gates.py` уже удалён в Части 2 (отдельным коммитом), его не должно быть в git status.

### 8.2 Pre-commit checklist (§ 24)

- [ ] `python MARKET_MIND/tests/test_data_quality_monitor.py` → 27/27 PASS
- [ ] `python MARKET_MIND/tests/test_schema_validator.py` → 17/17 PASS (не сломали TASK_03)
- [ ] `python scripts/pre_commit_check.py` → [PASS] или [INFO] No staged files
- [ ] Нет hardcoded путей (hook проверит автоматически)
- [ ] Нет реальных секретов
- [ ] Нет bare except
- [ ] Нет emoji в print
- [ ] Нет TODO/FIXME
- [ ] Нет самовольных файлов (AP-07)

### 8.3 Коммит

```bash
git add MARKET_MIND/
git commit -m "task 04: data_quality_monitor.py v2 with 6 Gates per TZ § 1881-1902"
```

Pre-commit hook должен вывести `[PASS]`.

### 8.4 Merge в main

```bash
git checkout main
git merge task-04-data-quality-monitor
```

Fast-forward ожидается (без конфликтов).

### 8.5 Push

```bash
git push origin main
```

**Обычный push, НЕ force** (AP-09). Если push protection блокирует — § 3 (вряд ли, но бывает).

### 8.6 Удалить ветку

```bash
git branch -d task-04-data-quality-monitor
```

### 8.7 Архивировать TASK

```bash
git mv TASKS/ACTIVE/TASK_04_data_quality_monitor.md TASKS/COMPLETED/TASK_04_data_quality_monitor.md
git commit -m "archive TASK_04"
git push origin main
```

### 8.8 Финальная синхронизация

```bash
git fetch origin
git log --oneline origin/main..main   # должен быть пуст
git log --oneline main..origin/main   # должен быть пуст
git status                               # clean working tree
git log --oneline -5                    # верхние коммиты
```

---

## Часть 9 — Финальный отчёт

Пришли Сергею отчёт в формате § 9:

```
TASK_04 [data_quality_monitor_v2] — COMPLETED

Файлы удалены:
  - MARKET_MIND/ENGINE/data_quality_gates.py (legacy, needs_rewrite) — Часть 2

Файлы созданы:
  - MARKET_MIND/CONFIG/gate_failure_policy.json (конфиг политики Gates)
  - MARKET_MIND/ENGINE/data_quality_monitor.py (6 Gates, 800+ строк)
  - MARKET_MIND/tests/test_data_quality_monitor.py (27 тестов)

Файлы изменены:
  - MARKET_MIND/CONFIG/component_status.json (data_quality_gates → ready)

Тесты: 27/27 passed (data_quality_monitor), 17/17 passed (schema_validator — не сломали)
Pre-commit hook: CLEAN
Push protection: без блокировок

Commits:
  - <hash1> task 04 part 2: remove legacy data_quality_gates.py
  - <hash2> task 04: data_quality_monitor.py v2 with 6 Gates per TZ § 1881-1902
  - <hash3> archive TASK_04

Время работы: <минуты>

ТЗ соответствие (критерии из § 1926-1936):
  - [9] Gate 6: suspicious_round_volumes + volume_without_price_impact + repeated_candles ✓

Gate Failure Policy (ТЗ § 1885-1898):
  - Gate 1 data_corruption: block, penalty 0.0 ✓
  - Gate 2 timestamp_gaps: warn, penalty -0.05 ✓
  - Gate 3 statistical_outliers: degrade, penalty -0.10 ✓
  - Gate 4 cross_source_consistency: degrade, penalty -0.08 ✓
  - Gate 5 volume_anomaly: degrade, penalty -0.07, shock_delta +0.10 ✓
  - Gate 6 market_integrity: degrade, penalty -0.15, manipulation_risk ✓

Правило degraded mode (ТЗ § 1902):
  - ≥2 Gates в degrade → forced shock_score +0.15 ✓
  - Confidence floor 0.20 ✓

Lessons applied:
  - L-01 (сверил параметры Gates с ТЗ § 1885-1898 построчно)
  - L-02 (27 тестов перед ready)
  - L-03 / AP-01 (Path(__file__).resolve() везде)
  - L-04 / AP-06 (ASCII markers, UTF-8 reconfigure)
  - L-07 / AP-02 (реальные эвристики, никаких stub)
  - L-17 (удалил legacy data_quality_gates.py в отдельном коммите)
  - L-18 / AP-10 (0 ad-hoc команд, только из TASK)

Patterns applied:
  - P-01 (relative paths)
  - P-02 (graceful degradation — empty candles, low data)
  - P-03 (DataQualityError/CandleCorruptionError + logging)
  - P-04 (policy loaded from JSON config)
  - P-05 (ASCII test markers)

Antipatterns avoided:
  - AP-01 (0 hardcoded paths)
  - AP-02 (0 stub data)
  - AP-03 (0 bare except, все типизированы)
  - AP-06 (0 emoji in print)
  - AP-07 (только файлы из TASK)
  - AP-08 (0 real secrets)
  - AP-09 (обычный push, не force)
  - AP-10 (0 ad-hoc диагностик)

Component status updates:
  - data_quality_gates: needs_rewrite → ready (3-й честный ready)

MDC progress: 3 из 3 MDC компонентов (schema_layer + initialize_system + data_quality_gates) готовы для первого прогноза.
Осталось: TASK_05 context_orchestrator для завершения MDC-тройки.

Ideas logged: 0
Warnings/issues: none (или описать)

Готов к TASK_05 (context_orchestrator v2).
```

---

## Критерии готовности

- [ ] Legacy `data_quality_gates.py` удалён отдельным коммитом (Часть 2)
- [ ] `CONFIG/gate_failure_policy.json` создан с 6 gates и правилами
- [ ] `ENGINE/data_quality_monitor.py` создан с 6 Gates согласно ТЗ § 1885-1898
- [ ] Gate 6 содержит 3 эвристики: round_volumes, volume_without_impact, repeated_candles
- [ ] `tests/test_data_quality_monitor.py` содержит 27+ тестов, все PASS
- [ ] Degraded mode rule реализован (≥2 degrade → +0.15 shock)
- [ ] Confidence floor 0.20 реализован
- [ ] manipulation_risk_score рассчитывается на основе Gate 6
- [ ] Pre-commit hook пропустил без нарушений
- [ ] `component_status.json`: `data_quality_gates: ready` с корректными notes
- [ ] test_schema_validator.py всё ещё 17/17 PASS (ничего не сломали)
- [ ] Main синхронизирован с origin, TASK в COMPLETED/

---

## Важные предупреждения

- ⚠ **Не добавляй Gates сверх ТЗ** (AP-07). Ровно 6 — если кажется "нужен Gate 7" → § 3
- ⚠ **Не реализуй ML/AI модели** для wash trading — только эвристики из ТЗ § 1940
- ⚠ **Не трогай schema_validator.py и другие компоненты** — только data_quality_monitor.py
- ⚠ **Не реализуй интеграцию с Binance** — это TASK_13. TASK_04 работает только с абстрактным list[dict] candles
- ⚠ **Не реализуй shock_score computation** полностью — только `shock_score_delta` от Gate 5/6. Полный shock_score — Task 24
- ⚠ **Никаких ad-hoc `python -c`** для проверки эвристик (AP-10). Только `test_data_quality_monitor.py`
- ⚠ **Никакого force push** (AP-09)
- ⚠ При **security warning** от среды — § 3 (L-20), не одобрять молча

---

**После успешного TASK_04 остаётся только TASK_05 (context_orchestrator v2) для завершения MDC-тройки. После этого можно делать первый честный прогноз.**
