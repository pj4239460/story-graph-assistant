"""
World state and story thread models (v2 expansion)
"""
from __future__ import annotations
from typing import Dict, List, Optional, Any, Literal
from pydantic import BaseModel, Field
from datetime import datetime


class WorldFact(BaseModel):
    """World fact/lore entry"""
    id: str
    content: str
    category: Optional[str] = None  # e.g., "setting", "rule", "history", "character"
    sourceSceneId: Optional[str] = None
    createdAt: datetime = Field(default_factory=datetime.utcnow)


class Effect(BaseModel):
    """
    Effect: A change/patch applied to world/character/relationship state
    
    Examples:
    - Character mood change: Effect(scope="character", target="alice", op="set", path="state.mood", value="anxious")
    - Relationship trust: Effect(scope="relationship", target="alice|bob", op="add", path="trust", value=10)
    - World flag: Effect(scope="world", target="world", op="set", path="vars.rumor_spread", value=True)
    - Character trait gain: Effect(scope="character", target="alice", op="add", path="traits", value="paranoid")
    """
    scope: Literal["character", "relationship", "world"]
    target: str  # character_id / "char_a|char_b" / "world"
    op: Literal["set", "add", "remove", "merge"]  # set: replace, add: append/increment, remove: delete, merge: deep merge
    path: str  # dot-notation path like "state.mood" or "relations.trust" or "vars.flag"
    value: Any
    reason: Optional[str] = None  # Human-readable explanation
    sourceSceneId: Optional[str] = None  # Which scene triggered this effect


class WorldEffect(BaseModel):
    """World effect/consequence (legacy compatibility - deprecated, use Effect instead)"""
    key: str
    value: str
    description: Optional[str] = None


class WorldState(BaseModel):
    """
    World state (v2) - Central repository for story worldview
    
    Facts: Structured worldview facts and lore
    Vars: Dynamic world variables (flags, counters, etc.)
    Relations: Global relationship data (future: will be superseded by character state)
    """
    facts: Dict[str, WorldFact] = Field(default_factory=dict)  # {fact_id: WorldFact}
    vars: Dict[str, Any] = Field(default_factory=dict)  # Custom variables
    relations: Dict[str, Any] = Field(default_factory=dict)  # Relationship state (placeholder)


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
