# AI Agent Development Guide

**Version:** v0.7  
**Last Updated:** January 2026

This guide explains how to extend the Story Graph Assistant's AI Agent capabilities using LangGraph and ChatLiteLLM.

## Architecture Overview

### Technology Stack
- **LangGraph**: State machine framework for agent workflow
- **ChatLiteLLM**: Multi-provider LLM interface (DeepSeek, OpenAI, Anthropic, Google Gemini, Ollama)
- **LangChain Tools**: Tool functions with `@tool` decorator
- **Token Tracking**: Built-in usage monitoring via callbacks

### Core Components

```
src/services/langgraph_agent_service.py
├── LangGraphAgentService
│   ├── __init__(): Initialize LLM, tools, and callbacks
│   ├── _create_tools(): Define all story query tools
│   ├── _build_graph(): Build StateGraph workflow with intent classification
│   ├── _classify_intent(): Route between chat/qa modes
│   └── chat(): Process user messages and return responses
│
├── TokenTrackingCallback
│   └── on_llm_end(): Record token usage per feature
│
└── StateGraph workflow
    ├── classify: Intent classification (chat vs qa)
    ├── chat_mode: Conversational responses
    ├── qa_mode: Agent with tool calling
    ├── agent: LLM reasoning with tool binding
    ├── tools: Tool execution node
    └── should_continue: Routing logic
```

### Available Tools (v0.7)

The agent has access to these story query tools:

**Character & Scene Tools:**
- `search_characters`: Search characters by traits/goals/fears
- `get_character_info`: Get detailed character information
- `search_scenes`: Search scenes by keywords
- `get_scene_details`: Get complete scene information

**Dynamic State Tools (v0.4+):**
- `get_character_state`: Query character state at specific story point
- `get_relationship`: Get relationship state between two characters
- `explain_state_change`: Explain state changes from effects

**Context Tools:**
- `search_story_context`: Semantic search across all story content (v0.3 RAG)
- `analyze_scene`: AI-powered scene analysis for plot/character insights

**World Director Tools (v0.5+):**
- `list_available_storylets`: Get currently available storylets
- `explain_unavailable_storylet`: Explain why a storylet is unavailable
- `get_storylet_details`: Get complete storylet information

## How to Add New Tools

### 1. Define Tool Function in `_create_tools()` Method

Tools are defined using the `@tool` decorator from LangChain. Each tool should have:
- Clear docstring with usage examples
- Type-annotated parameters
- Error handling
- Formatted return string

**Example: Adding a World Query Tool**

```python
def _create_tools(self):
    """Create LangChain tools for story queries"""
    project = self.project
    state_service = self.state_service  # Access injected services
    
    @tool
    def get_world_fact(fact_category: str, fact_key: str) -> str:
        """Get a world fact by category and key.
        
        Use this when user asks about world information like:
        - "What's the magic system in this world?"
        - "Tell me about the political structure"
        - "What's the history of the kingdom?"
        
        Args:
            fact_category: Category name (e.g., "magic_system", "politics")
            fact_key: Specific fact key within the category
            
        Returns:
            Fact value or error message
        """
        try:
            world_facts = project.world.facts.get(fact_category, {})
            if fact_key in world_facts:
                return f"**{fact_category}.{fact_key}**: {world_facts[fact_key]}"
            else:
                available_keys = ", ".join(world_facts.keys())
                return f"Fact '{fact_key}' not found in category '{fact_category}'. Available: {available_keys}"
        except Exception as e:
            return f"Error retrieving world fact: {str(e)}"
    
    # Add new tool to return list
    return [
        # Character tools
        search_characters,
        get_character_info,
        # State tools
        get_character_state,
        get_relationship,
        # ... other existing tools ...
        get_world_fact,  # ← Add your new tool here
    ]
```

**Tool Design Best Practices:**
1. **Descriptive docstrings**: Include 2-3 example user questions
2. **Type hints**: Always annotate parameters and return types
3. **Error handling**: Wrap logic in try/except blocks
4. **Formatted output**: Return structured, readable strings
5. **Context awareness**: Access `project`, `search_service`, `ai_service`, `state_service` from closure

### 2. Tool Definition Best Practices

