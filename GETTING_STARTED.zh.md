# 快速上手指南

## 安装

### 环境要求
- Python 3.10+
- LLM API 密钥（支持多种提供商）
  - DeepSeek：[免费获取](https://platform.deepseek.com/)
  - OpenAI：[API Keys](https://platform.openai.com/api-keys)
  - Anthropic Claude：[Console](https://console.anthropic.com/)
  - Google Gemini：[AI Studio](https://aistudio.google.com/)
  - 或使用本地模型（Ollama, LM Studio 等）

### 安装步骤

```bash
# 1. 克隆仓库
git clone https://github.com/pj4239460/story-graph-assistant.git
cd story-graph-assistant

# 2. 创建虚拟环境
python -m venv venv
venv\Scripts\activate  # Linux/Mac: source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置 API 密钥
copy .env.example .env
# 编辑 .env 文件，设置：
# DeepSeek: DEEPSEEK_API_KEY=sk-...
# OpenAI: OPENAI_API_KEY=sk-...
# Anthropic: ANTHROPIC_API_KEY=sk-ant-...
# Google: GEMINI_API_KEY=...
# 本地模型: 无需密钥，直接使用 ollama/模型名

# 5. 运行应用
streamlit run src/app.py
```

浏览器将自动打开 `http://localhost:8501`

## 第一步

### 1. 体验示例项目

点击侧边栏的示例按钮：
- 🇨🇳 **中文** - 中文时间旅行者故事
- 🇺🇸 **EN** - 英文时间旅行者故事

这将加载一个包含 3 个场景、2 个角色和分支选择的完整示例。

### 2. 探索界面

**标签页：**
- **📍 路线图** - 交互式剧情图谱
- **👤 角色** - 角色档案管理
- **🔧 AI 工具** - 场景分析工具
- **💬 对话** - 向 AI 提问
- **⚙️ 设置** - 配置 AI 模型和限额

### 3. 查看场景详情

点击图谱中的任意节点查看：
- **内容** - 场景文本和选项
- **AI 体检** - 综合分析（情感、事实、质量洞察）
- **元数据** - 技术细节

### 4. 创建自己的项目

1. 点击侧边栏的 **➕ 新建**
2. 输入项目名称并选择语言
3. 添加第一个场景
4. 通过添加选项和连接场景来构建故事

### 5. 体验世界导演（新功能！v1.6）

体验用"故事片段"创造涌现式叙事：

1. 加载 **"河湾镇"** 示例（即将推出）或创建带有 storylets 的项目
2. 导航到 **🎬 世界导演** 标签页
3. 创建故事线程（或选择已存在的）
4. 配置导演设置：
   - **每 Tick 事件数**：触发几个 storylet（1-5）
   - **节奏偏好**：平静/平衡/紧张
   - **多样性惩罚**：避免重复的程度（0-100%）
5. 点击 **▶️ 运行 Tick** 让世界演化
6. 查看结果：
   - 看哪些 storylet 被选中以及为什么
   - 查看应用的效果和状态变化
   - 探索强度指标
7. 运行多个 tick 观察涌现的故事发展

**世界导演有什么不同？**
- **无需手工分支**：定义 storylets（条件 + 效果），让系统自动组合
- **确定性**：相同状态 + 配置 = 相同结果（完全可重现）
- **可解释**：每个决定都有人类可读的理由
- **可回放**：完整历史，每个 tick 都有状态差异对比

## 核心功能

### 完整的编辑功能 ✅

**场景编辑：**
- 点击场景右侧的 ✏️ 按钮打开编辑表单
- 可编辑：标题、内容、章节、摘要、时间标签、是否结局
- 保存后自动更新图谱显示

**角色编辑：**
- 点击角色右侧的 ✏️ 按钮打开编辑表单
- 可编辑：名称、别名、描述、性格特征、目标、恐惧
- 特征/目标/恐惧支持多行输入（每行一个）

**分支选项编辑：**
- 在场景详情中，每个选项旁有 ✏️ 按钮
- 可编辑选项文本和目标场景
- 支持添加新选项和删除现有选项
- 目标场景支持下拉选择或设置为"无（结束）"

### 场景体检面板

AI 驱动的分析包括：
- **摘要** - 简洁的场景概述
- **事实** - 提取的世界观信息
- **情感** - 检测到的情感基调
- **OOC 风险** - 角色一致性警告（即将推出）

结果会被缓存以提高性能。点击 🔄 刷新可重新生成。

### AI 对话助手

基于 LiteLLM 的多模型支持，自然语言查询：
- "故事中有几个角色？"
- "scene-001 中提到了谁？"
- "故事有几个结局？"

使用 FAISS 语义搜索实现准确检索。

**支持的 LLM 提供商（截至 2025-12-31）：**
- 🚀 **DeepSeek** - 性价比最高，推荐使用
  - `deepseek-chat` (对话)
  - `deepseek-reasoner` (推理)
- 🧠 **OpenAI** - 最新GPT系列
  - GPT-5 系列: `gpt-5.2`, `gpt-5.2-pro`, `gpt-5-mini`
  - o 推理系列: `o3`, `o3-pro`, `o4-mini`
  - GPT-4.x: `gpt-4.1`, `gpt-4o`, `gpt-4o-mini`
- 🤖 **Anthropic** - Claude 4.5 最新系列
  - Claude 4.5: `claude-sonnet-4-5`, `claude-opus-4-5`, `claude-haiku-4-5`
  - Claude 3.x: `claude-3-7-sonnet-latest`, `claude-3-5-haiku-latest`
- 🌎 **Google** - Gemini 2.5/3.0 系列
  - Gemini 3: `gemini-3-pro-preview`, `gemini-3-flash-preview`
  - Gemini 2.5: `gemini-2.5-pro`, `gemini-2.5-flash`
  - Gemini 2.0: `gemini-2.0-flash`
- 💻 **本地模型** - Ollama 最新版本
  - Llama: `ollama/llama3.3`, `ollama/llama3.2`
  - Qwen: `ollama/qwen2.5`
  - 其他: `ollama/mistral`, `ollama/deepseek-coder-v2`, `ollama/gemma2`, `ollama/phi4`

**配置示例：**
```bash
# .env 文件
# 使用 DeepSeek（推荐）
DEEPSEEK_API_KEY=sk-...

# 或使用 OpenAI GPT-5
OPENAI_API_KEY=sk-...
# 在设置中选择模型: gpt-5.2 / gpt-5-mini / o3

# 或使用 Claude 4.5
ANTHROPIC_API_KEY=sk-ant-...
# 在设置中选择: claude-sonnet-4-5 / claude-opus-4-5

# 或使用 Gemini 2.5/3.0
GEMINI_API_KEY=AIza...
# 在设置中选择: gemini-2.5-pro / gemini-3-flash-preview

# 或使用本地 Ollama（无需 API Key）
# 1. 安装 Ollama: https://ollama.ai/
# 2. 拉取模型: ollama pull llama3.3
# 3. 在设置中选择: ollama/llama3.3
```

在应用的「⚙️ 设置」标签页中，可以选择不同的模型。LiteLLM 会自动识别模型格式并路由到对应的提供商。

### 项目管理

- **最近项目** - 快速访问最近的文件
- **JSON 存储** - 简单、可移植、适合版本控制
- **自动保存** - 更改自动保存

## 使用技巧

1. **使用标签** - 用 "战斗"、"恋爱"、"线索" 等标签组织场景
2. **角色 ID** - 使用一致的 ID（char-001, char-002）便于跟踪
3. **章节命名** - 将场景分组到章节中以便更好地组织
4. **Token 限额** - 在设置标签页监控使用量以避免超限
5. **导出分析** - 将场景体检报告下载为 JSON

## 故障排除

**API 密钥问题**
- 确认项目根目录存在 `.env` 文件
- 检查密钥格式：
  - DeepSeek: `DEEPSEEK_API_KEY=sk-...`
  - OpenAI: `OPENAI_API_KEY=sk-...`
  - Anthropic: `ANTHROPIC_API_KEY=sk-ant-...`
  - Google: `GEMINI_API_KEY=...`
- 编辑 `.env` 后重启应用

**本地模型配置**
- 使用 Ollama：先安装 [Ollama](https://ollama.ai/)，然后运行 `ollama pull llama3`
- 在设置中将模型改为 `ollama/llama3` 或 `ollama/qwen`
- LM Studio/vLLM：设置为 OpenAI 兼容模式，使用 `openai/模型名`

**FAISS 不工作**
- 应用可以在没有 FAISS 的情况下工作（回退到关键词搜索）
- 安装：`pip install faiss-cpu`

**性能慢**
- 场景体检使用缓存 - 首次运行慢，后续查看即时显示
- 点击 🔄 刷新按钮清除缓存

## 下一步

- 阅读[开发者指南](docs/developer_guide.zh.md)了解架构细节
- 在 AI 工具标签页探索 AI 功能
- 在 GitHub Issues 参与讨论

---

**需要帮助？** 在 [github.com/pj4239460/story-graph-assistant](https://github.com/pj4239460/story-graph-assistant) 提交 issue

3. **创建角色**
   - 切换到「👥 角色管理」标签页
   - 点击「➕ 新建角色」
   - 填写角色信息
   - 保存

4. **使用 AI 工具**
   - 切换到「🤖 AI 工具」标签页
   - 选择要使用的工具（场景摘要/设定提取/OOC检测）
   - 选择场景或角色
   - 点击「🚀 生成/检测」

5. **配置设置**
   - 切换到「⚙️ 设置」标签页
   - 调整 **项目总限额** (Project Token Limit)
   - 调整 **每日软限额** (Daily Soft Limit)
   - 查看模型配置

### 💡 布局小贴士

- **树形布局 (Tree)**：最适合标准的分支剧情，它会从起点开始层级化排列场景。
- **手动布局 (Manual)**：将节点重置为网格排列。如果图谱变得混乱，或者你想完全自定义排列，请使用此模式。
- **力导向布局 (Force)**：适合观察节点簇和有机连接，但在节点较多时可能不稳定。

### 加载示例项目

```powershell
# 在应用中点击「📂 加载」
# 输入路径：
./examples/sample_project/project.json
```

示例项目包含：
- 3个场景（时间旅行主题）
- 2个角色（李明、史密斯教授）
- 完整的故事开端

---

## 🏗️ 项目结构

```
story_graph_assistant/
├── src/
│   ├── app.py                  # Streamlit 主入口
│   ├── models/                 # 数据模型
│   │   ├── project.py          # 项目模型
│   │   ├── scene.py            # 场景模型
│   │   ├── character.py        # 角色模型
│   │   ├── event.py            # 事件模型
│   │   ├── world.py            # 世界状态（v2）
│   │   └── ai.py               # AI 配置
│   ├── repositories/           # 存储层
│   │   ├── base.py             # 基础接口
│   │   └── json_repo.py        # JSON 实现
│   ├── services/               # 业务逻辑
│   │   ├── project_service.py  # 项目管理
│   │   ├── scene_service.py    # 场景管理
│   │   ├── character_service.py# 角色管理
│   │   └── ai_service.py       # AI 功能
│   ├── infra/                  # 基础设施
│   │   ├── llm_client.py       # LLM 客户端
│   │   ├── token_stats.py      # Token 统计
│   │   └── i18n.py             # 国际化
│   └── ui/                     # UI 组件
│       ├── layout.py           # 主布局
│       ├── sidebar.py          # 侧边栏
│       ├── routes_view.py      # 路线视图
│       ├── characters_view.py  # 角色视图
│       └── ai_tools_view.py    # AI 工具视图
├── i18n/                       # 翻译文件
│   ├── zh.json                 # 中文
│   └── en.json                 # 英文
├── examples/                   # 示例项目
│   └── sample_project/
│       └── project.json
├── docs/                       # 文档
│   └── developer_guide.md
├── requirements.txt            # Python 依赖
├── .env.example                # 环境变量模板
└── README.md                   # 项目说明
```

---

## 下一步

- 阅读[开发者指南](docs/developer_guide.zh.md)了解架构细节
- 在 AI 工具标签页探索 AI 功能
- 在 GitHub Issues 参与讨论

---

**需要帮助？** 在 [github.com/pj4239460/story-graph-assistant](https://github.com/pj4239460/story-graph-assistant) 提交 issue
