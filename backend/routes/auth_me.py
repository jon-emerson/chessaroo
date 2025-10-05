"""Return the authenticated user's profile snapshot for GET /api/auth/me."""

from flask import Blueprint, jsonify

from backend.routes.helpers import get_current_user

bp = Blueprint('auth_me', __name__)


@bp.get('/api/auth/me')
def auth_me():
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Not authenticated'}), 401
    return jsonify({'user': user.to_dict(), 'authenticated': True}), 200
