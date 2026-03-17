# -*- coding: utf-8 -*-
"""
评分维度 - 各维度独立评分器
==============================

维度说明：
- T (Technical): 技术面评分，权重最高
- F (Fundamental): 基本面评分
- M (MoneyFlow): 资金面评分
- C (Chip): 筹码面评分
- S (Sentiment): 情绪面评分

每个维度返回：
- score: 标准化分数 (-10 到 +10)
- weight: 建议权重
- confidence: 数据置信度 (0-1)
- details: 评分详情
"""

import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class DimensionScore:
    """维度评分结果"""
    score: float  # -10 到 +10
    weight: float  # 建议权重
    confidence: float  # 0-1
    details: List[str]  # 评分详情
    raw_data: Dict[str, Any]  # 原始数据


class TechnicalScorer:
    """
    技术面评分 (T)
    ==============
    核心维度，数据通常最完整

    评分要素：
    1. 趋势分 (±4): MA排列、趋势强度
    2. 乖离分 (±3): 价格与均线偏离
    3. 动量分 (±3): MACD、KDJ、RSI
    """

    def calculate(self, data: Dict[str, Any]) -> DimensionScore:
        """计算技术面评分"""
        score = 0.0
        details = []
        confidence = 0.0
        has_data = False

        # 1. 趋势评分 (±4)
        trend_score = self._score_trend(data)
        score += trend_score
        if trend_score != 0:
            has_data = True
            confidence += 0.3

        # 2. 乖离评分 (±3)
        bias_score = self._score_bias(data)
        score += bias_score
        if bias_score != 0:
            has_data = True
            confidence += 0.25

        # 3. 动量评分 (±3)
        momentum_score = self._score_momentum(data)
        score += momentum_score
        if momentum_score != 0:
            has_data = True
            confidence += 0.25

        # 4. 技术形态 (±2)
        pattern_score = self._score_pattern(data)
        score += pattern_score
        if pattern_score != 0:
            has_data = True
            confidence += 0.2

        # 标准化到 ±10
        score = max(-10, min(10, score))

        return DimensionScore(
            score=round(score, 2),
            weight=5.0,  # 技术面权重最高
            confidence=min(1.0, confidence),
            details=details,
            raw_data=data
        )

    def _score_trend(self, data: Dict) -> float:
        """趋势评分 (±4)"""
        ma5 = data.get('ma5')
        ma10 = data.get('ma10')
        ma20 = data.get('ma20')
        ma60 = data.get('ma60')

        if ma5 is None or ma10 is None or ma20 is None:
            return 0.0

        score = 0.0

        # 完美多头: MA5>MA10>MA20>MA60
        if ma5 > ma10 > ma20:
            if ma60 and ma20 > ma60:
                score = 4.0  # 完美多头
            else:
                score = 3.0  # 短期多头
        # 混合多头: MA5>MA20
        elif ma5 > ma20:
            score = 1.5
        # 震荡
        elif abs(ma5 - ma20) / ma20 < 0.02:
            score = 0.0
        # 混合空头: MA5<MA20
        elif ma5 < ma20:
            score = -1.5
        # 完美空头
        if ma5 < ma10 < ma20:
            if ma60 and ma20 < ma60:
                score = -4.0
            else:
                score = -3.0

        return score

    def _score_bias(self, data: Dict) -> float:
        """乖离评分 (±3)"""
        bias = data.get('bias_ma5')
        if bias is None:
            return 0.0

        # 乖离率评分
        if 0 < bias < 2:
            return 3.0  # 最佳买入区间
        elif -5 < bias <= 0:
            return 2.0  # 良好
        elif 2 <= bias < 5:
            return 1.0  # 偏高
        elif bias >= 5:
            return -1.5  # 过高，不追高
        elif -10 < bias <= -5:
            return -1.0  # 偏低
        elif bias <= -10:
            return -2.5  # 严重超跌

        return 0.0

    def _score_momentum(self, data: Dict) -> float:
        """动量评分 (±3)"""
        score = 0.0

        # MACD
        macd = data.get('macd')
        macd_signal = data.get('macd_signal')
        if macd is not None and macd_signal is not None:
            if macd > macd_signal and macd > 0:
                score += 1.5
            elif macd < macd_signal and macd < 0:
                score -= 1.5

        # RSI
        rsi = data.get('rsi6')
        if rsi is not None:
            if rsi > 70:
                score -= 0.5  # 超买
            elif rsi < 30:
                score += 0.5  # 超卖

        # KDJ
        k = data.get('kdj_k')
        d = data.get('kdj_d')
        if k is not None and d is not None:
            if k > d and k < 80:
                score += 1.0
            elif k < d and k > 20:
                score -= 1.0

        return max(-3, min(3, score))

    def _score_pattern(self, data: Dict) -> float:
        """技术形态评分 (±2)"""
        score = 0.0

        # 九转信号
        nine_up = data.get('nine_up_turn')
        nine_down = data.get('nine_down_turn')
        if nine_up:
            score -= 1.0  # 九转上转，可能调整
        if nine_down:
            score += 1.0  # 九转下转，可能反弹

        # 布林带
        boll_upper = data.get('boll_upper')
        boll_lower = data.get('boll_lower')
        close = data.get('close')
        if all([boll_upper, boll_lower, close]):
            if close > boll_upper:
                score -= 0.5  # 突破上轨
            elif close < boll_lower:
                score += 0.5  # 跌破下轨

        return max(-2, min(2, score))


