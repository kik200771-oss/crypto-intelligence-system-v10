# Pattern Logic DSL Grammar V1.0

## Overview

Доменно-специфический язык (DSL) для описания логики торговых паттернов в поле `logic_dsl` схемы pattern_schema.json.

## Placeholder Structure

```
CONDITION ::= <market_condition> | <technical_indicator> | <composite_condition>
TIMEFRAME ::= "1m" | "5m" | "15m" | "30m" | "1h" | "4h" | "12h" | "1d" | "1w"
OPERATOR ::= "AND" | "OR" | "NOT"
```

## Status

**PLACEHOLDER** — полная спецификация будет разработана в отдельной задаче.

Текущие паттерны используют произвольный текстовый формат в поле `logic_dsl`.

## Future Expansion

- Формальная BNF грамматика
- Парсер и валидатор DSL выражений
- Компилятор DSL → исполняемый код
- Unit tests для DSL компонентов

## Related

- `pattern_schema.json` поле `logic_dsl`
- Task 8 Pattern Discovery (потребитель DSL)