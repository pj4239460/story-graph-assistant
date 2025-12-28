"""
Story routes view - Enhanced version
"""
import streamlit as st


def generate_mermaid_graph(scenes, i18n):
    """Generate Mermaid flowchart for scene graph"""
    if not scenes:
        return ""
    
    # Build Mermaid flowchart
    mermaid_lines = ["graph TD"]
    
    for scene in scenes:
        # Node style based on type
        node_id = scene.id[:8]  # Shorten ID for readability
        node_label = scene.title.replace('"', "'")
        
        if scene.isEnding:
            # Ending scenes with special style
            mermaid_lines.append(f'    {node_id}[["{node_label}"]]:::ending')
        else:
            mermaid_lines.append(f'    {node_id}["{node_label}"]')
        
        # Add edges for choices
        for i, choice in enumerate(scene.choices):
            if choice.targetSceneId:
                target_id = choice.targetSceneId[:8]
                choice_text = choice.text[:20] + "..." if len(choice.text) > 20 else choice.text
                choice_text = choice_text.replace('"', "'")
                mermaid_lines.append(f"    {node_id} -->|{choice_text}| {target_id}")
    
    # Add styles
    mermaid_lines.append("    classDef ending fill:#f96,stroke:#333,stroke-width:3px")
    
    return "\n".join(mermaid_lines)


