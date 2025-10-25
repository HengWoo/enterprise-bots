---
name: Campfire Daily Briefing
description: Generates and searches daily briefings from Campfire conversations. Collects messages, files, and key decisions from specified date or date range. Creates comprehensive summaries with highlights, action items, and important topics. Searches historical briefings by keywords or date range. Use when users ask for daily summaries, "what happened yesterday", "generate briefing for last week", or want to review past briefings.
---

# Campfire Daily Briefing

## Quick Start

When users request briefings or summaries:

1. **Generate briefing** - Use `generate_daily_briefing` to create new summary
2. **Search history** - Use `search_briefings` to find past briefings
3. **Customize output** - Configure briefing length and content
4. **Store as knowledge** - Briefings automatically saved to knowledge base

## Core Capabilities

### Daily Briefing Generation

**What gets included:**
- All conversations from specified date
- Uploaded files and attachments
- Key decisions and action items
- Active participants and rooms
- Important topics and highlights

**Briefing structure:**
```
📅 Daily Briefing - [Date]

## Summary
High-level overview of the day's activities

## Highlights
- Key points and decisions
- Important announcements
- Major discussions

## Conversations
Organized by room with participant lists

## Files & Attachments
List of all shared files

## Action Items
Extracted commitments and tasks

## Active Topics
Main themes discussed

## Participants
Who was active and where
```

### Historical Search

**Search capabilities:**
- Find briefings by keywords
- Filter by date range (start_date to end_date)
- Limit number of results
- Search across all stored briefings

**Use cases:**
- "What happened last week?"
- "Find briefings mentioning budget"
- "Show me September briefings"
- "When did we discuss the product launch?"

### Available Tools (2 Briefing Tools)

**1. generate_daily_briefing**
- Generate briefing for specific date (default: yesterday)
- Optional room filter (specific rooms only)
- Include/exclude file attachments
- Summary length: "concise" (default), "detailed", or "comprehensive"
- Auto-saves to knowledge base at `/briefings/YYYY/MM/daily-briefing-YYYY-MM-DD.md`

**2. search_briefings**
- Search by keywords (optional)
- Filter by date range (start_date, end_date)
- Configurable result limit (default: 5)
- Returns briefing excerpts with dates and paths

## Usage Workflows

### Workflow 1: Generate Today's Briefing

```
User: "生成今天的日报" (Generate today's briefing)

Step 1: Generate briefing for today
→ generate_daily_briefing(date="2025-10-18")

Step 2: Present summary
→ "📅 今日工作简报 - 2025年10月18日

   ## 核心总结
   [AI-generated high-level summary]

   ## 重要亮点
   - [Highlight 1]
   - [Highlight 2]
   - [Highlight 3]

   ## 讨论详情
   [Organized by room]

   完整日报已保存至: briefings/2025/10/daily-briefing-2025-10-18.md"
```

### Workflow 2: Review Yesterday's Activity

```
User: "What happened yesterday?"

Step 1: Generate briefing for yesterday
→ generate_daily_briefing()  # Defaults to yesterday

Step 2: Format and present
→ "📅 Yesterday's Briefing (October 17, 2025)

   **Summary:**
   [Overview of key activities]

   **Highlights:**
   - Q4 budget approved (¥500,000)
   - New hiring policy announced
   - Server migration scheduled

   **Conversations (15 messages across 3 rooms):**

   💼 Finance Team (8 messages):
   - Budget discussion with [names]
   - [Key points]

   👥 HR Team (5 messages):
   - Hiring policy update
   - [Details]

   🔧 Tech Team (2 messages):
   - Migration planning
   - [Notes]

   **Files Shared (3):**
   - Q4_budget_final.xlsx
   - hiring_policy_2025.pdf
   - server_migration_plan.md

   Full briefing: briefings/2025/10/daily-briefing-2025-10-17.md"
```

### Workflow 3: Search Historical Briefings

