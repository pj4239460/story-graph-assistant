# AI Agent 开发指南

本指南介绍如何扩展故事图谱助手的 AI Agent 功能。

## 🎯 最新更新

### 已实现的增强功能

✅ **RAG 工具** - `search_story_context(query)`: 语义搜索整个故事数据库  
✅ **场景分析工具** - `analyze_scene(scene_id)`: 综合场景分析（摘要+设定提取）  
✅ **意图分类** - 自动区分 QA 模式（事实查询）和 Chat 模式（讨论建议）

### 架构升级

```
用户输入
  ↓
classify_intent (意图分类节点)
  ├─ qa_agent (事实查询模式)
  │   ├─ 优先使用 search_story_context
  │   ├─ 可调用 analyze_scene
  │   └─ 其他查询工具
  └─ chat_agent (讨论模式)
      └─ 创意讨论，按需使用工具
```

## 架构概览

### 技术栈
- **LangGraph**: AI Agent 状态机框架（支持多节点路由）
- **ChatLiteLLM**: 统一的 LLM 接口（支持 DeepSeek、OpenAI、Claude 等）
- **LangChain Tools**: 使用 `@tool` 装饰器定义工具函数
- **FAISS**: 语义搜索向量数据库
- **SearchService**: RAG 层，整合向量搜索和关键词搜索

### 核心组件

```
langgraph_agent_service.py
├── LangGraphAgentService
│   ├── __init__(): 初始化 LLM、工具和 services
│   ├── _create_tools(): 定义所有工具函数（包括 RAG 工具）
│   ├── _build_graph(): 构建 StateGraph 工作流（带意图分类）
│   ├── _get_qa_system_prompt(): QA 模式的系统提示词
│   ├── _get_chat_system_prompt(): Chat 模式的系统提示词
│   └── chat(): 处理用户消息
│
└── StateGraph 工作流
    ├── classify_intent: 意图分类节点
    ├── qa_agent_node: QA 代理节点（事实查询）
    ├── chat_agent_node: Chat 代理节点（讨论建议）
    ├── tool_node: 工具执行节点
    └── route_by_intent: 路由决策
```

## 核心工具说明

### 1. 🔍 search_story_context (RAG 工具)

**最重要的工具** - 使用语义搜索查询整个故事数据库。

```python
@tool
def search_story_context(query: str) -> str:
    """在整个故事数据中进行检索，返回与 query 最相关的角色、场景和设定摘要。
    
    适合回答:
    - "在这个世界里帝国和教会的关系是怎样的？"
    - "主角目前经历了什么？"
    - "Which scenes involve memory manipulation?"
    """
```

**工作原理:**
1. 调用 `SearchService.get_contextual_summary(project, query)`
2. 使用 FAISS 向量数据库进行语义搜索
3. 返回格式化的上下文（相关角色 + 相关场景）

**何时使用:** Agent 会优先使用此工具处理大部分问题，特别是关于世界观、背景和情节的查询。

### 2. 📊 analyze_scene (场景分析工具)

综合分析特定场景的所有内容。

```python
@tool
def analyze_scene(scene_id: str) -> str:
    """对指定场景进行全面分析:
    - 生成 AI 摘要
    - 提取世界观设定和剧情点
    - 展示元数据（选项数、标签、参与角色）
    """
```

**输出示例:**
```markdown
# Scene Analysis: 雨夜的委托

**ID:** scene_01
**Chapter:** 第一章

---

## 📝 Summary
陈墨在雨夜收到神秘委托...
*(AI Generated)*

## 🌍 Extracted Facts & Plot Points
- [角色] 陈墨是一名私家侦探
- [设定] 新上海2077年，赛博朋克世界
- [伏笔] 委托人提到"记忆碎片"

---

## 📊 Scene Metadata
- **Choices:** 3 options
- **Tags:** #悬疑, #开场
- **Characters:** 陈墨, 神秘女人
```

### 3. 其他查询工具

- `get_all_characters()` - 列出所有角色
- `get_character_by_name(name)` - 查询特定角色详情
- `get_all_scenes()` - 列出所有场景
- `search_scenes(keyword)` - 关键词搜索场景
- `count_endings()` - 统计结局数量
- `get_world_facts()` - 获取已提取的世界观设定

## 意图分类机制

### QA 模式 (事实查询)

**触发条件:** 用户问事实性问题

示例问题:
- "现在有几个角色？"
- "陈墨是谁？"
- "这个故事有几个结局？"
- "分析一下 Scene 5"
- "帝国和教会的关系是什么？"

**行为特点:**
- 系统提示词强调"使用工具获取准确信息"
- 优先调用 `search_story_context`
- 不编造信息，找不到就明确说明

### Chat 模式 (讨论建议)

**触发条件:** 用户想要讨论、头脑风暴或征求建议

示例问题:
- "我觉得这个角色设定怎么样？"
- "有什么改进建议吗？"
- "怎么让这段剧情更吸引人？"

**行为特点:**
- 系统提示词强调"创意讨论和建设性反馈"
- 可以使用工具，但非必需
- 鼓励提问和探讨

