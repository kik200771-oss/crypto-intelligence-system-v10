# TASK_01 — УСТАНОВКА КОГНИТИВНОЙ СИСТЕМЫ И ОБНОВЛЕНИЕ CLAUDE.md

**Тип:** инфраструктура процесса / накопление знаний
**Приоритет:** критично — должно быть установлено до содержательных TASK_02+
**Исполнитель:** Claude Code
**Источник:** решение Сергея + архитектора Claude Opus (2026-04-18)
**Статус:** ACTIVE
**Блокирует:** TASK_02_rebuild_infrastructure

---

## ⚠ Contract reminder

Соблюдай CLAUDE.md § 1–28. При любом сомнении — § 3 (СТОП + вопрос Сергею).
Эта задача — установка самого CLAUDE.md v3 и когнитивной системы. Строго по тексту.

---

## Контекст

После TASK_00 репо очищено от legacy. Следующий шаг перед содержательной работой — установить **систему когнитивного обучения**:

- **CLAUDE.md v3** — расширенная версия с описанием ролей команды (§ "Структура команды") и § 28 про когнитивную систему
- **LESSONS_LEARNED.md** — журнал уроков из реальных ошибок (8 уроков уже сформулированы)
- **PATTERNS.md** — каталог одобренных паттернов кода (5 паттернов)
- **ANTIPATTERNS.md** — каталог запрещённых решений (7 антипаттернов)

**Цель:** после этой задачи Claude Code перед каждой последующей задачей автоматически будет прогонять эти файлы и избегать повторения ошибок.

Цитата из решения Сергея (2026-04-18):
> после того как ты проверяешь работу или код или задачу которую выполнял Claude Code если ты находишь ошибку в подходе решения или какую то системную ошибку или не ошибку, а даже просто указываешь на то, что это можно сделать лучше и не так, а вот так, это должно превращаться в новые знание которые и фиксируется в файле когнитивного опыта и знания.

---

## Рабочая директория