#### ✅ Good Tool Description
```python
@tool
def search_scenes(keyword: str) -> str:
    """Search for scenes containing specific keywords.
    
    Use when user wants to find scenes about a topic:
    - "哪些场景提到了记忆？"
    - "Find scenes about police"
    
    Args:
        keyword: Keyword to search for
    """
```

**Key Points:**
- Clear purpose statement
- Provide concrete user question examples
- Concise parameter descriptions

#### ❌ Poor Tool Description
```python
@tool
def search_scenes(keyword: str) -> str:
    """Search scenes"""  # Too brief, no examples
```

### 3. Accessing Project Data

Tool functions can access the `project` object via closure:

```python
@tool
def get_scene_count_by_chapter() -> str:
    """Count scenes per chapter"""
    chapters = {}
    for scene in project.scenes.values():  # Note: use .values(), not direct iteration
        chapter = scene.chapter or "Uncategorized"
        chapters[chapter] = chapters.get(chapter, 0) + 1
    
    result = "Scenes per chapter:\n"
    for chapter, count in sorted(chapters.items()):
        result += f"  {chapter}: {count} scenes\n"
    return result
```

**Important Notes:**
- `project.characters` and `project.scenes` are `Dict[str, T]` type
- Must use `.values()` when iterating: `for char in project.characters.values()`
- Directly iterating `project.characters` only gives keys (IDs)

### 4. Data Model Reference

#### Character Model
```python
class Character:
    id: str
    name: str
    alias: Optional[str] = None  # Note: 'alias' not 'aliases'
    description: str = ""
    traits: List[str] = []
    goals: List[str] = []
    fears: List[str] = []
    relationships: List[Relationship] = []
```

#### Scene Model
```python
class Scene:
    id: str
    title: str
    chapter: Optional[str] = None
    summary: Optional[str] = None
    body: str = ""
    tags: List[str] = []
    choices: List[Choice] = []
```

#### Relationship Model
```python
class Relationship:
    targetId: str  # Note: 'targetId' not 'targetName'
    summary: str   # Note: 'summary' not 'relationType'
```

## Tool Examples

### Example 1: Simple Query Tool

```python
@tool
def count_endings() -> str:
    """Count the number of story endings.
    
    Use when user asks about endings:
    - "这个故事有几个结局？"
    - "How many endings?"
    """
    endings = [
        s for s in project.scenes.values()
        if not s.choices or all(not c.nextSceneId for c in s.choices)
    ]
    
    if not endings:
        return "No clear ending scenes found."
    
    result = f"Found {len(endings)} ending(s):\n"
    for scene in endings:
        result += f"• {scene.id}. {scene.title}\n"
    return result
```

### Example 2: Parameterized Query Tool

```python
@tool
def get_character_by_name(name: str) -> str:
    """Get detailed information about a specific character.
    
    Use when user asks about a character:
    - "陈墨是谁？"
    - "Who is Chen Mo?"
    
    Args:
        name: Character name or alias
    """
    name_lower = name.lower()
    for char in project.characters.values():
        if (char.name.lower() == name_lower or 
            (char.alias and char.alias.lower() == name_lower)):
            result = f"**{char.name}**\n"
            if char.alias:
                result += f"Alias: {char.alias}\n"
            if char.description:
                result += f"\n{char.description}\n"
            return result
    
    available = ', '.join(c.name for c in project.characters.values())
    return f"Character '{name}' not found. Available: {available}"
```

### Example 3: Complex Analysis Tool

```python
@tool
def analyze_character_interactions() -> str:
    """Analyze character interaction relationships.
    
    Use when user wants to understand character interactions:
    - "角色之间有什么关系？"
    - "Which characters interact?"
    """
    interactions = {}
    
    # Count how many times each pair appears in the same scene
    for scene in project.scenes.values():
        char_ids = [p.characterId for p in scene.participants]
        for i, char1 in enumerate(char_ids):
            for char2 in char_ids[i+1:]:
                pair = tuple(sorted([char1, char2]))
                interactions[pair] = interactions.get(pair, 0) + 1
    
    # Sort by interaction count
    sorted_pairs = sorted(interactions.items(), key=lambda x: x[1], reverse=True)
    
    result = "Character interaction statistics (shared scenes):\n\n"
    for (id1, id2), count in sorted_pairs[:10]:
        name1 = project.characters.get(id1, type('obj', (), {'name': id1})).name
        name2 = project.characters.get(id2, type('obj', (), {'name': id2})).name
        result += f"{name1} ↔ {name2}: {count} scenes\n"
    
    return result
```

