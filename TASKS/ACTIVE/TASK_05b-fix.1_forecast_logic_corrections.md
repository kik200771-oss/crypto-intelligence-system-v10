# TASK_05b-fix.1 — Исправления отклонений от спецификации TASK_05b

**Версия:** v1
**Дата:** 2026-04-22
**Автор:** Claude Opus (архитектор)
**Исполнитель:** Claude Code
**Зависит от:** TASK_05b (COMPLETED, commit `372e858` + archive `3f8bd56`)
**Блокирует:** TASK_05c

**Pre-task analysis required: NO** (точечный fix-forward, scope ясен)

---

## 1. Контекст

### Что случилось

TASK_05b был выполнен и закоммичен в main (commit `372e858`). Post-commit verification через Channel 1 (`git show HEAD:...`) выявила 4 отклонения от спецификации:

1. **CRITICAL — ABORTED статус в Slow Lane** (строка 379 в `_build_forecast_context`). Противоречит TASK_05b секция 4 шаг 13: "*status: OK или DEGRADED — никогда ABORTED*".

2. **HIGH — Placeholder `conflict_flag=True`** (строка 312). При наличии UP паттерна `conflict_flag` всегда `True`, без реальной проверки KB. Это AP-02 violation (fake data вместо честного "not determined"). ТЗ требует два условия: KB conflicting + pattern UP; код проверяет только второе.

3. **MEDIUM — AXM Guard checks неверной природы**. ТЗ § 1.20: AXM — epistemic/causal guardrail про axioms of market mechanics (order flow, liquidity, causal consistency). В коде Check 2 — это input validation ("symbol in context"), Check 3 — data quality (timestamp not future). Эти проверки не относятся к AXM scope.

4. **LOW — Недопокрытие тестов**. По спеке 15 forecast тестов, по факту 14. Fast Lane Invariant тесты объединены в один `test_fast_lane_invariant_never_aborted` вместо раздельных 1h и 4h. Снижает diagnostic granularity.

### Корень CRITICAL проблемы — спецификационная двусмысленность

Проблема 1 — частично моя вина. L-08 текст в LESSONS_LEARNED:
> *"ABORT допустим только в Slow Lane (24h / research), где latency не критична."*

Эта формулировка была про **Model Core aggregation** (Math Model v6.3 раздел 7), где ABORT возможен при нарушении BINDING RULE aggregation. Но она была **переинтерпретирована** как разрешение ABORTED в Context Orchestrator forecast context — что неверно.

Context Orchestrator forecast context **никогда не должен возвращать ABORTED** — ни в Fast Lane, ни в Slow Lane. Slow Lane может быть медленнее, может пропускать больше блоков, но итоговый `ContextResult.status` — это `OK` или `DEGRADED`.

Эта задача также **обновляет L-08** для устранения ambiguity на будущее.

### Что исправляем в этом TASK

- 4 точечных fix в `context_orchestrator.py` (~30-40 строк изменений)
- 1 обновление тестов (split одного теста на 2-3 + add new test) (~20 строк)
- 1 обновление L-08 в LESSONS_LEARNED.md (~3-5 строк)
- Commit + push + archive

### Что НЕ делаем

- НЕ трогаем `_collect_*` методы — они правильные (P-02 compliance подтверждён)
- НЕ трогаем ThreadPoolExecutor logic — работает
- НЕ переименовываем existing тесты — только splitting одного + adding new
- НЕ обновляем `component_status.json` (всё ещё `not_started`, ждёт TASK_05c)

---

## 2. Предусловия

**Предусловие 1 — git status чистый.** После archive commit `3f8bd56` working tree clean. `git status` показывает только этот TASK файл в `TASKS/ACTIVE/` как untracked.

**Предусловие 2 — TASK_05b код на диске.**
- `ls MARKET_MIND/ENGINE/context_orchestrator.py` — existsEqually
- `python MARKET_MIND/tests/test_context_orchestrator.py` — `[PASS] 21/21 tests passed`

**Предусловие 3 — LESSONS_LEARNED v1.5 с L-08.** 
- `grep "^## L-08" LESSONS_LEARNED.md` — найдено
- Текст L-08 содержит фразу "ABORT допустим только в Slow Lane"

---

## 3. Части задачи

