#!/usr/bin/env python3
"""
TASK 01: Initialize CIS V10.0-r1 System
Создание полной структуры директорий и конфигурационных файлов для Crypto Intelligence System
"""

import json
import os
from pathlib import Path
from datetime import datetime
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SystemInitializer:
    def __init__(self, base_path="C:\\КОДИНГ\\MARKET ANALYSIS\\MARKET_MIND"):
        self.base_path = Path(base_path)
        logger.info(f"Инициализация системы в: {self.base_path}")

    def create_directory_structure(self):
        """Создание полной структуры директорий"""

        directories = [
            # Основные директории
            "ENGINE",
            "SCHEMAS",
            "CONFIG",
            "meta",

            # 8 слоев системы
            "LAYER_A_RESEARCH/patterns",
            "LAYER_A_RESEARCH/hypotheses",
            "LAYER_A_RESEARCH/experiments",
            "LAYER_A_RESEARCH/negatives",
            "LAYER_A_RESEARCH/models",
            "LAYER_A_RESEARCH/audit",
            "LAYER_A_RESEARCH/meta",

            "LAYER_B_DATA/features/snapshots",
            "LAYER_B_DATA/quality_logs",
            "LAYER_B_DATA/onchain",
            "LAYER_B_DATA/macro",
            "LAYER_B_DATA/news",

            "LAYER_C_KNOWLEDGE/knowledge_base",
            "LAYER_C_KNOWLEDGE/trust_system",

            "LAYER_D_MODEL/model_versions",
            "LAYER_D_MODEL/predictions",
            "LAYER_D_MODEL/weights",
            "LAYER_D_MODEL/shock_log",

            "LAYER_E_VALIDATION/backtest_results",
            "LAYER_E_VALIDATION/validation_reports",

            "LAYER_F_FEEDBACK/prediction_records",
            "LAYER_F_FEEDBACK/outcomes",
            "LAYER_F_FEEDBACK/drift_log",
            "LAYER_F_FEEDBACK/recalibration_log",
            "LAYER_F_FEEDBACK/integral_bias_log",

            "LAYER_G_NEWS/raw",
            "LAYER_G_NEWS/scored",

            "LAYER_H_INTERFACE/logs",
            "LAYER_H_INTERFACE/exports"
        ]

        created_count = 0
        for directory in directories:
            dir_path = self.base_path / directory
            if not dir_path.exists():
                dir_path.mkdir(parents=True, exist_ok=True)
                logger.info(f"✅ Создана директория: {directory}")
                created_count += 1
            else:
                logger.info(f"⏭️  Директория уже существует: {directory}")

        logger.info(f"Создано директорий: {created_count}/{len(directories)}")

    def create_system_manifest(self):
        """Создание CONFIG/system_manifest.json"""

        manifest = {
            "version": "10.0",
            "revision": "r1",
            "created_at": datetime.now().isoformat(),
            "canon": {
                "math_model": "v6.3-sealed",
                "schematics": "V5",
                "tz": "V10.0-r1"
            },
            "model_approximations": {
                "linear_aggregation": {
                    "description": "Линейная агрегация сигналов — предполагает аддитивность",
                    "review_condition": ">=50 confirmed patterns AND OOS accuracy > 0.65",
                    "status": "active"
                },
                "pi_lite": {
                    "description": "PI-lite вместо полного PID — нестационарный рынок",
                    "review_condition": ">=200 verified forecasts",
                    "status": "active"
                }
            },
            "required_modules": 30,
            "btc_as_macro_indicator": True,
            "trading_pairs_mode": "multi_pair_btc_context"
        }

        manifest_path = self.base_path / "CONFIG" / "system_manifest.json"
        if not manifest_path.exists():
            with open(manifest_path, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=2, ensure_ascii=False)
            logger.info("✅ Создан system_manifest.json")
        else:
            logger.info("⏭️  system_manifest.json уже существует")

    def create_component_status(self):
        """Создание CONFIG/component_status.json с 30 компонентами"""

        components = [
            "initialize_system", "schema_layer", "data_quality_gates", "context_orchestrator",
            "streamlit_ui_basic", "hypothesis_formalizer", "experiment_registry",
            "pattern_registry", "backtester", "validation_engine", "insight_saver",
            "knowledge_ingester", "knowledge_search", "feature_store", "regime_detector",
            "news_engine", "trust_manager", "macro_onchain", "negative_knowledge_manager",
            "pattern_decay_monitor", "evidence_grading_engine", "model_core",
            "decision_audit", "pattern_dsl_compiler", "feedback_system",
            "prediction_tracker", "rest_api", "backup_reports", "prior_manager",
            "determinism_contract"
        ]

        component_status = {}
        for component in components:
            component_status[component] = {
                "status": "not_started" if component != "initialize_system" else "ready",
                "updated_at": datetime.now().isoformat() if component == "initialize_system" else None,
                "notes": "Система инициализирована" if component == "initialize_system" else ""
            }

        status_path = self.base_path / "CONFIG" / "component_status.json"
        with open(status_path, 'w', encoding='utf-8') as f:
            json.dump(component_status, f, indent=2, ensure_ascii=False)
        logger.info(f"✅ Создан component_status.json с {len(components)} компонентами")

    def create_triz_contradictions(self):
        """Создание CONFIG/triz_contradictions.json"""

        triz_data = {}
        triz_entries = [
            ("TRZ-001", "Точность ↑ vs Скорость первого прогноза ↓", "candidate status + staged approach", "resolved", "v7.0"),
            ("TRZ-002", "Полнота контекста ↑ vs Размер окна ↓", "Context Orchestrator task-aware", "resolved", "v7.0"),
            ("TRZ-003", "Чувствительность к паттернам ↑ vs Шум ↓", "Validation Engine + OOS + baseline", "resolved", "v7.0"),
            ("TRZ-004", "Адаптивность ↑ vs Стабильность весов ↓", "Control Law beta>=alpha + drift detection", "resolved", "v7.0"),
            ("TRZ-005", "Богатство KB ↑ vs Confirmation bias ↓", "KB = только контекст, Inference Boundary", "resolved", "v7.0"),
            ("TRZ-006", "Персонализация ↑ vs Объективность ↓", "bias_log + warnings (не фильтрация)", "resolved", "v7.1"),
            ("TRZ-007", "Глубина DSL ↑ vs Сложность создания ↓", "hypothesis_formalizer через Claude API", "resolved", "v7.1"),
            ("TRZ-008", "Понятность уверенности ↑ vs Честность uncertainty ↓", "conformal_intervals + calibration_bucket + UI rename", "resolved", "V9.0"),
            ("TRZ-009", "Скорость обучения ↑ vs Шум в весах ↓", "market_condition_adaptive rates", "resolved", "V9.0"),
            ("TRZ-010", "Богатство паттернов ↑ vs Мультиколлинеарность ↓", "Family Cap + Correlation Penalty + orthogonalized_weight", "resolved", "V9.0"),
            ("TRZ-011", "Детерминизм ↑ vs Адаптивность ↓", "Determinism Contract 8 параметров + H(Pi_t) hash", "resolved", "V10.0"),
            ("TRZ-012", "Calibration ↑ vs Скорость feedback ↓", "Tx_Forecast/Tx_Feedback split — две транзакции", "resolved", "V10.0"),
            ("TRZ-013", "Governance ↑ vs Operational flexibility ↓", "Config Governance Partition: Safe/Heuristic/Model-semantic", "resolved", "V10.0"),
            ("TRZ-014", "Epistemic guardrail ↑ vs Scoring speed ↓", "AXM = post-scoring guardrail only, не pre-filter", "resolved", "V10.0"),
            ("TRZ-015", "Stability ↑ vs Sensitivity к режимам ↓", "Multiple Lyapunov P_r + ADT tau=71", "resolved", "V10.0"),
            ("TRZ-016", "Coverage guarantee ↑ vs Interval width ↓", "Conformal UQ asymmetric + conservative fallback", "resolved", "V10.0"),
            ("TRZ-017", "Feasibility check ↑ vs Latency ↓", "B_sev weighted + lightweight per-cycle check", "resolved", "V10.0"),
            ("TRZ-018", "Защита данных ↑ vs Доступность при отказе Gate ↓", "Stale Cache Policy — degrade вместо block, stale_cache_ttl", "resolved", "V10.0"),
            ("TRZ-019", "Быстрый control ↑ vs Медленный governance ↓", "Fast/Slow Feedback Split — два независимых контура", "resolved", "V10.0"),
            ("TRZ-020", "Устойчивость ↑ vs Чувствительность ↓", "Oscillation circuit breaker + dampening rule (MAX_WEIGHT_DELTA, phase lag)", "resolved", "V10.0")
        ]

        for triz_id, contradiction, resolution, status, version in triz_entries:
            triz_data[triz_id] = {
                "contradiction": contradiction,
                "resolution": resolution,
                "status": status,
                "version": version
            }

        triz_path = self.base_path / "CONFIG" / "triz_contradictions.json"
        if not triz_path.exists():
            with open(triz_path, 'w', encoding='utf-8') as f:
                json.dump(triz_data, f, indent=2, ensure_ascii=False)
            logger.info(f"✅ Создан triz_contradictions.json с {len(triz_data)} записями")
        else:
            logger.info("⏭️  triz_contradictions.json уже существует")

    def create_market_axioms(self):
        """Создание CONFIG/market_axioms.json"""

        axioms = {
            "AXM_001": {
                "axiom": "Цена движется только через ордера",
                "epistemic_status": "approximate",
                "v10_proxy": "Volume spike + price change correlation (OHLCV)",
                "axiom_proxy": True,
                "causal_confidence_penalty": -0.15
            },
            "AXM_002": {
                "axiom": "Bid/ask — механизм ценообразования",
                "epistemic_status": "approximate",
                "v10_proxy": "High-Low spread proxy",
                "axiom_proxy": True,
                "causal_confidence_penalty": -0.15
            },
            "AXM_003": {
                "axiom": "Тренд имеет инерцию",
                "epistemic_status": "direct",
                "v10_proxy": "MA + momentum indicators"
            },
            "AXM_004": {
                "axiom": "Ликвидность влияет на движение",
                "epistemic_status": "approximate",
                "v10_proxy": "Volume относительно rolling average",
                "axiom_proxy": True,
                "causal_confidence_penalty": -0.15
            },
            "AXM_005": {
                "axiom": "Режим рынка определяет применимость паттернов",
                "epistemic_status": "direct",
                "v10_proxy": "Regime Detector R1-R6"
            },
            "AXM_006": {
                "axiom": "BTC — macro-индикатор для всех альткоинов",
                "epistemic_status": "direct",
                "v10_proxy": "BTC OHLCV + dominance"
            },
            "AXM_007": {
                "axiom": "Множественные подтверждения снижают шум",
                "epistemic_status": "direct",
                "v10_proxy": "Family Cap + Correlation Penalty"
            },
            "AXM_008": {
                "axiom": "Крупные участники оставляют следы в объёме",
                "epistemic_status": "approximate",
                "v10_proxy": "Volume outlier detection (candles > 3sigma)",
                "axiom_proxy": True,
                "causal_confidence_penalty": -0.15
            },
            "AXM_009": {
                "axiom": "Паттерн валиден только в своём режиме",
                "epistemic_status": "direct",
                "v10_proxy": "valid_in_regimes filter"
            }
        }

        axioms_path = self.base_path / "CONFIG" / "market_axioms.json"
        if not axioms_path.exists():
            with open(axioms_path, 'w', encoding='utf-8') as f:
                json.dump(axioms, f, indent=2, ensure_ascii=False)
            logger.info(f"✅ Создан market_axioms.json с {len(axioms)} аксиомами")
        else:
            logger.info("⏭️  market_axioms.json уже существует")

    def create_structural_priors(self):
        """Создание CONFIG/structural_priors.json"""

        priors = {
            "PRI_001": {"description": "Тренд продолжается чаще чем разворачивается", "default_weight": 1.0, "category": "trend", "review_condition": ">=100 trend samples"},
            "PRI_002": {"description": "Более высокий TF доминирует", "default_weight": 1.0, "category": "trend", "review_condition": "TF conflict analysis"},
            "PRI_003": {"description": "Sideways режим снижает signal quality", "default_weight": 1.0, "category": "regime", "review_condition": "Regime detection accuracy > 70%"},
            "PRI_004": {"description": "Stress режим — все паттерны под сомнением", "default_weight": 1.0, "category": "regime", "review_condition": "Stress regime identification"},
            "PRI_005": {"description": "BTC определяет направление альткоинов", "default_weight": 1.0, "category": "regime", "review_condition": "BTC-ALT correlation > 0.6"},
            "PRI_006": {"description": "IS accuracy > OOS accuracy = overfit", "default_weight": 1.0, "category": "validation", "review_condition": "IS/OOS gap analysis"},
            "PRI_007": {"description": "Confirmed_cases < 20 = ненадёжно", "default_weight": 1.0, "category": "validation", "review_condition": "Pattern sample size"},
            "PRI_008": {"description": "Паттерн вне valid_in_regimes = weight × 0.2", "default_weight": 1.0, "category": "validation", "review_condition": "Regime validity matrix"},
            "PRI_009": {"description": "Calibration_bucket=uncalibrated = высокая неопределённость", "default_weight": 1.0, "category": "uncertainty", "review_condition": "Calibration assessment"},
            "PRI_010": {"description": "Data_stale=True = расширить uncertainty interval", "default_weight": 1.0, "category": "uncertainty", "review_condition": "Data freshness impact"},
            "PRI_011": {"description": "Drift_level >= 3 = recalibration", "default_weight": 1.0, "category": "feedback", "review_condition": "Drift monitoring"},
            "PRI_012": {"description": "I-term reset при regime shift", "default_weight": 1.0, "category": "feedback", "review_condition": "Regime transition detection"},
            "PRI_013": {"description": "Phase_lag = 1 цикл для weight changes", "default_weight": 1.0, "category": "feedback", "review_condition": "Weight update stability"},
            "PRI_014": {"description": "AXM применяется после scoring, не до", "default_weight": 1.0, "category": "epistemic", "review_condition": "Scoring pipeline order"},
            "PRI_015": {"description": "KB влияет только на контекст, не на direction", "default_weight": 1.0, "category": "epistemic", "review_condition": "KB-bias monitoring"},
            "PRI_016": {"description": "GPT-критик = независимый взгляд без KB-контекста", "default_weight": 1.0, "category": "epistemic", "review_condition": "Critical analysis independence"},
            "PRI_017": {"description": "Fast Feedback max 200ms Claude-free", "default_weight": 1.0, "category": "operational", "review_condition": "Latency benchmarks"},
            "PRI_018": {"description": "Tx_Feedback = отдельная транзакция от Tx_Forecast", "default_weight": 1.0, "category": "operational", "review_condition": "Transaction separation"},
            "PRI_019": {"description": "Silence Debt = diagnostic только, не actuator", "default_weight": 1.0, "category": "operational", "review_condition": "Silence debt monitoring"}
        }

        priors_path = self.base_path / "CONFIG" / "structural_priors.json"
        if not priors_path.exists():
            with open(priors_path, 'w', encoding='utf-8') as f:
                json.dump(priors, f, indent=2, ensure_ascii=False)
            logger.info(f"✅ Создан structural_priors.json с {len(priors)} прайорами")
        else:
            logger.info("⏭️  structural_priors.json уже существует")

    def create_additional_configs(self):
        """Создание дополнительных конфигурационных файлов"""

        # Timeframe core config
        timeframe_config = {
            "mode": "standard_core",
            "description": "User-configurable. Default: Standard Core.",
            "standard_core": {
                "timeframes": ["15m", "1h", "4h", "1d"],
                "primary": "4h",
                "context": "1d",
                "fast_lane": ["1h", "4h"]
            },
            "tf_multipliers": {
                "1w": 1.5, "1d": 1.3, "4h": 1.0,
                "1h": 0.85, "15m": 0.7, "5m": 0.55, "1m": 0.4
            },
            "tf_conflict_penalty": -0.10,
            "tf_agreement_bonus": 0.05
        }

        tf_path = self.base_path / "CONFIG" / "timeframe_core.json"
        if not tf_path.exists():
            with open(tf_path, 'w', encoding='utf-8') as f:
                json.dump(timeframe_config, f, indent=2, ensure_ascii=False)
            logger.info("✅ Создан timeframe_core.json")

        # Stale data policy
        stale_policy = {
            "stale_cache_ttl_seconds": 300,
            "uncertainty_penalty": 0.10,
            "sources": {
                "ohlcv": {"ttl_seconds": 300},
                "orderbook": {"ttl_seconds": 60},
                "funding_rate": {"ttl_seconds": 3600},
                "onchain": {"ttl_seconds": 7200},
                "macro": {"ttl_seconds": 86400}
            }
        }

        stale_path = self.base_path / "CONFIG" / "stale_data_policy.json"
        if not stale_path.exists():
            with open(stale_path, 'w', encoding='utf-8') as f:
                json.dump(stale_policy, f, indent=2, ensure_ascii=False)
            logger.info("✅ Создан stale_data_policy.json")

    def create_template_files(self):
        """Создание шаблонных файлов"""

        # How to read me guide
        guide_content = """# CIS V10.0-r1 — Руководство для Claude

## Inference Boundary
KB влияет только на explanation и context quality.
Не на direction прогноза. Это защита от KB-bias.

## TF Hierarchy
1w > 1d > 4h > 1h > 15m > 5m > 1m
При конфликте: junior TF weight × 0.3, confidence -= 0.10
При согласованности: confidence += 0.05

## Epistemic Status
- direct: данные напрямую измеряют явление
- approximate: OHLCV-proxy, causal_confidence_penalty = -0.15
- uncertain: недостаточно данных

## Три правила канона
1. Stability proof ≠ predictive validity
2. Determinism ≠ correctness
3. Conformal coverage ≠ trading edge

## Операциональный сценарий
Трейдер → гипотеза → Claude анализирует → Система считает →
Claude интерпретирует → GPT (опционально) критикует →
Трейдер принимает решение
"""

        guide_path = self.base_path / "LAYER_A_RESEARCH" / "meta" / "how_to_read_me.md"
        if not guide_path.exists():
            with open(guide_path, 'w', encoding='utf-8') as f:
                f.write(guide_content)
            logger.info("✅ Создан how_to_read_me.md")

        # Research index
        index_data = {
            "patterns_count": 0,
            "hypotheses_count": 0,
            "experiments_count": 0,
            "last_updated": datetime.now().isoformat()
        }

        index_path = self.base_path / "LAYER_A_RESEARCH" / "meta" / "index.json"
        if not index_path.exists():
            with open(index_path, 'w', encoding='utf-8') as f:
                json.dump(index_data, f, indent=2, ensure_ascii=False)
            logger.info("✅ Создан index.json")

        # Trust registry
        trust_registry = {
            "sources": {
                "CoinDesk": {"trust": 0.5, "category": "news"},
                "CoinTelegraph": {"trust": 0.5, "category": "news"},
                "Decrypt": {"trust": 0.5, "category": "news"},
                "Glassnode": {"trust": 0.5, "category": "onchain"},
                "Binance": {"trust": 0.8, "category": "exchange_data"}
            }
        }

        trust_path = self.base_path / "LAYER_C_KNOWLEDGE" / "trust_system" / "trust_registry.json"
        if not trust_path.exists():
            with open(trust_path, 'w', encoding='utf-8') as f:
                json.dump(trust_registry, f, indent=2, ensure_ascii=False)
            logger.info("✅ Создан trust_registry.json")

        # Session state
        session_state = {
            "current_session": None,
            "active_pair": None,
            "active_timeframe": None,
            "last_forecast": None,
            "regime": "unknown",
            "silence_debt": 0,
            "shock_score": 0.0
        }

        session_path = self.base_path / "LAYER_D_MODEL" / "session_state.json"
        if not session_path.exists():
            with open(session_path, 'w', encoding='utf-8') as f:
                json.dump(session_state, f, indent=2, ensure_ascii=False)
            logger.info("✅ Создан session_state.json")

    def run_verification(self):
        """Проверка созданной системы"""
        logger.info("🔍 Запуск проверки системы...")

        try:
            # 1. Проверка директорий
            layers = ["LAYER_A_RESEARCH", "LAYER_B_DATA", "LAYER_C_KNOWLEDGE",
                      "LAYER_D_MODEL", "LAYER_E_VALIDATION", "LAYER_F_FEEDBACK",
                      "LAYER_G_NEWS", "LAYER_H_INTERFACE"]
            for layer in layers:
                layer_path = self.base_path / layer
                assert layer_path.exists(), f"Missing: {layer}"
            logger.info("✅ Все слои директорий созданы")

            # 2. Проверка manifest
            with open(self.base_path / "CONFIG" / "system_manifest.json", encoding='utf-8') as f:
                manifest = json.load(f)
            assert manifest["version"] == "10.0"
            assert "model_approximations" in manifest
            assert len(manifest["model_approximations"]) == 2
            logger.info("✅ Manifest проверен")

            # 3. Проверка компонентов
            with open(self.base_path / "CONFIG" / "component_status.json", encoding='utf-8') as f:
                components = json.load(f)
            assert len(components) == 30, f"Expected 30 components, got {len(components)}"
            logger.info("✅ Все 30 компонентов зарегистрированы")

            # 4. TRIZ проверка
            with open(self.base_path / "CONFIG" / "triz_contradictions.json", encoding='utf-8') as f:
                triz = json.load(f)
            assert len(triz) == 20
            logger.info("✅ TRIZ противоречения (20 шт) созданы")

            # 5. Аксиомы
            with open(self.base_path / "CONFIG" / "market_axioms.json", encoding='utf-8') as f:
                axioms = json.load(f)
            assert len(axioms) == 9
            logger.info("✅ Рыночные аксиомы (9 шт) созданы")

            # 6. Прайоры
            with open(self.base_path / "CONFIG" / "structural_priors.json", encoding='utf-8') as f:
                priors = json.load(f)
            assert len(priors) == 19
            logger.info("✅ Структурные прайоры (19 шт) созданы")

            logger.info("🎉 ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ! Задача 1 выполнена успешно.")
            return True

        except Exception as e:
            logger.error(f"❌ Ошибка проверки: {e}")
            return False

    def initialize(self):
        """Главная функция инициализации"""
        logger.info("🚀 Начинаем инициализацию CIS V10.0-r1 системы")

        try:
            self.create_directory_structure()
            self.create_system_manifest()
            self.create_component_status()
            self.create_triz_contradictions()
            self.create_market_axioms()
            self.create_structural_priors()
            self.create_additional_configs()
            self.create_template_files()

            # Проверка
            if self.run_verification():
                logger.info("✅ ИНИЦИАЛИЗАЦИЯ ЗАВЕРШЕНА УСПЕШНО!")
                return True
            else:
                logger.error("❌ Инициализация завершилась с ошибками")
                return False

        except Exception as e:
            logger.error(f"❌ Критическая ошибка инициализации: {e}")
            return False

if __name__ == "__main__":
    initializer = SystemInitializer()
    success = initializer.initialize()

    if success:
        print("\n" + "="*60)
        print("🎉 CIS V10.0-r1 СИСТЕМА ИНИЦИАЛИЗИРОВАНА!")
        print("="*60)
        print("📁 Структура создана в: C:\\КОДИНГ\\MARKET ANALYSIS\\MARKET_MIND")
        print("📊 30 компонентов зарегистрированы")
        print("⚙️  Все конфигурации готовы")
        print("📋 ЗАДАЧА 1 - ВЫПОЛНЕНА ✅")
        exit(0)
    else:
        print("❌ Инициализация не завершена")
        exit(1)