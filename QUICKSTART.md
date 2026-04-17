# 🚀 Быстрый старт - Анализ криптовалют

## 1. 📦 Установка зависимостей

```bash
# Запустите скрипт автоматической установки
python setup.py

# Или установите вручную
pip install -r requirements.txt
```

## 2. 🔑 Настройка API ключей

1. Скопируйте файл конфигурации:
   ```bash
   cp config/.env.example config/.env
   ```

2. Отредактируйте `config/.env` и добавьте ваши ключи Binance:
   ```
   BINANCE_API_KEY=ваш_api_ключ
   BINANCE_SECRET_KEY=ваш_секретный_ключ
   ```

## 3. 🎯 Первые команды

```bash
# Проверьте конфигурацию
python main.py --config

# Соберите данные для BTC и ETH
python main.py --collect-data --symbols BTCUSDT ETHUSDT

# Обучите модели для BTC
python main.py --train-models --symbol BTCUSDT

# Создайте прогноз на 24 часа
python main.py --predict --symbol BTCUSDT --horizon 24
```

## 4. 📊 Jupyter анализ

```bash
# Запустите интерактивный анализ
jupyter notebook notebooks/crypto_analysis_demo.ipynb
```

## 5. 📈 Анализ портфеля

```bash
# Посмотрите текущую рыночную ситуацию
python main.py --portfolio
```

## 🎉 Готово!

Ваша система анализа криптовалют готова к работе. 

Начните с простых команд, изучите результаты, а затем переходите к более сложным анализам в Jupyter Notebook.

**Важно:** Это инструмент для анализа, а не для торговых сигналов!