from enum import Enum

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel, Field


class RunConfig(BaseModel):
    HOST: str
    PORT: int
    DEBUG: bool
    CORS_ORIGINS: list[str] = Field(default_factory=lambda: ["*"])

class ModeEnum(str, Enum):
    production = "production"
    testing = "testing"


class APIConfig(BaseModel):
    VERSION: str = 'v1'
    SERVICE_NAME: str
    SERVICE_SLUG: str
    MASTER_KEY: str


class SecurityConfig(BaseModel):
    ENCRYPTION_KEY: str


class DataBaseConfig(BaseModel):
    PORT: int
    HOST: str
    NAME: str
    USER: str
    PASSWORD: str

    def as_dns(self) -> str:
        return f"postgresql+asyncpg://{self.USER}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.NAME}"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env",
                                      env_nested_delimiter="__",
                                      case_sensitive=False)
    security: SecurityConfig
    api: APIConfig
    mode: ModeEnum
    run: RunConfig
    db: DataBaseConfig


settings = Settings()