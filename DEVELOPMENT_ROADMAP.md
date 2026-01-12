# Development Roadmap / 开发路线

> **Last Updated:** 2026-01-12  
> **Current Version:** v0.8  
> **In Development:** v0.9 - AI Enhancement

---

## 📍 Current Status / 当前状态

### ✅ Completed in v0.9 (Code Implementation)
- [x] Natural language conditions (Precondition.nl_condition field)
- [x] AIConditionsEvaluator service (350 lines, LLM-powered)
- [x] Three director modes (deterministic/ai_assisted/ai_primary)
- [x] Hybrid evaluation engine (rules + AI)
- [x] Smart caching with state hash
- [x] Token management and limits
- [x] AI mode selector UI
- [x] Bilingual i18n (9 new keys)
- [x] AI_DIRECTOR_GUIDE.md documentation

### 🎯 Core Value Proposition / 核心卖点
**"首个支持AI+规则混合的动态叙事引擎"**
- User has full control over AI usage (3 modes)
- Progressive adoption path (deterministic → ai_assisted → ai_primary)
- Explainable AI decisions (confidence + reasoning)
- Cost-controllable (use AI only when needed)

---

## 🚀 v0.9 Completion Plan / 完成计划

### Priority 1: Essential / 必须完成 ⭐⭐⭐

#### 1.1 Create Real NL Condition Examples
**Why:** Demonstrate actual value of AI conditions vs traditional rules

**Tasks:**
- [ ] Add 5-10 NL condition storylets to `town_factions` project
- [ ] Create examples showing NL condition advantages:
  - Complex social states: "Player is respected but financially struggling"
  - Emotional nuances: "Character is conflicted about their loyalty"
  - Contextual judgments: "The situation feels tense but manageable"
- [ ] Create comparison document: Traditional vs NL conditions
- [ ] Add comments explaining when to use each approach

**Example Storylets to Create:**
```
1. "Wealthy Merchant Approach" - NL: "Player has good reputation and appears wealthy"
2. "Factional Tension" - NL: "Relations between Red and Blue factions are strained"
3. "Character Trust" - NL: "NPC trusts the player despite recent conflicts"
4. "Moral Dilemma" - NL: "Player faces a difficult ethical choice"
5. "Atmospheric Check" - NL: "The town atmosphere is peaceful and safe"
```

#### 1.2 Complete Testing
**Why:** Ensure stability before declaring v0.9 ready

**Tasks:**
- [ ] Test mode switching (deterministic ↔ ai_assisted ↔ ai_primary)
- [ ] Test AI condition evaluation accuracy (10+ test cases)
- [ ] Test caching mechanism (verify cache hits/misses)
- [ ] Test token consumption (measure actual usage)
- [ ] Edge case testing:
  - [ ] Empty nl_condition
  - [ ] Very long nl_condition (>200 chars)
  - [ ] Invalid LLM response handling
  - [ ] API key missing/invalid
  - [ ] Token limit exceeded
  - [ ] Network timeout
- [ ] Create test report document

#### 1.3 Update Core Documentation
**Why:** Users need to understand the new AI features

**Tasks:**
- [ ] Update `docs/developer_guide.en.md`:
  - [ ] Add AIConditionsEvaluator to architecture diagram
  - [ ] Add "AI-Enhanced Director" section
  - [ ] Update Data Flow to include AI evaluation
  - [ ] Update version to v0.9
- [ ] Update `docs/world_director_guide.md`:
  - [ ] Add "Natural Language Conditions" chapter
  - [ ] Add examples of good NL conditions
  - [ ] Add best practices section
  - [ ] Add troubleshooting for AI mode
- [ ] Create `QUICKSTART_AI.md`:
  - [ ] 5-minute guide to AI Director
  - [ ] Step-by-step first NL condition
  - [ ] Mode selection guide

---

### Priority 2: Highly Recommended / 强烈推荐 ⭐⭐

#### 2.1 Performance Benchmarking
**Why:** Users need to understand trade-offs between modes

**Tasks:**
- [ ] Create benchmark script to measure:
  - [ ] Response time per mode (100 samples each)
  - [ ] Token consumption per mode (100 samples)
  - [ ] Cache hit rate over time
- [ ] Create performance comparison table:
  ```
  | Mode          | Avg Time | Token/Tick | Cache Hit | Use Case           |
  |---------------|----------|------------|-----------|---------------------|
  | Deterministic | <1ms     | 0          | N/A       | High performance   |
  | AI-Assisted   | ~500ms   | 200-800    | 40-60%    | Balanced           |
  | AI-Primary    | ~1-2s    | 500-2000   | 30-50%    | Narrative-first    |
  ```
- [ ] Add benchmark results to `AI_DIRECTOR_GUIDE.md`
- [ ] Create cost estimation guide (tokens → USD)

#### 2.2 UI/UX Improvements
**Why:** Make AI features discoverable and transparent

**Tasks:**
- [ ] **Storylet Editor Enhancements:**
  - [ ] Add "NL Condition Helper" button
  - [ ] Show suggestion templates:
    - "Character {name} feels {emotion}"
    - "Player has {quality} and {quality}"
    - "The situation is {description}"
  - [ ] Add validation: warn if NL condition is too vague
  - [ ] Add preview: "This will use AI evaluation"

