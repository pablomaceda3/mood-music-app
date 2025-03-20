"""add_users_table_and_update_mood_transitions

Revision ID: e72a4b9c8f3d
Revises: f5b7a8e9c4d2
Create Date: 2025-03-20 10:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic.
revision: str = 'e72a4b9c8f3d'
down_revision: Union[str, None] = 'f5b7a8e9c4d2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes on users table
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    
    # Add user_id column to mood_transitions table
    op.add_column('mood_transitions', sa.Column('user_id', sa.Integer(), nullable=True))
    
    # Create foreign key constraint
    op.create_foreign_key(
        'fk_mood_transitions_user_id',
        'mood_transitions',
        'users',
        ['user_id'],
        ['id']
    )
    
    # Create a default user for existing transitions
    op.execute("""
    INSERT INTO users (username, email, hashed_password, is_active)
    VALUES ('system', 'system@example.com', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', true)
    """)
    
    # Set all existing transitions to be owned by the system user
    op.execute("""
    UPDATE mood_transitions
    SET user_id = (SELECT id FROM users WHERE username = 'system')
    """)
    
    # Make user_id column non-nullable now that we've set a value for all rows
    op.alter_column('mood_transitions', 'user_id', nullable=False)


def downgrade() -> None:
    # Remove foreign key constraint
    op.drop_constraint('fk_mood_transitions_user_id', 'mood_transitions', type_='foreignkey')
    
    # Drop user_id column from mood_transitions
    op.drop_column('mood_transitions', 'user_id')
    
    # Drop indexes on users table
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    
    # Drop users table
    op.drop_table('users')