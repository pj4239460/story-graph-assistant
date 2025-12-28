"""
Character Service - Character management service
"""
from __future__ import annotations
import uuid
from typing import List, Optional

from ..models.project import Project
from ..models.character import Character, Relationship


class CharacterService:
    """Character management service"""
    
    def create_character(
        self,
        project: Project,
        name: str,
        description: str = "",
    ) -> Character:
        """Create character"""
        character = Character(
            id=str(uuid.uuid4()),
            name=name,
            description=description,
        )
        project.characters[character.id] = character
        return character
    
    def get_character(self, project: Project, character_id: str) -> Optional[Character]:
        """Get character by ID"""
        return project.characters.get(character_id)
    
    def update_character(
        self,
        project: Project,
        character_id: str,
        **kwargs
    ) -> Character:
        """Update character properties"""
        character = project.characters.get(character_id)
        if character is None:
            raise ValueError(f"Character {character_id} not found")
        
        for key, value in kwargs.items():
            if hasattr(character, key):
                setattr(character, key, value)
        
        return character
    
    def delete_character(self, project: Project, character_id: str) -> None:
        """Delete character"""
        if character_id in project.characters:
            del project.characters[character_id]
    
    def get_all_characters(self, project: Project) -> List[Character]:
        """Get all characters"""
        return list(project.characters.values())
    
    def add_relationship(
        self,
        project: Project,
        character_id: str,
        target_id: str,
        summary: str,
    ) -> None:
        """Add character relationship"""
        character = project.characters.get(character_id)
        if character is None:
            raise ValueError(f"Character {character_id} not found")
        
        relationship = Relationship(targetId=target_id, summary=summary)
        character.relationships.append(relationship)

