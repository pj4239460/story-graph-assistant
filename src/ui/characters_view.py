"""
Characters management view
"""
import streamlit as st


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
                        st.info(i18n.t('routes.edit_coming_soon'))
                    
                    if st.button(f"🗑️ {i18n.t('common.delete')}", key=f"delete_char_{character.id}", use_container_width=True):
                        character_service.delete_character(project, character.id)
                        st.success(i18n.t('characters.character_deleted', name=character.name))
                        st.rerun()
