#!/usr/bin/env python3
"""
Простой анализ криптовалют без эмодзи для Windows терминала
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

# Добавляем путь к модулям
sys.path.append(str(Path(__file__).parent))

from src.data.binance_client import BinanceClient
from src.analysis.technical_indicators import TechnicalIndicators

def analyze_crypto(symbol='BTCUSDT', days_back=30):
    """Простой анализ криптовалюты"""

    print("=" * 60)
    print(f"АНАЛИЗ КРИПТОВАЛЮТЫ: {symbol}")
    print("=" * 60)

    try:
        # Инициализация клиента
        print("Подключение к Binance API...")
        client = BinanceClient()

        if not client.test_connectivity():
            print("ОШИБКА: Не удалось подключиться к Binance API")
            return

        print("Подключение успешно!")

        # Загрузка данных
        print(f"Загрузка данных за {days_back} дней...")

        end_time = datetime.now()
        start_time = end_time - timedelta(days=days_back)

        df = client.get_historical_klines(
            symbol=symbol,
            interval='1h',
            start_time=start_time.isoformat(),
            end_time=end_time.isoformat()
        )

        if df.empty:
            print(f"ОШИБКА: Нет данных для {symbol}")
            return

        print(f"Загружено {len(df)} записей")

        # Расчет технических индикаторов
        print("Расчет технических индикаторов...")
        df_indicators = TechnicalIndicators.calculate_all_indicators(df)

        # Текущая цена и статистика
        current_price = df['close'].iloc[-1]
        price_change = ((df['close'].iloc[-1] - df['close'].iloc[0]) / df['close'].iloc[0]) * 100

        print("\n" + "=" * 40)
        print("ИНФОРМАЦИЯ О ЦЕНЕ")
        print("=" * 40)
        print(f"Текущая цена: ${current_price:,.2f}")
        print(f"Изменение за период: {price_change:+.2f}%")

        # 24ч статистика
        try:
            ticker = client.get_24hr_ticker(symbol)
            if not ticker.empty:
                ticker_data = ticker.iloc[0]
                change_24h = float(ticker_data['priceChangePercent'])
                volume_24h = float(ticker_data['quoteVolume'])
                print(f"Изменение за 24ч: {change_24h:+.2f}%")
                print(f"Объем за 24ч: ${volume_24h:,.0f}")
        except:
            print("24ч статистика недоступна")

        # Технические индикаторы
        print("\n" + "=" * 40)
        print("ТЕХНИЧЕСКИЕ ИНДИКАТОРЫ")
        print("=" * 40)

        latest = df_indicators.iloc[-1]

        # RSI
        if 'RSI' in latest:
            rsi = latest['RSI']
            if rsi > 70:
                rsi_signal = "ПРОДАЖА - Перекупленность"
                signal_strength = "СИЛЬНЫЙ"
            elif rsi < 30:
                rsi_signal = "ПОКУПКА - Перепроданность"
                signal_strength = "СИЛЬНЫЙ"
            else:
                rsi_signal = "НЕЙТРАЛЬНО"
                signal_strength = "СЛАБЫЙ"

            print(f"RSI: {rsi:.1f} - {rsi_signal} ({signal_strength})")

        # MACD
        if 'MACD' in latest and 'MACD_Signal' in latest:
            if latest['MACD'] > latest['MACD_Signal']:
                macd_signal = "ПОКУПКА - Бычий тренд"
            else:
                macd_signal = "ПРОДАЖА - Медвежий тренд"
            print(f"MACD: {macd_signal}")

        # SMA тренд
        if 'SMA_20' in latest and 'SMA_50' in latest:
            if latest['SMA_20'] > latest['SMA_50']:
                trend = "Восходящий тренд"
            else:
                trend = "Нисходящий тренд"
            print(f"SMA Тренд: {trend}")

        # Bollinger Bands
        if 'BB_Upper' in latest and 'BB_Lower' in latest:
            if current_price > latest['BB_Upper']:
                bb_status = "Выше верхней полосы - возможна коррекция"
            elif current_price < latest['BB_Lower']:
                bb_status = "Ниже нижней полосы - возможен отскок"
            else:
                bb_status = "В нормальном диапазоне"
            print(f"Bollinger Bands: {bb_status}")

        # Общий вывод
        print("\n" + "=" * 40)
        print("ТОРГОВЫЕ СИГНАЛЫ")
        print("=" * 40)

        buy_signals = 0
        sell_signals = 0

        # Подсчет сигналов
        if 'RSI' in latest:
            if latest['RSI'] < 30:
                buy_signals += 1
                print("RSI: ПОКУПКА (вероятность 85%)")
            elif latest['RSI'] > 70:
                sell_signals += 1
                print("RSI: ПРОДАЖА (вероятность 85%)")
            else:
                print("RSI: НЕЙТРАЛЬНО (вероятность 50%)")

        if 'MACD' in latest and 'MACD_Signal' in latest:
            if latest['MACD'] > latest['MACD_Signal']:
                buy_signals += 1
                print("MACD: ПОКУПКА (вероятность 70%)")
            else:
                sell_signals += 1
                print("MACD: ПРОДАЖА (вероятность 70%)")

        if 'SMA_20' in latest and 'SMA_50' in latest:
            if latest['SMA_20'] > latest['SMA_50'] and current_price > latest['SMA_20']:
                buy_signals += 1
                print("SMA: ПОКУПКА (вероятность 65%)")
            elif latest['SMA_20'] < latest['SMA_50'] and current_price < latest['SMA_20']:
                sell_signals += 1
                print("SMA: ПРОДАЖА (вероятность 65%)")

        # Итоговая рекомендация
        print("\n" + "=" * 40)
        print("ИТОГОВАЯ РЕКОМЕНДАЦИЯ")
        print("=" * 40)

        total_signals = buy_signals + sell_signals
        if total_signals == 0:
            final_recommendation = "НЕДОСТАТОЧНО ДАННЫХ"
            confidence = 0
        elif buy_signals > sell_signals:
            final_recommendation = "ПОКУПКА"
            confidence = min(90, 60 + (buy_signals * 15))
        elif sell_signals > buy_signals:
            final_recommendation = "ПРОДАЖА"
            confidence = min(90, 60 + (sell_signals * 15))
        else:
            final_recommendation = "НЕЙТРАЛЬНО"
            confidence = 50

        print(f"СИГНАЛ: {final_recommendation}")
        print(f"УВЕРЕННОСТЬ: {confidence}%")
        print(f"БАЗИС: {buy_signals} сигналов на покупку, {sell_signals} на продажу")

        # Простые прогнозы
        print("\n" + "=" * 40)
        print("КРАТКОСРОЧНЫЕ ПРОГНОЗЫ")
        print("=" * 40)

        short_trend = df['close'].pct_change(periods=24).iloc[-1] * 100 if len(df) >= 24 else 0

        # Различные сценарии
        conservative_pred = current_price * (1 + short_trend / 100 * 0.3)
        aggressive_pred = current_price * (1 + short_trend / 100 * 0.8)

        print(f"Консервативный прогноз: ${conservative_pred:.2f} (изменение: {((conservative_pred-current_price)/current_price)*100:+.1f}%)")
        print(f"Агрессивный прогноз: ${aggressive_pred:.2f} (изменение: {((aggressive_pred-current_price)/current_price)*100:+.1f}%)")

        # Уровни поддержки и сопротивления
        recent_data = df.tail(50) if len(df) >= 50 else df
        support_level = recent_data['low'].min()
        resistance_level = recent_data['high'].max()

        print(f"\nУровень поддержки: ${support_level:.2f}")
        print(f"Уровень сопротивления: ${resistance_level:.2f}")

        # Риски
        volatility = df['close'].pct_change().std() * 100
        if volatility > 3:
            risk_level = "ВЫСОКИЙ"
        elif volatility > 1.5:
            risk_level = "СРЕДНИЙ"
        else:
            risk_level = "НИЗКИЙ"

        print(f"Уровень риска: {risk_level} (волатильность: {volatility:.1f}%)")

        print(f"\nВремя анализа: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        print("\n" + "=" * 60)
        print("ВАЖНО: Это аналитическая информация, а не торговые советы!")
        print("Всегда проводите собственный анализ перед принятием решений.")
        print("=" * 60)

    except Exception as e:
        print(f"ОШИБКА: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Простой анализ криптовалют")
    parser.add_argument('--symbol', '-s', default='BTCUSDT', help='Символ для анализа')
    parser.add_argument('--days', '-d', type=int, default=30, help='Количество дней для анализа')

    args = parser.parse_args()

    analyze_crypto(args.symbol, args.days)