### Часть 1 — Diagnostic cat (baseline)

Перед правками — покажи **текущее** содержимое критических секций для baseline.

1. `cat MARKET_MIND/ENGINE/context_orchestrator.py | head -50` — начало файла (docstring + imports + constants)

2. Покажи **полный** блок `_build_forecast_context` — выведи через sed с номерами строк или через `awk`:
```
awk 'NR>=180 && NR<=400' MARKET_MIND/ENGINE/context_orchestrator.py
```
(Или через твой интерфейс — любой способ который даёт raw output примерно строк 180-400. Если awk не работает — `sed -n '180,400p'`. Если sed не работает — весь `cat` целиком, я найду секцию сам.)

**⚠ Внимание:** если среда триггернёт warning на `sed` (L-23 — sed compound triggers security warning) — **§ 3 STOP**, не одобряй. Используй `awk` вместо. Если оба triggers — используй `head -400 | tail -220` как compound-fallback. Если и это triggers — просто `cat` целиком.

3. Покажи `_invoke_axm_guard` отдельно — `awk 'NR>=XXX && NR<=YYY'` где XXX-YYY найдёшь через `grep -n "_invoke_axm_guard" MARKET_MIND/ENGINE/context_orchestrator.py`.

Цель: подтвердить что я вижу ту же картину что раньше, и что номера строк в моей diagnosis совпадают с реальным файлом.

**Критерии готовности Часть 1:**
- Я получил raw output одной из команд которая показывает `_build_forecast_context` в полноте
- Я получил raw output который показывает `_invoke_axm_guard` в полноте
- Никаких правок файла ещё не сделано

---

### Часть 2 — Fix 1: убрать ABORTED в Slow Lane

**Цель:** привести status logic в соответствие со спецификацией — status всегда `OK` или `DEGRADED` в `_build_forecast_context`, никогда `ABORTED`.

**Локация проблемы:** в `_build_forecast_context`, block "Status determination - applies L-08 Fast Lane Invariant", Slow Lane ветка.

**Текущий код** (по строкам ~371-385, из моего Channel 1 анализа):
```
if is_fast:
    # Fast Lane никогда не возвращает ABORTED - L-08
    if context_degraded:
        status = "DEGRADED"
    else:
        status = "OK"
else:
    # Slow Lane может возвращать ABORTED при критических ошибках
    missing_required = [name for name, _ in required_fast_sources if name not in collected_data]
    if len(missing_required) >= 2:  # Threshold: 2+ missing required sources
        status = "ABORTED"
    elif context_degraded:
        status = "DEGRADED"
    else:
        status = "OK"
```

**Целевое поведение:**
```
# Status determination — applies L-08 (updated)
# Context Orchestrator forecast context — никогда ABORTED, ни в одной lane.
# ABORT применим только в Model Core aggregation (Math Model v6.3 раздел 7), не здесь.
if context_degraded:
    status = "DEGRADED"
else:
    status = "OK"
```

**Как делать:**

1. Используй `str_replace` или Edit tool для точечной замены секции `# Status determination ...` до конца if-else блока (включая комментарий "Slow Lane никогда ABORTED ...")
2. Новый блок не имеет разветвления на Fast/Slow Lane — общий status determination
3. Комментарий обновлён на явную ссылку что ABORTED — domain Model Core, не Context Orchestrator

**Критерии готовности Часть 2:**
- `grep -n 'status = "ABORTED"' MARKET_MIND/ENGINE/context_orchestrator.py` — **пусто**
- `grep -n "missing_required" MARKET_MIND/ENGINE/context_orchestrator.py` — **пусто** (вспомогательная переменная больше не нужна)
- Логика: при любом сценарии status is either `"OK"` or `"DEGRADED"`

---

### Часть 3 — Fix 2: убрать placeholder conflict_flag

**Цель:** заменить fake placeholder `conflict_flag=True` на честную минимальную реализацию — `False` когда KB недоступен.

**Локация проблемы:** в `_build_forecast_context`, block "Conflict Exposure check (ТЗ Задача 3)".

