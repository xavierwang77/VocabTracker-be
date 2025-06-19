import json
import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Dict, Any


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
    
    # 服务器配置
    server_host: str = "localhost"
    server_port: int = 9163
    
    # 应用配置
    app_name: str = "VocabTracker API"
    debug: bool = False
    
    def __init__(self, **kwargs):
        """
        初始化配置，优先从JSON配置文件读取
        """
        super().__init__(**kwargs)
        self._load_from_json()
    
    def _load_from_json(self) -> None:
        """
        从JSON配置文件加载配置
        """
        # 获取项目根目录下的config.json文件路径
        project_root = Path(__file__).parent.parent.parent
        config_file = project_root / "config.json"
        
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                
                # 加载数据库配置
                if "database" in config_data:
                    db_config = config_data["database"]
                    self.database_host = db_config.get("host", self.database_host)
                    self.database_port = db_config.get("port", self.database_port)
                    self.database_user = db_config.get("user", self.database_user)
                    self.database_password = db_config.get("password", self.database_password)
                    self.database_name = db_config.get("name", self.database_name)
                
                # 加载服务器配置
                if "server" in config_data:
                    server_config = config_data["server"]
                    self.server_host = server_config.get("host", self.server_host)
                    self.server_port = server_config.get("port", self.server_port)
                
                # 加载应用配置
                if "app" in config_data:
                    app_config = config_data["app"]
                    self.app_name = app_config.get("name", self.app_name)
                    self.debug = app_config.get("debug", self.debug)
                    
            except (json.JSONDecodeError, FileNotFoundError, KeyError) as e:
                # 如果配置文件读取失败，使用默认值并记录警告
                print(f"警告: 无法读取配置文件 {config_file}: {e}，使用默认配置")
    
    # 数据库URL
    @property
    def database_url(self) -> str:
        """
        构建数据库连接URL
        """
        return f"postgresql://{self.database_user}:{self.database_password}@{self.database_host}:{self.database_port}/{self.database_name}"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# 全局配置实例
settings = Settings()