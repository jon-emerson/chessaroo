import os
import logging
import sys
from flask import Flask, jsonify, abort, request, session
from flask_cors import CORS
from models import db, Game, Move, User
import chess
import chess.pgn
from io import StringIO
from functools import wraps

def create_app():
    app = Flask(__name__)

    # Configure logging
    if not app.debug and not app.testing:
        # Production logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s %(levelname)s %(name)s: %(message)s',
            stream=sys.stdout
        )
        app.logger.setLevel(logging.INFO)
        app.logger.info('Chessaroo application startup')

    # Session configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

    # Database configuration - using PostgreSQL
    # Use environment variable for database URL, with fallback for local development
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

    # Configure SQLAlchemy engine for production resilience
    connect_args = {'connect_timeout': 10}

    # Only require SSL for production (AWS RDS), not for local development
    if 'amazonaws.com' in database_url:
        connect_args['sslmode'] = 'require'
    else:
        # Local development - disable SSL requirement
        connect_args['sslmode'] = 'prefer'

    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,  # Verify connections before use
        'pool_recycle': 3600,   # Recycle connections every hour
        'pool_size': 10,        # Connection pool size
        'max_overflow': 20,     # Max extra connections beyond pool_size
        'connect_args': connect_args
    }

    # Log database configuration (without credentials)
    if database_url:
        # Extract host from database URL for logging (without password)
        if 'localhost' in database_url:
            app.logger.info("Database: Connected to local PostgreSQL")
        elif 'amazonaws.com' in database_url:
            app.logger.info("Database: Connected to AWS RDS PostgreSQL")
        else:
            app.logger.info("Database: Connected to PostgreSQL")
    else:
        app.logger.warning("Database: No DATABASE_URL provided, using fallback configuration")

    # Initialize database
    db.init_app(app)

    # Enable CORS for React frontend
    CORS(app, supports_credentials=True)

    # Authentication decorator
    def login_required(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                return jsonify({'error': 'Authentication required'}), 401
            return f(*args, **kwargs)
        return decorated_function

    def get_current_user():
        """Get the current authenticated user"""
        if 'user_id' not in session:
            return None
        return User.query.filter_by(user_id=session['user_id']).first()

    # Authentication routes
    @app.route('/api/auth/register', methods=['POST'])
    def register():
        """Register a new user"""
        try:
            data = request.get_json()
            password = data.get('password', '')
            username = data.get('username', '').strip()

            # Validation
            if not password or not username:
                return jsonify({'error': 'Password and username are required'}), 400

            if len(password) < 6:
                return jsonify({'error': 'Password must be at least 6 characters long'}), 400

            if len(username) < 3:
                return jsonify({'error': 'Username must be at least 3 characters long'}), 400

            if len(username) > 100:
                return jsonify({'error': 'Username must be 100 characters or less'}), 400

            # Check if username already exists
            existing_username = User.query.filter_by(username=username).first()
            if existing_username:
                return jsonify({'error': 'Username is already taken'}), 409

            # Create new user
            user = User(username=username, password=password)
            db.session.add(user)
            db.session.commit()

            # Log them in immediately
            session['user_id'] = user.user_id

            return jsonify({
                'message': 'User registered successfully',
                'user': user.to_dict()
            }), 201

        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Registration failed for username {username}: {str(e)}", exc_info=True)
            return jsonify({'error': 'Registration failed'}), 500

    @app.route('/api/auth/login', methods=['POST'])
    def login():
        """Authenticate user login"""
        try:
            data = request.get_json()
            username = data.get('username', '').strip()
            password = data.get('password', '')

            if not username or not password:
                return jsonify({'error': 'Username and password are required'}), 400

            # Find user by username
            user = User.query.filter_by(username=username).first()
            if not user or not user.check_password(password):
                return jsonify({'error': 'Invalid username or password'}), 401

            # Update last login timestamp
            from datetime import datetime
            user.last_login = datetime.utcnow()
            db.session.commit()

            # Create session
            session['user_id'] = user.user_id

            return jsonify({
                'message': 'Login successful',
                'user': user.to_dict()
            }), 200

        except Exception as e:
            app.logger.error(f"Login failed for username {username}: {str(e)}", exc_info=True)
            return jsonify({'error': 'Login failed'}), 500

    @app.route('/api/auth/logout', methods=['POST'])
    def logout():
        """Log out current user"""
        session.clear()
        return jsonify({'message': 'Logged out successfully'}), 200

    @app.route('/api/auth/me')
    def get_current_user_info():
        """Get current user information"""
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Not authenticated'}), 401

        return jsonify({
            'user': user.to_dict(),
            'authenticated': True
        }), 200

    @app.route('/api/auth/update-profile', methods=['PUT'])
    @login_required
    def update_profile():
        """Update user profile information"""
        try:
            user = get_current_user()
            data = request.get_json()

            username = data.get('username', '').strip()
            email = data.get('email', '').strip().lower()

            # Validation
            if not username or not email:
                return jsonify({'error': 'Username and email are required'}), 400

            if len(username) < 3:
                return jsonify({'error': 'Username must be at least 3 characters long'}), 400

            if len(username) > 50:
                return jsonify({'error': 'Username must be 50 characters or less'}), 400

            # Check if username is taken by another user
            if username != user.username:
                existing_username = User.query.filter_by(username=username).first()
                if existing_username:
                    return jsonify({'error': 'Username is already taken'}), 409

            # Check if email is taken by another user
            if email != user.email:
                existing_email = User.query.filter_by(email=email).first()
                if existing_email:
                    return jsonify({'error': 'Email is already in use'}), 409

            # Update user information
            user.username = username
            user.email = email
            db.session.commit()

            return jsonify({
                'message': 'Profile updated successfully',
                'user': user.to_dict()
            }), 200

        except Exception as e:
            db.session.rollback()
            return jsonify({'error': 'Failed to update profile'}), 500

    @app.route('/api/auth/change-password', methods=['PUT'])
    @login_required
    def change_password():
        """Change user password"""
        try:
            user = get_current_user()
            data = request.get_json()

            current_password = data.get('current_password', '')
            new_password = data.get('new_password', '')

            # Validation
            if not current_password or not new_password:
                return jsonify({'error': 'Current password and new password are required'}), 400

            if len(new_password) < 6:
                return jsonify({'error': 'New password must be at least 6 characters long'}), 400

            # Verify current password
            if not user.check_password(current_password):
                return jsonify({'error': 'Current password is incorrect'}), 401

            # Update password
            from werkzeug.security import generate_password_hash
            user.password_hash = generate_password_hash(new_password, method='pbkdf2:sha256')
            db.session.commit()

            return jsonify({'message': 'Password changed successfully'}), 200

        except Exception as e:
            db.session.rollback()
            return jsonify({'error': 'Failed to change password'}), 500

    @app.route('/api/games')
    @login_required
    def list_games():
        """API endpoint to get list of games for the authenticated user"""
        user = get_current_user()
        games = Game.query.filter_by(user_id=user.user_id).order_by(Game.created_at.desc()).limit(10).all()
        games_data = []
        for game in games:
            games_data.append({
                'id': game.id,
                'title': game.title,
                'user_color': game.user_color,
                'opponent_name': game.opponent_name,
                'status': game.status,
                'result': game.result,
                'created_at': game.created_at.isoformat(),
                'move_count': game.moves.count()
            })

        return jsonify({'games': games_data})

    @app.route('/api/game/<int:game_id>/moves')
    @login_required
    def get_game_moves(game_id):
        """API endpoint to get game moves as JSON for authenticated user's games only"""
        user = get_current_user()
        game = Game.query.filter_by(id=game_id, user_id=user.user_id).first()
        if not game:
            return jsonify({'error': 'Game not found'}), 404

        moves = game.moves.order_by(Move.move_number, Move.color.desc()).all()

        moves_data = []
        for move in moves:
            moves_data.append({
                'moveNumber': move.move_number,
                'color': move.color,
                'algebraic': move.algebraic_notation,
                'fen': move.fen
            })

        return jsonify({
            'gameId': game.id,
            'title': game.title,
            'userColor': game.user_color,
            'opponentName': game.opponent_name,
            'startingFen': game.starting_fen,
            'currentFen': game.get_current_fen(),
            'moves': moves_data
        })

    @app.route('/api/create-sample-game')
    @login_required
    def create_sample_game():
        """Create a sample game for testing for the authenticated user"""
        user = get_current_user()
        # Create a new game (user plays as white)
        game = Game(
            title='Sample Chess Game',
            opponent_name='Claire',
            user_id=user.user_id,
            user_color='w',
            starting_fen='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
        )
        db.session.add(game)
        db.session.commit()

        # Update the title to include the game ID
        game.title = f'Sample Chess Game #{game.id}'
        db.session.commit()

        # Add some sample moves (Scholar's Mate opening)
        sample_moves = [
            (1, 'w', 'e4', 'rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1'),
            (1, 'b', 'e5', 'rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq e6 0 2'),
            (2, 'w', 'Bc4', 'rnbqkbnr/pppp1ppp/8/4p3/2B1P3/8/PPPP1PPP/RNBQK1NR b KQkq - 1 2'),
            (2, 'b', 'Nc6', 'r1bqkbnr/pppp1ppp/2n5/4p3/2B1P3/8/PPPP1PPP/RNBQK1NR w KQkq - 2 3'),
            (3, 'w', 'Qh5', 'r1bqkbnr/pppp1ppp/2n5/4p2Q/2B1P3/8/PPPP1PPP/RNB1K1NR b KQkq - 3 3'),
            (3, 'b', 'Nf6', 'r1bqkb1r/pppp1ppp/2n2n2/4p2Q/2B1P3/8/PPPP1PPP/RNB1K1NR w KQkq - 4 4'),
            (4, 'w', 'Qxf7#', 'r1bqkb1r/pppp1Qpp/2n2n2/4p3/2B1P3/8/PPPP1PPP/RNB1K1NR b KQkq - 0 4')
        ]

        for move_num, color, notation, fen in sample_moves:
            move = Move(
                game_id=game.id,
                move_number=move_num,
                color=color,
                algebraic_notation=notation,
                fen=fen
            )
            db.session.add(move)

        game.result = '1-0'  # White wins
        game.status = 'completed'
        db.session.commit()

        return jsonify({'gameId': game.id, 'message': 'Sample game created successfully'})

    # Note: Database migrations are now handled by migrations/deploy_user_games.py
    # This should be run separately during deployment

    def init_database():
        """Initialize database with tables and sample data"""
        try:
            app.logger.info("Database: Creating tables...")
            db.create_all()
            app.logger.info("Database: Tables created successfully")

            # Check if we already have games (avoid duplicate sample games)
            existing_games = Game.query.count()
            app.logger.info(f"Database: Found {existing_games} existing games")
            if existing_games == 0:
                # Only create sample game if there are users (since games now require user_id)
                user_count = User.query.count()
                if user_count > 0:
                    first_user = User.query.first()
                    app.logger.info("Database: Creating sample game...")
                    game = Game(
                        title='Sample Chess Game',
                        opponent_name='Claire',
                        user_id=first_user.user_id,
                        user_color='w',
                        starting_fen='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
                    )
                    db.session.add(game)
                    db.session.commit()

                    # Add sample moves (Scholar's Mate opening)
                    sample_moves = [
                        (1, 'w', 'e4', 'rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1'),
                        (1, 'b', 'e5', 'rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq e6 0 2'),
                        (2, 'w', 'Bc4', 'rnbqkbnr/pppp1ppp/8/4p3/2B1P3/8/PPPP1PPP/RNBQK1NR b KQkq - 1 2'),
                        (2, 'b', 'Nc6', 'r1bqkbnr/pppp1ppp/2n5/4p3/2B1P3/8/PPPP1PPP/RNBQK1NR w KQkq - 2 3'),
                        (3, 'w', 'Qh5', 'r1bqkbnr/pppp1ppp/2n5/4p2Q/2B1P3/8/PPPP1PPP/RNB1K1NR b KQkq - 3 3'),
                        (3, 'b', 'Nf6', 'r1bqkb1r/pppp1ppp/2n2n2/4p2Q/2B1P3/8/PPPP1PPP/RNB1K1NR w KQkq - 4 4'),
                        (4, 'w', 'Qxf7#', 'r1bqkb1r/pppp1Qpp/2n2n2/4p3/2B1P3/8/PPPP1PPP/RNB1K1NR b KQkq - 0 4')
                    ]

                    for move_num, color, notation, fen in sample_moves:
                        move = Move(
                            game_id=game.id,
                            move_number=move_num,
                            color=color,
                            algebraic_notation=notation,
                            fen=fen
                        )
                        db.session.add(move)

                    game.result = '1-0'  # White wins
                    game.status = 'completed'
                    db.session.commit()
                    app.logger.info("Database: Sample game created successfully")
                else:
                    app.logger.info("Database: No users found, skipping sample game creation")
        except Exception as e:
            app.logger.error(f"Database initialization failed: {str(e)}", exc_info=True)
            raise

    # Initialize database and create sample data
    with app.app_context():
        init_database()

    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)