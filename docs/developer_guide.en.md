# Developer Guide

> **Story Graph Assistant** - Technical documentation for contributors

**Version:** 0.9  
**Last Updated:** January 13, 2026

This guide provides comprehensive technical documentation for developers working on Story Graph Assistant. It covers system architecture, code organization, data flow, testing strategies, and guidelines for adding new features.

---

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [World Director System](#world-director-system)
- [AI-Enhanced Director (v0.9)](#ai-enhanced-director-v09)
- [Data Flow & Pipelines](#data-flow--pipelines)
- [Key Features Implementation](#key-features-implementation)
- [Development Workflow](#development-workflow)
- [Testing](#testing)
- [Contributing](#contributing)
- [Resources](#resources)

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
│  - DirectorService (storylet selection v0.9)     │
│  - AIConditionsEvaluator (NL condition eval v0.9)│
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
select_storylets() → 9-stage pipeline (v0.9)
    ├─ Stage 1: Precondition Filtering (v0.9: AI-powered NL conditions)
    ├─ Stage 2: Ordering Constraints (v0.7)
    ├─ Stage 3: Cooldown & Once
    ├─ Stage 4: Fallback Check (v0.7)
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
│   ├── storylet.py              # World Director models (v0.7)
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
│   │   ├── select_storylets()  # 9-stage selection pipeline (v0.9 enhanced)
│   │   ├── apply_effects()     # Apply effects to state
│   │   ├── tick()              # Execute one tick
│   │   ├── _filter_by_ordering_constraints()  # v0.7
│   │   └── _select_fallback_candidates()      # v0.7
│   ├── ai_conditions.py        # AI condition evaluation (v0.9 NEW)
│   │   └── AIConditionsEvaluator  # Natural language condition evaluation
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
│   ├── director_view.py        # World Director UI (v0.7 updated)
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

## World Director System

**Core Feature** (v0.7) with **AI Enhancement** (v0.9)

The World Director is the core dynamic narrative engine, responsible for selecting and triggering storylets based on preconditions, ordering constraints, pacing, and fallback mechanisms.

**v0.9 adds:** Natural language conditions, three director modes, and AI-powered condition evaluation alongside traditional rule-based logic.

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
        preconditions: List of conditions (v0.9: supports NL conditions)
        effects: List of state mutations to apply when triggered
        weight: Base selection probability (default: 0.3)
        once: If True, can only trigger once per playthrough
        cooldown: Minimum ticks before can trigger again
        intensity_delta: Change to narrative intensity (-0.3 to 0.3)
        tags: For diversity penalty and grouping
        
        # v0.7 NEW FIELDS:
        is_fallback: If True, only selected when idle threshold reached
        requires_fired: IDs of storylets that MUST have triggered first
        forbids_fired: IDs of storylets that must NOT have triggered
    """
    id: str
    title: str
    description: str = ""
    preconditions: List[Precondition] = []  # v0.9: can contain nl_condition
    effects: List[Effect] = []
    weight: float = 0.3
    once: bool = False
    cooldown: int = 0
    intensity_delta: float = 0.0
    tags: List[str] = []
    is_fallback: bool = False              # v0.7
    requires_fired: List[str] = []         # v0.7
    forbids_fired: List[str] = []          # v0.7
```

**v0.9 Precondition Enhancement:**

```python
class Precondition(BaseModel):
    """
    A condition that must be satisfied for a storylet to trigger.
    
    v0.9: Supports both traditional rule-based AND natural language conditions.
    """
    # Traditional fields (v0.8):
    path: Optional[str] = None       # e.g., "world.vars.power"
    op: Optional[str] = None         # e.g., ">=", "<", "=="
    value: Optional[Any] = None      # e.g., 60
    
    # v0.9 NEW:
    nl_condition: Optional[str] = None  # Natural language condition
    
    def is_nl_condition(self) -> bool:
        """Returns True if this is an NL condition."""
        return self.nl_condition is not None and self.nl_condition.strip() != ""
```


#### 2. DirectorConfig

```python
class DirectorConfig(BaseModel):
    """
    Configuration for World Director selection behavior.
    
    Attributes:
        events_per_tick: Number of storylets to select per tick
        diversity_penalty: Weight reduction for recently-used tags (0.0-0.3)
        diversity_window: Number of recent ticks to check for tag repetition
        pacing_scale: How strongly to adjust for intensity (0.0-0.3)
        
        # v0.7 NEW FIELD:
        fallback_after_idle_ticks: Trigger fallback after N empty ticks
        
        # v0.9 NEW FIELDS:
        ai_mode: Control AI usage ("deterministic", "ai_assisted", "ai_primary")
        ai_cache_enabled: Enable caching for AI evaluations
    """
    events_per_tick: int = 2
    diversity_penalty: float = 0.5
    diversity_window: int = 3
    pacing_scale: float = 0.3
    fallback_after_idle_ticks: int = 3     # v0.7
    ai_mode: Literal["deterministic", "ai_assisted", "ai_primary"] = "ai_assisted"  # v0.9
    ai_cache_enabled: bool = True          # v0.9
```


#### 3. TickHistory (v0.7 Updated)

```python
class TickHistory(BaseModel):
    """
    Tracks all ticks and storylet triggering history.
    
    Attributes:
        records: All tick records in chronological order
        last_triggered: Mapping of storylet_id → last tick triggered
        triggered_once: Mapping of storylet_id → has ever triggered (for "once")
        
        # v0.7 NEW FIELD:
        idle_tick_count: Consecutive ticks with no regular storylets
    """
    records: List[TickRecord] = []
    last_triggered: Dict[str, int] = {}
    triggered_once: Dict[str, bool] = {}
    idle_tick_count: int = 0               # v0.7
```

---

## AI-Enhanced Director (v0.9)

**New in v0.9:** The World Director now supports AI-powered natural language conditions alongside traditional rule-based conditions, enabling more nuanced and expressive narrative logic.

### Core Innovation: Hybrid Evaluation

The v0.9 enhancement introduces **three director modes** that give users full control over AI usage:

```python
class DirectorConfig(BaseModel):
    # ... existing fields ...
    
    # v0.9 NEW FIELDS:
    ai_mode: Literal["deterministic", "ai_assisted", "ai_primary"] = "ai_assisted"
    ai_cache_enabled: bool = True
```

**Three Modes:**

| Mode | Description | Performance | Use Case |
|------|-------------|-------------|----------|
| **🔧 Deterministic** | Pure rule-based evaluation (v0.8 behavior) | <1ms, 0 tokens | High performance, exact logic |
| **🤖 AI-Assisted** | Hybrid: rules first, AI for NL conditions | ~500ms, 200-800 tokens | Balanced, recommended |
| **🧠 AI-Primary** | AI evaluates all conditions | 1-2s, 500-2000 tokens | Maximum flexibility |

### Natural Language Conditions

**New Precondition field:**

```python
class Precondition(BaseModel):
    # Traditional (v0.8)
    path: Optional[str] = None       # e.g., "world.vars.power"
    op: Optional[str] = None         # e.g., ">=", "<", "=="
    value: Optional[Any] = None      # e.g., 60
    
    # v0.9 NEW:
    nl_condition: Optional[str] = None  # Natural language condition
    
    def is_nl_condition(self) -> bool:
        """Check if this is a natural language condition."""
        return self.nl_condition is not None and self.nl_condition.strip() != ""
```

**Examples of NL conditions:**

```json
{
  "preconditions": [
    {"nl_condition": "The player appears wealthy and has a good reputation"}
  ]
}
```

```json
{
  "preconditions": [
    {"nl_condition": "Relations between factions are severely strained"}
  ]
}
```

```json
{
  "preconditions": [
    {"nl_condition": "The common people are desperate and losing hope"}
  ]
}
```

### AIConditionsEvaluator

**New service:** `src/services/ai_conditions.py` (350 lines)

```python
class AIConditionsEvaluator:
    """
    Evaluates natural language conditions using LLM.
    
    Key features:
    - Converts world state to natural language context
    - Structured LLM prompts ensure consistent output
    - Returns (satisfied: bool, explanation: str)
    - Smart caching based on state hash
    """
    
    def __init__(self, llm_client: LLMClient, token_stats: TokenStats):
        self.llm = llm_client
        self.stats = token_stats
        self._cache: Dict[str, Tuple[bool, str]] = {}
    
    def evaluate(
        self,
        condition: str,
        project: Project,
        world_state: WorldState,
        character_states: Dict[str, CharacterState]
    ) -> Tuple[bool, str]:
        """
        Evaluate a single NL condition.
        
        Returns:
            (satisfied, explanation)
            
        Example explanation:
            "✓ [AI 0.92] Player appears wealthy (player_wealth=65, reputation=55)"
        """
        # Check cache first
        cache_key = self._make_cache_key(condition, world_state, character_states)
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Build natural language context
        context = self._build_context(world_state, character_states)
        
        # Call LLM with structured prompt
        response = self._call_llm(condition, context)
        
        # Parse structured response
        satisfied, confidence, reasoning = self._parse_response(response)
        
        # Format explanation
        explanation = f"{'✓' if satisfied else '✗'} [AI {confidence:.2f}] {reasoning}"
        
        # Cache result
        self._cache[cache_key] = (satisfied, explanation)
        
        return satisfied, explanation
```

**Caching mechanism:**

```python
def _make_cache_key(
    self,
    condition: str,
    world_state: WorldState,
    character_states: Dict[str, CharacterState]
) -> str:
    """
    Generate cache key from condition text and relevant state.
    
    Same condition + same state = cache hit (0 tokens)
    """
    state_hash = hashlib.md5()
    state_hash.update(condition.encode())
    state_hash.update(json.dumps(world_state.vars, sort_keys=True).encode())
    state_hash.update(json.dumps(world_state.facts, sort_keys=True).encode())
    # ... hash character moods and relationships ...
    return state_hash.hexdigest()
```

### Hybrid Evaluation Flow

**In DirectorService:**

```python
def _evaluate_conditions_hybrid(
    self,
    preconditions: List[Precondition],
    project: Project,
    world_state: WorldState,
    character_states: Dict[str, CharacterState],
    config: DirectorConfig
) -> Tuple[bool, List[str]]:
    """
    Evaluate preconditions using hybrid approach.
    
    Flow:
    1. If ai_mode == "deterministic": only rule-based
    2. If ai_mode == "ai_assisted" or "ai_primary":
       - Traditional conditions → ConditionsEvaluator (fast)
       - NL conditions → AIConditionsEvaluator (LLM)
    3. Return (all_satisfied, reasons)
    """
    
    if config.ai_mode == "deterministic":
        # Skip NL conditions entirely
        traditional_only = [c for c in preconditions if not c.is_nl_condition()]
        return self.conditions_evaluator.evaluate_all(traditional_only, ...)
    
    reasons = []
    
    for condition in preconditions:
        if condition.is_nl_condition():
            # Use AI evaluator
            satisfied, explanation = self.ai_conditions_evaluator.evaluate(
                condition.nl_condition,
                project,
                world_state,
                character_states
            )
            reasons.append(explanation)
            if not satisfied:
                return False, reasons
        else:
            # Use traditional evaluator
            satisfied, explanation = self.conditions_evaluator.evaluate_single(condition, ...)
            reasons.append(explanation)
            if not satisfied:
                return False, reasons
    
    return True, reasons
```

### UI Integration

**Director View (v0.9):**

```python
# AI Mode Selection
ai_mode = st.radio(
    "🎯 Director Mode",
    options=["deterministic", "ai_assisted", "ai_primary"],
    format_func=lambda x: {
        "deterministic": "🔧 Deterministic (Rule-based)",
        "ai_assisted": "🤖 AI-Assisted (Hybrid)",
        "ai_primary": "🧠 AI-Primary (Emergent)"
    }[x],
    horizontal=True
)

# Pass to DirectorConfig
config = DirectorConfig(
    events_per_tick=events_per_tick,
    pacing_preference=pacing_preference,
    ai_mode=ai_mode,  # v0.9
    ai_cache_enabled=True
)
```

### Best Practices for NL Conditions

**✅ Good NL Conditions:**

- **Clear and specific:** "The player is wealthy and respected"
- **Qualitative judgments:** "The atmosphere feels tense and dangerous"
- **Complex social states:** "Relations between factions are hostile"
- **Emotional states:** "The common people are desperate and losing hope"
- **Temporal reasoning:** "Violence seems imminent"

**❌ Avoid:**

- **Too vague:** "Something is wrong"
- **Too complex:** "If X then Y unless Z considering W..."
- **Numeric duplicates:** "power is greater than 60" (use traditional conditions!)
- **Self-referential:** "This condition should trigger"

### Performance Considerations

**Token Usage:**

- **AI-Assisted:** ~200-800 tokens per NL condition evaluation
- **Caching:** Same state → 0 tokens (instant)
- **Recommended limit:** 8000 tokens/day for hobby use

**Response Time:**

- **Deterministic:** <1ms (no AI)
- **AI-Assisted:** ~500ms per unique NL evaluation
- **Cache hits:** <1ms (instant)

**Cost Optimization:**

1. Use deterministic mode for performance-critical paths
2. Enable caching (default: on)
3. Write stable NL conditions (avoid random phrasing)
4. Mix traditional + NL conditions (evaluate cheap ones first)

### Testing AI Conditions

**Test projects included:**

- `examples/town_factions/` - 10 English NL condition storylets
- `examples/ai_test_zh/` - 10 Chinese NL condition storylets

**Testing approach:**

```python
# Test NL condition evaluation
config = DirectorConfig(ai_mode="ai_assisted")
tick_record = director_service.tick(project, thread_id, step_index, config)

# Check if NL storylets were triggered
for storylet, rationale in tick_record.selected_storylets:
    if storylet.id.startswith("st-nl-"):
        print(f"✓ NL storylet triggered: {storylet.title}")
        print(f"  Rationale: {rationale}")
```

---

## Data Flow & Pipelines

### World Director Pipeline

The `select_storylets()` method implements a **9-stage pipeline** with AI enhancements in v0.9:

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
    
    v0.9 enhancement: Stage 1 now includes AI-powered condition evaluation
    when ai_mode is "ai_assisted" or "ai_primary".
    
    Returns: List of (Storylet, rationale) tuples
    """
    tokenStats: TokenStats
```

**Pipeline Stages Overview:**

1. **Precondition Evaluation** (v0.9 enhanced):
   - **Traditional conditions** → Deterministic evaluator (<1ms)
   - **NL conditions** → AI evaluator (~500ms, if ai_mode allows)
   - All conditions must be satisfied (AND logic)
   - Returns eligible storylets only

2. **Recent History Filtering** - Remove recently triggered storylets

3. **Category Filtering** - Apply category-specific limits

4. **Priority Sorting** - Order by storylet importance

5. **Pacing Adjustment** - Match user's pacing preference

6. **Diversity Selection** - Avoid repetitive patterns

7. **Final Scoring** - Composite score calculation

8. **Top-N Selection** - Select best candidates

9. **Rationale Generation** - Explain selections

**Key v0.9 Enhancement in Stage 1:**

```python
# Pseudocode of Stage 1 with AI support
eligible = []
for storylet in all_storylets:
    satisfied, reasons = self._evaluate_conditions_hybrid(
        storylet.preconditions,
        project,
        world_state,
        character_states,
        config  # Contains ai_mode
    )
    if satisfied:
        eligible.append((storylet, reasons))
    else:
        # Log rejection with AI-generated explanations
        logger.debug(f"Rejected {storylet.id}: {reasons}")

return eligible  # Pass to Stage 2
```

---

### Models

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

### AI-Enhanced World Director (v0.9) 🌟

See [AI-Enhanced Director (v0.9)](#ai-enhanced-director-v09) section above for full details.

**Core files:**
- `src/services/ai_conditions.py` - AIConditionsEvaluator (350 lines)
- `src/services/director_service.py` - Hybrid evaluation logic
- `src/models/storylet.py` - Precondition.nl_condition field
- `src/ui/director_view.py` - AI mode selector UI

**Test projects with NL conditions:**
- `examples/town_factions/` - 10 English NL storylets
- `examples/ai_test_zh/` - 10 Chinese NL storylets

### Scene Analysis Tools (v0.6+)

**Scene Checkup Panel** - `src/ui/scene_checkup_panel.py`

AI-powered scene analysis with caching:
- Scene summarization
- Fact extraction  
- Emotion detection
- Character OOC checking

**Vector Search** - `src/infra/vector_db.py`

FAISS-based semantic search for scenes, characters, and lore:
- CPU-optimized (no GPU required)
- Multilingual support (paraphrase-multilingual-MiniLM-L12-v2)
- Project-level isolation

## Development Workflow

### Adding New Features

1. **Define Model** (if needed) in `src/models/`
2. **Create Service** in `src/services/`
3. **Build UI Component** in `src/ui/`
4. **Add i18n Keys** in `i18n/en.json` and `i18n/zh.json`
5. **Test** with sample project
6. **Update Documentation** (developer_guide.en.md, DEVELOPMENT_ROADMAP.md)

### Adding Natural Language Conditions (v0.9)

1. **Add to storylet preconditions:**
```json
{
  "preconditions": [
    {"nl_condition": "Your natural language condition here"}
  ]
}
```

2. **Test with AI-Assisted mode** to verify condition triggers correctly

3. **Document pattern** if it's a new design pattern

**See:** `examples/town_factions/NL_CONDITIONS_GUIDE.md` for patterns and best practices

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

### Testing AI-Enhanced Director (v0.9) 🌟

**Test Projects:**
- `examples/town_factions/` - 10 English NL condition storylets (faction politics)
- `examples/ai_test_zh/` - 10 Chinese NL condition storylets (武侠江湖)

**Testing Workflow:**
1. Load test project (e.g., `town_factions`)
2. Navigate to World Director view
3. Select AI mode (🔧 Deterministic / 🤖 AI-Assisted / 🧠 AI-Primary)
4. Click "▶️ Tick Forward" and observe:
   - Which storylets trigger (look for `st-nl-*` IDs)
   - AI evaluation explanations (e.g., "✓ [AI 0.92] Player appears wealthy...")
   - Response time and token usage
5. Change world state variables (e.g., `player_wealth`, `tension_level`)
6. Run tick again to verify NL conditions respond appropriately

**What to Test:**
- ✅ NL conditions trigger correctly based on state
- ✅ Traditional conditions still work (hybrid evaluation)
- ✅ Cache hits reduce token usage (run same state twice)
- ✅ AI mode switching works without errors
- ✅ Spinner shows during AI processing

### Manual Testing (General Features)

1. Load sample project: Click 🇨🇳 or 🇺🇸 button
2. Test graph interaction: Drag nodes, click for details
3. Test Scene Checkup: Click node → AI Checkup tab
4. Test World Director: Navigate to Director view, run ticks
5. Verify i18n: Switch language, check UI updates

### Sample Projects

**Current:**
- `examples/sample_project/` - Chinese interactive fiction
- `examples/sample_project_en/` - English version
- `examples/town_factions/` - English World Director test (10 NL storylets)
- `examples/ai_test_zh/` - Chinese World Director test (10 NL storylets, 武侠主题)

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

---

## Resources

- **Streamlit Docs**: https://docs.streamlit.io
- **FAISS**: https://github.com/facebookresearch/faiss
- **DeepSeek API**: https://platform.deepseek.com/docs
- **Full Roadmap**: See [DEVELOPMENT_ROADMAP.md](../DEVELOPMENT_ROADMAP.md) for v0.9 completion plan

---

## License

MIT License

---

## Contact

- GitHub: [yourusername/story-graph-assistant](https://github.com/yourusername/story-graph-assistant)
- Issues: [Report a bug](https://github.com/yourusername/story-graph-assistant/issues)

---

**Slogan**: *"Visual AI assistant for branching game stories."*
