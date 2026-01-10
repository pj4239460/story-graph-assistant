# World Director System Guide

## Overview

The **World Director** is a narrative design system that creates emergent, replayable stories using **storylets** (narrative fragments) and **dynamic state management**. Instead of manually authoring every story branch, you define:

1. **World State** - Variables, character moods, relationships
2. **Storylets** - Potential events with preconditions and effects
3. **Director Policy** - Pacing, diversity, and intensity preferences

The Director then automatically selects and triggers storylets based on the current state, creating unique stories that feel responsive and dynamic.

## Design Philosophy

### Traditional Branching vs World Director

**Traditional Branching Narrative:**
```
Scene A → Choice 1 → Scene B1 → Choice 2 → Scene C1
       → Choice 2 → Scene B2 → Choice 3 → Scene C2
                             → Choice 4 → Scene C3
```
- Manually author every path
- Exponential complexity: N scenes → N² branches
- Hard to maintain consistency across paths
- Limited replayability (same choices = same story)

**World Director Approach:**
```
State + Storylets → Director → Selected Events → New State
```
- Define reusable narrative fragments
- Linear complexity: N storylets → ∞ combinations
- Automatic consistency (state-driven)
- High replayability (different states = different stories)

### Inspirations

**Quality-Based Narrative (QBN)**
- Pioneered by Emily Short and Failbetter Games
- Used in: Fallen London, 80 Days, Sunless Sea
- Key insight: Stories emerge from *qualities* (state) not *trees* (branches)

**AI Director (Left 4 Dead)**
- Valve's dynamic difficulty and pacing system
- Monitors player stress and fatigue
- Creates "peaks and valleys" for engagement
- Adapts in real-time without player awareness

## Core Concepts

### 1. Storylets

A storylet is a self-contained narrative unit:

```json
{
  "id": "st-merchant-strike",
  "title": "Merchant Strike",
  "description": "Workers demand better wages",
  "tags": ["economic", "conflict"],
  "preconditions": [
    {"path": "world.vars.workers_dissatisfaction", "op": ">=", "value": 70},
    {"path": "world.vars.merchants_power", "op": ">", "value": 50}
  ],
  "effects": [
    {
      "scope": "world",
      "target": "world",
      "op": "add",
      "path": "vars.workers_dissatisfaction",
      "value": -20,
      "reason": "Strike releases tension"
    },
    {
      "scope": "world",
      "target": "world",
      "op": "add",
      "path": "vars.merchants_power",
      "value": -10,
      "reason": "Strike hurts merchant influence"
    }
  ],
  "weight": 2.0,
  "cooldown": 5,
  "once": false,
  "intensity_delta": 0.5
}
```

**Key Properties:**
- `id`: Unique identifier
- `title`: Human-readable name
- `tags`: Categories for diversity tracking
- `preconditions`: What must be true to trigger
- `effects`: What changes when triggered
- `weight`: Selection probability (higher = more likely)
- `cooldown`: Minimum ticks before can trigger again
- `once`: Can only trigger once per playthrough
- `intensity_delta`: Impact on story intensity (-1.0 to +1.0)

### 2. Preconditions

Preconditions determine *when* a storylet can trigger:

```json
{
  "path": "world.vars.faction_a_power",
  "op": ">=",
  "value": 60
}
```

**Path Types:**
- `world.vars.<key>` - World state variables
- `characters.<id>.<field>` - Character properties (mood, status, traits, etc.)
- `relationships.<a|b>.<field>` - Relationship values (trust, status, etc.)

**Operators:**
- Comparison: `==`, `!=`, `<`, `<=`, `>`, `>=`
- Membership: `in` (value in list), `contains` (list contains value)

**Examples:**
```json
// World variable comparison
{"path": "world.vars.tension", "op": ">=", "value": 70}

// Character mood check
{"path": "characters.alice.mood", "op": "==", "value": "angry"}

// Trait checking
{"path": "characters.bob.traits", "op": "contains", "value": "brave"}

// Relationship trust
{"path": "relationships.alice|bob.trust", "op": ">", "value": 50}
```

