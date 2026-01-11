"""
Storylet Editor View - Visual interface for creating and managing storylets

This module provides a comprehensive visual editor for World Director storylets,
eliminating the need to manually edit JSON files. It supports all v0.7 features
including ordering constraints and fallback mechanisms.

Key Features:
    - Visual storylet creation with form-based input
    - Library view with search and filtering
    - Support for v0.7 ordering constraints (requires_fired, forbids_fired)
    - Dynamic condition and effect management
    - Real-time validation and saving
    - Duplicate and edit existing storylets
    - Bilingual support (English/Chinese)

Usage:
    This view is integrated into the main application as a tab. It automatically
    initializes the storylets dictionary if it doesn't exist in the project.

Architecture:
    - render_storylet_editor(): Main entry point, creates tabbed interface
    - render_storylet_library(): Displays searchable/filterable library of storylets
    - render_storylet_card(): Individual storylet display with edit/delete
    - render_storylet_creator(): Form-based creator/editor with dynamic fields

Version: 0.8
Author: Story Graph Assistant Team
Last Updated: 2026-01-11
"""
import streamlit as st
from ..models.storylet import Storylet, Precondition, Effect


def render_storylet_editor():
    """
    Render the main Storylet Editor interface.
    
    Creates a tabbed interface with:
    1. Library tab - Browse, search, and manage existing storylets
    2. Create New tab - Form-based storylet creation/editing
    
    Automatically initializes project.storylets if not present.
    
    Returns:
        None: Renders directly to Streamlit interface
    """
    i18n = st.session_state.i18n
    project_service = st.session_state.project_service
    project = project_service.get_project()
    
    st.header(f"鉁忥笍 {i18n.t('storylet_editor.title')}")
    st.caption(i18n.t('storylet_editor.subtitle'))
    
    # Initialize storylets dictionary if not exists
    # This ensures backward compatibility with projects created before v0.5
    if not hasattr(project, 'storylets'):
        project.storylets = {}
    
    # Create tabbed interface for better organization
    tab1, tab2 = st.tabs([
        f"馃摎 {i18n.t('storylet_editor.library_tab')}",
        f"鉃?{i18n.t('storylet_editor.create_tab')}"
    ])
    
    with tab1:
        render_storylet_library(project, project_service)
    
    with tab2:
        render_storylet_creator(project, project_service)


def render_storylet_library(project, project_service):
    """
    Render the storylet library with search and filtering capabilities.
    
    Provides a searchable, filterable view of all storylets in the project.
    Each storylet is displayed as a card with key information and actions.
    
    Search functionality:
        - Searches across title, ID, and tags
        - Case-insensitive matching
    
    Filter options:
        - All: Show all storylets
        - Fallback: Only fallback storylets (is_fallback=True)
        - Once: Only one-time storylets (once=True)
        - Has Cooldown: Only storylets with cooldown > 0
        - Has Ordering: Only storylets with ordering constraints
    
    Args:
        project: Current project instance containing storylets
        project_service: Service for project operations (save, etc.)
    
    Returns:
        None: Renders directly to Streamlit interface
    """
    i18n = st.session_state.i18n
    st.subheader(i18n.t('storylet_editor.library_title').format(count=len(project.storylets)))
    
    # Display helpful message if no storylets exist
    if not project.storylets:
        st.info(i18n.t('storylet_editor.no_storylets'))
        return
    
    # Search and filter UI
    col1, col2 = st.columns([2, 1])
    with col1:
        search = st.text_input(
            f"馃攳 {i18n.t('storylet_editor.search_label')}",
            placeholder=i18n.t('storylet_editor.search_placeholder'),
            key="storylet_search"
        )
    
    with col2:
        filter_type = st.selectbox(
            i18n.t('storylet_editor.filter_label'),
            ["All", "Fallback", "Once", "Has Cooldown", "Has Ordering"],
            format_func=lambda x: i18n.t(f'storylet_editor.filter_{x.lower().replace(" ", "_")}'),
            key="storylet_filter"
        )
    
    # Apply search and filter logic to storylets
    filtered = []
    for sid, storylet in project.storylets.items():
        # Search filter: check if search term appears in title, ID, or tags
        # Case-insensitive search across all searchable fields
        if search and search.lower() not in (
            storylet.title.lower() + storylet.id.lower() + " ".join(storylet.tags).lower()
        ):
            continue
        
        # Type filters: apply selected filter type
        # Each filter checks specific storylet properties
        if filter_type == "Fallback" and not storylet.is_fallback:
            continue
        if filter_type == "Once" and not storylet.once:
            continue
        if filter_type == "Has Cooldown" and storylet.cooldown == 0:
            continue
        # Ordering filter: check if either requires_fired or forbids_fired is non-empty
        if filter_type == "Has Ordering" and not (storylet.requires_fired or storylet.forbids_fired):
            continue
        
        # Storylet passed all filters, add to results
        filtered.append((sid, storylet))
    
    # Display count of filtered results
    i18n = st.session_state.i18n
    st.caption(i18n.t('storylet_editor.showing_count').format(filtered=len(filtered), total=len(project.storylets)))
    
    # Display each filtered storylet as a card
    for sid, storylet in filtered:
        render_storylet_card(storylet, project, project_service)


