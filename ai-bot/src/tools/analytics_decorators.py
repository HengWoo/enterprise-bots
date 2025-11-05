"""
Restaurant analytics Supabase RPC tools
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
    name="get_daily_revenue",
    description="""Get daily revenue summary for a specific date from the restaurant POS system.

Use this tool when:
- User asks "今天的营业额是多少" (What's today's revenue?)
- User wants to see daily sales summary
- User asks about order count or average order value
- User wants to compare revenues across different days

Returns comprehensive daily metrics including total revenue, order count, average order value, and order status breakdown.

Example queries:
- "今天的营业额是多少？"
- "昨天有多少个订单？"
- "本周一的平均订单金额是多少？"

Returns: Revenue summary with total revenue, order counts by status, and averages.""",
    input_schema={
        "target_date": str  # Optional: Date in YYYY-MM-DD format (default: today)
    }
)
async def get_daily_revenue_tool(args):
    """Get daily revenue summary"""
    if not _supabase_tools:
        return {
            "content": [{
                "type": "text",
                "text": "⚠️ **Supabase tools not available**\n\nSupabase credentials have not been configured."
            }]
        }

    try:
        # Extract parameters
        target_date = args.get('target_date')

        # Call underlying implementation
        result = _supabase_tools.get_daily_revenue(target_date=target_date)

        # Format response
        if result.get('success') and result.get('data'):
            data = result['data']
            response_text = f"📊 **{target_date or '今天'}营业额报告**\n\n"
            response_text += f"💰 总营业额: ¥{data.get('total_revenue', 0):,.2f}\n"
            response_text += f"📦 订单总数: {data.get('order_count', 0)} 单\n"
            response_text += f"📈 平均客单价: ¥{data.get('avg_order_value', 0):,.2f}\n\n"

            # Order status breakdown if available
            if data.get('by_status'):
                response_text += "**订单状态分布:**\n"
                for status, count in data['by_status'].items():
                    response_text += f"- {status}: {count} 单\n"
        else:
            response_text = f"未找到 {target_date or '今天'} 的营业数据。"

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
                "text": f"查询营业额失败：{str(e)}"
            }]
        }


@tool(
    name="get_revenue_by_zone",
    description="""Get revenue breakdown by dining zone (A区, B区, C区, etc.).

Use this tool when:
- User asks about zone performance
- User wants to compare different dining areas
- User asks "哪个区域营业额最高？" (Which zone has highest revenue?)
- User wants to analyze table utilization by zone

Returns revenue, order count, and average order value for each zone.

Example queries:
- "各个区域的营业额如何？"
- "哪个区最赚钱？"
- "A区今天有多少订单？"

Returns: Zone-by-zone revenue breakdown with rankings.""",
    input_schema={
        "start_date": str,  # Optional: Start date in YYYY-MM-DD format (default: today)
        "end_date": str  # Optional: End date in YYYY-MM-DD format (default: today)
    }
)
async def get_revenue_by_zone_tool(args):
    """Get revenue by dining zone"""
    if not _supabase_tools:
        return {
            "content": [{
                "type": "text",
                "text": "⚠️ **Supabase tools not available**"
            }]
        }

    try:
        # Extract parameters
        start_date = args.get('start_date')
        end_date = args.get('end_date')

        # Call underlying implementation
        result = _supabase_tools.get_revenue_by_zone(
            start_date=start_date,
            end_date=end_date
        )

        # Format response
        if result.get('success') and result.get('data'):
            zones = result['data']
            response_text = f"📍 **各区域营业额分析**\n\n"

            for i, zone in enumerate(zones, 1):
                response_text += f"**{i}. {zone.get('zone_name', 'Unknown')}**\n"
                response_text += f"   💰 营业额: ¥{zone.get('revenue', 0):,.2f}\n"
                response_text += f"   📦 订单数: {zone.get('order_count', 0)} 单\n"
                response_text += f"   📈 平均客单价: ¥{zone.get('avg_order_value', 0):,.2f}\n\n"
        else:
            response_text = "未找到区域营业数据。"

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
                "text": f"查询区域营业额失败：{str(e)}"
            }]
        }


@tool(
    name="get_top_dishes",
    description="""Get top selling dishes ranked by quantity sold.

