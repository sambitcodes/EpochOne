"""Add FitbitSync table with metrics

Revision ID: 011
Revises: 010
Create Date: 2026-01-29 21:50:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic.
revision = '011'
down_revision = '010'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('fitbit_sync',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('access_token', sa.Text(), nullable=True),
        sa.Column('refresh_token', sa.Text(), nullable=True),
        sa.Column('expires_at', sa.Integer(), nullable=True),
        sa.Column('last_sync', sa.DateTime(), nullable=True),
        sa.Column('last_step_count', sa.Integer(), nullable=True, default=0),
        sa.Column('last_calories_burned', sa.Integer(), nullable=True, default=0),
        sa.Column('sync_status', sa.String(length=50), nullable=True, default='idle'),
        sa.Column('sync_steps', sa.Boolean(), nullable=True, default=True),
        sa.Column('sync_activities', sa.Boolean(), nullable=True, default=True),
        sa.Column('sync_calories', sa.Boolean(), nullable=True, default=True),
        sa.Column('sync_sleep', sa.Boolean(), nullable=True, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(), nullable=True, default=datetime.utcnow),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_fitbit_sync_user_id'), 'fitbit_sync', ['user_id'], unique=True)

def downgrade():
    op.drop_index(op.f('ix_fitbit_sync_user_id'), table_name='fitbit_sync')
    op.drop_table('fitbit_sync')
