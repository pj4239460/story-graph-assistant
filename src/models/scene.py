"""
Scene data models
"""
from __future__ import annotations
from typing import List, Optional, TYPE_CHECKING
from pydantic import BaseModel, field_validator

if TYPE_CHECKING:
    from .world import Effect


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
    
    # State effects (v2) - structured effects using Effect model
    effects: List['Effect'] = []  # Forward reference to Effect from world.py
    
    # Legacy worldEffects (deprecated but kept for backward compatibility)
    worldEffects: List[dict] = []
    
    @field_validator('effects', mode='before')
    @classmethod
    def migrate_world_effects(cls, v, info):
        """Migrate old worldEffects to new effects structure on load"""
        # If effects is empty but worldEffects exists, try to migrate
        if not v and info.data.get('worldEffects'):
            from ..models.world import Effect
            migrated = []
            for old_effect in info.data['worldEffects']:
                # Try to convert dict worldEffects to Effect objects
                if isinstance(old_effect, dict):
                    # Simple migration heuristic
                    try:
                        effect = Effect(
                            scope="world",
                            target="world",
                            op="set",
                            path=f"vars.{old_effect.get('key', 'unknown')}",
                            value=old_effect.get('value', ''),
                            reason=old_effect.get('description')
                        )
                        migrated.append(effect)
                    except:
                        pass  # Skip invalid entries
            return migrated
        return v or []
