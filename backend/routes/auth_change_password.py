"""PUT /api/auth/change-password"""

from flask import Blueprint, jsonify, request
from werkzeug.security import generate_password_hash

from backend.models import db
from backend.routes.helpers import get_current_user, login_required

bp = Blueprint('auth_change_password', __name__)


@bp.put('/api/auth/change-password')
@login_required
def auth_change_password():
    user = get_current_user()
    data = request.get_json() or {}
    current_password = data.get('current_password', '')
    new_password = data.get('new_password', '')

    if not current_password or not new_password:
        return jsonify({'error': 'Current password and new password are required'}), 400
    if len(new_password) < 6:
        return jsonify({'error': 'New password must be at least 6 characters long'}), 400
    if not user.check_password(current_password):
        return jsonify({'error': 'Current password is incorrect'}), 401

    try:
        user.password_hash = generate_password_hash(new_password, method='pbkdf2:sha256')
        db.session.commit()
    except Exception:  # pylint: disable=broad-except
        db.session.rollback()
        return jsonify({'error': 'Failed to change password'}), 500

    return jsonify({'message': 'Password changed successfully'}), 200
