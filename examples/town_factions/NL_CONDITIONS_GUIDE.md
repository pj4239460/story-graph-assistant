# Natural Language Conditions Guide
## Town Factions Project - AI-Enhanced Storylets

> **Version:** v0.9 (AI Enhancement)  
> **Purpose:** Demonstrate the power of AI-enhanced natural language conditions

---

## 🎯 What are NL Conditions?

Natural Language (NL) conditions allow you to write storylet preconditions in plain English/Chinese instead of rigid numeric comparisons. The AI evaluates whether the condition is satisfied based on the current game state.

### Traditional Condition Example:
```json
"preconditions": [
  {"path": "world.vars.merchants_power", "op": ">=", "value": 60},
  {"path": "world.vars.public_sentiment", "op": ">", "value": 50},
  {"path": "world.vars.guard_power", "op": "<", "value": 55}
]
```
**Problem:** Requires exact thresholds, hard to express nuance, rigid logic.

### NL Condition Example:
```json
"preconditions": [
  {"nl_condition": "The player appears wealthy and has a good reputation in town"}
]
```
**Advantage:** Natural expression, flexible interpretation, context-aware reasoning.

---

## 📊 10 AI-Enhanced Storylets in This Project

### 1. **Wealthy Merchant's Proposition** (`st-nl-wealthy-merchant-approach`)
**NL Condition:** `"The player appears wealthy and has a good reputation in town"`

**Why NL is Better:**
- Traditional approach would need: wealth > X AND reputation > Y
- But what defines "wealthy"? What's "good" reputation?
- NL condition lets AI judge contextually: Do behaviors/traits/possessions suggest wealth?
- More nuanced: Player might *appear* wealthy without high numeric wealth stat

**Use Case:** Social perception checks, reputation-based opportunities

---

### 2. **Brewing Factional Conflict** (`st-nl-factional-tension`)
**NL Condition:** `"Relations between the major factions are severely strained and hostile"`

**Why NL is Better:**
- Traditional: (merchants_power - assembly_power)² + (guard_power - merchants_power)² > threshold?
- Extremely awkward to express "all factions mutually hostile" in pure math
- NL condition: AI evaluates relationship dynamics, not just power differentials
- Captures *quality* of relations (strained, hostile) not just quantity

**Use Case:** Complex multi-party relationship states, conflict escalation

---

### 3. **Maya's Personal Appeal** (`st-nl-character-trust`)
**NL Condition:** `"Maya Chen trusts the player despite recent tensions or conflicts"`

**Why NL is Better:**
- Traditional: Can't track "trust despite conflicts" - no such variable exists!
- Would need separate trust counters, conflict counters, complex formulas
- NL condition: AI understands "despite" - reasoning about exceptions and nuance
- Emotional/relational intelligence impossible with numeric state alone

**Use Case:** Character relationships, emotional states, trust dynamics

---

### 4. **The Ethical Choice** (`st-nl-moral-dilemma`)
**NL Condition:** `"The player is facing a difficult ethical dilemma with no clear right answer"`

**Why NL is Better:**
- Traditional: How do you detect a "dilemma" numerically? Impossible!
- Dilemmas are narrative states, not world variables
- NL condition: AI recognizes complex moral situations from context
- Enables meta-narrative conditions (conditions *about* the story itself)

**Use Case:** Moral dilemmas, narrative meta-conditions, complex situations

---

### 5. **Days of Tranquility** (`st-nl-peaceful-atmosphere`)
**NL Condition:** `"The town atmosphere is peaceful, safe, and optimistic"`

**Why NL is Better:**
- Traditional: market_peace > 70 AND public_sentiment > 60 AND violence < 20?
- Missing: optimism, safety *feeling*, atmospheric quality
- NL condition: Holistic evaluation of multiple factors + qualitative assessment
- "Atmosphere" is emergent property, not simple sum of variables

**Use Case:** Atmospheric checks, mood assessment, emergent qualities

---

### 6. **Desperate Times** (`st-nl-desperation-rising`)
**NL Condition:** `"The common people are desperate, hungry, and losing hope"`

**Why NL is Better:**
- Traditional: food < 30 AND sentiment < 40 AND hope < 20?
- But "desperate" is qualitative state combining multiple factors
- NL condition: Understands "losing hope" (temporal/progressive aspect)
- Captures emotional intensity, not just numeric lows

**Use Case:** Crisis detection, emotional states, population mood

---

### 7. **Delicate Balance of Power** (`st-nl-power-balance`)
**NL Condition:** `"All three factions have roughly equal power, creating an unstable equilibrium"`

**Why NL is Better:**
- Traditional: |merchants - assembly| < 5 AND |assembly - guard| < 5 AND |guard - merchants| < 5?
- "Roughly equal" is fuzzy, context-dependent
- "Unstable equilibrium" adds qualitative meta-judgment
- NL condition: Understands both quantitative balance and qualitative instability

**Use Case:** Balance detection, equilibrium states, power dynamics

---

### 8. **Authoritarian Overreach** (`st-nl-guard-overreach`)
**NL Condition:** `"The guard is too powerful and acting in an authoritarian or oppressive manner"`

**Why NL is Better:**
- Traditional: guard_power > 65? (But high power ≠ oppression!)
- "Oppressive manner" is behavioral pattern, not power level
- Guards could be powerful but benevolent, or weak but brutal
- NL condition: Evaluates behavior and pattern, not just stats

**Use Case:** Behavioral patterns, qualitative judgments, action evaluation

---

