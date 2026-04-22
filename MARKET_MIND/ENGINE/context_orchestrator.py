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
from concurrent.futures import ThreadPoolExecutor, as_completed
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

        # TASK_05b: реализуем только forecast logic
        if task_type == "forecast":
            return self._build_forecast_context(symbol, timeframe)
        else:
            # research/monitoring/postmortem логика в TASK_05c
            raise NotImplementedError(f"Context building for task_type '{task_type}' implemented in TASK_05c")

    def save_session(self, summary: str, new_items: list[str], bias: str | None = None) -> None:
        """Публичный API из ТЗ Задача 3."""
        if not isinstance(summary, str):
            raise ValueError("summary must be string")

        if not isinstance(new_items, list) or not all(isinstance(item, str) for item in new_items):
            raise ValueError("new_items must be list of strings")

        if bias is not None and not isinstance(bias, str):
            raise ValueError("bias must be string or None")

        raise NotImplementedError("save_session logic implemented in TASK_05c")

    # =============================================================================
    # FORECAST CONTEXT LOGIC (TASK_05b)
    # =============================================================================

    def _build_forecast_context(self, symbol: str, timeframe: str) -> ContextResult:
        """
        Основная логика для task_type='forecast'.
        Applies L-08 Fast Lane Invariant - никогда ABORTED для 1h/4h.
        """
        start_time = time.time()
        context_degraded = False
        blocks_included = []
        blocks_dropped = []

        # Определяем Fast Lane vs Slow Lane
        is_fast = is_fast_lane("forecast", timeframe, self.config)

        # Получаем timeouts из конфига
        timeouts = self.config.get("context_orchestrator_timeouts", {})
        if is_fast:
            total_timeout_ms = timeouts.get("fast_lane_total_ms", 5000)
        else:
            total_timeout_ms = timeouts.get("slow_lane_total_ms", 30000)

        total_timeout = total_timeout_ms / 1000.0  # Convert to seconds

        self.logger.info(f"Building forecast context for {symbol}/{timeframe}, "
                        f"Fast Lane: {is_fast}, timeout: {total_timeout}s")

        # Базовый контекст
        context_data = {
            "symbol": symbol,
            "timeframe": timeframe,
            "task_type": "forecast",
            "timestamp": start_time,
            "is_fast_lane": is_fast
        }

        # Обязательные входы Fast Lane (ТЗ Задача 3)
        required_fast_sources = [
            ("features", self._collect_feature_snapshot),
            ("patterns", self._collect_validated_patterns),
            ("filters", self._collect_negative_filters)
        ]

        # Желательные входы Fast Lane
        optional_fast_sources = [
            ("regime", self._collect_regime_context),
            ("prior", self._collect_prior_snapshot)
        ]

        # В Fast Lane - последовательный сбор с single timeout
        # В Slow Lane - параллельный сбор с individual timeouts
        if is_fast:
            # Fast Lane: последовательный сбор, L-08 Fast Lane Invariant
            collected_data = {}

            for source_name, collector_func in required_fast_sources + optional_fast_sources:
                elapsed = time.time() - start_time
                remaining_time = total_timeout - elapsed

                if remaining_time <= 0:
                    # Timeout reached - applies L-08 (never ABORTED)
                    self.logger.warning(f"Fast Lane timeout reached, missing: {source_name}")
                    context_degraded = True
                    blocks_dropped.append(source_name)
                    continue

                try:
                    # Collect with remaining time limit
                    data = collector_func(symbol, timeframe)
                    if data is not None:
                        collected_data[source_name] = data
                        blocks_included.append(source_name)
                    else:
                        blocks_dropped.append(source_name)
                        if source_name in [name for name, _ in required_fast_sources]:
                            context_degraded = True

                except Exception as e:
                    self.logger.error(f"Error collecting {source_name}: {e}")
                    blocks_dropped.append(source_name)
                    if source_name in [name for name, _ in required_fast_sources]:
                        context_degraded = True

        else:
            # Slow Lane: параллельный сбор с ThreadPoolExecutor
            collected_data = {}
            all_sources = required_fast_sources + optional_fast_sources

            def collect_source(source_info):
                source_name, collector_func = source_info
                try:
                    data = collector_func(symbol, timeframe)
                    return source_name, data
                except Exception as e:
                    self.logger.error(f"Error collecting {source_name}: {e}")
                    return source_name, None

            with ThreadPoolExecutor(max_workers=6) as executor:
                future_to_source = {
                    executor.submit(collect_source, source_info): source_info[0]
                    for source_info in all_sources
                }

                for future in as_completed(future_to_source, timeout=total_timeout):
                    try:
                        source_name, data = future.result()
                        if data is not None:
                            collected_data[source_name] = data
                            blocks_included.append(source_name)
                        else:
                            blocks_dropped.append(source_name)

                    except Exception as e:
                        source_name = future_to_source[future]
                        self.logger.error(f"Future failed for {source_name}: {e}")
                        blocks_dropped.append(source_name)

            # В Slow Lane отсутствие обязательных источников тоже degraded
            for source_name, _ in required_fast_sources:
                if source_name not in collected_data:
                    context_degraded = True

        # Merge collected data into context
        context_data.update(collected_data)

        # Conflict Exposure check (ТЗ Задача 3)
        # Минимальная реализация TASK_05b-fix.1: без KB access — всегда False (честно "not determined").
        # Полная реализация с KB search — TASK_05c.
        conflict_flag = False
        context_data["conflict_flag"] = conflict_flag

        # AXM Guard invocation
        try:
            axm_result = self._invoke_axm_guard(context_data, symbol, timeframe)
            context_data.update(axm_result)
        except Exception as e:
            self.logger.error(f"AXM Guard failed: {e}")
            context_data["epistemic_risk_flag"] = True
            context_data["axm_notes"] = [f"AXM Guard error: {str(e)}"]

        # Build final context string
        context_lines = [
            f"=== FORECAST CONTEXT ({symbol}/{timeframe}) ===",
            f"Task Type: forecast",
            f"Fast Lane: {is_fast}",
            f"Timestamp: {context_data['timestamp']}",
            ""
        ]

        for source in blocks_included:
            if source in collected_data:
                data = collected_data[source]
                context_lines.append(f"[{source.upper()}]")
                if isinstance(data, dict):
                    for key, value in data.items():
                        context_lines.append(f"  {key}: {value}")
                elif isinstance(data, list):
                    context_lines.append(f"  count: {len(data)}")
                    for i, item in enumerate(data[:3]):  # Limit to first 3 items
                        context_lines.append(f"  [{i}]: {str(item)[:100]}")
                context_lines.append("")

        if context_data.get("conflict_flag"):
            context_lines.append("[CONFLICT EXPOSURE]")
            context_lines.append("  KB-Pattern conflict detected")
            context_lines.append("")

        if context_data.get("epistemic_risk_flag"):
            context_lines.append("[AXM GUARD ALERT]")
            for note in context_data.get("axm_notes", []):
                context_lines.append(f"  {note}")
            context_lines.append("")

        if blocks_dropped:
            context_lines.append("[MISSING SOURCES]")
            for dropped in blocks_dropped:
                context_lines.append(f"  - {dropped}")
            context_lines.append("")

        context_text = "\n".join(context_lines)
        token_count = _count_tokens(context_text)

        # Status determination — applies L-08 (clarified in TASK_05b-fix.1)
        # Context Orchestrator forecast context — никогда ABORTED, ни в одной lane.
        # ABORT применим только к Model Core aggregation (Math Model v6.3 раздел 7), не здесь.
        if context_degraded:
            status = "DEGRADED"
        else:
            status = "OK"

        elapsed_time = time.time() - start_time
        self.logger.info(f"Forecast context built in {elapsed_time:.2f}s, "
                        f"status: {status}, tokens: {token_count}, "
                        f"included: {len(blocks_included)}, dropped: {len(blocks_dropped)}")

        return ContextResult(
            context=context_text,
            total_tokens=token_count,
            blocks_included=blocks_included,
            blocks_dropped=blocks_dropped,
            context_degraded=context_degraded,
            status=status
        )

    def _collect_feature_snapshot(self, symbol: str, timeframe: str) -> dict | None:
        """Читает данные из Feature Store. Applies P-02 graceful degradation."""
        # applies L-07 (no stub data), P-02 (graceful degradation)
        features_dir = self.market_mind_root / "LAYER_B_DATA" / "features"

        if not features_dir.exists():
            self.logger.warning(f"Feature Store directory not found: {features_dir}")
            return None

        feature_file = features_dir / f"{symbol}_{timeframe}.json"
        if not feature_file.exists():
            self.logger.warning(f"Feature snapshot not found: {feature_file}")
            return None

        try:
            content = feature_file.read_text(encoding="utf-8")
            data = json.loads(content)

            # Minimal validation - требуются basic поля
            if not isinstance(data, dict) or "symbol" not in data or "timeframe" not in data:
                self.logger.warning(f"Invalid feature snapshot format in {feature_file}")
                return None

            return data
        except (json.JSONDecodeError, OSError) as e:
            self.logger.error(f"Error reading feature snapshot {feature_file}: {e}")
            return None

    def _collect_validated_patterns(self, symbol: str, timeframe: str) -> list[dict] | None:
        """Читает паттерны из Pattern Registry. Applies P-02 graceful degradation."""
        # applies L-07 (no stub data), P-02 (graceful degradation)
        patterns_dir = self.market_mind_root / "LAYER_A_RESEARCH" / "patterns"

        if not patterns_dir.exists():
            self.logger.warning(f"Pattern Registry directory not found: {patterns_dir}")
            return None

        try:
            patterns = []
            for pattern_file in patterns_dir.glob("*.json"):
                try:
                    content = pattern_file.read_text(encoding="utf-8")
                    data = json.loads(content)

                    # Фильтруем по symbol и timeframe
                    if (isinstance(data, dict) and
                        data.get("symbol") == symbol and
                        data.get("timeframe") == timeframe):
                        patterns.append(data)

                except (json.JSONDecodeError, OSError) as e:
                    self.logger.warning(f"Skipping invalid pattern file {pattern_file.name}: {e}")
                    continue

            return patterns if patterns else None

        except Exception as e:
            self.logger.error(f"Error reading patterns from {patterns_dir}: {e}")
            return None

    def _collect_negative_filters(self, symbol: str, timeframe: str) -> list[dict] | None:
        """Читает negative filters. Applies P-02 graceful degradation."""
        # applies L-07 (no stub data), P-02 (graceful degradation)
        filters_dir = self.market_mind_root / "LAYER_B_DATA" / "negative_filters"

        if not filters_dir.exists():
            self.logger.warning(f"Negative filters directory not found: {filters_dir}")
            return None

        filter_file = filters_dir / f"{symbol}_{timeframe}_filters.json"
        if not filter_file.exists():
            self.logger.warning(f"Negative filters not found: {filter_file}")
            return None

        try:
            content = filter_file.read_text(encoding="utf-8")
            data = json.loads(content)

            # Ожидаем список фильтров
            if not isinstance(data, list):
                self.logger.warning(f"Invalid negative filters format in {filter_file} - expected list")
                return None

            return data if data else None

        except (json.JSONDecodeError, OSError) as e:
            self.logger.error(f"Error reading negative filters {filter_file}: {e}")
            return None

    def _collect_regime_context(self, symbol: str, timeframe: str) -> dict | None:
        """Читает regime context from Regime Detector. Applies P-02 graceful degradation."""
        # applies L-07 (no stub data), P-02 (graceful degradation)
        regime_dir = self.market_mind_root / "LAYER_B_DATA" / "regime"

        if not regime_dir.exists():
            self.logger.warning(f"Regime detector directory not found: {regime_dir}")
            return None

        regime_file = regime_dir / f"{symbol}_{timeframe}_regime.json"
        if not regime_file.exists():
            self.logger.warning(f"Regime context not found: {regime_file}")
            return None

        try:
            content = regime_file.read_text(encoding="utf-8")
            data = json.loads(content)

            # Minimal validation - требуется basic structure
            if not isinstance(data, dict) or "regime_type" not in data:
                self.logger.warning(f"Invalid regime context format in {regime_file}")
                return None

            return data

        except (json.JSONDecodeError, OSError) as e:
            self.logger.error(f"Error reading regime context {regime_file}: {e}")
            return None

    def _collect_prior_snapshot(self, symbol: str, timeframe: str) -> dict | None:
        """Читает prior snapshot for Prior Manager integration. Applies P-02 graceful degradation."""
        # applies L-07 (no stub data), P-02 (graceful degradation)
        prior_dir = self.market_mind_root / "LAYER_D_MODEL" / "prior_snapshots"

        if not prior_dir.exists():
            self.logger.warning(f"Prior snapshots directory not found: {prior_dir}")
            return None

        prior_file = prior_dir / f"{symbol}_{timeframe}_prior.json"
        if not prior_file.exists():
            self.logger.warning(f"Prior snapshot not found: {prior_file}")
            return None

        try:
            content = prior_file.read_text(encoding="utf-8")
            data = json.loads(content)

            # Minimal validation - требуются snapshot_id и timestamp
            if (not isinstance(data, dict) or
                "snapshot_id" not in data or
                "timestamp" not in data):
                self.logger.warning(f"Invalid prior snapshot format in {prior_file}")
                return None

            return data

        except (json.JSONDecodeError, OSError) as e:
            self.logger.error(f"Error reading prior snapshot {prior_file}: {e}")
            return None

    def _invoke_axm_guard(self, context_data: dict, symbol: str, timeframe: str) -> dict:
        """
        Минимальная реализация AXM Guard согласно ТЗ § 1.20.

        AXM применяется как post-scoring epistemic check.
        НЕ модифицирует confidence/direction/score.

        Returns:
            dict with epistemic_risk_flag and axm_notes
        """
        # applies ТЗ § 1.20: AXM не contributing factor в scoring

        axm_result = {
            "epistemic_risk_flag": False,
            "axm_notes": [],
            "axm_checks_performed": []
        }

        try:
            # Minimal epistemic checks про axioms of market mechanics.
            # Per ТЗ § 1.20: AXM — post-scoring guardrail, не contributing factor.
            # Full AXM_001/002/004/008 — V10+ (требуют order flow / microstructure data).

            patterns = context_data.get("patterns") or []
            regime = context_data.get("regime") or {}
            features = context_data.get("features") or {}

            # Check 1 — Pattern-Regime Consistency:
            # patterns не должны предлагать direction во время HARD brake (R4).
            # Math Model v6.3 раздел 3: R4 направление подавляется (A4[m,q]=-0.20).
            regime_type = regime.get("regime_type") if isinstance(regime, dict) else None
            if regime_type == "R4" and any(
                p.get("direction") in ("UP", "DOWN") for p in patterns if isinstance(p, dict)
            ):
                axm_result["epistemic_risk_flag"] = True
                axm_result["axm_notes"].append(
                    "Patterns propose direction during R4 hard-brake regime"
                )
            axm_result["axm_checks_performed"].append("pattern_regime_consistency")

            # Check 2 — Pattern Direction Consistency:
            # На одном таймфрейме одновременные UP и DOWN patterns — сигнал noise.
            directions = {p.get("direction") for p in patterns if isinstance(p, dict)}
            if "UP" in directions and "DOWN" in directions:
                axm_result["epistemic_risk_flag"] = True
                axm_result["axm_notes"].append(
                    "Conflicting pattern directions (UP and DOWN) at same timeframe"
                )
            axm_result["axm_checks_performed"].append("pattern_direction_consistency")

            # Check 3 — Low Liquidity + Patterns (proxy for AXM_004 until microstructure exists):
            # Если features указывают на очень низкую ликвидность — patterns могут быть noise.
            liquidity = features.get("volume_indicator") if isinstance(features, dict) else None
            if (
                isinstance(liquidity, (int, float))
                and liquidity < 0.1
                and len(patterns) > 0
            ):
                axm_result["epistemic_risk_flag"] = True
                axm_result["axm_notes"].append(
                    "Patterns proposed with low liquidity (potential noise, proxy for AXM_004)"
                )
            axm_result["axm_checks_performed"].append("liquidity_pattern_plausibility")

            self.logger.debug(
                f"AXM Guard performed {len(axm_result['axm_checks_performed'])} checks, "
                f"risk_flag={axm_result['epistemic_risk_flag']}"
            )

        except Exception as e:
            self.logger.error(f"Error in AXM Guard: {e}")
            axm_result["epistemic_risk_flag"] = True
            axm_result["axm_notes"].append(f"AXM Guard inner error: {str(e)}")

        return axm_result


def build_context(query: str, symbol: str, timeframe: str, task_type: str = "forecast") -> ContextResult:
    """Module-level wrapper для build_context."""
    orchestrator = ContextOrchestrator()
    return orchestrator.build_context(query, symbol, timeframe, task_type)


def save_session(summary: str, new_items: list[str], bias: str | None = None) -> None:
    """Module-level wrapper для save_session."""
    orchestrator = ContextOrchestrator()
    return orchestrator.save_session(summary, new_items, bias)