from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    app_name: str = "my_personal_web"
    app_env: str = "local"
    debug: bool = False

    database_url: str = (
        "postgresql+asyncpg://my_personal_web:changeme@localhost:5432/my_personal_web"
    )
    database_test_url: str = "postgresql+asyncpg://my_personal_web:changeme@localhost:5432/my_personal_web_test"
    cors_origins: list[str] = ["http://localhost:3000"]


settings = Settings()
