"""POST /api/auth/register"""

from flask import Blueprint, jsonify, request, session, current_app

from backend.models import db, User

bp = Blueprint('auth_register', __name__)


@bp.post('/api/auth/register')
def auth_register():
    data = request.get_json() or {}
    password = data.get('password', '')
    username = (data.get('username') or '').strip()
    email = (data.get('email') or '').strip().lower()

    if not password or not username or not email:
        return jsonify({'error': 'Password, username, and email are required'}), 400
    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters long'}), 400
    if len(username) < 3:
        return jsonify({'error': 'Username must be at least 3 characters long'}), 400
    if len(username) > 100:
        return jsonify({'error': 'Username must be 100 characters or less'}), 400
    if '@' not in email or '.' not in email.split('@')[-1]:
        return jsonify({'error': 'Please enter a valid email address'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username is already taken'}), 409
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email is already registered'}), 409

    try:
        user = User(username=username, email=email, password=password)
        db.session.add(user)
        db.session.commit()
    except Exception as exc:  # pylint: disable=broad-except
        db.session.rollback()
        current_app.logger.error("Registration failed for %s: %s", username, exc, exc_info=True)
        return jsonify({'error': 'Registration failed'}), 500

    session['user_id'] = user.user_id
    return jsonify({'message': 'User registered successfully', 'user': user.to_dict()}), 201
