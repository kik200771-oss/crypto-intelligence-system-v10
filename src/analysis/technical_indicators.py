"""
Модуль для расчета технических индикаторов
"""

import pandas as pd
import numpy as np
from typing import Union, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')


class TechnicalIndicators:
    """Класс для расчета технических индикаторов"""

    @staticmethod
    def sma(data: pd.Series, period: int = 20) -> pd.Series:
        """
        Simple Moving Average (Простая скользящая средняя)

        Args:
            data: Серия цен
            period: Период для расчета

        Returns:
            Серия SMA
        """
        return data.rolling(window=period).mean()

    @staticmethod
    def ema(data: pd.Series, period: int = 20, alpha: Optional[float] = None) -> pd.Series:
        """
        Exponential Moving Average (Экспоненциальная скользящая средняя)

        Args:
            data: Серия цен
            period: Период для расчета
            alpha: Фактор сглаживания (если None, вычисляется автоматически)

        Returns:
            Серия EMA
        """
        if alpha is None:
            alpha = 2 / (period + 1)
        return data.ewm(alpha=alpha).mean()

    @staticmethod
    def rsi(data: pd.Series, period: int = 14) -> pd.Series:
        """
        Relative Strength Index (Индекс относительной силы)

        Args:
            data: Серия цен закрытия
            period: Период для расчета

        Returns:
            Серия RSI (0-100)
        """
        delta = data.diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)

        avg_gain = gain.rolling(window=period).mean()
        avg_loss = loss.rolling(window=period).mean()

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        return rsi

    @staticmethod
    def macd(data: pd.Series, fast_period: int = 12, slow_period: int = 26, signal_period: int = 9) -> pd.DataFrame:
        """
        MACD (Moving Average Convergence Divergence)

        Args:
            data: Серия цен закрытия
            fast_period: Период быстрой EMA
            slow_period: Период медленной EMA
            signal_period: Период сигнальной линии

        Returns:
            DataFrame с MACD, Signal и Histogram
        """
        ema_fast = TechnicalIndicators.ema(data, fast_period)
        ema_slow = TechnicalIndicators.ema(data, slow_period)

        macd_line = ema_fast - ema_slow
        signal_line = TechnicalIndicators.ema(macd_line, signal_period)
        histogram = macd_line - signal_line

        return pd.DataFrame({
            'MACD': macd_line,
            'Signal': signal_line,
            'Histogram': histogram
        })

    @staticmethod
    def bollinger_bands(data: pd.Series, period: int = 20, std_dev: float = 2) -> pd.DataFrame:
        """
        Bollinger Bands (Полосы Боллинджера)

        Args:
            data: Серия цен
            period: Период для расчета
            std_dev: Количество стандартных отклонений

        Returns:
            DataFrame с Upper, Middle, Lower полосами
        """
        middle = TechnicalIndicators.sma(data, period)
        std = data.rolling(window=period).std()

        upper = middle + (std * std_dev)
        lower = middle - (std * std_dev)

        return pd.DataFrame({
            'Upper': upper,
            'Middle': middle,
            'Lower': lower
        })

    @staticmethod
    def stochastic(high: pd.Series, low: pd.Series, close: pd.Series,
                   k_period: int = 14, d_period: int = 3) -> pd.DataFrame:
        """
        Stochastic Oscillator (Стохастический осциллятор)

        Args:
            high: Серия максимальных цен
            low: Серия минимальных цен
            close: Серия цен закрытия
            k_period: Период для %K
            d_period: Период для %D

        Returns:
            DataFrame с %K и %D
        """
        lowest_low = low.rolling(window=k_period).min()
        highest_high = high.rolling(window=k_period).max()

        k_percent = 100 * ((close - lowest_low) / (highest_high - lowest_low))
        d_percent = k_percent.rolling(window=d_period).mean()

        return pd.DataFrame({
            'K': k_percent,
            'D': d_percent
        })

    @staticmethod
    def atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
        """
        Average True Range (Средний истинный диапазон)

        Args:
            high: Серия максимальных цен
            low: Серия минимальных цен
            close: Серия цен закрытия
            period: Период для расчета

        Returns:
            Серия ATR
        """
        prev_close = close.shift(1)

        tr1 = high - low
        tr2 = abs(high - prev_close)
        tr3 = abs(low - prev_close)

        true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = true_range.rolling(window=period).mean()

        return atr

    @staticmethod
    def williams_r(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
        """
        Williams %R

        Args:
            high: Серия максимальных цен
            low: Серия минимальных цен
            close: Серия цен закрытия
            period: Период для расчета

        Returns:
            Серия Williams %R (-100 до 0)
        """
        highest_high = high.rolling(window=period).max()
        lowest_low = low.rolling(window=period).min()

        williams_r = -100 * ((highest_high - close) / (highest_high - lowest_low))

        return williams_r

    @staticmethod
    def cci(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 20) -> pd.Series:
        """
        Commodity Channel Index (Индекс товарного канала)

        Args:
            high: Серия максимальных цен
            low: Серия минимальных цен
            close: Серия цен закрытия
            period: Период для расчета

        Returns:
            Серия CCI
        """
        typical_price = (high + low + close) / 3
        sma_tp = typical_price.rolling(window=period).mean()

        mean_deviation = typical_price.rolling(window=period).apply(
            lambda x: np.mean(np.abs(x - x.mean()))
        )

        cci = (typical_price - sma_tp) / (0.015 * mean_deviation)

        return cci

    @staticmethod
    def adx(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.DataFrame:
        """
        Average Directional Index (Средний направленный индекс)

        Args:
            high: Серия максимальных цен
            low: Серия минимальных цен
            close: Серия цен закрытия
            period: Период для расчета

        Returns:
            DataFrame с ADX, +DI, -DI
        """
        # True Range
        atr_values = TechnicalIndicators.atr(high, low, close, period)

        # Directional Movement
        up_move = high - high.shift(1)
        down_move = low.shift(1) - low

        plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0)
        minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0)

        plus_dm = pd.Series(plus_dm, index=high.index).rolling(window=period).sum()
        minus_dm = pd.Series(minus_dm, index=high.index).rolling(window=period).sum()

        # Directional Indicators
        plus_di = 100 * (plus_dm / atr_values)
        minus_di = 100 * (minus_dm / atr_values)

        # ADX
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.rolling(window=period).mean()

        return pd.DataFrame({
            'ADX': adx,
            'Plus_DI': plus_di,
            'Minus_DI': minus_di
        })

    @staticmethod
    def fibonacci_retracement(high_price: float, low_price: float) -> dict:
        """
        Уровни коррекции Фибоначчи

        Args:
            high_price: Максимальная цена
            low_price: Минимальная цена

        Returns:
            Словарь с уровнями Фибоначчи
        """
        price_range = high_price - low_price

        levels = {
            '0.0%': high_price,
            '23.6%': high_price - (price_range * 0.236),
            '38.2%': high_price - (price_range * 0.382),
            '50.0%': high_price - (price_range * 0.5),
            '61.8%': high_price - (price_range * 0.618),
            '78.6%': high_price - (price_range * 0.786),
            '100.0%': low_price
        }

        return levels

    @staticmethod
    def pivot_points(high: float, low: float, close: float) -> dict:
        """
        Точки разворота (Pivot Points)

        Args:
            high: Максимальная цена предыдущего дня
            low: Минимальная цена предыдущего дня
            close: Цена закрытия предыдущего дня

        Returns:
            Словарь с уровнями поддержки и сопротивления
        """
        pivot = (high + low + close) / 3

        r1 = (2 * pivot) - low
        s1 = (2 * pivot) - high

        r2 = pivot + (high - low)
        s2 = pivot - (high - low)

        r3 = high + 2 * (pivot - low)
        s3 = low - 2 * (high - pivot)

        return {
            'Pivot': pivot,
            'R1': r1, 'R2': r2, 'R3': r3,
            'S1': s1, 'S2': s2, 'S3': s3
        }

    @classmethod
    def calculate_all_indicators(cls, df: pd.DataFrame) -> pd.DataFrame:
        """
        Расчет всех основных технических индикаторов

        Args:
            df: DataFrame с OHLCV данными

        Returns:
            DataFrame с добавленными индикаторами
        """
        result = df.copy()

        try:
            # Скользящие средние
            result['SMA_20'] = cls.sma(df['close'], 20)
            result['SMA_50'] = cls.sma(df['close'], 50)
            result['EMA_12'] = cls.ema(df['close'], 12)
            result['EMA_26'] = cls.ema(df['close'], 26)

            # RSI
            result['RSI'] = cls.rsi(df['close'])

            # MACD
            macd_data = cls.macd(df['close'])
            result['MACD'] = macd_data['MACD']
            result['MACD_Signal'] = macd_data['Signal']
            result['MACD_Histogram'] = macd_data['Histogram']

            # Bollinger Bands
            bb_data = cls.bollinger_bands(df['close'])
            result['BB_Upper'] = bb_data['Upper']
            result['BB_Middle'] = bb_data['Middle']
            result['BB_Lower'] = bb_data['Lower']

            # Stochastic
            stoch_data = cls.stochastic(df['high'], df['low'], df['close'])
            result['Stoch_K'] = stoch_data['K']
            result['Stoch_D'] = stoch_data['D']

            # ATR
            result['ATR'] = cls.atr(df['high'], df['low'], df['close'])

            # Williams %R
            result['Williams_R'] = cls.williams_r(df['high'], df['low'], df['close'])

            # CCI
            result['CCI'] = cls.cci(df['high'], df['low'], df['close'])

            # ADX
            adx_data = cls.adx(df['high'], df['low'], df['close'])
            result['ADX'] = adx_data['ADX']
            result['Plus_DI'] = adx_data['Plus_DI']
            result['Minus_DI'] = adx_data['Minus_DI']

            # Дополнительные расчеты
            result['Price_Change'] = df['close'].pct_change()
            result['Volume_SMA'] = cls.sma(df['volume'], 20)
            result['High_Low_Pct'] = ((df['high'] - df['low']) / df['close']) * 100

            # Сигналы
            result['RSI_Overbought'] = result['RSI'] > 70
            result['RSI_Oversold'] = result['RSI'] < 30
            result['MACD_Bullish'] = result['MACD'] > result['MACD_Signal']
            result['BB_Squeeze'] = (result['BB_Upper'] - result['BB_Lower']) < (result['BB_Middle'] * 0.1)

        except Exception as e:
            print(f"Ошибка при расчете индикаторов: {e}")

        return result


