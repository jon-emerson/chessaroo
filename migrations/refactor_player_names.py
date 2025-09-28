#!/usr/bin/env python3
"""
Migration: Complete database reset with user-centric schema

This migration:
1. Drops all existing tables
2. Recreates tables with the correct user-centric schema
3. Creates indexes for performance

It's safe to run multiple times and will reset the database to a clean state.
"""
import os
import sys
import logging
from sqlalchemy import create_engine, text, MetaData

def run_migration(database_url):
    """Run the complete database reset migration"""
    engine = create_engine(database_url)

    with engine.connect() as conn:
        # Start transaction
        trans = conn.begin()

        try:
            print("🗑️  Dropping all existing tables...")

            # Drop tables in correct order (games first due to foreign key)
            tables_to_drop = ['games', 'users']
            for table in tables_to_drop:
                try:
                    conn.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE"))
                    print(f"   ✓ Dropped {table} table")
                except Exception as e:
                    print(f"   ⚠️  Note: {table} table didn't exist or couldn't be dropped: {e}")

            print("📋 Creating users table...")
            conn.execute(text("""
                CREATE TABLE users (
                    user_id VARCHAR(20) PRIMARY KEY,
                    username VARCHAR(100) NOT NULL UNIQUE,
                    password_hash VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))

            print("🎮 Creating games table with user-centric schema...")
            conn.execute(text("""
                CREATE TABLE games (
                    id SERIAL PRIMARY KEY,
                    user_id VARCHAR(20) REFERENCES users(user_id),
                    user_color VARCHAR(1) CHECK (user_color IN ('w', 'b')),
                    title VARCHAR(255) DEFAULT 'Untitled Game',
                    opponent_name VARCHAR(100),
                    result VARCHAR(10) DEFAULT '*',
                    status VARCHAR(20) DEFAULT 'active',
                    starting_fen TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))

            print("📊 Creating indexes for performance...")
            conn.execute(text("""
                CREATE INDEX idx_games_user_id ON games(user_id)
            """))
            conn.execute(text("""
                CREATE INDEX idx_games_status ON games(status)
            """))
            conn.execute(text("""
                CREATE INDEX idx_games_created_at ON games(created_at)
            """))

            # Commit transaction
            trans.commit()
            print("✅ Database reset completed successfully!")
            print("🎯 All tables recreated with user-centric schema")
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