class FundamentalScorer:
    """
    基本面评分 (F)
    ==============
    估值 + 盈利 + 成长 + 财务健康

    评分要素：
    1. 估值分 (±3): PE、PB分位
    2. 盈利分 (±3): ROE、净利率
    3. 成长分 (±2): 营收、利润增长
    4. 健康分 (±2): 负债率、现金流
    """

    def calculate(self, data: Dict[str, Any]) -> DimensionScore:
        """计算基本面评分"""
        score = 0.0
        details = []
        confidence = 0.0

        # 1. 估值评分 (±3)
        pe_score = self._score_pe_pb(data)
        score += pe_score
        if pe_score != 0:
            confidence += 0.3

        # 2. 盈利评分 (±3)
        profit_score = self._score_profitability(data)
        score += profit_score
        if profit_score != 0:
            confidence += 0.3

        # 3. 成长评分 (±2)
        growth_score = self._score_growth(data)
        score += growth_score
        if growth_score != 0:
            confidence += 0.2

        # 4. 财务健康 (±2)
        health_score = self._score_financial_health(data)
        score += health_score
        if health_score != 0:
            confidence += 0.2

        score = max(-10, min(10, score))

        return DimensionScore(
            score=round(score, 2),
            weight=2.0,
            confidence=min(1.0, confidence),
            details=details,
            raw_data=data
        )

    def _score_pe_pb(self, data: Dict) -> float:
        """估值评分 (±3)"""
        pe = data.get('pe_ttm')
        pb = data.get('pb')

        if pe is None and pb is None:
            return 0.0

        score = 0.0

        # PE评分
        if pe is not None:
            if pe < 0:
                score -= 2.0  # 亏损
            elif pe < 15:
                score += 2.0  # 极度低估
            elif pe < 25:
                score += 1.0  # 低估
            elif pe < 40:
                score += 0.0  # 合理
            elif pe < 60:
                score -= 1.0  # 偏高
            else:
                score -= 2.0  # 极高

        # PB评分 (辅助)
        if pb is not None and pb > 0:
            if pb < 1.5:
                score += 0.5
            elif pb > 5:
                score -= 0.5

        return max(-3, min(3, score))

    def _score_profitability(self, data: Dict) -> float:
        """盈利评分 (±3)"""
        roe = data.get('roe')
        net_margin = data.get('netprofit_margin')

        if roe is None and net_margin is None:
            return 0.0

        score = 0.0

        if roe is not None:
            if roe > 20:
                score += 2.0
            elif roe > 15:
                score += 1.5
            elif roe > 10:
                score += 0.5
            elif roe < 0:
                score -= 2.0
            elif roe < 5:
                score -= 1.0

        if net_margin is not None:
            if net_margin > 30:
                score += 1.0
            elif net_margin < 0:
                score -= 1.0

        return max(-3, min(3, score))

    def _score_growth(self, data: Dict) -> float:
        """成长评分 (±2)"""
        revenue_yoy = data.get('op_yoy')
        profit_yoy = data.get('netprofit_yoy')

        if revenue_yoy is None and profit_yoy is None:
            return 0.0

        score = 0.0

        # 营收增长
        if revenue_yoy is not None:
            if revenue_yoy > 50:
                score += 1.0
            elif revenue_yoy > 20:
                score += 0.5
            elif revenue_yoy < -20:
                score -= 0.5

        # 利润增长
        if profit_yoy is not None:
            if profit_yoy > 100:
                score += 1.5
            elif profit_yoy > 50:
                score += 1.0
            elif profit_yoy > 20:
                score += 0.5
            elif profit_yoy < 0:
                score -= 1.0

        return max(-2, min(2, score))

    def _score_financial_health(self, data: Dict) -> float:
        """财务健康评分 (±2)"""
        debt_ratio = data.get('debt_to_assets')

        if debt_ratio is None:
            return 0.0

        score = 0.0

        if debt_ratio > 80:
            score -= 1.5  # 高负债
        elif debt_ratio > 60:
            score -= 0.5
        elif debt_ratio < 30:
            score += 0.5  # 低负债，财务稳健

        return max(-2, min(2, score))


