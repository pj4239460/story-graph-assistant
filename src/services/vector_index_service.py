"""
Vector Index Service - Manages vector database indexing for projects
"""
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..models.project import Project
    from ..infra.vector_db import VectorDatabase


class VectorIndexService:
    """Service to keep vector database in sync with project data"""
    
    @staticmethod
    def index_project(project: 'Project', vector_db: 'VectorDatabase'):
        """Index all characters and scenes in a project"""
        if not vector_db.is_available():
            print("Vector database not available, skipping indexing")
            return
            
        print(f"Indexing project: {project.name}")
        
        try:
            # Index all characters
            char_count = len(project.characters)
            print(f"Found {char_count} characters to index")
            for idx, (char_id, char) in enumerate(project.characters.items(), 1):
                try:
                    print(f"  [{idx}/{char_count}] Indexing character: {char.name}")
                    char_data = {
                        "name": char.name,
                        "alias": char.alias,
                        "description": char.description,
                        "traits": char.traits,
                        "goals": char.goals,
                        "fears": char.fears
                    }
                    vector_db.index_character(project.id, char_id, char_data)
                    print(f"  ✓ Character {char.name} indexed")
                except Exception as e:
                    print(f"  ✗ Warning: Failed to index character {char_id}: {e}")
                    import traceback
                    traceback.print_exc()
            
            # Index all scenes
            scene_count = len(project.scenes)
            print(f"Found {scene_count} scenes to index")
            for idx, (scene_id, scene) in enumerate(project.scenes.items(), 1):
                try:
                    print(f"  [{idx}/{scene_count}] Indexing scene: {scene.title}")
                    scene_data = {
                        "title": scene.title,
                        "chapter": scene.chapter,
                        "summary": scene.summary,
                        "body": scene.body,
                        "tags": scene.tags
                    }
                    vector_db.index_scene(project.id, scene_id, scene_data)
                    print(f"  ✓ Scene {scene.title} indexed")
                except Exception as e:
                    print(f"  ✗ Warning: Failed to index scene {scene_id}: {e}")
                    import traceback
                    traceback.print_exc()
            
            print(f"✓ Indexed {len(project.characters)} characters and {len(project.scenes)} scenes")
        except Exception as e:
            print(f"ERROR: Failed to index project: {e}")
            import traceback
            traceback.print_exc()
    
    @staticmethod
    def index_character(project_id: str, char_id: str, char_data: dict, vector_db: 'VectorDatabase'):
        """Index a single character"""
        vector_db.index_character(project_id, char_id, char_data)
    
    @staticmethod
    def index_scene(project_id: str, scene_id: str, scene_data: dict, vector_db: 'VectorDatabase'):
        """Index a single scene"""
        vector_db.index_scene(project_id, scene_id, scene_data)
    
    @staticmethod
    def remove_character(project_id: str, char_id: str, vector_db: 'VectorDatabase'):
        """Remove a character from index"""
        vector_db.delete_character(project_id, char_id)
    
    @staticmethod
    def remove_scene(project_id: str, scene_id: str, vector_db: 'VectorDatabase'):
        """Remove a scene from index"""
        vector_db.delete_scene(project_id, scene_id)
