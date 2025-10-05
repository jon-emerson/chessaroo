"""GET /api/imported-games/<id>"""

from flask import Blueprint, jsonify

from backend.models import ImportedGame
from backend.routes.helpers import get_current_user, login_required

bp = Blueprint('imported_game_get', __name__)


@bp.get('/api/imported-games/<int:imported_game_id>')
@login_required
def imported_game_get(imported_game_id: int):
    user = get_current_user()
    imported_game = ImportedGame.query.filter_by(id=imported_game_id, user_id=user.user_id).first()
    if not imported_game:
        return jsonify({'error': 'Imported game not found'}), 404

    return jsonify(
        {
            'id': imported_game.id,
            'chessComGameId': imported_game.chesscom_game_id,
            'sourceUrl': imported_game.source_url,
            'whiteUsername': imported_game.white_username,
            'blackUsername': imported_game.black_username,
            'resultMessage': imported_game.result_message,
            'isFinished': imported_game.is_finished,
            'gameEndReason': imported_game.game_end_reason,
            'endTime': imported_game.end_time.isoformat() if imported_game.end_time else None,
            'timeControl': imported_game.time_control,
            'importedAt': imported_game.imported_at.isoformat() if imported_game.imported_at else None,
            'uuid': imported_game.chesscom_uuid,
        }
    )
