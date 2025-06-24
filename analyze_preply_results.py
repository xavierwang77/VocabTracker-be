#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Preply词汇测试结果分析脚本

功能说明:
- 读取preply_results目录中的测试结果文件
- 分析用户认识的单词在各词汇表(CET4/CET6/考研/专四/专八)中的分布
- 基于词汇表分布计算用户词汇量
- 与Preply官方结果对比，计算差异率

使用方法:
    python analyze_vocab_results.py
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Tuple
from datetime import datetime
import logging

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import Settings
from app.models.vocabulary import (
    CET4Vocabulary, CET6Vocabulary, KaoyanVocabulary, 
    Level4Vocabulary, Level8Vocabulary
)
from app.service.vocabulary_service import VocabularyEstimateService

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('vocab_analysis.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class VocabResultAnalyzer:
    """
    词汇测试结果分析器
    """
    
    def __init__(self):
        """
        初始化分析器
        """
        self.settings = Settings()
        self.engine = None
        self.session = None
        self._setup_database()
        
        # 词汇表优先级映射（数字越大优先级越高）
        self.vocab_priority = {
            'cet4': 1,
            'cet6': 2, 
            'kaoyan': 3,
            'level4': 4,
            'level8': 5
        }
        
        # 词汇表模型映射
        self.vocab_models = {
            'cet4': CET4Vocabulary,
            'cet6': CET6Vocabulary,
            'kaoyan': KaoyanVocabulary,
            'level4': Level4Vocabulary,
            'level8': Level8Vocabulary
        }
        
        # 词汇表中文名称
        self.vocab_names = {
            'cet4': 'CET4',
            'cet6': 'CET6',
            'kaoyan': '考研',
            'level4': '专四',
            'level8': '专八'
        }
    
    def _setup_database(self):
        """
        设置数据库连接
        """
        try:
            # 构建数据库连接URL
            db_url = (
                f"postgresql://{self.settings.database_user}:"
                f"{self.settings.database_password}@"
                f"{self.settings.database_host}:"
                f"{self.settings.database_port}/"
                f"{self.settings.database_name}"
            )
            
            self.engine = create_engine(db_url, echo=False)
            SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            self.session = SessionLocal()
            
            logger.info("数据库连接成功")
            
        except Exception as e:
            logger.error(f"数据库连接失败: {e}")
            raise
    
    def get_test_result_files(self) -> List[str]:
        """
        获取preply_results目录中的所有测试结果文件
        
        Returns:
            List[str]: 测试结果文件路径列表
        """
        results_dir = project_root / 'preply_results'
        if not results_dir.exists():
            logger.error(f"结果目录不存在: {results_dir}")
            return []
        
        json_files = list(results_dir.glob('vocab_test_result_*.json'))
        logger.info(f"找到 {len(json_files)} 个测试结果文件")
        
        return [str(f) for f in json_files]
    
    def load_test_result(self, file_path: str) -> Dict[str, Any]:
        """
        加载测试结果文件
        
        Args:
            file_path: 测试结果文件路径
            
        Returns:
            Dict[str, Any]: 测试结果数据
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"成功加载测试结果: {file_path}")
            return data
        except Exception as e:
            logger.error(f"加载测试结果文件失败 {file_path}: {e}")
            return {}
    
    def extract_known_words(self, test_data: Dict[str, Any]) -> List[str]:
        """
        提取用户认识的单词列表
        
        Args:
            test_data: 测试结果数据
            
        Returns:
            List[str]: 用户认识的单词列表
        """
        known_words = []
        
        for round_data in test_data.get('rounds', []):
            for word_info in round_data.get('words', []):
                if word_info.get('known', False):
                    known_words.append(word_info.get('word', '').lower())
        
        # 去重
        known_words = list(set(known_words))
        logger.info(f"提取到 {len(known_words)} 个认识的单词")
        
        return known_words
    
    def analyze_word_distribution(self, known_words: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        分析单词在各词汇表中的分布
        
        Args:
            known_words: 用户认识的单词列表
            
        Returns:
            Dict[str, Dict[str, Any]]: 各词汇表的分析结果
        """
        distribution = {}
        word_levels = {}  # 记录每个单词的最高等级
        
        # 查询每个词汇表
        for vocab_type, model_class in self.vocab_models.items():
            try:
                # 查询该词汇表中存在的单词
                found_words = self.session.query(model_class.head_word).filter(
                    model_class.head_word.in_(known_words)
                ).all()
                
                found_word_list = [word[0].lower() for word in found_words]
                
                # 更新单词等级映射
                for word in found_word_list:
                    current_priority = self.vocab_priority[vocab_type]
                    if word not in word_levels or word_levels[word]['priority'] < current_priority:
                        word_levels[word] = {
                            'level': vocab_type,
                            'priority': current_priority
                        }
                
                distribution[vocab_type] = {
                    'found_words': found_word_list,
                    'count': len(found_word_list),
                    'total_tested': len(known_words)
                }
                
                logger.info(f"{self.vocab_names[vocab_type]}词汇表: 找到 {len(found_word_list)} 个单词")
                
            except Exception as e:
                logger.error(f"查询{vocab_type}词汇表时出错: {e}")
                distribution[vocab_type] = {
                    'found_words': [],
                    'count': 0,
                    'total_tested': len(known_words)
                }
        
        # 统计按最高等级分类的单词数量
        level_counts = {level: 0 for level in self.vocab_priority.keys()}
        for word_info in word_levels.values():
            level_counts[word_info['level']] += 1
        
        # 添加等级统计信息
        for vocab_type in distribution.keys():
            distribution[vocab_type]['highest_level_count'] = level_counts[vocab_type]
        
        return distribution
    
    def calculate_vocabulary_estimate(self, distribution: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        基于词汇表分布计算词汇量估算
        
        Args:
            distribution: 词汇表分布分析结果
            
        Returns:
            Dict[str, Any]: 词汇量估算结果
        """
        from app.service.vocabulary_service import VocabularyTestResult, VocabularyEstimateRequest
        
        # 构建测试结果
        test_results = {}
        for vocab_type, data in distribution.items():
            if data['total_tested'] > 0:
                test_results[vocab_type] = VocabularyTestResult(
                    known=data['highest_level_count'],  # 使用最高等级计数
                    total=data['total_tested']
                )
            else:
                test_results[vocab_type] = VocabularyTestResult(known=0, total=0)
        
        # 创建估算请求
        request = VocabularyEstimateRequest(
            cet4=test_results['cet4'],
            cet6=test_results['cet6'],
            kaoyan=test_results['kaoyan'],
            level4=test_results['level4'],
            level8=test_results['level8']
        )
        
        # 计算估算结果
        estimate_response = VocabularyEstimateService.estimate_vocabulary(request)
        
        return {
            'estimated_vocabulary': estimate_response.estimated_vocabulary,
            'breakdown': estimate_response.breakdown,
            'confidence_level': estimate_response.confidence_level,
            'recommendations': estimate_response.recommendations
        }
    
    def calculate_difference_rate(self, our_estimate: int, preply_result: str) -> Tuple[float, str]:
        """
        计算我们的估算与Preply结果的差异率
        
        Args:
            our_estimate: 我们的词汇量估算
            preply_result: Preply的词汇量结果
            
        Returns:
            Tuple[float, str]: (差异率, 差异描述)
        """
        try:
            preply_vocab = int(preply_result)
            if preply_vocab == 0:
                return 0.0, "Preply结果为0，无法计算差异率"
            
            difference_rate = abs(our_estimate - preply_vocab) / preply_vocab * 100
            
            if our_estimate > preply_vocab:
                direction = "高估"
            elif our_estimate < preply_vocab:
                direction = "低估"
            else:
                direction = "一致"
            
            return difference_rate, f"{direction} {difference_rate:.1f}%"
            
        except (ValueError, TypeError):
            return 0.0, "Preply结果格式错误，无法计算差异率"
    
    def analyze_single_result(self, file_path: str) -> Dict[str, Any]:
        """
        分析单个测试结果文件
        
        Args:
            file_path: 测试结果文件路径
            
        Returns:
            Dict[str, Any]: 分析结果
        """
        # 加载测试数据
        test_data = self.load_test_result(file_path)
        if not test_data:
            return {}
        
        # 提取用户信息
        file_name = os.path.basename(file_path)
        user_id = file_name.replace('vocab_test_result_', '').replace('.json', '')
        
        # 提取认识的单词
        known_words = self.extract_known_words(test_data)
        
        # 分析词汇表分布
        distribution = self.analyze_word_distribution(known_words)
        
        # 计算词汇量估算
        our_estimate = self.calculate_vocabulary_estimate(distribution)
        
        # 获取Preply结果
        preply_result = test_data.get('final_vocab_size', '0')
        
        # 计算差异率
        diff_rate, diff_desc = self.calculate_difference_rate(
            our_estimate['estimated_vocabulary'], 
            preply_result
        )
        
        return {
            'user_id': user_id,
            'file_path': file_path,
            'known_words_count': len(known_words),
            'distribution': distribution,
            'our_estimate': our_estimate,
            'preply_result': preply_result,
            'difference_rate': diff_rate,
            'difference_description': diff_desc,
            'test_summary': test_data.get('summary', {})
        }
    
    def analyze_all_results(self) -> List[Dict[str, Any]]:
        """
        分析所有测试结果文件
        
        Returns:
            List[Dict[str, Any]]: 所有用户的分析结果
        """
        result_files = self.get_test_result_files()
        if not result_files:
            logger.warning("没有找到测试结果文件")
            return []
        
        all_results = []
        
        for file_path in result_files:
            logger.info(f"正在分析: {file_path}")
            result = self.analyze_single_result(file_path)
            if result:
                all_results.append(result)
        
        return all_results
    
    def generate_summary_report(self, all_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        生成汇总报告
        
        Args:
            all_results: 所有用户的分析结果
            
        Returns:
            Dict[str, Any]: 汇总报告
        """
        if not all_results:
            return {}
        
        total_users = len(all_results)
        total_diff_rates = [r['difference_rate'] for r in all_results if r['difference_rate'] > 0]
        
        avg_diff_rate = sum(total_diff_rates) / len(total_diff_rates) if total_diff_rates else 0
        
        # 统计各词汇表的平均命中率
        vocab_stats = {}
        for vocab_type in self.vocab_priority.keys():
            hit_rates = []
            for result in all_results:
                dist = result['distribution'].get(vocab_type, {})
                if dist.get('total_tested', 0) > 0:
                    hit_rate = dist.get('highest_level_count', 0) / dist['total_tested'] * 100
                    hit_rates.append(hit_rate)
            
            vocab_stats[vocab_type] = {
                'name': self.vocab_names[vocab_type],
                'avg_hit_rate': sum(hit_rates) / len(hit_rates) if hit_rates else 0,
                'users_tested': len(hit_rates)
            }
        
        return {
            'total_users': total_users,
            'average_difference_rate': avg_diff_rate,
            'vocab_stats': vocab_stats,
            'analysis_time': datetime.now().isoformat()
        }
    
    def save_analysis_report(self, all_results: List[Dict[str, Any]], summary: Dict[str, Any]):
        """
        保存分析报告到文件
        
        Args:
            all_results: 所有用户的分析结果
            summary: 汇总报告
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = project_root / f'preply_results_analysis_report_{timestamp}.json'
        
        report_data = {
            'summary': summary,
            'detailed_results': all_results
        }
        
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"分析报告已保存到: {report_file}")
            print(f"📊 分析报告已保存到: {report_file}")
            
        except Exception as e:
            logger.error(f"保存分析报告失败: {e}")
    
    def print_summary_report(self, summary: Dict[str, Any]):
        """
        打印汇总报告
        
        Args:
            summary: 汇总报告数据
        """
        print("\n" + "=" * 80)
        print("📊 Preply词汇测试结果分析汇总报告")
        print("=" * 80)
        
        print(f"\n📈 总体统计:")
        print(f"   - 分析用户数: {summary.get('total_users', 0)}")
        print(f"   - 平均差异率: {summary.get('average_difference_rate', 0):.1f}%")
        
        print(f"\n📚 各词汇表命中率统计:")
        vocab_stats = summary.get('vocab_stats', {})
        for vocab_type, stats in vocab_stats.items():
            print(f"   - {stats['name']}: {stats['avg_hit_rate']:.1f}% (测试用户: {stats['users_tested']})")
        
        print(f"\n⏰ 分析时间: {summary.get('analysis_time', '')}")
        print("=" * 80)
    
    def close(self):
        """
        关闭数据库连接
        """
        if self.session:
            self.session.close()
        if self.engine:
            self.engine.dispose()
        logger.info("数据库连接已关闭")


def main():
    """
    主函数
    """
    print("\n🚀 开始Preply词汇测试结果分析...")
    
    analyzer = None
    try:
        # 创建分析器
        analyzer = VocabResultAnalyzer()
        
        # 分析所有结果
        all_results = analyzer.analyze_all_results()
        
        if not all_results:
            print("❌ 没有找到有效的测试结果文件")
            return
        
        # 生成汇总报告
        summary = analyzer.generate_summary_report(all_results)
        
        # 打印汇总报告
        analyzer.print_summary_report(summary)
        
        # 保存详细报告
        analyzer.save_analysis_report(all_results, summary)
        
        print("\n🎉 分析完成！")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断了分析过程")
    except Exception as e:
        logger.error(f"分析过程中发生错误: {e}")
        print(f"\n❌ 分析失败: {e}")
    finally:
        if analyzer:
            analyzer.close()


if __name__ == "__main__":
    main()