Use this tool when:
- User asks "哪些菜最畅销？" (What are the best-selling dishes?)
- User wants to know popular menu items
- User asks about dish sales ranking
- User wants to analyze menu performance

Returns dish name, quantity sold, revenue generated, and order count.

Example queries:
- "今天最受欢迎的菜是什么？"
- "列出销量前10的菜品"
- "糟辣椒炒饭卖了多少份？"

Returns: Ranked list of dishes with sales metrics.""",
    input_schema={
        "start_date": str,  # Optional: Start date in YYYY-MM-DD format (default: today)
        "end_date": str,  # Optional: End date in YYYY-MM-DD format (default: today)
        "top_n": int  # Optional: Number of top dishes to return (default: 10)
    }
)
async def get_top_dishes_tool(args):
    """Get top selling dishes"""
    if not _supabase_tools:
        return {
            "content": [{
                "type": "text",
                "text": "⚠️ **Supabase tools not available**"
            }]
        }

    try:
        # Extract parameters
        start_date = args.get('start_date')
        end_date = args.get('end_date')
        top_n = args.get('top_n', 10)

        # Call underlying implementation
        result = _supabase_tools.get_top_dishes(
            start_date=start_date,
            end_date=end_date,
            top_n=top_n
        )

        # Format response
        if result.get('success') and result.get('data'):
            dishes = result['data']
            response_text = f"🏆 **销量前{len(dishes)}名菜品**\n\n"

            for i, dish in enumerate(dishes, 1):
                medal = "🥇" if i == 1 else ("🥈" if i == 2 else ("🥉" if i == 3 else f"{i}."))
                response_text += f"{medal} **{dish.get('dish_name', 'Unknown')}**\n"
                response_text += f"   销量: {dish.get('quantity_sold', 0)} 份\n"
                response_text += f"   营业额: ¥{dish.get('revenue', 0):,.2f}\n"
                response_text += f"   订单数: {dish.get('order_count', 0)} 单\n\n"
        else:
            response_text = "未找到菜品销售数据。"

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
                "text": f"查询畅销菜品失败：{str(e)}"
            }]
        }


@tool(
    name="get_station_performance",
    description="""Get kitchen station performance metrics (荤菜, 素菜, 汤, etc.).

Use this tool when:
- User asks about kitchen station workload
- User wants to see which station is busiest
- User asks "荤菜站今天做了多少道菜？"
- User wants to analyze station efficiency

Returns items cooked, revenue generated, and average price per station.

Example queries:
- "各个厨房工作站的业绩如何？"
- "荤菜站今天的营业额是多少？"
- "哪个工作站最忙？"

Returns: Station-by-station performance metrics.""",
    input_schema={
        "start_date": str,  # Optional: Start date in YYYY-MM-DD format (default: today)
        "end_date": str  # Optional: End date in YYYY-MM-DD format (default: today)
    }
)
async def get_station_performance_tool(args):
    """Get kitchen station performance"""
    if not _supabase_tools:
        return {
            "content": [{
                "type": "text",
                "text": "⚠️ **Supabase tools not available**"
            }]
        }

    try:
        # Extract parameters
        start_date = args.get('start_date')
        end_date = args.get('end_date')

        # Call underlying implementation
        result = _supabase_tools.get_station_performance(
            start_date=start_date,
            end_date=end_date
        )

        # Format response
        if result.get('success') and result.get('data'):
            stations = result['data']
            response_text = f"👨‍🍳 **厨房工作站业绩分析**\n\n"

            for station in stations:
                response_text += f"**{station.get('station_name', 'Unknown')}**\n"
                response_text += f"   出品数: {station.get('items_cooked', 0)} 道\n"
                response_text += f"   营业额: ¥{station.get('revenue', 0):,.2f}\n"
                response_text += f"   均价: ¥{station.get('avg_price', 0):,.2f}\n\n"
        else:
            response_text = "未找到工作站数据。"

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
                "text": f"查询工作站业绩失败：{str(e)}"
            }]
        }


@tool(
    name="get_quick_stats",
    description="""Get quick dashboard summary with key metrics for the day.

