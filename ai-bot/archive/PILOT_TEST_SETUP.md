# v0.5.0 Pilot Validation - Test Workflow Instructions

**Testing Method:** Campfire UI (not curl)
**Bot:** 个人助手 (Personal Assistant)
**Environment:** Local Docker
**Duration:** 2-3 hours for all 5 workflows

---

## Prerequisites

✅ Local Docker environment running (see PILOT_LOCAL_DOCKER_SETUP.md)
✅ Campfire accessible at http://localhost:3000
✅ Test account created
✅ Test room created ("v0.5.0 Pilot Validation")
✅ PILOT_VALIDATION_LOG.md open for documenting results

---

## Monitoring Commands (Keep These Running)

**Open 2-3 terminal windows for monitoring:**

### Terminal 1: AI Bot Logs (Real-time)
```bash
# Navigate to project root
cd /Users/heng/Development/campfire

# Follow AI bot logs with verification filtering
docker logs -f campfire-ai-bot-dev 2>&1 | grep -E "(verification|error|warning|Gate|tool:|response_time)"
```

**What to watch for:**
- `✅ Verification module loaded` - Confirms verification active
- `Gate 1: Error caught` - Verification catching errors
- `Gate 2: Code generation used` - Template being used
- `tool: save_html_presentation` - File tools being called
- `response_time: X.Xs` - Performance metrics
- `⚠️ Warning:` - Validation warnings
- `❌ Error:` - Issues to investigate

### Terminal 2: All Logs (Unfiltered)
```bash
# View all logs from both containers
docker-compose -f docker-compose.dev.yml logs -f
```

**Or separate by service:**
```bash
# AI Bot only
docker logs -f campfire-ai-bot-dev

# Campfire only
docker logs -f campfire-dev

# Both interleaved with timestamps
docker-compose -f docker-compose.dev.yml logs -f --timestamps
```

### Terminal 3: Container Status (Optional)
```bash
# Watch container health status
watch -n 5 'docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"'
```

**Or manual checks:**
```bash
# Check container status
docker ps

# Check resource usage
docker stats --no-stream campfire-ai-bot-dev campfire-dev

# Check disk usage
docker system df
```

---

## Log Filtering Commands (Use During Testing)

### Verification Activity
```bash
# See all verification checks
docker logs campfire-ai-bot-dev 2>&1 | grep -i "verification"

# See errors caught (Gate 1)
docker logs campfire-ai-bot-dev 2>&1 | grep -i "error caught\|validation failed"

# See warnings (lenient mode)
docker logs campfire-ai-bot-dev 2>&1 | grep -i "warning"
```

### Code Generation Activity
```bash
# See code generation uses (Gate 2)
docker logs campfire-ai-bot-dev 2>&1 | grep -i "code generation\|template\|linting"

# See ruff linting results
docker logs campfire-ai-bot-dev 2>&1 | grep -i "ruff"

# See save_html_presentation calls
docker logs campfire-ai-bot-dev 2>&1 | grep -i "save_html_presentation"
```

### Performance Metrics (Gate 5)
```bash
# See response times
docker logs campfire-ai-bot-dev 2>&1 | grep -i "response_time\|elapsed\|duration"

# See tool execution times
docker logs campfire-ai-bot-dev 2>&1 | grep -i "tool execution"
```

### Errors and Issues
```bash
# Show errors only
docker logs campfire-ai-bot-dev 2>&1 | grep -i "error" | tail -20

# Show last 50 lines (recent activity)
docker logs --tail 50 campfire-ai-bot-dev

# Show logs since specific time
docker logs --since 10m campfire-ai-bot-dev

# Show logs between timestamps
docker logs --since "2025-10-31T10:00:00" --until "2025-10-31T11:00:00" campfire-ai-bot-dev
```

---

## Quick Troubleshooting Commands

### Container Issues
```bash
# Restart AI bot container
docker-compose -f /Users/heng/Development/campfire/docker-compose.dev.yml restart ai-bot

# Restart both containers
docker-compose -f /Users/heng/Development/campfire/docker-compose.dev.yml restart

# Check container health
curl http://localhost:8000/health
curl http://localhost:3000/up
```

