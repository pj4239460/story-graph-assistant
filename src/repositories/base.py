"""
Project Repository base interface
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from ..models.project import Project


class ProjectRepository(ABC):
    """Project storage interface"""
    
    @abstractmethod
    def load(self, path: str) -> Project:
        """Load project from storage"""
        ...
    
    @abstractmethod
    def save(self, project: Project, path: str) -> None:
        """Save project to storage"""
        ...
