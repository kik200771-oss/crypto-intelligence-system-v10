# TASK_04.5 — COGNITIVE UPDATE AFTER TASK_04

**Тип:** процессная задача — обновление когнитивной системы
**Приоритет:** нужна перед TASK_05 (чтобы новые уроки применялись в следующих задачах)
**Исполнитель:** Claude Code
**Источник:** итоги TASK_04 (2026-04-19) + процесс-наблюдения по debug_outlier.py / неточные lessons в отчёте / security warning с redirection
**Статус:** ACTIVE
**Зависимости:** TASK_04 (data_quality_monitor v2) — ✅
**Блокирует:** TASK_05 (context_orchestrator v2)

---

## ⚠ Contract reminder

Соблюдай CLAUDE.md v4. При любом сомнении — § 3 (СТОП).

Эта задача **короткая** (~15-20 минут). Обновляет только когнитивные файлы и verify-скрипт. Никакого нового кода, никакой инфраструктуры.

---

## Контекст

За TASK_04 (2026-04-19) накопилось 3 новых урока и расширение существующего антипаттерна:

- **L-21:** debug_*.py скрипты как обход AP-10. Реальный случай: `debug_outlier.py` попал в коммит `4a09703` в main, не удаляем (force push запрещён AP-09). Остаётся как постоянный артефакт-напоминание.
- **L-22:** Номера уроков в § 9 отчётах часто подтягиваются по памяти с ошибками. В отчёте TASK_04 5 из 7 ссылок на уроки были неправильные (L-05 был назван "graceful degradation", хотя это про токены; L-12 — "explicit logging", хотя это RESERVED номер, etc.).
- **L-23:** Compound commands с `cd` + output redirection (`2>/dev/null`) триггерят новую форму security warning от среды ("path resolution bypass"). Архитектор должен избегать таких конструкций в инструкциях.
- **AP-10 расширен:** теперь явно покрывает Form A (inline команды), Form B (debug_*.py, check_*.py, explore_*.py файлы) и Form C (canon location violations — файлы не в канонических местах).

Эти уроки оплачены TASK_04 работой. Без фиксации в файлах — забудутся и будут повторяться.

---

## Рабочая директория

`C:\CODE\MARKET ANALYSIS\`

---

## Предусловия

1. Текущая ветка — `main`, local = remote (после TASK_04 + archive + cleanup)
2. Последние 3 коммита в main через `git log --oneline -3`:
   - `557428c` chore: remove debug_outlier.py
   - `59a9c24` archive TASK_04
   - `4a09703` task 04: data quality monitor with 6 gates...
3. `git status` показывает **только** следующие изменения (L-09):
   - modified: `LESSONS_LEARNED.md` (preload v1.4 от архитектора)
   - modified: `ANTIPATTERNS.md` (preload v1.4 от архитектора)
   - untracked: `TASKS/ACTIVE/TASK_04_5_cognitive_update.md` (сам файл задачи)
4. `python scripts/verify_cognitive_foundation.py` возвращает `[PASS]` (текущая v1.3 проверка)
5. `python scripts/pre_commit_check.py` возвращает `[PASS]` или `[INFO] No staged files`
6. `python MARKET_MIND/tests/test_schema_validator.py` — 17/17 PASS
7. `python MARKET_MIND/tests/test_data_quality_monitor.py` — 27/27 PASS
8. Локальных веток кроме `main` нет: `git branch` → только `* main`

Если любое условие не выполнено → § 3.

---

## Часть 1 — Создать ветку

```bash
cd "C:\CODE\MARKET ANALYSIS"
git checkout main
git pull origin main
git checkout -b task-04-5-cognitive-update
```

---

## Часть 2 — Проверить содержимое preload-нутых файлов v1.4

Перед коммитом — убедиться что файлы содержат маркеры v1.4.

```bash
cd "C:\CODE\MARKET ANALYSIS"

echo "=== LESSONS_LEARNED.md v1.4 маркеры ==="
findstr /C:"## L-21:" LESSONS_LEARNED.md
findstr /C:"## L-22:" LESSONS_LEARNED.md
findstr /C:"## L-23:" LESSONS_LEARNED.md
findstr /C:"v1.4" LESSONS_LEARNED.md