**Текущий код** (строки ~303-315):
```
# Conflict Exposure check (ТЗ Задача 3)
conflict_flag = False
if "patterns" in collected_data and collected_data["patterns"]:
    # Минимальная Conflict Exposure логика
    patterns = collected_data["patterns"]
    if any(pattern.get("direction") == "UP" for pattern in patterns):
        # В реальной системе здесь был бы полноценный KB lookup
        # В TASK_05b делаем placeholder check
        conflict_flag = True  # Placeholder - всегда conflicting for testing

context_data["conflict_flag"] = conflict_flag
```

**Целевое поведение:**
```
# Conflict Exposure check (ТЗ Задача 3)
# ТЗ: conflict_flag = True если KB conflicting + pattern UP.
# Минимальная реализация TASK_05b-fix.1: без KB access возвращаем False (честно "not determined").
# Полная реализация с KB search — TASK_05c.
conflict_flag = False
context_data["conflict_flag"] = conflict_flag
```

**Ключевое изменение:**
- Убрать любые условия которые устанавливают `conflict_flag = True` в этой минимальной реализации
- Добавить комментарий про TASK_05c для полной реализации
- Патерн "minimal honest implementation без KB" — consistent с P-02 философией (лучше None/False чем fake True)

**Критерии готовности Часть 3:**
- `grep -n "conflict_flag = True" MARKET_MIND/ENGINE/context_orchestrator.py` — **пусто**
- `grep -n "Placeholder" MARKET_MIND/ENGINE/context_orchestrator.py` — **пусто** (убрали комментарий-placeholder)
- `conflict_flag` всегда `False` в output для TASK_05b-fix.1

---

### Часть 4 — Fix 3: переделать AXM Guard checks

**Цель:** заменить 3 существующих check'а на 2-3 check'а которые действительно про axioms of market mechanics (не input validation и не data quality).

**Локация проблемы:** метод `_invoke_axm_guard` целиком.

**Контекст по ТЗ § 1.20:**

> AXM в V9.1 функционирует как epistemic/causal guardrail layer. AXM_001, AXM_002, AXM_004, AXM_008 опираются на концепции order flow, taker side, bid/ask dynamics — данных которых нет в текущем Feature Store.

> BINDING RULE: AXM применяется исключительно как post-scoring epistemic check. Если объяснение нарушает AXM → epistemic_risk_flag, confidence_point и score не изменяются.

**Целевые checks** (все на основе уже доступных данных — patterns, regime, features):

**Check 1 — Pattern-Regime Consistency:**
- Если `regime.regime_type == "R4"` (HARD brake) и среди patterns есть direction=UP или direction=DOWN → `epistemic_risk_flag = True`, reason "patterns proposed during hard-brake regime violates determinism contract"
- Obоснование: в R4 модель замораживает decisions (Math Model v6.3 раздел 3: R4 "Hard Brake", `A4[m,q]=-0.20 direction suppressed`). Паттерны которые предлагают direction во время R4 — epistemic inconsistency.

**Check 2 — Pattern Direction Consistency:**
- Если patterns имеет смешанные направления (и UP и DOWN одновременно в одной коллекции) → `epistemic_risk_flag = True`, reason "conflicting pattern directions at same timeframe"
- Обоснование: на одном таймфрейме логически не могут существовать валидные UP и DOWN patterns одновременно без additional context. Это сигнал что один из них — noise.

**Check 3 (optional, добавить если просто) — Volume-Pattern Plausibility:**
- Если features.volume_indicator доступен и < 0.1 (очень низкая ликвидность) + patterns существуют → `epistemic_risk_flag = True`, reason "patterns proposed with low liquidity (potential noise)"
- Это proxy для AXM_004 (liquidity depletion) до момента когда microstructure данные появятся

**Общий формат return (не меняется):**
```
{
    "epistemic_risk_flag": bool,
    "axm_notes": list[str],  # non-empty only if flag=True или checks performed
    "axm_checks_performed": list[str]  # имена выполненных checks
}
```

**Что НЕ делать:**
- Не модифицировать confidence/direction/score (ТЗ § 1.20)
- Не raises — при любой inner ошибке `epistemic_risk_flag = True` + note + `axm_guard_completed = False` в возвращаемом dict
- Не убирать **сигнатуру** метода — она сохраняется `_invoke_axm_guard(self, context_data, symbol, timeframe)`

**Дополнительно — сигнатура метода:**

