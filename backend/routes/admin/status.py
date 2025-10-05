"""GET /admin/status"""

from flask import jsonify

from backend.routes.helpers import admin_authenticated, get_admin_password


def register(bp):
    @bp.get('/status')
    def admin_status():
        configured = bool(get_admin_password())
        if not configured:
            return jsonify({'configured': False, 'authenticated': False})
        return jsonify({'configured': True, 'authenticated': admin_authenticated()})
