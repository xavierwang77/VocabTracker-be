from typing import Dict, Any, List
from pydantic import BaseModel


class VocabularyTestResult(BaseModel):
    """
    词汇测试结果模型
    """
    known: int  # 认识的单词数
    total: int  # 总测试单词数


class VocabularyEstimateRequest(BaseModel):
    """
    词汇量估算请求模型
    """
    cet4: VocabularyTestResult
    cet6: VocabularyTestResult
    kaoyan: VocabularyTestResult
    level4: VocabularyTestResult
    level8: VocabularyTestResult


class VocabularyEstimateResponse(BaseModel):
    """
    词汇量估算响应模型
    """
    estimated_vocabulary: int  # 估算的总词汇量
    breakdown: Dict[str, Dict[str, Any]]  # 各词汇集的详细分析
    confidence_level: str  # 置信度等级
    recommendations: List[str]  # 学习建议


class VocabularyEstimateService:
    """
    词汇量估算服务类
    """
    
    # 各词汇集的平均词汇量基准（基于统计数据）
    VOCABULARY_BENCHMARKS = {
        "cet4": {
            "total_words": 4500,  # CET4词汇总量
            "average_mastery": 0.7,  # 平均掌握率
            "weight": 0.2  # 在总词汇量中的权重
        },
        "cet6": {
            "total_words": 6000,  # CET6词汇总量
            "average_mastery": 0.6,  # 平均掌握率
            "weight": 0.25  # 在总词汇量中的权重
        },
        "kaoyan": {
            "total_words": 5500,  # 考研词汇总量
            "average_mastery": 0.65,  # 平均掌握率
            "weight": 0.25  # 在总词汇量中的权重
        },
        "level4": {
            "total_words": 8000,  # 专四词汇总量
            "average_mastery": 0.5,  # 平均掌握率
            "weight": 0.15  # 在总词汇量中的权重
        },
        "level8": {
            "total_words": 12000,  # 专八词汇总量
            "average_mastery": 0.4,  # 平均掌握率
            "weight": 0.15  # 在总词汇量中的权重
        }
    }
    
    @classmethod
    def estimate_vocabulary(cls, request: VocabularyEstimateRequest) -> VocabularyEstimateResponse:
        """
        根据用户测试结果估算总词汇量
        
        Args:
            request: 词汇测试结果请求
            
        Returns:
            词汇量估算响应
        """
        breakdown = {}
        total_estimated = 0
        valid_tests = 0
        
        # 处理各个词汇集的测试结果
        test_results = {
            "cet4": request.cet4,
            "cet6": request.cet6,
            "kaoyan": request.kaoyan,
            "level4": request.level4,
            "level8": request.level8
        }
        
        for vocab_type, test_result in test_results.items():
            if test_result.total > 0:  # 只处理有效的测试结果
                mastery_rate = test_result.known / test_result.total
                benchmark = cls.VOCABULARY_BENCHMARKS[vocab_type]
                
                # 基于掌握率估算该词汇集的词汇量
                estimated_words = int(mastery_rate * benchmark["total_words"])
                
                # 计算相对于平均水平的表现
                relative_performance = mastery_rate / benchmark["average_mastery"]
                
                breakdown[vocab_type] = {
                    "known": test_result.known,
                    "total_tested": test_result.total,
                    "mastery_rate": round(mastery_rate * 100, 1),
                    "estimated_words": estimated_words,
                    "relative_performance": round(relative_performance, 2),
                    "performance_level": cls._get_performance_level(relative_performance)
                }
                
                # 加权计算总词汇量
                total_estimated += estimated_words * benchmark["weight"]
                valid_tests += 1
        
        # 如果没有有效测试，返回默认值
        if valid_tests == 0:
            total_estimated = 2000  # 基础词汇量
            confidence_level = "低"
        else:
            # 根据测试数量调整置信度
            confidence_level = cls._calculate_confidence_level(valid_tests, breakdown)
        
        # 生成学习建议
        recommendations = cls._generate_recommendations(breakdown)
        
        return VocabularyEstimateResponse(
            estimated_vocabulary=int(total_estimated),
            breakdown=breakdown,
            confidence_level=confidence_level,
            recommendations=recommendations
        )
    
    @staticmethod
    def _get_performance_level(relative_performance: float) -> str:
        """
        根据相对表现获取水平等级
        
        Args:
            relative_performance: 相对表现值
            
        Returns:
            水平等级描述
        """
        if relative_performance >= 1.3:
            return "优秀"
        elif relative_performance >= 1.1:
            return "良好"
        elif relative_performance >= 0.9:
            return "平均"
        elif relative_performance >= 0.7:
            return "一般"
        else:
            return "需要提高"
    
    @staticmethod
    def _calculate_confidence_level(valid_tests: int, breakdown: Dict[str, Dict[str, Any]]) -> str:
        """
        计算估算结果的置信度等级
        
        Args:
            valid_tests: 有效测试数量
            breakdown: 详细分析结果
            
        Returns:
            置信度等级
        """
        if valid_tests >= 4:
            return "高"
        elif valid_tests >= 2:
            return "中"
        else:
            return "低"
    
    @staticmethod
    def _generate_recommendations(breakdown: Dict[str, Dict[str, Any]]) -> List[str]:
        """
        根据测试结果生成学习建议
        
        Args:
            breakdown: 详细分析结果
            
        Returns:
            学习建议列表
        """
        recommendations = []
        
        # 分析各词汇集的表现
        weak_areas = []
        strong_areas = []
        
        for vocab_type, result in breakdown.items():
            performance = result.get("relative_performance", 0)
            if performance < 0.8:
                weak_areas.append(vocab_type)
            elif performance > 1.2:
                strong_areas.append(vocab_type)
        
        # 生成针对性建议
        if weak_areas:
            vocab_names = {
                "cet4": "CET4",
                "cet6": "CET6", 
                "kaoyan": "考研",
                "level4": "专业四级",
                "level8": "专业八级"
            }
            weak_names = [vocab_names.get(area, area) for area in weak_areas]
            recommendations.append(f"建议重点加强 {', '.join(weak_names)} 词汇的学习")
        
        if strong_areas:
            recommendations.append("在优势词汇领域继续保持，可以尝试更高难度的词汇")
        
        # 通用建议
        if len(breakdown) < 3:
            recommendations.append("建议完成更多词汇测试以获得更准确的评估")
        
        recommendations.append("建议每天坚持词汇学习，循序渐进提高词汇量")
        recommendations.append("可以通过阅读、听力等方式在语境中学习词汇")
        
        return recommendations