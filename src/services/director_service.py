"""
World Director Service

This module implements the core "Director" layer that orchestrates world evolution.
The Director observes the current story state and selects appropriate storylets to
trigger, creating emergent narratives that feel dynamic and responsive.

Design Philosophy:
    Unlike traditional branching narrative editors, the Director uses a "systems thinking"
    approach. Instead of manually authoring every possible story path, you define:
    1. Story state (world vars, character states, relationships)
    2. Storylets (potential events with preconditions and effects)
    3. Director policy (pacing, diversity, intensity preferences)
    
    The Director then combines these elements to generate unique, replayable stories.

Inspired By:
    - AI Director (Left 4 Dead): Pacing control, intensity curves, peaks-and-valleys
      https://steamcdn-a.akamaihd.net/apps/valve/2009/ai_systems_of_l4d_mike_booth.pdf
    
    - Storylets/QBN (Fallen London, 80 Days): Conditional narrative fragments
      https://emshort.blog/2019/11/29/storylets-you-want-them/

Key Features:
    - Deterministic: Same state + config = same selection (reproducible)
    - Explainable: Every decision has a human-readable rationale
    - Replayable: Complete tick history enables time-travel debugging
    - Controllable: Tune pacing, diversity, intensity via config

Example Flow:
    1. Compute current story state (world, characters, relationships)
    2. Filter storylets by preconditions (which CAN trigger?)
    3. Apply cooldown and once filters (which SHOULD trigger?)
    4. Apply diversity penalty (avoid repetition)
    5. Apply pacing adjustment (maintain intensity curve)
    6. Weighted random selection (final choice)
    7. Apply effects and record rationale
"""
import random
import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from copy import deepcopy
from datetime import datetime

from ..models.project import Project
from ..models.storylet import (
    Storylet, Precondition, TickHistory, TickRecord, TickEvent,
    DirectorConfig
)
from ..models.world import Effect, WorldState
from ..models.character import CharacterState
from .state_service import StateService
from .conditions import ConditionsEvaluator
from .ai_conditions import AIConditionsEvaluator