if __name__ == "__main__":
    # Пример использования
    import matplotlib.pyplot as plt

    # Создание тестовых данных
    np.random.seed(42)
    dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')

    # Симуляция цен
    price = 100
    prices = []
    highs = []
    lows = []
    volumes = []

    for _ in range(len(dates)):
        change = np.random.normal(0, 0.02)
        price = price * (1 + change)

        high = price * (1 + abs(np.random.normal(0, 0.01)))
        low = price * (1 - abs(np.random.normal(0, 0.01)))
        volume = np.random.randint(1000, 10000)

        prices.append(price)
        highs.append(high)
        lows.append(low)
        volumes.append(volume)

    df = pd.DataFrame({
        'open': prices,
        'high': highs,
        'low': lows,
        'close': prices,
        'volume': volumes
    }, index=dates)

    # Расчет индикаторов
    indicators = TechnicalIndicators()
    df_with_indicators = indicators.calculate_all_indicators(df)

    print("📊 Рассчитанные технические индикаторы:")
    print(df_with_indicators[['close', 'RSI', 'MACD', 'BB_Upper', 'BB_Lower']].tail())

    # Простая визуализация
    fig, axes = plt.subplots(3, 1, figsize=(12, 10))

    # Цена и Bollinger Bands
    axes[0].plot(df_with_indicators.index, df_with_indicators['close'], label='Close')
    axes[0].plot(df_with_indicators.index, df_with_indicators['BB_Upper'], label='BB Upper')
    axes[0].plot(df_with_indicators.index, df_with_indicators['BB_Lower'], label='BB Lower')
    axes[0].set_title('Price and Bollinger Bands')
    axes[0].legend()

    # RSI
    axes[1].plot(df_with_indicators.index, df_with_indicators['RSI'])
    axes[1].axhline(y=70, color='r', linestyle='--', label='Overbought')
    axes[1].axhline(y=30, color='g', linestyle='--', label='Oversold')
    axes[1].set_title('RSI')
    axes[1].legend()

    # MACD
    axes[2].plot(df_with_indicators.index, df_with_indicators['MACD'], label='MACD')
    axes[2].plot(df_with_indicators.index, df_with_indicators['MACD_Signal'], label='Signal')
    axes[2].bar(df_with_indicators.index, df_with_indicators['MACD_Histogram'],
                alpha=0.3, label='Histogram')
    axes[2].set_title('MACD')
    axes[2].legend()

    plt.tight_layout()
    plt.savefig('data/technical_indicators_example.png')
    print("📈 График сохранен в data/technical_indicators_example.png")