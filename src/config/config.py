from pydantic import Field
from pydantic_settings import BaseSettings


class AppConfig(BaseSettings):
    CORS_ORIGIN: str = Field(...)


class DBConfig(BaseSettings):
    MYSQL_HOST: str = Field(...)
    MYSQL_PORT: str = Field(default="3306")
    MYSQL_USER: str = Field(...)
    MYSQL_PASSWORD: str = Field(...)
    MYSQL_DB: str = Field(...)


class HcxConfig(BaseSettings):
    HCX_KEY: str = Field(...)
    HCX_URL: str = Field(...)


app_config = AppConfig()
db_config = DBConfig()
hcx_config = HcxConfig()
