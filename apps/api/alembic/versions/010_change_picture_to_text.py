"""Change picture to text

 Revision ID: 010
 Revises: 009
 Create Date: 2026-01-29

 """
from alembic import op
import sqlalchemy as sa

 # revision identifiers, used by Alembic.
revision = '010'
down_revision = '009'
branch_labels = None
depends_on = None

def upgrade():
    op.alter_column('users', 'picture',
               existing_type=sa.String(length=500),
               type_=sa.Text(),
               existing_nullable=True)

def downgrade():
    op.alter_column('users', 'picture',
               existing_type=sa.Text(),
               type_=sa.String(length=500),
               existing_nullable=True)
