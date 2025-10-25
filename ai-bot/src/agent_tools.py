"""
Agent SDK Tool Wrappers for Campfire
Imports and re-exports all tools from modular decorator files

NOTE: This file has been refactored in v0.3.3 to split 2,418 lines into modular files:
- src/tools/campfire_decorators.py (7 tools)
- src/tools/briefing_decorators.py (2 tools)
- src/tools/personal_decorators.py (4 tools)
- src/tools/operations_decorators.py (3 tools)
- src/tools/analytics_decorators.py (10 tools)
- src/tools/menu_engineering_decorators.py (5 tools)
- src/tools/image_decorators.py (1 tool)

Total: 32 tools across 7 modular files
"""

from src.tools.campfire_tools import CampfireTools
from src.tools import initialize_decorator_tools
from typing import Optional
import os

# Optional Supabase import
try:
    from src.tools.supabase_tools import SupabaseTools
except ImportError:
    SupabaseTools = None


# Global instances (will be initialized by app)
_campfire_tools: Optional[CampfireTools] = None
_supabase_tools: Optional[SupabaseTools] = None


def initialize_tools(campfire_tools: CampfireTools):
    """Initialize the global CampfireTools instance and all decorator modules"""
    global _campfire_tools, _supabase_tools
    _campfire_tools = campfire_tools

    # Initialize Supabase tools if available and credentials are present
    if SupabaseTools and os.environ.get("SUPABASE_URL") and os.environ.get("SUPABASE_KEY"):
        try:
            _supabase_tools = SupabaseTools()
            print("[Supabase] ✅ Supabase tools initialized")
        except Exception as e:
            print(f"[Supabase] ⚠️  Failed to initialize Supabase tools: {e}")
            _supabase_tools = None
    else:
        if not SupabaseTools:
            print("[Supabase] ℹ️  Supabase package not installed")
        else:
            print("[Supabase] ℹ️  Supabase credentials not found - operations tools disabled")

    # Initialize all decorator modules
    initialize_decorator_tools(_campfire_tools, _supabase_tools)
    print("[Tools] ✅ All 32 tool decorators initialized across 7 modules")


# Re-export all tool functions from decorator modules
from src.tools.campfire_decorators import (
    search_conversations_tool,
    get_user_context_tool,
    save_user_preference_tool,
    search_knowledge_base_tool,
    read_knowledge_document_tool,
    list_knowledge_documents_tool,
    store_knowledge_document_tool
)

from src.tools.briefing_decorators import (
    generate_daily_briefing_tool,
    search_briefings_tool
)

from src.tools.personal_decorators import (
    manage_personal_tasks_tool,
    set_reminder_tool,
    save_personal_note_tool,
    search_personal_notes_tool
)

from src.tools.operations_decorators import (
    query_operations_data_tool,
    update_operations_data_tool,
    get_operations_summary_tool
)

from src.tools.analytics_decorators import (
    get_daily_revenue_tool,
    get_revenue_by_zone_tool,
    get_top_dishes_tool,
    get_station_performance_tool,
    get_quick_stats_tool,
    get_hourly_revenue_tool,
    get_table_turnover_tool,
    get_return_analysis_tool,
    get_order_type_distribution_tool,
    get_revenue_trend_tool
)

from src.tools.menu_engineering_decorators import (
    get_menu_profitability_tool,
    get_top_profitable_dishes_tool,
    get_low_profit_dishes_tool,
    get_cost_coverage_rate_tool,
    get_dishes_missing_cost_tool
)

from src.tools.image_decorators import (
    process_image_tool
)

# Aggregate all tools into AGENT_TOOLS list (for SDK MCP server creation)
AGENT_TOOLS = [
    # Campfire tools (7)
    search_conversations_tool,
    get_user_context_tool,
    save_user_preference_tool,
    search_knowledge_base_tool,
    read_knowledge_document_tool,
    list_knowledge_documents_tool,
    store_knowledge_document_tool,
    # Briefing tools (2)
    generate_daily_briefing_tool,
    search_briefings_tool,
    # Personal tools (4)
    manage_personal_tasks_tool,
    set_reminder_tool,
    save_personal_note_tool,
    search_personal_notes_tool,
    # Operations tools (3)
    query_operations_data_tool,
    update_operations_data_tool,
    get_operations_summary_tool,
    # Analytics tools (10)
    get_daily_revenue_tool,
    get_revenue_by_zone_tool,
    get_top_dishes_tool,
    get_station_performance_tool,
    get_quick_stats_tool,
    get_hourly_revenue_tool,
    get_table_turnover_tool,
    get_return_analysis_tool,
    get_order_type_distribution_tool,
    get_revenue_trend_tool,
    # Menu engineering tools (5)
    get_menu_profitability_tool,
    get_top_profitable_dishes_tool,
    get_low_profit_dishes_tool,
    get_cost_coverage_rate_tool,
    get_dishes_missing_cost_tool,
    # Image tools (1)
    process_image_tool
]

# Export all for backward compatibility
__all__ = [
    'initialize_tools',
    'AGENT_TOOLS',
    # Campfire tools (7)
    'search_conversations_tool',
    'get_user_context_tool',
    'save_user_preference_tool',
    'search_knowledge_base_tool',
    'read_knowledge_document_tool',
    'list_knowledge_documents_tool',
    'store_knowledge_document_tool',
    # Briefing tools (2)
    'generate_daily_briefing_tool',
    'search_briefings_tool',
    # Personal tools (4)
    'manage_personal_tasks_tool',
    'set_reminder_tool',
    'save_personal_note_tool',
    'search_personal_notes_tool',
    # Operations tools (3)
    'query_operations_data_tool',
    'update_operations_data_tool',
    'get_operations_summary_tool',
    # Analytics tools (10)
    'get_daily_revenue_tool',
    'get_revenue_by_zone_tool',
    'get_top_dishes_tool',
    'get_station_performance_tool',
    'get_quick_stats_tool',
    'get_hourly_revenue_tool',
    'get_table_turnover_tool',
    'get_return_analysis_tool',
    'get_order_type_distribution_tool',
    'get_revenue_trend_tool',
    # Menu engineering tools (5)
    'get_menu_profitability_tool',
    'get_top_profitable_dishes_tool',
    'get_low_profit_dishes_tool',
    'get_cost_coverage_rate_tool',
    'get_dishes_missing_cost_tool',
    # Image tools (1)
    'process_image_tool'
]
