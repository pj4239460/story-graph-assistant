"""
Event data models
"""
from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel


class Event(BaseModel):
    """Timeline event"""
    id: str
    name: str
    description: str = ""
    sceneIds: List[str] = []  # Associated scenes
    characterIds: List[str] = []  # Involved characters
    timeIndex: int = 0
    timeLabel: Optional[str] = None
    tags: List[str] = []
