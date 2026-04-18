#!/usr/bin/env python3
"""
TASK_00_cleanup.md verification script
Проверяет корректность cleanup операций согласно § 2.13
"""

import json
import os
from pathlib import Path

def verify_cleanup():
    """Выполняет полную проверку cleanup результатов"""

    print("=== TASK_00_cleanup.md Verification ===\n")

    # Step 3.1a: Verify legacy directories removed
    print("Step 3.1a: Legacy directories check")
    legacy_dirs = ['src', 'data', 'logs', 'exports', 'config', 'ENGINE', 'HISTORY']
    legacy_found = []

    for dirname in legacy_dirs:
        if Path(dirname).exists():
            legacy_found.append(dirname)

    if legacy_found:
        print(f"FAIL: Legacy directories still exist: {legacy_found}")
        return False
    else:
        print("PASS: All legacy directories removed")

    # Step 3.1b: Verify MARKET_MIND canonical structure
    print("\nStep 3.1b: MARKET_MIND structure check")
    required_dirs = [
        'MARKET_MIND/ENGINE',
        'MARKET_MIND/SCHEMAS',
        'MARKET_MIND/CONFIG',
        'MARKET_MIND/LAYER_A_RESEARCH',
        'MARKET_MIND/LAYER_B_DATA',
        'MARKET_MIND/LAYER_C_KNOWLEDGE',
        'MARKET_MIND/LAYER_D_MODEL',
        'MARKET_MIND/LAYER_E_VALIDATION',
        'MARKET_MIND/LAYER_F_FEEDBACK',
        'MARKET_MIND/LAYER_G_NEWS',
        'MARKET_MIND/LAYER_H_INFRA'
    ]

    missing_dirs = []
    for dirname in required_dirs:
        if not Path(dirname).exists():
            missing_dirs.append(dirname)

    if missing_dirs:
        print(f"[FAIL] FAIL: Missing MARKET_MIND directories: {missing_dirs}")
        return False
    else:
        print("[PASS] PASS: All MARKET_MIND directories present")

    # Step 3.1c: Verify component status honesty
    print("\nStep 3.1c: Component status verification")
    try:
        with open('MARKET_MIND/CONFIG/component_status.json', 'r', encoding='utf-8') as f:
            status = json.load(f)

        # Check critical components have honest status
        critical_checks = {
            'initialize_system': ['needs_rebuild'],
            'schema_layer': ['needs_rewrite'],
            'data_quality_gates': ['needs_rewrite'],
            'context_orchestrator': ['not_started']
        }

        status_issues = []
        for component, allowed_status in critical_checks.items():
            if component not in status:
                status_issues.append(f"{component}: missing")
            elif status[component]['status'] not in allowed_status:
                status_issues.append(f"{component}: status={status[component]['status']} (expected one of {allowed_status})")

        if status_issues:
            print(f"[FAIL] FAIL: Component status issues: {status_issues}")
            return False
        else:
            print("[PASS] PASS: Component status reflects honest assessment")

    except Exception as e:
        print(f"[FAIL] FAIL: Cannot read component_status.json: {e}")
        return False

    # Step 3.1d: Verify CLAUDE.md contract
    print("\nStep 3.1d: CLAUDE.md contract verification")
    try:
        with open('CLAUDE.md', 'r', encoding='utf-8') as f:
            claude_content = f.read()

        # Check for key contract elements
        required_elements = [
            'Crypto Intelligence System V10.0-r1',
            'MARKET_MIND/',
            'ENGINE/',
            'SCHEMAS/',
            'CONFIG/',
            'LAYER_A_RESEARCH/',
            'LAYER_B_DATA/',
            'LAYER_C_KNOWLEDGE/',
            'LAYER_D_MODEL/',
            'LAYER_E_VALIDATION/',
            'LAYER_F_FEEDBACK/',
            'LAYER_G_NEWS/',
            'LAYER_H_INFRA/'
        ]

        missing_elements = []
        for element in required_elements:
            if element not in claude_content:
                missing_elements.append(element)

        if missing_elements:
            print(f"[FAIL] FAIL: CLAUDE.md missing elements: {missing_elements}")
            return False
        else:
            print("[PASS] PASS: CLAUDE.md contract properly installed")

    except Exception as e:
        print(f"[FAIL] FAIL: Cannot read CLAUDE.md: {e}")
        return False

    # Step 3.1e: Verify requirements.txt cleanup
    print("\nStep 3.1e: Requirements cleanup verification")
    try:
        with open('requirements.txt', 'r', encoding='utf-8') as f:
            reqs = f.read().strip()

        expected_deps = ['jsonschema>=4.0.0', 'python-dotenv>=1.0.0']
        lines = [line.strip() for line in reqs.split('\n') if line.strip() and not line.strip().startswith('#')]

        if set(lines) != set(expected_deps):
            print(f"[FAIL] FAIL: requirements.txt incorrect. Expected: {expected_deps}, Got: {lines}")
            return False
        else:
            print("[PASS] PASS: requirements.txt properly cleaned")

    except Exception as e:
        print(f"[FAIL] FAIL: Cannot read requirements.txt: {e}")
        return False

    print("\n=== VERIFICATION COMPLETE ===")
    print("[PASS] ALL CHECKS PASSED: Repository successfully cleaned according to TASK_00_cleanup.md")
    return True

if __name__ == '__main__':
    os.chdir(Path(__file__).parent.parent)
    success = verify_cleanup()
    exit(0 if success else 1)