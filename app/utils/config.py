from pydantic_settings import BaseSettings, SettingsConfigDict

class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    ENVIRONMENT: str = 'development'  # or 'production'
    DATABASE_URL: str = 'postgresql://postgres:postgres@localhost:5432/sprint_sync'
    AUTH_SECRET_KEY: str = 'your_auth_secret_key'

    def get_db_url(self) -> str:
        return self.DATABASE_URL