## 如何添加新工具

### 1. 在 `_create_tools()` 方法中定义新工具

```python
def _create_tools(self):
    """Create LangChain tools for story queries"""
    project = self.project
    
    @tool
    def your_new_tool(param1: str, param2: int) -> str:
        """
        工具描述：清晰说明工具的用途和使用场景
        
        当用户询问 XXX 时使用此工具，例如：
        - "用户问题示例1"
        - "用户问题示例2"
        
        Args:
            param1: 参数1的描述
            param2: 参数2的描述
            
        Returns:
            返回值的描述
        """
        # 工具实现逻辑
        result = f"处理结果: {param1}, {param2}"
        return result
    
    # 将新工具添加到返回列表
    return [
        get_all_characters,
        get_character_by_name,
        # ... 其他工具 ...
        your_new_tool,  # 添加这里
    ]
```

### 2. 工具定义最佳实践

#### ✅ 好的工具描述
```python
@tool
def search_scenes(keyword: str) -> str:
    """搜索包含特定关键词的场景。
    
    当用户想要查找关于某个主题的场景时使用，例如：
    - "哪些场景提到了记忆？"
    - "Find scenes about police"
    
    Args:
        keyword: 要搜索的关键词
    """
```

**要点：**
- 清楚说明工具用途
- 提供具体的用户问题示例
- 参数说明简洁明了

#### ❌ 不好的工具描述
```python
@tool
def search_scenes(keyword: str) -> str:
    """搜索场景"""  # 太简略，缺少示例
```

### 3. 访问项目数据

工具函数可以通过闭包访问 `project` 对象：

```python
@tool
def get_scene_count_by_chapter() -> str:
    """统计每章的场景数量"""
    chapters = {}
    for scene in project.scenes.values():  # 注意：是 .values() 不是直接迭代
        chapter = scene.chapter or "未分类"
        chapters[chapter] = chapters.get(chapter, 0) + 1
    
    result = "各章节场景数：\n"
    for chapter, count in sorted(chapters.items()):
        result += f"  {chapter}: {count}个场景\n"
    return result
```

**重要提示：**
- `project.characters` 和 `project.scenes` 是 `Dict[str, T]` 类型
- 迭代时必须使用 `.values()`: `for char in project.characters.values()`
- 直接迭代 `project.characters` 只会得到键（ID）

### 4. 数据模型参考

#### Character 模型
```python
class Character:
    id: str
    name: str
    alias: Optional[str] = None  # 注意：是 alias 不是 aliases
    description: str = ""
    traits: List[str] = []
    goals: List[str] = []
    fears: List[str] = []
    relationships: List[Relationship] = []
```

#### Scene 模型
```python
class Scene:
    id: str
    title: str
    chapter: Optional[str] = None
    summary: Optional[str] = None
    body: str = ""
    tags: List[str] = []
    choices: List[Choice] = []
```

#### Relationship 模型
```python
class Relationship:
    targetId: str  # 注意：是 targetId 不是 targetName
    summary: str   # 注意：是 summary 不是 relationType
```

## 工具示例

### 示例 1: 简单查询工具

```python
@tool
def count_endings() -> str:
    """统计故事的结局数量。
    
    当用户询问故事有多少个结局时使用：
    - "这个故事有几个结局？"
    - "How many endings?"
    """
    endings = [
        s for s in project.scenes.values()
        if not s.choices or all(not c.nextSceneId for c in s.choices)
    ]
    
    if not endings:
        return "未找到明确的结局场景。"
    
    result = f"共找到 {len(endings)} 个结局：\n"
    for scene in endings:
        result += f"• {scene.id}. {scene.title}\n"
    return result
```

### 示例 2: 带参数的查询工具

```python
@tool
def get_character_by_name(name: str) -> str:
    """获取特定角色的详细信息。
    
    当用户询问某个角色时使用：
    - "陈墨是谁？"
    - "Who is Chen Mo?"
    
    Args:
        name: 角色名称或别名
    """
    name_lower = name.lower()
    for char in project.characters.values():
        if (char.name.lower() == name_lower or 
            (char.alias and char.alias.lower() == name_lower)):
            result = f"**{char.name}**\n"
            if char.alias:
                result += f"别名: {char.alias}\n"
            if char.description:
                result += f"\n{char.description}\n"
            return result
    
    available = ', '.join(c.name for c in project.characters.values())
    return f"未找到角色 '{name}'。可用角色：{available}"
```

### 示例 3: 复杂分析工具