### Check Bot Configuration
```bash
# Verify verification enabled
docker exec campfire-ai-bot-dev cat /app/bots/personal_assistant.json | grep -A 5 '"verification"'

# Check environment variables
docker exec campfire-ai-bot-dev env | grep -E "ANTHROPIC|CAMPFIRE|FILE_TEMP"

# List bot files
docker exec campfire-ai-bot-dev ls -la /app/bots/
```

### Check File Registry (For HTML Downloads)
```bash
# Check file registry stats
curl http://localhost:8000/files/stats

# Check temp directory
docker exec campfire-ai-bot-dev ls -la /tmp/ | grep html
```

---

## Live Monitoring Dashboard (Single Terminal)

**Use this command for a comprehensive live view:**

```bash
# Navigate to project root
cd /Users/heng/Development/campfire

# Watch logs with color highlighting and filtering
docker logs -f campfire-ai-bot-dev 2>&1 | \
  grep --line-buffered -E "(verification|Gate|tool:|error|warning|response_time)" | \
  sed 's/verification/\x1b[32mverification\x1b[0m/g' | \
  sed 's/Gate/\x1b[33mGate\x1b[0m/g' | \
  sed 's/error/\x1b[31merror\x1b[0m/g'
```

**What this does:**
- Follows AI bot logs in real-time (`-f`)
- Filters for important events (verification, gates, tools, errors)
- Color highlights:
  - Green: verification
  - Yellow: Gate metrics
  - Red: errors

---

## Workflow Testing Template

For each workflow below, follow this process:

### Before Testing
1. Open PILOT_VALIDATION_LOG.md
2. Note current time
3. Prepare screenshot tool (Cmd+Shift+4 on Mac)

### During Testing
1. Type message in Campfire
2. @mention the bot: `@个人助手 [your query]`
3. Press Enter
4. Observe response
5. Time the response
6. Take screenshots

### After Testing
1. Document in PILOT_VALIDATION_LOG.md:
   - Expected behavior
   - Actual behavior
   - Response time
   - Verification checks performed
   - Gate metrics updated
   - Screenshots saved
2. Update PILOT_VALIDATION_METRICS.md with gate counts

---

## Workflow 1: Financial Calculation with Verification

**Objective:** Test verification module catches math errors and validates calculations

### Test 1.1: Valid Calculation
**Message:**
```
@个人助手 计算利润率：营业额 ¥120,000，成本 ¥85,000，请计算利润率并验证计算结果
```

**Expected:**
- Bot calculates profit margin: (120000 - 85000) / 120000 = 29.17%
- Verification module validates inputs (positive numbers)
- Verification module validates calculation
- Response includes verification confirmation
- Response time: ~2-3 seconds

**What to Document:**
- [ ] Profit margin calculated correctly?
- [ ] Verification messages visible in response?
- [ ] Response time recorded
- [ ] Screenshot saved
- [ ] Gate 1: +0 or +1 (if any warnings)
- [ ] Gate 5: Performance baseline established

### Test 1.2: Invalid Input (Negative Cost)
**Message:**
```
@个人助手 计算利润率：营业额 ¥100,000，成本 ¥-50,000
```

**Expected:**
- Verification module **catches negative cost**
- Bot responds with error or warning
- Calculation may proceed with warning (lenient mode)
- Gate 1 metric +1 (error caught!)

**What to Document:**
- [ ] Error caught by verification?
- [ ] Warning message shown?
- [ ] Gate 1: +1 error caught ✅

### Test 1.3: Division by Zero
**Message:**
```
@个人助手 计算 100 除以 0
```

**Expected:**
- Verification module catches division by zero
- Bot responds with appropriate error message
- Gate 1 metric +1 (error caught!)

**What to Document:**
- [ ] Error caught?
- [ ] Gate 1: +1 error caught ✅

---

## Workflow 2: HTML Report Generation

**Objective:** Test save_html_presentation tool + HTML verification

### Test 2.1: Create HTML Presentation
**Message:**
```
@个人助手 创建一个HTML演示文稿，主题是《v0.5.0新功能介绍》，包含3个部分：
1. 验证模块 - 三层验证架构
2. 代码生成 - 模板化代码生成系统
3. 测试基础设施 - 3个关键路径测试

请使用专业的样式，包含CSS动画和渐变效果。
```

