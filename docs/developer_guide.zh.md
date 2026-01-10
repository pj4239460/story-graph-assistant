# 开发者指南

> **Story Graph Assistant** - 技术文档与贡献指南

**版本：** 0.7  
**最后更新：** 2026年1月

本指南为Story Graph Assistant的开发者提供全面的技术文档，涵盖系统架构、代码组织、数据流、测试策略以及添加新功能的指南。

---

## 目录

- [架构概览](#架构概览)
- [技术栈](#技术栈)
- [项目结构](#项目结构)
- [世界导演系统（v0.7）](#世界导演系统v07)
- [数据流与管道](#数据流与管道)
- [状态管理](#状态管理)
- [测试策略](#测试策略)
- [添加新功能](#添加新功能)
- [代码规范](#代码规范)

---

## 架构概览

**本地优先架构**，采用 Python 后端和 Streamlit 前端。

**架构层次：**
```
┌─────────────────────────────────────────────────────┐
│                   Streamlit UI                      │
│  (app.py + ui/*)                                   │
│  - Director View (世界导演界面)                     │
│  - Characters View (角色编辑器)                     │
│  - Routes View (场景编辑器)                         │
│  - AI Tools View (LLM辅助工具)                     │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│                Service Layer                        │
│  - DirectorService (storylet选择 v0.7)            │
│  - StateService (时序状态计算)                      │
│  - ProjectService (项目增删改查)                    │
│  - AIService (LLM集成)                             │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│                 Model Layer                         │
│  - Pydantic V2 模型 (验证 + 序列化)                │
│  - Storylet, World, Effect, Condition               │
│  - 类型安全和模式强制                               │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│                Data Persistence                     │
│  - JSON 文件 (project.json)                        │
│  - Repository 模式 (base + json_repo)              │
│  - 本地优先存储                                     │
└─────────────────────────────────────────────────────┘
```

### 请求流示例：Tick Forward

```
用户在 director_view.py 点击 "▶️ Tick Forward"
    ↓
DirectorService.tick(scene_id, config)
    ↓
select_storylets() → 9阶段管道（v0.7）
    ├─ 阶段1：前置条件过滤
    ├─ 阶段2：顺序约束（v0.7）
    ├─ 阶段3：冷却时间与一次性
    ├─ 阶段4：回退检查（v0.7）
    ├─ 阶段5：多样性惩罚
    ├─ 阶段6：节奏调整
    ├─ 阶段7：加权选择
    ├─ 阶段8：效果应用
    └─ 阶段9：历史记录
    ↓
apply_effects() → 新世界状态
    ↓
StateService.compute_diffs(old_state, new_state)
    ↓
返回 TickRecord（包含 storylets + diffs + rationale）
    ↓
UI 在 director_view.py 显示结果
```

---

## 技术栈

| 组件 | 技术 | 用途 |
|------|------|------|
| 框架 | Streamlit 1.30+ | Web UI 框架 |
| 语言 | Python 3.11+ | 核心语言 |
| LLM | DeepSeek via LiteLLM | AI辅助 |
| 存储 | JSON | 项目持久化 |
| 验证 | Pydantic 2.0 | 数据验证 + 序列化 |
| 测试 | pytest | 单元和集成测试 |

---

## 项目结构

```
src/
├── app.py                        # Streamlit 应用入口
│
├── models/                       # Pydantic V2 数据模型
│   ├── __init__.py
│   ├── project.py               # 项目容器
│   ├── storylet.py              # 世界导演模型（v0.7）
│   │   ├── Storylet            # Storylet 定义
│   │   ├── DirectorConfig      # 选择配置
│   │   ├── TickRecord          # 单次tick结果
│   │   └── TickHistory         # 所有ticks + 跟踪
│   ├── world.py                 # 状态和效果
│   │   ├── World               # 全局状态
│   │   ├── Effect              # 状态变更
│   │   └── Condition           # 前置条件检查
│   ├── character.py             # 角色数据
│   ├── scene.py                 # 场景数据
│   ├── event.py                 # 事件数据
│   └── ai.py                    # AI 设置
│
├── services/                    # 业务逻辑层
│   ├── __init__.py
│   ├── director_service.py     # 世界导演编排
│   │   ├── DirectorService     # 主服务类
│   │   ├── select_storylets()  # 9阶段选择管道（v0.7）
│   │   ├── apply_effects()     # 应用效果到状态
│   │   ├── tick()              # 执行一次 tick
│   │   ├── _filter_by_ordering_constraints()  # v0.7
│   │   └── _select_fallback_candidates()      # v0.7
│   ├── state_service.py        # 状态计算
│   │   ├── compute_state()     # 时序状态计算
│   │   ├── compute_diffs()     # 前后对比
│   │   └── explain_condition() # 人类可读的解释
│   ├── conditions.py           # 条件评估
│   │   └── evaluate()          # 确定性条件检查
│   ├── project_service.py      # 项目增删改查
│   ├── scene_service.py        # 场景管理
│   ├── character_service.py    # 角色管理
│   └── ai_service.py           # LLM 集成
│
├── repositories/                # 数据访问层
│   ├── __init__.py
│   ├── base.py                 # 抽象仓库接口
│   └── json_repo.py            # JSON 文件后端实现
│
├── ui/                          # Streamlit 视图组件
│   ├── __init__.py
│   ├── layout.py               # 页面结构和导航
│   ├── sidebar.py              # 侧边栏导航
│   ├── director_view.py        # 世界导演 UI（v0.7 更新）
│   ├── characters_view.py      # 角色编辑器
│   ├── routes_view.py          # 场景编辑器
│   └── ai_tools_view.py        # AI 助手界面
│
└── infra/                       # 基础设施层
    ├── __init__.py
    ├── llm_client.py           # OpenAI/Claude 客户端封装
    ├── token_stats.py          # LLM token 使用跟踪
    └── i18n.py                 # 国际化（en/zh）
```

---

## 世界导演系统（v0.7）

世界导演是核心动态叙事引擎，负责根据前置条件、顺序约束、节奏和回退机制选择并触发storylet。

### 核心组件

#### 1. Storylet 模型

```python
class Storylet(BaseModel):
    """
    可被世界导演选择的叙事事件。
    
    属性：
        id: 唯一标识符（用于 requires_fired, forbids_fired）
        title: 显示名称
        description: 完整叙事内容
        preconditions: 必须全部满足的条件列表
        effects: 触发时应用的状态变更列表
        weight: 基础选择概率（默认：0.3）
        once: 如果为 True，每次游玩只能触发一次
        cooldown: 再次触发前的最小 tick 数
        intensity_delta: 叙事强度变化（-0.3 到 0.3）
        tags: 用于多样性惩罚和分组
        
        # v0.7 新字段：
        is_fallback: 如果为 True，仅在达到空闲阈值时选择
        requires_fired: 必须先触发的 storylet ID
        forbids_fired: 不能触发的 storylet ID
    """
    id: str
    title: str
    description: str = ""
    preconditions: List[Condition] = []
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

#### 2. DirectorConfig

```python
class DirectorConfig(BaseModel):
    """
    世界导演选择行为的配置。
    
    属性：
        events_per_tick: 每次 tick 选择的 storylet 数量
        diversity_penalty: 最近使用标签的权重减少（0.0-0.3）
        diversity_window: 检查标签重复的最近 tick 数量
        pacing_scale: 强度调整的强度（0.0-0.3）
        
        # v0.7 新字段：
        fallback_after_idle_ticks: N 次空 tick 后触发回退
    """
    events_per_tick: int = 2
    diversity_penalty: float = 0.5
    diversity_window: int = 3
    pacing_scale: float = 0.3
    fallback_after_idle_ticks: int = 3     # v0.7
```

#### 3. TickHistory（v0.7 更新）

```python
class TickHistory(BaseModel):
    """
    跟踪所有 ticks 和 storylet 触发历史。
    
    属性：
        records: 按时间顺序的所有 tick 记录
        last_triggered: storylet_id → 上次触发的 tick
        triggered_once: storylet_id → 是否曾经触发过（用于 "once"）
        
        # v0.7 新字段：
        idle_tick_count: 连续没有常规 storylet 的 tick 数
    """
    records: List[TickRecord] = []
    last_triggered: Dict[str, int] = {}
    triggered_once: Dict[str, bool] = {}
    idle_tick_count: int = 0               # v0.7
```

---

## 数据流与管道

### 世界导演管道（v0.7）

`select_storylets()` 方法实现了 9 阶段管道：

```python
def select_storylets(
    self,
    scene: Scene,
    current_state: World,
    config: DirectorConfig,
    history: TickHistory
) -> List[Tuple[Storylet, str]]:
    """
    执行 9 阶段 storylet 选择管道。
    
    返回：List of (Storylet, rationale) 元组
    """
    
    # 阶段 1：前置条件过滤
    # 过滤掉不满足 preconditions 的 storylet
    candidates = [s for s in scene.storylets 
                  if all(evaluate(cond, current_state) 
                        for cond in s.preconditions)]
    
    # 阶段 2：顺序约束（v0.7）
    # 过滤 requires_fired 和 forbids_fired
    candidates = self._filter_by_ordering_constraints(
        candidates, history
    )
    
    # 阶段 3：冷却时间与一次性
    # 移除正在冷却的 storylet 和已触发的 once storylet
    candidates = [s for s in candidates
                  if not self._is_on_cooldown(s, history)
                  and not (s.once and s.id in history.triggered_once)]
    
    # 阶段 4：回退检查（v0.7）
    # 如果没有候选者且空闲 tick 计数 >= 阈值，启用回退
    if not candidates and history.idle_tick_count >= config.fallback_after_idle_ticks:
        candidates = self._select_fallback_candidates(scene)
    
    # 阶段 5：多样性惩罚
    # 减少最近使用的标签的权重
    weights = self._apply_diversity_penalty(
        candidates, history, config
    )
    
    # 阶段 6：节奏调整
    # 根据当前强度调整权重
    weights = self._adjust_for_pacing(
        weights, current_state, config
    )
    
    # 阶段 7：加权选择
    # 使用调整后的权重随机选择 storylets
    selected = random.choices(
        candidates,
        weights=weights,
        k=config.events_per_tick
    )
    
    # 阶段 8：效果应用
    # （在单独的方法中处理）
    
    # 阶段 9：历史记录
    # 更新 TickHistory
    
    return [(s, self._generate_rationale(s)) for s in selected]
```

### 项目加载流程

```
用户选择项目文件
    ↓
ProjectService.load_project(path)
    ↓
JsonRepository.read(path)
    ↓
Pydantic 验证 (Project model)
    ↓
加载到 st.session_state.project
    ↓
UI 更新（scenes, characters, etc.）
```

### Storylet 执行流程

```
用户点击 "Tick Forward"
    ↓
DirectorService.tick(scene_id, config)
    ↓
select_storylets() → [Storylet, ...]
    ↓
apply_effects() → new World state
    ↓
StateService.compute_diffs(old, new)
    ↓
return TickRecord {
    tick_number: int
    selected_storylets: [...]
    state_before: World
    state_after: World
    diffs: [StateDiff, ...]
    timestamp: datetime
}
    ↓
UI 显示：
  - 选择的 storylets
  - 状态变化
  - 选择理由
```

---

## 状态管理

### Session State（st.session_state）

Streamlit 使用 session state 在页面刷新之间保持数据：

```python
# 初始化
if 'project' not in st.session_state:
    st.session_state.project = None
    st.session_state.tick_history = TickHistory()
    st.session_state.current_world = World()

# 访问
project = st.session_state.project

# 更新
st.session_state.current_world = new_world
```

### 持久化

项目数据保存为 JSON：

```python
# 保存
ProjectService.save_project(project, path)
    ↓
JsonRepository.write(project.model_dump(), path)

# 加载
project = ProjectService.load_project(path)
    ↓
data = JsonRepository.read(path)
    ↓
project = Project.model_validate(data)
```

### 状态同步

确保 UI 和数据层同步：

```python
# 在服务层更新后
new_state = DirectorService.tick(...)

# 立即更新 session state
st.session_state.current_world = new_state.state_after
st.session_state.tick_history.records.append(new_state)

# 触发 UI 重新渲染
st.rerun()
```

---

## 测试策略

### 单元测试

测试单个函数和类：

```python
# tests/test_conditions.py
import pytest
from src.services.conditions import evaluate
from src.models.world import Condition, World

def test_evaluate_equals():
    world = World(flags={"test_flag": 5})
    cond = Condition(
        check_type="equals",
        flag_name="test_flag",
        value=5
    )
    assert evaluate(cond, world) == True

def test_evaluate_greater_than():
    world = World(flags={"score": 100})
    cond = Condition(
        check_type="greater_than",
        flag_name="score",
        value=50
    )
    assert evaluate(cond, world) == True
```

### 集成测试

测试多个组件的交互：

```python
# tests/test_director_service.py
import pytest
from src.services.director_service import DirectorService
from src.models.storylet import Storylet, DirectorConfig
from src.models.world import World, Effect

def test_tick_with_ordering_constraints():
    # 设置
    service = DirectorService()
    scene = Scene(storylets=[
        Storylet(id="intro", title="Intro", weight=1.0),
        Storylet(
            id="followup",
            title="Follow-up",
            requires_fired=["intro"],
            weight=1.0
        )
    ])
    
    # 执行第一次 tick
    result1 = service.tick(scene, World(), DirectorConfig(), TickHistory())
    
    # 断言
    assert len(result1.selected_storylets) > 0
    assert result1.selected_storylets[0].id == "intro"
    
    # 执行第二次 tick
    history = result1.history
    result2 = service.tick(scene, result1.state_after, DirectorConfig(), history)
    
    # 现在 "followup" 应该可用
    selected_ids = [s.id for s in result2.selected_storylets]
    assert "followup" in selected_ids
```

### 覆盖率目标

- 单元测试：> 80%
- 集成测试：核心流程 100%
- 边缘情况：优先级高的场景

---

## 添加新功能

### 示例：添加 "multiply" 效果类型

#### 步骤 1：更新模型

```python
# src/models/world.py
class Effect(BaseModel):
    effect_type: Literal["set", "add", "multiply"]  # 添加 "multiply"
    flag_name: str
    value: float
```

#### 步骤 2：更新服务

```python
# src/services/director_service.py
def apply_effects(self, effects: List[Effect], world: World) -> World:
    new_flags = world.flags.copy()
    
    for effect in effects:
        if effect.effect_type == "set":
            new_flags[effect.flag_name] = effect.value
        elif effect.effect_type == "add":
            current = new_flags.get(effect.flag_name, 0)
            new_flags[effect.flag_name] = current + effect.value
        elif effect.effect_type == "multiply":  # 新功能
            current = new_flags.get(effect.flag_name, 1)
            new_flags[effect.flag_name] = current * effect.value
    
    return World(flags=new_flags, intensity=world.intensity)
```

#### 步骤 3：添加测试

```python
# tests/test_effects.py
def test_multiply_effect():
    world = World(flags={"damage": 10})
    effects = [Effect(
        effect_type="multiply",
        flag_name="damage",
        value=2.0
    )]
    
    service = DirectorService()
    new_world = service.apply_effects(effects, world)
    
    assert new_world.flags["damage"] == 20.0
```

#### 步骤 4：更新 UI

```python
# src/ui/director_view.py
effect_type = st.selectbox(
    "效果类型",
    options=["set", "add", "multiply"],  # 添加选项
    key=f"effect_type_{idx}"
)
```

#### 步骤 5：更新文档

```markdown
# docs/agent_guide.zh.md
## 效果类型

- **set**: 设置标志为特定值
- **add**: 将值加到现有标志
- **multiply**: 将现有标志乘以值（v0.7+）
```

---

## 代码规范

### Python 风格

遵循 [PEP 8](https://peps.python.org/pep-0008/)：

```python
# ✅ 好
def calculate_total_score(
    base_score: int,
    multiplier: float
) -> float:
    """计算总分数。
    
    Args:
        base_score: 基础分数
        multiplier: 倍数
        
    Returns:
        总分数
    """
    return base_score * multiplier

# ❌ 不好
def calc(b,m):
    return b*m
```

### Pydantic V2 模式

使用 Pydantic V2 API：

```python
# ✅ 好 (V2)
from pydantic import BaseModel, Field

class Character(BaseModel):
    name: str = Field(..., min_length=1)
    age: int = Field(ge=0, le=150)

# ❌ 不好 (V1)
from pydantic import BaseModel, validator

class Character(BaseModel):
    name: str
    age: int
    
    @validator('age')
    def check_age(cls, v):
        if v < 0:
            raise ValueError('age must be positive')
        return v
```

### Streamlit 最佳实践

```python
# ✅ 好：使用 key 避免状态冲突
st.button("保存", key="save_project_btn")

# ❌ 不好：无 key
st.button("保存")

# ✅ 好：缓存昂贵的计算
@st.cache_data
def load_large_dataset():
    return expensive_operation()

# ❌ 不好：每次都重新计算
def load_large_dataset():
    return expensive_operation()
```

### 提交信息

使用 [Conventional Commits](https://www.conventionalcommits.org/)：

```
feat(director): add ordering constraints support
fix(ui): resolve state sync issue in director view
docs(guide): update developer guide with v0.7 features
refactor(service): extract condition evaluation logic
perf(select): optimize storylet filtering
```

---

## 常见开发任务

### 添加新的 UI 视图

1. 在 `src/ui/` 创建文件（如 `timeline_view.py`）
2. 定义渲染函数：
   ```python
   def render_timeline_view():
       st.title("时间线")
       # 实现...
   ```
3. 在 `src/ui/layout.py` 注册：
   ```python
   if page == "时间线":
       timeline_view.render_timeline_view()
   ```
4. 在 `src/ui/sidebar.py` 添加导航：
   ```python
   if st.sidebar.button("⏱️ 时间线"):
       st.session_state.current_page = "时间线"
       st.rerun()
   ```

### 添加新的服务

1. 在 `src/services/` 创建文件（如 `export_service.py`）
2. 定义服务类：
   ```python
   class ExportService:
       def __init__(self, project: Project):
           self.project = project
       
       def export_to_twine(self) -> str:
           # 实现...
           pass
   ```
3. 在 UI 中使用：
   ```python
   from src.services.export_service import ExportService
   
   service = ExportService(st.session_state.project)
   twine_html = service.export_to_twine()
   ```

### 添加新的数据模型

1. 在 `src/models/` 创建/更新文件
2. 定义 Pydantic 模型：
   ```python
   from pydantic import BaseModel, Field
   
   class Timeline(BaseModel):
       events: List[TimelineEvent] = []
       start_date: str = Field(..., pattern=r"\d{4}-\d{2}-\d{2}")
   ```
3. 在 `Project` 模型中引用：
   ```python
   class Project(BaseModel):
       # ...
       timeline: Optional[Timeline] = None
   ```

---

## 调试技巧

### Streamlit 调试

```python
# 使用 st.write 打印调试信息
st.write("Debug:", st.session_state.project)

# 使用 st.json 格式化显示
st.json(world.model_dump())

# 使用 st.exception 捕获错误
try:
    risky_operation()
except Exception as e:
    st.exception(e)
```

### 日志记录

```python
import logging

logger = logging.getLogger(__name__)

def select_storylets(...):
    logger.info(f"Selecting storylets for scene {scene.id}")
    logger.debug(f"Candidates: {len(candidates)}")
    
    if not candidates:
        logger.warning("No candidates available")
```

### 性能分析

```python
import time

start = time.time()
result = expensive_operation()
elapsed = time.time() - start
print(f"Operation took {elapsed:.2f}s")
```

---

## 性能优化

### Streamlit 缓存

```python
@st.cache_data
def load_project(path: str) -> Project:
    """缓存项目加载"""
    return ProjectService.load_project(path)

@st.cache_resource
def get_llm_client():
    """缓存 LLM 客户端"""
    return LLMClient(api_key=...)
```

### 批量操作

```python
# ✅ 好：批量更新
def update_multiple_flags(world: World, updates: Dict[str, float]):
    new_flags = world.flags.copy()
    new_flags.update(updates)
    return World(flags=new_flags)

# ❌ 不好：逐个更新
def update_flags_one_by_one(world: World, updates: Dict[str, float]):
    for key, value in updates.items():
        world = World(flags={**world.flags, key: value})
    return world
```

---

## 贡献指南

### 开发流程

1. **Fork 仓库**
2. **创建分支**：`git checkout -b feature/amazing-feature`
3. **实现功能**：遵循代码规范
4. **添加测试**：覆盖新功能
5. **更新文档**：README、guide等
6. **提交代码**：使用 Conventional Commits
7. **推送分支**：`git push origin feature/amazing-feature`
8. **创建 Pull Request**

### Pull Request 检查清单

- [ ] 所有测试通过
- [ ] 代码遵循 PEP 8
- [ ] 添加了必要的文档
- [ ] 更新了 CHANGELOG
- [ ] PR 描述清晰说明了变更内容

---

## FAQ

### Q: 如何添加新的条件类型？

A: 在 `src/models/world.py` 的 `Condition` 模型中添加新的 `check_type`，然后在 `src/services/conditions.py` 的 `evaluate()` 函数中实现逻辑。

### Q: 如何集成新的 LLM 提供商？

A: 更新 `src/infra/llm_client.py`，添加新的客户端类，并在 `AIService` 中使用。

### Q: 如何优化大型项目的加载速度？

A: 使用 `@st.cache_data` 缓存项目加载，考虑实现增量加载或延迟加载策略。

---

## 资源

- **Streamlit 文档**: https://docs.streamlit.io
- **Pydantic 文档**: https://docs.pydantic.dev
- **pytest 文档**: https://docs.pytest.org
- **PEP 8 风格指南**: https://peps.python.org/pep-0008/

---

**有问题？** 在 [github.com/pj4239460/story-graph-assistant](https://github.com/pj4239460/story-graph-assistant) 提交 issue
