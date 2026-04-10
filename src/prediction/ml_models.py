"""
Модуль машинного обучения для прогнозирования цен криптовалют
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pickle
import os
from pathlib import Path
from typing import Tuple, List, Optional, Dict, Any
import warnings
warnings.filterwarnings('ignore')

# Машинное обучение
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import xgboost as xgb
import lightgbm as lgb

# Глубокое обучение
try:
    import tensorflow as tf
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import LSTM, Dense, Dropout, GRU
    from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
    KERAS_AVAILABLE = True
except ImportError:
    KERAS_AVAILABLE = False
    print("TensorFlow/Keras не установлен. LSTM модели недоступны.")

import logging
logger = logging.getLogger(__name__)


class CryptoPricePredictor:
    """Класс для прогнозирования цен криптовалют"""

    def __init__(self, model_save_path: str = "data/models/"):
        """
        Инициализация предсказателя

        Args:
            model_save_path: Путь для сохранения моделей
        """
        self.model_save_path = Path(model_save_path)
        self.model_save_path.mkdir(parents=True, exist_ok=True)

        self.models = {}
        self.scalers = {}
        self.feature_columns = []

    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Подготовка признаков для обучения

        Args:
            df: DataFrame с техническими индикаторами

        Returns:
            DataFrame с подготовленными признаками
        """
        features_df = df.copy()

        # Базовые признаки
        features_df['price_change'] = df['close'].pct_change()
        features_df['volume_change'] = df['volume'].pct_change()
        features_df['high_low_ratio'] = df['high'] / df['low']
        features_df['close_open_ratio'] = df['close'] / df['open']

        # Лаговые признаки (предыдущие значения)
        for lag in [1, 2, 3, 5, 10]:
            features_df[f'close_lag_{lag}'] = df['close'].shift(lag)
            features_df[f'volume_lag_{lag}'] = df['volume'].shift(lag)
            features_df[f'rsi_lag_{lag}'] = df.get('RSI', pd.Series()).shift(lag)

        # Скользящие средние отношения
        if 'SMA_20' in df.columns and 'SMA_50' in df.columns:
            features_df['sma_ratio'] = df['SMA_20'] / df['SMA_50']
            features_df['price_to_sma20'] = df['close'] / df['SMA_20']

        # Волатильность (скользящее стандартное отклонение)
        for window in [5, 10, 20]:
            features_df[f'volatility_{window}'] = df['close'].rolling(window=window).std()
            features_df[f'volume_volatility_{window}'] = df['volume'].rolling(window=window).std()

        # Технические сигналы
        if 'RSI' in df.columns:
            features_df['rsi_overbought'] = (df['RSI'] > 70).astype(int)
            features_df['rsi_oversold'] = (df['RSI'] < 30).astype(int)

        if 'MACD' in df.columns and 'MACD_Signal' in df.columns:
            features_df['macd_signal'] = (df['MACD'] > df['MACD_Signal']).astype(int)

        # Временные признаки
        features_df['hour'] = features_df.index.hour
        features_df['day_of_week'] = features_df.index.dayofweek
        features_df['month'] = features_df.index.month

        # Удаление NaN
        features_df.dropna(inplace=True)

        return features_df

    def prepare_lstm_data(self, df: pd.DataFrame, sequence_length: int = 60,
                         target_column: str = 'close') -> Tuple[np.ndarray, np.ndarray]:
        """
        Подготовка данных для LSTM

        Args:
            df: DataFrame с данными
            sequence_length: Длина последовательности
            target_column: Целевая колонка

        Returns:
            Кортеж (X, y) для обучения LSTM
        """
        # Выбираем только числовые колонки
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        data = df[numeric_columns].values

        # Нормализация
        scaler = MinMaxScaler()
        scaled_data = scaler.fit_transform(data)

        # Сохранение скейлера
        self.scalers['lstm_scaler'] = scaler

        X, y = [], []
        target_index = df.columns.get_loc(target_column)

        for i in range(sequence_length, len(scaled_data)):
            X.append(scaled_data[i-sequence_length:i])
            y.append(scaled_data[i, target_index])

        return np.array(X), np.array(y)

    def train_traditional_models(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, Any]:
        """
        Обучение традиционных ML моделей

        Args:
            X: Признаки
            y: Целевая переменная

        Returns:
            Словарь с обученными моделями и метриками
        """
        # Разделение данных
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, shuffle=False, random_state=42
        )

        # Нормализация
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        self.scalers['traditional_scaler'] = scaler

        models = {
            'LinearRegression': LinearRegression(),
            'Ridge': Ridge(alpha=1.0),
            'Lasso': Lasso(alpha=1.0),
            'RandomForest': RandomForestRegressor(n_estimators=100, random_state=42),
            'GradientBoosting': GradientBoostingRegressor(random_state=42),
            'XGBoost': xgb.XGBRegressor(random_state=42),
            'LightGBM': lgb.LGBMRegressor(random_state=42, verbose=-1)
        }

        results = {}

        for name, model in models.items():
            try:
                logger.info(f"Обучение модели {name}...")

                # Обучение
                if name in ['XGBoost', 'LightGBM']:
                    model.fit(X_train, y_train)
                else:
                    model.fit(X_train_scaled, y_train)

                # Предсказания
                if name in ['XGBoost', 'LightGBM']:
                    y_pred = model.predict(X_test)
                else:
                    y_pred = model.predict(X_test_scaled)

                # Метрики
                mse = mean_squared_error(y_test, y_pred)
                rmse = np.sqrt(mse)
                mae = mean_absolute_error(y_test, y_pred)
                r2 = r2_score(y_test, y_pred)

                results[name] = {
                    'model': model,
                    'mse': mse,
                    'rmse': rmse,
                    'mae': mae,
                    'r2': r2,
                    'predictions': y_pred,
                    'actual': y_test
                }

                logger.info(f"{name} - RMSE: {rmse:.4f}, MAE: {mae:.4f}, R²: {r2:.4f}")

            except Exception as e:
                logger.error(f"Ошибка при обучении {name}: {e}")
                continue

        self.models.update(results)
        return results

    def create_lstm_model(self, input_shape: Tuple[int, int]) -> 'tf.keras.Model':
        """
        Создание LSTM модели

        Args:
            input_shape: Форма входных данных

        Returns:
            Компилированная модель
        """
        if not KERAS_AVAILABLE:
            raise ImportError("TensorFlow не установлен")

        model = Sequential([
            LSTM(50, return_sequences=True, input_shape=input_shape),
            Dropout(0.2),
            LSTM(50, return_sequences=True),
            Dropout(0.2),
            LSTM(50, return_sequences=False),
            Dropout(0.2),
            Dense(25),
            Dense(1)
        ])

        model.compile(optimizer='adam', loss='mean_squared_error')
        return model

    def train_lstm_model(self, X: np.ndarray, y: np.ndarray, epochs: int = 50,
                        batch_size: int = 32) -> Dict[str, Any]:
        """
        Обучение LSTM модели

        Args:
            X: Входные данные
            y: Целевая переменная
            epochs: Количество эпох
            batch_size: Размер батча

        Returns:
            Словарь с результатами обучения
        """
        if not KERAS_AVAILABLE:
            logger.warning("TensorFlow недоступен. Пропуск LSTM обучения.")
            return {}

        try:
            # Разделение данных
            train_size = int(len(X) * 0.8)
            X_train, X_test = X[:train_size], X[train_size:]
            y_train, y_test = y[:train_size], y[train_size:]

            # Создание модели
            model = self.create_lstm_model((X.shape[1], X.shape[2]))

            # Callbacks
            early_stopping = EarlyStopping(patience=10, restore_best_weights=True)
            model_checkpoint = ModelCheckpoint(
                self.model_save_path / 'best_lstm_model.h5',
                save_best_only=True
            )

            # Обучение
            logger.info("Обучение LSTM модели...")
            history = model.fit(
                X_train, y_train,
                epochs=epochs,
                batch_size=batch_size,
                validation_split=0.1,
                callbacks=[early_stopping, model_checkpoint],
                verbose=1
            )

            # Оценка
            y_pred = model.predict(X_test)
            mse = mean_squared_error(y_test, y_pred)
            rmse = np.sqrt(mse)
            mae = mean_absolute_error(y_test, y_pred)

            results = {
                'model': model,
                'history': history.history,
                'mse': mse,
                'rmse': rmse,
                'mae': mae,
                'predictions': y_pred,
                'actual': y_test
            }

            self.models['LSTM'] = results
            logger.info(f"LSTM - RMSE: {rmse:.4f}, MAE: {mae:.4f}")

            return results

        except Exception as e:
            logger.error(f"Ошибка при обучении LSTM: {e}")
            return {}

    def predict_price(self, model_name: str, features: pd.DataFrame,
                     periods: int = 24) -> np.ndarray:
        """
        Прогнозирование цены

        Args:
            model_name: Название модели
            features: Признаки для прогнозирования
            periods: Количество периодов для прогноза

        Returns:
            Массив прогнозов
        """
        if model_name not in self.models:
            raise ValueError(f"Модель {model_name} не найдена")

        model_info = self.models[model_name]
        model = model_info['model']

        try:
            if model_name == 'LSTM':
                if not KERAS_AVAILABLE:
                    raise ImportError("TensorFlow недоступен")

                # Для LSTM нужны последние данные определенной длины
                scaler = self.scalers.get('lstm_scaler')
                if not scaler:
                    raise ValueError("Скейлер для LSTM не найден")

                # Подготовка данных для LSTM прогноза
                sequence_length = 60  # Должно соответствовать обучению
                numeric_features = features.select_dtypes(include=[np.number])
                scaled_features = scaler.transform(numeric_features)

                predictions = []
                current_sequence = scaled_features[-sequence_length:]

                for _ in range(periods):
                    pred = model.predict(current_sequence.reshape(1, sequence_length, -1))
                    predictions.append(pred[0, 0])

                    # Обновление последовательности (упрощенный подход)
                    new_row = current_sequence[-1].copy()
                    new_row[0] = pred[0, 0]  # Предполагаем, что цена в первой колонке
                    current_sequence = np.vstack([current_sequence[1:], new_row])

                # Обратная нормализация
                dummy_array = np.zeros((len(predictions), scaled_features.shape[1]))
                dummy_array[:, 0] = predictions
                original_scale = scaler.inverse_transform(dummy_array)[:, 0]

                return original_scale

            else:
                # Традиционные модели
                scaler = self.scalers.get('traditional_scaler')
                if scaler and model_name not in ['XGBoost', 'LightGBM']:
                    scaled_features = scaler.transform(features)
                    predictions = model.predict(scaled_features)
                else:
                    predictions = model.predict(features)

                # Для множественных предсказаний повторяем последнее
                if len(predictions) == 1 and periods > 1:
                    predictions = np.repeat(predictions, periods)

                return predictions

        except Exception as e:
            logger.error(f"Ошибка прогнозирования с моделью {model_name}: {e}")
            raise

    def ensemble_predict(self, features: pd.DataFrame, periods: int = 24,
                        models_to_use: Optional[List[str]] = None) -> Dict[str, np.ndarray]:
        """
        Ансамблевое прогнозирование

        Args:
            features: Признаки
            periods: Количество периодов
            models_to_use: Список моделей для использования

        Returns:
            Словарь с прогнозами каждой модели и средним
        """
        if models_to_use is None:
            models_to_use = list(self.models.keys())

        predictions = {}

        for model_name in models_to_use:
            try:
                pred = self.predict_price(model_name, features, periods)
                predictions[model_name] = pred
            except Exception as e:
                logger.warning(f"Не удалось получить прогноз от {model_name}: {e}")

        if predictions:
            # Средний прогноз
            all_preds = list(predictions.values())
            predictions['ensemble_mean'] = np.mean(all_preds, axis=0)

            # Взвешенный прогноз (по R²)
            weights = []
            weighted_preds = []

            for model_name in predictions.keys():
                if model_name != 'ensemble_mean' and model_name in self.models:
                    r2 = self.models[model_name].get('r2', 0)
                    if r2 > 0:
                        weights.append(r2)
                        weighted_preds.append(predictions[model_name])

            if weighted_preds:
                weights = np.array(weights) / sum(weights)  # Нормализация
                predictions['ensemble_weighted'] = np.average(weighted_preds, weights=weights, axis=0)

        return predictions

    def save_models(self):
        """Сохранение всех моделей"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        for model_name, model_info in self.models.items():
            try:
                if model_name == 'LSTM':
                    if KERAS_AVAILABLE and 'model' in model_info:
                        model_path = self.model_save_path / f"lstm_model_{timestamp}.h5"
                        model_info['model'].save(model_path)
                else:
                    model_path = self.model_save_path / f"{model_name}_{timestamp}.pkl"
                    with open(model_path, 'wb') as f:
                        pickle.dump(model_info, f)

                logger.info(f"Модель {model_name} сохранена")

            except Exception as e:
                logger.error(f"Ошибка сохранения модели {model_name}: {e}")

        # Сохранение скейлеров
        scaler_path = self.model_save_path / f"scalers_{timestamp}.pkl"
        with open(scaler_path, 'wb') as f:
            pickle.dump(self.scalers, f)

    def load_model(self, model_path: str, model_name: str):
        """Загрузка модели"""
        try:
            if model_name == 'LSTM':
                if not KERAS_AVAILABLE:
                    raise ImportError("TensorFlow недоступен")
                model = tf.keras.models.load_model(model_path)
                self.models[model_name] = {'model': model}
            else:
                with open(model_path, 'rb') as f:
                    self.models[model_name] = pickle.load(f)

            logger.info(f"Модель {model_name} загружена из {model_path}")

        except Exception as e:
            logger.error(f"Ошибка загрузки модели {model_name}: {e}")

    def get_model_performance(self) -> pd.DataFrame:
        """
        Получение производительности всех моделей

        Returns:
            DataFrame с метриками производительности
        """
        performance_data = []

        for model_name, model_info in self.models.items():
            if 'rmse' in model_info:
                performance_data.append({
                    'Model': model_name,
                    'RMSE': model_info.get('rmse', np.nan),
                    'MAE': model_info.get('mae', np.nan),
                    'R²': model_info.get('r2', np.nan),
                    'MSE': model_info.get('mse', np.nan)
                })

        if performance_data:
            df = pd.DataFrame(performance_data)
            return df.sort_values('RMSE')

        return pd.DataFrame()


if __name__ == "__main__":
    # Пример использования
    import logging
    logging.basicConfig(level=logging.INFO)

    # Создание тестовых данных
    np.random.seed(42)
    dates = pd.date_range(start='2023-01-01', periods=1000, freq='H')

    # Симуляция криптовалютных данных с трендом и волатильностью
    price = 50000
    prices = []
    volumes = []

    for i in range(len(dates)):
        trend = 0.0001 * i  # Восходящий тренд
        volatility = np.random.normal(0, 0.02)
        price = price * (1 + trend + volatility)
        prices.append(price)
        volumes.append(np.random.randint(100, 1000))

    df = pd.DataFrame({
        'open': prices,
        'high': [p * (1 + abs(np.random.normal(0, 0.01))) for p in prices],
        'low': [p * (1 - abs(np.random.normal(0, 0.01))) for p in prices],
        'close': prices,
        'volume': volumes
    }, index=dates)

    # Добавление технических индикаторов (упрощенно)
    from src.analysis.technical_indicators import TechnicalIndicators
    df = TechnicalIndicators.calculate_all_indicators(df)

    print(f"📊 Данные подготовлены: {len(df)} записей")

    # Инициализация предсказателя
    predictor = CryptoPricePredictor()

    # Подготовка признаков
    features_df = predictor.prepare_features(df)
    print(f"🔍 Признаков подготовлено: {features_df.shape[1]}")

    # Целевая переменная (будущая цена)
    target = features_df['close'].shift(-1).dropna()
    features_df = features_df[:-1]  # Удаляем последнюю строку

    # Обучение традиционных моделей
    feature_columns = features_df.select_dtypes(include=[np.number]).columns
    X = features_df[feature_columns].fillna(0)

    results = predictor.train_traditional_models(X, target)

    # Показать производительность
    performance = predictor.get_model_performance()
    print("\n📈 Производительность моделей:")
    print(performance)

    # Пример прогнозирования
    try:
        latest_features = X.tail(1)
        predictions = predictor.ensemble_predict(latest_features, periods=24)

        print(f"\n🔮 Прогнозы на следующие 24 часа:")
        for model_name, pred in predictions.items():
            if len(pred) > 0:
                print(f"{model_name}: {pred[0]:.2f}")

    except Exception as e:
        print(f"Ошибка прогнозирования: {e}")

    # Сохранение моделей
    predictor.save_models()
    print("💾 Модели сохранены")