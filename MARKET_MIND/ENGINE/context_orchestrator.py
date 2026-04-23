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

        # Диспетчер по task_type (TASK_05c: все 4 task_types)
        if task_type == "forecast":
            return self._build_forecast_context(symbol, timeframe)
        elif task_type == "research":
            return self._build_research_context(symbol, timeframe)
        elif task_type == "monitoring":
            return self._build_monitoring_context(symbol, timeframe)
        elif task_type == "postmortem":
            return self._build_postmortem_context(symbol, timeframe)
        else:
            # task_type уже валидирован через TASK_TYPES frozenset выше — unreachable
            raise ValueError(f"Unreachable: task_type {task_type} not in dispatcher")

    def save_session(self, summary: str, new_items: list[str], bias: str | None = None) -> None:
        """
        Публичный API из ТЗ Задача 3.

        Raises:
            ValueError: если summary не строка, new_items не list[str], или bias не str/None
            FileNotFoundError: если session_state.json не существует
            json.JSONDecodeError: если existing session_state.json невалидный JSON
            OSError: если write failed (permission, disk full, etc.)
        """
        if not isinstance(summary, str):
            raise ValueError("summary must be string")

        if not isinstance(new_items, list) or not all(isinstance(item, str) for item in new_items):
            raise ValueError("new_items must be list of strings")

        if bias is not None and not isinstance(bias, str):
            raise ValueError("bias must be string or None")

        session_file = self.market_mind_root / "CONFIG" / "session_state.json"

        try:
            # Прочитать existing state
            content = session_file.read_text(encoding="utf-8")
            state = json.loads(content)

            # Обновить 3 поля (сохраняя всё остальное)
            state["summary"] = summary
            state["new_items"] = new_items
            state["bias"] = bias

            # Atomic write через temp + rename
            temp_path = session_file.with_suffix('.json.tmp')
            temp_content = json.dumps(state, ensure_ascii=False, indent=2)
            temp_path.write_text(temp_content, encoding="utf-8")
            temp_path.replace(session_file)

            # Логирование
            self.logger.info(f"Session state saved: summary length {len(summary)}, {len(new_items)} new items, bias={bias}")

        except (OSError, json.JSONDecodeError) as e:
            self.logger.error(f"save_session failed: {e}")
            raise

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

    def _enforce_budget(
        self,
        context_lines: list[str],
        blocks_included: list[str],
        blocks_dropped: list[str],
        priority_order: list[str]
    ) -> tuple[list[str], int, list[str], list[str]]:
        """
        Если total_tokens > MAX_TOKENS, удаляет блоки с lowest priority
        (highest priority number) до fit в budget.

        Returns: (modified_context_lines, final_token_count, updated_blocks_included, updated_blocks_dropped)
        """
        # Подсчитать текущие tokens
        current_text = "\n".join(context_lines)
        current_tokens = _count_tokens(current_text)

        # Если в budget — return as-is
        if current_tokens <= MAX_TOKENS:
            return context_lines.copy(), current_tokens, blocks_included.copy(), blocks_dropped.copy()

        # Копируем входные данные для модификации
        modified_lines = context_lines.copy()
        updated_included = blocks_included.copy()
        updated_dropped = blocks_dropped.copy()

        # Защита от infinite loop — максимум 10 итераций
        max_iterations = 10
        iteration = 0

        while iteration < max_iterations:
            # Идентифицировать блоки в context_lines
            blocks_in_context = {}
            i = 0
            while i < len(modified_lines):
                line = modified_lines[i].strip()
                if line.startswith('[') and line.endswith(']'):
                    block_name = line[1:-1].lower()  # Remove [ ]
                    start_idx = i

                    # Найти конец блока
                    j = i + 1
                    while j < len(modified_lines):
                        next_line = modified_lines[j].strip()
                        if next_line.startswith('[') and next_line.endswith(']'):
                            break
                        j += 1

                    blocks_in_context[block_name] = (start_idx, j)
                    i = j
                else:
                    i += 1

            # Найти блок для удаления (последний в priority_order который присутствует)
            block_to_remove = None
            for block_name in reversed(priority_order):
                if block_name.lower() in blocks_in_context:
                    block_to_remove = block_name.lower()
                    break

            if block_to_remove is None:
                # Нет блоков для удаления — выход
                break

            # Удалить блок из context_lines
            start_idx, end_idx = blocks_in_context[block_to_remove]
            modified_lines = modified_lines[:start_idx] + modified_lines[end_idx:]

            # Обновить blocks_included и blocks_dropped
            original_block_name = block_to_remove
            for orig_name in blocks_included:
                if orig_name.lower() == block_to_remove:
                    original_block_name = orig_name
                    break

            if original_block_name in updated_included:
                updated_included.remove(original_block_name)
                updated_dropped.append(f"{original_block_name}:budget_exceeded")

            # Проверить новый token count
            new_text = "\n".join(modified_lines)
            new_tokens = _count_tokens(new_text)

            if new_tokens <= MAX_TOKENS:
                return modified_lines, new_tokens, updated_included, updated_dropped

            iteration += 1

        # Если после max_iterations всё ещё превышен budget
        final_text = "\n".join(modified_lines)
        final_tokens = _count_tokens(final_text)

        if final_tokens > MAX_TOKENS:
            updated_dropped.append("budget_critical_exceeded")

        return modified_lines, final_tokens, updated_included, updated_dropped

    def _collect_audit_entries(self, symbol: str, timeframe: str) -> list[dict] | None:
        """Читает audit entries из LAYER_F_FEEDBACK/predictions_history.json. Applies P-02 graceful degradation."""
        # applies L-07 (no stub data), P-02 (graceful degradation)
        audit_file = self.market_mind_root / "LAYER_F_FEEDBACK" / "predictions_history.json"

        if not audit_file.exists():
            self.logger.warning(f"Predictions history not found: {audit_file}")
            return None

        try:
            content = audit_file.read_text(encoding="utf-8")
            data = json.loads(content)

            # Ожидаем list of dicts (история предсказаний)
            if not isinstance(data, list):
                self.logger.warning(f"Invalid predictions history format in {audit_file} - expected list")
                return None

            # Фильтрация по symbol/timeframe если указаны в entries
            filtered_entries = []
            for entry in data:
                if not isinstance(entry, dict):
                    continue

                # Фильтруем по symbol и timeframe если поля есть
                if "symbol" in entry and "timeframe" in entry:
                    if entry["symbol"] == symbol and entry["timeframe"] == timeframe:
                        filtered_entries.append(entry)
                else:
                    # Entry без symbol/timeframe полей - включаем в результат
                    filtered_entries.append(entry)

            if not filtered_entries:
                return None

            # Сортируем по timestamp, берём top 20 most recent
            # Поддерживаем разные варианты timestamp полей
            def get_timestamp(entry):
                for ts_field in ["timestamp", "created_at", "prediction_time", "last_updated"]:
                    if ts_field in entry and isinstance(entry[ts_field], (int, float)):
                        return entry[ts_field]
                return 0

            filtered_entries.sort(key=get_timestamp, reverse=True)
            return filtered_entries[:20]

        except (json.JSONDecodeError, OSError) as e:
            self.logger.error(f"Error reading predictions history {audit_file}: {e}")
            return None

    def _collect_drift_metrics(self, symbol: str, timeframe: str) -> dict | None:
        """Читает drift metrics из LAYER_F_FEEDBACK/drift_log.json. Applies P-02 graceful degradation."""
        # applies L-07 (no stub data), P-02 (graceful degradation)
        drift_file = self.market_mind_root / "LAYER_F_FEEDBACK" / "drift_log.json"

        if not drift_file.exists():
            self.logger.warning(f"Drift log not found: {drift_file}")
            return None

        try:
            content = drift_file.read_text(encoding="utf-8")
            data = json.loads(content)

            # Ожидаем структуру с drift metrics
            if not isinstance(data, dict):
                self.logger.warning(f"Invalid drift log format in {drift_file} - expected dict")
                return None

            # Фильтруем по symbol и timeframe если указаны
            if "symbol" in data and "timeframe" in data:
                if data["symbol"] != symbol or data["timeframe"] != timeframe:
                    self.logger.warning(f"Drift log symbol/timeframe mismatch: expected {symbol}/{timeframe}")
                    return None

            # Minimal validation - требуются basic drift поля
            if "drift_score" not in data and "drift_metrics" not in data:
                self.logger.warning(f"Invalid drift log format - missing drift_score or drift_metrics")
                return None

            return data

        except (json.JSONDecodeError, OSError) as e:
            self.logger.error(f"Error reading drift log {drift_file}: {e}")
            return None

    def _collect_kb_excerpts(self, symbol: str, timeframe: str) -> list[dict] | None:
        """Читает KB excerpts из LAYER_A_RESEARCH/kb/. Applies P-02 graceful degradation."""
        # applies L-07 (no stub data), P-02 (graceful degradation)
        kb_dir = self.market_mind_root / "LAYER_A_RESEARCH" / "kb"

        if not kb_dir.exists():
            self.logger.warning(f"KB directory not found: {kb_dir}")
            return None

        try:
            excerpts = []
            # Поддерживаем как .json, так и .md файлы
            for kb_file in list(kb_dir.glob("*.json")) + list(kb_dir.glob("*.md")):
                try:
                    if kb_file.suffix == ".json":
                        content = kb_file.read_text(encoding="utf-8")
                        data = json.loads(content)

                        # Фильтруем по symbol и timeframe если есть в metadata
                        if isinstance(data, dict):
                            if (data.get("symbol") == symbol and
                                data.get("timeframe") == timeframe):
                                excerpts.append(data)
                            elif "symbol" not in data and "timeframe" not in data:
                                # Generic KB entry без фильтрации
                                excerpts.append(data)

                    elif kb_file.suffix == ".md":
                        # Простая markdown KB entry
                        content = kb_file.read_text(encoding="utf-8")
                        excerpt = {
                            "id": kb_file.stem,
                            "content": content[:500],  # Limit content size
                            "file_type": "markdown",
                            "last_updated": kb_file.stat().st_mtime
                        }
                        excerpts.append(excerpt)

                except (json.JSONDecodeError, OSError) as e:
                    self.logger.warning(f"Skipping invalid KB file {kb_file.name}: {e}")
                    continue

            # Сортируем по last_updated, берём top 10 most recent
            if excerpts:
                excerpts.sort(key=lambda x: x.get("last_updated", 0), reverse=True)
                return excerpts[:10]
            else:
                return None

        except Exception as e:
            self.logger.error(f"Error reading KB excerpts from {kb_dir}: {e}")
            return None

    def _collect_shock_score(self, symbol: str, timeframe: str) -> dict | None:
        """Читает shock_score из источника Brake Detector (Task 11). Applies P-02 graceful degradation — Task 11 not yet implemented."""
        # applies L-07 (no stub data), P-02 (graceful degradation)
        # ВАЖНО: Task 11 (Brake Detector) не реализован на момент TASK_05c-fix.1.
        # Метод возвращает None — monitoring context корректно не добавляет [BRAKE_ALERT].
        # Когда Task 11 будет реализован: body метода заменится на чтение канонического
        # shock_score артефакта. Path, schema, lifecycle определяются Task 11 scope.
        self.logger.info(
            f"shock_score collector: Task 11 (Brake Detector) not yet implemented — "
            f"returning None for {symbol}/{timeframe}"
        )
        return None

    # =============================================================================
    # RESEARCH/MONITORING/POSTMORTEM CONTEXT LOGIC (TASK_05c)
    # =============================================================================

    def _build_research_context(self, symbol: str, timeframe: str) -> ContextResult:
        """
        Context building для task_type='research'. Slow Lane only.
        По ТЗ Задача 3: scope "KB + hypotheses".

        Источники: validated patterns (hypotheses) + KB excerpts.
        Всегда Slow Lane независимо от timeframe. Budget enforcement в Part 5.
        """
        start_time = time.time()
        context_degraded = False
        blocks_included = []
        blocks_dropped = []

        # Research context - всегда Slow Lane
        is_fast = False  # research никогда не Fast Lane

        # Получаем Slow Lane timeout из конфига
        timeouts = self.config.get("context_orchestrator_timeouts", {})
        total_timeout_ms = timeouts.get("slow_lane_total_ms", 30000)
        total_timeout = total_timeout_ms / 1000.0

        self.logger.info(f"Building research context for {symbol}/{timeframe}, "
                        f"Slow Lane, timeout: {total_timeout}s")

        # Источники для research: patterns (hypotheses) + kb_excerpts
        research_sources = [
            ("patterns", self._collect_validated_patterns),
            ("kb_excerpts", self._collect_kb_excerpts)
        ]

        # Параллельный сбор с ThreadPoolExecutor (max_workers=2)
        collected_data = {}

        def collect_source(source_info):
            source_name, collector_func = source_info
            try:
                data = collector_func(symbol, timeframe)
                return source_name, data
            except Exception as e:
                self.logger.error(f"Error collecting {source_name}: {e}")
                return source_name, None

        with ThreadPoolExecutor(max_workers=2) as executor:
            future_to_source = {
                executor.submit(collect_source, source_info): source_info[0]
                for source_info in research_sources
            }

            for future in as_completed(future_to_source, timeout=total_timeout):
                try:
                    source_name, data = future.result()
                    if data is not None:
                        collected_data[source_name] = data
                        blocks_included.append(source_name)
                    else:
                        blocks_dropped.append(source_name)
                        context_degraded = True  # Любой отсутствующий источник → degraded

                except Exception as e:
                    source_name = future_to_source[future]
                    self.logger.error(f"Future failed for {source_name}: {e}")
                    blocks_dropped.append(source_name)
                    context_degraded = True

        # Build context string
        context_lines = [
            f"=== RESEARCH CONTEXT ({symbol}/{timeframe}) ===",
            f"Task Type: research",
            f"Fast Lane: {is_fast}",
            f"Timestamp: {start_time}",
            ""
        ]

        # Блоки в порядке: [PATTERNS], [KB_EXCERPTS], [MISSING SOURCES]
        if "patterns" in collected_data:
            patterns = collected_data["patterns"]
            context_lines.append("[PATTERNS]")
            if isinstance(patterns, list):
                context_lines.append(f"  count: {len(patterns)}")
                for i, pattern in enumerate(patterns[:3]):  # Limit to first 3
                    if isinstance(pattern, dict):
                        pattern_id = pattern.get("pattern_id", f"pattern_{i}")
                        pattern_desc = pattern.get("description", "No description")[:80]
                        context_lines.append(f"  [{i}] {pattern_id}: {pattern_desc}")
            context_lines.append("")

        if "kb_excerpts" in collected_data:
            kb_excerpts = collected_data["kb_excerpts"]
            context_lines.append("[KB_EXCERPTS]")
            if isinstance(kb_excerpts, list):
                context_lines.append(f"  count: {len(kb_excerpts)}")
                for i, excerpt in enumerate(kb_excerpts[:3]):  # Limit to first 3
                    if isinstance(excerpt, dict):
                        excerpt_id = excerpt.get("id", f"excerpt_{i}")
                        excerpt_content = excerpt.get("content", "No content")[:80]
                        context_lines.append(f"  [{i}] {excerpt_id}: {excerpt_content}")
            context_lines.append("")

        if blocks_dropped:
            context_lines.append("[MISSING SOURCES]")
            for dropped in blocks_dropped:
                context_lines.append(f"  - {dropped}")
            context_lines.append("")

        # Budget enforcement для research context
        priority_order = ["patterns", "kb_excerpts"]  # patterns higher priority
        context_lines, token_count, blocks_included, blocks_dropped = self._enforce_budget(
            context_lines, blocks_included, blocks_dropped, priority_order
        )
        if any("budget_exceeded" in d for d in blocks_dropped):
            context_degraded = True

        context_text = "\n".join(context_lines)

        # Status determination — applies L-08 clarification (никогда ABORTED)
        if context_degraded:
            status = "DEGRADED"
        else:
            status = "OK"

        elapsed_time = time.time() - start_time
        self.logger.info(f"Research context built in {elapsed_time:.2f}s, "
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

    def _build_monitoring_context(self, symbol: str, timeframe: str) -> ContextResult:
        """
        Context building для task_type='monitoring'. Slow Lane only.
        По ТЗ Задача 3: scope "health + drift + shock_score".

        Источники: regime (health proxy), shock_score, drift_metrics.
        Всегда Slow Lane. При shock_score > 0.25 добавляется [BRAKE_ALERT] блок.
        """
        start_time = time.time()
        context_degraded = False
        blocks_included = []
        blocks_dropped = []

        # Monitoring context - всегда Slow Lane
        is_fast = False  # monitoring никогда не Fast Lane

        # Получаем Slow Lane timeout из конфига
        timeouts = self.config.get("context_orchestrator_timeouts", {})
        total_timeout_ms = timeouts.get("slow_lane_total_ms", 30000)
        total_timeout = total_timeout_ms / 1000.0

        self.logger.info(f"Building monitoring context for {symbol}/{timeframe}, "
                        f"Slow Lane, timeout: {total_timeout}s")

        # Источники для monitoring: regime (health), shock_score, drift_metrics
        monitoring_sources = [
            ("regime", self._collect_regime_context),
            ("drift_metrics", self._collect_drift_metrics)
        ]

        # Параллельный сбор с ThreadPoolExecutor (max_workers=3, но пока 2 + shock_score отдельно)
        collected_data = {}

        def collect_source(source_info):
            source_name, collector_func = source_info
            try:
                data = collector_func(symbol, timeframe)
                return source_name, data
            except Exception as e:
                self.logger.error(f"Error collecting {source_name}: {e}")
                return source_name, None

        with ThreadPoolExecutor(max_workers=3) as executor:
            # Сбор regime и drift_metrics параллельно
            future_to_source = {
                executor.submit(collect_source, source_info): source_info[0]
                for source_info in monitoring_sources
            }

            # shock_score через канонический _collect_shock_score (Task 11 pending → None graceful)
            shock_future = executor.submit(self._collect_shock_score, symbol, timeframe)
            future_to_source[shock_future] = "shock_score"

            for future in as_completed(future_to_source, timeout=total_timeout):
                try:
                    source_name = future_to_source[future]
                    if source_name == "shock_score":
                        data = future.result()
                    else:
                        source_name, data = future.result()

                    if data is not None:
                        collected_data[source_name] = data
                        blocks_included.append(source_name)
                    else:
                        blocks_dropped.append(source_name)
                        context_degraded = True

                except Exception as e:
                    source_name = future_to_source[future]
                    self.logger.error(f"Future failed for {source_name}: {e}")
                    blocks_dropped.append(source_name)
                    context_degraded = True

        # Build context string
        context_lines = [
            f"=== MONITORING CONTEXT ({symbol}/{timeframe}) ===",
            f"Task Type: monitoring",
            f"Fast Lane: {is_fast}",
            f"Timestamp: {start_time}",
            ""
        ]

        # [BRAKE_ALERT] блок первый - только если shock_score > 0.25
        shock_data = collected_data.get("shock_score")
        shock_score_value = None
        if isinstance(shock_data, dict):
            shock_score_value = shock_data.get("shock_score")

        if isinstance(shock_score_value, (int, float)) and shock_score_value > 0.25:
            context_lines.append("[BRAKE_ALERT]")
            context_lines.append(f"  shock_score: {shock_score_value}")
            brake_level = "MEDIUM" if shock_score_value <= 0.5 else "HIGH" if shock_score_value <= 0.75 else "CRITICAL"
            context_lines.append(f"  brake_level: {brake_level}")
            context_lines.append(f"  rationale: shock_score exceeds monitoring threshold (0.25)")
            context_lines.append("")

        # Остальные блоки в порядке: [REGIME_HEALTH], [SHOCK_SCORE], [DRIFT]
        if "regime" in collected_data:
            regime = collected_data["regime"]
            context_lines.append("[REGIME_HEALTH]")
            if isinstance(regime, dict):
                regime_type = regime.get("regime_type", "unknown")
                context_lines.append(f"  regime_type: {regime_type}")
                if "confidence" in regime:
                    context_lines.append(f"  confidence: {regime['confidence']}")
                if "last_updated" in regime:
                    context_lines.append(f"  last_updated: {regime['last_updated']}")
            context_lines.append("")

        if "shock_score" in collected_data:
            context_lines.append("[SHOCK_SCORE]")
            if isinstance(shock_data, dict):
                for key, value in shock_data.items():
                    if key != "shock_score":  # shock_score уже показан в BRAKE_ALERT если нужно
                        context_lines.append(f"  {key}: {value}")
                if shock_score_value is not None:
                    context_lines.append(f"  current_value: {shock_score_value}")
            context_lines.append("")

        if "drift_metrics" in collected_data:
            drift = collected_data["drift_metrics"]
            context_lines.append("[DRIFT]")
            if isinstance(drift, dict):
                for key, value in drift.items():
                    if isinstance(value, (str, int, float)):
                        context_lines.append(f"  {key}: {value}")
                    else:
                        context_lines.append(f"  {key}: {str(value)[:50]}")
            context_lines.append("")

        if blocks_dropped:
            context_lines.append("[MISSING SOURCES]")
            for dropped in blocks_dropped:
                context_lines.append(f"  - {dropped}")
            context_lines.append("")

        # Budget enforcement для monitoring context
        priority_order = ["brake_alert", "shock_score", "regime_health", "drift"]  # brake_alert критичный
        context_lines, token_count, blocks_included, blocks_dropped = self._enforce_budget(
            context_lines, blocks_included, blocks_dropped, priority_order
        )
        if any("budget_exceeded" in d for d in blocks_dropped):
            context_degraded = True

        context_text = "\n".join(context_lines)

        # Status determination — applies L-08 clarification (никогда ABORTED)
        if context_degraded:
            status = "DEGRADED"
        else:
            status = "OK"

        elapsed_time = time.time() - start_time
        self.logger.info(f"Monitoring context built in {elapsed_time:.2f}s, "
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

    def _build_postmortem_context(self, symbol: str, timeframe: str) -> ContextResult:
        """
        Context building для task_type='postmortem'. Slow Lane only.
        По ТЗ Задача 3: scope "audit".

        Источники: audit entries из predictions history.
        Всегда Slow Lane. Минималистичная реализация с одним источником.
        """
        start_time = time.time()
        context_degraded = False
        blocks_included = []
        blocks_dropped = []

        # Postmortem context - всегда Slow Lane
        is_fast = False  # postmortem никогда не Fast Lane

        self.logger.info(f"Building postmortem context for {symbol}/{timeframe}, Slow Lane")

        # Единственный источник: audit_entries
        try:
            audit_entries = self._collect_audit_entries(symbol, timeframe)
            if audit_entries is not None:
                blocks_included.append("audit_entries")
            else:
                blocks_dropped.append("audit_entries")
                context_degraded = True

        except Exception as e:
            self.logger.error(f"Error collecting audit entries: {e}")
            blocks_dropped.append("audit_entries")
            context_degraded = True
            audit_entries = None

        # Build context string
        context_lines = [
            f"=== POSTMORTEM CONTEXT ({symbol}/{timeframe}) ===",
            f"Task Type: postmortem",
            f"Fast Lane: {is_fast}",
            f"Timestamp: {start_time}",
            ""
        ]

        # [AUDIT_ENTRIES] блок
        if audit_entries is not None:
            context_lines.append("[AUDIT_ENTRIES]")
            context_lines.append(f"  count: {len(audit_entries)}")
            for i, entry in enumerate(audit_entries[:5]):  # Limit to first 5 for context
                if isinstance(entry, dict):
                    prediction_id = entry.get("prediction_id", f"entry_{i}")
                    result = entry.get("result", entry.get("outcome", "unknown"))
                    accuracy = entry.get("accuracy", entry.get("score", "N/A"))
                    context_lines.append(f"  [{i}] {prediction_id}: result={result}, accuracy={accuracy}")
            if len(audit_entries) > 5:
                context_lines.append(f"  ... and {len(audit_entries) - 5} more entries")
            context_lines.append("")

        if blocks_dropped:
            context_lines.append("[MISSING SOURCES]")
            for dropped in blocks_dropped:
                context_lines.append(f"  - {dropped}")
            context_lines.append("")

        # Budget enforcement для postmortem context
        priority_order = ["audit_entries"]  # один источник
        context_lines, token_count, blocks_included, blocks_dropped = self._enforce_budget(
            context_lines, blocks_included, blocks_dropped, priority_order
        )
        if any("budget_exceeded" in d for d in blocks_dropped):
            context_degraded = True

        context_text = "\n".join(context_lines)

        # Status determination — applies L-08 clarification (никогда ABORTED)
        if context_degraded:
            status = "DEGRADED"
        else:
            status = "OK"

        elapsed_time = time.time() - start_time
        self.logger.info(f"Postmortem context built in {elapsed_time:.2f}s, "
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


def build_context(query: str, symbol: str, timeframe: str, task_type: str = "forecast") -> ContextResult:
    """Module-level wrapper для build_context."""
    orchestrator = ContextOrchestrator()
    return orchestrator.build_context(query, symbol, timeframe, task_type)


def save_session(summary: str, new_items: list[str], bias: str | None = None) -> None:
    """Module-level wrapper для save_session."""
    orchestrator = ContextOrchestrator()
    return orchestrator.save_session(summary, new_items, bias)