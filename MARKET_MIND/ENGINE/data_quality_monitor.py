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
    # Gate 3 — 3-sigma rule (стандартная статистика).
    # При малой выборке (N < 50) 5-sigma физически недостижим:
    # max z-score одного включённого значения = (N-1)/sqrt(N).
    # Для N=19 это ~4.13. Выбран 3.0 как баланс между чувствительностью
    # и false positives.
    "z_score_threshold": 3.0,
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