"""Unit tests for test result parser."""

from sandbox.result_parser import parse_test_output


class TestPytestParser:
    def test_all_passing(self):
        output = "======================== 10 passed in 1.23s ========================"
        result = parse_test_output(output, "python")
        assert result["passed"] == 10
        assert result["failed"] == 0
        assert result["failures"] == []

    def test_mixed_results(self):
        output = "============ 7 passed, 3 failed in 2.01s ============"
        result = parse_test_output(output, "python")
        assert result["passed"] == 7
        assert result["failed"] == 3

    def test_with_coverage(self):
        output = """
Name          Stmts   Miss  Cover
---------------------------------
module.py        50     10    80%
---------------------------------
TOTAL            50     10    80%
3 passed in 0.5s
"""
        result = parse_test_output(output, "python")
        assert result["coverage_pct"] == 80.0
        assert result["passed"] == 3


class TestJestParser:
    def test_jest_json_output(self):
        import json
        data = json.dumps({
            "numPassedTests": 5,
            "numFailedTests": 1,
            "testResults": [{
                "testResults": [{
                    "fullName": "should add numbers",
                    "status": "failed",
                    "failureMessages": ["Expected 3 but got 4"]
                }]
            }]
        })
        result = parse_test_output(data, "javascript")
        assert result["passed"] == 5
        assert result["failed"] == 1
        assert len(result["failures"]) == 1
