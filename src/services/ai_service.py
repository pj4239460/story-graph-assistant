"""
AI Service - AI functionality service (MVP version)
"""
from __future__ import annotations
from typing import Dict, List

from ..models.project import Project
from ..models.scene import Scene
from ..infra.llm_client import LLMClient
from ..infra.token_stats import check_token_limit


class AIService:
    """AI functionality service"""
    
    def __init__(self):
        self.llm_client = LLMClient()
    
    def summarize_scene(self, project: Project, scene: Scene) -> str:
        """
        Generate scene summary
        
        Args:
            project: Project object
            scene: Scene object
            
        Returns:
            Scene summary text
        """
        # Check token limit
        can_proceed, message = check_token_limit(project, estimated_tokens=500)
        if not can_proceed:
            return f"Error: {message}"
        
        # Build prompt
        messages = [
            {
                "role": "system",
                "content": "You are a professional story analysis assistant. Generate a concise summary for the given scene."
            },
            {
                "role": "user",
                "content": f"Scene Title: {scene.title}\n\nScene Content:\n{scene.body}\n\nPlease generate a concise summary (50-100 words)."
            }
        ]
        
        # Call LLM
        summary, _ = self.llm_client.call(
            project=project,
            task_type="summary",
            messages=messages,
            max_tokens=200,
        )
        
        return summary
    
    def extract_facts(self, project: Project, scene: Scene) -> List[str]:
        """
        Extract worldview facts from scene
        
        Args:
            project: Project object
            scene: Scene object
            
        Returns:
            List of extracted facts
        """
        can_proceed, message = check_token_limit(project, estimated_tokens=800)
        if not can_proceed:
            return [f"Error: {message}"]
        
        messages = [
            {
                "role": "system",
                "content": "You are a professional story analysis assistant. Extract key worldview facts, character settings, and plot information from scenes."
            },
            {
                "role": "user",
                "content": f"""Scene Title: {scene.title}

Scene Content:
{scene.body}

Please extract key information from this scene, including:
1. Character traits and background
2. Worldview settings
3. Important plot threads

Each piece of information should be on one line, format: [Type] Content
"""
            }
        ]
        
        response, _ = self.llm_client.call(
            project=project,
            task_type="extraction",
            messages=messages,
            max_tokens=500,
        )
        
        # Simple parsing of returned list
        facts = [line.strip() for line in response.split('\n') if line.strip()]
        return facts
    
    def check_ooc(
        self,
        project: Project,
        character_id: str,
        scene: Scene
    ) -> Dict[str, any]:
        """
        Check if character is OOC (Out of Character)
        
        Args:
            project: Project object
            character_id: Character ID
            scene: Scene object
            
        Returns:
            {
                "is_ooc": bool,
                "confidence": float,
                "explanation": str
            }
        """
        character = project.characters.get(character_id)
        if character is None:
            return {
                "is_ooc": False,
                "confidence": 0.0,
                "explanation": "Character does not exist"
            }
        
        can_proceed, message = check_token_limit(project, estimated_tokens=1000)
        if not can_proceed:
            return {
                "is_ooc": False,
                "confidence": 0.0,
                "explanation": f"Error: {message}"
            }
        
        # Build character profile
        character_profile = f"""Character Name: {character.name}
Description: {character.description}
Traits: {', '.join(character.traits)}
Goals: {', '.join(character.goals)}
Fears: {', '.join(character.fears)}
"""
        
        messages = [
            {
                "role": "system",
                "content": "You are a professional character consistency analyst. Analyze if a character's behavior matches their established personality traits."
            },
            {
                "role": "user",
                "content": f"""{character_profile}

Scene Content:
{scene.body}

Analyze if {character.name}'s behavior in this scene is consistent with their personality profile.

Return your analysis in this EXACT format:

JUDGMENT: [CONSISTENT or INCONSISTENT]
CONFIDENCE: [a number between 0.0 and 1.0]
REASONING: [2-3 sentences explaining your judgment, focusing on specific traits and behaviors]

Example:
JUDGMENT: CONSISTENT
CONFIDENCE: 0.85
REASONING: The character's cautious approach aligns with their "careful" trait. Their decision to gather information before acting matches their "analytical" personality. No significant deviations observed.
"""
            }
        ]
        
        response, _ = self.llm_client.call(
            project=project,
            task_type="ooc",
            messages=messages,
            max_tokens=300,
        )
        
        # Parse structured response
        is_ooc = False
        confidence = 0.5
        explanation = "Unable to analyze"
        
        if response:
            lines = response.strip().split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('JUDGMENT:'):
                    judgment = line.split(':', 1)[1].strip().upper()
                    is_ooc = 'INCONSISTENT' in judgment
                elif line.startswith('CONFIDENCE:'):
                    try:
                        confidence = float(line.split(':', 1)[1].strip())
                    except:
                        confidence = 0.5
                elif line.startswith('REASONING:'):
                    explanation = line.split(':', 1)[1].strip()
            
            # If no structured output, fallback to full response
            if explanation == "Unable to analyze":
                explanation = response
        
        return {
            "is_ooc": is_ooc,
            "confidence": confidence,
            "explanation": explanation
        }


