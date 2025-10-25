"""
Menu engineering profitability analysis tools
Agent SDK Tool Decorators
"""

from claude_agent_sdk import tool
from typing import Optional

# Global instances (will be initialized by app)
_campfire_tools: Optional = None
_supabase_tools: Optional = None


def set_tools(campfire_tools, supabase_tools):
    """Set the global tool instances"""
    global _campfire_tools, _supabase_tools
    _campfire_tools = campfire_tools
    _supabase_tools = supabase_tools


@tool(
    name="get_menu_profitability",
    description="""Analyze menu profitability using Boston Matrix methodology (⭐Stars, 🧩Puzzles, 🐴Plowhorses, 🐕Dogs).

Use this tool when:
- User asks "哪些菜最赚钱？" (Which dishes are most profitable?)
- User wants menu engineering analysis
- User asks "哪些菜应该下架？" (Which dishes should be removed?)
- User wants to optimize menu for profitability

Returns: Dishes categorized by profitability and popularity with actionable insights.

Categories explained:
- ⭐ Stars (高利润+高销量): 明星菜品，重点推广
- 🧩 Puzzles (高利润+低销量): 潜力菜品，加强营销
- 🐴 Plowhorses (低利润+高销量): 走量菜品，考虑提价
- 🐕 Dogs (低利润+低销量): 问题菜品，建议下架

Example queries:
- "菜单工程分析"
- "哪些菜最值得推广？"
- "哪些菜应该调整价格？"

Returns: Complete profitability analysis with Boston Matrix categorization.""",
    input_schema={
        "start_date": str,  # Optional: Start date YYYY-MM-DD (default: 30 days ago)
        "end_date": str,    # Optional: End date YYYY-MM-DD (default: today)
        "min_quantity": int # Optional: Minimum sales to include (default: 10)
    }
)
async def get_menu_profitability_tool(args):
    """Get menu profitability Boston Matrix analysis"""
    if not _supabase_tools:
        return {
            "content": [{
                "type": "text",
                "text": "⚠️ **Supabase tools not available**"
            }]
        }


@tool(
    name="get_top_profitable_dishes",
    description="""Get top profitable dishes ranked by gross profit contribution.

Use this tool when:
- User asks "最赚钱的菜是哪些？" (What are the most profitable dishes?)
- User wants to see top revenue contributors
- User asks "哪些菜贡献最大？"

Returns: Top 10 dishes by gross profit with revenue, cost, and margin analysis.

Example queries:
- "最赚钱的10道菜"
- "哪些菜毛利最高？"
- "利润贡献排行"

Returns: Top profitable dishes with detailed profit breakdown.""",
    input_schema={
        "start_date": str,  # Optional: Start date YYYY-MM-DD
        "end_date": str,    # Optional: End date YYYY-MM-DD
        "top_n": int        # Optional: Number of dishes (default: 10)
    }
)
async def get_top_profitable_dishes_tool(args):
    """Get top profitable dishes"""
    if not _supabase_tools:
        return {"content": [{"type": "text", "text": "⚠️ **Supabase tools not available**"}]}


@tool(
    name="get_low_profit_dishes",
    description="""Get low profit dishes with actionable recommendations (potentially remove or reprice).

Use this tool when:
- User asks "哪些菜不赚钱？" (Which dishes are unprofitable?)
- User wants to optimize menu by removing low performers
- User asks "哪些菜应该下架？"

Returns: Bottom 10 dishes with recommendations (下架/提价/降成本).

Example queries:
- "最不赚钱的菜"
- "哪些菜亏损？"
- "建议下架的菜品"

Returns: Low profit dishes with specific action recommendations.""",
    input_schema={
        "start_date": str,  # Optional: Start date YYYY-MM-DD
        "end_date": str,    # Optional: End date YYYY-MM-DD
        "bottom_n": int     # Optional: Number of dishes (default: 10)
    }
)
async def get_low_profit_dishes_tool(args):
    """Get low profit dishes with recommendations"""
    if not _supabase_tools:
        return {"content": [{"type": "text", "text": "⚠️ **Supabase tools not available**"}]}


@tool(
    name="get_cost_coverage_rate",
    description="""Check cost data coverage rate - shows which % of dishes have cost information.

Use this tool when:
- User asks "成本数据完整吗？" (Is cost data complete?)
- User wants to know data quality
- User asks "有多少菜没有成本信息？"

Returns: Coverage statistics showing dishes with/without cost data.

Example queries:
- "成本数据覆盖率"
- "有多少菜缺少成本？"
- "数据完整性检查"

Returns: Coverage rate with revenue impact analysis.""",
    input_schema={
        "start_date": str,  # Optional: Start date YYYY-MM-DD
        "end_date": str     # Optional: End date YYYY-MM-DD
    }
)
async def get_cost_coverage_rate_tool(args):
    """Get cost data coverage analysis"""
    if not _supabase_tools:
        return {"content": [{"type": "text", "text": "⚠️ **Supabase tools not available**"}]}


@tool(
    name="get_dishes_missing_cost",
    description="""Get list of dishes missing cost data (prioritized by revenue impact).

Use this tool when:
- User asks "哪些菜没有成本数据？" (Which dishes lack cost data?)
- User wants to know what cost data to add first
- User asks "哪些菜需要补充成本？"

Returns: Top 20 dishes missing cost data, ordered by revenue (fix high-revenue dishes first).

Example queries:
- "哪些菜缺少成本信息？"
- "需要补充成本的菜品"
- "优先添加哪些菜的成本？"

Returns: Missing cost dishes ranked by revenue priority.""",
    input_schema={
        "start_date": str,  # Optional: Start date YYYY-MM-DD
        "end_date": str,    # Optional: End date YYYY-MM-DD
        "top_n": int        # Optional: Number of dishes (default: 20)
    }
)
async def get_dishes_missing_cost_tool(args):
    """Get dishes missing cost data"""
    if not _supabase_tools:
        return {"content": [{"type": "text", "text": "⚠️ **Supabase tools not available**"}]}


