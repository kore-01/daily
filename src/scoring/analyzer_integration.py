# -*- coding: utf-8 -*-
"""
评分系统与Analyzer集成模块
============================
将多维度评分系统集成到现有AI分析流程中

功能：
1. 从analysis_context提取各维度数据
2. 计算多因子综合评分
3. 作为LLM评分的补充/后备
"""

import logging
from typing import Dict, Any, Optional
from dataclasses import asdict

from .multi_factor_scorer import MultiFactorScorer, ScoreResult

logger = logging.getLogger(__name__)


class ScoringIntegration:
    """
    评分系统集成器
    ==============

    将多维度评分系统集成到AI分析流程
    """

    def __init__(self):
        self.scorer = MultiFactorScorer()

    def calculate_from_context(self, context: Dict[str, Any]) -> Optional[ScoreResult]:
        """
        从analysis_context计算评分

        Args:
            context: analysis_context字典（来自storage.get_analysis_context）

        Returns:
            ScoreResult或None
        """
        try:
            # 提取各维度数据
            technical_data = self._extract_technical_data(context)
            fundamental_data = self._extract_fundamental_data(context)
            moneyflow_data = self._extract_moneyflow_data(context)
            chip_data = self._extract_chip_data(context)
            sentiment_data = self._extract_sentiment_data(context)
            stock_info = self._extract_stock_info(context)

            # 计算评分
            result = self.scorer.calculate(
                technical_data=technical_data,
                fundamental_data=fundamental_data,
                moneyflow_data=moneyflow_data,
                chip_data=chip_data,
                sentiment_data=sentiment_data,
                stock_info=stock_info
            )

            logger.info(f"[多因子评分] {stock_info.get('name', 'Unknown')}({stock_info.get('code', '')}) "
                       f"综合得分: {result.total_score}, 策略: {result.strategy.value}")

            return result

        except Exception as e:
            logger.error(f"[多因子评分] 计算失败: {e}")
            return None

    def _extract_technical_data(self, context: Dict) -> Dict[str, Any]:
        """提取技术面数据"""
        data = {}

        # 从technical提取
        tech = context.get('technical', {})
        if tech:
            data['ma5'] = tech.get('ma5')
            data['ma10'] = tech.get('ma10')
            data['ma20'] = tech.get('ma20')
            data['ma60'] = tech.get('ma60')
            data['bias_ma5'] = tech.get('bias_ma5')
            data['macd'] = tech.get('macd')
            data['macd_signal'] = tech.get('macd_signal')
            data['rsi6'] = tech.get('rsi6')
            data['kdj_k'] = tech.get('kdj_k')
            data['kdj_d'] = tech.get('kdj_d')
            data['boll_upper'] = tech.get('boll_upper')
            data['boll_lower'] = tech.get('boll_lower')
            data['close'] = tech.get('close')

        # 从realtime补充
        rt = context.get('realtime', {})
        if rt:
            if not data.get('close'):
                data['close'] = rt.get('price')

        return data

    def _extract_fundamental_data(self, context: Dict) -> Dict[str, Any]:
        """提取基本面数据"""
        data = {}

        # 从fundamental提取
        fund = context.get('fundamental', {})
        if fund:
            data['pe_ttm'] = fund.get('pe_ttm')
            data['pb'] = fund.get('pb')
            data['roe'] = fund.get('roe')
            data['netprofit_margin'] = fund.get('netprofit_margin')
            data['op_yoy'] = fund.get('op_yoy')
            data['netprofit_yoy'] = fund.get('netprofit_yoy')
            data['debt_to_assets'] = fund.get('debt_to_assets')

        # 从daily_basic补充
        db = context.get('daily_basic', {})
        if db:
            if not data.get('pe_ttm'):
                data['pe_ttm'] = db.get('pe')
            if not data.get('pb'):
                data['pb'] = db.get('pb')

        return data

    def _extract_moneyflow_data(self, context: Dict) -> Dict[str, Any]:
        """提取资金面数据"""
        data = {}

        # 从moneyflow提取
        mf = context.get('moneyflow', {})
        if mf:
            data['main_net_amount'] = mf.get('net_mf_amount')
            data['buy_lg_vol'] = mf.get('buy_lg_vol')
            data['sell_lg_vol'] = mf.get('sell_lg_vol')
            data['buy_elg_vol'] = mf.get('buy_elg_vol')
            data['sell_elg_vol'] = mf.get('sell_elg_vol')

        # 从realtime补充
        rt = context.get('realtime', {})
        if rt:
            data['volume_ratio'] = rt.get('volume_ratio')

        return data

    def _extract_chip_data(self, context: Dict) -> Dict[str, Any]:
        """提取筹码数据"""
        data = {}

        # 从chip_distribution提取
        chip = context.get('chip_distribution', {})
        if chip:
            data['profit_ratio'] = chip.get('profit_ratio')
            data['avg_cost'] = chip.get('avg_cost')
            data['concentration_90'] = chip.get('concentration_90')

        return data

    def _extract_sentiment_data(self, context: Dict) -> Dict[str, Any]:
        """提取情绪数据"""
        data = {}

        # 从news提取
        news = context.get('news', [])
        if news:
            # 简单统计新闻情绪
            positive = sum(1 for n in news if n.get('sentiment') == 'positive')
            negative = sum(1 for n in news if n.get('sentiment') == 'negative')
            total = len(news)

            if total > 0:
                if positive > negative:
                    data['news_sentiment'] = 'positive'
                elif negative > positive:
                    data['news_sentiment'] = 'negative'
                else:
                    data['news_sentiment'] = 'neutral'

        return data

    def _extract_stock_info(self, context: Dict) -> Dict[str, Any]:
        """提取股票基本信息"""
        return {
            'code': context.get('code', ''),
            'name': context.get('stock_name', ''),
            'industry': context.get('industry', ''),
        }

    def enhance_analysis_result(
        self,
        llm_result,
        score_result: ScoreResult
    ):
        """
        用多因子评分增强LLM分析结果

        Args:
            llm_result: AnalysisResult对象（来自LLM）
            score_result: ScoreResult对象（来自多因子评分）
        """
        # 如果LLM评分是默认值（50），用多因子评分替换
        if llm_result.sentiment_score == 50:
            llm_result.sentiment_score = score_result.total_score
            logger.info(f"[评分增强] 使用多因子评分替换默认评分: {score_result.total_score}")

        # 添加多维度评分详情到dashboard
        if not llm_result.dashboard:
            llm_result.dashboard = {}

        llm_result.dashboard['multi_factor_score'] = {
            'total': score_result.total_score,
            'technical': score_result.technical_score,
            'fundamental': score_result.fundamental_score,
            'moneyflow': score_result.moneyflow_score,
            'chip': score_result.chip_score,
            'sentiment': score_result.sentiment_score,
            'weights': score_result.weights,
            'strategy': score_result.strategy.value,
            'reliability': score_result.reliability,
            'suggestion': score_result.suggestion,
        }

        # 增强analysis_summary
        if score_result.veto_flags:
            llm_result.risk_warning = f"一票否决: {', '.join(score_result.veto_flags)}; " + \
                                     (llm_result.risk_warning or "")

        return llm_result

    def get_fallback_result(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        当LLM分析失败时，返回基于多因子评分的默认结果

        Returns:
            包含多因子评分的默认结果字典
        """
        score_result = self.calculate_from_context(context)

        if not score_result:
            return None

        code = context.get('code', 'Unknown')
        name = context.get('stock_name', f'股票{code}')

        # 根据总分生成建议
        score = score_result.total_score
        if score >= 80:
            trend = '强烈看多'
            advice = '买入'
        elif score >= 65:
            trend = '看多'
            advice = '增持'
        elif score >= 50:
            trend = '震荡'
            advice = '持有'
        elif score >= 35:
            trend = '看空'
            advice = '减仓'
        else:
            trend = '强烈看空'
            advice = '卖出'

        return {
            'sentiment_score': score,
            'trend_prediction': trend,
            'operation_advice': advice,
            'confidence_level': score_result.reliability,
            'analysis_summary': score_result.suggestion,
            'risk_warning': '; '.join(score_result.veto_flags) if score_result.veto_flags else '无',
            'multi_factor_score': {
                'total': score_result.total_score,
                'technical': score_result.technical_score,
                'fundamental': score_result.fundamental_score,
                'moneyflow': score_result.moneyflow_score,
                'chip': score_result.chip_score,
                'sentiment': score_result.sentiment_score,
            },
            'is_fallback': True,  # 标记为后备结果
        }


# 全局实例（单例模式）
_scoring_integration = None

def get_scoring_integration() -> ScoringIntegration:
    """获取评分系统集成器实例"""
    global _scoring_integration
    if _scoring_integration is None:
        _scoring_integration = ScoringIntegration()
    return _scoring_integration
