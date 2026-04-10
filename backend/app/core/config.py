from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "FinHub API"
    environment: str = "development"
    database_url: str = "sqlite:///./finhub.db"
    cors_origins: list[str] = ["http://localhost:3001"]
    gocardless_base_url: str = "https://bankaccountdata.gocardless.com/api/v2"
    gocardless_secret_id: str | None = None
    gocardless_secret_key: str | None = None
    gocardless_redirect_uri: str = "http://localhost:3001/connectors/gocardless/callback"
    auth_session_cookie: str = "finhub_session"
    auth_session_days: int = 30

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
