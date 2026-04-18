# TASK_02 — REBUILD ИНФРАСТРУКТУРЫ MARKET_MIND + ОБНОВЛЕНИЕ КОГНИТИВКИ

**Тип:** инфраструктура + cognitive update
**Приоритет:** критично — основа для всех последующих компонентов
**Исполнитель:** Claude Code
**Источник:** ТЗ V10.0-r1 § 1.2 (восьмислойная архитектура) + итоги TASK_01
**Статус:** ACTIVE
**Зависимости:** TASK_00 (cleanup) + TASK_01 (cognitive foundation) — завершены
**Блокирует:** TASK_03 (schema_layer v2)

---

## ⚠ Contract reminder

Соблюдай CLAUDE.md § 1-28. При любом сомнении — § 3 (СТОП + вопрос Сергею).

Перед началом задачи — **прочти когнитивные файлы** (§ 25, § 28):
- `LESSONS_LEARNED.md` — особенно L-01 (TASK vs ТЗ), L-03 (hardcoded пути), L-04 (ASCII в print), L-09 (предусловия с preload)
- `PATTERNS.md` — особенно P-01 (Path(__file__).resolve()), P-05 (структура теста)
- `ANTIPATTERNS.md` — особенно AP-01 (hardcoded), AP-06 (emoji), AP-07 (самовольный функционал), AP-08 (реальные секреты в доках)

В отчёте § 9 укажи какие применил.

---

## Контекст

После TASK_00 (cleanup) и TASK_01 (когнитивка) репо чистый и готов к содержательной работе. Первый содержательный шаг — **rebuild инфраструктуры MARKET_MIND** до 8 канонических слоёв согласно ТЗ V10.0-r1 § 1.2.

**Текущее состояние (проблемы):**
- `LAYER_H_INTERFACE/` — неправильное имя, должно быть `LAYER_H_INFRA/` (ТЗ стр. 208)
- Отсутствуют `LAYER_E_VALIDATION/`, `LAYER_F_FEEDBACK/`, `LAYER_G_NEWS/`
- В существующих слоях отсутствуют канонические подпапки из ТЗ
- `MARKET_MIND/ENGINE/initialize_system.py` либо отсутствует, либо не соответствует ТЗ (статус `needs_rebuild` в `component_status.json`)

**Цель задачи:**
После выполнения `MARKET_MIND/` должна **полностью** соответствовать структуре из ТЗ § 1.2. Компонент `initialize_system` впервые честно получит статус `ready`.

Дополнительно — обновить когнитивную систему уроками/антипаттернами из TASK_01 (L-09, L-10, L-11, L-13, AP-08).

---

## Рабочая директория

