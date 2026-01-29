"""Add calories_burned to workouts

Revision ID: 012
Revises: 011
Create Date: 2026-01-29 22:10:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '012'
down_revision = '011'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('workouts', sa.Column('calories_burned', sa.Integer(), nullable=True))


def downgrade():
    op.drop_column('workouts', 'calories_burned')
