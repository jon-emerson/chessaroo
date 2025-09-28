#!/usr/bin/env python3
"""
Database migration script for Chessaroo
Drops all existing tables and recreates them from scratch using current schemas
"""

import os
import sys
import logging
from flask import Flask
from models import db, Game, Move, User

def create_migration_app():
    """Create a minimal Flask app for database operations"""
    app = Flask(__name__)

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s: %(message)s',
        stream=sys.stdout
    )

    # Database configuration - using PostgreSQL
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        # Local development fallback
        db_host = os.environ.get('DB_HOST', 'localhost')
        db_port = os.environ.get('DB_PORT', '5432')
        db_name = os.environ.get('DB_NAME', 'chessaroo')
        db_user = os.environ.get('DB_USER', 'chessaroo_user')
        db_password = os.environ.get('DB_PASSWORD', 'chessaroo_pass')
        database_url = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'

    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Configure SQLAlchemy engine
    connect_args = {'connect_timeout': 10}

    # Only require SSL for production (AWS RDS), not for local development
    if 'amazonaws.com' in database_url:
        connect_args['sslmode'] = 'require'
    else:
        connect_args['sslmode'] = 'prefer'

    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        'pool_recycle': 3600,
        'pool_size': 10,
        'max_overflow': 20,
        'connect_args': connect_args
    }

    # Initialize database
    db.init_app(app)

    return app

def drop_all_tables():
    """Drop all existing tables"""
    try:
        logging.info("🗑️  Dropping all existing tables...")

        # Get all table names
        inspector = db.inspect(db.engine)
        table_names = inspector.get_table_names()

        if table_names:
            logging.info(f"Found tables to drop: {', '.join(table_names)}")

            # Drop all tables
            db.drop_all()
            logging.info("✅ All tables dropped successfully")
        else:
            logging.info("No existing tables found")

    except Exception as e:
        logging.error(f"❌ Error dropping tables: {str(e)}")
        raise

def create_all_tables():
    """Create all tables from current schema definitions"""
    try:
        logging.info("🏗️  Creating tables from current schemas...")

        # Create all tables
        db.create_all()

        # Verify tables were created
        inspector = db.inspect(db.engine)
        table_names = inspector.get_table_names()

        if table_names:
            logging.info(f"✅ Tables created successfully: {', '.join(sorted(table_names))}")
        else:
            raise Exception("No tables were created")

    except Exception as e:
        logging.error(f"❌ Error creating tables: {str(e)}")
        raise

def create_sample_data():
    """Create sample data for testing"""
    try:
        logging.info("🌱 Creating sample data...")

        # Create a sample user
        sample_user = User(username='testuser', password='testpass123')
        db.session.add(sample_user)
        db.session.commit()

        logging.info(f"✅ Created sample user: {sample_user.user_id} ({sample_user.username})")

        # Create a sample game
        sample_game = Game(
            title='Sample Chess Game',
            opponent_name='Claire',
            user_id=sample_user.user_id,
            user_color='w',
            starting_fen='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
        )
        db.session.add(sample_game)
        db.session.commit()

        # Update the title to include the game ID
        sample_game.title = f'Sample Chess Game #{sample_game.id}'
        db.session.commit()

        logging.info(f"✅ Created sample game: {sample_game.id} ({sample_game.title})")

        # Create some sample moves
        sample_moves = [
            Move(game_id=sample_game.id, move_number=1, color='w',
                 algebraic_notation='e4',
                 fen='rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1'),
            Move(game_id=sample_game.id, move_number=1, color='b',
                 algebraic_notation='e5',
                 fen='rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq e6 0 2'),
            Move(game_id=sample_game.id, move_number=2, color='w',
                 algebraic_notation='Nf3',
                 fen='rnbqkbnr/pppp1ppp/8/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq - 1 2'),
        ]

        for move in sample_moves:
            db.session.add(move)

        db.session.commit()
        logging.info(f"✅ Created {len(sample_moves)} sample moves")

    except Exception as e:
        logging.error(f"❌ Error creating sample data: {str(e)}")
        db.session.rollback()
        raise

def verify_migration():
    """Verify the migration was successful"""
    try:
        logging.info("🔍 Verifying migration...")

        # Check table structure
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()

        expected_tables = ['users', 'games', 'moves']
        for table in expected_tables:
            if table not in tables:
                raise Exception(f"Expected table '{table}' not found")

        # Check data counts
        user_count = User.query.count()
        game_count = Game.query.count()
        move_count = Move.query.count()

        logging.info(f"📊 Database contents:")
        logging.info(f"   Users: {user_count}")
        logging.info(f"   Games: {game_count}")
        logging.info(f"   Moves: {move_count}")

        # Verify relationships work
        sample_game = Game.query.first()
        if sample_game:
            logging.info(f"   Sample game moves: {sample_game.moves.count()}")
            logging.info(f"   Sample game owner: {sample_game.owner.username if sample_game.owner else 'None'}")

        logging.info("✅ Migration verification successful")

    except Exception as e:
        logging.error(f"❌ Migration verification failed: {str(e)}")
        raise

def main():
    """Main migration function"""
    try:
        logging.info("🚀 Starting database migration...")

        # Create Flask app
        app = create_migration_app()

        with app.app_context():
            # Step 1: Drop all tables
            drop_all_tables()

            # Step 2: Create tables from current schemas
            create_all_tables()

            # Step 3: Create sample data
            create_sample_data()

            # Step 4: Verify migration
            verify_migration()

        logging.info("🎉 Database migration completed successfully!")
        logging.info("You can now restart your application to use the fresh database schema.")

    except Exception as e:
        logging.error(f"💥 Migration failed: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()