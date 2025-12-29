"""
Streamlit Application Entry Point
"""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import streamlit as st

from src.repositories.json_repo import JsonProjectRepository
from src.services.project_service import ProjectService
from src.services.scene_service import SceneService
from src.services.character_service import CharacterService
from src.services.ai_service import AIService
from src.infra.i18n import get_i18n
from src.infra.app_db import AppDatabase
from src.infra.vector_db import VectorDatabase
from src.ui.layout import render_main_layout


def init_services():
    """Initialize services"""
    if "services_initialized" not in st.session_state:
        # Initialize DB
        st.session_state.app_db = AppDatabase()
        
        # Initialize Vector DB (optional, will fallback to keyword search if unavailable)
        print("Initializing Vector Database...")
        st.session_state.vector_db = VectorDatabase()
        if not st.session_state.vector_db.is_available():
            print("Vector database not available. Using keyword search fallback.")
        
        st.session_state.project_service = ProjectService(JsonProjectRepository())
        st.session_state.scene_service = SceneService()
        st.session_state.character_service = CharacterService()
        # st.session_state.ai_service = AIService() # Moved out to ensure update
        st.session_state.services_initialized = True
    
    # Always re-initialize stateless services to pick up code changes during dev
    st.session_state.ai_service = AIService()
    # Inject vector_db into ai_service's search_service
    st.session_state.ai_service.search_service.set_vector_db(st.session_state.vector_db)
    
    # Initialize i18n
    if "locale" not in st.session_state:
        # Try to load from DB, default to 'zh'
        db_locale = st.session_state.app_db.get_setting("locale", "zh")
        st.session_state.locale = db_locale
        
    if "i18n" not in st.session_state:
        st.session_state.i18n = get_i18n(st.session_state.locale)


def main():
    """Main function"""
    st.set_page_config(
        page_title="Story Graph Assistant | 故事图谱助手",
        page_icon="📖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize services
    init_services()
    
    # Render main layout
    render_main_layout()


if __name__ == "__main__":
    main()
