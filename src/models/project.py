"""
Project data model
"""
from __future__ import annotations
from typing import Dict, List, TYPE_CHECKING
from pydantic import BaseModel, Field
from datetime import datetime

from .scene import Scene
from .character import Character
from .event import Event
from .world import WorldState, StoryThread
from .ai import AISettings, TokenStats

if TYPE_CHECKING:
    from .storylet import Storylet, TickHistory


class Project(BaseModel):
    """Project/Workspace model"""
    id: str
    name: str
    locale: str = "zh"
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)
    
    aiSettings: AISettings = Field(default_factory=AISettings)
    tokenStats: TokenStats = Field(default_factory=TokenStats)
    
    scenes: Dict[str, Scene] = Field(default_factory=dict)
    characters: Dict[str, Character] = Field(default_factory=dict)
    events: Dict[str, Event] = Field(default_factory=dict)
    worldState: WorldState = Field(default_factory=WorldState)
    threads: Dict[str, StoryThread] = Field(default_factory=dict)
    
    # World Director extensions
    storylets: Dict[str, 'Storylet'] = Field(default_factory=dict)
    tick_histories: Dict[str, 'TickHistory'] = Field(default_factory=dict)
