#!/usr/bin/env python3
"""
Скрипт установки и инициализации проекта анализа криптовалют
"""

import os
import sys
import subprocess
from pathlib import Path
import shutil

def run_command(command, description):
    """Выполнение команды с отображением прогресса"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - успешно")
            return True
        else:
            print(f"❌ {description} - ошибка: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} - исключение: {e}")
        return False

def check_python_version():
    """Проверка версии Python"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Требуется Python 3.8 или выше")
        sys.exit(1)
    else:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro}")

def install_dependencies():
    """Установка зависимостей"""
    print("📦 Установка зависимостей Python...")

    # Обновление pip
    run_command(f"{sys.executable} -m pip install --upgrade pip", "Обновление pip")

    # Установка основных пакетов
    packages = [
        "python-binance",
        "pandas",
        "numpy",
        "matplotlib",
        "seaborn",
        "plotly",
        "scikit-learn",
        "xgboost",
        "lightgbm",
        "python-dotenv",
        "pyyaml",
        "tqdm",
        "jupyter"
    ]

    for package in packages:
        success = run_command(f"{sys.executable} -m pip install {package}", f"Установка {package}")
        if not success:
            print(f"⚠️ Не удалось установить {package}")

    # Попытка установки TensorFlow (опционально)
    print("\n🧠 Попытка установки TensorFlow для LSTM моделей...")
    tf_success = run_command(f"{sys.executable} -m pip install tensorflow", "Установка TensorFlow")
    if not tf_success:
        print("⚠️ TensorFlow не установлен. LSTM модели будут недоступны.")

    # Попытка установки TA-Lib
    print("\n📊 Попытка установки TA-Lib для дополнительных индикаторов...")
    talib_success = run_command(f"{sys.executable} -m pip install TA-Lib", "Установка TA-Lib")
    if not talib_success:
        print("⚠️ TA-Lib не установлен. Используются встроенные индикаторы.")

def create_directories():
    """Создание необходимых директорий"""
    print("📁 Создание структуры директорий...")

    directories = [
        "data/raw",
        "data/processed",
        "data/models",
        "logs",
        "config",
        "tests",
        "notebooks"
    ]

    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"   📂 {directory}")

def setup_config():
    """Настройка конфигурационных файлов"""
    print("⚙️ Настройка конфигурации...")

    # Копирование примера .env файла
    env_example = Path("config/.env.example")
    env_file = Path("config/.env")

    if env_example.exists() and not env_file.exists():
        shutil.copy(env_example, env_file)
        print("   📋 Создан файл config/.env")
        print("   ⚠️  Не забудьте добавить ваши API ключи Binance!")

    # Создание логов директории
    Path("logs").mkdir(exist_ok=True)

def create_gitignore():
    """Создание .gitignore файла"""
    gitignore_content = """
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py,cover
.hypothesis/
.pytest_cache/
cover/

# Environment variables
.env
*.env

# Data files
data/raw/*.csv
data/processed/*.csv
data/models/*.pkl
data/models/*.h5
*.db
*.sqlite3

# Logs
logs/*.log

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Jupyter Notebook
.ipynb_checkpoints

# API keys and secrets
config/.env
config/secrets.yaml
config/api_keys.json
"""

    with open(".gitignore", "w", encoding="utf-8") as f:
        f.write(gitignore_content)
    print("📄 Создан .gitignore файл")

def test_installation():
    """Тестирование установки"""
    print("🧪 Тестирование установки...")

    try:
        # Тест импортов
        print("   🔍 Проверка импортов...")
        sys.path.append(str(Path.cwd()))

        from src.utils.config import config
        from src.data.binance_client import BinanceClient
        from src.analysis.technical_indicators import TechnicalIndicators

        print("   ✅ Импорты успешны")

        # Тест создания экземпляров
        client = BinanceClient()
        indicators = TechnicalIndicators()

        print("   ✅ Создание объектов успешно")

        # Показать конфигурацию
        config.print_config_summary()

        return True

    except Exception as e:
        print(f"   ❌ Ошибка при тестировании: {e}")
        return False

def print_usage_instructions():
    """Инструкции по использованию"""
    print("\n" + "="*60)
    print("🎉 УСТАНОВКА ЗАВЕРШЕНА!")
    print("="*60)

    print("\n📝 СЛЕДУЮЩИЕ ШАГИ:")
    print("-" * 30)
    print("1. 🔑 Добавьте ваши API ключи Binance в config/.env:")
    print("   BINANCE_API_KEY=your_api_key_here")
    print("   BINANCE_SECRET_KEY=your_secret_key_here")

    print("\n2. 📊 Соберите данные:")
    print("   python main.py --collect-data --symbols BTCUSDT ETHUSDT")

    print("\n3. 🤖 Обучите модели:")
    print("   python main.py --train-models --symbol BTCUSDT")

    print("\n4. 🔮 Создайте прогноз:")
    print("   python main.py --predict --symbol BTCUSDT --horizon 24")

    print("\n5. 📱 Запустите Jupyter Notebook:")
    print("   jupyter notebook notebooks/crypto_analysis_demo.ipynb")

    print("\n💡 ПОЛЕЗНЫЕ КОМАНДЫ:")
    print("-" * 20)
    print("• Показать конфигурацию: python main.py --config")
    print("• Анализ портфеля: python main.py --portfolio")
    print("• Обновить данные: python main.py --update-data")
    print("• Помощь: python main.py --help")

    print("\n📚 ДОКУМЕНТАЦИЯ:")
    print("-" * 18)
    print("• README.md - общая информация")
    print("• Jupyter Notebook - интерактивные примеры")
    print("• src/ - исходный код модулей")

    print("\n⚠️ ВАЖНЫЕ НАПОМИНАНИЯ:")
    print("-" * 22)
    print("• Это система для анализа, а не для торговли")
    print("• Всегда проверяйте результаты на исторических данных")
    print("• Управляйте рисками и не инвестируйте больше, чем можете потерять")
    print("• Регулярно обновляйте данные для актуальности прогнозов")

def main():
    """Главная функция установки"""
    print("🚀 Установка системы анализа криптовалют")
    print("="*50)

    # Проверка версии Python
    check_python_version()

    # Создание директорий
    create_directories()

    # Установка зависимостей
    install_dependencies()

    # Настройка конфигурации
    setup_config()

    # Создание .gitignore
    create_gitignore()

    # Тестирование установки
    test_success = test_installation()

    if test_success:
        # Инструкции по использованию
        print_usage_instructions()
    else:
        print("\n❌ Установка завершена с ошибками")
        print("Проверьте сообщения об ошибках выше")
        sys.exit(1)

if __name__ == "__main__":
    main()