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

import json
import logging
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional, List, Dict

try:
    import tiktoken
except ImportError:
    tiktoken = None

logger = logging.getLogger(__name__)

# ТЗ Задача 3: Task Awareness taxonomy. НЕ расширять без обновления ТЗ.
TASK_TYPES: frozenset[str] = frozenset({"forecast", "research", "monitoring", "postmortem"})

# ТЗ Задача 3: лимит context в токенах для build_context()
MAX_TOKENS: int = 8000

TIKTOKEN_ENCODING: str = "cl100k_base"

BRAKE_THRESHOLDS: dict[str, float] = {
    "shock_score_include": 0.25,  # ТЗ Задача 3: при shock_score > 0.25 — brake_info в контекст
    "conflict_flag": 0.5,          # exposure threshold для conflict_flag (будет использоваться в TASK_05b)
}


@dataclass(frozen=True)
class BlockSpec:
    """Спецификация одного блока контекста."""
    name: str
    priority: int
    required: bool
    max_tokens: int | None


@dataclass(frozen=True)
class ContextBlock:
    """Один собранный блок с контентом."""
    name: str
    content: str
    token_count: int
    source_available: bool


@dataclass(frozen=True)
class ContextResult:
    """Результат build_context."""
    context: str
    total_tokens: int
    blocks_included: list[str]
    blocks_dropped: list[str]
    context_degraded: bool
    status: str


def _load_timeframe_core() -> dict:
    """Читает timeframe_core.json с P-01 + P-03 + P-04."""
    config_path = Path(__file__).resolve().parent.parent / "CONFIG" / "timeframe_core.json"

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        return config
    except FileNotFoundError as e:
        logger.error(f"timeframe_core.json not found: {e}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in timeframe_core.json: {e}")
        raise


def _count_tokens(text: str, encoding_name: str = TIKTOKEN_ENCODING) -> int:
    """Считает количество токенов в тексте."""
    if tiktoken is not None:
        try:
            enc = tiktoken.get_encoding(encoding_name)
            return len(enc.encode(text))
        except Exception as e:
            logger.warning(f"tiktoken error: {e}, using fallback")
            return len(text) // 4
    else:
        return len(text) // 4


def is_fast_lane(task_type: str, timeframe: str, config: dict | None = None) -> bool:
    """Определяет принадлежность к Fast Lane."""
    if config is None:
        config = _load_timeframe_core()

    try:
        fast_lane_list = config["standard_core"]["fast_lane"]
        return task_type == "forecast" and timeframe in fast_lane_list
    except KeyError as e:
        logger.warning(f"Malformed config, missing key: {e}")
        return False


class ContextOrchestrator:
    """Context Orchestrator для CIS V10.0-r1."""

    def __init__(self, market_mind_root: str | Path | None = None):
        if market_mind_root is None:
            market_mind_root = Path(__file__).resolve().parent.parent
        self.market_mind_root = Path(market_mind_root)
        self.config = _load_timeframe_core()
        self.logger = logging.getLogger(self.__class__.__name__)

    def build_context(self, query: str, symbol: str, timeframe: str, task_type: str = "forecast") -> ContextResult:
        """Публичный API ТЗ Задача 3."""
        if task_type not in TASK_TYPES:
            raise ValueError(f"Invalid task_type: {task_type}. Expected one of {TASK_TYPES}")

        if not symbol or not isinstance(symbol, str):
            raise ValueError("symbol must be non-empty string")

        if not timeframe or not isinstance(timeframe, str):
            raise ValueError("timeframe must be non-empty string")

        raise NotImplementedError("Context building logic implemented in TASK_05b (forecast) and TASK_05c (research/monitoring/postmortem)")

    def save_session(self, summary: str, new_items: list[str], bias: str | None = None) -> None:
        """Публичный API из ТЗ Задача 3."""
        if not isinstance(summary, str):
            raise ValueError("summary must be string")

        if not isinstance(new_items, list) or not all(isinstance(item, str) for item in new_items):
            raise ValueError("new_items must be list of strings")

        if bias is not None and not isinstance(bias, str):
            raise ValueError("bias must be string or None")

        raise NotImplementedError("save_session logic implemented in TASK_05c")


def build_context(query: str, symbol: str, timeframe: str, task_type: str = "forecast") -> ContextResult:
    """Module-level wrapper для build_context."""
    orchestrator = ContextOrchestrator()
    return orchestrator.build_context(query, symbol, timeframe, task_type)


def save_session(summary: str, new_items: list[str], bias: str | None = None) -> None:
    """Module-level wrapper для save_session."""
    orchestrator = ContextOrchestrator()
    return orchestrator.save_session(summary, new_items, bias)