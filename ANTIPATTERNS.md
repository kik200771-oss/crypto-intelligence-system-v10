# ANTIPATTERNS — Запрещённые решения в CIS V10.0-r1

> **Назначение:** каталог конкретных "никогда не делай так".
> Читается Claude Code **перед началом каждой задачи** (§ 25, § 28 в CLAUDE.md).
> Пополняется **только через TASK от архитектора** — сам не добавляй.
>
> Формат одного антипаттерна описан в CLAUDE.md § 28.
> Текущее количество антипаттернов: **7** (AP-01 ... AP-07).

---

## AP-01: Hardcoded абсолютный путь в коде модуля

**Категория:** code-quality
**Severity:** HIGH

**Что это:**
Строка с абсолютным путём вроде `r"C:\CODE\MARKET ANALYSIS\..."`, `"/home/user/..."`, `"D:\\MARKET_MIND\\..."` прописана прямо в коде модуля.

**Почему это вредно:**
- Код ломается при переезде проекта
- Код не работает на другой машине (у другого разработчика, в CI)
- Отладка на Linux/Mac невозможна
- Конфликтует с L-06 (единственный канонический путь через переменную)

**Реальный случай (когда встречалось):**
2026-04-17, `MARKET_MIND/ENGINE/context_orchestrator.py` строка 22:
```python
log_dir = Path(r'C:\CODE\MARKET ANALYSIS\MARKET_MIND\LAYER_H_INTERFACE\logs')
```
Также: `ENGINE/task_executor.py` имел путь `C:\КОДИНГ\MARKET ANALYSIS` — другая версия тех же данных.

**Правильная альтернатива:**
Паттерн **P-01** (`Path(__file__).resolve()` с опциональным параметром в конструкторе).

**Как проверить что я не допускаю:**
```bash
grep -rn "C:\\\\" MARKET_MIND/ENGINE/ 2>/dev/null
grep -rn "/home/" MARKET_MIND/ENGINE/ 2>/dev/null
grep -rn "/Users/" MARKET_MIND/ENGINE/ 2>/dev/null
# Все три должны вернуть пустой результат
```

---

## AP-02: Stub-данные в production-коде

**Категория:** architecture
**Severity:** CRITICAL

**Что это:**
Метод чтения данных возвращает hardcoded "тестовые" значения вместо реальных или `None`. Часто помечается полем `"stub": True` или `# TODO: replace with real implementation`.

**Почему это вредно:**
- Маскирует отсутствие модуля — вышестоящий код "видит валидные данные"
- Искусственно стабилизирует поведение системы (всегда одни и те же значения)
- При замене заглушки на реальный модуль поведение меняется скачком
- Если забыли заменить — stub попадает в production

**Реальный случай (когда встречалось):**
2026-04-17, `context_orchestrator.py`:
```python
def _get_feature_snapshot(self, symbol: str, timeframe: str) -> Dict[str, Any]:
    """Заглушка — будет заменена Feature Store (Task 13)"""
    time.sleep(0.02)
    return {
        "symbol": symbol,
        "rsi": 45.2,
        "macd": 0.001,
        "stub": True
    }
```

Тесты проходили, система "работала", но выдавала всегда одни и те же паттерны. При интеграции это бы дало систематическую ошибку прогнозирования.

**Правильная альтернатива:**
Паттерн **P-02** (graceful degradation — возврат `None` + warning в лог).

Если для тестов нужны фикстуры — положи их в `tests/fixtures/*.json`, импортируй только в тестах.

**Как проверить что я не допускаю:**
```bash
grep -rn '"stub"' MARKET_MIND/ENGINE/ 2>/dev/null
grep -rn "# заглушка" MARKET_MIND/ENGINE/ 2>/dev/null
grep -rn "# stub" MARKET_MIND/ENGINE/ 2>/dev/null
# Должны вернуть пустой результат
```

---

## AP-03: Голый `except:` без логирования

**Категория:** code-quality
**Severity:** HIGH

**Что это:**
Конструкция `try: ... except: pass` или `try: ... except Exception: pass` без логирования ошибки.

**Почему это вредно:**
- Скрывает баги и делает их невозможными для отладки
- Ловит даже `KeyboardInterrupt` и `SystemExit` (если голый `except:`)
- Stack trace теряется навсегда
- Нарушает § 18 CLAUDE.md

**Реальный случай (когда встречалось):**
2026-04-17, `context_orchestrator.py` `_run_parallel_guards()`:
```python
try:
    guards['axm_guard_result'] = future_axm.result(timeout=0.1)
except:                           # Голый except
    guards['axm_guard_result'] = {
        "passed": False, "violations": ["timeout"], "stub": True
    }
```
Комбо с AP-02 — и exception proglочен, и stub подменяет результат.

