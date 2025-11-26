"""Add settings and settings_history tables

Revision ID: 001
Revises:
Create Date: 2025-11-26 19:40:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create settings table
    op.create_table(
        'settings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('key', sa.String(length=255), nullable=False),
        sa.Column('value', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=False),
        sa.Column('description', sa.String(length=512), nullable=True),
        sa.Column('default_value', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('value_type', sa.String(length=50), nullable=False),
        sa.Column('validation_rules', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('is_sensitive', sa.Boolean(), nullable=False),
        sa.Column('requires_restart', sa.Boolean(), nullable=False),
        sa.Column('metadata', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('key')
    )
    op.create_index(op.f('ix_settings_key'), 'settings', ['key'], unique=True)
    op.create_index(op.f('ix_settings_category'), 'settings', ['category'], unique=False)

    # Create settings_history table
    op.create_table(
        'settings_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('setting_key', sa.String(length=255), nullable=False),
        sa.Column('old_value', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('new_value', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('changed_by', sa.String(length=255), nullable=True),
        sa.Column('reason', sa.String(length=512), nullable=True),
        sa.Column('metadata', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_settings_history_setting_key'), 'settings_history', ['setting_key'], unique=False)


def downgrade() -> None:
    # Drop indexes and tables
    op.drop_index(op.f('ix_settings_history_setting_key'), table_name='settings_history')
    op.drop_table('settings_history')

    op.drop_index(op.f('ix_settings_category'), table_name='settings')
    op.drop_index(op.f('ix_settings_key'), table_name='settings')
    op.drop_table('settings')