Use this tool when:
- User asks for a general overview or dashboard
- User wants to see today's highlights
- User asks "今天的情况怎么样？"
- User wants a quick status check

Returns key metrics including revenue, orders, top dish, busiest hour, and table status.

Example queries:
- "给我看看今天的概况"
- "今天表现怎么样？"
- "快速统计一下今天的数据"

Returns: Dashboard-style summary with 6 key metrics in Chinese.""",
    input_schema={
        "target_date": str  # Optional: Date in YYYY-MM-DD format (default: today)
    }
)
async def get_quick_stats_tool(args):
    """Get quick dashboard summary"""
    if not _supabase_tools:
        return {
            "content": [{
                "type": "text",
                "text": "⚠️ **Supabase tools not available**"
            }]
        }

    try:
        # Extract parameters
        target_date = args.get('target_date')

        # Call underlying implementation
        result = _supabase_tools.get_quick_stats(target_date=target_date)

        # Format response
        if result.get('success') and result.get('data'):
            stats = result['data']
            response_text = f"⚡ **{target_date or '今天'}快速统计**\n\n"
            response_text += f"💰 营业额: ¥{stats.get('revenue', 0):,.2f}\n"
            response_text += f"📦 订单数: {stats.get('orders', 0)} 单\n"
            response_text += f"🏆 Top菜品: {stats.get('top_dish', 'N/A')}\n"
            response_text += f"🔥 高峰时段: {stats.get('busiest_hour', 'N/A')}\n"
            response_text += f"📊 桌台状态: {stats.get('table_status', 'N/A')}\n"
        else:
            response_text = f"未找到 {target_date or '今天'} 的统计数据。"

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
                "text": f"查询快速统计失败：{str(e)}"
            }]
        }


@tool(
    name="get_hourly_revenue",
    description="""Get revenue pattern by hour of day (hourly breakdown).

Use this tool when:
- User asks "哪个时段最忙？" (Which time period is busiest?)
- User wants to see hourly sales patterns
- User asks "营业高峰是什么时候？"
- User wants to analyze peak hours

Returns: List of hours with order count, revenue, and average order value.

Example queries:
- "今天哪个时段生意最好？"
- "按小时统计今天的营业额"
- "高峰时段是几点？"

Returns: Hourly revenue breakdown with order counts.""",
    input_schema={
        "target_date": str  # Optional: Date in YYYY-MM-DD format (default: today)
    }
)
async def get_hourly_revenue_tool(args):
    """Get hourly revenue pattern"""
    if not _supabase_tools:
        return {
            "content": [{
                "type": "text",
                "text": "⚠️ **Supabase tools not available**"
            }]
        }

    try:
        # Extract parameters
        target_date = args.get('target_date')

        # Call underlying implementation
        result = _supabase_tools.get_hourly_revenue(target_date=target_date)

        # Format response
        if result.get('success') and result.get('data'):
            hours = result['data']
            response_text = f"⏰ **{target_date or '今天'}按小时营业额分析**\n\n"

            for hour_data in hours:
                hour = hour_data.get('hour', 'Unknown')
                response_text += f"**{hour}:00**\n"
                response_text += f"   订单: {hour_data.get('order_count', 0)} 单\n"
                response_text += f"   营业额: ¥{hour_data.get('revenue', 0):,.2f}\n"
                response_text += f"   均价: ¥{hour_data.get('avg_order_value', 0):,.2f}\n\n"
        else:
            response_text = f"未找到 {target_date or '今天'} 的小时数据。"

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
                "text": f"查询小时营业额失败：{str(e)}"
            }]
        }


@tool(
    name="get_table_turnover",
    description="""Get table turnover rate (orders per table) for analyzing table efficiency.

Use this tool when:
- User asks "哪个餐桌翻台率最高？" (Which table has highest turnover?)
- User wants to see table performance
- User asks "哪个区域生意最好？"
- User wants to analyze table utilization

Returns: List of tables with order count, revenue, capacity, and zone.

