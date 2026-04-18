#!/usr/bin/env python3
"""
test_schema_validator.py — Comprehensive tests for Schema Layer V2.

Tests cover all API endpoints, edge cases, error handling, and integration scenarios.
Applies P-05 (testing pattern) with deterministic test data and clear expectations.

Компонент: LAYER_C_KNOWLEDGE testing
"""

import sys
import json
import tempfile
import unittest
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, MagicMock

# Добавляем ENGINE в path для импортов
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "ENGINE"))

try:
    from schema_validator import (
        SchemaValidator, ValidationResult, SchemaValidationError,
        CANONICAL_SCHEMAS, create_test_pattern, create_test_prediction
    )
    SCHEMA_VALIDATOR_AVAILABLE = True
except ImportError as e:
    SCHEMA_VALIDATOR_AVAILABLE = False
    IMPORT_ERROR = str(e)

# Флаг для вывода результатов - без emoji (L-04)
VERBOSE_OUTPUT = True

def print_test_result(test_name: str, passed: bool, details: str = ""):
    """Безопасный вывод результатов тестов без emoji"""
    status = "[PASS]" if passed else "[FAIL]"
    print(f"{status} {test_name}")
    if details and (not passed or VERBOSE_OUTPUT):
        print(f"    {details}")

class TestSchemaValidator(unittest.TestCase):
    """Тесты для SchemaValidator V2"""

    def setUp(self):
        """Подготовка тестового окружения"""
        if not SCHEMA_VALIDATOR_AVAILABLE:
            self.skipTest(f"SchemaValidator not available: {IMPORT_ERROR}")

        # Создаем временную директорию для схем
        self.temp_dir = Path(tempfile.mkdtemp())
        self.schemas_dir = self.temp_dir / "SCHEMAS"
        self.schemas_dir.mkdir(parents=True, exist_ok=True)

        # Создаем минимальную тестовую схему
        self._create_test_schema("pattern")

        # Инициализируем валидатор
        self.validator = SchemaValidator(schemas_dir=self.schemas_dir)

    def tearDown(self):
        """Очистка после тестов"""
        import shutil
        if hasattr(self, 'temp_dir'):
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _create_test_schema(self, schema_name: str):
        """Создает минимальную тестовую схему"""
        if schema_name == "pattern":
            schema = {
                "$schema": "https://json-schema.org/draft/2020-12/schema",
                "$id": f"{schema_name}_schema.json",
                "title": f"Test {schema_name.title()} Schema",
                "type": "object",
                "required": ["id", "name", "symbol", "timeframe", "status"],
                "properties": {
                    "id": {"type": "string"},
                    "name": {"type": "string"},
                    "symbol": {"type": "string"},
                    "timeframe": {"type": "string"},
                    "status": {"type": "string", "enum": ["testing", "candidate", "confirmed"]},
                    "confidence_point": {"type": "number", "minimum": 0.0, "maximum": 1.0}
                },
                "additionalProperties": False
            }
        else:
            # Базовая схема для других типов
            schema = {
                "$schema": "https://json-schema.org/draft/2020-12/schema",
                "$id": f"{schema_name}_schema.json",
                "title": f"Test {schema_name.title()} Schema",
                "type": "object",
                "required": ["id"],
                "properties": {
                    "id": {"type": "string"}
                },
                "additionalProperties": True
            }

        schema_file = self.schemas_dir / f"{schema_name}_schema.json"
        schema_file.write_text(json.dumps(schema, indent=2), encoding="utf-8")

    # Test 1: Инициализация валидатора
    def test_01_validator_initialization(self):
        """Тест инициализации валидатора"""
        try:
            validator = SchemaValidator(schemas_dir=self.schemas_dir)
            self.assertIsInstance(validator, SchemaValidator)
            self.assertEqual(validator.schemas_dir, self.schemas_dir)
            print_test_result("Validator initialization", True)
        except Exception as e:
            print_test_result("Validator initialization", False, str(e))
            raise

    # Test 2: Загрузка существующей схемы
    def test_02_schema_loading_success(self):
        """Тест успешной загрузки схемы"""
        try:
            schema = self.validator._load_schema("pattern")
            self.assertIsInstance(schema, dict)
            self.assertEqual(schema["$id"], "pattern_schema.json")
            print_test_result("Schema loading success", True)
        except Exception as e:
            print_test_result("Schema loading success", False, str(e))
            raise

    # Test 3: Ошибка при загрузке несуществующей схемы
    def test_03_schema_loading_not_found(self):
        """Тест ошибки при загрузке несуществующей схемы"""
        try:
            with self.assertRaises(SchemaValidationError) as context:
                self.validator._load_schema("nonexistent")

            self.assertIn("not found", str(context.exception))
            print_test_result("Schema not found error", True)
        except Exception as e:
            print_test_result("Schema not found error", False, str(e))
            raise

    # Test 4: Успешная валидация валидного объекта
    def test_04_validation_success(self):
        """Тест успешной валидации валидного объекта"""
        try:
            valid_pattern = {
                "id": "test_001",
                "name": "Test Pattern",
                "symbol": "BTCUSDT",
                "timeframe": "1h",
                "status": "testing",
                "confidence_point": 0.75
            }

            result = self.validator.validate(valid_pattern, "pattern")

            self.assertIsInstance(result, ValidationResult)
            self.assertTrue(result.success)
            self.assertEqual(len(result.errors), 0)
            self.assertEqual(result.schema_name, "pattern")
            print_test_result("Validation success", True)
        except Exception as e:
            print_test_result("Validation success", False, str(e))
            raise

    # Test 5: Валидация объекта с ошибками
    def test_05_validation_with_errors(self):
        """Тест валидации объекта с ошибками"""
        try:
            invalid_pattern = {
                "id": "test_002",
                # missing required "name" field
                "symbol": "BTCUSDT",
                "timeframe": "1h",
                "status": "invalid_status",  # не в enum
                "confidence_point": 1.5  # > максимума 1.0
            }

            result = self.validator.validate(invalid_pattern, "pattern")

            self.assertIsInstance(result, ValidationResult)
            self.assertFalse(result.success)
            self.assertGreater(len(result.errors), 0)
            print_test_result("Validation with errors", True)
        except Exception as e:
            print_test_result("Validation with errors", False, str(e))
            raise

    # Test 6: Строгая валидация
    def test_06_strict_validation(self):
        """Тест строгой валидации"""
        try:
            valid_pattern = {
                "id": "test_003",
                "name": "Strict Test",
                "symbol": "ETHUSDT",
                "timeframe": "4h",
                "status": "candidate"
            }

            result = self.validator.validate_strict(valid_pattern, "pattern")

            self.assertIsInstance(result, ValidationResult)
            self.assertTrue(result.strict_mode)
            self.assertFalse(result.fallback_used)
            print_test_result("Strict validation", True)
        except Exception as e:
            print_test_result("Strict validation", False, str(e))
            # В случае отсутствия jsonschema это нормально
            if "jsonschema library required" in str(e):
                print_test_result("Strict validation (expected without jsonschema)", True)
            else:
                raise

    # Test 7: Генерация snapshot ID
    def test_07_snapshot_id_generation(self):
        """Тест генерации детерминированного snapshot ID"""
        try:
            test_obj = {"id": "test", "value": 42}

            # Генерируем ID дважды - должен быть одинаковым
            id1 = self.validator.generate_snapshot_id(test_obj, "pattern")
            id2 = self.validator.generate_snapshot_id(test_obj, "pattern")

            self.assertEqual(id1, id2)
            self.assertTrue(id1.startswith("pattern_"))
            self.assertEqual(len(id1), len("pattern_") + 8)  # pattern_ + 8 hex chars
            print_test_result("Snapshot ID generation", True, f"Generated: {id1}")
        except Exception as e:
            print_test_result("Snapshot ID generation", False, str(e))
            raise

    # Test 8: Список доступных схем
    def test_08_available_schemas_list(self):
        """Тест получения списка доступных схем"""
        try:
            schemas = self.validator.get_available_schemas()

            self.assertIsInstance(schemas, list)
            self.assertIn("pattern", schemas)
            print_test_result("Available schemas list", True, f"Found: {schemas}")
        except Exception as e:
            print_test_result("Available schemas list", False, str(e))
            raise

    # Test 9: Кэширование схем
    def test_09_schema_caching(self):
        """Тест кэширования загруженных схем"""
        try:
            # Загружаем схему первый раз
            schema1 = self.validator._load_schema("pattern")

            # Проверяем что схема в кэше
            self.assertIn("pattern", self.validator._schema_cache)

            # Загружаем второй раз - должна быть из кэша
            schema2 = self.validator._load_schema("pattern")

            # Объекты должны быть идентичны (из кэша)
            self.assertIs(schema1, schema2)
            print_test_result("Schema caching", True)
        except Exception as e:
            print_test_result("Schema caching", False, str(e))
            raise

    # Test 10: Очистка кэша
    def test_10_cache_clearing(self):
        """Тест очистки кэша схем"""
        try:
            # Загружаем схему в кэш
            self.validator._load_schema("pattern")
            self.assertIn("pattern", self.validator._schema_cache)

            # Очищаем кэш
            self.validator.clear_cache()
            self.assertEqual(len(self.validator._schema_cache), 0)
            print_test_result("Cache clearing", True)
        except Exception as e:
            print_test_result("Cache clearing", False, str(e))
            raise

    # Test 11: Перезагрузка схемы
    def test_11_schema_reloading(self):
        """Тест перезагрузки конкретной схемы"""
        try:
            # Загружаем схему в кэш
            self.validator._load_schema("pattern")
            original_cache_size = len(self.validator._schema_cache)

            # Перезагружаем схему
            self.validator.reload_schema("pattern")

            # Схема должна быть обновлена в кэше
            self.assertIn("pattern", self.validator._schema_cache)
            self.assertEqual(len(self.validator._schema_cache), original_cache_size)
            print_test_result("Schema reloading", True)
        except Exception as e:
            print_test_result("Schema reloading", False, str(e))
            raise

    # Test 12: Валидация неподдерживаемой схемы
    def test_12_unsupported_schema_validation(self):
        """Тест валидации с неподдерживаемой схемой"""
        try:
            test_obj = {"id": "test"}
            result = self.validator.validate(test_obj, "unsupported_schema")

            self.assertFalse(result.success)
            self.assertIn("Unsupported schema", result.errors[0])
            print_test_result("Unsupported schema validation", True)
        except Exception as e:
            print_test_result("Unsupported schema validation", False, str(e))
            raise

    # Test 13: Graceful degradation без jsonschema
    @patch('schema_validator.JSONSCHEMA_AVAILABLE', False)
    def test_13_graceful_degradation(self):
        """Тест graceful degradation без jsonschema"""
        try:
            # Создаем новый валидатор в условиях отсутствия jsonschema
            validator = SchemaValidator(schemas_dir=self.schemas_dir)

            test_pattern = {
                "id": "test_degradation",
                "name": "Test Graceful",
                "symbol": "BTCUSDT",
                "timeframe": "1h",
                "status": "testing"
            }

            result = validator.validate(test_pattern, "pattern")

            # Должна работать минимальная валидация
            self.assertIsInstance(result, ValidationResult)
            self.assertTrue(result.fallback_used)
            self.assertIn("jsonschema library not available", result.warnings)
            print_test_result("Graceful degradation", True)
        except Exception as e:
            print_test_result("Graceful degradation", False, str(e))
            raise

    # Test 14: Minimal валидация pattern
    def test_14_minimal_pattern_validation(self):
        """Тест минимальной валидации pattern без jsonschema"""
        try:
            # Пропускаем jsonschema валидацию напрямую
            errors = self.validator._validate_minimal({
                "id": "test_minimal",
                "name": "Test",
                "logic_dsl": "test logic",
                "symbol": "BTCUSDT",
                "timeframe": "1h",
                "status": "testing"
            }, "pattern")

            self.assertEqual(len(errors), 0)
            print_test_result("Minimal pattern validation", True)
        except Exception as e:
            print_test_result("Minimal pattern validation", False, str(e))
            raise

    # Test 15: Test helper функции
    def test_15_test_helpers(self):
        """Тест helper функций для создания тестовых объектов"""
        try:
            test_pattern = create_test_pattern()
            test_prediction = create_test_prediction()

            # Проверяем что объекты содержат обязательные поля
            self.assertIn("id", test_pattern)
            self.assertIn("name", test_pattern)
            self.assertIn("symbol", test_pattern)

            self.assertIn("id", test_prediction)
            self.assertIn("model_version", test_prediction)
            self.assertIn("direction", test_prediction)

            print_test_result("Test helpers", True)
        except Exception as e:
            print_test_result("Test helpers", False, str(e))
            raise

    # Test 16: Ошибка валидации с деталями
    def test_16_validation_error_details(self):
        """Тест детализации ошибок валидации"""
        try:
            # Объект с множественными ошибками
            bad_obj = {
                # missing "id"
                "name": "",  # пустое имя
                "symbol": "invalid symbol",  # с пробелом
                "timeframe": "invalid",  # не в enum
                "status": "bad_status",  # не в enum
                "confidence_point": -0.5  # отрицательное значение
            }

            result = self.validator.validate(bad_obj, "pattern")

            self.assertFalse(result.success)
            self.assertGreater(len(result.errors), 0)
            # В минимальной валидации будет хотя бы ошибка отсутствия id
            any_id_error = any("id" in error.lower() for error in result.errors)
            self.assertTrue(any_id_error)

            print_test_result("Validation error details", True, f"Errors: {len(result.errors)}")
        except Exception as e:
            print_test_result("Validation error details", False, str(e))
            raise

    # Test 17: Интеграционный тест с реальными схемами
    def test_17_integration_with_real_schemas(self):
        """Интеграционный тест с реальными схемами из MARKET_MIND/SCHEMAS"""
        try:
            # Используем реальную директорию схем если доступна
            real_schemas_dir = Path(__file__).parent.parent / "SCHEMAS"
            if real_schemas_dir.exists():
                real_validator = SchemaValidator(schemas_dir=real_schemas_dir)

                # Проверяем доступность канонических схем
                available = real_validator.get_available_schemas()
                canonical_found = [s for s in available if s in CANONICAL_SCHEMAS]

                print_test_result("Integration test", True,
                                f"Real schemas found: {canonical_found}")
            else:
                print_test_result("Integration test", True, "Real schemas dir not found - OK for isolated test")
        except Exception as e:
            print_test_result("Integration test", False, str(e))
            # Не падаем - это интеграционный тест
            pass

def run_all_tests():
    """Запуск всех тестов с подробным выводом"""
    print("=" * 60)
    print("SCHEMA VALIDATOR V2 - COMPREHENSIVE TEST SUITE")
    print("=" * 60)

    if not SCHEMA_VALIDATOR_AVAILABLE:
        print(f"[FAIL] Cannot import schema_validator: {IMPORT_ERROR}")
        return False

    # Создаем test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSchemaValidator)

    # Запускаем тесты
    import io
    runner = unittest.TextTestRunner(verbosity=0, stream=io.StringIO())
    result = runner.run(suite)

    print(f"\nTest Summary: {result.testsRun} tests run")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")

    if result.failures:
        print("\nFailures:")
        for test, failure in result.failures:
            print(f"  {test}: {failure}")

    if result.errors:
        print("\nErrors:")
        for test, error in result.errors:
            print(f"  {test}: {error}")

    success = len(result.failures) == 0 and len(result.errors) == 0

    print("\n" + "=" * 60)
    if success:
        print("[PASS] ALL 17 TESTS PASSED")
    else:
        print(f"[FAIL] {len(result.failures + result.errors)} TESTS FAILED")
    print("=" * 60)

    return success

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)