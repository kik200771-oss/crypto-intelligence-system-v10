#!/usr/bin/env python3
"""
CIS V10.0-r1 Command Line Interface
Alternative to MCP for system interaction
"""

import json
import sys
import argparse
from pathlib import Path
from datetime import datetime

class CISCLI:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.status_file = self.project_root / "MARKET_MIND" / "CONFIG" / "component_status.json"

    def load_status(self):
        """Load component status"""
        try:
            with open(self.status_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading status: {e}")
            return {}

    def cmd_status(self):
        """Show system status"""
        status_data = self.load_status()
        if not status_data:
            return

        ready = [name for name, comp in status_data.items() if comp.get('status') == 'ready']
        total = len(status_data)
        progress = len(ready) / total * 100

        print("=" * 50)
        print("CIS V10.0-r1 System Status")
        print("=" * 50)
        print(f"Ready components: {len(ready)}/{total}")
        print(f"Progress: {progress:.1f}%")
        print()

        print("Ready components:")
        for name in ready:
            comp = status_data[name]
            print(f"  + {name}: {comp.get('notes', 'No notes')}")

        print()
        print("Next 5 pending components:")
        pending = [name for name, comp in status_data.items() if comp.get('status') != 'ready']
        for name in pending[:5]:
            print(f"  - {name}")

    def cmd_tasks(self):
        """Show task status"""
        active_dir = self.project_root / "TASKS" / "ACTIVE"
        completed_dir = self.project_root / "TASKS" / "COMPLETED"

        print("=" * 50)
        print("Task Status")
        print("=" * 50)

        if active_dir.exists():
            active_tasks = list(active_dir.glob("*.md"))
            print(f"Active tasks ({len(active_tasks)}):")
            for task in active_tasks:
                print(f"  > {task.name}")
        else:
            print("Active tasks: None")

        print()

        if completed_dir.exists():
            completed_tasks = list(completed_dir.glob("*.md"))
            print(f"Completed tasks ({len(completed_tasks)}):")
            for task in completed_tasks[-5:]:  # Last 5
                print(f"  + {task.name}")
        else:
            print("Completed tasks: None")

    def cmd_component(self, name):
        """Show specific component status"""
        status_data = self.load_status()
        if name in status_data:
            comp = status_data[name]
            print(f"Component: {name}")
            print(f"Status: {comp.get('status', 'unknown')}")
            print(f"Updated: {comp.get('updated_at', 'never')}")
            print(f"Notes: {comp.get('notes', 'No notes')}")
        else:
            print(f"Component '{name}' not found")

    def cmd_next(self):
        """Show next task to work on"""
        active_dir = self.project_root / "TASKS" / "ACTIVE"
        if active_dir.exists():
            tasks = sorted(active_dir.glob("*.md"))
            if tasks:
                print(f"Next task: {tasks[0].name}")
                print(f"Path: {tasks[0]}")
            else:
                print("No active tasks")
        else:
            print("TASKS/ACTIVE directory not found")

def main():
    parser = argparse.ArgumentParser(description="CIS V10.0-r1 CLI")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Status command
    subparsers.add_parser('status', help='Show system status')

    # Tasks command
    subparsers.add_parser('tasks', help='Show task status')

    # Component command
    component_parser = subparsers.add_parser('component', help='Show component details')
    component_parser.add_argument('name', help='Component name')

    # Next command
    subparsers.add_parser('next', help='Show next task')

    args = parser.parse_args()

    cli = CISCLI()

    if args.command == 'status':
        cli.cmd_status()
    elif args.command == 'tasks':
        cli.cmd_tasks()
    elif args.command == 'component':
        cli.cmd_component(args.name)
    elif args.command == 'next':
        cli.cmd_next()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()