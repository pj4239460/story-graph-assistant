# Story Graph Assistant / 故事图谱助手

> **Visual AI assistant for emergent game narratives.**  
> **用 AI 导演 + 故事片段，自动演化你的游戏世界。**

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

A powerful tool for narrative game developers featuring **World Director** - an AI-powered system that creates emergent, replayable stories using storylets and dynamic state management.

**[English](#english)** | **[中文](#中文)**

---

## English

### ✨ Core Features

#### 🎬 World Director (v1.7.1)
Our **differentiated approach** to narrative design - move beyond manual branching and AI NPCs:

**Core System:**
- **Storylets System** - Define reusable narrative fragments with preconditions and effects
- **Quality-Based Narrative (QBN)** - Story emerges from state + rules, not manual branching
- **AI Director Pacing** - Automatic intensity control with peaks-and-valleys (inspired by Left 4 Dead)
- **Deterministic Selection** - Same state + config = same result (fully reproducible)
- **Explainable Decisions** - Every world tick includes human-readable rationale
- **Replayable History** - Complete tick-by-tick record with state diffs

**Advanced Features (v1.7.1 NEW!):**
- **Ordering Constraints** - Define narrative sequence dependencies (requires/forbids storylets)
- **Fallback Mechanism** - Prevents "world stuck" - triggers ambient storylets when no regular events qualify
- **Idle Detection** - Automatically tracks consecutive ticks with no activity
- **Complex Quest Chains** - Build multi-stage narratives with explicit ordering requirements

#### 📝 Story Building
- 🌳 **Interactive Story Graph** - Drag-and-drop visualization with multiple layouts
- ✏️ **Full Editing Support** - Edit scenes, characters, and choices with inline forms
- 📋 **Scene Checkup Panel** - AI-powered comprehensive scene analysis with caching
- 👥 **Character Management** - Centralized profiles and relationships

#### ⚡ Dynamic States
- **Effect-Based Mutations** - Define character/world/relationship changes
- **Play Path Mode** - Real-time state visualization as story progresses
- **State Viewer** - Query complete state at any point in saved threads
- **Temporal Replay** - Rewind and replay state changes

#### 🤖 AI Integration
- **Multi-LLM Support** - DeepSeek, OpenAI, Anthropic, Google, Ollama
- **AI Agent Assistant** - LangGraph-powered conversational queries
- **FAISS Semantic Search** - Vector-based scene retrieval
- **AI Agent Tools** - Query character states and relationships

#### 🌍 Other Features
- 📚 **Sample Projects** - Example projects with World Director demonstrations
- 🌍 **Bilingual Interface** - Full Chinese/English UI with dynamic switching
- 💾 **Simple Storage** - JSON-based portable project files

### 🚀 Quick Start

```bash
# Clone and setup
git clone https://github.com/pj4239460/story-graph-assistant.git
cd story-graph-assistant
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure API key
cp .env.example .env
# Edit .env: DEEPSEEK_API_KEY=your_key

# Run
streamlit run src/app.py
```

**Recommended:** Get a DeepSeek API key at [platform.deepseek.com](https://platform.deepseek.com/) (best value)  
Also supports: OpenAI, Anthropic, Google Gemini, and local models (Ollama)

### 📖 Usage

#### Traditional Story Building
1. **Try Samples** - Click 🇨🇳/🇺🇸 buttons in sidebar for example projects
2. **Create Project** - Click ➕ New to start your story
3. **Add Scenes** - Build your story graph with scenes and choices
4. **AI Analysis** - Click nodes to view Scene Checkup with AI insights
5. **Chat** - Ask AI questions about your story in natural language

#### World Director (Emergent Narratives)
1. **Load Example** - Try "Town of Riverhaven" faction politics example
2. **View Storylets** - See 20 pre-defined narrative fragments in World Director tab
3. **Configure Director** - Set events/tick, pacing preference, diversity penalty
4. **Run Tick** - Watch the Director select and trigger storylets based on state
5. **Review History** - Explore tick-by-tick evolution with complete rationale

### 🏗️ Tech Stack

- **Streamlit** - Interactive web framework
- **LangGraph** - AI agent orchestration
- **LiteLLM** - Multi-provider LLM routing (DeepSeek, OpenAI, Anthropic, Google, Ollama)
- **FAISS** - Vector search (CPU-optimized)
- **Pydantic V2** - Data validation and serialization

### 🛣️ Roadmap

**v1.0 - Vector Search** ✅
- [x] Vector-based retrieval (FAISS - migrated from ChromaDB)
- [x] Semantic similarity search with 384-dim embeddings
- [x] Auto-indexing on project load
- [x] Multi-LLM support with model selection UI

**v1.5 - Dynamic Character States** ✅
- [x] Effect model with scope/target/operation/path/value structure
- [x] StateService for temporal state computation and replay
- [x] Character state tracking (mood, status, traits, goals, fears, custom vars)
- [x] Relationship state tracking
- [x] World state tracking (global variables)
- [x] Effects editor UI with add/edit/delete
- [x] Play Path mode with real-time state visualization
- [x] State Viewer for querying states at any thread step
- [x] AI agent tools for state queries
- [x] Example projects with Effects demonstrations

**v1.6 - World Director (MVP)** ✅
- [x] Storylet data model (preconditions + effects + metadata)
- [x] ConditionsEvaluator (deterministic condition checking)
- [x] DirectorService (multi-stage selection pipeline)
- [x] World Director UI (tick controls, history, visualization)
- [x] Town of Riverhaven example (20 storylets, faction politics)
- [x] Comprehensive test suite (13 tests, 35+ assertions)

**v1.7.1 - Ordering & Fallback** ✅
- [x] Ordering constraints (requires_fired, forbids_fired)
- [x] Fallback storylets (ambient events when world stuck)
- [x] Idle tick tracking and reset logic
- [x] Enhanced UI displays (ordering constraints, idle counter)
- [x] Complete test suite (5 new tests for ordering/fallback)
- [x] Demo example with quest chains

**v1.7.2 - Actions Sequences** (In Progress - 1 week)
- [ ] Multi-stage storylet progression (cursor-based)
- [ ] Repeatable storylet support
- [ ] Enhanced tick history with cursor tracking
- [ ] Updated River Haven example with quest chains

**v1.8 - UI/UX Enhancements** (Next - 1-2 weeks)
- [ ] Tick timeline navigation (prev/next, jump to tick N)
- [ ] Visual intensity/pacing graphs
- [ ] Enhanced parameter tuning (presets, real-time tooltips)
- [ ] Export capabilities (JSON, Markdown reports, statistics)

**v1.9 - Author Tools** (Future - 1-2 weeks)
- [ ] Trigger accuracy labeling (✅/❌ feedback)
- [ ] Coverage report (dead content, spam detection)
- [ ] Consistency validation (ordering conflicts, unreachable storylets)
- [ ] Debugging dashboard

**v2.0 - AI Integration** (Future - 2-4 weeks)
- [ ] Natural language preconditions (LLM-based evaluation)
- [ ] AI-assisted storylet design (suggest preconditions/effects)
- [ ] Generate scene drafts from tick results
- [ ] Advanced what-if simulation (compare different configs)

### 📚 Documentation

- [Getting Started Guide](GETTING_STARTED.en.md) - Quick start tutorial
- [World Director Guide](docs/world_director_guide.md) - Comprehensive storylets reference
- [Developer Guide](docs/developer_guide.en.md) - System architecture and internals
- [API Documentation](docs/api_reference.md) - Complete API reference (Coming soon)

---

## 中文

### ✨ 功能特色

#### 🎬 世界导演系统 (v1.7.1)
我们的**差异化叙事设计方法** - 超越手工分支和AI NPC：

**核心系统：**
- **Storylets 系统** - 定义可复用的叙事片段，包含前置条件和效果
- **质量驱动叙事（QBN）** - 故事从状态+规则中涌现，而非手工分支
- **AI 导演节奏控制** - 自动强度控制，峰谷交替（受 Left 4 Dead 启发）
- **确定性选择** - 相同状态+配置=相同结果（完全可重现）
- **可解释决策** - 每次世界tick都包含人类可读的选择理由
- **可回放历史** - 完整的逐tick记录，包含状态差异

**高级功能（v1.7.1 新增！）：**
- **排序约束** - 定义叙事序列依赖（requires/forbids storylets）
- **备选机制** - 防止"世界卡住" - 当常规事件无法触发时，触发氛围storylets
- **空闲检测** - 自动跟踪连续无活动的ticks
- **复杂任务链** - 用显式排序要求构建多阶段叙事

#### 📝 故事构建
- 🌳 **交互式剧情图谱** - 拖拽可视化，多种布局算法
- ✏️ **完整编辑功能** - 内联表单编辑场景、角色和分支选项
- 📋 **场景体检面板** - AI 驱动的场景分析，带缓存机制
- 👥 **角色档案管理** - 集中管理角色信息和关系

#### ⚡ 动态状态系统
- **基于效果的变更** - 定义角色/世界/关系变化
- **路径试玩模式** - 故事推进时实时状态可视化
- **状态查看器** - 查询任意已保存线程中任意点的完整状态
- **时序回放** - 倒带和重放状态变化

#### 🤖 AI 集成
- **多模型支持** - DeepSeek、OpenAI、Anthropic、Google、Ollama
- **LangGraph 代理** - 自然语言查询和分析
- **语义搜索** - FAISS向量检索
- **Token 管理** - 内置用量跟踪和限额

### 🚀 快速开始

```bash
# 克隆并安装
git clone https://github.com/pj4239460/story-graph-assistant.git
cd story-graph-assistant
python -m venv venv
venv\Scripts\activate  # Linux/Mac: source venv/bin/activate
pip install -r requirements.txt

# 配置 API 密钥
copy .env.example .env
# 编辑 .env: DEEPSEEK_API_KEY=你的密钥

# 运行
streamlit run src/app.py
```

**推荐使用：** 在 [platform.deepseek.com](https://platform.deepseek.com/) 获取 DeepSeek API 密钥（性价比最高）  
也支持：OpenAI、Anthropic、Google Gemini、本地模型（Ollama）

### 📖 使用方法

1. **体验示例** - 点击侧边栏 🇨🇳/🇺🇸 按钮加载范例项目
2. **创建项目** - 点击 ➕ 新建开始你的故事
3. **添加场景** - 构建你的剧情图谱
4. **AI 分析** - 点击节点查看场景体检报告
5. **对话查询** - 用自然语言向 AI 提问

### 🏗️ 技术栈

- **Streamlit** - 交互式 Web 框架
- **LangGraph** - AI 智能体编排
- **LiteLLM** - 多提供商 LLM 路由（DeepSeek、OpenAI、Anthropic、Google、Ollama）
- **FAISS** - 向量检索（CPU 优化）
- **Pydantic** - 数据验证

### 🛣️ 开发路线

**v1.0 - 向量搜索** ✅
- [x] 基于向量的检索（FAISS - 从 ChromaDB 迁移）
- [x] 384 维嵌入的语义相似度搜索
- [x] 项目加载时自动索引
- [x] 多模型支持和模型选择 UI

**v1.5 - 动态角色状态系统** ✅
- [x] Effect 模型（作用域/目标/操作/路径/值）结构
- [x] StateService 实现时序状态计算和回放
- [x] 角色状态追踪（心情、状态、特质、目标、恐惧、自定义变量）
- [x] 关系状态追踪
- [x] 世界状态追踪（全局变量）
- [x] 效果编辑器 UI（添加/编辑/删除）
- [x] 路径试玩模式实时状态可视化
- [x] 状态查看器支持查询任意故事线步骤的状态
- [x] AI 代理状态查询工具
- [x] 示例项目包含效果演示

**v1.6 - 世界导演 MVP** ✅
- [x] Storylet 模型（前置条件 + 效果）
- [x] 7阶段选择流程（前置条件、冷却、多样性、节奏、选择、效果、记录）
- [x] DirectorService 实现
- [x] TickHistory 跟踪
- [x] 强度控制系统
- [x] 世界导演 UI
- [x] 完整测试覆盖

**v1.7.1 - 排序约束 + 备选机制** ✅
- [x] 排序约束（requires_fired、forbids_fired）
- [x] 备选机制（is_fallback、fallback_after_idle_ticks）
- [x] 空闲tick跟踪（idle_tick_count）
- [x] 增强UI显示（排序标记、空闲计数器）
- [x] 综合测试套件
- [x] 完整文档更新

**v1.7.2 - 动作序列** 🔄（开发中）
- [ ] 多步动作链（选择 → 动作序列 → 结果）
- [ ] 条件性动作分支
- [ ] 动作状态跟踪
- [ ] 动作可视化UI

**v1.8 - UI/UX 增强**
- [ ] Storylet 编辑器UI
- [ ] 可视化流程设计器
- [ ] 增强的历史浏览器
- [ ] 导出/导入功能

**v1.9 - 创作工具**
- [ ] Storylet 模板库
- [ ] AI 辅助的 storylet 生成
- [ ] 平衡和测试工具
- [ ] 叙事分析仪表板

**v2.0 - 高级分析与模拟**
- [ ] 角色弧分析
- [ ] 路线分析与状态演进可视化
- [ ] 情感节奏分析
- [ ] 高级假设模拟
- [ ] 一致性报告和验证

### 📚 文档

- [入门指南（中文）](GETTING_STARTED.zh.md)
- [入门指南（英文）](GETTING_STARTED.en.md)
- [开发者指南（英文）](docs/developer_guide.en.md)
- [世界导演指南（英文）](docs/world_director_guide.md)
- [世界导演指南（中文）](docs/world_director_guide.zh.md)

---

## 📝 License

MIT License - Copyright (c) 2025 Ji PEI

See [LICENSE](LICENSE) file for details.

---

## 👤 Author

**Ji PEI**

- GitHub: [@pj4239460](https://github.com/pj4239460)
- Email: pj4239460@gmail.com
- Project Link: [https://github.com/pj4239460/story-graph-assistant](https://github.com/pj4239460/story-graph-assistant)

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 🙏 Acknowledgments

- [Streamlit](https://streamlit.io/) - For the amazing web framework
- [LangGraph](https://github.com/langchain-ai/langgraph) - For agent orchestration
- [DeepSeek](https://www.deepseek.com/) - For powerful AI models
- [LiteLLM](https://github.com/BerriAI/litellm) - For unified LLM interface
- [FAISS](https://github.com/facebookresearch/faiss) - For efficient vector search

---

**Made with ❤️ by Ji PEI for narrative game developers worldwide**
