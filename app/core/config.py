from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    应用程序配置类
    管理数据库连接和其他应用设置
    """
    # 数据库配置
    database_host: str = "localhost"
    database_port: int = 5969
    database_user: str = "postgres"
    database_password: str = "xwCoder4Ever!"
    database_name: str = "postgres"
    
    # 数据库URL
    @property
    def database_url(self) -> str:
        """
        构建数据库连接URL
        """
        return f"postgresql://{self.database_user}:{self.database_password}@{self.database_host}:{self.database_port}/{self.database_name}"
    
    # 应用配置
    app_name: str = "VocabTracker API"
    debug: bool = True
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# 全局配置实例
settings = Settings()