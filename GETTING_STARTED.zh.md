# Story Graph Assistant - 启动指南

## 🎯 MVP v0.1 已完成！

基于你提供的开发者文档，MVP 版本已经构建完成，包含以下功能：

### ✅ 已实现的功能

1. **项目管理**
   - 创建、加载、保存项目
   - **最近项目**列表，快速访问
   - JSON 格式存储

2. **场景管理**
   - 创建、编辑、删除场景
   - 场景内容编辑
   - 分支选项管理
   - **交互式流程图** 基于 Streamlit Flow
   - 多种布局：树形、分层、力导向、手动
   - 拖拽节点自由排列
   - 统计仪表板

3. **角色管理**
   - 创建、编辑、删除角色
   - 角色档案（描述、性格、目标、恐惧）
   - 角色关系管理

4. **AI 智能工具**
   - 场景摘要生成
   - 世界观设定提取
   - OOC（人设崩坏）检测

5. **Token 统计**
   - 项目总用量追踪
   - 今日用量统计
   - 按功能分类统计

6. **国际化支持**
   - 中英文界面（已完全集成）
   - 动态语言切换
   - 130+ 翻译键值

---

## 🚀 快速启动

### 1. 安装依赖

```powershell
# 确保在项目根目录
cd d:\Workspace\game_projects\story_graph_assistant

# 创建虚拟环境（推荐）
python -m venv venv
.\venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置 API Key

```powershell
# 复制配置模板
copy .env.example .env

# 编辑 .env 文件，填入你的 DeepSeek API Key
# DEEPSEEK_API_KEY=sk-你的key
```

如果你没有 DeepSeek API Key：
- 访问 https://platform.deepseek.com/
- 注册并获取 API Key
- DeepSeek 提供非常优惠的价格（远低于 OpenAI）

### 3. 运行应用

```powershell
streamlit run src/app.py
```

应用将自动在浏览器中打开：`http://localhost:8501`

---

## 📖 使用指南

### 第一次使用

1. **创建项目**
   - 点击左侧菜单「➕ 新建」
   - 输入项目名称（如"我的第一个故事"）
   - 选择语言（中文/English）
   - 点击「创建」

2. **添加场景**
   - 切换到「📊 故事路线」标签页
   - 点击「➕ 新建场景」
   - 输入场景标题和内容
   - 保存

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
d:\Workspace\game_projects\story_graph_assistant\examples\sample_project\project.json
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

## 🎮 功能演示

### 场景摘要
- 自动为长场景生成简洁摘要
- 帮助快速了解场景内容
- 保存到场景对象中

### 设定提取
- 从场景文本中提取关键信息
- 自动分类：角色特征、世界观、剧情点
- 用于构建知识库（v2 将支持 RAG 检索）

### OOC 检测
- 根据角色档案检查场景中的行为
- AI 分析是否符合人设
- 给出详细解释和建议

---

## 🔧 故障排除

### 问题：无法安装 litellm

```powershell
pip install --upgrade pip
pip install litellm
```

### 问题：Streamlit 启动失败

```powershell
# 检查 Python 版本
python --version  # 应该 >= 3.10

# 重新安装 streamlit
pip install --upgrade streamlit
```

### 问题：AI 功能返回错误

1. 检查 `.env` 文件中的 API Key 是否正确
2. 确认 API Key 有足够的额度
3. 检查网络连接

---

## 📋 下一步开发计划

### v0.2 - 增强功能
- [ ] 场景编辑功能
- [ ] 角色编辑功能
- [ ] 场景间连接的可视化编辑
- [ ] 导出功能（Markdown/HTML）

### v0.3 - RAG 基础
- [ ] 时间线视图
- [ ] Keyword-based 检索
- [ ] 世界观问答
- [ ] 多场景 OOC 检查

---

## 💡 使用建议

1. **定期保存**：使用「💾 保存项目」避免数据丢失
2. **从小开始**：先创建简单的故事结构，逐步完善
3. **充分利用 AI**：为每个重要场景生成摘要和提取设定
4. **Token 管理**：注意 Token 使用量，合理使用 AI 功能
5. **备份项目**：JSON 文件可以直接复制备份

---

## 🤝 反馈与贡献

如有问题或建议，欢迎：
- 提交 Issue
- 发起 Pull Request
- 联系开发者

---

**祝你创作愉快！🎉**