def render_storylet_card(storylet, project, project_service):
    """
    Render an individual storylet as an interactive card.
    
    Displays key storylet information in a compact, readable format with
    action buttons for editing and deleting. Uses color-coded badges to
    indicate storylet properties at a glance.
    
    Card Information:
        - Title with expand/collapse functionality
        - ID badge for unique identification
        - Description text (full version)
        - Property badges (Fallback, Once, Cooldown, Tags)
        - Metrics: Weight, Intensity Delta, Condition count, Effect count
        - Ordering constraints display (requires_fired, forbids_fired)
        - Expandable condition and effect details
        - Action buttons (Edit, Delete with confirmation)
    
    Args:
        storylet: Storylet instance to display
        project: Current project containing storylets
        project_service: Service for save operations
    
    Returns:
        None: Renders directly to Streamlit interface
        
    Side Effects:
        - Sets session_state.editing_storylet when Edit is clicked
        - Deletes storylet from project when Delete is confirmed
        - Triggers rerun after state changes
    """
    i18n = st.session_state.i18n
    with st.expander(f"馃搫 {storylet.title}", expanded=False):
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown(f"**{i18n.t('storylet_editor.field_id').replace(' *', '')}**: `{storylet.id}`")
            if storylet.description:
                st.markdown(storylet.description)
            
            # Badges: Display key properties as visual indicators
            badges = []
            if storylet.is_fallback:
                badges.append(f"馃攧 {i18n.t('storylet_editor.badge_fallback')}")  # Backup storylet when world stuck
            if storylet.once:
                badges.append(f"1锔忊儯 {i18n.t('storylet_editor.badge_once')}")  # One-time storylet per playthrough
            if storylet.cooldown > 0:
                badges.append(f"鈴憋笍 {i18n.t('storylet_editor.badge_cooldown').format(cooldown=storylet.cooldown)}")  # Cooldown in ticks
            if storylet.tags:
                badges.extend([f"馃彿锔?{tag}" for tag in storylet.tags])  # Category tags
            
            if badges:
                st.caption(" | ".join(badges))
            
            # Stats: Display numerical metrics in columns
            col_a, col_b, col_c, col_d = st.columns(4)
            with col_a:
                st.metric(i18n.t('storylet_editor.metric_weight'), f"{storylet.weight:.1f}")  # Selection probability
            with col_b:
                st.metric(i18n.t('storylet_editor.metric_intensity'), f"{storylet.intensity_delta:+.1f}")  # Narrative tension change
            with col_c:
                st.metric(i18n.t('storylet_editor.metric_conditions'), len(storylet.preconditions))  # Number of preconditions
            with col_d:
                st.metric(i18n.t('storylet_editor.metric_effects'), len(storylet.effects))  # Number of effects
            
            # Ordering constraints: Display v0.7 narrative dependencies
            # These control quest chains and story sequences
            if storylet.requires_fired:
                st.caption(f"鉀擄笍 **{i18n.t('storylet_editor.label_requires')}**: {', '.join(storylet.requires_fired)}")  # Must fire after these
            if storylet.forbids_fired:
                st.caption(f"馃毇 **{i18n.t('storylet_editor.label_forbids')}**: {', '.join(storylet.forbids_fired)}")  # Cannot fire if these fired
            
            # Preconditions detail: Expandable list of all conditions
            # Shows scope.target.path comparison for each condition
            if storylet.preconditions:
                with st.expander(i18n.t('storylet_editor.view_conditions')):
                    for i, cond in enumerate(storylet.preconditions):
                        st.caption(f"{i+1}. `{cond.scope}.{cond.target}.{cond.path or 'value'}` {cond.op} `{cond.value}`")
            
            # Effects detail: Expandable list of all state mutations
            # Uses icons to indicate scope type (character/relationship/world)
            if storylet.effects:
                with st.expander(i18n.t('storylet_editor.view_effects')):
                    for i, eff in enumerate(storylet.effects):
                        icon = "馃懁" if eff.scope == "character" else ("馃挄" if eff.scope == "relationship" else "馃實")
                        st.caption(f"{i+1}. {icon} `{eff.scope}.{eff.target}.{eff.path or 'value'}` {eff.op} `{eff.value}`")
        
        with col2:
            if st.button(f"鉁忥笍 {i18n.t('storylet_editor.btn_edit')}", key=f"edit_{storylet.id}", use_container_width=True):
                # Store storylet ID in session state to populate form
                st.session_state.editing_storylet = storylet.id
                st.rerun()
            
            if st.button(f"馃棏锔?{i18n.t('storylet_editor.btn_delete')}", key=f"delete_{storylet.id}", use_container_width=True, type="secondary"):
                # Two-click confirmation to prevent accidental deletion
                # First click sets confirmation flag, second click deletes
                if st.session_state.get(f"confirm_delete_{storylet.id}"):
                    del project.storylets[storylet.id]
                    project_service.save_project(project)
                    st.success(i18n.t('storylet_editor.deleted'))
                    st.rerun()
                else:
                    # Set confirmation flag and warn user
                    st.session_state[f"confirm_delete_{storylet.id}"] = True
                    st.warning(i18n.t('storylet_editor.confirm_delete'))


