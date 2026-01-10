# Developer Guide

> **Story Graph Assistant** - Technical documentation for contributors

**Version:** 1.7.1  
**Last Updated:** 2024

This guide provides comprehensive technical documentation for developers working on Story Graph Assistant. It covers system architecture, code organization, data flow, testing strategies, and guidelines for adding new features.

---

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [World Director System (v1.7.1)](#world-director-system-v171)
- [Data Flow & Pipelines](#data-flow--pipelines)
- [State Management](#state-management)
- [Testing Strategy](#testing-strategy)
- [Adding New Features](#adding-new-features)
- [Code Standards](#code-standards)

---

## Architecture Overview

**Local-first architecture** with Python backend and Streamlit frontend.

**Layers:**
```
┌─────────────────────────────────────────────────────┐
│                   Streamlit UI                      │
│  (app.py + ui/*)                                   │
│  - Director View (World Director interface)        │
│  - Characters View (Character editor)              │
│  - Routes View (Scene editor)                      │
│  - AI Tools View (LLM assistance)                  │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│                Service Layer                        │
│  - DirectorService (storylet selection v1.7.1)     │
│  - StateService (temporal state computation)        │
│  - ProjectService (project CRUD)                    │
│  - AIService (LLM integration)                      │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│                 Model Layer                         │
│  - Pydantic V2 models (validation + serialization) │
│  - Storylet, World, Effect, Condition               │
│  - Type safety and schema enforcement               │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│                Data Persistence                     │
│  - JSON files (project.json)                       │
│  - Repository pattern (base + json_repo)           │
│  - Local-first storage                              │
└─────────────────────────────────────────────────────┘
```

### Request Flow Example: Tick Forward

```
User clicks "▶️ Tick Forward" in director_view.py
    ↓
DirectorService.tick(scene_id, config)
    ↓
select_storylets() → 9-stage pipeline (v1.7.1)
    ├─ Stage 1: Precondition Filtering
    ├─ Stage 2: Ordering Constraints (v1.7.1)
    ├─ Stage 3: Cooldown & Once
    ├─ Stage 4: Fallback Check (v1.7.1)
    ├─ Stage 5: Diversity Penalty
    ├─ Stage 6: Pacing Adjustment
    ├─ Stage 7: Weighted Selection
    ├─ Stage 8: Effect Application
    └─ Stage 9: History Recording
    ↓
apply_effects() → New World State
    ↓
StateService.compute_diffs(old_state, new_state)
    ↓
Return TickRecord with storylets + diffs + rationale
    ↓
UI displays results in director_view.py
```

---

## Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Framework | Streamlit 1.30+ | Web UI framework |
| Language | Python 3.11+ | Core language |
| LLM | DeepSeek via LiteLLM | AI assistance |
| Storage | JSON | Project persistence |
| Validation | Pydantic 2.0 | Data validation + serialization |
| Testing | pytest | Unit and integration tests |

---

## Project Structure

```
src/
├── app.py                        # Streamlit app entry point
│
├── models/                       # Pydantic V2 data models
│   ├── __init__.py
│   ├── project.py               # Project container
│   ├── storylet.py              # World Director models (v1.7.1)
│   │   ├── Storylet            # Storylet definition
│   │   ├── DirectorConfig      # Selection config
│   │   ├── TickRecord          # Single tick result
│   │   └── TickHistory         # All ticks + tracking
│   ├── world.py                 # State and effects
│   │   ├── World               # Global state
│   │   ├── Effect              # State mutation
│   │   └── Condition           # Precondition check
│   ├── character.py             # Character data
│   ├── scene.py                 # Scene data
│   ├── event.py                 # Event data
│   └── ai.py                    # AI settings
│
├── services/                    # Business logic layer
│   ├── __init__.py
│   ├── director_service.py     # World Director orchestration
│   │   ├── DirectorService     # Main service class
│   │   ├── select_storylets()  # 9-stage selection pipeline (v1.7.1)
│   │   ├── apply_effects()     # Apply effects to state
│   │   ├── tick()              # Execute one tick
│   │   ├── _filter_by_ordering_constraints()  # v1.7.1
│   │   └── _select_fallback_candidates()      # v1.7.1
│   ├── state_service.py        # State computation
│   │   ├── compute_state()     # Temporal state computation
│   │   ├── compute_diffs()     # Before/after comparison
│   │   └── explain_condition() # Human-readable explanations
│   ├── conditions.py           # Condition evaluation
│   │   └── evaluate()          # Deterministic condition checking
│   ├── project_service.py      # Project CRUD operations
│   ├── scene_service.py        # Scene management
│   ├── character_service.py    # Character management
│   └── ai_service.py           # LLM integration
│
├── repositories/                # Data access layer
│   ├── __init__.py
│   ├── base.py                 # Abstract repository interface
│   └── json_repo.py            # JSON file backend implementation
│
├── ui/                          # Streamlit view components
│   ├── __init__.py
│   ├── layout.py               # Page structure and navigation
│   ├── sidebar.py              # Sidebar navigation
│   ├── director_view.py        # World Director UI (v1.7.1 updated)
│   ├── characters_view.py      # Character editor
│   ├── routes_view.py          # Scene editor
│   └── ai_tools_view.py        # AI assistant interface
│
└── infra/                       # Infrastructure layer
    ├── __init__.py
    ├── llm_client.py           # OpenAI/Claude client wrappers
    ├── token_stats.py          # LLM token usage tracking
    └── i18n.py                 # Internationalization (en/zh)
```

---

## World Director System (v1.7.1)

The World Director is the core dynamic narrative engine, responsible for selecting and triggering storylets based on preconditions, ordering constraints, pacing, and fallback mechanisms.

### Key Components

#### 1. Storylet Model

```python
class Storylet(BaseModel):
    """
    A narrative event that can be selected by the World Director.
    
    Attributes:
        id: Unique identifier (used in requires_fired, forbids_fired)
        title: Display name
        description: Full narrative content
        preconditions: List of conditions that must ALL be satisfied
        effects: List of state mutations to apply when triggered
        weight: Base selection probability (default: 1.0)
        once: If True, can only trigger once per playthrough
        cooldown: Minimum ticks before can trigger again
        intensity_delta: Change to narrative intensity (-1.0 to 1.0)
        tags: For diversity penalty and grouping
        
        # v1.7.1 NEW FIELDS:
        is_fallback: If True, only selected when idle threshold reached
        requires_fired: IDs of storylets that MUST have triggered first
        forbids_fired: IDs of storylets that must NOT have triggered
    """
    id: str
    title: str
    description: str = ""
    preconditions: List[Condition] = []
    effects: List[Effect] = []
    weight: float = 1.0
    once: bool = False
    cooldown: int = 0
    intensity_delta: float = 0.0
    tags: List[str] = []
    is_fallback: bool = False              # v1.7.1
    requires_fired: List[str] = []         # v1.7.1
    forbids_fired: List[str] = []          # v1.7.1
```

#### 2. DirectorConfig

```python
class DirectorConfig(BaseModel):
    """
    Configuration for World Director selection behavior.
    
    Attributes:
        events_per_tick: Number of storylets to select per tick
        diversity_penalty: Weight reduction for recently-used tags (0.0-1.0)
        diversity_window: Number of recent ticks to check for tag repetition
        pacing_scale: How strongly to adjust for intensity (0.0-1.0)
        
        # v1.7.1 NEW FIELD:
        fallback_after_idle_ticks: Trigger fallback after N empty ticks
    """
    events_per_tick: int = 2
    diversity_penalty: float = 0.5
    diversity_window: int = 3
    pacing_scale: float = 0.3
    fallback_after_idle_ticks: int = 3     # v1.7.1
```

#### 3. TickHistory (v1.7.1 Updated)

```python
class TickHistory(BaseModel):
    """
    Tracks all ticks and storylet triggering history.
    
    Attributes:
        records: All tick records in chronological order
        last_triggered: Mapping of storylet_id → last tick triggered
        triggered_once: Mapping of storylet_id → has ever triggered (for "once")
        
        # v1.7.1 NEW FIELD:
        idle_tick_count: Consecutive ticks with no regular storylets
    """
    records: List[TickRecord] = []
    last_triggered: Dict[str, int] = {}
    triggered_once: Dict[str, bool] = {}
    idle_tick_count: int = 0               # v1.7.1
```

---

## Data Flow & Pipelines

### World Director Pipeline (v1.7.1)

The `select_storylets()` method implements a 9-stage pipeline:

```python
def select_storylets(
    self,
    scene: Scene,
    current_state: World,
    config: DirectorConfig,
    history: TickHistory
) -> List[Tuple[Storylet, str]]:
    """
    Execute the 9-stage storylet selection pipeline.
    
    Returns: List of (Storylet, rationale) tuples
    """
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
