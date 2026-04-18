**Crypto Intelligence System V10.0**

**Объединённый документ схем --- V5 (финальная)**

*17 схем · v6.3 Sealed Pre-Live Edition · V10.0-r1 · Апрель 2026*

  ----------------- ------------------------------- ---------------------- ----------------------------------------------------------------------------------------------------------
  **\#**            **Схема**                       **Статус**             **Ключевое изменение v6.3**

  1                 Контекст V10                    Без изменений          ---

  2                 Верхнеуровневая архитектура     Без изменений          ---

  3                 Поток данных                    ✓ ОБНОВЛЕНА            Two-transaction model, Config Governance, Tx_Feedback

  4                 Внутренний путь прогноза        ✓ ОБНОВЛЕНА            Feasibility Temporal Contract, Y_t, X_exec outcomes

  5                 Feedback & Control Loop         Без изменений          Fast/Slow split из v6.0

  6                 Эпистемическая архитектура      Без изменений          AXM/PRI/PAT неизменны

  7                 Переход V10→V11                 Без изменений          ---

  A1                Узкие места                     Без изменений          ---

  A5                Scope Drift                     Без изменений          ---

  B1                Stale Cache Policy              Без изменений          ---

  B2                Fast/Slow Feedback              Без изменений          ---

  B3                State Registry + Dampening      Без изменений          ---

  C1                Runtime Update Schedule         ⊕ НОВАЯ                Step 0-15, два transaction boundary, commit point

  C2                Decision Policy Operator        ⊕ НОВАЯ                P1-P11, P6a/P6b split, Uncertainty Escalation 2.5

  C3                Feasibility Temporal Contract   ⊕ НОВАЯ                Step 11 три выхода, current vs next cycle

  C4                Open Questions Register         ⊕ НОВАЯ                25 вопросов, 4 класса, RT-09..RT-11

  **C5**            **Операциональный контур**      **\"НОВАЯ V10.0-r1**   Трейдер + Claude + Система + GPT. Операциональный контур как система встроена в реальный рабочий процесс
  ----------------- ------------------------------- ---------------------- ----------------------------------------------------------------------------------------------------------

+--------------------------------------------------------------------------------------------------------------------------------------------+
| **Канон трёх документов --- три роли --- один источник истины**                                                                            |
|                                                                                                                                            |
| Mathematical Model v6.3 (57 разделов) --- математика, уравнения, contracts, governance                                                     |
|                                                                                                                                            |
| **Schematics V4 (этот документ) --- визуализация архитектуры и runtime semantics**                                                         |
|                                                                                                                                            |
| ТЗ V10.0-r1 --- операциональный документ: 30 задач, Phase Gates, acceptance criteria                                                       |
|                                                                                                                                            |
| *Начни с Mathematical Model v6.3 Intro (разделы 0.1/0.2/0.3) --- пояснительная записка, навигационная карта и аннотации всех 57 разделов.* |
+--------------------------------------------------------------------------------------------------------------------------------------------+

**ЧАСТЬ I --- АРХИТЕКТУРНЫЕ СХЕМЫ (схемы 1-7)**

Схемы 1-7 показывают архитектуру системы. Схемы 3 и 4 обновлены для v6.3.

**1. Контекст проекта и граница V10**

Граница V10/V11 зафиксирована Canon Scope Lock. V10 = Research & Signal Canon. V11+ требует Transition Gate.

![schema_1_context.png](media/c08d3d8b662a1c19bf1d1d1009778c0a6bb5917e.png "schema_1_context.png"){width="5.833333333333333in" height="2.0104166666666665in"}

> *Связь с моделью v6.3: разделы 1, 2, 3, 9 (AXM scope)*

**2. Верхнеуровневая архитектура V10**

Validation → Model Core только через Feedback. Return arrow (замкнутая петля).

![schema_2_architecture.png](media/32f775f33c6bf00add166d1691a641059c6443a7.png "schema_2_architecture.png"){width="5.833333333333333in" height="6.364583333333333in"}

> *Связь с моделью v6.3: разделы 2, 3, 11, 40 (8 слоёв LAYER_A-H)*

**3. Поток данных + Two-Transaction Model**

**✓ v6.3: ✓ ОБНОВЛЕНА v6.3: Two-transaction model (Tx_Forecast / Tx_Feedback), Config Governance Partition (3 класса), Step 0 Selection Rule.**

Левая часть: Tx_Forecast(t) --- основной поток прогноза. Правая часть: Tx_Feedback(t→t+1) --- Step 0 с Selection Rule. Два транзакционных объекта никогда не смешиваются.

![schema_3_dataflow.png](media/84f0a8829b82e359b41f9ce362e4bc1e57487014.png "schema_3_dataflow.png"){width="5.833333333333333in" height="2.53125in"}

> *Связь с моделью v6.3: разделы 40, 46, 47, 49, 52*

