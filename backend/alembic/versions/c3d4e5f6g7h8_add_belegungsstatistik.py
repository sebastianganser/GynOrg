"""add belegungsstatistik models

Revision ID: c3d4e5f6g7h8
Revises: 19fb7402e377
Create Date: 2026-03-18 17:05:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel

# revision identifiers, used by Alembic.
revision: str = 'c3d4e5f6g7h8'
down_revision: Union[str, None] = '19fb7402e377'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # stations
    op.create_table('stations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False),
        sa.Column('color', sqlmodel.sql.sqltypes.AutoString(length=7), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # station_capacities
    op.create_table('station_capacities',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('station_id', sa.Integer(), nullable=False),
        sa.Column('valid_from', sa.Date(), nullable=False),
        sa.Column('valid_to', sa.Date(), nullable=True),
        sa.Column('plan_beds', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['station_id'], ['stations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # daily_entries
    op.create_table('daily_entries',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('station_id', sa.Integer(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('occupied', sa.Integer(), nullable=False),
        sa.Column('admissions', sa.Integer(), nullable=False),
        sa.Column('discharges', sa.Integer(), nullable=False),
        sa.Column('blocked_beds', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['station_id'], ['stations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # daily_fremd
    op.create_table('daily_fremd',
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('count', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('date')
    )

    # calendar_tags
    op.create_table('calendar_tags',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tag_name', sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False),
        sa.Column('tag_category', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('is_automatic', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # day_tags
    op.create_table('day_tags',
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('tag_id', sa.Integer(), nullable=False),
        sa.Column('source', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('comment', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['tag_id'], ['calendar_tags.id'], ),
        sa.PrimaryKeyConstraint('date', 'tag_id')
    )

    # tag_multipliers
    op.create_table('tag_multipliers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tag_id', sa.Integer(), nullable=False),
        sa.Column('metric', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('multiplier', sa.Float(), nullable=False),
        sa.Column('sample_size', sa.Integer(), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('last_calculated', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['tag_id'], ['calendar_tags.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('tag_multipliers')
    op.drop_table('day_tags')
    op.drop_table('calendar_tags')
    op.drop_table('daily_fremd')
    op.drop_table('daily_entries')
    op.drop_table('station_capacities')
    op.drop_table('stations')
