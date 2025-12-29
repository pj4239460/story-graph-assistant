"""
LangGraph Story Agent with ChatLiteLLM
Uses LangGraph's StateGraph + ChatLiteLLM for a production-ready agent
"""
from typing import Literal
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from langchain_litellm import ChatLiteLLM
from langchain_core.tools import tool

from ..models.project import Project


class LangGraphAgentService:
    """
    LangGraph-powered story agent with ChatLiteLLM
    
    Architecture:
    - ChatLiteLLM: Multi-provider LLM interface (supports OpenAI, Anthropic, DeepSeek, etc.)
    - LangGraph: State machine for agent workflow
    - Tools: Story query functions decorated with @tool
    """
    
    def __init__(self, project: Project, model: str = "deepseek/deepseek-chat"):
        self.project = project
        self.model = model
        
        # Initialize ChatLiteLLM
        self.llm = ChatLiteLLM(
            model=model,
            temperature=0.2,
        )
        
        # Create tools
        self.tools = self._create_tools()
        
        # Bind tools to LLM
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        
        # Build agent graph
        self.agent = self._build_graph()
    
    def _create_tools(self):
        """Create LangChain tools for story queries"""
        project = self.project
        
        @tool
        def get_all_characters() -> str:
            """Get a list of all characters in the story. Use when user asks '现在整个故事中有几个角色？', 'How many characters?', '列出所有角色', etc."""
            chars = list(project.characters.values())
            if not chars:
                return "No characters found."
            
            result = f"Total: {len(chars)} characters\n\n"
            for char in chars:
                alias = f" (aka {char.alias})" if char.alias else ""
                traits = f"\nTraits: {', '.join(char.traits[:3])}" if char.traits else ""
                result += f"• {char.name}{alias}{traits}\n"
                if char.description:
                    desc = char.description[:100] + "..." if len(char.description) > 100 else char.description
                    result += f"  {desc}\n"
                result += "\n"
            return result
        
        @tool
        def get_character_by_name(name: str) -> str:
            """Get detailed information about a specific character. Use when user asks about a specific character like '陈墨是谁？', 'Who is Chen Mo?', '告诉我关于林雪薇的信息', etc.
            
            Args:
                name: Character name or alias to search for
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
                    if char.traits:
                        result += f"\nTraits: {', '.join(char.traits)}\n"
                    if char.goals:
                        result += f"\nGoals: {', '.join(char.goals)}\n"
                    if char.relationships:
                        result += f"\nRelationships:\n"
                        for rel in char.relationships:
                            result += f"  • {rel.targetId}: {rel.summary}\n"
                    return result
            available = ', '.join(c.name for c in project.characters.values())
            return f"Character '{name}' not found. Available: {available}"
        
        @tool
        def get_all_scenes() -> str:
            """Get a list of all scenes in the story. Use when user asks '有哪些场景？', 'What scenes are there?', '故事有多少章节？', etc."""
            scenes = list(project.scenes.values())
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
        
        @tool
        def search_scenes(keyword: str) -> str:
            """Search for scenes containing specific keywords. Use when user wants to find scenes about a topic like '哪些场景提到了记忆？', 'Find scenes about police', etc.
            
            Args:
                keyword: Keyword to search for in scene titles, summaries, and content
            """
            keyword_lower = keyword.lower()
            matches = []
            
            for scene in project.scenes.values():
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
        
        @tool
        def count_endings() -> str:
            """Count how many endings the story has. Use when user asks '这个故事有几个结局？', 'How many endings?', '有哪些结局？', etc."""
            endings = [s for s in project.scenes.values()
                       if not s.choices or all(not c.nextSceneId for c in s.choices)]
            
            if not endings:
                return "No clear endings found."
            
            result = f"Found {len(endings)} ending(s):\n"
            for scene in endings:
                result += f"• {scene.id}. {scene.title}\n"
            return result
        
        @tool
        def get_world_facts() -> str:
            """Get world-building facts and lore. Use when user asks about story setting, worldview, or background like '这个故事的世界观是什么？', 'What is the setting?', etc."""
            facts = getattr(project.worldState, 'facts', [])
            if not facts:
                return "No world facts have been extracted yet."
            
            result = f"World Facts ({len(facts)} total):\n\n"
            for fact in facts:
                content = fact.content if hasattr(fact, 'content') else str(fact)
                result += f"• {content}\n"
            return result
        
        return [
            get_all_characters,
            get_character_by_name,
            get_all_scenes,
            search_scenes,
            count_endings,
            get_world_facts,
        ]
    
    def _build_graph(self):
        """Build LangGraph agent workflow"""
        
        # Define agent node
        def agent_node(state: MessagesState):
            """Agent reasoning node - decides whether to use tools or respond"""
            messages = state["messages"]
            
            # Add system prompt if this is the first call
            if not messages or not any(isinstance(m, SystemMessage) for m in messages):
                system_msg = SystemMessage(content=self._get_system_prompt())
                messages = [system_msg] + messages
            
            # Call LLM with tools
            response = self.llm_with_tools.invoke(messages)
            
            return {"messages": [response]}
        
        # Define routing logic
        def should_continue(state: MessagesState) -> Literal["tools", END]:
            """Decide whether to call tools or end"""
            last_message = state["messages"][-1]
            
            # If LLM made tool calls, route to tools
            if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
                return "tools"
            
            # Otherwise, end
            return END
        
        # Create tool node
        tool_node = ToolNode(self.tools)
        
        # Build the graph
        workflow = StateGraph(MessagesState)
        
        # Add nodes
        workflow.add_node("agent", agent_node)
        workflow.add_node("tools", tool_node)
        
        # Add edges
        workflow.add_edge(START, "agent")
        workflow.add_conditional_edges(
            "agent",
            should_continue,
            {
                "tools": "tools",
                END: END
            }
        )
        workflow.add_edge("tools", "agent")  # After tool call, go back to agent
        
        # Compile
        return workflow.compile()
    
    def _get_system_prompt(self) -> str:
        """Get system prompt for the agent"""
        return f"""You are a helpful story assistant for the interactive fiction project "{self.project.name}".

