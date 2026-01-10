# 世界导演系统指南

**版本：** 1.7.1  
**最后更新：** 2024

本指南提供世界导演（World Director）系统的全面技术文档，这是一个动态叙事引擎，能够根据世界状态、前置条件、排序约束和节奏机制选择并触发故事片段（storylets）。

---

## 目录

- [什么是世界导演？](#什么是世界导演)
- [核心概念](#核心概念)
- [选择流程](#选择流程)
- [最佳实践与故障排除](#最佳实践与故障排除)
- [参考资料](#参考资料)

---

## 什么是世界导演？

世界导演是一个**确定性的动态叙事系统**，受到以下作品启发：
- **Fallen London / Sunless Sea**（Storylets 系统）
- **Left 4 Dead 的 AI 导演**（节奏控制）
- **质量驱动叙事**（基于条件的选择）

### 设计哲学

1. **作者控制** - 你定义规则，系统执行
2. **确定性** - 相同状态 + 配置 = 相同结果（完全可重现）
3. **可检视性** - 每个决定都有人类可读的理由
4. **组合性** - 小的叙事片段能够组合出复杂行为

### 与传统分支叙事的区别

| 传统分支 | 世界导演（Storylets） |
|---------|-------------------|
| 手工连接每个场景 | 定义条件，系统自动组合 |
| 指数级分支爆炸 | 线性增长的内容池 |
| 静态流程图 | 动态涌现叙事 |
| 难以平衡节奏 | 自动节奏调整 |
| 测试困难 | 确定性可重现 |

---

## 核心概念

### Storylet（故事片段）

**Storylet** 是一个可以被导演选择的叙事事件。每个 storylet 包含：

```python
{
  "id": "st-merchant-strike",           # 唯一标识符
  "title": "商人罢工",                   # 显示名称
  "description": "市场商人决定罢工...",  # 完整叙事内容
  
  # 前置条件（必须全部满足）
  "preconditions": [
    {"scope": "world", "path": "vars.worker_dissatisfaction", "op": ">=", "value": 70},
    {"scope": "world", "path": "vars.merchant_power", "op": ">", "value": 50}
  ],
  
  # 效果（触发时应用）
  "effects": [
    {"scope": "world", "op": "add", "path": "vars.market_activity", "value": -20},
    {"scope": "world", "op": "set", "path": "vars.strike_active", "value": true}
  ],
  
  # 选择权重
  "weight": 1.5,
  
  # 触发控制
  "once": false,              # 如果为true，只能触发一次
  "cooldown": 3,              # 触发后3个tick内不能再次触发
  
  # 节奏控制
  "intensity_delta": 0.2,     # 增加叙事强度
  
  # 多样性标签
  "tags": ["economic", "conflict"],
  
  # === v1.7.1 新增字段 ===
  
  # 排序约束
  "requires_fired": ["st-worker-protest"],    # 必须在这些storylet触发后
  "forbids_fired": ["st-peace-treaty"],       # 必须在这些storylet未触发
  
  # 备选机制
  "is_fallback": false        # 如果为true，仅在空闲时触发
}
```

### 前置条件（Preconditions）

前置条件决定 storylet 何时可用。**所有**前置条件必须满足才能触发。

**条件结构：**
```python
{
  "scope": "world",                    # "world" | "character.{id}"
  "path": "vars.gold",                 # 状态变量的路径
  "op": ">=",                          # 比较运算符
  "value": 100                         # 比较值
}
```

**支持的运算符：**

| 运算符 | 描述 | 示例 |
|-------|------|------|
| `==` | 等于 | `gold == 100` |
| `!=` | 不等于 | `faction != "rebels"` |
| `<`, `<=`, `>`, `>=` | 数值比较 | `power >= 50` |
| `in` | 值在列表中 | `"key" in inventory` |
| `not_in` | 值不在列表中 | `"cursed" not_in tags` |
| `contains` | 列表包含值 | `inventory contains "sword"` |
| `has_tag` | 标签存在 | `world has_tag "winter"` |
| `lacks_tag` | 标签不存在 | `world lacks_tag "tutorial_complete"` |

**示例：**
```python
# 简单条件
{"scope": "world", "path": "vars.gold", "op": ">=", "value": 100}
→ 检查：world.vars.gold >= 100

# 列表条件
{"scope": "world", "path": "vars.inventory", "op": "contains", "value": "key"}
→ 检查："key" in world.vars.inventory

# 角色条件
{"scope": "character.alice", "path": "vars.mood", "op": "==", "value": "happy"}
→ 检查：alice.vars.mood == "happy"

# 标签条件
{"scope": "world", "path": "tags", "op": "has_tag", "value": "winter"}
→ 检查："winter" in world.tags
```

### 效果（Effects）

效果是对世界状态的修改，在 storylet 触发时应用。

**效果结构：**
```python
{
  "scope": "world",                    # "world" | "character.{id}"
  "op": "add",                         # 操作类型
  "path": "vars.gold",                 # 目标路径
  "value": 50                          # 应用的值
}
```

**支持的操作：**

| 操作 | 描述 | 示例 |
|-----|------|------|
| `set` | 设置值 | `gold = 100` |
| `add` | 增加值 | `gold += 50` |
| `multiply` | 乘以值 | `damage *= 1.5` |
| `append` | 添加到列表 | `inventory.append("sword")` |
| `remove` | 从列表移除 | `inventory.remove("key")` |

**示例：**
```python
# 修改数值
{"scope": "world", "op": "add", "path": "vars.gold", "value": 100}
→ world.vars.gold += 100

# 设置布尔值
{"scope": "world", "op": "set", "path": "vars.quest_complete", "value": true}
→ world.vars.quest_complete = true

# 列表操作
{"scope": "world", "op": "append", "path": "vars.inventory", "value": "magic_sword"}
→ world.vars.inventory.append("magic_sword")

# 角色状态
{"scope": "character.bob", "op": "set", "path": "vars.mood", "value": "angry"}
→ bob.vars.mood = "angry"
```

### 导演配置（DirectorConfig）

导演配置控制选择行为：

```python
{
  "events_per_tick": 2,               # 每tick选择多少个storylet
  "diversity_penalty": 0.5,           # 标签重复的权重惩罚（0.0-1.0）
  "diversity_window": 3,              # 检查最近多少个tick的标签
  "pacing_scale": 0.3,                # 节奏调整的强度（0.0-1.0）
  
  # v1.7.1 新增
  "fallback_after_idle_ticks": 3      # 多少个空闲tick后触发备选
}
```

### Tick历史（TickHistory）v1.7.1

Tick历史跟踪所有已触发的 storylets 和系统状态：

```python
{
  "records": [...],                    # 所有tick记录
  "last_triggered": {                  # 上次触发时间
    "st-merchant-strike": 5            # storylet_id → tick编号
  },
  "triggered_once": {                  # 是否曾经触发过
    "st-tutorial": true,               # 用于"once"检查和排序约束
    "st-intro": true
  },
  
  # v1.7.1 新增
  "idle_tick_count": 0                 # 连续空闲tick计数
}
```

---

## 选择流程

导演使用9阶段流程来选择 storylets（v1.7.1 更新）：

### 阶段1：前置条件过滤

```
所有Storylets → 评估前置条件 → 候选池
```

- 分离常规和备选 storylets
- 评估每个常规 storylet 的前置条件
- 只保留**所有**前置条件都满足的 storylets
- 生成每个评估的解释

**示例：**
```
Storylet: "商人罢工"
前置条件：
  ✓ world.vars.workers_dissatisfaction = 75 (满足 >= 70)
  ✓ world.vars.merchants_power = 60 (满足 > 50)
→ 进入候选池
```

### 阶段2：排序约束（v1.7.1 新增！）

```
候选池 → 检查排序 → 满足约束的候选
```

**requires_fired**：Storylet 只能在指定 storylets 触发**之后**才能触发  
**forbids_fired**：Storylet 只能在指定 storylets **未**触发时才能触发

- 检查 `requires_fired` 列表：所有必须已触发
- 检查 `forbids_fired` 列表：所有必须未触发
- 用途：任务链、互斥路径、叙事依赖

**示例 - 任务链：**
```json
{
  "id": "quest_middle",
  "title": "任务进展",
  "requires_fired": ["quest_start"]
}
→ 只有在 "quest_start" 触发后才会出现

{
  "id": "quest_end",
  "title": "任务完成",
  "requires_fired": ["quest_start", "quest_middle"]
}
→ 需要前两步都完成
```

**示例 - 互斥路径：**
```json
{
  "id": "peaceful_resolution",
  "title": "和平条约",
  "once": true
}

{
  "id": "violent_resolution",
  "title": "全面战争",
  "forbids_fired": ["peaceful_resolution"],
  "once": true
}
→ 签订和平条约后就不能打仗了
```

### 阶段3：冷却与一次性过滤

```
满足约束的候选 → 检查冷却/一次性 → 可用池
```

- 移除还在冷却期的 storylets
  - 检查 `last_triggered[storylet_id] + cooldown <= current_tick`
- 移除已触发的"once" storylets
  - 检查 `triggered_once[storylet_id] == true`

### 阶段4：备选检查（v1.7.1 新增！）

```
可用池 → 检查是否为空 → 备选候选
```

如果没有常规 storylets 可用：
- 检查空闲tick计数器：`idle_tick_count >= fallback_after_idle_ticks`
- 如果达到阈值，评估备选 storylets
- 备选 storylets 也需要通过前置条件/排序/冷却检查

**目的**：防止"世界卡住" - 确保故事始终在进展

**示例备选 Storylets：**
```json
{
  "id": "weather_changes",
  "title": "天气变化",
  "is_fallback": true,
  "preconditions": [],  // 无要求
  "effects": [],  // 氛围事件
  "cooldown": 3,
  "intensity_delta": 0.0  // 中性
}

{
  "id": "crowd_activity",
  "title": "市场人群活动",
  "is_fallback": true,
  "preconditions": [],
  "effects": [
    {"scope": "world", "op": "add", "path": "vars.market_activity", "value": 5}
  ],
  "cooldown": 2,
  "intensity_delta": -0.1
}
```

### 阶段5：多样性惩罚

```
加权候选 → 应用多样性惩罚 → 调整后权重
```

- 检查最近tick中的标签重复
- 降低带有最近使用过标签的 storylets 的权重
- 公式：`weight *= (1 - diversity_penalty) ^ penalty_count`

**示例：**
```
Storylet: "贸易繁荣" (标签: ["economic", "positive"])
最近标签: ["economic", "economic", "political"]
惩罚计数: 2 (标签 "economic" 出现2次)
新权重: 1.5 * (1 - 0.5)² = 0.375
```

### 阶段6：节奏调整

```
加权候选 → 应用节奏调整 → 最终权重
```

- 检查当前强度 vs storylet 的 `intensity_delta`
- 如果太紧张，偏好平静的 storylets（负delta）
- 如果太平淡，偏好激化的 storylets（正delta）
- 公式：`weight *= 1 + pacing_scale * (target_adjustment * delta)`

**示例：**
```
当前强度: 0.8 (过高)
Storylet: "和平条约" (intensity_delta: -0.3)
目标: 降低强度
调整: 偏好负delta
新权重: weight * 1.5  // 提升平静storylets
```

### 阶段7：加权选择

```
最终权重 → 归一化 → 不放回选择N个
```

- 归一化权重为概率
- 选择 `events_per_tick` 个 storylets
- 使用不放回的加权随机抽样
- 记录每个选择的理由

**示例：**
```
最终候选：
  - "贸易繁荣" (权重: 1.2, 概率: 0.40)
  - "工人罢工" (权重: 0.9, 概率: 0.30)
  - "节日" (权重: 0.9, 概率: 0.30)

选择2个：
→ "贸易繁荣" (40% 概率)
→ "工人罢工" (30% 概率)
```

### 阶段8：效果应用

```
选中的Storylets → 应用效果 → 新状态 + 差异
```

- 深拷贝当前状态（用于差异计算）
- 按顺序应用每个 storylet 的效果
- 计算人类可读的状态差异（前后对比）
- 根据 storylet 的 deltas 更新强度
- 更新空闲tick计数器（v1.7.1）：
  - 如果选中了常规 storylets：重置 `idle_tick_count = 0`
  - 如果没有选中：增加 `idle_tick_count += 1`

**示例：**
```
之前：
  world.vars.merchants_power = 60
  world.vars.public_sentiment = 50

应用："贸易繁荣"
  效果: world.vars.merchants_power += 10

之后：
  world.vars.merchants_power = 70
  world.vars.public_sentiment = 50

差异：
  world.vars.merchants_power: 60 → 70
  
空闲跟踪：
  选中了常规storylet → idle_tick_count = 0
```

### 阶段9：历史记录

```
Tick结果 → 创建TickRecord → 追加到历史
```

- 创建 `TickRecord` 包含：
  - Tick编号和时间戳
  - 选中的 storylets 及理由
  - 应用的效果
  - 状态差异
  - 前后强度
  - 空闲tick计数（v1.7.1）
- 更新冷却跟踪
- 更新"once"跟踪
- 更新 triggered_once 用于排序约束（v1.7.1）
- 追加到 `TickHistory`

---

## 最佳实践与故障排除（v1.7.1 更新）

### 有效使用排序约束

**何时使用 `requires_fired`：**
- 必须按顺序进行的任务链
- 需要展开的故事线
- 分支叙事的前置条件
- 教程序列

**示例 - 教程链：**
```json
[
  {
    "id": "tut_basics",
    "title": "教程：基础",
    "once": true
  },
  {
    "id": "tut_advanced",
    "title": "教程：高级技巧",
    "requires_fired": ["tut_basics"],
    "once": true
  }
]
```

**何时使用 `forbids_fired`：**
- 互斥的故事路径
- 先前选择的后果
- 防止矛盾事件
- 备选结局

**示例 - 派系路径：**
```json
[
  {
    "id": "join_guild",
    "title": "加入商人公会",
    "once": true,
    "effects": [{"scope": "world", "op": "set", "path": "vars.faction", "value": "guild"}]
  },
  {
    "id": "join_rebels",
    "title": "加入叛军",
    "forbids_fired": ["join_guild"],
    "once": true,
    "effects": [{"scope": "world", "op": "set", "path": "vars.faction", "value": "rebels"}]
  },
  {
    "id": "guild_quest_1",
    "title": "公会任务：护送",
    "requires_fired": ["join_guild"],
    "forbids_fired": ["join_rebels"]
  }
]
```

### 设计备选 Storylets

**优秀备选 Storylets 的特征：**
1. **无前置条件**或要求极少
2. **氛围/环境性** - 增强世界而不影响主线
3. **中性强度**（0.0 或轻微负值如 -0.1）
4. **适度冷却**（2-5 ticks）提供多样性

**示例 - 环境备选：**
```json
[
  {
    "id": "weather_clear",
    "title": "☀️ 晴空万里",
    "is_fallback": true,
    "preconditions": [],
    "effects": [],
    "cooldown": 3,
    "intensity_delta": 0.0,
    "tags": ["ambient", "weather"]
  },
  {
    "id": "weather_rain",
    "title": "🌧️ 开始下雨",
    "is_fallback": true,
    "preconditions": [],
    "effects": [{"scope": "world", "op": "set", "path": "vars.weather", "value": "rain"}],
    "cooldown": 3,
    "intensity_delta": -0.05,
    "tags": ["ambient", "weather"]
  },
  {
    "id": "crowd_activity",
    "title": "👥 市场喧嚣",
    "is_fallback": true,
    "preconditions": [],
    "effects": [{"scope": "world", "op": "add", "path": "vars.market_activity", "value": 5}],
    "cooldown": 2,
    "intensity_delta": -0.1,
    "tags": ["ambient", "economic"]
  }
]
```

**推荐设置：**
- `fallback_after_idle_ticks: 3`（默认）- 大多数故事的良好平衡
- 创建 5-10 个备选 storylets 以提供多样性
- 使用多样性标签防止重复

### 故障排除：世界卡住

**症状：**没有 storylets 触发，空闲tick计数持续增加

**诊断步骤：**
1. 检查UI状态栏中的空闲tick计数器
2. 查看所有 storylets 的前置条件
3. 验证是否存在备选 storylets

**常见原因：**
- 所有 storylets 的前置条件都无法满足
- 未定义备选 storylets
- 备选 storylets 也有阻塞性前置条件
- 所有 storylets 同时在冷却期

**解决方案：**
```json
// 添加无前置条件的简单备选
{
  "id": "time_passes",
  "title": "时光静静流逝",
  "is_fallback": true,
  "preconditions": [],  // 重要：为空！
  "effects": [],
  "cooldown": 1,
  "intensity_delta": -0.2
}
```

### 故障排除：任务链断裂

**症状：**任务的中间步骤从未出现

**诊断步骤：**
1. 检查tick历史中的 `triggered_once`
2. 验证 `requires_fired` 中 storylet ID 的拼写
3. 检查是否有冲突的 `forbids_fired`

**常见错误：**
```json
// ❌ 错误 - requires_fired 中的拼写错误
{
  "id": "quest_part_2",
  "requires_fired": ["quest_part_1"],  // ID 实际上是 "quest_pt_1"
}

// ✅ 正确 - 匹配确切的ID
{
  "id": "quest_part_2",
  "requires_fired": ["quest_pt_1"],
}
```

### 故障排除：备选未触发

**症状：**idle_tick_count 超过阈值，但备选不触发

**诊断步骤：**
1. 检查备选 storylets 是否有 `"is_fallback": true`
2. 验证备选的前置条件已满足
3. 检查备选的冷却期
4. 确认 `fallback_after_idle_ticks` 设置

**修复示例：**
```json
// ❌ 问题 - 备选有阻塞性前置条件
{
  "id": "fallback_event",
  "is_fallback": true,
  "preconditions": [
    {"scope": "world", "path": "vars.impossible_condition", "op": "==", "value": 999}
  ]
}

// ✅ 解决方案 - 移除前置条件或使其简单
{
  "id": "fallback_event",
  "is_fallback": true,
  "preconditions": []
}
```

### 性能考虑

**大型 Storylet 池（100+ storylets）：**
- 前置条件评估是 O(n)
- 使用具体的前置条件提前过滤
- 考虑拆分到不同场景/上下文

**深层任务链（10+ 步骤）：**
- 使用 `once: true` 防止重复触发
- 用测试验证链的完整性
- 考虑使用状态变量跟踪进度

**推荐限制：**
- 每个上下文 50-100 个 storylets（良好性能）
- 每tick 5-10 个 storylets（叙事清晰度）
- `requires_fired` 深度 3-5 层（可维护性）

---

## 参考资料

- Emily Short 的 Storylet 研究：https://emshort.blog/2019/11/29/storylets-you-want-them/
- Left 4 Dead AI 导演：https://steamcdn-a.akamaihd.net/apps/valve/2009/ai_systems_of_l4d_mike_booth.pdf
- 质量驱动叙事：https://www.gdcvault.com/play/1015317/
- Fallen London 设计：https://www.failbettergames.com/news/
