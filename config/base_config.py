from pydantic_settings import BaseSettings

class BaseAppConfig(BaseSettings):
    """
    所有 Config 共用的基底類別。
    在這邊定義好共同的行為，如讀取 .env 檔案與忽略額外變數。
    """
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"
