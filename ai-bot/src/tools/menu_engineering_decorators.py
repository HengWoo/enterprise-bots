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
                "text": "⚠️ **Supabase tools not available**\n\nSupabase credentials have not been configured. Please set SUPABASE_URL and SUPABASE_KEY environment variables."
            }]
        }

    try:
        start_date = args.get("start_date")
        end_date = args.get("end_date")
        min_quantity = args.get("min_quantity", 5)

        result = _supabase_tools.get_menu_profitability(
            start_date=start_date,
            end_date=end_date,
            min_quantity=min_quantity
        )

        if result["success"] and result.get("data"):
            data = result["data"]
            response_text = "🎯 **菜单盈利能力分析（波士顿矩阵）**\n\n"

            # Group by category
            categories = {
                "stars": ("⭐ 明星菜品", "高利润+高销量，重点推广"),
                "puzzles": ("🧩 谜题菜品", "高利润+低销量，加强营销"),
                "plowhorses": ("🐴 主力菜品", "低利润+高销量，考虑提价"),
                "dogs": ("🐕 问题菜品", "低利润+低销量，建议下架")
            }

            for cat_key, (cat_name, cat_desc) in categories.items():
                dishes = data.get(cat_key, [])
                if dishes:
                    response_text += f"**{cat_name}** ({cat_desc})\n"
                    for dish in dishes[:5]:  # Show top 5 in each category
                        response_text += f"  • {dish.get('dish_name', 'Unknown')}\n"
                        response_text += f"    销量: {dish.get('quantity', 0)} | 利润: ¥{dish.get('profit', 0):,.2f}\n"
                    if len(dishes) > 5:
                        response_text += f"  ...还有 {len(dishes) - 5} 道菜\n"
                    response_text += "\n"
        else:
            response_text = f"未找到菜单数据。{result.get('message', '')}"

        return {
            "content": [{
                "type": "text",
                "text": response_text
            }]
        }
    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": f"菜单盈利分析失败：{str(e)}"
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
        return {"content": [{"type": "text", "text": "⚠️ **Supabase tools not available**\n\nSupabase credentials have not been configured. Please set SUPABASE_URL and SUPABASE_KEY environment variables."}]}

    try:
        start_date = args.get("start_date")
        end_date = args.get("end_date")
        top_n = args.get("top_n", 10)

        result = _supabase_tools.get_top_profitable_dishes(
            start_date=start_date,
            end_date=end_date,
            top_n=top_n
        )

        if result.get("success") and result.get("data"):
            dishes = result["data"]
            response_text = f"💰 **最赚钱的菜品 TOP {top_n}**\n\n"

            for i, dish in enumerate(dishes, 1):
                # Medal for top 3
                if i == 1:
                    medal = "🥇"
                elif i == 2:
                    medal = "🥈"
                elif i == 3:
                    medal = "🥉"
                else:
                    medal = f"{i}."

                response_text += f"{medal} **{dish.get('dish_name', 'Unknown')}**\n"
                response_text += f"   销量: {dish.get('quantity', 0)} 份\n"
                response_text += f"   营业额: ¥{dish.get('revenue', 0):,.2f}\n"
                response_text += f"   成本: ¥{dish.get('cost', 0):,.2f}\n"
                response_text += f"   毛利润: ¥{dish.get('profit', 0):,.2f}\n"

                # Calculate margin if we have the data
                if dish.get('revenue', 0) > 0:
                    margin = (dish.get('profit', 0) / dish.get('revenue', 1)) * 100
                    response_text += f"   毛利率: {margin:.1f}%\n"

                response_text += "\n"
        elif result.get("success"):
            response_text = f"未找到盈利菜品数据。{result.get('message', '')}"
        else:
            response_text = f"查询失败：{result.get('message', '未知错误')}"

        return {
            "content": [{
                "type": "text",
                "text": response_text
            }]
        }
    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": f"Error calling top profitable dishes tool: {str(e)}"
            }]
        }


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
        return {"content": [{"type": "text", "text": "⚠️ **Supabase tools not available**\n\nSupabase credentials have not been configured. Please set SUPABASE_URL and SUPABASE_KEY environment variables."}]}

    try:
        start_date = args.get("start_date")
        end_date = args.get("end_date")
        bottom_n = args.get("bottom_n", 10)

        result = _supabase_tools.get_low_profit_dishes(
            start_date=start_date,
            end_date=end_date,
            bottom_n=bottom_n
        )

        if result.get("success") and result.get("data"):
            dishes = result["data"]
            response_text = f"⚠️ **低利润菜品分析 (需要关注的 {bottom_n} 道菜)**\n\n"

            for i, dish in enumerate(dishes, 1):
                response_text += f"{i}. **{dish.get('dish_name', 'Unknown')}**\n"
                response_text += f"   销量: {dish.get('quantity', 0)} 份\n"
                response_text += f"   营业额: ¥{dish.get('revenue', 0):,.2f}\n"
                response_text += f"   成本: ¥{dish.get('cost', 0):,.2f}\n"
                response_text += f"   毛利润: ¥{dish.get('profit', 0):,.2f}\n"

                # Calculate margin
                if dish.get('revenue', 0) > 0:
                    margin = (dish.get('profit', 0) / dish.get('revenue', 1)) * 100
                    response_text += f"   毛利率: {margin:.1f}%\n"

                # Add recommendation
                recommendation = dish.get('recommendation', '')
                if recommendation:
                    response_text += f"   💡 建议: {recommendation}\n"
                elif dish.get('profit', 0) < 0:
                    response_text += f"   💡 建议: ❌ 亏损菜品，建议下架\n"
                elif margin < 20:
                    response_text += f"   💡 建议: 📈 利润率过低，考虑提价或降成本\n"
                else:
                    response_text += f"   💡 建议: 🔍 需要进一步分析\n"

                response_text += "\n"
        elif result.get("success"):
            response_text = f"未找到低利润菜品数据。{result.get('message', '')}"
        else:
            response_text = f"查询失败：{result.get('message', '未知错误')}"

        return {
            "content": [{
                "type": "text",
                "text": response_text
            }]
        }
    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": f"Error calling low profit dishes tool: {str(e)}"
            }]
        }


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
        return {"content": [{"type": "text", "text": "⚠️ **Supabase tools not available**\n\nSupabase credentials have not been configured. Please set SUPABASE_URL and SUPABASE_KEY environment variables."}]}

    try:
        start_date = args.get("start_date")
        end_date = args.get("end_date")

        result = _supabase_tools.get_cost_coverage_rate(
            start_date=start_date,
            end_date=end_date
        )

        if result.get("success") and result.get("data"):
            data = result["data"]
            response_text = "📊 **成本数据覆盖率分析**\n\n"

            # Coverage statistics
            total_dishes = data.get('total_dishes', 0)
            with_cost = data.get('dishes_with_cost', 0)
            without_cost = data.get('dishes_without_cost', 0)
            coverage_rate = data.get('coverage_rate', 0)

            response_text += f"**数据完整性：**\n"
            response_text += f"✅ 有成本数据: {with_cost} 道菜\n"
            response_text += f"❌ 缺少成本数据: {without_cost} 道菜\n"
            response_text += f"📈 覆盖率: {coverage_rate:.1f}%\n\n"

            # Revenue impact
            total_revenue = data.get('total_revenue', 0)
            revenue_with_cost = data.get('revenue_with_cost', 0)
            revenue_without_cost = data.get('revenue_without_cost', 0)

            if total_revenue > 0:
                revenue_coverage = (revenue_with_cost / total_revenue) * 100
                response_text += f"**营业额影响：**\n"
                response_text += f"✅ 有成本数据的菜品营业额: ¥{revenue_with_cost:,.2f}\n"
                response_text += f"❌ 无成本数据的菜品营业额: ¥{revenue_without_cost:,.2f}\n"
                response_text += f"📊 营业额覆盖率: {revenue_coverage:.1f}%\n\n"

            # Assessment
            if coverage_rate >= 80:
                response_text += "✅ **评估**: 成本数据覆盖率良好\n"
            elif coverage_rate >= 60:
                response_text += "⚠️ **评估**: 成本数据覆盖率中等，建议补充高营业额菜品的成本信息\n"
            else:
                response_text += "❌ **评估**: 成本数据覆盖率较低，影响盈利分析准确性，建议优先补充\n"

        elif result.get("success"):
            response_text = f"未找到成本覆盖率数据。{result.get('message', '')}"
        else:
            response_text = f"查询失败：{result.get('message', '未知错误')}"

        return {
            "content": [{
                "type": "text",
                "text": response_text
            }]
        }
    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": f"Error calling cost coverage rate tool: {str(e)}"
            }]
        }


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
        return {"content": [{"type": "text", "text": "⚠️ **Supabase tools not available**\n\nSupabase credentials have not been configured. Please set SUPABASE_URL and SUPABASE_KEY environment variables."}]}

    try:
        start_date = args.get("start_date")
        end_date = args.get("end_date")
        top_n = args.get("top_n", 20)

        result = _supabase_tools.get_dishes_missing_cost(
            start_date=start_date,
            end_date=end_date,
            top_n=top_n
        )

        if result.get("success") and result.get("data"):
            dishes = result["data"]
            response_text = f"⚠️ **缺少成本数据的菜品 (优先级排序 TOP {top_n})**\n\n"
            response_text += "💡 **提示**: 按营业额排序，优先补充高营业额菜品的成本数据\n\n"

            for i, dish in enumerate(dishes, 1):
                # Priority indicator
                if i <= 5:
                    priority = "🔴 高优先级"
                elif i <= 10:
                    priority = "🟡 中优先级"
                else:
                    priority = "🟢 低优先级"

                response_text += f"{i}. **{dish.get('dish_name', 'Unknown')}** ({priority})\n"
                response_text += f"   销量: {dish.get('quantity', 0)} 份\n"
                response_text += f"   营业额: ¥{dish.get('revenue', 0):,.2f}\n"
                response_text += f"   平均单价: ¥{dish.get('avg_price', 0):,.2f}\n"

                # Impact assessment
                revenue = dish.get('revenue', 0)
                if revenue > 10000:
                    response_text += f"   📊 影响: 高营业额菜品，急需补充成本数据\n"
                elif revenue > 5000:
                    response_text += f"   📊 影响: 中等营业额菜品，建议补充成本数据\n"
                else:
                    response_text += f"   📊 影响: 营业额较低，可稍后补充\n"

                response_text += "\n"

            # Summary
            total_missing_revenue = sum(dish.get('revenue', 0) for dish in dishes)
            response_text += f"**汇总：**\n"
            response_text += f"缺少成本数据的菜品总营业额: ¥{total_missing_revenue:,.2f}\n"

        elif result.get("success"):
            response_text = "✅ 所有菜品都有成本数据，无需补充。"
        else:
            response_text = f"查询失败：{result.get('message', '未知错误')}"

        return {
            "content": [{
                "type": "text",
                "text": response_text
            }]
        }
    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": f"Error calling dishes missing cost tool: {str(e)}"
            }]
        }


