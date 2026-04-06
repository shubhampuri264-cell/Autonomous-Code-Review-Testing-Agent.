"""Custom exception classes."""


class AgentError(Exception):
    """Base exception for agent errors."""


class CloneError(AgentError):
    """Failed to clone repository."""


class ParseError(AgentError):
    """Failed to parse source code."""


class TestGenerationError(AgentError):
    """Failed to generate tests via LLM."""


class SandboxError(AgentError):
    """Docker sandbox execution error."""


class SandboxTimeoutError(SandboxError):
    """Container exceeded timeout."""


class CoverageThresholdError(AgentError):
    """Coverage threshold not met after max iterations."""


class GitHubAPIError(AgentError):
    """GitHub API call failed."""


class PRCreationError(GitHubAPIError):
    """Failed to create pull request."""


class LLMError(AgentError):
    """LLM API call failed."""


class DatabaseError(AgentError):
    """Database operation failed."""
