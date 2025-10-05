"""POST /api/auth/logout"""

from flask import Blueprint, jsonify, session

bp = Blueprint('auth_logout', __name__)


@bp.post('/api/auth/logout')
def auth_logout():
    session.clear()
    return jsonify({'message': 'Logged out successfully'}), 200
