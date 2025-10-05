"""POST /api/imported-games"""

from flask import Blueprint, jsonify, request

from helpers.chesscom_import import (
    import_chesscom_game as import_chesscom_game_service,
    ChessComImportError,
)
from backend.routes.helpers import get_current_user, login_required

bp = Blueprint('imported_games', __name__)


@bp.post('/api/imported-games')
@login_required
def imported_games():
    user = get_current_user()
    payload = request.get_json(silent=True) or {}
    game_url = (payload.get('url') or payload.get('gameUrl') or '').strip()

    try:
        imported_game, summary = import_chesscom_game_service(user, game_url)
    except ChessComImportError as exc:
        return jsonify({'error': str(exc)}), exc.status_code

    return jsonify(
        {
            'importedGameId': imported_game.id,
            'chessComGameId': imported_game.chesscom_game_id,
            'sourceUrl': imported_game.source_url,
            'payloadSummary': summary,
        }
    ), 201
