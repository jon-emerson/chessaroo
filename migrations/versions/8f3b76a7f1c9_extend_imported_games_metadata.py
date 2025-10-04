"""extend imported games metadata

Revision ID: 8f3b76a7f1c9
Revises: 7e6ac74736cb
Create Date: 2025-09-29 06:45:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8f3b76a7f1c9'
down_revision = '7e6ac74736cb'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('imported_games', sa.Column('white_username', sa.String(length=100), nullable=True))
    op.add_column('imported_games', sa.Column('black_username', sa.String(length=100), nullable=True))
    op.add_column('imported_games', sa.Column('result_message', sa.String(length=255), nullable=True))
    op.add_column('imported_games', sa.Column('is_finished', sa.Boolean(), nullable=True))
    op.add_column('imported_games', sa.Column('game_end_reason', sa.String(length=100), nullable=True))
    op.add_column('imported_games', sa.Column('end_time', sa.DateTime(), nullable=True))
    op.add_column('imported_games', sa.Column('time_control', sa.String(length=50), nullable=True))
    op.add_column('imported_games', sa.Column('chesscom_uuid', sa.String(length=64), nullable=True))


def downgrade() -> None:
    op.drop_column('imported_games', 'chesscom_uuid')
    op.drop_column('imported_games', 'time_control')
    op.drop_column('imported_games', 'end_time')
    op.drop_column('imported_games', 'game_end_reason')
    op.drop_column('imported_games', 'is_finished')
    op.drop_column('imported_games', 'result_message')
    op.drop_column('imported_games', 'black_username')
    op.drop_column('imported_games', 'white_username')
