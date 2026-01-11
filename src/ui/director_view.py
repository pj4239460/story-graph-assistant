"""
World Director view - Storylet-driven world evolution

Allows users to tick the world forward using storylets and view state changes.
"""
import streamlit as st
from ..models.storylet import DirectorConfig
from ..services.director_service import DirectorService


def render_director_view():
    """Render World Director view"""
    i18n = st.session_state.i18n
    project_service = st.session_state.project_service
    
    project = project_service.get_project()
    
    st.header("🎬 World Director" if st.session_state.locale == "en" else "🎬 世界导演")
    st.caption(
        "Drive world evolution using storylets - reusable narrative events triggered by conditions"
        if st.session_state.locale == "en"
        else "使用故事块驱动世界演化 - 基于条件触发的可重用叙事事件"
    )
    
    # Check if project has storylets
    if not hasattr(project, 'storylets') or not project.storylets:
        st.info(
            "📦 No storylets found. Storylets are reusable narrative events that trigger based on world state."
            if st.session_state.locale == "en"
            else "📦 未找到故事块。故事块是基于世界状态触发的可重用叙事事件。"
        )
        
        with st.expander("ℹ️ What are Storylets?" if st.session_state.locale == "en" else "ℹ️ 什么是故事块？"):
            if st.session_state.locale == "en":
                st.markdown("""
                **Storylets** are a narrative design pattern for dynamic storytelling:
                
                - **Preconditions**: Requirements that must be met to trigger
                - **Effects**: Changes to world/character/relationship state when triggered
                - **Weight**: Probability of being selected when conditions met
                - **Cooldown**: Minimum ticks before can trigger again
                - **Tags**: Used for diversity (avoid repetitive events)
                
                This approach reduces branching explosion and creates emergent narratives.
                
                **Example Storylet**:
                - Title: "Market Day Incident"
                - Preconditions: Guild A power > 50, Market peace < 30
                - Effects: Guild A power -5, Market tension +10
                - Tags: conflict, economic
                """)
            else:
                st.markdown("""
                **故事块（Storylets）** 是动态叙事的设计模式：
                
                - **前置条件（Preconditions）**：触发所需的要求
                - **效果（Effects）**：触发时对世界/角色/关系状态的改变
                - **权重（Weight）**：满足条件时被选中的概率
                - **冷却（Cooldown）**：再次触发前的最小tick数
                - **标签（Tags）**：用于多样性控制（避免重复事件）
                
                这种方法减少分支爆炸，创造涌现式叙事。
                
                **故事块示例**：
                - 标题："市场日事件"
                - 前置条件：工会A势力 > 50，市场和平度 < 30
                - 效果：工会A势力 -5，市场紧张度 +10
                - 标签：冲突、经济
                """)
        
        st.info(
            "💡 Tip: Load the example projects (wuxia_rpg, scifi_adventure, romance_sim) to see storylets in action!"
            if st.session_state.locale == "en"
            else "💡 提示：加载示例项目（武侠RPG、科幻冒险、恋爱模拟）查看故事块的实际应用！"
        )
        
        return
    
    # Display storylets library
    st.divider()
    st.subheader(f"📚 Storylets Library ({len(project.storylets)})" if st.session_state.locale == "en" else f"📚 故事块库 ({len(project.storylets)})")
    
    with st.expander("View All Storylets" if st.session_state.locale == "en" else "查看所有故事块", expanded=False):
        for storylet_id, storylet in project.storylets.items():
            st.markdown(f"**{storylet.title}** (`{storylet.id}`)")
            if storylet.description:
                st.caption(storylet.description)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.caption(f"Tags: {', '.join(storylet.tags) if storylet.tags else 'none'}")
            with col2:
                st.caption(f"Weight: {storylet.weight}")
            with col3:
                st.caption(f"Cooldown: {storylet.cooldown} | Once: {storylet.once}")
            
            # Show fallback and ordering constraints
            if storylet.is_fallback:
                st.info("🔄 Fallback storylet (triggers when world stuck)")
            
            if storylet.requires_fired:
                st.caption(f"⛓️ Requires: {', '.join(storylet.requires_fired)}")
            
            if storylet.forbids_fired:
                st.caption(f"🚫 Forbids: {', '.join(storylet.forbids_fired)}")
            
            if storylet.preconditions:
                st.caption(f"Conditions: {len(storylet.preconditions)}")
            if storylet.effects:
                st.caption(f"Effects: {len(storylet.effects)}")
            
            st.divider()
    
    # Thread selection
    st.divider()
    st.subheader("🎮 Tick Control" if st.session_state.locale == "en" else "🎮 Tick 控制")
    
    if not project.threads:
        st.info(
            "No story threads found. Create a thread using Play Path mode in Routes first."
            if st.session_state.locale == "en"
            else "未找到故事线。请先在路线图的路径试玩模式中创建故事线。"
        )
        return
    
    # Select thread
    thread_options = {tid: thread.name for tid, thread in project.threads.items()}
    selected_thread_id = st.selectbox(
        "Story Thread" if st.session_state.locale == "en" else "故事线",
        options=list(thread_options.keys()),
        format_func=lambda x: f"{thread_options[x]} ({len(project.threads[x].steps)} steps)",
        key="director_thread"
    )
    
    thread = project.threads[selected_thread_id]
    
    # Select step
    step_index = st.slider(
        "Story Progress (Step)" if st.session_state.locale == "en" else "故事进度（步骤）",
        min_value=0,
        max_value=len(thread.steps) - 1 if thread.steps else 0,
        value=len(thread.steps) - 1 if thread.steps else 0,
        key="director_step"
    )
    
    if thread.steps:
        current_scene = project.scenes.get(thread.steps[step_index].sceneId)
        if current_scene:
            st.caption(f"Current scene: {current_scene.title}")
    
    # Director configuration
    st.divider()
    st.subheader("⚙️ Director Settings" if st.session_state.locale == "en" else "⚙️ 导演设置")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        events_per_tick = st.number_input(
            "Events per tick" if st.session_state.locale == "en" else "每次事件数",
            min_value=1,
            max_value=5,
            value=2,
            key="director_events"
        )
    
    with col2:
        pacing_preference = st.selectbox(
            "Pacing" if st.session_state.locale == "en" else "节奏",
            options=["balanced", "calm", "intense"],
            format_func=lambda x: {"balanced": "Balanced/平衡", "calm": "Calm/平缓", "intense": "Intense/紧张"}[x],
            key="director_pacing"
        )
    
    with col3:
        diversity_penalty = st.slider(
            "Diversity penalty" if st.session_state.locale == "en" else "多样性惩罚",
            min_value=0.0,
            max_value=1.0,
            value=0.5,
            step=0.1,
            help="Higher = more variety (penalize recent tags)" if st.session_state.locale == "en" else "越高越多样（惩罚最近的标签）",
            key="director_diversity"
        )
    
    # Advanced settings
    with st.expander("⚙️ Advanced Settings" if st.session_state.locale == "en" else "⚙️ 高级设置"):
        fallback_ticks = st.number_input(
            "Fallback after idle ticks" if st.session_state.locale == "en" else "空闲tick后启用备选",
            min_value=0,
            max_value=10,
            value=3,
            help="Trigger fallback storylets after N consecutive ticks with no regular events (0=disabled)"
                 if st.session_state.locale == "en"
                 else "连续N个没有常规事件的tick后触发备选故事块（0=禁用）",
            key="director_fallback"
        )
    
    # Tick button
    st.divider()
    
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("🎲 Run Tick" if st.session_state.locale == "en" else "🎲 执行 Tick", use_container_width=True, type="primary"):
            # Execute tick
            director_service = DirectorService()
            config = DirectorConfig(
                events_per_tick=events_per_tick,
                pacing_preference=pacing_preference,
                diversity_penalty=diversity_penalty,
                fallback_after_idle_ticks=fallback_ticks
            )
            
            with st.spinner("Running tick..." if st.session_state.locale == "en" else "执行 tick..."):
                tick_record = director_service.tick(
                    project,
                    selected_thread_id,
                    step_index,
                    config
                )
                
                # Save project (no argument needed - uses current path)
                project_service.save_project()
                
                # Store in session for display
                st.session_state.last_tick_record = tick_record
                st.success("✅ Tick complete!" if st.session_state.locale == "en" else "✅ Tick 完成！")
                st.rerun()
    
    with col2:
        # Get tick history
        tick_history_key = f"tick_history_{selected_thread_id}"
        if hasattr(project, 'tick_histories') and tick_history_key in project.tick_histories:
            tick_history = project.tick_histories[tick_history_key]
            idle_info = f" | Idle: {tick_history.idle_tick_count}" if tick_history.idle_tick_count > 0 else ""
            st.caption(
                f"Tick history: {len(tick_history.ticks)} ticks | Intensity: {tick_history.current_intensity:.2f}{idle_info}"
                if st.session_state.locale == "en"
                else f"Tick 历史：{len(tick_history.ticks)} 次 | 强度：{tick_history.current_intensity:.2f}{idle_info}"
            )
    
    # Display last tick result
    if 'last_tick_record' in st.session_state:
        render_tick_result(st.session_state.last_tick_record, project, i18n)
    
    # Display tick history
    st.divider()
    render_tick_history(project, selected_thread_id, i18n)