Для context_data проверки AXM Guard нужен доступ к collected `patterns`, `regime`, `features`. Они уже в `context_data` после `context_data.update(collected_data)`.

В текущем коде AXM Guard получает `context_data` через параметр — оставляем как есть. Просто меняется логика внутри.

**Критерии готовности Часть 4:**
- Метод `_invoke_axm_guard` содержит 2-3 check'а описанные выше
- Не содержит check про "symbol in required_keys" (это было input validation, не AXM)
- Не содержит check про "timestamp > current_time + 3600" (это было data quality)
- Возвращаемая структура совместима с текущими тестами (epistemic_risk_flag, axm_notes ключи сохранены)
- Check 1 (Pattern-Regime Consistency) **явно** проверяет `regime.regime_type == "R4"` — это самый важный check, не пропустить

---

### Часть 5 — Fix 4: расширить тесты

**Цель:** split existing test + добавить 1-2 новых теста для улучшения coverage.

**Текущее состояние тестов:** 7 skeleton + 14 forecast = 21.

**Целевое состояние:** 7 skeleton + 16 forecast = 23.

**Изменения в `test_context_orchestrator.py`:**

**Изменение 1: Split `test_fast_lane_invariant_never_aborted`**

Существующий тест проверяет что в Fast Lane никогда не возвращается ABORTED. По имени звучит как один monolithic test. Разделить на:

- `test_fast_lane_invariant_1h_never_aborted` — explicit assertion для timeframe="1h"
- `test_fast_lane_invariant_4h_never_aborted` — explicit assertion для timeframe="4h"

Каждый тест:
1. Создаёт `ContextOrchestrator` с temp директорией (все источники будут None)
2. Вызывает `orchestrator.build_context("test query", "BTCUSDT", <timeframe>)`
3. Assert `result.status != "ABORTED"`
4. Assert `result.status in ["OK", "DEGRADED"]`
5. Assert `result.context_degraded == True` (потому что все источники None)

**Изменение 2: Добавить `test_slow_lane_never_aborted_either`**

**Это новый тест**, критически важный после Fix 1. Проверяет что Slow Lane (1d) тоже не возвращает ABORTED.

Структура:
1. Создаёт `ContextOrchestrator` с temp директорией
2. Вызывает `orchestrator.build_context("test query", "BTCUSDT", "1d")`
3. Assert `result.status != "ABORTED"` — **это главный assertion**, проверяет Fix 1
4. Assert `result.status in ["OK", "DEGRADED"]`
5. Assert `result.context_degraded == True`

**Изменение 3 (optional, если просто добавляется): Добавить `test_conflict_flag_false_without_kb`**

Проверяет Fix 2 — что `conflict_flag` всегда False при отсутствии KB.

Структура:
1. Создаёт `ContextOrchestrator` с pre-populated patterns (patterns with direction=UP)
2. Вызывает `build_context(...)`
3. Parse context string или inspect `result.context` — убедиться что `conflict_flag = True` **не появляется** (в TASK_05b-fix.1 это не ожидается)
4. Или: если блок `[CONFLICT EXPOSURE]` появляется в context — fail

**Примечание по Изменению 3:** если сложно сделать через black-box test (parsing context string) — можно опустить, оставить 2 изменения. Тогда final count: 7 skeleton + 15 forecast = 22.

**Runner обновить:** `tests` list в `run_all_tests` (если использует такой паттерн) должен включать новые тесты. Или если используется pattern с разделением на `skeleton_tests` и `forecast_tests` lists — добавить в forecast_tests.

**Критерии готовности Часть 5:**
- `python MARKET_MIND/tests/test_context_orchestrator.py` → `[PASS] 23/23 tests passed` (или 22/22 если опустить Изменение 3)
- Raw output теста содержит строки `[OK] test_fast_lane_invariant_1h_never_aborted` и `[OK] test_fast_lane_invariant_4h_never_aborted` как отдельные
- Присутствует `[OK] test_slow_lane_never_aborted_either`

---

### Часть 6 — Обновление L-08 в LESSONS_LEARNED.md

**Цель:** устранить ambiguity в текущей формулировке L-08.

**Текущее состояние L-08** (по памяти, подтверди через `cat`):

Секция "Правильный подход" содержит фразу:
> *"ABORT допустим **только** в Slow Lane (24h / research), где latency не критична."*

