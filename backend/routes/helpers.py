"""Shared helpers and decorators for backend routes."""

from datetime import datetime
from functools import wraps
from typing import Callable, Optional

from flask import jsonify, current_app, request, session
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from backend.models import User


def login_required(func: Callable) -> Callable:
    """Ensure the user has an authenticated session before accessing a route."""

    @wraps(func)
    def wrapped(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return func(*args, **kwargs)

    return wrapped


def get_current_user() -> Optional[User]:
    """Return the current authenticated user, if any."""
    user_id = session.get('user_id')
    if not user_id:
        return None
    return User.query.filter_by(user_id=user_id).first()


def get_admin_password() -> Optional[str]:
    env = current_app.config.get('APP_ENV', 'production')
    if env in ('production', 'prod'):
        return current_app.config.get('ADMIN_MASTER_PASSWORD')
    return current_app.config.get('ADMIN_MASTER_PASSWORD_DEV')


def get_admin_serializer() -> URLSafeTimedSerializer:
    secret = current_app.config['SECRET_KEY']
    salt = 'blunderlab-admin-cookie'
    return URLSafeTimedSerializer(secret_key=secret, salt=salt)


def set_admin_cookie(response):
    serializer = get_admin_serializer()
    token = serializer.dumps({'ts': datetime.utcnow().isoformat()})
    response.set_cookie(
        current_app.config['ADMIN_SESSION_COOKIE_NAME'],
        token,
        max_age=current_app.config['ADMIN_SESSION_MAX_AGE'],
        httponly=True,
        secure=current_app.config.get('SESSION_COOKIE_SECURE', False),
        samesite='Strict',
    )
    return response


def clear_admin_cookie(response):
    response.delete_cookie(current_app.config['ADMIN_SESSION_COOKIE_NAME'])
    return response


def admin_authenticated() -> bool:
    token = request.cookies.get(current_app.config['ADMIN_SESSION_COOKIE_NAME'])
    if not token:
        return False
    serializer = get_admin_serializer()
    try:
        serializer.loads(token, max_age=current_app.config['ADMIN_SESSION_MAX_AGE'])
        return True
    except (BadSignature, SignatureExpired):
        return False


__all__ = [
    'login_required',
    'get_current_user',
    'get_admin_password',
    'set_admin_cookie',
    'clear_admin_cookie',
    'admin_authenticated',
]