**4. Внутренний путь прогнозирования + Feasibility Temporal Contract**

**✓ v6.3: ✓ ОБНОВЛЕНА v6.3: Step 11 три выхода (safety_action_t + mode_next_t + status). Y_t FIRST classification → P6a application → Y_t final. X_exec outcomes.**

Step 11 --- центральный новый элемент. safety_action влияет на текущий цикл. mode_next_t --- только на следующий. X_exec фиксируется после P6a.

![schema_4_forecast_path.png](media/2da30094dffc9782fb996ae79ba7b2059931d287.png "schema_4_forecast_path.png"){width="5.833333333333333in" height="4.854166666666667in"}

> *Связь с моделью v6.3: разделы 7, 20, 51, 53*

**5. Feedback & Control Loop**

Fast Feedback Loop (≤200ms, Claude-free) + Slow Feedback Loop (async). Silence Debt --- diagnostic only.

![schema_5_feedback_loop.png](media/5591eef5a11fadeea0acf940f512b213ad272028.png "schema_5_feedback_loop.png"){width="5.833333333333333in" height="2.5833333333333335in"}

> *Связь с моделью v6.3: разделы 11, 40, 47, 52 (Fast/Slow + Tx_Feedback)*

**6. Эпистемическая архитектура AXM/PRI/PAT**

AXM = post-scoring guardrail only. PAT = основной сигнал. PRI = confidence modifier. Неизменно с v6.0.

![schema_6_epistemic.png](media/083ab595b72d3e197acd08e829d7eb96348c0535.png "schema_6_epistemic.png"){width="5.833333333333333in" height="3.90625in"}

> *Связь с моделью v6.3: разделы 9 (AXM/PRI), 20 (D_t=Ψ), 29 (E_ctrl)*

**7. Переход V10→V11**

Три зоны: Core/Support/Research. Kill Criteria + Transition Gate. Полный список условий в разделе 45 модели.

![schema_7_transition.png](media/d0fd465a2eb70b0d806c7a4ce296cf118f4a6fc0.png "schema_7_transition.png"){width="5.833333333333333in" height="5.229166666666667in"}

> *Связь с моделью v6.3: разделы 45 (Spec Freeze), 57 (Open Questions)*

**ЧАСТЬ II --- ПРОБЛЕМНО-АНАЛИТИЧЕСКИЕ СХЕМЫ (A1, A5)**

Специализированные схемы для аудита структурных рисков. Актуальны без изменений.

**A1. Карта узких мест и рисков**

Все узкие места из v6.0-v6.2 закрыты. Runtime Schedule (раздел 40) --- новый hot corridor v6.3.

![schema_A1_bottlenecks.png](media/9c2c6bde934f9721aec18194cd58a3af581994db.png "schema_A1_bottlenecks.png"){width="5.833333333333333in" height="2.5416666666666665in"}

**A5. Риск Scope Drift**

Core / Support / Research зоны неизменны. Causal multiplier и NP controller --- за границей V10 (V10.1+ gated).

![schema_A5_scope_drift.png](media/b0a2842d9f0847723dd85293f5f6be8b3d15d952.png "schema_A5_scope_drift.png"){width="5.833333333333333in" height="5.833333333333333in"}

**ЧАСТЬ III --- СХЕМЫ ЗАКРЫТЫХ СТРУКТУРНЫХ ПРОБЛЕМ (B1-B3)**

Схемы B1-B3 документируют закрытые проблемы из предыдущих итераций. Актуальны без изменений в v6.3.

**B1. Stale Cache Policy**

Gate 1 block → Stale Cache Fallback при stale_age ≤ TTL. В v6.3 закреплено в Fallback Eligibility Matrix (раздел 53).

![schema_B1_stale_cache.png](media/5345223183abfd7cf008fa6ee6cf7e0332123ffd.png "schema_B1_stale_cache.png"){width="5.833333333333333in" height="2.7395833333333335in"}

**B2. Fast/Slow Feedback Split**

Fast Feedback ≤200ms + Slow Feedback async. В v6.3 Tx_Feedback = отдельная транзакция (Step 0 следующего цикла). Связь с моделью v6.3: разделы 11, 40, 47, 49, 52 (Fast/Slow + Transaction Boundary + Deferred Queue + Step 0 Selection Rule).

![schema_B2_fast_slow_feedback.png](media/03900d38daa13515c50da82161050d867e9d8db5.png "schema_B2_fast_slow_feedback.png"){width="5.833333333333333in" height="2.9270833333333335in"}

**B3. State Registry + Second-Order Dampening**

atomic_update() + write ordering + second-order loop dampening (μ_t). Неизменно.

![schema_B3_state_dampening.png](media/ed4817131b5c83e701a7f4732394c2fbd3a5c39e.png "schema_B3_state_dampening.png"){width="5.833333333333333in" height="2.5625in"}