### 9. **Economic Boom** (`st-nl-economic-prosperity`)
**NL Condition:** `"The town economy is booming and people are generally prosperous"`

**Why NL is Better:**
- Traditional: merchants_power > 60 AND sentiment > 60 AND trade_volume > X?
- "Booming" implies growth rate, not just level
- "Generally prosperous" = most people, not just average
- NL condition: Holistic economic assessment with temporal aspect

**Use Case:** Economic states, prosperity assessment, temporal trends

---

### 10. **Violence Imminent** (`st-nl-imminent-violence`)
**NL Condition:** `"The situation is extremely tense and violence seems imminent"`

**Why NL is Better:**
- Traditional: market_peace < 35 AND sentiment < 40 AND conflict > 70?
- "Imminent" = predictive judgment about near future
- "Extremely tense" = qualitative intensity
- NL condition: AI reasons about trajectories and breaking points

**Use Case:** Crisis prediction, escalation detection, breaking points

---

## 🎨 Design Patterns for NL Conditions

### 1. **Social Perception**
- "The player appears/seems [quality]"
- "Others view the player as [quality]"
- Example: "The player appears wealthy and trustworthy"

### 2. **Relationship Quality**
- "Character X [emotion/stance] the player"
- "Relations between X and Y are [quality]"
- Example: "Maya Chen trusts the player despite recent conflicts"

### 3. **Atmospheric/Holistic**
- "The [place] atmosphere is [qualities]"
- "The overall situation is [description]"
- Example: "The town atmosphere is peaceful and optimistic"

### 4. **Emotional States**
- "People are feeling [emotions]"
- "The populace is [emotional state]"
- Example: "The common people are desperate and losing hope"

### 5. **Behavioral Patterns**
- "Faction X is acting [manner]"
- "Character Y is behaving [description]"
- Example: "The guard is acting in an oppressive manner"

### 6. **Comparative Balance**
- "X and Y are roughly equal/balanced"
- "Power is distributed [pattern]"
- Example: "All factions have roughly equal power"

### 7. **Temporal/Progressive**
- "Situation is [temporal verb]"
- "Trend is [direction]"
- Example: "Violence seems imminent"

### 8. **Meta-Narrative**
- "The story is at [stage]"
- "Player faces [narrative situation]"
- Example: "The player faces a difficult ethical dilemma"

---

## 📈 Performance Comparison

| Condition Type | Evaluation Time | Token Cost | Expressiveness | Maintainability |
|----------------|-----------------|------------|----------------|-----------------|
| Traditional    | <1ms            | 0          | ⭐⭐☆☆☆          | ⭐⭐⭐☆☆          |
| NL (Cached)    | <1ms            | 0          | ⭐⭐⭐⭐⭐          | ⭐⭐⭐⭐⭐          |
| NL (Uncached)  | ~500ms          | 200-400    | ⭐⭐⭐⭐⭐          | ⭐⭐⭐⭐⭐          |

**Recommendation:** Use NL conditions for:
- Complex social/emotional states
- Multi-factor assessments
- Situations hard to express numerically
- When nuance matters more than speed

Use traditional conditions for:
- Simple numeric thresholds
- High-frequency checks
- Performance-critical paths
- When exact logic is clear

---

## 🔧 Using AI Modes with This Project

### Deterministic Mode (No AI)
- All NL condition storylets will be **skipped**
- Only traditional storylets fire
- Best for: Performance testing, reproducible simulations

### AI-Assisted Mode (Recommended)
- Traditional conditions checked first (fast)
- NL conditions evaluated by AI (when needed)
- Best for: Balanced experience, most users

### AI-Primary Mode (Maximum Flexibility)
- AI evaluates all conditions, even traditional ones
- Most expressive, most token usage
- Best for: Creative narrative experimentation

---

## 🎯 Testing These Storylets

1. **Load the project:**
   - Open Story Graph Assistant
   - Load `examples/town_factions/project.json`

2. **Configure AI mode:**
   - Go to 🎬 World Director tab
   - Select "AI-Assisted" mode (recommended for first try)

3. **Set up initial state:**
   - Run initial scene to set up world state
   - Check World State tab to see variables

4. **Run ticks and observe:**
   - Click "Run Tick" multiple times
   - Watch which storylets fire
   - Note the AI evaluation reasoning in logs

5. **Compare modes:**
   - Try running same state with different AI modes
   - See how NL condition storylets behave
   - Check token consumption statistics

---

## 💡 Writing Effective NL Conditions

### ✅ Good NL Conditions:
- **Clear and specific:** "The player is wealthy and respected"
- **Context-aware:** "Relations between factions are hostile"
- **Qualitative:** "The atmosphere feels tense and dangerous"
- **Natural language:** Write how you'd explain it to a human

### ❌ Poor NL Conditions:
- **Too vague:** "Something is wrong" (AI can't judge "something")
- **Too complex:** "If X then Y unless Z but considering W..." (break into multiple conditions)
- **Numeric duplicates:** "merchant_power is greater than 60" (just use traditional condition!)
- **Self-referential:** "This condition should trigger" (circular logic)

---

## 📚 Further Reading

- [AI Director Guide](../../docs/AI_DIRECTOR_GUIDE.md) - Complete AI features documentation
- [World Director Guide](../../docs/world_director_guide.md) - Storylet system fundamentals
- [Development Roadmap](../../DEVELOPMENT_ROADMAP.md) - Future AI enhancements

---

**Made with ❤️ to showcase AI-enhanced narrative design in v0.9**
