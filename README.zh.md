# 故事图谱助手（Story Graph Assistant）

> 用图谱和 AI 来管理游戏剧情与世界观的创作助手。

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

故事图谱助手专为剧情游戏 / 视觉小说 / 网状叙事设计，帮助你管理复杂的分支剧情和角色设定。

**文档**: [English](README.md) | [中文](#)  
**完整文档**: [English](GETTING_STARTED.en.md) | [中文](GETTING_STARTED.zh.md)  
**开发者指南**: [English](docs/developer_guide.en.md) | [中文](docs/developer_guide.zh.md)

---

## ✨ 核心功能

### 1. **交互式剧情图谱**
- 🌳 基于 Streamlit Flow 的可视化流程图
- 🖱️ 拖拽节点自由排列
- 📐 多种布局算法（树形、分层、力导向、手动）
- 🔍 缩放、平移、小地图导航
- 💡 点击节点查看详细信息
- 📊 实时统计面板（场景数、结局数、选择数）

### 2. **角色档案管理**
- 集中管理角色描述、性格特征、目标和恐惧
- 记录角色间的关系
- 快速查找和编辑角色信息
- 场景中角色参与度追踪

### 3. **AI 智能分析**
- **场景摘要生成**：自动生成场景内容的简洁摘要
- **设定提取**：从场景中提取世界观信息和关键剧情点
- **OOC 检测**：检查角色行为是否符合人设
- Token 使用量跟踪和限额管理

### 4. **双语界面与配置**
- 🌐 完整的中英文双语界面，动态语言切换
- ⚙️ **可配置设置**：自定义 AI Token 限额和模型选择
- 🕒 **最近项目**：快速访问最近打开的项目
- 🎯 130+ 翻译键值覆盖所有 UI 文本

### 5. **本地优先架构**
- 基于 JSON 的简单存储格式
- 无需数据库配置
- 易于版本控制和备份

---

## 🚀 快速开始

### 环境要求
- Python 3.10+
- DeepSeek API Key（[申请地址](https://platform.deepseek.com/)）

### 安装步骤

```bash
# 克隆仓库
git clone https://github.com/pj4239460/story-graph-assistant.git
cd story-graph-assistant

# 创建虚拟环境
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
copy .env.example .env
# 编辑 .env 文件，填入你的 DEEPSEEK_API_KEY
```

### 运行应用

```bash
streamlit run src/app.py
```

在浏览器中打开 `http://localhost:8501`

---

## 🏗️ 技术栈

- **Streamlit**：快速搭建交互式 Web 应用
- **Streamlit Flow**：基于 React Flow 的交互式流程图组件
- **Pydantic**：数据验证和序列化
- **LiteLLM**：统一的 LLM 接口，支持 DeepSeek 等多个模型
- **JSON**：轻量级本地存储

---

## 📖 文档

- [快速开始指南](GETTING_STARTED.zh.md)
- [开发者指南](docs/developer_guide.zh.md)

---

## 🛣️ 开发路线图

**v0.1 - MVP（当前版本）**
- [x] 项目管理（创建、加载、保存）
- [x] 场景管理（增删改查）
- [x] 角色管理（增删改查）
- [x] 交互式流程图可视化（Streamlit Flow）
- [x] 多种图布局算法
- [x] 统计仪表板
- [x] AI 场景摘要生成
- [x] AI 设定提取
- [x] AI OOC 检测
- [x] Token 使用跟踪
- [x] 完整双语支持（中英文）

**v0.3 - RAG 基础**
- [ ] 时间轴视图
- [ ] 关键词检索
- [ ] 世界观问答
- [ ] 多场景 OOC 检查

**v1.0 - 完整 RAG**
- [ ] 向量检索（FAISS/Chroma）
- [ ] 角色弧光分析
- [ ] 路线分析
- [ ] 情感节奏分析

**v2.0 - 世界推演**
- [ ] WorldState 和 StoryThread
- [ ] 高级 What-if 推演
- [ ] 一致性报告

---

## 📄 许可证

MIT License

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

**口号**：*「用图谱 + AI，捋清你的分支剧情。」*
