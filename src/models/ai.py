"""
AI configuration and token statistics models
"""
from __future__ import annotations
from typing import Dict
from pydantic import BaseModel


class AISettings(BaseModel):
    """AI configuration settings"""
    provider: str = "deepseek"
    modelExtraction: str = "deepseek/deepseek-chat"
    modelOOC: str = "deepseek/deepseek-chat"
    modelWhatIf: str = "deepseek/deepseek-reasoner"
    maxTokensPerCall: int = 2000
    worldSimEnabled: bool = False
    worldSimMaxTokensPerRun: int = 3000
    projectTokenLimit: int = 50000
    dailyTokenSoftLimit: int = 8000


class TokenStats(BaseModel):
    """Token usage statistics"""
    projectUsed: int = 0
    todayUsed: int = 0
    byFeature: Dict[str, int] = {}
    todayDate: str = ""  # "YYYY-MM-DD"
