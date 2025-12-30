"""
Story routes view - Enhanced version with Streamlit Flow
"""
import streamlit as st
import math
from streamlit_flow import streamlit_flow
from streamlit_flow.elements import StreamlitFlowNode, StreamlitFlowEdge
from streamlit_flow.state import StreamlitFlowState
from streamlit_flow.layouts import TreeLayout, ManualLayout


def calculate_layout(nodes, edges, layout_type="Tree", direction="down"):
    """
    Calculate node positions manually in Python to ensure layout works.
    This is a fallback/enhancement because frontend ELK layout can be unreliable.
    """
    if not nodes:
        return nodes

    # Configuration
    node_width = 220
    node_height = 100
    spacing_x = 50
    spacing_y = 80
    
    # Build graph structure
    adj = {node.id: [] for node in nodes}
    in_degree = {node.id: 0 for node in nodes}
    node_map = {node.id: node for node in nodes}
    
    for edge in edges:
        if edge.source in adj and edge.target in in_degree:
            adj[edge.source].append(edge.target)
            in_degree[edge.target] += 1
            
    # Find roots (nodes with in-degree 0)
    roots = [nid for nid, deg in in_degree.items() if deg == 0]
    if not roots and nodes:
        roots = [nodes[0].id] # Fallback for cycles
        
    # --- Grid Layout (Only for Manual) ---
    if layout_type == "Manual":
        # Simple grid for manual start
        cols = math.ceil(math.sqrt(len(nodes)))
        for i, node in enumerate(nodes):
            row = i // cols
            col = i % cols
            node.position = {
                "x": col * (node_width + spacing_x),
                "y": row * (node_height + spacing_y)
            }
    
    # --- Tree / Layered Layout (BFS Levels) ---
    # We also use this as a fallback for Force layout to give it a good initial state
    else:
        levels = {} # node_id -> level
        queue = [(root, 0) for root in roots]
        visited = set(roots)
        
        # Assign levels
        while queue:
            curr, level = queue.pop(0)
            levels[curr] = level
            
            for neighbor in adj[curr]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, level + 1))
        
        # Handle disconnected components or unvisited nodes
        for node in nodes:
            if node.id not in visited:
                levels[node.id] = 0 # Put them at top/start
        
        # Group by level
        level_nodes = {}
        for nid, level in levels.items():
            if level not in level_nodes:
                level_nodes[level] = []
            level_nodes[level].append(nid)
            
        # Assign positions
        max_width = max(len(ns) for ns in level_nodes.values()) * (node_width + spacing_x)
        
        for level, nids in level_nodes.items():
            row_width = len(nids) * (node_width + spacing_x) - spacing_x
            start_x = (max_width - row_width) / 2
            
            for i, nid in enumerate(nids):
                node = node_map[nid]
                
                if direction == "down":
                    x = start_x + i * (node_width + spacing_x)
                    y = level * (node_height + spacing_y)
                    node.source_position = 'bottom'
                    node.target_position = 'top'
                elif direction == "up":
                    x = start_x + i * (node_width + spacing_x)
                    y = -level * (node_height + spacing_y)
                    node.source_position = 'top'
                    node.target_position = 'bottom'
                elif direction == "right":
                    x = level * (node_width + spacing_x)
                    y = start_x + i * (node_height + spacing_y)
                    node.source_position = 'right'
                    node.target_position = 'left'
                elif direction == "left":
                    x = -level * (node_width + spacing_x)
                    y = start_x + i * (node_height + spacing_y)
                    node.source_position = 'left'
                    node.target_position = 'right'
                
                # Update position directly
                # Note: StreamlitFlowNode expects pos tuple in constructor, but we modify .position dict here
                # because that's what asdict() uses
                node.position = {"x": x, "y": y} 
            
    return nodes


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
        
        # Set all nodes to origin - let layout algorithm position them
        # IMPORTANT: We must provide explicit width/height for ELK layout to work in frontend
        node = StreamlitFlowNode(
            id=scene.id,
            pos=(0, 0),
            data=node_data,
            node_type='default',
            source_position='right',
            target_position='left',
            style=node_style,
            draggable=True,
            width=200,  # Explicit width for ELK
            height=100  # Explicit height for ELK
        )
        nodes.append(node)
    
    # Create set of valid node IDs for validation
    valid_node_ids = {node.id for node in nodes}
    
    # Create edges from choices
    for scene in scenes:
        for choice in scene.choices:
            # Only create edge if target scene actually exists in our node list
            # ELK layout engine will CRASH if an edge points to a non-existent node
            if choice.targetSceneId and choice.targetSceneId in valid_node_ids:
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
            # Direction for layouts (disabled for Force and Manual)
            layout_direction = st.selectbox(
                "Direction" if st.session_state.locale == "en" else "方向",
                ["Down", "Right", "Up", "Left"],
                key="flow_direction",
                disabled=(layout_type in ["Force", "Manual"])
            )
        with col3:
            show_text_view = st.checkbox(
                "Text View" if st.session_state.locale == "en" else "文本视图",
                value=False,
                key="show_text_view"
            )
        
        
        if not show_text_view:
            # Map direction string to lowercase for API
            direction_map = {"Down": "down", "Right": "right", "Up": "up", "Left": "left"}
            direction = direction_map.get(layout_direction, "down")
            
            # Get layout based on selection with parameters
            if layout_type == "Tree":
                from streamlit_flow.layouts import TreeLayout
                layout = TreeLayout(direction=direction, node_node_spacing=100)
            elif layout_type == "Layered":
                from streamlit_flow.layouts import LayeredLayout
                layout = LayeredLayout(direction=direction, node_node_spacing=80, node_layer_spacing=120)
            elif layout_type == "Force":
                from streamlit_flow.layouts import ForceLayout
                layout = ForceLayout(node_node_spacing=150)
            else:
                from streamlit_flow.layouts import ManualLayout
                layout = ManualLayout()
            
            # Recreate state when layout changes to force ELK recalculation
            layout_key = f"{layout_type}_{direction}"
            if 'flow_state' not in st.session_state or st.session_state.get('last_layout_key') != layout_key:
                # Create fresh state
                new_state = create_flow_state_from_scenes(scenes)
                
                # If Manual layout, calculate positions in Python as a starting point
                if layout_type == "Manual":
                    new_state.nodes = calculate_layout(new_state.nodes, new_state.edges, "Manual", direction)
                
                st.session_state.flow_state = new_state
                st.session_state.last_layout_key = layout_key
            
            # Instructions
            if st.session_state.locale == "en":
                st.caption("Drag nodes to rearrange, scroll to zoom, double-click to fit view")
                st.caption("Right-click canvas to access 'Reset Layout' for recalculation")
            else:
                st.caption("拖动节点重排，滚轮缩放，双击适应视图")
                st.caption("右键画布访问 'Reset Layout' 重新计算")
            
            # Render the flow
            # Use dynamic key to force component remount when layout changes
            # This ensures ELK layout algorithm runs on fresh nodes
            component_key = f"scene_flow_{layout_key}"
            
            # For Manual layout, we don't pass a layout object to let our calculated positions take effect
            # For others, we pass the ELK layout object
            flow_layout = ManualLayout() if layout_type == "Manual" else layout
            
            st.session_state.flow_state = streamlit_flow(
                component_key,
                st.session_state.flow_state,
                layout=flow_layout,
                fit_view=True,
                height=600,
                enable_pane_menu=True,
                enable_node_menu=True,
                enable_edge_menu=True,
                show_minimap=True,
                hide_watermark=True,
                pan_on_drag=True,
                allow_zoom=True,
                min_zoom=0.1,
                # Enable node selection
                get_node_on_click=True,
            )
            
            # Handle node click - check if state has selected nodes
            if hasattr(st.session_state.flow_state, 'selected_id') and st.session_state.flow_state.selected_id:
                st.session_state.selected_scene_id = st.session_state.flow_state.selected_id
            
            # Check if any node was selected (clicked)
            # Display scene details in expander when available
            if 'selected_scene_id' in st.session_state and st.session_state.selected_scene_id:
                scene_id = st.session_state.selected_scene_id
                scene = project_service.get_project().scenes.get(scene_id)
                
                if scene:
                    with st.expander(f"📄 Scene Details: {scene.title}", expanded=True):
                        tabs = st.tabs(["📝 Content", "🔬 AI Checkup", "⚙️ Metadata"])
                        
                        with tabs[0]:
                            # Content tab
                            st.markdown(f"**Title:** {scene.title}")
                            if scene.chapter:
                                st.markdown(f"**Chapter:** {scene.chapter}")
                            if scene.summary:
                                st.markdown(f"**Summary:** {scene.summary}")
                            st.markdown("**Body:**")
                            st.text_area("", value=scene.body, height=200, disabled=True, key=f"body_{scene_id}")
                            
                            if scene.choices:
                                st.markdown(f"**Choices ({len(scene.choices)}):**")
                                for i, choice in enumerate(scene.choices, 1):
                                    st.caption(f"{i}. {choice.text} → {choice.targetSceneId or 'END'}")
                        
                        with tabs[1]:
                            # AI Checkup tab
                            from .scene_checkup_panel import render_scene_checkup_tab
                            ai_service = st.session_state.ai_service
                            render_scene_checkup_tab(project_service.get_project(), scene, ai_service)
                        
                        with tabs[2]:
                            # Metadata tab
                            st.json({
                                "ID": scene.id,
                                "Chapter": scene.chapter or "N/A",
                                "Tags": scene.tags,
                                "Participants": [p.characterId for p in scene.participants],
                                "Choices": len(scene.choices),
                            })
                        
                        if st.button("✖ Close", key="close_scene_details"):
                            st.session_state.selected_scene_id = None
                            st.rerun()
            
            # Note: Streamlit Flow doesn't directly return selected ID
            # Users can interact with nodes through context menus
            if st.session_state.locale == "en":
                st.caption("Right-click nodes for edit/delete options | Click nodes to view details")
            else:
                st.caption("右键点击节点进行编辑/删除操作 | 单击查看详情")

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
