"""
Tests for ConditionsEvaluator

Validates all operators and path resolution logic.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.conditions import ConditionsEvaluator
from src.models.storylet import Precondition
from src.models.world import WorldState
from src.models.character import CharacterState


def test_world_vars_comparison():
    """Test world.vars path with comparison operators"""
    evaluator = ConditionsEvaluator()
    
    world_state = WorldState(vars={"power": 60, "peace": 45})
    char_states = {}
    rel_states = {}
    
    # Test ==
    cond = Precondition(path="world.vars.power", op="==", value=60)
    result, explanation = evaluator.evaluate(cond, world_state, char_states, rel_states)
    assert result == True, f"Expected True, got {result}"
    assert "✓" in explanation
    
    # Test !=
    cond = Precondition(path="world.vars.power", op="!=", value=50)
    result, _ = evaluator.evaluate(cond, world_state, char_states, rel_states)
    assert result == True
    
    # Test >
    cond = Precondition(path="world.vars.power", op=">", value=55)
    result, _ = evaluator.evaluate(cond, world_state, char_states, rel_states)
    assert result == True
    
    # Test >=
    cond = Precondition(path="world.vars.power", op=">=", value=60)
    result, _ = evaluator.evaluate(cond, world_state, char_states, rel_states)
    assert result == True
    
    # Test <
    cond = Precondition(path="world.vars.peace", op="<", value=50)
    result, _ = evaluator.evaluate(cond, world_state, char_states, rel_states)
    assert result == True
    
    # Test <=
    cond = Precondition(path="world.vars.peace", op="<=", value=45)
    result, _ = evaluator.evaluate(cond, world_state, char_states, rel_states)
    assert result == True
    
    print("✓ World vars comparison tests passed")


def test_character_state_access():
    """Test characters.<id>.<field> path resolution"""
    evaluator = ConditionsEvaluator()
    
    world_state = WorldState()
    char_states = {
        "char-001": CharacterState(
            characterId="char-001",
            mood="angry",
            status="active",
            location="market",
            active_traits=["brave", "reckless"],
            active_goals=["revenge"],
            vars={"trust_level": 30}
        )
    }
    rel_states = {}
    
    # Test mood
    cond = Precondition(path="characters.char-001.mood", op="==", value="angry")
    result, _ = evaluator.evaluate(cond, world_state, char_states, rel_states)
    assert result == True
    
    # Test location
    cond = Precondition(path="characters.char-001.location", op="==", value="market")
    result, _ = evaluator.evaluate(cond, world_state, char_states, rel_states)
    assert result == True
    
    # Test traits list with 'contains'
    cond = Precondition(path="characters.char-001.traits", op="contains", value="brave")
    result, _ = evaluator.evaluate(cond, world_state, char_states, rel_states)
    assert result == True
    
    # Test nested vars
    cond = Precondition(path="characters.char-001.vars.trust_level", op="<", value=50)
    result, _ = evaluator.evaluate(cond, world_state, char_states, rel_states)
    assert result == True
    
    print("✓ Character state access tests passed")


def test_relationship_access():
    """Test relationships.<a|b>.<field> path resolution"""
    evaluator = ConditionsEvaluator()
    
    world_state = WorldState()
    char_states = {}
    rel_states = {
        "char-001|char-002": {
            "trust": 75,
            "status": "alliance"
        }
    }
    
    # Test relationship field
    cond = Precondition(path="relationships.char-001|char-002.trust", op=">=", value=70)
    result, _ = evaluator.evaluate(cond, world_state, char_states, rel_states)
    assert result == True
    
    # Test relationship status
    cond = Precondition(path="relationships.char-001|char-002.status", op="==", value="alliance")
    result, _ = evaluator.evaluate(cond, world_state, char_states, rel_states)
    assert result == True
    
    print("✓ Relationship access tests passed")


def test_in_and_contains_operators():
    """Test 'in' and 'contains' operators"""
    evaluator = ConditionsEvaluator()
    
    world_state = WorldState()
    char_states = {
        "char-001": CharacterState(
            characterId="char-001",
            active_traits=["brave", "smart", "loyal"]
        )
    }
    rel_states = {}
    
    # Test 'in' operator (value in list)
    cond = Precondition(path="characters.char-001.traits", op="contains", value="brave")
    result, _ = evaluator.evaluate(cond, world_state, char_states, rel_states)
    assert result == True
    
    # Test 'in' with string
    world_state.vars["message"] = "The kingdom is in danger"
    cond = Precondition(path="world.vars.message", op="in", value=["The kingdom is in danger", "Peace prevails"])
    result, _ = evaluator.evaluate(cond, world_state, char_states, rel_states)
    assert result == True
    
    print("✓ In/contains operator tests passed")


def test_evaluate_all():
    """Test evaluate_all with multiple conditions (AND logic)"""
    evaluator = ConditionsEvaluator()
    
    world_state = WorldState(vars={"power": 60, "peace": 45})
    char_states = {}
    rel_states = {}
    
    # All conditions satisfied
    conditions = [
        Precondition(path="world.vars.power", op=">", value=50),
        Precondition(path="world.vars.peace", op="<", value=50)
    ]
    
    all_satisfied, explanations = evaluator.evaluate_all(conditions, world_state, char_states, rel_states)
    assert all_satisfied == True
    assert len(explanations) == 2
    assert all("✓" in exp for exp in explanations)
    
    # One condition fails
    conditions = [
        Precondition(path="world.vars.power", op=">", value=50),
        Precondition(path="world.vars.peace", op=">", value=50)  # This will fail
    ]
    
    all_satisfied, explanations = evaluator.evaluate_all(conditions, world_state, char_states, rel_states)
    assert all_satisfied == False
    assert any("✗" in exp for exp in explanations)
    
    # Empty conditions (always satisfied)
    all_satisfied, explanations = evaluator.evaluate_all([], world_state, char_states, rel_states)
    assert all_satisfied == True
    
    print("✓ Evaluate all tests passed")


def test_missing_path_handling():
    """Test handling of missing/invalid paths"""
    evaluator = ConditionsEvaluator()
    
    world_state = WorldState()
    char_states = {}
    rel_states = {}
    
    # Missing world var
    cond = Precondition(path="world.vars.nonexistent", op="==", value=50)
    result, explanation = evaluator.evaluate(cond, world_state, char_states, rel_states)
    assert result == False  # None == 50 is False
    
    # Missing character
    cond = Precondition(path="characters.nonexistent.mood", op="==", value="happy")
    result, _ = evaluator.evaluate(cond, world_state, char_states, rel_states)
    assert result == False
    
    print("✓ Missing path handling tests passed")


def run_all_tests():
    """Run all condition evaluator tests"""
    print("\n=== Testing ConditionsEvaluator ===\n")
    
    test_world_vars_comparison()
    test_character_state_access()
    test_relationship_access()
    test_in_and_contains_operators()
    test_evaluate_all()
    test_missing_path_handling()
    
    print("\n✅ All ConditionsEvaluator tests passed!\n")


if __name__ == "__main__":
    run_all_tests()
