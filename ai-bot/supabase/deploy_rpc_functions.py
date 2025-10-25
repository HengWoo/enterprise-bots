#!/usr/bin/env python3
"""
Deploy RPC Functions to Supabase
Reads SQL migration files and executes them on Supabase PostgreSQL
"""

import os
import sys
from pathlib import Path

# Try to import psycopg2 for direct PostgreSQL connection
try:
    import psycopg2
    from psycopg2 import sql
    HAS_PSYCOPG2 = True
except ImportError:
    HAS_PSYCOPG2 = False
    print("⚠️  psycopg2 not installed, trying alternative method...")

# Fallback: use supabase-py
from supabase import create_client, Client

def deploy_via_psycopg2(connection_string: str, sql_file: Path):
    """Deploy SQL using direct PostgreSQL connection"""
    print(f"\n📦 Deploying via psycopg2 (PostgreSQL direct connection)")
    print(f"   File: {sql_file.name}")
    print("-" * 80)

    try:
        # Read SQL file
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()

        # Connect to database
        print("🔌 Connecting to Supabase PostgreSQL...")
        conn = psycopg2.connect(connection_string)
        conn.autocommit = True
        cursor = conn.cursor()

        # Execute SQL
        print("⚙️  Executing SQL migration...")
        cursor.execute(sql_content)

        # Get function count
        cursor.execute("""
            SELECT count(*)
            FROM pg_proc p
            JOIN pg_namespace n ON p.pronamespace = n.oid
            WHERE n.nspname = 'public'
            AND p.proname LIKE 'get_%'
        """)
        function_count = cursor.fetchone()[0]

        cursor.close()
        conn.close()

        print(f"✅ Successfully deployed! Total RPC functions: {function_count}")
        return True

    except Exception as e:
        print(f"❌ Error deploying via psycopg2: {e}")
        return False


def deploy_via_supabase_client(supabase_url: str, supabase_key: str, sql_file: Path):
    """Deploy SQL using Supabase Python client"""
    print(f"\n📦 Deploying via Supabase REST API")
    print(f"   File: {sql_file.name}")
    print("-" * 80)

    try:
        # Read SQL file
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()

        # Create Supabase client
        supabase: Client = create_client(supabase_url, supabase_key)

        # Try to execute via RPC (requires exec_sql function to exist)
        print("⚙️  Attempting to execute SQL via Supabase RPC...")

        # Split SQL into individual statements
        statements = [s.strip() for s in sql_content.split(';') if s.strip()]

        print(f"📝 Found {len(statements)} SQL statements")

        for i, statement in enumerate(statements, 1):
            if not statement:
                continue

            # Skip comments and empty lines
            if statement.startswith('--') or statement.startswith('/*'):
                continue

            print(f"   Executing statement {i}/{len(statements)}...")

            try:
                # Try to use rpc to execute SQL
                result = supabase.rpc('exec_sql', {'query': statement}).execute()
                print(f"   ✅ Statement {i} executed")
            except Exception as e:
                # If exec_sql doesn't exist, we can't proceed
                if "function public.exec_sql() does not exist" in str(e).lower():
                    print(f"\n❌ Error: The exec_sql() RPC function doesn't exist in your Supabase project.")
                    print("   You need to either:")
                    print("   1. Install psycopg2: pip install psycopg2-binary")
                    print("   2. Or manually run the SQL in Supabase SQL Editor")
                    return False
                else:
                    print(f"   ⚠️  Warning on statement {i}: {e}")

        print(f"✅ Successfully deployed {len(statements)} statements!")
        return True

    except Exception as e:
        print(f"❌ Error deploying via Supabase client: {e}")
        return False


def main():
    print("=" * 80)
    print("🚀 Supabase RPC Function Deployment Tool")
    print("=" * 80)

    # Get Supabase credentials
    supabase_url = os.environ.get('SUPABASE_URL')
    supabase_key = os.environ.get('SUPABASE_SERVICE_ROLE_KEY') or os.environ.get('SUPABASE_KEY')

    # PostgreSQL connection string (for direct connection)
    # Format: postgresql://postgres:[PASSWORD]@[HOST]:[PORT]/postgres
    postgres_connection = os.environ.get('SUPABASE_DB_URL') or os.environ.get('DATABASE_URL')

    if not supabase_url or not supabase_key:
        print("❌ Missing Supabase credentials!")
        print("   Set SUPABASE_URL and SUPABASE_KEY environment variables")
        sys.exit(1)

    # Get SQL file to deploy
    if len(sys.argv) > 1:
        sql_file = Path(sys.argv[1])
    else:
        # Default to menu engineering migration
        script_dir = Path(__file__).parent
        sql_file = script_dir / "migrations" / "20251023_create_menu_engineering_rpc.sql"

    if not sql_file.exists():
        print(f"❌ SQL file not found: {sql_file}")
        sys.exit(1)

    print(f"\n📄 SQL File: {sql_file}")
    print(f"   Size: {sql_file.stat().st_size} bytes")
    print(f"   Supabase URL: {supabase_url}")

    # Try deployment methods in order of preference
    deployed = False

    # Method 1: Direct PostgreSQL connection (most reliable)
    if HAS_PSYCOPG2 and postgres_connection:
        deployed = deploy_via_psycopg2(postgres_connection, sql_file)
    elif HAS_PSYCOPG2 and not postgres_connection:
        print("\n⚠️  psycopg2 is installed but SUPABASE_DB_URL is not set")
        print("   To use direct PostgreSQL connection, set SUPABASE_DB_URL")
        print("   Example: postgresql://postgres:PASSWORD@db.xxx.supabase.co:5432/postgres")

    # Method 2: Supabase REST API (fallback)
    if not deployed:
        deployed = deploy_via_supabase_client(supabase_url, supabase_key, sql_file)

    # Final result
    print("\n" + "=" * 80)
    if deployed:
        print("✅ Deployment completed successfully!")
        print("=" * 80)
        sys.exit(0)
    else:
        print("❌ Deployment failed!")
        print("\n💡 Manual deployment instructions:")
        print("   1. Go to https://supabase.com/dashboard")
        print("   2. Select your project")
        print("   3. Go to SQL Editor")
        print(f"   4. Copy and paste the contents of: {sql_file}")
        print("   5. Click 'Run' to execute")
        print("=" * 80)
        sys.exit(1)


if __name__ == "__main__":
    main()
