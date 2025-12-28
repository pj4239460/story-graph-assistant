"""
Character data models
"""
from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel


class Relationship(BaseModel):
    """Character relationship"""
    targetId: str
    summary: str


class CharacterTimelineItem(BaseModel):
    """Character timeline entry"""
    eventId: str
    role: str  # e.g. "protagonist", "support", "antagonist"


class Character(BaseModel):
    """Character profile"""
    id: str
    name: str
    alias: Optional[str] = None
    description: str = ""
    traits: List[str] = []
    goals: List[str] = []
    fears: List[str] = []
    relationships: List[Relationship] = []
    timeline: List[CharacterTimelineItem] = []
