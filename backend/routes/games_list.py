"""GET /api/games"""

from flask import Blueprint, jsonify

from backend.models import Game
from backend.routes.helpers import get_current_user, login_required

bp = Blueprint('games_list', __name__)


@bp.get('/api/games')
@login_required
def games_list():
    user = get_current_user()
    games = (
        Game.query.filter_by(user_id=user.user_id)
        .order_by(Game.created_at.desc())
        .limit(10)
        .all()
    )

    games_data = [
        {
            'id': game.id,
            'title': game.title,
            'user_color': game.user_color,
            'opponent_name': game.opponent_name,
            'status': game.status,
            'result': game.result,
            'created_at': game.created_at.isoformat(),
            'move_count': game.moves.count(),
        }
        for game in games
    ]
    return jsonify({'games': games_data})
