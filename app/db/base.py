from sqlalchemy import Column, Integer, DateTime, func
from sqlalchemy.ext.declarative import declared_attr
from app.db import Base


class TimestampMixin:
    """
    时间戳混入类
    为模型添加创建时间和更新时间字段
    """
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="创建时间"
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="更新时间"
    )


class BaseModel(Base, TimestampMixin):
    """
    基础模型类
    所有数据库模型的基类
    """
    __abstract__ = True
    
    id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
        comment="主键ID"
    )
    
    @declared_attr
    def __tablename__(cls):
        """
        自动生成表名（类名转换为小写下划线格式）
        """
        import re
        # 将驼峰命名转换为下划线命名
        name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', cls.__name__)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()
    
    def to_dict(self):
        """
        将模型实例转换为字典
        """
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }
    
    def __repr__(self):
        """
        模型的字符串表示
        """
        return f"<{self.__class__.__name__}(id={self.id})>"