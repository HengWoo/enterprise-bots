---
name: personal-productivity
description: "Personal task management, reminders, notes, and user preference tracking. Comprehensive workflows for organizing work, setting reminders, saving private notes, and remembering user habits. Use when helping users manage their day-to-day productivity."
version: 1.0.0
license: MIT
---

# Personal Productivity Skill

## Overview

This skill provides workflows for managing personal tasks, reminders, notes, and user preferences. All data is private to each user and stored securely in Campfire's database.

## When to Use This Skill

Load this skill when users request:
- "添加任务" / "Add task"
- "查看待办事项" / "Show my tasks"
- "设置提醒" / "Set a reminder"
- "保存笔记" / "Save a note"
- "搜索我的笔记" / "Search my notes"
- "记住我的偏好" / "Remember my preferences"
- Any personal productivity management request

## Tools Available

| Tool | Purpose | When to Use |
|------|---------|-------------|
| `manage_personal_tasks` | Create, list, update, complete, delete tasks | Task management |
| `set_reminder` | Set time-based or event-based reminders | Reminders |
| `save_personal_note` | Save private notes | Note-taking |
| `search_personal_notes` | Search notes by keywords | Note retrieval |
| `save_user_preference` | Remember user habits and preferences | Personalization |
| `get_user_context` | Retrieve user profile and preferences | Context understanding |

---

## Task Management Workflows

### Workflow 1: Creating Tasks

**When to use:** User asks to add task, create todo, or remember to do something.

**Steps:**

1. **Parse user request:**
   - Extract: task title, priority, due date (if mentioned)
   - Default priority: "medium"
   - Default due date: None (no deadline)

2. **Call manage_personal_tasks:**
   ```python
   manage_personal_tasks(
       action="create",
       title="Complete project proposal",
       description="Draft Q4 proposal with budget estimates",
       priority="high",
       due_date="2025-11-15"  # YYYY-MM-DD format
   )
   ```

3. **Confirm to user:**
   - Acknowledge task created
   - State priority and due date
   - Offer to set reminder if due date exists

**Priority Levels:**
- `high`: Urgent/important tasks
- `medium`: Normal tasks (default)
- `low`: Nice-to-have tasks

**Example Conversation:**
```
User: "Add a task to review the contract by Friday"

Bot:
✅ Task created: "Review the contract"
📅 Due: 2025-11-01 (Friday)
🔔 Priority: medium

Would you like me to set a reminder for this?
```

### Workflow 2: Listing Tasks

**When to use:** User asks to see tasks, check todos, or review what's pending.

**Steps:**

1. **Determine filter:**
   - All tasks: `status="all"`
   - Pending only: `status="pending"` (default)
   - Completed: `status="completed"`
   - By priority: `priority="high"`

2. **Call manage_personal_tasks:**
   ```python
   manage_personal_tasks(
       action="list",
       status="pending"
   )
   ```

3. **Format results:**
   - Group by priority (high → medium → low)
   - Show due dates prominently
   - Highlight overdue tasks
   - Use visual separators

**Example Output:**
```html
<div style="padding: 10px;">
  <h2>📋 Your Tasks (3 pending)</h2>

  <h3 style="color: #d32f2f;">⚠️ High Priority</h3>
  <ul style="line-height: 2.0;">
    <li><strong>Review contract</strong> - Due: 2025-11-01 (Tomorrow)</li>
  </ul>

  <h3>📌 Medium Priority</h3>
  <ul style="line-height: 2.0;">
    <li><strong>Prepare slides</strong> - Due: 2025-11-05</li>
    <li><strong>Email client</strong> - No deadline</li>
  </ul>
</div>
```

### Workflow 3: Completing Tasks

**When to use:** User says task is done, finished, or completed.

**Steps:**

1. **Identify task:**
   - By ID: If user provides task ID
   - By title: Search for matching title

2. **Call manage_personal_tasks:**
   ```python
   manage_personal_tasks(
       action="complete",
       task_id=123
   )
   ```

3. **Celebrate completion:**
   - Use encouraging language
   - Show updated task count
   - Suggest next task if available

**Example:**
```
User: "Mark 'Review contract' as done"

Bot:
✅ Great job! Task completed: "Review contract"

You have 2 remaining tasks:
1. Prepare slides (Due: Nov 5)
2. Email client (No deadline)
```

### Workflow 4: Updating Tasks

**When to use:** User wants to change task details (priority, due date, description).

**Steps:**

1. **Identify what to update:**
   - Priority change: `priority="high"`
   - Due date change: `due_date="2025-11-10"`
   - Description update: `description="Updated details"`

2. **Call manage_personal_tasks:**
   ```python
   manage_personal_tasks(
       action="update",
       task_id=123,
       priority="high",
       due_date="2025-11-10"
   )
   ```

3. **Confirm changes:**
   Show old values → new values

### Workflow 5: Deleting Tasks

**When to use:** User wants to remove task (not complete, but delete).

**Steps:**

1. **Confirm deletion:**
   Ask user if they're sure (tasks can't be recovered)

2. **Call manage_personal_tasks:**
   ```python
   manage_personal_tasks(
       action="delete",
       task_id=123
   )
   ```

