# Story Graph Assistant / 故事图谱助手

> **Visual AI assistant for branching game stories.**  
> **用图谱 + AI，捋清你的分支剧情。**

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

A powerful tool for narrative game developers to manage complex branching stories with AI-powered analysis and scene validation.

**[English](#english)** | **[中文](#中文)**

---

## English

### ✨ Features

- 🌳 **Interactive Story Graph** - Drag-and-drop visualization with multiple layouts
- ✏️ **Full Editing Support** - Edit scenes, characters, and choices with inline forms
- 📋 **Scene Checkup Panel** - AI-powered comprehensive scene analysis with caching
- 👥 **Character Management** - Centralized profiles and relationships
- ⚡ **Dynamic Character States** - Effect-based state mutation system with temporal replay
  - Define Effects to change character mood, traits, goals, relationships, and world variables
  - Play Path mode shows real-time state changes as story progresses
  - State Viewer shows complete character state at any point in saved threads
  - AI agent tools for querying character states and relationships
- 🤖 **AI Agent Assistant** - LangGraph-powered conversational queries with FAISS semantic search
- 🅱️ **Multi-LLM Support** - Works with DeepSeek, OpenAI, Anthropic, Google, local models via LiteLLM
- 📚 **Sample Projects** - One-click Chinese/English example stories with dynamic state examples
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

1. **Try Samples** - Click 🇨🇳/🇺🇸 buttons in sidebar for example projects
2. **Create Project** - Click ➕ New to start your story
3. **Add Scenes** - Build your story graph with scenes and choices
4. **AI Analysis** - Click nodes to view Scene Checkup with AI insights
5. **Chat** - Ask AI questions about your story in natural language

### 🏗️ Tech Stack

- **Streamlit** - Interactive web framework
- **LangGraph** - AI agent orchestration
- **LiteLLM** - Multi-provider LLM routing (DeepSeek, OpenAI, Anthropic, Google, Ollama)
- **FAISS** - Vector search (CPU-optimized)
- **Pydantic** - Data validation

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

**v2.0 - Advanced Analytics & Simulation**
- [ ] Character arc analysis
- [ ] Route analysis with state progression visualization
- [ ] Emotional pacing analysis
- [ ] Advanced What-if simulation
- [ ] Consistency reports and validation

### 📚 Documentation

- [Getting Started Guide](GETTING_STARTED.en.md)
- [Developer Guide](docs/developer_guide.en.md)

---

## 中文

### ✨ 功能特色

- 🌳 **交互式剧情图谱** - 拖拽可视化，多种布局算法
- ✏️ **完整编辑功能** - 内联表单编辑场景、角色和分支选项
- 📋 **场景体检面板** - AI 驱动的场景分析，带缓存机制
- 👥 **角色档案管理** - 集中管理角色信息和关系
- ⚡ **动态角色状态系统** - 基于效果（Effect）的状态变更系统，支持时序回放
  - 定义效果来改变角色心情、特质、目标、关系和世界变量
  - 路径试玩模式实时显示剧情推进时的状态变化
  - 状态查看器可查询任意已保存故事线中的完整角色状态
  - AI 代理工具支持查询角色状态和关系
- 🤖 **AI 智能助手** - LangGraph 对话代理，支持自然语言查询，基于 FAISS 语义搜索
- 🅱️ **多模型支持** - 通过 LiteLLM 支持 DeepSeek、OpenAI、Anthropic、Google、本地模型
- 📚 **示例项目** - 一键加载中英文范例故事，包含动态状态演示
- 🌍 **双语界面** - 完整中英文 UI，动态切换
- 💾 **简洁存储** - 基于 JSON 的可移植项目文件

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

**v2.0 - 高级分析与模拟**
- [ ] 角色弧分析
- [ ] 路线分析与状态演进可视化
- [ ] 情感节奏分析
- [ ] 高级假设模拟
- [ ] 一致性报告和验证

### 📚 文档

- [入门指南](GETTING_STARTED.zh.md)
- [开发者指南](docs/developer_guide.zh.md)

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
