"""
Storylet and World Director models

This module defines the core data structures for the World Director system, which uses
Quality-Based Narrative (QBN) patterns to evolve the story world automatically.

The World Director observes the current story state and selects appropriate storylets
to trigger based on preconditions, pacing requirements, and diversity preferences.
This creates emergent, replayable narratives that feel dynamic and responsive.
"""
from __future__ import annotations
from typing import List, Dict, Any, Optional, Literal
from pydantic import BaseModel, Field
from datetime import datetime


class Precondition(BaseModel):
    """
    A condition that must be satisfied for a storylet to trigger.
    
    Preconditions use dot-notation paths to access world state, character state,
    or relationship state. They support various comparison operators for flexible
    condition checking.
    
    Examples:
        - World variable: path="world.vars.faction_a_power", op=">=", value=60
        - Character mood: path="characters.char-001.mood", op="==", value="angry"
        - Relationship trust: path="relationships.alice|bob.trust", op=">", value=50
        - Tag checking: path="characters.char-001.active_traits", op="contains", value="brave"
    """
    path: str  # Dot-notation path to state value
    op: Literal["==", "!=", "<", "<=", ">", ">=", "in", "contains", "has_tag"]
    value: Any  # Value to compare against
    
    def __str__(self) -> str:
        return f"{self.path} {self.op} {self.value}"


class Storylet(BaseModel):
    """
    A storylet is a reusable narrative unit that triggers when conditions are met.
    
    Storylets are the core building blocks of the World Director system. Each storylet
    represents a potential event that can occur in your story world. When its preconditions
    are satisfied, the Director may choose to trigger it based on weighting, cooldowns,
    and pacing considerations.
    
    Design Pattern:
        This follows Quality-Based Narrative (QBN) patterns from interactive fiction,
        popularized by games like Fallen London and 80 Days. The key insight is that
        stories can emerge from a pool of conditional narrative fragments rather than
        being manually authored as branching trees.
    
    References:
        - Emily Short's storylet work: https://emshort.blog/2019/11/29/storylets-you-want-them/
        - QBN in Failbetter Games: https://www.failbettergames.com/news/
    
    Attributes:
        id: Unique identifier for this storylet
        title: Human-readable title shown in the UI
        description: Optional longer description of what this represents
        tags: Categories for diversity tracking (e.g., ["economic", "conflict"])
        preconditions: List of conditions that must ALL be true to trigger
        effects: List of state changes to apply when triggered
        weight: Base probability weight (higher = more likely to be selected)
        cooldown: Minimum number of ticks before this can trigger again
        once: If True, can only trigger once per playthrough
        intensity_delta: How this affects story intensity (-1.0 calming to +1.0 escalating)
    """
    id: str
    title: str
    description: str = ""
    tags: List[str] = Field(default_factory=list)
    
    # Triggering conditions (ALL must be satisfied)
    preconditions: List[Precondition] = Field(default_factory=list)
    
    # State changes to apply when triggered (uses existing Effect model)
    effects: List['Effect'] = Field(default_factory=list)
    
    # Director policy parameters
    weight: float = 1.0  # Base selection probability (can use 0.1-10.0 range)
    cooldown: int = 0  # Number of ticks before can trigger again (0 = no cooldown)
    once: bool = False  # If True, can only trigger once per thread
    
    # Pacing control: affects story intensity for peaks-and-valleys pacing
    intensity_delta: float = 0.0  # -1.0 (calming) to +1.0 (escalating)
    
    class Config:
        arbitrary_types_allowed = True


class TickEvent(BaseModel):
    """
    Record of a storylet being triggered during a tick.
    
    Each time a storylet is selected and executed, a TickEvent is created to
    document what happened. This enables full replay and analysis of how the
    story world evolved over time.
    
    Attributes:
        storylet_id: Which storylet was triggered
        storylet_title: Human-readable title for UI display
        tick_number: When this occurred (0-indexed)
        timestamp: ISO format timestamp of when this was created
        satisfied_conditions: Which preconditions were met (for explanation)
        applied_effects: What state changes occurred
        rationale: Why the Director chose this storylet
    """
    storylet_id: str
    storylet_title: str
    tick_number: int
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    
    # What conditions were satisfied (for explainability)
    satisfied_conditions: List[str] = Field(default_factory=list)
    
    # What effects were applied (serialized Effect objects)
    applied_effects: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Rationale for why this was selected (human-readable explanation)
    rationale: str = ""


