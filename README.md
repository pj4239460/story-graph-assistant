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

#### 🎬 World Director (v0.8 Current)
Our **differentiated approach** to narrative design - move beyond manual branching and AI NPCs:

**Core System:**
- **Storylets System** - Define reusable narrative fragments with preconditions and effects
- **Quality-Based Narrative (QBN)** - Story emerges from state + rules, not manual branching
- **AI Director Pacing** - Automatic intensity control with peaks-and-valleys (inspired by Left 4 Dead)
- **Deterministic Selection** - Same state + config = same result (fully reproducible)
- **Explainable Decisions** - Every world tick includes human-readable rationale
- **Replayable History** - Complete tick-by-tick record with state diffs

**Advanced Features:**
- **Ordering Constraints** - Define narrative sequence dependencies (requires/forbids storylets)
- **Fallback Mechanism** - Prevents "world stuck" - triggers ambient storylets when no regular events qualify
- **Idle Detection** - Automatically tracks consecutive ticks with no activity
- **Complex Quest Chains** - Build multi-stage narratives with explicit ordering requirements

**New in v0.8 (Current):**
- **✏️ Storylet Editor** - Visual interface for creating/editing storylets without JSON editing
- **Search & Filter** - Find storylets by keyword, type, or property
- **Dynamic Forms** - Add/remove conditions and effects with user-friendly forms
- **Real-time Validation** - Instant feedback on storylet configuration
- **Enhanced Examples** - 3 new demo projects (wuxia RPG, sci-fi adventure, romance sim)

**🚀 Planned for v0.9 (AI Enhancement):**
- **Natural Language Conditions** - Write preconditions in natural language (e.g., "The player is wealthy and trusted")
- **AI-Assisted Mode** - Hybrid evaluation: rules for performance, AI for nuanced judgment
- **Three Director Modes:**
  - 🔧 **Deterministic** - Pure rule-based (current system, fastest)
  - 🤖 **AI-Assisted** - Mix of rules + AI conditions (balanced)
  - 🧠 **AI-Primary** - AI-driven decisions with rule validation (most flexible)
- **Smart Caching** - AI evaluation results cached by state hash (cost optimization)
- **Token Management** - Built-in usage tracking and limits
- **Explainable AI** - Confidence scores + reasoning for every AI decision

#### 📝 Story Building
- 🌳 **Interactive Story Graph** - Drag-and-drop visualization with multiple layouts
- ✏️ **Full Editing Support** - Edit scenes, characters, storylets, and choices with inline forms
- 📋 **Scene Checkup Panel** - AI-powered comprehensive scene analysis with caching
- 👥 **Character Management** - Centralized profiles and relationships
- ✏️ **Storylet Editor** - Visual storylet creation with search, filter, and form-based editing

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
1. **Load Example** - Try "wuxia_rpg", "scifi_adventure", or "romance_sim" example projects
2. **View Storylets** - Navigate to **✏️ Storylets** tab to browse/create narrative fragments
3. **Use Editor** - Create new storylets with the visual form (no JSON needed)
4. **Configure Director** - In **🎬 World Director** tab, set events/tick, pacing, diversity
5. **Run Tick** - Watch the Director select and trigger storylets based on state
6. **Review History** - Explore tick-by-tick evolution with complete rationale

### 🏗️ Tech Stack

- **Streamlit** - Interactive web framework
- **LangGraph** - AI agent orchestration
- **LiteLLM** - Multi-provider LLM routing (DeepSeek, OpenAI, Anthropic, Google, Ollama)
- **FAISS** - Vector search (CPU-optimized)
- **Pydantic V2** - Data validation and serialization

### 🛣️ Roadmap

**v0.3 - Vector Search** ✅
- [x] Vector-based retrieval (FAISS)
- [x] Semantic similarity search with 384-dim embeddings
- [x] Auto-indexing on project load
- [x] Multi-LLM support (DeepSeek, OpenAI, Anthropic, Google, Ollama)

**v0.4 - Dynamic States** ✅
- [x] Effect model (scope/target/operation/path/value)
- [x] StateService for temporal computation
- [x] Character/World/Relationship state tracking
- [x] Effects editor UI
- [x] Play Path mode with real-time visualization
- [x] State Viewer and AI agent tools

