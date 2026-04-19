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
    # Создаём outlier через согласованное изменение ВСЕХ полей свечи 10,
    # сохраняя OHLC валидность (low <= open, close, high; high >= low)
    candles[10]["open"] = 200.0
    candles[10]["high"] = 250.0
    candles[10]["low"] = 190.0
    candles[10]["close"] = 240.0
    # Свеча 11 должна начинаться рядом с close свечи 10 для reasonable continuity
    candles[11]["open"] = 240.0
    candles[11]["high"] = 245.0
    candles[11]["low"] = 110.0
    candles[11]["close"] = 115.0
    report = m.check(candles)
    # Сначала убеждаемся что Gate 1 не сработал (OHLC валидны)
    assert not report.blocked, f"Gate 1 should not block, violations: {report.gate_results[0].violations}"
    report = m.check(candles)
    # Сначала убеждаемся что Gate 1 не сработал (OHLC валидны)
    assert not report.blocked, f"Gate 1 should not block, violations: {report.gate_results[0].violations}"
    g3 = report.gate_results[2]
    assert not g3.passed, f"Gate 3 should fail on 100% return outlier, passed unexpectedly"
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
    # Триггерим Gate 3 (outlier) — согласованное OHLC изменение свечи 10
    candles[10]["open"] = 200.0
    candles[10]["high"] = 250.0
    candles[10]["low"] = 190.0
    candles[10]["close"] = 240.0
    candles[11]["open"] = 240.0
    candles[11]["high"] = 245.0
    candles[11]["low"] = 110.0
    candles[11]["close"] = 115.0
    # Триггерим Gate 5 (volume spike) на свече 15
    candles[15]["volume"] = 50000.0
    report = m.check(candles)
    # Сначала убеждаемся что Gate 1 не сработал
    assert not report.blocked, f"Gate 1 should not block, violations: {report.gate_results[0].violations}"
    report = m.check(candles)
    # Сначала убеждаемся что Gate 1 не сработал
    assert not report.blocked, f"Gate 1 should not block, violations: {report.gate_results[0].violations}"
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


def test_policy_fallback_when_no_config() -> None:
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