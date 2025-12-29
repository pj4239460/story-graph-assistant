# Story Graph Assistant / 故事图谱助手

> **Visual AI assistant for branching game stories.**  
> **用图谱 + AI，捋清你的分支剧情。**

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

A powerful tool for narrative game developers to manage complex branching stories with AI-powered analysis.

**Documentation**: [English](#english) | [中文](#中文)  
**Full Docs**: [English](GETTING_STARTED.en.md) | [中文](GETTING_STARTED.zh.md)  
**Developer Guide**: [English](docs/developer_guide.en.md) | [中文](docs/developer_guide.zh.md)

---

## English

### ✨ Features

- 🌳 **Interactive Story Graph** - Powered by Streamlit Flow
  - Drag-and-drop node repositioning
  - Multiple layouts (Tree, Layered, Force, Manual)
  - Zoom, pan, and minimap navigation
  - Click nodes to view details
- 📊 **Story Analytics Dashboard** - Real-time statistics for scenes, endings, and choices
- 👥 **Character Management** - Centralized character profiles and relationships
- 🤖 **AI-Powered Analysis**
  - Scene summarization
  - World-building fact extraction
  - Out-of-Character (OOC) detection
- 🌍 **Bilingual Interface** - Full Chinese/English support with dynamic language switching
- ⚙️ **Configurable Settings** - Customize AI token limits and model selection
- 🕒 **Recent Projects** - Quickly access your recently opened projects
- 💾 **JSON-based Storage** - Simple, portable project files

### 🚀 Quick Start

#### Prerequisites
- Python 3.10+
- DeepSeek API Key ([Get one here](https://platform.deepseek.com/))

#### Installation

```bash
# Clone the repository
git clone https://github.com/pj4239460/story-graph-assistant.git
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

### 📖 Documentation

- [Getting Started Guide](GETTING_STARTED.en.md)
- [Developer Guide](docs/developer_guide.en.md)

### 🛣️ Roadmap

**v0.1 - MVP (Current)**
- [x] Project management (create, load, save)
- [x] Scene management (CRUD)
- [x] Character management (CRUD)
- [x] AI scene summarization
- [x] AI fact extraction
- [x] AI OOC detection
- [x] Token usage tracking

**v0.3 - RAG Foundation**
- [ ] Timeline view
- [ ] Keyword-based retrieval
- [ ] World Q&A
- [ ] Multi-scene OOC checking

**v1.0 - Full RAG**
- [ ] Vector-based retrieval (FAISS/Chroma)
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
- 🌍 **双语界面** - 完整的中英文支持和动态切换
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

- **Streamlit** - Fast interactive web application framework
- **Pydantic** - Data validation and serialization
- **LiteLLM** - Unified LLM interface supporting DeepSeek and more
- **JSON** - Lightweight local storage

### 📖 Documentation

- [Getting Started Guide](GETTING_STARTED.en.md)
- [Developer Guide](docs/developer_guide.en.md)

### 🛣️ Roadmap

**v0.1 - MVP (Current)**
- [x] Project management (create, load, save)
- [x] Scene management (CRUD)
- [x] Character management (CRUD)
- [x] AI scene summarization
- [x] AI fact extraction
- [x] AI OOC detection
- [x] Token usage tracking

**v0.3 - RAG Foundation**
- [ ] Timeline view
- [ ] Keyword-based retrieval
- [ ] World Q&A
- [ ] Multi-scene OOC checking

**v1.0 - Full RAG**
- [ ] Vector-based retrieval (FAISS/Chroma)
- [ ] Character arc analysis
- [ ] Route analysis
- [ ] Emotional pacing

**v2.0 - World Simulation**
- [ ] WorldState & StoryThread
- [ ] Advanced What-if simulation
- [ ] Consistency reports

---

## 📝 License

MIT License

---

## 🤝 Contributing

Contributions are welcome! Feel free to open issues and pull requests.

---

**Made with ❤️ for narrative game developers**
