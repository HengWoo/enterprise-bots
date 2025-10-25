---
name: Campfire Conversations
description: Searches past conversations and manages user context. Retrieves chat history by keywords, user, or room. Maintains user preferences, expertise areas, and conversation memory. Use when users ask "what did we discuss", "who said", "when did I mention", or when you need context from past interactions to provide personalized responses.
---

# Campfire Conversations

## Quick Start

When you need context from past conversations or user preferences:

1. **Search conversations** - Use `search_conversations` to find past messages
2. **Get user context** - Use `get_user_context` to understand user preferences
3. **Save context** - Use `save_user_context` to remember important information
4. **Provide context-aware responses** - Use retrieved information to personalize answers

## Core Capabilities

### Conversation Search

**What you can search:**
- Message content (keywords, phrases)
- User mentions ("what did John say about...")
- Topics discussed ("when did we talk about the budget?")
- Time-based queries ("last week's discussions")

**Search results include:**
- Message content (plain text)
- Sender name and ID
- Room name and ID
- Timestamp
- Relevance ranking

### User Context Management

**User context includes:**
- **Basic info**: Name, email, role
- **Preferences**: Language, communication style, reporting formats
- **Expertise**: Known areas of expertise
- **Conversation memory**: Important topics, decisions, patterns
- **Activity**: Recent rooms, frequent topics

### Available Tools (3 Conversation Tools)

**1. search_conversations**
- Search past messages by keywords
- Optional room filter (search specific room)
- Configurable result limit (default: 10)
- Returns ranked results with full context

**2. get_user_context**
- Retrieve user information from database
- Load saved preferences from JSON file
- Get expertise areas and conversation history
- Returns comprehensive user profile

**3. save_user_context**
- Save user preferences (language, formats, etc.)
- Record expertise areas
- Store conversation memory/patterns
- Updates JSON file for persistence

## Usage Workflows

### Workflow 1: Finding Past Discussions

```
User: "What did we discuss about the Q3 budget last week?"

Step 1: Search for relevant conversations
→ search_conversations(query="Q3 budget", limit=10)

Step 2: Filter by timeframe (in analysis)
→ Look for messages from last 7 days in results

Step 3: Summarize findings
→ "Last week, you discussed the Q3 budget with [names]:

   On [date], [name] mentioned: '[excerpt]'
   On [date], you said: '[excerpt]'

   The main points were:
   - [Point 1]
   - [Point 2]

   Would you like me to search for more details on any specific aspect?"
```

### Workflow 2: Understanding User Preferences

```
User: "@财务分析师 分析这份报表" (Analyze this report)

Step 1: Get user context
→ get_user_context(user_id=1)

Step 2: Check preferences
→ User prefers: Chinese language, YoY comparisons, detailed tables

Step 3: Tailor response accordingly
→ Generate analysis in Chinese
→ Include YoY comparisons
→ Use detailed HTML tables

Result: Personalized response matching user preferences
```

### Workflow 3: Learning from Interactions

```
User: "I prefer my financial reports to show year-over-year comparisons"

Step 1: Get current context
→ get_user_context(user_id=1)

Step 2: Update preferences
→ save_user_context(
     user_id=1,
     preferences={
       "reporting_format": "YoY comparison",
       "comparison_type": "year-over-year"
     }
   )

Step 3: Confirm
→ "✅ Got it! I'll always include year-over-year comparisons in your financial reports.

   This preference has been saved for future interactions."
```

### Workflow 4: Cross-Room Context

```
User: "Did anyone mention the new hiring policy?"

Step 1: Search across all rooms (no room filter)
→ search_conversations(query="hiring policy", limit=20)

Step 2: Group by room
→ Organize results by room for clarity

Step 3: Present findings
→ "The new hiring policy was discussed in multiple rooms:

   💼 HR Team (Room #5):
   - [Name] announced the policy on [date]
   - [Excerpt]

   💡 Management (Room #2):
   - [Name] asked about implementation on [date]
   - [Excerpt]

   Would you like me to search for more details in any of these rooms?"
```

### Workflow 5: Expert Identification

```
User: "Who knows about database optimization?"

Step 1: Search for discussions on topic
→ search_conversations(query="database optimization", limit=50)

Step 2: Analyze who contributed
→ Count messages per person on this topic

Step 3: Check saved expertise
→ get_user_context for frequent contributors

Step 4: Provide recommendations
→ "Based on past conversations, these team members have discussed database optimization:

   🥇 [Name1] - 12 messages, expertise noted in: PostgreSQL, indexing
   🥈 [Name2] - 8 messages, expertise noted in: Query optimization
   🥉 [Name3] - 5 messages, expertise noted in: Database architecture

   I'd recommend reaching out to [Name1] for database optimization help."
```

