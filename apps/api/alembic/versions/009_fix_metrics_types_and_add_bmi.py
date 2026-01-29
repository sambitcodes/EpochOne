"""Fix metrics types and add bmi

Revision ID: 009
Revises: 008
Create Date: 2026-01-29

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '009'
down_revision = '008'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('users', sa.Column('bmi', sa.Float(), nullable=True))
    # Alter column types to Float
    op.alter_column('users', 'body_fat_pct',
               existing_type=sa.INTEGER(),
               type_=sa.Float(),
               existing_nullable=True)
    op.alter_column('users', 'lean_body_mass',
               existing_type=sa.INTEGER(),
               type_=sa.Float(),
               existing_nullable=True)

def downgrade():
    op.alter_column('users', 'lean_body_mass',
               existing_type=sa.Float(),
               type_=sa.INTEGER(),
               existing_nullable=True)
    op.alter_column('users', 'body_fat_pct',
               existing_type=sa.Float(),
               type_=sa.INTEGER(),
               existing_nullable=True)
    op.drop_column('users', 'bmi')
