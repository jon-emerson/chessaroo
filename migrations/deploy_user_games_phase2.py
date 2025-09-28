#!/usr/bin/env python3
"""
PHASE 2 Deployment migration: Make user_id NOT NULL

This migration adds the NOT NULL constraint to the user_id column.
Run this AFTER Phase 1 has been deployed and is stable.
It's idempotent and safe to run multiple times.
"""
import os
import sys
import logging
from sqlalchemy import create_engine, text, MetaData

def run_migration(database_url):
    """Run the Phase 2 user_id migration"""
    engine = create_engine(database_url)

    with engine.connect() as conn:
        # Start transaction
        trans = conn.begin()

        try:
            print("🔍 Checking if user_id column is already NOT NULL...")

            # Check if user_id column is already NOT NULL
            result = conn.execute(text("""
                SELECT is_nullable FROM information_schema.columns
                WHERE table_name = 'games' AND column_name = 'user_id'
            """))

            row = result.fetchone()
            if not row:
                print("❌ user_id column does not exist - run Phase 1 first")
                trans.rollback()
                return False

            is_nullable = row[0] == 'YES'

            if not is_nullable:
                print("✅ user_id column is already NOT NULL - migration already applied")
                trans.commit()
                return True

            # Check if any games have NULL user_id
            print("🔍 Checking for games with NULL user_id...")
            result = conn.execute(text("""
                SELECT COUNT(*) FROM games WHERE user_id IS NULL
            """))

            null_count = result.scalar()
            if null_count > 0:
                print(f"❌ Found {null_count} games with NULL user_id - cannot proceed")
                print("   Please ensure all games have been assigned to users")
                trans.rollback()
                return False

            print("✅ All games have user_id assigned")

            # Make user_id NOT NULL
            print("🔗 Adding NOT NULL constraint to user_id column...")
            conn.execute(text("""
                ALTER TABLE games
                ALTER COLUMN user_id SET NOT NULL
            """))

            # Commit transaction
            trans.commit()
            print("✅ Phase 2 migration completed successfully!")
            return True

        except Exception as e:
            trans.rollback()
            print(f"❌ Phase 2 migration failed: {str(e)}")
            return False

if __name__ == "__main__":
    # Get database URL from environment or command line
    database_url = os.environ.get('DATABASE_URL')

    if len(sys.argv) > 1:
        database_url = sys.argv[1]

    if not database_url:
        print("❌ Please provide DATABASE_URL environment variable or as argument")
        sys.exit(1)

    print(f"🚀 Running user-games Phase 2 migration...")
    print(f"📊 Database: {database_url.split('@')[1] if '@' in database_url else 'localhost'}")

    success = run_migration(database_url)
    sys.exit(0 if success else 1)