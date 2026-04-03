#!/usr/bin/env python3
"""
Run all automated test suites and produce a summary report.

Usage:
    python tests/run_all_tests.py

Runs each test suite as a subprocess, captures pass/fail counts,
and prints a summary table. Exit code 0 if all pass, 1 if any fail.
"""

import subprocess
import sys
import os
import re
import time

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Test suites to run: (display_name, script_path)
TEST_SUITES = [
    ("test_vision",        os.path.join("tests", "automated", "test_vision.py")),
    ("test_planning",      os.path.join("tests", "automated", "test_planning.py")),
    ("test_utils",         os.path.join("tests", "automated", "test_utils.py")),
    ("geofence_unit_test", os.path.join("tests", "automated", "geofence_unit_test.py")),
    ("test_imports",       os.path.join("tests", "integration", "test_imports.py")),
    ("0d_planning_test",   os.path.join("tests", "flight", "0d_planning_test.py")),
    ("0e_geofence_test",   os.path.join("tests", "flight", "0e_geofence_test.py")),
]


def parse_results(name, output, returncode):
    """Parse test output to extract passed/failed counts.

    Returns (passed, failed) or (None, None) if unparseable.
    """
    # Pattern 1: "RESULTS: X/Y tests passed" (test_vision, test_planning, geofence_unit_test)
    m = re.search(r"RESULTS:\s*(\d+)/(\d+)\s*tests?\s*passed", output)
    if m:
        passed = int(m.group(1))
        total = int(m.group(2))
        return passed, total - passed

    # Pattern 2: "Results: X passed, Y failed, Z total" (test_utils)
    m = re.search(r"Results:\s*(\d+)\s*passed,\s*(\d+)\s*failed", output)
    if m:
        return int(m.group(1)), int(m.group(2))

    # Pattern 3: pytest short summary "X passed" / "X failed" (test_imports)
    passed = 0
    failed = 0
    m_pass = re.search(r"(\d+)\s+passed", output)
    m_fail = re.search(r"(\d+)\s+failed", output)
    if m_pass:
        passed = int(m_pass.group(1))
    if m_fail:
        failed = int(m_fail.group(1))
    if m_pass or m_fail:
        return passed, failed

    # Pattern 4: count [+]/[X] markers (0d_planning_test, 0e_geofence_test)
    plus_count = len(re.findall(r"\[\+\]", output))
    x_count = len(re.findall(r"\[X\]", output))
    if plus_count + x_count > 0:
        return plus_count, x_count

    # Pattern 5: count [PASS]/[FAIL] markers
    pass_count = len(re.findall(r"\[PASS\]", output))
    fail_count = len(re.findall(r"\[FAIL\]", output))
    if pass_count + fail_count > 0:
        return pass_count, fail_count

    # Fallback: use return code
    if returncode == 0:
        return 1, 0  # assume 1 test passed
    else:
        return 0, 1


def run_suite(name, script_path):
    """Run a single test suite and return (name, passed, failed, duration, error)."""
    full_path = os.path.join(PROJECT_ROOT, script_path)
    if not os.path.exists(full_path):
        return name, 0, 0, 0.0, f"File not found: {script_path}"

    # Use pytest for test_imports (it uses pytest fixtures/classes)
    if "test_imports" in script_path:
        cmd = [sys.executable, "-m", "pytest", full_path, "-v", "--tb=short"]
    else:
        cmd = [sys.executable, full_path]

    start = time.time()
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
            cwd=PROJECT_ROOT,
        )
        duration = time.time() - start
        output = result.stdout + "\n" + result.stderr
        passed, failed = parse_results(name, output, result.returncode)
        error = None

        # If returncode != 0 and we parsed 0 failures, something crashed
        if result.returncode != 0 and (failed is None or failed == 0):
            # Check for unhandled exceptions
            if "Traceback" in output or "Error" in result.stderr:
                error = "Crashed (see output above)"
                failed = max(failed or 0, 1)

        return name, passed or 0, failed or 0, duration, error

    except subprocess.TimeoutExpired:
        duration = time.time() - start
        return name, 0, 1, duration, "TIMEOUT (120s)"
    except Exception as e:
        duration = time.time() - start
        return name, 0, 1, duration, str(e)


def main():
    print("=" * 65)
    print("  SAR DRONE -- ALL TESTS RUNNER")
    print("=" * 65)
    print()

    results = []
    total_passed = 0
    total_failed = 0
    any_error = False

    for name, script_path in TEST_SUITES:
        print(f"--- Running: {name} ---")
        name, passed, failed, duration, error = run_suite(name, script_path)
        results.append((name, passed, failed, duration, error))
        total_passed += passed
        total_failed += failed

        status = "PASS" if failed == 0 and error is None else "FAIL"
        detail = f"{passed} passed, {failed} failed, {duration:.1f}s"
        if error:
            detail += f" ({error})"
            any_error = True
        print(f"  [{status}] {detail}")
        print()

    # Summary table
    print()
    print("=" * 65)
    print("  SUMMARY")
    print("=" * 65)
    print()
    print(f"  {'Suite':<25} {'Passed':>7} {'Failed':>7} {'Time':>8}  Status")
    print(f"  {'-'*25} {'-'*7} {'-'*7} {'-'*8}  {'-'*6}")

    for name, passed, failed, duration, error in results:
        status = "PASS" if failed == 0 and error is None else "FAIL"
        err_note = f" ({error})" if error else ""
        print(f"  {name:<25} {passed:>7} {failed:>7} {duration:>7.1f}s  {status}{err_note}")

    print(f"  {'-'*25} {'-'*7} {'-'*7} {'-'*8}  {'-'*6}")
    print(f"  {'TOTAL':<25} {total_passed:>7} {total_failed:>7}")
    print()

    if total_failed == 0 and not any_error:
        print("  ALL SUITES PASSED")
        print("=" * 65)
        return 0
    else:
        failed_suites = [n for n, p, f, d, e in results if f > 0 or e]
        print(f"  {len(failed_suites)} SUITE(S) FAILED: {', '.join(failed_suites)}")
        print("=" * 65)
        return 1


if __name__ == "__main__":
    sys.exit(main())
