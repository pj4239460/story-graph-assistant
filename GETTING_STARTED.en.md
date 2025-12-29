# Story Graph Assistant - Getting Started

## 🎯 MVP v0.1 Complete!

Based on the developer documentation, MVP version has been built with the following features:

### ✅ Implemented Features

1. **Project Management**
   - Create, load, save projects
   - JSON format storage

2. **Scene Management**
   - Create, edit, delete scenes
   - Scene content editing
   - Branch choice management
   - **Interactive flow diagram** with Streamlit Flow
   - Multiple layouts: Tree, Layered, Force, Manual
   - Drag-and-drop repositioning
   - Statistics dashboard

3. **Character Management**
   - Create, edit, delete characters
   - Character profiles (description, personality, goals, fears)
   - Relationship management

4. **AI Tools**
   - Scene summarization
   - Worldbuilding lore extraction
   - Out-of-Character (OOC) detection

5. **Token Statistics**
   - Project total usage tracking
   - Daily usage statistics
   - Usage by feature

6. **Internationalization**
   - Chinese/English UI (infrastructure ready)

---

## 🚀 Quick Start

### 1. Install Dependencies

```powershell
# Navigate to project root
cd d:\Workspace\game_projects\story_graph_assistant

# Create virtual environment (recommended)
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure API Key

```powershell
# Copy configuration template
copy .env.example .env

# Edit .env file and add your DeepSeek API Key
# DEEPSEEK_API_KEY=sk-your_key_here
```

If you don't have a DeepSeek API Key:
- Visit https://platform.deepseek.com/
- Register and get an API Key
- DeepSeek offers very competitive pricing (much lower than OpenAI)

### 3. Run Application

```powershell
streamlit run src/app.py
```

The application will automatically open in your browser at: `http://localhost:8501`

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

### 💡 Layout Tips

- **Tree Layout**: Best for standard branching stories. It organizes scenes hierarchically from the start.
- **Manual Layout**: Resets nodes to a grid. Use this if the graph gets messy or if you want to arrange everything yourself.
- **Force Layout**: Good for seeing clusters and organic connections, but can be unstable with many nodes.

### Load Sample Project

```powershell
# In the app, click "📂 Load"
# Enter path:
d:\Workspace\game_projects\story_graph_assistant\examples\sample_project\project.json
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

### v0.2 - Enhanced Features
- [ ] Scene editing functionality
- [ ] Character editing functionality
- [ ] Visual editing for scene connections
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