def render_routes_view():
    """Render story routes view"""
    i18n = st.session_state.i18n
    project_service = st.session_state.project_service
    scene_service = st.session_state.scene_service
    
    project = project_service.get_project()
    
    st.header(f"📊 {i18n.t('routes.title')}")
    
    # Scene list
    scenes = scene_service.get_all_scenes(project)
    
    # Statistics dashboard
    if scenes:
        col1, col2, col3, col4 = st.columns(4)
        
        # Count different types
        total_scenes = len(scenes)
        ending_scenes = sum(1 for s in scenes if s.isEnding)
        total_choices = sum(len(s.choices) for s in scenes)
        chapters = len(set(s.chapter for s in scenes if s.chapter))
        
        with col1:
            st.metric("📝 Total Scenes" if st.session_state.locale == "en" else "📝 总场景数", total_scenes)
        with col2:
            st.metric("🏁 Endings" if st.session_state.locale == "en" else "🏁 结局数", ending_scenes)
        with col3:
            st.metric("🔀 Choices" if st.session_state.locale == "en" else "🔀 选择数", total_choices)
        with col4:
            st.metric("📚 Chapters" if st.session_state.locale == "en" else "📚 章节数", chapters if chapters > 0 else "-")
        
        st.divider()
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader(f"{i18n.t('routes.scene_list')} ({len(scenes)})")
    with col2:
        if st.button(f"➕ {i18n.t('routes.new_scene')}", use_container_width=True, type="primary"):
            st.session_state.show_scene_create = True
    
    # New scene form
    if st.session_state.get("show_scene_create", False):
        with st.form("create_scene_form"):
            st.subheader(i18n.t('routes.create_scene'))
            title = st.text_input(i18n.t('routes.scene_title'), placeholder=i18n.t('routes.placeholder_title'))
            body = st.text_area(i18n.t('routes.scene_content'), height=200, placeholder=i18n.t('routes.placeholder_content'))
            chapter = st.text_input(i18n.t('routes.chapter'), placeholder=i18n.t('routes.placeholder_chapter'))
            
            col1, col2 = st.columns(2)
            with col1:
                submitted = st.form_submit_button(i18n.t('common.create'), use_container_width=True)
            with col2:
                cancelled = st.form_submit_button(i18n.t('common.cancel'), use_container_width=True)
            
            if submitted and title:
                scene = scene_service.create_scene(project, title, body, chapter)
                st.session_state.show_scene_create = False
                st.success(f"✅ {i18n.t('routes.scene_created', title=title)}")
                st.rerun()
            
            if cancelled:
                st.session_state.show_scene_create = False
                st.rerun()
    
    # Display scene list
    if not scenes:
        st.info(i18n.t('routes.no_scenes'))
    else:
        # Add filter options
        col1, col2, col3 = st.columns([2, 2, 2])
        with col1:
            filter_chapter = st.selectbox(
                "Filter by Chapter" if st.session_state.locale == "en" else "按章节筛选",
                ["All" if st.session_state.locale == "en" else "全部"] + sorted(list(set(s.chapter for s in scenes if s.chapter))),
                key="filter_chapter"
            )
        with col2:
            filter_type = st.selectbox(
                "Filter by Type" if st.session_state.locale == "en" else "按类型筛选",
                ["All" if st.session_state.locale == "en" else "全部", 
                 "Ending" if st.session_state.locale == "en" else "结局", 
                 "Regular" if st.session_state.locale == "en" else "普通"],
                key="filter_type"
            )
        with col3:
            sort_by = st.selectbox(
                "Sort by" if st.session_state.locale == "en" else "排序方式",
                ["Title" if st.session_state.locale == "en" else "标题", 
                 "Time" if st.session_state.locale == "en" else "时间"],
                key="sort_by"
            )
        
        # Apply filters
        filtered_scenes = scenes
        if filter_chapter not in ["All", "全部"]:
            filtered_scenes = [s for s in filtered_scenes if s.chapter == filter_chapter]
        if filter_type == "Ending" or filter_type == "结局":
            filtered_scenes = [s for s in filtered_scenes if s.isEnding]
        elif filter_type == "Regular" or filter_type == "普通":
            filtered_scenes = [s for s in filtered_scenes if not s.isEnding]
        
        # Sort
        if sort_by in ["Time", "时间"] and any(s.timeIndex is not None for s in filtered_scenes):
            filtered_scenes = sorted(filtered_scenes, key=lambda s: s.timeIndex if s.timeIndex is not None else 999)
        else:
            filtered_scenes = sorted(filtered_scenes, key=lambda s: s.title)
        
        st.caption(f"Showing {len(filtered_scenes)} of {len(scenes)} scenes" if st.session_state.locale == "en" else f"显示 {len(filtered_scenes)} / {len(scenes)} 个场景")
        
        for scene in filtered_scenes:
            # Enhanced scene card
            scene_icon = "🏁" if scene.isEnding else "🎬"
            title_suffix = f" ({scene.chapter})" if scene.chapter else ""
            time_badge = f" ⏰ {scene.timeLabel}" if scene.timeLabel else ""
            
            with st.expander(f"{scene_icon} **{scene.title}**{title_suffix}{time_badge}", expanded=False):
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    # Quick info badges
                    badge_cols = st.columns([1, 1, 1, 3])
                    with badge_cols[0]:
                        st.caption(f"🆔 `{scene.id[:8]}`")
                    with badge_cols[1]:
                        st.caption(f"🔀 {len(scene.choices)} choices" if st.session_state.locale == "en" else f"🔀 {len(scene.choices)} 个选择")
                    with badge_cols[2]:
                        if scene.participants:
                            st.caption(f"👥 {len(scene.participants)} chars" if st.session_state.locale == "en" else f"👥 {len(scene.participants)} 个角色")
                    
                    # Summary or preview
                    if scene.summary:
                        st.info(f"📋 {scene.summary}")
                    else:
                        preview = scene.body[:200] + "..." if len(scene.body) > 200 else scene.body
                        st.caption(preview)
                    
                    # Full content in expander
                    if scene.body:
                        with st.expander("📄 " + ("View Full Content" if st.session_state.locale == "en" else "查看完整内容")):
                            st.text_area(
                                i18n.t('routes.content'),
                                value=scene.body,
                                height=200,
                                disabled=True,
                                key=f"scene_body_{scene.id}",
                                label_visibility="collapsed"
                            )
                    
                    # Choice list
                    if scene.choices:
                        st.markdown(f"**{i18n.t('routes.choices')}：**")
                        for i, choice in enumerate(scene.choices):
                            target_title = i18n.t('routes.not_connected')
                            if choice.targetSceneId:
                                target_scene = scene_service.get_scene(project, choice.targetSceneId)
                                if target_scene:
                                    target_title = target_scene.title
                            st.markdown(f"{i+1}. {choice.text} → `{target_title}`")
                
                with col2:
                    if st.button(f"✏️ {i18n.t('common.edit')}", key=f"edit_{scene.id}", use_container_width=True):
                        st.info(i18n.t('routes.edit_coming_soon'))
                    
                    if st.button(f"🗑️ {i18n.t('common.delete')}", key=f"delete_{scene.id}", use_container_width=True):
                        scene_service.delete_scene(project, scene.id)
                        st.success(i18n.t('routes.scene_deleted', title=scene.title))
                        st.rerun()
    
    # Graph visualization
    if scenes:
        st.divider()
        st.subheader(f"📈 {i18n.t('routes.simple_graph')}")
        
        # Tabs for different views
        tab1, tab2 = st.tabs([
            "🌳 " + ("Flow Chart" if st.session_state.locale == "en" else "流程图"),
            "📋 " + ("Text View" if st.session_state.locale == "en" else "文本视图")
        ])
        
        with tab1:
            # Mermaid visualization
            mermaid_code = generate_mermaid_graph(scenes, i18n)
            if mermaid_code:
                st.code(mermaid_code, language="mermaid")
                st.caption("💡 " + ("Copy the code above and paste into a Mermaid viewer" if st.session_state.locale == "en" else "复制上面的代码并粘贴到 Mermaid 查看器中"))
                st.caption("🔗 Mermaid Live Editor: https://mermaid.live")
            else:
                st.info(i18n.t('routes.no_scenes'))
        
        with tab2:
            # Text representation
            graph = scene_service.get_scene_graph(project)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**{i18n.t('routes.nodes')}：**")
                for node in graph["nodes"]:
                    ending_badge = "🏁" if node['isEnding'] else "📄"
                    chapter_info = f" - {node['chapter']}" if node.get('chapter') else ""
                    st.markdown(f"{ending_badge} {node['title']}{chapter_info}")
            
            with col2:
                st.markdown(f"**{i18n.t('routes.connections')}：**")
                if not graph["edges"]:
                    st.info(i18n.t('routes.no_connections'))
                else:
                    for edge in graph["edges"]:
                        from_scene = scene_service.get_scene(project, edge["from"])
                        to_scene = scene_service.get_scene(project, edge["to"])
                        if from_scene and to_scene:
                            st.markdown(f"➡️ {from_scene.title} → {to_scene.title}")
                            st.caption(f"   💬 {edge['label'][:40]}..." if len(edge['label']) > 40 else f"   💬 {edge['label']}")
