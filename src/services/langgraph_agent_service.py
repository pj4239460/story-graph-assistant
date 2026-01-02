"""
LangGraph Story Agent with ChatLiteLLM
Uses LangGraph's StateGraph + ChatLiteLLM for a production-ready agent

Enhanced with:
- RAG tool: search_story_context
- Scene analysis tool: analyze_scene  
- Intent classification: chat vs qa modes
- Dynamic state tools: get_character_state, get_relationship, explain_state_change
- Token usage tracking via callback handler
"""
from typing import Literal, Optional
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from langchain_litellm import ChatLiteLLM
from langchain_core.tools import tool
from langchain_core.callbacks import BaseCallbackHandler

from ..models.project import Project
from .search_service import SearchService
from .ai_service import AIService
from .state_service import StateService
from ..infra.token_stats import record_usage


class TokenTrackingCallback(BaseCallbackHandler):
    """Callback handler to track token usage from LangChain LLM calls"""
    
    def __init__(self, project: Project, feature: str = "agent_chat"):
        self.project = project
        self.feature = feature
    
    def on_llm_end(self, response, **kwargs):
        """Called when LLM finishes"""
        try:
            # Extract token usage from response
            if hasattr(response, 'llm_output') and response.llm_output:
                usage = response.llm_output.get('token_usage', {})
                if usage:
                    # Record usage
                    record_usage(self.project, self.feature, usage)
        except Exception as e:
            # Silently fail - don't break agent execution
            pass


