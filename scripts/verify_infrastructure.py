#!/usr/bin/env python3
"""Верификация канонической структуры MARKET_MIND — TASK_02 Часть 7."""
import sys
from pathlib import Path

# L-04 / P-05: UTF-8 reconfigure для Windows cp1251
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

# P-01: относительный путь
ROOT = Path(__file__).resolve().parent.parent
MARKET_MIND = ROOT / "MARKET_MIND"

# Каноническая структура из ТЗ V10.0-r1 § 1.2
# ВАЖНО: должно совпадать с initialize_system.CANONICAL_STRUCTURE
CANONICAL_DIRS = [
    "SCHEMAS",
    "CONFIG",
    "ENGINE",
    "meta",

    "LAYER_A_RESEARCH",
    "LAYER_A_RESEARCH/patterns",
    "LAYER_A_RESEARCH/hypotheses",
    "LAYER_A_RESEARCH/experiments",
    "LAYER_A_RESEARCH/negatives",
    "LAYER_A_RESEARCH/models",
    "LAYER_A_RESEARCH/audit",

    "LAYER_B_DATA",
    "LAYER_B_DATA/features",
    "LAYER_B_DATA/features/snapshots",
    "LAYER_B_DATA/quality_logs",
    "LAYER_B_DATA/onchain",
    "LAYER_B_DATA/macro",
    "LAYER_B_DATA/news",

    "LAYER_C_KNOWLEDGE",
    "LAYER_C_KNOWLEDGE/knowledge_base",
    "LAYER_C_KNOWLEDGE/trust_system",

    "LAYER_D_MODEL",
    "LAYER_D_MODEL/model_versions",
    "LAYER_D_MODEL/predictions",
    "LAYER_D_MODEL/weights",
    "LAYER_D_MODEL/shock_log",

    "LAYER_E_VALIDATION",
    "LAYER_E_VALIDATION/backtest_results",
    "LAYER_E_VALIDATION/validation_reports",

    "LAYER_F_FEEDBACK",
    "LAYER_F_FEEDBACK/prediction_records",
    "LAYER_F_FEEDBACK/outcomes",
    "LAYER_F_FEEDBACK/drift_log",
    "LAYER_F_FEEDBACK/recalibration_log",
    "LAYER_F_FEEDBACK/integral_bias_log",

    "LAYER_G_NEWS",

    "LAYER_H_INFRA",
    "LAYER_H_INFRA/user_profile",
    "LAYER_H_INFRA/backup",
    "LAYER_H_INFRA/api",
    "LAYER_H_INFRA/logs",
]

FORBIDDEN_DIRS = [
    "LAYER_H_INTERFACE",  # старое имя, должно быть переименовано в LAYER_H_INFRA
]

errors: list[str] = []

# 1. MARKET_MIND существует
if not MARKET_MIND.is_dir():
    errors.append(f"Missing MARKET_MIND directory at {MARKET_MIND}")
    print("[FAIL]")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)

# 2. Все канонические директории существуют
for rel in CANONICAL_DIRS:
    p = MARKET_MIND / rel
    if not p.is_dir():
        errors.append(f"MUST EXIST: MARKET_MIND/{rel}")

# 3. Ни одной запрещённой директории нет
for rel in FORBIDDEN_DIRS:
    p = MARKET_MIND / rel
    if p.exists():
        errors.append(f"MUST NOT EXIST: MARKET_MIND/{rel} (legacy name)")

# 4. initialize_system.py существует и содержит каноническую структуру
init_path = MARKET_MIND / "ENGINE" / "initialize_system.py"
if not init_path.is_file():
    errors.append("Missing MARKET_MIND/ENGINE/initialize_system.py")
else:
    content = init_path.read_text(encoding="utf-8")
    required_markers = [
        "CANONICAL_STRUCTURE",
        "LAYER_A_RESEARCH/patterns",
        "LAYER_B_DATA/features/snapshots",
        "LAYER_F_FEEDBACK/integral_bias_log",
        "LAYER_H_INFRA/user_profile",
        "def initialize_structure",
        "Path(__file__).resolve()",  # P-01 / L-03 compliance
    ]
    for m in required_markers:
        if m not in content:
            errors.append(f"initialize_system.py missing marker: {m!r}")
    # Anti-check: no hardcoded C:\ paths (AP-01)
    for bad in (r"C:\\CODE", r"C:\\КОДИНГ", "/home/", "/Users/"):
        if bad in content:
            errors.append(f"initialize_system.py contains hardcoded path: {bad!r} (AP-01)")

# Финальный результат
if errors:
    print("[FAIL]")
    print(f"{len(errors)} errors:")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)
else:
    print("[PASS] - Infrastructure canonical per TZ V10.0-r1 § 1.2")
    print(f"  - {len(CANONICAL_DIRS)} canonical directories present")
    print(f"  - No legacy directory names (LAYER_H_INTERFACE absent)")
    print(f"  - initialize_system.py compliant (P-01, no hardcoded paths)")
    sys.exit(0)