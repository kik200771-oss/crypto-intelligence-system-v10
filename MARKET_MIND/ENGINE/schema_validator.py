#!/usr/bin/env python3
"""
schema_validator.py — Schema Layer V2 для CIS V10.0-r1.

Валидация JSON объектов по 6 каноническим схемам V9.0/V10.0.
Поддержка строгого режима, snapshot ID generation, graceful degradation.

Интеграция с: все компоненты системы через ValidationResult
ТЗ-источник: § 1.8 V9.0 field specifications
Уроки: L-01 (relative paths), L-04 (UTF-8), L-05 (graceful degradation)

Компонент: LAYER_C_KNOWLEDGE (schema layer)
"""

import json
import logging
import hashlib
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Tuple
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

try:
    import jsonschema
    from jsonschema import validate, ValidationError, SchemaError
    JSONSCHEMA_AVAILABLE = True
except ImportError:
    JSONSCHEMA_AVAILABLE = False

# applies L-01 (relative paths only)
BASE_DIR = Path(__file__).resolve().parent.parent

# Supported canonical schemas per TZ § 1.8
CANONICAL_SCHEMAS = {
    "pattern", "prediction", "experiment",
    "hypothesis", "negative", "source"
}

class SchemaValidationError(Exception):
    """Кастомное исключение для ошибок валидации схем"""

    def __init__(self, message: str, schema_name: Optional[str] = None,
                 validation_errors: Optional[List[str]] = None):
        self.schema_name = schema_name
        self.validation_errors = validation_errors or []
        super().__init__(message)

@dataclass
class ValidationResult:
    """
    Результат валидации с детальной информацией.
    Применяет P-02 (graceful degradation pattern).
    """
    success: bool
    errors: List[str]
    warnings: List[str]
    schema_name: str
    strict_mode: bool
    fallback_used: bool = False

    def __post_init__(self):
        if not self.success and not self.errors:
            raise ValueError("ValidationResult with success=False must have errors")