def render_tick_result(tick_record, project, i18n):
    """Render the result of a tick"""
    st.divider()
    st.subheader(f"📊 Tick #{tick_record.tick_number} Results" if st.session_state.locale == "en" else f"📊 Tick #{tick_record.tick_number} 结果")
    
    # Intensity display
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            "Intensity Before" if st.session_state.locale == "en" else "之前强度",
            f"{tick_record.intensity_before:.2f}"
        )
    with col2:
        intensity_change = tick_record.intensity_after - tick_record.intensity_before
        st.metric(
            "Intensity After" if st.session_state.locale == "en" else "之后强度",
            f"{tick_record.intensity_after:.2f}",
            delta=f"{intensity_change:+.2f}"
        )
    with col3:
        st.metric(
            "Events Triggered" if st.session_state.locale == "en" else "触发事件",
            len(tick_record.events)
        )
    
    # Events
    if tick_record.events:
        st.markdown("### 🎯 Selected Storylets" if st.session_state.locale == "en" else "### 🎯 选中的故事块")
        
        for i, event in enumerate(tick_record.events):
            with st.expander(f"{i+1}. {event.storylet_title}", expanded=True):
                st.caption(f"**ID**: `{event.storylet_id}`")
                
                # Rationale
                if event.rationale:
                    st.markdown("**Why selected:**" if st.session_state.locale == "en" else "**选择原因：**")
                    st.text(event.rationale)
                
                # Effects
                if event.applied_effects:
                    st.markdown("**Applied effects:**" if st.session_state.locale == "en" else "**应用的效果：**")
                    for effect in event.applied_effects:
                        icon = "👤" if effect["scope"] == "character" else ("💕" if effect["scope"] == "relationship" else "🌍")
                        st.caption(f"{icon} {effect['scope']}/{effect['target']}: {effect['op']} {effect['path']} = {effect['value']}")
                        if effect.get('reason'):
                            st.caption(f"   ↳ {effect['reason']}")
    
    # State diff
    if tick_record.state_diff:
        st.markdown("### 📝 State Changes" if st.session_state.locale == "en" else "### 📝 状态变化")
        
        with st.expander("View Detailed Diff" if st.session_state.locale == "en" else "查看详细差异", expanded=False):
            # World changes
            if "world" in tick_record.state_diff:
                st.markdown("**🌍 World Variables:**" if st.session_state.locale == "en" else "**🌍 世界变量：**")
                for key, change in tick_record.state_diff["world"].items():
                    st.write(f"• `{key}`: {change['before']} → {change['after']}")
            
            # Character changes
            if "characters" in tick_record.state_diff:
                st.markdown("**👤 Character Changes:**" if st.session_state.locale == "en" else "**👤 角色变化：**")
                for char_id, changes in tick_record.state_diff["characters"].items():
                    char = project.characters.get(char_id)
                    char_name = char.name if char else char_id
                    st.markdown(f"**{char_name}:**")
                    for field, change in changes.items():
                        if field == "vars":
                            for var_key, var_change in change.items():
                                st.write(f"  • {var_key}: {var_change['before']} → {var_change['after']}")
                        else:
                            st.write(f"  • {field}: {change['before']} → {change['after']}")
            
            # Relationship changes
            if "relationships" in tick_record.state_diff:
                st.markdown("**💕 Relationship Changes:**" if st.session_state.locale == "en" else "**💕 关系变化：**")
                for rel_key, changes in tick_record.state_diff["relationships"].items():
                    st.markdown(f"**{rel_key}:**")
                    for field, change in changes.items():
                        st.write(f"  • {field}: {change['before']} → {change['after']}")


def render_tick_history(project, thread_id, i18n):
    """Render tick history timeline"""
    tick_history_key = f"tick_history_{thread_id}"
    
    if not hasattr(project, 'tick_histories') or tick_history_key not in project.tick_histories:
        return
    
    tick_history = project.tick_histories[tick_history_key]
    
    if not tick_history.ticks:
        return
    
    st.subheader(f"📜 Tick History ({len(tick_history.ticks)} ticks)" if st.session_state.locale == "en" else f"📜 Tick 历史 ({len(tick_history.ticks)} 次)")
    
    with st.expander("View Timeline" if st.session_state.locale == "en" else "查看时间线", expanded=False):
        for tick_record in reversed(tick_history.ticks[-10:]):  # Show last 10
            col1, col2 = st.columns([1, 4])
            
            with col1:
                st.markdown(f"**Tick #{tick_record.tick_number}**")
                st.caption(f"Intensity: {tick_record.intensity_after:.2f}")
            
            with col2:
                if tick_record.events:
                    event_titles = [e.storylet_title for e in tick_record.events]
                    st.markdown(f"🎯 {', '.join(event_titles)}")
                else:
                    st.caption("(No events)")
            
            st.divider()
