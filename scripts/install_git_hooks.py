#!/usr/bin/env python3
"""
install_git_hooks — устанавливает git hooks для CIS V10.0-r1.

Копирует pre-commit hook в .git/hooks/. Нужен потому что .git/ не под
контролем версий — каждый разработчик должен запустить этот скрипт один раз.

Запуск: python scripts/install_git_hooks.py
"""
from __future__ import annotations

import os
import stat
import sys
from pathlib import Path

# L-04 / P-05: UTF-8 reconfigure
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

# applies P-01 (relative paths)
ROOT = Path(__file__).resolve().parent.parent

PRE_COMMIT_HOOK_CONTENT = """#!/bin/sh
# Pre-commit hook for CIS V10.0-r1
# Runs scripts/pre_commit_check.py before allowing commit.
#
# This hook is local (.git/hooks/ is not committed to repo).
# To reinstall: python scripts/install_git_hooks.py

python scripts/pre_commit_check.py
exit $?
"""


def install_pre_commit_hook() -> bool:
    """
    Устанавливает pre-commit hook в .git/hooks/pre-commit.

    Returns:
        True если успешно, False при ошибке.
    """
    hooks_dir = ROOT / ".git" / "hooks"
    if not hooks_dir.is_dir():
        print(f"[FAIL] .git/hooks/ not found at {hooks_dir}")
        print("[HINT] Are you in a git repository?")
        return False

    hook_path = hooks_dir / "pre-commit"

    # Проверка не затрём ли существующий custom hook
    if hook_path.exists():
        existing = hook_path.read_text(encoding="utf-8", errors="ignore")
        if "pre_commit_check.py" in existing:
            print(f"[INFO] pre-commit hook already installed at {hook_path}")
            return True
        print(f"[WARN] Existing pre-commit hook found at {hook_path}")
        print(f"       Content preview: {existing[:100]}...")
        response = input("Overwrite? (y/N): ").strip().lower()
        if response != "y":
            print("[ABORT] User declined overwrite")
            return False

    try:
        hook_path.write_text(PRE_COMMIT_HOOK_CONTENT, encoding="utf-8")
        # Сделать исполняемым (важно для Linux/Mac, не обязательно для Windows)
        try:
            current_mode = hook_path.stat().st_mode
            hook_path.chmod(current_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        except OSError:
            # Windows — chmod работает ограниченно, но hook всё равно запустится
            pass
        print(f"[PASS] pre-commit hook installed at {hook_path}")
        return True
    except OSError as e:
        # P-03: конкретный exception + логирование
        print(f"[FAIL] Cannot write hook: {e}")
        return False


def main() -> int:
    """CLI entry point."""
    print(f"[INFO] Installing git hooks for {ROOT}")
    ok = install_pre_commit_hook()
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())