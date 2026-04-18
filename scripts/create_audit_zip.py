#!/usr/bin/env python3
"""
CIS V10.0-r1 Audit Archive Creator
Создает zip-архив проекта для передачи архитектору (Claude Opus)
"""

import os
import zipfile
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parent.parent.resolve()
ZIP_NAME = f"cis_audit_{datetime.now().strftime('%Y-%m-%d')}.zip"
OUT_PATH = ROOT / ZIP_NAME

EXCLUDE_DIRS = {
    'node_modules', '__pycache__', '.git', '.pytest_cache',
    'venv', '.venv', 'env', '.idea', '.vscode',
    'src', 'data', 'exports', 'HISTORY',  # legacy — safety
}
EXCLUDE_EXT = {'.pyc', '.pyo', '.ipynb', '.DS_Store'}
EXCLUDE_FILES = {'Thumbs.db', '.DS_Store', ZIP_NAME, '.env'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB
MAX_LOG_SIZE = 10 * 1024          # 10 KB для .log

def should_include(path: Path) -> tuple[bool, str]:
    # Исключить любой env-файл независимо от расширения и расположения
    if path.name == '.env' or path.name.startswith('.env.'):
        return False, "env_file"
    # Исключить по директории
    for part in path.parts:
        if part in EXCLUDE_DIRS:
            return False, f"dir:{part}"
    # Исключить по имени файла
    if path.name in EXCLUDE_FILES:
        return False, "filename"
    # Исключить по расширению
    if path.suffix in EXCLUDE_EXT:
        return False, f"ext:{path.suffix}"
    # Размер
    try:
        size = path.stat().st_size
    except OSError:
        return False, "stat_error"
    # Логи — только мелкие
    if path.suffix == '.log' and size > MAX_LOG_SIZE:
        return False, f"log_too_big:{size}"
    # Общий лимит размера
    if size > MAX_FILE_SIZE:
        return False, f"too_big:{size}"
    return True, ""

included = 0
skipped = []
total_size = 0

print(f"Creating {OUT_PATH}")
print(f"Root: {ROOT}")

with zipfile.ZipFile(OUT_PATH, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
    for path in ROOT.rglob('*'):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT)
        ok, reason = should_include(rel)
        if not ok:
            skipped.append((str(rel), reason))
            continue
        zf.write(path, rel)
        included += 1
        total_size += path.stat().st_size

print(f"\nDone.")
print(f"Included: {included} files")
print(f"Original size: {total_size / 1024:.1f} KB")
print(f"Zip size: {OUT_PATH.stat().st_size / 1024:.1f} KB")
print(f"Skipped: {len(skipped)} items")

# Топ-20 исключённых — чтобы убедиться что не выкинули лишнего
print("\nFirst 20 skipped:")
for name, reason in skipped[:20]:
    print(f"  - {name} [{reason}]")

# Проверка ключевых файлов — должны быть в архиве
critical = [
    "MARKET_MIND/CONFIG/component_status.json",
    "MARKET_MIND/ENGINE/context_orchestrator.py",
    "MARKET_MIND/ENGINE/schema_validator.py",
    "MARKET_MIND/ENGINE/data_quality_gates.py",
    "CLAUDE.md",
    "README.md",
]
with zipfile.ZipFile(OUT_PATH, 'r') as zf:
    names = set(zf.namelist())
    # normalize Windows/Unix слэши
    names = {n.replace('\\', '/') for n in names}
    print("\nCritical files check:")
    for f in critical:
        status = "OK" if f in names else "MISSING"
        print(f"  [{status}] {f}")

print(f"\nAbsolute path: {OUT_PATH.absolute()}")
print(f"Ready for transfer to Claude Opus architect!")