#!/usr/bin/env python3
"""
Schema Validator для Crypto Intelligence System V10.0-r1
Валидация JSON объектов по схемам из SCHEMAS/
"""

import json
import os
import logging
from pathlib import Path
from typing import Dict, Tuple, List, Any
from datetime import datetime

try:
    from jsonschema import validate, ValidationError, SchemaError
except ImportError:
    raise ImportError("Требуется установить jsonschema: pip install jsonschema")


class SchemaValidator:
    """
    Валидатор JSON объектов по схемам

    Загружает схемы из SCHEMAS/ и кэширует их
    Валидирует объекты и возвращает (bool, list[str])
    Логирует ошибки в LAYER_H_INTERFACE/logs/schema_validation.log
    """

    def __init__(self, market_mind_root: str = None):
        if market_mind_root is None:
            market_mind_root = Path(__file__).parent.parent
        else:
            market_mind_root = Path(market_mind_root)

        self.market_mind_root = market_mind_root
        self.schemas_dir = self.market_mind_root / "SCHEMAS"
        self.log_dir = self.market_mind_root / "LAYER_H_INTERFACE" / "logs"

        # Создаем директорию для логов если не существует
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Настраиваем логирование
        self._setup_logging()

        # Кэш для загруженных схем
        self._schema_cache: Dict[str, Dict] = {}

        self.logger.info("SchemaValidator инициализирован")

    def _setup_logging(self):
        """Настройка логирования ошибок валидации"""
        log_file = self.log_dir / "schema_validation.log"

        self.logger = logging.getLogger("schema_validator")
        self.logger.setLevel(logging.INFO)

        # Удаляем существующие handlers
        self.logger.handlers.clear()

        # Файловый handler
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)

        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)

    def _load_schema(self, schema_name: str) -> Dict:
        """
        Загружает схему из файла и кэширует её

        Args:
            schema_name: Имя схемы без расширения (например, 'ohlcv_candle')

        Returns:
            Dict: JSON схема

        Raises:
            FileNotFoundError: Если файл схемы не найден
            json.JSONDecodeError: Если схема содержит некорректный JSON
        """
        if schema_name in self._schema_cache:
            return self._schema_cache[schema_name]

        schema_file = self.schemas_dir / f"{schema_name}.json"

        if not schema_file.exists():
            raise FileNotFoundError(f"Схема не найдена: {schema_file}")

        try:
            with open(schema_file, 'r', encoding='utf-8') as f:
                schema = json.load(f)

            # Кэшируем схему
            self._schema_cache[schema_name] = schema

            self.logger.info(f"Схема загружена и закэширована: {schema_name}")
            return schema

        except json.JSONDecodeError as e:
            error_msg = f"Некорректный JSON в схеме {schema_name}: {e}"
            self.logger.error(error_msg)
            raise json.JSONDecodeError(error_msg, e.doc, e.pos)

    def validate(self, obj: Any, schema_name: str) -> Tuple[bool, List[str]]:
        """
        Валидирует объект по указанной схеме

        Args:
            obj: Объект для валидации
            schema_name: Имя схемы без расширения

        Returns:
            Tuple[bool, List[str]]: (успех, список ошибок)
        """
        errors = []

        try:
            # Загружаем схему
            schema = self._load_schema(schema_name)

            # Валидируем объект
            validate(instance=obj, schema=schema)

            self.logger.info(f"Валидация успешна: {schema_name}")
            return True, []

        except FileNotFoundError as e:
            error_msg = f"Схема не найдена: {schema_name}"
            errors.append(error_msg)
            self.logger.error(f"Ошибка валидации: {error_msg}")

        except json.JSONDecodeError as e:
            error_msg = f"Некорректная схема {schema_name}: {str(e)}"
            errors.append(error_msg)
            self.logger.error(f"Ошибка валидации: {error_msg}")

        except ValidationError as e:
            error_msg = f"Объект не соответствует схеме {schema_name}: {e.message}"
            if e.path:
                error_msg += f" (путь: {'.'.join(map(str, e.path))})"
            errors.append(error_msg)
            self.logger.error(f"Ошибка валидации: {error_msg}")

        except SchemaError as e:
            error_msg = f"Некорректная схема {schema_name}: {e.message}"
            errors.append(error_msg)
            self.logger.error(f"Ошибка схемы: {error_msg}")

        except Exception as e:
            error_msg = f"Неожиданная ошибка валидации {schema_name}: {str(e)}"
            errors.append(error_msg)
            self.logger.error(f"Неожиданная ошибка: {error_msg}")

        return False, errors

    def get_available_schemas(self) -> List[str]:
        """
        Возвращает список доступных схем

        Returns:
            List[str]: Список имен схем без расширения
        """
        if not self.schemas_dir.exists():
            return []

        schemas = []
        for schema_file in self.schemas_dir.glob("*.json"):
            schemas.append(schema_file.stem)

        return sorted(schemas)

    def clear_cache(self):
        """Очищает кэш схем"""
        self._schema_cache.clear()
        self.logger.info("Кэш схем очищен")

    def reload_schema(self, schema_name: str):
        """Перезагружает конкретную схему"""
        if schema_name in self._schema_cache:
            del self._schema_cache[schema_name]

        # Загружаем заново
        self._load_schema(schema_name)
        self.logger.info(f"Схема перезагружена: {schema_name}")


def main():
    """Тестирование Schema Validator"""
    print("🧪 Тестирование Schema Validator")

    validator = SchemaValidator()

    # Тест валидной OHLCV свечи
    candle = {
        "symbol": "BTCUSDT",
        "timestamp": 1700000000000,
        "open": 45000.0,
        "high": 45500.0,
        "low": 44800.0,
        "close": 45200.0,
        "volume": 1234.5,
        "quality_flag": "ok",
        "data_stale": False
    }

    ok, errors = validator.validate(candle, "ohlcv_candle")
    print(f"Валидная свеча: {ok}, ошибки: {errors}")

    # Тест невалидной свечи (отрицательная цена)
    bad_candle = {
        "symbol": "BTCUSDT",
        "timestamp": 1700000000000,
        "open": -45000.0,  # Некорректная отрицательная цена
        "high": 45500.0,
        "low": 44800.0,
        "close": 45200.0,
        "volume": 1234.5
    }

    ok, errors = validator.validate(bad_candle, "ohlcv_candle")
    print(f"Невалидная свеча: {ok}, ошибки: {errors}")

    # Показываем доступные схемы
    schemas = validator.get_available_schemas()
    print(f"Доступные схемы: {schemas}")


if __name__ == "__main__":
    main()