class MoneyFlowScorer:
    """
    资金面评分 (M)
    ==============
    主力资金流向 + 成交量分析

    评分要素：
    1. 主力净流入 (±4)
    2. 成交量配合 (±3)
    3. 资金持续性 (±3)
    """

    def calculate(self, data: Dict[str, Any]) -> DimensionScore:
        """计算资金面评分"""
        score = 0.0
        details = []
        confidence = 0.0

        # 1. 主力净流入评分 (±4)
        main_score = self._score_main_moneyflow(data)
        score += main_score
        if main_score != 0:
            confidence += 0.4

        # 2. 成交量评分 (±3)
        vol_score = self._score_volume(data)
        score += vol_score
        if vol_score != 0:
            confidence += 0.3

        # 3. 大单动向 (±3)
        big_order_score = self._score_big_order(data)
        score += big_order_score
        if big_order_score != 0:
            confidence += 0.3

        score = max(-10, min(10, score))

        return DimensionScore(
            score=round(score, 2),
            weight=1.5,
            confidence=min(1.0, confidence),
            details=details,
            raw_data=data
        )

    def _score_main_moneyflow(self, data: Dict) -> float:
        """主力净流入评分 (±4)"""
        main_net = data.get('main_net_amount')
        total_mv = data.get('total_mv')

        if main_net is None:
            return 0.0

        # 标准化到亿元
        main_yi = main_net / 10000 if main_net else 0

        # 考虑市值占比
        if total_mv and total_mv > 0:
            ratio = main_net / total_mv * 100
        else:
            ratio = 0

        if main_yi > 1 or ratio > 0.5:
            return 4.0
        elif main_yi > 0.5 or ratio > 0.3:
            return 2.0
        elif main_yi > 0:
            return 0.5
        elif main_yi > -0.5:
            return -0.5
        elif main_yi > -1:
            return -2.0
        else:
            return -4.0

    def _score_volume(self, data: Dict) -> float:
        """成交量评分 (±3)"""
        vol_ratio = data.get('volume_ratio')

        if vol_ratio is None:
            return 0.0

        # 量比评分
        if vol_ratio > 3:
            return 3.0  # 放量
        elif vol_ratio > 2:
            return 2.0
        elif vol_ratio > 1.5:
            return 1.0
        elif vol_ratio > 0.8:
            return 0.0  # 正常
        elif vol_ratio > 0.5:
            return -1.0  # 缩量
        else:
            return -2.0  # 严重缩量

    def _score_big_order(self, data: Dict) -> float:
        """大单评分 (±3)"""
        big_buy = data.get('buy_lg_vol')
        big_sell = data.get('sell_lg_vol')

        if big_buy is None or big_sell is None:
            return 0.0

        total = big_buy + big_sell
        if total == 0:
            return 0.0

        ratio = (big_buy - big_sell) / total

        if ratio > 0.3:
            return 3.0
        elif ratio > 0.1:
            return 1.5
        elif ratio > -0.1:
            return 0.0
        elif ratio > -0.3:
            return -1.5
        else:
            return -3.0


