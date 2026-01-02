"""
Character data models
"""
from __future__ import annotations
from typing import List, Optional, Dict, Any
from pydantic import BaseModel


class Relationship(BaseModel):
    """Character relationship"""
    targetId: str
    summary: str


class CharacterTimelineItem(BaseModel):
    """Character timeline entry"""
    eventId: str
    role: str  # e.g. "protagonist", "support", "antagonist"


class CharacterState(BaseModel):
    """
    Dynamic character state (computed from effects along a story thread)
    
    This represents "character at a specific point in the story", separate from the
    static Character profile which stores base/initial information.
    """
    characterId: str
    
    # Dynamic attributes that can be modified by effects
    mood: Optional[str] = None  # e.g., "anxious", "confident", "angry"
    status: Optional[str] = None  # e.g., "alive", "injured", "captured"
    location: Optional[str] = None
    
    # Dynamic traits/goals/fears (can add/remove via effects)
    active_traits: List[str] = []
    active_goals: List[str] = []
    active_fears: List[str] = []
    
    # Custom state variables
    vars: Dict[str, Any] = {}  # User-defined state like "trust_level", "secret_known", etc.
    
    # Relationship states at this point
    relationships: Dict[str, Any] = {}  # {target_id: relationship_data}


class Character(BaseModel):
    """Character profile (static/base information)"""
    id: str
    name: str
    alias: Optional[str] = None
    description: str = ""
    traits: List[str] = []  # Base traits
    goals: List[str] = []  # Base goals
    fears: List[str] = []  # Base fears
    relationships: List[Relationship] = []  # Base relationships
    timeline: List[CharacterTimelineItem] = []
