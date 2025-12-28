"""
AI tools view
"""
import streamlit as st


def render_ai_tools_view():
    """Render AI tools view"""
    i18n = st.session_state.i18n
    project_service = st.session_state.project_service
    scene_service = st.session_state.scene_service
    character_service = st.session_state.character_service
    ai_service = st.session_state.ai_service
    
    project = project_service.get_project()
    
    st.header(f"🤖 {i18n.t('ai_tools.title')}")
    
    # Tool selection
    tool_map = {
        i18n.t('ai_tools.scene_summary'): "scene_summary",
        i18n.t('ai_tools.fact_extraction'): "fact_extraction",
        i18n.t('ai_tools.ooc_check'): "ooc_check"
    }
    tool = st.selectbox(
        i18n.t('ai_tools.select_tool'),
        list(tool_map.keys()),
        help=i18n.t('ai_tools.tool_help')
    )
    tool_key = tool_map[tool]
    
    st.divider()
    
    # Scene summarization
    if tool_key == "scene_summary":
        st.subheader(f"📝 {i18n.t('ai_tools.scene_summary_title')}")
        st.caption(i18n.t('ai_tools.scene_summary_desc'))
        
        scenes = scene_service.get_all_scenes(project)
        if not scenes:
            st.warning(i18n.t('ai_tools.no_scenes_warning'))
            return
        
        scene_options = {f"{s.title} ({s.id[:8]})": s.id for s in scenes}
        selected_scene_name = st.selectbox(i18n.t('ai_tools.select_scene'), list(scene_options.keys()))
        selected_scene_id = scene_options[selected_scene_name]
        scene = scene_service.get_scene(project, selected_scene_id)
        
        if scene:
            st.text_area(i18n.t('ai_tools.scene_preview'), value=scene.body[:500] + "..." if len(scene.body) > 500 else scene.body, height=150, disabled=True)
            
            if st.button(f"🚀 {i18n.t('ai_tools.generate_summary')}", type="primary"):
                with st.spinner(i18n.t('ai_tools.ai_analyzing')):
                    summary = ai_service.summarize_scene(project, scene)
                    scene.summary = summary
                    
                    st.success(f"✅ {i18n.t('ai_tools.summary_generated')}")
                    st.markdown(f"**{i18n.t('ai_tools.generated_summary')}**")
                    st.info(summary)
    
    # Setting extraction
    elif tool_key == "fact_extraction":
        st.subheader(f"🔍 {i18n.t('ai_tools.fact_extraction_title')}")
        st.caption(i18n.t('ai_tools.fact_extraction_desc'))
        
        scenes = scene_service.get_all_scenes(project)
        if not scenes:
            st.warning(i18n.t('ai_tools.no_scenes_warning'))
            return
        
        scene_options = {f"{s.title} ({s.id[:8]})": s.id for s in scenes}
        selected_scene_name = st.selectbox(i18n.t('ai_tools.select_scene'), list(scene_options.keys()))
        selected_scene_id = scene_options[selected_scene_name]
        scene = scene_service.get_scene(project, selected_scene_id)
        
        if scene:
            st.text_area(i18n.t('ai_tools.scene_preview'), value=scene.body[:500] + "..." if len(scene.body) > 500 else scene.body, height=150, disabled=True)
            
            if st.button(f"🚀 {i18n.t('ai_tools.extract_facts')}", type="primary"):
                with st.spinner(i18n.t('ai_tools.ai_analyzing')):
                    facts = ai_service.extract_facts(project, scene)
                    
                    st.success(f"✅ {i18n.t('ai_tools.facts_extracted')}")
                    st.markdown(f"**{i18n.t('ai_tools.extracted_facts')}**")
                    for fact in facts:
                        st.markdown(f"- {fact}")
    
    # OOC detection
    elif tool_key == "ooc_check":
        st.subheader(f"🎭 {i18n.t('ai_tools.ooc_check_title')}")
        st.caption(i18n.t('ai_tools.ooc_check_desc'))
        
        characters = character_service.get_all_characters(project)
        scenes = scene_service.get_all_scenes(project)
        
        if not characters:
            st.warning(i18n.t('ai_tools.no_characters_warning'))
            return
        
        if not scenes:
            st.warning(i18n.t('ai_tools.no_scenes_warning'))
            return
        
        col1, col2 = st.columns(2)
        
        with col1:
            character_options = {f"{c.name}": c.id for c in characters}
            selected_char_name = st.selectbox(i18n.t('ai_tools.select_character'), list(character_options.keys()))
            selected_char_id = character_options[selected_char_name]
        
        with col2:
            scene_options = {f"{s.title}": s.id for s in scenes}
            selected_scene_name = st.selectbox(i18n.t('ai_tools.select_scene'), list(scene_options.keys()))
            selected_scene_id = scene_options[selected_scene_name]
        
        character = character_service.get_character(project, selected_char_id)
        scene = scene_service.get_scene(project, selected_scene_id)
        
        if character and scene:
            # Display character information
            with st.expander(i18n.t('ai_tools.character_profile')):
                st.markdown(f"**{i18n.t('characters.description')}：** {character.description}")
                if character.traits:
                    st.markdown(f"**{i18n.t('characters.traits')}：** {', '.join(character.traits)}")
                if character.goals:
                    st.markdown(f"**{i18n.t('characters.goals')}：** {', '.join(character.goals)}")
            
            # Display scene content
            st.text_area(i18n.t('ai_tools.scene_preview'), value=scene.body[:500] + "..." if len(scene.body) > 500 else scene.body, height=150, disabled=True)
            
            if st.button(f"🚀 {i18n.t('ai_tools.check_ooc')}", type="primary"):
                with st.spinner(i18n.t('ai_tools.ai_analyzing')):
                    result = ai_service.check_ooc(project, selected_char_id, scene)
                    
                    ooc_result_text = i18n.t('ai_tools.is_ooc', result="" if not result["is_ooc"] else "不")
                    
                    if result["is_ooc"]:
                        st.error(f"⚠️ {ooc_result_text}")
                    else:
                        st.success(f"✅ {ooc_result_text}")
                    
                    st.markdown(f"**{i18n.t('ai_tools.ooc_confidence')}：** {result['confidence']:.2f}")
                    st.markdown(f"**{i18n.t('ai_tools.ooc_explanation')}**")
                    st.info(result["explanation"])
    
    # Token usage hint
    st.divider()
    st.caption(f"💡 {i18n.t('metrics.project_tokens')}: {project.tokenStats.projectUsed:,} / {project.aiSettings.projectTokenLimit:,}")
