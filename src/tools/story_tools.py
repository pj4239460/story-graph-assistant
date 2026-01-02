"""
Story-related Tools for Agent
"""
from typing import Dict, Any, List
from .base_tool import BaseTool
from ..models.project import Project


class GetAllCharactersTool(BaseTool):
    """Tool to get all characters in the story"""
    
    def __init__(self, project: Project):
        self.project = project
    
    @property
    def name(self) -> str:
        return "get_all_characters"
    
    @property
    def description(self) -> str:
        return "Get a list of all characters in the story with their names, aliases, and brief descriptions"
    
    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {},
            "required": []
        }
    
    def execute(self, **kwargs) -> str:
        """Get all characters"""
        if not self.project.characters:
            return "No characters found in the story."
        
        result = f"Total characters: {len(self.project.characters)}\n\n"
        for char in self.project.characters:
            aliases = f" (aka {', '.join(char.aliases)})" if char.aliases else ""
            traits = f"\nTraits: {', '.join(char.traits[:3])}" if char.traits else ""
            result += f"• {char.name}{aliases}{traits}\n"
            if char.description:
                desc = char.description[:100] + "..." if len(char.description) > 100 else char.description
                result += f"  Description: {desc}\n"
            result += "\n"
        
        return result


class GetCharacterByNameTool(BaseTool):
    """Tool to get detailed information about a specific character"""
    
    def __init__(self, project: Project):
        self.project = project
    
    @property
    def name(self) -> str:
        return "get_character_by_name"
    
    @property
    def description(self) -> str:
        return "Get detailed information about a specific character by name or alias"
    
    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Character name or alias to search for"
                }
            },
            "required": ["name"]
        }
    
    def execute(self, name: str, **kwargs) -> str:
        """Get character by name"""
        name_lower = name.lower()
        
        for char in self.project.characters.values():
            if (char.name.lower() == name_lower or 
                (char.alias and char.alias.lower() == name_lower)):
                
                result = f"Character: {char.name}\n"
                if char.alias:
                    result += f"Alias: {char.alias}\n"
                if char.description:
                    result += f"\nDescription:\n{char.description}\n"
                if char.traits:
                    result += f"\nTraits: {', '.join(char.traits)}\n"
                if char.goals:
                    result += f"\nGoals: {', '.join(char.goals)}\n"
                if char.relationships:
                    result += f"\nRelationships:\n"
                    for rel in char.relationships:
                        result += f"  • {rel.targetName}: {rel.relationType}\n"
                
                return result
        
        return f"Character '{name}' not found. Available characters: {', '.join(c.name for c in self.project.characters)}"


class GetAllScenesTool(BaseTool):
    """Tool to get all scenes in the story"""
    
    def __init__(self, project: Project):
        self.project = project
    
    @property
    def name(self) -> str:
        return "get_all_scenes"
    
    @property
    def description(self) -> str:
        return "Get a list of all scenes in the story with titles, chapters, and summaries"
    
    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {},
            "required": []
        }
    
    def execute(self, **kwargs) -> str:
        """Get all scenes"""
        if not self.project.scenes:
            return "No scenes found in the story."
        
        result = f"Total scenes: {len(self.project.scenes)}\n\n"
        
        # Group by chapter
        chapters = {}
        for scene in self.project.scenes.values():
            chapter = scene.chapter or "No Chapter"
            if chapter not in chapters:
                chapters[chapter] = []
            chapters[chapter].append(scene)
        
        for chapter, scenes in sorted(chapters.items()):
            result += f"\n=== {chapter} ===\n"
            for scene in scenes:
                result += f"\n{scene.id}. {scene.title}\n"
                if scene.summary:
                    summary = scene.summary[:150] + "..." if len(scene.summary) > 150 else scene.summary
                    result += f"   Summary: {summary}\n"
                if scene.tags:
                    result += f"   Tags: {', '.join(scene.tags)}\n"
        
        return result


class GetSceneByIdTool(BaseTool):
    """Tool to get detailed information about a specific scene"""
    
    def __init__(self, project: Project):
        self.project = project
    
    @property
    def name(self) -> str:
        return "get_scene_by_id"
    
    @property
    def description(self) -> str:
        return "Get detailed information about a specific scene by its ID"
    
    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "scene_id": {
                    "type": "string",
                    "description": "Scene ID to retrieve"
                }
            },
            "required": ["scene_id"]
        }
    
    def execute(self, scene_id: str, **kwargs) -> str:
        """Get scene by ID"""
        for scene in self.project.scenes.values():
            if scene.id == scene_id:
                result = f"Scene: {scene.title}\n"
                result += f"ID: {scene.id}\n"
                if scene.chapter:
                    result += f"Chapter: {scene.chapter}\n"
                if scene.summary:
                    result += f"\nSummary:\n{scene.summary}\n"
                if scene.body:
                    body = scene.body[:500] + "..." if len(scene.body) > 500 else scene.body
                    result += f"\nContent:\n{body}\n"
                if scene.choices:
                    result += f"\nChoices ({len(scene.choices)}):\n"
                    for choice in scene.choices:
                        result += f"  → {choice.text} (leads to: {choice.nextSceneId or 'None'})\n"
                if scene.tags:
                    result += f"\nTags: {', '.join(scene.tags)}\n"
                
                return result
        
        return f"Scene with ID '{scene_id}' not found."