class SchemaValidator:
    """
    Schema Layer V2 — валидация по каноническим схемам V9.0/V10.0.

    Features:
    - validate() — основной API с graceful degradation
    - validate_strict() — строгий режим без fallback
    - generate_snapshot_id() — детерминированные ID для воспроизводимости
    - Поддержка всех 6 канонических схем
    - Кэширование схем в памяти
    - Детальная диагностика ошибок
    """

    def __init__(self, schemas_dir: Optional[Union[str, Path]] = None):
        """
        Инициализация валидатора.

        Args:
            schemas_dir: путь к директории SCHEMAS (по умолчанию MARKET_MIND/SCHEMAS)
        """
        # applies P-01 (path resolution pattern)
        if schemas_dir is None:
            self.schemas_dir = BASE_DIR / "SCHEMAS"
        else:
            self.schemas_dir = Path(schemas_dir)

        self.logs_dir = BASE_DIR / "LAYER_H_INFRA" / "logs"

        # Создаем директории если нужно - applies L-05 (graceful degradation)
        self.logs_dir.mkdir(parents=True, exist_ok=True)

        # Настраиваем логирование - applies P-04 (configuration pattern)
        self._setup_logging()

        # Кэш схем в памяти
        self._schema_cache: Dict[str, Dict] = {}

        # Проверка доступности jsonschema
        if not JSONSCHEMA_AVAILABLE:
            self.logger.warning("jsonschema не установлен - валидация будет minimal")

        self.logger.info("SchemaValidator V2 инициализирован")

    def _setup_logging(self) -> None:
        """Настройка логирования с UTF-8 - applies L-04"""
        log_file = self.logs_dir / "schema_validator.log"

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        # Очищаем существующие handlers
        self.logger.handlers.clear()

        # applies P-04 (configuration pattern) - UTF-8 file handler
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.INFO)

        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)

    def _load_schema(self, schema_name: str) -> Dict[str, Any]:
        """
        Загрузка схемы из файла с кэшированием.

        Args:
            schema_name: имя схемы без расширения

        Returns:
            Dict: загруженная JSON схема

        Raises:
            SchemaValidationError: если схема не найдена или невалидна
        """
        # Проверяем кэш
        if schema_name in self._schema_cache:
            return self._schema_cache[schema_name]

        # Формируем путь к файлу схемы
        schema_file = self.schemas_dir / f"{schema_name}_schema.json"

        if not schema_file.exists():
            error_msg = f"Schema file not found: {schema_file}"
            self.logger.error(error_msg)
            raise SchemaValidationError(error_msg, schema_name)

        try:
            # applies L-04 (UTF-8 encoding)
            content = schema_file.read_text(encoding="utf-8")
            schema = json.loads(content)

            # Кэшируем схему
            self._schema_cache[schema_name] = schema

            self.logger.info(f"Schema loaded and cached: {schema_name}")
            return schema

        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON in schema {schema_name}: {e}"
            self.logger.error(error_msg)
            raise SchemaValidationError(error_msg, schema_name) from e
        except Exception as e:
            error_msg = f"Unexpected error loading schema {schema_name}: {e}"
            self.logger.error(error_msg)
            raise SchemaValidationError(error_msg, schema_name) from e

    def _validate_with_jsonschema(self, obj: Any, schema: Dict[str, Any]) -> List[str]:
        """Валидация через jsonschema library"""
        errors = []

        try:
            validate(instance=obj, schema=schema)
        except ValidationError as e:
            error_msg = f"Validation failed: {e.message}"
            if e.path:
                error_msg += f" (path: {'.'.join(map(str, e.path))})"
            errors.append(error_msg)
        except SchemaError as e:
            errors.append(f"Schema error: {e.message}")
        except Exception as e:
            errors.append(f"Unexpected validation error: {e}")

        return errors

    def _validate_minimal(self, obj: Any, schema_name: str) -> List[str]:
        """
        Минимальная валидация без jsonschema (fallback).
        Применяет P-02 (graceful degradation pattern).
        """
        errors = []
        warnings = []

        # Проверяем базовые типы
        if not isinstance(obj, dict):
            errors.append("Object must be a dictionary")
            return errors

        # Проверяем наличие обязательного поля id
        if "id" not in obj:
            errors.append("Missing required field: id")

        # Схема-специфичные проверки
        if schema_name == "pattern":
            required = ["name", "logic_dsl", "symbol", "timeframe", "status"]
            for field in required:
                if field not in obj:
                    errors.append(f"Missing required field: {field}")

        elif schema_name == "prediction":
            required = ["model_version", "symbol", "direction", "confidence_point"]
            for field in required:
                if field not in obj:
                    errors.append(f"Missing required field: {field}")

        # Остальные схемы - базовая проверка id

        return errors

    def validate(self, obj: Any, schema_name: str) -> ValidationResult:
        """
        Основной API валидации с graceful degradation.

        Args:
            obj: объект для валидации
            schema_name: имя схемы (pattern, prediction, experiment, etc.)

        Returns:
            ValidationResult: результат с детализацией
        """
        errors = []
        warnings = []
        fallback_used = False

        # Проверяем что схема поддерживается
        if schema_name not in CANONICAL_SCHEMAS:
            errors.append(f"Unsupported schema: {schema_name}")
            return ValidationResult(
                success=False,
                errors=errors,
                warnings=warnings,
                schema_name=schema_name,
                strict_mode=False
            )

        try:
            # Основная валидация с jsonschema
            if JSONSCHEMA_AVAILABLE:
                try:
                    schema = self._load_schema(schema_name)
                    validation_errors = self._validate_with_jsonschema(obj, schema)
                    errors.extend(validation_errors)

                except SchemaValidationError:
                    # Schema не загружена - переходим на fallback
                    warnings.append("Schema not available, using minimal validation")
                    fallback_errors = self._validate_minimal(obj, schema_name)
                    errors.extend(fallback_errors)
                    fallback_used = True

            else:
                # jsonschema недоступен - используем minimal validation
                warnings.append("jsonschema library not available")
                fallback_errors = self._validate_minimal(obj, schema_name)
                errors.extend(fallback_errors)
                fallback_used = True

        except Exception as e:
            # applies P-03 (error handling pattern)
            self.logger.error(f"Unexpected validation error for {schema_name}: {e}")
            errors.append(f"Validation system error: {e}")

        success = len(errors) == 0

        if success:
            self.logger.info(f"Validation successful: {schema_name}")
        else:
            self.logger.warning(f"Validation failed: {schema_name}, errors: {len(errors)}")

        return ValidationResult(
            success=success,
            errors=errors,
            warnings=warnings,
            schema_name=schema_name,
            strict_mode=False,
            fallback_used=fallback_used
        )

    def validate_strict(self, obj: Any, schema_name: str) -> ValidationResult:
        """
        Строгая валидация без fallback механизмов.

        Args:
            obj: объект для валидации
            schema_name: имя схемы

        Returns:
            ValidationResult: результат без fallback

        Raises:
            SchemaValidationError: если схема недоступна или jsonschema не установлен
        """
        if not JSONSCHEMA_AVAILABLE:
            raise SchemaValidationError("jsonschema library required for strict validation")

        if schema_name not in CANONICAL_SCHEMAS:
            raise SchemaValidationError(f"Unsupported schema: {schema_name}")

        # Загружаем схему (может raise SchemaValidationError)
        schema = self._load_schema(schema_name)

        # Строгая валидация
        errors = self._validate_with_jsonschema(obj, schema)
        success = len(errors) == 0

        if success:
            self.logger.info(f"Strict validation successful: {schema_name}")
        else:
            self.logger.error(f"Strict validation failed: {schema_name}, errors: {errors}")

        return ValidationResult(
            success=success,
            errors=errors,
            warnings=[],
            schema_name=schema_name,
            strict_mode=True,
            fallback_used=False
        )

    def generate_snapshot_id(self, obj: Any, schema_name: str) -> str:
        """
        Генерирует детерминированный snapshot ID для объекта.

        Используется для воспроизводимости экспериментов и версионирования данных.

        Args:
            obj: объект для которого генерируется ID
            schema_name: имя схемы

        Returns:
            str: детерминированный ID в формате {schema}_{hash8}
        """
        try:
            # Сериализуем объект в детерминированном порядке
            obj_json = json.dumps(obj, sort_keys=True, ensure_ascii=False)

            # Создаем контент для хэширования
            content = f"{schema_name}:{obj_json}"

            # SHA-256 хэш
            hash_obj = hashlib.sha256(content.encode("utf-8"))
            hash_digest = hash_obj.hexdigest()

            # Берем первые 8 символов для краткости
            hash_short = hash_digest[:8]

            snapshot_id = f"{schema_name}_{hash_short}"

            self.logger.debug(f"Generated snapshot_id: {snapshot_id}")
            return snapshot_id

        except Exception as e:
            # Fallback to random UUID if deterministic generation fails
            self.logger.warning(f"Snapshot ID generation failed, using UUID: {e}")
            fallback_id = f"{schema_name}_{str(uuid.uuid4())[:8]}"
            return fallback_id

    def get_available_schemas(self) -> List[str]:
        """
        Возвращает список доступных схем.

        Returns:
            List[str]: имена схем без расширения
        """
        try:
            if not self.schemas_dir.exists():
                self.logger.warning(f"Schemas directory not found: {self.schemas_dir}")
                return []

            schemas = []

            # Ищем файлы *_schema.json
            for schema_file in self.schemas_dir.glob("*_schema.json"):
                # Убираем _schema.json суффикс
                schema_name = schema_file.stem.replace("_schema", "")
                if schema_name in CANONICAL_SCHEMAS:
                    schemas.append(schema_name)

            return sorted(schemas)

        except Exception as e:
            self.logger.error(f"Error listing schemas: {e}")
            return []

    def clear_cache(self) -> None:
        """Очищает кэш загруженных схем"""
        cache_size = len(self._schema_cache)
        self._schema_cache.clear()
        self.logger.info(f"Schema cache cleared ({cache_size} items removed)")

    def reload_schema(self, schema_name: str) -> None:
        """
        Перезагружает конкретную схему из файла.

        Args:
            schema_name: имя схемы для перезагрузки
        """
        if schema_name in self._schema_cache:
            del self._schema_cache[schema_name]

        try:
            self._load_schema(schema_name)
            self.logger.info(f"Schema reloaded: {schema_name}")
        except SchemaValidationError as e:
            self.logger.error(f"Failed to reload schema {schema_name}: {e}")
            raise