Your role is to help users understand and explore this branching narrative story by:
- Answering questions about characters, their relationships, and traits
- Providing information about scenes, plot points, and story structure  
- Explaining world-building facts and lore
- Analyzing story branches and endings

IMPORTANT INSTRUCTIONS:
1. When the user asks a question, THINK about what information you need
2. USE TOOLS to get accurate information from the story database
3. Do NOT make up or hallucinate information
4. After getting tool results, provide a clear, helpful answer to the user

Available tools:
- get_all_characters() - List all characters
- get_character_by_name(name) - Get character details
- get_all_scenes() - List all scenes
- search_scenes(keyword) - Find scenes by keyword
- count_endings() - Count story endings
- get_world_facts() - Get world lore

Current project: {self.project.name}
Locale: {self.project.locale}

Respond in the same language as the user's question (Chinese or English)."""
    
    def chat(self, user_message: str, history: list = None):
        """
        Chat with the agent
        
        Args:
            user_message: User's question
            history: Previous chat history (list of dicts with 'role' and 'content')
            
        Returns:
            {
                "response": "Final answer",
                "steps": [{"type": "thinking|tool_call|tool_result", ...}],
                "total_rounds": 3
            }
        """
        # Convert history to LangChain message format
        messages = []
        if history:
            for msg in history:
                if msg["role"] == "user":
                    messages.append(HumanMessage(content=msg["content"]))
                elif msg["role"] == "assistant":
                    messages.append(AIMessage(content=msg["content"]))
        
        # Add current message
        messages.append(HumanMessage(content=user_message))
        
        # Invoke agent
        result = self.agent.invoke({"messages": messages})
        
        # Extract steps and final response
        steps = []
        round_count = 0
        final_response = ""
        
        for msg in result["messages"]:
            if isinstance(msg, AIMessage):
                if hasattr(msg, 'tool_calls') and msg.tool_calls:
                    # Agent decided to use tools
                    round_count += 1
                    steps.append({
                        "type": "thinking",
                        "content": f"🤔 Thinking... (Round {round_count})"
                    })
                    for tc in msg.tool_calls:
                        steps.append({
                            "type": "tool_call",
                            "tool": tc["name"],
                            "args": tc.get("args", {})
                        })
                else:
                    # Final response
                    final_response = msg.content
            elif isinstance(msg, ToolMessage):
                # Tool result
                steps.append({
                    "type": "tool_result",
                    "tool": msg.name,
                    "content": msg.content[:500] + "..." if len(msg.content) > 500 else msg.content
                })
        
        return {
            "response": final_response,
            "steps": steps,
            "total_rounds": round_count
        }