**Правильная альтернатива:**
Паттерн **P-03** (конкретные exception-типы + логирование).

**Как проверить что я не допускаю:**
```bash
grep -rn "except:" MARKET_MIND/ENGINE/ 2>/dev/null
grep -rn "except Exception: pass" MARKET_MIND/ENGINE/ 2>/dev/null
# Должны вернуть пустой результат
```

---

## AP-04: `ABORTED` статус в Fast Lane pipeline

**Категория:** architecture
**Severity:** CRITICAL

**Что это:**
Код в критическом пути Fast Lane (Context Orchestrator, Input Assembly, Model Core на 1h/4h таймфреймах) при timeout / отсутствии данных возвращает статус `"ABORTED"` или эквивалент, блокирующий выдачу прогноза.

**Почему это вредно:**
- Прямое нарушение Fast Lane Implementation Invariant из ТЗ V10.0-r1
- Пользователь не получает прогноз когда он ожидается
- Ломает контракт "Fast Lane всегда возвращает результат < 30 секунд"
- Противоречит § 10 канону ТЗ

Цитата из ТЗ V10.0-r1, Задача 3:
> **— прогноз НЕ блокируется — это нарушало бы Fast Lane Invariant**

**Реальный случай (когда встречалось):**
2026-04-17, `context_orchestrator.py` `_collect_block_inputs()`:
```python
for input_name, future in futures.items():
    try:
        inputs[input_name] = future.result(timeout=self.timeouts[input_name])
    except TimeoutError:
        raise TimeoutError(f"timeout_{input_name}")
# → orchestrate() ловит и возвращает _abort_context() со статусом ABORTED
```

**Правильная альтернатива:**
В Fast Lane при любом timeout:
- `context_degraded = True`
- Missing данные помечаются (но не блокируют)
- Возвращается минимальный валидный контекст (header + query + что успели)
- Статус `"OK"` или `"DEGRADED"`, **никогда `"ABORTED"`** в Fast Lane

ABORT допустим **только** в Slow Lane (24h / research), где latency не критична.

**Как проверить что я не допускаю:**
- Найти в коде все упоминания `timeframe in ("1h", "4h")` или `FAST_LANE_TIMEFRAMES`
- Убедиться что в этих ветках нет `return {"status": "ABORTED"}`, `raise AbortError`, или эквивалента
- Проверить что Failover возвращает осмысленный контекст, не исключение

См. **L-08** для полного обоснования.

---

## AP-05: Токен/пароль/ключ в коде или в закоммиченном файле

**Категория:** security
**Severity:** CRITICAL

**Что это:**
GitHub token, Binance API key, Anthropic API key, любой другой секрет прописан:
- В коде модуля (строка, переменная по умолчанию)
- В закоммиченном `.env` (даже если `.gitignore` их исключает — вдруг кто забудет)
- В TASK файле, README, docstring
- В логах (через `print(os.environ)` или аналог)
- В сообщении коммита
- В zip-архиве для ревью

**Почему это вредно:**
- Утечка в публичный репо = компрометация аккаунта
- Токен в логах попадает в системы сбора логов
- Удаление из git-истории требует force push + revoke
- Нарушает § 11 CLAUDE.md

**Реальный случай (когда встречалось):**
2026-04-18, `.env` проекта содержал:
```
GITHUB_TOKEN=ghp_REDACTED_CLASSIC_TOKEN_WAS_HERE_DO_NOT_RESTORE
```
`.gitignore` защитил от коммита, но при сборке zip для ревью токен попал в архив. По счастливой случайности `.env` был только у архитектора, не публично, и токен был сразу отозван.

**Правильная альтернатива:**
- GitHub push → через Windows Credential Manager, никаких токенов в `.env`
- API ключи Binance/и т.п. → в `.env` (локально), **никогда** в коде и коммитах
- Тестовые ключи → отдельный `.env.test`, в `.gitignore`
- Urgent отзыв при малейшем подозрении утечки

См. **L-05** для полного обоснования.

**Как проверить что я не допускаю:**
```bash
# Перед коммитом:
git diff --cached | grep -iE "(ghp_|github_pat_|sk-|api[_-]?key)" 
# Должен быть пустой результат

# В коде:
grep -rn "ghp_\|github_pat_" MARKET_MIND/ENGINE/ scripts/ 2>/dev/null
# Должен быть пустой результат
```

---

