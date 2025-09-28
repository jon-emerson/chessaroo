#!/usr/bin/env python3
"""
Migration: Refactor player names to user-centric model

This migration:
1. Drops the white_player column
2. Renames black_player to opponent_name
3. Updates existing data to preserve opponent names based on user_color

It's idempotent and safe to run multiple times.
"""
import os
import sys
import logging
from sqlalchemy import create_engine, text, MetaData

def run_migration(database_url):
    """Run the player names refactor migration"""
    engine = create_engine(database_url)

    with engine.connect() as conn:
        # Start transaction
        trans = conn.begin()

        try:
            print("🔍 Checking if migration has already been applied...")

            # Check if white_player column still exists
            result = conn.execute(text("""
                SELECT COUNT(*) FROM information_schema.columns
                WHERE table_name = 'games' AND column_name = 'white_player'
            """))

            white_player_exists = result.scalar() > 0

            # Check if opponent_name column exists
            result = conn.execute(text("""
                SELECT COUNT(*) FROM information_schema.columns
                WHERE table_name = 'games' AND column_name = 'opponent_name'
            """))

            opponent_name_exists = result.scalar() > 0

            if not white_player_exists and opponent_name_exists:
                print("✅ Migration already applied - white_player dropped and opponent_name exists")
                trans.commit()
                return True

            if not white_player_exists or not opponent_name_exists:
                print("❌ Unexpected state - partial migration detected")
                trans.rollback()
                return False

            print("➡️  Starting player names refactor...")

            # Step 1: Add opponent_name column
            print("➕ Adding opponent_name column...")
            conn.execute(text("""
                ALTER TABLE games
                ADD COLUMN opponent_name VARCHAR(100)
            """))

            # Step 2: Migrate data based on user_color
            print("📋 Migrating existing player data...")

            # For users who played white, opponent is black_player
            result = conn.execute(text("""
                UPDATE games
                SET opponent_name = black_player
                WHERE user_color = 'w' AND black_player IS NOT NULL
            """))
            white_users_updated = result.rowcount

            # For users who played black, opponent is white_player
            result = conn.execute(text("""
                UPDATE games
                SET opponent_name = white_player
                WHERE user_color = 'b' AND white_player IS NOT NULL
            """))
            black_users_updated = result.rowcount

            # For games without user_color, try to preserve black_player as opponent
            result = conn.execute(text("""
                UPDATE games
                SET opponent_name = black_player
                WHERE user_color IS NULL AND black_player IS NOT NULL
            """))
            null_color_updated = result.rowcount

            print(f"✏️  Updated {white_users_updated} games where user played white")
            print(f"✏️  Updated {black_users_updated} games where user played black")
            print(f"✏️  Updated {null_color_updated} games with null user_color")

            # Step 3: Drop the old columns
            print("🗑️  Dropping white_player column...")
            conn.execute(text("""
                ALTER TABLE games DROP COLUMN white_player
            """))

            print("🗑️  Dropping black_player column...")
            conn.execute(text("""
                ALTER TABLE games DROP COLUMN black_player
            """))

            # Commit transaction
            trans.commit()
            print("✅ Player names refactor completed successfully!")
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

    print(f"🚀 Running player names refactor migration...")
    print(f"📊 Database: {database_url.split('@')[1] if '@' in database_url else 'localhost'}")

    success = run_migration(database_url)
    sys.exit(0 if success else 1)