#!/usr/bin/env python3
"""
Inspect Product Cost Tables in Supabase
Checks product_bom table and product_cost_analysis view
"""

import os
from supabase import create_client, Client

# Get Supabase credentials from environment
SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY') or os.environ.get('SUPABASE_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Missing Supabase credentials!")
    print("Set SUPABASE_URL and SUPABASE_KEY environment variables")
    exit(1)

# Create Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

print("=" * 80)
print("🔍 Inspecting Product Cost Tables in Supabase")
print("=" * 80)
print()

# 1. List all tables and views
print("📋 Step 1: Listing all tables and views...")
print("-" * 80)
try:
    # Query information_schema to list all tables
    result = supabase.rpc('exec_sql', {
        'query': """
        SELECT
            table_name,
            table_type
        FROM information_schema.tables
        WHERE table_schema = 'public'
        ORDER BY table_type, table_name;
        """
    }).execute()

    print(f"Found {len(result.data)} tables/views:\n")
    for row in result.data:
        icon = "📊" if row['table_type'] == 'VIEW' else "🗂️"
        print(f"{icon} {row['table_name']} ({row['table_type']})")
    print()
except Exception as e:
    print(f"⚠️ Could not list tables using RPC, trying direct query...")
    # Alternative: Just try to query the tables directly
    print()

# 2. Inspect product_bom table
print("=" * 80)
print("🗂️  Step 2: Inspecting product_bom table")
print("-" * 80)
try:
    # Get table structure
    result = supabase.table('product_bom').select('*').limit(0).execute()
    print("✅ Table exists!")
    print("\nTrying to get sample data...")

    # Get sample records
    sample = supabase.table('product_bom').select('*').limit(5).execute()

    if sample.data:
        print(f"\n📝 Sample data ({len(sample.data)} records):")
        print("-" * 80)

        # Show column names from first record
        if sample.data:
            print(f"\n🔑 Columns: {', '.join(sample.data[0].keys())}\n")

            # Pretty print first 3 records
            for i, record in enumerate(sample.data[:3], 1):
                print(f"Record #{i}:")
                for key, value in record.items():
                    print(f"  {key}: {value}")
                print()
    else:
        print("⚠️ Table exists but has no data")

except Exception as e:
    print(f"❌ Error accessing product_bom: {e}")
    print()

# 3. Inspect product_cost_analysis view
print("=" * 80)
print("📊 Step 3: Inspecting product_cost_analysis view")
print("-" * 80)
try:
    # Get view structure
    result = supabase.table('product_cost_analysis').select('*').limit(0).execute()
    print("✅ View exists!")
    print("\nTrying to get sample data...")

    # Get sample records
    sample = supabase.table('product_cost_analysis').select('*').limit(5).execute()

    if sample.data:
        print(f"\n📝 Sample data ({len(sample.data)} records):")
        print("-" * 80)

        # Show column names from first record
        if sample.data:
            print(f"\n🔑 Columns: {', '.join(sample.data[0].keys())}\n")

            # Pretty print first 3 records
            for i, record in enumerate(sample.data[:3], 1):
                print(f"Record #{i}:")
                for key, value in record.items():
                    # Format money values
                    if 'cost' in key.lower() or 'price' in key.lower() or 'margin' in key.lower():
                        if isinstance(value, (int, float)):
                            print(f"  {key}: ¥{value:.2f}" if value else f"  {key}: {value}")
                        else:
                            print(f"  {key}: {value}")
                    else:
                        print(f"  {key}: {value}")
                print()
    else:
        print("⚠️ View exists but has no data")

except Exception as e:
    print(f"❌ Error accessing product_cost_analysis: {e}")
    print()

# 4. Try to understand the relationship
print("=" * 80)
print("🔗 Step 4: Understanding data relationship")
print("-" * 80)
try:
    # Query to see if we can join sales data with cost data
    print("\n📊 Checking how to join sales data with product costs...")

    # Get a few item names from order_items
    items_result = supabase.table('rsp_order_items').select('item_name').limit(5).execute()

    if items_result.data:
        print(f"\nSample dish names from rsp_order_items:")
        for item in items_result.data[:5]:
            print(f"  - {item['item_name']}")

    print("\nNow checking product_cost_analysis for matching products...")

    # Try to get matching products
    cost_result = supabase.table('product_cost_analysis').select('*').limit(10).execute()

    if cost_result.data:
        print(f"\nSample products from product_cost_analysis:")
        for item in cost_result.data[:5]:
            # Try to find name field
            name_field = None
            for key in ['name', 'product_name', 'item_name', 'dish_name']:
                if key in item:
                    name_field = key
                    break

            if name_field:
                print(f"  - {item[name_field]}")
            else:
                print(f"  - (No name field found, keys: {list(item.keys())})")

    print("\n💡 Next step: Determine the join key between rsp_order_items.item_name and product_cost_analysis")

except Exception as e:
    print(f"⚠️ Could not analyze relationship: {e}")

print()
print("=" * 80)
print("✅ Inspection complete!")
print("=" * 80)
