# AI-Enhanced World Director (v0.9)

## 概述

v0.9版本引入了**AI增强的世界导演系统**，让用户可以选择使用AI来驱动叙事演化，实现更自然、更涌现的故事体验。

## 三种导演模式

### 1. 🔧 确定性模式（Deterministic）

**特点**：
- ✅ 最快速（无LLM调用）
- ✅ 100%可复现
- ✅ 最低token成本
- ⚠️ 需要显式编写条件规则

**适用场景**：
- 需要精确控制的叙事逻辑
- 性能优先的项目
- 调试和测试阶段
- 预算有限的项目

**示例条件**：
```python
Precondition(
    path="world.vars.tension",
    op=">=",
    value=70
)
```

---

### 2. 🤖 AI辅助模式（AI-Assisted）

**特点**：
- ✅ 速度与灵活性的平衡
- ✅ 支持自然语言条件
- ✅ 确定性条件仍然快速
- ⚠️ 中等token消耗
- ⚠️ NL条件略慢（~500ms/条件）

**适用场景**：
- 需要复杂情境判断的事件
- 原型开发阶段
- 混合使用规则和AI
- 渐进式AI采用

**示例条件混合使用**：
```python
# 确定性条件（快速筛选）
Precondition(path="world.vars.tension", op=">=", value=70)

# AI条件（细腻判断）
Precondition(nl_condition="Alice feels cornered and desperate")
Precondition(nl_condition="Multiple factions are in open conflict")
```

**工作流程**：
1. 确定性条件先筛选（< 1ms）
2. 通过后，AI评估NL条件（~500ms）
3. 全部满足后触发storylet

---

### 3. 🧠 AI主导模式（AI-Primary）

**特点**：
- ✅ 最大叙事涌现性
- ✅ 适应复杂语境
- ✅ 可处理模糊/隐式条件
- ⚠️ 最慢（~1-2s/tick）
- ⚠️ 高token消耗
- ⚠️ 可复现性降低

**适用场景**：
- 实验性叙事设计
- 高度动态的故事世界
- 追求意外和惊喜
- 最终用户体验优先

**示例纯NL条件**：
```python
Precondition(nl_condition="The political situation is unstable")
Precondition(nl_condition="Characters are emotionally exhausted")
Precondition(nl_condition="A catalyst for change is needed")
```

---

## 技术实现

### 条件评估流程

```
用户配置Director模式
    ↓
DirectorService.select_storylets()
    ↓
_evaluate_conditions_hybrid()
    ↓
├─ 确定性条件 → ConditionsEvaluator （< 1ms）
└─ NL条件 → AIConditionsEvaluator （~500ms）
    ↓
LLMClient.call()
    ↓
结构化响应解析
    ↓
缓存结果（相同状态不重复调用）
```

### AI条件评估器

**核心功能**：
- 将世界状态转换为自然语言上下文
- 使用结构化prompt确保一致输出
- 返回：判断结果 + 置信度 + 推理过程
- 智能缓存（相同状态复用结果）

**提示模板**：
```
=== CURRENT STORY STATE ===
World Variables:
  - world.vars.tension = 85
  - world.vars.faction_a_power = 60

Character States:
  - characters.alice:
      mood = angry
      status = cornered

=== CONDITION TO EVALUATE ===
"Alice feels cornered and desperate"

=== YOUR TASK ===
Is this condition satisfied? Respond:
JUDGMENT: [YES/NO]
CONFIDENCE: [0.0-1.0]
REASONING: [explanation citing state values]
```

**输出示例**：
```
✓ [AI 0.92] Alice feels cornered (mood=angry, status=cornered confirmed)
```

---

## 使用指南

### 1. 在UI中选择模式

在World Director界面：
```
🎯 Director Mode
○ 🔧 Deterministic (Rule-based)
○ 🤖 AI-Assisted (Hybrid)  ← 推荐开始这里
○ 🧠 AI-Primary (Emergent)
```

### 2. 创建带NL条件的Storylet

**在Storylet Editor中**：
```json
{
  "id": "alice-breakdown",
  "title": "Alice's Emotional Breakdown",
  "preconditions": [
    {
      "nl_condition": "Alice has been under extreme pressure for days"
    },
    {
      "nl_condition": "Her support network has failed her"
    }
  ],
  "effects": [
    {
      "scope": "character",
      "target": "alice",
      "path": "mood",
      "op": "set",
      "value": "broken"
    }
  ]
}
```

### 3. 监控Token消耗

**每次tick的预估成本**：
- 确定性模式：0 tokens
- AI辅助模式：~200-800 tokens （取决于NL条件数量）
- AI主导模式：~500-2000 tokens

**项目限额管理**：
- 在Settings中设置`projectTokenLimit`
- 系统会在超限前警告
- TokenStats自动记录所有LLM调用

---

## 最佳实践

### 何时使用确定性条件

