# CIS V10.0-r1 — Руководство для Claude

## Inference Boundary
KB влияет только на explanation и context quality.
Не на direction прогноза. Это защита от KB-bias.

## TF Hierarchy
1w > 1d > 4h > 1h > 15m > 5m > 1m
При конфликте: junior TF weight × 0.3, confidence -= 0.10
При согласованности: confidence += 0.05

## Epistemic Status
- direct: данные напрямую измеряют явление
- approximate: OHLCV-proxy, causal_confidence_penalty = -0.15
- uncertain: недостаточно данных

## Три правила канона
1. Stability proof ≠ predictive validity
2. Determinism ≠ correctness
3. Conformal coverage ≠ trading edge

## Операциональный сценарий
Трейдер → гипотеза → Claude анализирует → Система считает →
Claude интерпретирует → GPT (опционально) критикует →
Трейдер принимает решение
