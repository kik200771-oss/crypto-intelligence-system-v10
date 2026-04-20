# Observation: Conditional error-pattern mining — механизм условной калибровки по сигнатуре входных признаков

**Дата:** 2026-04-20
**Автор:** Сергей (Product Owner) + Claude Opus (архитектор) — обсуждение после Ритуала старта сессии
**Контекст TASK:** до начала TASK_05 (context_orchestrator v2), как продолжение идеи 2026-04-19_bias_correction_idea.md
**Тип:** observation

---

## Что замечено

Сергей предложил расширить идею bias correction новым механизмом — **поиском условных закономерностей в ошибках прогноза**. В отличие от простого усреднённого коэффициента, этот механизм группирует ошибки по **сигнатуре входных признаков** и выявляет паттерны вида "в определённых условиях мы систематически ошибаемся предсказуемым образом".

**Два типа закономерностей которые ловит механизм:**

**Тип 1 — систематическое глобальное смещение (уже частично покрыт bias_correction_idea):**
- Прогноз 1.0 → факт 1.2 (ошибка +0.2)
- Прогноз 0.8 → факт 1.0 (ошибка +0.2)
- Стабильное смещение в одну сторону независимо от контекста

**Тип 2 — условные закономерности по сигнатуре (новое):**
- При наборе признаков `{RSI_14=30, volume_spike=True, BTC_dominance=high}` прогноз систематически занижает на 5-8%
- При наборе `{RSI_14=70, low_volume=True, trend_persistent=True}` прогноз систематически завышает на 3-5%
- Закономерность связана **не с глобальным режимом рынка**, а с конкретной комбинацией входных данных которая использовалась для прогноза

---

## Чем это отличается от bias_correction_idea (2026-04-19)

| Параметр | bias_correction_idea | Conditional error-pattern mining (эта идея) |
|---|---|---|
| Принцип группировки ошибок | По **режиму** рынка (bull/bear/flat) | По **сигнатуре входных признаков** прогноза |
| Источник группировки | Внешний классификатор (Task 16) | Эмпирический анализ истории ошибок |
| Количество "карманов" | 3-5 режимов (фиксировано) | Множество кластеров признаков (обнаруживается из данных) |
| Формулировка коррекции | "В bull рынке занижаем на 8%" | "Когда совпали условия A+B+C — занижаем на 5%" |
| Зависимость от Task 16 | Обязательная | Опциональная (сигнатура может включать режим как один из признаков) |
| Требуемый объём данных | ≥200 прогнозов MDC | ≥500-1000 прогнозов + holdout split |
| Риск переобучения | Низкий-средний | **Высокий** (нужна жёсткая валидация) |

**Ключевой вывод:** это **не подкатегория** bias correction, а **самостоятельный механизм**. В общем roadmap становится **#9**, параллельно #1.

---

## Почему это может быть интересно

- **Ловит то что regime-calibration не увидит.** Ошибка может коррелировать не с режимом, а с комбинацией признаков (RSI + volume + time-of-day + pattern_id), которая пересекает несколько режимов.
- **Не требует заранее определённой таксономии.** Кластеры обнаруживаются из данных, не декларируются архитектором.
- **Потенциально вскрывает систематические слабости конкретных паттернов** которые мы используем для прогноза — например "паттерн P-023 работает хуже при high_volatility + low_volume".
- **Может работать параллельно с bias correction**, не конкурирует — два независимых уровня калибровки, финальный прогноз проходит через оба.

---

## Честные риски

### Риск 1: Overfitting к шуму (severity: HIGH)

С ограниченной выборкой легко обнаружить "закономерность" которая распадётся на новых данных. На 53 точках (как в эксперименте bias_correction_idea) такой механизм **гарантированно переобучится**.

**Контрмера:** обязательный holdout split — обнаружение на first half, валидация на second half. Без прохождения holdout коэффициент не активируется.

### Риск 2: Проклятие размерности (severity: MEDIUM)

Если сигнатура = 10 признаков, количество возможных комбинаций взрывается. Каждая конкретная сигнатура встретится редко → статистика на малых карманах.

**Контрмера:** кластеризация вместо точного матчинга. Decision tree на ошибках (target = знак+величина ошибки, features = входы прогноза) автоматически группирует близкие сигнатуры.

### Риск 3: Data leakage (severity: MEDIUM)

Если признак (например, `time_of_day` или `recent_volatility`) уже используется в самом прогнозе, а затем используется в сигнатуре для коррекции — это двойной учёт. Коррекция может "отменять" сигнал который должен был работать.

**Контрмера:** раздельный набор признаков для прогноза и для сигнатуры, либо явная проверка независимости через информационный анализ.

### Риск 4: Нестабильность коэффициентов (severity: MEDIUM)

Обнаруженный коэффициент может "улетать" со временем (смена режима, изменение поведения рынка). Применение устаревшего коэффициента ухудшает прогноз.

**Контрмера:** sliding window пересчёт коэффициентов, deactivation листа если stability check не проходит (std коэффициентов > threshold).

