"""
Database models for Chessaroo chess application
"""
import os
import secrets
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    """
    Model for storing user accounts
    """
    __tablename__ = 'users'

    user_id = db.Column(db.String(20), primary_key=True)  # Public facing ID, now the primary key
    username = db.Column(db.String(100), unique=True, nullable=False)  # Display name for other users
    email = db.Column(db.String(255), unique=True, nullable=False)  # Email for login and communication
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=False)

    # Relationship to games
    games = db.relationship(
        'Game',
        backref=db.backref('owner', passive_deletes=True),
        lazy='dynamic',
        cascade='all, delete-orphan',
        passive_deletes=True
    )

    imported_games = db.relationship(
        'ImportedGame',
        backref=db.backref('owner', passive_deletes=True),
        lazy='dynamic',
        cascade='all, delete-orphan',
        passive_deletes=True
    )

    def __init__(self, username, email, password, user_id=None):
        self.username = username.strip()
        self.email = email.strip().lower()
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')
        self.user_id = user_id or self._generate_user_id()
        self.last_login = datetime.utcnow()

    def _generate_user_id(self):
        """Generate a unique public user ID"""
        while True:
            # Generate a random alphanumeric ID
            user_id = secrets.token_hex(4).upper()
            if not User.query.filter_by(user_id=user_id).first():
                return user_id

    def check_password(self, password):
        """Check if provided password matches the stored hash"""
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        """Convert user to dictionary (excluding sensitive info)"""
        return {
            'user_id': self.user_id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

    def __repr__(self):
        return f'<User {self.user_id}: {self.username}>'

class Game(db.Model):
    """
    Model for storing chess games
    """
    __tablename__ = 'games'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.String(20),
        db.ForeignKey('users.user_id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    user_color = db.Column(db.String(1), nullable=True)  # 'w' or 'b' - which color the user played
    title = db.Column(db.String(255), default='Untitled Game')
    opponent_name = db.Column(db.String(100))  # Name of the opponent player
    result = db.Column(db.String(10), default='*')  # 1-0, 0-1, 1/2-1/2, *
    status = db.Column(db.String(20), default='active')  # active, completed, abandoned
    starting_fen = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Additional indexes for common queries
    __table_args__ = (
        db.Index('ix_games_status', 'status'),
        db.Index('ix_games_created_at', 'created_at'),
        db.CheckConstraint("user_color IN ('w', 'b')", name='ck_games_user_color'),
    )

    # Relationship to moves
    moves = db.relationship(
        'Move',
        backref=db.backref('game', passive_deletes=True),
        lazy='dynamic',
        cascade='all, delete-orphan',
        passive_deletes=True
    )

    def __repr__(self):
        return f'<Game {self.id}: {self.title}>'

    def get_current_fen(self):
        """Get the current FEN from the last move, or starting FEN if no moves"""
        last_move = self.moves.order_by(Move.move_number.desc(), Move.color.desc()).first()
        if last_move:
            return last_move.fen
        return self.starting_fen

    def get_moves_pgn(self):
        """Get moves in PGN format"""
        moves = self.moves.order_by(Move.move_number, Move.color).all()
        pgn_moves = []

        for i, move in enumerate(moves):
            if move.color == 'w':
                pgn_moves.append(f"{move.move_number}. {move.algebraic_notation}")
            else:
                pgn_moves.append(move.algebraic_notation)

        return ' '.join(pgn_moves)

class Move(db.Model):
    """
    Model for storing individual chess moves
    """
    __tablename__ = 'moves'

    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(
        db.Integer,
        db.ForeignKey('games.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    move_number = db.Column(db.Integer, nullable=False)
    color = db.Column(db.String(1), nullable=False)  # 'w' or 'b'
    algebraic_notation = db.Column(db.String(10), nullable=False)
    fen = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Composite unique constraint
    __table_args__ = (
        db.UniqueConstraint('game_id', 'move_number', 'color', name='uq_moves_game_move_color'),
        db.CheckConstraint("color IN ('w', 'b')", name='ck_moves_color'),
    )

    def __repr__(self):
        return f'<Move {self.game_id}-{self.move_number}{self.color}: {self.algebraic_notation}>'


class ImportedGame(db.Model):
    """Store raw Chess.com import payloads"""
    __tablename__ = 'imported_games'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.String(20),
        db.ForeignKey('users.user_id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    chesscom_game_id = db.Column(db.String(32), nullable=False)
    source_url = db.Column(db.String(512), nullable=False)
    raw_payload = db.Column(db.Text, nullable=False)
    imported_at = db.Column(db.DateTime, default=datetime.utcnow)
    white_username = db.Column(db.String(100))
    black_username = db.Column(db.String(100))
    result_message = db.Column(db.String(255))
    is_finished = db.Column(db.Boolean, default=False)
    game_end_reason = db.Column(db.String(100))
    end_time = db.Column(db.DateTime, nullable=True)
    time_control = db.Column(db.String(50))
    chesscom_uuid = db.Column(db.String(64))

    __table_args__ = (
        db.UniqueConstraint('user_id', 'chesscom_game_id', name='uq_imported_games_user_game'),
    )

    def __repr__(self):
        return f'<ImportedGame {self.user_id}:{self.chesscom_game_id}>'