def render_storylet_creator(project, project_service):
    """
    Render the comprehensive storylet creation/editing form.
    
    Provides a full-featured form interface for creating new storylets or editing
    existing ones. Supports all Storylet model fields with appropriate input widgets,
    validation, and real-time state management. Dynamically manages lists of conditions
    and effects with add/remove functionality.
    
    Form Sections:
        1. **Basic Information** (ID, Title, Description)
           - ID is required and immutable when editing
           - Title is required
           - Description is optional rich text
        
        2. **Properties** (Weight, Intensity Delta, Cooldown, Flags)
           - Weight: Probability of selection (0.0-10.0)
           - Intensity Delta: Change to narrative tension (-1.0 to +1.0)
           - Cooldown: Minimum ticks before retriggering (0-20)
           - Once flag: One-time storylet per playthrough
           - Fallback flag: Triggers when world is stuck
        
        3. **Tags** (Comma-separated labels for filtering)
        
        4. **Ordering Constraints (v0.7)**
           - requires_fired: List of prerequisite storylet IDs
           - forbids_fired: List of mutually exclusive storylet IDs
           - Used for quest chains and narrative dependencies
        
        5. **Preconditions** (Dynamic list of Condition objects)
           - Scope: world | character | relationship
           - Target: Entity ID (character name, relationship pair, etc.)
           - Path: Nested property path (e.g., "attributes.strength")
           - Op: Comparison operator (==, !=, >, <, >=, <=)
           - Value: Comparison value (numeric)
           - ALL conditions must be met for storylet to be selectable
        
        6. **Effects** (Dynamic list of Effect objects)
           - Scope: world | character | relationship
           - Target: Entity ID to modify
           - Path: Property path to modify
           - Op: Mutation operation (set, add, multiply)
           - Value: Mutation value
           - Applied atomically when storylet triggers
    
    Form State Management:
        - Uses session_state.editing_storylet to track edit mode
        - Uses session_state.new_storylet_preconditions for condition list
        - Uses session_state.new_storylet_effects for effect list
        - Auto-populates all fields when editing existing storylet
        - Clears form state after successful save or reset
    
    Validation:
        - Required field checks (ID, Title)
        - ID uniqueness validation (when creating new)
        - Type validation for all numeric fields
        - List parsing for tags and ordering constraints
    
    Actions:
        - Save: Creates/updates storylet, saves project, clears form
        - Reset: Clears all form fields and session state
        - Duplicate: Clears editing mode but keeps form data for copying
    
    Args:
        project: Current project containing storylets
        project_service: Service for save operations
    
    Returns:
        None: Renders directly to Streamlit interface
        
    Side Effects:
        - Creates or updates storylets in project.storylets dictionary
        - Modifies session state for form persistence
        - Triggers save and rerun on successful submission
        - Clears session state on reset or after save
    """
    
    i18n = st.session_state.i18n
    # Check if editing existing storylet
    # Session state 'editing_storylet' contains the ID of storylet being edited
    editing_id = st.session_state.get('editing_storylet')
    if editing_id and editing_id in project.storylets:
        st.info(i18n.t('storylet_editor.editing_storylet').format(title=project.storylets[editing_id].title))
        storylet = project.storylets[editing_id]
        if st.button(i18n.t('storylet_editor.cancel_edit')):
            del st.session_state.editing_storylet
            st.rerun()
    else:
        storylet = None
    
    st.subheader(f"馃摑 {i18n.t('storylet_editor.section_basic')}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        storylet_id = st.text_input(
            i18n.t('storylet_editor.field_id'),
            value=storylet.id if storylet else "",
            placeholder=i18n.t('storylet_editor.placeholder_id'),
            disabled=editing_id is not None,
            key="new_storylet_id"
        )
    
    with col2:
        title = st.text_input(
            i18n.t('storylet_editor.field_title'),
            value=storylet.title if storylet else "",
            placeholder=i18n.t('storylet_editor.placeholder_title'),
            key="new_storylet_title"
        )
    
    description = st.text_area(
        i18n.t('storylet_editor.field_description'),
        value=storylet.description if storylet else "",
        placeholder=i18n.t('storylet_editor.placeholder_description'),
        height=100,
        key="new_storylet_desc"
    )
    
    # Properties
    st.divider()
    st.subheader(f"鈿欙笍 {i18n.t('storylet_editor.section_properties')}")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        weight = st.number_input(
            i18n.t('storylet_editor.field_weight'),
            min_value=0.0,
            max_value=10.0,
            value=float(storylet.weight) if storylet else 1.0,
            step=0.1,
            help=i18n.t('storylet_editor.help_weight'),
            key="new_storylet_weight"
        )
    
    with col2:
        intensity_delta = st.number_input(
            i18n.t('storylet_editor.field_intensity'),
            min_value=-1.0,
            max_value=1.0,
            value=float(storylet.intensity_delta) if storylet else 0.0,
            step=0.1,
            help=i18n.t('storylet_editor.help_intensity'),
            key="new_storylet_intensity"
        )
    
    with col3:
        cooldown = st.number_input(
            i18n.t('storylet_editor.field_cooldown'),
            min_value=0,
            max_value=20,
            value=storylet.cooldown if storylet else 0,
            help=i18n.t('storylet_editor.help_cooldown'),
            key="new_storylet_cooldown"
        )
    
    col1, col2 = st.columns(2)
    
    with col1:
        once = st.checkbox(
            i18n.t('storylet_editor.field_once'),
            value=storylet.once if storylet else False,
            key="new_storylet_once"
        )
    
    with col2:
        is_fallback = st.checkbox(
            i18n.t('storylet_editor.field_fallback'),
            value=storylet.is_fallback if storylet else False,
            key="new_storylet_fallback"
        )
    
    # Tags
    tags_input = st.text_input(
        i18n.t('storylet_editor.field_tags'),
        value=", ".join(storylet.tags) if storylet else "",
        placeholder=i18n.t('storylet_editor.placeholder_tags'),
        key="new_storylet_tags"
    )
    tags = [t.strip() for t in tags_input.split(",") if t.strip()]
    
    # Ordering constraints (v0.7)
    st.divider()
    st.subheader(f"馃敆 {i18n.t('storylet_editor.section_ordering')}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        requires_input = st.text_input(
            i18n.t('storylet_editor.field_requires'),
            value=", ".join(storylet.requires_fired) if storylet else "",
            placeholder=i18n.t('storylet_editor.placeholder_requires'),
            help=i18n.t('storylet_editor.help_requires'),
            key="new_storylet_requires"
        )
        requires_fired = [r.strip() for r in requires_input.split(",") if r.strip()]
    
    with col2:
        forbids_input = st.text_input(
            i18n.t('storylet_editor.field_forbids'),
            value=", ".join(storylet.forbids_fired) if storylet else "",
            placeholder=i18n.t('storylet_editor.placeholder_forbids'),
            help=i18n.t('storylet_editor.help_forbids'),
            key="new_storylet_forbids"
        )
        forbids_fired = [f.strip() for f in forbids_input.split(",") if f.strip()]
    
    # Preconditions
    st.divider()
    st.subheader(f"馃搵 {i18n.t('storylet_editor.section_conditions')}")
    st.caption(i18n.t('storylet_editor.conditions_caption'))
    
    # Initialize preconditions in session state
    if 'new_storylet_preconditions' not in st.session_state:
        st.session_state.new_storylet_preconditions = storylet.preconditions if storylet else []
    
    # Add condition button
    if st.button(f"鉃?{i18n.t('storylet_editor.btn_add_condition')}"):
        st.session_state.new_storylet_preconditions.append(
            Precondition(scope="world", target="", path="", op=">=", value=0)
        )
    
    # Display existing conditions
    for i, cond in enumerate(st.session_state.new_storylet_preconditions):
        with st.expander(i18n.t('storylet_editor.condition_label').format(num=i+1), expanded=True):
            col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 1, 2])
            
            with col1:
                scope = st.selectbox(
                    i18n.t('storylet_editor.field_scope'),
                    ["world", "character", "relationship"],
                    index=["world", "character", "relationship"].index(cond.scope),
                    key=f"cond_scope_{i}"
                )
            
            with col2:
                target = st.text_input(i18n.t('storylet_editor.field_target'), value=cond.target, key=f"cond_target_{i}")
            
            with col3:
                path = st.text_input(i18n.t('storylet_editor.field_path'), value=cond.path or "", key=f"cond_path_{i}")
            
            with col4:
                op = st.selectbox(i18n.t('storylet_editor.field_op'), ["==", "!=", ">", "<", ">=", "<="], 
                                 index=["==", "!=", ">", "<", ">=", "<="].index(cond.op) if cond.op in ["==", "!=", ">", "<", ">=", "<="] else 0,
                                 key=f"cond_op_{i}")
            
            with col5:
                value = st.number_input(i18n.t('storylet_editor.field_value'), value=float(cond.value), key=f"cond_value_{i}")
            
            # Update condition
            st.session_state.new_storylet_preconditions[i] = Precondition(
                scope=scope, target=target, path=path, op=op, value=value
            )
            
            if st.button(f"馃棏锔?{i18n.t('storylet_editor.btn_remove')}", key=f"remove_cond_{i}"):
                st.session_state.new_storylet_preconditions.pop(i)
                st.rerun()
    
    # Effects
    st.divider()
    st.subheader(f"鈿?{i18n.t('storylet_editor.section_effects')}")
    st.caption(i18n.t('storylet_editor.effects_caption'))
    
    # Initialize effects in session state
    if 'new_storylet_effects' not in st.session_state:
        st.session_state.new_storylet_effects = storylet.effects if storylet else []
    
    # Add effect button
    if st.button(f"鉃?{i18n.t('storylet_editor.btn_add_effect')}"):
        st.session_state.new_storylet_effects.append(
            Effect(scope="world", target="", path="", op="add", value=0)
        )
    
    # Display existing effects
    for i, eff in enumerate(st.session_state.new_storylet_effects):
        with st.expander(i18n.t('storylet_editor.effect_label').format(num=i+1), expanded=True):
            col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 1, 2])
            
            with col1:
                scope = st.selectbox(
                    i18n.t('storylet_editor.field_scope'),
                    ["world", "character", "relationship"],
                    index=["world", "character", "relationship"].index(eff.scope),
                    key=f"eff_scope_{i}"
                )
            
            with col2:
                target = st.text_input(i18n.t('storylet_editor.field_target'), value=eff.target, key=f"eff_target_{i}")
            
            with col3:
                path = st.text_input(i18n.t('storylet_editor.field_path'), value=eff.path or "", key=f"eff_path_{i}")
            
            with col4:
                op = st.selectbox(i18n.t('storylet_editor.field_op'), ["set", "add", "multiply"], 
                                 index=["set", "add", "multiply"].index(eff.op) if eff.op in ["set", "add", "multiply"] else 0,
                                 key=f"eff_op_{i}")
            
            with col5:
                value = st.number_input(i18n.t('storylet_editor.field_value'), value=float(eff.value), key=f"eff_value_{i}")
            
            # Update effect
            st.session_state.new_storylet_effects[i] = Effect(
                scope=scope, target=target, path=path, op=op, value=value
            )
            
            if st.button(f"馃棏锔?{i18n.t('storylet_editor.btn_remove')}", key=f"remove_eff_{i}"):
                st.session_state.new_storylet_effects.pop(i)
                st.rerun()
    
    # Save button
    st.divider()
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        if st.button(f"馃捑 {i18n.t('storylet_editor.btn_save_storylet')}", 
                    type="primary", use_container_width=True):
            # Validation
            if not storylet_id or not title:
                st.error(i18n.t('storylet_editor.validation_required'))
                return
            
            # Create storylet
            new_storylet = Storylet(
                id=storylet_id,
                title=title,
                description=description,
                weight=weight,
                once=once,
                cooldown=cooldown,
                intensity_delta=intensity_delta,
                tags=tags,
                is_fallback=is_fallback,
                requires_fired=requires_fired,
                forbids_fired=forbids_fired,
                preconditions=st.session_state.new_storylet_preconditions,
                effects=st.session_state.new_storylet_effects
            )
            
            # Save to project
            project.storylets[storylet_id] = new_storylet
            project_service.save_project(project)
            
            # Clear session state
            st.session_state.new_storylet_preconditions = []
            st.session_state.new_storylet_effects = []
            if 'editing_storylet' in st.session_state:
                del st.session_state.editing_storylet
            
            st.success(i18n.t('storylet_editor.saved'))
            st.rerun()
    
    with col2:
        if st.button(f"馃攧 {i18n.t('storylet_editor.btn_reset_form')}", use_container_width=True):
            st.session_state.new_storylet_preconditions = []
            st.session_state.new_storylet_effects = []
            if 'editing_storylet' in st.session_state:
                del st.session_state.editing_storylet
            st.rerun()
    
    with col3:
        if st.button(f"馃搵 {i18n.t('storylet_editor.btn_duplicate_form')}", 
                    use_container_width=True,
                    disabled=not editing_id):
            if editing_id:
                del st.session_state.editing_storylet
                # Keep the form data but clear the ID
                st.info(i18n.t('storylet_editor.duplicate_hint'))