Example queries:
- "今天哪个餐桌最忙？"
- "各个区域的翻台率怎么样？"
- "哪些桌子利用率低？"

Returns: Table-by-table performance analysis.""",
    input_schema={
        "start_date": str,  # Optional: Start date in YYYY-MM-DD format (default: today)
        "end_date": str     # Optional: End date in YYYY-MM-DD format (default: today)
    }
)
async def get_table_turnover_tool(args):
    """Get table turnover rate"""
    if not _supabase_tools:
        return {
            "content": [{
                "type": "text",
                "text": "⚠️ **Supabase tools not available**"
            }]
        }

    try:
        # Extract parameters
        start_date = args.get('start_date')
        end_date = args.get('end_date')

        # Call underlying implementation
        result = _supabase_tools.get_table_turnover(
            start_date=start_date,
            end_date=end_date
        )

        # Format response
        if result.get('success') and result.get('data'):
            tables = result['data']
            response_text = f"🪑 **餐桌翻台率分析**\n\n"

            for table in tables[:15]:  # Show top 15 tables
                response_text += f"**{table.get('table_name', 'Unknown')}** ({table.get('zone', 'N/A')})\n"
                response_text += f"   翻台: {table.get('order_count', 0)} 次\n"
                response_text += f"   营业额: ¥{table.get('revenue', 0):,.2f}\n"
                response_text += f"   容量: {table.get('capacity', 'N/A')} 人\n\n"

            if len(tables) > 15:
                response_text += f"...还有 {len(tables) - 15} 张桌子\n"
        else:
            response_text = "未找到餐桌数据。"

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
                "text": f"查询餐桌翻台率失败：{str(e)}"
            }]
        }


@tool(
    name="get_return_analysis",
    description="""Get return/refund analysis by dish (退菜分析).

Use this tool when:
- User asks "哪些菜品退菜率高？" (Which dishes have high return rates?)
- User wants to see refund analysis
- User asks "今天有多少退菜？"
- User wants to identify problematic dishes

Returns: List of returned dishes with return count, quantity, revenue loss, and return rate.

Example queries:
- "今天退菜情况怎么样？"
- "哪道菜退得最多？"
- "退菜造成了多少损失？"

Returns: Dish-by-dish return analysis with rates and revenue impact.""",
    input_schema={
        "start_date": str,  # Optional: Start date in YYYY-MM-DD format (default: today)
        "end_date": str     # Optional: End date in YYYY-MM-DD format (default: today)
    }
)
async def get_return_analysis_tool(args):
    """Get return/refund analysis"""
    if not _supabase_tools:
        return {
            "content": [{
                "type": "text",
                "text": "⚠️ **Supabase tools not available**"
            }]
        }

    try:
        # Extract parameters
        start_date = args.get('start_date')
        end_date = args.get('end_date')

        # Call underlying implementation
        result = _supabase_tools.get_return_analysis(
            start_date=start_date,
            end_date=end_date
        )

        # Format response
        if result.get('success') and result.get('data'):
            returns = result['data']
            response_text = f"🔙 **退菜分析报告**\n\n"

            for item in returns:
                response_text += f"**{item.get('dish_name', 'Unknown')}**\n"
                response_text += f"   退菜次数: {item.get('return_count', 0)} 次\n"
                response_text += f"   退菜数量: {item.get('quantity_returned', 0)} 份\n"
                response_text += f"   损失金额: ¥{item.get('revenue_loss', 0):,.2f}\n"
                response_text += f"   退菜率: {item.get('return_rate', 0):.1f}%\n\n"
        else:
            response_text = "未找到退菜数据（这是好消息！）"

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
                "text": f"查询退菜分析失败：{str(e)}"
            }]
        }


@tool(
    name="get_order_type_distribution",
    description="""Get order type distribution (dine_in, takeout, delivery).