### 3. Effects

Effects define *what happens* when a storylet triggers:

```json
{
  "scope": "character",
  "target": "alice",
  "op": "set",
  "path": "mood",
  "value": "relieved",
  "reason": "Resolved the conflict peacefully"
}
```

**Scopes:**
- `world` - Modify world variables
- `character` - Modify character state
- `relationship` - Modify relationship between two characters

**Operations:**
- `set` - Replace value
- `add` - Increment/append
- `remove` - Decrement/delete

**Examples:**
```json
// Change character mood
{
  "scope": "character",
  "target": "alice",
  "op": "set",
  "path": "mood",
  "value": "angry"
}

// Add character trait
{
  "scope": "character",
  "target": "alice",
  "op": "add",
  "path": "traits",
  "value": "paranoid"
}

// Increase relationship trust
{
  "scope": "relationship",
  "target": "alice|bob",
  "op": "add",
  "path": "trust",
  "value": 10
}

// Set world variable
{
  "scope": "world",
  "target": "world",
  "op": "set",
  "path": "vars.war_declared",
  "value": true
}
```

### 4. Director Configuration

The Director's behavior is controlled by policy parameters:

```json
{
  "events_per_tick": 2,
  "diversity_window": 5,
  "diversity_penalty": 0.5,
  "intensity_min": 0.2,
  "intensity_max": 0.8,
  "intensity_decay": 0.1,
  "pacing_preference": "balanced"
}
```

**Parameters:**
- `events_per_tick` (1-5): How many storylets to select each tick
- `diversity_window` (0-20): How many recent ticks to check for repetition
- `diversity_penalty` (0.0-1.0): Weight reduction for recently-used tags
- `intensity_min/max` (0.0-1.0): Intensity bounds
- `intensity_decay` (0.0-0.5): How quickly intensity returns to 0.5
- `pacing_preference`: "calm", "balanced", or "intense"

## Selection Pipeline

The Director uses a multi-stage process to select storylets (updated in v1.7.1):

### Stage 1: Precondition Filtering

```
All Storylets → Evaluate Preconditions → Candidates
```

- Separate regular and fallback storylets
- Evaluate each regular storylet's preconditions against current state
- Keep only storylets where **ALL** preconditions are satisfied
- Generate explanations for each evaluation

**Example:**
```
Storylet: "Merchant Strike"
Preconditions:
  ✓ world.vars.workers_dissatisfaction = 75 (satisfies >= 70)
  ✓ world.vars.merchants_power = 60 (satisfies > 50)
→ Candidate
```

### Stage 2: Ordering Constraints (v1.7.1 NEW!)

```
Candidates → Check Ordering → Ordered Candidates
```

**requires_fired**: Storylet can only trigger AFTER specified storylets have fired
**forbids_fired**: Storylet can only trigger if specified storylets have NOT fired

- Check `requires_fired` list: ALL must have triggered
- Check `forbids_fired` list: NONE must have triggered
- Use for: Quest chains, mutually exclusive paths, narrative dependencies

**Example - Quest Chain:**
```json
{
  "id": "quest_middle",
  "title": "Quest Progress",
  "requires_fired": ["quest_start"]
}
→ Will only appear after "quest_start" has triggered

{
  "id": "quest_end",
  "title": "Quest Complete",
  "requires_fired": ["quest_start", "quest_middle"]
}
→ Requires both previous steps
```

**Example - Mutually Exclusive Paths:**
```json
{
  "id": "peaceful_resolution",
  "title": "Peace Treaty",
  "once": true
}

{
  "id": "violent_resolution",
  "title": "All-Out War",
  "forbids_fired": ["peaceful_resolution"],
  "once": true
}
→ Can't have war if peace treaty signed
```

