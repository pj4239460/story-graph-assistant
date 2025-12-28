"""
Scene data models
"""
from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel


class Choice(BaseModel):
    """Choice/Branch in the story"""
    id: str
    text: str
    targetSceneId: Optional[str] = None
    conditions: List[str] = []


class Scene(BaseModel):
    """Scene/Node in the story graph"""
    id: str
    title: str
    body: str = ""
    summary: Optional[str] = None
    chapter: Optional[str] = None
    tags: List[str] = []
    participants: List[str] = []  # Character IDs
    choices: List[Choice] = []
    isEnding: bool = False
    endingType: Optional[str] = None
    
    # Timeline related
    timeIndex: Optional[int] = None
    timeLabel: Optional[str] = None
    
    # worldEffects for v2 (future expansion)
    worldEffects: List[dict] = []
