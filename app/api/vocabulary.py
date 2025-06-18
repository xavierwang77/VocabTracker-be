from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict, Any
from pydantic import BaseModel

from app.db import get_db
from app.models.vocabulary import (
    CET4Vocabulary,
    CET6Vocabulary, 
    KaoyanVocabulary,
    Level4Vocabulary,
    Level8Vocabulary
)

router = APIRouter(prefix="/vocabulary", tags=["词汇"])


class VocabularyItem(BaseModel):
    """
    词汇项响应模型
    """
    id: int
    word_rank: int
    head_word: str
    translation: str
    book_id: str
    word_id: str
    us_phone: str
    uk_phone: str
    
    class Config:
        from_attributes = True


class RandomVocabularyResponse(BaseModel):
    """
    随机词汇响应模型
    """
    cet4: List[VocabularyItem]
    cet6: List[VocabularyItem]
    kaoyan: List[VocabularyItem]
    level4: List[VocabularyItem]
    level8: List[VocabularyItem]
    total_count: int


def get_random_words(db: Session, model_class, count: int = 20) -> List[VocabularyItem]:
    """
    从指定模型中随机获取词汇
    
    Args:
        db: 数据库会话
        model_class: 词汇模型类
        count: 获取数量，默认20个
        
    Returns:
        词汇列表
    """
    try:
        # 使用SQLAlchemy的func.random()进行随机查询
        words = db.query(model_class).order_by(func.random()).limit(count).all()
        return [VocabularyItem.from_orm(word) for word in words]
    except Exception as e:
        # 如果表为空或查询失败，返回空列表
        return []


@router.get("/random", response_model=RandomVocabularyResponse)
async def get_random_vocabulary(db: Session = Depends(get_db)):
    """
    随机获取各类型词汇
    
    从CET4、CET6、考研、专四、专八词汇表中各随机获取20个单词
    
    Returns:
        包含各类型词汇列表的响应
    """
    try:
        # 从各个表中随机获取20个词汇
        cet4_words = get_random_words(db, CET4Vocabulary, 20)
        cet6_words = get_random_words(db, CET6Vocabulary, 20)
        kaoyan_words = get_random_words(db, KaoyanVocabulary, 20)
        level4_words = get_random_words(db, Level4Vocabulary, 20)
        level8_words = get_random_words(db, Level8Vocabulary, 20)
        
        # 计算总词汇数
        total_count = (
            len(cet4_words) + 
            len(cet6_words) + 
            len(kaoyan_words) + 
            len(level4_words) + 
            len(level8_words)
        )
        
        return RandomVocabularyResponse(
            cet4=cet4_words,
            cet6=cet6_words,
            kaoyan=kaoyan_words,
            level4=level4_words,
            level8=level8_words,
            total_count=total_count
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取随机词汇失败: {str(e)}"
        )


@router.get("/random/{vocabulary_type}", response_model=List[VocabularyItem])
async def get_random_vocabulary_by_type(
    vocabulary_type: str,
    count: int = 20,
    db: Session = Depends(get_db)
):
    """
    根据类型随机获取词汇
    
    Args:
        vocabulary_type: 词汇类型 (cet4, cet6, kaoyan, level4, level8)
        count: 获取数量，默认20个，最大100个
        
    Returns:
        指定类型的词汇列表
    """
    # 限制最大获取数量
    if count > 100:
        count = 100
    
    # 词汇类型映射
    vocabulary_models = {
        "cet4": CET4Vocabulary,
        "cet6": CET6Vocabulary,
        "kaoyan": KaoyanVocabulary,
        "level4": Level4Vocabulary,
        "level8": Level8Vocabulary,
    }
    
    if vocabulary_type not in vocabulary_models:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的词汇类型: {vocabulary_type}。支持的类型: {', '.join(vocabulary_models.keys())}"
        )
    
    try:
        model_class = vocabulary_models[vocabulary_type]
        words = get_random_words(db, model_class, count)
        return words
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取{vocabulary_type}词汇失败: {str(e)}"
        )


@router.get("/stats")
async def get_vocabulary_stats(db: Session = Depends(get_db)):
    """
    获取词汇统计信息
    
    Returns:
        各类型词汇的数量统计
    """
    try:
        stats = {
            "cet4_count": db.query(CET4Vocabulary).count(),
            "cet6_count": db.query(CET6Vocabulary).count(),
            "kaoyan_count": db.query(KaoyanVocabulary).count(),
            "level4_count": db.query(Level4Vocabulary).count(),
            "level8_count": db.query(Level8Vocabulary).count(),
        }
        
        stats["total_count"] = sum(stats.values())
        return stats
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取词汇统计失败: {str(e)}"
        )