## Testing New Tools

### 1. Restart Application
```bash
streamlit run src/app.py
```

### 2. Test in Chat Interface

Ask questions that should trigger the new tool:
- "现在整个故事中有几个角色？"
- "Who is Chen Mo?"
- "How many endings does this story have?"

### 3. View Agent Thinking Process

Click "🔍 View Agent Thinking Process" to expand and see:
- 🤔 Thinking: Agent decision process
- 🔧 Tool Call: Which tool was called, with what parameters
- 📊 Result: Tool return value
- ✅ Final Answer: Final response

## Common Issues

### Q1: Tool not being called?

**Cause:** Tool description unclear, or example questions don't match

**Solution:**
1. Add more user question examples in tool docstring
2. Clearly explain tool purpose in natural language
3. Ensure examples cover both Chinese and English

### Q2: Tool error: 'str' object has no attribute ...

**Cause:** Iterating Dict without using `.values()`

**Solution:**
```python
# ❌ Wrong
for char in project.characters:
    print(char.name)  # char is str type ID

# ✅ Correct
for char in project.characters.values():
    print(char.name)  # char is Character object
```

### Q3: Tool output too long, gets truncated

**Solution:** Limit output length in tool
```python
@tool
def get_all_scenes() -> str:
    """Get list of all scenes"""
    scenes = list(project.scenes.values())
    result = f"Total {len(scenes)} scenes:\n\n"
    
    for scene in scenes[:20]:  # Show only first 20
        result += f"{scene.id}. {scene.title}\n"
        if scene.summary:
            # Limit summary to 100 chars
            summary = scene.summary[:100] + "..." if len(scene.summary) > 100 else scene.summary
            result += f"   {summary}\n"
    
    if len(scenes) > 20:
        result += f"\n... and {len(scenes) - 20} more scenes"
    
    return result
```

### Q4: How to support multiple languages?

**Solution:** System prompt instructs Agent to respond in user's language

Current implementation includes:
```python
def _get_system_prompt(self) -> str:
    return f"""...
Current project: {self.project.name}
Locale: {self.project.locale}

Respond in the same language as the user's question (Chinese or English)."""
```

Tool return values can be in English; Agent will translate based on user's language.

## Advanced Topics

### Async Tool Calls

For external API calls, use async tools:

```python
import asyncio
from langchain_core.tools import tool

@tool
async def search_web(query: str) -> str:
    """Search web for information"""
    # Async HTTP request
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.example.com/search?q={query}") as resp:
            data = await resp.json()
            return data["result"]
```

**Note:** Need to modify `_build_graph()` to use async ToolNode.

### Tool Dependencies and Composition

Tools can reuse other tool logic:

```python
@tool
def get_character_summary(name: str) -> str:
    """Get character summary (including scenes)"""
    # Reuse get_character_by_name logic
    char_info = get_character_by_name.invoke(name)
    
    # Add scene statistics
    scene_count = sum(
        1 for scene in project.scenes.values()
        if any(p.characterId == name for p in scene.participants)
    )
    
    return f"{char_info}\n\nScenes participated: {scene_count}"
```

### Error Handling

Tools should handle errors gracefully:

```python
@tool
def get_scene_by_id(scene_id: str) -> str:
    """Get scene details by ID"""
    try:
        scene = project.scenes.get(scene_id)
        if not scene:
            available = ', '.join(list(project.scenes.keys())[:5])
            return f"Scene '{scene_id}' not found. Example IDs: {available}"
        
        result = f"**{scene.title}**\n"
        result += f"ID: {scene.id}\n"
        if scene.chapter:
            result += f"Chapter: {scene.chapter}\n"
        # ...
        return result
        
    except Exception as e:
        return f"Error getting scene info: {str(e)}"
```

## References

- [LangGraph Documentation](https://python.langchain.com/docs/langgraph)
- [LangChain Tools](https://python.langchain.com/docs/modules/tools/)
- [ChatLiteLLM](https://docs.litellm.ai/docs/providers)
- [Project Code: langgraph_agent_service.py](../src/services/langgraph_agent_service.py)

---

**Tip:** After adding new tools, restart the Streamlit app and test that tools work correctly. Use the Agent thinking process panel to debug tool calls.
