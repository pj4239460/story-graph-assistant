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
