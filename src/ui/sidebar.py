"""
Sidebar component
"""
import streamlit as st


def render_sidebar():
    """Render sidebar"""
    i18n = st.session_state.i18n
    
    with st.sidebar:
        st.header(f"📁 {i18n.t('sidebar.project_management')}")
        
        project_service = st.session_state.project_service
        
        # Project operations
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button(f"➕ {i18n.t('sidebar.new_project')}", use_container_width=True):
                st.session_state.show_create_dialog = True
        
        with col2:
            if st.button(f"📂 {i18n.t('sidebar.load_project')}", use_container_width=True):
                st.session_state.show_load_dialog = True
        
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
                    st.session_state.show_create_dialog = False
                    st.success(f"✅ {i18n.t('sidebar.project_created', name=name)}")
                    st.rerun()
        
        # Load project dialog
        if st.session_state.get("show_load_dialog", False):
            with st.form("load_project_form"):
                st.subheader(i18n.t('sidebar.load_project_title'))
                path = st.text_input(i18n.t('sidebar.project_path'), placeholder="path/to/project.json")
                
                submitted = st.form_submit_button(i18n.t('common.load'))
                if submitted and path:
                    try:
                        project = project_service.load_project(path)
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
                            st.session_state.show_save_as_dialog = False
                            st.success(f"✅ {i18n.t('sidebar.saved_to', path=save_path)}")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ {i18n.t('sidebar.save_failed', error=str(e))}")
        
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
            - [{i18n.t('help.github')}](https://github.com/yourusername/story-graph-assistant)
            """)

