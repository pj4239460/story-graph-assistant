# AI Narrative / Worldbuilding Assistant – Developer Guide

> Version: v0.1 MVP  
> Project: Story Graph Assistant

---

## Table of Contents

1. [Product & Features](#product--features)
2. [Technical Implementation](#technical-implementation)
3. [Quick Start](#quick-start)
4. [Development Roadmap](#development-roadmap)

---

## Product & Features

### Product Positioning

**One-Sentence Pitch**

> A narrative & worldbuilding management tool with AI analysis assistant  
> for story-driven games, visual novels, and branching narratives.

It combines:

- **Twine**-like visual story node/flow graph for structure design
- **Arcweave**-style component management (characters/items/locations) for worldbuilding
- **RAG + LLM** "story brain" layer for:
  - Lore extraction
  - Out-of-Character (OOC) detection
  - Route and worldbuilding consistency analysis
  - What-if simulations

### Target Users

- Indie game developers, Galgame/AVG writers
- RPG / TRPG worldbuilding designers
- Narrative designers working on complex, multi-branch stories

### Core Value

1. **Visible Story Structure**: Manage complex plots with route maps and timelines
2. **Organized Worldbuilding Database**: Extract and retrieve lore from dialogues
3. **Consistent Characters & Timelines**: Character life arcs + timeline views
4. **AI-Powered Validation & Inspiration**: OOC detection, worldbuilding QA, route analysis, what-if simulations

---

## Technical Implementation

### Architecture Overview

- **Architecture Style**: Local-first / standalone application
  - Python backend + Streamlit frontend, ready to use
- **Layers**:
  - UI (Streamlit)
  - Services (Project/Scene/Character/AI)
  - Repositories (project storage)
  - Infra (LLM, token stats, i18n)

### Tech Stack

- **Language**: Python 3.10+
- **UI**: Streamlit
- **LLM Integration**:
  - DeepSeek API (`https://api.deepseek.com`)
  - LiteLLM as unified calling layer
- **Storage**:
  - v0/v1: JSON file format
  - v2+: Optional SQLite
- **RAG**:
  - v0: Keyword-based pseudo-RAG
  - v1+: Vector store (FAISS/Chroma) + embedding models

### Data Models

Core entities:

- `Project` - Project/workspace
- `Scene` - Scene/node
- `Choice` - Choice/branch
- `Character` - Character
- `Event` - Event (timeline)
- `WorldState` - World state (v2)
- `StoryThread` - Story thread (v2)
- `AISettings` - AI configuration
- `TokenStats` - Token usage statistics

### Project Structure

```
story_graph_assistant/
├── src/
│   ├── app.py              # Streamlit entry point
│   ├── models/             # Data models
│   ├── repositories/       # Storage layer
│   ├── services/           # Business logic
│   ├── infra/              # Infrastructure (LLM, i18n)
│   └── ui/                 # UI components
├── i18n/                   # Internationalization
├── examples/               # Sample projects
├── docs/                   # Documentation
├── requirements.txt
├── .env.example
└── README.md
```

---

## Quick Start

### 1. Install Dependencies

```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy configuration template
cp .env.example .env

# Edit .env file and add your DeepSeek API Key
# DEEPSEEK_API_KEY=your_api_key_here
```

### 3. Run Application

```bash
streamlit run src/app.py
```

Application will start at `http://localhost:8501`.

### 4. Create Your First Project

1. Click "➕ New" in the sidebar
2. Enter project name and click "Create"
3. Add scenes in "📊 Story Routes" tab
4. Create characters in "👥 Characters" tab
5. Use AI features in "🤖 AI Tools" tab

---

## MVP Feature List (v0.1)

### ✅ Implemented

- [x] Project creation, loading, saving
- [x] Scene management (CRUD)
- [x] Character management (CRUD)
- [x] AI scene summarization
- [x] AI lore extraction
- [x] AI OOC detection
- [x] Token usage tracking

### 🚧 Planned

- [ ] Scene connection/branch management
- [ ] Graph visualization (Graphviz/D3.js)
- [ ] Timeline view
- [ ] RAG knowledge base
- [ ] What-if simulations
- [ ] Export features

---

## Development Roadmap

### v0.1 - MVP (Current Version)
- ✅ Basic project management
- ✅ Scene and character CRUD
- ✅ Single-scene AI features
- ✅ Token statistics

### v0.3 - RAG Foundation
- [ ] Timeline view
- [ ] Keyword-based retrieval
- [ ] Worldbuilding Q&A
- [ ] Multi-scene OOC checking

### v1.0 - Full RAG
- [ ] Vector retrieval (FAISS/Chroma)
- [ ] Character life arcs
- [ ] Route analysis
- [ ] Emotional pacing

### v2.0 - World Simulation
- [ ] WorldState & StoryThread
- [ ] Advanced what-if simulations
- [ ] Project consistency reports
- [ ] Cost modes

---

## API Documentation

### Services

#### ProjectService

```python
# Create project
project = project_service.create_project(name="My Story", locale="en")

# Load project
project = project_service.load_project("path/to/project.json")

# Save project
project_service.save_project("path/to/project.json")
```

#### SceneService

```python
# Create scene
scene = scene_service.create_scene(
    project, 
    title="Opening", 
    body="The story begins...",
    chapter="Chapter 1"
)

# Add choice
choice = scene_service.add_choice(
    project,
    scene.id,
    text="Choice A",
    target_scene_id=another_scene.id
)
```

#### AIService

```python
# Scene summarization
summary = ai_service.summarize_scene(project, scene)

# Lore extraction
facts = ai_service.extract_facts(project, scene)

# OOC detection
result = ai_service.check_ooc(project, character_id, scene)
```

---

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the project
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## License

MIT License

---

## Contact

- GitHub: [yourusername/story-graph-assistant](https://github.com/yourusername/story-graph-assistant)
- Issues: [Report a bug](https://github.com/yourusername/story-graph-assistant/issues)

---

**Slogan**: *"Visual AI assistant for branching game stories."*
