"""Add manual auth fields

Revision ID: 005_add_manual_auth_fields
Revises: 004_migrate_to_health_connect
Create Date: 2026-01-29 15:50:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None


def upgrade():
    # Make auth0_sub nullable
    op.alter_column('users', 'auth0_sub',
               existing_type=sa.VARCHAR(length=255),
               nullable=True)
    
    # Add username and hashed_password
    op.add_column('users', sa.Column('username', sa.String(length=255), nullable=True))
    op.add_column('users', sa.Column('hashed_password', sa.String(length=255), nullable=True))
    
    # Create index for username
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)


def downgrade():
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_column('users', 'hashed_password')
    op.drop_column('users', 'username')
    op.alter_column('users', 'auth0_sub',
               existing_type=sa.VARCHAR(length=255),
               nullable=False)
