"""
Initial database schema migration.
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    """Create initial tables."""
    op.create_table(
        'users',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('auth0_sub', sa.String(255), unique=True, nullable=False),
        sa.Column('email', sa.String(255), unique=True, nullable=False),
        sa.Column('name', sa.String(255), nullable=True),
        sa.Column('picture', sa.String(500), nullable=True),
        sa.Column('units', sa.String(50), default='metric'),
        sa.Column('calorie_target', sa.Integer, default=2200),
        sa.Column('protein_target', sa.Integer, default=150),
        sa.Column('xp', sa.Integer, default=0),
        sa.Column('level', sa.Integer, default=1),
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, default=sa.func.now()),
    )

    op.create_index('ix_users_auth0_sub', 'users', ['auth0_sub'])
    op.create_index('ix_users_email', 'users', ['email'])

    op.create_table(
        'workouts',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('date', sa.DateTime, default=sa.func.now()),
        sa.Column('duration_minutes', sa.Integer, nullable=False),
        sa.Column('rpe', sa.Integer, nullable=True),
        sa.Column('notes', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
    )

    op.create_index('ix_workouts_user_id_date', 'workouts', ['user_id', 'date'])

def downgrade():
    """Drop initial tables."""
    op.drop_table('workouts')
    op.drop_table('users')