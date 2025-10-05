"""GET /api/deployment-info"""

from datetime import datetime

from flask import Blueprint, jsonify, current_app

bp = Blueprint('deployment_info', __name__)


@bp.get('/api/deployment-info')
def deployment_info():
    deployment_time: datetime = current_app.config['DEPLOYMENT_TIME']
    current_time = datetime.now(tz=deployment_time.tzinfo)
    return jsonify(
        {
            'deploymentTime': deployment_time.isoformat(),
            'serverTime': current_time.isoformat(),
        }
    )