### Риск 5: Конфликт с pre-registration principle ТЗ (severity: CRITICAL для governance)

ТЗ V10.0-r1 в разделе Research Inbox требует **pre-registration гипотез** для защиты от p-hacking. Error pattern mining по природе **post-hoc**. Это может конфликтовать с принципами исследования системы.

**Контрмера:** механизм должен иметь **обязательный holdout как встроенный компонент**, не опциональный. Формулировка:
- Обнаружение паттерна на training split
- Фиксация гипотезы в prediction_schema как `hypothesis_candidate` с датой обнаружения
- Валидация на out-of-sample данных (forward-walking)
- Активация только после PASS out-of-sample теста

Так механизм становится **semi-automated pre-registration**: система сама регистрирует гипотезу при обнаружении и сама её тестирует на новых данных.

---

## Технический набросок (не план реализации)

**Disclaimer:** это эскиз концепции, не TASK spec. Реальный механизм будет проектироваться в Task 24 после MDC complete и накопления ≥500 прогнозов.

### Фаза 1: Feature logging
Для каждого прогноза сохраняется запись в `MARKET_MIND/LAYER_F_FEEDBACK/error_signatures/<date>.jsonl`:

```json
{
  "prediction_id": "pred_20260420_btc_1h_001",
  "timestamp": "2026-04-20T15:00:00Z",
  "symbol": "BTCUSDT",
  "timeframe": "1h",
  "signature": {
    "rsi_14": 62.3,
    "volume_ratio_24h": 1.4,
    "btc_dominance": 0.52,
    "pattern_id_used": "P_023",
    "regime": "uptrend",
    "volatility_bucket": "low",
    "session": "US",
    "time_of_day": 15
  },
  "predicted": 42500.0,
  "actual": 42800.0,
  "error_absolute": 300.0,
  "error_relative": 0.00706,
  "error_sign": 1
}
```

### Фаза 2: Post-hoc mining (offline, раз в N прогнозов)

1. Загрузить все записи за последний период (window, например 90 дней)
2. Разбить на train (first 60%) / holdout (last 40%)
3. На train — построить decision tree: features = signature, target = (error_sign × error_relative)
4. Найти "листья" с:
   - `|mean(error)| > 2 × std_noise` — смещение выше шума
   - `std(error) / |mean(error)| < 0.5` — низкая дисперсия (стабильный паттерн)
   - `N_samples_in_leaf >= 30` — статистическая достоверность
5. Для каждого такого листа → записать кандидата `conditional_correction_candidate` с сигнатурой + предлагаемый коэффициент + train stats

### Фаза 3: Holdout validation

Применить каждого кандидата на holdout split:
- `MAPE_holdout_with_correction` vs `MAPE_holdout_without_correction`
- Если `improvement > threshold` (например, ≥ 2 процентных пункта) И `p_value < 0.05` → активировать кандидата как `active_correction`
- Иначе → отклонить, записать в `rejected_candidates` с причиной

### Фаза 4: Runtime application

При новом прогнозе:
1. Вычислить сигнатуру
2. Проверить матч с любой из `active_corrections` (пройти по decision tree)
3. Если матч → применить коэффициент, пометить `conditional_calibration_applied: <correction_id>` в prediction_schema
4. Если нет матча → прогноз без коррекции, пометить `conditional_calibration_applied: null`

### Фаза 5: Monitoring + deactivation

Для каждой `active_correction`:
- После каждого prediction в её сигнатурном поле — обновить running statistics
- Если stability check не проходит (std растёт, mean дрейфует) → deactivate, запись в `deactivated_corrections` с причиной

---

## Связь с Task 7 (Trust System)

ТЗ содержит Task 7 — систему доверия паттернам на основе track record. Механика пересекается:

| Task 7 Trust | Conditional correction |
|---|---|
| Trust score паттерна | Trust score коэффициента |
| Обновление на каждом outcome | Обновление на каждом applied correction |
| Deactivation паттерна при падении trust | Deactivation коэффициента при нестабильности |

**Предложение:** при реализации в Task 24 использовать те же базовые принципы trust scoring что Task 7, возможно выделить shared utility. Это снижает код и стандартизирует governance.

---

## Связь с Task 5 (context_orchestrator) — Conflict Exposure

Если активная `conditional_correction` противоречит сигналу паттерна — это конфликт:
- Паттерн P-023 говорит "прогноз рост на 1.2%"
- `conditional_correction` по сигнатуре говорит "в этом контексте наш прогноз обычно занижает на 0.5%"
- → финальный прогноз: рост на 1.2% + коррекция +0.5% = 1.7%

Метаданные должны содержать **оба факта**, не только результат:
```json
{
  "raw_forecast": 1.012,
  "pattern_driver": "P_023",
  "conditional_correction_applied": "cc_005",
  "correction_factor": 1.005,
  "final_forecast": 1.017
}
```

Это соответствует **Conflict Exposure principle** которая закладывается в TASK_05.

---

## Условия применимости (когда это будет работать хорошо)

