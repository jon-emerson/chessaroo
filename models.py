"""
Database models for Chessaroo chess application
"""
import os
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Game(db.Model):
    """
    Model for storing chess games
    """
    __tablename__ = 'games'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), default='Untitled Game')
    white_player = db.Column(db.String(100))
    black_player = db.Column(db.String(100))
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