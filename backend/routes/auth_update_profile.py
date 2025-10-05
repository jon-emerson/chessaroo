"""Let authenticated users update their profile details via PUT /api/auth/update-profile."""

from flask import Blueprint, jsonify, request

from backend.models import db, User
from backend.routes.helpers import get_current_user, login_required

bp = Blueprint('auth_update_profile', __name__)


@bp.put('/api/auth/update-profile')
@login_required
def auth_update_profile():
    user = get_current_user()
    data = request.get_json() or {}
    username = (data.get('username') or '').strip()
    email = (data.get('email') or '').strip().lower()

    if not username or not email:
        return jsonify({'error': 'Username and email are required'}), 400
    if len(username) < 3:
        return jsonify({'error': 'Username must be at least 3 characters long'}), 400
    if len(username) > 50:
        return jsonify({'error': 'Username must be 50 characters or less'}), 400

    if username != user.username and User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username is already in use'}), 409
    if email != user.email and User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email is already in use'}), 409

    try:
        user.username = username
        user.email = email
        db.session.commit()
        return jsonify({'message': 'Profile updated successfully', 'user': user.to_dict()}), 200
    except Exception:  # pylint: disable=broad-except
        db.session.rollback()
        return jsonify({'error': 'Failed to update profile'}), 500
