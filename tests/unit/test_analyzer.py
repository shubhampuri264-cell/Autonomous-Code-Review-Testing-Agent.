"""Unit tests for AST analyzer."""



class TestDetectLanguage:
    def test_python_file(self):
        from parsing.languages import detect_language
        assert detect_language("src/main.py") == "python"

    def test_javascript_file(self):
        from parsing.languages import detect_language
        assert detect_language("src/index.js") == "javascript"

    def test_typescript_file(self):
        from parsing.languages import detect_language
        assert detect_language("src/app.ts") == "typescript"

    def test_unknown_file(self):
        from parsing.languages import detect_language
        assert detect_language("README.md") == "unknown"


class TestResultParser:
    def test_parse_pytest_passing(self):
        from sandbox.result_parser import parse_test_output
        output = "5 passed in 0.12s"
        result = parse_test_output(output, "python")
        assert result["passed"] == 5
        assert result["failed"] == 0

    def test_parse_pytest_with_failures(self):
        from sandbox.result_parser import parse_test_output
        output = "3 passed, 2 failed in 0.45s"
        result = parse_test_output(output, "python")
        assert result["passed"] == 3
        assert result["failed"] == 2
