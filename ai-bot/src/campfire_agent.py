"""
Campfire Agent - Claude Agent SDK Wrapper
Wraps the Claude Agent SDK to provide bot functionality for Campfire
"""

from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, create_sdk_mcp_server
from src.bot_manager import BotConfig
from src.agent_tools import AGENT_TOOLS, initialize_tools
from src.tools.campfire_tools import CampfireTools
from src.progress_classifier import ProgressClassifier
from typing import Dict, Optional, Callable


class CampfireAgent:
    """
    Wrapper around Claude Agent SDK for Campfire bots.

    Handles:
    - Agent SDK client initialization
    - Tool configuration
    - Message processing with context
    - Streaming response handling
    """

    def __init__(self, bot_config: BotConfig, campfire_tools: CampfireTools, resume_session: Optional[str] = None):
        """
        Initialize Campfire agent with bot configuration.

        Args:
            bot_config: Bot configuration from BotManager
            campfire_tools: CampfireTools instance for database access
            resume_session: Optional session ID to resume conversation
        """
        self.bot_config = bot_config
        self.campfire_tools = campfire_tools
        self.client: Optional[ClaudeSDKClient] = None
        self.resume_session = resume_session

        # Initialize tools with campfire_tools instance
        initialize_tools(campfire_tools)

        # Create Agent SDK client
        self._create_client()

        # Client needs to be connected before use
        self._connected = False

    def _get_allowed_tools_for_bot(self) -> list:
        """
        Get allowed tools based on bot configuration.

        Returns:
            List of tool names including both MCP tools and built-in SDK tools
        """
        # Built-in SDK tools (available by default unless restricted)
        # Reference: https://docs.claude.com/en/api/agent-sdk/overview
        builtin_tools = [
            "WebSearch",      # Search the web for information
            "WebFetch",       # Fetch web page content
            "Read",           # Read file contents
            "Write",          # Write to files
            "Edit",           # Edit files
            "Bash",           # Execute shell commands
            "Grep",           # Search within files
            "Glob"            # Find files by pattern
        ]

        # Base MCP tools (available to all bots)
        base_tools = [
            "mcp__campfire__search_conversations",
            "mcp__campfire__get_user_context",
            "mcp__campfire__save_user_preference",
            "mcp__campfire__search_knowledge_base",
            "mcp__campfire__read_knowledge_document",
            "mcp__campfire__list_knowledge_documents",
            "mcp__campfire__store_knowledge_document",
            "mcp__campfire__process_image"  # Image analysis with vision API
        ]

        # Start with built-in tools + base MCP tools
        allowed_tools = builtin_tools + base_tools

        # Financial analyst gets financial tools
        if self.bot_config.bot_id == "financial_analyst":
            financial_tools = [
                # Simple Tools
                "mcp__fin-report-agent__read_excel_region",
                "mcp__fin-report-agent__search_in_excel",
                "mcp__fin-report-agent__get_excel_info",
                "mcp__fin-report-agent__calculate",
                "mcp__fin-report-agent__show_excel_visual",
                # Navigation Tools
                "mcp__fin-report-agent__find_account",
                "mcp__fin-report-agent__get_financial_overview",
                "mcp__fin-report-agent__get_account_context",
                # Thinking Tools
                "mcp__fin-report-agent__think_about_financial_data",
                "mcp__fin-report-agent__think_about_analysis_completeness",
                "mcp__fin-report-agent__think_about_assumptions",
                # Memory Tools
                "mcp__fin-report-agent__save_analysis_insight",
                "mcp__fin-report-agent__get_session_context",
                "mcp__fin-report-agent__write_memory_note",
                "mcp__fin-report-agent__get_session_recovery_info",
                # Complex Tools
                "mcp__fin-report-agent__validate_account_structure",
                # Skills MCP tools for document creation (complementary to financial analysis)
                "mcp__skills__list_skills",
                "mcp__skills__load_skill",
                "mcp__skills__load_skill_file"
            ]
            allowed_tools.extend(financial_tools)
            return allowed_tools

        # Briefing assistant gets briefing tools
        if self.bot_config.bot_id == "briefing_assistant":
            briefing_tools = [
                "mcp__campfire__generate_daily_briefing",
                "mcp__campfire__search_briefings"
            ]
            allowed_tools.extend(briefing_tools)
            return allowed_tools

        # Personal assistant gets personal productivity tools
        if self.bot_config.bot_id == "personal_assistant":
            personal_tools = [
                "mcp__campfire__manage_personal_tasks",
                "mcp__campfire__set_reminder",
                "mcp__campfire__save_personal_note",
                "mcp__campfire__search_personal_notes",
                # Skills MCP tools for progressive skill disclosure
                "mcp__skills__list_skills",
                "mcp__skills__load_skill",
                "mcp__skills__load_skill_file"
            ]
            allowed_tools.extend(personal_tools)
            return allowed_tools

        # Operations assistant gets Supabase tools (read-only for now)
        if self.bot_config.bot_id == "operations_assistant":
            operations_tools = [
                # Basic Supabase tools
                "mcp__campfire__query_operations_data",
                # "mcp__campfire__update_operations_data",  # Paused - requires service_role key
                "mcp__campfire__get_operations_summary",
                # Restaurant analytics RPC tools
                "mcp__campfire__get_daily_revenue",
                "mcp__campfire__get_revenue_by_zone",
                "mcp__campfire__get_top_dishes",
                "mcp__campfire__get_station_performance",
                "mcp__campfire__get_hourly_revenue",
                "mcp__campfire__get_table_turnover",
                "mcp__campfire__get_return_analysis",
                "mcp__campfire__get_order_type_distribution",
                "mcp__campfire__get_revenue_trend",
                "mcp__campfire__get_quick_stats"
            ]
            allowed_tools.extend(operations_tools)
            return allowed_tools

        # Menu engineer gets menu engineering Supabase tools
        if self.bot_config.bot_id == "menu_engineer":
            menu_engineering_tools = [
                # Menu profitability analysis (Boston Matrix)
                "mcp__campfire__get_menu_profitability",
                "mcp__campfire__get_top_profitable_dishes",
                "mcp__campfire__get_low_profit_dishes",
                "mcp__campfire__get_cost_coverage_rate",
                "mcp__campfire__get_dishes_missing_cost"
            ]
            allowed_tools.extend(menu_engineering_tools)
            return allowed_tools

        # Technical assistant or other bots: base tools only (built-in + campfire MCP)
        return allowed_tools

    def _create_client(self):
        """Create Claude Agent SDK client with bot configuration"""

        # Create Campfire MCP server from our tools
        campfire_mcp_server = create_sdk_mcp_server(
            name="campfire",
            version="1.0.0",
            tools=AGENT_TOOLS
        )

        # MCP servers configuration
        mcp_servers = {
            "campfire": campfire_mcp_server
        }

        # Add Financial MCP for financial_analyst bot
        if self.bot_config.bot_id == "financial_analyst":
            # External Financial MCP (stdio transport via uv)
            # Use uv run to ensure dependencies are available
            mcp_servers["fin-report-agent"] = {
                "transport": "stdio",
                "command": "uv",
                "args": [
                    "run",
                    "--directory",
                    "/app/financial-mcp",
                    "python",
                    "run_mcp_server.py"
                ]
            }

        # Add Skills MCP for bots with progressive skill disclosure capability
        if self.bot_config.capabilities.get('skills_progressive_disclosure'):
            # Skills MCP for on-demand skill loading (reduces token usage by ~63%)
            # Complementary to Financial MCP: Skills focuses on creation, Financial on analysis
            import os
            skills_dir = os.environ.get("SKILLS_DIR", "/app/.claude/skills")

            # Use environment-aware path for Skills MCP (local vs Docker)
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            skills_mcp_dir = os.path.join(project_root, "skills-mcp")

            mcp_servers["skills"] = {
                "transport": "stdio",
                "command": "uv",
                "args": [
                    "run",
                    "--directory",
                    skills_mcp_dir,  # Environment-aware path (works local + Docker)
                    "python",
                    "server.py"
                ],
                "env": {
                    "SKILLS_DIR": skills_dir
                }
            }

            print(f"[Skills MCP] ✅ Loaded Skills MCP for {self.bot_config.bot_id} (progressive skill disclosure)")
            print(f"[Skills MCP] Directory: {skills_mcp_dir}")

        # Get allowed tools based on bot type
        allowed_tools = self._get_allowed_tools_for_bot()

        # Create Agent SDK options
        # Use /tmp/campfire-files for local testing, /campfire-files in Docker
        import os
        # Get the project root directory (where .claude/skills/ exists)
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # CRITICAL: Always use project root for skills discovery
        # The .claude/skills/ directory is in the project root, not in /tmp/campfire-files
        cwd_path = project_root

        # Add current date/time to system prompt so bot knows what "today" is
        from datetime import datetime
        current_date = datetime.now().strftime('%Y-%m-%d')
        current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        enhanced_system_prompt = f"""**IMPORTANT: Current Date and Time**
Today's date: {current_date}
Current date/time: {current_datetime}
Timezone: System local time

When users ask about "today", "this week", "this month", use the date above.

---

{self.bot_config.system_prompt}"""

        # Base options
        options_dict = {
            "model": self.bot_config.model,
            "system_prompt": enhanced_system_prompt,
            "mcp_servers": mcp_servers,
            "allowed_tools": allowed_tools,
            "permission_mode": 'default',
            "cwd": cwd_path,  # Set working directory for file operations
            "max_turns": 30  # Allow 30 turns for complex multi-step analyses with multiple tool calls
        }

        # Debug: log skills configuration
        print(f"[Skills] Working directory: {cwd_path}")
        print(f"[Skills] Skills MCP: {'ENABLED' if 'skills' in mcp_servers else 'DISABLED'}")

        # Add resume parameter if session exists (enables multi-turn conversation)
        if self.resume_session:
            options_dict["resume"] = self.resume_session
            print(f"[Agent Init] 🔄 Resuming session: {self.resume_session}")
        else:
            print(f"[Agent Init] 🆕 Starting new session")

        options = ClaudeAgentOptions(**options_dict)

        # Create client
        self.client = ClaudeSDKClient(options=options)

    async def process_message(
        self,
        content: str,
        context: Dict,
        on_text_block: Optional[Callable[[str], None]] = None,
        on_milestone: Optional[Callable[[str], None]] = None
    ) -> tuple[str, Optional[str]]:
        """
        Process a message with API fallback support.

        Fallback strategy:
        1. Try primary API (configured via ANTHROPIC_BASE_URL/ANTHROPIC_API_KEY)
        2. On failure, switch to fallback API (ANTHROPIC_BASE_URL_FALLBACK/ANTHROPIC_API_KEY_FALLBACK)
        3. Return error if both fail

        Args:
            content: Message content from user
            context: Dict with keys:
                - user_id: User ID
                - user_name: User name
                - room_id: Room ID
                - room_name: Room name
                - message_id: Message ID (optional)
            on_text_block: Optional callback function called for each text block
                as it streams in. Useful for posting intermediate messages.
            on_milestone: Optional callback for significant progress milestones
                (smart filtering - not every text block, only major steps)

        Returns:
            Tuple of (response_text, session_id)
            - response_text: AI response text
            - session_id: Session ID from SystemMessage (for caching)
        """
        import os

        # Store original configuration
        original_base_url = os.environ.get('ANTHROPIC_BASE_URL')
        original_api_key = os.environ.get('ANTHROPIC_API_KEY')
        original_model = self.bot_config.model

        try:
            # Try primary API first
            print(f"[API] Using primary API: {original_base_url}")
            return await self._process_with_current_config(
                content, context, on_text_block, on_milestone
            )

        except Exception as primary_error:
            print(f"[API Fallback] ⚠️ Primary API failed: {type(primary_error).__name__}: {str(primary_error)[:200]}")

            # Check if fallback is configured
            fallback_url = os.environ.get('ANTHROPIC_BASE_URL_FALLBACK')
            fallback_key = os.environ.get('ANTHROPIC_API_KEY_FALLBACK')
            fallback_model = os.environ.get('FALLBACK_MODEL', 'claude-haiku-4-5-20251001')

            if not fallback_url or not fallback_key:
                print("[API Fallback] ❌ No fallback configured, propagating error")
                raise primary_error

            try:
                print(f"[API Fallback] 🔄 Switching to fallback API: {fallback_url}")
                print(f"[API Fallback] 📝 Using fallback model: {fallback_model}")

                # Swap environment variables
                os.environ['ANTHROPIC_BASE_URL'] = fallback_url
                os.environ['ANTHROPIC_API_KEY'] = fallback_key

                # Update bot config model for this request
                self.bot_config.model = fallback_model

                # Recreate client with fallback configuration
                self._create_client()
                self._connected = False  # Force reconnection

                # Retry with fallback
                result = await self._process_with_current_config(
                    content, context, on_text_block, on_milestone
                )

                print("[API Fallback] ✅ Fallback API succeeded")
                return result

            except Exception as fallback_error:
                print(f"[API Fallback] ❌ Fallback API also failed: {type(fallback_error).__name__}: {str(fallback_error)[:200]}")
                # Return the original error (more likely to be useful for debugging)
                raise primary_error

            finally:
                # Always restore original configuration
                print("[API Fallback] 🔙 Restoring original configuration")
                if original_base_url:
                    os.environ['ANTHROPIC_BASE_URL'] = original_base_url
                if original_api_key:
                    os.environ['ANTHROPIC_API_KEY'] = original_api_key
                self.bot_config.model = original_model

                # Recreate client with original config for next request
                self._create_client()
                self._connected = False

    async def _process_with_current_config(
        self,
        content: str,
        context: Dict,
        on_text_block: Optional[Callable[[str], None]] = None,
        on_milestone: Optional[Callable[[str], None]] = None
    ) -> tuple[str, Optional[str]]:
        """
        Process a message with the current API configuration.

        This is the actual processing logic, extracted to allow reuse
        for both primary and fallback API attempts.
        """
        if not self.client:
            raise RuntimeError("Agent client not initialized")

        # Connect client if not already connected
        if not self._connected:
            await self.client.connect()
            self._connected = True

        # Build prompt with context
        prompt = self._build_prompt(content, context)

        # Send query (no session_id parameter - session managed by resume)
        await self.client.query(prompt)

        # Receive response (streaming)
        response_text = ""
        session_id = None
        last_tool_name = None  # Track last tool called for milestone context
        milestone_count = 0  # Prevent milestone spam
        MAX_MILESTONES = 5  # Maximum milestones to post

        async for message in self.client.receive_response():
            # Print message type for debugging
            print(f"[Agent SDK] Received: {message.__class__.__name__}")

            # Extract session_id from SystemMessage with subtype 'init' (first message in conversation)
            if hasattr(message, '__class__') and message.__class__.__name__ == 'SystemMessage':
                # Session ID is in data['session_id'] when subtype == 'init'
                if hasattr(message, 'subtype') and message.subtype == 'init':
                    if hasattr(message, 'data') and 'session_id' in message.data:
                        session_id = message.data['session_id']
                        print(f"[Agent Session] 💾 Captured session_id: {session_id}")

            # Only extract text from AssistantMessage content blocks
            # Ignore SystemMessage, UserMessage (tool results), ResultMessage
            if hasattr(message, '__class__') and message.__class__.__name__ == 'AssistantMessage':
                if hasattr(message, 'content'):
                    for block in message.content:
                        block_type = block.__class__.__name__

                        # Log ToolUseBlock FIRST (before text blocks)
                        if block_type == 'ToolUseBlock':
                            tool_name = getattr(block, 'name', 'unknown')
                            tool_input = getattr(block, 'input', {})
                            last_tool_name = tool_name  # Track for milestone context

                            print(f"[Agent Tool Call] 🔧 Tool: {tool_name}")
                            print(f"[Agent Tool Call]    Input: {tool_input}")

                            # Post tool milestone if it's a major tool
                            if on_milestone and milestone_count < MAX_MILESTONES:
                                milestone_msg = ProgressClassifier.get_tool_milestone(tool_name)
                                if milestone_msg:
                                    try:
                                        await on_milestone(milestone_msg)
                                        milestone_count += 1
                                        print(f"[Milestone] Posted tool milestone: {milestone_msg}")
                                    except Exception as e:
                                        print(f"[Warning] Error in on_milestone callback: {e}")

                        # TextBlock contains the actual response text
                        elif block_type == 'TextBlock':
                            if hasattr(block, 'text'):
                                text = block.text
                                # Print text as it arrives
                                print(f"[Agent Message] {text[:200]}...")

                                # Detect API errors in response text and raise exception for fallback
                                if "API Error:" in text or "无效的令牌" in text or "invalid_api_key" in text:
                                    error_msg = text[:500]  # Get first 500 chars of error
                                    print(f"[API Error Detected] {error_msg}")
                                    raise RuntimeError(f"API authentication failed: {error_msg}")

                                response_text += text

                                # Check if this is a milestone message (smart filtering)
                                if on_milestone and milestone_count < MAX_MILESTONES:
                                    if ProgressClassifier.is_milestone(text, last_tool_name):
                                        # Extract meaningful preview for milestone
                                        preview = ProgressClassifier.truncate_for_preview(text, max_length=150)
                                        try:
                                            await on_milestone(f"💭 {preview}")
                                            milestone_count += 1
                                            print(f"[Milestone] Posted text milestone: {preview[:50]}...")
                                        except Exception as e:
                                            print(f"[Warning] Error in on_milestone callback: {e}")

                                # Call on_text_block callback if provided (for legacy compatibility)
                                if on_text_block and text.strip():
                                    try:
                                        on_text_block(text)
                                    except Exception as e:
                                        print(f"[Warning] Error in on_text_block callback: {e}")

        return response_text, session_id

    def _build_prompt(self, content: str, context: Dict) -> str:
        """
        Build prompt with context for Agent SDK.

        Args:
            content: User message content
            context: Context dict with user/room info

        Returns:
            Formatted prompt string
        """
        # Get recent conversation history from current room
        recent_messages = []
        try:
            room_id = context.get('room_id')
            if room_id:
                # Search for recent messages (empty query returns all)
                messages = self.campfire_tools.search_conversations(
                    query="",  # Empty query to get all recent messages
                    room_id=room_id,
                    limit=10
                )
                recent_messages = messages
                print(f"[Context] Loaded {len(messages)} messages from room {room_id}:")
                for msg in messages:
                    print(f"  - {msg['creator_name']}: {msg['body'][:100]}")
        except Exception as e:
            print(f"[Warning] Could not load conversation history: {e}")

        # Build base context
        prompt = f"""CURRENT CONTEXT:
You are responding in room: {context.get('room_name', 'Unknown')} (Room ID: {context.get('room_id', 'unknown')})
User: {context.get('user_name', 'Unknown')} (User ID: {context.get('user_id', 'unknown')})"""

        # Add recent conversation history
        if recent_messages:
            prompt += f"\n\nRECENT CONVERSATION HISTORY ({len(recent_messages)} recent messages):"
            for msg in reversed(recent_messages):  # Chronological order
                prompt += f"\n{msg['creator_name']}: {msg['body'][:200]}..."  # Truncate long messages

            # Count conversation rounds (back-and-forth between user and bot)
            current_user = context.get('user_name', 'Unknown')
            bot_name = self.bot_config.name if hasattr(self, 'bot_config') else 'Bot'

            # Count messages from current user
            user_message_count = len([m for m in recent_messages if m['creator_name'] == current_user])

            # If conversation is getting long (>10 user messages), suggest dedicated chat
            if user_message_count > 10:
                prompt += f"\n\n🔔 CONVERSATION LENGTH NOTICE:"
                prompt += f"\nThis conversation has {user_message_count} messages from {current_user}."
                prompt += f"\nConsider suggesting: '建议创建专属对话以获得更好的上下文管理和对话连续性。'"
                prompt += f"\n(After 10+ rounds, a dedicated chat provides better context management.)"

        # Query room files from database (cross-message file discovery)
        room_files = []
        try:
            room_id = context.get('room_id')
            if room_id:
                room_files = self.campfire_tools.get_recent_room_files(
                    room_id=room_id,
                    limit=10  # Last 10 files uploaded in room
                )
                if room_files:
                    print(f"[Room Files] Found {len(room_files)} file(s) in room {room_id}")
        except Exception as e:
            print(f"[Warning] Could not load room files: {e}")

        # Add room files to prompt
        if room_files:
            prompt += f"\n\nFILES AVAILABLE IN THIS ROOM:"
            prompt += f"\nWorking directory: /campfire-files"
            prompt += f"\nRecently uploaded files ({len(room_files)}):"
            for f in room_files:
                prompt += f"\n  📎 {f['filename']} - {f['file_path']}"

        # Add guidelines
        prompt += f"""

IMPORTANT GUIDELINES:
- When searching conversations, default to room_id={context.get('room_id', 'unknown')} (search the CURRENT room)
- Only search other rooms if the user explicitly asks about them
- When saving user preferences, use user_id={context.get('user_id', 'unknown')}
- You are currently in "{context.get('room_name', 'Unknown')}" room - search here by default"""

        # Add file analysis guidance for financial analyst
        if room_files and hasattr(self, 'bot_config') and self.bot_config.bot_id == "financial_analyst":
            prompt += f"""

FILE ANALYSIS GUIDANCE:
- Files are in working directory: /campfire-files
- Use Glob to search: Glob(pattern='**/*报表*.xlsx') finds financial reports
- File paths are provided above - use them directly in tool calls
- For Excel analysis: START with get_excel_info, then read_excel_region
- For financial reports: Use validate_account_structure to parse structure
- For visualization: use show_excel_visual after reading data

MANDATORY VALIDATION WORKFLOW (财务分析必须执行):
🚨 CRITICAL: You MUST follow this interactive validation workflow:

Step 1 - Initial Exploration (初步探索):
- Use think_about_financial_data() to assess what information you need
- Ask user: "我看到文件有X行Y列，包含Y-M月数据。您希望重点分析哪些方面？（盈利能力/成本控制/趋势分析）"
- Wait for user confirmation before proceeding

Step 2 - Structure Validation (结构验证):
- Use validate_account_structure() to show account hierarchy
- Ask user: "我发现了这样的账户结构：[show structure]。这个结构是否正确？"
- If long-term prepaid expenses exist, ask: "长期待摊费用的摊销期是多少年？（通常3-5年）"
- Wait for user confirmation on structure and assumptions

Step 3 - Analysis Approach (分析方法确认):
- Use think_about_assumptions() to validate your approach
- Ask user: "我计划使用叶子账户避免重复计算，并与行业基准对比。您是否同意这个分析方法？"
- Wait for user approval

Step 4 - Execute Analysis (执行分析):
- Only after user confirms Steps 1-3, proceed with detailed analysis
- Use read_excel_region() and calculate() as needed
- Document all confirmed assumptions in your report

Step 5 - Save Insights (保存洞察):
- Use save_analysis_insight() to store key findings
- Use write_memory_note() to document patterns for future reference

TOOL COMMUNICATION (CRITICAL):
- BEFORE calling tool: Tell user what you're doing ("让我先查看文件结构...")
- AFTER tool returns: Explain findings in your own words, don't show raw output
- ASK QUESTIONS: Don't just narrate - actively seek user input and confirmation
- WAIT for responses: Each validation step requires user confirmation before proceeding
- Keep analysis narrative flowing naturally - tools are internal, insights are what user sees
- Example: "我看到这个文件有X行Y列，您希望我重点关注哪些指标？" NOT just "[Image #1]" or passive narration"""

        prompt += f"\n\nUser Message: {content}"

        return prompt
