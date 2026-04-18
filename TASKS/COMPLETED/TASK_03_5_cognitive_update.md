# TASK_03.5 — COGNITIVE UPDATE AFTER TASK_03

**Тип:** процессная задача — обновление когнитивной системы
**Приоритет:** нужна перед TASK_04 (чтобы новые уроки применялись в следующих задачах)
**Исполнитель:** Claude Code
**Источник:** итоги TASK_03 + cleanup итераций (2026-04-18)
**Статус:** ACTIVE
**Зависимости:** TASK_03 (schema_layer v2) — ✅
**Блокирует:** TASK_04 (data_quality_gates v2)

---

## ⚠ Contract reminder

Соблюдай CLAUDE.md v4. При любом сомнении — § 3 (СТОП).

Эта задача **короткая** (~15-20 минут). Обновляет только когнитивные файлы и verify-скрипт. Никакого нового кода, никакой инфраструктуры.

---

## Контекст

За день 2026-04-18 мы накопили 4 новых урока и 1 антипаттерн из реальной работы:

- **L-17:** Cleanup tasks должны проверять внутренности канонических директорий, не только top-level legacy. Обнаружен когда в mini-audit после TASK_03 нашлись 3 legacy файла в `SCHEMAS/` которые survived TASK_00.
- **L-18:** Ad-hoc диагностика через `python -c`, `echo | python`, изолированный `grep` — AP-07 даже если команды безобидные. Три попытки за день, все отклонены.
- **L-19:** API mismatch в ad-hoc тестах (`result.success` вместо `result.ok`) — дополнительный аргумент почему ad-hoc тесты опасны. Результат теста не отражает реальное состояние кода.
- **L-20:** Security warnings от среды ("Newline followed by # inside a quoted argument", "Command too long 1373 bytes > 893") — серьёзные сигналы. Никогда не одобрять молча.
- **AP-10:** Формализация L-18 как запрещённого паттерна. Теперь в AP-10 описаны конкретные формы (`python -c`, `echo | python`, изолированный `grep`) и правила когда inline-команды допустимы.

Эти уроки оплачены сегодняшней работой. Без фиксации в файлах — забудутся и будут повторяться.

---

## Рабочая директория

`C:\CODE\MARKET ANALYSIS\`

---

## Предусловия

1. Текущая ветка — `main`, local = remote (после TASK_03 cleanup и log untrack)
2. Последние коммиты в main: `ac17dc5 chore: untrack log files`, `35d8789 archive TASK_03`, `e565e4e task 03 cleanup`, `12862fb task 03`
3. `git status` показывает **только** следующие изменения (L-09):
   - modified: `LESSONS_LEARNED.md` (preload v1.3 от архитектора)
   - modified: `ANTIPATTERNS.md` (preload v1.3 от архитектора)
   - untracked: `TASKS/ACTIVE/TASK_03_5_cognitive_update.md` (сам файл задачи)
4. `python scripts/verify_cognitive_foundation.py` возвращает `[PASS]` (пока для v4 маркеров)
5. `python scripts/pre_commit_check.py` — возвращает `[PASS]` или `[INFO] No staged files` (hook работает)
6. Локальных веток кроме `main` нет: `git branch` → только `* main`

Если любое условие не выполнено → § 3.

---

## Часть 1 — Создать ветку

```bash
cd "C:\CODE\MARKET ANALYSIS"
git checkout main
git pull origin main
git checkout -b task-03-5-cognitive-update
```

---

## Часть 2 — Проверить содержимое preload-нутых файлов v1.3

Перед коммитом — убедиться что файлы содержат действительно v1.3 маркеры.

```bash
echo "=== LESSONS_LEARNED.md v1.3 маркеры ==="
findstr /C:"## L-17:" LESSONS_LEARNED.md
findstr /C:"## L-18:" LESSONS_LEARNED.md
findstr /C:"## L-19:" LESSONS_LEARNED.md
findstr /C:"## L-20:" LESSONS_LEARNED.md
findstr /C:"v1.3" LESSONS_LEARNED.md

