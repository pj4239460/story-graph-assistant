"""
AI Service - AI functionality service (MVP version)
"""
from __future__ import annotations
from typing import Dict, List
import uuid

from ..models.project import Project
from ..models.scene import Scene
from ..models.world import WorldFact
from ..infra.llm_client import LLMClient
from ..infra.token_stats import check_token_limit
from .search_service import SearchService


class AIService:
    """AI functionality service"""
    
    def __init__(self, app_db=None):
        self.llm_client = LLMClient(app_db)
        self.search_service = SearchService()
    
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
    
    def extract_facts(self, project: Project, scene: Scene, save_to_project: bool = True) -> List[str]:
        """
        Extract worldview facts from scene and optionally save to project.worldState.facts
        
        Args:
            project: Project object
            scene: Scene object
            save_to_project: Whether to persist extracted facts to project (default: True)
            
        Returns:
            List of extracted fact content strings (for backward compatibility)
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

Each piece of information should be on one line, format: [Category] Content
Example:
[Character] Alice is a skilled hacker
[Setting] The city is under constant surveillance
[Plot] A mysterious virus is spreading through the network
"""
            }
        ]
        
        response, _ = self.llm_client.call(
            project=project,
            task_type="extraction",
            messages=messages,
            max_tokens=500,
        )
        
        # Parse and structure the facts
        fact_contents = []
        for line in response.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            # Parse [Category] Content format
            category = None
            content = line
            if line.startswith('[') and ']' in line:
                end_bracket = line.index(']')
                category = line[1:end_bracket].strip().lower()
                content = line[end_bracket + 1:].strip()
            
            if content:
                fact_contents.append(content)
                
                # Save to project if requested
                if save_to_project:
                    fact_id = f"fact_{scene.id}_{uuid.uuid4().hex[:8]}"
                    world_fact = WorldFact(
                        id=fact_id,
                        content=content,
                        category=category,
                        sourceSceneId=scene.id
                    )
                    project.worldState.facts[fact_id] = world_fact
        
        return fact_contents
    
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

    def chat_with_story(self, project: Project, query: str, history: List[Dict]) -> str:
        """
        Chat with the story context using RAG (Retrieval-Augmented Generation)
        
        Args:
            project: Project object
            query: User question
            history: Chat history [{"role": "user", "content": "..."}, ...]
            
        Returns:
            AI response
        """
        # Check token limit (reduced estimate since we use RAG)
        can_proceed, message = check_token_limit(project, estimated_tokens=1000)
        if not can_proceed:
            return f"Error: {message}"
            
        # Use SearchService to retrieve only relevant content (RAG approach)
        context = self.search_service.get_contextual_summary(project, query)
        
        # Build System Prompt with retrieved context
        system_prompt = {
            "role": "system",
            "content": f"""You are an expert story consultant and co-author for the project "{project.name}".

You have been provided with RELEVANT context based on the user's question. Answer based on this context.
If the answer is not in the provided context, acknowledge what you don't know and suggest what additional information might help.

=== RETRIEVED CONTEXT ===
{context}

=== INSTRUCTIONS ===
- Answer the user's question using the context above
- Be specific and reference the characters/scenes mentioned
- If the context doesn't contain enough information, say so honestly
- Suggest creative ideas that are consistent with the existing lore
"""
        }
        
        # Combine messages
        messages = [system_prompt] + history + [{"role": "user", "content": query}]
        
        # Call LLM
        try:
            response, _ = self.llm_client.call(
                project=project,
                task_type="what_if", # Use reasoning model if available
                messages=messages,
                max_tokens=1000
            )
            return response
        except Exception as e:
            import traceback
            print(f"LLM CALL ERROR: {str(e)}\n{traceback.format_exc()}")
            raise e


