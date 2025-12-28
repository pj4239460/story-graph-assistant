"""
Project Service - Project management service
"""
from __future__ import annotations
from datetime import datetime
import uuid

from ..models.project import Project
from ..repositories.base import ProjectRepository


class ProjectService:
    """Project management service"""
    
    def __init__(self, repository: ProjectRepository):
        self.repository = repository
        self.current_project: Project | None = None
        self.current_path: str | None = None
    
    def create_project(self, name: str, locale: str = "zh") -> Project:
        """Create new project"""
        project = Project(
            id=str(uuid.uuid4()),
            name=name,
            locale=locale,
            createdAt=datetime.utcnow(),
            updatedAt=datetime.utcnow(),
        )
        self.current_project = project
        return project
    
    def load_project(self, path: str) -> Project:
        """Load project from file"""
        project = self.repository.load(path)
        self.current_project = project
        self.current_path = path
        return project
    
    def save_project(self, path: str | None = None) -> None:
        """Save project to file"""
        if self.current_project is None:
            raise ValueError("No project loaded")
        
        save_path = path or self.current_path
        if save_path is None:
            raise ValueError("No path specified")
        
        self.repository.save(self.current_project, save_path)
        self.current_path = save_path
    
    def get_project(self) -> Project:
        """Get current project"""
        if self.current_project is None:
            raise ValueError("No project loaded")
        return self.current_project
    
    def has_project(self) -> bool:
        """Check if project is loaded"""
        return self.current_project is not None
