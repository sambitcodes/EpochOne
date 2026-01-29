"""Add onboarding fields to user

Revision ID: 007
Revises: 006
Create Date: 2026-01-29

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '007'
down_revision = '005'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('users', sa.Column('weight', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('height', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('motive', sa.String(length=255), nullable=True))
    op.add_column('users', sa.Column('lifestyle_type', sa.String(length=255), nullable=True))
    op.add_column('users', sa.Column('workout_days_per_week', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('onboarding_complete', sa.Boolean(), nullable=False, server_default='0'))

def downgrade():
    op.drop_column('users', 'onboarding_complete')
    op.drop_column('users', 'workout_days_per_week')
    op.drop_column('users', 'lifestyle_type')
    op.drop_column('users', 'motive')
    op.drop_column('users', 'height')
    op.drop_column('users', 'weight')
