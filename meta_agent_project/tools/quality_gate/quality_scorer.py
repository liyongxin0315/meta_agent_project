"""
质量评分器 - 核心实现
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any
from enum import Enum, auto

from meta_agent.core.logging import get_logger

logger = get_logger(__name__)


class QualityCategory(Enum):
    """质量类别"""
    TEST_COVERAGE = auto()
    TEST_PASS_RATE = auto()
    CODE_QUALITY = auto()
    SECURITY = auto()
    PERFORMANCE = auto()
    DOCUMENTATION = auto()


@dataclass
class QualityMetric:
    """质量指标"""
    category: QualityCategory
    name: str
    value: float
    weight: float = 1.0
    threshold: float = 0.8
    passed: bool = False


@dataclass
class QualityScore:
    """质量评分结果"""
    overall_score: float
    category_scores: Dict[QualityCategory, float]
    metrics: List[QualityMetric]
    passed: bool
    recommendations: List[str] = field(default_factory=list)


class QualityScorer:
    """质量评分器"""
    
    def __init__(self):
        self._category_weights: Dict[QualityCategory, float] = {
            QualityCategory.TEST_COVERAGE: 0.25,
            QualityCategory.TEST_PASS_RATE: 0.30,
            QualityCategory.CODE_QUALITY: 0.20,
            QualityCategory.SECURITY: 0.15,
            QualityCategory.PERFORMANCE: 0.05,
            QualityCategory.DOCUMENTATION: 0.05,
        }
        self._thresholds: Dict[QualityCategory, float] = {
            QualityCategory.TEST_COVERAGE: 0.80,
            QualityCategory.TEST_PASS_RATE: 0.95,
            QualityCategory.CODE_QUALITY: 0.75,
            QualityCategory.SECURITY: 0.90,
            QualityCategory.PERFORMANCE: 0.70,
            QualityCategory.DOCUMENTATION: 0.60,
        }
        self._overall_pass_threshold: float = 0.80
    
    def calculate_score(
        self,
        metrics: Dict[str, Any]
    ) -> QualityScore:
        """
        计算质量评分
        
        Args:
            metrics: 质量指标数据
            
        Returns:
            QualityScore: 质量评分结果
        """
        quality_metrics = self._extract_metrics(metrics)
        category_scores = self._calculate_category_scores(quality_metrics)
        overall_score = self._calculate_overall_score(category_scores)
        
        passed = overall_score >= self._overall_pass_threshold
        recommendations = self._generate_recommendations(quality_metrics, category_scores)
        
        return QualityScore(
            overall_score=overall_score,
            category_scores=category_scores,
            metrics=quality_metrics,
            passed=passed,
            recommendations=recommendations
        )
    
    def _extract_metrics(self, metrics_data: Dict[str, Any]) -> List[QualityMetric]:
        """从输入数据中提取质量指标"""
        quality_metrics: List[QualityMetric] = []
        
        coverage = metrics_data.get("test_coverage", 0.0)
        quality_metrics.append(QualityMetric(
            category=QualityCategory.TEST_COVERAGE,
            name="语句覆盖率",
            value=coverage,
            weight=1.0,
            threshold=self._thresholds[QualityCategory.TEST_COVERAGE],
            passed=coverage >= self._thresholds[QualityCategory.TEST_COVERAGE]
        ))
        
        pass_rate = metrics_data.get("test_pass_rate", 0.0)
        quality_metrics.append(QualityMetric(
            category=QualityCategory.TEST_PASS_RATE,
            name="测试通过率",
            value=pass_rate,
            weight=1.0,
            threshold=self._thresholds[QualityCategory.TEST_PASS_RATE],
            passed=pass_rate >= self._thresholds[QualityCategory.TEST_PASS_RATE]
        ))
        
        code_quality = metrics_data.get("code_quality", 0.0)
        quality_metrics.append(QualityMetric(
            category=QualityCategory.CODE_QUALITY,
            name="代码质量评分",
            value=code_quality,
            weight=1.0,
            threshold=self._thresholds[QualityCategory.CODE_QUALITY],
            passed=code_quality >= self._thresholds[QualityCategory.CODE_QUALITY]
        ))
        
        security_score = metrics_data.get("security_score", 0.0)
        quality_metrics.append(QualityMetric(
            category=QualityCategory.SECURITY,
            name="安全评分",
            value=security_score,
            weight=1.0,
            threshold=self._thresholds[QualityCategory.SECURITY],
            passed=security_score >= self._thresholds[QualityCategory.SECURITY]
        ))
        
        performance_score = metrics_data.get("performance_score", 0.0)
        quality_metrics.append(QualityMetric(
            category=QualityCategory.PERFORMANCE,
            name="性能评分",
            value=performance_score,
            weight=1.0,
            threshold=self._thresholds[QualityCategory.PERFORMANCE],
            passed=performance_score >= self._thresholds[QualityCategory.PERFORMANCE]
        ))
        
        doc_score = metrics_data.get("documentation_score", 0.0)
        quality_metrics.append(QualityMetric(
            category=QualityCategory.DOCUMENTATION,
            name="文档完整性",
            value=doc_score,
            weight=1.0,
            threshold=self._thresholds[QualityCategory.DOCUMENTATION],
            passed=doc_score >= self._thresholds[QualityCategory.DOCUMENTATION]
        ))
        
        return quality_metrics
    
    def _calculate_category_scores(
        self,
        metrics: List[QualityMetric]
    ) -> Dict[QualityCategory, float]:
        """计算各类别的评分"""
        category_scores: Dict[QualityCategory, float] = {}
        category_metrics: Dict[QualityCategory, List[QualityMetric]] = {}
        
        for metric in metrics:
            if metric.category not in category_metrics:
                category_metrics[metric.category] = []
            category_metrics[metric.category].append(metric)
        
        for category, cat_metrics in category_metrics.items():
            total_weight = sum(m.weight for m in cat_metrics)
            if total_weight > 0:
                weighted_score = sum(m.value * m.weight for m in cat_metrics) / total_weight
                category_scores[category] = weighted_score
            else:
                category_scores[category] = 0.0
        
        for category in QualityCategory:
            if category not in category_scores:
                category_scores[category] = 0.0
        
        return category_scores
    
    def _calculate_overall_score(
        self,
        category_scores: Dict[QualityCategory, float]
    ) -> float:
        """计算综合评分"""
        total_weight = sum(self._category_weights.values())
        weighted_sum = sum(
            category_scores[category] * self._category_weights[category]
            for category in QualityCategory
        )
        return weighted_sum / total_weight if total_weight > 0 else 0.0
    
    def _generate_recommendations(
        self,
        metrics: List[QualityMetric],
        category_scores: Dict[QualityCategory, float]
    ) -> List[str]:
        """生成改进建议"""
        recommendations: List[str] = []
        
        for metric in metrics:
            if not metric.passed:
                recommendations.append(
                    f"[{metric.category.name}] {metric.name} 不达标 "
                    f"(当前: {metric.value:.2%}, 阈值: {metric.threshold:.2%})"
                )
        
        for category, score in category_scores.items():
            threshold = self._thresholds[category]
            if score < threshold:
                recommendations.append(
                    f"建议优先提升 {category.name} 类别质量 "
                    f"(当前: {score:.2%}, 阈值: {threshold:.2%})"
                )
        
        return recommendations
