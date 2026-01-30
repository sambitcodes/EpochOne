"""add failure to workout exercises

Revision ID: 014
Revises: 013
Create Date: 2024-03-24 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '014'
down_revision = '013'
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.add_column('workout_exercises', sa.Column('failure', sa.Boolean(), nullable=True, default=False))

def downgrade() -> None:
    op.drop_column('workout_exercises', 'failure')