`C:\CODE\MARKET ANALYSIS\`

---

## Предусловия (проверить перед началом)

1. `git status` → рабочая директория чистая, нет uncommitted changes
2. Текущая ветка — `main`
3. `MARKET_MIND/CONFIG/component_status.json` существует (после TASK_00)
4. `TASKS/ACTIVE/` содержит этот файл TASK_01
5. `TASKS/NOTES/` существует (создан в TASK_00)

Если любое условие не выполнено → § 3 (СТОП + вопрос Сергею).

---

## Часть 1 — Создать ветку

```bash
cd "C:\CODE\MARKET ANALYSIS"
git checkout main
git pull origin main
git checkout -b task-01-cognitive-foundation
```

---

## Часть 2 — Заменить CLAUDE.md на v3

Текущий CLAUDE.md в корне (от TASK_00) содержит 27 параграфов. Нужна v3 с:
- Новым разделом "Структура команды и роли" (перед § 1)
- Новым § 28 "Когнитивная система — обучение на опыте"
- Обновлённым § 25 (шаг 1 — читать когнитивные файлы)
- Обновлённым § 24 (pre-commit checklist включает проверки против ANTIPATTERNS)
- Обновлённой структурой репо (показаны 3 новых файла)

### Действие

Замени полностью содержимое `C:\CODE\MARKET ANALYSIS\CLAUDE.md` на файл **`CLAUDE.md`**, приложенный к этой задаче (получен от архитектора как отдельный файл в чате).

**Важно:** если вместо отдельного файла Сергей передал содержимое в сообщении — бери его оттуда. В этот TASK текст CLAUDE.md не вкладываю повторно чтобы избежать путаницы с экранированием backticks.

### Проверка

После замены выполни:
```bash
# Проверить наличие ключевых маркеров v3
findstr /C:"§ 28. Как работают когнитивные файлы" CLAUDE.md
findstr /C:"СТРУКТУРА КОМАНДЫ И РОЛИ" CLAUDE.md
findstr /C:"LESSONS_LEARNED.md" CLAUDE.md
findstr /C:"PATTERNS.md" CLAUDE.md
findstr /C:"ANTIPATTERNS.md" CLAUDE.md
```

Все 5 поисков должны найти соответствующие строки. Если хоть один не найден → § 3.

---

## Часть 3 — Создать три когнитивных файла

Создай в корне проекта `C:\CODE\MARKET ANALYSIS\` три файла из переданных архитектором:

1. `LESSONS_LEARNED.md` — 8 уроков L-01...L-08
2. `PATTERNS.md` — 5 паттернов P-01...P-05
3. `ANTIPATTERNS.md` — 7 антипаттернов AP-01...AP-07

Файлы передаются отдельно как артефакты в чате с Сергеем. **Содержимое не изменять**.

### Проверка

После создания:

```bash
# Проверка что файлы существуют и не пустые
dir LESSONS_LEARNED.md PATTERNS.md ANTIPATTERNS.md
```

Все три должны быть > 0 байт.

```bash
# Проверка ключевых маркеров в каждом
findstr /C:"L-01:" LESSONS_LEARNED.md
findstr /C:"L-08:" LESSONS_LEARNED.md
findstr /C:"P-01:" PATTERNS.md
findstr /C:"P-05:" PATTERNS.md
findstr /C:"AP-01:" ANTIPATTERNS.md
findstr /C:"AP-07:" ANTIPATTERNS.md
```

Все 6 маркеров должны быть найдены.

---

## Часть 4 — Прочитать когнитивные файлы полностью

Это не формальность. Прочти каждый файл целиком с пониманием:

1. **LESSONS_LEARNED.md** — разобраться в каждом из 8 уроков: что было неправильно, что правильно, когда применять
2. **PATTERNS.md** — разобраться в 5 паттернах: когда использовать, почему именно так, какие альтернативы неприемлемы
3. **ANTIPATTERNS.md** — разобраться в 7 антипаттернах: как их опознать, как проверять что не допускаешь, какие альтернативы правильны

### Самопроверка (мысленно, не пиши в отчёт)

Ответь себе на 7 вопросов:

1. Какой урок обязывает меня не хардкодить `C:\CODE\...` в коде модуля?
2. Какой паттерн даёт решение вопроса "как читать JSON с graceful fallback"?
3. Какой антипаттерн описывает проблему с emoji в print() на Windows?
4. Какой урок применим когда я вижу в TASK что-то похожее на Input Assembler вместо Context Orchestrator?
5. Какой паттерн использует `Path(__file__).resolve().parent.parent`?
6. Какой антипаттерн запрещает `except: pass`?
7. Какие уроки применимы для любой задачи (не только специфической)?

**Правильные ответы (проверь себя):** L-03 • P-02 • AP-06 • L-01 • P-01 • AP-03 • L-01, L-02, L-04

Если не смог ответить на 2+ вопроса — **перечитай файлы**. Понимание этих файлов критично для всех последующих задач.

---

## Часть 5 — Обновить `.gitignore` и `component_status.json`

### 5.1. `.gitignore`

В `.gitignore` **ничего не добавлять** — когнитивные файлы должны быть под git (они общая память проекта). Просто проверь что они **не попадают** под существующие exclude-правила.

Быстрая проверка:
```bash
git check-ignore LESSONS_LEARNED.md PATTERNS.md ANTIPATTERNS.md CLAUDE.md
```
Все четыре должны вернуть "не игнорируется" (обычно — пустой вывод с exit code 1).

### 5.2. `component_status.json`

Компоненты CIS V10.0-r1 не меняются (это инфраструктура процесса, не компонент системы). **Не трогать** `component_status.json` в этой задаче.

---

## Часть 6 — Тест-скрипт verify_cognitive_foundation.py

Создай файл `scripts/verify_cognitive_foundation.py`:

```python
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
        "§ 28. Как работают когнитивные файлы",
        "СТРУКТУРА КОМАНДЫ И РОЛИ",
        "LESSONS_LEARNED.md",
        "PATTERNS.md",
        "ANTIPATTERNS.md",
        "Lessons applied:",  # в шаблоне отчёта § 9
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
```

### Запуск

```bash
python scripts/verify_cognitive_foundation.py
```

Должен вывести `[PASS]`. Если `[FAIL]` — не коммитить, разбираться по списку ошибок или § 3.

---

## Часть 7 — Финальный коммит и merge

### 7.1. Проверка git-состояния

```bash
git status
```

Ожидаемые изменения:
- Modified: `CLAUDE.md`
- Added: `LESSONS_LEARNED.md`, `PATTERNS.md`, `ANTIPATTERNS.md`
- Added: `scripts/verify_cognitive_foundation.py`

**Никаких других файлов не должно быть изменено.** Если есть — § 3.

### 7.2. Pre-commit checklist (§ 24)

Пройди чеклист из CLAUDE.md § 24. Особенно:
- [ ] В коммит не попали `.env`, логи, zip, `__pycache__/`?
- [ ] Все файлы UTF-8 без BOM?
- [ ] В `verify_cognitive_foundation.py` нет emoji, только ASCII-маркеры?

### 7.3. Коммит

```bash
git add CLAUDE.md LESSONS_LEARNED.md PATTERNS.md ANTIPATTERNS.md scripts/verify_cognitive_foundation.py
git commit -m "task 01: install cognitive foundation (CLAUDE.md v3 + lessons + patterns + antipatterns)"
```

### 7.4. Merge и push

```bash
git checkout main
git merge task-01-cognitive-foundation
git push origin main
git branch -d task-01-cognitive-foundation
```

### 7.5. Архивировать TASK

```bash
git mv TASKS/ACTIVE/TASK_01_cognitive_foundation.md TASKS/COMPLETED/TASK_01_cognitive_foundation.md
git commit -m "archive TASK_01"
git push
```

---

## Часть 8 — Финальный отчёт Сергею

Пришли в чат отчёт в формате § 9 CLAUDE.md:

```
TASK_01 [cognitive_foundation] — COMPLETED

