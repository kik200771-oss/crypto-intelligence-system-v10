# ЗАДАЧА 1 — ВЕРИФИКАЦИЯ ИНИЦИАЛИЗАЦИИ [Этап 1]

## Статус
`initialize_system` ✅ — по данным разработчика инициализация выполнена.

Эта задача — **проверка** что всё создано корректно и соответствует спецификации V10.0-r1.

**Рабочая директория:** `C:\КОДИНГ\MARKET ANALYSIS\MARKET_MIND\`

---

## Запусти проверочный скрипт

```python
import json, os, sys
from pathlib import Path
from datetime import datetime

BASE = Path(r"C:\КОДИНГ\MARKET ANALYSIS\MARKET_MIND")
errors = []
warnings = []

def check(condition, message, is_warning=False):
    if not condition:
        if is_warning:
            warnings.append(f"⚠️  {message}")
        else:
            errors.append(f"❌ {message}")
    else:
        print(f"✅ {message}")

# ── 1. Структура директорий ────────────────────────────────────────
layers = [
    "ENGINE", "SCHEMAS", "CONFIG", "meta",
    "LAYER_A_RESEARCH", "LAYER_A_RESEARCH/patterns", "LAYER_A_RESEARCH/hypotheses",
    "LAYER_A_RESEARCH/experiments", "LAYER_A_RESEARCH/negatives",
    "LAYER_A_RESEARCH/models", "LAYER_A_RESEARCH/audit",
    "LAYER_B_DATA", "LAYER_B_DATA/features", "LAYER_B_DATA/features/snapshots",
    "LAYER_B_DATA/quality_logs", "LAYER_B_DATA/onchain", "LAYER_B_DATA/macro",
    "LAYER_B_DATA/news",
    "LAYER_C_KNOWLEDGE", "LAYER_C_KNOWLEDGE/knowledge_base",
    "LAYER_C_KNOWLEDGE/trust_system",
    "LAYER_D_MODEL", "LAYER_D_MODEL/model_versions", "LAYER_D_MODEL/predictions",
    "LAYER_D_MODEL/weights", "LAYER_D_MODEL/shock_log",
    "LAYER_E_VALIDATION", "LAYER_E_VALIDATION/backtest_results",
    "LAYER_E_VALIDATION/validation_reports",
    "LAYER_F_FEEDBACK", "LAYER_F_FEEDBACK/prediction_records",
    "LAYER_F_FEEDBACK/outcomes", "LAYER_F_FEEDBACK/drift_log",
    "LAYER_F_FEEDBACK/recalibration_log", "LAYER_F_FEEDBACK/integral_bias_log",
    "LAYER_G_NEWS", "LAYER_G_NEWS/raw", "LAYER_G_NEWS/scored",
    "LAYER_H_INTERFACE", "LAYER_H_INTERFACE/logs", "LAYER_H_INTERFACE/exports",
]
for layer in layers:
    check((BASE / layer).exists(), f"Directory exists: {layer}")

# ── 2. system_manifest.json ────────────────────────────────────────
try:
    with open(BASE / "CONFIG/system_manifest.json") as f:
        m = json.load(f)
    check(m.get("version") == "10.0", "manifest version = 10.0")
    check(m.get("revision") == "r1", "manifest revision = r1")
    check("model_approximations" in m, "manifest has model_approximations")
    check(len(m.get("model_approximations", {})) == 2, "manifest has exactly 2 approximations")
    check(m.get("btc_as_macro_indicator") == True, "btc_as_macro_indicator = True")
    check(m.get("required_modules") == 30, "required_modules = 30")
    check("canon" in m, "manifest has canon reference")
except Exception as e:
    errors.append(f"❌ system_manifest.json: {e}")

# ── 3. component_status.json ───────────────────────────────────────
try:
    with open(BASE / "CONFIG/component_status.json") as f:
        cs = json.load(f)
    check(len(cs) == 30, f"component_status has 30 components (got {len(cs)})")
    check(cs.get("initialize_system", {}).get("status") == "ready",
          "initialize_system status = ready")
    not_started = [k for k, v in cs.items() if v.get("status") == "not_started"]
    check(len(not_started) == 29, f"29 components in not_started (got {len(not_started)})")
