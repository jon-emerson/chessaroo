"""Expose a paginated user list for admins reviewing accounts via GET /admin/users."""

from flask import jsonify

from backend.models import User
from backend.routes.helpers import admin_authenticated


def register(bp):
    @bp.get('/users')
    def admin_users():
        if not admin_authenticated():
            return jsonify({'error': 'Admin authentication required'}), 401

        users = User.query.order_by(User.created_at.desc()).all()
        payload = [
            {
                'user_id': user.user_id,
                'username': user.username,
                'email': user.email,
                'created_at': user.created_at.isoformat() if user.created_at else None,
                'updated_at': user.updated_at.isoformat() if user.updated_at else None,
                'last_login': user.last_login.isoformat() if user.last_login else None,
            }
            for user in users
        ]
        return jsonify({'users': payload})
