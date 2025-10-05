"""Route blueprints for the Chessaroo backend."""

from . import (
    deployment_info,
    auth_register,
    auth_login,
    auth_logout,
    auth_me,
    auth_update_profile,
    auth_change_password,
    games_list,
    game_moves,
    create_sample_game,
    imported_games,
    imported_game_get,
)
from .admin import bp as admin_bp


BLUEPRINTS = [
    deployment_info.bp,
    auth_register.bp,
    auth_login.bp,
    auth_logout.bp,
    auth_me.bp,
    auth_update_profile.bp,
    auth_change_password.bp,
    games_list.bp,
    game_moves.bp,
    create_sample_game.bp,
    imported_games.bp,
    imported_game_get.bp,
    admin_bp,
]


def register_blueprints(app):
    """Register all application blueprints."""
    for blueprint in BLUEPRINTS:
        app.register_blueprint(blueprint)


__all__ = ["register_blueprints"]