**ЧАСТЬ IV --- СХЕМЫ v6.3 SEALED EDITION (C1-C54)**

Четыре новые схемы закрывающие implementation semantics v6.3. Центральные для разработчиков Tasks 21/24/29/30. Основаны на разделах 51-57 математической модели: Feasibility Temporal Contract (51), Step 0 Selection Rule (52), Fallback Eligibility Matrix (53), Hysteresis Admissible Region (54), Final Errata Patch (55), Implementation Guide (56), Open Questions Register (57).

**C1. Runtime Update Schedule Contract**

**⊕ НОВАЯ v6.3: ⊕ НОВАЯ v6.3: Step 0-15 с двумя transaction boundary. Tx_Feedback (Step 0) завершается до Step 2 (snapshot read). Tx_Forecast (Steps 1-14) --- atomic commit point. Step 15 --- только queue append.**

Разделы 40, 47. Ключевой артефакт для реализации Tasks 21/24. Step 14 = commit point, Step 15 вне транзакции.

![schema_C1_runtime_schedule.png](media/25289a0f8e7abe411a9983c6c86932fbc830ae8d.png "schema_C1_runtime_schedule.png"){width="5.833333333333333in" height="3.7604166666666665in"}

> *Без понимания этой схемы реализация Tasks 21/24/29/30 невозможна.*

**C2. Decision Policy Operator D_t = Ψ**

**⊕ НОВАЯ v6.3: ⊕ НОВАЯ v6.3: Полный Runtime Precedence Order P1-P11. P6 разделён на P6a (current-cycle safety action, после Y_t) и P6b (next-cycle mode constraint). Uncertainty Escalation на позиции 2.5.**

Раздел 48. Критически важно: P6a применяется ПОСЛЕ Step 10 (Y_t), не до D_t. P3 (external override) short-circuits P4-P9.

![schema_C2_decision_policy.png](media/474b64e1ca4d0657ea88bd8f99e7bce95995b58c.png "schema_C2_decision_policy.png"){width="5.833333333333333in" height="3.75in"}

> *Без понимания этой схемы реализация Tasks 21/24/29/30 невозможна.*

**C3. Feasibility Temporal Contract**

**⊕ НОВАЯ v6.3: ⊕ НОВАЯ v6.3: Закрывает критический конфликт P6 vs Step 11. Step 11 выдаёт три раздельных выхода. Канонический порядок: D_t → Y_t (first) → P6a → Y_t recalc → X_exec.**

Раздел 51. При force_neutral: Y_t пересчитывается. При reject/hard_override: Y_t=DIR_INVALID (override, без пересчёта). mode_next_t хранится до Step 3 следующего цикла.

![schema_C3_feasibility_temporal.png](media/f97d4f55c251b3b281fd1fb5b934595d90f01257.png "schema_C3_feasibility_temporal.png"){width="5.833333333333333in" height="3.3541666666666665in"}

> *Без понимания этой схемы реализация Tasks 21/24/29/30 невозможна.*

**C4. Open Questions Register**

**⊕ НОВАЯ v6.3: ⊕ НОВАЯ v6.3: Карта честного знания. 25 вопросов в 4 классах: Live (7), Implementation (8), V10.1+ (4), Fundamental (6). RT-09..RT-11 как новые официальные Reopen Triggers.**

Раздел 57. observe = мониторить без активных действий. monitor = конкретный threshold и trigger. gated = только при gate conditions. reopen candidate = немедленный Architecture Review при проявлении.

![schema_C4_open_questions.png](media/f99b147ca25571bf9b46b06e62103415a19dc19e.png "schema_C4_open_questions.png"){width="5.833333333333333in" height="4.166666666666667in"}

> *Без понимания этой схемы реализация Tasks 21/24/29/30 невозможна.*

*Связь с моделью v6.3: разделы 42 (Silence Debt), 45 (RT-01..RT-08), 57 (Open Questions Register). RT-09..RT-11 добавлены в v6.3 финальной редакции.*

CIS V10.0 \| Schematics V4 \| 16 схем \| v6.3 Sealed \| Апрель 2026

*Модель v6.3 + документ схем V4 синхронизированы. Готово к Tasks 21/24/29/30.*

**C5. Операциональный контур --- четыре участника рабочего процесса**

НОВАЯ V10.0-r1: Схема показывает не внутреннюю архитектуру системы, а то как система встроена в реальный рабочий процесс. См. ТЗ V10.0-r1 разделы 1.32, 1.33, 1.34.

![](media/schema_C5_operational_contour.png){width="7.99912510936133in" height="4.999453193350831in"}

*Связь с ТЗ V10.0-r1: разделы 1.32 (операциональный сценарий), 1.33 (роль Claude), 1.34 (интеграция GPT). Мат.модель v6.3 не затронута.*

**Без понимания этой схемы разработчик не будет понимать для кого строится система и как она будет использоваться на практике.**