```python
@tool
def analyze_character_interactions() -> str:
    """分析角色之间的互动关系。
    
    当用户想了解角色互动时使用：
    - "角色之间有什么关系？"
    - "Which characters interact?"
    """
    interactions = {}
    
    # 统计每对角色在同一场景出现的次数
    for scene in project.scenes.values():
        char_ids = [p.characterId for p in scene.participants]
        for i, char1 in enumerate(char_ids):
            for char2 in char_ids[i+1:]:
                pair = tuple(sorted([char1, char2]))
                interactions[pair] = interactions.get(pair, 0) + 1
    
    # 按互动次数排序
    sorted_pairs = sorted(interactions.items(), key=lambda x: x[1], reverse=True)
    
    result = "角色互动统计（共同出现场景数）：\n\n"
    for (id1, id2), count in sorted_pairs[:10]:
        name1 = project.characters.get(id1, type('obj', (), {'name': id1})).name
        name2 = project.characters.get(id2, type('obj', (), {'name': id2})).name
        result += f"{name1} ↔ {name2}: {count}个场景\n"
    
    return result
```

## 测试新工具

### 1. 重启应用
```bash
streamlit run src/app.py
```

### 2. 在聊天界面测试

问一些能触发新工具的问题，例如：
- "现在整个故事中有几个角色？"
- "陈墨是谁？"
- "这个故事有几个结局？"

### 3. 查看 Agent 思考过程

点击 "🔍 View Agent Thinking Process" 展开面板，查看：
- 🤔 Thinking: Agent 决策过程
- 🔧 Tool Call: 调用了哪个工具，参数是什么
- 📊 Result: 工具返回的结果
- ✅ Final Answer: 最终回答

## 常见问题

### Q1: 工具没有被调用？

**原因：** 工具描述不够清晰，或示例问题不匹配

**解决：**
1. 在工具 docstring 中添加更多用户问题示例
2. 用自然语言清楚说明工具用途
3. 确保示例问题覆盖中英文

### Q2: 工具报错 'str' object has no attribute ...

**原因：** 迭代 Dict 时没有使用 `.values()`

**解决：**
```python
# ❌ 错误
for char in project.characters:
    print(char.name)  # char 是 str 类型的 ID

# ✅ 正确
for char in project.characters.values():
    print(char.name)  # char 是 Character 对象
```

### Q3: 工具返回结果太长，被截断

**解决：** 在工具中限制输出长度
```python
@tool
def get_all_scenes() -> str:
    """获取所有场景列表"""
    scenes = list(project.scenes.values())
    result = f"共 {len(scenes)} 个场景：\n\n"
    
    for scene in scenes[:20]:  # 只显示前20个
        result += f"{scene.id}. {scene.title}\n"
        if scene.summary:
            # 摘要限制在100字符
            summary = scene.summary[:100] + "..." if len(scene.summary) > 100 else scene.summary
            result += f"   {summary}\n"
    
    if len(scenes) > 20:
        result += f"\n... 还有 {len(scenes) - 20} 个场景"
    
    return result
```

### Q4: 如何让工具支持多语言？

**方案：** 在 system prompt 中指示 Agent 用用户的语言回答

当前实现已经包含：
```python
def _get_system_prompt(self) -> str:
    return f"""...
Current project: {self.project.name}
Locale: {self.project.locale}

Respond in the same language as the user's question (Chinese or English)."""
```

工具返回值可以用英文，Agent 会根据用户问题的语言翻译。

## 高级主题

### 异步工具调用

如果需要调用外部 API，使用异步工具：

```python
import asyncio
from langchain_core.tools import tool

@tool
async def search_web(query: str) -> str:
    """搜索网络获取信息"""
    # 异步 HTTP 请求
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.example.com/search?q={query}") as resp:
            data = await resp.json()
            return data["result"]
```

**注意：** 需要修改 `_build_graph()` 使用异步 ToolNode。

### 工具依赖和组合

工具可以调用其他工具的逻辑：

```python
@tool
def get_character_summary(name: str) -> str:
    """获取角色摘要（包括参与场景）"""
    # 复用 get_character_by_name 的逻辑
    char_info = get_character_by_name.invoke(name)
    
    # 添加场景统计
    scene_count = sum(
        1 for scene in project.scenes.values()
        if any(p.characterId == name for p in scene.participants)
    )
    
    return f"{char_info}\n\n参与场景数: {scene_count}"
```

### 错误处理

工具应该优雅地处理错误：

```python
@tool
def get_scene_by_id(scene_id: str) -> str:
    """根据 ID 获取场景详情"""
    try:
        scene = project.scenes.get(scene_id)
        if not scene:
            available = ', '.join(list(project.scenes.keys())[:5])
            return f"场景 '{scene_id}' 不存在。可用场景 ID 示例：{available}"
        
        result = f"**{scene.title}**\n"
        result += f"ID: {scene.id}\n"
        if scene.chapter:
            result += f"章节: {scene.chapter}\n"
        # ...
        return result
        
    except Exception as e:
        return f"获取场景信息时出错：{str(e)}"
```

## 参考资料

- [LangGraph 文档](https://python.langchain.com/docs/langgraph)
- [LangChain Tools](https://python.langchain.com/docs/modules/tools/)
- [ChatLiteLLM](https://docs.litellm.ai/docs/providers)
- [项目代码：langgraph_agent_service.py](../src/services/langgraph_agent_service.py)

---

**提示：** 每次添加新工具后，重启 Streamlit 应用并测试工具是否正确工作。通过查看 Agent 思考过程面板来调试工具调用。
