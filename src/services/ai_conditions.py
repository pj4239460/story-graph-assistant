"""
AI-powered condition evaluator for storylet preconditions

This module provides LLM-based evaluation of natural language conditions,
complementing the deterministic ConditionsEvaluator. It enables authors to
specify conditions in human-readable format like:
- "The tension is high and Alice is angry"
- "Multiple factions are in conflict"
- "The protagonist feels cornered"

Design Philosophy:
    AI conditions trade determinism for expressiveness. They're useful when:
    - Conditions are too complex for explicit rules
    - You want emergent behavior that adapts to narrative context
    - Prototyping new storylets before formalizing conditions
    
    However, they come with costs:
    - LLM calls are slower (~500ms vs <1ms)
    - Results may vary slightly (though we minimize this)
    - Token consumption increases
    
    Best Practice: Use deterministic conditions when possible, AI when necessary.

Example Flow:
    1. Build context string from world/character/relationship state
    2. Ask LLM: "Given this state, is condition X satisfied?"
    3. Parse structured response (YES/NO + confidence + reasoning)
    4. Cache result for same state hash (performance optimization)
"""
from typing import Dict, Any, Optional, Tuple
from hashlib import md5
import json

from ..models.storylet import Precondition
from ..models.world import WorldState
from ..models.character import CharacterState
from ..models.project import Project
from ..infra.llm_client import LLMClient
from ..infra.token_stats import check_token_limit