3. **Acknowledge deletion**

---

## Reminder Workflows

### Workflow 6: Setting Time-Based Reminders

**When to use:** User wants to be reminded at specific time.

**Steps:**

1. **Parse reminder details:**
   - Extract: description, date/time, repeat pattern (if mentioned)

2. **Call set_reminder:**
   ```python
   set_reminder(
       description="Call client about proposal",
       remind_at="2025-11-01T14:00:00",  # ISO 8601 format
       repeat="none"  # Options: none, daily, weekly, monthly
   )
   ```

3. **Confirm reminder:**
   - State what will be reminded
   - State when reminder will trigger
   - Explain repeat pattern (if applicable)

**Time Parsing:**
- "Tomorrow at 2pm" → Next day at 14:00
- "Friday morning" → Next Friday at 09:00
- "In 3 hours" → Current time + 3 hours
- "Every Monday" → Weekly repeat

**Example:**
```
User: "Remind me to call the client tomorrow at 2pm"

Bot:
🔔 Reminder set!
📌 What: Call the client
⏰ When: 2025-11-01 at 14:00
🔄 Repeat: None (one-time)

I'll notify you tomorrow afternoon!
```

### Workflow 7: Setting Event-Based Reminders

**When to use:** User wants reminder when something happens (not time-based).

**Note:** Current implementation focuses on time-based reminders. For event-based (e.g., "remind me when John replies"), recommend using task with high priority instead.

**Alternative:**
```python
manage_personal_tasks(
    action="create",
    title="Follow up when John replies",
    priority="high",
    description="Check for John's response"
)
```

---

## Note-Taking Workflows

### Workflow 8: Saving Notes

**When to use:** User wants to save information for later.

**Steps:**

1. **Determine note type:**
   - Quick note: Short text
   - Detailed note: Longer content with context
   - Code snippet: Include code blocks
   - Link/reference: Save URLs

2. **Extract note details:**
   - Title (generate if not provided)
   - Content
   - Tags (optional)
   - Category (optional)

3. **Call save_personal_note:**
   ```python
   save_personal_note(
       title="Meeting notes - Q4 Planning",
       content="Discussed: Budget increase, hiring 2 devs, new features...",
       tags=["meeting", "planning", "q4"]
   )
   ```

4. **Confirm save:**
   - Acknowledge note saved
   - Mention how to retrieve it later

**Best Practices:**
- Add descriptive titles
- Use tags for easy searching
- Include date/context in content

**Example:**
```
User: "Save this for later: The API key is abc123xyz"

Bot:
💾 Note saved!
📝 Title: API Key Reference
🏷️ Tags: api, credentials
📅 Saved: 2025-11-01

You can find it later by searching for "API key"
```

### Workflow 9: Searching Notes

**When to use:** User wants to find saved notes.

**Steps:**

1. **Parse search query:**
   - Keywords: Main terms to search
   - Tags: Filter by tags
   - Date range: Filter by date (if mentioned)

2. **Call search_personal_notes:**
   ```python
   search_personal_notes(
       query="API key",
       tags=["credentials"],
       limit=10
   )
   ```

3. **Format results:**
   - Show most recent first
   - Highlight matching keywords
   - Include snippets
   - Provide full content if only 1 result

**Search Tips:**
- Search by keywords in title or content
- Filter by tags for specific categories
- Combine multiple keywords for narrower results

**Example:**
```
User: "Find my notes about API keys"

Bot:
🔍 Found 2 notes matching "API key":

1. **API Key Reference** (Nov 1, 2025)
   Tags: api, credentials
   Content: The API key is abc123xyz...

2. **Production API Setup** (Oct 28, 2025)
   Tags: api, deployment
   Content: Production API keys stored in...
```

---

## User Preference Management

### Workflow 10: Saving User Preferences

**When to use:** User expresses preferences, habits, or wants you to remember something.

**Common Preferences to Track:**
- Communication style: Formal vs casual
- Language preference: Chinese, English, or mixed
- Time zone and working hours
- Notification preferences
- Work habits and patterns
- Project contexts

**Steps:**

1. **Identify preference type:**
   - Explicit: User directly states preference
   - Implicit: Inferred from behavior (ask for confirmation)

2. **Call save_user_preference:**
   ```python
   save_user_preference(
       key="communication_style",
       value="casual_chinese",
       category="interaction"
   )
   ```

3. **Confirm saved:**
   Acknowledge that you'll remember the preference

**Preference Categories:**
- `interaction`: Communication style, language
- `work`: Work hours, productivity patterns
- `notification`: Reminder preferences
- `projects`: Current projects, contexts
- `tools`: Favorite tools, workflows

**Example:**
```
User: "I prefer casual tone in Chinese, and I usually work 9am-6pm"

Bot:
✅ Got it! I'll remember:
1. Communication: Casual tone in Chinese
2. Work hours: 9am-6pm

I'll tailor my responses and timing accordingly.
```

### Workflow 11: Retrieving User Context

**When to use:** Need to personalize responses based on user preferences.

**Steps:**

