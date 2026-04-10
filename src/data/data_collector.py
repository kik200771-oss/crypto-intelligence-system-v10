"""
Модуль для сбора и управления криптовалютными данными
"""

import os
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
from typing import List, Optional, Dict
import logging
from pathlib import Path

from .binance_client import BinanceClient

logger = logging.getLogger(__name__)


class DataCollector:
    """Класс для сбора и управления данными криптовалют"""

    def __init__(self, db_path: Optional[str] = None):
        """
        Инициализация коллектора данных

        Args:
            db_path: Путь к базе данных SQLite
        """
        self.db_path = db_path or os.getenv('DATABASE_URL', 'data/crypto_data.db')
        self.binance_client = BinanceClient()

        # Создание директории для данных если не существует
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        # Инициализация базы данных
        self._init_database()

    def _init_database(self):
        """Инициализация базы данных и создание таблиц"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Таблица для OHLCV данных
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS ohlcv_data (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        symbol TEXT NOT NULL,
                        interval TEXT NOT NULL,
                        timestamp DATETIME NOT NULL,
                        open REAL NOT NULL,
                        high REAL NOT NULL,
                        low REAL NOT NULL,
                        close REAL NOT NULL,
                        volume REAL NOT NULL,
                        close_time DATETIME,
                        quote_asset_volume REAL,
                        number_of_trades INTEGER,
                        taker_buy_base_asset_volume REAL,
                        taker_buy_quote_asset_volume REAL,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(symbol, interval, timestamp)
                    )
                """)

                # Таблица для 24-часовой статистики
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS ticker_24hr (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        symbol TEXT NOT NULL,
                        price_change REAL,
                        price_change_percent REAL,
                        weighted_avg_price REAL,
                        prev_close_price REAL,
                        last_price REAL,
                        last_qty REAL,
                        bid_price REAL,
                        bid_qty REAL,
                        ask_price REAL,
                        ask_qty REAL,
                        open_price REAL,
                        high_price REAL,
                        low_price REAL,
                        volume REAL,
                        quote_volume REAL,
                        open_time DATETIME,
                        close_time DATETIME,
                        count INTEGER,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # Индексы для оптимизации
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_ohlcv_symbol_interval_timestamp
                    ON ohlcv_data(symbol, interval, timestamp)
                """)

                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_ticker_symbol_created
                    ON ticker_24hr(symbol, created_at)
                """)

                conn.commit()
                logger.info(f"База данных инициализирована: {self.db_path}")

        except Exception as e:
            logger.error(f"Ошибка инициализации базы данных: {e}")
            raise

    def collect_historical_data(
        self,
        symbols: List[str],
        intervals: List[str],
        days_back: int = 365,
        save_to_db: bool = True,
        save_to_csv: bool = False
    ) -> Dict[str, pd.DataFrame]:
        """
        Сбор исторических данных для списка символов

        Args:
            symbols: Список торговых пар
            intervals: Список интервалов времени
            days_back: Количество дней назад для загрузки
            save_to_db: Сохранить в базу данных
            save_to_csv: Сохранить в CSV файлы

        Returns:
            Словарь с данными {symbol_interval: DataFrame}
        """
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days_back)

        collected_data = {}

        for symbol in symbols:
            for interval in intervals:
                try:
                    logger.info(f"Загрузка данных для {symbol} с интервалом {interval}")

                    df = self.binance_client.get_historical_klines(
                        symbol=symbol,
                        interval=interval,
                        start_time=start_time.isoformat(),
                        end_time=end_time.isoformat()
                    )

                    if df.empty:
                        logger.warning(f"Нет данных для {symbol} с интервалом {interval}")
                        continue

                    # Добавление метаданных
                    df['symbol'] = symbol
                    df['interval'] = interval

                    key = f"{symbol}_{interval}"
                    collected_data[key] = df

                    if save_to_db:
                        self._save_to_database(df, symbol, interval)

                    if save_to_csv:
                        self._save_to_csv(df, symbol, interval)

                    logger.info(f"✅ Загружено {len(df)} записей для {symbol}_{interval}")

                except Exception as e:
                    logger.error(f"Ошибка загрузки данных для {symbol}_{interval}: {e}")
                    continue

        logger.info(f"Сбор данных завершен. Всего наборов: {len(collected_data)}")
        return collected_data

    def _save_to_database(self, df: pd.DataFrame, symbol: str, interval: str):
        """Сохранение данных в базу данных"""
        try:
            # Подготовка данных для сохранения
            df_to_save = df.copy().reset_index()

            # Переименование колонок для соответствия схеме БД
            column_mapping = {
                'timestamp': 'timestamp',
                'open': 'open',
                'high': 'high',
                'low': 'low',
                'close': 'close',
                'volume': 'volume',
                'close_time': 'close_time',
                'quote_asset_volume': 'quote_asset_volume',
                'number_of_trades': 'number_of_trades',
                'taker_buy_base_asset_volume': 'taker_buy_base_asset_volume',
                'taker_buy_quote_asset_volume': 'taker_buy_quote_asset_volume'
            }

            df_to_save = df_to_save[list(column_mapping.keys())].rename(columns=column_mapping)
            df_to_save['symbol'] = symbol
            df_to_save['interval'] = interval

            # Сохранение с обработкой дубликатов
            with sqlite3.connect(self.db_path) as conn:
                df_to_save.to_sql(
                    'ohlcv_data',
                    conn,
                    if_exists='append',
                    index=False,
                    method='ignore'  # Игнорировать дубликаты
                )

                logger.info(f"Данные сохранены в БД: {symbol}_{interval}")

        except Exception as e:
            logger.error(f"Ошибка сохранения в БД для {symbol}_{interval}: {e}")

    def _save_to_csv(self, df: pd.DataFrame, symbol: str, interval: str):
        """Сохранение данных в CSV файл"""
        try:
            csv_dir = Path('data/raw')
            csv_dir.mkdir(parents=True, exist_ok=True)

            filename = f"{symbol}_{interval}_{datetime.now().strftime('%Y%m%d')}.csv"
            filepath = csv_dir / filename

            df.to_csv(filepath)
            logger.info(f"Данные сохранены в CSV: {filepath}")

        except Exception as e:
            logger.error(f"Ошибка сохранения CSV для {symbol}_{interval}: {e}")

    def load_data_from_db(
        self,
        symbol: str,
        interval: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> pd.DataFrame:
        """
        Загрузка данных из базы данных

        Args:
            symbol: Торговая пара
            interval: Интервал времени
            start_time: Начальное время
            end_time: Конечное время

        Returns:
            DataFrame с данными
        """
        try:
            query = """
                SELECT timestamp, open, high, low, close, volume,
                       close_time, quote_asset_volume, number_of_trades,
                       taker_buy_base_asset_volume, taker_buy_quote_asset_volume
                FROM ohlcv_data
                WHERE symbol = ? AND interval = ?
            """
            params = [symbol, interval]

            if start_time:
                query += " AND timestamp >= ?"
                params.append(start_time)

            if end_time:
                query += " AND timestamp <= ?"
                params.append(end_time)

            query += " ORDER BY timestamp ASC"

            with sqlite3.connect(self.db_path) as conn:
                df = pd.read_sql_query(query, conn, params=params)

                if not df.empty:
                    df['timestamp'] = pd.to_datetime(df['timestamp'])
                    df.set_index('timestamp', inplace=True)

                logger.info(f"Загружено {len(df)} записей из БД для {symbol}_{interval}")
                return df

        except Exception as e:
            logger.error(f"Ошибка загрузки данных из БД: {e}")
            return pd.DataFrame()

    def update_latest_data(self, symbols: List[str], intervals: List[str]):
        """
        Обновление данных до последнего времени

        Args:
            symbols: Список символов
            intervals: Список интервалов
        """
        for symbol in symbols:
            for interval in intervals:
                try:
                    # Найти последнюю временную метку в БД
                    with sqlite3.connect(self.db_path) as conn:
                        cursor = conn.execute(
                            "SELECT MAX(timestamp) FROM ohlcv_data WHERE symbol=? AND interval=?",
                            (symbol, interval)
                        )
                        result = cursor.fetchone()
                        last_timestamp = result[0] if result[0] else None

                    if last_timestamp:
                        start_time = pd.to_datetime(last_timestamp) + pd.Timedelta(minutes=1)
                    else:
                        # Если данных нет, загружаем за последние 30 дней
                        start_time = datetime.now() - timedelta(days=30)

                    # Загрузка новых данных
                    df = self.binance_client.get_historical_klines(
                        symbol=symbol,
                        interval=interval,
                        start_time=start_time.isoformat()
                    )

                    if not df.empty:
                        self._save_to_database(df, symbol, interval)
                        logger.info(f"Обновлено {len(df)} записей для {symbol}_{interval}")
                    else:
                        logger.info(f"Новых данных нет для {symbol}_{interval}")

                except Exception as e:
                    logger.error(f"Ошибка обновления данных для {symbol}_{interval}: {e}")

    def get_available_data_info(self) -> pd.DataFrame:
        """
        Получение информации о доступных данных в базе

        Returns:
            DataFrame с информацией о данных
        """
        try:
            query = """
                SELECT
                    symbol,
                    interval,
                    COUNT(*) as records_count,
                    MIN(timestamp) as start_date,
                    MAX(timestamp) as end_date
                FROM ohlcv_data
                GROUP BY symbol, interval
                ORDER BY symbol, interval
            """

            with sqlite3.connect(self.db_path) as conn:
                df = pd.read_sql_query(query, conn)

                if not df.empty:
                    df['start_date'] = pd.to_datetime(df['start_date'])
                    df['end_date'] = pd.to_datetime(df['end_date'])

                return df

        except Exception as e:
            logger.error(f"Ошибка получения информации о данных: {e}")
            return pd.DataFrame()


if __name__ == "__main__":
    # Пример использования
    import logging
    logging.basicConfig(level=logging.INFO)

    collector = DataCollector()

    # Получение топ символов
    top_symbols = collector.binance_client.get_top_symbols(limit=10)
    intervals = ['1h', '4h', '1d']

    print(f"Начинаем сбор данных для символов: {top_symbols}")

    # Сбор исторических данных
    data = collector.collect_historical_data(
        symbols=top_symbols[:3],  # Первые 3 для теста
        intervals=intervals,
        days_back=30
    )

    # Информация о собранных данных
    info = collector.get_available_data_info()
    print("\n📊 Информация о собранных данных:")
    print(info)