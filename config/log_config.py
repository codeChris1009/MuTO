from config.base_config import BaseAppConfig


class LogConfig(BaseAppConfig):
    """
    日誌設定專用
    """

    log_level: str = "INFO"


log_settings = LogConfig()
