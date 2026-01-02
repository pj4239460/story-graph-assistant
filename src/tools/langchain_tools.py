"""
LangChain Tools for Story Agent
Refactored to use @tool decorator for LangGraph compatibility
"""
from typing import List, Optional
from langchain.tools import tool
from ..models.project import Project


# Tool functions with @tool decorator
@tool
def get_all_characters(project: Project) -> str:
    """Get a list of all characters in the story with their names, aliases, and brief descriptions.
    
    Use this tool when the user asks questions like:
    - "现在整个故事中有几个角色？" / "How many characters are in the story?"
    - "给我列出所有的角色" / "List all characters"
    - "谁是这个故事的人物？" / "Who are the characters?"
    """
    if not project.characters:
        return "No characters found in the story."
    
    result = f"Total characters: {len(project.characters)}\n\n"
    for char in project.characters:
        aliases = f" (aka {', '.join(char.aliases)})" if char.aliases else ""
        traits = f"\nTraits: {', '.join(char.traits[:3])}" if char.traits else ""
        result += f"• {char.name}{aliases}{traits}\n"
        if char.description:
            desc = char.description[:100] + "..." if len(char.description) > 100 else char.description
            result += f"  Description: {desc}\n"
        result += "\n"
    
    return result


@tool
def get_character_by_name(name: str, project: Project) -> str:
    """Get detailed information about a specific character by name or alias.
    
    Args:
        name: Character name or alias to search for
        
    Use this tool when the user asks about a specific character like:
    - "陈墨是谁？" / "Who is Chen Mo?"
    - "告诉我关于林雪薇的信息" / "Tell me about Lin Xuewei"
    - "神秘女人有什么特征？" / "What are the mysterious woman's traits?"
    """
    name_lower = name.lower()
    
    for char in project.characters:
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
    
    return f"Character '{name}' not found. Available characters: {', '.join(c.name for c in project.characters)}"


@tool
def get_all_scenes(project: Project) -> str:
    """Get a list of all scenes in the story with titles, chapters, and summaries.
    
    Use this tool when the user asks:
    - "有哪些场景？" / "What scenes are there?"
    - "故事有多少章节？" / "How many chapters in the story?"
    - "列出所有剧情" / "List all plot points"
    """
    if not project.scenes:
        return "No scenes found in the story."
    
    result = f"Total scenes: {len(project.scenes)}\n\n"
    
    # Group by chapter
    chapters = {}
    for scene in project.scenes.values():
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


@tool
def get_scene_by_id(scene_id: str, project: Project) -> str:
    """Get detailed information about a specific scene by its ID.
    
    Args:
        scene_id: Scene ID to retrieve
        
    Use this tool when you need full scene details after finding it in the scene list.
    """
    for scene in project.scenes.values():
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


@tool
def search_scenes(keyword: str, project: Project) -> str:
    """Search for scenes containing specific keywords in title, summary, or content.
    
    Args:
        keyword: Keyword to search for in scenes
        
    Use this tool when the user asks to find scenes about a specific topic:
    - "哪些场景提到了记忆？" / "Which scenes mention memory?"
    - "找到关于警局的场景" / "Find scenes about the police station"
    """
    keyword_lower = keyword.lower()
    matching_scenes = []
    
    for scene in project.scenes.values():
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


@tool
def count_endings(project: Project) -> str:
    """Count how many ending scenes exist in the story (scenes with no choices or outgoing connections).
    
    Use this tool when the user asks:
    - "这个故事有几个结局？" / "How many endings does the story have?"
    - "有哪些结局？" / "What are the endings?"
    """
    endings = []
    
    for scene in project.scenes.values():
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


@tool
def get_world_facts(project: Project) -> str:
    """Get world-building facts and lore information about the story universe.
    
    Use this tool when the user asks about:
    - "这个故事的世界观是什么？" / "What is the world setting?"
    - "有哪些世界观设定？" / "What world-building facts are there?"
    """
    facts_list = list(project.worldState.facts.values()) if project.worldState.facts else []
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


def create_story_tools(project: Project) -> List:
    """
    Create a list of tools bound to the current project.
    
    Returns:
        List of LangChain tools ready for use with LangGraph agent
    """
    # Create partial functions with project bound
    from functools import partial
    
    tools = [
        get_all_characters,
        get_character_by_name,
        get_all_scenes,
        get_scene_by_id,
        search_scenes,
        count_endings,
        get_world_facts,
    ]
    
    # Bind project to each tool
    bound_tools = []
    for tool_func in tools:
        # Create a wrapper that binds the project
        bound_tool = partial(tool_func.func, project=project)
        bound_tool.__name__ = tool_func.name
        bound_tool.__doc__ = tool_func.description
        bound_tools.append(tool_func)
    
    return bound_tools
