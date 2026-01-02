"""
Search Service - RAG for story content retrieval using Vector Database
"""
from __future__ import annotations
from typing import List, Dict, Set, Optional
from ..models.project import Project
from ..models.character import Character
from ..models.scene import Scene
from ..infra.vector_db import VectorDatabase


class SearchService:
    """Content search and retrieval using semantic search"""
    
    def __init__(self, vector_db: Optional[VectorDatabase] = None):
        self.vector_db = vector_db
    
    def set_vector_db(self, vector_db: VectorDatabase):
        """Set the vector database instance"""
        self.vector_db = vector_db
    
    def search_relevant_content(
        self, 
        project: Project, 
        query: str, 
        max_chars: int = 3,
        max_scenes: int = 3
    ) -> Dict[str, any]:
        """
        Search for relevant characters and scenes using semantic search
        
        Args:
            project: Project object
            query: User's question
            max_chars: Maximum number of characters to return
            max_scenes: Maximum number of scenes to return
            
        Returns:
            {
                "characters": List[Character],
                "scenes": List[Scene],
                "matched_keywords": Set[str]
            }
        """
        matched_keywords = set()
        
        if not self.vector_db or not self.vector_db.is_available():
            # Fallback to keyword search if vector DB not available
            return self._keyword_search(project, query, max_chars, max_scenes)
        
        # Get project identifier
        project_id = project.id
        
        # Search using vector database
        char_results = self.vector_db.search_characters(project_id, query, top_k=max_chars)
        scene_results = self.vector_db.search_scenes(project_id, query, top_k=max_scenes)
        
        # Convert results back to model objects
        selected_chars = []
        for result in char_results:
            char_id = result['id']
            if char_id in project.characters:
                selected_chars.append(project.characters[char_id])
                matched_keywords.add(project.characters[char_id].name)
        
        selected_scenes = []
        for result in scene_results:
            scene_id = result['id']
            if scene_id in project.scenes:
                selected_scenes.append(project.scenes[scene_id])
                matched_keywords.add(project.scenes[scene_id].title)
        
        return {
            "characters": selected_chars,
            "scenes": selected_scenes,
            "matched_keywords": matched_keywords
        }
    
    def _keyword_search(
        self,
        project: Project,
        query: str,
        max_chars: int,
        max_scenes: int
    ) -> Dict[str, any]:
        """Fallback keyword-based search (original implementation)"""
        query_lower = query.lower()
        matched_keywords = set()
        
        # Search characters
        relevant_chars = []
        for char in project.characters.values():
            score = 0
            if char.name.lower() in query_lower:
                score += 10
                matched_keywords.add(char.name)
            if char.alias and char.alias.lower() in query_lower:
                score += 8
                matched_keywords.add(char.alias)
            if any(word in char.description.lower() for word in query_lower.split() if len(word) > 2):
                score += 2
            for trait in char.traits:
                if trait.lower() in query_lower:
                    score += 3
                    matched_keywords.add(trait)
            
            if score > 0:
                relevant_chars.append((score, char))
        
        relevant_chars.sort(key=lambda x: x[0], reverse=True)
        selected_chars = [char for _, char in relevant_chars[:max_chars]]
        
        # Search scenes
        relevant_scenes = []
        for scene in project.scenes.values():
            score = 0
            if scene.title.lower() in query_lower:
                score += 10
                matched_keywords.add(scene.title)
            if scene.chapter and scene.chapter.lower() in query_lower:
                score += 5
                matched_keywords.add(scene.chapter)
            for tag in scene.tags:
                if tag.lower() in query_lower:
                    score += 4
                    matched_keywords.add(tag)
            for char in selected_chars:
                if char.id in scene.participants:
                    score += 6
            if scene.body and any(word in scene.body.lower() for word in query_lower.split() if len(word) > 3):
                score += 1
            
            if score > 0:
                relevant_scenes.append((score, scene))
        
        relevant_scenes.sort(key=lambda x: x[0], reverse=True)
        selected_scenes = [scene for _, scene in relevant_scenes[:max_scenes]]
        
        return {
            "characters": selected_chars,
            "scenes": selected_scenes,
            "matched_keywords": matched_keywords
        }
    
    def get_contextual_summary(self, project: Project, query: str) -> str:
        """
        Generate a contextual summary for the query (for RAG context)
        
        Returns a formatted string containing relevant characters, scenes, and world facts
        """
        results = self.search_relevant_content(project, query)
        
        context = f"Project: {project.name}\n\n"
        
        # Add matched characters
        if results["characters"]:
            context += "=== RELEVANT CHARACTERS ===\n"
            for char in results["characters"]:
                context += f"\n**{char.name}**"
                if char.alias:
                    context += f" (aka {char.alias})"
                context += f"\n- Description: {char.description}\n"
                if char.traits:
                    context += f"- Traits: {', '.join(char.traits)}\n"
                if char.goals:
                    context += f"- Goals: {', '.join(char.goals)}\n"
                if char.fears:
                    context += f"- Fears: {', '.join(char.fears)}\n"
        
        # Add matched scenes
        if results["scenes"]:
            context += "\n=== RELEVANT SCENES ===\n"
            for scene in results["scenes"]:
                context += f"\n**{scene.title}**"
                if scene.chapter:
                    context += f" (Chapter: {scene.chapter})"
                context += "\n"
                
                if scene.summary:
                    context += f"Summary: {scene.summary}\n"
                elif scene.body:
                    # Use truncated body if no summary
                    preview = scene.body[:300] + "..." if len(scene.body) > 300 else scene.body
                    context += f"Content: {preview}\n"
                
                if scene.tags:
                    context += f"Tags: {', '.join(scene.tags)}\n"
        
        # Add world facts if they exist and are relevant
        if project.worldState.facts:
            # Simple keyword matching for facts (can be enhanced with vector search later)
            relevant_facts = []
            query_lower = query.lower()
            for fact in project.worldState.facts.values():
                if any(word in fact.content.lower() for word in query_lower.split() if len(word) > 2):
                    relevant_facts.append(fact)
            
            if relevant_facts:
                context += "\n=== WORLD FACTS & LORE ===\n"
                for fact in relevant_facts[:5]:  # Limit to top 5 facts
                    context += f"\n- {fact.content}"
                    if fact.category:
                        context += f" [{fact.category}]"
                    if fact.sourceSceneId:
                        context += f" (from scene: {fact.sourceSceneId})"
                    context += "\n"
        
        # If nothing matched, provide a general summary
        if not results["characters"] and not results["scenes"] and not project.worldState.facts:
            context += "\n=== GENERAL PROJECT INFO ===\n"
            context += f"Total Characters: {len(project.characters)}\n"
            context += f"Total Scenes: {len(project.scenes)}\n"
            context += f"Total World Facts: {len(project.worldState.facts)}\n"
            context += "\nNote: No specific matches found for your query. You may want to be more specific.\n"
        
        return context