### Stage 3: Cooldown & Once Filtering

```
Ordered Candidates → Check Cooldown/Once → Available
```

- Remove storylets still on cooldown
  - Check `last_triggered[storylet_id] + cooldown <= current_tick`
- Remove "once" storylets that have already triggered
  - Check `triggered_once[storylet_id] == true`

### Stage 4: Fallback Check (v1.7.1 NEW!)

```
Available → Check if Empty → Fallback Candidates
```

If no regular storylets are available:
- Check idle tick counter: `idle_tick_count >= fallback_after_idle_ticks`
- If threshold reached, evaluate fallback storylets
- Fallback storylets undergo same precondition/ordering/cooldown checks

**Purpose**: Prevents "world stuck" - ensures story always progresses

**Example Fallback Storylets:**
```json
{
  "id": "weather_changes",
  "title": "The Weather Shifts",
  "is_fallback": true,
  "preconditions": [],  // No requirements
  "effects": [],  // Ambient event
  "cooldown": 3,
  "intensity_delta": 0.0  // Neutral
}

{
  "id": "crowd_activity",
  "title": "Market Crowd Activity",
  "is_fallback": true,
  "preconditions": [],
  "effects": [
    {"scope": "world", "op": "add", "path": "vars.market_activity", "value": 5}
  ],
  "cooldown": 2,
  "intensity_delta": -0.1
}
```

### Stage 5: Diversity Penalty

```
Available → Apply Diversity Penalty → Weighted Candidates
```

- Check recent ticks for tag repetition
- Reduce weight for storylets with recently-used tags
- Formula: `weight *= (1 - diversity_penalty) ^ penalty_count`

**Example:**
```
Storylet: "Trade Boom" (tags: ["economic", "positive"])
Recent tags: ["economic", "economic", "political"]
Penalty count: 2 (tag "economic" appears twice)
New weight: 1.5 * (1 - 0.5)² = 0.375
```

### Stage 6: Pacing Adjustment

```
Weighted Candidates → Apply Pacing Adjustment → Final Weights
```

- Check current intensity vs storylet `intensity_delta`
- If too intense, favor calming storylets (negative delta)
- If too calm, favor escalating storylets (positive delta)
- Formula: `weight *= 1 + pacing_scale * (target_adjustment * delta)`

**Example:**
```
Current intensity: 0.8 (too high)
Storylet: "Peace Treaty" (intensity_delta: -0.3)
Target: Reduce intensity
Adjustment: Favor negative deltas
New weight: weight * 1.5  // Boost calming storylets
```

### Stage 7: Weighted Selection

```
Final Weights → Normalize → Select N without Replacement
```

- Normalize weights to probabilities
- Select `events_per_tick` storylets
- Use weighted random sampling without replacement
- Record rationale for each selection

**Example:**
```
Final candidates:
  - "Trade Boom" (weight: 1.2, prob: 0.40)
  - "Worker Strike" (weight: 0.9, prob: 0.30)
  - "Festival" (weight: 0.9, prob: 0.30)

Select 2:
→ "Trade Boom" (40% chance)
→ "Worker Strike" (30% chance)
```

### Stage 8: Effect Application

```
Selected Storylets → Apply Effects → New State + Diff
```

- Deep copy current state (for diff calculation)
- Apply each storylet's effects in order
- Compute human-readable state diff (before/after)
- Update intensity based on storylet deltas
- Update idle tick counter:
  - If regular storylets selected: Reset `idle_tick_count = 0`
  - If no storylets selected: Increment `idle_tick_count += 1`

**Example:**
```
Before:
  world.vars.merchants_power = 60
  world.vars.public_sentiment = 50

Apply: "Trade Boom"
  Effect: world.vars.merchants_power += 10

After:
  world.vars.merchants_power = 70
  world.vars.public_sentiment = 50

Diff:
  world.vars.merchants_power: 60 → 70
  
Idle tracking:
  Regular storylet selected → idle_tick_count = 0
```

