#!/usr/bin/env python3
"""
Главный файл системы анализа и прогнозирования криптовалют

Пример использования:
    python main.py --collect-data --symbols BTCUSDT ETHUSDT --intervals 1h 4h
    python main.py --train-models --symbol BTCUSDT
    python main.py --predict --symbol BTCUSDT --horizon 24
"""

import sys
import argparse
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Optional

# Добавляем текущую директорию в путь
sys.path.append(str(Path(__file__).parent))

from src.utils.config import config
from src.data.binance_client import BinanceClient
from src.data.data_collector import DataCollector
from src.analysis.technical_indicators import TechnicalIndicators
from src.prediction.ml_models import CryptoPricePredictor


def setup_logging():
    """Настройка системы логирования"""
    config.LOG_DIR.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(config.LOG_FILE, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )

    return logging.getLogger(__name__)


def collect_data(symbols: List[str], intervals: List[str], days_back: int = 365):
    """
    Сбор исторических данных

    Args:
        symbols: Список торговых пар
        intervals: Список интервалов
        days_back: Количество дней для загрузки
    """
    logger = logging.getLogger(__name__)
    logger.info(f"🔄 Начинаем сбор данных для {len(symbols)} символов")

    try:
        collector = DataCollector()

        # Проверка подключения
        if not collector.binance_client.test_connectivity():
            logger.error("❌ Не удалось подключиться к Binance API")
            return False

        # Сбор данных
        collected_data = collector.collect_historical_data(
            symbols=symbols,
            intervals=intervals,
            days_back=days_back,
            save_to_db=True,
            save_to_csv=True
        )

        if collected_data:
            logger.info(f"✅ Успешно собраны данные для {len(collected_data)} наборов")

            # Информация о собранных данных
            info_df = collector.get_available_data_info()
            print("\n📊 Информация о собранных данных:")
            print(info_df)
            return True
        else:
            logger.error("❌ Не удалось собрать данные")
            return False

    except Exception as e:
        logger.error(f"❌ Ошибка при сборе данных: {e}")
        return False


def train_models(symbol: str, interval: str = '1h', test_lstm: bool = False):
    """
    Обучение моделей машинного обучения

    Args:
        symbol: Торговая пара
        interval: Интервал данных
        test_lstm: Обучать ли LSTM модель
    """
    logger = logging.getLogger(__name__)
    logger.info(f"🤖 Начинаем обучение моделей для {symbol}")

    try:
        # Загрузка данных
        collector = DataCollector()
        df = collector.load_data_from_db(symbol, interval)

        if df.empty:
            logger.error(f"❌ Нет данных для {symbol} с интервалом {interval}")
            logger.info("Попробуйте сначала собрать данные: python main.py --collect-data")
            return False

        # Расчет технических индикаторов
        logger.info("📈 Расчет технических индикаторов...")
        df_with_indicators = TechnicalIndicators.calculate_all_indicators(df)

        # Инициализация предсказателя
        predictor = CryptoPricePredictor()

        # Подготовка данных
        logger.info("🔍 Подготовка признаков...")
        features_df = predictor.prepare_features(df_with_indicators)

        if features_df.empty:
            logger.error("❌ Не удалось подготовить признаки")
            return False

        # Целевая переменная (будущая цена)
        target = features_df['close'].shift(-1).dropna()
        features_df = features_df[:-1]

        # Традиционные модели
        feature_columns = features_df.select_dtypes(include=['number']).columns
        X = features_df[feature_columns].fillna(0)

        logger.info("🎯 Обучение традиционных ML моделей...")
        results = predictor.train_traditional_models(X, target)

        if results:
            # Показать производительность
            performance = predictor.get_model_performance()
            print("\n📊 Производительность моделей:")
            print(performance.to_string(index=False))

            # Найти лучшую модель
            best_model = performance.iloc[0]['Model']
            best_rmse = performance.iloc[0]['RMSE']
            logger.info(f"🏆 Лучшая модель: {best_model} (RMSE: {best_rmse:.4f})")

        # LSTM модель (опционально)
        if test_lstm:
            try:
                logger.info("🧠 Обучение LSTM модели...")
                X_lstm, y_lstm = predictor.prepare_lstm_data(df_with_indicators)
                lstm_results = predictor.train_lstm_model(X_lstm, y_lstm)

                if lstm_results:
                    logger.info(f"🧠 LSTM - RMSE: {lstm_results['rmse']:.4f}")

            except Exception as e:
                logger.warning(f"⚠️ Не удалось обучить LSTM: {e}")

        # Сохранение моделей
        logger.info("💾 Сохранение моделей...")
        predictor.save_models()

        logger.info("✅ Обучение моделей завершено")
        return True

    except Exception as e:
        logger.error(f"❌ Ошибка при обучении моделей: {e}")
        return False


