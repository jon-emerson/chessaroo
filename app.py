import os
from flask import Flask, jsonify, abort
from flask_cors import CORS
from models import db, Game, Move
import chess
import chess.pgn
from io import StringIO

def create_app():
    app = Flask(__name__)

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

    # Initialize database
    db.init_app(app)

    # Enable CORS for React frontend
    CORS(app)

    @app.route('/api/games')
    def list_games():
        """API endpoint to get list of games"""
        games = Game.query.order_by(Game.created_at.desc()).limit(10).all()
        games_data = []
        for game in games:
            games_data.append({
                'id': game.id,
                'title': game.title,
                'white_player': game.white_player,
                'black_player': game.black_player,
                'status': game.status,
                'result': game.result,
                'created_at': game.created_at.isoformat(),
                'move_count': game.moves.count()
            })

        return jsonify({'games': games_data})

    @app.route('/api/game/<int:game_id>/moves')
    def get_game_moves(game_id):
        """API endpoint to get game moves as JSON"""
        game = Game.query.get_or_404(game_id)
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
            'whitePlayer': game.white_player,
            'blackPlayer': game.black_player,
            'startingFen': game.starting_fen,
            'currentFen': game.get_current_fen(),
            'moves': moves_data
        })

    @app.route('/api/create-sample-game')
    def create_sample_game():
        """Create a sample game for testing"""
        # Create a new game
        game = Game(
            title='Sample Chess Game',
            white_player='Alice',
            black_player='Bob'
        )
        db.session.add(game)
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

    def init_database():
        """Initialize database with tables and sample data"""
        db.create_all()

        # Check if we already have games (avoid duplicate sample games)
        existing_games = Game.query.count()
        if existing_games == 0:
            # Create sample game automatically
            game = Game(
                title='Sample Chess Game',
                white_player='Alice',
                black_player='Bob'
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
            print("✅ Sample game created successfully")

    # Initialize database and create sample data
    with app.app_context():
        init_database()

    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)