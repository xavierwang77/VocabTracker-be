import json
import os
import sys
import json
from pathlib import Path
from typing import List, Dict, Any
import logging

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.orm import Session
from app.db import SessionLocal, init_db, check_db_connection
from app.models import TABLE_MODEL_MAPPING

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class VocabularyDataSync:
    """
    词汇数据同步类
    负责从JSON文件读取数据并同步到数据库
    """
    
    def __init__(self, datasets_dir: str = "datasets"):
        """
        初始化数据同步器
        
        Args:
            datasets_dir: 数据集目录路径
        """
        self.datasets_dir = Path(datasets_dir)
        self.db_session: Session = None
        
        # 文件名到表名的映射
        self.file_table_mapping = {
            "cet4.json": "cet4",
            "cet6.json": "cet6", 
            "kaoyan.json": "kaoyan",
            "level4.json": "level4",
            "level8.json": "level8"
        }
    
    def _get_db_session(self) -> Session:
        """
        获取数据库会话
        """
        if self.db_session is None:
            self.db_session = SessionLocal()
        return self.db_session
    
    def _close_db_session(self):
        """
        关闭数据库会话
        """
        if self.db_session:
            self.db_session.close()
            self.db_session = None
    
    def _extract_translation(self, word_data: Dict[str, Any]) -> str:
        """
        从词汇数据中提取中文翻译
        
        Args:
            word_data: 单词数据字典
            
        Returns:
            中文翻译字符串
        """
        try:
            content = word_data.get("content", {})
            word_content = content.get("word", {})
            word_detail = word_content.get("content", {})
            trans_list = word_detail.get("trans", [])
            
            # 提取所有翻译并合并
            translations = []
            for trans in trans_list:
                tran_cn = trans.get("tranCn", "")
                pos = trans.get("pos", "")
                if tran_cn:
                    if pos:
                        translations.append(f"{pos}. {tran_cn}")
                    else:
                        translations.append(tran_cn)
            
            return "; ".join(translations) if translations else ""
        except Exception as e:
            logger.warning(f"提取翻译失败: {e}")
            return ""
    
    def _extract_phonetics(self, word_data: Dict[str, Any]) -> tuple:
        """
        从词汇数据中提取音标信息
        
        Args:
            word_data: 单词数据字典
            
        Returns:
            (美音音标, 英音音标) 元组
        """
        try:
            content = word_data.get("content", {})
            word_content = content.get("word", {})
            word_detail = word_content.get("content", {})
            
            us_phone = word_detail.get("usphone", "")
            uk_phone = word_detail.get("ukphone", "")
            
            return us_phone, uk_phone
        except Exception as e:
            logger.warning(f"提取音标失败: {e}")
            return "", ""
    
    def _extract_word_id(self, word_data: Dict[str, Any]) -> str:
        """
        从词汇数据中提取单词ID
        
        Args:
            word_data: 单词数据字典
            
        Returns:
            单词ID字符串
        """
        try:
            content = word_data.get("content", {})
            word_content = content.get("word", {})
            return word_content.get("wordId", "")
        except Exception as e:
            logger.warning(f"提取单词ID失败: {e}")
            return ""
    
    def _parse_json_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        解析JSON文件 - 支持每行一个JSON对象的格式
        
        Args:
            file_path: JSON文件路径
            
        Returns:
            解析后的数据列表
        """
        data_list = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:  # 跳过空行
                        continue
                    
                    try:
                        # 解析每行的JSON数据
                        json_data = json.loads(line)
                        data_list.append(json_data)
                    except json.JSONDecodeError as e:
                        logger.warning(f"第{line_num}行JSON解析失败: {e}")
                        continue
                        
            logger.info(f"成功解析 {len(data_list)} 条记录从文件 {file_path}")
            return data_list
                
        except Exception as e:
            logger.error(f"解析JSON文件失败 {file_path}: {e}")
            return []
    
    def _create_vocabulary_record(self, word_data: Dict[str, Any], model_class) -> object:
        """
        创建词汇记录对象
        
        Args:
            word_data: 单词数据字典
            model_class: 模型类
            
        Returns:
            词汇记录对象
        """
        # 提取基本信息
        word_rank = word_data.get("wordRank", 0)
        head_word = word_data.get("headWord", "")
        book_id = word_data.get("bookId", "")
        
        # 提取翻译
        translation = self._extract_translation(word_data)
        
        # 提取音标
        us_phone, uk_phone = self._extract_phonetics(word_data)
        
        # 提取单词ID
        word_id = self._extract_word_id(word_data)
        
        # 创建记录
        return model_class(
            word_rank=word_rank,
            head_word=head_word,
            translation=translation,
            book_id=book_id,
            word_id=word_id,
            us_phone=us_phone,
            uk_phone=uk_phone
        )
    
    def sync_file(self, file_name: str) -> bool:
        """
        同步单个文件到数据库
        
        Args:
            file_name: 文件名
            
        Returns:
            是否同步成功
        """
        if file_name not in self.file_table_mapping:
            logger.error(f"不支持的文件: {file_name}")
            return False
        
        table_name = self.file_table_mapping[file_name]
        model_class = TABLE_MODEL_MAPPING[table_name]
        
        file_path = self.datasets_dir / file_name
        if not file_path.exists():
            logger.error(f"文件不存在: {file_path}")
            return False
        
        logger.info(f"开始同步文件: {file_name} -> 表: t_{table_name}")
        
        try:
            # 解析JSON数据
            word_list = self._parse_json_file(file_path)
            if not word_list:
                logger.warning(f"文件 {file_name} 中没有有效数据")
                return True
            
            db = self._get_db_session()
            
            # 清空现有数据
            db.query(model_class).delete()
            logger.info(f"清空表 t_{table_name} 的现有数据")
            
            # 批量插入新数据
            success_count = 0
            for word_data in word_list:
                try:
                    record = self._create_vocabulary_record(word_data, model_class)
                    db.add(record)
                    success_count += 1
                except Exception as e:
                    logger.warning(f"创建记录失败: {e}, 数据: {word_data.get('headWord', 'unknown')}")
            
            # 提交事务
            db.commit()
            logger.info(f"成功同步 {success_count} 条记录到表 t_{table_name}")
            return True
            
        except Exception as e:
            logger.error(f"同步文件 {file_name} 失败: {e}")
            if self.db_session:
                self.db_session.rollback()
            return False
    
    def sync_all(self) -> bool:
        """
        同步所有支持的文件到数据库
        
        Returns:
            是否全部同步成功
        """
        logger.info("开始同步所有词汇数据...")
        
        success_count = 0
        total_count = len(self.file_table_mapping)
        
        for file_name in self.file_table_mapping.keys():
            if self.sync_file(file_name):
                success_count += 1
            else:
                logger.error(f"同步文件 {file_name} 失败")
        
        logger.info(f"同步完成: {success_count}/{total_count} 个文件同步成功")
        return success_count == total_count
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self._close_db_session()


def main():
    """
    主函数 - 数据同步脚本入口
    """
    logger.info("=== 词汇数据同步脚本启动 ===")
    
    # 检查数据库连接
    if not check_db_connection():
        logger.error("数据库连接失败，请检查数据库配置")
        sys.exit(1)
    
    # 初始化数据库（创建表）
    try:
        init_db()
        logger.info("数据库初始化成功")
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        sys.exit(1)
    
    # 执行数据同步
    try:
        with VocabularyDataSync() as sync_tool:
            if sync_tool.sync_all():
                logger.info("=== 所有数据同步成功 ===")
            else:
                logger.error("=== 部分数据同步失败 ===")
                sys.exit(1)
    except Exception as e:
        logger.error(f"数据同步过程中发生错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()