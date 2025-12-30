"""
Scene Checkup Panel - Structured AI Analysis
Provides one-click comprehensive scene analysis with caching
"""
import streamlit as st
from typing import Dict, Optional
from datetime import datetime
import json

from ..models.project import Project
from ..models.scene import Scene
from ..services.ai_service import AIService


class SceneCheckup:
    """Scene analysis with structured output and caching"""
    
    def __init__(self, ai_service: AIService):
        self.ai_service = ai_service
        
        # Initialize cache in session state
        if 'scene_checkup_cache' not in st.session_state:
            st.session_state.scene_checkup_cache = {}
    
    def get_cache_key(self, project: Project, scene: Scene) -> str:
        """Generate cache key for scene analysis"""
        # Use project name, scene ID, and scene body hash to detect changes
        scene_hash = hash(scene.body)
        return f"{project.name}_{scene.id}_{scene_hash}"
    
    def run_checkup(self, project: Project, scene: Scene, force_refresh: bool = False) -> Dict:
        """
        Run comprehensive scene analysis
        
        Returns:
            {
                "summary": str,
                "facts": List[str],
                "ooc_risk": {"level": "low|medium|high", "details": str},
                "emotions": List[str],
                "metadata": {...},
                "timestamp": str,
                "cached": bool
            }
        """
        cache_key = self.get_cache_key(project, scene)
        
        # Check cache
        if not force_refresh and cache_key in st.session_state.scene_checkup_cache:
            result = st.session_state.scene_checkup_cache[cache_key]
            result['cached'] = True
            return result
        
        # Run fresh analysis
        with st.spinner("🔍 Analyzing scene..."):
            result = {
                "timestamp": datetime.now().isoformat(),
                "cached": False,
            }
            
            # 1. Generate summary
            try:
                if scene.summary:
                    result['summary'] = scene.summary
                else:
                    result['summary'] = self.ai_service.summarize_scene(project, scene)
            except Exception as e:
                result['summary'] = f"Error: {str(e)}"
            
            # 2. Extract facts
            try:
                result['facts'] = self.ai_service.extract_facts(project, scene)
            except Exception as e:
                result['facts'] = [f"Error: {str(e)}"]
            
            # 3. OOC check (if scene has participants)
            result['ooc_risk'] = {"level": "unknown", "details": "Not yet implemented"}
            # TODO: Implement once check_ooc is ready in AIService
            # if scene.participants:
            #     result['ooc_risk'] = self.ai_service.check_ooc(project, scene)
            
            # 4. Extract emotions/tags (simple version)
            result['emotions'] = self._extract_emotions(scene)
            
            # 5. Metadata
            result['metadata'] = {
                "scene_id": scene.id,
                "scene_title": scene.title,
                "chapter": scene.chapter or "N/A",
                "choices_count": len(scene.choices),
                "tags": scene.tags,
                "participants": scene.participants,  # Already a list of character IDs
            }
            
            # Cache result
            st.session_state.scene_checkup_cache[cache_key] = result
            
            return result
    
    def _extract_emotions(self, scene: Scene) -> list:
        """Extract emotion keywords from scene content (simple heuristic)"""
        emotion_keywords = {
            "joy": ["happy", "笑", "欢乐", "兴奋"],
            "sadness": ["sad", "悲伤", "哭", "失落"],
            "anger": ["angry", "愤怒", "生气", "暴怒"],
            "fear": ["afraid", "恐惧", "害怕", "紧张"],
            "surprise": ["surprised", "惊讶", "意外", "震惊"],
        }
        
        detected = []
        text = (scene.body + " " + " ".join(scene.tags)).lower()
        
        for emotion, keywords in emotion_keywords.items():
            if any(kw in text for kw in keywords):
                detected.append(emotion)
        
        return detected or ["neutral"]
    
    def render_checkup_panel(self, project: Project, scene: Scene):
        """Render the scene checkup panel in Streamlit UI"""
        st.subheader(f"🔬 Scene Checkup: {scene.title}")
        
        # Control buttons
        col1, col2 = st.columns([3, 1])
        with col1:
            st.caption(f"Scene ID: `{scene.id}` | Chapter: {scene.chapter or 'N/A'}")
        with col2:
            if st.button("🔄 Refresh", key=f"refresh_{scene.id}"):
                result = self.run_checkup(project, scene, force_refresh=True)
            else:
                result = self.run_checkup(project, scene, force_refresh=False)
        
        # Display cached status
        if result['cached']:
            st.info("📦 Using cached analysis. Click 'Refresh' to re-analyze.")
        
        # Render results
        st.markdown("---")
        
        # 1. Summary
        with st.expander("📝 Summary", expanded=True):
            st.write(result['summary'])
        
        # 2. Extracted Facts
        with st.expander(f"🌍 Extracted Facts & Plot Points ({len(result['facts'])})", expanded=True):
            if result['facts'] and not result['facts'][0].startswith("Error"):
                for fact in result['facts']:
                    st.markdown(f"- {fact}")
            else:
                st.caption("No facts extracted or error occurred.")
        
        # 3. OOC Risk
        with st.expander("⚠️ OOC Risk Assessment", expanded=False):
            risk_level = result['ooc_risk']['level']
            if risk_level == "low":
                st.success("✅ Low risk - Characters behave consistently")
            elif risk_level == "medium":
                st.warning("⚠️ Medium risk - Some behaviors may need review")
            elif risk_level == "high":
                st.error("🚨 High risk - Potential out-of-character issues")
            else:
                st.info("🔧 OOC detection not yet implemented")
            
            st.caption(result['ooc_risk']['details'])
        
        # 4. Emotions
        st.markdown("**Detected Emotions:**")
        emotion_icons = {
            "joy": "😊",
            "sadness": "😢",
            "anger": "😠",
            "fear": "😨",
            "surprise": "😮",
            "neutral": "😐",
        }
        cols = st.columns(len(result['emotions']))
        for i, emotion in enumerate(result['emotions']):
            with cols[i]:
                st.metric(emotion.title(), emotion_icons.get(emotion, "🎭"))
        
        # 5. Metadata
        with st.expander("📊 Scene Metadata", expanded=False):
            meta = result['metadata']
            st.json({
                "Scene ID": meta['scene_id'],
                "Chapter": meta['chapter'],
                "Choices": meta['choices_count'],
                "Tags": meta['tags'],
                "Participants": meta['participants'],
            })
        
        # Export button
        st.markdown("---")
        if st.button("💾 Export Report", key=f"export_{scene.id}"):
            # Export as JSON
            report_json = json.dumps(result, indent=2, ensure_ascii=False)
            st.download_button(
                label="Download JSON",
                data=report_json,
                file_name=f"checkup_{scene.id}.json",
                mime="application/json"
            )


def render_scene_checkup_tab(project: Project, scene: Scene, ai_service: AIService):
    """Render scene checkup as a tab in scene details"""
    checkup = SceneCheckup(ai_service)
    checkup.render_checkup_panel(project, scene)