```
User: "Find briefings mentioning the product launch"

Step 1: Search briefings with keyword
→ search_briefings(query="product launch", max_results=10)

Step 2: Present results
→ "Found 5 briefings mentioning 'product launch':

   📅 2025-10-15 - Daily Briefing
   Excerpt: '...announced product launch timeline for Q1 2026...'
   Path: briefings/2025/10/daily-briefing-2025-10-15.md

   📅 2025-10-08 - Daily Briefing
   Excerpt: '...product launch team formed with 5 members...'
   Path: briefings/2025/10/daily-briefing-2025-10-08.md

   📅 2025-09-25 - Daily Briefing
   Excerpt: '...initial product launch proposal discussed...'
   Path: briefings/2025/09/daily-briefing-2025-09-25.md

   Would you like me to show any of these in detail?"
```

### Workflow 4: Weekly Summary

```
User: "Summarize last week's activity"

Step 1: Search briefings for date range
→ search_briefings(
     start_date="2025-10-11",
     end_date="2025-10-17",
     max_results=7
   )

Step 2: Analyze and synthesize
→ "📅 Weekly Summary (October 11-17, 2025)

   **Overview:**
   Active week with 127 messages across 5 rooms.

   **Key Themes:**
   1. Q4 Budget Planning (mentioned 23 times)
   2. New Hiring Policy (mentioned 15 times)
   3. Server Migration (mentioned 12 times)

   **Major Decisions:**
   - Q4 budget approved at ¥500,000
   - 3 new positions opened
   - Migration scheduled for November

   **Most Active Days:**
   - Tuesday (Oct 15): 34 messages
   - Wednesday (Oct 16): 28 messages

   **Daily Briefings:**
   - briefings/2025/10/daily-briefing-2025-10-11.md
   - briefings/2025/10/daily-briefing-2025-10-12.md
   - [...]
   - briefings/2025/10/daily-briefing-2025-10-17.md"
```

### Workflow 5: Specific Room Briefing

```
User: "Generate briefing for Finance Team room only"

Step 1: Get room ID (Finance Team = room #5)

Step 2: Generate filtered briefing
→ generate_daily_briefing(
     date="2025-10-18",
     room_ids=[5],
     summary_length="detailed"
   )

Step 3: Present focused summary
→ "📊 Finance Team Briefing - October 18, 2025

   **Activity Summary:**
   12 messages, 2 files shared, 4 participants

   **Participants:**
   - WU HENG
   - [Finance Manager]
   - [Accountant 1]
   - [Accountant 2]

   **Discussion Topics:**
   1. Monthly Financial Report Review
      [Details]

   2. Q4 Budget Allocation
      [Details]

   3. Expense Tracking Updates
      [Details]

   **Files Shared:**
   - october_financial_report.xlsx
   - Q4_budget_breakdown.pdf

   **Action Items:**
   - [ ] Submit revised budget by Friday (WU HENG)
   - [ ] Review expense categories (Manager)

   Saved to: briefings/2025/10/daily-briefing-finance-2025-10-18.md"
```

## Briefing Customization

### Summary Length Options

**1. Concise (default)**
- Quick overview in 2-3 paragraphs
- Top 3-5 highlights
- Brief room summaries
- Essential action items only
- Best for: Daily quick reviews

**2. Detailed**
- Comprehensive overview
- All highlights organized by importance
- Full conversation summaries per room
- All action items with context
- File descriptions included
- Best for: Weekly reviews, thorough documentation

**3. Comprehensive**
- Full narrative of the day/period
- Detailed participant activity
- Complete conversation transcripts
- All files with metadata
- Topic analysis and trends
- Best for: Historical records, in-depth analysis

### Configuring Briefings

```python
# Quick daily summary (default)
generate_daily_briefing()

# Detailed yesterday's activity
generate_daily_briefing(
    date="2025-10-17",
    summary_length="detailed"
)

# Comprehensive multi-room briefing
generate_daily_briefing(
    date="2025-10-18",
    room_ids=[2, 5, 7],  # Management, Finance, Marketing
    include_files=True,
    summary_length="comprehensive"
)

# Focused room briefing without files
generate_daily_briefing(
    date="2025-10-18",
    room_ids=[5],  # Finance only
    include_files=False,
    summary_length="concise"
)
```

