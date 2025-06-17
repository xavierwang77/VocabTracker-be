# VocabTracker Backend

词汇追踪器后端API，基于FastAPI和SQLAlchemy构建。

## 功能特性

- 🚀 基于FastAPI的高性能异步API
- 🗄️ SQLAlchemy ORM数据库操作
- 🐘 PostgreSQL数据库支持
- 📝 完整的中文注释
- 🔧 灵活的配置管理
- 📊 健康检查接口

## 项目结构

```
VocabTracker-be/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI应用主文件
│   ├── api/                 # API路由
│   ├── core/
│   │   └── config.py        # 配置管理
│   ├── db/
│   │   ├── __init__.py      # 数据库初始化
│   │   └── base.py          # 基础模型类
│   └── service/             # 业务逻辑层
├── requirements.txt         # 项目依赖
├── run.py                  # 应用启动入口
├── .env.example            # 环境变量模板
└── README.md
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置数据库

确保PostgreSQL服务正在运行，并创建数据库：

```sql
CREATE DATABASE vocabtracker;
```

### 3. 配置环境变量（可选）

复制环境变量模板：
```bash
cp .env.example .env
```

编辑 `.env` 文件，修改数据库配置（如果需要）：
```
DATABASE_HOST=localhost
DATABASE_PORT=5969
DATABASE_USER=postgres
DATABASE_PASSWORD=xwCoder4Ever!
DATABASE_NAME=vocabtracker
```

### 4. 启动应用

```bash
python run.py
```

或者使用uvicorn直接启动：
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 5. 访问API

- API文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/health
- 根路径: http://localhost:8000/

## 数据库配置

项目默认连接到以下数据库：
- 主机: localhost
- 端口: 5969
- 用户: postgres
- 密码: xwCoder4Ever!
- 数据库: vocabtracker

## API接口

### 基础接口

- `GET /` - 根路径，返回API基本信息
- `GET /health` - 健康检查，验证应用和数据库状态
- `GET /hello/{name}` - 问候接口

### 响应示例

**健康检查成功响应：**
```json
{
  "status": "healthy",
  "database": "connected",
  "message": "应用运行正常"
}
```

## 开发说明

### 数据库模型

所有数据库模型应继承 `BaseModel` 类，该类提供：
- 自动生成的主键ID
- 创建时间和更新时间字段
- 自动生成表名
- 通用的 `to_dict()` 方法

### 添加新模型示例

```python
from app.db.base import BaseModel
from sqlalchemy import Column, String, Text

class Vocabulary(BaseModel):
    """词汇模型"""
    word = Column(String(100), nullable=False, comment="单词")
    definition = Column(Text, comment="定义")
    example = Column(Text, comment="例句")
```

### 数据库会话

使用 `get_db()` 函数获取数据库会话，支持FastAPI依赖注入：

```python
from fastapi import Depends
from sqlalchemy.orm import Session
from app.db import get_db

@app.get("/example")
def example_endpoint(db: Session = Depends(get_db)):
    # 使用数据库会话
    pass
```

## 注意事项

1. 确保PostgreSQL服务正在运行
2. 数据库用户需要有创建表的权限
3. 首次启动时会自动创建数据库表
4. 开发模式下会打印SQL语句到控制台

## 技术栈

- **FastAPI** - 现代高性能Web框架
- **SQLAlchemy** - Python SQL工具包和ORM
- **PostgreSQL** - 开源关系型数据库
- **Uvicorn** - ASGI服务器
- **Pydantic** - 数据验证和设置管理