**v0.5 - World Director MVP** ✅
- [x] Storylet model (preconditions + effects)
- [x] ConditionsEvaluator (deterministic checking)
- [x] DirectorService (7-stage pipeline)
- [x] World Director UI
- [x] Comprehensive test suite

**v0.7 - Ordering & Fallback** ✅
- [x] Ordering constraints (requires_fired, forbids_fired)
- [x] Fallback mechanism (prevents world stuck)
- [x] Idle tick tracking
- [x] Enhanced UI and complete tests
- [x] Full documentation

**v0.8 - Polish & Examples** ✅ (Current)
- [x] Improved storylet editor UI (Visual editor with search/filter)
- [x] More example projects (3 new: wuxia RPG, sci-fi adventure, romance sim)
- [x] Chinese developer guide translation
- [x] Complete documentation update

**v0.9 - AI Enhancement** (In Development)
- [x] Natural language conditions (Precondition.nl_condition field)
- [x] AIConditionsEvaluator service (350 lines, LLM-powered)
- [x] Three director modes (deterministic/ai_assisted/ai_primary)
- [x] Hybrid evaluation engine (rules + AI)
- [x] Smart caching with state hash
- [x] Token management and limits
- [x] AI mode selector UI
- [x] Bilingual i18n (9 new keys)
- [ ] Documentation updates (in progress)
- [ ] Example NL condition storylets
- [ ] Testing and validation
- [ ] Performance benchmarks
- [ ] Community feedback and refinement
- [ ] Tutorial content

**Future Enhancements** (Long-term Vision)
- [ ] AI-generated storylets (LLM creates storylets dynamically)
- [ ] Natural language effects ("Increase player trust")
- [ ] Timeline visualization (state evolution graph)
- [ ] Batch AI evaluation (optimize multi-condition checks)
- [ ] Multiplayer state synchronization
- [ ] Visual node-based storylet editor
- [ ] Plugin system for custom evaluators
- [ ] Export to game engines (Unity/Godot)

### 📚 Documentation

- [Getting Started Guide](GETTING_STARTED.en.md) - Quick start tutorial
- [World Director Guide](docs/world_director_guide.md) - Comprehensive storylets reference
- [AI Director Guide](docs/AI_DIRECTOR_GUIDE.md) - AI-enhanced narrative features (v0.9+)
- [Developer Guide](docs/developer_guide.en.md) - System architecture and internals
- [Agent Development Guide](docs/agent_guide.en.md) - Extending AI capabilities
- [Documentation Index](docs/INDEX.md) - Complete documentation overview

### 🎮 Example Projects

