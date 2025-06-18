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
│   ├── models/              # 数据库模型
│   │   ├── __init__.py
│   │   └── vocabulary.py    # 词汇表模型
│   └── service/             # 业务逻辑层
├── scripts/                 # 脚本目录
│   ├── __init__.py
│   └── sync_vocabulary.py   # 词汇数据同步脚本
├── datasets/                # 数据集目录
│   ├── README.md
│   └── cet4_sample.json     # 示例数据文件
├── requirements.txt         # 项目依赖
├── run.py                  # API服务启动入口
├── sync_data.py            # 数据同步脚本启动入口
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

### 4. 准备词汇数据

将词汇JSON数据文件放置在 `datasets/` 目录中：
- `cet4.json` - CET4词汇数据
- `cet6.json` - CET6词汇数据
- `kaoyan.json` - 考研词汇数据
- `level4.json` - 专四词汇数据
- `level8.json` - 专八词汇数据

### 5. 同步词汇数据到数据库

```bash
# 同步所有词汇数据
python sync_data.py

# 或者同步指定文件
python sync_data.py --file cet4.json

# 查看帮助信息
python sync_data.py --help
```

### 6. 启动API服务

```bash
python run.py
```

或者使用uvicorn直接启动：
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 7. 访问API

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

## 数据同步脚本

### 脚本功能

项目提供了独立的数据同步脚本，用于将JSON格式的词汇数据导入到数据库中：

- **脚本入口**: `sync_data.py`
- **支持的数据表**: t_cet4, t_cet6, t_kaoyan, t_level4, t_level8
- **数据来源**: `datasets/` 目录中的JSON文件

### 使用方法

```bash
# 同步所有数据文件
python sync_data.py

# 同步指定文件
python sync_data.py --file cet4.json

# 指定数据集目录
python sync_data.py --datasets-dir ./my_data

# 强制同步（覆盖现有数据）
python sync_data.py --force

# 查看帮助
python sync_data.py --help
```

### JSON数据格式

数据集文件应为 JSON Lines 格式（每行一个JSON对象），包含以下字段：

```json
{"wordRank":1,"headWord":"refuse","content":{"word":{"wordHead":"refuse","wordId":"CET4luan_2_1","content":{"trans":[{"tranCn":"拒绝","pos":"v"}],"usphone":"ri'fjʊz","ukphone":"rɪ'fjuːz"}}},"bookId":"CET4luan_2"}
{"wordRank":2,"headWord":"soluble","content":{"word":{"wordHead":"soluble","wordId":"CET4luan_2_2","content":{"trans":[{"tranCn":"可溶的；可以解决的","pos":"adj"}],"usphone":"'sɑljəbl","ukphone":"'sɒljʊb(ə)l"}}},"bookId":"CET4luan_2"}
```

**注意：**
- 文件格式为 JSON Lines（每行一个独立的JSON对象）
- 不是标准的JSON数组格式
- 每行必须是完整的JSON对象，以花括号包裹

脚本会从JSON数据中提取以下字段：
- `wordRank` → `word_rank` (单词序号)
- `headWord` → `head_word` (单词)
- `content.word.content.trans[].tranCn` → `translation` (中文翻译)
- `bookId` → `book_id` (单词书ID)
- `content.word.wordId` → `word_id` (单词ID)
- `content.word.content.usphone` → `us_phone` (美音音标)
- `content.word.content.ukphone` → `uk_phone` (英音音标)

### 数据表结构

每张词汇表包含以下字段：
- `id` - 主键ID
- `word_rank` - 单词序号
- `head_word` - 单词（建立索引）
- `translation` - 中文翻译
- `book_id` - 单词书ID
- `word_id` - 单词ID
- `us_phone` - 美音音标
- `uk_phone` - 英音音标
- `created_at` - 创建时间
- `updated_at` - 更新时间

## 注意事项

1. 确保PostgreSQL服务正在运行
2. 数据库用户需要有创建表的权限
3. 首次启动时会自动创建数据库表
4. 开发模式下会打印SQL语句到控制台
5. 数据同步脚本与API服务是独立的，可以分别运行
6. 同步数据前请确保JSON文件格式正确

## 技术栈

- **FastAPI** - 现代高性能Web框架
- **SQLAlchemy** - Python SQL工具包和ORM
- **PostgreSQL** - 开源关系型数据库
- **Uvicorn** - ASGI服务器
- **Pydantic** - 数据验证和设置管理