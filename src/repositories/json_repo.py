"""
JSON-based project storage implementation
"""
from __future__ import annotations
import json
from datetime import datetime
from pathlib import Path

from .base import ProjectRepository
from ..models.project import Project


class JsonProjectRepository(ProjectRepository):
    """JSON file storage implementation"""
    
    def load(self, path: str) -> Project:
        """Load project from JSON file"""
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"Project file not found: {path}")
        
        data = json.loads(p.read_text(encoding="utf-8"))
        project = Project.model_validate(data)
        return project
    
    def save(self, project: Project, path: str) -> None:
        """Save project to JSON file"""
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        
        project.updatedAt = datetime.utcnow()
        text = project.model_dump_json(indent=2, ensure_ascii=False)
        p.write_text(text, encoding="utf-8")
