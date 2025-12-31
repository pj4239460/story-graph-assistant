"""
Settings View
"""
import streamlit as st

def render_settings_view():
    """Render settings view"""
    i18n = st.session_state.i18n
    project_service = st.session_state.project_service
    project = project_service.get_project()
    
    st.header(f"⚙️ {i18n.t('tabs.settings')}")
    
    # AI Configuration
    st.subheader(f"🤖 {i18n.t('settings.ai_config')}")
    
    with st.form("settings_form"):
        # Token Limits
        st.markdown(f"#### {i18n.t('settings.token_limits')}")
        col1, col2 = st.columns(2)
        
        with col1:
            project_limit = st.number_input(
                i18n.t('settings.project_limit'),
                min_value=1000,
                max_value=1000000,
                value=project.aiSettings.projectTokenLimit,
                step=1000,
                help="Total token limit for the entire project"
            )
            
        with col2:
            daily_limit = st.number_input(
                i18n.t('settings.daily_limit'),
                min_value=1000,
                max_value=100000,
                value=project.aiSettings.dailyTokenSoftLimit,
                step=1000,
                help="Daily warning limit (does not block usage)"
            )
            
        st.divider()
        
        # Model Configuration
        st.markdown(f"#### {i18n.t('settings.model_config')}")
        
        st.caption("💡 Select provider and choose from popular models")
        
        provider = st.selectbox(
            i18n.t('settings.provider'),
            ["deepseek", "openai", "anthropic", "google", "ollama"],
            index=["deepseek", "openai", "anthropic", "google", "ollama"].index(project.aiSettings.provider) if project.aiSettings.provider in ["deepseek", "openai", "anthropic", "google", "ollama"] else 0,
            help="Select your preferred LLM provider"
        )
        
        # Model options based on provider (Updated 2025-12-31)
        model_options = {
            "deepseek": {
                "deepseek-chat": "DeepSeek Chat (Latest)",
                "deepseek-reasoner": "DeepSeek Reasoner (R1)",
                "custom": "Custom model name..."
            },
            "openai": {
                # GPT-5 Series (Latest)
                "gpt-5.2": "GPT-5.2 (Latest)",
                "gpt-5.2-pro": "GPT-5.2 Pro (Most Capable)",
                "gpt-5.1": "GPT-5.1",
                "gpt-5": "GPT-5",
                "gpt-5-mini": "GPT-5 Mini (Fast & Cheap)",
                "gpt-5-nano": "GPT-5 Nano (Ultra Fast)",
                # o Series (Reasoning)
                "o3": "o3 (Reasoning)",
                "o3-pro": "o3 Pro (Advanced Reasoning)",
                "o4-mini": "o4 Mini (Fast Reasoning)",
                # GPT-4.x Series (Production Stable)
                "gpt-4.1": "GPT-4.1 (Stable)",
                "gpt-4.1-mini": "GPT-4.1 Mini",
                "gpt-4o": "GPT-4o (Multimodal)",
                "gpt-4o-mini": "GPT-4o Mini (Balanced)",
                "custom": "Custom model name..."
            },
            "anthropic": {
                # Claude 4.5 Series (Latest)
                "claude-sonnet-4-5": "Claude Sonnet 4.5 (Latest)",
                "claude-opus-4-5": "Claude Opus 4.5 (Most Capable)",
                "claude-haiku-4-5": "Claude Haiku 4.5 (Fast)",
                # Claude 4.x Series (Stable)
                "claude-sonnet-4-20250514": "Claude Sonnet 4.0 (Stable)",
                "claude-opus-4-20250514": "Claude Opus 4.0 (Stable)",
                "claude-opus-4-1-20250805": "Claude Opus 4.1 (Enhanced)",
                # Claude 3.x Series (Legacy Compatible)
                "claude-3-7-sonnet-latest": "Claude Sonnet 3.7 (Latest 3.x)",
                "claude-3-5-haiku-latest": "Claude Haiku 3.5 (Latest)",
                "claude-3-opus-latest": "Claude Opus 3.0",
                "custom": "Custom model name..."
            },
            "google": {
                # Gemini 3 Series (Preview)
                "gemini-3-pro-preview": "Gemini 3 Pro (Preview)",
                "gemini-3-flash-preview": "Gemini 3 Flash (Preview)",
                # Gemini 2.5 Series (Current Flagship)
                "gemini-2.5-pro": "Gemini 2.5 Pro (Latest)",
                "gemini-2.5-flash": "Gemini 2.5 Flash (Fast)",
                "gemini-2.5-flash-lite-preview-06-2025": "Gemini 2.5 Flash Lite (Preview)",
                # Gemini 2.0 Series (Stable)
                "gemini-2.0-flash": "Gemini 2.0 Flash",
                "gemini-2.0-flash-lite": "Gemini 2.0 Flash Lite",
                "custom": "Custom model name..."
            },
            "ollama": {
                "ollama/llama3.3": "Llama 3.3 (Meta, 70B)",
                "ollama/llama3.2": "Llama 3.2 (Meta, 3B)",
                "ollama/llama3.1": "Llama 3.1 (Meta, 8B/70B)",
                "ollama/qwen2.5": "Qwen 2.5 (Alibaba, 7B/14B/32B)",
                "ollama/mistral": "Mistral 7B v0.3",
                "ollama/deepseek-coder-v2": "DeepSeek Coder V2 (16B/236B)",
                "ollama/gemma2": "Gemma 2 (Google, 9B/27B)",
                "ollama/phi4": "Phi-4 (Microsoft, 14B)",
                "custom": "Custom model name..."
            }
        }
        
        current_models = model_options[provider]
        
        # Quick select for main model
        st.markdown("**Quick Model Selection (applies to all tasks):**")
        quick_model_key = st.selectbox(
            "Primary Model",
            options=list(current_models.keys()),
            format_func=lambda x: current_models[x],
            index=0,
            help="Select a common model or choose 'Custom' to enter manually"
        )
        
        if quick_model_key == "custom":
            quick_model = st.text_input(
                "Enter custom model name",
                placeholder=f"e.g., {list(current_models.keys())[0]}",
                help="Enter the full model identifier for LiteLLM",
                value=project.aiSettings.modelExtraction
            )
        else:
            quick_model = quick_model_key
        
        st.divider()
        
        # Advanced model settings (collapsible)
        with st.expander("🔧 Advanced: Per-Task Model Settings"):
            st.caption("Override models for specific tasks. By default, all tasks use the Primary Model above.")
            
            # Use quick_model as default if it's set and valid
            default_extraction = quick_model if quick_model and quick_model != "custom" else project.aiSettings.modelExtraction
            default_ooc = quick_model if quick_model and quick_model != "custom" else project.aiSettings.modelOOC
            default_whatif = quick_model if quick_model and quick_model != "custom" else project.aiSettings.modelWhatIf
            
            extraction_key = st.selectbox(
                "Extraction Model (summaries, facts)",
                options=list(current_models.keys()),
                format_func=lambda x: current_models[x],
                index=list(current_models.keys()).index(default_extraction) if default_extraction in current_models else 0,
                key="extraction_select"
            )
            
            if extraction_key == "custom":
                model_extraction = st.text_input(
                    "Custom extraction model",
                    value=default_extraction if default_extraction not in current_models else ""
                )
            else:
                model_extraction = extraction_key
            
            ooc_key = st.selectbox(
                "OOC Detection Model",
                options=list(current_models.keys()),
                format_func=lambda x: current_models[x],
                index=list(current_models.keys()).index(default_ooc) if default_ooc in current_models else 0,
                key="ooc_select"
            )
            
            if ooc_key == "custom":
                model_ooc = st.text_input(
                    "Custom OOC model",
                    value=default_ooc if default_ooc not in current_models else ""
                )
            else:
                model_ooc = ooc_key
            
            whatif_key = st.selectbox(
                "What-If Model (future)",
                options=list(current_models.keys()),
                format_func=lambda x: current_models[x],
                index=list(current_models.keys()).index(default_whatif) if default_whatif in current_models else 0,
                key="whatif_select"
            )
            
            if whatif_key == "custom":
                model_whatif = st.text_input(
                    "Custom what-if model",
                    value=default_whatif if default_whatif not in current_models else ""
                )
            else:
                model_whatif = whatif_key
            
        submitted = st.form_submit_button(i18n.t('common.save'))
        
        if submitted:
            # Ensure we have valid model names
            if not quick_model or quick_model == "custom":
                st.error("Please enter a valid model name")
                st.stop()
            
            # Use quick_model for all tasks if custom inputs are empty or match quick_model
            final_extraction = model_extraction if model_extraction and model_extraction != "custom" else quick_model
            final_ooc = model_ooc if model_ooc and model_ooc != "custom" else quick_model
            final_whatif = model_whatif if model_whatif and model_whatif != "custom" else quick_model
            
            # Update settings
            new_settings = project.aiSettings.copy()
            new_settings.provider = provider
            new_settings.projectTokenLimit = project_limit
            new_settings.dailyTokenSoftLimit = daily_limit
            new_settings.modelExtraction = final_extraction
            new_settings.modelOOC = final_ooc
            new_settings.modelWhatIf = final_whatif
            
            # Save project
            project.aiSettings = new_settings
            project_service.save_project()
            
            st.success(f"✅ {i18n.t('settings.save_success')}")
            st.rerun()
    
    # Display current configuration
    st.divider()
    st.subheader("📋 Current Configuration")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Provider", project.aiSettings.provider.upper())
        st.caption(f"**Extraction:** `{project.aiSettings.modelExtraction}`")
        st.caption(f"**OOC Check:** `{project.aiSettings.modelOOC}`")
    with col2:
        st.metric("Project Tokens Used", f"{project.tokenStats.projectUsed:,} / {project.aiSettings.projectTokenLimit:,}")
        st.caption(f"**What-If:** `{project.aiSettings.modelWhatIf}`")
