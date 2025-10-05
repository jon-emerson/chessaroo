"""POST /api/auth/login"""

from datetime import datetime

from flask import Blueprint, jsonify, request, session, current_app

from backend.models import User

bp = Blueprint('auth_login', __name__)


@bp.post('/api/auth/login')
def auth_login():
    data = request.get_json() or {}
    username = (data.get('username') or '').strip()
    password = data.get('password', '')

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid username or password'}), 401

    try:
        user.last_login = datetime.utcnow()
        session['user_id'] = user.user_id
        current_app.logger.info("User %s logged in", username)
        return jsonify({'message': 'Login successful', 'user': user.to_dict()}), 200
    except Exception as exc:  # pylint: disable=broad-except
        current_app.logger.error("Login failed for %s: %s", username, exc, exc_info=True)
        return jsonify({'error': 'Login failed'}), 500
