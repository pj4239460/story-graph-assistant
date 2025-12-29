"""
Simple Agent Service with Tool Calling
Uses LiteLLM's function calling for a lightweight agent implementation
"""
from typing import Dict, List, Any, Optional
import json
from litellm import completion

from ..models.project import Project


class SimpleAgentService:
    """
    Lightweight agent with tool calling capabilities
    
    Architecture:
    1. User asks a question
    2. Agent thinks and decides which tools to use
    3. Tools are executed
    4. Agent synthesizes final answer
    
    Maximum 5 rounds to prevent infinite loops
    """
    
    def __init__(self, project: Project, model: str = "deepseek/deepseek-chat"):
        self.project = project
        self.model = model
        self.max_rounds = 5
        
    def get_tools_schema(self) -> List[Dict]:
        """Define available tools in OpenAI function calling format"""
        return [
            {
                "type": "function",
                "function": {
                    "name": "get_all_characters",
                    "description": "Get a list of all characters in the story. Use when user asks '现在整个故事中有几个角色？', 'How many characters?', '列出所有角色', etc.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_character_by_name",
                    "description": "Get detailed information about a specific character. Use when user asks about a specific character like '陈墨是谁？', 'Who is Chen Mo?', '告诉我关于林雪薇的信息', etc.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "Character name or alias to search for"
                            }
                        },
                        "required": ["name"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_all_scenes",
                    "description": "Get a list of all scenes in the story. Use when user asks '有哪些场景？', 'What scenes are there?', '故事有多少章节？', etc.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "search_scenes",
                    "description": "Search for scenes containing specific keywords. Use when user wants to find scenes about a topic like '哪些场景提到了记忆？', 'Find scenes about police', etc.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "keyword": {
                                "type": "string",
                                "description": "Keyword to search for in scene titles, summaries, and content"
                            }
                        },
                        "required": ["keyword"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "count_endings",
                    "description": "Count how many endings the story has. Use when user asks '这个故事有几个结局？', 'How many endings?', '有哪些结局？', etc.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_world_facts",
                    "description": "Get world-building facts and lore. Use when user asks about story setting, worldview, or background like '这个故事的世界观是什么？', 'What is the setting?', etc.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            }
        ]
    
    def execute_tool(self, tool_name: str, arguments: Dict) -> str:
        """Execute a tool and return the result"""
        try:
            if tool_name == "get_all_characters":
                return self._get_all_characters()
            elif tool_name == "get_character_by_name":
                return self._get_character_by_name(arguments.get("name", ""))
            elif tool_name == "get_all_scenes":
                return self._get_all_scenes()
            elif tool_name == "search_scenes":
                return self._search_scenes(arguments.get("keyword", ""))
            elif tool_name == "count_endings":
                return self._count_endings()
            elif tool_name == "get_world_facts":
                return self._get_world_facts()
            else:
                return f"Unknown tool: {tool_name}"
        except Exception as e:
            return f"Error executing {tool_name}: {str(e)}"
    
    # Tool implementations
    def _get_all_characters(self) -> str:
        chars = list(self.project.characters.values())
        if not chars:
            return "No characters found."
        
        result = f"Total: {len(chars)} characters\n\n"
        for char in chars:
            aliases = f" (aka {', '.join(char.aliases)})" if char.aliases else ""
            traits = f"\nTraits: {', '.join(char.traits[:3])}" if char.traits else ""
            result += f"• {char.name}{aliases}{traits}\n"
            if char.description:
                desc = char.description[:100] + "..." if len(char.description) > 100 else char.description
                result += f"  {desc}\n"
            result += "\n"
        return result
    
    def _get_character_by_name(self, name: str) -> str:
        name_lower = name.lower()
        for char in self.project.characters.values():
            if (char.name.lower() == name_lower or 
                any(alias.lower() == name_lower for alias in char.aliases)):
                result = f"**{char.name}**\n"
                if char.aliases:
                    result += f"Aliases: {', '.join(char.aliases)}\n"
                if char.description:
                    result += f"\n{char.description}\n"
                if char.traits:
                    result += f"\nTraits: {', '.join(char.traits)}\n"
                if char.goals:
                    result += f"\nGoals: {', '.join(char.goals)}\n"
                if char.relationships:
                    result += f"\nRelationships:\n"
                    for rel in char.relationships:
                        result += f"  • {rel.targetName}: {rel.relationType}\n"
                return result
        available = ', '.join(c.name for c in self.project.characters.values())
        return f"Character '{name}' not found. Available: {available}"
    
    def _get_all_scenes(self) -> str:
        scenes = list(self.project.scenes.values())
        if not scenes:
            return "No scenes found."
        
        result = f"Total: {len(scenes)} scenes\n\n"
        chapters = {}
        for scene in scenes:
            chapter = scene.chapter or "No Chapter"
            if chapter not in chapters:
                chapters[chapter] = []
            chapters[chapter].append(scene)
        
        for chapter, scene_list in sorted(chapters.items()):
            result += f"\n**{chapter}**\n"
            for scene in scene_list:
                result += f"{scene.id}. {scene.title}\n"
                if scene.summary:
                    summary = scene.summary[:100] + "..." if len(scene.summary) > 100 else scene.summary
                    result += f"   {summary}\n"
        return result
    
    def _search_scenes(self, keyword: str) -> str:
        keyword_lower = keyword.lower()
        matches = []
        
        for scene in self.project.scenes.values():
            if (keyword_lower in scene.title.lower() or
                (scene.summary and keyword_lower in scene.summary.lower()) or
                (scene.body and keyword_lower in scene.body.lower()) or
                any(keyword_lower in tag.lower() for tag in scene.tags)):
                matches.append(scene)
        
        if not matches:
            return f"No scenes found containing '{keyword}'."
        
        result = f"Found {len(matches)} scene(s) with '{keyword}':\n\n"
        for scene in matches:
            result += f"• {scene.id}. {scene.title}\n"
            if scene.chapter:
                result += f"  Chapter: {scene.chapter}\n"
        return result
    
    def _count_endings(self) -> str:
        endings = [s for s in self.project.scenes.values()
                   if not s.choices or all(not c.nextSceneId for c in s.choices)]
        
        if not endings:
            return "No clear endings found."
        
        result = f"Found {len(endings)} ending(s):\n"
        for scene in endings:
            result += f"• {scene.id}. {scene.title}\n"
        return result
    
    def _get_world_facts(self) -> str:
        # Check if worldFacts exists in WorldState
        facts = getattr(self.project.worldState, 'facts', [])
        if not facts:
            return "No world facts have been extracted yet."
        
        result = f"World Facts ({len(facts)} total):\n\n"
        for fact in facts:
            content = fact.content if hasattr(fact, 'content') else str(fact)
            result += f"• {content}\n"
        return result
    
    def chat(self, user_message: str, history: Optional[List[Dict]] = None) -> Dict:
        """
        Chat with the agent
        
        Args:
            user_message: User's question
            history: Previous chat history in OpenAI format
            
        Returns:
            {
                "response": "Final answer",
                "steps": [{"type": "thinking|tool_call|tool_result", ...}],
                "total_rounds": 3
            }
        """
        messages = history or []
        messages.append({"role": "user", "content": user_message})
        
        steps = []
        round_count = 0
        
        # System prompt
        system_prompt = f"""You are a helpful story assistant for "{self.project.name}".

Your role is to help users explore this interactive fiction story by answering questions about:
- Characters, their traits, relationships, and goals
- Scenes, plot points, and story structure
- World-building facts and lore
- Story branches and endings

CRITICAL INSTRUCTIONS:
1. When user asks a question, THINK about what information you need
2. USE TOOLS to retrieve accurate information from the story database
3. NEVER make up or hallucinate information
4. After getting tool results, synthesize a clear, helpful answer

Available tools:
- get_all_characters() - List all characters
- get_character_by_name(name) - Get character details
- get_all_scenes() - List all scenes
- search_scenes(keyword) - Find scenes by keyword
- count_endings() - Count story endings
- get_world_facts() - Get world lore

Respond in the same language as the user's question."""

        full_messages = [{"role": "system", "content": system_prompt}] + messages
        
        # Agent loop
        while round_count < self.max_rounds:
            round_count += 1
            
            # Call LLM with tools
            response = completion(
                model=self.model,
                messages=full_messages,
                tools=self.get_tools_schema(),
                tool_choice="auto",
            )
            
            assistant_message = response.choices[0].message
            
            # Check if LLM wants to use tools
            if hasattr(assistant_message, 'tool_calls') and assistant_message.tool_calls:
                # LLM decided to call tools
                steps.append({
                    "type": "thinking",
                    "content": f"🤔 Thinking... (Round {round_count})"
                })
                
                tool_results = []
                for tool_call in assistant_message.tool_calls:
                    tool_name = tool_call.function.name
                    try:
                        tool_args = json.loads(tool_call.function.arguments) if isinstance(tool_call.function.arguments, str) else tool_call.function.arguments
                    except:
                        tool_args = {}
                    
                    steps.append({
                        "type": "tool_call",
                        "tool": tool_name,
                        "args": tool_args
                    })
                    
                    # Execute tool
                    result = self.execute_tool(tool_name, tool_args)
                    
                    steps.append({
                        "type": "tool_result",
                        "tool": tool_name,
                        "content": result[:500] + "..." if len(result) > 500 else result
                    })
                    
                    tool_results.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_name,
                        "content": result
                    })
                
                # Add assistant's tool calls and tool results to messages
                full_messages.append({
                    "role": "assistant",
                    "content": assistant_message.content or "",
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments
                            }
                        }
                        for tc in assistant_message.tool_calls
                    ]
                })
                full_messages.extend(tool_results)
                
                # Continue loop to let LLM synthesize answer
                
            else:
                # LLM provided final answer
                final_answer = assistant_message.content
                
                steps.append({
                    "type": "final_answer",
                    "content": final_answer
                })
                
                return {
                    "response": final_answer,
                    "steps": steps,
                    "total_rounds": round_count
                }
        
        # Max rounds reached
        return {
            "response": "抱歉，我无法在限定步骤内完成回答。请尝试更具体的问题。 / Sorry, I couldn't complete the answer within the limit. Please try a more specific question.",
            "steps": steps,
            "total_rounds": round_count
        }
