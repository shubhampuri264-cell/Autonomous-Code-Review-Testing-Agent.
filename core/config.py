"""Application configuration via pydantic-settings."""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Central configuration loaded from environment variables."""

    # App
    app_name: str = "Autonomous Code Review & Testing Agent"
    debug: bool = False

    # LLM
    gemini_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    llm_provider: str = "gemini"  # "gemini" | "anthropic" | "bedrock"
    gemini_model: str = "gemini-2.5-flash"
    anthropic_model: str = "claude-sonnet-4-6"
    bedrock_model: str = "anthropic.claude-sonnet-4-20250514-v1:0"
    aws_region: str = "us-east-1"

    # LLM guardrails (rate-limit + per-run token budget kill switch)
    llm_min_request_interval: float = 1.0  # seconds between LLM calls
    llm_max_retries: int = 3
    token_budget_per_run: int = 200_000  # 0 disables the kill switch

    # GitHub
    github_token: Optional[str] = None
    github_app_id: Optional[str] = None
    github_app_private_key: Optional[str] = None
    github_webhook_secret: Optional[str] = None

    # Supabase
    supabase_url: Optional[str] = None
    supabase_key: Optional[str] = None
    supabase_service_role_key: Optional[str] = None

    # Docker
    docker_host: str = "unix:///var/run/docker.sock"
    sandbox_memory_limit: str = "512m"
    sandbox_cpu_limit: float = 1.0
    sandbox_timeout: int = 60

    # Agent
    default_coverage_threshold: int = 80
    max_iterations: int = 3

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


settings = Settings()