✅ **推荐**：
- 数值比较：`tension >= 70`
- 标签检查：`active_traits contains "brave"`
- 状态等式：`mood == "angry"`
- 关系度量：`trust > 50`

### 何时使用AI条件

✅ **推荐**：
- 复杂情境判断："角色处于道德困境"
- 隐式状态推断："气氛紧张且不安"
- 模糊概念："局势不稳定"
- 多维综合："所有条件都指向冲突爆发"

❌ **不推荐**：
- 简单数值判断（浪费token）
- 高频触发的条件（性能问题）
- 需要确定性的逻辑（可复现性）

### 混合策略

**推荐架构**：
```python
# Storylet: "Faction War Erupts"
preconditions = [
    # 硬性条件（确定性，快速筛选）
    Precondition(path="world.vars.faction_a_power", op=">=", value=60),
    Precondition(path="world.vars.faction_b_power", op=">=", value=60),
    Precondition(path="world.vars.tension", op=">=", value=80),
    
    # 软性条件（AI，细腻判断）
    Precondition(nl_condition="Recent events have pushed both sides past the point of no return"),
    Precondition(nl_condition="Key characters are ready to commit to violence")
]
```

**优势**：
- 确定性条件先筛选，避免无效LLM调用
- AI条件处理难以形式化的情境
- 保持核心逻辑的可控性

---

## 性能优化

### 1. 缓存机制

AI评估器自动缓存结果：
```python
cache_key = hash(condition + world_state + char_states)
if cache_key in cache:
    return cached_result  # 无需重复LLM调用
```

**清空缓存**：
```python
director_service.ai_conditions_evaluator.clear_cache()
```

### 2. 批量评估

系统自动批处理同一tick中的所有条件评估，减少网络往返。

### 3. Token预算

在`DirectorConfig`中设置限制：
```python
config = DirectorConfig(
    ai_mode="ai_assisted",
    ai_cache_enabled=True  # 启用缓存（默认）
)
```

---

## 示例项目

### 1. 混合模式示例

**project:** `examples/town_factions`

**特点**：
- 13个storylets，部分使用NL条件
- 展示确定性+AI混合策略
- 完整的faction dynamics模拟

**关键storylet**：
```json
{
  "id": "market-tension-boils",
  "preconditions": [
    {"path": "world.vars.market_tension", "op": ">=", "value": 80},
    {"nl_condition": "Merchants and guild members are at each other's throats"}
  ]
}
```

### 2. AI主导示例

**创建中...** 未来会添加完全基于NL条件的示例项目。

---

## 论文基础

本系统基于以下研究和理论：

1. **Quality-Based Narrative (QBN)**
   - Emily Short的storylet理论
   - Fallen London的实践经验
   
2. **AI Director（Left 4 Dead）**
   - 动态难度调整
   - 节奏控制（peaks and valleys）

3. **LLM-powered Narrative Systems**
   - 结合符号AI与神经AI的混合架构
   - 可解释性与涌现性的平衡

参考论文：`2501.09099v1.pdf` （具体内容请查看附件）

---

## 路线图

### v0.9 (当前)
- ✅ 三种导演模式
- ✅ AI条件评估器
- ✅ 混合条件支持
- ✅ 缓存优化

### v1.0 (计划)
- [ ] AI驱动的storylet生成
- [ ] 自然语言效果描述
- [ ] 智能fallback推荐
- [ ] A/B测试框架（确定性 vs AI）

### v1.1+ (未来)
- [ ] 多Agent协同叙事
- [ ] 长期记忆与角色成长
- [ ] 情感弧线分析
- [ ] 自动调参（学习用户偏好）

---

## 常见问题

**Q: AI模式会让故事变得不可控吗？**

A: 不会。AI辅助模式仍然遵循你定义的storylet结构和effects。AI只是帮助评估复杂条件，最终触发什么、产生什么效果，仍由你的设计决定。

**Q: Token成本会不会很高？**

A: 取决于使用方式。AI辅助模式下，每个tick约消耗200-800 tokens（假设2-4个NL条件）。按DeepSeek的价格，每1000次tick约消耗$0.5-2。合理使用缓存和混合策略可以显著降低成本。

**Q: 如何调试AI条件？**

A: 每次评估都返回详细explanation：
```
✓ [AI 0.92] Alice feels cornered (mood=angry, status=cornered confirmed)
```
包含置信度和推理过程，帮助你理解AI的判断逻辑。

**Q: 可以不用AI功能吗？**

A: 当然！选择"确定性模式"即可，系统完全回退到v0.8的纯规则模式，零token消耗。

---

## 反馈与支持

欢迎在GitHub Issues中分享你的使用体验、建议和bug报告：
- 📝 Feature requests
- 🐛 Bug reports
- 💡 AI模式使用技巧
- 📊 性能优化建议

让我们一起探索AI增强叙事的可能性！