`C:\CODE\MARKET ANALYSIS\`

---

## Предусловия (проверить перед началом)

1. Текущая ветка — `main`, рабочая директория чистая **или** содержит только preload-файлы из этой задачи (L-09)
2. Last commits in main (проверить через `git log --oneline -5`):
   - `fd95096 archive TASK_01`
   - `1cb40d4 task 01: install cognitive foundation (...)`
3. Local main и origin/main синхронизированы: `git log main..origin/main` и `git log origin/main..main` оба пустые
4. `TASKS/ACTIVE/` содержит **только** `TASK_02_rebuild_infrastructure.md`
5. `TASKS/NOTES/` существует (создан в TASK_00)
6. Файлы `LESSONS_LEARNED.md` и `ANTIPATTERNS.md` preload-нуты Сергеем в корень проекта с обновлённым содержимым (v1.1)

Если любое условие не выполнено → § 3 (СТОП + вопрос Сергею).

---

## Часть 1 — Создать ветку

```bash
cd "C:\CODE\MARKET ANALYSIS"
git checkout main
git pull origin main
git status    # Ожидается: modified LESSONS_LEARNED.md и ANTIPATTERNS.md (preload v1.1)
git checkout -b task-02-rebuild-infrastructure
```

---

## БЛОК А — ОБНОВЛЕНИЕ КОГНИТИВНОЙ СИСТЕМЫ

Делаем первым — чтобы все последующие шаги в этом же TASK опирались уже на обновлённые файлы.

### Часть 2 — Закоммитить обновлённые когнитивные файлы

`LESSONS_LEARNED.md` и `ANTIPATTERNS.md` preload-нуты Сергеем с новым содержимым (v1.1). Проверить что они действительно содержат новые уроки:

```bash
findstr /C:"## L-09:" LESSONS_LEARNED.md
findstr /C:"## L-10:" LESSONS_LEARNED.md
findstr /C:"## L-11:" LESSONS_LEARNED.md
findstr /C:"## L-13:" LESSONS_LEARNED.md
findstr /C:"## AP-08:" ANTIPATTERNS.md
findstr /C:"v1.1" LESSONS_LEARNED.md
findstr /C:"v1.1" ANTIPATTERNS.md
```

Все 7 команд должны найти соответствующие маркеры. Если что-то не найдено — § 3 (преloadнутые файлы неполные).

**Закоммить обновления отдельным коммитом** (это независимое улучшение от rebuild):

```bash
git add LESSONS_LEARNED.md ANTIPATTERNS.md
git commit -m "task 02 block A: update cognitive system with lessons from TASK_01 (L-09, L-10, L-11, L-13, AP-08)"
```

Не пушить пока — push будет в самом конце после всего TASK_02.

---

## БЛОК Б — REBUILD ИНФРАСТРУКТУРЫ

### Часть 3 — Переименовать `LAYER_H_INTERFACE/` → `LAYER_H_INFRA/`

Согласно ТЗ V10.0-r1 стр. 208: `LAYER_H_INFRA\\ user_profile|backup|api`. Наше текущее имя `LAYER_H_INTERFACE` не соответствует канону.

Использовать `git mv` чтобы сохранить историю файлов:

```bash
git mv MARKET_MIND/LAYER_H_INTERFACE MARKET_MIND/LAYER_H_INFRA
```

Проверить:
```bash
dir MARKET_MIND\LAYER_H_INFRA
dir MARKET_MIND\LAYER_H_INTERFACE   # Должно: File Not Found
```

### Часть 4 — Создать канонические подпапки каждого слоя

Согласно ТЗ V10.0-r1 § 1.2 (стр. 192-209). Создать структуру точно по спецификации:

#### LAYER_A_RESEARCH/
```
MARKET_MIND/LAYER_A_RESEARCH/
├── patterns/
├── hypotheses/
├── experiments/
├── negatives/
├── models/
└── audit/
```

#### LAYER_B_DATA/
```
MARKET_MIND/LAYER_B_DATA/
├── features/
│   └── snapshots/
├── quality_logs/
├── onchain/
├── macro/
└── news/
```

#### LAYER_C_KNOWLEDGE/
```
MARKET_MIND/LAYER_C_KNOWLEDGE/
├── knowledge_base/
└── trust_system/
```

#### LAYER_D_MODEL/
```
MARKET_MIND/LAYER_D_MODEL/
├── model_versions/
├── predictions/
├── weights/
└── shock_log/
```

#### LAYER_E_VALIDATION/ (создать слой с нуля если отсутствует)
```
MARKET_MIND/LAYER_E_VALIDATION/
├── backtest_results/
└── validation_reports/
```

#### LAYER_F_FEEDBACK/ (создать слой с нуля если отсутствует)
```
MARKET_MIND/LAYER_F_FEEDBACK/
├── prediction_records/
├── outcomes/
├── drift_log/
├── recalibration_log/
└── integral_bias_log/
```

#### LAYER_G_NEWS/ (создать слой с нуля если отсутствует)
```
MARKET_MIND/LAYER_G_NEWS/
```
(В ТЗ подпапки не указаны явно — слой создаётся с .gitkeep, подпапки появятся при реализации Task 22 News Collector)

#### LAYER_H_INFRA/ (уже переименован в Части 3)
```
MARKET_MIND/LAYER_H_INFRA/
├── user_profile/
├── backup/
├── api/
└── logs/
```

**Важно:** `logs/` в LAYER_H_INFRA — это для production-логов модулей (§ 17 CLAUDE.md). В ТЗ явно не перечислен, но упоминается как destination для логов ENGINE.

### Часть 5 — Добавить `.gitkeep` в каждую пустую директорию

Git не отслеживает пустые папки. Чтобы структура сохранялась в репо, в каждую только что созданную папку добавить пустой файл `.gitkeep`.

Список директорий куда нужно добавить `.gitkeep` (всего **30 штук**):

```
MARKET_MIND/LAYER_A_RESEARCH/patterns/.gitkeep
MARKET_MIND/LAYER_A_RESEARCH/hypotheses/.gitkeep
MARKET_MIND/LAYER_A_RESEARCH/experiments/.gitkeep
MARKET_MIND/LAYER_A_RESEARCH/negatives/.gitkeep
MARKET_MIND/LAYER_A_RESEARCH/models/.gitkeep
MARKET_MIND/LAYER_A_RESEARCH/audit/.gitkeep

