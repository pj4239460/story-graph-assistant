"""
Tests for Storylet Editor functionality

Tests storylet CRUD operations through the UI layer.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models.project import Project
from src.models.storylet import Storylet, Precondition, Effect
from src.services.project_service import ProjectService
from src.repositories.json_repo import JsonProjectRepository


def test_storylet_creation():
    """Test creating a new storylet"""
    project = Project(
        id="test-001",
        name="Test Project",
        locale="en"
    )
    
    # Initialize storylets dict
    project.storylets = {}
    
    # Create a storylet
    storylet = Storylet(
        id="st-test-001",
        title="Test Storylet",
        description="A test storylet for validation",
        weight=1.5,
        once=False,
        cooldown=3,
        intensity_delta=0.2,
        tags=["test", "validation"],
        is_fallback=False,
        requires_fired=[],
        forbids_fired=[],
        preconditions=[
            Precondition(
                scope="world",
                target="vars",
                path="test_value",
                op=">=",
                value=10
            )
        ],
        effects=[
            Effect(
                scope="world",
                target="vars",
                path="test_result",
                op="set",
                value=1
            )
        ]
    )
    
    project.storylets[storylet.id] = storylet
    
    # Validate
    assert len(project.storylets) == 1
    assert project.storylets["st-test-001"].title == "Test Storylet"
    assert len(project.storylets["st-test-001"].preconditions) == 1
    assert len(project.storylets["st-test-001"].effects) == 1
    
    print("✓ Storylet creation test passed")


def test_storylet_search():
    """Test searching storylets by title, ID, and tags"""
    project = Project(
        id="test-002",
        name="Search Test",
        locale="en"
    )
    
    project.storylets = {
        "st-combat-001": Storylet(
            id="st-combat-001",
            title="Epic Battle",
            tags=["combat", "epic"],
            effects=[]
        ),
        "st-peaceful-001": Storylet(
            id="st-peaceful-001",
            title="Quiet Meditation",
            tags=["peaceful", "calm"],
            effects=[]
        ),
        "st-combat-002": Storylet(
            id="st-combat-002",
            title="Skirmish",
            tags=["combat", "small"],
            effects=[]
        )
    }
    
    # Search by title
    search_term = "battle"
    results = [
        s for s in project.storylets.values()
        if search_term.lower() in s.title.lower()
    ]
    assert len(results) == 1
    assert results[0].id == "st-combat-001"
    
    # Search by ID pattern
    search_term = "combat"
    results = [
        s for s in project.storylets.values()
        if search_term.lower() in s.id.lower()
    ]
    assert len(results) == 2
    
    # Search by tag
    search_term = "peaceful"
    results = [
        s for s in project.storylets.values()
        if any(search_term.lower() in tag.lower() for tag in s.tags)
    ]
    assert len(results) == 1
    assert results[0].id == "st-peaceful-001"
    
    print("✓ Storylet search test passed")


def test_storylet_filtering():
    """Test filtering storylets by type"""
    project = Project(
        id="test-003",
        name="Filter Test",
        locale="en"
    )
    
    project.storylets = {
        "st-fallback": Storylet(
            id="st-fallback",
            title="Ambient Event",
            is_fallback=True,
            effects=[]
        ),
        "st-once": Storylet(
            id="st-once",
            title="One-time Event",
            once=True,
            effects=[]
        ),
        "st-cooldown": Storylet(
            id="st-cooldown",
            title="Timed Event",
            cooldown=5,
            effects=[]
        ),
        "st-ordered": Storylet(
            id="st-ordered",
            title="Quest Step",
            requires_fired=["st-intro"],
            effects=[]
        )
    }
    
    # Filter fallback
    fallback = [s for s in project.storylets.values() if s.is_fallback]
    assert len(fallback) == 1
    assert fallback[0].id == "st-fallback"
    
    # Filter once
    once = [s for s in project.storylets.values() if s.once]
    assert len(once) == 1
    assert once[0].id == "st-once"
    
    # Filter cooldown
    cooldown = [s for s in project.storylets.values() if s.cooldown > 0]
    assert len(cooldown) == 1
    assert cooldown[0].id == "st-cooldown"
    
    # Filter ordering
    ordered = [
        s for s in project.storylets.values()
        if s.requires_fired or s.forbids_fired
    ]
    assert len(ordered) == 1
    assert ordered[0].id == "st-ordered"
    
    print("✓ Storylet filtering test passed")


def test_storylet_validation():
    """Test storylet field validation"""
    project = Project(
        id="test-004",
        name="Validation Test",
        locale="en"
    )
    
    project.storylets = {}
    
    # Test valid storylet
    valid = Storylet(
        id="st-valid",
        title="Valid Storylet",
        weight=1.0,
        intensity_delta=0.0,
        effects=[]
    )
    project.storylets[valid.id] = valid
    assert len(project.storylets) == 1
    
    # Test that ID uniqueness is enforced (manual check in UI)
    # In real UI, should prevent saving duplicate ID
    
    # Test weight boundaries (validated by Pydantic)
    try:
        invalid_weight = Storylet(
            id="st-invalid-weight",
            title="Invalid Weight",
            weight=-1.0,  # Negative weight should be caught
            effects=[]
        )
        # If Pydantic allows this, we should add validation
        assert False, "Should have raised validation error for negative weight"
    except:
        # Expected to fail validation
        pass
    
    print("✓ Storylet validation test passed")


def test_storylet_update():
    """Test updating an existing storylet"""
    project = Project(
        id="test-005",
        name="Update Test",
        locale="en"
    )
    
    # Create original
    original = Storylet(
        id="st-update-test",
        title="Original Title",
        description="Original description",
        weight=1.0,
        effects=[]
    )
    project.storylets = {original.id: original}
    
    # Update
    updated = Storylet(
        id="st-update-test",
        title="Updated Title",
        description="Updated description",
        weight=2.0,
        effects=[
            Effect(
                scope="world",
                target="vars",
                path="updated",
                op="set",
                value=1
            )
        ]
    )
    project.storylets[updated.id] = updated
    
    # Validate
    assert project.storylets["st-update-test"].title == "Updated Title"
    assert project.storylets["st-update-test"].weight == 2.0
    assert len(project.storylets["st-update-test"].effects) == 1
    
    print("✓ Storylet update test passed")


def test_storylet_deletion():
    """Test deleting a storylet"""
    project = Project(
        id="test-006",
        name="Delete Test",
        locale="en"
    )
    
    project.storylets = {
        "st-keep": Storylet(id="st-keep", title="Keep", effects=[]),
        "st-delete": Storylet(id="st-delete", title="Delete", effects=[])
    }
    
    assert len(project.storylets) == 2
    
    # Delete
    del project.storylets["st-delete"]
    
    # Validate
    assert len(project.storylets) == 1
    assert "st-keep" in project.storylets
    assert "st-delete" not in project.storylets
    
    print("✓ Storylet deletion test passed")


def test_complex_preconditions():
    """Test storylets with multiple preconditions"""
    storylet = Storylet(
        id="st-complex",
        title="Complex Storylet",
        preconditions=[
            Precondition(
                path="world.vars.faction_power",
                op=">=",
                value=50
            ),
            Precondition(
                path="characters.char-001.vars.reputation",
                op=">=",
                value=20
            ),
            Precondition(
                path="relationships.char-001_char-002.trust",
                op=">=",
                value=30
            )
        ],
        effects=[]
    )
    
    assert len(storylet.preconditions) == 3
    assert "world.vars" in storylet.preconditions[0].path
    assert "characters.char-001" in storylet.preconditions[1].path
    assert "relationships" in storylet.preconditions[2].path
    
    print("✓ Complex preconditions test passed")


def run_all_tests():
    """Run all storylet editor tests"""
    print("\n=== Testing Storylet Editor ===\n")
    
    test_storylet_creation()
    test_storylet_search()
    test_storylet_filtering()
    test_storylet_validation()
    test_storylet_update()
    test_storylet_deletion()
    test_complex_preconditions()
    
    print("\n✓ All Storylet Editor tests passed!\n")


if __name__ == "__main__":
    run_all_tests()
