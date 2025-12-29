"""
Story routes view - Enhanced version with Streamlit Flow
"""
import streamlit as st
from streamlit_flow import streamlit_flow
from streamlit_flow.elements import StreamlitFlowNode, StreamlitFlowEdge
from streamlit_flow.state import StreamlitFlowState
from streamlit_flow.layouts import TreeLayout


def create_flow_state_from_scenes(scenes):
    """Create Streamlit Flow state from scene list"""
    if not scenes:
        return StreamlitFlowState([], [])
    
    nodes = []
    edges = []
    
    # Create nodes
    for i, scene in enumerate(scenes):
        # Node styling based on scene type
        node_style = {
            'background': '#ff6666' if scene.isEnding else '#4a90e2',
            'color': 'white',
            'border': '2px solid #333',
            'borderRadius': '8px',
            'padding': '10px',
            'fontSize': '14px',
            'fontWeight': 'bold',
            'minWidth': '150px',
            'minHeight': '60px'
        }
        
        # Node label with metadata
        label_parts = [f"**{scene.title}**"]
        if scene.chapter:
            label_parts.append(f"📚 {scene.chapter}")
        if scene.isEnding:
            label_parts.append("🏁 Ending")
        if scene.choices:
            label_parts.append(f"🔀 {len(scene.choices)} choices")
        
        node_data = {
            'content': '\n\n'.join(label_parts)
        }
        
        node = StreamlitFlowNode(
            id=scene.id,
            pos=(0, i * 150),  # Initial vertical layout
            data=node_data,
            node_type='default',
            source_position='right',
            target_position='left',
            style=node_style,
            draggable=True
        )
        nodes.append(node)
    
    # Create edges from choices
    for scene in scenes:
        for choice in scene.choices:
            if choice.targetSceneId:
                edge = StreamlitFlowEdge(
                    id=f"{scene.id}-{choice.targetSceneId}",
                    source=scene.id,
                    target=choice.targetSceneId,
                    label=choice.text[:30] + "..." if len(choice.text) > 30 else choice.text,
                    edge_type='default',
                    animated=False,
                    style={'stroke': '#888', 'strokeWidth': 2},
                    label_style={'fill': '#555', 'fontSize': 12},
                    marker_end={'type': 'arrow', 'color': '#888'}
                )
                edges.append(edge)
    
    return StreamlitFlowState(nodes, edges)


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
                    
                    # Full content in toggle
                    if scene.body and st.session_state.get(f"show_content_{scene.id}", False):
                        st.text_area(
                            i18n.t('routes.content'),
                            value=scene.body,
                            height=200,
                            disabled=True,
                            key=f"scene_body_{scene.id}",
                            label_visibility="collapsed"
                        )
                    
                    if scene.body:
                        toggle_text = "Hide Full Content" if st.session_state.get(f"show_content_{scene.id}", False) else "View Full Content"
                        toggle_text_zh = "隐藏完整内容" if st.session_state.get(f"show_content_{scene.id}", False) else "查看完整内容"
                        if st.button(f"📄 {toggle_text if st.session_state.locale == 'en' else toggle_text_zh}", key=f"toggle_content_{scene.id}"):
                            st.session_state[f"show_content_{scene.id}"] = not st.session_state.get(f"show_content_{scene.id}", False)
                            st.rerun()
                    
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
    
    # Interactive Flow Visualization
    if scenes:
        st.divider()
        st.subheader(f"🌳 {i18n.t('routes.simple_graph')}")
        
        # Layout options
        col1, col2, col3 = st.columns([2, 2, 4])
        with col1:
            layout_type = st.selectbox(
                "Layout" if st.session_state.locale == "en" else "布局",
                ["Tree", "Layered", "Force", "Manual"],
                key="flow_layout"
            )
        with col2:
            show_text_view = st.checkbox(
                "Text View" if st.session_state.locale == "en" else "文本视图",
                value=False,
                key="show_text_view"
            )
        
        if not show_text_view:
            # Initialize flow state in session
            if 'flow_state' not in st.session_state or st.session_state.get('flow_needs_refresh', True):
                st.session_state.flow_state = create_flow_state_from_scenes(scenes)
                st.session_state.flow_needs_refresh = False
            
            # Render interactive flow diagram
            st.caption("💡 " + ("Drag nodes to rearrange, scroll to zoom, click for details" if st.session_state.locale == "en" else "拖动节点重排，滚轮缩放，点击查看详情"))
            
            # Get layout based on selection
            if layout_type == "Tree":
                from streamlit_flow.layouts import TreeLayout
                layout = TreeLayout(direction='down')
            elif layout_type == "Layered":
                from streamlit_flow.layouts import LayeredLayout
                layout = LayeredLayout(direction='down')
            elif layout_type == "Force":
                from streamlit_flow.layouts import ForceLayout
                layout = ForceLayout()
            else:
                from streamlit_flow.layouts import ManualLayout
                layout = ManualLayout()
            
            # Render the flow
            selected_id = streamlit_flow(
                'scene_flow',
                st.session_state.flow_state,
                layout=layout,
                fit_view=True,
                height=600,
                enable_pane_menu=True,
                enable_node_menu=True,
                enable_edge_menu=True,
                show_minimap=True,
                hide_watermark=True,
                allow_zoom=True,
                allow_pan=True
            )
            
            # Show selected node details
            if selected_id:
                st.info(f"Selected: {selected_id}")
                selected_scene = scene_service.get_scene(project, selected_id)
                if selected_scene:
                    with st.expander(f"📖 {selected_scene.title}", expanded=True):
                        if selected_scene.chapter:
                            st.caption(f"📚 Chapter: {selected_scene.chapter}")
                        if selected_scene.isEnding:
                            st.warning("🏁 This is an ending scene")
                        if selected_scene.summary:
                            st.info(selected_scene.summary)
                        if selected_scene.body:
                            st.text_area("Content", selected_scene.body, height=150, disabled=True)
        
        else:
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
