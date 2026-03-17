# -*- coding: utf-8 -*-
"""
多因子评分器
============
整合技术面、基本面、资金面、筹码面、情绪面的综合评分系统

参考：GEMINI-5D Pro v3.0 最优评分标准
"""

import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

from .score_dimensions import (
    TechnicalScorer,
    FundamentalScorer,
    MoneyFlowScorer,
    ChipScorer,
    SentimentScorer,
)

logger = logging.getLogger(__name__)


class StrategyType(Enum):
    """评分策略类型"""
    FULL_DATA = "full_data"      # 数据完整，标准权重
    TECH_FOCUS = "tech_focus"    # 技术面主导
    CONSERVATIVE = "conservative"  # 保守策略，技术面绝对主导


@dataclass
class ScoreResult:
    """评分结果"""
    # 各维度得分 (-10 到 +10)
    technical_score: float
    fundamental_score: float
    moneyflow_score: float
    chip_score: float
    sentiment_score: float

    # 综合评分 (0-100)
    total_score: int

    # 权重配置
    weights: Dict[str, float]

    # 策略类型
    strategy: StrategyType

    # 数据完整度 (0-1)
    data_completeness: float

    # 可靠性评级
    reliability: str  # "高" / "中" / "低"

    # 各维度详情
    details: Dict[str, Dict[str, Any]]

    # 投资建议
    suggestion: str

    # 一票否决标记
    veto_flags: List[str]


