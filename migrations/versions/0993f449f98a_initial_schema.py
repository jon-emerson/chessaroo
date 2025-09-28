"""initial schema

Revision ID: 0993f449f98a
Revises: 
Create Date: 2025-09-28 22:15:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0993f449f98a'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('user_id', sa.String(length=20), nullable=False),
        sa.Column('username', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('last_login', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('user_id'),
        sa.UniqueConstraint('username', name='uq_users_username'),
        sa.UniqueConstraint('email', name='uq_users_email')
    )

    op.create_table(
        'games',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(length=20), nullable=False),
        sa.Column('user_color', sa.String(length=1), nullable=True),
        sa.Column('title', sa.String(length=255), server_default=sa.text("'Untitled Game'"), nullable=False),
        sa.Column('opponent_name', sa.String(length=100), nullable=True),
        sa.Column('result', sa.String(length=10), server_default=sa.text("'*'"), nullable=False),
        sa.Column('status', sa.String(length=20), server_default=sa.text("'active'"), nullable=False),
        sa.Column('starting_fen', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.CheckConstraint("user_color IN ('w', 'b')", name='ck_games_user_color'),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_games_user_id', 'games', ['user_id'])
    op.create_index('ix_games_status', 'games', ['status'])
    op.create_index('ix_games_created_at', 'games', ['created_at'])

    op.create_table(
        'moves',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('game_id', sa.Integer(), nullable=False),
        sa.Column('move_number', sa.Integer(), nullable=False),
        sa.Column('color', sa.String(length=1), nullable=False),
        sa.Column('algebraic_notation', sa.String(length=10), nullable=False),
        sa.Column('fen', sa.String(length=100), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.CheckConstraint("color IN ('w', 'b')", name='ck_moves_color'),
        sa.ForeignKeyConstraint(['game_id'], ['games.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('game_id', 'move_number', 'color', name='uq_moves_game_move_color')
    )
    op.create_index('ix_moves_game_id', 'moves', ['game_id'])


def downgrade() -> None:
    op.drop_index('ix_moves_game_id', table_name='moves')
    op.drop_table('moves')

    op.drop_index('ix_games_created_at', table_name='games')
    op.drop_index('ix_games_status', table_name='games')
    op.drop_index('ix_games_user_id', table_name='games')
    op.drop_table('games')

    op.drop_table('users')
