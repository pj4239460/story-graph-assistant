"""
Base Tool Class for Agent
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List


class BaseTool(ABC):
    """Base class for all agent tools"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Tool name (used by LLM for function calling)"""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Tool description (helps LLM decide when to use it)"""
        pass
    
    @property
    @abstractmethod
    def parameters(self) -> Dict[str, Any]:
        """
        Tool parameters in JSON Schema format
        
        Example:
        {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Character name to search for"
                }
            },
            "required": ["name"]
        }
        """
        pass
    
    @abstractmethod
    def execute(self, **kwargs) -> str:
        """
        Execute the tool with given parameters
        
        Args:
            **kwargs: Tool parameters
            
        Returns:
            Tool execution result as string
        """
        pass
    
    def to_function_schema(self) -> Dict[str, Any]:
        """Convert tool to OpenAI function calling schema"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            }
        }
