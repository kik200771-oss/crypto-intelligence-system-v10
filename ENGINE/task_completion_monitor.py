#!/usr/bin/env python3
"""
Financial CTO Task Completion Monitor
Автоматический мониторинг и архивирование выполненных задач
"""

import json
import os
import shutil
from pathlib import Path
from datetime import datetime
import logging

class TaskCompletionMonitor:
    """
    Financial CTO система автоматического управления lifecycle задач
    """

    def __init__(self, project_root="C:\\КОДИНГ\\MARKET ANALYSIS"):
        self.project_root = Path(project_root)
        self.tasks_dir = self.project_root / "TASKS"
        self.history_dir = self.project_root / "HISTORY"
        self.market_mind_dir = self.project_root / "MARKET_MIND"
        self.engine_dir = self.project_root / "ENGINE"

        self.task_log_file = self.history_dir / "task_log.json"

        # Логирование в стиле Financial CTO
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - FINANCIAL_CTO - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger("FinancialCTO.TaskMonitor")

    def load_task_log(self):
        """Загрузка текущего лога задач"""
        try:
            with open(self.task_log_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            self.logger.error("task_log.json not found - system not initialized")
            return None

    def save_task_log(self, task_log):
        """Сохранение обновленного лога"""
        with open(self.task_log_file, 'w', encoding='utf-8') as f:
            json.dump(task_log, f, indent=2, ensure_ascii=False)

    def detect_completed_tasks(self):
        """
        Определение завершенных задач на основе deliverables
        Financial CTO анализирует структурные изменения в системе
        """
        completed_tasks = []

        # Проверка MARKET_MIND структуры (Task 01 indicator)
        if self.market_mind_dir.exists():
            config_files_count = len(list((self.market_mind_dir / "CONFIG").glob("*.json")))
            if config_files_count >= 7:  # system_manifest + 6 других конфигов
                completed_tasks.append({
                    "task_id": "task_001",
                    "task_name": "initialize_system",
                    "evidence": f"MARKET_MIND structure created with {config_files_count} config files",
                    "deliverables_found": [
                        str(self.market_mind_dir / "CONFIG" / "system_manifest.json"),
                        str(self.market_mind_dir / "CONFIG" / "component_status.json"),
                        "8-layer directory structure"
                    ]
                })

        # TODO: Добавить детекторы для других задач (Task 02-30)
        # Например:
        # - Task 02 (Schema Layer): проверка SCHEMAS/ директории
        # - Task 03 (Data Quality Gates): проверка quality_logs/
        # - Task 04 (Context Orchestrator): проверка LAYER_C_KNOWLEDGE/

        return completed_tasks

    def verify_task_deliverables(self, task_info):
        """
        Верификация deliverables согласно Financial CTO стандартам
        """
        task_id = task_info["task_id"]

        if task_id == "task_001":
            # Task 01: Initialize System - проверка критериев готовности
            required_deliverables = {
                "system_manifest": self.market_mind_dir / "CONFIG" / "system_manifest.json",
                "component_status": self.market_mind_dir / "CONFIG" / "component_status.json",
                "layer_a": self.market_mind_dir / "LAYER_A_RESEARCH",
                "layer_b": self.market_mind_dir / "LAYER_B_DATA",
                "layer_c": self.market_mind_dir / "LAYER_C_KNOWLEDGE",
                "layer_d": self.market_mind_dir / "LAYER_D_MODEL",
                "layer_e": self.market_mind_dir / "LAYER_E_VALIDATION",
                "layer_f": self.market_mind_dir / "LAYER_F_FEEDBACK",
                "layer_g": self.market_mind_dir / "LAYER_G_NEWS",
                "layer_h": self.market_mind_dir / "LAYER_H_INTERFACE"
            }

            missing_deliverables = []
            for name, path in required_deliverables.items():
                if not path.exists():
                    missing_deliverables.append(f"{name}: {path}")

            if missing_deliverables:
                self.logger.error(f"Task {task_id} deliverables missing: {missing_deliverables}")
                return False

            # Проверка качества deliverables
            try:
                with open(required_deliverables["system_manifest"], 'r') as f:
                    manifest = json.load(f)
                    if manifest.get("version") != "10.0":
                        self.logger.error(f"Task {task_id} - invalid system version in manifest")
                        return False

                with open(required_deliverables["component_status"], 'r') as f:
                    components = json.load(f)
                    if len(components) != 30:
                        self.logger.error(f"Task {task_id} - expected 30 components, got {len(components)}")
                        return False

            except Exception as e:
                self.logger.error(f"Task {task_id} deliverable validation failed: {e}")
                return False

            self.logger.info(f"Task {task_id} deliverables verified successfully")
            return True

        # TODO: Добавить верификацию для других задач
        return False

    def archive_completed_task(self, task_info):
        """
        Архивирование завершенной задачи с полным audit trail
        """
        task_id = task_info["task_id"]
        task_name = task_info["task_name"]

        # Поиск файла задачи в ACTIVE
        active_dir = self.tasks_dir / "ACTIVE"
        completed_dir = self.tasks_dir / "COMPLETED"

        task_files = list(active_dir.glob(f"*{task_name}*"))
        if not task_files:
            task_files = list(active_dir.glob(f"TASK_01*"))  # Fallback для task_001

        if task_files:
            task_file = task_files[0]
            new_path = completed_dir / task_file.name

            try:
                shutil.move(str(task_file), str(new_path))
                self.logger.info(f"Task file moved: {task_file} -> {new_path}")
                task_info["archived_file"] = str(new_path)
                return True
            except Exception as e:
                self.logger.error(f"Failed to archive task file: {e}")
                return False
        else:
            self.logger.warning(f"No task file found for {task_id} in ACTIVE directory")
            return False

    def update_task_tracking(self, task_info):
        """
        Обновление системы tracking с Financial CTO audit trail
        """
        task_log = self.load_task_log()
        if not task_log:
            return False

        task_id = task_info["task_id"]

        # Проверяем, не обновлена ли уже эта задача
        existing_task = None
        for task in task_log.get("tasks", []):
            if task["task_id"] == task_id:
                existing_task = task
                break

        if existing_task and existing_task.get("status") == "COMPLETED":
            self.logger.info(f"Task {task_id} already marked as COMPLETED")
            return True

        # Создаем или обновляем запись задачи
        task_entry = {
            "task_id": task_id,
            "task_name": task_info["task_name"],
            "status": "COMPLETED",
            "completed_by": "Financial_CTO_Auto_Detection",
            "completion_time": datetime.now().isoformat(),
            "evidence": task_info["evidence"],
            "deliverables": task_info["deliverables_found"],
            "verification_status": "PASSED",
            "archived_file": task_info.get("archived_file", "")
        }

        if existing_task:
            # Обновляем существующую запись
            existing_task.update(task_entry)
        else:
            # Добавляем новую запись
            if "tasks" not in task_log:
                task_log["tasks"] = []
            task_log["tasks"].append(task_entry)
            task_log["task_counter"] = max(task_log.get("task_counter", 0), 1)

        # Обновляем статистику
        total_tasks = len(task_log["tasks"])
        completed_tasks = len([t for t in task_log["tasks"] if t["status"] == "COMPLETED"])
        active_tasks = len(list((self.tasks_dir / "ACTIVE").glob("*.md")))

        task_log["statistics"] = {
            "total_tasks": total_tasks,
            "active_tasks": active_tasks,
            "completed_tasks": completed_tasks,
            "failed_tasks": total_tasks - completed_tasks - active_tasks
        }

        # Сохраняем обновленный лог
        self.save_task_log(task_log)
        self.logger.info(f"Task tracking updated for {task_id}")
        return True

    def check_and_prepare_dependencies(self, completed_task_id):
        """
        Проверка зависимостей и подготовка следующих задач
        """
        # Карта зависимостей задач CIS V10
        dependencies = {
            "task_001": ["task_002", "task_005"],  # initialize_system -> schema_layer, streamlit_ui_basic
            "task_002": ["task_003"],              # schema_layer -> data_quality_gates
            "task_003": ["task_014"],              # data_quality_gates -> feature_store
            # TODO: Расширить карту зависимостей для всех 30 задач
        }

        dependent_tasks = dependencies.get(completed_task_id, [])
        if dependent_tasks:
            self.logger.info(f"Task {completed_task_id} enables: {dependent_tasks}")
            # TODO: Автоматически создать файлы следующих задач в ACTIVE

    def run_monitoring_cycle(self):
        """
        Полный цикл мониторинга Financial CTO
        """
        self.logger.info("Financial CTO - Starting task completion monitoring cycle")

        try:
            # 1. Детекция завершенных задач
            completed_tasks = self.detect_completed_tasks()

            if not completed_tasks:
                self.logger.info("No new completed tasks detected")
                return

            # 2. Обработка каждой завершенной задачи
            for task_info in completed_tasks:
                task_id = task_info["task_id"]
                self.logger.info(f"Processing completed task: {task_id}")

                # 3. Верификация deliverables
                if not self.verify_task_deliverables(task_info):
                    self.logger.error(f"Task {task_id} failed deliverable verification")
                    continue

                # 4. Архивирование задачи
                if not self.archive_completed_task(task_info):
                    self.logger.warning(f"Task {task_id} archival had issues")

                # 5. Обновление tracking системы
                if not self.update_task_tracking(task_info):
                    self.logger.error(f"Task {task_id} tracking update failed")
                    continue

                # 6. Проверка зависимостей
                self.check_and_prepare_dependencies(task_id)

                self.logger.info(f"Task {task_id} successfully processed and archived")

        except Exception as e:
            self.logger.error(f"Financial CTO monitoring cycle failed: {e}")
            raise

if __name__ == "__main__":
    print("🏦 Financial CTO - Task Completion Monitor")
    print("=" * 50)

    monitor = TaskCompletionMonitor()
    monitor.run_monitoring_cycle()

    print("✅ Financial CTO monitoring complete")