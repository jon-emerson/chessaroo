"""Seed a demo chess match for the user when they call GET /api/create-sample-game."""

from flask import Blueprint, jsonify

from backend.models import db, Game, Move
from backend.routes.helpers import get_current_user, login_required

bp = Blueprint('create_sample_game', __name__)


@bp.get('/api/create-sample-game')
@login_required
def create_sample_game():
    user = get_current_user()
    game = Game(
        title='Sample Chess Game',
        opponent_name='Claire',
        user_id=user.user_id,
        user_color='w',
        starting_fen='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1',
    )
    db.session.add(game)
    db.session.commit()

    game.title = f'Sample Chess Game #{game.id}'
    db.session.commit()

    sample_moves = [
        (1, 'w', 'e4', 'rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1'),
        (1, 'b', 'e5', 'rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq e6 0 2'),
        (2, 'w', 'Bc4', 'rnbqkbnr/pppp1ppp/8/4p3/2B1P3/8/PPPP1PPP/RNBQK1NR b KQkq - 1 2'),
        (2, 'b', 'Nc6', 'r1bqkbnr/pppp1ppp/2n5/4p3/2B1P3/8/PPPP1PPP/RNBQK1NR w KQkq - 2 3'),
        (3, 'w', 'Qh5', 'r1bqkbnr/pppp1ppp/2n5/4p2Q/2B1P3/8/PPPP1PPP/RNB1K1NR b KQkq - 3 3'),
        (3, 'b', 'Nf6', 'r1bqkb1r/pppp1ppp/2n2n2/4p2Q/2B1P3/8/PPPP1PPP/RNB1K1NR w KQkq - 4 4'),
        (4, 'w', 'Qxf7#', 'r1bqkb1r/pppp1Qpp/2n2n2/4p3/2B1P3/8/PPPP1PPP/RNB1K1NR b KQkq - 0 4'),
    ]

    for move_num, color, notation, fen in sample_moves:
        db.session.add(
            Move(
                game_id=game.id,
                move_number=move_num,
                color=color,
                algebraic_notation=notation,
                fen=fen,
            )
        )

    game.result = '1-0'
    game.status = 'completed'
    db.session.commit()

    return jsonify({'gameId': game.id, 'message': 'Sample game created successfully'})
