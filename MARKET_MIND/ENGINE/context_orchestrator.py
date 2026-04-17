"""
Context Orchestrator - центральный диспетчер системы для сборки контекста прогноза
Crypto Intelligence System V10.0-r1

Собирает все необходимые входы для Model Core:
- Параллельно вызывает AXM Guard и Prior Manager
- Управляет таймаутами для каждого входа отдельно
- При сбое любого входа активирует failover
- Возвращает собранный контекст с пометками о качестве
"""

import time
import json
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, TimeoutError, as_completed
from typing import Dict, Any, Optional

# Настройка логирования
log_dir = Path(r'C:\CODE\MARKET ANALYSIS\MARKET_MIND\LAYER_H_INTERFACE\logs')
log_dir.mkdir(parents=True, exist_ok=True)
log_file = log_dir / 'orchestrator.log'

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ContextOrchestrator:
    """
    Центральный диспетчер для сборки контекста прогноза.
    Управляет 6 входами с индивидуальными таймаутами и failover логикой.
    """

    def __init__(self):
        """Инициализация оркестратора"""
        self.timeouts = {
            'feature_snapshot': 0.1,      # 100ms - BLOCK
            'validated_patterns': 0.15,   # 150ms - BLOCK
            'regime_context': 0.08,       # 80ms - DEGRADE
            'prior_snapshot': 0.2,        # 200ms - SKIP
            'timeframe_context': 0.08,    # 80ms - DEGRADE
            'change_id': 0.05             # 50ms - SKIP
        }

    def orchestrate(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Главный метод оркестрации контекста

        Args:
            request: Запрос на прогноз с symbol, timeframe, horizon_hours и др.

        Returns:
            Собранный контекст для Model Core или ABORTED при критических сбоях
        """
        start_time = time.time()
        request_id = request.get('request_id', str(uuid.uuid4()))
        symbol = request['symbol']
        timeframe = request['timeframe']

        logger.info(f"{request_id} | {symbol} | orchestrating context | start")

        try:
            # Инициализация результата
            context = {
                'request_id': request_id,
                'symbol': symbol,
                'timeframe': timeframe,
                'horizon_hours': request['horizon_hours'],
                'status': 'OK',
                'context_degraded': False,
                'total_penalty': 0.0,
                'assembled_at': datetime.now(timezone.utc).isoformat()
            }

            # Сбор обязательных входов (BLOCK)
            try:
                block_inputs = self._collect_block_inputs(symbol, timeframe)
                context.update(block_inputs)
            except TimeoutError as e:
                return self._abort_context(request_id, str(e))

            # Сбор опциональных входов (DEGRADE/SKIP) параллельно
            optional_inputs = self._collect_optional_inputs(symbol, timeframe)
            context.update(optional_inputs)

            # Параллельный вызов AXM Guard и Prior Manager
            parallel_results = self._run_parallel_guards(context)
            context.update(parallel_results)

            # BTC как macro индикатор
            if request.get('btc_context', True):
                context['btc_macro'] = self._get_btc_macro()

            # Финализация
            end_time = time.time()
            latency_ms = round((end_time - start_time) * 1000, 1)
            context['assembly_latency_ms'] = latency_ms

            # Определение финального статуса
            if context['total_penalty'] > 0 or context['context_degraded']:
                context['status'] = 'DEGRADED'

            logger.info(
                f"{request_id} | {symbol} | {context['status']} | "
                f"{latency_ms}ms | penalty={context['total_penalty']}"
            )

            return context

        except Exception as e:
            logger.error(f"{request_id} | {symbol} | ERROR | {str(e)}")
            return self._abort_context(request_id, f"unexpected_error: {str(e)}")

    def _collect_block_inputs(self, symbol: str, timeframe: str) -> Dict[str, Any]:
        """Сбор обязательных входов (BLOCK) с жёсткими таймаутами"""
        inputs = {}

        with ThreadPoolExecutor(max_workers=2) as executor:
            # Запуск обязательных входов параллельно
            futures = {
                'feature_snapshot': executor.submit(self._get_feature_snapshot, symbol, timeframe),
                'validated_patterns': executor.submit(self._get_validated_patterns, symbol, 'unknown')
            }

            # Сбор результатов с таймаутами
            for input_name, future in futures.items():
                try:
                    inputs[input_name] = future.result(timeout=self.timeouts[input_name])
                except TimeoutError:
                    raise TimeoutError(f"timeout_{input_name}")
                except Exception as e:
                    raise TimeoutError(f"error_{input_name}: {str(e)}")

        return inputs

    def _collect_optional_inputs(self, symbol: str, timeframe: str) -> Dict[str, Any]:
        """Сбор опциональных входов (DEGRADE/SKIP) с failover"""
        inputs = {
            'regime_context': None,
            'prior_snapshot': None,
            'timeframe_context': None,
            'change_id': None,
            'total_penalty': 0.0,
            'context_degraded': False
        }

        with ThreadPoolExecutor(max_workers=4) as executor:
            # Запуск опциональных входов
            futures = {
                'regime_context': executor.submit(self._get_regime_context, symbol),
                'prior_snapshot': executor.submit(self._get_prior_snapshot),
                'timeframe_context': executor.submit(self._get_timeframe_context, timeframe),
                'change_id': executor.submit(self._get_change_id)
            }

            # Сбор результатов с failover логикой
            for input_name, future in futures.items():
                try:
                    inputs[input_name] = future.result(timeout=self.timeouts[input_name])
                except TimeoutError:
                    if input_name == 'regime_context':
                        # DEGRADE: использовать default и penalty
                        inputs[input_name] = {"regime": "sideways", "confidence": 0.50, "defaulted": True}
                        inputs['total_penalty'] += 0.05
                        logger.warning(f"regime_context timeout → degraded to sideways")
                    else:
                        # SKIP: оставить None
                        inputs[input_name] = None
                        if input_name in ['prior_snapshot']:
                            inputs['context_degraded'] = True
                        logger.warning(f"{input_name} timeout → skipped")
                except Exception as e:
                    logger.warning(f"{input_name} error: {str(e)} → skipped")
                    inputs[input_name] = None

        return inputs

    def _run_parallel_guards(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Параллельный запуск AXM Guard и Prior Manager"""
        guards = {}

        with ThreadPoolExecutor(max_workers=2) as executor:
            # Параллельный запуск guards
            future_axm = executor.submit(self._run_axm_guard, context)
            future_prior = executor.submit(self._validate_priors, context)

            # Сбор результатов
            try:
                guards['axm_guard_result'] = future_axm.result(timeout=0.1)
            except:
                guards['axm_guard_result'] = {"passed": False, "violations": ["timeout"], "stub": True}

            try:
                guards['prior_validation'] = future_prior.result(timeout=0.1)
            except:
                guards['prior_validation'] = {"valid": True, "warnings": ["timeout"], "stub": True}

        return guards

    def _abort_context(self, request_id: str, reason: str) -> Dict[str, Any]:
        """Создание ABORTED контекста при критических сбоях"""
        logger.error(f"{request_id} | ABORTED | {reason}")
        return {
            "request_id": request_id,
            "status": "ABORTED",
            "reason": reason,
            "context_degraded": True,
            "assembled_at": datetime.now(timezone.utc).isoformat()
        }

    # ========== ЗАГЛУШКИ ДЛЯ БУДУЩИХ МОДУЛЕЙ ==========

    def _get_feature_snapshot(self, symbol: str, timeframe: str) -> Dict[str, Any]:
        """Заглушка — будет заменена Feature Store (Task 13)"""
        time.sleep(0.02)  # Имитация работы
        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "rsi": 45.2,
            "macd": 0.001,
            "volume_ratio": 1.2,
            "bollinger_position": 0.35,
            "trend_strength": 0.6,
            "stub": True
        }

    def _get_validated_patterns(self, symbol: str, regime: str) -> list:
        """Заглушка — будет заменена Pattern Registry (Task 7)"""
        time.sleep(0.03)  # Имитация работы
        return [
            {"pattern_id": "doji_reversal", "confidence": 0.72, "direction": "bearish"},
            {"pattern_id": "volume_surge", "confidence": 0.85, "direction": "bullish"}
        ]

    def _get_regime_context(self, symbol: str) -> Dict[str, Any]:
        """Заглушка — будет заменена Regime Detector (Task 14)"""
        time.sleep(0.02)  # Имитация работы
        return {
            "regime": "sideways",
            "confidence": 0.60,
            "regime_duration_hours": 48,
            "volatility_regime": "normal",
            "stub": True
        }

    def _get_prior_snapshot(self) -> Optional[Dict[str, Any]]:
        """Заглушка — будет заменена Prior Manager (Task 29)"""
        time.sleep(0.05)  # Имитация работы
        return {
            "prior_id": "structural_001",
            "weight": 0.3,
            "source": "historical_pattern",
            "stub": True
        }

    def _get_timeframe_context(self, timeframe: str) -> Dict[str, Any]:
        """Заглушка — будет заменена Timeframe Core"""
        time.sleep(0.01)  # Имитация работы
        return {
            "timeframe": timeframe,
            "timeframe_category": "Standard Core",
            "horizon_compatibility": "full",
            "stub": True
        }

    def _get_change_id(self) -> Optional[str]:
        """Заглушка — будет заменена Change Detection"""
        time.sleep(0.01)  # Имитация работы
        return None  # Baseline mode

    def _get_btc_macro(self) -> Dict[str, Any]:
        """Заглушка — будет заменена Feature Store BTC (Task 13)"""
        time.sleep(0.01)  # Имитация работы
        return {
            "symbol": "BTCUSDT",
            "trend": "neutral",
            "dominance": 52.3,
            "correlation_target": 0.78,
            "macro_regime": "consolidation",
            "stub": True
        }

    def _run_axm_guard(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Заглушка — будет заменена AXM Guard (Task 29)"""
        time.sleep(0.02)  # Имитация работы
        return {
            "passed": True,
            "violations": [],
            "checked_axioms": ["AXM_001", "AXM_003", "AXM_007"],
            "stub": True
        }

    def _validate_priors(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Заглушка — валидация structural priors"""
        time.sleep(0.03)  # Имитация работы
        return {
            "valid": True,
            "warnings": [],
            "applied_priors": ["PRI_001", "PRI_005"],
            "stub": True
        }