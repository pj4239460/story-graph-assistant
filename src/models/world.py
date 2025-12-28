"""
World state and story thread models (v2 expansion)
"""
from __future__ import annotations
from typing import Dict, List, Optional
from pydantic import BaseModel


class WorldEffect(BaseModel):
    """World effect/consequence"""
    key: str
    value: str
    description: Optional[str] = None


class WorldState(BaseModel):
    """World state (v2)"""
    facts: Dict[str, str] = {}
    history: List[str] = []


class ThreadStep(BaseModel):
    """Thread step in a story route"""
    sceneId: str
    choiceId: Optional[str] = None


class StoryThread(BaseModel):
    """Story thread (route/path)"""
    id: str
    name: str
    steps: List[ThreadStep] = []
    description: Optional[str] = None
