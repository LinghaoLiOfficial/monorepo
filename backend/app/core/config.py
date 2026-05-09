from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    app_name: str = "myapp"
    app_env: str = "local"
    debug: bool = False

    database_url: str = "postgresql+asyncpg://myapp:changeme@localhost:5432/myapp"
    database_test_url: str = (
        "postgresql+asyncpg://myapp:changeme@localhost:5432/myapp_test"
    )
    cors_origins: list[str] = ["http://localhost:3000"]


settings = Settings()
