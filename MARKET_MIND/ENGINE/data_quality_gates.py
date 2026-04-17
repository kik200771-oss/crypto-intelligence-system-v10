#!/usr/bin/env python3
"""
Data Quality Gates для Crypto Intelligence System V10.0-r1
6 последовательных проверок качества входящих OHLCV данных
"""

import json
import logging
import statistics
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any, Tuple


class DataQualityGates:
    """
    6 последовательных проверок качества данных:
    1. Market Integrity - аномальные скачки цен
    2. Volume Anomaly - аномалии объёма
    3. Price Continuity - проверка непрерывности цен
    4. Timestamp Validation - валидация временных меток
    5. Source Reliability - доверие к источнику
    6. Staleness Check - проверка свежести данных
    """

    def __init__(self, market_mind_root: str = None):
        if market_mind_root is None:
            market_mind_root = Path(__file__).parent.parent
        else:
            market_mind_root = Path(market_mind_root)

        self.market_mind_root = market_mind_root
        self.log_dir = self.market_mind_root / "LAYER_B_DATA" / "quality_logs"

        # Создаем директорию для логов
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Настраиваем логирование
        self._setup_logging()

        # Загружаем конфигурации
        self._load_configs()

        self.logger.info("DataQualityGates инициализированы")

    def _setup_logging(self):
        """Настройка логирования результатов gates"""
        today = datetime.now().strftime("%Y-%m-%d")
        log_file = self.log_dir / f"gates_{today}.log"

        self.logger = logging.getLogger("data_quality_gates")
        self.logger.setLevel(logging.INFO)

        # Удаляем существующие handlers
        self.logger.handlers.clear()

        # Файловый handler
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)

        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)

    def _load_configs(self):
        """Загружает конфигурационные файлы"""
        # Загружаем stale data policy
        stale_policy_file = self.market_mind_root / "CONFIG" / "stale_data_policy.json"
        try:
            with open(stale_policy_file, 'r', encoding='utf-8') as f:
                self.stale_policy = json.load(f)
        except Exception as e:
            self.logger.error(f"Ошибка загрузки stale_data_policy.json: {e}")
            self.stale_policy = {"stale_cache_ttl_seconds": 300}

        # Загружаем trust registry
        trust_registry_file = self.market_mind_root / "LAYER_C_KNOWLEDGE" / "trust_system" / "trust_registry.json"
        try:
            with open(trust_registry_file, 'r', encoding='utf-8') as f:
                trust_data = json.load(f)
                self.trust_registry = trust_data.get("sources", {})
        except Exception as e:
            self.logger.error(f"Ошибка загрузки trust_registry.json: {e}")
            self.trust_registry = {}

    def _gate_1_market_integrity(self, candles: List[Dict], symbol: str) -> Dict:
        """
        Gate 1: Market Integrity
        Проверяет на аномальные ценовые скачки (>30% за 1 свечу)
        failure_mode: block
        """
        gate_result = {
            "gate_id": 1,
            "gate_name": "market_integrity",
            "passed": True,
            "failure_mode": "block",
            "penalty": 0.0,
            "data_stale": False,
            "message": "Целостность рынка OK"
        }

        try:
            for i, candle in enumerate(candles):
                if i == 0:
                    continue  # Первую свечу не с чем сравнивать

                prev_close = candles[i-1]["close"]
                curr_open = candle["open"]
                curr_high = candle["high"]
                curr_low = candle["low"]
                curr_close = candle["close"]

                # Проверяем скачки между свечами
                price_change = abs(curr_open - prev_close) / prev_close
                if price_change > 0.30:  # 30% скачок
                    gate_result.update({
                        "passed": False,
                        "message": f"Аномальный скачок цены {price_change:.2%} на свече {i} ({symbol})"
                    })
                    return gate_result

                # Проверяем внутри свечи
                intrabar_high_change = abs(curr_high - curr_open) / curr_open
                intrabar_low_change = abs(curr_low - curr_open) / curr_open

                if intrabar_high_change > 0.30 or intrabar_low_change > 0.30:
                    gate_result.update({
                        "passed": False,
                        "message": f"Аномальный внутрисвечной скачок {max(intrabar_high_change, intrabar_low_change):.2%} на свече {i} ({symbol})"
                    })
                    return gate_result

        except Exception as e:
            gate_result.update({
                "passed": False,
                "message": f"Ошибка в Gate 1: {str(e)}"
            })

        return gate_result

    def _gate_2_volume_anomaly(self, candles: List[Dict], symbol: str) -> Dict:
        """
        Gate 2: Volume Anomaly
        Объём в пределах 10× от rolling average за 20 периодов
        failure_mode: warn
        """
        gate_result = {
            "gate_id": 2,
            "gate_name": "volume_anomaly",
            "passed": True,
            "failure_mode": "warn",
            "penalty": 0.0,
            "data_stale": False,
            "message": "Объём в норме"
        }

        try:
            if len(candles) < 3:
                return gate_result  # Недостаточно данных

            # Берём последние свечи для расчёта среднего
            volumes = [c["volume"] for c in candles[-min(20, len(candles)):]]
            avg_volume = statistics.mean(volumes)

            # Проверяем последнюю свечу
            last_volume = candles[-1]["volume"]
            volume_ratio = last_volume / avg_volume if avg_volume > 0 else 0

            if volume_ratio > 10.0:  # Объём превышает в 10 раз
                gate_result.update({
                    "passed": False,
                    "penalty": -0.05,
                    "message": f"Аномальный объём: {volume_ratio:.1f}x от среднего ({symbol})"
                })

        except Exception as e:
            gate_result.update({
                "passed": False,
                "penalty": -0.05,
                "message": f"Ошибка в Gate 2: {str(e)}"
            })

        return gate_result

    def _gate_3_price_continuity(self, candles: List[Dict], symbol: str) -> Dict:
        """
        Gate 3: Price Continuity
        Проверяет gaps - цена открытия ≈ цене закрытия предыдущей свечи (допуск 5%)
        failure_mode: degrade
        """
        gate_result = {
            "gate_id": 3,
            "gate_name": "price_continuity",
            "passed": True,
            "failure_mode": "degrade",
            "penalty": 0.0,
            "data_stale": False,
            "message": "Непрерывность цен OK"
        }

        try:
            for i in range(1, len(candles)):
                prev_close = candles[i-1]["close"]
                curr_open = candles[i]["open"]

                gap = abs(curr_open - prev_close) / prev_close if prev_close > 0 else 0

                if gap > 0.05:  # 5% gap
                    gate_result.update({
                        "passed": False,
                        "penalty": -0.03,
                        "message": f"Gap {gap:.2%} между свечами {i-1}-{i} ({symbol})"
                    })
                    break

        except Exception as e:
            gate_result.update({
                "passed": False,
                "penalty": -0.03,
                "message": f"Ошибка в Gate 3: {str(e)}"
            })

        return gate_result

    def _gate_4_timestamp_validation(self, candles: List[Dict], symbol: str) -> Dict:
        """
        Gate 4: Timestamp Validation
        Временные метки монотонно возрастают, нет дубликатов
        failure_mode: block
        """
        gate_result = {
            "gate_id": 4,
            "gate_name": "timestamp_validation",
            "passed": True,
            "failure_mode": "block",
            "penalty": 0.0,
            "data_stale": False,
            "message": "Временные метки OK"
        }

        try:
            timestamps = [c["timestamp"] for c in candles]

            # Проверяем на дубликаты
            if len(timestamps) != len(set(timestamps)):
                gate_result.update({
                    "passed": False,
                    "message": f"Обнаружены дублирующиеся временные метки ({symbol})"
                })
                return gate_result

            # Проверяем монотонность
            for i in range(1, len(timestamps)):
                if timestamps[i] <= timestamps[i-1]:
                    gate_result.update({
                        "passed": False,
                        "message": f"Нарушение монотонности временных меток между {i-1} и {i} ({symbol})"
                    })
                    return gate_result

        except Exception as e:
            gate_result.update({
                "passed": False,
                "message": f"Ошибка в Gate 4: {str(e)}"
            })

        return gate_result

    def _gate_5_source_reliability(self, candles: List[Dict], symbol: str) -> Dict:
        """
        Gate 5: Source Reliability
        trust_score источника из trust_registry.json ≥ 0.3
        failure_mode: degrade
        """
        gate_result = {
            "gate_id": 5,
            "gate_name": "source_reliability",
            "passed": True,
            "failure_mode": "degrade",
            "penalty": 0.0,
            "data_stale": False,
            "message": "Источник надёжен"
        }

        try:
            # Берём источник из последней свечи
            source = candles[-1].get("source", "unknown")
            trust_score = self.trust_registry.get(source, {}).get("trust", 0.0)

            if trust_score < 0.3:
                gate_result.update({
                    "passed": False,
                    "penalty": -0.03,
                    "message": f"Низкое доверие к источнику {source}: {trust_score} < 0.3 ({symbol})"
                })

        except Exception as e:
            gate_result.update({
                "passed": False,
                "penalty": -0.03,
                "message": f"Ошибка в Gate 5: {str(e)}"
            })

        return gate_result

    def _gate_6_staleness_check(self, candles: List[Dict], symbol: str) -> Dict:
        """
        Gate 6: Staleness Check
        Данные не старше stale_cache_ttl из CONFIG/stale_data_policy.json
        failure_mode: block → stale_cache fallback
        """
        gate_result = {
            "gate_id": 6,
            "gate_name": "staleness_check",
            "passed": True,
            "failure_mode": "block",
            "penalty": 0.0,
            "data_stale": False,
            "message": "Данные свежие"
        }

        try:
            now = datetime.now(timezone.utc).timestamp()
            last_timestamp = candles[-1]["timestamp"]

            # Если timestamp в миллисекундах, конвертируем
            if last_timestamp > 1e12:
                last_timestamp = last_timestamp / 1000

            age_seconds = now - last_timestamp
            ttl_seconds = self.stale_policy.get("stale_cache_ttl_seconds", 300)

            if age_seconds > ttl_seconds:
                # Активируем stale cache fallback
                gate_result.update({
                    "passed": False,  # Но не блокируем полностью
                    "data_stale": True,
                    "penalty": self.stale_policy.get("uncertainty_penalty", 0.1),
                    "message": f"Устаревшие данные: {age_seconds:.0f}s > {ttl_seconds}s, используем stale cache ({symbol})"
                })

        except Exception as e:
            gate_result.update({
                "passed": False,
                "data_stale": True,
                "penalty": 0.1,
                "message": f"Ошибка в Gate 6: {str(e)}"
            })

        return gate_result

    def run(self, candles: List[Dict], symbol: str) -> Dict:
        """
        Запускает все 6 gates на входящих данных

        Args:
            candles: Список OHLCV свечей
            symbol: Символ торговой пары

        Returns:
            Dict: Итоговый результат всех проверок
        """
        start_time = datetime.now()

        # Запускаем все gates
        gates_results = []
        gates_results.append(self._gate_1_market_integrity(candles, symbol))
        gates_results.append(self._gate_2_volume_anomaly(candles, symbol))
        gates_results.append(self._gate_3_price_continuity(candles, symbol))
        gates_results.append(self._gate_4_timestamp_validation(candles, symbol))
        gates_results.append(self._gate_5_source_reliability(candles, symbol))
        gates_results.append(self._gate_6_staleness_check(candles, symbol))

        # Подсчитываем итоговый результат
        all_passed = all(gate["passed"] for gate in gates_results)
        blocked = any(
            not gate["passed"] and gate["failure_mode"] == "block" and not gate.get("data_stale", False)
            for gate in gates_results
        )
        data_stale = any(gate.get("data_stale", False) for gate in gates_results)
        total_penalty = sum(gate["penalty"] for gate in gates_results)

        # Определяем quality_flag
        quality_flag = "ok"
        if not all_passed and not blocked:
            quality_flag = "degraded"

        result = {
            "symbol": symbol,
            "timestamp": datetime.now().isoformat(),
            "all_passed": all_passed,
            "blocked": blocked,
            "data_stale": data_stale,
            "total_penalty": total_penalty,
            "quality_flag": quality_flag,
            "gates": gates_results,
            "processing_time_ms": (datetime.now() - start_time).total_seconds() * 1000
        }

        # Логируем результат
        self.logger.info(f"Gates result for {symbol}: passed={all_passed}, blocked={blocked}, penalty={total_penalty:.3f}")

        return result