echo "=== ANTIPATTERNS.md v1.4 маркеры ==="
findstr /C:"Форма B" ANTIPATTERNS.md
findstr /C:"debug_*.py" ANTIPATTERNS.md
findstr /C:"4a09703" ANTIPATTERNS.md
findstr /C:"v1.4" ANTIPATTERNS.md
```

Все 8 findstr должны найти маркеры. Если что-то не найдено → § 3 (preload файлы неполные).

---

## Часть 3 — Коммит обновлённых когнитивных файлов

```bash
cd "C:\CODE\MARKET ANALYSIS"
git add LESSONS_LEARNED.md ANTIPATTERNS.md
git commit -m "task 04.5: update cognitive system with L-21, L-22, L-23 and AP-10 extension from TASK_04"
```

Pre-commit hook должен пройти `[PASS]`. Если блокирует — § 3.

---

## Часть 4 — Обновить `scripts/verify_cognitive_foundation.py`

Расширить проверку чтобы verify валидировал v1.4 маркеры.

### 4.1 — Прочитать текущий файл

```bash
type scripts\verify_cognitive_foundation.py
```

Он уже содержит проверки для v1.1, v1.2, v1.3 (TASK_01, TASK_02.5, TASK_03.5).

### 4.2 — Применить точечные правки через `str_replace`

Найти в файле блок проверки LESSONS_LEARNED v1.3:

```python
# v4: проверка LESSONS_LEARNED v1.2 + v1.3
lessons_path = ROOT / "LESSONS_LEARNED.md"
if lessons_path.exists():
    lessons_content = lessons_path.read_text(encoding="utf-8")
    # v1.2 уроки
    for new_lesson in ("## L-14:", "## L-15:", "## L-16:"):
        if new_lesson not in lessons_content:
            errors.append(f"LESSONS_LEARNED.md missing v1.2 entry: {new_lesson}")
    # v1.3 уроки (новые из TASK_03)
    for new_lesson in ("## L-17:", "## L-18:", "## L-19:", "## L-20:"):
        if new_lesson not in lessons_content:
            errors.append(f"LESSONS_LEARNED.md missing v1.3 entry: {new_lesson}")
    # Должна быть последняя версия
    if "v1.3" not in lessons_content:
        errors.append("LESSONS_LEARNED.md missing v1.3 marker")
```

**Заменить** на расширенную версию:

```python
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
```

Аналогично найти блок проверки ANTIPATTERNS v1.3:

```python
# v4: проверка ANTIPATTERNS v1.2 + v1.3
antipatterns_path = ROOT / "ANTIPATTERNS.md"
if antipatterns_path.exists():
    ap_content = antipatterns_path.read_text(encoding="utf-8")
    if "## AP-09:" not in ap_content:
        errors.append("ANTIPATTERNS.md missing AP-09")
    if "## AP-10:" not in ap_content:
        errors.append("ANTIPATTERNS.md missing AP-10")
    if "v1.3" not in ap_content:
        errors.append("ANTIPATTERNS.md missing v1.3 marker")
```

**Заменить** на:

```python
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
```

### 4.3 — Запустить verify

```bash
python scripts/verify_cognitive_foundation.py
```

Должен вывести `[PASS]` с обновлёнными v1.4 проверками.

### 4.4 — Коммит

```bash
git add scripts/verify_cognitive_foundation.py
git commit -m "task 04.5: extend verify_cognitive_foundation for v1.4 markers (L-21..L-23, AP-10 v1.4)"
```

Hook должен PASS.

---

## Часть 5 — Финальный merge и push

### 5.1 Проверка состояния

```bash
cd "C:\CODE\MARKET ANALYSIS"
git log --oneline main..task-04-5-cognitive-update
```

Ожидается 2 коммита:
- `<hash>` task 04.5: extend verify_cognitive_foundation for v1.4 markers
- `<hash>` task 04.5: update cognitive system with L-21, L-22, L-23...

### 5.2 Merge в main

```bash
git checkout main
git merge task-04-5-cognitive-update
```

Fast-forward ожидается.

### 5.3 Push

```bash
git push origin main
```

**Не force push** (AP-09). Обычный push.

### 5.4 Удалить ветку

```bash
git branch -d task-04-5-cognitive-update
```

### 5.5 Архивировать TASK

```bash
git mv TASKS/ACTIVE/TASK_04_5_cognitive_update.md TASKS/COMPLETED/TASK_04_5_cognitive_update.md
git commit -m "archive TASK_04.5"
git push origin main
```

### 5.6 Финальный sync check

```bash
git fetch origin
git log --oneline origin/main..main
git log --oneline main..origin/main
git status
git log --oneline -5
```

Оба git log должны быть пустыми. Working tree clean.

---

## Часть 6 — Финальный отчёт

По § 9 CLAUDE.md. **Важно по L-22:** перед указанием уроков — сверься с `LESSONS_LEARNED.md` или используй "L-??" placeholder если не уверен.

```
TASK_04.5 [cognitive_update] — COMPLETED

