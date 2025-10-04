"""Chess.com import helpers."""

import re
from datetime import datetime
from typing import Tuple, Dict, Any
from urllib.parse import urlparse

import requests
from flask import current_app

from models import db, ImportedGame


class ChessComImportError(Exception):
    """Raised when a Chess.com import fails."""

    def __init__(self, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.status_code = status_code


def extract_chesscom_game_id(game_reference: str) -> str:
    """Extract the numeric Chess.com game identifier from a URL or raw string."""
    if not game_reference:
        raise ChessComImportError('Chess.com game URL is required', 400)

    candidate = game_reference.strip()
    parsed = urlparse(candidate)

    if parsed.netloc and 'chess.com' not in parsed.netloc.lower():
        raise ChessComImportError('Provided URL is not a Chess.com link', 400)

    search_targets = [parsed.path or '', parsed.fragment or '', candidate if not parsed.netloc else '']
    for target in search_targets:
        match = re.search(r'(\d+)(?:/)?$', target)
        if match:
            return match.group(1)

    raise ChessComImportError('Unable to determine Chess.com game ID from URL', 400)


def fetch_chesscom_payload(game_id: str) -> Tuple[str, Dict[str, Any]]:
    """Retrieve the raw and parsed game payload from Chess.com."""
    api_url = f'https://www.chess.com/callback/live/game/{game_id}'
    headers = {
        'User-Agent': 'Chessaroo/1.0 (https://github.com/jon-emerson/chessaroo)',
        'Accept': 'application/json'
    }

    try:
        response = requests.get(api_url, headers=headers, timeout=10)
    except requests.RequestException as exc:
        current_app.logger.exception('Failed to reach Chess.com: %s', exc)
        raise ChessComImportError('Unable to reach Chess.com', 502) from exc

    if response.status_code == 404:
        raise ChessComImportError('Chess.com game not found', 404)

    if not response.ok:
        current_app.logger.warning('Chess.com returned unexpected status %s for %s', response.status_code, api_url)
        raise ChessComImportError('Failed to fetch game from Chess.com', 502)

    try:
        response_json = response.json()
    except ValueError as exc:
        current_app.logger.warning('Received non-JSON payload from Chess.com for %s', api_url)
        raise ChessComImportError('Invalid data received from Chess.com', 502) from exc

    return response.text, response_json


def import_chesscom_game(user, game_url: str):
    """Import a Chess.com game for the provided user."""
    game_id = extract_chesscom_game_id(game_url)
    raw_payload, payload_json = fetch_chesscom_payload(game_id)

    game_data = payload_json.get('game', {}) or {}
    players = payload_json.get('players', {}) or {}
    white_player = players.get('bottom', {}) or {}
    black_player = players.get('top', {}) or {}
    headers = game_data.get('pgnHeaders') or {}

    imported_game = ImportedGame.query.filter_by(
        user_id=user.user_id,
        chesscom_game_id=game_id
    ).first()

    if imported_game:
        imported_game.raw_payload = raw_payload
        imported_game.source_url = game_url
        imported_game.imported_at = datetime.utcnow()
    else:
        imported_game = ImportedGame(
            user_id=user.user_id,
            chesscom_game_id=game_id,
            source_url=game_url,
            raw_payload=raw_payload,
        )
        db.session.add(imported_game)

    imported_game.white_username = white_player.get('username') or headers.get('White')
    imported_game.black_username = black_player.get('username') or headers.get('Black')
    imported_game.result_message = game_data.get('resultMessage') or headers.get('Result')
    imported_game.is_finished = bool(game_data.get('isFinished')) if game_data else False
    imported_game.game_end_reason = game_data.get('gameEndReason')
    end_epoch = game_data.get('endTime')
    if isinstance(end_epoch, (int, float)):
        imported_game.end_time = datetime.utcfromtimestamp(end_epoch)
    else:
        imported_game.end_time = None
    imported_game.time_control = headers.get('TimeControl')
    imported_game.chesscom_uuid = game_data.get('uuid')

    try:
        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        current_app.logger.exception('Failed to store imported game: %s', exc)
        raise ChessComImportError('Failed to save imported game', 500) from exc

    summary = {
        'whiteUsername': imported_game.white_username,
        'blackUsername': imported_game.black_username,
        'resultMessage': imported_game.result_message,
        'isFinished': imported_game.is_finished,
    }

    return imported_game, summary
