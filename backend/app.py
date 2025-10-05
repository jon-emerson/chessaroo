import logging
import os
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate

from backend.models import db
from backend.routes import register_blueprints

load_dotenv()
load_dotenv('.env.local', override=True)

PT_ZONE = ZoneInfo('America/Los_Angeles')
CONTAINER_GUARD_EXIT_CODE = 72
DEPLOYMENT_TIME = datetime.now(tz=PT_ZONE)

migrate = Migrate()


def _ensure_container_runtime():
    """Ensure the backend only runs inside a sanctioned container environment."""
    if os.environ.get('ALLOW_NON_CONTAINER') == '1':
        return
    if os.environ.get('CI'):
        return
    if os.path.exists('/.dockerenv'):
        return
    if os.environ.get('RUNNING_IN_CONTAINER') == '1':
        return
    ecs_metadata_keys = ('ECS_CONTAINER_METADATA_URI', 'ECS_CONTAINER_METADATA_URI_V4')
    if any(os.environ.get(key) for key in ecs_metadata_keys):
        return
    if os.environ.get('AWS_EXECUTION_ENV', '').startswith('AWS_ECS'):
        return

    message = (
        'Chessaroo backend detected a non-container environment. Start services via '
        '`docker compose up` (or set ALLOW_NON_CONTAINER=1 if you intentionally bypass this check).'
    )
    sys.stderr.write(message + '\n')
    raise SystemExit(CONTAINER_GUARD_EXIT_CODE)


def _configure_logging(app: Flask) -> None:
    if app.debug or app.testing:
        return
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(name)s: %(message)s',
        stream=sys.stdout,
    )
    app.logger.setLevel(logging.INFO)
    app.logger.info('Chessaroo application startup')


def _configure_database(app: Flask) -> None:
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        db_host = os.environ.get('DB_HOST', '127.0.0.1')
        db_port = os.environ.get('DB_PORT', '5432')
        db_name = os.environ.get('DB_NAME', 'chessaroo')
        db_user = os.environ.get('DB_USER', 'chessaroo_user')
        db_password = os.environ.get('DB_PASSWORD', 'chessaroo_pass')
        database_url = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'

    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    connect_args: dict[str, object] = {}
    if database_url.startswith('postgresql'):
        connect_args['connect_timeout'] = 10
        if 'amazonaws.com' in database_url:
            connect_args['sslmode'] = 'require'

    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        'pool_recycle': 3600,
        'pool_size': 10,
        'max_overflow': 20,
        'connect_args': connect_args,
    }

    if 'localhost' in database_url:
        app.logger.info("Database: Connected to local PostgreSQL")
    elif 'amazonaws.com' in database_url:
        app.logger.info("Database: Connected to AWS RDS PostgreSQL")
    else:
        app.logger.info("Database: Connected to PostgreSQL")


def create_app():
    _ensure_container_runtime()
    app = Flask(__name__)

    _configure_logging(app)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

    app_env = os.environ.get('APP_ENV')
    if not app_env:
        flask_env = os.environ.get('FLASK_ENV') or app.config.get('ENV')
        if flask_env:
            app_env = flask_env
        elif app.debug:
            app_env = 'development'
        else:
            app_env = 'production'
    app.config['APP_ENV'] = app_env.lower()

    app.config['ADMIN_MASTER_PASSWORD'] = os.environ.get('ADMIN_MASTER_PASSWORD')
    app.config['ADMIN_MASTER_PASSWORD_DEV'] = os.environ.get('ADMIN_MASTER_PASSWORD_DEV')
    app.config.setdefault('ADMIN_SESSION_MAX_AGE', int(os.environ.get('ADMIN_SESSION_MAX_AGE', '3600')))
    app.config.setdefault('ADMIN_SESSION_COOKIE_NAME', os.environ.get('ADMIN_SESSION_COOKIE_NAME', 'chessaroo_admin_session'))
    app.config['DEPLOYMENT_TIME'] = DEPLOYMENT_TIME

    _configure_database(app)

    db.init_app(app)
    migrate.init_app(app, db)

    CORS(app, supports_credentials=True)

    register_blueprints(app)

    return app


app = create_app()


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)