echo "=== ANTIPATTERNS.md v1.3 маркеры ==="
findstr /C:"## AP-10:" ANTIPATTERNS.md
findstr /C:"v1.3" ANTIPATTERNS.md
```

Все 6 findstr должны найти соответствующие маркеры. Если что-то не найдено — § 3 (preload файлы неполные).

---

## Часть 3 — Коммит обновлённых когнитивных файлов

```bash
git add LESSONS_LEARNED.md ANTIPATTERNS.md
git commit -m "task 03.5: update cognitive system with L-17, L-18, L-19, L-20, AP-10 from TASK_03"
```

Pre-commit hook должен пройти `[PASS]`. Если блокирует — § 3.

---

## Часть 4 — Обновить `scripts/verify_cognitive_foundation.py`

Расширить проверку чтобы verify валидировал v1.3 маркеры в LESSONS и ANTIPATTERNS.

### 4.1 — Прочитать текущий файл

```bash
type scripts\verify_cognitive_foundation.py | more
```

Он уже содержит проверки для v1.1 и v1.2 (добавлены в TASK_01 и TASK_02.5 соответственно).

### 4.2 — Применить точечные правки через `str_replace`

Найти в файле блок проверки LESSONS_LEARNED v1.2:

```python
# v4: проверка LESSONS_LEARNED v1.2
lessons_path = ROOT / "LESSONS_LEARNED.md"
if lessons_path.exists():
    lessons_content = lessons_path.read_text(encoding="utf-8")
    for new_lesson in ("## L-14:", "## L-15:", "## L-16:"):
        if new_lesson not in lessons_content:
            errors.append(f"LESSONS_LEARNED.md missing v1.2 entry: {new_lesson}")
    if "v1.2" not in lessons_content:
        errors.append("LESSONS_LEARNED.md missing v1.2 marker")
```

**Заменить** на расширенную версию:

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

Аналогично найти блок проверки ANTIPATTERNS v1.2:

```python
# v4: проверка ANTIPATTERNS v1.2
antipatterns_path = ROOT / "ANTIPATTERNS.md"
if antipatterns_path.exists():
    ap_content = antipatterns_path.read_text(encoding="utf-8")
    if "## AP-09:" not in ap_content:
        errors.append("ANTIPATTERNS.md missing AP-09")
    if "v1.2" not in ap_content:
        errors.append("ANTIPATTERNS.md missing v1.2 marker")
```

**Заменить** на:

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

### 4.3 — Запустить verify

```bash
python scripts/verify_cognitive_foundation.py
```

Должен вывести `[PASS]` с обновлённым количеством проверок (должны быть все v1.0, v1.1, v1.2, v1.3).

### 4.4 — Коммит

```bash
git add scripts/verify_cognitive_foundation.py
git commit -m "task 03.5: extend verify_cognitive_foundation for v1.3 markers (L-17..L-20, AP-10)"
```

Hook должен PASS.

---

## Часть 5 — Финальный merge и push

### 5.1 Проверка состояния

```bash
git log --oneline main..task-03-5-cognitive-update
# Ожидается 2 коммита:
#   <hash> task 03.5: extend verify_cognitive_foundation for v1.3 markers
#   <hash> task 03.5: update cognitive system with L-17, L-18, L-19, L-20, AP-10
```

### 5.2 Merge в main

```bash
git checkout main
git merge task-03-5-cognitive-update
# Должен быть fast-forward (без конфликтов)
```

### 5.3 Push

```bash
git push origin main
```

**Не force push** (AP-09). Обычный push.

Если push protection блокирует — STOP и сообщи. Но не должен: в новых уроках нет реальных токенов, hook уже проверил.

### 5.4 Удалить ветку

```bash
git branch -d task-03-5-cognitive-update
```

### 5.5 Архивировать TASK

```bash
git mv TASKS/ACTIVE/TASK_03_5_cognitive_update.md TASKS/COMPLETED/TASK_03_5_cognitive_update.md
git commit -m "archive TASK_03.5"
git push origin main
```

### 5.6 Финальный sync check

```bash
git fetch origin
git log --oneline origin/main..main    # должен быть пусто
git log --oneline main..origin/main    # должен быть пусто
git status                               # clean working tree
git log --oneline -5                    # последние 5 коммитов main
```

---

## Часть 6 — Финальный отчёт

По § 9 CLAUDE.md:

```
TASK_03.5 [cognitive_update] — COMPLETED

