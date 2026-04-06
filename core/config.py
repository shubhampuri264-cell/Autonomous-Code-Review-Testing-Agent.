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
    llm_provider: str = "gemini"  # "gemini" or "anthropic"

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

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
