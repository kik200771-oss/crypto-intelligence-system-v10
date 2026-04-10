"""
Модуль конфигурации системы
"""

import os
from pathlib import Path
from typing import List, Dict, Any
import yaml
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv(Path(__file__).parent.parent.parent / 'config' / '.env')


class Config:
    """Класс конфигурации системы"""

    # Пути
    BASE_DIR = Path(__file__).parent.parent.parent
    DATA_DIR = BASE_DIR / 'data'
    MODEL_DIR = DATA_DIR / 'models'
    LOG_DIR = BASE_DIR / 'logs'

    # Binance API
    BINANCE_API_KEY = os.getenv('BINANCE_API_KEY')
    BINANCE_SECRET_KEY = os.getenv('BINANCE_SECRET_KEY')

    # База данных
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///data/crypto_data.db')

    # Символы и интервалы по умолчанию
    DEFAULT_SYMBOLS = os.getenv('DEFAULT_SYMBOLS', 'BTCUSDT,ETHUSDT,ADAUSDT').split(',')
    DEFAULT_INTERVALS = os.getenv('DEFAULT_INTERVALS', '1m,5m,15m,1h,4h,1d').split(',')

    # ML параметры
    MODEL_SAVE_PATH = os.getenv('MODEL_SAVE_PATH', str(MODEL_DIR))
    PREDICTION_HORIZON_HOURS = int(os.getenv('PREDICTION_HORIZON_HOURS', 24))
    BACKTESTING_PERIOD_DAYS = int(os.getenv('BACKTESTING_PERIOD_DAYS', 365))

    # Логирование
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', str(LOG_DIR / 'crypto_analysis.log'))

    # Риск-менеджмент
    MAX_POSITION_SIZE = float(os.getenv('MAX_POSITION_SIZE', 0.1))
    STOP_LOSS_PERCENTAGE = float(os.getenv('STOP_LOSS_PERCENTAGE', 0.05))
    TAKE_PROFIT_PERCENTAGE = float(os.getenv('TAKE_PROFIT_PERCENTAGE', 0.15))

    # Технические индикаторы - параметры по умолчанию
    TECHNICAL_INDICATORS = {
        'SMA_PERIODS': [20, 50, 200],
        'EMA_PERIODS': [12, 26],
        'RSI_PERIOD': 14,
        'MACD_FAST': 12,
        'MACD_SLOW': 26,
        'MACD_SIGNAL': 9,
        'BB_PERIOD': 20,
        'BB_STD': 2,
        'STOCH_K': 14,
        'STOCH_D': 3,
        'ATR_PERIOD': 14,
        'CCI_PERIOD': 20,
        'ADX_PERIOD': 14
    }

    # ML модели - параметры по умолчанию
    ML_CONFIG = {
        'LSTM_EPOCHS': 50,
        'LSTM_BATCH_SIZE': 32,
        'LSTM_SEQUENCE_LENGTH': 60,
        'TRAIN_TEST_SPLIT': 0.8,
        'CROSS_VALIDATION_FOLDS': 5,
        'RANDOM_STATE': 42
    }

    # Интервалы для различных целей
    INTERVALS_CONFIG = {
        'SCALPING': ['1m', '3m', '5m'],
        'INTRADAY': ['15m', '30m', '1h'],
        'SWING': ['4h', '6h', '12h'],
        'POSITION': ['1d', '3d', '1w']
    }

    # Топ криптовалюты по категориям
    SYMBOL_CATEGORIES = {
        'MAJOR': ['BTCUSDT', 'ETHUSDT', 'BNBUSDT'],
        'ALTCOINS': ['ADAUSDT', 'DOTUSDT', 'LINKUSDT', 'UNIUSDT', 'LTCUSDT'],
        'DEFI': ['AAVEUSDT', 'COMPUSDT', 'MKRUSDT', 'SUSHIUSDT'],
        'MEME': ['DOGEUSDT', 'SHIBUSDT'],
        'STABLECOINS': ['USDCUSDT', 'BUSDUSDT']
    }

    @classmethod
    def create_directories(cls):
        """Создание необходимых директорий"""
        directories = [
            cls.DATA_DIR,
            cls.DATA_DIR / 'raw',
            cls.DATA_DIR / 'processed',
            cls.MODEL_DIR,
            cls.LOG_DIR,
            cls.BASE_DIR / 'notebooks',
            cls.BASE_DIR / 'tests'
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    @classmethod
    def get_symbols_by_category(cls, category: str) -> List[str]:
        """
        Получение символов по категории

        Args:
            category: Название категории

        Returns:
            Список символов
        """
        return cls.SYMBOL_CATEGORIES.get(category.upper(), [])

    @classmethod
    def get_all_symbols(cls) -> List[str]:
        """
        Получение всех символов

        Returns:
            Список всех символов
        """
        all_symbols = []
        for symbols in cls.SYMBOL_CATEGORIES.values():
            all_symbols.extend(symbols)
        return list(set(all_symbols))

    @classmethod
    def get_intervals_by_strategy(cls, strategy: str) -> List[str]:
        """
        Получение интервалов по торговой стратегии

        Args:
            strategy: Тип стратегии

        Returns:
            Список интервалов
        """
        return cls.INTERVALS_CONFIG.get(strategy.upper(), cls.DEFAULT_INTERVALS)

    @classmethod
    def validate_config(cls) -> Dict[str, bool]:
        """
        Валидация конфигурации

        Returns:
            Словарь с результатами валидации
        """
        validation_results = {}

        # Проверка API ключей
        validation_results['binance_api_key'] = bool(cls.BINANCE_API_KEY)
        validation_results['binance_secret_key'] = bool(cls.BINANCE_SECRET_KEY)

        # Проверка директорий
        validation_results['base_directory_exists'] = cls.BASE_DIR.exists()
        validation_results['data_directory_writable'] = os.access(cls.DATA_DIR.parent, os.W_OK)

        # Проверка параметров ML
        validation_results['prediction_horizon_valid'] = (
            isinstance(cls.PREDICTION_HORIZON_HOURS, int) and
            cls.PREDICTION_HORIZON_HOURS > 0
        )

        # Проверка символов
        validation_results['default_symbols_valid'] = (
            isinstance(cls.DEFAULT_SYMBOLS, list) and
            len(cls.DEFAULT_SYMBOLS) > 0
        )

        return validation_results

    @classmethod
    def save_config_to_file(cls, filepath: str):
        """
        Сохранение конфигурации в YAML файл

        Args:
            filepath: Путь к файлу
        """
        config_dict = {
            'binance': {
                'api_key_set': bool(cls.BINANCE_API_KEY),
                'secret_key_set': bool(cls.BINANCE_SECRET_KEY)
            },
            'trading': {
                'default_symbols': cls.DEFAULT_SYMBOLS,
                'default_intervals': cls.DEFAULT_INTERVALS,
                'max_position_size': cls.MAX_POSITION_SIZE,
                'stop_loss_percentage': cls.STOP_LOSS_PERCENTAGE,
                'take_profit_percentage': cls.TAKE_PROFIT_PERCENTAGE
            },
            'machine_learning': cls.ML_CONFIG,
            'technical_indicators': cls.TECHNICAL_INDICATORS,
            'intervals': cls.INTERVALS_CONFIG,
            'symbol_categories': cls.SYMBOL_CATEGORIES
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            yaml.dump(config_dict, f, default_flow_style=False, allow_unicode=True)

    @classmethod
    def load_config_from_file(cls, filepath: str) -> Dict[str, Any]:
        """
        Загрузка конфигурации из YAML файла

        Args:
            filepath: Путь к файлу

        Returns:
            Словарь с конфигурацией
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            return {}

    @classmethod
    def get_database_path(cls) -> str:
        """
        Получение пути к базе данных

        Returns:
            Путь к БД
        """
        if cls.DATABASE_URL.startswith('sqlite:///'):
            db_path = cls.DATABASE_URL.replace('sqlite:///', '')
            if not Path(db_path).is_absolute():
                return str(cls.BASE_DIR / db_path)
            return db_path
        return cls.DATABASE_URL

    @classmethod
    def get_trading_parameters(cls) -> Dict[str, Any]:
        """
        Получение параметров торговли

        Returns:
            Словарь с параметрами
        """
        return {
            'max_position_size': cls.MAX_POSITION_SIZE,
            'stop_loss_percentage': cls.STOP_LOSS_PERCENTAGE,
            'take_profit_percentage': cls.TAKE_PROFIT_PERCENTAGE,
            'prediction_horizon_hours': cls.PREDICTION_HORIZON_HOURS
        }

    @classmethod
    def print_config_summary(cls):
        """Вывод краткого обзора конфигурации"""
        print("🔧 Конфигурация системы:")
        print(f"   📁 Базовая директория: {cls.BASE_DIR}")
        print(f"   💾 База данных: {cls.get_database_path()}")
        print(f"   🔑 API ключи: {'✅' if cls.BINANCE_API_KEY else '❌'}")
        print(f"   📊 Символы по умолчанию: {len(cls.DEFAULT_SYMBOLS)}")
        print(f"   ⏰ Интервалы по умолчанию: {len(cls.DEFAULT_INTERVALS)}")
        print(f"   🤖 Горизонт прогноза: {cls.PREDICTION_HORIZON_HOURS} часов")
        print(f"   📈 Максимальный размер позиции: {cls.MAX_POSITION_SIZE * 100}%")

        validation = cls.validate_config()
        valid_count = sum(validation.values())
        total_count = len(validation)
        print(f"   ✅ Валидация: {valid_count}/{total_count} проверок пройдено")

        if not all(validation.values()):
            print("   ⚠️  Обнаружены проблемы:")
            for check, result in validation.items():
                if not result:
                    print(f"      - {check}")


# Создание экземпляра конфигурации
config = Config()

# Автоматическое создание директорий
config.create_directories()

if __name__ == "__main__":
    # Пример использования
    config.print_config_summary()

    # Сохранение конфигурации
    config_path = config.BASE_DIR / 'config' / 'system_config.yaml'
    config.save_config_to_file(str(config_path))
    print(f"\n💾 Конфигурация сохранена в {config_path}")

    # Проверка валидации
    validation_results = config.validate_config()
    print(f"\n🔍 Результаты валидации:")
    for check, result in validation_results.items():
        status = "✅" if result else "❌"
        print(f"   {status} {check}: {result}")

    # Показать все символы по категориям
    print(f"\n📊 Доступные символы по категориям:")
    for category, symbols in config.SYMBOL_CATEGORIES.items():
        print(f"   {category}: {symbols}")

    # Показать интервалы по стратегиям
    print(f"\n⏰ Интервалы по торговым стратегиям:")
    for strategy, intervals in config.INTERVALS_CONFIG.items():
        print(f"   {strategy}: {intervals}")