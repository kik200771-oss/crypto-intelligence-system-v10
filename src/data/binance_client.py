"""
Binance API Client для загрузки данных криптовалют
"""

import os
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from binance.client import Client
from binance.exceptions import BinanceAPIException
import logging

logger = logging.getLogger(__name__)


class BinanceClient:
    """Клиент для работы с Binance API"""

    def __init__(self, api_key: Optional[str] = None, secret_key: Optional[str] = None):
        """
        Инициализация клиента

        Args:
            api_key: API ключ Binance
            secret_key: Секретный ключ Binance
        """
        self.api_key = api_key or os.getenv('BINANCE_API_KEY')
        self.secret_key = secret_key or os.getenv('BINANCE_SECRET_KEY')

        if not self.api_key or not self.secret_key:
            logger.warning("API ключи не найдены. Работа только с публичными данными.")
            self.client = Client()
        else:
            self.client = Client(self.api_key, self.secret_key)

    def get_historical_klines(
        self,
        symbol: str,
        interval: str,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        limit: int = 1000
    ) -> pd.DataFrame:
        """
        Получение исторических данных свечей

        Args:
            symbol: Торговая пара (например, 'BTCUSDT')
            interval: Временной интервал ('1m', '5m', '1h', '1d' и т.д.)
            start_time: Начальная дата (ISO формат или timestamp)
            end_time: Конечная дата (ISO формат или timestamp)
            limit: Максимальное количество записей

        Returns:
            DataFrame с историческими данными
        """
        try:
            klines = self.client.get_historical_klines(
                symbol=symbol,
                interval=interval,
                start_str=start_time,
                end_str=end_time,
                limit=limit
            )

            # Преобразование в DataFrame
            df = pd.DataFrame(klines, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_asset_volume', 'number_of_trades',
                'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume',
                'ignore'
            ])

            # Преобразование типов данных
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df['close_time'] = pd.to_datetime(df['close_time'], unit='ms')

            numeric_columns = ['open', 'high', 'low', 'close', 'volume',
                             'quote_asset_volume', 'number_of_trades',
                             'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume']

            for col in numeric_columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

            df.set_index('timestamp', inplace=True)
            df.drop('ignore', axis=1, inplace=True)

            logger.info(f"Загружено {len(df)} записей для {symbol} с интервалом {interval}")
            return df

        except BinanceAPIException as e:
            logger.error(f"Ошибка Binance API: {e}")
            raise
        except Exception as e:
            logger.error(f"Неожиданная ошибка: {e}")
            raise

    def get_symbol_info(self, symbol: str) -> Dict[str, Any]:
        """
        Получение информации о торговой паре

        Args:
            symbol: Торговая пара

        Returns:
            Словарь с информацией о символе
        """
        try:
            info = self.client.get_symbol_info(symbol)
            return info
        except Exception as e:
            logger.error(f"Ошибка получения информации о символе {symbol}: {e}")
            raise

    def get_exchange_info(self) -> Dict[str, Any]:
        """
        Получение информации об обменнике

        Returns:
            Словарь с информацией об обменнике
        """
        try:
            return self.client.get_exchange_info()
        except Exception as e:
            logger.error(f"Ошибка получения информации об обменнике: {e}")
            raise

    def get_top_symbols(self, quote_asset: str = 'USDT', limit: int = 50) -> List[str]:
        """
        Получение топ торговых пар по объему

        Args:
            quote_asset: Базовая валюта (USDT, BTC и т.д.)
            limit: Количество символов

        Returns:
            Список символов
        """
        try:
            ticker = self.client.get_ticker()

            # Фильтрация по базовой валюте
            filtered_symbols = [
                item for item in ticker
                if item['symbol'].endswith(quote_asset)
            ]

            # Сортировка по объему
            sorted_symbols = sorted(
                filtered_symbols,
                key=lambda x: float(x['quoteVolume']),
                reverse=True
            )

            top_symbols = [item['symbol'] for item in sorted_symbols[:limit]]

            logger.info(f"Получены топ {len(top_symbols)} символов для {quote_asset}")
            return top_symbols

        except Exception as e:
            logger.error(f"Ошибка получения топ символов: {e}")
            raise

    def get_24hr_ticker(self, symbol: Optional[str] = None) -> pd.DataFrame:
        """
        Получение 24-часовой статистики

        Args:
            symbol: Торговая пара (если None, то для всех пар)

        Returns:
            DataFrame со статистикой
        """
        try:
            if symbol:
                ticker = [self.client.get_24hr_ticker(symbol=symbol)]
            else:
                ticker = self.client.get_24hr_ticker()

            df = pd.DataFrame(ticker)

            # Преобразование числовых колонок
            numeric_columns = [
                'priceChange', 'priceChangePercent', 'weightedAvgPrice',
                'prevClosePrice', 'lastPrice', 'lastQty', 'bidPrice', 'bidQty',
                'askPrice', 'askQty', 'openPrice', 'highPrice', 'lowPrice',
                'volume', 'quoteVolume', 'count'
            ]

            for col in numeric_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')

            logger.info(f"Получена 24ч статистика для {'всех символов' if not symbol else symbol}")
            return df

        except Exception as e:
            logger.error(f"Ошибка получения 24ч статистики: {e}")
            raise

    def test_connectivity(self) -> bool:
        """
        Тест подключения к API

        Returns:
            True если подключение успешно
        """
        try:
            self.client.ping()
            logger.info("Подключение к Binance API успешно")
            return True
        except Exception as e:
            logger.error(f"Ошибка подключения к API: {e}")
            return False

    def get_account_info(self) -> Dict[str, Any]:
        """
        Получение информации об аккаунте

        Returns:
            Словарь с информацией об аккаунте
        """
        try:
            if not self.api_key or not self.secret_key:
                raise ValueError("Требуются API ключи для получения информации об аккаунте")

            account_info = self.client.get_account()
            logger.info("Информация об аккаунте получена успешно")
            return account_info

        except Exception as e:
            logger.error(f"Ошибка получения информации об аккаунте: {e}")
            raise


if __name__ == "__main__":
    # Пример использования
    from dotenv import load_dotenv
    load_dotenv('../config/.env')

    client = BinanceClient()

    # Тест подключения
    if client.test_connectivity():
        print("✅ Подключение к Binance API установлено")

        # Получение данных за последние 100 дней
        end_time = datetime.now()
        start_time = end_time - timedelta(days=100)

        df = client.get_historical_klines(
            symbol='BTCUSDT',
            interval='1d',
            start_time=start_time.isoformat(),
            end_time=end_time.isoformat()
        )

        print(f"📊 Загружено {len(df)} дневных свечей для BTC/USDT")
        print(df.head())

    else:
        print("❌ Ошибка подключения к Binance API")