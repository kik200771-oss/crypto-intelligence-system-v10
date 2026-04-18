#!/usr/bin/env python3
"""
pre_commit_check — автоматическая проверка staged изменений на антипаттерны.

Защищает от повторения AP-01, AP-03, AP-05, AP-06, AP-08 через статический
анализ diff'а staged файлов. Возвращает exit code 1 если найдены нарушения,
0 если всё чисто.

Предназначен для запуска:
- вручную перед git commit (§ 24 CLAUDE.md)
- автоматически через git pre-commit hook (.git/hooks/pre-commit)

Проверяет:
- AP-05/AP-08: паттерны валидных секретов (GitHub/OpenAI/Anthropic/AWS tokens)
- AP-01: hardcoded абсолютные пути в .py файлах
- AP-06: emoji в print() statements
- AP-03: except: и except Exception: pass без логирования (через AST)
- § 29.6: TODO/FIXME в production-коде

Не модифицирует файлы, только читает staged content через git diff.
"""
from __future__ import annotations

import ast
import re
import subprocess
import sys
from pathlib import Path

# L-04 / P-05: UTF-8 reconfigure для Windows cp1251
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")


# applies P-01 (relative paths, no hardcoded — L-03/AP-01)
ROOT = Path(__file__).resolve().parent.parent


# === ДЕТЕКТОРЫ СЕКРЕТОВ (AP-05, AP-08) ===
# Паттерны которые выглядят как валидные токены
# Ключевые слова REDACTED/EXAMPLE/FAKE/NOT_A_REAL исключаются из срабатывания
SECRET_PATTERNS: list[tuple[str, str]] = [
    # GitHub classic PAT: ghp_ + 36 chars
    ("GitHub classic PAT", r"ghp_[a-zA-Z0-9]{36}"),
    # GitHub fine-grained PAT: github_pat_ + 22 + _ + 59
    ("GitHub fine-grained PAT", r"github_pat_[a-zA-Z0-9]{22}_[a-zA-Z0-9]{59}"),
    # GitHub OAuth: gho_ + 36 chars
    ("GitHub OAuth", r"gho_[a-zA-Z0-9]{36}"),
    # OpenAI API key: sk- + 48 chars (sk-XXXXXXXX...)
    ("OpenAI API key", r"sk-[a-zA-Z0-9]{48}"),
    # OpenAI project key: sk-proj- + 48+
    ("OpenAI project key", r"sk-proj-[a-zA-Z0-9_-]{40,}"),
    # Anthropic API key: sk-ant- + 95 chars
    ("Anthropic API key", r"sk-ant-[a-zA-Z0-9_-]{95,}"),
    # AWS access key: AKIA + 16 chars
    ("AWS access key", r"AKIA[0-9A-Z]{16}"),
    # Slack webhook
    ("Slack webhook", r"hooks\.slack\.com/services/T[A-Z0-9]{8,}/B[A-Z0-9]{8,}/[a-zA-Z0-9]{24}"),
]

# Явные маркеры которые ОЗНАЧАЮТ что это не реальный секрет
# Если в строке есть любой из этих маркеров — пропускаем
SAFE_MARKERS: list[str] = [
    "REDACTED",
    "EXAMPLE",
    "FAKE",
    "NOT_A_REAL",
    "DO_NOT_RESTORE",
    "WOULD_BE_HERE",
    "PLACEHOLDER",
    "your_",  # "your_binance_key_here"
]


# === ДЕТЕКТОРЫ HARDCODED ПУТЕЙ (AP-01) ===
HARDCODED_PATH_PATTERNS: list[tuple[str, str]] = [
    # Windows absolute path: "C:\..." or "C:/..." — один или два backslash
    ("Windows path with drive letter", r'["\'][A-Za-z]:[\\\/]'),
    # Linux/Mac absolute paths in string literals
    ("Unix absolute path", r'["\']/(?:home|Users|opt|etc|var)/'),
]


# === ДЕТЕКТОРЫ TODO/FIXME (§ 29.6) ===
TODO_PATTERNS: list[tuple[str, str]] = [
    ("TODO in code", r"#\s*TODO\b"),
    ("FIXME in code", r"#\s*FIXME\b"),
    ("XXX in code", r"#\s*XXX\b"),
]


