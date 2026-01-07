"""
Conditions evaluator for storylet preconditions

This module provides deterministic condition evaluation for the World Director system.
Unlike AI-based evaluation, this uses explicit rules and comparison operators to
determine whether a storylet's preconditions are met.

Key features:
- Deterministic: Same state always produces same result
- Explainable: Every evaluation returns a human-readable explanation
- Flexible: Supports multiple path types and comparison operators
- Safe: Handles missing values and invalid paths gracefully

Example usage:
    evaluator = ConditionsEvaluator()
    precondition = Precondition(path="world.vars.tension", op=">=", value=70)
    satisfied, explanation = evaluator.evaluate(precondition, world_state, chars, rels)
    if satisfied:
        print("Can trigger!")  # tension is >= 70
"""
from typing import Any, Dict
from ..models.storylet import Precondition
from ..models.character import CharacterState
from ..models.world import WorldState


class ConditionsEvaluator:
    """
    Evaluates preconditions against world/character/relationship state.
    
    This evaluator supports three types of paths:
    
    1. World paths: "world.vars.<key>" or "world.facts.<key>"
       - Access world state variables
       - Example: "world.vars.faction_a_power" >= 60
    
    2. Character paths: "characters.<id>.<field>"
       - Access character state fields (mood, status, location, traits, goals, vars)
       - Example: "characters.alice.mood" == "angry"
    
    3. Relationship paths: "relationships.<a|b>.<field>"
       - Access relationship fields between two characters
       - Example: "relationships.alice|bob.trust" > 50
    
    Supported operators:
    - Comparison: ==, !=, <, <=, >, >=
    - Membership: in (value in list), contains (list contains value)
    - Special: has_tag (for tag checking)
    """
    
    def __init__(self):
        pass
    
    def evaluate(
        self,
        precondition: Precondition,
        world_state: WorldState,
        char_states: Dict[str, CharacterState],
        rel_states: Dict[str, Any]
    ) -> tuple[bool, str]:
        """
        Evaluate a single precondition against current state.
        
        This method:
        1. Resolves the path to get the actual value from state
        2. Compares the actual value against the expected value using the operator
        3. Returns both the boolean result and a human-readable explanation
        
        Args:
            precondition: The condition to evaluate
            world_state: Current world state
            char_states: Map of character_id -> CharacterState
            rel_states: Map of "char_a|char_b" -> relationship data
        
        Returns:
            (result, explanation) where:
            - result: True if condition is satisfied, False otherwise
            - explanation: Human-readable string with ✓ or ✗ prefix
        
        Example:
            >>> precondition = Precondition(path="world.vars.tension", op=">=", value=70)
            >>> result, explanation = evaluator.evaluate(precondition, world, chars, rels)
            >>> print(explanation)
            "✓ world.vars.tension = 80 (satisfies >= 70)"
        """
        try:
            # Step 1: Resolve the path to get actual value
            actual_value = self._get_value(
                precondition.path,
                world_state,
                char_states,
                rel_states
            )
            
            # Step 2: Compare actual value against expected value
            result = self._compare(
                actual_value,
                precondition.op,
                precondition.value
            )
            
            # Step 3: Generate explanation
            if result:
                explanation = f"✓ {precondition.path} = {actual_value} (satisfies {precondition.op} {precondition.value})"
            else:
                explanation = f"✗ {precondition.path} = {actual_value} (fails {precondition.op} {precondition.value})"
            
            return result, explanation
            
        except Exception as e:
            # Handle errors gracefully (e.g., missing paths, invalid operators)
            return False, f"✗ Error evaluating {precondition.path}: {str(e)}"
    
    def evaluate_all(
        self,
        preconditions: list[Precondition],
        world_state: WorldState,
        char_states: Dict[str, CharacterState],
        rel_states: Dict[str, Any]
    ) -> tuple[bool, list[str]]:
        """
        Evaluate multiple preconditions using AND logic.
        
        All preconditions must be satisfied for the result to be True.
        This is the standard behavior for storylet triggering: a storylet
        can only trigger if ALL of its preconditions are met.
        
        Args:
            preconditions: List of conditions to evaluate
            world_state: Current world state
            char_states: Character states
            rel_states: Relationship states
        
        Returns:
            (all_satisfied, explanations) where:
            - all_satisfied: True only if ALL conditions are satisfied
            - explanations: List of human-readable explanations for each condition
        
        Example:
            >>> preconditions = [
            ...     Precondition(path="world.vars.tension", op=">=", value=70),
            ...     Precondition(path="characters.alice.mood", op="==", value="angry")
            ... ]
            >>> all_ok, explanations = evaluator.evaluate_all(preconditions, ...)
            >>> if all_ok:
            ...     print("All conditions satisfied, can trigger storylet!")
        """
        if not preconditions:
            return True, ["No preconditions (always satisfied)"]
        
        explanations = []
        all_satisfied = True
        
        for cond in preconditions:
            satisfied, explanation = self.evaluate(cond, world_state, char_states, rel_states)
            explanations.append(explanation)
            if not satisfied:
                all_satisfied = False  # AND logic: one failure means all fail
        
        return all_satisfied, explanations
    
    def _get_value(
        self,
        path: str,
        world_state: WorldState,
        char_states: Dict[str, CharacterState],
        rel_states: Dict[str, Any]
    ) -> Any:
        """
        Extract value from state using dot-notation path.
        
        This method resolves paths like "world.vars.tension" or "characters.alice.mood"
        into actual values from the state objects.
        
        Path formats:
        
        1. World paths:
           - "world.vars.<key>" -> world_state.vars[key]
           - "world.facts.<id>" -> world_state.facts[id]
        
        2. Character paths:
           - "characters.<id>.mood" -> char_states[id].mood
           - "characters.<id>.status" -> char_states[id].status
           - "characters.<id>.location" -> char_states[id].location
           - "characters.<id>.traits" -> char_states[id].active_traits (list)
           - "characters.<id>.goals" -> char_states[id].active_goals (list)
           - "characters.<id>.vars.<key>" -> char_states[id].vars[key]
        
        3. Relationship paths:
           - "relationships.<a|b>.<field>" -> rel_states["a|b"][field]
        
        Args:
            path: Dot-notation path string
            world_state: WorldState object
            char_states: Map of character_id -> CharacterState
            rel_states: Map of relationship keys -> relationship data
        
        Returns:
            The value at that path, or None if not found
        
        Raises:
            ValueError: If path format is invalid
        """
        parts = path.split('.')
        
        if parts[0] == "world":
            # World state access
            if len(parts) < 2:
                raise ValueError(f"Invalid world path: {path}")
            
            if parts[1] == "vars":
                # Access world.vars dictionary
                key = '.'.join(parts[2:])  # Support nested keys like "faction.a.power"
                return world_state.vars.get(key, None)
            
            elif parts[1] == "facts":
                # Access world.facts dictionary
                if len(parts) < 3:
                    raise ValueError(f"Invalid facts path: {path}")
                fact_id = parts[2]
                return world_state.facts.get(fact_id, None)
            
            else:
                raise ValueError(f"Unknown world accessor: {parts[1]}")
        
        elif parts[0] == "characters":
            # Character state access
            if len(parts) < 3:
                raise ValueError(f"Invalid character path: {path} (need characters.<id>.<field>)")
            
            char_id = parts[1]
            field = parts[2]
            
            if char_id not in char_states:
                return None  # Character doesn't exist
            
            char_state = char_states[char_id]
            
            # Map field names to CharacterState attributes
            if field == "mood":
                return char_state.mood
            elif field == "status":
                return char_state.status
            elif field == "location":
                return char_state.location
            elif field == "traits":
                # Return list of active traits
                return char_state.active_traits
            elif field == "goals":
                # Return list of active goals
                return char_state.active_goals
            elif field == "fears":
                # Return list of active fears
                return char_state.active_fears
            elif field == "vars":
                # Character-specific variables
                if len(parts) < 4:
                    return char_state.vars  # Return entire vars dict
                var_key = '.'.join(parts[3:])  # Support nested keys
                return char_state.vars.get(var_key, None)
            else:
                raise ValueError(f"Unknown character field: {field}")
        
        elif parts[0] == "relationships":
            # Relationship state access
            if len(parts) < 3:
                raise ValueError(f"Invalid relationship path: {path}")
            
            rel_key = parts[1]  # e.g., "char-001|char-002" or "alice|bob"
            field = parts[2]
            
            if rel_key not in rel_states:
                return None  # Relationship doesn't exist
            
            rel_data = rel_states[rel_key]
            
            if len(parts) == 3:
                # Direct field access (e.g., "relationships.alice|bob.trust")
                return rel_data.get(field, None)
            else:
                # Nested access (e.g., "relationships.alice|bob.vars.conflict_level")
                nested_key = '.'.join(parts[3:])
                current = rel_data.get(field)
                for key in parts[3:]:
                    if isinstance(current, dict):
                        current = current.get(key)
                    else:
                        return None
                return current
        
        else:
            raise ValueError(f"Unknown path root: {parts[0]} (expected world/characters/relationships)")
    
    def _compare(self, actual: Any, op: str, expected: Any) -> bool:
        """
        Perform comparison operation between actual and expected values.
        
        This method implements all supported comparison operators.
        
        Operators:
        - ==, !=: Equality comparison (works for any type)
        - <, <=, >, >=: Numeric comparison (requires comparable types)
        - in: Check if expected is in actual (actual must be a collection)
        - contains: Check if actual contains expected (actual must be a collection)
        - has_tag: Alias for contains, commonly used for trait/tag checking
        
        Args:
            actual: The actual value from state
            op: The comparison operator
            expected: The expected value from precondition
        
        Returns:
            True if comparison succeeds, False otherwise
        
        Examples:
            >>> self._compare(80, ">=", 70)  # True
            >>> self._compare("angry", "==", "angry")  # True
            >>> self._compare(["brave", "smart"], "contains", "brave")  # True
            >>> self._compare("brave", "in", ["brave", "smart"])  # True
        """
        # Handle None values
        if actual is None:
            return op == "==" and expected is None
        
        # Equality operators (work for any type)
        if op == "==":
            return actual == expected
        
        elif op == "!=":
            return actual != expected
        
        # Numeric comparison operators (require comparable types)
        elif op == "<":
            return actual < expected
        
        elif op == "<=":
            return actual <= expected
        
        elif op == ">":
            return actual > expected
        
        elif op == ">=":
            return actual >= expected
        
        # Membership operators (for lists, sets, strings)
        elif op == "in":
            # Check if expected is IN actual
            # Example: "brave" in ["brave", "smart", "loyal"]
            return expected in actual
        
        elif op == "contains" or op == "has_tag":
            # Check if actual CONTAINS expected
            # Example: ["brave", "smart"] contains "brave"
            # This is the reverse of "in" and is more intuitive for trait checking
            return expected in actual
        
        else:
            raise ValueError(f"Unknown operator: {op}")
        
        elif op == "in":
            # Check if actual is in expected (expected should be list/set)
            if isinstance(expected, (list, set, tuple)):
                return actual in expected
            elif isinstance(expected, str):
                return str(actual) in expected
            return False
        
        elif op == "contains":
            # Check if expected is in actual (actual should be list/set/string)
            if isinstance(actual, (list, set, tuple)):
                return expected in actual
            elif isinstance(actual, str):
                return str(expected) in actual
            return False
        
        elif op == "has_tag":
            # Check if actual (list of tags) contains expected tag
            if isinstance(actual, (list, set, tuple)):
                return expected in actual
            return False
        
        else:
            raise ValueError(f"Unknown operator: {op}")