Файлы изменены: LESSONS_LEARNED.md (v1.2 → v1.3), ANTIPATTERNS.md (v1.2 → v1.3),
                scripts/verify_cognitive_foundation.py
Файлы созданы: none
Файлы удалены: none

Добавлены в когнитивку:
  - L-17 (cleanup inspect internals of canonical directories)
  - L-18 (ad-hoc diagnostics = AP-07 violation)
  - L-19 (API mismatch in ad-hoc tests, false panic potential)
  - L-20 (security warnings from environment — never approve)
  - AP-10 (ad-hoc diagnostic commands outside TASK scope)

Тесты:
  - python scripts/verify_cognitive_foundation.py — [PASS]
  - python scripts/pre_commit_check.py — [PASS]

Commits:
  - <hash> task 03.5: update cognitive system with L-17, L-18, L-19, L-20, AP-10
  - <hash> task 03.5: extend verify_cognitive_foundation for v1.3 markers
  - <hash> archive TASK_03.5

Время работы: <минуты>
Push в origin/main: успешный

Lessons applied:
  - L-09 (учёл preload-файлы в предусловиях)

Antipatterns avoided:
  - AP-07 (только изменения из TASK)
  - AP-09 (обычный push, не force)
  - AP-10 (никаких ad-hoc диагностик — только findstr/python из инструкции)

Component status updates: нет (TASK_03.5 — процессная инфраструктура, не компонент)

Cognitive system summary:
  - 19 уроков (L-01..L-20, L-12 reserved)
  - 5 паттернов (P-01..P-05)
  - 10 антипаттернов (AP-01..AP-10)

Ideas logged: 0
Warnings/issues: none

Готов к TASK_04 (data_quality_gates v2).
```

---

## Критерии готовности

- [ ] `LESSONS_LEARNED.md` v1.3 с L-17, L-18, L-19, L-20 закоммичен в main
- [ ] `ANTIPATTERNS.md` v1.3 с AP-10 закоммичен в main
- [ ] `scripts/verify_cognitive_foundation.py` расширен, возвращает `[PASS]`
- [ ] 3 коммита в main (2 content + 1 archive)
- [ ] Ветка `task-03-5-cognitive-update` удалена
- [ ] TASK файл в `COMPLETED/`
- [ ] `git status` показывает clean working tree
- [ ] `git log --oneline origin/main..main` и `main..origin/main` оба пустые

---

## Важные предупреждения

- ⚠ **Не изменяй** содержимое preload-нутых `LESSONS_LEARNED.md` и `ANTIPATTERNS.md` — они от архитектора, только закоммить как есть в Части 3 (L-09)
- ⚠ **Не трогай** другие файлы — эта задача точечная
- ⚠ **Не запускай ad-hoc команды** (`python -c`, `echo | python`, изолированный `grep`) — AP-10. Если нужна диагностика — только команды из инструкции TASK
- ⚠ **Никакого force push** (AP-09). Обычные push только
- ⚠ Если pre-commit hook где-то блокирует — разбираемся (§ 3), не обходим через `--no-verify`

---

**После успешного TASK_03.5 — переходим к TASK_04 (data_quality_gates v2).**

TASK_04 будет писать архитектор утром и положит в чат. Запускать TASK_04 только **после** закрытия TASK_03.5.
