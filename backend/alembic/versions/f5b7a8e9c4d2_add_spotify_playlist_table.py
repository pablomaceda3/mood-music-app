"""add_spotify_playlists_table

Revision ID: f5b7a8e9c4d2
Revises: d65a295f1560
Create Date: 2025-03-07 10:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic.
revision: str = 'f5b7a8e9c4d2'
down_revision: Union[str, None] = 'd65a295f1560'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create the spotify_playlists table
    op.create_table(
        'spotify_playlists',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('transition_id', sa.Integer(), nullable=True),
        sa.Column('spotify_id', sa.String(), nullable=False),
        sa.Column('playlist_url', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True, default=datetime.utcnow),
        sa.ForeignKeyConstraint(['transition_id'], ['mood_transitions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index(op.f('ix_spotify_playlists_id'), 'spotify_playlists', ['id'], unique=False)
    op.create_index(op.f('ix_spotify_playlists_spotify_id'), 'spotify_playlists', ['spotify_id'], unique=True)


def downgrade() -> None:
    # Drop indexes
    op.drop_index(op.f('ix_spotify_playlists_spotify_id'), table_name='spotify_playlists')
    op.drop_index(op.f('ix_spotify_playlists_id'), table_name='spotify_playlists')
    
    # Drop the table
    op.drop_table('spotify_playlists')