"""seed_moods

Revision ID: d65a295f1560
Revises: 
Create Date: 2024-12-17 15:17:32.320043

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# Define moods data
moods_data = [
    {"name": "Angry", "color": "#FF4D4D"},
    {"name": "Happy", "color": "#FFD700"},
    {"name": "Sad", "color": "#4169E1"},
    {"name": "Indifferent", "color": "#A9A9A9"},
]

# revision identifiers, used by Alembic.
revision: str = 'd65a295f1560'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Get the moods table
    moods_table = sa.table('moods',
        sa.column('name', sa.String),
        sa.column('color', sa.String),
    )

    # Insert the moods
    op.bulk_insert(moods_table, moods_data)

def downgrade() -> None:
    op.execute('TRUNCATE TABLE moods')