Use this tool when:
- User asks "堂食和外卖各占多少？" (What's the dine-in vs takeout split?)
- User wants to see order type breakdown
- User asks "外卖订单有多少？"
- User wants to analyze sales channels

Returns: List of order types with count, revenue, average order value, and percentage of total.

Example queries:
- "今天堂食和外卖的比例？"
- "外卖营业额占多少？"
- "订单类型分布"

Returns: Order type breakdown with percentages and revenue.""",
    input_schema={
        "start_date": str,  # Optional: Start date in YYYY-MM-DD format (default: today)
        "end_date": str     # Optional: End date in YYYY-MM-DD format (default: today)
    }
)
async def get_order_type_distribution_tool(args):
    """Get order type distribution"""
    if not _supabase_tools:
        return {
            "content": [{
                "type": "text",
                "text": "⚠️ **Supabase tools not available**"
            }]
        }

    try:
        # Extract parameters
        start_date = args.get('start_date')
        end_date = args.get('end_date')

        # Call underlying implementation
        result = _supabase_tools.get_order_type_distribution(
            start_date=start_date,
            end_date=end_date
        )

        # Format response
        if result.get('success') and result.get('data'):
            types = result['data']
            response_text = f"📋 **订单类型分布**\n\n"

            for order_type in types:
                type_name = order_type.get('order_type', 'Unknown')
                response_text += f"**{type_name}**\n"
                response_text += f"   订单数: {order_type.get('count', 0)} 单\n"
                response_text += f"   营业额: ¥{order_type.get('revenue', 0):,.2f}\n"
                response_text += f"   均价: ¥{order_type.get('avg_order_value', 0):,.2f}\n"
                response_text += f"   占比: {order_type.get('percentage', 0):.1f}%\n\n"
        else:
            response_text = "未找到订单类型数据。"

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
                "text": f"查询订单类型分布失败：{str(e)}"
            }]
        }


@tool(
    name="get_revenue_trend",
    description="""Get revenue trend over a date range (day-by-day breakdown for trend analysis).

Use this tool when:
- User asks "这周的营业额趋势？" (What's this week's revenue trend?)
- User wants to see multi-day comparison
- User asks "最近几天生意怎么样？"
- User wants to analyze growth or decline

This tool REQUIRES both start_date and end_date (not optional like other tools).

Returns: List of daily revenue with date, total revenue, order count, and average order value.

Example queries:
- "本周营业额走势"
- "最近7天的营业额对比"
- "10月1日到10月7日的营业额"

Returns: Day-by-day revenue trend with growth indicators.""",
    input_schema={
        "start_date": str,  # Required: Start date in YYYY-MM-DD format
        "end_date": str     # Required: End date in YYYY-MM-DD format
    }
)
async def get_revenue_trend_tool(args):
    """Get revenue trend over date range"""
    if not _supabase_tools:
        return {
            "content": [{
                "type": "text",
                "text": "⚠️ **Supabase tools not available**"
            }]
        }

    try:
        # Extract parameters (REQUIRED for this tool)
        start_date = args.get('start_date')
        end_date = args.get('end_date')

        if not start_date or not end_date:
            return {
                "content": [{
                    "type": "text",
                    "text": "❌ 错误：get_revenue_trend 需要提供 start_date 和 end_date 参数"
                }]
            }

        # Call underlying implementation
        result = _supabase_tools.get_revenue_trend(
            start_date=start_date,
            end_date=end_date
        )

        # Format response
        if result.get('success') and result.get('data'):
            days = result['data']
            response_text = f"📈 **营业额趋势分析** ({start_date} ~ {end_date})\n\n"

            for day in days:
                date = day.get('date', 'Unknown')
                response_text += f"**{date}**\n"
                response_text += f"   营业额: ¥{day.get('total_revenue', 0):,.2f}\n"
                response_text += f"   订单数: {day.get('order_count', 0)} 单\n"
                response_text += f"   均价: ¥{day.get('avg_order_value', 0):,.2f}\n"

                # Growth indicator if available
                if day.get('growth_percentage') is not None:
                    growth = day['growth_percentage']
                    arrow = "📈" if growth > 0 else ("📉" if growth < 0 else "➡️")
                    response_text += f"   {arrow} 增长: {growth:+.1f}%\n"

                response_text += "\n"
        else:
            response_text = f"未找到 {start_date} ~ {end_date} 的趋势数据。"

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
                "text": f"查询营业额趋势失败：{str(e)}"
            }]
        }