## Search Best Practices

### Effective Search Queries

**Good queries (specific keywords):**
- "Q3 budget meeting"
- "expense policy update"
- "server migration timeline"
- "hiring requirements frontend"

**Poor queries (too vague):**
- "meeting" (too common)
- "update" (too generic)
- "help" (no specific topic)

### Using Room Filters

```python
# Search specific room (faster, more relevant)
search_conversations(query="budget", room_id=5)

# Search all rooms (comprehensive)
search_conversations(query="budget")  # room_id=None
```

**When to use room filter:**
- User specifies room: "What did we discuss in Finance Team room?"
- Topic is room-specific: Project discussions, team meetings
- Performance: Faster for large message histories

**When to search all rooms:**
- Cross-team topics: Company-wide announcements, policies
- User doesn't specify room
- Finding first mention of a topic

### Result Limit Strategy

```python
# Quick lookup (default)
search_conversations(query="...", limit=10)

# Comprehensive search
search_conversations(query="...", limit=50)

# Recent mentions only
search_conversations(query="...", limit=5)
```

## User Context Structure

### Preferences Examples

```json
{
  "language": "zh-CN",
  "reporting_format": "YoY comparison",
  "communication_style": "professional",
  "preferred_analysis_depth": "detailed",
  "chart_type": "tables",
  "timezone": "Asia/Shanghai",
  "working_hours": "9:00-18:00"
}
```

### Expertise Areas Examples

```json
[
  "Financial Analysis",
  "Excel Power User",
  "Restaurant Operations",
  "Data Visualization",
  "Chinese Accounting Standards"
]
```

### Conversation Memory Examples

```json
[
  "Prefers monthly reports on first Monday",
  "Interested in cost optimization strategies",
  "Frequently asks about ROE and profit margins",
  "Works with Yebailing Restaurant data",
  "Mentioned launching delivery service in August"
]
```

## When to Save User Context

### Save preferences when:

**User explicitly states preference:**
```
User: "Always show me detailed breakdowns"
→ save_user_context(preferences={"analysis_depth": "detailed"})
```

**User corrects your approach:**
```
User: "I prefer simpler summaries, not detailed tables"
→ save_user_context(preferences={"format": "summary", "detail_level": "simple"})
```

**User mentions expertise:**
```
User: "I have experience with PostgreSQL optimization"
→ save_user_context(expertise=["PostgreSQL optimization"])
```

### Don't save for:

- One-time requests: "Show details this time only"
- Temporary conditions: "I'm in a hurry today"
- Questions/exploration: "What if I wanted YoY?"

## Common Use Cases

### Use Case 1: Recall Past Decisions

```
User: "What did we decide about the Q4 marketing budget?"

Bot Workflow:
1. search_conversations(query="Q4 marketing budget decision")
2. Filter for decision-making language ("decided", "agreed", "approved")
3. Present decision with context:

"On October 5th, you decided to allocate ¥500,000 for Q4 marketing:

[Quote from conversation]

Participants: [Names]
Room: Marketing Team

Would you like to see the full discussion?"
```

### Use Case 2: Track Action Items

```
User: "Did I commit to anything in yesterday's meeting?"

Bot Workflow:
1. search_conversations(query="[user name]", limit=20)
2. Filter by timestamp (yesterday)
3. Look for commitment language ("I will", "I'll", "I can")
4. Present action items:

"In yesterday's meeting, you committed to:

1. 'I'll send the financial report by Friday' (Finance Team room)
2. 'I can review the proposal tonight' (Management room)

Would you like me to help with any of these?"
```

### Use Case 3: Introduction Context

```
New user first interaction:

Bot Workflow:
1. get_user_context(user_id=X)
2. Check if context file exists
3. If new user:

"Hi [Name]! I'm the Campfire AI assistant. I can help you with:
- Financial analysis
- Searching past conversations
- Accessing company knowledge base

I'll remember your preferences as we interact. What can I help you with today?"
```

### Use Case 4: Topic Tracking

```
User: "How many times have we discussed the new product launch?"

Bot Workflow:
1. search_conversations(query="new product launch", limit=100)
2. Count unique messages
3. Group by date/room
4. Present statistics:

"The new product launch has been discussed 34 times:

By room:
- Product Team (Room #3): 18 times
- Marketing (Room #7): 12 times
- Management (Room #2): 4 times

Timeline:
- Last week: 15 mentions
- This week: 8 mentions

Most recent: [Latest message excerpt]"
```

### Use Case 5: Expertise Matching