Эта формулировка относилась к Model Core aggregation (Math Model v6.3 раздел 7), но была **переинтерпретирована** в TASK_05b как разрешение на ABORTED в Context Orchestrator forecast context.

**Как делать:**

1. `grep -n "ABORT допустим" LESSONS_LEARNED.md` — найти точную строку
2. Прочитать контекст (5-10 строк вокруг)
3. Точечный `str_replace` на обновлённый текст:

**Старая формулировка** (то что грепать):
```
ABORT допустим **только** в Slow Lane (24h / research), где latency не критична.
```

**Новая формулировка** (что поставить на место):
```
**Scope уточнение (TASK_05b-fix.1, 2026-04-22):**

ABORT применим **только** к Model Core aggregation (Math Model v6.3 раздел 7, BINDING RULE aggregation) при невозможности собрать обязательные входы в timeout.

ABORT **не применим** к Context Orchestrator forecast context — `ContextResult.status` всегда либо `"OK"` либо `"DEGRADED"`, независимо от lane. Это уточнение сделано после incident в TASK_05b где формулировка "ABORT допустим в Slow Lane" была переинтерпретирована как разрешение ABORTED в `_build_forecast_context` Slow Lane branch — что привело к дополнительному fix TASK.

Оригинальная формулировка "ABORT допустим только в Slow Lane" — verbatim остаётся актуальной для **aggregation level** (Model Core), но **не** для Context Orchestrator.
```

**Критерии готовности Часть 6:**
- Обновлённый текст присутствует в L-08
- `grep -n "TASK_05b-fix.1" LESSONS_LEARNED.md` — найдена ссылка на эту задачу
- Общая структура урока L-08 (Когда возникло / Категория / Симптом / Причина / Правильный подход / Правило / Применимость) сохранена
- В таблице "История обновлений" добавить строку про изменение L-08 (но **не** увеличивать счётчик уроков — это clarification existing, не new lesson)

---

### Часть 7 — Pre-commit check + L-24 checkpoint (staging + diff --cached)

Применение L-24 как в TASK_05a-fix.5.

1. `python scripts/pre_commit_check.py` — пришли полный stdout
2. `git status` — raw output
3. `git add MARKET_MIND/ENGINE/context_orchestrator.py`
4. `git add MARKET_MIND/tests/test_context_orchestrator.py`
5. `git add LESSONS_LEARNED.md`
6. `git add TASKS/ACTIVE/TASK_05b-fix.1_forecast_logic_corrections.md`
7. `git status` — raw output (все 4 файла в staged)
8. `git diff --cached --stat` — raw output
9. `git diff --cached MARKET_MIND/ENGINE/context_orchestrator.py` — **полный** diff (ключевой файл)
10. `git diff --cached LESSONS_LEARNED.md` — **полный** diff
11. `git diff --cached MARKET_MIND/tests/test_context_orchestrator.py` — **полный** diff

**ОСТАНОВИСЬ после шага 11 и жди моего подтверждения.**

Я проверю:
- В context_orchestrator.py: отсутствие `status = "ABORTED"`, отсутствие `conflict_flag = True` в коде, AXM Guard новые checks
- В тестах: +2 новых теста (split + slow_lane_never_aborted)
- В LESSONS_LEARNED: обновление L-08 с ссылкой на TASK_05b-fix.1

Только после моего подтверждения — Часть 8.

---

### Часть 8 — Commit + push + PA-08 verification + archive

1. `git commit -m "task 05b-fix.1: remove ABORTED in slow lane + honest conflict_flag + AXM checks + L-08 clarification"` — raw output
2. `git show --stat HEAD` — raw output (PA-08 Channel 1)
3. `git push origin main` — **полный** raw output
4. `git mv TASKS/ACTIVE/TASK_05b-fix.1_forecast_logic_corrections.md TASKS/COMPLETED/TASK_05b-fix.1_forecast_logic_corrections.md`
5. `git commit -m "task 05b-fix.1: archive to completed"`
6. `git push origin main`
7. `git status` — должно быть clean

Финальный § 9 отчёт: короткий формат + short Reflection Block.

---

## 4. Формат финального отчёта

