# Crypto Market Analysis & Prediction System

Система анализа и прогнозирования колебаний криптовалют с использованием Binance API.

## Структура проекта

```
├── src/
│   ├── data/               # Модули для работы с данными
│   │   ├── binance_client.py    # Клиент для Binance API
│   │   ├── data_collector.py    # Сбор данных
│   │   └── data_processor.py    # Обработка данных
│   ├── analysis/           # Модули анализа
│   │   ├── technical_indicators.py  # Технические индикаторы
│   │   ├── pattern_recognition.py   # Распознавание паттернов
│   │   └── market_analysis.py       # Рыночный анализ
│   ├── prediction/         # Модули прогнозирования
│   │   ├── ml_models.py         # ML модели
│   │   ├── prediction_engine.py  # Движок прогнозов
│   │   └── backtesting.py       # Бэктестинг
│   └── utils/              # Утилиты
│       ├── config.py            # Конфигурация
│       ├── logging_setup.py     # Логирование
│       └── helpers.py           # Вспомогательные функции
├── data/                   # Папка для данных
│   ├── raw/                # Сырые данные
│   ├── processed/          # Обработанные данные
│   └── models/             # Сохраненные модели
├── notebooks/              # Jupyter notebooks для анализа
├── tests/                  # Тесты
├── config/                 # Файлы конфигурации
└── requirements.txt        # Зависимости

## Функциональность

### 1. Сбор данных
- Подключение к Binance API
- Загрузка исторических данных
- Реальное время данные
- Сохранение в локальную БД

### 2. Анализ
- Технические индикаторы (RSI, MACD, Bollinger Bands)
- Анализ объемов
- Распознавание паттернов
- Корреляционный анализ

### 3. Прогнозирование
- LSTM нейронные сети
- Random Forest
- ARIMA модели
- Ensemble методы

### 4. Визуализация
- Интерактивные графики
- Dashboard в реальном времени
- Отчеты по производительности

## Установка

```bash
pip install -r requirements.txt
```

## Конфигурация

Создайте файл `config/.env` с вашими API ключами:
```
BINANCE_API_KEY=your_api_key
BINANCE_SECRET_KEY=your_secret_key
```

## Использование

```python
from src.data.binance_client import BinanceClient
from src.prediction.prediction_engine import PredictionEngine

# Инициализация
client = BinanceClient()
predictor = PredictionEngine()

# Анализ
predictions = predictor.predict('BTCUSDT', timeframe='1h', horizon=24)
```