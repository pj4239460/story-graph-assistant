"""
Chat with Story View
"""
import streamlit as st
from ..config import DEBUG_MODE

def render_chat_view():
    """Render chat view"""
    i18n = st.session_state.i18n
    project_service = st.session_state.project_service
    ai_service = st.session_state.ai_service
    app_db = st.session_state.app_db
    project = project_service.get_project()
    
    st.header(f"💬 {i18n.t('chat.title')}")
    
    # Get project identifier (use current path if available, otherwise project ID)
    project_id = project_service.current_path or project.id
    
    # Initialize chat history from database
    if "chat_history" not in st.session_state:
        # Load from database
        db_history = app_db.get_chat_history(project_id)
        st.session_state.chat_history = [{"role": msg["role"], "content": msg["content"]} for msg in db_history]
        
    # Initialize processing state
    if "chat_processing" not in st.session_state:
        st.session_state.chat_processing = False
    
    # Track current project to reload history when switching projects
    if "chat_current_project" not in st.session_state:
        st.session_state.chat_current_project = project_id
    elif st.session_state.chat_current_project != project_id:
        # Project changed, reload history
        db_history = app_db.get_chat_history(project_id)
        st.session_state.chat_history = [{"role": msg["role"], "content": msg["content"]} for msg in db_history]
        st.session_state.chat_current_project = project_id
        st.session_state.chat_processing = False
        
    print(f"DEBUG: render_chat_view start. History size: {len(st.session_state.chat_history)}, Processing: {st.session_state.chat_processing}")
    
    # Clear history button
    if st.button(f"🗑️ {i18n.t('chat.clear_history')}"):
        st.session_state.chat_history = []
        st.session_state.chat_processing = False
        # Clear from database
        app_db.clear_chat_history(project_id)
        st.rerun()
        
    # Display chat messages
    if not st.session_state.chat_history:
        st.info(f"👋 {i18n.t('chat.welcome')}")
    
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
    # Handle pending AI response (State Machine Approach)
    if st.session_state.chat_processing:
        with st.chat_message("assistant"):
            with st.spinner(i18n.t('chat.thinking')):
                try:
                    print("DEBUG: Processing pending chat request...")
                    # Get the last user message as prompt
                    last_user_msg = st.session_state.chat_history[-1]
                    prompt = last_user_msg["content"]
                    
                    # Prepare history (exclude the last user message which is the current prompt)
                    history_context = st.session_state.chat_history[:-1]
                    
                    if DEBUG_MODE:
                        # Use hardcoded response to save tokens during development
                        import time
                        time.sleep(0.5)  # Simulate API delay
                        response = f"""你好！我是故事助手。

关于你的问题「{prompt}」：

这是一个测试响应。在实际使用中，我会根据你的故事内容（角色、场景、设定）来回答问题。

目前的故事项目包含：
- **角色数量**: {len(project.characters)}
- **场景数量**: {len(project.scenes)}

你可以问我：
- 角色之间的关系如何？
- 某个场景的逻辑是否合理？
- 剧情是否存在矛盾？

*（开发模式：硬编码响应，不消耗 Token）*"""
                    else:
                        # Production: Use real AI service
                        response = ai_service.chat_with_story(
                            project=project,
                            query=prompt,
                            history=history_context
                        )
                    
                    print(f"DEBUG: AI Response generated (len={len(response) if response else 0})")
                    
                    if not response:
                        response = i18n.t('chat.error_no_response') if hasattr(i18n, 't') else "Error: No response from AI."

                    # Add assistant response to history
                    st.session_state.chat_history.append({"role": "assistant", "content": response})
                    
                    # Save to database
                    app_db.save_chat_message(project_id, "assistant", response)
                    
                    # Reset processing state
                    st.session_state.chat_processing = False
                    
                    # Rerun to display the new message normally
                    st.rerun()
                    
                except Exception as e:
                    import traceback
                    error_msg = f"Error: {str(e)}"
                    print(f"CHAT ERROR: {error_msg}\n{traceback.format_exc()}")
                    st.error(error_msg)
                    error_content = f"⚠️ {error_msg}"
                    st.session_state.chat_history.append({"role": "assistant", "content": error_content})
                    # Save error to database
                    app_db.save_chat_message(project_id, "assistant", error_content)
                    st.session_state.chat_processing = False
                    st.rerun()

    # Chat input
    # Only show input if not processing
    if not st.session_state.chat_processing:
        if prompt := st.chat_input(i18n.t('chat.placeholder')):
            print(f"DEBUG: Chat input received: {prompt}")
            # Add user message to history
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            # Save to database
            app_db.save_chat_message(project_id, "user", prompt)
            # Set processing flag
            st.session_state.chat_processing = True
            # Rerun immediately to trigger the processing block above
            st.rerun()