def make_prediction(symbol: str, interval: str = '1h', horizon: int = 24):
    """
    Создание прогноза

    Args:
        symbol: Торговая пара
        interval: Интервал данных
        horizon: Горизонт прогноза в часах
    """
    logger = logging.getLogger(__name__)
    logger.info(f"🔮 Создание прогноза для {symbol} на {horizon} часов")

    try:
        # Загрузка последних данных
        collector = DataCollector()
        end_time = datetime.now()
        start_time = end_time - timedelta(days=30)  # Последние 30 дней

        df = collector.load_data_from_db(
            symbol, interval, start_time, end_time
        )

        if df.empty:
            logger.error(f"❌ Нет данных для {symbol}")
            return False

        # Расчет технических индикаторов
        df_with_indicators = TechnicalIndicators.calculate_all_indicators(df)

        # Подготовка признаков
        predictor = CryptoPricePredictor()
        features_df = predictor.prepare_features(df_with_indicators)

        if features_df.empty:
            logger.error("❌ Не удалось подготовить признаки")
            return False

        # Получение последних признаков
        latest_features = features_df.tail(1)
        feature_columns = latest_features.select_dtypes(include=['number']).columns
        latest_features_clean = latest_features[feature_columns].fillna(0)

        # Создание фиктивных моделей для демонстрации
        # В реальном использовании здесь будет загрузка сохраненных моделей
        logger.info("📊 Создание демо-прогнозов...")

        current_price = df['close'].iloc[-1]

        # Простые прогнозы для демонстрации
        predictions = {
            'Текущая цена': current_price,
            'Простой тренд (+1%)': current_price * 1.01,
            'Консервативный (+0.5%)': current_price * 1.005,
            'Медвежий (-0.5%)': current_price * 0.995,
            'Бычий (+2%)': current_price * 1.02
        }

        print(f"\n🔮 Прогнозы для {symbol} (горизонт: {horizon}ч):")
        print("-" * 50)

        for model_name, pred_price in predictions.items():
            change_pct = ((pred_price - current_price) / current_price) * 100
            direction = "📈" if change_pct > 0 else "📉" if change_pct < 0 else "➡️"
            print(f"{direction} {model_name}: ${pred_price:.2f} ({change_pct:+.2f}%)")

        # Технический анализ
        latest_data = df_with_indicators.iloc[-1]

        print(f"\n📊 Текущие технические индикаторы:")
        print("-" * 40)

        if 'RSI' in latest_data:
            rsi = latest_data['RSI']
            rsi_signal = "Перекупленность" if rsi > 70 else "Перепроданность" if rsi < 30 else "Нейтрально"
            print(f"RSI: {rsi:.2f} - {rsi_signal}")

        if 'MACD' in latest_data and 'MACD_Signal' in latest_data:
            macd_signal = "Бычий" if latest_data['MACD'] > latest_data['MACD_Signal'] else "Медвежий"
            print(f"MACD: {macd_signal} сигнал")

        if 'BB_Upper' in latest_data and 'BB_Lower' in latest_data:
            bb_position = "Верхняя полоса" if current_price > latest_data['BB_Upper'] else \
                         "Нижняя полоса" if current_price < latest_data['BB_Lower'] else \
                         "Средняя зона"
            print(f"Bollinger Bands: {bb_position}")

        logger.info("✅ Прогноз создан")
        return True

    except Exception as e:
        logger.error(f"❌ Ошибка при создании прогноза: {e}")
        return False


