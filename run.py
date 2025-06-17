import uvicorn
from app.main import app
from app.core.config import settings

if __name__ == "__main__":
    """
    应用启动入口
    使用uvicorn启动FastAPI应用
    """
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=9163,
        reload=settings.debug,
        log_level="info"
    )