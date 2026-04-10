"""
Crypto Market Analysis & Prediction System

Система анализа и прогнозирования криптовалютных рынков с использованием
машинного обучения и технического анализа.
"""

__version__ = "1.0.0"
__author__ = "Crypto Analysis System"
__description__ = "Advanced cryptocurrency market analysis and prediction system"

from .utils.config import config
from .data.binance_client import BinanceClient
from .data.data_collector import DataCollector
from .analysis.technical_indicators import TechnicalIndicators
from .prediction.ml_models import CryptoPricePredictor

__all__ = [
    'config',
    'BinanceClient',
    'DataCollector',
    'TechnicalIndicators',
    'CryptoPricePredictor'
]