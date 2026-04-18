# TASK_02.5 — HARDENING + STANDARDS

**Тип:** процессная инфраструктура / автоматизация защиты
**Приоритет:** критично — закрывает уязвимость "повторные push protection инциденты"
**Исполнитель:** Claude Code
**Источник:** решение Сергея + итоги TASK_02 (3 push protection инцидента)
**Статус:** ACTIVE
**Зависимости:** TASK_02 (rebuild infrastructure) — завершён
**Блокирует:** TASK_03 (schema_layer v2)

---

## ⚠ Contract reminder

Соблюдай CLAUDE.md § 1–28. При любом сомнении — § 3 (СТОП + вопрос Сергею).

Перед началом — прочти когнитивные файлы:
- `LESSONS_LEARNED.md` (v1.2 с L-14, L-15, L-16 preload-нуто) — особенно L-14 (рекурсивная ошибка), L-15 (git log перед amend), L-16 (soft reset)
- `ANTIPATTERNS.md` (v1.2 с AP-09 preload-нуто) — особенно AP-08, AP-09
- `PATTERNS.md` — текущая версия

В отчёте § 9 укажи какие применил.

---

## Контекст

После TASK_02 репо в правильном состоянии: 8 слоёв, `initialize_system` ready, когнитивная система v1.2. Но за TASK_01 + TASK_02 было **3 GitHub push protection инцидента** — все из-за одного типа ошибки (реальные токены в документации). Эти инциденты:
1. Замедлили выполнение задач
2. Вынудили использовать `git commit --amend` и `git reset --soft`
3. Создали 4 новых урока (L-14, L-15, L-16, L-14 мета-урок)

**Цель TASK_02.5:** установить защитный контур который физически не допустит 4-го повтора. Плюс закрыть несколько разрозненных улучшений:
- Стандарт комментирования кода (§ 29 в CLAUDE.md)
- Правила для архитектора в новой сессии (§ 30)
- Расширение § 11 (запрет force push в main)
- Pre-commit автоматический контроль через git hook

---

## Рабочая директория

`C:\CODE\MARKET ANALYSIS\`

---

## Предусловия (проверить перед началом)

1. Текущая ветка — `main`
2. `git status` показывает **только** следующие изменения (L-09):
   - modified: `LESSONS_LEARNED.md` (preload v1.2)
   - modified: `ANTIPATTERNS.md` (preload v1.2)
   - untracked: `TASKS/ACTIVE/TASK_02_5_hardening_and_standards.md` (сам файл задачи)
3. Последний коммит в main — `f217515 chore: sync claude code settings after TASK_02` (или более свежий если были коммиты)
4. `git log --oneline origin/main..main` и `git log --oneline main..origin/main` оба пустые (sync)
5. Нет локальных веток кроме `main`: `git branch` → только `* main`

Если любое условие не выполнено → § 3 (СТОП).

---

## Часть 1 — Создать ветку

```bash
cd "C:\CODE\MARKET ANALYSIS"
git checkout main
git pull origin main
git checkout -b task-02-5-hardening
```

---

## Часть 2 — Закоммитить preload-нутые когнитивные файлы v1.2

### 2.1 Проверка что файлы содержат новое

```bash
findstr /C:"## L-14:" LESSONS_LEARNED.md
findstr /C:"## L-15:" LESSONS_LEARNED.md
findstr /C:"## L-16:" LESSONS_LEARNED.md
findstr /C:"## AP-09:" ANTIPATTERNS.md
findstr /C:"v1.2" LESSONS_LEARNED.md
findstr /C:"v1.2" ANTIPATTERNS.md
```

Все 6 команд должны найти соответствующие маркеры. Если что-то не найдено → § 3.

### 2.2 Коммит

```bash
git add LESSONS_LEARNED.md ANTIPATTERNS.md
git commit -m "task 02.5 part 2: update cognitive system with L-14, L-15, L-16, AP-09 from TASK_02"
```

**Не пушить пока** — push в конце TASK.

---

## Часть 3 — Обновить CLAUDE.md до v4

Текущий CLAUDE.md v3 (27 параграфов). Нужна v4 с:
- Новый § 29 "Стандарт комментирования кода"
- Новый § 30 "Источники правды для новой сессии архитектора"
- Расширение § 11 (запрет force push в main)
- Обновление § 24 pre-commit чеклиста (включает запуск pre_commit_check.py)
- Обновление § 28 (упоминание pre_commit_check как инфраструктуры для защиты от антипаттернов)

### 3.1 Прочитай текущий CLAUDE.md

```bash
type CLAUDE.md | more
```

Сейчас в файле есть:
- "Структура команды и роли"
- § 1-27 контракта
- § 28 когнитивная система
- "Структура репозитория", "Связь", "Принципы"

### 3.2 Модификации

Внести следующие изменения в CLAUDE.md (точечно через str_replace, не переписывая файл целиком).

#### 3.2.1 Расширить § 11 (GitHub и секреты)

Найти в файле существующий блок § 11. Он начинается строкой:
```
### § 11. GitHub и секреты
```

И заканчивается перед:
```
### § 12. Биржевые операции — запрещены
```

**Добавить** в конец § 11 перед заголовком § 12 новый подраздел:

```markdown
### Запрет force push в main

