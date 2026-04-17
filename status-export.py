#!/usr/bin/env python3
"""
Export CIS V10.0-r1 status for external access
Alternative to MCP when having connection issues
"""

import json
import os
from datetime import datetime
from pathlib import Path

def export_system_status():
    """Export current system status to text files"""

    project_root = Path(__file__).parent
    export_dir = project_root / "exports"
    export_dir.mkdir(exist_ok=True)

    # Read component status
    status_file = project_root / "MARKET_MIND" / "CONFIG" / "component_status.json"

    try:
        with open(status_file, 'r', encoding='utf-8') as f:
            status_data = json.load(f)

        ready_components = [name for name, comp in status_data.items()
                          if comp.get('status') == 'ready']
        total_components = len(status_data)

        # Create status report
        report = f"""🏦 CIS V10.0-r1 System Status
Generated: {datetime.now().isoformat()}

📊 Component Summary:
Ready: {len(ready_components)}/{total_components}
Progress: {len(ready_components)/total_components*100:.1f}%

✅ Ready Components:
"""
        for name in ready_components:
            comp = status_data[name]
            report += f"- {name}: {comp.get('notes', 'No notes')}\n"

        report += f"\n⏳ Pending Components:\n"
        pending = [name for name, comp in status_data.items()
                  if comp.get('status') != 'ready']
        for name in pending[:5]:  # Show first 5
            report += f"- {name}\n"

        if len(pending) > 5:
            report += f"... and {len(pending)-5} more\n"

        # Write report
        with open(export_dir / "system_status.txt", 'w', encoding='utf-8') as f:
            f.write(report)

        # Export raw JSON
        with open(export_dir / "component_status.json", 'w', encoding='utf-8') as f:
            json.dump(status_data, f, indent=2, ensure_ascii=False)

        print(f"✅ Status exported to {export_dir}/")
        print(f"Ready components: {len(ready_components)}/{total_components}")

        return report

    except Exception as e:
        error_msg = f"❌ Error exporting status: {str(e)}"
        print(error_msg)
        return error_msg

if __name__ == "__main__":
    export_system_status()