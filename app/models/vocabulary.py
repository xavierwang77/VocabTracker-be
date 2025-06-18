from sqlalchemy import Column, String, Text, Integer
from app.db.base import BaseModel


class CET4Vocabulary(BaseModel):
    """
    CET4词汇表模型
    """
    __tablename__ = "t_cet4"
    
    word_rank = Column(Integer, nullable=False, comment="单词序号")
    head_word = Column(String(100), nullable=False, index=True, comment="单词")
    translation = Column(Text, comment="中文翻译")
    book_id = Column(String(50), comment="单词书ID")
    word_id = Column(String(50), comment="单词ID")
    us_phone = Column(String(100), comment="美音音标")
    uk_phone = Column(String(100), comment="英音音标")
    
    def __repr__(self):
        return f"<CET4Vocabulary(head_word='{self.head_word}')>"


class CET6Vocabulary(BaseModel):
    """
    CET6词汇表模型
    """
    __tablename__ = "t_cet6"
    
    word_rank = Column(Integer, nullable=False, comment="单词序号")
    head_word = Column(String(100), nullable=False, index=True, comment="单词")
    translation = Column(Text, comment="中文翻译")
    book_id = Column(String(50), comment="单词书ID")
    word_id = Column(String(50), comment="单词ID")
    us_phone = Column(String(100), comment="美音音标")
    uk_phone = Column(String(100), comment="英音音标")
    
    def __repr__(self):
        return f"<CET6Vocabulary(head_word='{self.head_word}')>"


class KaoyanVocabulary(BaseModel):
    """
    考研词汇表模型
    """
    __tablename__ = "t_kaoyan"
    
    word_rank = Column(Integer, nullable=False, comment="单词序号")
    head_word = Column(String(100), nullable=False, index=True, comment="单词")
    translation = Column(Text, comment="中文翻译")
    book_id = Column(String(50), comment="单词书ID")
    word_id = Column(String(50), comment="单词ID")
    us_phone = Column(String(100), comment="美音音标")
    uk_phone = Column(String(100), comment="英音音标")
    
    def __repr__(self):
        return f"<KaoyanVocabulary(head_word='{self.head_word}')>"


class Level4Vocabulary(BaseModel):
    """
    专四词汇表模型
    """
    __tablename__ = "t_level4"
    
    word_rank = Column(Integer, nullable=False, comment="单词序号")
    head_word = Column(String(100), nullable=False, index=True, comment="单词")
    translation = Column(Text, comment="中文翻译")
    book_id = Column(String(50), comment="单词书ID")
    word_id = Column(String(50), comment="单词ID")
    us_phone = Column(String(100), comment="美音音标")
    uk_phone = Column(String(100), comment="英音音标")
    
    def __repr__(self):
        return f"<Level4Vocabulary(head_word='{self.head_word}')>"


class Level8Vocabulary(BaseModel):
    """
    专八词汇表模型
    """
    __tablename__ = "t_level8"
    
    word_rank = Column(Integer, nullable=False, comment="单词序号")
    head_word = Column(String(100), nullable=False, index=True, comment="单词")
    translation = Column(Text, comment="中文翻译")
    book_id = Column(String(50), comment="单词书ID")
    word_id = Column(String(50), comment="单词ID")
    us_phone = Column(String(100), comment="美音音标")
    uk_phone = Column(String(100), comment="英音音标")
    
    def __repr__(self):
        return f"<Level8Vocabulary(head_word='{self.head_word}')>"


# 表名到模型类的映射
TABLE_MODEL_MAPPING = {
    "cet4": CET4Vocabulary,
    "cet6": CET6Vocabulary,
    "kaoyan": KaoyanVocabulary,
    "level4": Level4Vocabulary,
    "level8": Level8Vocabulary,
}