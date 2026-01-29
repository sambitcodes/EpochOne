"""Add detailed health metrics

Revision ID: 008
Revises: 007
Create Date: 2026-01-29

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '008'
down_revision = '007'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('users', sa.Column('target_weight', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('age', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('gender', sa.String(length=20), nullable=True))
    op.add_column('users', sa.Column('waist', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('neck', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('chest', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('thigh', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('hip', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('body_fat_pct', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('lean_body_mass', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('maintenance_calories', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('step_goal', sa.Integer(), nullable=False, server_default='10000'))

def downgrade():
    op.drop_column('users', 'step_goal')
    op.drop_column('users', 'maintenance_calories')
    op.drop_column('users', 'lean_body_mass')
    op.drop_column('users', 'body_fat_pct')
    op.drop_column('users', 'hip')
    op.drop_column('users', 'thigh')
    op.drop_column('users', 'chest')
    op.drop_column('users', 'neck')
    op.drop_column('users', 'waist')
    op.drop_column('users', 'gender')
    op.drop_column('users', 'age')
    op.drop_column('users', 'target_weight')
