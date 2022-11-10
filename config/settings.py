from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    host: str = Field("localhost")
    port: int = Field(5000)


settings = Settings
