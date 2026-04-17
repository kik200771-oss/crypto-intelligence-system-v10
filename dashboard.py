#!/usr/bin/env python3
"""
CIS V10.0-r1 Status Dashboard
Alternative to MCP - generates HTML reports for web access
"""

import json
import os
from datetime import datetime
from pathlib import Path

def generate_dashboard():
    """Generate HTML dashboard for system status"""

    project_root = Path(__file__).parent
    exports_dir = project_root / "exports"
    exports_dir.mkdir(exist_ok=True)

    # Read component status
    status_file = project_root / "MARKET_MIND" / "CONFIG" / "component_status.json"

    try:
        with open(status_file, 'r', encoding='utf-8') as f:
            status_data = json.load(f)

        # Calculate statistics
        ready_components = [(name, comp) for name, comp in status_data.items()
                          if comp.get('status') == 'ready']
        pending_components = [(name, comp) for name, comp in status_data.items()
                            if comp.get('status') != 'ready']

        total = len(status_data)
        ready_count = len(ready_components)
        progress = ready_count / total * 100

        # Read active tasks
        active_tasks = []
        tasks_dir = project_root / "TASKS" / "ACTIVE"
        if tasks_dir.exists():
            active_tasks = [f.name for f in tasks_dir.glob("*.md")]

        # Generate HTML
        html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>CIS V10.0-r1 Dashboard</title>
    <meta http-equiv="refresh" content="60">
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ background: #2c3e50; color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }}
        .stats {{ display: flex; gap: 20px; margin-bottom: 20px; }}
        .stat-card {{ background: white; padding: 20px; border-radius: 10px; flex: 1; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
        .stat-number {{ font-size: 2em; font-weight: bold; color: #3498db; }}
        .component-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
        .component-section {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
        .component-item {{ padding: 10px; margin: 5px 0; border-left: 4px solid #27ae60; background: #f8f9fa; }}
        .pending-item {{ border-left-color: #e74c3c; }}
        .progress-bar {{ width: 100%; height: 20px; background: #ecf0f1; border-radius: 10px; overflow: hidden; }}
        .progress-fill {{ height: 100%; background: #27ae60; transition: width 0.3s; }}
        .timestamp {{ color: #7f8c8d; font-size: 0.9em; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏦 CIS V10.0-r1 System Dashboard</h1>
            <p>Crypto Intelligence System - Real-time Status</p>
        </div>

        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">{ready_count}/{total}</div>
                <div>Components Ready</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{progress:.1f}%</div>
                <div>Progress</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{len(active_tasks)}</div>
                <div>Active Tasks</div>
            </div>
        </div>

        <div class="progress-bar">
            <div class="progress-fill" style="width: {progress}%"></div>
        </div>

        <div class="component-grid">
            <div class="component-section">
                <h2>✅ Ready Components ({ready_count})</h2>'''

        for name, comp in ready_components:
            notes = comp.get('notes', 'No notes')
            updated = comp.get('updated_at', 'Unknown')
            html += f'''
                <div class="component-item">
                    <strong>{name}</strong><br>
                    <small>{notes}</small><br>
                    <span class="timestamp">Updated: {updated}</span>
                </div>'''

        html += f'''
            </div>

            <div class="component-section">
                <h2>⏳ Pending Components ({len(pending_components)})</h2>'''

        for name, comp in pending_components[:10]:  # Show first 10
            html += f'''
                <div class="component-item pending-item">
                    <strong>{name}</strong><br>
                    <small>Status: {comp.get('status', 'not_started')}</small>
                </div>'''

        if len(pending_components) > 10:
            html += f'<div class="component-item pending-item"><strong>... and {len(pending_components)-10} more</strong></div>'

        html += f'''
            </div>
        </div>

        <div class="component-section" style="margin-top: 20px;">
            <h2>📋 Active Tasks</h2>'''

        if active_tasks:
            for task in active_tasks:
                html += f'<div class="component-item"><strong>{task}</strong></div>'
        else:
            html += '<div class="component-item">No active tasks</div>'

        html += f'''
        </div>

        <div class="timestamp" style="text-align: center; margin-top: 20px;">
            Last updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        </div>
    </div>
</body>
</html>'''

        # Save HTML dashboard
        dashboard_file = exports_dir / "dashboard.html"
        with open(dashboard_file, 'w', encoding='utf-8') as f:
            f.write(html)

        print(f"Dashboard generated: {dashboard_file}")
        print(f"Open in browser: file:///{dashboard_file.absolute()}")
        return str(dashboard_file.absolute())

    except Exception as e:
        print(f"Error generating dashboard: {e}")
        return None

if __name__ == "__main__":
    generate_dashboard()