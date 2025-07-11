# run.py
import uvicorn
from app.core.config import settings
from app.core.logger import init_logger


if __name__ == "__main__":
    """
    应用启动入口
    使用uvicorn启动FastAPI应用
    """
    # 初始化日志
    init_logger()

    uvicorn.run(
        "app.main:app",
        host=settings.server_host,
        port=settings.server_port,
        reload=settings.debug,
        log_level="info",
        log_config=None
    )