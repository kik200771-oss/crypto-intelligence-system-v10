"""Skeleton tests для context_orchestrator (TASK_05a). Тесты API сигнатур и constants, не бизнес-логики."""

import sys
from pathlib import Path

# L-04 / P-05
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

# applies P-01
BASE = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE))

from MARKET_MIND.ENGINE.context_orchestrator import (
    ContextOrchestrator,
    build_context,
    save_session,
    BlockSpec,
    ContextBlock,
    ContextResult,
    TASK_TYPES,
    MAX_TOKENS,
    is_fast_lane,
)


def test_module_imports():
    """Все публичные символы импортируются без ошибок."""
    assert ContextOrchestrator is not None
    assert build_context is not None
    assert save_session is not None
    assert BlockSpec is not None
    assert ContextBlock is not None
    assert ContextResult is not None
    assert TASK_TYPES is not None
    assert MAX_TOKENS is not None
    assert is_fast_lane is not None
    print("[OK] test_module_imports")


def test_task_types_constant():
    """TASK_TYPES — frozenset ровно из 4 значений дословно из ТЗ."""
    assert TASK_TYPES == frozenset({"forecast", "research", "monitoring", "postmortem"})
    assert isinstance(TASK_TYPES, frozenset)
    assert len(TASK_TYPES) == 4
    print("[OK] test_task_types_constant")


def test_max_tokens_constant():
    """MAX_TOKENS == 8000, int type."""
    assert MAX_TOKENS == 8000
    assert isinstance(MAX_TOKENS, int)
    print("[OK] test_max_tokens_constant")


def test_is_fast_lane_correctness():
    """Комплексный тест is_fast_lane функции."""
    assert is_fast_lane("forecast", "1h") == True
    assert is_fast_lane("forecast", "4h") == True
    assert is_fast_lane("forecast", "1d") == False
    assert is_fast_lane("forecast", "15m") == False
    assert is_fast_lane("research", "1h") == False
    assert is_fast_lane("monitoring", "4h") == False
    assert is_fast_lane("postmortem", "1h") == False
    print("[OK] test_is_fast_lane_correctness")


def test_context_orchestrator_instantiates():
    """ContextOrchestrator() создаётся без ошибок, имеет нужные атрибуты."""
    orchestrator = ContextOrchestrator()
    assert hasattr(orchestrator, 'market_mind_root')
    assert hasattr(orchestrator, 'config')
    assert isinstance(orchestrator.market_mind_root, Path)
    assert isinstance(orchestrator.config, dict)
    print("[OK] test_context_orchestrator_instantiates")


def test_build_context_raises_notimplemented():
    """build_context поднимает NotImplementedError."""
    orchestrator = ContextOrchestrator()
    raised = False
    try:
        orchestrator.build_context("test", "BTCUSDT", "4h")
    except NotImplementedError:
        raised = True
    assert raised
    print("[OK] test_build_context_raises_notimplemented")


def test_build_context_validates_task_type():
    """build_context валидирует task_type ДО NotImplementedError."""
    orchestrator = ContextOrchestrator()
    raised = False
    try:
        orchestrator.build_context("test", "BTCUSDT", "4h", task_type="invalid_type")
    except ValueError:
        raised = True
    except NotImplementedError:
        raised = False  # ValueError должен быть ДО NotImplementedError
    assert raised
    print("[OK] test_build_context_validates_task_type")


def test_save_session_raises_notimplemented():
    """save_session поднимает NotImplementedError."""
    orchestrator = ContextOrchestrator()
    raised = False
    try:
        orchestrator.save_session("test summary", [], None)
    except NotImplementedError:
        raised = True
    assert raised
    print("[OK] test_save_session_raises_notimplemented")


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