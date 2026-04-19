#!/usr/bin/env python3
"""Debug script to understand Gate 3 outlier detection."""
import sys
import statistics
from pathlib import Path

# UTF-8 fix for Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

# Add MARKET_MIND to path
sys.path.insert(0, str(Path(__file__).resolve().parent / "MARKET_MIND"))

def _make_valid_candles(n: int = 20, start_ts: int = 1_700_000_000, interval: int = 3600) -> list[dict]:
    """Copy of test data generation."""
    candles = []
    for i in range(n):
        base = 100.0 + i * 0.5
        candles.append({
            "timestamp": start_ts + i * interval,
            "open": base,
            "high": base + 0.3,
            "low": base - 0.3,
            "close": base + 0.1,
            "volume": 1500.0 + (i * 17),
        })
    return candles

def analyze_outlier_test():
    """Analyze the outlier test data."""
    candles = _make_valid_candles(20)

    print("=== Original candles (first 12) ===")
    for i in range(12):
        c = candles[i]
        print(f"Candle {i:2d}: close={c['close']:6.1f}")

    # Apply the outlier modification (extreme case)
    candles[10]["open"] = 104.6
    candles[10]["high"] = 1000.0
    candles[10]["low"] = 104.0
    candles[10]["close"] = 1000.0
    candles[11]["open"] = 1000.0
    candles[11]["high"] = 1000.0
    candles[11]["low"] = 105.0
    candles[11]["close"] = 105.6

    print("\n=== Modified candles (around the outlier) ===")
    for i in range(8, 14):
        c = candles[i]
        print(f"Candle {i:2d}: close={c['close']:6.1f}")

    # Calculate returns
    closes = [float(c["close"]) for c in candles]
    returns = []
    for i in range(len(closes) - 1):
        if closes[i] > 0:
            returns.append((closes[i+1] - closes[i]) / closes[i])

    print(f"\n=== Returns analysis (total {len(returns)} returns) ===")
    for i in range(min(15, len(returns))):
        print(f"Return {i:2d}: {returns[i]:8.4f} ({returns[i]*100:6.2f}%)")

    # Statistics
    mean = statistics.mean(returns)
    stdev = statistics.stdev(returns)
    print(f"\nMean return: {mean:8.4f} ({mean*100:6.2f}%)")
    print(f"Std dev:     {stdev:8.4f} ({stdev*100:6.2f}%)")

    print(f"\n=== Z-scores (threshold=5.0) ===")
    threshold = 5.0
    outliers = 0
    for i, r in enumerate(returns):
        z = abs(r - mean) / stdev if stdev > 0 else 0
        flag = " <-- OUTLIER" if z > threshold else ""
        print(f"Return {i:2d}: z-score={z:6.2f}{flag}")
        if z > threshold:
            outliers += 1

    print(f"\nTotal outliers detected: {outliers}")
    return outliers > 0

if __name__ == "__main__":
    detected = analyze_outlier_test()
    print(f"\nOutlier detection: {'SUCCESS' if detected else 'FAILED'}")