Файлы изменены: CLAUDE.md (обновлён до v3)
Файлы созданы: LESSONS_LEARNED.md, PATTERNS.md, ANTIPATTERNS.md, 
              scripts/verify_cognitive_foundation.py
Файлы удалены: none
Тесты: verify_cognitive_foundation.py — [PASS]
Commit: <hash> task 01: install cognitive foundation (CLAUDE.md v3 + lessons + patterns + antipatterns)
Merge commit: <hash>
Время работы: <минуты>

Прочитал целиком:
- LESSONS_LEARNED.md (8 уроков L-01..L-08)
- PATTERNS.md (5 паттернов P-01..P-05)
- ANTIPATTERNS.md (7 антипаттернов AP-01..AP-07)

Самопроверка Часть 4: ответы на 7 вопросов совпали с эталоном.

Ключевое что понял:
- L-01: не доверяй TASK слепо, сверяй с ТЗ при сомнении
- L-07/AP-02: никаких stub-данных в production-коде, только graceful None
- L-08/AP-04: Fast Lane никогда не ABORT
- P-01: Path(__file__).resolve().parent.parent вместо hardcoded
- AP-07: не добавлять функционал не указанный в TASK

Ideas logged: 0
Lessons applied: L-03 (P-01 в verify скрипте), L-04 (ASCII маркеры + UTF-8 reconfigure), P-05 (структура теста)
Warnings/issues: none

Готов применять когнитивную систему в следующих задачах.
Готов к TASK_02.
```

---

## Критерии готовности (acceptance criteria)

- [ ] `CLAUDE.md` в корне — версия v3 (содержит § 28 и раздел "Структура команды")
- [ ] `LESSONS_LEARNED.md` создан, содержит уроки L-01...L-08
- [ ] `PATTERNS.md` создан, содержит паттерны P-01...P-05
- [ ] `ANTIPATTERNS.md` создан, содержит антипаттерны AP-01...AP-07
- [ ] `scripts/verify_cognitive_foundation.py` создан и выдаёт `[PASS]`
- [ ] Все 4 markdown файла UTF-8 без BOM
- [ ] Файлы закоммичены в main, ветка task-01-cognitive-foundation удалена
- [ ] TASK файл перемещён из ACTIVE/ в COMPLETED/
- [ ] Отчёт в чат Сергею по формату § 9

---

## Важные предупреждения

- ⚠ **Не изменяй содержимое** CLAUDE.md / LESSONS / PATTERNS / ANTIPATTERNS самостоятельно. Эти файлы — от архитектора, твоя задача их установить дословно.
- ⚠ **Не добавляй** новые уроки / паттерны / антипаттерны от себя. § 4 (идеи → NOTES).
- ⚠ **Не изменяй** `component_status.json` в этой задаче — это инфраструктура процесса, не компонент системы.
- ⚠ **Не трогай** `TZ/`, `MARKET_MIND/` в этой задаче (кроме того что само собой подразумевается — ничего не должно там меняться).
- ⚠ Если при Самопроверке Часть 4 не смог ответить на 2+ вопроса — **не переходи к Части 5**, сначала перечитай файлы.

---

**После успешного выполнения — ждём TASK_02 (rebuild инфраструктуры MARKET_MIND до 8 канонических слоёв).**