MARKET_MIND/LAYER_B_DATA/features/.gitkeep
MARKET_MIND/LAYER_B_DATA/features/snapshots/.gitkeep
MARKET_MIND/LAYER_B_DATA/quality_logs/.gitkeep
MARKET_MIND/LAYER_B_DATA/onchain/.gitkeep
MARKET_MIND/LAYER_B_DATA/macro/.gitkeep
MARKET_MIND/LAYER_B_DATA/news/.gitkeep

MARKET_MIND/LAYER_C_KNOWLEDGE/knowledge_base/.gitkeep
MARKET_MIND/LAYER_C_KNOWLEDGE/trust_system/.gitkeep

MARKET_MIND/LAYER_D_MODEL/model_versions/.gitkeep
MARKET_MIND/LAYER_D_MODEL/predictions/.gitkeep
MARKET_MIND/LAYER_D_MODEL/weights/.gitkeep
MARKET_MIND/LAYER_D_MODEL/shock_log/.gitkeep

MARKET_MIND/LAYER_E_VALIDATION/backtest_results/.gitkeep
MARKET_MIND/LAYER_E_VALIDATION/validation_reports/.gitkeep

MARKET_MIND/LAYER_F_FEEDBACK/prediction_records/.gitkeep
MARKET_MIND/LAYER_F_FEEDBACK/outcomes/.gitkeep
MARKET_MIND/LAYER_F_FEEDBACK/drift_log/.gitkeep
MARKET_MIND/LAYER_F_FEEDBACK/recalibration_log/.gitkeep
MARKET_MIND/LAYER_F_FEEDBACK/integral_bias_log/.gitkeep

MARKET_MIND/LAYER_G_NEWS/.gitkeep