### Stage 9: History Recording

```
Tick Results → Create TickRecord → Append to History
```

- Create `TickRecord` with:
  - Tick number and timestamp
  - Selected storylets with rationale
  - Applied effects
  - State diff
  - Intensity before/after
  - Idle tick count (v1.7.1)
- Update cooldown tracking
- Update "once" tracking
- Update triggered_once for ordering constraints (v1.7.1)
- Append to `TickHistory`

## Best Practices

### Storylet Design

**1. Use Clear, Descriptive Titles**
```
✓ Good: "Merchant Guild Declares Embargo"
✗ Bad: "Event 17"
```

**2. Add Meaningful Tags**
```
✓ Good: ["economic", "conflict", "merchants"]
✗ Bad: ["misc", "other"]
```

**3. Set Appropriate Weights**
- 0.1 - Very rare special events
- 1.0 - Normal frequency
- 5.0 - Common recurring events
- 10.0 - Almost always available

**4. Use Cooldowns to Prevent Repetition**
```
✓ Good: cooldown: 5  // Can't trigger again for 5 ticks
✗ Bad: cooldown: 0   // Can trigger every tick
```

**5. Balance Intensity Deltas**
```
Positive (escalating): +0.3 to +0.5
Neutral: 0.0
Negative (calming): -0.3 to -0.5
```

### Precondition Tips

**1. Use Ranges, Not Exact Values**
```
✓ Good: {"path": "world.vars.tension", "op": ">=", "value": 70}
✗ Bad: {"path": "world.vars.tension", "op": "==", "value": 75}
```

**2. Combine Multiple Conditions**
```
✓ Good:
[
  {"path": "world.vars.faction_a_power", "op": ">", "value": 60},
  {"path": "world.vars.faction_b_power", "op": "<", "value": 40}
]
```

**3. Test Edge Cases**
- What if value is 0?
- What if character doesn't exist?
- What if relationship hasn't been established?

### Pacing Control

**High Diversity Penalty (0.7-1.0)**
- More variety in storylets
- Prevents "spam" of same tags
- Good for long playthroughs

**Low Diversity Penalty (0.0-0.3)**
- More repetition allowed
- Focuses on most relevant storylets
- Good for short, intense sequences

**Intensity Decay**
- High (0.3-0.5): Quick return to calm
- Medium (0.1-0.2): Gradual pacing
- Low (0.01-0.05): Long intense/calm periods

**Pacing Preference**
- "calm": Favors low-intensity storylets
- "balanced": Maintains intensity around 0.5
- "intense": Favors high-intensity storylets

## Example: Town of Riverhaven

See `examples/town_factions/project.json` for a complete implementation.

**Setting:**
- Three competing factions: Merchants' Guild, People's Assembly, Ironwatch Guard
- Dynamic power balance
- Economic, political, and conflict events

**Storylets (20 total):**
- Economic: Trade boom, smuggling, monopoly, strikes
- Political: Protests, rallies, elections, reforms
- Conflict: Crackdowns, riots, tax disputes
- Disasters: Fires, food shortages
- Positive: Festivals, peace treaties

**Try This:**
1. Load the example
2. Create a new thread (Play Path mode)
3. Navigate to World Director tab
4. Run 10+ ticks with default settings
5. Observe how the story emerges

**What to Notice:**
- Different runs produce different stories
- Factions rise and fall organically
- Events have clear cause-and-effect
- Each tick includes explanations

## Troubleshooting

### "No storylets selected"
**Cause:** No storylets satisfy preconditions
**Fix:** 
- Check initial state values
- Verify precondition operators
- Add storylets with no preconditions (always available)

### "Same storylets keep triggering"
**Cause:** Low diversity penalty or high weights
**Fix:**
- Increase diversity_penalty (0.5-0.8)
- Add more storylets with same tags
- Use cooldowns (3-5 ticks)

