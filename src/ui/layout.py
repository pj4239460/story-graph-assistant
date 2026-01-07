"""
Main layout management
"""
import streamlit as st

from .sidebar import render_sidebar
from .routes_view import render_routes_view
from .characters_view import render_characters_view
from .ai_tools_view import render_ai_tools_view
from .chat_view import render_chat_view
from .director_view import render_director_view
from .settings_view import render_settings_view


def render_main_layout():
    """Render main layout"""
    i18n = st.session_state.i18n
    
    # Sidebar
    render_sidebar()
    
    # Main title
    st.title(f"📖 {i18n.t('app.title')}")
    st.caption(i18n.t('app.subtitle'))
    
    # Check if project is loaded
    project_service = st.session_state.project_service
    
    if not project_service.has_project():
        st.info(i18n.t('app.no_project_hint'))
        
        # Display welcome message
        st.markdown(f"""
        ## {i18n.t('app.welcome_title')}
        
        {i18n.t('app.welcome_desc')}
        
        ### ✨ {i18n.t('welcome.features_title')}
        
        - 📊 **{i18n.t('welcome.feature_routes')}** - {i18n.t('welcome.feature_routes_desc')}
        - 👥 **{i18n.t('welcome.feature_characters')}** - {i18n.t('welcome.feature_characters_desc')}
        - 🤖 **{i18n.t('welcome.feature_ai')}** - {i18n.t('welcome.feature_ai_desc')}
        - 🎲 **{i18n.t('welcome.feature_whatif')}** - {i18n.t('welcome.feature_whatif_desc')}
        
        ### 🚀 {i18n.t('welcome.quickstart_title')}
        
        1. {i18n.t('welcome.quickstart_step1')}
        2. {i18n.t('welcome.quickstart_step2')}
        """)
        return
    
    # Display project info
    project = project_service.get_project()
    st.success(f"✅ {i18n.t('app.current_project')}：**{project.name}**")
    
    # Token usage statistics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            i18n.t('metrics.project_tokens'),
            f"{project.tokenStats.projectUsed:,}",
            f"/ {project.aiSettings.projectTokenLimit:,}"
        )
    with col2:
        st.metric(
            i18n.t('metrics.today_usage'),
            f"{project.tokenStats.todayUsed:,}",
            f"/ {project.aiSettings.dailyTokenSoftLimit:,}"
        )
    with col3:
        usage_pct = (project.tokenStats.projectUsed / project.aiSettings.projectTokenLimit) * 100
        st.metric(i18n.t('metrics.usage_rate'), f"{usage_pct:.1f}%")
    
    st.divider()
    
    # Tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        f"📊 {i18n.t('tabs.routes')}", 
        f"👥 {i18n.t('tabs.characters')}", 
        f"🎬 World Director",
        f"🤖 {i18n.t('tabs.ai_tools')}",
        f"💬 {i18n.t('tabs.chat')}",
        f"⚙️ {i18n.t('tabs.settings')}"
    ])
    
    with tab1:
        render_routes_view()
    
    with tab2:
        render_characters_view()
    
    with tab3:
        render_director_view()
    
    with tab4:
        render_ai_tools_view()
        
    with tab5:
        render_chat_view()
        
    with tab6:
        render_settings_view()
    
    # Footer with copyright
    st.divider()
    cols = st.columns([2, 1])
    with cols[0]:
        st.caption("© 2025 Ji PEI | Story Graph Assistant | Licensed under MIT")
    with cols[1]:
        st.caption("Powered by Streamlit & DeepSeek AI")