```
TASK_05b-fix.1 [Forecast Logic Corrections] — COMPLETED

Файлы изменены:
  - MARKET_MIND/ENGINE/context_orchestrator.py (4 точечных fix: ABORTED, conflict_flag, AXM checks, Slow Lane status logic)
  - MARKET_MIND/tests/test_context_orchestrator.py (+2 теста: split Fast Lane Invariant, add Slow Lane test)
  - LESSONS_LEARNED.md (обновление L-08 с TASK_05b-fix.1 clarification)

Файлы перемещены:
  - TASKS/ACTIVE/TASK_05b-fix.1_*.md → TASKS/COMPLETED/

Тесты: 23/23 passed (7 skeleton + 16 forecast) [или 22/22 если Изменение 3 опущено]
Commit (main): <hash> task 05b-fix.1: remove ABORTED in slow lane + ...
Commit (archive): <hash> task 05b-fix.1: archive to completed
Время работы: <минуты>

Git verification (L-24 + PA-08 Channel 1):
<первые 20 строк git show --stat HEAD>

Verification greps:
  - `grep -n 'status = "ABORTED"'` → пусто ✓
  - `grep -n 'conflict_flag = True'` → пусто ✓

Lessons applied: L-01, L-07, L-08 (updated), L-22 (сверил уроки перед отчётом), L-24 (git diff --cached checkpoint), L-25 (PA-08 Channel 1 post-commit)

=== REFLECTION BLOCK (короткий) ===

## Observations from this task
<1-3 пункта — особенно про опыт fix-forward после отклонений TASK_05b>

## Self-critique
<1-2 пункта>

=== END REFLECTION BLOCK ===

Готов к TASK_05c.
```

---

## 5. Важные предупреждения

### 5.1 Это fix-forward, не re-implementation

Scope узкий: 4 точечных fix + L-08 update. **Не** переписывать всё `_build_forecast_context`, **не** менять работающие `_collect_*` методы, **не** трогать ThreadPoolExecutor logic.

Если чувствуешь соблазн "а заодно переписать Y для чистоты" — § 3 STOP. Scope creep превращает fix в re-do.

### 5.2 Applied lessons 05b-fix.1

- **L-24** — git diff --cached как обязательный checkpoint (Часть 7)
- **L-25 (PA-08)** — post-commit verification через git show HEAD (Часть 8)
- **L-22** — сверка номеров уроков с LESSONS_LEARNED перед финальным отчётом

### 5.3 L-23 commands по одной

Все git команды одной строкой. При необходимости sed/awk для выборочного просмотра файлов — попробуй сначала `awk` (у нас не было прецедента проблем с awk), затем другие. Если среда триггернёт warning на любую команду — § 3 STOP.

### 5.4 Не делать post-commit web_fetch на raw.github (L-25)

В Часть 8 post-commit verification — через `git show --stat HEAD` (Channel 1), **не** через raw.github. L-25 cache TTL 15-30 минут, и мы только что коммитим.

### 5.5 Не обновлять component_status.json

`context_orchestrator.status` всё ещё `not_started` — модуль функционален в forecast режиме, но research/monitoring/postmortem `NotImplementedError`. Статус `ready` меняется **только** после TASK_05c (и скорее всего после ещё одной verification итерации).

### 5.6 Timestamp в git коммитах

Заметил в TASK_05b commit что git указал `Date: Wed Apr 22 19:01:15 2026 +0300`. Это **локальное время** машины Сергея — не проблема, но если будешь видеть timestamps в отчётах — используй ISO формат или локальное время Сергея, не мой UTC.

---

## 6. Ожидаемые метрики

- **Размер изменений в `context_orchestrator.py`:** ~40-60 строк (измененные + удалённые)
- **Размер изменений в `test_context_orchestrator.py`:** +20-30 строк (2 новых + refactor runner)
- **Размер изменений в `LESSONS_LEARNED.md`:** +5-10 строк (обновление L-08)
- **Время Claude Code:** 30-45 минут (8 Частей, но большинство короткие)
- **Approvals:** ~15-20 (git commands + pip check + sed/awk/cat)
- **Commits:** 2 (main + archive)

---

**Конец TASK_05b-fix.1.**

После завершения этого TASK:
- TASK_05b архитектурно соответствует спецификации
- L-08 не имеет ambiguity
- TASK_05c может начинаться с clean baseline
