"""add imported games table

Revision ID: 7e6ac74736cb
Revises: 0993f449f98a
Create Date: 2025-09-29 05:00:00.000000

"""
import logging

from alembic import op
import sqlalchemy as sa


logger = logging.getLogger('alembic.runtime.migration')


# revision identifiers, used by Alembic.
revision = '7e6ac74736cb'
down_revision = '0993f449f98a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind) if bind else None

    if inspector and 'imported_games' in inspector.get_table_names():
        logger.info('imported_games table already exists; skipping creation')
        return

    logger.info('Creating imported_games table')
    op.create_table(
        'imported_games',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(length=20), nullable=False),
        sa.Column('chesscom_game_id', sa.String(length=32), nullable=False),
        sa.Column('source_url', sa.String(length=512), nullable=False),
        sa.Column('raw_payload', sa.Text(), nullable=False),
        sa.Column('imported_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'chesscom_game_id', name='uq_imported_games_user_game')
    )
    op.create_index('ix_imported_games_user_id', 'imported_games', ['user_id'])
    logger.info('imported_games table created successfully')


def downgrade() -> None:
    logger.info('Dropping imported_games table')
    op.drop_index('ix_imported_games_user_id', table_name='imported_games')
    op.drop_table('imported_games')
    logger.info('imported_games table dropped')
