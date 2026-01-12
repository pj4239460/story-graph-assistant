"""
Story routes view - Enhanced version with Streamlit Flow
"""
import streamlit as st
import math
import uuid
from streamlit_flow import streamlit_flow
from streamlit_flow.elements import StreamlitFlowNode, StreamlitFlowEdge
from streamlit_flow.state import StreamlitFlowState
from streamlit_flow.layouts import TreeLayout, ManualLayout

from ..models.world import StoryThread, ThreadStep, Effect


def render_effects_editor(scene, project, scene_service, i18n):
    """Render Effects editor for a scene"""
    st.subheader("⚡ Dynamic Effects" if st.session_state.locale == "en" else "⚡ 动态效果")
    st.caption("Define how this scene changes character/relationship/world state" if st.session_state.locale == "en" else "定义这个场景如何改变角色/关系/世界状态")
    
    # Display existing effects
    if scene.effects:
        for i, effect in enumerate(scene.effects):
            with st.expander(f"Effect {i+1}: {effect.scope} → {effect.target} ({effect.op} {effect.path})"):
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.write(f"**Scope:** {effect.scope}")
                    st.write(f"**Target:** {effect.target}")
                    st.write(f"**Operation:** {effect.op}")
                    st.write(f"**Path:** {effect.path}")
                    st.write(f"**Value:** {effect.value}")
                    if effect.reason:
                        st.caption(f"Reason: {effect.reason}")
                with col2:
                    if st.button("🗑️", key=f"del_effect_{scene.id}_{i}"):
                        scene.effects.pop(i)
                        scene_service.update_scene(project, scene.id, effects=scene.effects)
                        st.success("Effect deleted!" if st.session_state.locale == "en" else "效果已删除！")
                        st.rerun()
    else:
        st.info("No effects defined yet. Add effects to make this scene change character states!" if st.session_state.locale == "en" else "尚未定义效果。添加效果来让这个场景改变角色状态！")
    
    # Add new effect
    if st.button("➕ Add Effect" if st.session_state.locale == "en" else "➕ 添加效果", key=f"add_effect_btn_{scene.id}"):
        st.session_state[f"adding_effect_{scene.id}"] = True
        st.rerun()
    
    if st.session_state.get(f"adding_effect_{scene.id}", False):
        with st.form(f"add_effect_form_{scene.id}"):
            st.caption("➕ Add New Effect" if st.session_state.locale == "en" else "➕ 添加新效果")
            
            scope = st.selectbox(
                "Scope" if st.session_state.locale == "en" else "作用域",
                ["character", "relationship", "world"],
                help="What this effect modifies" if st.session_state.locale == "en" else "这个效果修改什么"
            )
            
            # Target selection based on scope
            if scope == "character":
                char_options = {c.id: c.name for c in project.characters.values()}
                if char_options:
                    target = st.selectbox(
                        "Target Character" if st.session_state.locale == "en" else "目标角色",
                        options=list(char_options.keys()),
                        format_func=lambda x: char_options[x]
                    )
                else:
                    st.warning("No characters available. Create characters first!" if st.session_state.locale == "en" else "没有可用角色。请先创建角色！")
                    target = st.text_input("Target Character ID" if st.session_state.locale == "en" else "目标角色ID")
            
            elif scope == "relationship":
                char_list = list(project.characters.values())
                if len(char_list) >= 2:
                    col1, col2 = st.columns(2)
                    with col1:
                        char_a = st.selectbox(
                            "Character A" if st.session_state.locale == "en" else "角色A",
                            options=[c.id for c in char_list],
                            format_func=lambda x: project.characters[x].name
                        )
                    with col2:
                        char_b = st.selectbox(
                            "Character B" if st.session_state.locale == "en" else "角色B",
                            options=[c.id for c in char_list if c.id != char_a],
                            format_func=lambda x: project.characters[x].name
                        )
                    target = f"{char_a}|{char_b}"
                else:
                    st.warning("Need at least 2 characters for relationship effects!" if st.session_state.locale == "en" else "关系效果需要至少2个角色！")
                    target = st.text_input("Target (e.g., alice|bob)" if st.session_state.locale == "en" else "目标（例如：alice|bob）")
            
            else:  # world
                target = "world"
                st.info("World scope affects global variables" if st.session_state.locale == "en" else "世界作用域影响全局变量")
            
            op = st.selectbox(
                "Operation" if st.session_state.locale == "en" else "操作",
                ["set", "add", "remove", "merge"],
                help="set=replace, add=append/increment, remove=delete, merge=deep merge" if st.session_state.locale == "en" else "set=替换，add=追加/增加，remove=删除，merge=深度合并"
            )
            
            # Path suggestions based on scope
            if scope == "character":
                path_suggestions = ["mood", "status", "location", "traits", "goals", "fears", "vars.trust_level", "vars.secret_known"]
            elif scope == "relationship":
                path_suggestions = ["trust", "status", "intimacy"]
            else:
                path_suggestions = ["vars.flag_name", "vars.counter"]
            
            path = st.selectbox(
                "Path" if st.session_state.locale == "en" else "路径",
                options=["custom"] + path_suggestions,
                help="Dot notation path to the property" if st.session_state.locale == "en" else "属性的点记法路径"
            )
            
            if path == "custom":
                path = st.text_input(
                    "Custom Path" if st.session_state.locale == "en" else "自定义路径",
                    placeholder="state.mood" if scope == "character" else "vars.my_variable"
                )
            
            value = st.text_input(
                "Value" if st.session_state.locale == "en" else "值",
                help="The value to set/add/remove. For numbers, will be converted automatically." if st.session_state.locale == "en" else "要设置/添加/删除的值。数字会自动转换。"
            )
            
            reason = st.text_input(
                "Reason (optional)" if st.session_state.locale == "en" else "原因（可选）",
                placeholder="Alice becomes paranoid after seeing the lab" if st.session_state.locale == "en" else "Alice在看到实验室后变得偏执"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                add_submitted = st.form_submit_button("💾 Add Effect" if st.session_state.locale == "en" else "💾 添加效果", use_container_width=True)
            with col2:
                add_cancelled = st.form_submit_button("Cancel" if st.session_state.locale == "en" else "取消", use_container_width=True)
            
            if add_submitted and path and value:
                # Convert value type
                converted_value = value
                try:
                    if value.lower() in ['true', 'false']:
                        converted_value = value.lower() == 'true'
                    elif value.replace('-', '').replace('.', '').isdigit():
                        converted_value = float(value) if '.' in value else int(value)
                except:
                    pass  # Keep as string
                
                # Create new effect
                new_effect = Effect(
                    scope=scope,
                    target=target,
                    op=op,
                    path=path,
                    value=converted_value,
                    reason=reason if reason else None,
                    sourceSceneId=scene.id
                )
                
                scene.effects.append(new_effect)
                scene_service.update_scene(project, scene.id, effects=scene.effects)
                
                st.session_state[f"adding_effect_{scene.id}"] = False
                st.success("✅ Effect added!" if st.session_state.locale == "en" else "✅ 效果已添加！")
                st.rerun()
            
            if add_cancelled:
                st.session_state[f"adding_effect_{scene.id}"] = False
                st.rerun()


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
                            
                            choice_col1, choice_col2 = st.columns([5, 1])
                            with choice_col1:
                                st.markdown(f"{i+1}. {choice.text} → `{target_title}`")
                            with choice_col2:
                                if st.button("✏️", key=f"edit_choice_{choice.id}", help=i18n.t('common.edit')):
                                    st.session_state[f"editing_choice_{choice.id}"] = True
                                    st.rerun()
                            
                            # Edit choice form
                            if st.session_state.get(f"editing_choice_{choice.id}", False):
                                with st.form(f"edit_choice_form_{choice.id}"):
                                    st.caption(f"✏️ {i18n.t('routes.edit_choice')}")
                                    
                                    choice_text = st.text_input(
                                        i18n.t('routes.choice_text'),
                                        value=choice.text,
                                        key=f"text_{choice.id}"
                                    )
                                    
                                    # Target scene selection
                                    scene_options = {s.id: s.title for s in scenes}
                                    scene_options[""] = i18n.t('routes.no_target')
                                    current_target = choice.targetSceneId or ""
                                    
                                    target_scene_id = st.selectbox(
                                        i18n.t('routes.target_scene'),
                                        options=list(scene_options.keys()),
                                        format_func=lambda x: scene_options[x],
                                        index=list(scene_options.keys()).index(current_target) if current_target in scene_options else 0,
                                        key=f"target_{choice.id}"
                                    )
                                    
                                    choice_col1, choice_col2, choice_col3 = st.columns(3)
                                    with choice_col1:
                                        save_choice = st.form_submit_button(i18n.t('common.save'), use_container_width=True)
                                    with choice_col2:
                                        delete_choice = st.form_submit_button(i18n.t('common.delete'), use_container_width=True)
                                    with choice_col3:
                                        cancel_choice = st.form_submit_button(i18n.t('common.cancel'), use_container_width=True)
                                    
                                    if save_choice:
                                        scene_service.update_choice(
                                            project,
                                            scene.id,
                                            choice.id,
                                            text=choice_text,
                                            target_scene_id=target_scene_id if target_scene_id else None
                                        )
                                        st.session_state[f"editing_choice_{choice.id}"] = False
                                        st.success(f"✅ {i18n.t('routes.choice_updated')}")
                                        st.rerun()
                                    
                                    if delete_choice:
                                        scene_service.delete_choice(project, scene.id, choice.id)
                                        st.session_state[f"editing_choice_{choice.id}"] = False
                                        st.success(f"🗑️ {i18n.t('routes.choice_deleted')}")
                                        st.rerun()
                                    
                                    if cancel_choice:
                                        st.session_state[f"editing_choice_{choice.id}"] = False
                                        st.rerun()
                    
                    # Add new choice button
                    if st.button(f"➕ {i18n.t('routes.add_choice')}", key=f"add_choice_{scene.id}"):
                        st.session_state[f"adding_choice_{scene.id}"] = True
                        st.rerun()
                    
                    # Display effects (read-only in view mode)
                    if scene.effects:
                        st.markdown("**⚡ " + ("Dynamic Effects" if st.session_state.locale == "en" else "动态效果") + "**")
                        for i, effect in enumerate(scene.effects):
                            effect_desc = f"{effect.scope} → {effect.target}: {effect.op} {effect.path} = {effect.value}"
                            st.caption(f"{i+1}. {effect_desc}")
                            if effect.reason:
                                st.caption(f"   ↳ {effect.reason}")
                    
                    # Add choice form
                    if st.session_state.get(f"adding_choice_{scene.id}", False):
                        with st.form(f"add_choice_form_{scene.id}"):
                            st.caption(f"➕ {i18n.t('routes.add_choice')}")
                            
                            new_choice_text = st.text_input(i18n.t('routes.choice_text'))
                            
                            scene_options = {s.id: s.title for s in scenes}
                            scene_options[""] = i18n.t('routes.no_target')
                            
                            new_target_scene_id = st.selectbox(
                                i18n.t('routes.target_scene'),
                                options=list(scene_options.keys()),
                                format_func=lambda x: scene_options[x],
                                key=f"new_target_{scene.id}"
                            )
                            
                            add_col1, add_col2 = st.columns(2)
                            with add_col1:
                                add_submitted = st.form_submit_button(i18n.t('common.add'), use_container_width=True)
                            with add_col2:
                                add_cancelled = st.form_submit_button(i18n.t('common.cancel'), use_container_width=True)
                            
                            if add_submitted and new_choice_text:
                                scene_service.add_choice(
                                    project,
                                    scene.id,
                                    text=new_choice_text,
                                    target_scene_id=new_target_scene_id if new_target_scene_id else None
                                )
                                st.session_state[f"adding_choice_{scene.id}"] = False
                                st.success(f"✅ {i18n.t('routes.choice_added')}")
                                st.rerun()
                            
                            if add_cancelled:
                                st.session_state[f"adding_choice_{scene.id}"] = False
                                st.rerun()
                
                
                with col2:
                    if st.button(f"✏️ {i18n.t('common.edit')}", key=f"edit_{scene.id}", use_container_width=True):
                        st.session_state[f"editing_scene_{scene.id}"] = True
                        st.rerun()
                    
                    if st.button(f"🗑️ {i18n.t('common.delete')}", key=f"delete_{scene.id}", use_container_width=True):
                        scene_service.delete_scene(project, scene.id)
                        st.success(i18n.t('routes.scene_deleted', title=scene.title))
                        st.rerun()
                
                # Edit form
                if st.session_state.get(f"editing_scene_{scene.id}", False):
                    st.divider()
                    with st.form(f"edit_scene_form_{scene.id}"):
                        st.subheader(f"✏️ {i18n.t('common.edit')} - {scene.title}")
                        
                        new_title = st.text_input(i18n.t('routes.scene_title'), value=scene.title)
                        new_body = st.text_area(i18n.t('routes.scene_content'), value=scene.body, height=200)
                        new_chapter = st.text_input(i18n.t('routes.chapter'), value=scene.chapter or "")
                        new_summary = st.text_area(i18n.t('routes.summary'), value=scene.summary or "", height=100)
                        new_time_label = st.text_input(i18n.t('routes.time_label'), value=scene.timeLabel or "")
                        new_is_ending = st.checkbox(i18n.t('routes.is_ending'), value=scene.isEnding)
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            submitted = st.form_submit_button(i18n.t('common.save'), use_container_width=True)
                        with col2:
                            cancelled = st.form_submit_button(i18n.t('common.cancel'), use_container_width=True)
                        
                        if submitted:
                            scene_service.update_scene(
                                project, 
                                scene.id,
                                title=new_title,
                                body=new_body,
                                chapter=new_chapter if new_chapter else None,
                                summary=new_summary if new_summary else None,
                                timeLabel=new_time_label if new_time_label else None,
                                isEnding=new_is_ending
                            )
                            st.session_state[f"editing_scene_{scene.id}"] = False
                            st.success(f"✅ {i18n.t('routes.scene_updated', title=new_title)}")
                            st.rerun()
                        
                        if cancelled:
                            st.session_state[f"editing_scene_{scene.id}"] = False
                            st.rerun()
                    
                    # Effects Management (outside form)
                    st.divider()
                    render_effects_editor(scene, project, scene_service, i18n)
    
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
                                "Participants": scene.participants,
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
    
    # ===== NEW: Play Path Mode =====
    st.divider()
    with st.expander("🎮 Play Path Mode - Walk Through Story" if st.session_state.locale == "en" else "🎮 路径试玩模式 - 体验故事"):
        render_play_path_mode(project, scene_service, i18n)


def render_play_path_mode(project, scene_service, i18n):
    """
    Render Play Path mode where users can walk through the story by clicking choices.
    This generates a StoryThread automatically.
    """
    # Initialize play state
    if "play_thread_steps" not in st.session_state:
        st.session_state.play_thread_steps = []
    if "play_current_scene" not in st.session_state:
        st.session_state.play_current_scene = None
    
    scenes = list(project.scenes.values())
    if not scenes:
        st.info("No scenes to play. Create some scenes first!" if st.session_state.locale == "en" else "没有场景可以试玩。请先创建一些场景！")
        return
    
    # Start new playthrough
    if st.session_state.play_current_scene is None:
        st.subheader("🎬 Start New Playthrough" if st.session_state.locale == "en" else "🎬 开始新的试玩")
        
        # Find root scenes (scenes with no incoming edges)
        all_targets = set()
        for scene in scenes:
            for choice in scene.choices:
                if choice.targetSceneId:
                    all_targets.add(choice.targetSceneId)
        
        root_scenes = [s for s in scenes if s.id not in all_targets]
        if not root_scenes:
            root_scenes = [scenes[0]]  # Fallback
        
        st.write("Select starting scene:" if st.session_state.locale == "en" else "选择起始场景：")
        for scene in root_scenes[:5]:  # Show top 5 roots
            if st.button(f"▶️ {scene.title}", key=f"start_{scene.id}"):
                st.session_state.play_current_scene = scene.id
                st.session_state.play_thread_steps = [{"sceneId": scene.id, "choiceId": None}]
                st.rerun()
        
        return
    
    # Continue playthrough
    current_scene_id = st.session_state.play_current_scene
    current_scene = project.scenes.get(current_scene_id)
    
    if not current_scene:
        st.error("Scene not found!" if st.session_state.locale == "en" else "场景未找到！")
        if st.button("🔄 Reset"):
            st.session_state.play_current_scene = None
            st.session_state.play_thread_steps = []
            st.rerun()
        return
    
    # Display current path
    col1, col2 = st.columns([3, 1])
    with col1:
        st.caption(f"**Current Path ({len(st.session_state.play_thread_steps)} steps):**" if st.session_state.locale == "en" else f"**当前路径 ({len(st.session_state.play_thread_steps)} 步):**")
        path_display = " → ".join([
            project.scenes[step["sceneId"]].title 
            for step in st.session_state.play_thread_steps 
            if step["sceneId"] in project.scenes
        ])
        st.text(path_display[:100] + "..." if len(path_display) > 100 else path_display)
    with col2:
        if st.button("🔄 Restart" if st.session_state.locale == "en" else "🔄 重新开始"):
            st.session_state.play_current_scene = None
            st.session_state.play_thread_steps = []
            st.rerun()
    
    st.divider()
    
    # Display current scene
    st.subheader(f"📄 {current_scene.title}")
    if current_scene.chapter:
        st.caption(f"Chapter: {current_scene.chapter}" if st.session_state.locale == "en" else f"章节：{current_scene.chapter}")
    
    if current_scene.body:
        with st.container(border=True):
            st.markdown(current_scene.body)
    
    # Show state changes from this scene's effects
    if current_scene.effects:
        st.divider()
        with st.expander(f"⚡ State Changes in This Scene ({len(current_scene.effects)})" if st.session_state.locale == "en" else f"⚡ 本场景的状态变化 ({len(current_scene.effects)})", expanded=False):
            for effect in current_scene.effects:
                icon = "👤" if effect.scope == "character" else ("💕" if effect.scope == "relationship" else "🌍")
                target_name = effect.target
                
                # Get character name if available
                if effect.scope == "character" and effect.target in project.characters:
                    target_name = project.characters[effect.target].name
                elif effect.scope == "relationship" and "|" in effect.target:
                    char_ids = effect.target.split("|")
                    names = []
                    for cid in char_ids:
                        if cid in project.characters:
                            names.append(project.characters[cid].name)
                    if names:
                        target_name = " & ".join(names)
                
                st.markdown(f"{icon} **{target_name}**: {effect.path} → `{effect.value}` ({effect.op})")
                if effect.reason:
                    st.caption(f"  ↳ {effect.reason}")
    
    st.divider()
    
    # Show choices
    if current_scene.choices and not current_scene.isEnding:
        st.write("**Choose your action:**" if st.session_state.locale == "en" else "**选择你的行动：**")
        
        for i, choice in enumerate(current_scene.choices):
            target_scene = project.scenes.get(choice.targetSceneId) if choice.targetSceneId else None
            button_text = f"{i+1}. {choice.text}"
            if target_scene:
                button_text += f" → {target_scene.title}"
            
            if st.button(button_text, key=f"choice_{choice.id}", use_container_width=True):
                # Record this step
                st.session_state.play_thread_steps.append({
                    "sceneId": choice.targetSceneId or current_scene_id,
                    "choiceId": choice.id
                })
                st.session_state.play_current_scene = choice.targetSceneId
                st.rerun()
    
    else:
        # Reached an ending
        st.success("🏁 **THE END**" if st.session_state.locale == "en" else "🏁 **结局**")
        if current_scene.endingType:
            st.info(f"Ending Type: {current_scene.endingType}" if st.session_state.locale == "en" else f"结局类型：{current_scene.endingType}")
        
        st.divider()
        
        # Save thread option
        st.subheader("💾 Save this playthrough as a Story Thread?" if st.session_state.locale == "en" else "💾 保存这次试玩为故事线？")
        
        with st.form("save_thread_form"):
            thread_name = st.text_input(
                "Thread Name" if st.session_state.locale == "en" else "故事线名称",
                value=f"Playthrough {len(project.threads) + 1}",
                placeholder="My favorite route"
            )
            thread_desc = st.text_area(
                "Description (optional)" if st.session_state.locale == "en" else "描述（可选）",
                placeholder="This is the path where..."
            )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("💾 Save Thread" if st.session_state.locale == "en" else "💾 保存故事线", use_container_width=True):
                    # Create StoryThread
                    thread_id = f"thread_{uuid.uuid4().hex[:8]}"
                    thread = StoryThread(
                        id=thread_id,
                        name=thread_name,
                        description=thread_desc,
                        steps=[ThreadStep(**step) for step in st.session_state.play_thread_steps]
                    )
                    project.threads[thread_id] = thread
                    
                    # Save project
                    project_service = st.session_state.project_service
                    project_service.save_project()
                    
                    st.success(f"✅ Thread '{thread_name}' saved!" if st.session_state.locale == "en" else f"✅ 故事线「{thread_name}」已保存！")
                    st.balloons()
            
            with col2:
                if st.form_submit_button("🔄 Play Again" if st.session_state.locale == "en" else "🔄 再玩一次", use_container_width=True):
                    st.session_state.play_current_scene = None
                    st.session_state.play_thread_steps = []
                    st.rerun()
    
    # Show saved threads
    if project.threads:
        st.divider()
        st.subheader(f"📚 Saved Threads ({len(project.threads)})" if st.session_state.locale == "en" else f"📚 已保存的故事线 ({len(project.threads)})")
        
        for thread_id, thread in list(project.threads.items())[:5]:  # Show first 5
            with st.expander(f"📖 {thread.name} ({len(thread.steps)} steps)"):
                if thread.description:
                    st.caption(thread.description)
                
                st.write("**Path:**" if st.session_state.locale == "en" else "**路径：**")
                for i, step in enumerate(thread.steps):
                    scene = project.scenes.get(step.sceneId)
                    if scene:
                        st.text(f"{i+1}. {scene.title}")
                
                if st.button("🗑️ Delete" if st.session_state.locale == "en" else "🗑️ 删除", key=f"del_thread_{thread_id}"):
                    del project.threads[thread_id]
                    project_service = st.session_state.project_service
                    project_service.save_project()
                    st.rerun()