### "Story feels repetitive"
**Cause:** Not enough state mutation
**Fix:**
- Ensure effects actually change state
- Add more world variables
- Use cumulative effects (add, not set)

### "Intensity stays at extremes"
**Cause:** Unbalanced intensity_delta values
**Fix:**
- Balance positive and negative deltas
- Increase intensity_decay
- Add more neutral storylets (delta: 0.0)

## Advanced Topics

### Multi-Actor Systems
Future enhancement: Multiple characters making simultaneous decisions
```json
{
  "actors": ["alice", "bob", "guard"],
  "selection_mode": "parallel",
  "conflict_resolution": "priority"
}
```

### Time-Based Triggers
Future enhancement: Storylets that trigger after N ticks
```json
{
  "trigger_condition": {
    "type": "time",
    "ticks_since": "st-war-declared",
    "min_ticks": 10
  }
}
```

### State Queries in Preconditions
Future enhancement: More complex condition logic
```json
{
  "precondition": {
    "type": "aggregation",
    "operation": "sum",
    "paths": ["world.vars.faction_a_power", "world.vars.faction_b_power"],
    "op": ">",
    "value": 100
  }
}
```

---

## Best Practices & Troubleshooting (v1.7.1 Updated)

### Using Ordering Constraints Effectively

**When to use `requires_fired`:**
- Quest chains with mandatory progression
- Story arcs that must unfold in sequence
- Prerequisites for branching narratives
- Tutorial sequences

**Example - Tutorial Chain:**
```json
[
  {
    "id": "tut_basics",
    "title": "Tutorial: Basics",
    "once": true
  },
  {
    "id": "tut_advanced",
    "title": "Tutorial: Advanced Techniques",
    "requires_fired": ["tut_basics"],
    "once": true
  }
]
```

**When to use `forbids_fired`:**
- Mutually exclusive story paths
- Consequences of previous choices
- Preventing contradictory events
- Alternative endings

**Example - Faction Paths:**
```json
[
  {
    "id": "join_guild",
    "title": "Join the Merchant Guild",
    "once": true,
    "effects": [{"scope": "world", "op": "set", "path": "vars.faction", "value": "guild"}]
  },
  {
    "id": "join_rebels",
    "title": "Join the Rebellion",
    "forbids_fired": ["join_guild"],
    "once": true,
    "effects": [{"scope": "world", "op": "set", "path": "vars.faction", "value": "rebels"}]
  },
  {
    "id": "guild_quest_1",
    "title": "Guild Mission: Escort",
    "requires_fired": ["join_guild"],
    "forbids_fired": ["join_rebels"]
  }
]
```

### Designing Fallback Storylets

**Characteristics of Good Fallback Storylets:**
1. **No preconditions** or very minimal requirements
2. **Ambient/atmospheric** - enhance world without major plot impact
3. **Neutral intensity** (0.0 or slight negative like -0.1)
4. **Moderate cooldown** (2-5 ticks) to provide variety

**Example - Environmental Fallbacks:**
```json
[
  {
    "id": "weather_clear",
    "title": "☀️ Clear Skies",
    "is_fallback": true,
    "preconditions": [],
    "effects": [],
    "cooldown": 3,
    "intensity_delta": 0.0,
    "tags": ["ambient", "weather"]
  },
  {
    "id": "weather_rain",
    "title": "🌧️ Rain Begins",
    "is_fallback": true,
    "preconditions": [],
    "effects": [{"scope": "world", "op": "set", "path": "vars.weather", "value": "rain"}],
    "cooldown": 3,
    "intensity_delta": -0.05,
    "tags": ["ambient", "weather"]
  },
  {
    "id": "crowd_activity",
    "title": "👥 Market Bustle",
    "is_fallback": true,
    "preconditions": [],
    "effects": [{"scope": "world", "op": "add", "path": "vars.market_activity", "value": 5}],
    "cooldown": 2,
    "intensity_delta": -0.1,
    "tags": ["ambient", "economic"]
  }
]
```

