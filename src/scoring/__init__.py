# -*- coding: utf-8 -*-
"""
多维度股票评分系统
==================
整合技术面、基本面、资金面、情绪面、筹码面等多维度评分

参考方案：
- v3.0 最优评分标准
- comprehensive_scorer.py 综合评分系统
- prompt_generator.py Tushare数据获取
"""

from .multi_factor_scorer import MultiFactorScorer, ScoreResult
from .score_dimensions import (
    TechnicalScorer,
    FundamentalScorer,
    MoneyFlowScorer,
    ChipScorer,
    SentimentScorer,
    DimensionScore,
)
from .analyzer_integration import (
    ScoringIntegration,
    get_scoring_integration,
)

__all__ = [
    'MultiFactorScorer',
    'ScoreResult',
    'TechnicalScorer',
    'FundamentalScorer',
    'MoneyFlowScorer',
    'ChipScorer',
    'SentimentScorer',
    'DimensionScore',
    'ScoringIntegration',
    'get_scoring_integration',
]
