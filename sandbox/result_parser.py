"""Parse test runner output into structured results."""

import json
import re


def parse_test_output(raw_output: str, language: str) -> dict:
    """Parse pytest/jest output into structured result dict."""
    if language == "python":
        return _parse_pytest_output(raw_output)
    else:
        return _parse_jest_output(raw_output)


def _parse_pytest_output(output: str) -> dict:
    """Parse pytest verbose output."""
    result = {
        "passed": 0,
        "failed": 0,
        "errors": 0,
        "coverage_pct": 0.0,
        "failures": [],
    }

    # Match summary line: "X passed, Y failed"
    summary = re.search(r"(\d+) passed", output)
    if summary:
        result["passed"] = int(summary.group(1))

    failed = re.search(r"(\d+) failed", output)
    if failed:
        result["failed"] = int(failed.group(1))

    errors = re.search(r"(\d+) error", output)
    if errors:
        result["errors"] = int(errors.group(1))

    # Extract individual failure details
    failure_blocks = re.findall(
        r"FAILED (.*?) - (.*?)(?:\n|$)", output
    )
    for test_name, error_msg in failure_blocks:
        result["failures"].append({
            "test_name": test_name,
            "error_message": error_msg,
        })

    # Extract coverage if present
    cov = re.search(r"TOTAL\s+\d+\s+\d+\s+(\d+)%", output)
    if cov:
        result["coverage_pct"] = float(cov.group(1))

    return result


def _parse_jest_output(output: str) -> dict:
    """Parse jest JSON output."""
    result = {
        "passed": 0,
        "failed": 0,
        "errors": 0,
        "coverage_pct": 0.0,
        "failures": [],
    }

    try:
        data = json.loads(output)
        result["passed"] = data.get("numPassedTests", 0)
        result["failed"] = data.get("numFailedTests", 0)

        for suite in data.get("testResults", []):
            for test in suite.get("testResults", []):
                if test["status"] == "failed":
                    result["failures"].append({
                        "test_name": test["fullName"],
                        "error_message": "\n".join(test.get("failureMessages", [])),
                    })
    except json.JSONDecodeError:
        # Fall back to regex parsing
        pass

    return result