class ChipScorer:
    """
    筹码面评分 (C)
    ==============
    筹码分布 + 获利比例 + 集中度

    评分要素：
    1. 获利比例 (±4)
    2. 筹码集中度 (±3)
    3. 成本与现价关系 (±3)
    """

    def calculate(self, data: Dict[str, Any]) -> DimensionScore:
        """计算筹码面评分"""
        score = 0.0
        details = []
        confidence = 0.0

        # 1. 获利比例评分 (±4)
        profit_score = self._score_profit_ratio(data)
        score += profit_score
        if profit_score != 0:
            confidence += 0.4

        # 2. 筹码集中度评分 (±3)
        conc_score = self._score_concentration(data)
        score += conc_score
        if conc_score != 0:
            confidence += 0.3

        # 3. 成本与现价关系 (±3)
        cost_score = self._score_cost_position(data)
        score += cost_score
        if cost_score != 0:
            confidence += 0.3

        score = max(-10, min(10, score))

        return DimensionScore(
            score=round(score, 2),
            weight=1.5,
            confidence=min(1.0, confidence),
            details=details,
            raw_data=data
        )

    def _score_profit_ratio(self, data: Dict) -> float:
        """获利比例评分 (±4)"""
        profit_ratio = data.get('profit_ratio')

        if profit_ratio is None:
            return 0.0

        # 转换为小数
        if profit_ratio > 1:
            profit_ratio = profit_ratio / 100

        if profit_ratio >= 0.9:
            return -2.0  # 获利盘极高，风险大
        elif profit_ratio >= 0.7:
            return 1.0
        elif profit_ratio >= 0.5:
            return 2.0
        elif profit_ratio >= 0.3:
            return 3.0
        elif profit_ratio >= 0.1:
            return 1.5
        else:
            return -4.0  # 几乎无人获利，严重套牢

    def _score_concentration(self, data: Dict) -> float:
        """筹码集中度评分 (±3)"""
        conc_90 = data.get('concentration_90')

        if conc_90 is None:
            return 0.0

        # 转换为小数
        if conc_90 > 1:
            conc_90 = conc_90 / 100

        # 集中度越低越好
        if conc_90 < 0.08:
            return 3.0  # 高度集中
        elif conc_90 < 0.15:
            return 2.0  # 较集中
        elif conc_90 < 0.25:
            return 0.0  # 一般
        else:
            return -2.0  # 分散

    def _score_cost_position(self, data: Dict) -> float:
        """成本与现价关系评分 (±3)"""
        avg_cost = data.get('avg_cost')
        close = data.get('close')

        if avg_cost is None or close is None or avg_cost == 0:
            return 0.0

        diff = (close - avg_cost) / avg_cost * 100

        if diff > 20:
            return -2.0  # 远高于成本，追高风险
        elif diff > 10:
            return -1.0
        elif diff > 5:
            return 0.5
        elif diff > -5:
            return 2.0  # 在成本附近，最佳
        elif diff > -10:
            return 1.0
        else:
            return -1.0  # 远低于成本，弱势


class SentimentScorer:
    """
    情绪面评分 (S)
    ==============
    新闻情绪 + 市场热度 + 分析师评级

    评分要素：
    1. 新闻情绪 (±3)
    2. 市场热度 (±3)
    3. 分析师评级 (±4)
    """

    def calculate(self, data: Dict[str, Any]) -> DimensionScore:
        """计算情绪面评分"""
        score = 0.0
        details = []
        confidence = 0.0

        # 1. 新闻情绪 (±3)
        news_score = self._score_news_sentiment(data)
        score += news_score
        if news_score != 0:
            confidence += 0.3

        # 2. 市场热度 (±3)
        heat_score = self._score_market_heat(data)
        score += heat_score
        if heat_score != 0:
            confidence += 0.3

        # 3. 分析师评级 (±4)
        rating_score = self._score_analyst_rating(data)
        score += rating_score
        if rating_score != 0:
            confidence += 0.4

        score = max(-10, min(10, score))

        return DimensionScore(
            score=round(score, 2),
            weight=1.0,
            confidence=min(1.0, confidence),
            details=details,
            raw_data=data
        )

    def _score_news_sentiment(self, data: Dict) -> float:
        """新闻情绪评分 (±3)"""
        sentiment = data.get('news_sentiment')

        if sentiment is None:
            return 0.0

        if sentiment == 'positive':
            return 2.0
        elif sentiment == 'negative':
            return -2.0
        else:
            return 0.0

    def _score_market_heat(self, data: Dict) -> float:
        """市场热度评分 (±3)"""
        heat = data.get('market_heat')

        if heat is None:
            return 0.0

        if heat > 80:
            return 3.0
        elif heat > 60:
            return 1.5
        elif heat > 40:
            return 0.0
        elif heat > 20:
            return -1.0
        else:
            return -2.0

    def _score_analyst_rating(self, data: Dict) -> float:
        """分析师评级评分 (±4)"""
        rating = data.get('analyst_rating')

        if rating is None:
            return 0.0

        rating_map = {
            '强烈买入': 4.0,
            '买入': 3.0,
            '增持': 2.0,
            '中性': 0.0,
            '减持': -2.0,
            '卖出': -3.0,
            '强烈卖出': -4.0,
        }

        return rating_map.get(rating, 0.0)
