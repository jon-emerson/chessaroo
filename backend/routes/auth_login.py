"""POST /api/auth/login"""

from datetime import datetime

from flask import Blueprint, jsonify, request, session, current_app

from backend.models import User

bp = Blueprint('auth_login', __name__)


@bp.post('/api/auth/login')
def auth_login():
    data = request.get_json() or {}
    identifier = (data.get('identifier') or data.get('username') or '').strip()
    password = (data.get('password') or '').strip()

    if not identifier or not password:
        return jsonify({'error': 'Username or email and password are required'}), 400

    identifier_email = identifier.lower()
    user = (
        User.query.filter((User.username == identifier) | (User.email == identifier_email))
        .first()
    )

    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid username/email or password'}), 401

    try:
        user.last_login = datetime.utcnow()
        session['user_id'] = user.user_id
        current_app.logger.info("User %s logged in", user.username)
        return jsonify({'message': 'Login successful', 'user': user.to_dict()}), 200
    except Exception as exc:  # pylint: disable=broad-except
        current_app.logger.error("Login failed for %s: %s", user.username, exc, exc_info=True)
        return jsonify({'error': 'Login failed'}), 500
