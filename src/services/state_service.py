"""
State Service - Compute dynamic character/world state by replaying effects along story threads
"""
from __future__ import annotations
from typing import Dict, List, Tuple, Any, Optional
from copy import deepcopy

from ..models.project import Project
from ..models.character import CharacterState
from ..models.world import Effect, WorldState


class StateService:
    """
    Service for computing dynamic state at any point in a story thread
    
    Core concept: Character/World state changes over time as the story progresses.
    - Character base profile is static (stored in Character model)
    - CharacterState is dynamic (computed by applying Effects from scenes)
    - Each scene can have Effects that modify character/relationship/world state
    - By replaying a thread (sequence of scenes), we get "state at step N"
    """
    
    def compute_state(
        self,
        project: Project,
        thread_id: str,
        step_index: int
    ) -> Tuple[WorldState, Dict[str, CharacterState], Dict[str, Any]]:
        """
        Compute the effective state at a specific step in a story thread
        
        Args:
            project: Project object
            thread_id: Story thread ID to follow
            step_index: Which step to compute state for (0-based index)
            
        Returns:
            (world_state, character_states, relationship_states)
            - world_state: WorldState with vars/facts at this point
            - character_states: {character_id: CharacterState}
            - relationship_states: {relation_key: relation_data}
        """
        # Get the thread
        if thread_id not in project.threads:
            raise ValueError(f"Thread {thread_id} not found in project")
        
        thread = project.threads[thread_id]
        
        # Initialize states from base data
        world_state = deepcopy(project.worldState)
        character_states = self._init_character_states(project)
        relationship_states = {}
        
        # Replay effects up to step_index
        for i, step in enumerate(thread.steps):
            if i > step_index:
                break
            
            scene_id = step.sceneId
            if scene_id not in project.scenes:
                continue
            
            scene = project.scenes[scene_id]
            
            # Apply all effects from this scene
            for effect in scene.effects:
                self._apply_effect(
                    effect,
                    world_state,
                    character_states,
                    relationship_states
                )
        
        return world_state, character_states, relationship_states
    
    def _init_character_states(self, project: Project) -> Dict[str, CharacterState]:
        """Initialize character states from base Character profiles"""
        states = {}
        for char_id, char in project.characters.items():
            state = CharacterState(
                characterId=char_id,
                active_traits=char.traits.copy(),
                active_goals=char.goals.copy(),
                active_fears=char.fears.copy(),
            )
            states[char_id] = state
        return states
    
    def _apply_effect(
        self,
        effect: Effect,
        world_state: WorldState,
        character_states: Dict[str, CharacterState],
        relationship_states: Dict[str, Any]
    ):
        """
        Apply a single effect to the current state
        
        Effect operations:
        - set: Replace the value at path
        - add: Append to list or increment number
        - remove: Remove from list or delete key
        - merge: Deep merge dicts
        """
        if effect.scope == "character":
            self._apply_character_effect(effect, character_states)
        elif effect.scope == "relationship":
            self._apply_relationship_effect(effect, relationship_states)
        elif effect.scope == "world":
            self._apply_world_effect(effect, world_state)
    
    def _apply_character_effect(
        self,
        effect: Effect,
        character_states: Dict[str, CharacterState]
    ):
        """Apply effect to a character's state"""
        char_id = effect.target
        if char_id not in character_states:
            return
        
        char_state = character_states[char_id]
        path_parts = effect.path.split('.')
        
        # Simple path resolution for common cases
        if effect.path in ["mood", "state.mood"]:
            char_state.mood = effect.value if effect.op == "set" else char_state.mood
        elif effect.path in ["status", "state.status"]:
            char_state.status = effect.value if effect.op == "set" else char_state.status
        elif effect.path in ["location", "state.location"]:
            char_state.location = effect.value if effect.op == "set" else char_state.location
        elif effect.path == "traits":
            if effect.op == "add" and effect.value not in char_state.active_traits:
                char_state.active_traits.append(effect.value)
            elif effect.op == "remove" and effect.value in char_state.active_traits:
                char_state.active_traits.remove(effect.value)
        elif effect.path == "goals":
            if effect.op == "add" and effect.value not in char_state.active_goals:
                char_state.active_goals.append(effect.value)
            elif effect.op == "remove" and effect.value in char_state.active_goals:
                char_state.active_goals.remove(effect.value)
        elif effect.path == "fears":
            if effect.op == "add" and effect.value not in char_state.active_fears:
                char_state.active_fears.append(effect.value)
            elif effect.op == "remove" and effect.value in char_state.active_fears:
                char_state.active_fears.remove(effect.value)
        elif path_parts[0] == "vars":
            # Custom variables like vars.trust_level
            var_name = '.'.join(path_parts[1:])
            if effect.op == "set":
                char_state.vars[var_name] = effect.value
            elif effect.op == "add" and isinstance(effect.value, (int, float)):
                char_state.vars[var_name] = char_state.vars.get(var_name, 0) + effect.value
            elif effect.op == "remove":
                char_state.vars.pop(var_name, None)
    
    def _apply_relationship_effect(
        self,
        effect: Effect,
        relationship_states: Dict[str, Any]
    ):
        """Apply effect to a relationship"""
        relation_key = effect.target  # e.g., "alice|bob"
        
        if effect.op == "set":
            if relation_key not in relationship_states:
                relationship_states[relation_key] = {}
            
            # Parse path like "trust" or "status"
            path_parts = effect.path.split('.')
            if len(path_parts) == 1:
                relationship_states[relation_key][effect.path] = effect.value
            else:
                # Nested path handling (simplified)
                current = relationship_states[relation_key]
                for part in path_parts[:-1]:
                    if part not in current:
                        current[part] = {}
                    current = current[part]
                current[path_parts[-1]] = effect.value
        
        elif effect.op == "add":
            if relation_key not in relationship_states:
                relationship_states[relation_key] = {}
            
            current_val = relationship_states[relation_key].get(effect.path, 0)
            if isinstance(effect.value, (int, float)):
                relationship_states[relation_key][effect.path] = current_val + effect.value
    
    def _apply_world_effect(self, effect: Effect, world_state: WorldState):
        """Apply effect to world state"""
        path_parts = effect.path.split('.')
        
        if path_parts[0] == "vars":
            # World variables like vars.rumor_spread
            var_name = '.'.join(path_parts[1:])
            if effect.op == "set":
                world_state.vars[var_name] = effect.value
            elif effect.op == "add":
                if isinstance(effect.value, (int, float)):
                    world_state.vars[var_name] = world_state.vars.get(var_name, 0) + effect.value
            elif effect.op == "remove":
                world_state.vars.pop(var_name, None)
    
    def diff_state(
        self,
        project: Project,
        thread_id: str,
        from_step: int,
        to_step: int
    ) -> Dict[str, Any]:
        """
        Compute the difference between states at two steps
        
        Returns:
            {
                "characters": {char_id: {field: (old_val, new_val)}},
                "relationships": {relation_key: {field: (old_val, new_val)}},
                "world": {var_name: (old_val, new_val)}
            }
        """
        # Get states at both steps
        world_from, chars_from, rels_from = self.compute_state(project, thread_id, from_step)
        world_to, chars_to, rels_to = self.compute_state(project, thread_id, to_step)
        
        diff = {
            "characters": {},
            "relationships": {},
            "world": {}
        }
        
        # Compare character states
        for char_id in set(chars_from.keys()) | set(chars_to.keys()):
            char_diff = {}
            state_from = chars_from.get(char_id)
            state_to = chars_to.get(char_id)
            
            if state_from and state_to:
                # Check each field
                if state_from.mood != state_to.mood:
                    char_diff["mood"] = (state_from.mood, state_to.mood)
                if state_from.status != state_to.status:
                    char_diff["status"] = (state_from.status, state_to.status)
                if set(state_from.active_traits) != set(state_to.active_traits):
                    char_diff["traits"] = (state_from.active_traits, state_to.active_traits)
                if state_from.vars != state_to.vars:
                    char_diff["vars"] = (state_from.vars, state_to.vars)
            
            if char_diff:
                diff["characters"][char_id] = char_diff
        
        # Compare relationships
        for rel_key in set(rels_from.keys()) | set(rels_to.keys()):
            if rels_from.get(rel_key) != rels_to.get(rel_key):
                diff["relationships"][rel_key] = (rels_from.get(rel_key), rels_to.get(rel_key))
        
        # Compare world vars
        for var_name in set(world_from.vars.keys()) | set(world_to.vars.keys()):
            if world_from.vars.get(var_name) != world_to.vars.get(var_name):
                diff["world"][var_name] = (world_from.vars.get(var_name), world_to.vars.get(var_name))
        
        return diff
    
    def get_character_state_at_step(
        self,
        project: Project,
        thread_id: str,
        step_index: int,
        character_id: str
    ) -> Optional[CharacterState]:
        """Convenience method to get a single character's state at a specific step"""
        _, char_states, _ = self.compute_state(project, thread_id, step_index)
        return char_states.get(character_id)
