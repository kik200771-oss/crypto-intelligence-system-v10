#!/usr/bin/env python3
"""
Financial CTO - Complete Task Lifecycle Manager
Автоматический мониторинг новых задач + завершение + архивирование
"""

import json
import os
import shutil
from pathlib import Path
from datetime import datetime
import logging
import time
import hashlib

class TaskLifecycleManager:
    """
    Financial CTO - полная система управления жизненным циклом задач:
    1. Отслеживание новых задач в ACTIVE
    2. Мониторинг их выполнения
    3. Автоматическое архивирование после завершения
    """

    def __init__(self, project_root="C:\\КОДИНГ\\MARKET ANALYSIS"):
        self.project_root = Path(project_root)
        self.tasks_dir = self.project_root / "TASKS"
        self.active_dir = self.tasks_dir / "ACTIVE"
        self.completed_dir = self.tasks_dir / "COMPLETED"
        self.history_dir = self.project_root / "HISTORY"
        self.market_mind_dir = self.project_root / "MARKET_MIND"
        self.engine_dir = self.project_root / "ENGINE"

        self.task_log_file = self.history_dir / "task_log.json"
        self.state_file = self.history_dir / "cto_monitoring_state.json"

        # Financial CTO logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - FINANCIAL_CTO - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger("FinancialCTO.Lifecycle")

        # Состояние мониторинга
        self.monitoring_state = self.load_monitoring_state()

    def load_monitoring_state(self):
        """Загрузка состояния мониторинга CTO"""
        try:
            with open(self.state_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            # Инициализация состояния
            initial_state = {
                "last_check": datetime.now().isoformat(),
                "known_active_tasks": {},  # task_file -> {hash, registered_time}
                "monitoring_enabled": True,
                "check_interval_seconds": 60
            }
            self.save_monitoring_state(initial_state)
            return initial_state

    def save_monitoring_state(self, state):
        """Сохранение состояния мониторинга"""
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)

    def get_file_hash(self, file_path):
        """Получение хеша файла для отслеживания изменений"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except:
            return None

    def discover_active_tasks(self):
        """
        Обнаружение новых задач в ACTIVE директории
        Financial CTO автоматически регистрирует все новые .md файлы
        """
        current_tasks = {}
        new_tasks = []

        # Сканируем ACTIVE директорию
        if not self.active_dir.exists():
            return [], current_tasks

        for task_file in self.active_dir.glob("*.md"):
            file_key = task_file.name
            file_hash = self.get_file_hash(task_file)

            current_tasks[file_key] = {
                "hash": file_hash,
                "path": str(task_file),
                "discovered_time": datetime.now().isoformat()
            }

            # Проверяем, новая ли это задача
            if file_key not in self.monitoring_state["known_active_tasks"]:
                new_tasks.append({
                    "file": file_key,
                    "path": str(task_file),
                    "hash": file_hash
                })
                self.logger.info(f"NEW TASK DISCOVERED: {file_key}")

        return new_tasks, current_tasks

    def register_new_task(self, task_info):
        """
        Регистрация новой задачи в системе Financial CTO
        """
        task_file = task_info["file"]
        task_path = task_info["path"]

        try:
            # Читаем содержимое задачи для извлечения метаданных
            with open(task_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Простое извлечение названия задачи из заголовка
            task_name = "unknown_task"
            lines = content.split('\n')
            for line in lines[:10]:  # Ищем в первых 10 строках
                if line.strip().startswith('#') and ('ЗАДАЧА' in line or 'TASK' in line):
                    task_name = line.strip().replace('#', '').strip()
                    break

            # Генерируем task_id
            task_counter = self.get_next_task_counter()
            task_id = f"task_{task_counter:03d}"

            # Регистрируем в tracking системе
            task_log = self.load_task_log()
            if not task_log:
                task_log = self.create_initial_task_log()

            task_entry = {
                "task_id": task_id,
                "task_name": task_name,
                "task_file": task_info["path"],
                "status": "REGISTERED",
                "registered_by": "Financial_CTO_Auto_Discovery",
                "registered_time": datetime.now().isoformat(),
                "file_hash": task_info["hash"]
            }

            task_log["tasks"].append(task_entry)
            task_log["task_counter"] = task_counter
            self.save_task_log(task_log)

            self.logger.info(f"Task registered: {task_id} - {task_name}")
            return task_id

        except Exception as e:
            self.logger.error(f"Failed to register task {task_file}: {e}")
            return None

    def detect_task_completion(self, task_id):
        """
        Определение завершения задачи на основе deliverables
        """
        # Загружаем информацию о задаче
        task_log = self.load_task_log()
        task_info = None

        for task in task_log.get("tasks", []):
            if task["task_id"] == task_id:
                task_info = task
                break

        if not task_info:
            return False

        # Различные методы детекции в зависимости от типа задачи
        if "initialize_system" in task_info.get("task_name", "").lower():
            return self.check_initialize_system_completion()
        elif "schema_layer" in task_info.get("task_name", "").lower():
            return self.check_schema_layer_completion()
        elif "data_quality" in task_info.get("task_name", "").lower():
            return self.check_data_quality_completion()
        # TODO: Добавить детекторы для всех типов задач

        # Общий детектор - проверка существования скрипта результата
        script_path = self.engine_dir / "scripts" / f"{task_id}_*.py"
        script_files = list(self.engine_dir.glob(f"scripts/{task_id}*.py"))

        if script_files:
            # Проверяем, был ли скрипт выполнен (по логам или результатам)
            return self.check_script_execution_completion(script_files[0])

        return False

    def check_initialize_system_completion(self):
        """Проверка завершения Task 01 - Initialize System"""
        required_paths = [
            self.market_mind_dir / "CONFIG" / "system_manifest.json",
            self.market_mind_dir / "CONFIG" / "component_status.json",
            self.market_mind_dir / "LAYER_A_RESEARCH",
            self.market_mind_dir / "LAYER_D_MODEL"
        ]

        return all(path.exists() for path in required_paths)

    def check_schema_layer_completion(self):
        """Проверка завершения Task 02 - Schema Layer"""
        schema_dir = self.market_mind_dir / "SCHEMAS"
        if not schema_dir.exists():
            return False

        # Ожидаем минимум 3 схемы
        schema_files = list(schema_dir.glob("*.json"))
        return len(schema_files) >= 3

    def check_data_quality_completion(self):
        """Проверка завершения Task 03 - Data Quality Gates"""
        quality_dir = self.market_mind_dir / "LAYER_B_DATA" / "quality_logs"
        return quality_dir.exists() and len(list(quality_dir.iterdir())) > 0

    def check_script_execution_completion(self, script_path):
        """Проверка выполнения скрипта по косвенным признакам"""
        # Проверяем логи выполнения
        log_dir = self.engine_dir / "logs"
        if log_dir.exists():
            recent_logs = [f for f in log_dir.iterdir()
                          if f.stat().st_mtime > (datetime.now().timestamp() - 3600)]  # За последний час
            if recent_logs:
                return True

        # Проверяем outputs директорию
        outputs_dir = self.engine_dir / "outputs"
        if outputs_dir.exists():
            recent_outputs = [f for f in outputs_dir.iterdir()
                             if f.stat().st_mtime > (datetime.now().timestamp() - 3600)]
            if recent_outputs:
                return True

        return False

    def archive_completed_task(self, task_id):
        """Архивирование завершенной задачи"""
        task_log = self.load_task_log()
        task_info = None

        for task in task_log.get("tasks", []):
            if task["task_id"] == task_id:
                task_info = task
                break

        if not task_info:
            return False

        task_file_path = Path(task_info["task_file"])
        if task_file_path.exists() and task_file_path.parent.name == "ACTIVE":
            try:
                # Перемещаем в COMPLETED
                new_path = self.completed_dir / task_file_path.name
                shutil.move(str(task_file_path), str(new_path))

                # Обновляем запись в логе
                task_info["status"] = "COMPLETED"
                task_info["completed_time"] = datetime.now().isoformat()
                task_info["completed_by"] = "Financial_CTO_Auto_Archive"
                task_info["archived_path"] = str(new_path)

                self.save_task_log(task_log)
                self.logger.info(f"Task {task_id} archived successfully")
                return True

            except Exception as e:
                self.logger.error(f"Failed to archive task {task_id}: {e}")
                return False

        return False

    def get_next_task_counter(self):
        """Получение следующего номера задачи"""
        task_log = self.load_task_log()
        if task_log:
            return task_log.get("task_counter", 0) + 1
        return 1

    def load_task_log(self):
        """Загрузка лога задач"""
        try:
            with open(self.task_log_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return None

    def save_task_log(self, task_log):
        """Сохранение лога задач"""
        with open(self.task_log_file, 'w', encoding='utf-8') as f:
            json.dump(task_log, f, indent=2, ensure_ascii=False)

    def create_initial_task_log(self):
        """Создание начального лога задач"""
        return {
            "project": "CRYPTO INTELLIGENCE SYSTEM V10",
            "task_counter": 0,
            "tasks": [],
            "metadata": {
                "created": datetime.now().isoformat(),
                "managed_by": "Financial_CTO_Auto_System"
            }
        }

    def run_full_lifecycle_check(self):
        """
        Полный цикл управления lifecycle задач
        """
        self.logger.info("Financial CTO - Starting full task lifecycle check")

        try:
            # 1. Обнаруживаем новые задачи
            new_tasks, current_tasks = self.discover_active_tasks()

            # 2. Регистрируем новые задачи
            for task_info in new_tasks:
                task_id = self.register_new_task(task_info)
                if task_id:
                    self.logger.info(f"New task {task_id} registered and being monitored")

            # 3. Обновляем состояние мониторинга
            self.monitoring_state["known_active_tasks"] = current_tasks
            self.monitoring_state["last_check"] = datetime.now().isoformat()

            # 4. Проверяем завершение зарегистрированных задач
            task_log = self.load_task_log()
            if task_log:
                for task in task_log.get("tasks", []):
                    if task.get("status") == "REGISTERED":
                        task_id = task["task_id"]
                        if self.detect_task_completion(task_id):
                            self.logger.info(f"Task {task_id} completion detected")
                            if self.archive_completed_task(task_id):
                                self.logger.info(f"Task {task_id} successfully archived")

            # 5. Сохраняем состояние
            self.save_monitoring_state(self.monitoring_state)

            self.logger.info("Financial CTO lifecycle check completed successfully")

        except Exception as e:
            self.logger.error(f"Financial CTO lifecycle check failed: {e}")
            raise

    def start_continuous_monitoring(self, interval_seconds=None):
        """
        Запуск непрерывного мониторинга
        """
        if interval_seconds is None:
            interval_seconds = self.monitoring_state.get("check_interval_seconds", 60)

        self.logger.info(f"Financial CTO - Starting continuous monitoring (interval: {interval_seconds}s)")

        try:
            while self.monitoring_state.get("monitoring_enabled", True):
                self.run_full_lifecycle_check()
                time.sleep(interval_seconds)

                # Перезагружаем состояние на случай внешних изменений
                self.monitoring_state = self.load_monitoring_state()

        except KeyboardInterrupt:
            self.logger.info("Financial CTO monitoring stopped by user")
        except Exception as e:
            self.logger.error(f"Financial CTO continuous monitoring failed: {e}")

if __name__ == "__main__":
    print("🏦 Financial CTO - Complete Task Lifecycle Manager")
    print("=" * 60)
    print("Capabilities:")
    print("✅ Auto-discover new tasks in ACTIVE/")
    print("✅ Auto-register tasks in tracking system")
    print("✅ Monitor task completion via deliverables")
    print("✅ Auto-archive completed tasks to COMPLETED/")
    print("✅ Maintain full audit trail")
    print("=" * 60)

    manager = TaskLifecycleManager()

    # Запуск разового цикла проверки
    manager.run_full_lifecycle_check()

    print("\n🎯 To start continuous monitoring:")
    print("manager.start_continuous_monitoring(60)  # Check every 60 seconds")