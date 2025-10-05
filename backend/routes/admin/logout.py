"""Sign an admin out by clearing the cookie on POST /admin/logout."""

from flask import jsonify

from backend.routes.helpers import clear_admin_cookie


def register(bp):
    @bp.post('/logout')
    def admin_logout():
        response = jsonify({'message': 'Admin logged out'})
        return clear_admin_cookie(response)
