"""
Characters management view
"""
import streamlit as st
from ..services.state_service import StateService


def render_characters_view():
    """Render characters management view"""
    i18n = st.session_state.i18n
    project_service = st.session_state.project_service
    character_service = st.session_state.character_service
    
    project = project_service.get_project()
    
    st.header(f"👥 {i18n.t('characters.title')}")
    
    characters = character_service.get_all_characters(project)
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader(f"{i18n.t('characters.character_list')} ({len(characters)})")
    with col2:
        if st.button(f"➕ {i18n.t('characters.new_character')}", use_container_width=True):
            st.session_state.show_character_create = True
    
    # New character form
    if st.session_state.get("show_character_create", False):
        with st.form("create_character_form"):
            st.subheader(i18n.t('characters.create_character'))
            name = st.text_input(i18n.t('characters.character_name'), placeholder=i18n.t('characters.placeholder_name'))
            alias = st.text_input(i18n.t('characters.alias'), placeholder=i18n.t('characters.placeholder_alias'))
            description = st.text_area(i18n.t('characters.description'), height=150, placeholder=i18n.t('characters.placeholder_description'))
            
            col1, col2 = st.columns(2)
            with col1:
                submitted = st.form_submit_button(i18n.t('common.create'), use_container_width=True)
            with col2:
                cancelled = st.form_submit_button(i18n.t('common.cancel'), use_container_width=True)
            
            if submitted and name:
                character = character_service.create_character(project, name, description)
                if alias:
                    character.alias = alias
                st.session_state.show_character_create = False
                st.success(f"✅ {i18n.t('characters.character_created', name=name)}")
                st.rerun()
            
            if cancelled:
                st.session_state.show_character_create = False
                st.rerun()
    
    # Display character list
    if not characters:
        st.info(i18n.t('characters.no_characters'))
    else:
        for character in characters:
            with st.expander(f"👤 {character.name} {f'({character.alias})' if character.alias else ''}"):
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    st.markdown(f"**{i18n.t('common.id')}:** `{character.id}`")
                    
                    if character.description:
                        st.markdown(f"**{i18n.t('characters.description')}：**")
                        st.write(character.description)
                    
                    # Traits
                    if character.traits:
                        st.markdown(f"**{i18n.t('characters.traits')}：**")
                        st.write(", ".join(character.traits))
                    else:
                        st.caption(f"_{i18n.t('characters.no_traits')}_")
                    
                    # Goals
                    if character.goals:
                        st.markdown(f"**{i18n.t('characters.goals')}：**")
                        for goal in character.goals:
                            st.write(f"- {goal}")
                    
                    # Fears
                    if character.fears:
                        st.markdown(f"**{i18n.t('characters.fears')}：**")
                        for fear in character.fears:
                            st.write(f"- {fear}")
                    
                    # Relationships
                    if character.relationships:
                        st.markdown(f"**{i18n.t('characters.relationships')}：**")
                        for rel in character.relationships:
                            target = character_service.get_character(project, rel.targetId)
                            target_name = target.name if target else i18n.t('characters.unknown')
                            st.write(f"- {i18n.t('characters.with')} {target_name}：{rel.summary}")
                
                with col2:
                    if st.button(f"✏️ {i18n.t('common.edit')}", key=f"edit_char_{character.id}", use_container_width=True):
                        st.session_state[f"editing_char_{character.id}"] = True
                        st.rerun()
                    
                    if st.button(f"🗑️ {i18n.t('common.delete')}", key=f"delete_char_{character.id}", use_container_width=True):
                        character_service.delete_character(project, character.id)
                        st.success(i18n.t('characters.character_deleted', name=character.name))
                        st.rerun()
                
                # Edit form
                if st.session_state.get(f"editing_char_{character.id}", False):
                    st.divider()
                    with st.form(f"edit_character_form_{character.id}"):
                        st.subheader(f"✏️ {i18n.t('common.edit')} - {character.name}")
                        
                        new_name = st.text_input(i18n.t('characters.character_name'), value=character.name)
                        new_alias = st.text_input(i18n.t('characters.alias'), value=character.alias or "")
                        new_description = st.text_area(i18n.t('characters.description'), value=character.description, height=150)
                        
                        # Traits
                        traits_text = st.text_area(
                            i18n.t('characters.traits'),
                            value="\n".join(character.traits) if character.traits else "",
                            height=100,
                            help=i18n.t('characters.traits_help')
                        )
                        
                        # Goals
                        goals_text = st.text_area(
                            i18n.t('characters.goals'),
                            value="\n".join(character.goals) if character.goals else "",
                            height=100,
                            help=i18n.t('characters.goals_help')
                        )
                        
                        # Fears
                        fears_text = st.text_area(
                            i18n.t('characters.fears'),
                            value="\n".join(character.fears) if character.fears else "",
                            height=100,
                            help=i18n.t('characters.fears_help')
                        )
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            submitted = st.form_submit_button(i18n.t('common.save'), use_container_width=True)
                        with col2:
                            cancelled = st.form_submit_button(i18n.t('common.cancel'), use_container_width=True)
                        
                        if submitted:
                            # Parse multi-line text into lists
                            new_traits = [t.strip() for t in traits_text.split('\n') if t.strip()]
                            new_goals = [g.strip() for g in goals_text.split('\n') if g.strip()]
                            new_fears = [f.strip() for f in fears_text.split('\n') if f.strip()]
                            
                            character_service.update_character(
                                project,
                                character.id,
                                name=new_name,
                                alias=new_alias if new_alias else None,
                                description=new_description,
                                traits=new_traits,
                                goals=new_goals,
                                fears=new_fears
                            )
                            st.session_state[f"editing_char_{character.id}"] = False
                            st.success(f"✅ {i18n.t('characters.character_updated', name=new_name)}")
                            st.rerun()
                        
                        if cancelled:
                            st.session_state[f"editing_char_{character.id}"] = False
                            st.rerun()
    
    # ===== NEW: Dynamic State Viewer =====
    st.divider()
    with st.expander("🔮 Dynamic State Viewer - See Character States at Any Point" if st.session_state.locale == "en" else "🔮 动态状态查看器 - 查看任意时间点的角色状态", expanded=False):
        render_state_viewer(project, i18n)