def update_data(symbols: List[str], intervals: List[str]):
    """
    Обновление данных до последнего времени

    Args:
        symbols: Список символов
        intervals: Список интервалов
    """
    logger = logging.getLogger(__name__)
    logger.info(f"🔄 Обновление данных для {len(symbols)} символов")

    try:
        collector = DataCollector()
        collector.update_latest_data(symbols, intervals)

        # Показать обновленную информацию
        info_df = collector.get_available_data_info()
        print("\n📊 Обновленная информация о данных:")
        print(info_df.to_string(index=False))

        logger.info("✅ Данные обновлены")
        return True

    except Exception as e:
        logger.error(f"❌ Ошибка при обновлении данных: {e}")
        return False


def show_portfolio_analysis():
    """Показать анализ портфеля (демо-функция)"""
    logger = logging.getLogger(__name__)
    logger.info("📊 Анализ портфеля")

    try:
        # Получение информации о топ символах
        client = BinanceClient()

        if not client.test_connectivity():
            logger.error("❌ Не удалось подключиться к Binance API")
            return False

        # 24ч статистика для топ символов
        top_symbols = config.get_symbols_by_category('major')

        print(f"\n📈 24-часовая статистика для основных криптовалют:")
        print("-" * 70)

        for symbol in top_symbols:
            try:
                ticker = client.get_24hr_ticker(symbol)
                if not ticker.empty:
                    data = ticker.iloc[0]
                    price = float(data['lastPrice'])
                    change = float(data['priceChangePercent'])
                    volume = float(data['volume'])

                    direction = "📈" if change > 0 else "📉"
                    print(f"{direction} {symbol:<12} ${price:>10.2f} ({change:>+6.2f}%) Vol: {volume:,.0f}")

            except Exception as e:
                logger.warning(f"Не удалось получить данные для {symbol}: {e}")

        return True

    except Exception as e:
        logger.error(f"❌ Ошибка анализа портфеля: {e}")
        return False


def main():
    """Главная функция"""
    parser = argparse.ArgumentParser(
        description="Система анализа и прогнозирования криптовалют"
    )

    # Основные команды
    parser.add_argument('--collect-data', action='store_true',
                       help='Собрать исторические данные')
    parser.add_argument('--update-data', action='store_true',
                       help='Обновить данные')
    parser.add_argument('--train-models', action='store_true',
                       help='Обучить модели ML')
    parser.add_argument('--predict', action='store_true',
                       help='Создать прогноз')
    parser.add_argument('--portfolio', action='store_true',
                       help='Анализ портфеля')
    parser.add_argument('--config', action='store_true',
                       help='Показать конфигурацию')

    # Параметры
    parser.add_argument('--symbols', nargs='+',
                       default=config.DEFAULT_SYMBOLS,
                       help='Список торговых пар')
    parser.add_argument('--intervals', nargs='+',
                       default=config.DEFAULT_INTERVALS,
                       help='Список интервалов времени')
    parser.add_argument('--symbol', type=str, default='BTCUSDT',
                       help='Торговая пара для обучения/прогноза')
    parser.add_argument('--interval', type=str, default='1h',
                       help='Интервал времени')
    parser.add_argument('--horizon', type=int,
                       default=config.PREDICTION_HORIZON_HOURS,
                       help='Горизонт прогноза в часах')
    parser.add_argument('--days-back', type=int, default=365,
                       help='Количество дней для загрузки')
    parser.add_argument('--lstm', action='store_true',
                       help='Включить обучение LSTM')

    args = parser.parse_args()

    # Настройка логирования
    logger = setup_logging()

    # Показать конфигурацию при запуске
    if args.config or (not any([args.collect_data, args.update_data,
                                args.train_models, args.predict, args.portfolio])):
        config.print_config_summary()
        return

    success = True

    # Выполнение команд
    if args.collect_data:
        success &= collect_data(args.symbols, args.intervals, args.days_back)

    if args.update_data:
        success &= update_data(args.symbols, args.intervals)

    if args.train_models:
        success &= train_models(args.symbol, args.interval, args.lstm)

    if args.predict:
        success &= make_prediction(args.symbol, args.interval, args.horizon)

    if args.portfolio:
        success &= show_portfolio_analysis()

    if success:
        logger.info("✅ Все операции выполнены успешно")
    else:
        logger.error("❌ Некоторые операции завершились с ошибками")
        sys.exit(1)


if __name__ == "__main__":
    main()