- **sample_project/** - Time travel story (Chinese)
- **sample_project_en/** - Time travel story (English)
- **wuxia_rpg/** - Martial arts RPG (15 scenes, 5 endings, moral choices)
- **scifi_adventure/** - Quantum paradox adventure (25 scenes, 12 endings, AI ethics)
- **romance_sim/** - School romance (19 scenes, 4 endings, 3 routes)
- **town_factions/** - World Director faction politics demo

---

## 中文

### ✨ 功能特色

#### 🎬 世界导演系统 (v0.8 当前版本)
我们的**差异化叙事设计方法** - 超越手工分支和AI NPC：

**核心系统：**
- **Storylets 系统** - 定义可复用的叙事片段，包含前置条件和效果
- **质量驱动叙事（QBN）** - 故事从状态+规则中涌现，而非手工分支
- **AI 导演节奏控制** - 自动强度控制，峰谷交替（受 Left 4 Dead 启发）
- **确定性选择** - 相同状态+配置=相同结果（完全可重现）
- **可解释决策** - 每次世界tick都包含人类可读的选择理由
- **可回放历史** - 完整的逐tick记录，包含状态差异

**高级功能：**
- **排序约束** - 定义叙事序列依赖（requires/forbids storylets）
- **备选机制** - 防止"世界卡住" - 当常规事件无法触发时，触发氛围storylets
- **空闲检测** - 自动跟踪连续无活动的ticks
- **复杂任务链** - 用显式排序要求构建多阶段叙事

**v0.8 新功能（当前版本）：**
- **✏️ Storylet编辑器** - 可视化界面，无需手写JSON
- **搜索与过滤** - 按关键词、类型或属性查找storylets
- **动态表单** - 用户友好的条件和效果添加/删除
- **实时验证** - 即时配置反馈
- **增强示例** - 3个新演示项目（武侠RPG、科幻冒险、校园恋爱）

**🚀 v0.9 计划（AI增强）：**
- **自然语言条件** - 用自然语言编写前置条件（如"玩家富有且受信任"）
- **AI辅助模式** - 混合评估：规则保证性能，AI处理细腻判断
- **三种导演模式：**
  - 🔧 **确定性** - 纯规则（当前系统，最快）
  - 🤖 **AI辅助** - 规则+AI条件混合（平衡）
  - 🧠 **AI主导** - AI驱动决策+规则验证（最灵活）
- **智能缓存** - 按状态哈希缓存AI评估结果（成本优化）
- **Token管理** - 内置用量追踪和限额
- **可解释AI** - 每个AI决策都包含置信度+推理

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

### 🛣️ 开发路线

**v0.3 - 向量搜索** ✅
- [x] 基于向量的检索（FAISS）
- [x] 384 维嵌入的语义相似度搜索
- [x] 项目加载时自动索引
- [x] 多模型支持（DeepSeek、OpenAI、Anthropic、Google、Ollama）

**v0.4 - 动态状态系统** ✅
- [x] Effect 模型（作用域/目标/操作/路径/值）
- [x] StateService 时序状态计算
- [x] 角色/世界/关系状态追踪
- [x] 效果编辑器 UI
- [x] 路径试玩模式实时可视化

**v0.5 - 世界导演 MVP** ✅
- [x] Storylet 系统（前置条件 + 效果）
- [x] 7阶段选择流程
- [x] DirectorService 实现
- [x] TickHistory 和强度控制
- [x] 世界导演 UI

**v0.7 - 排序约束 + 备选机制** ✅
- [x] 排序约束（requires_fired、forbids_fired）
- [x] 备选机制（防止世界卡住）
- [x] 空闲tick跟踪
- [x] 增强UI和完整测试
- [x] 完整文档

**v0.8 - 完善与示例** ✅（当前版本）
- [x] Storylet 编辑器UI改进（可视化编辑器+搜索/过滤）
- [x] 更多示例项目（3个新项目：武侠RPG、科幻冒险、校园恋爱）
- [x] 中文开发者指南翻译
- [x] 完整文档更新

**v0.9 - AI增强** （开发中）
- [x] 自然语言条件（Precondition.nl_condition字段）
- [x] AIConditionsEvaluator服务（350行，LLM驱动）
- [x] 三种导演模式（deterministic/ai_assisted/ai_primary）
- [x] 混合评估引擎（规则+AI）
- [x] 基于状态哈希的智能缓存
- [x] Token管理和限额
- [x] AI模式选择器UI
- [x] 双语i18n（9个新键）
- [ ] 文档更新（进行中）
- [ ] NL条件示例storylets
- [ ] 测试和验证
- [ ] 性能基准测试
- [ ] 社区反馈和改进
- [ ] 教程内容

**未来功能** （长期愿景）
- [ ] AI生成storylets（LLM动态创建storylets）
- [ ] 自然语言效果（"增加玩家信任度"）
- [ ] 时间线可视化（状态演化图）
- [ ] 批量AI评估（优化多条件检查）
- [ ] 多人状态同步
- [ ] 可视化节点编辑器
- [ ] 自定义评估器插件系统
- [ ] 导出到游戏引擎（Unity/Godot）

### 📚 文档

**核心文档：**
- [入门指南（中文）](GETTING_STARTED.zh.md) - 快速上手
- [入门指南（英文）](GETTING_STARTED.en.md) - Quick Start
- [开发者指南](docs/developer_guide.en.md) - 架构与API文档
- [世界导演指南（英文）](docs/world_director_guide.md) - Storylet系统深度解析
- [世界导演指南（中文）](docs/world_director_guide.zh.md) - Storylet系统中文详解

**完整索引：** [docs/INDEX.md](docs/INDEX.md)

---

## 📝 License

MIT License - Copyright (c) 2026 Ji PEI

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
