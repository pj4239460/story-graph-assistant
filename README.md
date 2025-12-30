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
- 📋 **Scene Checkup Panel** - AI-powered comprehensive scene analysis with caching
- 👥 **Character Management** - Centralized profiles and relationships
- 🤖 **AI Agent Assistant** - LangGraph-powered conversational queries with FAISS semantic search
- 📚 **Sample Projects** - One-click Chinese/English example stories
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

Get your free DeepSeek API key at [platform.deepseek.com](https://platform.deepseek.com/)

### 📖 Usage

1. **Try Samples** - Click 🇨🇳/🇺🇸 buttons in sidebar for example projects
2. **Create Project** - Click ➕ New to start your story
3. **Add Scenes** - Build your story graph with scenes and choices
4. **AI Analysis** - Click nodes to view Scene Checkup with AI insights
5. **Chat** - Ask AI questions about your story in natural language

**v1.0 - Vector Search** ✅ 
- [x] Vector-based retrieval (FAISS - migrated from ChromaDB)
- [x] Semantic similarity search with 384-dim embeddings
- [x] Auto-indexing on project load
- [ ] Character arc analysis
- [ ] Route analysis
- [ ] Emotional pacing

**v2.0 - World Simulation**
- [ ] WorldState & StoryThread
- [ ] Advanced What-if simulation
- [ ] Consistency reports

---

## 中文

### ✨ Features

- 🌳 **交互式剧情图谱** - 基于 Streamlit Flow 的可视化流程图
- 📊 **统计面板** - 实时场景、结局、选择统计
- 👥 **角色档案** - 集中管理角色特征、目标和关系
- 🤖 **AI 智能分析**
  - 场景摘要生成
  - 世界观设定提取
  - OOC（人设崩坏）检测
  - 与故事对话（基于关键词检索的 RAG）
- 🌍 **双语界面** - 完整的中英文支持和动态切换
- 💬 **聊天历史** - SQLite 持久化存储
- 💾 **本地优先存储** - 简单的 JSON 项目文件

### 🚀 Quick Start

#### Prerequisites
- Python 3.10+
- DeepSeek API Key ([Get one here](https://platform.deepseek.com/))

#### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/story-graph-assistant.git
cd story-graph-assistant

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your DEEPSEEK_API_KEY
```

#### Run the Application

```bash
streamlit run src/app.py
```

Open your browser at `http://localhost:8501`

### 🏗️ Tech Stack

- **Streamlit** - Interactive web framework
- **LangGraph** - AI agent orchestration
- **DeepSeek** - LLM provider
- **FAISS** - Vector search (CPU-optimized)
- **Pydantic** - Data validation

### 🛣️ Roadmap

- [x] Interactive graph with drag-and-drop
- [x] Scene Checkup panel with AI analysis
- [x] Sample projects (Chinese/English)
- [x] Vector search with FAISS
- [x] Chat history with SQLite
- [ ] Play Path feature (experience player routes)
- [ ] Timeline view
- [ ] Multi-scene consistency checking

---

## 中文

### ✨ 功能特色

- 🌳 **交互式剧情图谱** - 拖拽可视化，多种布局算法
- 📋 **场景体检面板** - AI 驱动的场景分析，带缓存机制
- 👥 **角色档案管理** - 集中管理角色信息和关系
- 🤖 **AI 智能助手** - LangGraph 对话代理，支持自然语言查询
- 📚 **示例项目** - 一键加载中英文范例故事
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

在 [platform.deepseek.com](https://platform.deepseek.com/) 获取免费 API 密钥

### 📖 使用方法

1. **体验示例** - 点击侧边栏 🇨🇳/🇺🇸 按钮加载范例项目
2. **创建项目** - 点击 ➕ 新建开始你的故事
3. **添加场景** - 构建你的剧情图谱
4. **AI 分析** - 点击节点查看场景体检报告
5. **对话查询** - 用自然语言向 AI 提问

### 🏭️ 技术栈

- **Streamlit** - 交互式 Web 框架
- **LangGraph** - AI 智能体编排
- **DeepSeek** - 大语言模型
- **FAISS** - 向量检索（CPU 优化）
- **Pydantic** - 数据验证

### 🛣️ 开发路线

- [x] 可交互图谱，支持拖拽
- [x] 场景体检面板（AI 分析）
- [x] 中英文示例项目
- [x] FAISS 向量搜索
- [x] SQLite 聊天记录
- [ ] 路径试玩功能
- [ ] 时间线视图
- [ ] 多场景一致性检查

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
- [FAISS](https://github.com/facebookresearch/faiss) - For efficient vector search

---

**Made with ❤️ by Ji PEI for narrative game developers worldwide**
