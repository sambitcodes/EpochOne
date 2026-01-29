"""Migrate to Health Connect

Revision ID: 004
Revises: 001
Create Date: 2026-01-29 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '004'
down_revision = '001'
branch_labels = None
depends_on = None

def upgrade():
    # 1. Add columns to users table
    op.add_column('users', sa.Column('health_connect_enabled', sa.Boolean(), server_default='false', nullable=True))
    op.add_column('users', sa.Column('apple_health_enabled', sa.Boolean(), server_default='false', nullable=True))
    op.add_column('users', sa.Column('share_profile', sa.Boolean(), server_default='false', nullable=True))
    op.add_column('users', sa.Column('settings_json', sa.JSON(), server_default='{}', nullable=True))
    op.add_column('users', sa.Column('streak_workout', sa.Integer(), server_default='0', nullable=True))
    op.add_column('users', sa.Column('streak_nutrition', sa.Integer(), server_default='0', nullable=True))
    
    # 2. Create health_connect_sync table
    op.create_table('health_connect_sync',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('last_sync', sa.DateTime(), nullable=True),
        sa.Column('sync_status', sa.String(length=50), nullable=True),
        sa.Column('sync_steps', sa.Boolean(), nullable=True),
        sa.Column('sync_activities', sa.Boolean(), nullable=True),
        sa.Column('sync_calories', sa.Boolean(), nullable=True),
        sa.Column('sync_heart_rate', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_health_connect_sync_user_id'), 'health_connect_sync', ['user_id'], unique=True)

    # 3. Create apple_health_sync table
    op.create_table('apple_health_sync',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('webhook_secret', sa.String(length=255), nullable=True),
        sa.Column('last_sync', sa.DateTime(), nullable=True),
        sa.Column('sync_status', sa.String(length=50), nullable=True),
        sa.Column('sync_steps', sa.Boolean(), nullable=True),
        sa.Column('sync_workouts', sa.Boolean(), nullable=True),
        sa.Column('sync_sleep', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_apple_health_sync_user_id'), 'apple_health_sync', ['user_id'], unique=True)

    # 4. Create other tables missing from 001 (e.g. activities, meals, body_metrics, daily_nutrition)
    # Since 001 only had users/workouts, we should add the rest here for completeness
    
    op.create_table('activities',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('activity_type', sa.String(length=100), nullable=False),
        sa.Column('date', sa.DateTime(), nullable=True),
        sa.Column('duration_minutes', sa.Integer(), nullable=False),
        sa.Column('distance_km', sa.Float(), nullable=True),
        sa.Column('intensity', sa.String(length=50), nullable=True),
        sa.Column('calories_burned', sa.Float(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('source', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_activities_date'), 'activities', ['date'], unique=False)
    op.create_index(op.f('ix_activities_user_id'), 'activities', ['user_id'], unique=False)

    op.create_table('daily_nutrition',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('date', sa.DateTime(), nullable=True),
        sa.Column('calories', sa.Integer(), nullable=True),
        sa.Column('protein_g', sa.Float(), nullable=True),
        sa.Column('carbs_g', sa.Float(), nullable=True),
        sa.Column('fat_g', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_daily_nutrition_date'), 'daily_nutrition', ['date'], unique=False)
    op.create_index(op.f('ix_daily_nutrition_user_id'), 'daily_nutrition', ['user_id'], unique=False)

    op.create_table('meals',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('date', sa.DateTime(), nullable=True),
        sa.Column('meal_type', sa.String(length=50), nullable=False),
        sa.Column('calories', sa.Integer(), nullable=False),
        sa.Column('protein_g', sa.Float(), nullable=False),
        sa.Column('carbs_g', sa.Float(), nullable=False),
        sa.Column('fat_g', sa.Float(), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('ai_estimated', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_meals_date'), 'meals', ['date'], unique=False)
    op.create_index(op.f('ix_meals_user_id'), 'meals', ['user_id'], unique=False)

    op.create_table('body_metrics',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('date', sa.DateTime(), nullable=True),
        sa.Column('metric_type', sa.String(length=100), nullable=False),
        sa.Column('value', sa.Float(), nullable=False),
        sa.Column('unit', sa.String(length=20), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_body_metrics_date'), 'body_metrics', ['date'], unique=False)
    op.create_index(op.f('ix_body_metrics_user_id'), 'body_metrics', ['user_id'], unique=False)


def downgrade():
    op.drop_table('health_connect_sync')
    op.drop_table('apple_health_sync')
    op.drop_table('activities')
    op.drop_table('meals')
    op.drop_table('daily_nutrition')
    op.drop_table('body_metrics')
    op.drop_column('users', 'health_connect_enabled')
    op.drop_column('users', 'apple_health_enabled')
    op.drop_column('users', 'share_profile')
    op.drop_column('users', 'settings_json')
    op.drop_column('users', 'streak_workout')
    op.drop_column('users', 'streak_nutrition')