MARKET_MIND/LAYER_H_INFRA/user_profile/.gitkeep
MARKET_MIND/LAYER_H_INFRA/backup/.gitkeep
MARKET_MIND/LAYER_H_INFRA/api/.gitkeep
MARKET_MIND/LAYER_H_INFRA/logs/.gitkeep
```

**Важно:** если какая-то подпапка уже существует и содержит реальные файлы (например, `LAYER_H_INFRA/logs/` может содержать предыдущие логи которые мы решили оставить) — `.gitkeep` в ней не нужен (в такой папке уже есть что-то для git). Команда создания `.gitkeep` должна быть идемпотентна (не падать если файл уже есть).

### Часть 6 — Создать правильный `initialize_system.py`

Это **ключевой компонент** Задачи 1 из ТЗ. Его назначение: идемпотентно создавать всю каноническую структуру `MARKET_MIND/` на основе констант (не hardcoded).

#### Расположение

`MARKET_MIND/ENGINE/initialize_system.py`

Если файл существует — **перезаписать** (статус был `needs_rebuild`).

#### Содержимое

Применяем:
- **P-01** (относительные пути через `Path(__file__).resolve()`)
- **P-03** (типизированные exception, логирование)
- **P-05** (ASCII маркеры если есть print)
- **L-03, L-06** (никаких hardcoded C:\)
- **§ 13** (UTF-8)
- **§ 16** (docstrings + type hints)

```python
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
```

#### Запустить для проверки

```bash
cd "C:\CODE\MARKET ANALYSIS"
python MARKET_MIND/ENGINE/initialize_system.py
```

Должен вывести:
```
[INIT] MARKET_MIND root: C:\CODE\MARKET ANALYSIS\MARKET_MIND
[INIT] Directories created: <N>
[INIT] Directories existed: <M>
[INIT] Total expected: 36
[PASS] Structure canonical per TZ V10.0-r1 § 1.2
```

Точное число created/existed зависит от того что было до запуска. Важно: `errors=0`, `Total expected=36`.

### Часть 7 — `verify_infrastructure.py`

Отдельный скрипт проверки соответствия структуры ТЗ. Расположение: `scripts/verify_infrastructure.py`.

Применяем P-01, P-05, L-04.

```python
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
```

#### Запустить

```bash
python scripts/verify_infrastructure.py
```

Должен вывести `[PASS]`. Если `[FAIL]` — **не коммитить**, разбираться по списку ошибок или § 3.

### Часть 8 — Обновить `component_status.json`

Компонент `initialize_system` впервые получает честный статус `ready`.

Открыть `MARKET_MIND/CONFIG/component_status.json`, найти секцию `initialize_system`, изменить:

```json
"initialize_system": {
    "status": "ready",
    "updated_at": "2026-04-18",
    "notes": "Task 02: пересобран с нуля. Идемпотентно создаёт все 36 канонических директорий согласно TZ V10.0-r1 § 1.2. Использует Path(__file__).resolve() (P-01, L-03). verify_infrastructure.py [PASS]."
}
```

**Остальные компоненты не трогать.**

Остальные компоненты MDC (schema_layer, data_quality_gates, context_orchestrator) остаются в статусах `needs_rewrite` / `not_started` до следующих задач:
- TASK_03 → schema_layer v2
- TASK_04 → data_quality_gates v2
- TASK_05 → context_orchestrator v2

---

## Часть 9 — Финальный коммит, merge, push

### 9.1. Проверить git status

```bash
git status
```

Ожидаемые изменения в ветке `task-02-rebuild-infrastructure`:
- **Блок А** (закоммичен в Части 2): LESSONS_LEARNED.md, ANTIPATTERNS.md
- **Блок Б** (ещё не закоммичен):
  - Renamed: MARKET_MIND/LAYER_H_INTERFACE → MARKET_MIND/LAYER_H_INFRA (+ подпапки)
  - Added: ~30 `.gitkeep` файлов в новых/пустых директориях
  - Modified or Added: MARKET_MIND/ENGINE/initialize_system.py
  - Added: scripts/verify_infrastructure.py
  - Modified: MARKET_MIND/CONFIG/component_status.json

Если есть **другие** изменения не из этого списка — § 3.

### 9.2. Pre-commit checklist (§ 24)

Пройди весь чеклист. Особенно:
- [ ] В коде нет hardcoded `C:\КОДИНГ\`, `C:\CODE\`, `/home/`, `/Users/` (AP-01, L-03)
- [ ] В коде нет реальных секретов (AP-05, AP-08)
- [ ] `initialize_system.py` использует `Path(__file__).resolve()` (P-01)
- [ ] `verify_infrastructure.py` использует ASCII маркеры `[OK]`/`[FAIL]`/`[PASS]` (L-04, AP-06)
- [ ] Все `.py` файлы UTF-8 без BOM
- [ ] Нет самовольно добавленных файлов (AP-07)

### 9.3. Коммит Блок Б

```bash
git add MARKET_MIND/ scripts/verify_infrastructure.py
git commit -m "task 02 block B: rebuild MARKET_MIND to 8 canonical layers per TZ V10.0-r1 § 1.2"
```

### 9.4. Merge и push

```bash
git checkout main
git merge task-02-rebuild-infrastructure
git push origin main
git branch -d task-02-rebuild-infrastructure
```

Проверить что push прошёл успешно:
```bash
git fetch origin
git log --oneline origin/main..main     # Должен быть пустой вывод
git log --oneline main..origin/main     # Должен быть пустой вывод
```

Если есть diff — § 3.

### 9.5. Архивировать TASK

```bash
git mv TASKS/ACTIVE/TASK_02_rebuild_infrastructure.md TASKS/COMPLETED/TASK_02_rebuild_infrastructure.md
git commit -m "archive TASK_02"
git push origin main
```

---

## Часть 10 — Финальный отчёт Сергею

Пришли в чат отчёт по § 9 CLAUDE.md:

```
TASK_02 [rebuild_infrastructure + cognitive_update] — COMPLETED

БЛОК A — когнитивная система:
  Файлы изменены: LESSONS_LEARNED.md (v1.0 → v1.1), ANTIPATTERNS.md (v1.0 → v1.1)
  Добавлены: L-09, L-10, L-11, L-13 (урок L-12 reserved), AP-08
  Commit (A): <hash> task 02 block A: update cognitive system with lessons from TASK_01