1. **Call get_user_context:**
   ```python
   get_user_context()
   ```

2. **Use context to personalize:**
   - Adjust language and tone
   - Respect work hours for reminders
   - Reference past conversations
   - Consider ongoing projects

**Example Internal Usage:**
```python
# Before responding, check user context
context = get_user_context()

if context.communication_style == "casual_chinese":
    # Use informal Chinese
    response = "好的！我来帮你..."
else:
    # Use formal tone
    response = "我将为您..."

if context.work_hours:
    # Don't set reminders outside work hours
    # (unless explicitly requested)
```

---

## Best Practices

### Task Management
- ✅ Always confirm task creation
- ✅ Use clear priorities (high/medium/low)
- ✅ Highlight overdue tasks
- ✅ Suggest reminders for due dates
- ✅ Group tasks by priority when listing

### Reminders
- ✅ Parse natural language times ("tomorrow at 2pm")
- ✅ Clarify ambiguous times ("morning" → 9am)
- ✅ Confirm repeat patterns clearly
- ✅ Set reasonable defaults (9am for "morning", 2pm for "afternoon")

### Notes
- ✅ Generate descriptive titles if user doesn't provide
- ✅ Encourage tags for organization
- ✅ Include context (date, project) in content
- ✅ Highlight search results clearly

### Preferences
- ✅ Ask for confirmation when inferring preferences
- ✅ Respect stated preferences consistently
- ✅ Update preferences when user's habits change
- ✅ Don't assume preferences transfer across contexts

---

## Common Mistakes to Avoid

### ❌ Mistake 1: Not Confirming Task Creation
```
User: "Add task to review contract"
Bot: "Ok" ← TOO BRIEF
```

**✅ Correct:**
```
Bot: "✅ Task added: Review contract
📅 Priority: medium
Would you like to set a due date?"
```

### ❌ Mistake 2: Ignoring Priority
```
User: "This is urgent - call client ASAP"
Bot creates task with priority="medium"  ← WRONG
```

**✅ Correct:** Detect urgency keywords ("urgent", "ASAP", "critical") → `priority="high"`

### ❌ Mistake 3: Ambiguous Reminders
```
User: "Remind me to call tomorrow"
Bot sets reminder for 00:00 tomorrow  ← NOT HELPFUL
```

**✅ Correct:** Set reasonable default (9am) or ask: "What time tomorrow?"

### ❌ Mistake 4: Not Organizing Search Results
```
Bot returns 20 notes in random order  ← OVERWHELMING
```

**✅ Correct:** Show most recent first, limit to 5-10, offer to show more

---

## Example: Complete Day Management

**User Scenario:** "Help me organize my day"

**Bot Response:**

1. **Check existing tasks:**
   ```python
   tasks = manage_personal_tasks(action="list", status="pending")
   ```

2. **Show organized view:**
   ```html
   <div style="padding: 10px;">
     <h2>📅 Your Day Overview</h2>

     <h3>⚠️ Urgent (Due Today)</h3>
     <ul>
       <li><strong>Review contract</strong> - 2pm deadline</li>
       <li><strong>Submit proposal</strong> - End of day</li>
     </ul>

     <h3>📌 This Week</h3>
     <ul>
       <li><strong>Prepare presentation</strong> - Due Friday</li>
       <li><strong>Team meeting prep</strong> - Due Thursday</li>
     </ul>

     <h3>💡 Suggestions</h3>
     <ul>
       <li>Set reminder for contract review at 1:30pm</li>
       <li>Block 2 hours tomorrow for presentation prep</li>
     </ul>
   </div>
   ```

3. **Offer proactive help:**
   - Set recommended reminders
   - Create placeholder tasks for suggestions
   - Ask about priorities

---

## Integration with Other Skills

**Combine with presentation-generation:**
```
User: "Create presentation and add task to review it"

1. load_skill("presentation-generation")
2. Generate presentation
3. manage_personal_tasks(
     action="create",
     title="Review generated presentation",
     priority="medium",
     due_date=tomorrow
   )
```

**Combine with document-skills:**
```
User: "Analyze this contract and save key points as note"

1. load_skill("docx")
2. Extract contract text
3. Analyze key clauses
4. save_personal_note(
     title="Contract Key Points - Acme Corp",
     content="<summary>",
     tags=["contract", "legal", "acme"]
   )
```

---

## Summary

**Key Takeaways:**
1. ✅ Use manage_personal_tasks for all task management
2. ✅ Set reminders with clear times and descriptions
3. ✅ Save notes with descriptive titles and tags
4. ✅ Remember user preferences for personalization
5. ✅ Always confirm actions and provide clear feedback
6. ✅ Group tasks by priority, show most important first
7. ✅ Use HTML formatting for clear, organized displays

**Most Common Workflow:** Creating tasks (70% of requests)

**Success Metric:** User feels organized and in control of their work

---

## Privacy Note

**All data is private to each user:**
- Tasks visible only to task owner
- Notes accessible only by creator
- Preferences stored per-user
- Reminders trigger only for relevant user
- No cross-user data sharing

**Best Practice:** Remind users that DM (Direct Message) rooms provide maximum privacy.