- ≥ 500-1000 реальных прогнозов накоплено (холодный старт невозможен)
- Стабильный base forecast (MAPE < 25% до коррекции)
- Достаточное разнообразие рыночных условий в обучающей выборке
- Holdout split показывает устойчивое улучшение на out-of-sample данных
- Decision tree кандидат имеет ≥ 30 наблюдений в листе

---

## Условия НЕприменимости (когда не поможет или навредит)

- Выборка < 500 прогнозов — статистика недостоверна, риск overfitting
- Holdout validation не пройден — коэффициент не активируется, пишется в `rejected_candidates`
- Смена рыночного режима большего масштаба (bull-to-bear cycle transition) — коэффициенты могут устареть, требуется sliding window с коротким окном
- Конфликт с pre-registered гипотезой из Research Inbox (если гипотеза явно говорит "не корректировать") → не применять

---

## Предложение (для будущего Task 24)

Реализовать как **отдельный модуль** `conditional_calibration.py` в `MARKET_MIND/ENGINE/`:

1. **API:**
   ```python
   def find_matching_correction(signature: dict) -> CorrectionMatch | None
   def apply_correction(forecast: float, match: CorrectionMatch) -> float
   def update_correction_stats(correction_id: str, outcome: float) -> None
   def mine_new_candidates(window_days: int = 90) -> list[Candidate]
   def validate_on_holdout(candidate: Candidate) -> ValidationResult
   ```

2. **Состояние:** JSON-store в `LAYER_F_FEEDBACK/conditional_corrections/`
   - `active_corrections.json` — работающие коэффициенты
   - `rejected_candidates.json` — не прошли holdout (аудит)
   - `deactivated_corrections.json` — отключены по stability check (аудит)

3. **Integration point:** вызывается из `calibration_engine.py` (из bias_correction_idea) после применения regime-based коррекции:
   ```
   raw_forecast → regime_calibration → conditional_calibration → final_forecast
   ```

4. **Trust scoring:** переиспользовать компоненты Task 7.

5. **Holdout discipline:** встроена в workflow mining → validation → activation. Без прохождения holdout активация невозможна.

---

## Связь с существующими артефактами

- **ТЗ Task 24 (Feedback System):** место для реализации, модуль `conditional_calibration.py` рядом с `calibration_engine.py`
- **ТЗ Task 7 (Trust System):** shared principles для trust scoring коэффициентов
- **ТЗ Task 5 (Context Orchestrator) — Conflict Exposure:** метаданные применённой коррекции проходят через оркестратор
- **ТЗ Research Inbox — pre-registration:** holdout validation как форма automated pre-registration
- **2026-04-19_bias_correction_idea.md:** параллельный механизм, работает совместно
- **2026-04-19_forecast_refinement_roadmap.md:** добавить как **#9 Conditional error-pattern mining** в roadmap, приоритет для спота — **средний** (не топ, так как требует много данных)

---

## Оценка качества

**Ожидаемое влияние на MAPE:** оценка на основе экспертной догадки, не эмпирики.

- **Если holdout дисциплина соблюдается:** диапазон -3% до +10% улучшения MAPE относительно base+regime_calibration, с медианной оценкой +2-4%
- **Если holdout дисциплина нарушается (post-hoc без проверки):** диапазон -15% до +5%, медиана -2-5% (ухудшение)

**Уровень уверенности оценки:** низкий. Без реальных данных и реализации это экспертная догадка, фактический результат может отличаться ±50%.

**Основная ценность механизма — не улучшение MAPE, а ловля систематических слабостей конкретных сигнатур.** Даже если средний эффект близок к нулю, механизм может резко улучшить прогноз на редких но предсказуемых контекстах.

---

## Тэги

`task-24`, `feedback-system`, `conditional-calibration`, `error-pattern-mining`, `potential-pattern`, `future-work`, `holdout-critical`, `post-mdc`, `roadmap-item-9`

---

## История обсуждения

- 2026-04-19: Сергей сформулировал идею bias_correction (обсуждение на Excel 53 точки)
- 2026-04-20: Сергей расширил идею — "не просто коэффициент, а поиск закономерностей по сигнатуре входных данных"
- 2026-04-20: Архитектор разделил на Тип 1 (уже покрыт bias_correction) и Тип 2 (новый механизм)
- 2026-04-20: Consensus — записать как отдельный observation, добавить в roadmap как #9, реализовать в Task 24 после MDC complete и накопления ≥500 прогнозов
- Согласованное название: **Conditional error-pattern mining**

---

## Следующий шаг

1. Сергей загружает файл в `C:\CODE\MARKET ANALYSIS\TASKS\NOTES\observations\`
2. Сергей загружает обновлённую копию в project knowledge (для контекста архитектора в будущих сессиях)
3. Обновить `2026-04-19_forecast_refinement_roadmap.md` — добавить секцию #9 с кросс-ссылкой на этот файл (отдельным шагом)
4. При реализации Task 24 (после MDC complete) — использовать этот файл как отправную точку спецификации
