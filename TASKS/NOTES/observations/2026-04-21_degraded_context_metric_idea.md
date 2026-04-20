# Observation: Degraded context rate как health metric для мониторинга

**Дата:** 2026-04-21  
**Автор:** Claude Code (замечено в Pre-task Analysis TASK_05a)  
**Тип:** observation  
**Связанные задачи:** TASK_05a, future TASK_05c  
**Тэги:** observability, monitoring, task-5c-preparation, context-quality  

## Наблюдение

TASK_05a skeleton включает поле `ContextResult.context_degraded: bool`. При накоплении прогнозов эта булева метрика может быть агрегирована в `degraded_context_rate` — доля прогнозов где context неполный из-за timeouts или недоступности источников данных.

## Почему это полезно

Метрика `degraded_context_rate` может служить health indicator системы: если >5-10% прогнозов работают с неполным контекстом, это сигнал о том что timeouts слишком агрессивны или источники данных (Pattern Registry, KB, Feature Store) часто недоступны. Threshold 5-10% может служить предупреждающим порогом для мониторинга.

## Связь с будущими задачами

TASK_05c будет реализовывать `_build_monitoring_context()` — возможное место для включения этой метрики в системы мониторинга. Также полезно для `_build_postmortem_context()` при анализе качества исторических прогнозов.

## Статус

Idea, требует обсуждения с архитектором до формализации в конкретную задачу.