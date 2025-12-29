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
        # Check DeepSeek API Key
        if "DEEPSEEK_API_KEY" not in os.environ:
            # Try to load from database
            if app_db:
                api_key = app_db.get_setting("deepseek_api_key", "")
                if api_key:
                    os.environ["DEEPSEEK_API_KEY"] = api_key
                    print("INFO: Loaded DEEPSEEK_API_KEY from database")
                else:
                    print("WARNING: DEEPSEEK_API_KEY not set in environment or database")
            else:
                print("WARNING: DEEPSEEK_API_KEY not set in environment")
        
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