Файлы изменены:
  - LESSONS_LEARNED.md (v1.3 → v1.4)
  - ANTIPATTERNS.md (v1.3 → v1.4 с расширенным AP-10)
  - scripts/verify_cognitive_foundation.py (добавлены v1.4 проверки)

Файлы созданы: none
Файлы удалены: none

Добавлены в когнитивку:
  - L-21 (debug_*.py scripts = AP-10 through file form)
  - L-22 (lesson numbers in § 9 reports — verify or use L-?? placeholder)
  - L-23 (compound commands with cd + output redirection trigger new security warnings)
  - AP-10 extended (Form A inline commands, Form B debug files, Form C canon location violations)

Тесты:
  - python scripts/verify_cognitive_foundation.py — [PASS]
  - python scripts/pre_commit_check.py — [PASS] (или [INFO] No staged files)

Commits:
  - <hash1> task 04.5: update cognitive system with L-21, L-22, L-23 and AP-10 extension
  - <hash2> task 04.5: extend verify_cognitive_foundation for v1.4 markers
  - <hash3> archive TASK_04.5

Время работы: <минуты>
Push в origin/main: успешный

Lessons applied:
  - L-09 (учёл preload-файлы в предусловиях)
  - L-22 (сверился с LESSONS_LEARNED.md перед составлением этого отчёта)

Antipatterns avoided:
  - AP-07 (только изменения из TASK)
  - AP-09 (обычный push, не force)
  - AP-10 (никаких ad-hoc команд или debug-файлов)

Component status updates: нет (TASK_04.5 — процессная инфраструктура, не компонент)

Cognitive system summary:
  - 22 урока (L-01..L-23, L-12 reserved)
  - 5 паттернов (P-01..P-05)
  - 10 антипаттернов (AP-01..AP-10, AP-10 в форме v1.4 покрывает все 3 формы)

Ideas logged: 0
Warnings/issues: none

Готов к TASK_05 (context_orchestrator v2) — последняя задача MDC-тройки.
```

---

## Критерии готовности

- [ ] `LESSONS_LEARNED.md` v1.4 с L-21, L-22, L-23 закоммичен в main
- [ ] `ANTIPATTERNS.md` v1.4 с расширенным AP-10 (Форма B, C) закоммичен в main
- [ ] `scripts/verify_cognitive_foundation.py` расширен, возвращает `[PASS]`
- [ ] 3 коммита в main (2 content + 1 archive)
- [ ] Ветка `task-04-5-cognitive-update` удалена
- [ ] TASK файл в `COMPLETED/`
- [ ] `git status` показывает clean working tree
- [ ] `git log --oneline origin/main..main` и `main..origin/main` оба пустые

---

## Важные предупреждения

- ⚠ **Не изменяй** содержимое preload-нутых `LESSONS_LEARNED.md` и `ANTIPATTERNS.md` — они от архитектора, только закоммить как есть (L-09)
- ⚠ **Не создавай debug_*.py или любые другие ad-hoc файлы** — теперь это явно AP-10 (Форма B). Эта задача **впервые** применяется с расширенным AP-10.
- ⚠ **Никаких ad-hoc `python -c`** (AP-10 Форма A). Если сомневаешься в чём-то — § 3.
- ⚠ **Никакого force push** (AP-09)
- ⚠ Если pre-commit hook где-то блокирует — разбираемся (§ 3), не обходим через `--no-verify`
- ⚠ При составлении финального отчёта (Часть 6) — **применяй L-22**: сверяйся с LESSONS_LEARNED.md перед указанием номеров уроков, или используй "L-??" для неуверенных ссылок

---

**После успешного TASK_04.5 — переходим к TASK_05 (context_orchestrator v2) для завершения MDC-тройки.**

TASK_05 будет писать архитектор. Запускать TASK_05 только **после** закрытия TASK_04.5.