**Критически важно (связь с AP-09):**

- `git push origin main --force` — **запрещено** всегда
- `git push origin main --force-with-lease` — **запрещено** всегда
- `git push -f origin main` — **запрещено** всегда

Допустимые исключения отсутствуют. Если история main требует изменения — использовать:
- `git revert <bad-commit>` — создать reverting коммит
- `git filter-repo` — только по отдельной задаче от архитектора с явным ritual процессом
- Отказаться от изменения истории, решить проблему "вперёд"

Force push допустим **только** в личных feature-ветках (`task-NN-*`, `feature/*`) через `--force-with-lease`, и то до merge в main.

Проверка перед любым force-push:
```bash
git rev-parse --abbrev-ref HEAD
# Если main/master/develop/release/* → СТОП (§ 3). Не push.
```
```

#### 3.2.2 Обновить § 24 (Pre-commit checklist)

Найти блок:
```
### § 24. Pre-commit checklist
```

**Заменить** весь блок § 24 на следующее (старый блок удалить, вставить новый):

```markdown
### § 24. Pre-commit checklist

Перед каждым `git commit` прогони:

**Автоматическая проверка (обязательно):**
- [ ] Запустить `python scripts/pre_commit_check.py` — должен вернуть `[PASS]`. Если `[FAIL]` — не коммить пока не исправлено.

**Ручная проверка:**
- [ ] Делал ли я только то, что просили?
- [ ] Нет ли `TODO` / `FIXME` из моих импровизаций?
- [ ] Все тесты зелёные?
- [ ] `component_status.json` обновлён если это нужно?
- [ ] В коммит не попали `.env`, логи, zip, `__pycache__/`?
- [ ] Коммит-сообщение по формату `task NN: <описание>`?
- [ ] Публичные функции имеют docstring + type hints (§ 16)?
- [ ] Комментарии соответствуют § 29 (модульный docstring, ссылки на уроки)?
- [ ] Я применил релевантные уроки из `LESSONS_LEARNED.md` (§ 28)?
- [ ] Я не нарушил ни один антипаттерн из `ANTIPATTERNS.md` (§ 28)?
- [ ] Есть сомнения хоть в чём — не коммитил?

**Если делаешь push с force-флагом (редко, только в feature-ветке):**
- [ ] Ветка точно не `main`/`master`/`develop`/`release/*` (§ 11, AP-09)?
- [ ] Использую `--force-with-lease`, не `--force`?

Если хоть один пункт нет — **не коммить**, иди по § 3.

Pre-commit hook (`.git/hooks/pre-commit`) запускает автоматическую проверку без необходимости ручного вызова. Если он установлен — автопроверка срабатывает на каждый `git commit`. Если установка hook прошла — ручной запуск `pre_commit_check.py` становится опциональным.
```

#### 3.2.3 Расширить § 28 (Когнитивная система)

В конце § 28 найти строку:
```
**Если ты сам хочешь предложить урок** — не пиши в LESSONS_LEARNED сразу.
```

**Перед** этой строкой добавить новый подраздел:

```markdown
### Автоматическая защита от антипаттернов