**Expected:**
- Bot generates HTML content
- Bot calls `save_html_presentation` tool
- Tool returns purple gradient download button HTML
- Bot includes download button in response (verbatim from tool)
- HTML verification performed (quality score calculated)
- File saved with UUID token
- Gate 2 metric +1 (code generation used!)

**What to Document:**
- [ ] HTML generated?
- [ ] save_html_presentation tool called?
- [ ] Download button visible in response?
- [ ] Click download button - file downloads?
- [ ] Open HTML file - renders correctly?
- [ ] HTML verification performed? (check logs)
- [ ] Quality score shown?
- [ ] Screenshot of download button
- [ ] Screenshot of opened HTML file
- [ ] Gate 1: +0 or +1 (HTML validation)
- [ ] Gate 2: +1 code generation used ✅

### Test 2.2: Download and Verify HTML
**Action:**
1. Click download button from previous response
2. Save file
3. Open in browser
4. Inspect HTML quality

**What to Check:**
- [ ] File downloads successfully?
- [ ] File name correct? (e.g., v0_5_0新功能介绍.html)
- [ ] HTML renders in browser?
- [ ] CSS styles applied?
- [ ] Content accurate (3 sections)?
- [ ] Professional appearance?
- [ ] Responsive design?

---

## Workflow 3: Data Query with Validation

**Objective:** Test search_conversations with input validation

### Test 3.1: Conversation Search
**Message:**
```
@个人助手 搜索我最近10条对话记录，找出关于"menu engineering"或"菜单工程"的讨论，并总结关键要点
```

**Expected:**
- Input validation: query parameters validated
- search_conversations tool called
- Results returned and summarized
- Response time: ~2-4 seconds

**What to Document:**
- [ ] Search executed?
- [ ] Results found?
- [ ] Summary accurate?
- [ ] Input validation performed? (check logs)
- [ ] Response time
- [ ] Gate 1: +0 or +1 (validation performed)

### Test 3.2: Invalid Query (Empty Search)
**Message:**
```
@个人助手 搜索我的对话记录，关键词是""（空）
```

**Expected:**
- Verification catches empty search term
- Bot responds with appropriate message
- Gate 1 metric +1 (error caught!)

**What to Document:**
- [ ] Empty query caught?
- [ ] Gate 1: +1 error caught ✅

---

## Workflow 4: Code Generation

**Objective:** Test code generation templates + ruff linting

### Test 4.1: Generate Python Script
**Message:**
```
@个人助手 生成一个Python脚本来计算ROI（投资回报率）。

要求：
- 函数名：calculate_roi
- 输入：cost (成本), revenue (收益)
- 输出：ROI百分比
- 处理除零错误
- 包含docstring
- 通过ruff linting检查
```

**Expected:**
- Bot uses code generation template (Financial or Operations)
- Python code generated
- Code linted with ruff
- Validation report shows "passed" or warnings
- Gate 2 metric +1 (code generation used!)

**What to Document:**
- [ ] Code generated?
- [ ] Template used? (check logs for "template")
- [ ] Ruff linting performed?
- [ ] Code valid Python syntax?
- [ ] Handles division by zero?
- [ ] Includes docstring?
- [ ] Copy code and test locally?
- [ ] Screenshot of generated code
- [ ] Gate 2: +1 code generation used ✅

### Test 4.2: Generate SQL Query
**Message:**
```
@个人助手 生成一个SQL查询，用于查找销售额最高的前10个菜品，包含菜品名称和总销售额
```

**Expected:**
- SQL code generation used
- Query validated (no dangerous operations like DELETE/UPDATE)
- Safe query returned
- Gate 2 metric +1 (code generation used!)

**What to Document:**
- [ ] SQL generated?
- [ ] Query safe (SELECT only)?
- [ ] Validation performed?
- [ ] Gate 2: +1 code generation used ✅

---

## Workflow 5: Multi-Step Task + HTML Checklist

**Objective:** Test workflow coordination and multiple tool calls

