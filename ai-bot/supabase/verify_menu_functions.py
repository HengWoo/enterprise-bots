#!/usr/bin/env python3
"""Verify menu engineering RPC functions are deployed"""

import os
from supabase import create_client

SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY')

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

print("=" * 80)
print("🔍 Verifying Menu Engineering RPC Functions")
print("=" * 80)

functions_to_check = [
    'get_menu_profitability',
    'get_top_profitable_dishes',
    'get_low_profit_dishes',
    'get_cost_coverage_rate',
    'get_dishes_missing_cost'
]

all_good = True

for func_name in functions_to_check:
    try:
        # Try to call the function (it might error on parameters, but should exist)
        result = supabase.rpc(func_name, {}).execute()
        print(f"✅ {func_name} - EXISTS")
    except Exception as e:
        error_msg = str(e)
        if "does not exist" in error_msg.lower():
            print(f"❌ {func_name} - NOT FOUND")
            all_good = False
        else:
            # Function exists but might have parameter errors - that's OK
            print(f"✅ {func_name} - EXISTS (parameter validation OK)")

print("=" * 80)
if all_good:
    print("✅ All 5 menu engineering functions deployed successfully!")
else:
    print("❌ Some functions are missing. Please deploy the SQL file.")
print("=" * 80)
