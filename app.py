import os
import logging
import sys
import hmac
from datetime import datetime
from zoneinfo import ZoneInfo
from flask import Flask, jsonify, request, session
from dotenv import load_dotenv
from flask_cors import CORS
from flask_migrate import Migrate
from models import db, Game, Move, User
import chess
import chess.pgn
from io import StringIO
from functools import wraps
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired


load_dotenv()
load_dotenv('.env.local', override=True)


PT_ZONE = ZoneInfo('America/Los_Angeles')


def _ensure_container_runtime():
    """Ensure the backend only runs inside the Docker environment."""
    if os.environ.get('ALLOW_NON_CONTAINER') == '1':
        return
    if os.environ.get('CI'):
        return
    if os.path.exists('/.dockerenv') or os.environ.get('RUNNING_IN_CONTAINER') == '1':
        return
    raise RuntimeError(
        'Chessaroo backend detected a non-container environment. Start services via '
        '`docker compose up` (or set ALLOW_NON_CONTAINER=1 if you intentionally bypass this check).'
    )


migrate = Migrate()

# Set deployment timestamp when server starts (Pacific Time)
DEPLOYMENT_TIME = datetime.now(tz=PT_ZONE)

def create_app():
    _ensure_container_runtime()
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
        db_host = os.environ.get('DB_HOST', '127.0.0.1')
        db_port = os.environ.get('DB_PORT', '5432')
        db_name = os.environ.get('DB_NAME', 'chessaroo')
        db_user = os.environ.get('DB_USER', 'chessaroo_user')
        db_password = os.environ.get('DB_PASSWORD', 'chessaroo_pass')
        database_url = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'

    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Configure SQLAlchemy engine for production resilience
    connect_args = {}
    if database_url.startswith('postgresql'):
        connect_args['connect_timeout'] = 10
        if 'amazonaws.com' in database_url:
            connect_args['sslmode'] = 'require'

    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,  # Verify connections before use
        'pool_recycle': 3600,   # Recycle connections every hour
        'pool_size': 10,        # Connection pool size
        'max_overflow': 20,     # Max extra connections beyond pool_size
        'connect_args': connect_args
    }

    # Application environment + admin password configuration
    app_env = os.environ.get('APP_ENV')
    if not app_env:
        flask_env = os.environ.get('FLASK_ENV') or app.config.get('ENV')
        if flask_env:
            app_env = flask_env
        elif app.debug:
            app_env = 'development'
        else:
            app_env = 'production'

    app.config['APP_ENV'] = app_env.lower()
    app.config['ADMIN_MASTER_PASSWORD'] = os.environ.get('ADMIN_MASTER_PASSWORD')
    app.config['ADMIN_MASTER_PASSWORD_DEV'] = os.environ.get('ADMIN_MASTER_PASSWORD_DEV')
    app.config.setdefault('ADMIN_SESSION_MAX_AGE', int(os.environ.get('ADMIN_SESSION_MAX_AGE', '3600')))
    app.config.setdefault('ADMIN_SESSION_COOKIE_NAME', os.environ.get('ADMIN_SESSION_COOKIE_NAME', 'chessaroo_admin_session'))

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
    migrate.init_app(app, db)

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

    def get_admin_password():
        env = app.config.get('APP_ENV', 'production')
        if env in ('production', 'prod'):
            return app.config.get('ADMIN_MASTER_PASSWORD')
        return app.config.get('ADMIN_MASTER_PASSWORD_DEV')

    def get_admin_serializer():
        secret = app.config['SECRET_KEY']
        salt = 'chessaroo-admin-cookie'
        return URLSafeTimedSerializer(secret_key=secret, salt=salt)

    def set_admin_cookie(response):
        serializer = get_admin_serializer()
        token = serializer.dumps({'ts': datetime.utcnow().isoformat()})
        response.set_cookie(
            app.config['ADMIN_SESSION_COOKIE_NAME'],
            token,
            max_age=app.config['ADMIN_SESSION_MAX_AGE'],
            httponly=True,
            secure=app.config.get('SESSION_COOKIE_SECURE', False),
            samesite='Strict',
        )
        return response

    def clear_admin_cookie(response):
        response.delete_cookie(app.config['ADMIN_SESSION_COOKIE_NAME'])
        return response

    def admin_authenticated():
        token = request.cookies.get(app.config['ADMIN_SESSION_COOKIE_NAME'])
        if not token:
            return False
        serializer = get_admin_serializer()
        try:
            serializer.loads(token, max_age=app.config['ADMIN_SESSION_MAX_AGE'])
            return True
        except (BadSignature, SignatureExpired):
            return False

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
            email = data.get('email', '').strip().lower()

            # Validation
            if not password or not username or not email:
                return jsonify({'error': 'Password, username, and email are required'}), 400

            if len(password) < 6:
                return jsonify({'error': 'Password must be at least 6 characters long'}), 400

            if len(username) < 3:
                return jsonify({'error': 'Username must be at least 3 characters long'}), 400

            if len(username) > 100:
                return jsonify({'error': 'Username must be 100 characters or less'}), 400

            # Basic email validation
            if '@' not in email or '.' not in email.split('@')[-1]:
                return jsonify({'error': 'Please enter a valid email address'}), 400

            # Check if username already exists
            existing_username = User.query.filter_by(username=username).first()
            if existing_username:
                return jsonify({'error': 'Username is already taken'}), 409

            # Check if email already exists
            existing_email = User.query.filter_by(email=email).first()
            if existing_email:
                return jsonify({'error': 'Email is already registered'}), 409

            # Create new user
            user = User(username=username, email=email, password=password)
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

    # Database migrations are managed via Alembic/Flask-Migrate (use `flask db upgrade`)

    @app.route('/api/admin/login', methods=['POST'])
    def admin_login():
        """Authenticate admin access using master password independent of user auth."""
        data = request.get_json(silent=True) or {}
        password = data.get('password', '')
        master_password = get_admin_password()

        if not master_password:
            app.logger.error('Admin login attempted without configured master password')
            return jsonify({'error': 'Admin master password is not configured'}), 500

        if not password:
            return jsonify({'error': 'Password is required'}), 400

        if not hmac.compare_digest(password, master_password):
            return jsonify({'error': 'Invalid master password'}), 401

        response = jsonify({'message': 'Admin authentication successful'})
        return set_admin_cookie(response)

    @app.route('/api/admin/logout', methods=['POST'])
    def admin_logout():
        """Clear admin authentication state."""
        response = jsonify({'message': 'Admin logged out'})
        return clear_admin_cookie(response)

    @app.route('/api/admin/users', methods=['GET'])
    def admin_list_users():
        """Return all users for admin view."""
        if not admin_authenticated():
            return jsonify({'error': 'Admin authentication required'}), 401
        users = User.query.order_by(User.created_at.desc()).all()
        response = []
        for user in users:
            response.append({
                'user_id': user.user_id,
                'username': user.username,
                'email': user.email,
                'created_at': user.created_at.isoformat() if user.created_at else None,
                'updated_at': user.updated_at.isoformat() if user.updated_at else None,
                'last_login': user.last_login.isoformat() if user.last_login else None,
            })
        return jsonify({'users': response})

    @app.route('/api/deployment-info', methods=['GET'])
    def deployment_info():
        """Return deployment information including server start time."""
        current_time = datetime.now(tz=PT_ZONE)
        return jsonify({
            'deploymentTime': DEPLOYMENT_TIME.isoformat(),
            'serverTime': current_time.isoformat(),
        })

    @app.cli.command('seed-sample-data')
    def seed_sample_data() -> None:
        """Populate the database with a demo user and sample game (development use only)."""
        try:
            if User.query.count() == 0:
                sample_user = User(
                    username='testuser',
                    email='testuser@example.com',
                    password='testpass123'
                )
                db.session.add(sample_user)
                db.session.commit()
                app.logger.info("Seed: Created sample user %s", sample_user.user_id)
            else:
                sample_user = User.query.first()
                if not sample_user:
                    app.logger.error("Seed: No user records available after lookup")
                    raise SystemExit(1)

            if Game.query.count() == 0:
                game = Game(
                    title='Sample Chess Game',
                    opponent_name='Claire',
                    user_id=sample_user.user_id,
                    user_color='w',
                    starting_fen='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
                )
                db.session.add(game)
                db.session.commit()

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
                    db.session.add(Move(
                        game_id=game.id,
                        move_number=move_num,
                        color=color,
                        algebraic_notation=notation,
                        fen=fen
                    ))

                game.result = '1-0'
                game.status = 'completed'
                db.session.commit()
                app.logger.info("Seed: Created sample game %s", game.id)
            else:
                app.logger.info("Seed: Existing games found, skipping sample game creation")
        except Exception as exc:
            db.session.rollback()
            app.logger.error("Seed command failed: %s", exc, exc_info=True)
            raise SystemExit(1)

    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)
