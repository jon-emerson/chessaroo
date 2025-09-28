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

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(20), unique=True, nullable=False)  # Public facing ID
    username = db.Column(db.String(50), unique=True, nullable=False)  # Display name for other users
    email = db.Column(db.String(255), unique=True, nullable=False)   # Private, for login
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)

    # Relationship to games
    games = db.relationship('Game', backref='owner', lazy='dynamic', cascade='all, delete-orphan')

    def __init__(self, email, password, username, user_id=None):
        self.email = email.lower().strip()
        self.username = username.strip()
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')
        self.user_id = user_id or self._generate_user_id()

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

    def update_last_login(self):
        """Update the last login timestamp"""
        self.last_login = datetime.utcnow()
        db.session.commit()

    def to_dict(self):
        """Convert user to dictionary (excluding sensitive info)"""
        return {
            'user_id': self.user_id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

    def __repr__(self):
        return f'<User {self.user_id}: {self.email}>'

class Game(db.Model):
    """
    Model for storing chess games
    """
    __tablename__ = 'games'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(20), db.ForeignKey('users.user_id'), nullable=True, index=True)
    user_color = db.Column(db.String(1), nullable=True)  # 'w' or 'b' - which color the user played
    title = db.Column(db.String(255), default='Untitled Game')
    opponent_name = db.Column(db.String(100))  # Name of the opponent player
    result = db.Column(db.String(10), default='*')  # 1-0, 0-1, 1/2-1/2, *
    status = db.Column(db.String(20), default='active')  # active, completed, abandoned
    starting_fen = db.Column(db.String(100), default='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship to moves
    moves = db.relationship('Move', backref='game', lazy='dynamic', cascade='all, delete-orphan')

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
    game_id = db.Column(db.Integer, db.ForeignKey('games.id'), nullable=False)
    move_number = db.Column(db.Integer, nullable=False)
    color = db.Column(db.String(1), nullable=False)  # 'w' or 'b'
    algebraic_notation = db.Column(db.String(10), nullable=False)
    fen = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Composite unique constraint
    __table_args__ = (db.UniqueConstraint('game_id', 'move_number', 'color'),)

    def __repr__(self):
        return f'<Move {self.game_id}-{self.move_number}{self.color}: {self.algebraic_notation}>'