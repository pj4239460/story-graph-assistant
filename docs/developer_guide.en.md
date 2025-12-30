# Developer Guide

> **Story Graph Assistant** - Technical documentation for contributors

## Architecture

### Overview

**Local-first architecture** with Python backend and Streamlit frontend.

**Layers:**
```
UI Layer (Streamlit)
    ↓
Services (Business Logic)
    ↓
Repositories (Data Access)
    ↓
Infrastructure (LLM, DB, i18n)
```

### Tech Stack

| Component | Technology |
|-----------|-----------|
| Framework | Streamlit 1.30+ |
| Language | Python 3.10+ |
| LLM | DeepSeek via LiteLLM |
| Vector DB | FAISS (CPU-optimized) |
| Storage | JSON + SQLite |
| Validation | Pydantic 2.0 |
| Agent | LangGraph |

### Project Structure

```
src/
├── app.py              # Entry point
├── models/             # Pydantic data models
│   ├── project.py
│   ├── scene.py
│   └── character.py
├── repositories/       # Data persistence
│   ├── base.py
│   └── json_repo.py
├── services/           # Business logic
│   ├── project_service.py
│   ├── scene_service.py
│   ├── character_service.py
│   └── ai_service.py
├── infra/              # Infrastructure
│   ├── llm_client.py
│   ├── vector_db.py
│   ├── app_db.py       # SQLite wrapper
│   └── i18n.py
└── ui/                 # UI components
    ├── layout.py
    ├── sidebar.py
    ├── routes_view.py
    ├── scene_checkup_panel.py
    └── chat_view.py
```

## Data Models

### Core Entities

```python
# Project
class Project(BaseModel):
    id: str
    name: str
    locale: str
    scenes: Dict[str, Scene]
    characters: Dict[str, Character]
    aiSettings: AISettings
    tokenStats: TokenStats

# Scene
class Scene(BaseModel):
    id: str
    title: str
    body: str
    chapter: Optional[str]
    participants: List[str]  # Character IDs
    choices: List[Choice]
    isEnding: bool

# Character
class Character(BaseModel):
    id: str
    name: str
    description: str
    traits: List[str]
    goals: List[str]
    fears: List[str]
```

## Key Features Implementation

### 1. Scene Checkup Panel

**File:** `src/ui/scene_checkup_panel.py`

Implements caching for AI analysis:

```python
class SceneCheckup:
    def get_cache_key(self, project: Project, scene: Scene) -> str:
        # Cache based on content hash
        content_hash = hash(scene.body)
        return f"{project.name}_{scene.id}_{content_hash}"
    
    def run_checkup(self, project, scene, force_refresh=False):
        cache_key = self.get_cache_key(project, scene)
        
        if not force_refresh and cache_key in st.session_state.checkup_cache:
            return st.session_state.checkup_cache[cache_key]
        
        # Run AI analysis...
        result = {
            'summary': ...,
            'facts': ...,
            'emotions': ...,
            'metadata': ...
        }
        
        # Cache result
        st.session_state.checkup_cache[cache_key] = result
        return result
```

### 2. FAISS Vector Search

**File:** `src/infra/vector_db.py`

CPU-optimized semantic search:

```python
class VectorDatabase:
    def __init__(self):
        self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        self.indices = {}  # project_name -> index_dict
    
    def add_documents(self, project_name, doc_type, documents):
        embeddings = self.model.encode(texts)
        dimension = embeddings.shape[1]
        
        index = faiss.IndexFlatL2(dimension)
        index.add(embeddings)
        
        self.indices[project_name][doc_type] = {
            'index': index,
            'documents': documents
        }
    
    def search(self, project_name, query, top_k=5):
        query_embedding = self.model.encode([query])
        distances, indices = index.search(query_embedding, top_k)
        return results
```

### 3. LangGraph Agent

**File:** `src/services/ai_service.py`

Conversational agent with tool calling:

```python
from langgraph.prebuilt import create_react_agent

@tool
def search_scenes(query: str) -> str:
    """Search for scenes matching the query"""
    # Use vector DB to find relevant scenes
    results = vector_db.search(project_name, query)
    return json.dumps(results)

@tool
def count_characters() -> str:
    """Count total characters in the project"""
    return str(len(project.characters))

# Create agent
agent = create_react_agent(
    model=llm,
    tools=[search_scenes, count_characters, ...]
)
```

## Development Workflow

### Adding New Features

1. **Define Model** (if needed) in `src/models/`
2. **Create Service** in `src/services/`
3. **Build UI Component** in `src/ui/`
4. **Add i18n Keys** in `i18n/en.json` and `i18n/zh.json`
5. **Test** with sample project

### Adding AI Tools

Create a new `@tool` function in `src/services/ai_service.py`:

```python
@tool
def my_new_tool(param: str) -> str:
    """Description for the AI agent"""
    # Implementation
    return result
```

The agent will automatically discover and use it.

### Internationalization

Add translation keys to `i18n/*.json`:

```json
{
  "my_feature": {
    "title": "My Feature",
    "button": "Click Me"
  }
}
```

Use in code:

```python
i18n = st.session_state.i18n
st.button(i18n.t('my_feature.button'))
```

## Testing

### Manual Testing

1. Load sample project: Click 🇨🇳 or 🇺🇸 button
2. Test graph interaction: Drag nodes, click for details
3. Test Scene Checkup: Click node → AI Checkup tab
4. Test chat: Ask "How many characters?"
5. Test caching: Click Refresh button, verify speed

### Sample Projects

- `examples/sample_project/` - Chinese time travel story
- `examples/sample_project_en/` - English version

## Contributing

### Code Style

- Use type hints
- Follow PEP 8
- Add docstrings to public functions
- Keep functions under 50 lines

### Commit Messages

```
feat: add new feature
fix: bug fix
docs: documentation update
refactor: code refactoring
perf: performance improvement
```

### Pull Request Process

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'feat: add amazing feature'`
4. Push branch: `git push origin feature/amazing-feature`
5. Open Pull Request

## Roadmap

### Current (v0.3)
- ✅ Interactive graph with drag-and-drop
- ✅ Scene Checkup panel
- ✅ Sample projects (CN/EN)
- ✅ FAISS vector search
- ✅ Chat history

### Next (v0.4)
- [ ] Play Path feature (test player routes)
- [ ] Timeline view
- [ ] Multi-scene consistency checks
- [ ] Export to Twine/Articy format

### Future (v1.0)
- [ ] Character arc analysis
- [ ] Emotional pacing visualization
- [ ] What-if simulation
- [ ] Collaborative editing

## Resources

- **Streamlit Docs**: https://docs.streamlit.io
- **LangGraph**: https://langchain-ai.github.io/langgraph
- **FAISS**: https://github.com/facebookresearch/faiss
- **DeepSeek API**: https://platform.deepseek.com/docs

---

**Questions?** Open an issue at [github.com/pj4239460/story-graph-assistant](https://github.com/pj4239460/story-graph-assistant)
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