except Exception as e:
    errors.append(f"❌ component_status.json: {e}")

# ── 4. triz_contradictions.json ────────────────────────────────────
try:
    with open(BASE / "CONFIG/triz_contradictions.json") as f:
        triz = json.load(f)
    check(len(triz) == 20, f"triz has 20 entries (got {len(triz)})")
    ids = [t.get("id") for t in triz] if isinstance(triz, list) else list(triz.keys())
    check("TRZ-001" in str(ids), "TRZ-001 present")
    check("TRZ-020" in str(ids), "TRZ-020 present")
except Exception as e:
    errors.append(f"❌ triz_contradictions.json: {e}")

# ── 5. market_axioms.json ─────────────────────────────────────────
try:
    with open(BASE / "CONFIG/market_axioms.json") as f:
        axm = json.load(f)
    count = len(axm) if isinstance(axm, list) else len(axm)
    check(count == 9, f"market_axioms has 9 entries (got {count})")
except Exception as e:
    errors.append(f"❌ market_axioms.json: {e}")

# ── 6. structural_priors.json ─────────────────────────────────────
try:
    with open(BASE / "CONFIG/structural_priors.json") as f:
        pri = json.load(f)
    count = len(pri) if isinstance(pri, list) else len(pri)
    check(count == 19, f"structural_priors has 19 entries (got {count})")
except Exception as e:
    errors.append(f"❌ structural_priors.json: {e}")

# ── 7. Дополнительные конфиги ─────────────────────────────────────
for config_file in ["timeframe_core.json", "stale_data_policy.json"]:
    check((BASE / "CONFIG" / config_file).exists(), f"CONFIG/{config_file} exists")

# ── 8. Trust registry ─────────────────────────────────────────────
trust_path = BASE / "LAYER_C_KNOWLEDGE/trust_system/trust_registry.json"
check(trust_path.exists(), "trust_registry.json exists")
if trust_path.exists():
    with open(trust_path) as f:
        tr = json.load(f)
    check("Binance" in str(tr), "Binance in trust_registry")

# ── 9. how_to_read_me.md ──────────────────────────────────────────
readme_path = BASE / "LAYER_A_RESEARCH/meta/how_to_read_me.md"
check(readme_path.exists(), "how_to_read_me.md exists", is_warning=True)

# ── ИТОГ ──────────────────────────────────────────────────────────
print("\n" + "="*50)
if errors:
    print(f"\n❌ НАЙДЕНО ПРОБЛЕМ: {len(errors)}")
    for e in errors:
        print(f"  {e}")
else:
    print("✅ ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ")

if warnings:
    print(f"\n⚠️  ПРЕДУПРЕЖДЕНИЯ: {len(warnings)}")
    for w in warnings:
        print(f"  {w}")

if errors:
    print("\n⚡ Что исправить: запусти ENGINE/initialize_system.py повторно")
    sys.exit(1)
else:
    print("\n🚀 Задача 1 верифицирована. Можно переходить к Задаче 2.")
```

---

## Если найдены проблемы

Запусти `ENGINE/initialize_system.py` — скрипт idempotent, не затрёт существующие данные, только создаст недостающее.

Если `component_status.json` содержит не 30 компонентов или не те имена — обнови его вручную добавив недостающие в статусе `"not_started"`.

Полный список 30 компонентов:
`initialize_system, schema_layer, data_quality_gates, context_orchestrator,
streamlit_ui_basic, hypothesis_formalizer, experiment_registry,
pattern_registry, backtester, validation_engine, insight_saver,
knowledge_ingester, knowledge_search, feature_store, regime_detector,
news_engine, trust_manager, macro_onchain, negative_knowledge_manager,
pattern_decay_monitor, evidence_grading_engine, model_core,
decision_audit, pattern_dsl_compiler, feedback_system,
prediction_tracker, rest_api, backup_reports, prior_manager,
determinism_contract`
