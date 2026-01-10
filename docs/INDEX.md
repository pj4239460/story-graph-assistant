# Story Graph Assistant - 文档索引

**当前版本：** v0.7  
**最后更新：** 2026-01

---

## 📚 核心文档

### 快速入门
- **[英文入门指南](../GETTING_STARTED.en.md)** - 新用户快速上手教程
- **[中文入门指南](../GETTING_STARTED.zh.md)** - 中文版快速上手教程

### 技术参考
- **[世界导演指南（英文）](world_director_guide.md)** - World Director系统完整技术文档
- **[世界导演指南（中文）](world_director_guide.zh.md)** - 世界导演系统中文技术文档
- **[开发者指南（英文）](developer_guide.en.md)** - 系统架构和开发指南
- **[开发者指南（中文）](developer_guide.zh.md)** - 系统架构和开发指南（中文版）

### 高级主题
- **[Agent开发指南（英文）](agent_guide.en.md)** - LangGraph Agent扩展开发指南
- **[Agent开发指南（中文）](agent_guide.zh.md)** - LangGraph Agent扩展开发指南（中文版）

### 示例项目
- **[examples/ordering_fallback_demo.py](../examples/ordering_fallback_demo.py)** - 排序约束和备选机制演示
- **[examples/sample_project/](../examples/sample_project/)** - 基础示例项目（穿越题材）
- **[examples/wuxia_rpg/](../examples/wuxia_rpg/)** - 武侠RPG完整示例（15场景，5结局）

---

## 📖 文档结构

---

## 📖 文档结构

```
docs/
├── INDEX.md                      # 本文件 - 文档索引
├── CLEANUP_REPORT.md             # 文档清理记录
├── world_director_guide.md       # World Director技术参考（英文）
├── world_director_guide.zh.md    # World Director技术参考（中文）
├── developer_guide.en.md         # 开发者指南（英文）
├── developer_guide.zh.md         # 开发者指南（中文）
├── agent_guide.en.md            # Agent开发指南（英文）
├── agent_guide.zh.md            # Agent开发指南（中文）
└── archive/                      # 归档文档（历史参考）
    ├── agent_enhancement_report.md
    └── product_enhancement_report.md
```

---

## 🎯 按需求查找文档

### 我是新用户
→ 从 [GETTING_STARTED](../GETTING_STARTED.en.md) 开始

### 我想了解World Director系统
→ 阅读 [World Director Guide](world_director_guide.md)

### 我想贡献代码
→ 查看 [Developer Guide](developer_guide.en.md)

### 我遇到问题
→ 检查文档中的"故障排除"章节或提交 [GitHub Issue](https://github.com/pj4239460/story-graph-assistant/issues)

---

## 🔄 版本历史

### v0.7（当前）- 排序约束与备选机制
- 排序约束（requires_fired、forbids_fired）
- 备选机制（防止世界卡住）
- 空闲tick跟踪

### v0.5 - World Director MVP
- Storylet系统核心功能
- 7阶段选择流程

### v0.4 - 动态状态系统
- Effect模型
- StateService
- 状态追踪

### v0.3 - 向量搜索
- FAISS集成
- 语义搜索

---

## 📝 文档维护

所有核心文档应保持：
1. **双语支持**：重要文档提供中英文版本
2. **版本同步**：所有文档应反映当前版本（v0.7）
3. **示例丰富**：每个功能至少有一个实际示例
4. **故障排除**：包含常见问题和解决方案

---

**需要帮助？** 提交Issue到 [GitHub仓库](https://github.com/pj4239460/story-graph-assistant)
- Development workflow
- How to add features
- Testing guidelines

## Need Help?

- 📧 Email: pj4239460@gmail.com
- 🐛 Issues: [GitHub Issues](https://github.com/pj4239460/story-graph-assistant/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/pj4239460/story-graph-assistant/discussions)