def get_staged_files() -> list[Path]:
    """
    Возвращает список путей к staged файлам через git.

    Returns:
        Список Path объектов относительно ROOT.
    """
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
            encoding="utf-8",
        )
        files = [Path(line.strip()) for line in result.stdout.splitlines() if line.strip()]
        return files
    except subprocess.CalledProcessError as e:
        # P-03: конкретный exception + логирование
        print(f"[ERROR] git diff failed: {e}")
        print(f"        stderr: {e.stderr}")
        return []


def get_staged_content(file_path: Path) -> str | None:
    """
    Возвращает staged содержимое файла (из git index, не с диска).

    Args:
        file_path: путь относительно ROOT

    Returns:
        Содержимое файла или None если не удалось прочитать.
    """
    try:
        result = subprocess.run(
            ["git", "show", f":{file_path.as_posix()}"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
            encoding="utf-8",
        )
        return result.stdout
    except subprocess.CalledProcessError:
        # Файл может быть удалён/переименован — нормально, пропускаем
        return None
    except UnicodeDecodeError:
        # Бинарный файл — пропускаем
        return None


def check_secrets(file_path: Path, content: str) -> list[str]:
    """
    Проверяет файл на паттерны секретов (AP-05, AP-08).

    Args:
        file_path: путь к файлу (для сообщений об ошибках)
        content: содержимое файла

    Returns:
        Список найденных нарушений (строк для репорта).
    """
    violations: list[str] = []
    for line_num, line in enumerate(content.splitlines(), 1):
        # Пропускаем строки с явными маркерами "это не секрет"
        if any(marker in line for marker in SAFE_MARKERS):
            continue
        for pattern_name, regex in SECRET_PATTERNS:
            if re.search(regex, line):
                # Обрезаем показ чтобы не вывести сам потенциальный секрет
                preview = line.strip()[:60]
                violations.append(
                    f"  AP-05/AP-08: {file_path}:{line_num} — {pattern_name}"
                    f"\n    Preview: {preview}..."
                    f"\n    Fix: replace with REDACTED-style marker (see AP-08)"
                )
    return violations


def check_hardcoded_paths(file_path: Path, content: str) -> list[str]:
    """
    Проверяет .py файлы на hardcoded абсолютные пути (AP-01).

    Args:
        file_path: путь к файлу
        content: содержимое файла

    Returns:
        Список нарушений.
    """
    if file_path.suffix != ".py":
        return []
    violations: list[str] = []
    for line_num, line in enumerate(content.splitlines(), 1):
        # Пропускаем docstring-примеры и комментарии-примеры
        stripped = line.strip()
        if stripped.startswith("#") or stripped.startswith('"""') or stripped.startswith("'''"):
            continue
        # Пропускаем строки-комментарии начинающиеся с # и явно помеченные как "пример"
        if stripped.startswith("#") and (
            "example:" in stripped.lower()
            or "пример:" in stripped.lower()
            or "e.g." in stripped.lower()
        ):
            continue
        for pattern_name, regex in HARDCODED_PATH_PATTERNS:
            if re.search(regex, line):
                violations.append(
                    f"  AP-01: {file_path}:{line_num} — {pattern_name}"
                    f"\n    Line: {stripped[:80]}"
                    f"\n    Fix: use Path(__file__).resolve().parent.parent (see P-01)"
                )
    return violations


def check_emoji_in_print(file_path: Path, content: str) -> list[str]:
    """
    Проверяет .py файлы на non-ASCII символы в print() (AP-06).

    Args:
        file_path: путь к файлу
        content: содержимое файла

    Returns:
        Список нарушений.
    """
    if file_path.suffix != ".py":
        return []
    violations: list[str] = []
    # Примитивная проверка: строки содержащие "print(" и non-ASCII в аргументах
    print_pattern = re.compile(r"print\s*\([^)]*\)")
    for line_num, line in enumerate(content.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        matches = print_pattern.findall(line)
        for match in matches:
            # Проверяем есть ли non-ASCII символы кроме русских букв
            # (русский текст в print допустим если используется UTF-8 reconfigure)
            # Проверяем конкретно emoji-диапазоны Unicode
            for ch in match:
                code = ord(ch)
                # Диапазоны emoji
                if (
                    0x1F300 <= code <= 0x1F9FF
                    or 0x2600 <= code <= 0x27BF  # symbols
                    or 0x1F000 <= code <= 0x1F2FF  # mahjong, playing cards
                    or code in (0x2705, 0x274C, 0x26A0, 0x2B50)  # common ones
                ):
                    violations.append(
                        f"  AP-06: {file_path}:{line_num} — emoji in print()"
                        f"\n    Char: U+{code:04X} in: {stripped[:60]}"
                        f"\n    Fix: use ASCII markers [OK]/[FAIL]/[PASS] (see P-05)"
                    )
                    break
    return violations


def check_bare_except(file_path: Path, content: str) -> list[str]:
    """
    Проверяет .py файлы на голый except: или except Exception: pass (AP-03).

    Использует AST для точности.

    Args:
        file_path: путь к файлу
        content: содержимое файла

    Returns:
        Список нарушений.
    """
    if file_path.suffix != ".py":
        return []
    violations: list[str] = []
    try:
        tree = ast.parse(content)
    except SyntaxError:
        # Файл с синтаксической ошибкой — не наша задача ловить, pass
        return []

    for node in ast.walk(tree):
        if isinstance(node, ast.ExceptHandler):
            # Голый except: (без типа исключения)
            if node.type is None:
                violations.append(
                    f"  AP-03: {file_path}:{node.lineno} — bare except:"
                    f"\n    Fix: catch specific exception type (see P-03)"
                )
                continue
            # except Exception: pass — тело это только pass
            if (
                isinstance(node.type, ast.Name)
                and node.type.id == "Exception"
                and len(node.body) == 1
                and isinstance(node.body[0], ast.Pass)
            ):
                violations.append(
                    f"  AP-03: {file_path}:{node.lineno} — except Exception: pass"
                    f"\n    Fix: log the exception or re-raise (see P-03)"
                )
    return violations


def check_todo_fixme(file_path: Path, content: str) -> list[str]:
    """
    Проверяет .py файлы на TODO/FIXME комментарии (§ 29.6).

    Args:
        file_path: путь к файлу
        content: содержимое файла

    Returns:
        Список нарушений.
    """
    if file_path.suffix != ".py":
        return []
    violations: list[str] = []
    for line_num, line in enumerate(content.splitlines(), 1):
        for pattern_name, regex in TODO_PATTERNS:
            if re.search(regex, line):
                violations.append(
                    f"  TODO/FIXME: {file_path}:{line_num} — {pattern_name}"
                    f"\n    Line: {line.strip()[:80]}"
                    f"\n    Fix: move to TASKS/NOTES/ or resolve before commit (§ 29.6)"
                )
    return violations


def main() -> int:
    """
    CLI-точка входа. Проверяет все staged файлы, возвращает exit code.

    Returns:
        0 если чисто, 1 если найдены нарушения.
    """
    staged = get_staged_files()
    if not staged:
        print("[INFO] No staged files — nothing to check")
        return 0

    print(f"[INFO] Checking {len(staged)} staged file(s)...")

    all_violations: list[str] = []
    checked_count = 0

    for file_path in staged:
        content = get_staged_content(file_path)
        if content is None:
            continue
        checked_count += 1

        # Запускаем все чекеры
        all_violations.extend(check_secrets(file_path, content))
        all_violations.extend(check_hardcoded_paths(file_path, content))
        all_violations.extend(check_emoji_in_print(file_path, content))
        all_violations.extend(check_bare_except(file_path, content))
        all_violations.extend(check_todo_fixme(file_path, content))

    if all_violations:
        print(f"\n[FAIL] Found {len(all_violations)} antipattern violation(s) in {checked_count} file(s):\n")
        for v in all_violations:
            print(v)
        print("\n[HINT] See LESSONS_LEARNED.md / ANTIPATTERNS.md / PATTERNS.md for context.")
        print("[HINT] Fix violations and re-run check. Do NOT bypass via --no-verify (§ 28).")
        return 1

    print(f"[PASS] {checked_count} file(s) checked, 0 antipattern violations")
    return 0


if __name__ == "__main__":
    sys.exit(main())