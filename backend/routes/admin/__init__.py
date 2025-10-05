"""Assemble the admin blueprint and register its login, logout, status, and user routes."""

from flask import Blueprint

from .login import register as register_login
from .logout import register as register_logout
from .status import register as register_status
from .users import register as register_users

bp = Blueprint('admin', __name__, url_prefix='/admin')


def register_routes():
    register_login(bp)
    register_logout(bp)
    register_status(bp)
    register_users(bp)


register_routes()

__all__ = ["bp"]