Помимо чтения ANTIPATTERNS.md перед задачей, ты защищён **автоматически** через:

1. **`scripts/pre_commit_check.py`** — скрипт проверяющий staged изменения на:
   - AP-05, AP-08 — паттерны валидных токенов (ghp_, github_pat_, sk-, sk-ant-, AWS keys, etc.)
   - AP-01 — hardcoded абсолютные пути (`C:\КОДИНГ`, `C:\CODE\`, `/home/`, `/Users/`) в `.py` файлах
   - AP-06 — emoji в `print()` statements (non-ASCII)
   - AP-03 — `except:` и `except Exception: pass` без логирования (через AST)
   - Запрещённые паттерны TODO/FIXME в production-коде (§ 29)

2. **Git pre-commit hook** (`.git/hooks/pre-commit`) — автоматически запускает `pre_commit_check.py` на каждом `git commit`. Если найдены нарушения — коммит не создаётся.

Если hook заблокировал коммит — это сигнал что ты собирался нарушить антипаттерн. Прочитай его вывод, исправь проблемы, и только затем коммить. **Не обходи hook** через `--no-verify`.

Исключения (редкие случаи когда hook ошибается):
- `--no-verify` допустим **только** с явным согласованием через § 3
- В сообщении коммита обязательно упомяни что делал `--no-verify` и почему
```

#### 3.2.4 Добавить § 29 (Стандарт комментирования кода)

После § 28 и перед существующим разделом "## СТРУКТУРА РЕПОЗИТОРИЯ" добавить:

```markdown
---

## СТАНДАРТ КОММЕНТИРОВАНИЯ КОДА

### § 29. Стандарт комментирования кода

Качественный комментарий объясняет **"почему"**, а не **"что"**. Комментарий который повторяет содержимое кода — шум. Комментарий который раскрывает намерение, ссылается на урок или на ТЗ — ценность.

#### 29.1 Модульный docstring — обязателен

Каждый файл `.py` в `MARKET_MIND/ENGINE/` и `scripts/` начинается с docstring объясняющим назначение модуля:

```python
"""
<module_name> — <краткое описание одной строкой>.

<Расширенное описание в 2-3 предложения>

<Ссылка на Задачу ТЗ если применимо>. Компонент: <component_name>.
"""
```

Пример:
```python
"""
initialize_system — идемпотентная инициализация структуры MARKET_MIND.

Создаёт все 8 канонических слоёв с подпапками согласно ТЗ V10.0-r1 § 1.2.
Безопасна для повторных запусков: существующие директории не удаляются,
существующие файлы не перезаписываются.

Задача 1 из ТЗ V10.0-r1. Компонент: initialize_system.
"""
```

#### 29.2 Docstrings функций — по § 16

Правило уже установлено в § 16:
- Публичные функции (не начинающиеся с `_`) — обязательный docstring + type hints
- Приватные функции (`_funcname`) — docstring желателен, type hints опциональны

#### 29.3 Ссылки на уроки и паттерны в коде

Когда применяешь паттерн из `PATTERNS.md` или избегаешь антипаттерна — **оставляй метку в коде**:

```python
# applies P-01 (relative paths, no hardcoded L-03/AP-01)
BASE = Path(__file__).resolve().parent.parent

# L-04 / AP-06: UTF-8 reconfigure для Windows cp1251
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

# P-02: graceful degradation — None вместо stub данных (AP-02)
if not features_file.exists():
    logger.warning(f"Features not found: {features_file}")
    return None
```

Эти метки работают как:
- Living documentation — каждая метка = пруф что урок применён
- Reverse lookup — можно `grep -rn "P-01"` и увидеть все места где применён паттерн
- Защита при рефакторинге — если кто-то удалит условие с меткой, grep покажет какой урок был забыт

#### 29.4 Inline-комментарии — только "почему"

**Хорошо (объясняет намерение):**
```python
# Проверяем содержимое кроме самого .gitkeep — если в папке только .gitkeep, 
# она всё ещё считается "пустой" для наших целей
has_content = any(p.name != ".gitkeep" for p in contents)
```

**Плохо (повторяет код):**
```python
# Увеличиваем i на 1
i = i + 1

# Открываем файл
with open(path, "r") as f:
    ...
```

**Плохо (шум без смысла):**
```python
# важно
result = process(data)

# hack!!!
x = complex_expression()
```

#### 29.5 Ссылки на ТЗ в спецификационной логике

Когда код реализует конкретное требование ТЗ — ссылайся на раздел:

```python
# TZ V10.0-r1 § 1.20 — Fast Lane timeout 5000ms
FAST_LANE_TIMEOUT_MS = 5000

# TZ V10.0-r1 Задача 3 — Fast Lane Invariant:
# прогноз 1h/4h никогда не блокируется (L-08, AP-04)
if timeframe in FAST_LANE_TIMEFRAMES:
    return _build_degraded_context(query, partial_data)
```

#### 29.6 Запрет на TODO/FIXME в коммитах

**TODO и FIXME в закоммиченном коде запрещены** (§ 4, § 24). Если что-то нужно доделать:
- Мелочь, успеешь до коммита → доделай
- Не успеешь/вне scope → `TASKS/NOTES/ideas_YYYY-MM-DD.md` (§ 4)

`pre_commit_check.py` детектит `TODO` и `FIXME` в staged `.py` файлах и блокирует коммит.

Исключение: если TODO **явно упомянут в тексте TASK файла** как отложенный (например, "TODO: implement in Task 14"), то допустимо — но такие TODO должны ссылаться на конкретную будущую задачу.

#### 29.7 Комментарии к классам и сложным структурам

Классы и большие структуры данных (dict/list с нетривиальной формой) получают пояснение:

```python
# Каноническая структура MARKET_MIND согласно ТЗ V10.0-r1 § 1.2
# Ключ — путь относительно MARKET_MIND/, значение — описание для логов
CANONICAL_STRUCTURE: dict[str, str] = {
    # Core infrastructure
    "SCHEMAS": "JSON schemas (6 canonical + dsl_grammar)",
    ...
    # Layer A — Research Core
    "LAYER_A_RESEARCH": "Research Core layer root",
    ...
}
```

Для публичных классов — docstring описывающий инвариант и публичный контракт:

```python
class SchemaValidator:
    """
    Валидатор JSON-объектов по схемам из SCHEMAS/.
    
    Инвариант: загруженные схемы кэшируются в памяти после первого обращения.
    Публичный контракт: метод validate() принимает dict и имя схемы без расширения,
    возвращает (bool, list[str]) — успех и список ошибок валидации.
    
    Соответствует ТЗ V10.0-r1 Задача 2. Использует паттерны P-01, P-03, P-04.
    """
```
```

#### 3.2.5 Добавить § 30 (Источники правды для новой сессии архитектора)

Сразу после § 29:

```markdown
### § 30. Источники правды для новой сессии архитектора (Claude Opus)

В Project Knowledge хранятся только **канонические документы ТЗ**:
- `TZ/CIS_TZ_V10_0_r1.md`
- `TZ/CIS_V10_Mathematical_Model_v63_COMPLETE.md`
- `TZ/CIS_V10_Combined_Schematics_V5.md`

Когнитивные файлы (`LESSONS_LEARNED.md`, `PATTERNS.md`, `ANTIPATTERNS.md`) и `CLAUDE.md` **НЕ хранятся в Project Knowledge** — чтобы избежать дрейфа между версией в репо и версией в знаниях.

**В начале каждой новой сессии** архитектор (Claude Opus) выполняет web_fetch на актуальные raw-ссылки:

- `https://raw.githubusercontent.com/kik200771-oss/crypto-intelligence-system-v10/main/CLAUDE.md`
- `https://raw.githubusercontent.com/kik200771-oss/crypto-intelligence-system-v10/main/LESSONS_LEARNED.md`
- `https://raw.githubusercontent.com/kik200771-oss/crypto-intelligence-system-v10/main/PATTERNS.md`
- `https://raw.githubusercontent.com/kik200771-oss/crypto-intelligence-system-v10/main/ANTIPATTERNS.md`

Это гарантирует что архитектор работает с **актуальной версией** когнитивки, включая уроки добавленные в предыдущих задачах, без зависимости от ручного обновления Project Knowledge.

Raw-ссылки менее кэшированы чем рендер страницы GitHub UI (L-13) — обновляются в течение минут после push.

**Claude Code** не затронут — он читает когнитивные файлы из рабочей директории локально (§ 25 шаг 1), где они всегда актуальны.
```

#### 3.2.6 Обновить блок "Структура репозитория"

В разделе "Структура репозитория" найти строки когнитивных файлов и добавить `scripts/pre_commit_check.py`:

Найти блок вроде:
```
├── scripts/                # утилиты (audit zip и т.д.)
```

**Заменить** на:
```
├── scripts/                # утилиты (audit zip, pre_commit_check, verify_*)
```

#### 3.2.7 Обновить финальную строку

В самом конце файла найти:
```
**Когнитивные файлы (LESSONS_LEARNED, PATTERNS, ANTIPATTERNS) — твоя память. Без них ты каждый раз начинаешь с нуля.**
```

**Заменить** на:
```
**Когнитивные файлы (LESSONS_LEARNED, PATTERNS, ANTIPATTERNS) — твоя память. Без них ты каждый раз начинаешь с нуля.**

**Pre-commit hook и pre_commit_check.py — твой защитник. Он ловит повторение антипаттернов до того, как они попадут в git.**
```

### 3.3 Проверка CLAUDE.md v4

После всех изменений:

```bash
findstr /C:"§ 29. Стандарт комментирования кода" CLAUDE.md
findstr /C:"§ 30. Источники правды для новой сессии" CLAUDE.md
findstr /C:"Запрет force push в main" CLAUDE.md
findstr /C:"pre_commit_check.py" CLAUDE.md
findstr /C:"AP-09" CLAUDE.md
```

Все 5 поисков должны найти маркеры. Если что-то не найдено → § 3.

### 3.4 Коммит CLAUDE.md

```bash
git add CLAUDE.md
git commit -m "task 02.5 part 3: update CLAUDE.md to v4 (§ 29 comments standard, § 30 fetch sources, § 11 no force push)"
```

---

## Часть 4 — Создать `scripts/pre_commit_check.py`

Единый скрипт проверяющий staged изменения перед коммитом на **все** антипаттерны по которым у нас есть детектор.

### 4.1 Создать файл

Путь: `scripts/pre_commit_check.py`

Содержимое:

```python
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
    ("Windows path C:\\", r'["\'](?:[A-Z]:\\\\|[A-Z]:/)'),
    ("Linux absolute path", r'["\']/(?:home|Users|opt|etc|var)/'),
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
        # Пропускаем строки в которых явно пример (# applies, # example, etc.)
        if "example" in line.lower() or "пример" in line.lower():
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
```

### 4.2 Первый запуск для проверки работы

```bash
python scripts/pre_commit_check.py
```

Поскольку сейчас staged только CLAUDE.md (из Части 3) и LESSONS/ANTIPATTERNS (из Части 2, уже закоммичены) — скрипт должен либо вывести `[INFO] No staged files` либо `[PASS] 0 files checked, 0 violations` либо конкретно описать что проверял.

### 4.3 Коммит pre_commit_check.py

```bash
git add scripts/pre_commit_check.py
git commit -m "task 02.5 part 4: add pre_commit_check.py - static analysis for staged files"
```

Важно: коммит самого скрипта не должен запускаться через собственный hook (hook ещё не установлен в Части 5). Проверь что коммит прошёл.

---

## Часть 5 — Установить git pre-commit hook

### 5.1 Создать hook-файл

Путь: `.git/hooks/pre-commit`

**Важно:** `.git/` — это локальная директория git, она **не коммитится в репо**. Hook устанавливается локально, не синхронизируется через push. Это нормально — каждый разработчик должен установить hook сам.

Содержимое hook-файла:

```bash
#!/bin/sh
# Pre-commit hook for CIS V10.0-r1
# Runs scripts/pre_commit_check.py before allowing commit.
#
# This hook is local (.git/hooks/ is not committed to repo).
# To reinstall: see scripts/install_git_hooks.py

python scripts/pre_commit_check.py
exit $?
```

### 5.2 Сделать hook исполняемым

На Windows с Git Bash:
```bash
chmod +x .git/hooks/pre-commit
```

На чистой Windows (без bash) — просто создать файл без расширения, Git сам его запустит через shell.

### 5.3 Создать helper `scripts/install_git_hooks.py`

Поскольку `.git/hooks/` не коммитится, создаём скрипт-установщик который можно запускать вручную. Содержимое:

```python
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
```

### 5.4 Запуск установщика

```bash
python scripts/install_git_hooks.py
```

Ожидаемый вывод:
```
[INFO] Installing git hooks for C:\CODE\MARKET ANALYSIS
[PASS] pre-commit hook installed at C:\CODE\MARKET ANALYSIS\.git\hooks\pre-commit
```

Если `[WARN] Existing pre-commit hook found` — ответить `y` для замены (у нас его не должно быть).

### 5.5 Закоммитить install_git_hooks.py

```bash
git add scripts/install_git_hooks.py
git commit -m "task 02.5 part 5: add install_git_hooks.py for manual hook setup"
```

---

## Часть 6 — Smoke test hook

Проверяем что hook реально блокирует нарушения.

### 6.1 Попытка коммита безобидного файла

Создать временный `test_hook_smoke.py`:

```bash
echo from pathlib import Path > test_hook_smoke.py
echo # applies P-01 >> test_hook_smoke.py
echo BASE = Path(__file__).resolve().parent.parent >> test_hook_smoke.py

git add test_hook_smoke.py
git commit -m "smoke test"
```

Ожидается `[PASS]` и успешный коммит (файл не нарушает антипаттернов).

### 6.2 Попытка коммита с нарушением

Отредактировать `test_hook_smoke.py` — добавить плохой код:

```bash
echo # Bad hardcoded path (should trigger AP-01) >> test_hook_smoke.py
echo LOG = r"C:\CODE\MARKET ANALYSIS\logs" >> test_hook_smoke.py

git add test_hook_smoke.py
git commit -m "smoke test with violation"
```

Ожидается `[FAIL]` и блокировка коммита с выводом похожим на:
```
  AP-01: test_hook_smoke.py:N — Windows path C:\
    Line: LOG = r"C:\CODE\MARKET ANALYSIS\logs"
    Fix: use Path(__file__).resolve().parent.parent (see P-01)
```

### 6.3 Откат smoke test

После демонстрации что hook работает — удалить тестовый файл и откатить коммит из 6.1:

```bash
# Откатить коммит из 6.1 (если прошёл) — soft reset
git reset --soft HEAD~1

# Удалить файл из staging и из рабочей директории
git reset HEAD test_hook_smoke.py
del test_hook_smoke.py
```

Проверить что ничего не осталось:
```bash
git status
dir test_hook_smoke.py 2>nul
```

Оба должны показать что файла нет и рабочее дерево чистое (кроме предыдущих коммитов этой ветки).

---

## Часть 7 — Обновить `scripts/verify_cognitive_foundation.py`

Добавить проверку что CLAUDE.md содержит маркеры v4 и что новые скрипты существуют.

### 7.1 Найти существующий verify_cognitive_foundation.py

```bash
type scripts\verify_cognitive_foundation.py | more
```

Он был создан в TASK_01, проверяет наличие 4 файлов и ключевых маркеров CLAUDE.md v3.

### 7.2 Расширить проверки

В файле `scripts/verify_cognitive_foundation.py` найти блок с `markers` — список маркеров для проверки CLAUDE.md. Добавить в него новые маркеры v4:

```python
markers = [
    # v3 markers (already present):
    "§ 28. Как работают когнитивные файлы",
    "СТРУКТУРА КОМАНДЫ И РОЛИ",
    "LESSONS_LEARNED.md",
    "PATTERNS.md",
    "ANTIPATTERNS.md",
    "Lessons applied:",
    # v4 markers (new):
    "§ 29. Стандарт комментирования кода",
    "§ 30. Источники правды для новой сессии",
    "Запрет force push в main",
    "pre_commit_check.py",
]
```

Также добавить **новые проверки** после существующих:

```python
# v4: проверка наличия новых скриптов
v4_scripts = [
    "scripts/pre_commit_check.py",
    "scripts/install_git_hooks.py",
]
for s in v4_scripts:
    path = ROOT / s
    if not path.is_file():
        errors.append(f"Missing v4 script: {s}")

# v4: проверка LESSONS_LEARNED v1.2
lessons_path = ROOT / "LESSONS_LEARNED.md"
if lessons_path.exists():
    lessons_content = lessons_path.read_text(encoding="utf-8")
    for new_lesson in ("## L-14:", "## L-15:", "## L-16:"):
        if new_lesson not in lessons_content:
            errors.append(f"LESSONS_LEARNED.md missing v1.2 entry: {new_lesson}")
    if "v1.2" not in lessons_content:
        errors.append("LESSONS_LEARNED.md missing v1.2 marker")

# v4: проверка ANTIPATTERNS v1.2
antipatterns_path = ROOT / "ANTIPATTERNS.md"
if antipatterns_path.exists():
    ap_content = antipatterns_path.read_text(encoding="utf-8")
    if "## AP-09:" not in ap_content:
        errors.append("ANTIPATTERNS.md missing AP-09")
    if "v1.2" not in ap_content:
        errors.append("ANTIPATTERNS.md missing v1.2 marker")
```

### 7.3 Запустить verify

```bash
python scripts/verify_cognitive_foundation.py
```

Должен вывести `[PASS]`. Если `[FAIL]` — § 3.

### 7.4 Коммит

```bash
git add scripts/verify_cognitive_foundation.py
git commit -m "task 02.5 part 7: extend verify_cognitive_foundation for v4 markers"
```

---

## Часть 8 — Финальный merge и push

### 8.1 Проверка истории коммитов в ветке

```bash
git log --oneline main..task-02-5-hardening
```

Ожидаются примерно такие коммиты (в обратном порядке по времени):
- `<hash> task 02.5 part 7: extend verify_cognitive_foundation for v4 markers`
- `<hash> task 02.5 part 5: add install_git_hooks.py for manual hook setup`
- `<hash> task 02.5 part 4: add pre_commit_check.py - static analysis for staged files`
- `<hash> task 02.5 part 3: update CLAUDE.md to v4 (§ 29 comments standard, § 30 fetch sources, § 11 no force push)`
- `<hash> task 02.5 part 2: update cognitive system with L-14, L-15, L-16, AP-09 from TASK_02`

### 8.2 Merge в main

```bash
git checkout main
git merge task-02-5-hardening
```

Должен быть fast-forward (без конфликтов).

### 8.3 Push

```bash
git push origin main
```

**Ожидается успешный push.** Pre-commit hook на push не работает (он только на commit), но если в коде случайно остался паттерн секрета — GitHub push protection всё равно заблокирует.

Если push заблокирован → § 3 (это был бы индикатор что наш pre_commit_check не поймал что-то).

### 8.4 Удалить ветку

```bash
git branch -d task-02-5-hardening
```

### 8.5 Архивировать TASK

```bash
git mv TASKS/ACTIVE/TASK_02_5_hardening_and_standards.md TASKS/COMPLETED/TASK_02_5_hardening_and_standards.md
git commit -m "archive TASK_02.5"
git push origin main
```

### 8.6 Финальная проверка синхронизации

```bash
git fetch origin
git log --oneline origin/main..main   # должен быть пуст
git log --oneline main..origin/main   # должен быть пуст
git branch -a                          # только main + remotes/origin/*
git status                             # clean working tree
```

---

## Часть 9 — Финальный отчёт

Формат § 9 CLAUDE.md:

```
TASK_02.5 [hardening_and_standards] — COMPLETED

БЛОК A — когнитивная система v1.2:
  Added: L-14 (рекурсивная ошибка AP-08), L-15 (git log перед amend), L-16 (soft reset)
  Added: AP-09 (force push в main запрещён)
  Commit (cognitive): <hash>

БЛОК Б — CLAUDE.md v4:
  Added: § 29 (стандарт комментирования)
  Added: § 30 (источники правды архитектора — fetch raw.githubusercontent)
  Extended: § 11 (запрет force push в main)
  Updated: § 24 (pre-commit чеклист с запуском pre_commit_check.py)
  Extended: § 28 (упоминание автоматической защиты через hook)
  Commit: <hash>

БЛОК В — автоматическая защита:
  Created: scripts/pre_commit_check.py (проверка AP-01, AP-03, AP-05, AP-06, AP-08, TODO/FIXME)
  Created: scripts/install_git_hooks.py (установщик git hooks)
  Installed: .git/hooks/pre-commit (локально, не в репо)
  Commits: <hash1>, <hash2>

БЛОК Г — верификация:
  Updated: scripts/verify_cognitive_foundation.py (проверка v4 маркеров)
  Tests:
    python scripts/pre_commit_check.py — [PASS]
    python scripts/verify_cognitive_foundation.py — [PASS]
    smoke test hook (часть 6) — detected AP-01 in test file, blocked commit
  Commit: <hash>

ТЕХНИЧЕСКИЙ:
  Branch: task-02-5-hardening (удалена после merge)
  Archive commit: <hash>
  Push в origin/main: успешный (без push protection блокировки)

Время работы: <минуты>

Lessons applied:
  - L-04 / AP-06 (ASCII маркеры в pre_commit_check.py и install_git_hooks.py)
  - L-03 / AP-01 (Path(__file__).resolve() везде)
  - L-09 (предусловия учли preload L/AP файлов)
  - L-14 (проверил что сам pre_commit_check.py не содержит реальных токенов в паттернах)
  - L-15 (перед git операциями делал git log/status)

Patterns applied:
  - P-01 (относительные пути в обоих скриптах)
  - P-03 (subprocess.CalledProcessError с логированием в pre_commit_check)
  - P-05 (UTF-8 reconfigure + ASCII маркеры в скриптах)

Antipatterns avoided:
  - AP-01 (0 hardcoded путей)
  - AP-03 (AST-based detection — 0 bare except в новом коде)
  - AP-05 / AP-08 (pre_commit_check сам проверял себя — 0 violations при коммите)
  - AP-06 (ASCII в print)
  - AP-09 (0 force push в main)

Component status updates: нет (TASK_02.5 — процессная инфраструктура, не компонент системы)

Ideas logged: <N>
Warnings/issues: none

Готов к TASK_03 (schema_layer v2).
```

---

## Критерии готовности (acceptance criteria)

- [ ] `LESSONS_LEARNED.md` v1.2 с L-14, L-15, L-16 закоммичен в main
- [ ] `ANTIPATTERNS.md` v1.2 с AP-09 закоммичен в main
- [ ] `CLAUDE.md` v4 с § 29 и § 30, расширенными § 11 и § 24, закоммичен
- [ ] `scripts/pre_commit_check.py` создан, закоммичен, запускается `[PASS]` на чистом репо
- [ ] `scripts/install_git_hooks.py` создан, закоммичен, успешно устанавливает hook
- [ ] `.git/hooks/pre-commit` установлен локально (не в репо — это нормально)
- [ ] Smoke test из Части 6 показал что hook блокирует коммит с AP-01 нарушением
- [ ] `scripts/verify_cognitive_foundation.py` расширен, выдаёт `[PASS]`
- [ ] Все изменения в main, ветка `task-02-5-hardening` удалена
- [ ] TASK файл в `COMPLETED/`, финальный отчёт Сергею

---

## Важные предупреждения

- ⚠ **Не пытайся закоммитить реальный токен** в pre_commit_check.py для "тестирования паттернов". Паттерны в regex работают без реальных значений — используй `ghp_[PLACEHOLDER_PATTERN_EXAMPLE]` в комментариях или вообще не показывай примеры
- ⚠ **Не используй `--no-verify`** для обхода hook во время этой задачи. Если hook что-то блокирует — исправь проблему, не обходи
- ⚠ **Не делай force push в main** ни при каких обстоятельствах (AP-09). Если что-то пошло не так на последних этапах — soft reset + single commit (L-16)
- ⚠ **`.git/hooks/`** не коммитится — это нормально, для этого есть install_git_hooks.py
- ⚠ При smoke test в Части 6 **обязательно откатить** тестовый коммит из 6.1 через `git reset --soft HEAD~1` — не оставлять в истории

---

**После успешного выполнения TASK_02.5 — мы закрываем тему push protection раз и навсегда (через автоматическую защиту) и устанавливаем стандарт комментирования. Готовы к TASK_03 (schema_layer v2).**
