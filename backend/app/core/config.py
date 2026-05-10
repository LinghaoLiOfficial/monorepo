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

    # Optional object storage (Aliyun OSS)
    oss_enabled: bool = False
    oss_access_key_id: str = ""
    oss_access_key_secret: str = ""
    oss_bucket: str = ""
    oss_region: str = ""
    oss_endpoint: str = ""
    oss_max_connections: int = 20
    oss_disable_ssl: bool = False
    oss_use_cname: bool = True
    oss_load_max_size: int = 50 * 1024 * 1024


settings = Settings()