```
User: "I need help with Excel pivot tables"

Bot Workflow:
1. search_conversations(query="Excel pivot tables expert", limit=30)
2. Check for users who've helped others with this topic
3. get_user_context for potential experts
4. Suggest:

"Based on past conversations, [Name] has Excel expertise:

They've helped with:
- Pivot table creation (5 times)
- Advanced formulas (8 times)
- Data visualization (3 times)

Their latest tip on pivot tables: '[excerpt]'

You could @mention them, or I can try to help!"
```

## Integration with Other Skills

This skill enhances other skills by providing context:

**Financial Analysis Skill:**
- Remember user's preferred financial metrics
- Recall past analyses for comparison
- Know user's industry/business context

**Knowledge Base Skill:**
- Track which policies user frequently references
- Remember user's common questions
- Suggest relevant documentation based on history

**Daily Briefing Skill:**
- Include topics user cares about
- Format briefings per user preferences
- Highlight action items for specific user

## When to Use This Skill

**Trigger Scenarios:**
- User asks "what did we discuss..."
- User wants to "find when I said..."
- User mentions "last week we talked about..."
- User asks "who mentioned..."
- User states a preference
- User demonstrates expertise in conversation
- You need to personalize a response

**Keywords that should trigger this skill:**
- what did, when did, who said, who mentioned
- last week, yesterday, last month, previously
- we discussed, we talked about, we decided
- remember, recall, find, search
- I prefer, I like, I want, my preference
- history, past, previous, earlier
- everyone, team, group, participants

## Success Criteria

A successful conversation interaction should:
- ✅ Find relevant past messages quickly
- ✅ Provide context (who, when, where)
- ✅ Summarize findings clearly
- ✅ Remember user preferences accurately
- ✅ Personalize responses based on context
- ✅ Update user context when learning new preferences

## Error Handling

### No Results Found

```
User: "What did we discuss about XYZ?"

If search returns nothing:
→ "I couldn't find any past discussions about XYZ.

   This might be the first time it's been mentioned, or it may have been
   discussed using different terminology.

   Would you like me to search for related topics?"
```

### Ambiguous Time Reference

```
User: "What did we discuss recently?"

Response:
→ "I'd be happy to search recent discussions. To give you the most relevant results:

   - What topic are you interested in?
   - Which room? (or all rooms)
   - How far back? (today, this week, this month)

   Or I can show you the most recent messages across all rooms."
```

### User Context Not Found

```
If get_user_context returns minimal data:
→ "I don't have much context saved for you yet. As we interact more,
   I'll learn your preferences and expertise areas.

   Feel free to tell me about your preferences anytime!"
```

## Privacy & Data Handling

### What Gets Saved

**✅ Always saved:**
- Message content (in Campfire database)
- User preferences (in JSON file)
- Expertise areas (in JSON file)
- Conversation patterns (in JSON file)

**❌ Never saved separately:**
- Passwords or credentials
- Personal sensitive information
- Private messages not in Campfire

### User Control

**Users can:**
- View their saved preferences anytime: "Show me my preferences"
- Update preferences: "Change my preference for..."
- Clear conversation memory: "Forget what I said about..."

**Users cannot:**
- Delete messages from Campfire (use Campfire UI)
- Access other users' private contexts
- See deleted messages (respect Campfire deletions)

## Best Practices

### Do's

✅ **Remember explicit preferences**
```
User: "I prefer Chinese for financial reports"
→ Save this preference immediately
```

✅ **Provide context in summaries**
```
When summarizing: Include who, when, which room
Not just: "Someone said the budget was approved"
But: "On Oct 5th in Finance Team, John approved the ¥500K budget"
```

✅ **Ask for clarification when ambiguous**
```
User: "What did we discuss?"
→ Ask: What topic? Which room? When?
```

✅ **Update context incrementally**
```
As you learn about user:
- Add expertise when they demonstrate knowledge
- Note preferences when they state them
- Remember important topics they care about
```

### Don'ts

❌ **Don't save assumptions**
```
User asks one financial question
→ Don't assume they always want financial topics
→ Wait for pattern or explicit preference
```

❌ **Don't overwhelm with results**
```
If search returns 100 messages
→ Don't dump all 100 on user
→ Summarize top 5-10, offer to show more
```

❌ **Don't make up context**
```
If search returns nothing
→ Say "no results found"
→ Don't invent what might have been discussed
```

❌ **Don't ignore user corrections**
```
User: "Actually, I prefer summary format"
→ Update preference immediately
→ Don't keep using detailed format
```

---

**Last Updated:** October 18, 2025
**Use Case:** Conversation search and user context management for Campfire AI bots
**Progressive Disclosure:** Loads only when needing to search past conversations or manage user preferences
