#!/usr/bin/env python3
"""
Migration: Add user_color column to games table

This migration adds a user_color column to track whether the authenticated user
was playing white ('w') or black ('b') in each game.
It's idempotent and safe to run multiple times.
"""
import os
import sys
import logging
from sqlalchemy import create_engine, text, MetaData

def run_migration(database_url):
    """Run the user_color migration"""
    engine = create_engine(database_url)

    with engine.connect() as conn:
        # Start transaction
        trans = conn.begin()

        try:
            print("🔍 Checking if user_color column exists in games table...")

            # Check if user_color column exists
            result = conn.execute(text("""
                SELECT COUNT(*) FROM information_schema.columns
                WHERE table_name = 'games' AND column_name = 'user_color'
            """))

            column_exists = result.scalar() > 0

            if column_exists:
                print("✅ user_color column already exists - migration already applied")
                trans.commit()
                return True

            print("➕ Adding user_color column to games table...")

            # Add the user_color column
            conn.execute(text("""
                ALTER TABLE games
                ADD COLUMN user_color VARCHAR(1)
            """))

            # For existing games, we can't automatically determine user color
            # This will need to be set when users edit their games or we implement a UI for it
            print("ℹ️  user_color column added - existing games will need manual assignment")

            # Commit transaction
            trans.commit()
            print("✅ Migration completed successfully!")
            return True

        except Exception as e:
            trans.rollback()
            print(f"❌ Migration failed: {str(e)}")
            return False

if __name__ == "__main__":
    # Get database URL from environment or command line
    database_url = os.environ.get('DATABASE_URL')

    if len(sys.argv) > 1:
        database_url = sys.argv[1]

    if not database_url:
        print("❌ Please provide DATABASE_URL environment variable or as argument")
        sys.exit(1)

    print(f"🚀 Running user_color migration...")
    print(f"📊 Database: {database_url.split('@')[1] if '@' in database_url else 'localhost'}")

    success = run_migration(database_url)
    sys.exit(0 if success else 1)