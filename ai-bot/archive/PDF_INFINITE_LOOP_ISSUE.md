# 🔴 CRITICAL: PDF Reading Infinite Loop Issue

**Date:** 2025-10-21
**Severity:** HIGH - Blocks entire bot for 5+ minutes
**Affected Bot:** Personal Assistant (`personal_assistant`)
**Status:** ❌ UNRESOLVED - Requires immediate fix

---

## 📊 Problem Summary

When user asks personal assistant to analyze a PDF file, the bot gets stuck in an **infinite binary search loop** trying to read the file with the Read tool, which:
1. **Blocks the bot** for 5+ minutes
2. **Fails subsequent requests** from the same user/room
3. **Wastes API tokens** (60+ failed tool calls)
4. **Never produces a result** - eventually times out

---

## 🔍 Root Cause Analysis

### What Happened

**User request:** "群里有一份pdf文件，分析这个文件并输出总结"

**Bot's attempt sequence:**
1. ✅ Detects PDF file in room: `/campfire-files/p4/8x/p48x22af3oaa4gxhhmjjb0yxwdsr`
2. ❌ Tries `Read(file_path)` → Fails (PDF is 295.7KB binary)
3. ❌ Tries `WebFetch(url='file:///campfire-files/...')` → Fails (WebFetch can't read local files)
4. ❌ Tries `Task(subagent_type='general-purpose')` → Subagent also can't read PDF
5. ❌ **ENTERS INFINITE LOOP** - Binary search for "perfect" limit value:
   ```
   Read(limit=2000) → Error
   Read(limit=1000) → Error
   Read(limit=1500) → Error
   Read(limit=1800) → Error
   Read(limit=1700) → Error
   ... 60+ attempts ...
   Read(limit=889) → Error
   Read(limit=887) → Error
   Read(limit=886) → Still trying...
   ```

6. ❌ After 5 minutes, second user request comes in → Gets blocked
7. ❌ Queue timeout → "Sorry, I'm overloaded right now"

### Why It Happens

#### 1. **No PDF Tool Available**
- Personal assistant doesn't have `pdf` skill loaded
- Skills MCP is enabled but bot doesn't know PDF is a skill
- System prompt only mentions docx, xlsx, pptx - **PDF is missing**

#### 2. **Read Tool Can't Handle Binary Files**
- Read tool expects text files (line-based reading)
- PDFs are binary - Read tool returns error or garbled bytes
- Each attempt with different `limit` also fails

#### 3. **No Retry Limit**
- Agent SDK has no max tool calls per turn
- Bot keeps trying to find the "sweet spot" limit value
- Binary search pattern: tries 2000, 1000, 1500, 1800, 1700, 1600, ... 889, 887, 886...
- No logic to say "I've tried 10 times, this won't work"

#### 4. **No Error Pattern Recognition**
- Bot doesn't recognize that ALL Read attempts are failing
- Doesn't understand that PDF requires special handling
- No guidance in prompt to "give up after N failures"

---

## 🎯 Impact

### User Experience
- **Immediate**: Request hangs for 5+ minutes with no response
- **Secondary**: Subsequent requests from same user/room fail
- **Perception**: Bot appears broken or slow

### System Impact
- **API Cost**: 60+ wasted tool calls @ ~$0.001 each = ~$0.06 per stuck request
- **Queue Blocking**: One stuck request blocks all requests for that room/bot
- **Resource**: Ties up agent session for 5+ minutes

### Scale Risk
- **Current**: 1-2 PDF requests/day = Manageable annoyance
- **If scaled**: 10 PDF requests/day = 50+ minutes of bot downtime
- **At scale**: 100 PDF requests/day = Bot effectively unusable

---

## ✅ Solutions

### Solution 1: Add PDF Skill Support (Immediate Fix)

**Update `personal_assistant.json` system prompt:**

```markdown
### 可用工具

1. **list_skills** - 查看所有可用技能
2. **load_skill** - 加载特定技能的专业知识
   - Word文档: load_skill(skill_name="docx")
   - Excel表格: load_skill(skill_name="xlsx")
   - PowerPoint: load_skill(skill_name="pptx")
   - PDF文档: load_skill(skill_name="pdf")  ← ADD THIS
3. **load_skill_file** - 加载技能的详细文档（第三级）

### 文档类型识别

**根据文件扩展名或用户描述识别文档类型：**
- `.docx`, `Word`, `word文档` → 加载 docx 技能
- `.xlsx`, `Excel`, `表格` → 加载 xlsx 技能
- `.pptx`, `PowerPoint`, `PPT` → 加载 pptx 技能
- `.pdf`, `PDF文件`, `pdf文档` → 加载 pdf 技能  ← ADD THIS
```

### Solution 2: Add Tool Retry Limits (Critical)

**Add to system prompt:**

```markdown
### ⚠️ CRITICAL: 工具使用限制

**避免工具滥用导致无限循环！**

1. **Read工具限制：**
   - ❌ **不要用Read工具读取PDF文件** - PDF是二进制文件，Read会失败
   - ❌ **不要反复尝试不同的limit值** - 如果Read失败3次，停止
   - ✅ **PDF必须用pdf技能** - 加载pdf技能后使用专门的PDF工具

2. **最多重试规则：**
   - **同一个工具最多调用3次**
   - 如果3次都失败，停止并告诉用户无法处理
   - 不要binary search寻找perfect limit

3. **错误处理流程：**
   ```
   如果工具调用失败：
   1. 第1次失败 → 尝试调整参数
   2. 第2次失败 → 尝试不同方法
   3. 第3次失败 → 停止并告诉用户

   ❌ 错误示例：
   Read(limit=2000) fails
   Read(limit=1000) fails
   Read(limit=1500) fails
   ... (60+ attempts) ❌ NEVER DO THIS

   ✅ 正确示例：
   Read(limit=2000) fails → "文件太大"
   尝试: load_skill("pdf")
   如果PDF工具不可用 → "抱歉，暂时无法处理此PDF"
   ```

4. **PDF文件特殊处理：**
   - 检测到PDF文件 → **直接加载PDF技能**
   - 不要先尝试Read工具
   - 不要尝试WebFetch
   - PDF = load_skill("pdf")
```

### Solution 3: SDK-Level Max Tool Calls (Systemic Fix)

**Update `src/campfire_agent.py`:**

```python
# In CampfireAgent.__init__() or create_agent()
agent = Agent(
    model=model_name,
    mcp_servers=mcp_servers,
    allowed_tools=allowed_tools,
    max_turns=10,
    max_tool_calls_per_turn=15,  # ← ADD THIS
    # ... other options
)
```

**Benefits:**
- Prevents ANY infinite loop, not just PDF
- Protects against future similar issues
- Graceful degradation instead of hang

**Note:** Check if Agent SDK supports `max_tool_calls_per_turn` parameter. If not available, we need to track it manually.

### Solution 4: Queue Timeout Improvements (UX Fix)

**Current behavior:**
- Request waits 5 minutes → "Sorry, I'm overloaded"
- No indication of what went wrong

**Better behavior:**
```python
# In app_fastapi.py, add timeout detection
@app.post("/webhook/{bot_id}")
async def webhook_handler(...):
    # ... existing code ...

    # Check if previous request is stuck
    if session_age > 5 minutes and tool_calls > 20:
        # Kill stuck session
        await session_manager.force_close_session(room_id, bot_id)
        logger.warning(f"[Queue] Killed stuck session for room {room_id}")

    # ... continue with new request
```

---

## 🧪 Test Cases

### Test Case 1: PDF File

**Input:** "群里有一份pdf文件，分析这个文件并输出总结"

**Expected behavior (after fix):**
1. Bot detects "PDF文件" → Identifies file type as PDF
2. Bot calls `load_skill("pdf")` → Loads PDF skill
3. Bot uses PDF skill tools to extract text and analyze
4. Bot returns summary with insights

**Current behavior (before fix):**
1. Bot tries Read → Fails
2. Bot tries WebFetch → Fails
3. Bot tries Read with binary search → 60+ failures
4. Bot times out after 5 minutes

### Test Case 2: Word Document

**Input:** "总结这份word文件"

**Expected behavior:**
1. Bot detects "word文件" → Identifies file type as Word
2. Bot calls `load_skill("docx")` → Loads docx skill
3. Bot analyzes document
4. Bot returns summary

**Current behavior:**
✅ **Works correctly** - docx skill is in the prompt

### Test Case 3: Too Many Failures

**Input:** (Provide a file that can't be read for any reason)

**Expected behavior (after fix):**
1. Bot tries Read → Fails
2. Bot tries alternative method → Fails
3. Bot tries one more time → Fails
4. Bot says: "抱歉，我暂时无法读取这个文件。可能的原因：文件损坏、格式不支持、或权限问题。"

**Current behavior (before fix):**
1-60. Bot keeps trying different approaches indefinitely

---

## 📝 Implementation Plan

### Phase 1: Immediate Hotfix (30 minutes)

**Files to modify:**
- `bots/personal_assistant.json`

**Changes:**
1. Add PDF to skill list
2. Add file type identification guide
3. Add "max 3 retries" rule
4. Add "PDF must use PDF skill" warning

**Testing:**
- Upload PDF to test room
- Ask "@个人助手 分析这份PDF文件"
- Verify bot loads PDF skill
- Verify bot doesn't use Read tool

### Phase 2: SDK-Level Protection (1 hour)

**Files to modify:**
- `src/campfire_agent.py`

**Changes:**
1. Add max_tool_calls_per_turn to Agent config (if supported)
2. OR implement manual tracking:
   ```python
   tool_calls_this_turn = 0
   while agent.running:
       if tool_calls_this_turn > 15:
           logger.warning("[Agent] Max tool calls reached, stopping")
           break
       # ... process turn ...
       tool_calls_this_turn += len(tool_uses)
   ```

**Testing:**
- Intentionally trigger infinite loop scenario
- Verify agent stops after 15 tool calls
- Verify error message is helpful

### Phase 3: Queue Management (1 hour)

**Files to modify:**
- `src/app_fastapi.py`
- `src/session_manager.py`

**Changes:**
1. Add stuck session detection
2. Add force-close capability
3. Add better error messages

**Testing:**
- Trigger stuck session
- Verify new request can force-close it
- Verify helpful error message

### Phase 4: Comprehensive Testing (1 hour)

**Test all document types:**
- [ ] PDF - with PDF skill
- [ ] Word - with docx skill
- [ ] Excel - with xlsx skill
- [ ] PowerPoint - with pptx skill
- [ ] Unknown format - graceful failure

**Test error scenarios:**
- [ ] Corrupted file
- [ ] File too large
- [ ] Permission denied
- [ ] Tool unavailable

---

## 🎯 Success Criteria

**The fix will be considered successful when:**

1. ✅ PDF files are processed correctly using PDF skill
2. ✅ No more than 5 tool calls for the same operation
3. ✅ Bot gives up gracefully after 3 failures
4. ✅ Subsequent requests are not blocked
5. ✅ Clear error messages when file can't be processed
6. ✅ All 4 document types (PDF, Word, Excel, PPT) work correctly

---

## 📊 Monitoring

**After deployment, monitor:**

```sql
-- Count of Read tool calls per session (should be < 5)
SELECT session_id, COUNT(*) as read_calls
FROM tool_calls
WHERE tool_name = 'Read'
GROUP BY session_id
HAVING COUNT(*) > 5;

-- Average session duration (should be < 30 seconds)
SELECT AVG(duration_seconds)
FROM sessions
WHERE bot_id = 'personal_assistant';

-- Failed sessions (should be < 5%)
SELECT
    COUNT(CASE WHEN status = 'failed' THEN 1 END) * 100.0 / COUNT(*) as failure_rate
FROM sessions
WHERE bot_id = 'personal_assistant';
```

---

## 🔄 Related Issues

This fix addresses:
1. ✅ PDF infinite loop (primary issue)
2. ✅ General infinite loop protection (systemic)
3. ✅ Queue blocking from stuck sessions
4. ✅ Poor error messages

This does NOT address:
- ❌ Large file handling (>10MB) - separate issue
- ❌ OCR for scanned PDFs - requires additional capability
- ❌ Multi-page PDF summarization - may need chunking strategy

---

## 💡 Prevention

**To prevent similar issues in future:**

1. **Always add retry limits** to system prompts
2. **Document tool limitations** clearly
3. **Add SDK-level protections** for all bots
4. **Test with edge cases** (binary files, large files, corrupted files)
5. **Monitor tool call patterns** in production

---

**Document Version:** 1.0
**Created:** 2025-10-21
**Priority:** HIGH - Should be fixed before next deployment
**Estimated Fix Time:** 3 hours (all 4 phases)
**Risk if not fixed:** Bot becomes unusable when PDF requests increase