БЛОК Б — инфраструктура:
  Файлы перемещены: LAYER_H_INTERFACE → LAYER_H_INFRA (с подпапками)
  Файлы созданы:
    - ~30 .gitkeep в канонических подпапках
    - MARKET_MIND/ENGINE/initialize_system.py (пересоздан)
    - scripts/verify_infrastructure.py (новый)
  Файлы изменены: MARKET_MIND/CONFIG/component_status.json (initialize_system → ready)
  
  Тесты:
    python MARKET_MIND/ENGINE/initialize_system.py — [PASS]
    python scripts/verify_infrastructure.py — [PASS]
  
  Commit (Б): <hash> task 02 block B: rebuild MARKET_MIND to 8 canonical layers
  Archive commit: <hash> archive TASK_02

Время работы: <минуты>
Push в origin/main подтверждён (git log main..origin/main пустой).

Lessons applied:
  - L-01 (сверил структуру с ТЗ § 1.2 построчно)
  - L-03 / AP-01 (в initialize_system только Path(__file__).resolve())
  - L-04 / AP-06 (ASCII маркеры + UTF-8 reconfigure в verify-скрипте)
  - L-09 (проверил предусловия с учётом preload-файлов L/AP от Сергея)

Patterns applied:
  - P-01 (Path(__file__).resolve().parent.parent в initialize_system и verify)
  - P-03 (except OSError с логированием)
  - P-05 (структура verify_infrastructure.py)

Antipatterns avoided:
  - AP-01 (grep показал 0 hardcoded путей в новом коде)
  - AP-06 (0 emoji в print тестов)
  - AP-07 (только файлы из TASK: initialize_system.py, verify_infrastructure.py, .gitkeep, component_status обновление — ничего лишнего)
  - AP-08 (в документации нет реальных секретов)

Component status updates:
  - initialize_system: needs_rebuild → ready (впервые честно по L-02)

Ideas logged: <N>
Warnings/issues: none (или описать)

Готов к TASK_03 (schema_layer v2).
```

---

## Критерии готовности (acceptance criteria)

- [ ] `LAYER_H_INFRA/` существует, `LAYER_H_INTERFACE/` отсутствует
- [ ] Все 3 новых слоя (E, F, G) созданы
- [ ] Все 36 канонических директорий существуют (см. CANONICAL_DIRS в verify)
- [ ] В каждой пустой директории есть `.gitkeep`
- [ ] `MARKET_MIND/ENGINE/initialize_system.py` использует `Path(__file__).resolve()`, не содержит hardcoded путей
- [ ] `MARKET_MIND/ENGINE/initialize_system.py` запускается и выводит `[PASS]`
- [ ] `scripts/verify_infrastructure.py` существует, запускается, выводит `[PASS]`
- [ ] `component_status.json`: `initialize_system: ready` с датой 2026-04-18
- [ ] `LESSONS_LEARNED.md` версия v1.1 с L-09, L-10, L-11, L-13
- [ ] `ANTIPATTERNS.md` версия v1.1 с AP-08
- [ ] Два коммита в main: Блок А + Блок Б, плюс archive TASK_02
- [ ] `git log main..origin/main` и `git log origin/main..main` — оба пустые (синхронизация)
- [ ] TASK файл перемещён в `TASKS/COMPLETED/`
- [ ] Отчёт Сергею по § 9

---

## Важные предупреждения

- ⚠ **Не изменяй** содержимое preload-нутых `LESSONS_LEARNED.md` и `ANTIPATTERNS.md` — они от архитектора, только закоммить как есть в Части 2
- ⚠ **Не трогай** `TZ/` — канон
- ⚠ **Не трогай** другие компоненты в `component_status.json` кроме `initialize_system` — их обновят последующие задачи
- ⚠ **Не перезаписывай** `MARKET_MIND/ENGINE/schema_validator.py` и `data_quality_gates.py` — они `needs_rewrite`, будут переписаны в TASK_03 и TASK_04 соответственно
- ⚠ **Не добавляй** в `initialize_system.py` никакой логики кроме создания директорий (AP-07). Никаких "helpful utilities", config-загрузок, db-setup — только директории
- ⚠ **Не удаляй** существующее содержимое в `MARKET_MIND/CONFIG/`, `MARKET_MIND/SCHEMAS/`, `MARKET_MIND/meta/` — оно остаётся как есть
- ⚠ Если при создании директорий встретил существующий файл с именем папки (например, `patterns` — файл, а не директория) — § 3 (СТОП, странная ситуация)
- ⚠ При любом `[FAIL]` в тестах — **не коммить**, иди по § 3

---

**После успешного выполнения — ждём TASK_03 (schema_layer v2: 6 канонических схем + dsl_grammar.md).**
