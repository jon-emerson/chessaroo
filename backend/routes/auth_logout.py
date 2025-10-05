"""Clear the current session with POST /api/auth/logout so the user is signed out."""

from flask import Blueprint, jsonify, session

bp = Blueprint('auth_logout', __name__)


@bp.post('/api/auth/logout')
def auth_logout():
    session.pop('user_id', None)
    return jsonify({'message': 'Logged out successfully from this session'}), 200