def render_state_viewer(project, i18n):
    """Render dynamic state viewer for saved threads"""
    if not project.threads:
        st.info("No saved story threads yet. Use Play Path mode in Routes to create threads!" if st.session_state.locale == "en" else "还没有保存的故事线。请在路线图的路径试玩模式中创建故事线！")
        return
    
    st.caption("Select a saved thread and step to view character states at that point" if st.session_state.locale == "en" else "选择一个已保存的故事线和步骤，查看该时间点的角色状态")
    
    # Thread selection
    thread_options = {tid: thread.name for tid, thread in project.threads.items()}
    selected_thread_id = st.selectbox(
        "Story Thread" if st.session_state.locale == "en" else "故事线",
        options=list(thread_options.keys()),
        format_func=lambda x: f"{thread_options[x]} ({len(project.threads[x].steps)} steps)"
    )
    
    if not selected_thread_id:
        return
    
    thread = project.threads[selected_thread_id]
    
    # Step selection
    step_options = {}
    for i, step in enumerate(thread.steps):
        scene = project.scenes.get(step.sceneId)
        step_label = f"Step {i+1}: {scene.title if scene else step.sceneId}"
        step_options[i] = step_label
    
    selected_step = st.selectbox(
        "Time Point (Step)" if st.session_state.locale == "en" else "时间点（步骤）",
        options=list(step_options.keys()),
        format_func=lambda x: step_options[x]
    )
    
    if selected_step is None:
        return
    
    # Compute state at this point
    state_service = StateService()
    
    try:
        world_state, char_states, rel_states = state_service.compute_state(
            project, 
            selected_thread_id, 
            selected_step
        )
        
        st.divider()
        st.subheader(f"📊 State at {step_options[selected_step]}" if st.session_state.locale == "en" else f"📊 {step_options[selected_step]} 的状态")
        
        # Character states
        if char_states:
            st.markdown("### 👤 Character States" if st.session_state.locale == "en" else "### 👤 角色状态")
            
            for char_id, state in char_states.items():
                char = project.characters.get(char_id)
                if not char:
                    continue
                
                with st.expander(f"👤 {char.name}", expanded=len(char_states) <= 2):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Basic Info**" if st.session_state.locale == "en" else "**基本信息**")
                        if state.mood:
                            st.write(f"😊 Mood: {state.mood}" if st.session_state.locale == "en" else f"😊 心情：{state.mood}")
                        if state.status:
                            st.write(f"📍 Status: {state.status}" if st.session_state.locale == "en" else f"📍 状态：{state.status}")
                        if state.location:
                            st.write(f"🗺️ Location: {state.location}" if st.session_state.locale == "en" else f"🗺️ 位置：{state.location}")
                        
                        if state.active_traits:
                            st.markdown("**Active Traits**" if st.session_state.locale == "en" else "**当前特质**")
                            for trait in state.active_traits:
                                st.caption(f"  • {trait}")
                    
                    with col2:
                        if state.active_goals:
                            st.markdown("**Active Goals**" if st.session_state.locale == "en" else "**当前目标**")
                            for goal in state.active_goals:
                                st.caption(f"  🎯 {goal}")
                        
                        if state.active_fears:
                            st.markdown("**Active Fears**" if st.session_state.locale == "en" else "**当前恐惧**")
                            for fear in state.active_fears:
                                st.caption(f"  😰 {fear}")
                        
                        if state.vars:
                            st.markdown("**Custom Variables**" if st.session_state.locale == "en" else "**自定义变量**")
                            for key, value in state.vars.items():
                                st.caption(f"  `{key}`: {value}")
        
        # Relationship states
        if rel_states:
            st.markdown("### 💕 Relationship States" if st.session_state.locale == "en" else "### 💕 关系状态")
            
            for rel_key, rel_data in rel_states.items():
                char_ids = rel_key.split("|")
                char_names = []
                for cid in char_ids:
                    if cid in project.characters:
                        char_names.append(project.characters[cid].name)
                
                if char_names:
                    rel_name = " & ".join(char_names)
                    with st.expander(f"💕 {rel_name}"):
                        for key, value in rel_data.items():
                            st.write(f"**{key}**: {value}")
        
        # World state
        if world_state.vars:
            st.markdown("### 🌍 World State" if st.session_state.locale == "en" else "### 🌍 世界状态")
            
            with st.expander("🌍 Global Variables" if st.session_state.locale == "en" else "🌍 全局变量", expanded=True):
                for key, value in world_state.vars.items():
                    st.write(f"**{key}**: `{value}`")
        
        # Show state diff option
        if selected_step > 0:
            st.divider()
            if st.button("🔍 Show Changes Since Previous Step" if st.session_state.locale == "en" else "🔍 显示与上一步的变化"):
                diff = state_service.diff_state(project, selected_thread_id, selected_step - 1, selected_step)
                
                st.markdown("### 📝 Changes" if st.session_state.locale == "en" else "### 📝 变化")
                
                if diff.get("characters"):
                    st.markdown("**Character Changes:**" if st.session_state.locale == "en" else "**角色变化：**")
                    for char_id, changes in diff["characters"].items():
                        char = project.characters.get(char_id)
                        if char:
                            st.write(f"**{char.name}:**")
                            for field, (old_val, new_val) in changes.items():
                                st.caption(f"  • {field}: `{old_val}` → `{new_val}`")
                
                if diff.get("relationships"):
                    st.markdown("**Relationship Changes:**" if st.session_state.locale == "en" else "**关系变化：**")
                    for rel_key, changes in diff["relationships"].items():
                        st.write(f"**{rel_key}:**")
                        for field, (old_val, new_val) in changes.items():
                            st.caption(f"  • {field}: `{old_val}` → `{new_val}`")
                
                if diff.get("world"):
                    st.markdown("**World Changes:**" if st.session_state.locale == "en" else "**世界变化：**")
                    for field, (old_val, new_val) in diff["world"].items():
                        st.caption(f"  • {field}: `{old_val}` → `{new_val}`")
    
    except Exception as e:
        st.error(f"Error computing state: {str(e)}" if st.session_state.locale == "en" else f"计算状态时出错：{str(e)}")