class DirectorService:
    """
    The World Director: Orchestrates story evolution by selecting and triggering storylets.
    
    The Director implements a multi-stage selection pipeline:
    
    Stage 1: Precondition Filtering
        - Evaluate each storylet's preconditions against current state
        - Keep only storylets where ALL preconditions are satisfied
        - Generate explanations for why each passed or failed
    
    Stage 2: Cooldown & Once Filtering
        - Remove storylets still on cooldown (last_triggered + cooldown > current_tick)
        - Remove storylets marked "once" that have already triggered
    
    Stage 3: Diversity Penalty
        - Check recent ticks for tag repetition
        - Reduce weight for storylets with recently-used tags
        - Formula: weight *= (1 - diversity_penalty) ^ penalty_count
    
    Stage 4: Pacing Adjustment
        - Check current intensity vs storylet intensity_delta
        - If too intense, favor calming storylets (negative delta)
        - If too calm, favor escalating storylets (positive delta)
        - Formula: weight *= 1 + pacing_scale * (target_adjustment * intensity_delta)
    
    Stage 5: Weighted Selection
        - Use normalized weights as probabilities
        - Select N storylets without replacement
        - Record selection rationale
    
    Stage 6: Effect Application
        - Deep copy state (for diff calculation)
        - Apply each storylet's effects
        - Compute human-readable state diff
        - Update intensity based on storylet deltas
    
    Stage 7: History Recording
        - Create TickRecord with events, rationale, diff
        - Update cooldown tracking
        - Update once tracking
        - Append to TickHistory
    """
    
    def __init__(self, llm_client=None):
        """Initialize the Director with required services."""
        self.state_service = StateService()
        self.conditions_evaluator = ConditionsEvaluator()
        self.ai_conditions_evaluator = AIConditionsEvaluator(llm_client)
    
    def load_storylets(self, project: Project) -> List[Storylet]:
        """
        Load all storylets from the project.
        
        Storylets can be stored in the project in two formats:
        1. As a dictionary: project.storylets = {"st-001": Storylet(...), ...}
        2. As a list: project.storylets = [Storylet(...), Storylet(...), ...]
        
        This method normalizes both formats into a list.
        
        Args:
            project: The Project containing storylets
        
        Returns:
            List of Storylet objects
        
        Future Enhancement:
            Support loading from external files (e.g., project_dir/storylets/*.json)
            for better organization of large storylet libraries.
        """
        storylets = []
        
        # Check if project has storylets
        if hasattr(project, 'storylets') and project.storylets:
            # Handle dict format (recommended for projects with many storylets)
            if isinstance(project.storylets, dict):
                for storylet_id, storylet_data in project.storylets.items():
                    if isinstance(storylet_data, Storylet):
                        storylets.append(storylet_data)
                    elif isinstance(storylet_data, dict):
                        # Convert dict to Storylet object
                        storylets.append(Storylet(**storylet_data))
            
            # Handle list format (simpler for small projects)
            elif isinstance(project.storylets, list):
                for storylet_data in project.storylets:
                    if isinstance(storylet_data, Storylet):
                        storylets.append(storylet_data)
                    elif isinstance(storylet_data, dict):
                        storylets.append(Storylet(**storylet_data))
        
        return storylets
    
    def select_storylets(
        self,
        available_storylets: List[Storylet],
        world_state: WorldState,
        char_states: Dict[str, CharacterState],
        rel_states: Dict[str, Any],
        tick_history: TickHistory,
        config: DirectorConfig,
        project: Project
    ) -> Tuple[List[Storylet], List[str]]:
        """
        Select storylets to trigger based on current state and director policy.
        
        This implements the 9-stage World Director pipeline (v0.7):
        1. Precondition Filtering - Keep only storylets whose conditions are met
        2. Ordering Constraints (v0.7) - Check requires_fired and forbids_fired
        3. Cooldown & Once - Remove storylets on cooldown or already triggered
        4. Fallback Check (v0.7) - Use fallback storylets if pool is empty
        5. Diversity Penalty - Reduce weight for recently-used tags
        6. Pacing Adjustment - Favor storylets that match desired intensity
        7. Weighted Selection - Probabilistic selection based on final weights
        8. Effect Application - Apply selected storylets' effects to state
        9. History Recording - Record results and update tracking
        
        Args:
            available_storylets: All storylets in current scene/context
            world_state: Current global world state
            char_states: Current character states (by character ID)
            rel_states: Current relationship states
            tick_history: History of all previous ticks + tracking data
            config: Director configuration (events_per_tick, diversity, pacing, etc.)
            
        Returns:
            Tuple of:
            - selected_storylets: List of Storylet objects chosen for this tick
            - rationales: List of human-readable explanations for each selection
            
        Example:
            >>> storylets = [...]  # Scene's storylet pool
            >>> world = WorldState(vars={"gold": 100, ...})
            >>> config = DirectorConfig(events_per_tick=2)
            >>> selected, reasons = service.select_storylets(storylets, world, {}, {}, history, config)
            >>> # selected = [<Storylet "Merchant Visit">, <Storylet "Weather Change">]
            >>> # reasons = ["Preconditions satisfied (gold >= 50)", "Fallback (idle count=3)"]
        """
        # ═══════════════════════════════════════════════════════════════════
        # STAGE 1: Separate Regular and Fallback Storylets
        # ═══════════════════════════════════════════════════════════════════
        # Regular storylets are the main narrative content. Fallback storylets
        # are ambient events that only trigger when the narrative would otherwise
        # be stuck (no regular storylets available for N consecutive ticks).
        
        regular_storylets = [s for s in available_storylets if not s.is_fallback]
        fallback_storylets = [s for s in available_storylets if s.is_fallback]
        
        # ═══════════════════════════════════════════════════════════════════
        # STAGE 2: Precondition Filtering
        # ═══════════════════════════════════════════════════════════════════
        # Evaluate preconditions for each regular storylet. Only storylets
        # where ALL preconditions are satisfied become candidates.
        # Also check basic cooldown and "once" flags here.
        
        candidates = []
        for storylet in regular_storylets:
            # Check cooldown: Has enough time passed since last trigger?
            # Formula: current_tick - last_triggered >= cooldown
            if storylet.cooldown > 0:
                last_tick = tick_history.last_triggered.get(storylet.id, -999)
                current_tick = len(tick_history.ticks)
                if current_tick - last_tick < storylet.cooldown:
                    # Still on cooldown, skip this storylet
                    continue
            
            # Check "once" flag: Has this storylet already triggered?
            # Used for unique events like "Character Death", "Quest Complete"
            if storylet.once and tick_history.triggered_once.get(storylet.id, False):
                # Already triggered and marked as "once", skip
                continue
            
            # Evaluate all preconditions using hybrid evaluator
            # Supports both deterministic and AI-powered conditions
            # Returns: (bool: all_satisfied, List[str]: explanations)
            satisfied, explanations = self._evaluate_conditions_hybrid(
                storylet.preconditions,
                world_state,
                char_states,
                rel_states,
                project,
                config.ai_mode
            )
            
            if satisfied:
                # All preconditions met! Add to candidate pool
                candidates.append((storylet, explanations))
        
        # ═══════════════════════════════════════════════════════════════════
        # STAGE 3: Ordering Constraints (v0.7 NEW)
        # ═══════════════════════════════════════════════════════════════════
        # Filter candidates by requires_fired and forbids_fired.
        # This enables quest chains, mutually exclusive paths, and narrative
        # dependencies without complex precondition logic.
        
        candidates = self._filter_by_ordering_constraints(
            candidates,
            tick_history
        )
        
        # ═══════════════════════════════════════════════════════════════════
        # STAGE 4: Fallback Check (v0.7 NEW)
        # ═══════════════════════════════════════════════════════════════════
        # If no regular candidates remain, check if we should trigger fallback
        # storylets. This prevents the narrative from getting "stuck" when
        # no regular storylets can fire (e.g., waiting for player to gain
        # resources, time to pass, etc.).
        
        if not candidates:
            # Check if we should trigger fallback
            if (config.fallback_after_idle_ticks > 0 and 
                tick_history.idle_tick_count >= config.fallback_after_idle_ticks):
                # Use fallback storylets
                candidates = self._select_fallback_candidates(
                    fallback_storylets,
                    world_state,
                    char_states,
                    rel_states,
                    tick_history,
                    project,
                    config
                )
                
                if not candidates:
                    return [], ["No regular or fallback storylets available"]
                
                # Mark that we used fallback
                is_fallback_tick = True
            else:
                # No candidates and not time for fallback yet
                return [], ["No storylets satisfy preconditions"]
        else:
            is_fallback_tick = False
        
        # Step 5: Apply diversity penalty (tag-based)
        recent_tags = self._get_recent_tags(tick_history, config.diversity_window)
        
        weighted_candidates = []
        for storylet, explanations in candidates:
            weight = storylet.weight
            
            # Diversity penalty: reduce weight if tags appeared recently
            penalty_count = sum(1 for tag in storylet.tags if tag in recent_tags)
            if penalty_count > 0:
                weight *= (0.3 - config.diversity_penalty) ** penalty_count
            
            # Pacing adjustment: prefer storylets that move toward target intensity
            intensity_adjustment = self._calculate_intensity_adjustment(
                storylet,
                tick_history.current_intensity,
                config
            )
            weight *= intensity_adjustment
            
            weighted_candidates.append((storylet, weight, explanations))
        
        # Step 6: Sample based on weights
        total_weight = sum(w for _, w, _ in weighted_candidates)
        if total_weight <= 0:
            # Fallback: pick random
            selected_count = min(config.events_per_tick, len(weighted_candidates))
            selected = random.sample(weighted_candidates, selected_count)
        else:
            # Weighted sampling without replacement
            selected = []
            remaining = weighted_candidates.copy()
            
            for _ in range(min(config.events_per_tick, len(remaining))):
                if not remaining:
                    break
                
                # Normalize weights
                current_total = sum(w for _, w, _ in remaining)
                probs = [w / current_total for _, w, _ in remaining]
                
                # Sample one
                idx = random.choices(range(len(remaining)), weights=probs, k=1)[0]
                selected.append(remaining.pop(idx))
        
        # Build rationales
        rationales = []
        selected_storylets = []
        
        for storylet, weight, explanations in selected:
            selected_storylets.append(storylet)
            
            reason_parts = [
                f"Selected '{storylet.title}' (weight: {weight:.2f})",
                f"  Tags: {', '.join(storylet.tags)}",
                "  Satisfied conditions:"
            ]
            for exp in explanations:
                reason_parts.append(f"    {exp}")
            
            rationales.append("\n".join(reason_parts))
        
        return selected_storylets, rationales
    
    def tick(
        self,
        project: Project,
        thread_id: Optional[str],
        step_index: int,
        config: Optional[DirectorConfig] = None
    ) -> TickRecord:
        """
        Execute one world tick: select storylets, apply effects, record changes.
        
        Args:
            project: The story project
            thread_id: Story thread to tick (or None for standalone)
            step_index: Current step in the thread
            config: Director configuration (uses default if None)
        
        Returns:
            TickRecord with selected events and state changes
        """
        if config is None:
            config = DirectorConfig()
        
        # Get or create tick history for this thread
        tick_history_key = f"tick_history_{thread_id}" if thread_id else "tick_history_main"
        
        if not hasattr(project, 'tick_histories'):
            project.tick_histories = {}
        
        if tick_history_key not in project.tick_histories:
            project.tick_histories[tick_history_key] = TickHistory(
                thread_id=thread_id or "main"
            )
        
        tick_history = project.tick_histories[tick_history_key]
        tick_number = len(tick_history.ticks)
        
        # Compute current state
        world_state, char_states, rel_states = self.state_service.compute_state(
            project,
            thread_id,
            step_index
        )
        
        # Load storylets
        storylets = self.load_storylets(project)
        
        if not storylets:
            # No storylets available
            tick_record = TickRecord(
                tick_number=tick_number,
                step_index=step_index,
                intensity_before=tick_history.current_intensity,
                intensity_after=tick_history.current_intensity,
                events=[],
                state_diff={}
            )
            tick_history.ticks.append(tick_record)
            return tick_record
        
        # Select storylets
        selected, rationales = self.select_storylets(
            storylets,
            world_state,
            char_states,
            rel_states,
            tick_history,
            config,
            project
        )
        
        # Update idle tick count
        if not selected:
            tick_history.idle_tick_count += 1
        else:
            # Check if any selected storylets are NOT fallback
            has_regular_storylet = any(not s.is_fallback for s in selected)
            if has_regular_storylet:
                # Reset idle counter when regular storylets trigger
                tick_history.idle_tick_count = 0
            else:
                # Fallback storylets don't reset idle counter
                tick_history.idle_tick_count += 1
        
        # Create deep copies for diff comparison
        world_before = deepcopy(world_state)
        char_before = deepcopy(char_states)
        rel_before = deepcopy(rel_states)
        
        # Apply effects
        tick_events = []
        for storylet, rationale in zip(selected, rationales):
            # Apply each effect
            applied_effects = []
            for effect in storylet.effects:
                self.state_service._apply_effect(
                    effect,
                    world_state,
                    char_states,
                    rel_states
                )
                applied_effects.append({
                    "scope": effect.scope,
                    "target": effect.target,
                    "op": effect.op,
                    "path": effect.path,
                    "value": effect.value,
                    "reason": effect.reason
                })
            
            # Record event
            tick_event = TickEvent(
                storylet_id=storylet.id,
                storylet_title=storylet.title,
                tick_number=tick_number,
                satisfied_conditions=[line for line in rationale.split('\n') if '✓' in line],
                applied_effects=applied_effects,
                rationale=rationale
            )
            tick_events.append(tick_event)
            
            # Update tick history tracking
            tick_history.last_triggered[storylet.id] = tick_number
            if storylet.once:
                tick_history.triggered_once[storylet.id] = True
        
        # Compute state diff
        state_diff = self._compute_diff(
            world_before, char_before, rel_before,
            world_state, char_states, rel_states
        )
        
        # Update intensity
        intensity_before = tick_history.current_intensity
        intensity_change = sum(s.intensity_delta for s in selected)
        new_intensity = max(config.intensity_min, min(config.intensity_max, 
                           intensity_before + intensity_change))
        
        # Apply decay toward 0.5
        new_intensity += (0.5 - new_intensity) * config.intensity_decay
        tick_history.current_intensity = new_intensity
        
        # Create tick record
        tick_record = TickRecord(
            tick_number=tick_number,
            step_index=step_index,
            intensity_before=intensity_before,
            intensity_after=new_intensity,
            events=tick_events,
            state_diff=state_diff
        )
        
        tick_history.ticks.append(tick_record)
        
        return tick_record
    
    def _get_recent_tags(self, tick_history: TickHistory, window: int) -> set:
        """Get tags from recent ticks for diversity calculation"""
        recent_tags = set()
        start_idx = max(0, len(tick_history.ticks) - window)
        
        for tick_record in tick_history.ticks[start_idx:]:
            if tick_record is None:
                continue
            for event in tick_record.events:
                # Would need to look up storylet to get tags
                # For MVP, we'll track tags in TickEvent
                pass
        
        return recent_tags
    
    def _filter_by_ordering_constraints(
        self,
        candidates: List[Tuple[Storylet, List[str]]],
        tick_history: TickHistory
    ) -> List[Tuple[Storylet, List[str]]]:
        """
        Filter candidates based on ordering constraints (v0.7).
        
        This method implements narrative ordering logic without complex preconditions:
        
        **requires_fired**: "This storylet can only trigger AFTER these storylets have fired"
        - Use for: Quest chains, story progression, prerequisites
        - Example: "Quest Part 2" requires_fired: ["quest_part_1"]
        - Check: ALL required storylets must have triggered at least once
        
        **forbids_fired**: "This storylet can only trigger if these storylets have NOT fired"
        - Use for: Mutually exclusive paths, consequences of choices
        - Example: "Join Rebels" forbids_fired: ["join_guild"]
        - Check: NONE of the forbidden storylets must have triggered
        
        Why This Matters:
        Without ordering constraints, you'd need complex preconditions like:
            {"scope": "world", "path": "vars.quest_part_1_complete", "op": "==", "value": true}
        
        With ordering constraints, simply:
            requires_fired: ["quest_part_1"]
        
        This is:
        - More explicit (clear intent)
        - Easier to author (no manual state tracking)
        - Automatically maintained (Director updates triggered_once)
        
        Args:
            candidates: List of (Storylet, explanations) tuples from precondition filtering
            tick_history: TickHistory containing triggered_once mapping
                         (storylet_id → True if ever triggered, False/missing if not)
        
        Returns:
            Filtered list of (Storylet, explanations) tuples that satisfy ordering constraints
            
        Example:
            >>> # Setup: Quest chain
            >>> history = TickHistory(triggered_once={"quest_start": True})
            >>> candidates = [
            ...     (Storylet(id="quest_middle", requires_fired=["quest_start"]), []),
            ...     (Storylet(id="quest_end", requires_fired=["quest_middle"]), [])
            ... ]
            >>> filtered = service._filter_by_ordering_constraints(candidates, history)
            >>> # Result: Only quest_middle passes (quest_start fired, but quest_middle hasn't)
            >>> # quest_end blocked because quest_middle hasn't fired yet
        """
        filtered = []
        
        for storylet, explanations in candidates:
            # ═══════════════════════════════════════════════════════════
            # Check requires_fired: ALL required storylets must have fired
            # ═══════════════════════════════════════════════════════════
            # Loop through each required storylet ID and verify it has
            # triggered at least once. If ANY required storylet is missing,
            # this storylet is blocked.
            
            if storylet.requires_fired:
                all_required_fired = all(
                    tick_history.triggered_once.get(req_id, False)
                    for req_id in storylet.requires_fired
                )
                if not all_required_fired:
                    # Dependencies not met - skip this storylet
                    # Could log which requirements are missing for debugging:
                    # missing = [r for r in storylet.requires_fired 
                    #           if not tick_history.triggered_once.get(r, False)]
                    continue
            
            # ═══════════════════════════════════════════════════════════
            # Check forbids_fired: NONE of forbidden storylets must have fired
            # ═══════════════════════════════════════════════════════════
            # Loop through each forbidden storylet ID. If ANY forbidden
            # storylet has triggered, this storylet is blocked (it's now
            # "too late" for this path).
            
            if storylet.forbids_fired:
                any_forbidden_fired = any(
                    tick_history.triggered_once.get(forbid_id, False)
                    for forbid_id in storylet.forbids_fired
                )
                if any_forbidden_fired:
                    # Forbidden constraint violated - skip this storylet
                    # This prevents contradictory narrative paths:
                    # e.g., can't join rebels if already joined guild
                    continue
            
            # This storylet passes all ordering constraints!
            # Add to filtered list with original explanations intact
            filtered.append((storylet, explanations))
        
        return filtered
    
    def _select_fallback_candidates(
        self,
        fallback_storylets: List[Storylet],
        world_state: WorldState,
        char_states: Dict[str, CharacterState],
        rel_states: Dict[str, Any],
        tick_history: TickHistory,
        project: Project,
        config: DirectorConfig
    ) -> List[Tuple[Storylet, List[str]]]:
        """
        Select fallback storylet candidates (v0.7).
        
        Fallback storylets are "ambient" events that keep the narrative moving
        when regular storylets can't fire. Common reasons for needing fallbacks:
        - Player needs to accumulate resources
        - Time needs to pass for cooldowns to expire
        - World state needs to change before next plot point
        
        Design Philosophy:
        Instead of hard-blocking (narrative stuck), provide low-impact ambient events:
        - "Time passes quietly"
        - "Weather changes"
        - "Market activity"
        - "Background conversations"
        
        These maintain world dynamism without forcing major plot progression.
        
        Important: Fallback storylets STILL undergo precondition checks!
        This allows semi-conditional fallbacks like:
            {"id": "rain", "is_fallback": true, "preconditions": [{"path": "vars.season", "op": "==", "value": "spring"}]}
        
        Args:
            fallback_storylets: List of Storylet objects with is_fallback=True
            world_state, char_states, rel_states: Current game state for precondition evaluation
            tick_history: History for cooldown/once tracking (fallbacks can have cooldowns!)
        
        Returns:
            List of (Storylet, explanations) tuples that qualify as fallback options
            
        Example:
            >>> # Fallback after 3 idle ticks
            >>> fallbacks = [
            ...     Storylet(id="weather", is_fallback=True, preconditions=[], cooldown=2),
            ...     Storylet(id="crowd", is_fallback=True, preconditions=[], cooldown=2)
            ... ]
            >>> candidates = service._select_fallback_candidates(fallbacks, world, {}, {}, history)
            >>> # Returns both if not on cooldown, providing variety
        """
        candidates = []
        current_tick = len(tick_history.ticks)
        
        for storylet in fallback_storylets:
            # ═══════════════════════════════════════════════════════════
            # Check cooldown (fallbacks can have cooldowns for variety!)
            # ═══════════════════════════════════════════════════════════
            # Without cooldowns, same fallback would trigger repeatedly.
            # With cooldowns, you get variety: weather, then crowd, then weather...
            
            if storylet.cooldown > 0:
                last_tick = tick_history.last_triggered.get(storylet.id, -999)
                if current_tick - last_tick < storylet.cooldown:
                    # This fallback recently triggered, skip
                    continue
            
            # ═══════════════════════════════════════════════════════════
            # Check "once" flag (rare for fallbacks, but supported)
            # ═══════════════════════════════════════════════════════════
            # Example use case: "First Snow" (fallback, but only once per playthrough)
            
            if storylet.once and tick_history.triggered_once.get(storylet.id, False):
                # This "once" fallback already triggered
                continue
            
            # ═══════════════════════════════════════════════════════════
            # Evaluate preconditions (yes, fallbacks can have conditions!)
            # ═══════════════════════════════════════════════════════════
            # This allows contextual fallbacks:
            # - "Rain" only in spring/summer
            # - "Snow" only in winter
            # - "Market bustle" only during day
            
            # Evaluate preconditions using hybrid evaluator
            satisfied, explanations = self._evaluate_conditions_hybrid(
                storylet.preconditions,
                world_state,
                char_states,
                rel_states,
                project,
                config.ai_mode
            )
            
            if satisfied:
                # Add "(FALLBACK)" marker to explanations
                fallback_explanations = ["(FALLBACK STORYLET)"] + explanations
                candidates.append((storylet, fallback_explanations))
        
        # Fallback storylets also respect ordering constraints
        candidates = self._filter_by_ordering_constraints(
            candidates,
            tick_history
        )
        
        return candidates
    
    def _calculate_intensity_adjustment(
        self,
        storylet: Storylet,
        current_intensity: float,
        config: DirectorConfig
    ) -> float:
        """
        Calculate weight adjustment based on pacing preference.
        
        If intensity is high, prefer calming storylets (negative delta).
        If intensity is low, prefer escalating storylets (positive delta).
        """
        if config.pacing_preference == "calm":
            # Prefer calming regardless of current intensity
            if storylet.intensity_delta < 0:
                return 0.4
            elif storylet.intensity_delta > 0:
                return 0.7
        
        elif config.pacing_preference == "intense":
            # Prefer escalating regardless
            if storylet.intensity_delta > 0:
                return 0.4
            elif storylet.intensity_delta < 0:
                return 0.7
        
        else:  # balanced
            # Use peaks-and-valleys approach
            if current_intensity > 0.6 and storylet.intensity_delta < 0:
                return 1.3  # Moving away from high intensity
            elif current_intensity < 0.4 and storylet.intensity_delta > 0:
                return 1.3  # Moving away from low intensity
            elif current_intensity > 0.6 and storylet.intensity_delta > 0:
                return 0.8  # Don't pile on high intensity
            elif current_intensity < 0.4 and storylet.intensity_delta < 0:
                return 0.8  # Don't stay too calm
        
        return 0.3
    
    def _compute_diff(
        self,
        world_before: WorldState,
        char_before: Dict[str, CharacterState],
        rel_before: Dict[str, Any],
        world_after: WorldState,
        char_after: Dict[str, CharacterState],
        rel_after: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Compute human-readable diff of state changes"""
        diff = {}
        
        # World vars changes
        world_changes = {}
        all_vars = set(world_before.vars.keys()) | set(world_after.vars.keys())
        for key in all_vars:
            before_val = world_before.vars.get(key)
            after_val = world_after.vars.get(key)
            if before_val != after_val:
                world_changes[key] = {"before": before_val, "after": after_val}
        
        if world_changes:
            diff["world"] = world_changes
        
        # Character changes
        char_changes = {}
        for char_id in set(char_before.keys()) | set(char_after.keys()):
            before_state = char_before.get(char_id)
            after_state = char_after.get(char_id)
            
            if not before_state or not after_state:
                continue
            
            char_diff = {}
            if before_state.mood != after_state.mood:
                char_diff["mood"] = {"before": before_state.mood, "after": after_state.mood}
            if before_state.status != after_state.status:
                char_diff["status"] = {"before": before_state.status, "after": after_state.status}
            if before_state.location != after_state.location:
                char_diff["location"] = {"before": before_state.location, "after": after_state.location}
            if before_state.active_traits != after_state.active_traits:
                char_diff["traits"] = {"before": before_state.active_traits, "after": after_state.active_traits}
            if before_state.active_goals != after_state.active_goals:
                char_diff["goals"] = {"before": before_state.active_goals, "after": after_state.active_goals}
            
            # Vars
            var_changes = {}
            all_vars = set(before_state.vars.keys()) | set(after_state.vars.keys())
            for key in all_vars:
                before_val = before_state.vars.get(key)
                after_val = after_state.vars.get(key)
                if before_val != after_val:
                    var_changes[key] = {"before": before_val, "after": after_val}
            if var_changes:
                char_diff["vars"] = var_changes
            
            if char_diff:
                char_changes[char_id] = char_diff
        
        if char_changes:
            diff["characters"] = char_changes
        
        # Relationship changes
        rel_changes = {}
        for rel_key in set(rel_before.keys()) | set(rel_after.keys()):
            before_rel = rel_before.get(rel_key, {})
            after_rel = rel_after.get(rel_key, {})
            
            all_keys = set(before_rel.keys()) | set(after_rel.keys())
            rel_diff = {}
            for key in all_keys:
                before_val = before_rel.get(key)
                after_val = after_rel.get(key)
                if before_val != after_val:
                    rel_diff[key] = {"before": before_val, "after": after_val}
            
            if rel_diff:
                rel_changes[rel_key] = rel_diff
        
        if rel_changes:
            diff["relationships"] = rel_changes
        
        return diff
    
    def _evaluate_conditions_hybrid(
        self,
        preconditions: List[Precondition],
        world_state: WorldState,
        char_states: Dict[str, CharacterState],
        rel_states: Dict[str, Any],
        project: Project,
        ai_mode: str
    ) -> Tuple[bool, List[str]]:
        """
        Evaluate preconditions using hybrid deterministic+AI approach.
        
        This method routes condition evaluation based on AI mode:
        - "deterministic": Only use rule-based evaluation (fast, default)
        - "ai_assisted": Use AI for NL conditions, rules for others
        - "ai_primary": Use AI when available, rules as fallback
        
        Args:
            preconditions: List of conditions to evaluate
            world_state: Current world state
            char_states: Character states
            rel_states: Relationship states
            project: Project context (for LLM settings)
            ai_mode: Which evaluation mode to use
        
        Returns:
            (all_satisfied, explanations) - same as ConditionsEvaluator.evaluate_all
        
        Example:
            >>> # Mix of deterministic and NL conditions
            >>> preconditions = [
            ...     Precondition(path="world.vars.tension", op=">=", value=70),
            ...     Precondition(nl_condition="Alice is feeling desperate")
            ... ]
            >>> satisfied, explanations = self._evaluate_conditions_hybrid(
            ...     preconditions, world, chars, rels, project, "ai_assisted"
            ... )
        """
        if not preconditions:
            return True, ["No preconditions (always satisfied)"]
        
        if ai_mode == "deterministic":
            # Pure rule-based, no AI
            # NL conditions will be skipped (ConditionsEvaluator can't handle them)
            return self.conditions_evaluator.evaluate_all(
                preconditions, world_state, char_states, rel_states
            )
        
        # AI-assisted or AI-primary modes
        explanations = []
        all_satisfied = True
        
        for cond in preconditions:
            if cond.is_nl_condition():
                # This is a natural language condition
                if ai_mode in ["ai_assisted", "ai_primary"]:
                    # Use AI evaluator
                    satisfied, explanation = self.ai_conditions_evaluator.evaluate(
                        cond, world_state, char_states, rel_states, project
                    )
                    explanations.append(explanation)
                    if not satisfied:
                        all_satisfied = False
                else:
                    # Should not reach here, but handle gracefully
                    explanations.append(f"⚠ NL condition in deterministic mode: {cond.nl_condition}")
                    all_satisfied = False
            else:
                # This is a deterministic condition
                satisfied, explanation = self.conditions_evaluator.evaluate(
                    cond, world_state, char_states, rel_states
                )
                explanations.append(explanation)
                if not satisfied:
                    all_satisfied = False
        
        return all_satisfied, explanations
