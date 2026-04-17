"""
Терминальный интерфейс для отображения торговых сигналов и анализа
"""

import os
import sys
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pandas as pd
from pathlib import Path

# Добавляем путь к модулям
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.data.binance_client import BinanceClient
from src.data.data_collector import DataCollector
from src.analysis.technical_indicators import TechnicalIndicators
from src.prediction.ml_models import CryptoPricePredictor
from src.utils.config import config

try:
    from colorama import Fore, Back, Style, init
    init()  # Инициализация colorama для Windows
    COLORS_AVAILABLE = True
except ImportError:
    COLORS_AVAILABLE = False
    # Заглушки если colorama не установлена
    class Fore:
        RED = GREEN = YELLOW = BLUE = MAGENTA = CYAN = WHITE = RESET = ""
    class Back:
        RED = GREEN = YELLOW = BLUE = MAGENTA = CYAN = WHITE = RESET = ""
    class Style:
        DIM = NORMAL = BRIGHT = RESET_ALL = ""


class TerminalInterface:
    """Класс для красивого вывода результатов анализа в терминале"""

    def __init__(self):
        self.client = BinanceClient()
        self.collector = DataCollector()

    def clear_screen(self):
        """Очистка экрана"""
        os.system('cls' if os.name == 'nt' else 'clear')

    def print_header(self, title: str):
        """Печать красивого заголовка"""
        width = 80
        print(Fore.CYAN + "=" * width + Style.RESET_ALL)
        print(Fore.CYAN + f"{title:^{width}}" + Style.RESET_ALL)
        print(Fore.CYAN + "=" * width + Style.RESET_ALL)
        print()

    def print_section(self, title: str):
        """Печать заголовка секции"""
        print(Fore.YELLOW + f"\n{'='*10} {title} {'='*10}" + Style.RESET_ALL)

    def print_signal(self, signal_type: str, direction: str, strength: str,
                    reason: str, probability: float = None):
        """
        Печать торгового сигнала

        Args:
            signal_type: Тип сигнала (RSI, MACD, etc.)
            direction: Направление (BUY, SELL, HOLD)
            strength: Сила сигнала (Weak, Medium, Strong)
            reason: Причина сигнала
            probability: Вероятность в процентах
        """
        # Цвета по направлению
        if direction.upper() == 'BUY':
            color = Fore.GREEN
            icon = "📈"
        elif direction.upper() == 'SELL':
            color = Fore.RED
            icon = "📉"
        else:
            color = Fore.YELLOW
            icon = "➡️"

        # Интенсивность по силе
        if strength.upper() == 'STRONG':
            style = Style.BRIGHT
        elif strength.upper() == 'MEDIUM':
            style = Style.NORMAL
        else:
            style = Style.DIM

        print(f"{color}{style}{icon} {signal_type:<15}{Style.RESET_ALL}", end="")
        print(f"{color}{style}{direction:<8}{Style.RESET_ALL}", end="")
        print(f"{color}{style}{strength:<8}{Style.RESET_ALL}", end="")

        if probability:
            print(f"{color}{style}{probability:5.1f}%{Style.RESET_ALL}", end="")

        print(f"  {reason}")

    def print_price_info(self, symbol: str, current_price: float,
                        change_24h: float, volume_24h: float):
        """Печать информации о цене"""
        change_color = Fore.GREEN if change_24h >= 0 else Fore.RED
        change_icon = "▲" if change_24h >= 0 else "▼"

        print(f"\n{Fore.CYAN}💰 {symbol}{Style.RESET_ALL}")
        print(f"   Текущая цена: {Fore.WHITE}{Style.BRIGHT}${current_price:,.2f}{Style.RESET_ALL}")
        print(f"   Изменение 24ч: {change_color}{change_icon} {change_24h:+.2f}%{Style.RESET_ALL}")
        print(f"   Объем 24ч: {Fore.BLUE}${volume_24h:,.0f}{Style.RESET_ALL}")

    def print_technical_summary(self, indicators: Dict):
        """Печать сводки технических индикаторов"""
        print("\n📊 Технические индикаторы:")
        print("-" * 40)

        for name, data in indicators.items():
            value = data.get('value', 'N/A')
            status = data.get('status', 'Unknown')
            color = data.get('color', Fore.WHITE)

            print(f"{name:<15}: {color}{value:<12}{Style.RESET_ALL} {status}")

    def print_predictions(self, predictions: List[Dict]):
        """Печать прогнозов моделей"""
        print("\n🔮 Прогнозы моделей:")
        print("-" * 60)
        print(f"{'Модель':<20} {'Цена':<12} {'Изменение':<12} {'Вероятность':<12}")
        print("-" * 60)

        for pred in predictions:
            model = pred.get('model', 'Unknown')
            price = pred.get('price', 0)
            change = pred.get('change_percent', 0)
            confidence = pred.get('confidence', 0)

            change_color = Fore.GREEN if change >= 0 else Fore.RED
            change_icon = "▲" if change >= 0 else "▼"

            print(f"{model:<20} ${price:<11.2f} {change_color}{change_icon}{change:+5.1f}%{Style.RESET_ALL}     {confidence:5.1f}%")

    def print_risk_analysis(self, risk_data: Dict):
        """Печать анализа рисков"""
        print("\n⚠️ Анализ рисков:")
        print("-" * 30)

        risk_level = risk_data.get('level', 'Unknown')
        volatility = risk_data.get('volatility', 0)
        support = risk_data.get('support_level', 0)
        resistance = risk_data.get('resistance_level', 0)

        # Цвет по уровню риска
        if risk_level.upper() == 'HIGH':
            risk_color = Fore.RED
            risk_icon = "🚨"
        elif risk_level.upper() == 'MEDIUM':
            risk_color = Fore.YELLOW
            risk_icon = "⚠️"
        else:
            risk_color = Fore.GREEN
            risk_icon = "✅"

        print(f"Уровень риска: {risk_color}{risk_icon} {risk_level}{Style.RESET_ALL}")
        print(f"Волатильность: {volatility:.2f}%")
        print(f"Поддержка:     ${support:,.2f}")
        print(f"Сопротивление: ${resistance:,.2f}")

    def analyze_symbol(self, symbol: str, interval: str = '1h', days_back: int = 30):
        """
        Полный анализ символа с красивым выводом

        Args:
            symbol: Торговая пара
            interval: Интервал данных
            days_back: Количество дней истории
        """
        self.clear_screen()
        self.print_header(f"CRYPTO ANALYSIS - {symbol}")

        try:
            # Загрузка данных
            print(f"{Fore.BLUE}🔄 Загрузка данных...{Style.RESET_ALL}")

            end_time = datetime.now()
            start_time = end_time - timedelta(days=days_back)

            df = self.client.get_historical_klines(
                symbol=symbol,
                interval=interval,
                start_time=start_time.isoformat(),
                end_time=end_time.isoformat()
            )

            if df.empty:
                print(f"{Fore.RED}❌ Не удалось загрузить данные для {symbol}{Style.RESET_ALL}")
                return

            # Расчет индикаторов
            print(f"{Fore.BLUE}📊 Расчет технических индикаторов...{Style.RESET_ALL}")
            df_indicators = TechnicalIndicators.calculate_all_indicators(df)

            # 24ч статистика
            ticker = self.client.get_24hr_ticker(symbol)
            current_price = df['close'].iloc[-1]

            if not ticker.empty:
                ticker_data = ticker.iloc[0]
                change_24h = float(ticker_data['priceChangePercent'])
                volume_24h = float(ticker_data['quoteVolume'])
            else:
                change_24h = 0
                volume_24h = 0

            # Вывод информации о цене
            self.print_price_info(symbol, current_price, change_24h, volume_24h)

            # Генерация торговых сигналов
            signals = self.generate_trading_signals(df_indicators)

            self.print_section("ТОРГОВЫЕ СИГНАЛЫ")
            print(f"{'Индикатор':<15} {'Сигнал':<8} {'Сила':<8} {'Вер-ть':<6} Причина")
            print("-" * 70)

            for signal in signals:
                self.print_signal(
                    signal['indicator'],
                    signal['direction'],
                    signal['strength'],
                    signal['reason'],
                    signal.get('probability')
                )

            # Технические индикаторы
            indicators_summary = self.generate_indicators_summary(df_indicators)
            self.print_technical_summary(indicators_summary)

            # Простые прогнозы
            predictions = self.generate_simple_predictions(df_indicators, symbol)
            self.print_predictions(predictions)

            # Анализ рисков
            risk_analysis = self.calculate_risk_metrics(df_indicators)
            self.print_risk_analysis(risk_analysis)

            # Общий вывод
            self.print_section("ОБЩИЙ ВЫВОД")
            overall_signal = self.calculate_overall_signal(signals)

            if overall_signal['direction'].upper() == 'BUY':
                conclusion_color = Fore.GREEN
                conclusion_icon = "📈"
            elif overall_signal['direction'].upper() == 'SELL':
                conclusion_color = Fore.RED
                conclusion_icon = "📉"
            else:
                conclusion_color = Fore.YELLOW
                conclusion_icon = "➡️"

            print(f"\n{conclusion_color}{Style.BRIGHT}{conclusion_icon} РЕКОМЕНДАЦИЯ: {overall_signal['direction']}{Style.RESET_ALL}")
            print(f"Уверенность: {overall_signal['confidence']:.1f}%")
            print(f"Основание: {overall_signal['reason']}")

            # Время анализа
            print(f"\n{Fore.CYAN}⏰ Время анализа: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Style.RESET_ALL}")

        except Exception as e:
            print(f"{Fore.RED}❌ Ошибка при анализе: {str(e)}{Style.RESET_ALL}")

    def generate_trading_signals(self, df) -> List[Dict]:
        """Генерация торговых сигналов"""
        latest = df.iloc[-1]
        signals = []

        # RSI сигнал
        if 'RSI' in latest:
            rsi = latest['RSI']
            if rsi > 70:
                signals.append({
                    'indicator': 'RSI',
                    'direction': 'SELL',
                    'strength': 'Strong',
                    'reason': f'Перекупленность (RSI: {rsi:.1f})',
                    'probability': min(95, 70 + (rsi - 70) * 2)
                })
            elif rsi < 30:
                signals.append({
                    'indicator': 'RSI',
                    'direction': 'BUY',
                    'strength': 'Strong',
                    'reason': f'Перепроданность (RSI: {rsi:.1f})',
                    'probability': min(95, 70 + (30 - rsi) * 2)
                })
            else:
                signals.append({
                    'indicator': 'RSI',
                    'direction': 'HOLD',
                    'strength': 'Weak',
                    'reason': f'Нейтральная зона (RSI: {rsi:.1f})',
                    'probability': 50
                })

        # MACD сигнал
        if 'MACD' in latest and 'MACD_Signal' in latest:
            macd_bullish = latest['MACD'] > latest['MACD_Signal']
            strength = 'Strong' if abs(latest['MACD'] - latest['MACD_Signal']) > 0.01 else 'Medium'

            if macd_bullish:
                signals.append({
                    'indicator': 'MACD',
                    'direction': 'BUY',
                    'strength': strength,
                    'reason': 'MACD выше сигнальной линии',
                    'probability': 75 if strength == 'Strong' else 65
                })
            else:
                signals.append({
                    'indicator': 'MACD',
                    'direction': 'SELL',
                    'strength': strength,
                    'reason': 'MACD ниже сигнальной линии',
                    'probability': 75 if strength == 'Strong' else 65
                })

        # Bollinger Bands сигнал
        if 'BB_Upper' in latest and 'BB_Lower' in latest:
            price = latest['close']
            if price > latest['BB_Upper']:
                signals.append({
                    'indicator': 'Bollinger',
                    'direction': 'SELL',
                    'strength': 'Medium',
                    'reason': 'Цена выше верхней полосы',
                    'probability': 70
                })
            elif price < latest['BB_Lower']:
                signals.append({
                    'indicator': 'Bollinger',
                    'direction': 'BUY',
                    'strength': 'Medium',
                    'reason': 'Цена ниже нижней полосы',
                    'probability': 70
                })

        # SMA тренд
        if 'SMA_20' in latest and 'SMA_50' in latest:
            sma20_above_sma50 = latest['SMA_20'] > latest['SMA_50']
            price_above_sma20 = latest['close'] > latest['SMA_20']

            if sma20_above_sma50 and price_above_sma20:
                signals.append({
                    'indicator': 'SMA Trend',
                    'direction': 'BUY',
                    'strength': 'Medium',
                    'reason': 'Восходящий тренд',
                    'probability': 65
                })
            elif not sma20_above_sma50 and not price_above_sma20:
                signals.append({
                    'indicator': 'SMA Trend',
                    'direction': 'SELL',
                    'strength': 'Medium',
                    'reason': 'Нисходящий тренд',
                    'probability': 65
                })

        return signals

    def generate_indicators_summary(self, df) -> Dict:
        """Генерация сводки индикаторов"""
        latest = df.iloc[-1]
        indicators = {}

        if 'RSI' in latest:
            rsi = latest['RSI']
            if rsi > 70:
                status = "Перекупленность"
                color = Fore.RED
            elif rsi < 30:
                status = "Перепроданность"
                color = Fore.GREEN
            else:
                status = "Нормальная зона"
                color = Fore.YELLOW
            indicators['RSI'] = {'value': f'{rsi:.1f}', 'status': status, 'color': color}

        if 'MACD' in latest:
            macd = latest['MACD']
            status = "Бычий тренд" if macd > 0 else "Медвежий тренд"
            color = Fore.GREEN if macd > 0 else Fore.RED
            indicators['MACD'] = {'value': f'{macd:.4f}', 'status': status, 'color': color}

        if 'ATR' in latest:
            atr = latest['ATR']
            atr_pct = (atr / latest['close']) * 100
            if atr_pct > 2:
                status = "Высокая волатильность"
                color = Fore.RED
            elif atr_pct < 1:
                status = "Низкая волатильность"
                color = Fore.GREEN
            else:
                status = "Средняя волатильность"
                color = Fore.YELLOW
            indicators['ATR'] = {'value': f'{atr:.2f}', 'status': status, 'color': color}

        return indicators

    def generate_simple_predictions(self, df, symbol) -> List[Dict]:
        """Простые прогнозы на основе трендов"""
        current_price = df['close'].iloc[-1]

        # Расчет трендов
        short_trend = df['close'].pct_change(periods=24).iloc[-1] * 100  # 24 периода назад
        long_trend = df['close'].pct_change(periods=168).iloc[-1] * 100  # 7 дней назад
        volatility = df['close'].pct_change().std() * 100

        predictions = []

        # Трендовая модель
        trend_pred = current_price * (1 + short_trend / 100 * 0.1)
        predictions.append({
            'model': 'Трендовая',
            'price': trend_pred,
            'change_percent': ((trend_pred - current_price) / current_price) * 100,
            'confidence': min(80, 60 + abs(short_trend))
        })

        # Консервативная модель
        conservative_pred = current_price * (1 + short_trend / 100 * 0.05)
        predictions.append({
            'model': 'Консервативная',
            'price': conservative_pred,
            'change_percent': ((conservative_pred - current_price) / current_price) * 100,
            'confidence': 75
        })

        # Модель волатильности
        vol_pred = current_price * (1 + (short_trend + volatility * 0.5) / 100 * 0.08)
        predictions.append({
            'model': 'Волатильность',
            'price': vol_pred,
            'change_percent': ((vol_pred - current_price) / current_price) * 100,
            'confidence': max(45, 70 - volatility)
        })

        return predictions

    def calculate_risk_metrics(self, df) -> Dict:
        """Расчет метрик риска"""
        current_price = df['close'].iloc[-1]

        # Волатильность
        volatility = df['close'].pct_change().std() * 100 * (252 ** 0.5)  # Годовая

        # Простые уровни поддержки и сопротивления
        recent_data = df.tail(50)  # Последние 50 периодов
        support = recent_data['low'].min()
        resistance = recent_data['high'].max()

        # Уровень риска
        if volatility > 50:
            risk_level = 'HIGH'
        elif volatility > 25:
            risk_level = 'MEDIUM'
        else:
            risk_level = 'LOW'

        return {
            'level': risk_level,
            'volatility': volatility,
            'support_level': support,
            'resistance_level': resistance
        }

    def calculate_overall_signal(self, signals) -> Dict:
        """Расчет общего сигнала"""
        if not signals:
            return {'direction': 'HOLD', 'confidence': 0, 'reason': 'Недостаточно данных'}

        buy_count = sum(1 for s in signals if s['direction'] == 'BUY')
        sell_count = sum(1 for s in signals if s['direction'] == 'SELL')

        # Взвешенная оценка по вероятностям
        buy_weight = sum(s.get('probability', 50) for s in signals if s['direction'] == 'BUY')
        sell_weight = sum(s.get('probability', 50) for s in signals if s['direction'] == 'SELL')

        if buy_weight > sell_weight:
            direction = 'BUY'
            confidence = min(95, buy_weight / len(signals))
            reason = f'Преобладают сигналы на покупку ({buy_count} из {len(signals)})'
        elif sell_weight > buy_weight:
            direction = 'SELL'
            confidence = min(95, sell_weight / len(signals))
            reason = f'Преобладают сигналы на продажу ({sell_count} из {len(signals)})'
        else:
            direction = 'HOLD'
            confidence = 50
            reason = 'Противоречивые сигналы'

        return {
            'direction': direction,
            'confidence': confidence,
            'reason': reason
        }

    def run_live_monitor(self, symbols: List[str], interval: int = 300):
        """
        Запуск мониторинга в реальном времени

        Args:
            symbols: Список символов для мониторинга
            interval: Интервал обновления в секундах
        """
        print(f"{Fore.GREEN}🚀 Запуск мониторинга в реальном времени{Style.RESET_ALL}")
        print(f"Символы: {', '.join(symbols)}")
        print(f"Интервал обновления: {interval} секунд")
        print(f"Нажмите Ctrl+C для остановки\n")

        try:
            while True:
                for symbol in symbols:
                    self.analyze_symbol(symbol, '1h', 7)  # Быстрый анализ за неделю

                    if len(symbols) > 1:
                        print(f"\n{Fore.BLUE}Следующее обновление через {interval} секунд...{Style.RESET_ALL}")
                        time.sleep(interval)

                if len(symbols) == 1:
                    print(f"\n{Fore.BLUE}Следующее обновление через {interval} секунд...{Style.RESET_ALL}")
                    time.sleep(interval)

        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}👋 Мониторинг остановлен{Style.RESET_ALL}")


if __name__ == "__main__":
    # Пример использования
    interface = TerminalInterface()

    # Анализ одного символа
    interface.analyze_symbol('BTCUSDT')

    input(f"\n{Fore.CYAN}Нажмите Enter для продолжения...{Style.RESET_ALL}")

    # Можно запустить мониторинг
    # interface.run_live_monitor(['BTCUSDT', 'ETHUSDT'], interval=60)