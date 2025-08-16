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

class StorageConfig(BaseSettings):
    NCP_ACCESS_KEY: str = Field(...)
    NCP_SECRET_KEY: str = Field(...)
    NCP_OS_BUCKET: str = Field(...)
    NCP_OS_REGION: str = Field(default="kr-standard")
    NCP_OS_ENDPOINT: str = Field(default="https://kr.object.ncloudstorage.com")
    # NCP_OS_PUBLIC_READ: bool = Field(default=True)

app_config = AppConfig()
db_config = DBConfig()
hcx_config = HcxConfig()
storage_config = StorageConfig()