## Automated Briefing Generation

### Cron Job Integration

**The system supports automated daily briefing generation via cron:**

```bash
# Run at 9:00 AM daily (generates previous day's briefing)
0 9 * * * python /app/scripts/generate_daily_briefing.py

# Run with specific date
python scripts/generate_daily_briefing.py --date 2025-10-15

# Run for specific room
python scripts/generate_daily_briefing.py --room 5
```

**How it works:**
1. Cron job triggers at scheduled time
2. Script calls `generate_daily_briefing()` tool
3. Briefing generated and saved to knowledge base
4. Notification posted to Campfire (optional)

**Benefits:**
- Team gets daily summary automatically
- No manual trigger needed
- Consistent briefing schedule
- Historical record built automatically

## When to Use This Skill

**Trigger Scenarios:**
- User asks for "daily briefing", "daily summary", "what happened"
- User wants to "generate briefing for [date]"
- User searches "show me last week's briefings"
- User asks "when did we discuss [topic]" (search historical)
- User requests "recap" or "summary" of activity

**Keywords that should trigger this skill:**
- briefing, daily briefing, summary, recap
- what happened, activity, updates
- yesterday, today, last week, this month
- generate, create, make briefing
- search briefings, find briefings, past briefings
- show me, when did we, historical

## Integration with Other Skills

This skill enhances other skills:

**Knowledge Base Skill:**
- Briefings stored as official documentation
- Can be searched via KB tools
- Part of company knowledge archive

**Conversations Skill:**
- Uses conversation search to build briefings
- Provides structured summaries of discussions
- Complements detailed message search

**Financial Analysis Skill:**
- Include financial insights in briefings
- Highlight key financial discussions
- Track financial decision history

## Briefing Storage

### Knowledge Base Location

All briefings automatically saved to:
```
/ai-knowledge/company_kb/briefings/
├── 2025/
│   ├── 09/
│   │   ├── daily-briefing-2025-09-25.md
│   │   ├── daily-briefing-2025-09-26.md
│   │   └── ...
│   ├── 10/
│   │   ├── daily-briefing-2025-10-01.md
│   │   ├── daily-briefing-2025-10-15.md
│   │   ├── daily-briefing-2025-10-18.md
│   │   └── ...
```

### Briefing File Format

```markdown
# Daily Briefing - October 18, 2025

**Generated:** 2025-10-18 09:00:00
**Period:** 2025-10-17 00:00:00 to 2025-10-17 23:59:59
**Rooms:** 3 active rooms
**Messages:** 45 messages
**Participants:** 8 people
**Files:** 3 files shared

---

## Summary

[AI-generated high-level overview of the day's activities]

## Highlights

- ✨ Q4 budget approved at ¥500,000
- 📢 New hiring policy announced
- 🔧 Server migration scheduled for November 15

## Conversations by Room

### 💼 Finance Team (Room #5) - 18 messages

**Participants:** WU HENG, [Manager], [Accountant]

**Key Topics:**
- Monthly financial report review
- Q4 budget discussion
- Expense tracking updates

**Notable Messages:**
> "The Q4 budget has been approved at ¥500,000. Let's allocate 40% to marketing." - Manager, 14:35

[More conversation summaries...]

### 👥 HR Team (Room #3) - 15 messages

[Similar structure...]

## Files & Attachments

1. **october_financial_report.xlsx** (Finance Team, 14:20)
   - Uploaded by: WU HENG
   - Size: 248 KB
   - Monthly financial analysis

2. **hiring_policy_2025.pdf** (HR Team, 11:45)
   - Uploaded by: HR Manager
   - Size: 156 KB
   - Updated hiring guidelines

[More files...]

## Action Items

- [ ] **WU HENG**: Submit revised Q4 budget breakdown by Friday
- [ ] **HR Manager**: Announce new hiring policy company-wide
- [ ] **Tech Lead**: Finalize server migration timeline

## Topic Analysis

**Most Discussed Topics:**
1. Budget & Finance (23 mentions)
2. Hiring & Recruitment (15 mentions)
3. Technical Infrastructure (12 mentions)

---

*Generated by Campfire Daily Briefing Bot*
*Full archive: /briefings/2025/10/*
```