class SearchScenesTool(BaseTool):
    """Tool to search scenes by keywords"""
    
    def __init__(self, project: Project):
        self.project = project
    
    @property
    def name(self) -> str:
        return "search_scenes"
    
    @property
    def description(self) -> str:
        return "Search for scenes containing specific keywords in title, summary, or content"
    
    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "keyword": {
                    "type": "string",
                    "description": "Keyword to search for in scenes"
                }
            },
            "required": ["keyword"]
        }
    
    def execute(self, keyword: str, **kwargs) -> str:
        """Search scenes by keyword"""
        keyword_lower = keyword.lower()
        matching_scenes = []
        
        for scene in self.project.scenes.values():
            if (keyword_lower in scene.title.lower() or
                (scene.summary and keyword_lower in scene.summary.lower()) or
                (scene.body and keyword_lower in scene.body.lower()) or
                any(keyword_lower in tag.lower() for tag in scene.tags)):
                matching_scenes.append(scene)
        
        if not matching_scenes:
            return f"No scenes found containing keyword '{keyword}'."
        
        result = f"Found {len(matching_scenes)} scene(s) containing '{keyword}':\n\n"
        for scene in matching_scenes:
            result += f"• {scene.id}. {scene.title}\n"
            if scene.chapter:
                result += f"  Chapter: {scene.chapter}\n"
            if scene.summary:
                summary = scene.summary[:100] + "..." if len(scene.summary) > 100 else scene.summary
                result += f"  Summary: {summary}\n"
            result += "\n"
        
        return result


class CountEndingsTool(BaseTool):
    """Tool to count the number of endings in the story"""
    
    def __init__(self, project: Project):
        self.project = project
    
    @property
    def name(self) -> str:
        return "count_endings"
    
    @property
    def description(self) -> str:
        return "Count how many ending scenes exist in the story (scenes with no choices or outgoing connections)"
    
    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {},
            "required": []
        }
    
    def execute(self, **kwargs) -> str:
        """Count endings"""
        endings = []
        
        for scene in self.project.scenes.values():
            # A scene is an ending if it has no choices or all choices lead nowhere
            if not scene.choices or all(not choice.nextSceneId for choice in scene.choices):
                endings.append(scene)
        
        if not endings:
            return "No clear endings found in the story. All scenes have outgoing choices."
        
        result = f"Found {len(endings)} ending(s):\n\n"
        for scene in endings:
            result += f"• {scene.id}. {scene.title}\n"
            if scene.chapter:
                result += f"  Chapter: {scene.chapter}\n"
            if scene.tags and any('ending' in tag.lower() or '结局' in tag.lower() for tag in scene.tags):
                result += f"  (Tagged as ending)\n"
            result += "\n"
        
        return result


class GetWorldFactsTool(BaseTool):
    """Tool to get world-building facts"""
    
    def __init__(self, project: Project):
        self.project = project
    
    @property
    def name(self) -> str:
        return "get_world_facts"
    
    @property
    def description(self) -> str:
        return "Get world-building facts and lore information about the story universe"
    
    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {},
            "required": []
        }
    
    def execute(self, **kwargs) -> str:
        """Get world facts"""
        facts_list = list(self.project.worldState.facts.values()) if self.project.worldState.facts else []
        if not facts_list:
            return "No world-building facts have been extracted yet."
        
        result = f"World Facts ({len(facts_list)} total):\n\n"
        
        # Group by category if available
        categorized = {}
        for fact in facts_list:
            category = getattr(fact, 'category', 'General')
            if category not in categorized:
                categorized[category] = []
            categorized[category].append(fact)
        
        for category, facts in sorted(categorized.items()):
            if len(categorized) > 1:
                result += f"\n=== {category} ===\n"
            for fact in facts:
                result += f"• {fact.content}\n"
                if hasattr(fact, 'source') and fact.source:
                    result += f"  (Source: Scene {fact.source})\n"
        
        return result
