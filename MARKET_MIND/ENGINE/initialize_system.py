"""
initialize_system — идемпотентная инициализация структуры MARKET_MIND.

Создаёт все 8 канонических слоёв с подпапками согласно ТЗ V10.0-r1 § 1.2.
Безопасна для повторных запусков: существующие директории не удаляются,
существующие файлы не перезаписываются.

Задача 1 из ТЗ V10.0-r1. Компонент: initialize_system.
"""
from __future__ import annotations

import logging
import sys
from pathlib import Path

# Защита от Windows cp1251 при запуске как скрипт (L-04, AP-06)
if __name__ == "__main__":
    if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8")

logger = logging.getLogger(__name__)

# Каноническая структура MARKET_MIND согласно ТЗ V10.0-r1 § 1.2
# Ключ — путь относительно MARKET_MIND/, значение — описание для логов
CANONICAL_STRUCTURE: dict[str, str] = {
    # Core infrastructure
    "SCHEMAS": "JSON schemas (6 canonical + dsl_grammar)",
    "CONFIG": "System configs (manifest, component_status, axioms, etc)",
    "ENGINE": "Python modules for all components",
    "meta": "How-to-read index for humans and agents",

    # Layer A — Research Core
    "LAYER_A_RESEARCH": "Research Core layer root",
    "LAYER_A_RESEARCH/patterns": "Pattern records with 6 statuses",
    "LAYER_A_RESEARCH/hypotheses": "Pre-registered hypotheses",
    "LAYER_A_RESEARCH/experiments": "Experiment records",
    "LAYER_A_RESEARCH/negatives": "Negative knowledge (debunked)",
    "LAYER_A_RESEARCH/models": "Research models (per-pattern)",
    "LAYER_A_RESEARCH/audit": "Audit trails for research decisions",

    # Layer B — Data & Features
    "LAYER_B_DATA": "Data and features layer root",
    "LAYER_B_DATA/features": "Feature store current state",
    "LAYER_B_DATA/features/snapshots": "Feature snapshots (for reproducibility)",
    "LAYER_B_DATA/quality_logs": "Quality Gates audit logs",
    "LAYER_B_DATA/onchain": "On-chain metrics",
    "LAYER_B_DATA/macro": "Macro indicators (DXY, VIX, etc)",
    "LAYER_B_DATA/news": "News data inputs (feeds to Layer G)",

    # Layer C — Knowledge & Context
    "LAYER_C_KNOWLEDGE": "Knowledge & Context layer root",
    "LAYER_C_KNOWLEDGE/knowledge_base": "KB (classics, references)",
    "LAYER_C_KNOWLEDGE/trust_system": "Trust profiles and scores",

    # Layer D — Signal & Model Core
    "LAYER_D_MODEL": "Signal & Model Core layer root",
    "LAYER_D_MODEL/model_versions": "Versioned model artifacts",
    "LAYER_D_MODEL/predictions": "Generated predictions",
    "LAYER_D_MODEL/weights": "Model weights / parameters",
    "LAYER_D_MODEL/shock_log": "Shock Score events log",

    # Layer E — Validation
    "LAYER_E_VALIDATION": "Validation layer root",
    "LAYER_E_VALIDATION/backtest_results": "Backtest outputs",
    "LAYER_E_VALIDATION/validation_reports": "Evidence grading reports",

    # Layer F — Feedback & Control
    "LAYER_F_FEEDBACK": "Feedback & Control layer root",
    "LAYER_F_FEEDBACK/prediction_records": "Tx_Forecast records",
    "LAYER_F_FEEDBACK/outcomes": "Tx_Feedback outcomes",
    "LAYER_F_FEEDBACK/drift_log": "Drift detection events",
    "LAYER_F_FEEDBACK/recalibration_log": "Recalibration events",
    "LAYER_F_FEEDBACK/integral_bias_log": "PI-lite I-term state history",

    # Layer G — News & Trust
    "LAYER_G_NEWS": "News & Trust layer root",

    # Layer H — Interface & Ops (canonical name per TZ)
    "LAYER_H_INFRA": "Interface & Ops layer root",
    "LAYER_H_INFRA/user_profile": "User profile data",
    "LAYER_H_INFRA/backup": "System backups",
    "LAYER_H_INFRA/api": "API endpoints configuration",
    "LAYER_H_INFRA/logs": "Production module logs",
}


