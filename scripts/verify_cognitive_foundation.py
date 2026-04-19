#!/usr/bin/env python3
"""Верификация установки когнитивной системы — TASK_01."""
import sys
from pathlib import Path

# L-04 / P-05: UTF-8 reconfigure для Windows cp1251
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

# P-01: относительный путь
ROOT = Path(__file__).resolve().parent.parent

errors: list[str] = []

# 1. Четыре файла существуют
required_files = [
    "CLAUDE.md",
    "LESSONS_LEARNED.md",
    "PATTERNS.md",
    "ANTIPATTERNS.md",
]
for f in required_files:
    path = ROOT / f
    if not path.exists():
        errors.append(f"Missing file: {f}")
    elif path.stat().st_size == 0:
        errors.append(f"Empty file: {f}")

# 2. CLAUDE.md содержит маркеры v3
claude = ROOT / "CLAUDE.md"
if claude.exists():
    content = claude.read_text(encoding="utf-8")
    markers = [
        # v3 markers (already present):
        "§ 28. Как работают когнитивные файлы",
        "СТРУКТУРА КОМАНДЫ И РОЛИ",
        "LESSONS_LEARNED.md",
        "PATTERNS.md",
        "ANTIPATTERNS.md",
        "Lessons applied:",
        # v4 markers (new from TASK_02.5):
        "§ 29. Стандарт комментирования кода",
        "§ 30. Источники правды для новой сессии",
        "Запрет force push в main",
        "pre_commit_check.py",
    ]
    for m in markers:
        if m not in content:
            errors.append(f"CLAUDE.md missing marker: {m!r}")

# 3. LESSONS_LEARNED содержит 8 уроков
lessons = ROOT / "LESSONS_LEARNED.md"
if lessons.exists():
    content = lessons.read_text(encoding="utf-8")
    for i in range(1, 9):
        marker = f"## L-0{i}:"
        if marker not in content:
            errors.append(f"LESSONS_LEARNED.md missing lesson {marker}")

# 4. PATTERNS содержит 5 паттернов
patterns = ROOT / "PATTERNS.md"
if patterns.exists():
    content = patterns.read_text(encoding="utf-8")
    for i in range(1, 6):
        marker = f"## P-0{i}:"
        if marker not in content:
            errors.append(f"PATTERNS.md missing pattern {marker}")

# 5. ANTIPATTERNS содержит 7 антипаттернов
antipatterns = ROOT / "ANTIPATTERNS.md"
if antipatterns.exists():
    content = antipatterns.read_text(encoding="utf-8")
    for i in range(1, 8):
        marker = f"## AP-0{i}:"
        if marker not in content:
            errors.append(f"ANTIPATTERNS.md missing antipattern {marker}")

# 6. Все четыре файла UTF-8 без BOM
for f in required_files:
    path = ROOT / f
    if path.exists():
        raw = path.read_bytes()
        if raw.startswith(b"\xef\xbb\xbf"):
            errors.append(f"{f} has UTF-8 BOM (should not)")

# v4: проверка наличия новых скриптов
v4_scripts = [
    "scripts/pre_commit_check.py",
    "scripts/install_git_hooks.py",
]
for s in v4_scripts:
    path = ROOT / s
    if not path.is_file():
        errors.append(f"Missing v4 script: {s}")

# v4: проверка LESSONS_LEARNED v1.2 + v1.3 + v1.4
lessons_path = ROOT / "LESSONS_LEARNED.md"
if lessons_path.exists():
    lessons_content = lessons_path.read_text(encoding="utf-8")
    # v1.2 уроки
    for new_lesson in ("## L-14:", "## L-15:", "## L-16:"):
        if new_lesson not in lessons_content:
            errors.append(f"LESSONS_LEARNED.md missing v1.2 entry: {new_lesson}")
    # v1.3 уроки (из TASK_03)
    for new_lesson in ("## L-17:", "## L-18:", "## L-19:", "## L-20:"):
        if new_lesson not in lessons_content:
            errors.append(f"LESSONS_LEARNED.md missing v1.3 entry: {new_lesson}")
    # v1.4 уроки (новые из TASK_04)
    for new_lesson in ("## L-21:", "## L-22:", "## L-23:"):
        if new_lesson not in lessons_content:
            errors.append(f"LESSONS_LEARNED.md missing v1.4 entry: {new_lesson}")
    # Должна быть последняя версия
    if "v1.4" not in lessons_content:
        errors.append("LESSONS_LEARNED.md missing v1.4 marker")

# v4: проверка ANTIPATTERNS v1.2 + v1.3 + v1.4
antipatterns_path = ROOT / "ANTIPATTERNS.md"
if antipatterns_path.exists():
    ap_content = antipatterns_path.read_text(encoding="utf-8")
    if "## AP-09:" not in ap_content:
        errors.append("ANTIPATTERNS.md missing AP-09")
    if "## AP-10:" not in ap_content:
        errors.append("ANTIPATTERNS.md missing AP-10")
    # v1.4: AP-10 расширен формами B и C
    if "Форма B" not in ap_content:
        errors.append("ANTIPATTERNS.md missing AP-10 v1.4 extension (Форма B)")
    if "v1.4" not in ap_content:
        errors.append("ANTIPATTERNS.md missing v1.4 marker")

# Финальный результат
if errors:
    print("[FAIL]")
    print(f"{len(errors)} errors:")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)
else:
    print("[PASS] - Cognitive foundation verified")
    print(f"  - 4 files present: CLAUDE.md, LESSONS_LEARNED, PATTERNS, ANTIPATTERNS")
    print(f"  - CLAUDE.md v3 markers found")
    print(f"  - 8 lessons / 5 patterns / 7 antipatterns confirmed")
    print(f"  - All files UTF-8 without BOM")
    sys.exit(0)