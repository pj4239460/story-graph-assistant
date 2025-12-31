"""
LLM Client (LiteLLM + DeepSeek)
"""
from __future__ import annotations
from typing import List, Dict, Tuple
import os

try:
    from litellm import completion
    LITELLM_AVAILABLE = True
except ImportError:
    LITELLM_AVAILABLE = False

from ..models.project import Project
from .token_stats import record_usage


class LLMClient:
    """Unified LLM client"""
    
    def __init__(self, app_db=None):
        # Load all API keys from database if available
        if app_db:
            # DeepSeek
            if "DEEPSEEK_API_KEY" not in os.environ:
                deepseek_key = app_db.get_setting("deepseek_api_key", "")
                if deepseek_key:
                    os.environ["DEEPSEEK_API_KEY"] = deepseek_key
                    print("INFO: Loaded DEEPSEEK_API_KEY from database")
            
            # OpenAI
            if "OPENAI_API_KEY" not in os.environ:
                openai_key = app_db.get_setting("openai_api_key", "")
                if openai_key:
                    os.environ["OPENAI_API_KEY"] = openai_key
                    print("INFO: Loaded OPENAI_API_KEY from database")
            
            # Anthropic
            if "ANTHROPIC_API_KEY" not in os.environ:
                anthropic_key = app_db.get_setting("anthropic_api_key", "")
                if anthropic_key:
                    os.environ["ANTHROPIC_API_KEY"] = anthropic_key
                    print("INFO: Loaded ANTHROPIC_API_KEY from database")
            
            # Google Gemini
            if "GEMINI_API_KEY" not in os.environ:
                gemini_key = app_db.get_setting("gemini_api_key", "")
                if gemini_key:
                    os.environ["GEMINI_API_KEY"] = gemini_key
                    print("INFO: Loaded GEMINI_API_KEY from database")
        
        if not LITELLM_AVAILABLE:
            print("WARNING: litellm not installed. AI features will be disabled.")
    
    def call(
        self,
        project: Project,
        task_type: str,
        messages: List[Dict],
        max_tokens: int = 1024,
        thinking: bool = False,
    ) -> Tuple[str, Dict]:
        """
        Call LLM
        
        Args:
            project: Project object
            task_type: Task type (summary/extraction/ooc/what_if)
            messages: Message list
            max_tokens: Maximum tokens
            thinking: Enable reasoning mode
            
        Returns:
            (response_content, usage_info)
        """
        if not LITELLM_AVAILABLE:
            return "LiteLLM not installed. Please install: pip install litellm", {}
        
        # Select model based on task type
        model = self._select_model(project, task_type)
        
        # Build call parameters
        kwargs = {}
        if "reasoner" in model or thinking:
            kwargs["thinking"] = {"type": "enabled"}
        
        try:
            resp = completion(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                **kwargs,
            )
            
            # Extract usage information
            usage = {}
            if hasattr(resp, "usage") and resp.usage:
                usage = {
                    "total_tokens": getattr(resp.usage, "total_tokens", 0),
                    "input_tokens": getattr(resp.usage, "prompt_tokens", 0),
                    "output_tokens": getattr(resp.usage, "completion_tokens", 0),
                }
            
            # Record token usage
            record_usage(project, task_type, usage)
            
            # Return content and usage
            content = resp.choices[0].message.content
            return content, usage
            
        except Exception as e:
            return f"Error calling LLM: {str(e)}", {}
    
    def _select_model(self, project: Project, task_type: str) -> str:
        """Select model based on task type"""
        if task_type in ("summary", "extraction"):
            return project.aiSettings.modelExtraction
        elif task_type in ("ooc", "character_arc"):
            return project.aiSettings.modelOOC
        elif task_type in ("what_if", "world_sim"):
            return project.aiSettings.modelWhatIf
        else:
            return project.aiSettings.modelExtraction
