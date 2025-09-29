from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openai_api_key: str | None = None
    langsmith_tracing: bool = False
    langsmith_api_key: str | None = None
    lam_agent_model: str = "gpt-4o-mini"
    lam_browser_headless: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()  # type: ignore[call-arg]

