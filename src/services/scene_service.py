"""
Scene Service - Scene management service
"""
from __future__ import annotations
import uuid
from typing import List, Optional

from ..models.project import Project
from ..models.scene import Scene, Choice


class SceneService:
    """Scene management service"""
    
    def create_scene(
        self,
        project: Project,
        title: str,
        body: str = "",
        chapter: Optional[str] = None,
    ) -> Scene:
        """Create a new scene"""
        scene = Scene(
            id=str(uuid.uuid4()),
            title=title,
            body=body,
            chapter=chapter,
        )
        project.scenes[scene.id] = scene
        return scene
    
    def get_scene(self, project: Project, scene_id: str) -> Optional[Scene]:
        """Get scene by ID"""
        return project.scenes.get(scene_id)
    
    def update_scene(
        self,
        project: Project,
        scene_id: str,
        **kwargs
    ) -> Scene:
        """Update scene properties"""
        scene = project.scenes.get(scene_id)
        if scene is None:
            raise ValueError(f"Scene {scene_id} not found")
        
        # Update fields
        for key, value in kwargs.items():
            if hasattr(scene, key):
                setattr(scene, key, value)
        
        return scene
    
    def delete_scene(self, project: Project, scene_id: str) -> None:
        """Delete scene"""
        if scene_id in project.scenes:
            del project.scenes[scene_id]
        
        # Clean up choices pointing to this scene
        for scene in project.scenes.values():
            scene.choices = [
                choice for choice in scene.choices
                if choice.targetSceneId != scene_id
            ]
    
    def add_choice(
        self,
        project: Project,
        scene_id: str,
        text: str,
        target_scene_id: Optional[str] = None,
    ) -> Choice:
        """Add choice to scene"""
        scene = project.scenes.get(scene_id)
        if scene is None:
            raise ValueError(f"Scene {scene_id} not found")
        
        choice = Choice(
            id=str(uuid.uuid4()),
            text=text,
            targetSceneId=target_scene_id,
        )
        scene.choices.append(choice)
        return choice
    
    def get_all_scenes(self, project: Project) -> List[Scene]:
        """Get all scenes"""
        return list(project.scenes.values())
    
    def get_scene_graph(self, project: Project) -> dict:
        """
        Get scene graph structure for visualization
        
        Returns:
            {
                "nodes": [{"id": "...", "title": "...", ...}],
                "edges": [{"from": "...", "to": "...", "label": "..."}]
            }
        """
        nodes = []
        edges = []
        
        for scene in project.scenes.values():
            nodes.append({
                "id": scene.id,
                "title": scene.title,
                "isEnding": scene.isEnding,
                "chapter": scene.chapter,
            })
            
            for choice in scene.choices:
                if choice.targetSceneId:
                    edges.append({
                        "from": scene.id,
                        "to": choice.targetSceneId,
                        "label": choice.text,
                    })
        
        return {"nodes": nodes, "edges": edges}

