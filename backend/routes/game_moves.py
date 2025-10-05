"""GET /api/game/<game_id>/moves"""

from flask import Blueprint, jsonify

from backend.models import Game, Move
from backend.routes.helpers import get_current_user, login_required

bp = Blueprint('game_moves', __name__)


@bp.get('/api/game/<int:game_id>/moves')
@login_required
def game_moves(game_id: int):
    user = get_current_user()
    game = Game.query.filter_by(id=game_id, user_id=user.user_id).first()
    if not game:
        return jsonify({'error': 'Game not found'}), 404

    moves = game.moves.order_by(Move.move_number, Move.color.desc()).all()
    moves_data = [
        {
            'moveNumber': move.move_number,
            'color': move.color,
            'algebraic': move.algebraic_notation,
            'fen': move.fen,
        }
        for move in moves
    ]

    return jsonify(
        {
            'gameId': game.id,
            'title': game.title,
            'userColor': game.user_color,
            'opponentName': game.opponent_name,
            'startingFen': game.starting_fen,
            'currentFen': game.get_current_fen(),
            'moves': moves_data,
        }
    )
