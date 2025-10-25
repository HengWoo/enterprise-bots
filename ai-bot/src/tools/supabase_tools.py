"""
Supabase Tools for Operations Data Management
Provides tools for the Operations Assistant bot to query and update operations data
"""

import os
from typing import Optional, Dict, List, Any
from supabase import create_client, Client


class SupabaseTools:
    """
    Supabase tools for operations data management.

    Provides methods to:
    - Query operations data from Supabase tables
    - Update operations metrics and records
    - Generate summary reports from operations data
    """

    def __init__(self):
        """Initialize Supabase client from environment variables"""
        self.supabase_url = os.environ.get("SUPABASE_URL")
        self.supabase_key = os.environ.get("SUPABASE_KEY")

        if not self.supabase_url or not self.supabase_key:
            raise ValueError(
                "Supabase credentials not found. Please set SUPABASE_URL and SUPABASE_KEY environment variables."
            )

        self.client: Client = create_client(self.supabase_url, self.supabase_key)

    def query_operations_data(
        self,
        table: str,
        filters: Optional[Dict[str, Any]] = None,
        columns: Optional[str] = "*",
        limit: int = 100,
        order_by: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Query operations data from a Supabase table.

        Args:
            table: Table name to query (e.g., 'operations_metrics', 'projects', 'tasks')
            filters: Optional dict of column-value pairs to filter by
                    Example: {'status': 'active', 'priority': 'high'}
            columns: Columns to select (default "*" for all)
            limit: Maximum number of records to return (default 100)
            order_by: Column name to order by (prefix with '-' for descending)
                     Example: '-created_at' for newest first

        Returns:
            Dict with keys:
                - success: bool
                - data: List of records
                - count: Number of records returned
                - message: Status message

        Example:
            # Get all active projects
            query_operations_data(
                table='projects',
                filters={'status': 'active'},
                limit=50,
                order_by='-updated_at'
            )
        """
        try:
            # Start query
            query = self.client.table(table).select(columns)

            # Apply filters if provided
            if filters:
                for column, value in filters.items():
                    query = query.eq(column, value)

            # Apply ordering if provided
            if order_by:
                if order_by.startswith('-'):
                    # Descending order
                    query = query.order(order_by[1:], desc=True)
                else:
                    # Ascending order
                    query = query.order(order_by)

            # Apply limit
            query = query.limit(limit)

            # Execute query
            response = query.execute()

            return {
                "success": True,
                "data": response.data,
                "count": len(response.data),
                "message": f"Retrieved {len(response.data)} record(s) from {table}"
            }

        except Exception as e:
            return {
                "success": False,
                "data": [],
                "count": 0,
                "message": f"Error querying {table}: {str(e)}"
            }

    def update_operations_data(
        self,
        table: str,
        record_id: Any,
        data: Dict[str, Any],
        id_column: str = "id"
    ) -> Dict[str, Any]:
        """
        Update an operations data record in Supabase.

        Args:
            table: Table name to update
            record_id: ID of the record to update
            data: Dict of column-value pairs to update
                 Example: {'status': 'completed', 'completion_date': '2025-10-20'}
            id_column: Name of the ID column (default 'id')

        Returns:
            Dict with keys:
                - success: bool
                - data: Updated record
                - message: Status message

        Example:
            # Mark a task as completed
            update_operations_data(
                table='tasks',
                record_id=123,
                data={'status': 'completed', 'completed_at': '2025-10-20T10:30:00Z'}
            )
        """
        try:
            # Update record
            response = self.client.table(table).update(data).eq(id_column, record_id).execute()

            if response.data:
                return {
                    "success": True,
                    "data": response.data[0],
                    "message": f"Successfully updated record {record_id} in {table}"
                }
            else:
                return {
                    "success": False,
                    "data": None,
                    "message": f"No record found with {id_column}={record_id} in {table}"
                }

        except Exception as e:
            return {
                "success": False,
                "data": None,
                "message": f"Error updating {table}: {str(e)}"
            }

    def get_operations_summary(
        self,
        date_range: Optional[Dict[str, str]] = None,
        metrics: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Generate a summary report of operations data.

        Args:
            date_range: Optional dict with 'start_date' and 'end_date' (YYYY-MM-DD format)
                       Example: {'start_date': '2025-10-01', 'end_date': '2025-10-20'}
            metrics: Optional list of metric names to include in summary
                    Example: ['tasks', 'projects', 'revenue']

        Returns:
            Dict with keys:
                - success: bool
                - summary: Dict of summary data organized by metric/category
                - period: Date range covered
                - message: Status message

        Example:
            # Get summary for October 2025
            get_operations_summary(
                date_range={'start_date': '2025-10-01', 'end_date': '2025-10-31'},
                metrics=['tasks', 'projects']
            )
        """
        try:
            summary = {}

            # Default to last 30 days if no date range provided
            if not date_range:
                from datetime import datetime, timedelta
                end_date = datetime.now()
                start_date = end_date - timedelta(days=30)
                date_range = {
                    'start_date': start_date.strftime('%Y-%m-%d'),
                    'end_date': end_date.strftime('%Y-%m-%d')
                }

            # Query different metrics based on requested metrics
            # This is a template - actual implementation depends on your Supabase schema

            if not metrics or 'tasks' in metrics:
                # Example: Get task summary
                tasks_response = self.client.table('tasks').select('status').gte(
                    'created_at', date_range['start_date']
                ).lte('created_at', date_range['end_date']).execute()

                tasks_data = tasks_response.data
                summary['tasks'] = {
                    'total': len(tasks_data),
                    'by_status': self._group_by_field(tasks_data, 'status')
                }

            if not metrics or 'projects' in metrics:
                # Example: Get project summary
                projects_response = self.client.table('projects').select('status').gte(
                    'created_at', date_range['start_date']
                ).lte('created_at', date_range['end_date']).execute()

                projects_data = projects_response.data
                summary['projects'] = {
                    'total': len(projects_data),
                    'by_status': self._group_by_field(projects_data, 'status')
                }

            return {
                "success": True,
                "summary": summary,
                "period": f"{date_range['start_date']} to {date_range['end_date']}",
                "message": f"Generated operations summary for period: {date_range['start_date']} to {date_range['end_date']}"
            }

        except Exception as e:
            return {
                "success": False,
                "summary": {},
                "period": None,
                "message": f"Error generating summary: {str(e)}"
            }

    def _group_by_field(self, records: List[Dict], field: str) -> Dict[str, int]:
        """Helper method to group records by a field and count occurrences"""
        groups = {}
        for record in records:
            value = record.get(field, 'unknown')
            groups[value] = groups.get(value, 0) + 1
        return groups

    def aggregate_operations_data(
        self,
        table: str,
        aggregations: Dict[str, str],
        group_by: Optional[List[str]] = None,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None,
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        Query operations data with aggregations (SUM, COUNT, AVG, etc.)

        Args:
            table: Table name to query
            aggregations: Dict of {column: function} to aggregate
                         Example: {'total': 'sum', 'id': 'count'}
                         Functions: sum, count, avg, min, max
            group_by: Optional list of columns to group by
                     Example: ['station_id', 'status']
            filters: Optional dict of column-value pairs to filter by
            order_by: Optional column to order by (use aggregated column name)
            limit: Maximum number of groups to return (default 100)

        Returns:
            Dict with keys:
                - success: bool
                - data: List of aggregated results
                - count: Number of groups returned
                - message: Status message

        Examples:
            # Total revenue by table
            aggregate_operations_data(
                table='rsp_orders',
                aggregations={'total': 'sum', 'id': 'count'},
                group_by=['table_id'],
                filters={'status': 'completed'}
            )

            # Average order value
            aggregate_operations_data(
                table='rsp_orders',
                aggregations={'total': 'avg'},
                filters={'status': 'completed'}
            )

            # Top selling dishes
            aggregate_operations_data(
                table='rsp_order_items',
                aggregations={'quantity': 'sum', 'total_price': 'sum'},
                group_by=['item_name'],
                order_by='-quantity',  # Descending
                limit=10
            )
        """
        try:
            # Build select string with aggregations
            select_parts = []

            # Add group by columns first
            if group_by:
                select_parts.extend(group_by)

            # Add aggregations using PostgREST syntax
            for column, function in aggregations.items():
                # PostgREST format: column.function()
                select_parts.append(f"{column}.{function}()")

            select_string = ','.join(select_parts)

            # Start query
            query = self.client.table(table).select(select_string)

            # Apply filters if provided
            if filters:
                for column, value in filters.items():
                    query = query.eq(column, value)

            # Apply ordering if provided
            if order_by:
                if order_by.startswith('-'):
                    # Descending order
                    query = query.order(order_by[1:], desc=True)
                else:
                    # Ascending order
                    query = query.order(order_by)

            # Apply limit
            query = query.limit(limit)

            # Execute query
            response = query.execute()

            return {
                "success": True,
                "data": response.data,
                "count": len(response.data),
                "message": f"Aggregated {len(response.data)} result(s) from {table}"
            }

        except Exception as e:
            return {
                "success": False,
                "data": [],
                "count": 0,
                "message": f"Error aggregating {table}: {str(e)}"
            }

    # ========================================================================
    # Restaurant Analytics RPC Functions
    # ========================================================================

    def get_daily_revenue(self, target_date: Optional[str] = None) -> Dict[str, Any]:
        """
        Get daily revenue summary for a specific date.

        Args:
            target_date: Date in YYYY-MM-DD format (default: today)

        Returns:
            Dict with:
                - total_revenue: Total completed revenue
                - order_count: Total orders
                - avg_order_value: Average order value
                - completed_orders: Number of completed orders
                - pending_orders: Number of pending orders
                - cancelled_orders: Number of cancelled orders
        """
        try:
            params = {}
            if target_date:
                params['target_date'] = target_date

            response = self.client.rpc('get_daily_revenue', params).execute()

            if response.data:
                return {
                    "success": True,
                    "data": response.data[0],
                    "message": f"Retrieved daily revenue for {target_date or 'today'}"
                }
            else:
                return {
                    "success": False,
                    "data": None,
                    "message": "No data returned"
                }

        except Exception as e:
            return {
                "success": False,
                "data": None,
                "message": f"Error getting daily revenue: {str(e)}"
            }

    def get_revenue_by_zone(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, Any]:
        """
        Get revenue breakdown by dining zone.

        Args:
            start_date: Start date in YYYY-MM-DD format (default: today)
            end_date: End date in YYYY-MM-DD format (default: today)

        Returns:
            List of zones with revenue, order count, and average order value
        """
        try:
            params = {}
            if start_date:
                params['start_date'] = start_date
            if end_date:
                params['end_date'] = end_date

            response = self.client.rpc('get_revenue_by_zone', params).execute()

            return {
                "success": True,
                "data": response.data,
                "count": len(response.data),
                "message": f"Retrieved revenue by zone for {start_date or 'today'} to {end_date or 'today'}"
            }

        except Exception as e:
            return {
                "success": False,
                "data": [],
                "count": 0,
                "message": f"Error getting revenue by zone: {str(e)}"
            }

    def get_top_dishes(self, start_date: Optional[str] = None, end_date: Optional[str] = None, top_n: int = 10) -> Dict[str, Any]:
        """
        Get top selling dishes by quantity.

        Args:
            start_date: Start date in YYYY-MM-DD format (default: today)
            end_date: End date in YYYY-MM-DD format (default: today)
            top_n: Number of top dishes to return (default: 10)

        Returns:
            List of dishes with total quantity, revenue, and order count
        """
        try:
            params = {'top_n': top_n}
            if start_date:
                params['start_date'] = start_date
            if end_date:
                params['end_date'] = end_date

            response = self.client.rpc('get_top_dishes', params).execute()

            return {
                "success": True,
                "data": response.data,
                "count": len(response.data),
                "message": f"Retrieved top {top_n} dishes for {start_date or 'today'} to {end_date or 'today'}"
            }

        except Exception as e:
            return {
                "success": False,
                "data": [],
                "count": 0,
                "message": f"Error getting top dishes: {str(e)}"
            }

    def get_station_performance(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, Any]:
        """
        Get kitchen station performance metrics.

        Args:
            start_date: Start date in YYYY-MM-DD format (default: today)
            end_date: End date in YYYY-MM-DD format (default: today)

        Returns:
            List of stations with item count, revenue, and average price
        """
        try:
            params = {}
            if start_date:
                params['start_date'] = start_date
            if end_date:
                params['end_date'] = end_date

            response = self.client.rpc('get_station_performance', params).execute()

            return {
                "success": True,
                "data": response.data,
                "count": len(response.data),
                "message": f"Retrieved station performance for {start_date or 'today'} to {end_date or 'today'}"
            }

        except Exception as e:
            return {
                "success": False,
                "data": [],
                "count": 0,
                "message": f"Error getting station performance: {str(e)}"
            }

    def get_hourly_revenue(self, target_date: Optional[str] = None) -> Dict[str, Any]:
        """
        Get revenue pattern by hour of day.

        Args:
            target_date: Date in YYYY-MM-DD format (default: today)

        Returns:
            List of hours with order count, revenue, and average order value
        """
        try:
            params = {}
            if target_date:
                params['target_date'] = target_date

            response = self.client.rpc('get_hourly_revenue', params).execute()

            return {
                "success": True,
                "data": response.data,
                "count": len(response.data),
                "message": f"Retrieved hourly revenue for {target_date or 'today'}"
            }

        except Exception as e:
            return {
                "success": False,
                "data": [],
                "count": 0,
                "message": f"Error getting hourly revenue: {str(e)}"
            }

    def get_table_turnover(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, Any]:
        """
        Get table turnover rate (orders per table).

        Args:
            start_date: Start date in YYYY-MM-DD format (default: today)
            end_date: End date in YYYY-MM-DD format (default: today)

        Returns:
            List of tables with order count, revenue, and capacity
        """
        try:
            params = {}
            if start_date:
                params['start_date'] = start_date
            if end_date:
                params['end_date'] = end_date

            response = self.client.rpc('get_table_turnover', params).execute()

            return {
                "success": True,
                "data": response.data,
                "count": len(response.data),
                "message": f"Retrieved table turnover for {start_date or 'today'} to {end_date or 'today'}"
            }

        except Exception as e:
            return {
                "success": False,
                "data": [],
                "count": 0,
                "message": f"Error getting table turnover: {str(e)}"
            }

    def get_return_analysis(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, Any]:
        """
        Get return/refund analysis by dish.

        Args:
            start_date: Start date in YYYY-MM-DD format (default: today)
            end_date: End date in YYYY-MM-DD format (default: today)

        Returns:
            List of returned dishes with return count, quantity, revenue loss, and return rate
        """
        try:
            params = {}
            if start_date:
                params['start_date'] = start_date
            if end_date:
                params['end_date'] = end_date

            response = self.client.rpc('get_return_analysis', params).execute()

            return {
                "success": True,
                "data": response.data,
                "count": len(response.data),
                "message": f"Retrieved return analysis for {start_date or 'today'} to {end_date or 'today'}"
            }

        except Exception as e:
            return {
                "success": False,
                "data": [],
                "count": 0,
                "message": f"Error getting return analysis: {str(e)}"
            }

    def get_order_type_distribution(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, Any]:
        """
        Get order type distribution (dine_in, takeout, delivery).

        Args:
            start_date: Start date in YYYY-MM-DD format (default: today)
            end_date: End date in YYYY-MM-DD format (default: today)

        Returns:
            List of order types with count, revenue, and percentage of total
        """
        try:
            params = {}
            if start_date:
                params['start_date'] = start_date
            if end_date:
                params['end_date'] = end_date

            response = self.client.rpc('get_order_type_distribution', params).execute()

            return {
                "success": True,
                "data": response.data,
                "count": len(response.data),
                "message": f"Retrieved order type distribution for {start_date or 'today'} to {end_date or 'today'}"
            }

        except Exception as e:
            return {
                "success": False,
                "data": [],
                "count": 0,
                "message": f"Error getting order type distribution: {str(e)}"
            }

    def get_revenue_trend(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """
        Get revenue trend over a date range (day-by-day breakdown).

        Args:
            start_date: Start date in YYYY-MM-DD format (required)
            end_date: End date in YYYY-MM-DD format (required)

        Returns:
            List of daily revenue with date, total revenue, order count, and average order value
        """
        try:
            params = {
                'start_date': start_date,
                'end_date': end_date
            }

            response = self.client.rpc('get_revenue_trend', params).execute()

            return {
                "success": True,
                "data": response.data,
                "count": len(response.data),
                "message": f"Retrieved revenue trend from {start_date} to {end_date}"
            }

        except Exception as e:
            return {
                "success": False,
                "data": [],
                "count": 0,
                "message": f"Error getting revenue trend: {str(e)}"
            }

    def get_quick_stats(self, target_date: Optional[str] = None) -> Dict[str, Any]:
        """
        Get quick dashboard summary (today's key metrics).

        Args:
            target_date: Date in YYYY-MM-DD format (default: today)

        Returns:
            List of key metrics with values and descriptions in Chinese
        """
        try:
            params = {}
            if target_date:
                params['target_date'] = target_date

            response = self.client.rpc('get_quick_stats', params).execute()

            return {
                "success": True,
                "data": response.data,
                "count": len(response.data),
                "message": f"Retrieved quick stats for {target_date or 'today'}"
            }

        except Exception as e:
            return {
                "success": False,
                "data": [],
                "count": 0,
                "message": f"Error getting quick stats: {str(e)}"
            }

    # ============================================================================
    # Menu Engineering Analytics (Boston Matrix Analysis)
    # ============================================================================

    def get_menu_profitability(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        min_quantity: int = 10
    ) -> Dict[str, Any]:
        """
        Get menu profitability analysis using Boston Matrix methodology.

        Args:
            start_date: Start date in YYYY-MM-DD format (default: 30 days ago)
            end_date: End date in YYYY-MM-DD format (default: today)
            min_quantity: Minimum quantity sold to include dish (default: 10)

        Returns:
            List of dishes categorized as Stars/Puzzles/Plowhorses/Dogs
        """
        try:
            params = {'min_quantity': min_quantity}
            if start_date:
                params['start_date'] = start_date
            if end_date:
                params['end_date'] = end_date

            response = self.client.rpc('get_menu_profitability', params).execute()

            return {
                "success": True,
                "data": response.data,
                "count": len(response.data),
                "message": f"Retrieved menu profitability analysis ({len(response.data)} dishes)"
            }

        except Exception as e:
            return {
                "success": False,
                "data": [],
                "count": 0,
                "message": f"Error getting menu profitability: {str(e)}"
            }

    def get_top_profitable_dishes(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        top_n: int = 10
    ) -> Dict[str, Any]:
        """
        Get top profitable dishes by gross profit.

        Args:
            start_date: Start date in YYYY-MM-DD format (default: 30 days ago)
            end_date: End date in YYYY-MM-DD format (default: today)
            top_n: Number of top dishes to return (default: 10)

        Returns:
            List of top profitable dishes with revenue, cost, and profit
        """
        try:
            params = {'top_n': top_n}
            if start_date:
                params['start_date'] = start_date
            if end_date:
                params['end_date'] = end_date

            response = self.client.rpc('get_top_profitable_dishes', params).execute()

            return {
                "success": True,
                "data": response.data,
                "count": len(response.data),
                "message": f"Retrieved top {len(response.data)} profitable dishes"
            }

        except Exception as e:
            return {
                "success": False,
                "data": [],
                "count": 0,
                "message": f"Error getting top profitable dishes: {str(e)}"
            }

    def get_low_profit_dishes(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        bottom_n: int = 10
    ) -> Dict[str, Any]:
        """
        Get low profit dishes with actionable recommendations.

        Args:
            start_date: Start date in YYYY-MM-DD format (default: 30 days ago)
            end_date: End date in YYYY-MM-DD format (default: today)
            bottom_n: Number of bottom dishes to return (default: 10)

        Returns:
            List of low profit dishes with recommendations
        """
        try:
            params = {'bottom_n': bottom_n}
            if start_date:
                params['start_date'] = start_date
            if end_date:
                params['end_date'] = end_date

            response = self.client.rpc('get_low_profit_dishes', params).execute()

            return {
                "success": True,
                "data": response.data,
                "count": len(response.data),
                "message": f"Retrieved {len(response.data)} low profit dishes"
            }

        except Exception as e:
            return {
                "success": False,
                "data": [],
                "count": 0,
                "message": f"Error getting low profit dishes: {str(e)}"
            }

    def get_cost_coverage_rate(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get cost data coverage rate analysis.

        Args:
            start_date: Start date in YYYY-MM-DD format (default: 30 days ago)
            end_date: End date in YYYY-MM-DD format (default: today)

        Returns:
            Coverage statistics showing % of dishes with cost data
        """
        try:
            params = {}
            if start_date:
                params['start_date'] = start_date
            if end_date:
                params['end_date'] = end_date

            response = self.client.rpc('get_cost_coverage_rate', params).execute()

            return {
                "success": True,
                "data": response.data[0] if response.data else {},
                "message": f"Retrieved cost coverage analysis"
            }

        except Exception as e:
            return {
                "success": False,
                "data": {},
                "message": f"Error getting cost coverage rate: {str(e)}"
            }

    def get_dishes_missing_cost(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        top_n: int = 20
    ) -> Dict[str, Any]:
        """
        Get dishes that are missing cost data (prioritized by revenue).

        Args:
            start_date: Start date in YYYY-MM-DD format (default: 30 days ago)
            end_date: End date in YYYY-MM-DD format (default: today)
            top_n: Number of dishes to return (default: 20)

        Returns:
            List of dishes missing cost data, ordered by revenue
        """
        try:
            params = {'top_n': top_n}
            if start_date:
                params['start_date'] = start_date
            if end_date:
                params['end_date'] = end_date

            response = self.client.rpc('get_dishes_missing_cost', params).execute()

            return {
                "success": True,
                "data": response.data,
                "count": len(response.data),
                "message": f"Retrieved {len(response.data)} dishes missing cost data"
            }

        except Exception as e:
            return {
                "success": False,
                "data": [],
                "count": 0,
                "message": f"Error getting dishes missing cost: {str(e)}"
            }