## AP-06: Emoji в `print()` тестового/CLI скрипта

**Категория:** code-quality
**Severity:** MEDIUM

**Что это:**
Тестовый скрипт или CLI-утилита использует emoji в `print()` — `✅`, `❌`, `⚠️`, `🎯` и т.п.

**Почему это вредно:**
- На Windows с cp1251 (русская локаль по умолчанию) скрипт падает с `UnicodeEncodeError`
- Тест "работает у меня" перестаёт работать у пользователя
- Без fix через `sys.stdout.reconfigure()` проблему трудно отлавливать

**Реальный случай (когда встречалось):**
2026-04-17, тесты TASK_03 v1:
```python
print(f'\u2705 Test 1 OK: status={result["status"]}')
# → UnicodeEncodeError: 'charmap' codec can't encode character '\u2705'
```

**Правильная альтернатива:**
Паттерн **P-05** — ASCII-маркеры (`[OK]`, `[FAIL]`, `[PASS]`, `[WARN]`) плюс опциональный UTF-8 reconfigure в начале скрипта.

**Как проверить что я не допускаю:**
```bash
# Ищем emoji-символы в print() в .py файлах
grep -rnE "print.*[\U0001F300-\U0001F9FF✅❌⚠🎯🔥]" --include="*.py" .
# Должен быть пустой результат
```

См. **L-04** для полного обоснования.

---

## AP-07: Самовольное добавление функционала, не описанного в TASK

**Категория:** workflow
**Severity:** HIGH

**Что это:**
Claude Code в процессе выполнения TASK добавляет:
- Новые файлы не указанные в TASK
- Новые зависимости в `requirements.txt` без согласования
- "Полезные" функции/классы которые не запрашивались
- CLI-команды / dashboard / utilities "на всякий случай"
- "Улучшения" сверх описанного
- Рефакторинг существующего кода сверх требуемого

**Почему это вредно:**
- Расхождение между замыслом (архитектор) и реализацией (исполнитель)
- Новые строки кода = новые точки отказа
- Сложнее ревью: надо понимать "зачем вообще это тут"
- Каждое самовольное изменение накапливает технический долг

**Реальный случай (когда встречалось):**
2026-04-17, при выполнении задач 0-2 в репо появилось:
- `dashboard.py`, `cis-cli.py`, `status-export.py` — CLI и веб-дашборд не просили
- `mcp-server.js`, `simple-mcp-server.js`, `test-mcp.js` — MCP-интеграция не запрашивалась
- Корневой `ENGINE/` с "Financial CTO" — task_executor, task_lifecycle_manager — вся автоматизация задач не заказывалась
- 4 документа (CRYPTO_INTELLIGENCE_SYSTEM_STRUCTURE.md, PROJECT_DESCRIPTION.md, INTERFACES_GUIDE.md, QUICKSTART.md) — не по TASK

Всё это пришлось удалить в TASK_00 — впустую потраченные часы работы и объём ревью.

**Правильная альтернатива:**
- TASK описывает ровно то что нужно сделать — § 1, § 2 CLAUDE.md
- Появилась идея в процессе → файл `TASKS/NOTES/ideas_YYYY-MM-DD.md` (§ 4), реализацию не трогаешь
- Видишь что в TASK "не хватает" чего-то → § 3 (СТОП + вопрос Сергею)
- Видишь удобный способ сделать лучше → тот же § 3 или в NOTES

**Как проверить что я не допускаю:**
Перед коммитом — пройди по списку файлов которые ты создал/изменил. Для каждого спроси:
- Этот файл упомянут в TASK? Если нет — зачем он?
- Эта функция нужна для acceptance criteria TASK? Если нет — зачем она?
- Эта зависимость в requirements.txt была в TASK? Если нет — § 3.

См. **§ 1-2** CLAUDE.md.

---

## Индекс по severity

| Severity | Антипаттерны |
|---|---|
| CRITICAL | AP-02 (stub данные), AP-04 (ABORT в Fast Lane), AP-05 (секреты) |
| HIGH | AP-01 (hardcoded пути), AP-03 (голый except), AP-07 (самовольный функционал) |
| MEDIUM | AP-06 (emoji в print) |

## Индекс по категориям

| Категория | Антипаттерны |
|---|---|
| architecture | AP-02, AP-04 |
| code-quality | AP-01, AP-03, AP-06 |
| security | AP-05 |
| workflow | AP-07 |

---

## История обновлений

| Дата | Версия | Что добавлено |
|---|---|---|
| 2026-04-18 | v1.0 | Initial — 7 антипаттернов AP-01..AP-07 из первого ревью |