class LangGraphAgentService:
    """
    LangGraph-powered story agent with ChatLiteLLM
    
    Architecture:
    - ChatLiteLLM: Multi-provider LLM interface (supports OpenAI, Anthropic, DeepSeek, etc.)
    - LangGraph: State machine for agent workflow
    - Tools: Story query functions decorated with @tool
    """
    
    def __init__(self, project: Project, model: str = "deepseek/deepseek-chat", 
                 search_service: Optional[SearchService] = None,
                 ai_service: Optional[AIService] = None,
                 state_service: Optional[StateService] = None):
        self.project = project
        self.model = model
        self.search_service = search_service or SearchService()
        self.ai_service = ai_service or AIService()
        self.state_service = state_service or StateService()
        
        # Token tracking callback
        self.token_callback = TokenTrackingCallback(project, feature="agent_chat")
        
        # Initialize ChatLiteLLM with callback
        self.llm = ChatLiteLLM(
            model=model,
            temperature=0.2,
            callbacks=[self.token_callback]
        )
        
        # Initialize classifier LLM with callback
        self.classifier_llm = ChatLiteLLM(
            model=model,
            temperature=0.0,
            callbacks=[self.token_callback]
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
        search_service = self.search_service
        ai_service = self.ai_service
        state_service = self.state_service
        
        # ===== NEW: Dynamic State Query Tools =====
        
        @tool
        def get_character_state(character_id: str, thread_id: str, step_index: int) -> str:
            """Get a character's dynamic state at a specific point in a story thread.
            
            Use this when user asks about a character's state at a specific moment like:
            - "在第3章Alice的心情如何？" / "What's Alice's mood in chapter 3?"
            - "Bob在这个时候有什么目标？" / "What are Bob's goals at this point?"
            - "角色在这条路线上有什么变化？" / "How has the character changed in this route?"
            
            Args:
                character_id: Character ID to query
                thread_id: Story thread (route) ID
                step_index: Step number (0-based index) in the thread
            
            Returns:
                Formatted character state at that point
            """
            try:
                char_state = state_service.get_character_state_at_step(
                    project, thread_id, step_index, character_id
                )
                
                if not char_state:
                    return f"Character '{character_id}' not found or no state available."
                
                # Get base character info
                char = project.characters.get(character_id)
                char_name = char.name if char else character_id
                
                result = f"**{char_name}** at Thread '{thread_id}', Step {step_index}\n\n"
                
                if char_state.mood:
                    result += f"- **Mood:** {char_state.mood}\n"
                if char_state.status:
                    result += f"- **Status:** {char_state.status}\n"
                if char_state.location:
                    result += f"- **Location:** {char_state.location}\n"
                
                if char_state.active_traits:
                    result += f"- **Active Traits:** {', '.join(char_state.active_traits)}\n"
                if char_state.active_goals:
                    result += f"- **Current Goals:** {', '.join(char_state.active_goals)}\n"
                if char_state.active_fears:
                    result += f"- **Active Fears:** {', '.join(char_state.active_fears)}\n"
                
                if char_state.vars:
                    result += f"\n**Custom State Variables:**\n"
                    for key, val in char_state.vars.items():
                        result += f"  - {key}: {val}\n"
                
                return result
                
            except Exception as e:
                return f"Error getting character state: {str(e)}"
        
        @tool
        def get_relationship(char_a_id: str, char_b_id: str, thread_id: str, step_index: int) -> str:
            """Get the relationship state between two characters at a specific point.
            
            Use when user asks about relationships like:
            - "Alice和Bob的关系怎么样？" / "What's the relationship between Alice and Bob?"
            - "在这个时候他们是否信任彼此？" / "Do they trust each other at this point?"
            
            Args:
                char_a_id: First character ID
                char_b_id: Second character ID
                thread_id: Story thread ID
                step_index: Step number in the thread
            
            Returns:
                Relationship state information
            """
            try:
                _, _, rel_states = state_service.compute_state(project, thread_id, step_index)
                
                # Try both orderings
                rel_key = f"{char_a_id}|{char_b_id}"
                rel_key_rev = f"{char_b_id}|{char_a_id}"
                
                rel_data = rel_states.get(rel_key) or rel_states.get(rel_key_rev)
                
                if not rel_data:
                    return f"No relationship data found between '{char_a_id}' and '{char_b_id}' at this point."
                
                char_a = project.characters.get(char_a_id)
                char_b = project.characters.get(char_b_id)
                name_a = char_a.name if char_a else char_a_id
                name_b = char_b.name if char_b else char_b_id
                
                result = f"**{name_a} ↔ {name_b}** at Thread '{thread_id}', Step {step_index}\n\n"
                
                for key, val in rel_data.items():
                    result += f"- {key}: {val}\n"
                
                return result
                
            except Exception as e:
                return f"Error getting relationship: {str(e)}"
        
        @tool
        def explain_state_change(target: str, thread_id: str, from_step: int, to_step: int) -> str:
            """Explain what changed in character/world state between two points in the story.
            
            Use when user asks:
            - "Alice从第2章到第5章发生了什么变化？" / "How did Alice change from chapter 2 to 5?"
            - "这条路线上世界状态有什么不同？" / "What world state changes in this route?"
            
            Args:
                target: What to check changes for ("world" or character_id)
                thread_id: Story thread ID
                from_step: Starting step
                to_step: Ending step
            
            Returns:
                Description of changes
            """
            try:
                diff = state_service.diff_state(project, thread_id, from_step, to_step)
                
                result = f"**Changes from Step {from_step} → {to_step}** in Thread '{thread_id}'\n\n"
                
                if target == "world":
                    if diff["world"]:
                        result += "## World Changes:\n"
                        for var_name, (old_val, new_val) in diff["world"].items():
                            result += f"- {var_name}: {old_val} → {new_val}\n"
                    else:
                        result += "No world state changes.\n"
                
                elif target in project.characters:
                    if target in diff["characters"]:
                        char = project.characters[target]
                        result += f"## {char.name} Changes:\n"
                        for field, change in diff["characters"][target].items():
                            if isinstance(change, tuple):
                                old_val, new_val = change
                                result += f"- {field}: {old_val} → {new_val}\n"
                            else:
                                result += f"- {field}: {change}\n"
                    else:
                        result += f"No changes for character '{target}'.\n"
                else:
                    result += "Invalid target. Use 'world' or a valid character_id.\n"
                
                # Also show relationship changes
                if diff["relationships"]:
                    result += "\n## Relationship Changes:\n"
                    for rel_key, (old_val, new_val) in diff["relationships"].items():
                        result += f"- {rel_key}: {old_val} → {new_val}\n"
                
                return result
                
            except Exception as e:
                return f"Error explaining state change: {str(e)}"
        
        # ===== RAG Tool =====
        @tool
        def search_story_context(query: str) -> str:
            """Search the entire story database for relevant context about characters, scenes, and worldview.
            
            Use this tool when you need to find information about:
            - Character backgrounds, relationships, or traits
            - Specific plot events or scenes
            - Worldview settings and lore
            - Any story-related questions that need factual answers
            
            Examples:
            - "在这个世界里帝国和教会的关系是怎样的？"
            - "What is the protagonist's background?"
            - "Which scenes involve memory manipulation?"
            
            Args:
                query: The search query (can be in Chinese or English)
                
            Returns:
                Formatted context with relevant characters and scenes
            """
            try:
                context = search_service.get_contextual_summary(project, query)
                if not context or len(context) < 50:
                    return "No relevant context found. Try rephrasing your query."
                return context
            except Exception as e:
                return f"Error searching context: {str(e)}"
        
        # ===== NEW: Scene Analysis Tool =====
        @tool
        def analyze_scene(scene_id: str) -> str:
            """Perform comprehensive analysis on a specific scene.
            
            This tool combines multiple AI capabilities:
            - Generate scene summary
            - Extract worldview facts and plot points
            - (Future) Check for OOC issues
            
            Use when user asks to:
            - "分析这个场景"
            - "这个scene有什么问题吗？"
            - "帮我看看 Scene X 的内容"
            - "Analyze scene 12"
            
            Args:
                scene_id: The scene ID to analyze
                
            Returns:
                Multi-section analysis report in Markdown format
            """
            try:
                scene = project.scenes.get(scene_id)
                if not scene:
                    available = ', '.join(list(project.scenes.keys())[:10])
                    return f"Scene '{scene_id}' not found. Available scene IDs (first 10): {available}"
                
                result = f"# Scene Analysis: {scene.title}\n\n"
                result += f"**ID:** {scene_id}\n"
                if scene.chapter:
                    result += f"**Chapter:** {scene.chapter}\n"
                result += "\n---\n\n"
                
                # Generate summary
                result += "## 📝 Summary\n\n"
                if scene.summary:
                    result += f"{scene.summary}\n\n"
                else:
                    summary = ai_service.summarize_scene(project, scene)
                    result += f"{summary}\n\n"
                    result += "*（AI Generated）*\n\n"
                
                # Extract facts
                result += "## 🌍 Extracted Facts & Plot Points\n\n"
                facts = ai_service.extract_facts(project, scene)
                if facts and not facts[0].startswith("Error"):
                    for fact in facts:
                        result += f"- {fact}\n"
                else:
                    result += "*(No facts extracted)*\n"
                
                result += "\n---\n\n"
                
                # Scene metadata
                result += "## 📊 Scene Metadata\n\n"
                result += f"- **Choices:** {len(scene.choices)} options\n"
                if scene.tags:
                    result += f"- **Tags:** {', '.join(scene.tags)}\n"
                if scene.participants:
                    char_names = []
                    for p in scene.participants:
                        char = project.characters.get(p.characterId)
                        if char:
                            char_names.append(char.name)
                    if char_names:
                        result += f"- **Characters:** {', '.join(char_names)}\n"
                
                return result
                
            except Exception as e:
                return f"Error analyzing scene: {str(e)}"
        
        # ===== Original Basic Query Tools =====
        
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
            # State query tools (NEW - highest priority for dynamic character analysis)
            get_character_state,
            get_relationship,
            explain_state_change,
            # RAG and analysis tools
            search_story_context,
            analyze_scene,
            # Basic query tools
            get_all_characters,
            get_character_by_name,
            get_all_scenes,
            search_scenes,
            count_endings,
            get_world_facts,
        ]
    
    def _build_graph(self):
        """Build LangGraph agent workflow with intent classification"""
        
        # Define intent classification node
        def classify_intent(state: MessagesState) -> dict:
            """Classify user intent: 'chat' or 'qa'"""
            messages = state["messages"]
            
            # Get last user message
            last_user_msg = None
            for msg in reversed(messages):
                if isinstance(msg, HumanMessage):
                    last_user_msg = msg.content
                    break
            
            if not last_user_msg:
                return {"intent": "chat"}
            
            # Simple classification prompt
            classification_prompt = f"""Classify the user's intent as either 'chat' or 'qa':

- 'qa': User is asking factual questions about the story, characters, scenes, worldview, plot details, or wants analysis.
  Examples: "现在有几个角色？", "陈墨是谁？", "这个故事有几个结局？", "分析一下Scene 5", "帝国和教会的关系"
  
- 'chat': User wants to discuss, brainstorm, get suggestions, or general conversation about writing.
  Examples: "我觉得这个角色设定怎么样？", "有什么建议吗？", "怎么改进这段剧情？", "你好"

User message: "{last_user_msg}"

Respond with ONLY ONE WORD: either 'qa' or 'chat'"""

            try:
                response = self.classifier_llm.invoke([HumanMessage(content=classification_prompt)])
                intent = response.content.strip().lower()
                
                # Validate response
                if intent not in ['qa', 'chat']:
                    # Default to qa for ambiguous cases (safer)
                    intent = 'qa'
                
                # Store intent in state metadata
                return {"intent": intent}
            except:
                # Fallback to qa mode
                return {"intent": "qa"}
        
        # Define QA agent node (with tools)
        def qa_agent_node(state: MessagesState):
            """QA agent with full tool access for factual queries"""
            messages = state["messages"]
            
            # Add system prompt if needed
            if not messages or not any(isinstance(m, SystemMessage) for m in messages):
                system_msg = SystemMessage(content=self._get_qa_system_prompt())
                messages = [system_msg] + messages
            
            # Call LLM with all tools
            response = self.llm_with_tools.invoke(messages)
            
            return {"messages": [response]}
        
        # Define chat agent node (lightweight, minimal tools)
        def chat_agent_node(state: MessagesState):
            """Chat agent for discussions and brainstorming"""
            messages = state["messages"]
            
            # Add system prompt if needed
            if not messages or not any(isinstance(m, SystemMessage) for m in messages):
                system_msg = SystemMessage(content=self._get_chat_system_prompt())
                messages = [system_msg] + messages
            
            # Use LLM without tools (or with minimal tools)
            # For now, reuse the same tools but with different prompting
            response = self.llm_with_tools.invoke(messages)
            
            return {"messages": [response]}
        
        # Define routing logic
        def route_by_intent(state: MessagesState) -> Literal["qa_agent", "chat_agent"]:
            """Route to appropriate agent based on intent"""
            intent = state.get("intent", "qa")
            return "qa_agent" if intent == "qa" else "chat_agent"
        
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
        
        # Build the graph with intent classification
        workflow = StateGraph(MessagesState)
        
        # Add nodes
        workflow.add_node("classify", classify_intent)
        workflow.add_node("qa_agent", qa_agent_node)
        workflow.add_node("chat_agent", chat_agent_node)
        workflow.add_node("tools", tool_node)
        
        # Add edges
        workflow.add_edge(START, "classify")  # Start with classification
        workflow.add_conditional_edges(
            "classify",
            route_by_intent,
            {
                "qa_agent": "qa_agent",
                "chat_agent": "chat_agent"
            }
        )
        
        # QA agent can use tools
        workflow.add_conditional_edges(
            "qa_agent",
            should_continue,
            {
                "tools": "tools",
                END: END
            }
        )
        
        # Chat agent typically doesn't need tools, but can use them
        workflow.add_conditional_edges(
            "chat_agent",
            should_continue,
            {
                "tools": "tools",
                END: END
            }
        )
        
        # After tool execution, go back to appropriate agent
        # For simplicity, always return to qa_agent after tools
        workflow.add_edge("tools", "qa_agent")
        
        # Compile
        return workflow.compile()
    
    def _get_qa_system_prompt(self) -> str:
        """Get system prompt for QA agent (factual queries)"""
        return f"""You are a professional story database assistant for the interactive fiction project "{self.project.name}".

Your role is to provide ACCURATE, FACTUAL answers about this story by using the available tools.

IMPORTANT RULES:
1. When user asks factual questions, ALWAYS use tools to get accurate information
2. Do NOT make up or hallucinate information
3. If you can't find information with tools, say so clearly
4. Prioritize using 'search_story_context' for general queries about worldview, lore, or background
5. Use 'analyze_scene' when user asks to analyze or review a specific scene
6. Use specific query tools (get_character_by_name, search_scenes, etc.) for targeted lookups

Available tools:
- search_story_context(query) - **Use this FIRST for most questions** - Semantic search across all story content
- analyze_scene(scene_id) - Comprehensive scene analysis with AI-generated summary and fact extraction
- get_all_characters() - List all characters
- get_character_by_name(name) - Get character details
- get_all_scenes() - List all scenes
- search_scenes(keyword) - Find scenes by keyword
- count_endings() - Count story endings
- get_world_facts() - Get extracted world lore

Current project: {self.project.name}
Total characters: {len(self.project.characters)}
Total scenes: {len(self.project.scenes)}

Respond in the same language as the user's question (Chinese or English)."""

    def _get_chat_system_prompt(self) -> str:
        """Get system prompt for chat agent (discussions and brainstorming)"""
        return f"""You are a creative writing consultant for the interactive fiction project "{self.project.name}".

Your role is to DISCUSS, BRAINSTORM, and provide SUGGESTIONS about story development.

IMPORTANT RULES:
1. You can ask clarifying questions
2. Provide constructive feedback and creative suggestions
3. You MAY use tools if you need to check facts, but prioritize conversation
4. Be encouraging and supportive of the writer's creative process
5. Help identify potential plot holes or character inconsistencies

When discussing:
- Story structure and pacing
- Character development arcs
- Narrative themes and motifs
- Player choices and branching logic
- Emotional impact and player engagement

Current project: {self.project.name}
Locale: {self.project.locale}

Respond in the same language as the user's question (Chinese or English)."""

    def _get_system_prompt(self) -> str:
        """Legacy system prompt (fallback)"""
        return self._get_qa_system_prompt()
    
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
