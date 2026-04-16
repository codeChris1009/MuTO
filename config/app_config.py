from config.base_config import BaseAppConfig

class AppConfig(BaseAppConfig):
    """
    專案基礎設定，如環境與啟動相關
    """
    environment: str = "dev"
    
app_settings = AppConfig()