### Test 5.1: Create Task + Generate Checklist
**Message:**
```
@个人助手 请完成两个任务：

1. 创建一个任务提醒：明天下午3点提醒我完成v0.5.0验证报告
2. 为这个验证工作生成一个HTML checklist，包含5个验证门控的检查项：
   - Gate 1: 验证模块捕获错误 (≥3个)
   - Gate 2: 代码生成成功使用 (≥5次)
   - Gate 3: 回归测试检测 (≥1个)
   - Gate 4: CI/CD稳定性 (≥95%)
   - Gate 5: 性能开销 (≤10%)

请创建一个可以打勾的HTML checklist，带有进度百分比显示。
```

**Expected:**
- Bot executes TWO steps:
  1. manage_personal_tasks tool (create task)
  2. save_html_presentation tool (generate checklist)
- Both tools succeed
- Download button provided for HTML checklist
- Response time: ~5-8 seconds
- Gate 2 metric +1 (HTML generation used!)

**What to Document:**
- [ ] Task created successfully?
- [ ] HTML checklist generated?
- [ ] Download button visible?
- [ ] Download and open HTML checklist
- [ ] Checklist has all 5 gates?
- [ ] Interactive (can check boxes)?
- [ ] Progress percentage shown?
- [ ] Screenshot of checklist
- [ ] Gate 1: +0 or +1 (multi-step validation)
- [ ] Gate 2: +1 code generation used ✅
- [ ] Gate 5: Multi-step performance

---

## Performance Tracking

After each workflow, record response time in table:

| Workflow | Baseline | With v0.5.0 | Overhead | Gate 5 |
|----------|----------|-------------|----------|--------|
| Financial | TBD | TBD | TBD% | ⏳ |
| HTML Report | TBD | TBD | TBD% | ⏳ |
| Data Query | TBD | TBD | TBD% | ⏳ |
| Code Generation | TBD | TBD | TBD% | ⏳ |
| Multi-Step | TBD | TBD | TBD% | ⏳ |

**Target:** Average overhead ≤10%

---

## Gate Metrics Checklist

Track throughout testing:

### Gate 1: Verification Catches Errors
- [ ] Error 1: _______________ (workflow, error type)
- [ ] Error 2: _______________
- [ ] Error 3: _______________
- **Total:** _ / 3 needed ✅

### Gate 2: Code Generation Used
- [ ] Use 1: _______________ (workflow, template)
- [ ] Use 2: _______________
- [ ] Use 3: _______________
- [ ] Use 4: _______________
- [ ] Use 5: _______________
- **Total:** _ / 5 needed ✅

### Gate 5: Performance
- Average overhead: ___%
- **Target:** ≤10% ✅

---

## Screenshots Checklist

Save screenshots for final report:

- [ ] Financial calculation response
- [ ] Division by zero error caught
- [ ] HTML download button
- [ ] Opened HTML presentation
- [ ] Generated Python code
- [ ] Generated SQL query
- [ ] HTML checklist downloaded
- [ ] Task created confirmation
- [ ] Verification warning examples (≥2)
- [ ] Campfire UI showing bot response

**Screenshot naming:** `pilot_workflow_X_description.png`

---

## Troubleshooting

### Bot not responding?
```bash
# Check bot is running
curl http://localhost:8000/health

# Check logs
docker logs -f campfire-ai-bot-dev

# Check webhook URL
docker logs campfire-dev | grep webhook
```

### Verification not working?
```bash
# Check bot config
docker exec campfire-ai-bot-dev cat /app/bots/personal_assistant.json | grep verification

# Check logs for verification messages
docker logs campfire-ai-bot-dev | grep -i verification
```

### Download button not working?
```bash
# Check file registry
curl http://localhost:8000/files/stats

# Check FILE_TEMP_DIR
docker exec campfire-ai-bot-dev env | grep FILE_TEMP
```

---

## Completion Checklist

After all 5 workflows:

- [ ] All workflows tested
- [ ] PILOT_VALIDATION_LOG.md filled out
- [ ] PILOT_VALIDATION_METRICS.md updated
- [ ] Screenshots saved
- [ ] Performance data collected
- [ ] Gate metrics tracked
- [ ] Issues documented
- [ ] Ready for Day 4 validation

**Next Steps:** Proceed to Day 4 - Gate Validation (see PILOT_VALIDATION_LOG.md)

---

**Testing started:** ___________
**Testing completed:** ___________
**Total time:** ___________ hours
**Workflows completed:** _ / 5
**Gate 1 progress:** _ / 3
**Gate 2 progress:** _ / 5
