# AI Conditions Testing Session
## Date: 2026-01-13
## Purpose: Test v0.9 AI-enhanced natural language conditions

---

## 🧪 Test Plan

### Test 1: Load Project and Configure AI Mode
**Objective:** Verify AI mode selector works correctly

**Steps:**
1. ✅ Open http://localhost:8501
2. Load `town_factions` project (click folder icon or use sidebar)
3. Navigate to 🎬 World Director tab
4. Check that AI mode selector appears with 3 options:
   - 🔧 Deterministic
   - 🤖 AI-Assisted
   - 🧠 AI-Primary

**Expected Result:**
- All three modes visible
- Default should be AI-Assisted
- Help text displays for selected mode

**Actual Result:**
- [ ] Pass / [ ] Fail
- Notes: _____________________

---

### Test 2: Run Initial Scene Setup
**Objective:** Initialize world state for testing

**Steps:**
1. Go to 🎬 World Director tab
2. Click "Run Initial Scene" or similar setup
3. Check World State tab to verify:
   - `world.vars.merchants_power` = 60
   - `world.vars.assembly_power` = 40
   - `world.vars.guard_power` = 50
   - `world.vars.market_peace` = 70
   - `world.vars.public_sentiment` = 50

**Expected Result:**
- Initial state set correctly
- All faction powers initialized

**Actual Result:**
- [ ] Pass / [ ] Fail
- Initial state: _____________________

---

### Test 3: Test Deterministic Mode (Baseline)
**Objective:** Verify traditional storylets still work, NL storylets skipped

**Steps:**
1. Set Director Mode to "🔧 Deterministic"
2. Click "Run Tick" 5 times
3. Observe which storylets fire

**Expected Result:**
- Only traditional storylets fire (st-trade-boom, st-price-protest, etc.)
- NO NL storylets fire (st-nl-* should be filtered out)
- Response time: <1ms per tick
- Token usage: 0

**Actual Result:**
- [ ] Pass / [ ] Fail
- Storylets fired: _____________________
- Any NL storylets? _____________________

---

### Test 4: Test AI-Assisted Mode (Hybrid)
**Objective:** Test mixed evaluation - traditional + NL conditions

**Steps:**
1. **Reset state** (reload project or set to known state)
2. Set Director Mode to "🤖 AI-Assisted"
3. Run "Run Tick" 10 times
4. Observe:
   - Which storylets fire
   - AI evaluation logs (if visible)
   - Token consumption
   - Response time

**Expected Result:**
- Both traditional AND NL storylets can fire
- NL storylets show AI evaluation reasoning
- Response time: ~500ms when NL conditions evaluated
- Token usage: 200-800 per NL evaluation

**Actual Result:**
- [ ] Pass / [ ] Fail
- Traditional storylets: _____________________
- NL storylets fired: _____________________
- Token usage: _____________________
- Response time: _____________________

**NL Storylets to Watch For:**
- `st-nl-peaceful-atmosphere` (should fire when peace > 70 and sentiment > 50)
- `st-nl-wealthy-merchant-approach` (may fire if conditions right)
- `st-nl-factional-tension` (should fire if tensions rise)

---

### Test 5: Trigger Specific NL Condition
**Objective:** Force a specific NL condition to evaluate

**Scenario A: Peaceful Atmosphere**
**Setup:**
1. Manually set (or engineer through ticks):
   - `market_peace` = 75
   - `public_sentiment` = 65
   - All faction powers balanced (50-55 range)
2. Set AI mode to AI-Assisted
3. Run Tick

**Expected:** `st-nl-peaceful-atmosphere` should fire
- NL condition: "The town atmosphere is peaceful, safe, and optimistic"
- AI should judge this as TRUE given high peace and sentiment

**Actual Result:**
- [ ] Fired / [ ] Did not fire
- AI reasoning: _____________________

---

**Scenario B: Desperation Rising**
**Setup:**
1. Manually set:
   - `public_sentiment` = 35
   - `market_peace` = 45
   - `merchants_power` = 68 (exploiting people)
2. Run Tick

**Expected:** `st-nl-desperation-rising` should fire
- NL condition: "The common people are desperate, hungry, and losing hope"

**Actual Result:**
- [ ] Fired / [ ] Did not fire
- AI reasoning: _____________________

---

**Scenario C: Power Balance**
**Setup:**
1. Manually set:
   - `merchants_power` = 52
   - `assembly_power` = 51
   - `guard_power` = 53
2. Run Tick

