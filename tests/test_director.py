"""
Tests for DirectorService

Validates storylet selection, tick execution, and state changes.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import random
from src.services.director_service import DirectorService
from src.models.project import Project
from src.models.storylet import Storylet, Precondition, DirectorConfig, TickHistory
from src.models.world import WorldState, Effect, StoryThread, ThreadStep
from src.models.character import CharacterState, Character
from src.models.scene import Scene


def create_test_project():
    """Create a minimal test project"""
    project = Project(
        id="test-001",
        name="Test Project",
        locale="en"
    )
    
    # Add a simple scene
    project.scenes["scene-001"] = Scene(
        id="scene-001",
        title="Test Scene",
        body="Test content"
    )
    
    # Add test characters
    project.characters["char-001"] = Character(
        id="char-001",
        name="Alice",
        description="Test character"
    )
    
    # Initialize world state
    project.worldState = WorldState(
        vars={
            "faction_a_power": 50,
            "faction_b_power": 40,
            "market_peace": 60
        }
    )
    
    # Add a test thread
    project.threads["thread-001"] = StoryThread(
        id="thread-001",
        name="Test Thread",
        steps=[
            ThreadStep(sceneId="scene-001", choiceId=None)
        ]
    )
    
    return project


def test_storylet_loading():
    """Test loading storylets from project"""
    director = DirectorService()
    project = create_test_project()
    
    # Add storylets
    project.storylets = {
        "st-001": Storylet(
            id="st-001",
            title="Test Event",
            tags=["test"],
            effects=[]
        )
    }
    
    storylets = director.load_storylets(project)
    assert len(storylets) == 1
    assert storylets[0].id == "st-001"
    
    print("Storylet loading test passed")


def test_precondition_filtering():
    """Test storylet filtering by preconditions"""
    director = DirectorService()
    project = create_test_project()
    
    # Create storylets with different preconditions
    storylets = [
        Storylet(
            id="st-high-power",
            title="High Power Event",
            tags=["power"],
            preconditions=[
                Precondition(path="world.vars.faction_a_power", op=">=", value=60)
            ],
            effects=[]
        ),
        Storylet(
            id="st-low-power",
            title="Low Power Event",
            tags=["power"],
            preconditions=[
                Precondition(path="world.vars.faction_a_power", op="<", value=60)
            ],
            effects=[]
        ),
        Storylet(
            id="st-peaceful",
            title="Peaceful Event",
            tags=["peace"],
            preconditions=[
                Precondition(path="world.vars.market_peace", op=">=", value=50)
            ],
            effects=[]
        )
    ]
    
    # Setup state
    world_state = project.worldState
    char_states = {"char-001": CharacterState(characterId="char-001")}
    rel_states = {}
    tick_history = TickHistory(thread_id="thread-001")
    config = DirectorConfig(events_per_tick=5)  # Maximum allowed, select all that match
    
    # faction_a_power is 50, so only st-low-power and st-peaceful should match
    selected, rationales = director.select_storylets(
        storylets, world_state, char_states, rel_states, tick_history, config
    )
    
    selected_ids = [s.id for s in selected]
    assert "st-low-power" in selected_ids, f"Expected st-low-power, got {selected_ids}"
    assert "st-peaceful" in selected_ids, f"Expected st-peaceful, got {selected_ids}"
    assert "st-high-power" not in selected_ids, f"st-high-power should not be selected"
    
    print("Precondition filtering test passed")


def test_cooldown_enforcement():
    """Test that cooldown prevents immediate re-triggering"""
    director = DirectorService()
    project = create_test_project()
    
    storylet = Storylet(
        id="st-cooldown",
        title="Cooldown Test",
        tags=["test"],
        cooldown=3,
        effects=[]
    )
    
    world_state = project.worldState
    char_states = {"char-001": CharacterState(characterId="char-001")}
    rel_states = {}
    tick_history = TickHistory(thread_id="thread-001")
    config = DirectorConfig()
    
    # First selection - should work
    selected, _ = director.select_storylets(
        [storylet], world_state, char_states, rel_states, tick_history, config
    )
    assert len(selected) == 1
    
    # Mark as triggered at tick 0
    tick_history.last_triggered["st-cooldown"] = 0
    tick_history.ticks = [None] * 1  # 1 tick has passed
    
    # Try again at tick 1 - should be blocked (cooldown=3 means need to wait 3 ticks)
    selected, _ = director.select_storylets(
        [storylet], world_state, char_states, rel_states, tick_history, config
    )
    assert len(selected) == 0, "Cooldown should block re-selection"
    
    # Try at tick 3 - should work again
    tick_history.ticks = [None] * 3
    selected, _ = director.select_storylets(
        [storylet], world_state, char_states, rel_states, tick_history, config
    )
    assert len(selected) == 1, "After cooldown expires, should be selectable"
    
    print("Cooldown enforcement test passed")


def test_once_flag():
    """Test that 'once' storylets can only trigger once"""
    director = DirectorService()
    project = create_test_project()
    
    storylet = Storylet(
        id="st-once",
        title="Once Only",
        tags=["unique"],
        once=True,
        effects=[]
    )
    
    world_state = project.worldState
    char_states = {"char-001": CharacterState(characterId="char-001")}
    rel_states = {}
    tick_history = TickHistory(thread_id="thread-001")
    config = DirectorConfig()
    
    # First selection - should work
    selected, _ = director.select_storylets(
        [storylet], world_state, char_states, rel_states, tick_history, config
    )
    assert len(selected) == 1
    
    # Mark as triggered once
    tick_history.triggered_once["st-once"] = True
    
    # Try again - should be blocked
    selected, _ = director.select_storylets(
        [storylet], world_state, char_states, rel_states, tick_history, config
    )
    assert len(selected) == 0, "'once' storylet should not be selectable again"
    
    print("Once flag test passed")


def test_tick_execution():
    """Test full tick execution with effects"""
    director = DirectorService()
    project = create_test_project()
    
    # Add a storylet that changes world state
    project.storylets = {
        "st-power-shift": Storylet(
            id="st-power-shift",
            title="Power Shift",
            tags=["political"],
            preconditions=[],
            effects=[
                Effect(
                    scope="world",
                    target="world",
                    op="set",
                    path="vars.faction_a_power",
                    value=70,
                    reason="Power shift occurs"
                ),
                Effect(
                    scope="world",
                    target="world",
                    op="set",
                    path="vars.market_peace",
                    value=50,
                    reason="Tensions rise"
                )
            ],
            weight=1.0
        )
    }
    
    # Execute tick
    config = DirectorConfig(events_per_tick=1)
    tick_record = director.tick(project, "thread-001", 0, config)
    
    # Verify tick record
    assert len(tick_record.events) == 1
    assert tick_record.events[0].storylet_id == "st-power-shift"
    assert tick_record.events[0].tick_number == 0
    
    # Verify effects were applied (check state diff)
    assert "world" in tick_record.state_diff
    assert "faction_a_power" in tick_record.state_diff["world"]
    assert tick_record.state_diff["world"]["faction_a_power"]["after"] == 70
    
    # Verify tick history was updated
    assert "tick_history_thread-001" in project.tick_histories
    tick_history = project.tick_histories["tick_history_thread-001"]
    assert len(tick_history.ticks) == 1
    assert "st-power-shift" in tick_history.last_triggered
    
    print("Tick execution test passed")


def test_weighted_selection():
    """Test that higher weight storylets are more likely to be selected"""
    director = DirectorService()
    project = create_test_project()
    
    # Set random seed for reproducibility
    random.seed(42)
    
    storylets = [
        Storylet(id="st-low", title="Low Weight", tags=[], weight=0.1, effects=[]),
        Storylet(id="st-high", title="High Weight", tags=[], weight=10.0, effects=[])
    ]
    
    world_state = project.worldState
    char_states = {"char-001": CharacterState(characterId="char-001")}
    rel_states = {}
    tick_history = TickHistory(thread_id="thread-001")
    config = DirectorConfig(events_per_tick=1)
    
    # Run selection multiple times and count
    selections = {"st-low": 0, "st-high": 0}
    for _ in range(100):
        selected, _ = director.select_storylets(
            storylets, world_state, char_states, rel_states, tick_history, config
        )
        if selected:
            selections[selected[0].id] += 1
    
    # High weight should be selected much more often
    assert selections["st-high"] > selections["st-low"] * 5, \
        f"High weight should be selected much more often: {selections}"
    
    print(f"Weighted selection test passed (high: {selections['st-high']}, low: {selections['st-low']})")


def test_intensity_tracking():
    """Test that intensity is properly tracked and updated"""
    director = DirectorService()
    project = create_test_project()
    
    project.storylets = {
        "st-escalate": Storylet(
            id="st-escalate",
            title="Escalating Event",
            tags=["conflict"],
            intensity_delta=0.2,
            effects=[]
        )
    }
    
    config = DirectorConfig()
    
    # Get initial intensity
    tick_history_key = "tick_history_thread-001"
    project.tick_histories[tick_history_key] = TickHistory(thread_id="thread-001")
    initial_intensity = project.tick_histories[tick_history_key].current_intensity
    
    # Execute tick
    tick_record = director.tick(project, "thread-001", 0, config)
    
    # Intensity should have increased
    final_intensity = project.tick_histories[tick_history_key].current_intensity
    assert final_intensity > initial_intensity, \
        f"Intensity should increase: {initial_intensity} -> {final_intensity}"
    
    print("Intensity tracking test passed")


def run_all_tests():
    """Run all director service tests"""
    print("\n=== Testing DirectorService ===\n")
    
    test_storylet_loading()
    test_precondition_filtering()
    test_cooldown_enforcement()
    test_once_flag()
    test_tick_execution()
    test_weighted_selection()
    test_intensity_tracking()
    
    print("\nAll DirectorService tests passed!\n")


if __name__ == "__main__":
    run_all_tests()
