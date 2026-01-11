# Getting Started Guide

## Installation

### Prerequisites
- Python 3.10+
- LLM API Key (supports multiple providers)
  - DeepSeek: [Get free key](https://platform.deepseek.com/)
  - OpenAI: [API Keys](https://platform.openai.com/api-keys)
  - Anthropic Claude: [Console](https://console.anthropic.com/)
  - Google Gemini: [AI Studio](https://aistudio.google.com/)
  - Or use local models (Ollama, LM Studio, etc.)

### Setup

```bash
# 1. Clone repository
git clone https://github.com/pj4239460/story-graph-assistant.git
cd story-graph-assistant

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure API key
cp .env.example .env
# Edit .env and set:
# DeepSeek: DEEPSEEK_API_KEY=sk-...
# OpenAI: OPENAI_API_KEY=sk-...
# Anthropic: ANTHROPIC_API_KEY=sk-ant-...
# Google: GEMINI_API_KEY=...
# Local models: No key needed, use ollama/model-name

# 5. Run application
streamlit run src/app.py
```

Browser will open at `http://localhost:8501`

## First Steps

### 1. Try Sample Projects

Click the sample buttons in sidebar:
- 🇨🇳 **中文** - Chinese time travel story
- 🇺🇸 **EN** - English time travel story

This loads a complete example with 3 scenes, 2 characters, and branching choices.

### 2. Explore the Interface

**Tabs:**
- **📍 Routes** - Interactive story graph
- **👤 Characters** - Character profiles
- **🔧 AI Tools** - Scene analysis tools
- **💬 Chat** - Ask AI about your story
- **⚙️ Settings** - Configure AI models and limits

### 3. View Scene Details

Click any node in the graph to see:
- **Content** - Scene text and choices
- **AI Checkup** - Comprehensive analysis with emotions, facts, and quality insights
- **Metadata** - Technical details

### 4. Create Your Own Project

1. Click **➕ New** in sidebar
2. Enter project name and choose language
3. Add your first scene
4. Build story by adding choices and connecting scenes

### 5. Try World Director (NEW! v0.5)

Experience emergent narratives with the World Director system:

1. Load the **"Town of Riverhaven"** example (coming soon) or create a project with storylets
2. Navigate to **🎬 World Director** tab
3. Create a story thread (or select existing one)
4. Configure Director settings:
   - **Events/Tick**: How many storylets to trigger (1-5)
   - **Pacing**: Calm/Balanced/Intense
   - **Diversity**: How much to avoid repetition (0-100%)
5. Click **▶️ Run Tick** to evolve the world
6. Review results:
   - See which storylets were selected and why
   - View applied effects and state changes
   - Explore intensity metrics
7. Run multiple ticks to see emergent story development

**What makes World Director different?**
- **No Manual Branching**: Define storylets (conditions + effects), let the system combine them
- **Deterministic**: Same state + config = same result (fully reproducible)
- **Explainable**: Every decision has human-readable rationale
- **Replayable**: Complete history with state diffs at each tick

## Key Features

### Full Editing Support ✅

**Scene Editing:**
- Click ✏️ button next to any scene to open edit form
- Edit: title, content, chapter, summary, time label, ending status
- Changes automatically update graph visualization

**Character Editing:**
- Click ✏️ button next to any character to open edit form
- Edit: name, alias, description, traits, goals, fears
- Traits/goals/fears support multi-line input (one per line)

**Choice/Branch Editing:**
- Each choice in scene details has an ✏️ button
- Edit choice text and target scene
- Add new choices or delete existing ones
- Target scene supports dropdown selection or "None (Ending)"

### Scene Checkup Panel

AI-powered analysis includes:
- **Summary** - Concise scene overview
- **Facts** - Extracted world-building information
- **Emotions** - Detected emotional tones
- **OOC Risk** - Character consistency warnings (coming soon)

Results are cached for performance. Click 🔄 Refresh to regenerate.

### AI Chat Assistant

Powered by LiteLLM with multi-model support. Natural language queries:
- "How many characters are in the story?"
- "Who is mentioned in scene-001?"
- "How many endings does the story have?"

Uses FAISS semantic search for accurate retrieval.

**Supported LLM Providers (as of 2025-12-31):**
- 🚀 **DeepSeek** - Best value for money, recommended
  - `deepseek-chat` (Chat)
  - `deepseek-reasoner` (Reasoning)
- 🧠 **OpenAI** - Latest GPT series
  - GPT-5 series: `gpt-5.2`, `gpt-5.2-pro`, `gpt-5-mini`
  - o reasoning: `o3`, `o3-pro`, `o4-mini`
  - GPT-4.x: `gpt-4.1`, `gpt-4o`, `gpt-4o-mini`
- 🤖 **Anthropic** - Claude 4.5 latest series
  - Claude 4.5: `claude-sonnet-4-5`, `claude-opus-4-5`, `claude-haiku-4-5`
  - Claude 3.x: `claude-3-7-sonnet-latest`, `claude-3-5-haiku-latest`
- 🌎 **Google** - Gemini 2.5/3.0 series
  - Gemini 3: `gemini-3-pro-preview`, `gemini-3-flash-preview`
  - Gemini 2.5: `gemini-2.5-pro`, `gemini-2.5-flash`
  - Gemini 2.0: `gemini-2.0-flash`
- 💻 **Local Models** - Latest Ollama versions
  - Llama: `ollama/llama3.3`, `ollama/llama3.2`
  - Qwen: `ollama/qwen2.5`
  - Others: `ollama/mistral`, `ollama/deepseek-coder-v2`, `ollama/gemma2`, `ollama/phi4`

**Configuration Examples:**
```bash
# .env file
# Use DeepSeek (recommended)
DEEPSEEK_API_KEY=sk-...

# Or use OpenAI GPT-5
OPENAI_API_KEY=sk-...
# Select model in settings: gpt-5.2 / gpt-5-mini / o3

# Or use Claude 4.5
ANTHROPIC_API_KEY=sk-ant-...
# Select in settings: claude-sonnet-4-5 / claude-opus-4-5

# Or use Gemini 2.5/3.0
GEMINI_API_KEY=AIza...
# Select in settings: gemini-2.5-pro / gemini-3-flash-preview

# Or use local Ollama (no API key needed)
# 1. Install Ollama: https://ollama.ai/
# 2. Pull model: ollama pull llama3.3
# 3. Select in settings: ollama/llama3.3
```

In the app's ⚙️ Settings tab, you can select different models. LiteLLM automatically recognizes the model format and routes to the appropriate provider.

### Project Management

- **Recent Projects** - Quick access to recent files
- **JSON Storage** - Simple, portable, version-control friendly
- **Auto-save** - Changes saved automatically

## Tips

1. **Use Tags** - Organize scenes with tags like "combat", "romance", "clue"
2. **Character IDs** - Use consistent IDs (char-001, char-002) for tracking
3. **Chapter Names** - Group scenes into chapters for better organization
4. **Token Limits** - Monitor usage in Settings tab to avoid overages
5. **Export Analysis** - Download Scene Checkup reports as JSON

## Troubleshooting

**API Key Issues**
- Verify `.env` file exists in project root
- Check key format:
  - DeepSeek: `DEEPSEEK_API_KEY=sk-...`
  - OpenAI: `OPENAI_API_KEY=sk-...`
  - Anthropic: `ANTHROPIC_API_KEY=sk-ant-...`
  - Google: `GEMINI_API_KEY=...`
- Restart application after editing `.env`

**Local Model Configuration**
- Using Ollama: Install [Ollama](https://ollama.ai/) first, then run `ollama pull llama3`
- Change model in settings to `ollama/llama3` or `ollama/qwen`
- LM Studio/vLLM: Set up OpenAI-compatible mode, use `openai/model-name`

**FAISS Not Working**
- Application works without FAISS (falls back to keyword search)
- Install: `pip install faiss-cpu`

**Slow Performance**
- Scene Checkup uses caching - first run is slow, subsequent views are instant
- Clear cache by clicking 🔄 Refresh button

## Next Steps

- Read [Developer Guide](docs/developer_guide.en.md) for architecture details
- Explore AI tools in the AI Tools tab
- Join discussions on GitHub Issues

---

**Need Help?** Open an issue at [github.com/pj4239460/story-graph-assistant](https://github.com/pj4239460/story-graph-assistant)

---

## 📖 User Guide

### First Time Use

1. **Create a Project**
   - Click "➕ New" in the sidebar
   - Enter project name (e.g., "My First Story")
   - Select language (Chinese/English)
   - Click "Create"

2. **Add Scenes**
   - Switch to "📊 Story Routes" tab
   - Click "➕ New Scene"
   - Enter scene title and content
   - Save

3. **Create Characters**
   - Switch to "👥 Characters" tab
   - Click "➕ New Character"
   - Fill in character information
   - Save

4. **Use AI Tools**
   - Switch to "🤖 AI Tools" tab
   - Select a tool (Scene Summary/Lore Extraction/OOC Detection)
   - Select scene or character
   - Click "🚀 Generate/Detect"

5. **Configure Settings**
   - Switch to "⚙️ Settings" tab
   - Adjust **Project Token Limit** (Total budget)
   - Adjust **Daily Soft Limit** (Warning threshold)
   - View Model Configuration

### 💡 Layout Tips

- **Tree Layout**: Best for standard branching stories. It organizes scenes hierarchically from the start.
- **Manual Layout**: Resets nodes to a grid. Use this if the graph gets messy or if you want to arrange everything yourself.
- **Force Layout**: Good for seeing clusters and organic connections, but can be unstable with many nodes.

### Load Sample Project

```bash
# In the app, click "📂 Load"
# Enter path:
./examples/sample_project/project.json
```

Sample project includes:
- 3 scenes (time travel theme)
- 2 characters (Li Ming, Professor Smith)
- Complete story opening

---

## 🏗️ Project Structure

```
story_graph_assistant/
├── src/
│   ├── app.py                  # Streamlit main entry
│   ├── models/                 # Data models
│   │   ├── project.py          # Project model
│   │   ├── scene.py            # Scene model
│   │   ├── character.py        # Character model
│   │   ├── event.py            # Event model
│   │   ├── world.py            # World state (v2)
│   │   └── ai.py               # AI configuration
│   ├── repositories/           # Storage layer
│   │   ├── base.py             # Base interface
│   │   └── json_repo.py        # JSON implementation
│   ├── services/               # Business logic
│   │   ├── project_service.py  # Project management
│   │   ├── scene_service.py    # Scene management
│   │   ├── character_service.py# Character management
│   │   └── ai_service.py       # AI features
│   ├── infra/                  # Infrastructure
│   │   ├── llm_client.py       # LLM client
│   │   ├── token_stats.py      # Token statistics
│   │   └── i18n.py             # Internationalization
│   └── ui/                     # UI components
│       ├── layout.py           # Main layout
│       ├── sidebar.py          # Sidebar
│       ├── routes_view.py      # Routes view
│       ├── characters_view.py  # Characters view
│       └── ai_tools_view.py    # AI tools view
├── i18n/                       # Translation files
│   ├── zh.json                 # Chinese
│   └── en.json                 # English
├── examples/                   # Sample projects
│   └── sample_project/
│       └── project.json
├── docs/                       # Documentation
│   └── developer_guide.en.md
├── requirements.txt            # Python dependencies
├── .env.example                # Environment template
└── README.md                   # Project overview
```

---

## 🎮 Feature Demos

### Scene Summarization
- Automatically generates concise summaries for long scenes
- Helps quickly understand scene content
- Saves to scene object

### Lore Extraction
- Extracts key information from scene text
- Automatically categorizes: character traits, worldbuilding, plot points
- Used to build knowledge base (v2 will support RAG retrieval)

### OOC Detection
- Checks character behavior in scenes against character profiles
- AI analyzes consistency with character traits
- Provides detailed explanations and suggestions

## 🎬 World Director Guide

### Understanding the System

The **World Director** is a fundamentally different approach to narrative design:

**Traditional Approach:**
- Manually author every story branch
- Exponential complexity (100 scenes → 10,000 branches)
- Difficult to maintain consistency

**World Director Approach:**
- Define storylets (narrative fragments with conditions)
- System automatically combines them based on state
- Linear effort (100 storylets → infinite combinations)

### ✏️ Storylet Editor (NEW! v0.8)

The **Storylet Editor** provides a user-friendly visual interface for creating and managing storylets without manually editing JSON files.

**Accessing the Editor:**
1. Open your project
2. Navigate to **✏️ Storylets** tab
3. You'll see two sub-tabs:
   - **📚 Library** - Browse and manage existing storylets
   - **➕ Create New** - Build new storylets with forms

**Using the Library:**
- **Search**: Type keywords to find storylets by title, ID, or tags
- **Filters**: Quick filter by type
  - `All` - Show all storylets
  - `Fallback` - Only backup storylets
  - `Once` - One-time storylets
  - `Has Cooldown` - Storylets with cooldown timers
  - `Has Ordering` - Storylets with sequence dependencies
- **Cards**: Each storylet displays as an expandable card showing:
  - Property badges (Fallback, Once, Cooldown, Tags)
  - Metrics (Weight, Intensity Delta, Conditions, Effects)
  - Ordering constraints (requires_fired, forbids_fired)
  - Detailed conditions and effects
- **Actions**:
  - `✏️ Edit` - Load storylet into form for modification
  - `🗑️ Delete` - Remove storylet (requires confirmation)

**Creating/Editing Storylets:**

The creation form is organized into sections:

1. **Basic Information**
   - `ID` (required, immutable when editing) - Unique identifier
   - `Title` (required) - Display name
   - `Description` - What happens in this storylet

2. **Properties**
   - `Weight` (0.0-10.0) - Selection probability when conditions met
   - `Intensity Δ` (-1.0 to +1.0) - Change to narrative tension
   - `Cooldown` (0-20 ticks) - Minimum time before retriggering
   - `Once` checkbox - Can only trigger once per playthrough
   - `Fallback` checkbox - Triggers when world is stuck (no regular storylets qualify)
   - `Tags` - Comma-separated labels for filtering

3. **Ordering Constraints (v0.7)**
   - `Requires Fired` - Comma-separated storylet IDs that must fire first
     - Example: `intro_01, setup_02` means this storylet needs those two to fire first
   - `Forbids Fired` - Storylet IDs that block this storylet if they've fired
     - Example: `bad_end_01` means this can't fire if that ending has triggered
   - Use for quest chains and narrative dependencies

4. **Preconditions** (Dynamic list)
   - Click `➕ Add Condition` to add each condition
   - Each condition specifies:
     - `Scope`: `world` | `character` | `relationship`
     - `Target`: Entity ID (character name, "world", etc.)
     - `Path`: Nested property path (e.g., "vars.gold", "attributes.strength")
     - `Op`: Comparison operator (`==`, `!=`, `>`, `<`, `>=`, `<=`)
     - `Value`: Numeric value to compare against
   - ALL conditions must be met for storylet to be selectable
   - Click `🗑️ Remove` to delete a condition

5. **Effects** (Dynamic list)
   - Click `➕ Add Effect` to add each effect
   - Each effect specifies:
     - `Scope`: `world` | `character` | `relationship`
     - `Target`: Entity ID to modify
     - `Path`: Property path to modify
     - `Op`: Mutation operation
       - `set` - Replace value
       - `add` - Add to existing value
       - `multiply` - Multiply existing value
     - `Value`: Value to apply
   - All effects are applied atomically when storylet triggers
   - Click `🗑️ Remove` to delete an effect

**Form Actions:**
- `💾 Save Storylet` - Create/update storylet and save project
- `🔄 Reset Form` - Clear all fields
- `📋 Duplicate` - Keep form data but clear ID for copying

**Tips:**
- Use meaningful IDs (e.g., `market_boom_01`, `quest_dragon_accept`)
- Tag storylets by type (`combat`, `economic`, `relationship`) for filtering
- Test preconditions carefully - storylets won't appear if conditions don't match
- Use fallback storylets to prevent "world stuck" scenarios
- Ordering constraints are powerful for quest chains and story sequences

### Core Concepts

**1. Storylets**
A storylet is a reusable narrative unit:
```json
{
  "id": "st-trade-boom",
  "title": "Trade Boom",
  "description": "Merchant faction gains economic power",
  "tags": ["economic", "positive"],
  "preconditions": [
    {"path": "world.vars.market_peace", "op": ">=", "value": 60}
  ],
  "effects": [
    {
      "scope": "world",
      "target": "world",
      "op": "add",
      "path": "vars.merchants_power",
      "value": 10,
      "reason": "Successful trade increases merchant influence"
    }
  ],
  "weight": 0.4,
  "cooldown": 3,
  "intensity_delta": 0.2
}
```

**2. Preconditions**
Conditions that must be met for a storylet to trigger:
- `world.vars.<key>` - World state variables
- `characters.<id>.<field>` - Character properties
- `relationships.<a|b>.<field>` - Relationship values

Supported operators:
- Comparison: `==`, `!=`, `<`, `<=`, `>`, `>=`
- Membership: `in`, `contains`

**3. Effects**
Changes applied when a storylet triggers:
- `scope`: "world", "character", "relationship"
- `op`: "set", "add", "remove"
- `path`: Dot-notation to the value
- `value`: New value or delta

**4. Director Policy**
Configuration for selection behavior:
- **events_per_tick**: How many storylets to select (1-5)
- **diversity_penalty**: Reduce weight for recently-used tags (0-100%)
- **pacing_preference**: "calm", "balanced", or "intense"
- **intensity control**: Min/max bounds, decay rate

### Selection Pipeline

The Director uses a multi-stage process:

1. **Precondition Filtering**
   - Check all storylets' conditions against current state
   - Keep only those where ALL conditions are satisfied

2. **Ordering Constraints** *(v0.7 NEW!)*
   - **requires_fired**: Storylet only triggers AFTER specified storylets have fired
   - **forbids_fired**: Storylet only triggers if specified storylets have NOT fired
   - Use for: Quest chains, mutually exclusive paths, narrative dependencies

3. **Cooldown/Once Filtering**
   - Remove storylets still on cooldown
   - Remove "once" storylets that already triggered

4. **Fallback Check** *(v0.7 NEW!)*
   - If no regular storylets qualify, check idle tick count
   - After N consecutive idle ticks, trigger fallback storylets
   - Fallback storylets are ambient events that keep world alive

5. **Diversity Penalty**
   - Check recent ticks for tag repetition
   - Reduce weight: `weight *= (1 - penalty) ^ repetitions`

6. **Pacing Adjustment**
   - If intensity too high, favor calming storylets (negative delta)
   - If intensity too low, favor escalating storylets (positive delta)

7. **Weighted Selection**
   - Normalize weights to probabilities
   - Select N storylets without replacement
   - Record rationale for each

8. **Effect Application**
   - Apply all selected storylets' effects
   - Compute state diff (before/after comparison)
   - Update intensity based on deltas
   - Reset idle counter if regular storylet triggered

### Best Practices

**Storylet Design:**
- Use clear, descriptive titles
- Add tags for diversity tracking
- Set appropriate weights (0.1 = rare, 10.0 = very common)
- Use cooldowns to prevent repetition
- Balance intensity_delta across storylets
- Mark ambient events as fallback (is_fallback=true)
- Use ordering constraints for quest chains

**Precondition Tips:**
- Start with simple conditions
- Use ranges rather than exact values: `>= 60` not `== 65`
- Combine multiple conditions for specificity
- Test edge cases (what if value is 0?)

**Pacing Control:**
- Higher diversity_penalty = more variety
- Lower intensity_decay = longer intense/calm periods
- "balanced" pacing works well for most stories
- Monitor intensity in tick history
- Set fallback_after_idle_ticks=3 to prevent stuck worlds

**Ordering Constraints (v0.7):**
- Use `requires_fired` for quest sequences:
  - Example: "Quest Complete" requires ["Quest Start", "Quest Progress"]
- Use `forbids_fired` for mutually exclusive paths:
  - Example: "Peaceful Path" forbids ["Violent Path"]
- Combine both for complex branching:
  - "Secret Ending" requires ["Clue 1", "Clue 2"] and forbids ["Bad Choice"]

**Fallback Storylets (v0.7):**
- Mark with `is_fallback: true`
- Use for ambient events: weather, crowd activity, time passage
- Don't require specific state conditions
- Keep intensity_delta near 0 (neutral pacing)
- Add variety with different cooldowns

### Example: Faction Politics

See `examples/town_factions/project.json` for a complete example:
- 3 competing factions (Merchants, Assembly, Guard)
- 20 storylets covering economic, political, and conflict events
- Dynamic power balance based on state changes
- Emergent narratives from simple rules

Try running 10+ ticks and observe:
- Factions rise and fall based on events
- Different runs produce different stories
- Each tick has clear rationale

---

## 🔧 Troubleshooting

### Issue: Cannot install litellm

```powershell
pip install --upgrade pip
pip install litellm
```

### Issue: Streamlit fails to start

```powershell
# Check Python version
python --version  # Should be >= 3.10

# Reinstall streamlit
pip install --upgrade streamlit
```

### Issue: AI features return errors

1. Check if API Key in `.env` file is correct
2. Verify API Key has sufficient credits
3. Check network connection

---

## 📋 Next Development Steps

### v0.2 - Enhanced Features ✅
- [x] Scene editing functionality (title, content, chapter, summary, time label, ending status)
- [x] Character editing functionality (name, alias, description, traits, goals, fears)
- [x] Choice/connection editing (add, edit, delete scene branches)
- [ ] Export features (Markdown/HTML)

### v0.3 - RAG Foundation
- [ ] Timeline view
- [ ] Keyword-based retrieval
- [ ] Worldbuilding Q&A
- [ ] Multi-scene OOC checking

---

## 💡 Usage Tips

1. **Save Regularly**: Use "💾 Save Project" to avoid data loss
2. **Start Small**: Begin with simple story structures, gradually expand
3. **Leverage AI**: Generate summaries and extract lore for important scenes
4. **Token Management**: Monitor token usage, use AI features wisely
5. **Backup Projects**: JSON files can be directly copied for backup

---

## 🤝 Feedback & Contribution

For issues or suggestions, please:
- Submit an Issue
- Create a Pull Request
- Contact the developer

---

**Happy creating! 🎉**
