from pydantic_settings import BaseSettings


class AppConfig(BaseSettings):
    CORS_ORIGIN: str = ""


class DBConfig(BaseSettings):
    MYSQL_HOST: str = ""
    MYSQL_PORT: str = ""
    MYSQL_USER: str = ""
    MYSQL_PASSWORD: str = ""
    MYSQL_DB: str = ""


app_config = AppConfig()
db_config = DBConfig()
