"""
Tests for ordering constraints and fallback storylets (v1.7.1)

Tests:
- Ordering constraint filtering (requires_fired, forbids_fired)
- Fallback storylet selection when regular storylets unavailable
- Idle tick counting and reset logic
"""
import pytest
from src.models.project import Project
from src.models.world import WorldState, Effect, StoryThread, ThreadStep
from src.models.character import Character
from src.models.scene import Scene
from src.models.storylet import (
    Storylet, Precondition, TickHistory, DirectorConfig
)
from src.services.director_service import DirectorService


def test_requires_fired_constraint():
    """Test that storylets with requires_fired only trigger after dependencies"""
    # Setup project
    project = Project(
        id="test-ordering",
        name="Ordering Test",
        worldState=WorldState(vars={"test": 1}),
        characters={
            "char-001": Character(id="char-001", name="Alice")
        },
        scenes={},
        threads={},
        storylets={
            "intro": Storylet(
                id="intro",
                title="Introduction",
                preconditions=[],
                effects=[],
                once=True
            ),
            "chapter2": Storylet(
                id="chapter2",
                title="Chapter 2",
                preconditions=[],
                effects=[],
                requires_fired=["intro"],  # Must fire after intro
                once=True
            )
        }
    )
    
    # Create tick history
    tick_history = TickHistory(thread_id="test")
    
    director = DirectorService()
    
    # Tick 1: Both storylets pass preconditions, but chapter2 blocked by ordering
    candidates = [
        (project.storylets["intro"], []),
        (project.storylets["chapter2"], [])
    ]
    
    filtered = director._filter_by_ordering_constraints(candidates, tick_history)
    
    # Only intro should pass
    assert len(filtered) == 1
    assert filtered[0][0].id == "intro"
    
    # Mark intro as triggered
    tick_history.triggered_once["intro"] = True
    
    # Tick 2: Now chapter2 should pass
    filtered = director._filter_by_ordering_constraints(candidates, tick_history)
    
    # Both should pass now (intro already triggered, chapter2 requirement met)
    filtered_ids = [s.id for s, _ in filtered]
    assert "chapter2" in filtered_ids


def test_forbids_fired_constraint():
    """Test that storylets with forbids_fired don't trigger after forbidden events"""
    project = Project(
        id="test-forbid",
        name="Forbid Test",
        worldState=WorldState(vars={"test": 1}),
        characters={
            "char-001": Character(id="char-001", name="Alice")
        },
        scenes={},
        threads={},
        storylets={
            "peaceful": Storylet(
                id="peaceful",
                title="Peaceful Resolution",
                preconditions=[],
                effects=[],
                once=True
            ),
            "revenge": Storylet(
                id="revenge",
                title="Path of Revenge",
                preconditions=[],
                effects=[],
                forbids_fired=["peaceful"],  # Can't trigger if peaceful path taken
                once=True
            )
        }
    )
    
    tick_history = TickHistory(thread_id="test")
    director = DirectorService()
    
    # Initially both available
    candidates = [
        (project.storylets["peaceful"], []),
        (project.storylets["revenge"], [])
    ]
    
    filtered = director._filter_by_ordering_constraints(candidates, tick_history)
    assert len(filtered) == 2
    
    # Trigger peaceful path
    tick_history.triggered_once["peaceful"] = True
    
    # Now revenge should be blocked
    filtered = director._filter_by_ordering_constraints(candidates, tick_history)
    
    filtered_ids = [s.id for s, _ in filtered]
    assert "peaceful" in filtered_ids
    assert "revenge" not in filtered_ids  # Blocked by forbids_fired


def test_fallback_after_idle_ticks():
    """Test that fallback storylets trigger after N idle ticks"""
    project = Project(
        id="test-fallback",
        name="Fallback Test",
        worldState=WorldState(vars={"available": False}),
        characters={
            "char-001": Character(id="char-001", name="Alice")
        },
        scenes={
            "scene-001": Scene(id="scene-001", title="Test Scene")
        },
        threads={
            "thread-001": StoryThread(
                id="thread-001",
                name="Test Thread",
                steps=[ThreadStep(sceneId="scene-001")]
            )
        },
        storylets={
            "regular": Storylet(
                id="regular",
                title="Regular Event",
                preconditions=[
                    Precondition(path="world.vars.available", op="==", value=True)
                ],
                effects=[]
            ),
            "fallback": Storylet(
                id="fallback",
                title="Something Always Happens",
                preconditions=[],
                effects=[],
                is_fallback=True
            )
        }
    )
    
    director = DirectorService()
    config = DirectorConfig(
        events_per_tick=1,
        fallback_after_idle_ticks=3
    )
    
    # Tick 1: No regular storylets available, idle_tick_count = 0
    tick_record = director.tick(project, "thread-001", 0, config)
    tick_history = project.tick_histories["tick_history_thread-001"]
    
    assert len(tick_record.events) == 0
    assert tick_history.idle_tick_count == 1
    
    # Tick 2: Still no regular storylets
    tick_record = director.tick(project, "thread-001", 0, config)
    assert len(tick_record.events) == 0
    assert tick_history.idle_tick_count == 2
    
    # Tick 3: Still no regular storylets
    tick_record = director.tick(project, "thread-001", 0, config)
    assert len(tick_record.events) == 0
    assert tick_history.idle_tick_count == 3
    
    # Tick 4: After 3 idle ticks, fallback should trigger
    tick_record = director.tick(project, "thread-001", 0, config)
    assert len(tick_record.events) == 1
    assert tick_record.events[0].storylet_id == "fallback"
    # Fallback doesn't reset idle counter
    assert tick_history.idle_tick_count == 4


