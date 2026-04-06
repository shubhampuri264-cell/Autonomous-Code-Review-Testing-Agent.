"""Application-wide constants."""

# Agent workflow
MAX_ITERATIONS = 3
DEFAULT_COVERAGE_THRESHOLD = 80
SANDBOX_TIMEOUT_SECONDS = 60
SANDBOX_MEMORY_LIMIT = "512m"
SANDBOX_CPU_LIMIT = 1.0

# Supported languages
SUPPORTED_LANGUAGES = ["python", "javascript", "typescript"]

# Test frameworks per language
TEST_FRAMEWORKS = {
    "python": "pytest",
    "javascript": "jest",
    "typescript": "jest",
}

# File extensions per language
LANGUAGE_EXTENSIONS = {
    "python": [".py"],
    "javascript": [".js", ".jsx"],
    "typescript": [".ts", ".tsx"],
}

# Run statuses
class RunStatus:
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"

# Trigger types
class TriggerType:
    MANUAL = "manual"
    WEBHOOK = "webhook"
    SCHEDULED = "scheduled"

# Correction results
class CorrectionResult:
    RESOLVED = "resolved"
    UNRESOLVED = "unresolved"
    PARTIAL = "partial"
