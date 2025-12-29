"""
LangGraph Agent Service
Uses LangGraph to build a story assistant agent with tool calling capabilities
"""
from typing import Dict, List, Literal
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from litellm import completion

from ..models.project import Project
from ..tools.langchain_tools import create_story_tools


class StoryAgentService:
    """
    LangGraph-based story assistant agent
    
    The agent can:
    - Answer questions about characters, scenes, and world facts
    - Use tools to retrieve accurate information
    - Provide thoughtful responses with reasoning
    """
    
    def __init__(self, project: Project, model: str = "deepseek/deepseek-chat"):
        self.project = project
        self.model = model
        self.tools = create_story_tools(project)
        self.agent = self._build_agent()
    
    def _build_agent(self):
        """Build the LangGraph agent workflow"""
        
        # Create tool node
        tool_node = ToolNode(self.tools)
        
        # Define the agent graph
        workflow = StateGraph(MessagesState)
        
        # Add nodes
        workflow.add_node("agent", self._agent_node)
        workflow.add_node("tools", tool_node)
        
        # Add edges
        workflow.add_edge(START, "agent")
        workflow.add_conditional_edges(
            "agent",
            self._should_continue,
            {
                "tools": "tools",
                END: END
            }
        )
        workflow.add_edge("tools", "agent")
        
        # Compile
        return workflow.compile()
    
    def _agent_node(self, state: MessagesState):
        """
        Agent node: LLM decides whether to use tools or respond
        """
        messages = state["messages"]
        
        # Add system message
        system_msg = SystemMessage(content=self._get_system_prompt())
        full_messages = [system_msg] + messages
        
        # Call LLM with tools
        response = completion(
            model=self.model,
            messages=[self._format_message(msg) for msg in full_messages],
            tools=[self._tool_to_openai_format(tool) for tool in self.tools],
            tool_choice="auto",
        )
        
        ai_message = response.choices[0].message
        
        # Convert to LangChain message format
        if hasattr(ai_message, 'tool_calls') and ai_message.tool_calls:
            tool_calls = [
                {
                    "name": tc.function.name,
                    "args": tc.function.arguments,
                    "id": tc.id,
                }
                for tc in ai_message.tool_calls
            ]
            return {"messages": [AIMessage(content=ai_message.content or "", tool_calls=tool_calls)]}
        else:
            return {"messages": [AIMessage(content=ai_message.content)]}
    
    def _should_continue(self, state: MessagesState) -> Literal["tools", END]:
        """
        Decide whether to continue with tools or end
        """
        last_message = state["messages"][-1]
        
        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            return "tools"
        
        return END
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the agent"""
        return f"""You are a helpful story assistant for the interactive fiction project "{self.project.name}".

Your role is to help users understand and explore this branching narrative story by:
- Answering questions about characters, their relationships, and traits
- Providing information about scenes, plot points, and story structure  
- Explaining world-building facts and lore
- Analyzing story branches and endings

IMPORTANT INSTRUCTIONS:
1. When the user asks a question, THINK about what information you need
2. USE TOOLS to get accurate information from the story data
3. Do NOT make up or hallucinate information
4. If you're not sure about specific details, use tools like:
   - get_all_characters() to list all characters
   - get_character_by_name() for specific character details
   - get_all_scenes() to see the story structure
   - search_scenes() to find scenes about specific topics
   - count_endings() to analyze story branches

5. After getting tool results, provide a clear, helpful answer to the user

Current project: {self.project.name}
Locale: {self.project.locale}

Respond in the same language as the user's question (Chinese or English)."""
    
    def _format_message(self, msg) -> Dict:
        """Convert LangChain message to LiteLLM format"""
        if isinstance(msg, SystemMessage):
            return {"role": "system", "content": msg.content}
        elif isinstance(msg, HumanMessage):
            return {"role": "user", "content": msg.content}
        elif isinstance(msg, AIMessage):
            result = {"role": "assistant", "content": msg.content or ""}
            if hasattr(msg, 'tool_calls') and msg.tool_calls:
                result["tool_calls"] = [
                    {
                        "id": tc["id"],
                        "type": "function",
                        "function": {
                            "name": tc["name"],
                            "arguments": tc["args"]
                        }
                    }
                    for tc in msg.tool_calls
                ]
            return result
        elif isinstance(msg, ToolMessage):
            return {
                "role": "tool",
                "content": msg.content,
                "tool_call_id": msg.tool_call_id
            }
        else:
            return {"role": "user", "content": str(msg.content)}
    
    def _tool_to_openai_format(self, tool) -> Dict:
        """Convert LangChain tool to OpenAI function format"""
        return {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "project": {
                            "type": "object",
                            "description": "Project object (automatically provided)"
                        }
                    },
                    "required": []
                }
            }
        }
    
    def chat(self, user_message: str) -> tuple[str, List[Dict]]:
        """
        Chat with the agent
        
        Args:
            user_message: User's question or request
            
        Returns:
            (final_response, intermediate_steps)
            - final_response: The agent's final answer
            - intermediate_steps: List of tool calls and reasoning steps
        """
        # Invoke the agent
        result = self.agent.invoke({
            "messages": [HumanMessage(content=user_message)]
        })
        
        # Extract final response
        messages = result["messages"]
        final_response = ""
        intermediate_steps = []
        
        for msg in messages:
            if isinstance(msg, AIMessage):
                if hasattr(msg, 'tool_calls') and msg.tool_calls:
                    # Agent decided to use tools
                    for tc in msg.tool_calls:
                        intermediate_steps.append({
                            "type": "tool_call",
                            "tool": tc["name"],
                            "args": tc["args"]
                        })
                else:
                    # Final response
                    final_response = msg.content
            elif isinstance(msg, ToolMessage):
                # Tool result
                intermediate_steps.append({
                    "type": "tool_result",
                    "content": msg.content[:200] + "..." if len(msg.content) > 200 else msg.content
                })
        
        return final_response, intermediate_steps
    
    def stream_chat(self, user_message: str):
        """
        Stream chat responses (for future implementation)
        
        This would allow real-time display of agent thinking and tool usage
        """
        # TODO: Implement streaming with LangGraph
        pass