- [ ] **World Director Panel Enhancements:**
  - [ ] Display current tick statistics:
    - AI evaluations count
    - Total tokens used
    - Cache hit rate
  - [ ] Add "AI Evaluation Log" expander:
    - Show each NL condition evaluated
    - Show confidence score
    - Show reasoning
  - [ ] Add session token tracker with cost estimate

- [ ] **Settings Panel:**
  - [ ] Add "Clear AI Cache" button
  - [ ] Add cache statistics display
  - [ ] Add token limit configuration

#### 2.3 Tutorial Content
**Why:** Lower learning curve for new users

**Tasks:**
- [ ] Write "5-Minute AI Director Guide":
  - [ ] What is AI enhancement?
  - [ ] When to use each mode?
  - [ ] Your first NL condition
  - [ ] Understanding AI decisions
- [ ] Create comparison document:
  - [ ] Traditional QBN example
  - [ ] Same scenario with AI enhancement
  - [ ] Side-by-side benefits
- [ ] Prepare demo project:
  - [ ] Small story (5-10 scenes)
  - [ ] Mix of traditional and NL conditions
  - [ ] Comments explaining design choices
  - [ ] Name: `ai_demo_project/`

---

### Priority 3: Optional Improvements / 可选优化 ⭐

#### 3.1 Error Handling Enhancement
**Tasks:**
- [ ] Graceful degradation: fallback to deterministic on LLM failure
- [ ] User-friendly error messages:
  - [ ] "API key not configured" with setup link
  - [ ] "Token limit exceeded" with upgrade suggestion
  - [ ] "LLM request failed" with retry option
- [ ] Add retry mechanism (max 3 attempts with exponential backoff)
- [ ] Add error logging to file for debugging

#### 3.2 AI Prompt Optimization
**Tasks:**
- [ ] Collect 10+ real evaluation cases
- [ ] Test different prompt variations
- [ ] Optimize `_build_context()` output:
  - [ ] More concise state description
  - [ ] Only include relevant variables
  - [ ] Better formatting
- [ ] Consider adding few-shot examples to prompt
- [ ] A/B test prompts with different LLMs

#### 3.3 Caching Strategy Improvements
**Tasks:**
- [ ] Add cache statistics tracking
- [ ] Implement persistent cache:
  - [ ] Save cache to `.cache/ai_evaluations.json`
  - [ ] Load cache on startup
  - [ ] Add cache expiration (24 hours?)
- [ ] Add cache management UI:
  - [ ] Show cache size and hit rate
  - [ ] "Clear Cache" button
  - [ ] "Export Cache" for debugging

---

## 📊 Development Focus / 开发重点

### Core Strategy: "AI + Rules Hybrid Narrative Engine"
**Target Users:**
1. **Indie game developers** - Need powerful narrative tools without AAA budget
2. **Interactive fiction writers** - Want creative freedom beyond rigid branching
3. **Narrative designers** - Need explainable, controllable AI assistance

**Key Differentiators:**
1. ✅ User controls AI usage level (3 modes)
2. ✅ Hybrid approach (best of rules + AI)
3. ✅ Explainable decisions (confidence + reasoning)
4. ✅ Cost optimization (caching + smart evaluation)
5. 🔲 Rich examples demonstrating value (TODO)
6. 🔲 Clear documentation for adoption (TODO)

---

## 📝 Definition of Done / 完成标准

### v0.9 is Ready When:
- [ ] **Functionality:** All Priority 1 tasks completed
- [ ] **Quality:** No critical bugs, all tests passing
- [ ] **Documentation:** Core docs updated, quickstart guide exists
- [ ] **Examples:** At least 5 real NL condition storylets working
- [ ] **Performance:** Benchmarks documented, acceptable for target use
- [ ] **User Testing:** At least 2-3 people have tried AI features successfully

### Optional (Nice to Have):
- [ ] Priority 2 tasks: 50%+ completed
- [ ] Tutorial video or comprehensive written guide
- [ ] Community feedback incorporated
- [ ] Performance optimizations applied

---

## 🔄 Review & Adjust / 审查和调整

**Review Frequency:** Weekly or after completing major tasks

**Questions to Ask:**
1. Are we still aligned with core value proposition?
2. What user feedback have we received?
3. What's blocking progress?
4. Do priorities need adjustment?
5. Should we add/remove tasks?

**Update This Document:**
- Mark completed tasks with `[x]`
- Add new insights and learnings
- Adjust priorities based on findings
- Remove tasks that no longer make sense
- Add discovered tasks

---

## 📌 Next Steps / 下一步

**Recommended Starting Point:**
1. **Create NL condition examples** (Priority 1.1)
   - Start with `town_factions` project
   - Add 2-3 simple NL conditions first
   - Test with all three modes
   - Gather learnings

2. **Run basic testing** (Priority 1.2)
   - Focus on happy path first
   - Document any issues found
   - Fix critical bugs before proceeding

3. **Update developer guide** (Priority 1.3)
   - Add AI architecture section
   - Keep it concise initially
   - Expand based on questions

---

**Let's build the first truly AI-enhanced narrative engine! 🚀**
