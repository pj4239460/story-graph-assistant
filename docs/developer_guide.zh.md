# AI 剧情 / 世界观助手 – 开发者指南

> 版本：v0.1 MVP  
> 项目：Story Graph Assistant / 故事图谱助手

---

## 目录

1. [产品与功能说明](#产品与功能说明)
2. [技术与实现方案](#技术与实现方案)
3. [快速开始](#快速开始)
4. [开发路线](#开发路线)

---

## 产品与功能说明

### 产品定位

**一句话简介**

> 一款面向剧情游戏 / 视觉小说 / 网状叙事的  
> 「剧情 & 世界观管理 + AI 分析助手」。

它融合了：

- 类似 **Twine** 的可视化剧情节点/流程图，用于结构设计；
- 类似 **Arcweave** 的"角色/物品/地点等组件管理"思路，用于世界观建模；
- 再加上一层 **RAG + 大语言模型** 的"故事大脑"，负责：
  - 设定抽取
  - 角色不出戏（OOC）检查
  - 路线和世界观一致性分析
  - What-if 世界推演

### 目标用户

- 独立游戏作者、Galgame/AVG 编剧
- RPG / TRPG 的世界观策划
- 想做复杂世界观、多分支结局的叙事设计师

### 核心价值

1. **看得见的故事结构**：用路线图和时间线管理复杂剧情结构；
2. **不丢设定的世界观数据库**：设定从对白中"抽出来"，可检索；
3. **角色和时间线更自洽**：角色人生线 + 时间轴视图；
4. **AI 做理性检查 & 灵感扩展**：OOC、世界观QA、路线分析、What-if 推演。

---

## 技术与实现方案

### 总体架构

- **架构风格**：本地优先 / 单机运行
  - Python 后端 + Streamlit 前端，启动即用
- **分层**：
  - UI（Streamlit）
  - Services（Project/Scene/Character/AI）
  - Repositories（项目存储）
  - Infra（LLM、Token统计、i18n）

### 技术栈

- **语言**：Python 3.10+
- **UI**：Streamlit
- **LLM 接入**：
  - DeepSeek API (`https://api.deepseek.com`)
  - LiteLLM 作为统一调用层
- **存储**：
  - v0/v1：JSON 文件形式的工程
  - v2+：可选 SQLite
- **RAG**：
  - v0：Keyword-based 伪 RAG
  - v1+：向量库（FAISS/Chroma） + embedding 模型

### 数据模型

核心实体：

- `Project` - 项目/工程
- `Scene` - 场景/节点
- `Choice` - 选项/分支
- `Character` - 角色
- `Event` - 事件（时间线）
- `WorldState` - 世界状态（v2）
- `StoryThread` - 故事线程（v2）
- `AISettings` - AI 配置
- `TokenStats` - Token 统计

### 项目结构

```
story_graph_assistant/
├── src/
│   ├── app.py              # Streamlit 入口
│   ├── models/             # 数据模型
│   ├── repositories/       # 存储层
│   ├── services/           # 业务逻辑
│   ├── infra/              # 基础设施（LLM、i18n）
│   └── ui/                 # UI 组件
├── i18n/                   # 国际化
├── examples/               # 示例项目
├── docs/                   # 文档
├── requirements.txt
├── .env.example
└── README.md
```

---

## 快速开始

### 1. 安装依赖

```bash
# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Windows: venv\\Scripts\\activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
# 复制配置模板
cp .env.example .env

# 编辑 .env 文件，填入你的 DeepSeek API Key
# DEEPSEEK_API_KEY=your_api_key_here
```

### 3. 运行应用

```bash
streamlit run src/app.py
```

应用将在 `http://localhost:8501` 启动。

### 4. 创建第一个项目

1. 点击侧边栏「➕ 新建」
2. 输入项目名称，点击「创建」
3. 在「📊 故事路线」标签页中添加场景
4. 在「👥 角色管理」标签页中创建角色
5. 在「🤖 AI 工具」标签页中使用 AI 功能

---

## MVP 功能清单（v0.1）

### ✅ 已实现

- [x] 项目创建、加载、保存
- [x] 场景管理（CRUD）
- [x] 角色管理（CRUD）
- [x] AI 场景摘要
- [x] AI 设定提取
- [x] AI OOC 检测
- [x] Token 使用统计

### 🚧 计划中

- [ ] 场景间连接/分支管理
- [ ] 图谱可视化（Graphviz/D3.js）
- [ ] 时间线视图
- [ ] RAG 知识库
- [ ] What-if 推演
- [ ] 导出功能

---

## 开发路线

### v0.1 - MVP（当前版本）
- ✅ 基础项目管理
- ✅ 场景和角色 CRUD
- ✅ 单场景 AI 功能
- ✅ Token 统计

### v0.3 - 初级 RAG
- [ ] 时间线视图
- [ ] Keyword-based 检索
- [ ] 世界观问答
- [ ] 多场景 OOC 检查

### v0.3 - 完整 RAG
- [ ] 向量检索（FAISS/Chroma）
- [ ] 角色人生线
- [ ] 路线分析
- [ ] 情感曲线

### v2.0 - 世界模拟
- [ ] WorldState & StoryThread
- [ ] 高级 What-if 推演
- [ ] 项目一致性报告
- [ ] 成本模式

---

## API 文档

### Services

#### ProjectService

```python
# 创建项目
project = project_service.create_project(name="我的故事", locale="zh")

# 加载项目
project = project_service.load_project("path/to/project.json")

# 保存项目
project_service.save_project("path/to/project.json")
```

#### SceneService

```python
# 创建场景
scene = scene_service.create_scene(
    project, 
    title="开场", 
    body="故事从这里开始...",
    chapter="第一章"
)

# 添加选项
choice = scene_service.add_choice(
    project,
    scene.id,
    text="选择A",
    target_scene_id=another_scene.id
)
```

#### AIService

```python
# 场景摘要
summary = ai_service.summarize_scene(project, scene)

# 设定提取
facts = ai_service.extract_facts(project, scene)

# OOC 检测
result = ai_service.check_ooc(project, character_id, scene)
```

---

## 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 许可证

MIT License

---

## 联系方式

- GitHub: [yourusername/story-graph-assistant](https://github.com/yourusername/story-graph-assistant)
- Issues: [Report a bug](https://github.com/yourusername/story-graph-assistant/issues)

---

**Slogan**: *"Visual AI assistant for branching game stories."*  
**口号**：*「用图谱 + AI，捋清你的分支剧情。」*