def test_idle_counter_reset_on_regular_storylet():
    """Test that idle counter resets when regular storylets trigger"""
    project = Project(
        id="test-reset",
        name="Reset Test",
        worldState=WorldState(vars={"available": True}),
        characters={
            "char-001": Character(id="char-001", name="Alice")
        },
        scenes={
            "scene-001": Scene(id="scene-001", title="Test Scene")
        },
        threads={
            "thread-001": StoryThread(
                id="thread-001",
                name="Test Thread",
                steps=[ThreadStep(sceneId="scene-001")]
            )
        },
        storylets={
            "regular": Storylet(
                id="regular",
                title="Regular Event",
                preconditions=[
                    Precondition(path="world.vars.available", op="==", value=True)
                ],
                effects=[
                    Effect(
                        scope="world",
                        target="main",
                        op="set",
                        path="available",
                        value=False
                    )
                ]
            )
        }
    )
    
    director = DirectorService()
    config = DirectorConfig(events_per_tick=1)
    
    # Initialize tick history with idle ticks
    tick_history_key = "tick_history_thread-001"
    if not hasattr(project, 'tick_histories'):
        project.tick_histories = {}
    project.tick_histories[tick_history_key] = TickHistory(thread_id="thread-001")
    project.tick_histories[tick_history_key].idle_tick_count = 5
    
    # Tick: Regular storylet should trigger and reset counter
    tick_record = director.tick(project, "thread-001", 0, config)
    
    assert len(tick_record.events) == 1
    assert tick_record.events[0].storylet_id == "regular"
    
    tick_history = project.tick_histories[tick_history_key]
    assert tick_history.idle_tick_count == 0  # Reset!


def test_complex_ordering_chain():
    """Test a more complex ordering constraint scenario"""
    project = Project(
        id="test-chain",
        name="Chain Test",
        worldState=WorldState(vars={}),
        characters={
            "char-001": Character(id="char-001", name="Alice")
        },
        scenes={},
        threads={},
        storylets={
            "quest_start": Storylet(
                id="quest_start",
                title="Quest Begins",
                preconditions=[],
                effects=[],
                once=True
            ),
            "quest_middle": Storylet(
                id="quest_middle",
                title="Quest Progress",
                preconditions=[],
                effects=[],
                requires_fired=["quest_start"],
                once=True
            ),
            "quest_end": Storylet(
                id="quest_end",
                title="Quest Complete",
                preconditions=[],
                effects=[],
                requires_fired=["quest_start", "quest_middle"],
                once=True
            ),
            "quest_alternative": Storylet(
                id="quest_alternative",
                title="Alternative Path",
                preconditions=[],
                effects=[],
                requires_fired=["quest_start"],
                forbids_fired=["quest_middle"],  # Alternative to middle
                once=True
            )
        }
    )
    
    tick_history = TickHistory(thread_id="test")
    director = DirectorService()
    
    candidates = [
        (project.storylets["quest_start"], []),
        (project.storylets["quest_middle"], []),
        (project.storylets["quest_end"], []),
        (project.storylets["quest_alternative"], [])
    ]
    
    # Stage 1: Only quest_start available
    filtered = director._filter_by_ordering_constraints(candidates, tick_history)
    assert len(filtered) == 1
    assert filtered[0][0].id == "quest_start"
    
    # Trigger quest_start
    tick_history.triggered_once["quest_start"] = True
    
    # Stage 2: quest_middle and quest_alternative available, not quest_end
    filtered = director._filter_by_ordering_constraints(candidates, tick_history)
    filtered_ids = [s.id for s, _ in filtered]
    assert "quest_middle" in filtered_ids
    assert "quest_alternative" in filtered_ids
    assert "quest_end" not in filtered_ids  # Requires both start AND middle
    
    # Trigger quest_middle
    tick_history.triggered_once["quest_middle"] = True
    
    # Stage 3: quest_end available, quest_alternative blocked
    filtered = director._filter_by_ordering_constraints(candidates, tick_history)
    filtered_ids = [s.id for s, _ in filtered]
    assert "quest_end" in filtered_ids
    assert "quest_alternative" not in filtered_ids  # Forbidden by quest_middle


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
