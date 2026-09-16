from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Open Financial Terminal Backend"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"

    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "terminal_user"
    POSTGRES_PASSWORD: str = "terminal_password"
    POSTGRES_DB: str = "terminal_relational"

    TIMESCALE_SERVER: str = "localhost"
    TIMESCALE_PORT: int = 5433
    TIMESCALE_USER: str = "terminal_user"
    TIMESCALE_PASSWORD: str = "terminal_password"
    TIMESCALE_DB: str = "terminal_timeseries"

    REDIS_URL: str = "redis://localhost:6379/0"

    SECRET_KEY: str = "dev_secret_key_change_in_production_32bytes_min"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 11520

    @property
    def postgres_async_url(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @property
    def postgres_sync_url(self) -> str:
        return f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @property
    def timescale_async_url(self) -> str:
        return f"postgresql+asyncpg://{self.TIMESCALE_USER}:{self.TIMESCALE_PASSWORD}@{self.TIMESCALE_SERVER}:{self.TIMESCALE_PORT}/{self.TIMESCALE_DB}"

    @property
    def timescale_sync_url(self) -> str:
        return f"postgresql+psycopg2://{self.TIMESCALE_USER}:{self.TIMESCALE_PASSWORD}@{self.TIMESCALE_SERVER}:{self.TIMESCALE_PORT}/{self.TIMESCALE_DB}"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=True, extra="ignore")


settings = Settings()