## Best Practices

### Do's

✅ **Generate briefings daily**
- Consistency helps track patterns
- Builds searchable archive
- Provides reliable history

✅ **Customize for audience**
- Management: Concise with highlights
- Team leads: Detailed with action items
- Archival: Comprehensive for records

✅ **Include context**
- Date and time range
- Rooms covered
- Participant counts

✅ **Extract action items**
- Look for commitments ("I will", "We'll")
- Note deadlines and owners
- Highlight important decisions

### Don'ts

❌ **Don't generate empty briefings**
```
If no activity on date:
→ "No messages or files for October 18, 2025.
   Would you like a briefing for a different date?"
```

❌ **Don't duplicate briefings unnecessarily**
```
If briefing already exists for date:
→ "Briefing for Oct 18 already generated. Would you like to:
   - View existing briefing
   - Regenerate with different settings"
```

❌ **Don't make briefings too long**
```
If 500+ messages in day:
→ Use "concise" mode by default
→ Focus on highlights and key themes
→ Offer detailed version if needed
```

❌ **Don't forget date context**
```
Always specify which date in briefing
Not: "Daily Briefing"
But: "Daily Briefing - October 18, 2025"
```

## Common Use Cases

### Use Case 1: Daily Team Standup

```
Manager: "Generate today's briefing for the team meeting"

Bot Workflow:
1. generate_daily_briefing(summary_length="concise")
2. Present top highlights and action items
3. Ready for team review in standup

Result: Quick, focused summary for team discussion
```

### Use Case 2: Weekly Executive Summary

```
Executive: "Show me this week's key activities"

Bot Workflow:
1. search_briefings(start_date="Mon", end_date="Fri")
2. Synthesize cross-day themes
3. Highlight major decisions and trends

Result: Strategic overview for leadership
```

### Use Case 3: Project Tracking

```
PM: "Find all briefings mentioning the mobile app project"

Bot Workflow:
1. search_briefings(query="mobile app", max_results=20)
2. Extract project-related updates
3. Build project timeline

Result: Historical project activity tracker
```

### Use Case 4: Onboarding New Team Member

```
New hire: "What has the team been working on?"

Bot Workflow:
1. search_briefings(start_date="30 days ago")
2. Identify recurring themes and projects
3. Present overview with context

Result: Quick catch-up for new team members
```

## Error Handling

### No Activity for Date

```
If generate_daily_briefing returns no messages:
→ "📅 No activity on October 18, 2025

   No messages or files were shared on this date.

   Would you like to:
   - Check a different date
   - Generate briefing for yesterday
   - Search for recent activity"
```

### Invalid Date Format

```
User: "Generate briefing for tomorrow"

Response:
→ "I can only generate briefings for past dates (already completed).

   Today's briefing will be available tomorrow.

   Would you like:
   - Yesterday's briefing (Oct 17)
   - Today's briefing so far (Oct 18, incomplete)
   - A specific past date?"
```

### Search Returns Too Many Results

```
If search_briefings returns 50+ results:
→ "Found 50+ briefings matching 'budget'.

   To narrow results:
   - Specify date range (e.g., 'last month')
   - Use more specific keywords
   - Limit to specific period

   Showing top 5 most recent: [...]"
```

---

**Last Updated:** October 18, 2025
**Use Case:** Daily briefing generation and historical search for Campfire AI bots
**Progressive Disclosure:** Loads only when generating briefings or searching briefing history