def main():
    """Тестирование Data Quality Gates"""
    print("🧪 Тестирование Data Quality Gates")

    gates = DataQualityGates()

    # Тест 1: Чистые данные
    clean_candles = [
        {"symbol": "BTCUSDT", "timestamp": 1700000000, "open": 45000, "high": 45500,
         "low": 44800, "close": 45200, "volume": 1234, "source": "Binance"},
        {"symbol": "BTCUSDT", "timestamp": 1700003600, "open": 45200, "high": 45600,
         "low": 45100, "close": 45400, "volume": 1100, "source": "Binance"},
    ]

    result = gates.run(clean_candles, "BTCUSDT")
    print(f"Чистые данные: passed={result['all_passed']}, blocked={result['blocked']}")

    # Тест 2: Ценовой скачок (Gate 1)
    spike_candles = [
        {"symbol": "BTCUSDT", "timestamp": 1700000000, "open": 45000, "high": 45500,
         "low": 44800, "close": 45200, "volume": 1234, "source": "Binance"},
        {"symbol": "BTCUSDT", "timestamp": 1700003600, "open": 45200, "high": 90000,
         "low": 45100, "close": 88000, "volume": 1100, "source": "Binance"},
    ]

    result = gates.run(spike_candles, "BTCUSDT")
    print(f"Ценовой скачок: passed={result['all_passed']}, blocked={result['blocked']}")
    print(f"Gate 1 result: {result['gates'][0]['message']}")


if __name__ == "__main__":
    main()