def get_market_mind_root() -> Path:
    """
    Возвращает путь до корня MARKET_MIND относительно этого файла.

    ENGINE/initialize_system.py → MARKET_MIND/

    Применяем P-01 (no hardcoded paths, L-03).
    """
    return Path(__file__).resolve().parent.parent


def ensure_directory(path: Path) -> tuple[bool, str]:
    """
    Идемпотентно создаёт директорию (включая родительские).

    Args:
        path: абсолютный путь директории

    Returns:
        (created, status): created=True если создали сейчас, False если уже была.
        status — человекочитаемое описание ('created' / 'exists' / 'error: ...').
    """
    try:
        if path.exists():
            if path.is_dir():
                return False, "exists"
            return False, f"error: path exists but is not a directory: {path}"
        path.mkdir(parents=True, exist_ok=True)
        return True, "created"
    except OSError as e:
        # P-03 — конкретный except + логирование
        logger.error(f"Cannot create directory {path}: {e}")
        return False, f"error: {e}"


def ensure_gitkeep(directory: Path) -> bool:
    """
    Создаёт .gitkeep в директории если она пустая.

    Если директория уже содержит файлы — .gitkeep не нужен.

    Args:
        directory: существующая директория

    Returns:
        True если .gitkeep создан или уже существовал, False при ошибке.
    """
    if not directory.is_dir():
        return False

    # Проверяем есть ли что-то в директории кроме .gitkeep
    try:
        contents = list(directory.iterdir())
    except OSError as e:
        logger.error(f"Cannot list directory {directory}: {e}")
        return False

    # Есть ли реальное содержимое (не считая самого .gitkeep)
    has_content = any(p.name != ".gitkeep" for p in contents)

    if has_content:
        return True  # .gitkeep не нужен — в папке уже что-то есть

    gitkeep = directory / ".gitkeep"
    if gitkeep.exists():
        return True  # уже был

    try:
        gitkeep.touch()
        return True
    except OSError as e:
        logger.error(f"Cannot create .gitkeep in {directory}: {e}")
        return False


def initialize_structure(root: Path | None = None) -> dict[str, str]:
    """
    Создаёт всю каноническую структуру MARKET_MIND/ по ТЗ V10.0-r1 § 1.2.

    Идемпотентная: безопасно вызывать повторно.

    Args:
        root: корень MARKET_MIND. По умолчанию — через get_market_mind_root().
              Параметр для тестов и нестандартных развёртываний.

    Returns:
        dict: {relative_path: status} для всех 36 директорий канонической структуры.
    """
    if root is None:
        root = get_market_mind_root()

    results: dict[str, str] = {}

    for rel_path, description in CANONICAL_STRUCTURE.items():
        full_path = root / rel_path
        _, status = ensure_directory(full_path)
        if status == "created":
            logger.info(f"Created: {rel_path} — {description}")
        results[rel_path] = status

        # В созданную директорию кладём .gitkeep если она пустая
        if full_path.is_dir():
            ensure_gitkeep(full_path)

    return results


def main() -> int:
    """
    CLI-точка входа. Запускает initialize_structure() и печатает результат.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    root = get_market_mind_root()
    print(f"[INIT] MARKET_MIND root: {root}")

    results = initialize_structure(root)

    created = sum(1 for s in results.values() if s == "created")
    existed = sum(1 for s in results.values() if s == "exists")
    errors = [p for p, s in results.items() if s.startswith("error")]

    print(f"[INIT] Directories created: {created}")
    print(f"[INIT] Directories existed: {existed}")
    print(f"[INIT] Total expected: {len(CANONICAL_STRUCTURE)}")

    if errors:
        print(f"[FAIL] {len(errors)} errors:")
        for e in errors:
            print(f"  - {e}: {results[e]}")
        return 1

    print("[PASS] Structure canonical per TZ V10.0-r1 § 1.2")
    return 0


if __name__ == "__main__":
    sys.exit(main())