**Recommended Settings:**
- `fallback_after_idle_ticks: 3` (default) - Good balance for most stories
- Create 5-10 fallback storylets for variety
- Use diversity tags to prevent repetition

### Troubleshooting: World Gets Stuck

**Symptom:** No storylets fire, idle tick count keeps increasing

**Diagnostic Steps:**
1. Check idle tick counter in UI status bar
2. Review preconditions of all storylets
3. Verify fallback storylets exist

**Common Causes:**
- All storylets have preconditions that can't be satisfied
- No fallback storylets defined
- Fallback storylets also have blocking preconditions
- All storylets on cooldown simultaneously

**Solutions:**
```json
// Add simple fallbacks with NO preconditions
{
  "id": "time_passes",
  "title": "Time Passes Quietly",
  "is_fallback": true,
  "preconditions": [],  // IMPORTANT: Empty!
  "effects": [],
  "cooldown": 1,
  "intensity_delta": -0.2
}
```

### Troubleshooting: Quest Chain Broken

**Symptom:** Middle steps of quest never appear

**Diagnostic Steps:**
1. Check `triggered_once` in tick history
2. Verify spelling of storylet IDs in `requires_fired`
3. Check if storylet has conflicting `forbids_fired`

**Common Mistakes:**
```json
// ❌ WRONG - Typo in requires_fired
{
  "id": "quest_part_2",
  "requires_fired": ["quest_part_1"],  // ID is actually "quest_pt_1"
}

// ✅ CORRECT - Match exact IDs
{
  "id": "quest_part_2",
  "requires_fired": ["quest_pt_1"],
}
```

### Troubleshooting: Fallbacks Not Triggering

**Symptom:** idle_tick_count exceeds threshold, but fallbacks don't fire

**Diagnostic Steps:**
1. Check fallback storylets have `"is_fallback": true`
2. Verify fallback preconditions are satisfied
3. Check fallback cooldowns
4. Confirm `fallback_after_idle_ticks` setting

**Example Fix:**
```json
// ❌ PROBLEM - Fallback with blocking precondition
{
  "id": "fallback_event",
  "is_fallback": true,
  "preconditions": [
    {"scope": "world", "path": "vars.impossible_condition", "op": "==", "value": 999}
  ]
}

// ✅ SOLUTION - Remove preconditions or make them trivial
{
  "id": "fallback_event",
  "is_fallback": true,
  "preconditions": []
}
```

### Performance Considerations

**Large Storylet Pools (100+ storylets):**
- Precondition evaluation is O(n)
- Use specific preconditions to filter early
- Consider splitting into separate scenes/contexts

**Deep Quest Chains (10+ steps):**
- Use `once: true` to prevent re-triggering
- Verify chain completeness with tests
- Consider using state variables for progress tracking

**Recommended Limits:**
- 50-100 storylets per context (good performance)
- 5-10 storylets per tick (narrative clarity)
- 3-5 levels of `requires_fired` depth (maintainability)

## References

- Emily Short's Storylet Work: https://emshort.blog/2019/11/29/storylets-you-want-them/
- Left 4 Dead AI Director: https://steamcdn-a.akamaihd.net/apps/valve/2009/ai_systems_of_l4d_mike_booth.pdf
- Quality-Based Narrative: https://www.gdcvault.com/play/1015317/
- Fallen London Design: https://www.failbettergames.com/news/

## Next Steps

1. **Try the Example**: Load Town of Riverhaven and run 10+ ticks
2. **Create Your Own**: Define 5-10 storylets for your setting
3. **Tune Parameters**: Experiment with diversity and pacing settings
4. **Iterate**: Add more storylets based on what feels missing
5. **Share**: Export tick logs and share your emergent stories!