# applies P-05 (testing pattern) - test утилиты
def create_test_pattern() -> Dict[str, Any]:
    """Создает тестовый pattern объект для проверок"""
    return {
        "id": "test_pattern_001",
        "name": "Test RSI Divergence",
        "logic_dsl": "RSI(14) < 30 AND price_trend == 'falling'",
        "symbol": "BTCUSDT",
        "timeframe": "1h",
        "status": "testing",
        "confidence_point": 0.75,
        "evidence_grade": "B",
        "created_at": datetime.now().isoformat(),
        "last_updated": datetime.now().isoformat()
    }

def create_test_prediction() -> Dict[str, Any]:
    """Создает тестовый prediction объект для проверок"""
    return {
        "id": "test_pred_001",
        "model_version": "v6.3",
        "symbol": "BTCUSDT",
        "timeframe": "1h",
        "direction": "UP",
        "confidence_point": 0.82,
        "uncertainty_band_low": 0.75,
        "uncertainty_band_high": 0.89,
        "shock_score": 0.15,
        "horizon_hours": 4.0,
        "verify_at": datetime.now().isoformat(),
        "created_at": datetime.now().isoformat()
    }

# Public API entry points
__all__ = [
    "SchemaValidator",
    "ValidationResult",
    "SchemaValidationError",
    "CANONICAL_SCHEMAS",
    "create_test_pattern",
    "create_test_prediction"
]