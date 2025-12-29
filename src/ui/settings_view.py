"""
Settings View
"""
import streamlit as st
from src.models.ai import AISettings

def render_settings_view():
    """Render settings view"""
    i18n = st.session_state.i18n
    project_service = st.session_state.project_service
    project = project_service.get_project()
    
    st.header(f"⚙️ {i18n.t('tabs.settings')}")
    
    # AI Configuration
    st.subheader(f"🤖 {i18n.t('settings.ai_config')}")
    
    with st.form("settings_form"):
        # Token Limits
        st.markdown(f"#### {i18n.t('settings.token_limits')}")
        col1, col2 = st.columns(2)
        
        with col1:
            project_limit = st.number_input(
                i18n.t('settings.project_limit'),
                min_value=1000,
                max_value=1000000,
                value=project.aiSettings.projectTokenLimit,
                step=1000,
                help="Total token limit for the entire project"
            )
            
        with col2:
            daily_limit = st.number_input(
                i18n.t('settings.daily_limit'),
                min_value=1000,
                max_value=100000,
                value=project.aiSettings.dailyTokenSoftLimit,
                step=1000,
                help="Daily warning limit (does not block usage)"
            )
            
        st.divider()
        
        # Model Configuration
        st.markdown(f"#### {i18n.t('settings.model_config')}")
        
        provider = st.selectbox(
            i18n.t('settings.provider'),
            ["deepseek", "openai", "anthropic"],
            index=0 if project.aiSettings.provider == "deepseek" else 0, # Default to deepseek for now
            disabled=True, # Only deepseek supported in MVP
            help="Currently only DeepSeek is supported in MVP"
        )
        
        # Advanced model settings (collapsible)
        with st.expander("Advanced Model Settings"):
            model_extraction = st.text_input(
                "Extraction Model",
                value=project.aiSettings.modelExtraction
            )
            model_ooc = st.text_input(
                "OOC Detection Model",
                value=project.aiSettings.modelOOC
            )
            model_whatif = st.text_input(
                "What-If Model",
                value=project.aiSettings.modelWhatIf
            )
            
        submitted = st.form_submit_button(i18n.t('common.save'))
        
        if submitted:
            # Update settings
            new_settings = project.aiSettings.copy()
            new_settings.projectTokenLimit = project_limit
            new_settings.dailyTokenSoftLimit = daily_limit
            new_settings.modelExtraction = model_extraction
            new_settings.modelOOC = model_ooc
            new_settings.modelWhatIf = model_whatif
            
            # Save project
            project.aiSettings = new_settings
            project_service.save_project()
            
            st.success(f"✅ {i18n.t('settings.save_success')}")
            st.rerun()