class AIConditionsEvaluator:
    """
    LLM-based evaluator for natural language conditions.
    
    This evaluator converts story state into natural language context,
    then asks the LLM to evaluate whether a condition is satisfied.
    
    Features:
    - Structured prompts for consistent outputs
    - Confidence scoring (0.0-1.0)
    - Explanation generation (for debugging)
    - Result caching (same state = same result)
    - Token limit checking
    
    Cache Strategy:
        We cache results based on a hash of (condition + state_summary).
        This ensures that the same condition evaluated against the same state
        always returns the cached result, improving performance and consistency.
    """
    
    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm_client = llm_client or LLMClient()
        self._cache: Dict[str, Tuple[bool, float, str]] = {}  # Hash -> (result, confidence, explanation)
    
    def evaluate(
        self,
        precondition: Precondition,
        world_state: WorldState,
        char_states: Dict[str, CharacterState],
        rel_states: Dict[str, Any],
        project: Project
    ) -> Tuple[bool, str]:
        """
        Evaluate a natural language condition using LLM.
        
        Args:
            precondition: Must have nl_condition set
            world_state: Current world state
            char_states: Character states
            rel_states: Relationship states
            project: Project (for token limits and LLM settings)
        
        Returns:
            (satisfied, explanation) where:
            - satisfied: True if LLM judges condition is met
            - explanation: Human-readable reasoning with confidence
        
        Example:
            >>> cond = Precondition(nl_condition="The tension is very high")
            >>> satisfied, explanation = evaluator.evaluate(cond, world, chars, rels, proj)
            >>> print(explanation)
            "✓ [AI 0.92] The tension is very high (world.vars.tension=85, conflict events recent)"
        """
        if not precondition.is_nl_condition():
            return False, "✗ Not a natural language condition (use ConditionsEvaluator instead)"
        
        nl_condition = precondition.nl_condition
        
        # Check cache first
        cache_key = self._make_cache_key(nl_condition, world_state, char_states, rel_states)
        if cache_key in self._cache:
            result, confidence, reasoning = self._cache[cache_key]
            explanation = self._format_explanation(result, confidence, nl_condition, reasoning)
            return result, explanation
        
        # Check token limit
        can_proceed, message = check_token_limit(project, estimated_tokens=800)
        if not can_proceed:
            return False, f"✗ [AI] Token limit exceeded: {message}"
        
        # Build context
        context = self._build_context(world_state, char_states, rel_states)
        
        # Build prompt
        messages = [
            {
                "role": "system",
                "content": """You are a narrative state analyzer for an interactive story system.
Your job is to evaluate whether a natural language condition is satisfied given the current story state.

You must respond in this EXACT format:

JUDGMENT: [YES or NO]
CONFIDENCE: [0.0 to 1.0]
REASONING: [Brief explanation citing specific state values]

Example:
JUDGMENT: YES
CONFIDENCE: 0.85
REASONING: world.vars.tension=80 (high) and characters.alice.mood=angry (confirmed)"""
            },
            {
                "role": "user",
                "content": f"""=== CURRENT STORY STATE ===
{context}

=== CONDITION TO EVALUATE ===
"{nl_condition}"

=== YOUR TASK ===
Is this condition satisfied given the current state? Respond in the exact format specified."""
            }
        ]
        
        try:
            # Call LLM
            response, _ = self.llm_client.call(
                project=project,
                task_type="condition_eval",
                messages=messages,
                max_tokens=300
            )
            
            # Parse structured response
            result, confidence, reasoning = self._parse_response(response)
            
            # Cache result
            self._cache[cache_key] = (result, confidence, reasoning)
            
            # Format explanation
            explanation = self._format_explanation(result, confidence, nl_condition, reasoning)
            return result, explanation
            
        except Exception as e:
            error_msg = f"✗ [AI] Error evaluating condition: {str(e)}"
            return False, error_msg
    
    def evaluate_all(
        self,
        preconditions: list[Precondition],
        world_state: WorldState,
        char_states: Dict[str, CharacterState],
        rel_states: Dict[str, Any],
        project: Project
    ) -> Tuple[bool, list[str]]:
        """
        Evaluate multiple NL conditions using AND logic.
        
        All conditions must be satisfied for the result to be True.
        
        Args:
            preconditions: List of conditions (can mix NL and deterministic)
            world_state: Current world state
            char_states: Character states
            rel_states: Relationship states
            project: Project context
        
        Returns:
            (all_satisfied, explanations) where:
            - all_satisfied: True only if ALL conditions are satisfied
            - explanations: List of explanations for each condition
        
        Note:
            This method can handle mixed conditions. Non-NL conditions will
            return a message indicating they should use ConditionsEvaluator.
        """
        if not preconditions:
            return True, ["No preconditions (always satisfied)"]
        
        explanations = []
        all_satisfied = True
        
        for cond in preconditions:
            if not cond.is_nl_condition():
                # Not an NL condition, skip but note it
                explanations.append(f"⚠ {cond} (deterministic, use ConditionsEvaluator)")
                continue
            
            satisfied, explanation = self.evaluate(cond, world_state, char_states, rel_states, project)
            explanations.append(explanation)
            if not satisfied:
                all_satisfied = False
        
        return all_satisfied, explanations
    
    def _build_context(
        self,
        world_state: WorldState,
        char_states: Dict[str, CharacterState],
        rel_states: Dict[str, Any]
    ) -> str:
        """
        Convert story state into natural language context for LLM.
        
        This creates a concise, readable summary of:
        - World variables (faction power, tension, resources)
        - Character states (mood, status, location)
        - Relationship states (trust, romance, rivalry)
        
        Design Note:
            We keep this concise (<500 tokens) to minimize cost and latency.
            Only include the most relevant state information.
        """
        lines = []
        
        # World state
        if world_state.vars:
            lines.append("World Variables:")
            for key, value in sorted(world_state.vars.items()):
                lines.append(f"  - world.vars.{key} = {value}")
        
        # Character states (limit to first 5 to avoid token explosion)
        if char_states:
            lines.append("\nCharacter States:")
            for char_id, state in list(char_states.items())[:5]:
                lines.append(f"  - characters.{char_id}:")
                if state.mood:
                    lines.append(f"      mood = {state.mood}")
                if state.status:
                    lines.append(f"      status = {state.status}")
                if state.location:
                    lines.append(f"      location = {state.location}")
                if state.active_traits:
                    lines.append(f"      active_traits = {state.active_traits}")
        
        # Relationship states (limit to first 3)
        if rel_states:
            lines.append("\nRelationship States:")
            for rel_key, rel_data in list(rel_states.items())[:3]:
                lines.append(f"  - relationships.{rel_key}:")
                if isinstance(rel_data, dict):
                    for field, value in sorted(rel_data.items()):
                        lines.append(f"      {field} = {value}")
        
        return "\n".join(lines) if lines else "(Empty state)"
    
    def _parse_response(self, response: str) -> Tuple[bool, float, str]:
        """
        Parse structured LLM response into (result, confidence, reasoning).
        
        Expected format:
            JUDGMENT: YES
            CONFIDENCE: 0.85
            REASONING: world.vars.tension=80 (high)...
        
        Returns:
            (result, confidence, reasoning) with defaults on parse failure
        """
        result = False
        confidence = 0.5
        reasoning = "Unable to parse LLM response"
        
        if not response:
            return result, confidence, reasoning
        
        lines = response.strip().split('\n')
        for line in lines:
            line = line.strip()
            
            if line.startswith('JUDGMENT:'):
                judgment = line.split(':', 1)[1].strip().upper()
                result = 'YES' in judgment
            
            elif line.startswith('CONFIDENCE:'):
                try:
                    confidence = float(line.split(':', 1)[1].strip())
                    confidence = max(0.0, min(1.0, confidence))  # Clamp to [0,1]
                except:
                    confidence = 0.5
            
            elif line.startswith('REASONING:'):
                reasoning = line.split(':', 1)[1].strip()
        
        # If no structured output, use full response as reasoning
        if reasoning == "Unable to parse LLM response":
            reasoning = response[:200]  # Truncate to prevent bloat
        
        return result, confidence, reasoning
    
    def _format_explanation(
        self,
        result: bool,
        confidence: float,
        condition: str,
        reasoning: str
    ) -> str:
        """Format a human-readable explanation with confidence scoring."""
        symbol = "✓" if result else "✗"
        # Truncate condition and reasoning to keep explanations concise
        condition_short = condition[:60] + "..." if len(condition) > 60 else condition
        reasoning_short = reasoning[:100] + "..." if len(reasoning) > 100 else reasoning
        return f"{symbol} [AI {confidence:.2f}] {condition_short} ({reasoning_short})"
    
    def _make_cache_key(
        self,
        condition: str,
        world_state: WorldState,
        char_states: Dict[str, CharacterState],
        rel_states: Dict[str, Any]
    ) -> str:
        """
        Generate cache key from condition + state.
        
        This creates a hash of the condition text and relevant state values,
        so the same evaluation against the same state returns cached results.
        """
        state_summary = {
            "world_vars": dict(sorted(world_state.vars.items())),
            "char_moods": {cid: cs.mood for cid, cs in char_states.items()},
            "rel_states": {k: v for k, v in rel_states.items()}
        }
        
        cache_input = f"{condition}||{json.dumps(state_summary, sort_keys=True)}"
        return md5(cache_input.encode()).hexdigest()
    
    def clear_cache(self):
        """Clear all cached evaluations (useful for testing or forcing re-evaluation)."""
        self._cache.clear()
