#!/usr/bin/env python3
"""
Task Executor для CRYPTO INTELLIGENCE SYSTEM
Система выполнения задач с логированием и архивацией
"""

import json
import os
import datetime
from pathlib import Path
import subprocess
import logging

class TaskExecutor:
    """Исполнитель задач с полным lifecycle management"""

    def __init__(self, project_root="C:\\КОДИНГ\\MARKET ANALYSIS"):
        self.project_root = Path(project_root)
        self.tasks_dir = self.project_root / "TASKS"
        self.engine_dir = self.project_root / "ENGINE"
        self.history_dir = self.project_root / "HISTORY"
        self.task_log_file = self.history_dir / "task_log.json"

        self.setup_logging()

    def setup_logging(self):
        """Настройка логирования"""
        log_dir = self.engine_dir / "logs"
        log_dir.mkdir(exist_ok=True)

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / f"executor_{datetime.date.today()}.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def load_task_log(self):
        """Загрузка лога задач"""
        try:
            with open(self.task_log_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                "project": "CRYPTO INTELLIGENCE SYSTEM V10",
                "task_counter": 0,
                "tasks": [],
                "statistics": {"total_tasks": 0, "active_tasks": 0, "completed_tasks": 0, "failed_tasks": 0}
            }

    def save_task_log(self, task_log):
        """Сохранение лога задач"""
        with open(self.task_log_file, 'w', encoding='utf-8') as f:
            json.dump(task_log, f, indent=2, ensure_ascii=False)

    def register_task(self, task_file_path, task_script_path):
        """Регистрация новой задачи"""
        task_log = self.load_task_log()
        task_log["task_counter"] += 1

        task_id = f"task_{task_log['task_counter']:03d}"

        task_entry = {
            "task_id": task_id,
            "task_file": str(task_file_path),
            "script_file": str(task_script_path),
            "status": "REGISTERED",
            "created": datetime.datetime.now().isoformat(),
            "execution_log": []
        }

        task_log["tasks"].append(task_entry)
        task_log["statistics"]["total_tasks"] += 1
        task_log["statistics"]["active_tasks"] += 1

        self.save_task_log(task_log)
        self.logger.info(f"Зарегистрирована задача {task_id}")

        return task_id

    def execute_task(self, task_id):
        """Выполнение задачи"""
        task_log = self.load_task_log()
        task_entry = None

        for task in task_log["tasks"]:
            if task["task_id"] == task_id:
                task_entry = task
                break

        if not task_entry:
            self.logger.error(f"Задача {task_id} не найдена")
            return False

        script_path = Path(task_entry["script_file"])
        if not script_path.exists():
            self.logger.error(f"Скрипт {script_path} не найден")
            return False

        # Выполнение скрипта
        self.logger.info(f"Выполнение задачи {task_id}...")
        task_entry["status"] = "RUNNING"
        task_entry["started"] = datetime.datetime.now().isoformat()

        try:
            result = subprocess.run(
                ["python", str(script_path)],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )

            execution_entry = {
                "timestamp": datetime.datetime.now().isoformat(),
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }

            task_entry["execution_log"].append(execution_entry)

            if result.returncode == 0:
                task_entry["status"] = "COMPLETED"
                task_log["statistics"]["active_tasks"] -= 1
                task_log["statistics"]["completed_tasks"] += 1
                self.logger.info(f"Задача {task_id} выполнена успешно")
            else:
                task_entry["status"] = "FAILED"
                task_log["statistics"]["active_tasks"] -= 1
                task_log["statistics"]["failed_tasks"] += 1
                self.logger.error(f"Задача {task_id} завершилась с ошибкой")

        except Exception as e:
            task_entry["status"] = "ERROR"
            task_entry["error"] = str(e)
            self.logger.error(f"Ошибка выполнения задачи {task_id}: {e}")

        task_entry["completed"] = datetime.datetime.now().isoformat()
        self.save_task_log(task_log)

        return task_entry["status"] == "COMPLETED"

    def get_task_status(self, task_id):
        """Получение статуса задачи"""
        task_log = self.load_task_log()
        for task in task_log["tasks"]:
            if task["task_id"] == task_id:
                return task["status"]
        return None

    def list_tasks(self, status=None):
        """Список задач"""
        task_log = self.load_task_log()
        tasks = task_log["tasks"]

        if status:
            tasks = [t for t in tasks if t["status"] == status]

        return tasks

    def archive_completed_task(self, task_id):
        """Архивация завершенной задачи"""
        task_log = self.load_task_log()

        for task in task_log["tasks"]:
            if task["task_id"] == task_id and task["status"] == "COMPLETED":
                # Перемещаем файл задачи в COMPLETED
                task_file = Path(task["task_file"])
                if task_file.exists():
                    completed_dir = self.tasks_dir / "COMPLETED"
                    completed_dir.mkdir(exist_ok=True)
                    task_file.rename(completed_dir / task_file.name)

                # Архивируем результаты
                self.logger.info(f"Задача {task_id} архивирована")
                break

if __name__ == "__main__":
    executor = TaskExecutor()
    print("🔧 Task Executor готов к работе")
    print(f"📊 Статистика: {executor.load_task_log()['statistics']}")