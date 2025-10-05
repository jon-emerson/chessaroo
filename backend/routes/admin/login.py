"""Authenticate an admin via POST /admin/login using the master password and set the session cookie."""

import hmac

from flask import jsonify, request, current_app

from backend.routes.helpers import get_admin_password, set_admin_cookie


def register(bp):
    @bp.post('/login')
    def admin_login():
        payload = request.get_json(silent=True) or {}
        password = (payload.get('password') or '').strip()
        master_password = get_admin_password()

        if not master_password:
            current_app.logger.error('Admin login attempted without configured master password')
            return jsonify({'error': 'Admin master password is not configured'}), 500
        if not password:
            return jsonify({'error': 'Password is required'}), 400
        if not hmac.compare_digest(password, master_password):
            return jsonify({'error': 'Invalid master password'}), 401

        response = jsonify({'message': 'Admin authentication successful'})
        return set_admin_cookie(response)