class TickHistory(BaseModel):
    """
    Complete history of all world ticks for a story thread.
    
    The TickHistory tracks everything that happens during world evolution:
    - A chronological list of all ticks (TickRecords)
    - Cooldown state for each storylet
    - "Once" flag state (which storylets have already triggered)
    - Current intensity level for pacing
    
    This enables:
    - Full replay of world evolution
    - Debugging ("why did this happen?")
    - Analytics (which storylets trigger most often?)
    - Save/load (persist the entire evolution history)
    
    Attributes:
        thread_id: Which story thread this belongs to
        ticks: Chronological list of all ticks that have occurred
        last_triggered: Maps storylet_id to the tick when it last triggered
        triggered_once: Maps storylet_id to True if it has already triggered
        current_intensity: Current story intensity (0.0=calm, 1.0=intense)
    """
    thread_id: str
    ticks: List['TickRecord'] = Field(default_factory=list)
    
    # Cooldown tracking: storylet_id -> tick_number when it was last triggered
    last_triggered: Dict[str, int] = Field(default_factory=dict)
    
    # Once tracking: storylet_id -> True if already triggered
    triggered_once: Dict[str, bool] = Field(default_factory=dict)
    
    # Current intensity level for pacing (0.0 = calm, 1.0 = intense)
    current_intensity: float = 0.5


class TickRecord(BaseModel):
    """
    A snapshot of a single world evolution tick.
    
    Each tick represents a moment when the Director evaluated the world state
    and selected storylets to trigger. The TickRecord captures:
    - When and where (in the story) this happened
    - What the intensity was before/after
    - Which storylets were triggered
    - What state changes occurred
    
    This granular recording enables the "replayable and explainable" design goal.
    
    Attributes:
        tick_number: Sequential tick number (0-indexed)
        timestamp: When this tick was executed
        step_index: Which step in the story thread this corresponds to
        intensity_before: Story intensity before this tick
        intensity_after: Story intensity after applying all effects
        events: List of storylets that were triggered
        state_diff: Human-readable before/after state comparison
    """
    tick_number: int
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    
    # Context at this tick
    step_index: int  # Where in the story thread this tick occurred
    intensity_before: float
    intensity_after: float
    
    # Events that occurred (selected storylets)
    events: List[TickEvent] = Field(default_factory=list)
    
    # State changes in human-readable diff format
    # Example: {"world": {"vars": {"faction_a_power": "50 → 70"}}, "characters": {...}}
    state_diff: Dict[str, Any] = Field(default_factory=dict)


class DirectorConfig(BaseModel):
    """
    Configuration parameters for the World Director's behavior.
    
    These parameters control how the Director selects storylets:
    
    - Events per tick: How many storylets to trigger each time
    - Diversity: Prevents the same tags from repeating too often
    - Intensity: Creates "peaks and valleys" pacing like Left 4 Dead's AI Director
    - Pacing preference: Bias toward calm, balanced, or intense stories
    
    You can tune these parameters to achieve different narrative feels:
    - High diversity_penalty = more variety, less repetition
    - Low intensity_decay = longer intense/calm periods
    - "calm" pacing = favors low-intensity storylets
    - "intense" pacing = favors high-intensity storylets
    
    Attributes:
        events_per_tick: How many storylets to select (1-5)
        diversity_window: How many recent ticks to check for tag repetition
        diversity_penalty: Weight reduction for recently-used tags (0.0-1.0)
        intensity_min: Minimum intensity threshold (0.0-1.0)
        intensity_max: Maximum intensity threshold (0.0-1.0)
        intensity_decay: How much intensity decays per tick toward 0.5 (0.0-0.5)
        pacing_preference: Overall story pacing bias
    """
    # How many storylets to trigger per tick
    events_per_tick: int = Field(default=2, ge=1, le=5)
    
    # Diversity: penalize recently used tags to avoid repetition
    diversity_window: int = Field(default=5, ge=0, le=20)  # Look back N ticks
    diversity_penalty: float = Field(default=0.5, ge=0.0, le=1.0)  # Weight reduction
    
    # Pacing: intensity bounds and decay (peaks-and-valleys pattern)
    intensity_min: float = Field(default=0.2, ge=0.0, le=1.0)
    intensity_max: float = Field(default=0.8, ge=0.0, le=1.0)
    intensity_decay: float = Field(default=0.1, ge=0.0, le=0.5)  # Pull toward 0.5
    
    # Pacing preference: affects storylet selection weighting
    pacing_preference: Literal["balanced", "calm", "intense"] = "balanced"


# Forward references resolution
from .world import Effect
Storylet.model_rebuild()