**Expected:** `st-nl-power-balance` should fire
- NL condition: "All three factions have roughly equal power"

**Actual Result:**
- [ ] Fired / [ ] Did not fire
- AI reasoning: _____________________

---

### Test 6: Test AI-Primary Mode
**Objective:** Maximum AI involvement, all conditions evaluated by AI

**Steps:**
1. Set Director Mode to "🧠 AI-Primary"
2. Run Tick 5 times
3. Observe behavior differences from AI-Assisted

**Expected Result:**
- Even traditional conditions get AI "second opinion"
- Most flexible but highest token cost
- Response time: 1-2s per tick
- Token usage: 500-2000 per tick

**Actual Result:**
- [ ] Pass / [ ] Fail
- Token usage: _____________________
- Response time: _____________________
- Differences from AI-Assisted: _____________________

---

### Test 7: Cache Effectiveness
**Objective:** Verify AI results are cached

**Steps:**
1. Set AI-Assisted mode
2. Engineer a specific state (e.g., peaceful atmosphere)
3. Run Tick (NL condition evaluated, should use tokens)
4. **Don't change state**
5. Run Tick again immediately

**Expected Result:**
- First tick: AI evaluation, tokens consumed
- Second tick: Cache hit, 0 tokens consumed
- Response time: <1ms on second tick (cached)

**Actual Result:**
- [ ] Pass / [ ] Fail
- First tick tokens: _____________________
- Second tick tokens: _____________________
- Cache hit observed: [ ] Yes / [ ] No

---

### Test 8: Edge Cases
**Objective:** Test error handling

**Test A: Missing API Key**
1. Temporarily remove/invalidate API key
2. Try to run tick in AI-Assisted mode

**Expected:** Graceful error message, doesn't crash

**Actual:** _____________________

---

**Test B: Very Long NL Condition**
1. Add storylet with 300+ character NL condition
2. Try to evaluate

**Expected:** Either works or clear error about length

**Actual:** _____________________

---

**Test C: Ambiguous NL Condition**
1. Test with vague condition: "Something feels off"
2. Observe AI behavior

**Expected:** AI attempts evaluation, may have low confidence

**Actual:** _____________________

---

### Test 9: Mode Switching
**Objective:** Verify switching between modes works correctly

**Steps:**
1. Start in Deterministic
2. Run 3 ticks (note results)
3. Switch to AI-Assisted
4. Run 3 ticks (note results)
5. Switch to AI-Primary
6. Run 3 ticks (note results)

**Expected Result:**
- No errors on mode switch
- Behavior changes appropriately
- State persists correctly across switches

**Actual Result:**
- [ ] Pass / [ ] Fail
- Issues: _____________________

---

### Test 10: Token Management
**Objective:** Verify token tracking and limits work

**Steps:**
1. Check initial token stats (should be 0)
2. Run 20 ticks in AI-Assisted mode
3. Check updated token stats
4. Verify counts are reasonable

**Expected Result:**
- Token stats update after each AI call
- Cumulative count increases
- Daily limit warning if approaching limit

**Actual Result:**
- [ ] Pass / [ ] Fail
- Tokens after 20 ticks: _____________________
- Average per tick: _____________________
- Warning displayed: [ ] Yes / [ ] No

---

## 📊 Summary Results

### Overall Test Success Rate
- Total tests: 10
- Passed: ___ / 10
- Failed: ___ / 10
- Success rate: ___%

### Critical Issues Found
1. _____________________
2. _____________________
3. _____________________

### Minor Issues Found
1. _____________________
2. _____________________
3. _____________________

### Performance Metrics
| Mode          | Avg Response Time | Avg Token/Tick | Notes              |
|---------------|-------------------|----------------|--------------------|
| Deterministic | ___ms             | 0              | __________________ |
| AI-Assisted   | ___ms             | ___            | __________________ |
| AI-Primary    | ___ms             | ___            | __________________ |

### Most Interesting Findings
1. _____________________
2. _____________________
3. _____________________

---

## 🎯 Next Steps

Based on test results:
- [ ] Fix critical bugs
- [ ] Optimize performance if needed
- [ ] Improve error messages
- [ ] Adjust AI prompts
- [ ] Update documentation based on findings

---

## ✅ Sign-off

**Tester:** _____________________
**Date:** 2026-01-13
**Overall Assessment:** [ ] Ready for v0.9 / [ ] Needs work / [ ] Blocked

**Notes:** 
_____________________
_____________________
