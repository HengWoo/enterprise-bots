"""
Agent SDK Tools Package
Re-exports all tool decorators from modular files
"""

from src.tools.campfire_tools import CampfireTools

# Optional Supabase import (only available if supabase package is installed)
try:
    from src.tools.supabase_tools import SupabaseTools
except ImportError:
    SupabaseTools = None

from src.tools import (
    campfire_decorators,
    briefing_decorators,
    personal_decorators,
    operations_decorators,
    analytics_decorators,
    menu_engineering_decorators
)


def initialize_decorator_tools(campfire_tools_instance, supabase_tools_instance=None):
    """
    Initialize all decorator modules with the required tool instances

    Args:
        campfire_tools_instance: CampfireTools instance
        supabase_tools_instance: SupabaseTools instance (optional)
    """
    # Set tools for all decorator modules
    campfire_decorators.set_tools(campfire_tools_instance, supabase_tools_instance)
    briefing_decorators.set_tools(campfire_tools_instance, supabase_tools_instance)
    personal_decorators.set_tools(campfire_tools_instance, supabase_tools_instance)
    operations_decorators.set_tools(campfire_tools_instance, supabase_tools_instance)
    analytics_decorators.set_tools(campfire_tools_instance, supabase_tools_instance)
    menu_engineering_decorators.set_tools(campfire_tools_instance, supabase_tools_instance)


# Re-export all tool functions for backward compatibility
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

# Image and document processing removed - use Skills MCP or Read tool

__all__ = [
    # Core classes
    'CampfireTools',
    'SupabaseTools',

    # Initialization
    'initialize_decorator_tools',

    # Campfire tools
    'search_conversations_tool',
    'get_user_context_tool',
    'save_user_preference_tool',
    'search_knowledge_base_tool',
    'read_knowledge_document_tool',
    'list_knowledge_documents_tool',
    'store_knowledge_document_tool',

    # Briefing tools
    'generate_daily_briefing_tool',
    'search_briefings_tool',

    # Personal tools
    'manage_personal_tasks_tool',
    'set_reminder_tool',
    'save_personal_note_tool',
    'search_personal_notes_tool',

    # Operations tools
    'query_operations_data_tool',
    'update_operations_data_tool',
    'get_operations_summary_tool',

    # Analytics tools
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

    # Menu engineering tools
    'get_menu_profitability_tool',
    'get_top_profitable_dishes_tool',
    'get_low_profit_dishes_tool',
    'get_cost_coverage_rate_tool',
    'get_dishes_missing_cost_tool'
]
