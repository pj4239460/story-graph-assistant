"""
Sidebar component
"""
import streamlit as st
import os
from ..services.vector_index_service import VectorIndexService


def render_sidebar():
    """Render sidebar"""
    i18n = st.session_state.i18n
    app_db = st.session_state.app_db
    
    with st.sidebar:
        st.header(f"📁 {i18n.t('sidebar.project_management')}")
        
        # Author attribution
        st.caption("Created by Ji PEI | Story Graph Assistant")
        
        project_service = st.session_state.project_service
        
        # Project operations
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button(f"➕ {i18n.t('sidebar.new_project')}", use_container_width=True):
                st.session_state.show_create_dialog = True
        
        with col2:
            if st.button(f"📂 {i18n.t('sidebar.load_project')}", use_container_width=True):
                st.session_state.show_load_dialog = True
        
        # Sample project buttons
        st.caption("📚 Sample Projects / 示例项目:")
        col_s1, col_s2 = st.columns(2)
        
        with col_s1:
            if st.button("🇨🇳 中文", use_container_width=True, help="时间旅行者 (中文版)"):
                sample_path = os.path.abspath("./examples/sample_project/project.json")
                if os.path.exists(sample_path):
                    try:
                        project_service.load_project(sample_path)
                        app_db.add_recent_project(sample_path, "示例项目 - 时间旅行者")
                        st.success("✅ 中文示例已加载！")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to load sample: {str(e)}")
                else:
                    st.error(f"Sample not found: {sample_path}")
        
        with col_s2:
            if st.button("🇺🇸 EN", use_container_width=True, help="Time Traveler (English)"):
                sample_path = os.path.abspath("./examples/sample_project_en/project.json")
                if os.path.exists(sample_path):
                    try:
                        project_service.load_project(sample_path)
                        app_db.add_recent_project(sample_path, "Sample Project - Time Traveler")
                        st.success("✅ English sample loaded!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to load sample: {str(e)}")
                else:
                    st.error(f"Sample not found: {sample_path}")
        
        # Create project dialog
        if st.session_state.get("show_create_dialog", False):
            with st.form("create_project_form"):
                st.subheader(i18n.t('sidebar.create_new_project'))
                name = st.text_input(i18n.t('sidebar.project_name'), placeholder=i18n.t('sidebar.my_story'))
                locale = st.selectbox(
                    i18n.t('sidebar.language'), 
                    ["zh", "en"], 
                    format_func=lambda x: "中文" if x == "zh" else "English"
                )
                
                submitted = st.form_submit_button(i18n.t('common.create'))
                if submitted and name:
                    project = project_service.create_project(name, locale)
                    # Add to recent projects (assuming default path ./projects/name.json)
                    default_path = os.path.abspath(f"./projects/{name}.json")
                    app_db.add_recent_project(default_path, name)
                    
                    st.session_state.show_create_dialog = False
                    st.success(f"✅ {i18n.t('sidebar.project_created', name=name)}")
                    st.rerun()
        
        # Load project dialog
        if st.session_state.get("show_load_dialog", False):
            st.subheader(i18n.t('sidebar.load_project_title'))
            
            # Recent projects list
            recent_projects = app_db.get_recent_projects()
            if recent_projects:
                st.caption("🕒 Recent Projects")
                for rp in recent_projects:
                    col_rp1, col_rp2 = st.columns([4, 1])
                    with col_rp1:
                        if st.button(f"📄 {rp['name']}", key=f"load_recent_{rp['path']}", help=rp['path'], use_container_width=True):
                            try:
                                project = project_service.load_project(rp['path'])
                                app_db.add_recent_project(rp['path'], project.name)
                                # Index project in vector database
                                if 'vector_db' in st.session_state:
                                    VectorIndexService.index_project(project, st.session_state.vector_db)
                                st.session_state.show_load_dialog = False
                                st.success(f"✅ {i18n.t('sidebar.project_loaded', name=project.name)}")
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ {i18n.t('sidebar.load_failed', error=str(e))}")
                    with col_rp2:
                        if st.button("❌", key=f"del_recent_{rp['path']}", help="Remove from history"):
                            app_db.remove_recent_project(rp['path'])
                            st.rerun()

            with st.form("load_project_form"):
                path = st.text_input(i18n.t('sidebar.project_path'), placeholder="path/to/project.json")
                
                submitted = st.form_submit_button(i18n.t('common.load'))
                if submitted and path:
                    try:
                        project = project_service.load_project(path)
                        app_db.add_recent_project(path, project.name)
                        # Index project in vector database
                        if 'vector_db' in st.session_state:
                            VectorIndexService.index_project(project, st.session_state.vector_db)
                        st.session_state.show_load_dialog = False
                        st.success(f"✅ {i18n.t('sidebar.project_loaded', name=project.name)}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ {i18n.t('sidebar.load_failed', error=str(e))}")
        
        # Save project
        if project_service.has_project():
            st.divider()
            
            if st.button(f"💾 {i18n.t('sidebar.save_project')}", use_container_width=True):
                if project_service.current_path:
                    project_service.save_project()
                    # Update timestamp in recent projects
                    app_db.add_recent_project(project_service.current_path, project_service.get_project().name)
                    st.success(f"✅ {i18n.t('sidebar.project_saved')}")
                else:
                    st.session_state.show_save_as_dialog = True
            
            # Save as dialog
            if st.session_state.get("show_save_as_dialog", False):
                with st.form("save_as_form"):
                    st.subheader(i18n.t('sidebar.save_as'))
                    save_path = st.text_input(
                        i18n.t('sidebar.save_path'),
                        value=f"./projects/{project_service.get_project().name}.json"
                    )
                    
                    submitted = st.form_submit_button(i18n.t('common.save'))
                    if submitted and save_path:
                        try:
                            project_service.save_project(save_path)
                            # Add to recent projects
                            app_db.add_recent_project(save_path, project_service.get_project().name)
                            
                            st.session_state.show_save_as_dialog = False
                            st.success(f"✅ {i18n.t('sidebar.saved_to', path=save_path)}")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ {i18n.t('sidebar.save_failed', error=str(e))}")
        
        # API Settings
        st.divider()
        with st.expander(f"⚙️ {i18n.t('sidebar.api_settings')}"):
            st.caption("🔑 LLM API Keys - Choose your provider")
            
            # Tabs for different providers
            provider_tab1, provider_tab2, provider_tab3, provider_tab4, provider_tab5 = st.tabs([
                "🚀 DeepSeek", 
                "🧠 OpenAI", 
                "🤖 Anthropic",
                "🌎 Google",
                "💻 Local"
            ])
            
            # DeepSeek
            with provider_tab1:
                current_deepseek = app_db.get_setting("deepseek_api_key", "")
                if current_deepseek:
                    st.success(f"✅ {i18n.t('sidebar.api_key_configured')}")
                
                with st.form("deepseek_form"):
                    deepseek_key = st.text_input(
                        "DeepSeek API Key",
                        value=current_deepseek,
                        type="password",
                        placeholder="sk-...",
                        help="Get from platform.deepseek.com"
                    )
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.form_submit_button("💾 Save", use_container_width=True):
                            if deepseek_key:
                                app_db.set_setting("deepseek_api_key", deepseek_key)
                                os.environ["DEEPSEEK_API_KEY"] = deepseek_key
                                st.success("✅ Saved!")
                                st.rerun()
                    with col2:
                        if st.form_submit_button("🗑️ Clear", use_container_width=True):
                            app_db.set_setting("deepseek_api_key", "")
                            if "DEEPSEEK_API_KEY" in os.environ:
                                del os.environ["DEEPSEEK_API_KEY"]
                            st.success("✅ Cleared!")
                            st.rerun()
            
            # OpenAI
            with provider_tab2:
                current_openai = app_db.get_setting("openai_api_key", "")
                if current_openai:
                    st.success(f"✅ {i18n.t('sidebar.api_key_configured')}")
                
                with st.form("openai_form"):
                    openai_key = st.text_input(
                        "OpenAI API Key",
                        value=current_openai,
                        type="password",
                        placeholder="sk-...",
                        help="Get from platform.openai.com/api-keys"
                    )
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.form_submit_button("💾 Save", use_container_width=True):
                            if openai_key:
                                app_db.set_setting("openai_api_key", openai_key)
                                os.environ["OPENAI_API_KEY"] = openai_key
                                st.success("✅ Saved!")
                                st.rerun()
                    with col2:
                        if st.form_submit_button("🗑️ Clear", use_container_width=True):
                            app_db.set_setting("openai_api_key", "")
                            if "OPENAI_API_KEY" in os.environ:
                                del os.environ["OPENAI_API_KEY"]
                            st.success("✅ Cleared!")
                            st.rerun()
            
            # Anthropic
            with provider_tab3:
                current_anthropic = app_db.get_setting("anthropic_api_key", "")
                if current_anthropic:
                    st.success(f"✅ {i18n.t('sidebar.api_key_configured')}")
                
                with st.form("anthropic_form"):
                    anthropic_key = st.text_input(
                        "Anthropic API Key",
                        value=current_anthropic,
                        type="password",
                        placeholder="sk-ant-...",
                        help="Get from console.anthropic.com"
                    )
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.form_submit_button("💾 Save", use_container_width=True):
                            if anthropic_key:
                                app_db.set_setting("anthropic_api_key", anthropic_key)
                                os.environ["ANTHROPIC_API_KEY"] = anthropic_key
                                st.success("✅ Saved!")
                                st.rerun()
                    with col2:
                        if st.form_submit_button("🗑️ Clear", use_container_width=True):
                            app_db.set_setting("anthropic_api_key", "")
                            if "ANTHROPIC_API_KEY" in os.environ:
                                del os.environ["ANTHROPIC_API_KEY"]
                            st.success("✅ Cleared!")
                            st.rerun()
            
            # Google
            with provider_tab4:
                current_gemini = app_db.get_setting("gemini_api_key", "")
                if current_gemini:
                    st.success(f"✅ {i18n.t('sidebar.api_key_configured')}")
                
                with st.form("gemini_form"):
                    gemini_key = st.text_input(
                        "Google Gemini API Key",
                        value=current_gemini,
                        type="password",
                        placeholder="AIza...",
                        help="Get from aistudio.google.com"
                    )
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.form_submit_button("💾 Save", use_container_width=True):
                            if gemini_key:
                                app_db.set_setting("gemini_api_key", gemini_key)
                                os.environ["GEMINI_API_KEY"] = gemini_key
                                st.success("✅ Saved!")
                                st.rerun()
                    with col2:
                        if st.form_submit_button("🗑️ Clear", use_container_width=True):
                            app_db.set_setting("gemini_api_key", "")
                            if "GEMINI_API_KEY" in os.environ:
                                del os.environ["GEMINI_API_KEY"]
                            st.success("✅ Cleared!")
                            st.rerun()
            
            # Local Models
            with provider_tab5:
                st.info("💻 Local models (Ollama, LM Studio) don't need API keys!")
                st.markdown("""
                **Setup:**
                1. Install [Ollama](https://ollama.ai/) or [LM Studio](https://lmstudio.ai/)
                2. Pull a model: `ollama pull llama3`
                3. In Settings tab, set model to `ollama/llama3`
                
                **Supported formats:**
                - `ollama/llama3`
                - `ollama/mistral`
                - `ollama/qwen`
                - `openai/custom` (for LM Studio/vLLM OpenAI-compatible mode)
                """)
        
        # Language switch
        st.divider()
        st.caption(f"{i18n.t('sidebar.language')} / Language")
        current_locale = st.session_state.get('locale', 'zh')
        locale_options = {"中文": "zh", "English": "en"}
        selected = st.selectbox(
            i18n.t('sidebar.ui_language'),
            list(locale_options.keys()),
            index=0 if current_locale == "zh" else 1,
            label_visibility="collapsed"
        )
        new_locale = locale_options[selected]
        if new_locale != st.session_state.locale:
            st.session_state.locale = new_locale
            st.session_state.i18n.set_locale(new_locale)
            # Save to DB
            app_db.set_setting("locale", new_locale)
            st.rerun()
        
        # Help information
        st.divider()
        with st.expander(f"ℹ️ {i18n.t('sidebar.help')}"):
            st.markdown(f"""
            ### {i18n.t('help.guide_title')}
            
            1. **{i18n.t('help.guide_create')}** - {i18n.t('help.guide_create_desc')}
            2. **{i18n.t('help.guide_scenes')}** - {i18n.t('help.guide_scenes_desc')}
            3. **{i18n.t('help.guide_characters')}** - {i18n.t('help.guide_characters_desc')}
            4. **{i18n.t('help.guide_ai')}** - {i18n.t('help.guide_ai_desc')}
            
            ### {i18n.t('help.shortcuts_title')}
            - `Ctrl+S` - {i18n.t('help.shortcuts_save')}
            
            ### {i18n.t('help.docs_title')}
            - [{i18n.t('help.developer_guide')}](./docs/developer_guide.md)
            - [{i18n.t('help.github')}](https://github.com/pj4239460/story-graph-assistant)
            
            ---
            
            **Story Graph Assistant**  
            © 2025 Ji PEI. Licensed under MIT.  
            Powered by Streamlit, LangGraph, and DeepSeek AI.
            """)

