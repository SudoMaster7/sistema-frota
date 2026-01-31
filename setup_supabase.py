"""
Setup Supabase Database - Create Tables
Run this first before migration
"""

from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

def setup_database():
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_KEY')
    
    if not url or not key:
        print("Error: SUPABASE_URL and SUPABASE_KEY must be set in .env")
        return
    
    client = create_client(url, key)
    
    print("="*60)
    print("  SUPABASE DATABASE SETUP")
    print("="*60)
    print()
    print("Connected to:", url)
    print()
    print("IMPORTANT: You need to run the schema.sql file manually in Supabase")
    print()
    print("Steps:")
    print("1. Go to https://supabase.com/dashboard/project/<your-project>/sql")
    print("2. Copy the contents of schema.sql")
    print("3. Paste and run in the SQL editor")
    print()
    print("After that, come back and run: python migrate_to_supabase.py")
    print()
    print("="*60)
    
    # Test connection
    try:
        # Try to query usuarios table to see if it exists
        response = client.table('usuarios').select('count', count='exact').execute()
        print("✓ Database tables found!")
        print(f"  Users count: {response.count}")
        return True
    except Exception as e:
        print("✗ Tables not created yet. Please run schema.sql in Supabase dashboard.")
        print(f"  Error: {e}")
        return False

if __name__ == "__main__":
    setup_database()
