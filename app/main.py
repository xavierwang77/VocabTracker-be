# app/main.py
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from loguru import logger

from app.db import get_db, init_db, check_db_connection
from app.core.config import settings


# 创建FastAPI应用实例
app = FastAPI(
    title=settings.app_name,
    description="词汇量追踪器后端API",
    version="1.0.0",
    debug=settings.debug
)


@app.on_event("startup")
async def startup_event():
    """
    应用启动事件
    检查数据库连接并初始化数据库
    """
    logger.info("正在启动应用...")
    
    # 检查数据库连接
    if check_db_connection():
        logger.info("数据库连接成功")
        # 初始化数据库（创建表）
        init_db()
    else:
        logger.error("数据库连接失败，请检查数据库配置")
        raise Exception("数据库连接失败")
    
    logger.info("应用启动完成")


@app.on_event("shutdown")
async def shutdown_event():
    """
    应用关闭事件
    """
    logger.info("应用正在关闭...")


@app.get("/")
async def root():
    """
    根路径接口
    返回API基本信息
    """
    return {
        "message": "欢迎使用词汇追踪器API",
        "app_name": settings.app_name,
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """
    健康检查接口
    检查应用和数据库状态
    """
    try:
        # 执行简单的数据库查询来验证连接
        db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected",
            "message": "应用运行正常"
        }
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "message": "数据库连接异常"
        }


@app.get("/hello/{name}")
async def say_hello(name: str):
    """
    问候接口
    """
    return {"message": f"你好 {name}！"}