class MultiFactorScorer:
    """
    多因子综合评分器
    =================

    评分逻辑：
    1. 各维度独立评分 (-10 到 +10)
    2. 根据数据完整度选择评分策略
    3. 加权计算综合得分 (0-100)
    4. 一票否决检查
    """

    def __init__(self):
        self.technical_scorer = TechnicalScorer()
        self.fundamental_scorer = FundamentalScorer()
        self.moneyflow_scorer = MoneyFlowScorer()
        self.chip_scorer = ChipScorer()
        self.sentiment_scorer = SentimentScorer()

        # 权重配置 (可根据策略动态调整)
        self.weights = {
            'technical': 5.0,    # 技术面权重最高
            'fundamental': 2.0,  # 基本面
            'moneyflow': 1.5,    # 资金面
            'chip': 1.5,         # 筹码面
            'sentiment': 1.0,    # 情绪面
        }

    def calculate(
        self,
        technical_data: Dict[str, Any],
        fundamental_data: Dict[str, Any],
        moneyflow_data: Dict[str, Any],
        chip_data: Dict[str, Any],
        sentiment_data: Dict[str, Any],
        stock_info: Optional[Dict] = None
    ) -> ScoreResult:
        """
        计算多维度综合评分

        Args:
            technical_data: 技术面数据 (MA, MACD, KDJ, RSI等)
            fundamental_data: 基本面数据 (PE, ROE, 成长等)
            moneyflow_data: 资金面数据 (主力流向, 成交量等)
            chip_data: 筹码数据 (获利比例, 集中度等)
            sentiment_data: 情绪数据 (新闻情绪, 分析师评级等)
            stock_info: 股票基本信息 (名称, 行业等)

        Returns:
            ScoreResult: 完整评分结果
        """
        # 1. 各维度独立评分
        tech_result = self.technical_scorer.calculate(technical_data)
        fund_result = self.fundamental_scorer.calculate(fundamental_data)
        money_result = self.moneyflow_scorer.calculate(moneyflow_data)
        chip_result = self.chip_scorer.calculate(chip_data)
        sent_result = self.sentiment_scorer.calculate(sentiment_data)

        # 2. 计算数据完整度
        completeness = self._calculate_completeness([
            tech_result, fund_result, money_result, chip_result, sent_result
        ])

        # 3. 根据完整度选择策略
        strategy = self._select_strategy(completeness)
        weights = self._adjust_weights(strategy)

        # 4. 检查一票否决
        veto_flags = self._check_veto(stock_info, fund_result)

        # 5. 加权计算综合得分
        total_score = self._calculate_weighted_score(
            tech_result.score,
            fund_result.score,
            money_result.score,
            chip_result.score,
            sent_result.score,
            weights,
            veto_flags
        )

        # 6. 确定可靠性评级
        reliability = self._get_reliability(completeness)

        # 7. 生成投资建议
        suggestion = self._generate_suggestion(
            total_score, tech_result.score, veto_flags
        )

        return ScoreResult(
            technical_score=round(tech_result.score, 2),
            fundamental_score=round(fund_result.score, 2),
            moneyflow_score=round(money_result.score, 2),
            chip_score=round(chip_result.score, 2),
            sentiment_score=round(sent_result.score, 2),
            total_score=total_score,
            weights=weights,
            strategy=strategy,
            data_completeness=completeness,
            reliability=reliability,
            details={
                'technical': {
                    'score': tech_result.score,
                    'confidence': tech_result.confidence,
                    'details': tech_result.details,
                },
                'fundamental': {
                    'score': fund_result.score,
                    'confidence': fund_result.confidence,
                    'details': fund_result.details,
                },
                'moneyflow': {
                    'score': money_result.score,
                    'confidence': money_result.confidence,
                    'details': money_result.details,
                },
                'chip': {
                    'score': chip_result.score,
                    'confidence': chip_result.confidence,
                    'details': chip_result.details,
                },
                'sentiment': {
                    'score': sent_result.score,
                    'confidence': sent_result.confidence,
                    'details': sent_result.details,
                },
            },
            suggestion=suggestion,
            veto_flags=veto_flags
        )

    def _calculate_completeness(self, results: List) -> float:
        """计算数据完整度"""
        total_confidence = sum(r.confidence for r in results)
        # 最大可能置信度是5 (每个维度最大1.0)
        return min(1.0, total_confidence / 5.0)

    def _select_strategy(self, completeness: float) -> StrategyType:
        """根据完整度选择评分策略"""
        if completeness >= 0.8:
            return StrategyType.FULL_DATA
        elif completeness >= 0.5:
            return StrategyType.TECH_FOCUS
        else:
            return StrategyType.CONSERVATIVE

    def _adjust_weights(self, strategy: StrategyType) -> Dict[str, float]:
        """根据策略调整权重"""
        if strategy == StrategyType.FULL_DATA:
            # 标准权重
            return self.weights.copy()
        elif strategy == StrategyType.TECH_FOCUS:
            # 技术面提升
            return {
                'technical': 7.0,
                'fundamental': 1.0,
                'moneyflow': 1.0,
                'chip': 0.5,
                'sentiment': 0.5,
            }
        else:  # CONSERVATIVE
            # 技术面绝对主导
            return {
                'technical': 9.0,
                'fundamental': 0.5,
                'moneyflow': 0.0,
                'chip': 0.5,
                'sentiment': 0.0,
            }

    def _check_veto(self, stock_info: Optional[Dict], fund_result) -> List[str]:
        """检查一票否决项"""
        flags = []

        if not stock_info:
            return flags

        # ST股
        name = stock_info.get('name', '')
        if 'ST' in name or '*ST' in name:
            flags.append('ST股票')

        # 连续亏损
        roe = fund_result.raw_data.get('roe')
        if roe is not None and roe < -10:
            flags.append('严重亏损(ROE<-10%)')

        # 极高负债
        debt = fund_result.raw_data.get('debt_to_assets')
        if debt is not None and debt > 90:
            flags.append('高负债(>90%)')

        return flags

    def _calculate_weighted_score(
        self,
        tech: float,
        fund: float,
        money: float,
        chip: float,
        sent: float,
        weights: Dict[str, float],
        veto_flags: List[str]
    ) -> int:
        """计算加权综合得分"""
        # 基础加权得分
        total_weight = sum(weights.values())
        if total_weight == 0:
            total_weight = 1

        weighted = (
            tech * weights['technical'] +
            fund * weights['fundamental'] +
            money * weights['moneyflow'] +
            chip * weights['chip'] +
            sent * weights['sentiment']
        ) / total_weight

        # 一票否决扣分
        if veto_flags:
            weighted -= 5.0

        # 映射到 0-100
        # -10 映射到 0, 0 映射到 50, +10 映射到 100
        score = int((weighted + 10) / 20 * 100)
        score = max(0, min(100, score))

        return score

    def _get_reliability(self, completeness: float) -> str:
        """获取可靠性评级"""
        if completeness >= 0.8:
            return "高"
        elif completeness >= 0.5:
            return "中"
        else:
            return "低"

    def _generate_suggestion(
        self,
        total_score: int,
        tech_score: float,
        veto_flags: List[str]
    ) -> str:
        """生成投资建议"""
        if veto_flags:
            return f"一票否决: {'; '.join(veto_flags)} - 建议规避"

        if total_score >= 80:
            return "强烈推荐 - 多维度表现优秀"
        elif total_score >= 65:
            return "增持 - 整体表现良好"
        elif total_score >= 50:
            if tech_score >= 5:
                return "观望偏乐观 - 技术面良好，等待其他维度改善"
            else:
                return "观望 - 整体表现中性"
        elif total_score >= 35:
            return "减仓 - 整体偏弱"
        else:
            return "规避 - 多维度表现不佳"

    def format_report(self, result: ScoreResult) -> str:
        """格式化评分报告"""
        lines = []
        lines.append("=" * 60)
        lines.append("多维度综合评分报告")
        lines.append("=" * 60)

        # 基本信息
        lines.append(f"\n综合评分: {result.total_score}/100")
        lines.append(f"评级: {result.reliability}可靠性 ({result.strategy.value})")
        lines.append(f"数据完整度: {result.data_completeness:.1%}")

        # 一票否决
        if result.veto_flags:
            lines.append(f"\n⚠️ 一票否决: {', '.join(result.veto_flags)}")

        # 各维度得分
        lines.append("\n各维度得分 (-10 ~ +10):")
        lines.append(f"  技术面: {result.technical_score:+.2f} (权重: {result.weights['technical']:.1f})")
        lines.append(f"  基本面: {result.fundamental_score:+.2f} (权重: {result.weights['fundamental']:.1f})")
        lines.append(f"  资金面: {result.moneyflow_score:+.2f} (权重: {result.weights['moneyflow']:.1f})")
        lines.append(f"  筹码面: {result.chip_score:+.2f} (权重: {result.weights['chip']:.1f})")
        lines.append(f"  情绪面: {result.sentiment_score:+.2f} (权重: {result.weights['sentiment']:.1f})")

        # 投资建议
        lines.append(f"\n💡 建议: {result.suggestion}")

        lines.append("=" * 60)

        return "\n".join(lines)
