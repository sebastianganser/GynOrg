"""add holiday half day settings

Revision ID: e5f6g7h8i9j0
Revises: d4e5f6g7h8i9
Create Date: 2026-03-19 16:15:00.000000

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel

# revision identifiers, used by Alembic.
revision = 'e5f6g7h8i9j0'
down_revision = 'd4e5f6g7h8i9'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Add columns to calendar_settings
    op.add_column('calendar_settings', sa.Column('employer_federal_state', sqlmodel.sql.sqltypes.AutoString(), server_default='NORDRHEIN_WESTFALEN', nullable=False))
    op.add_column('calendar_settings', sa.Column('dec_24_is_half_day', sa.Boolean(), server_default='true', nullable=False))
    op.add_column('calendar_settings', sa.Column('dec_31_is_half_day', sa.Boolean(), server_default='true', nullable=False))

    # Add columns to absences
    op.add_column('absences', sa.Column('half_day_time', sqlmodel.sql.sqltypes.AutoString(), nullable=True))
    op.add_column('absences', sa.Column('duration_days', sa.Float(), server_default='0', nullable=False))

def downgrade() -> None:
    # Remove columns from absences
    op.drop_column('absences', 'duration_days')
    op.drop_column('absences', 'half_day_time')

    # Remove columns from calendar_settings
    op.drop_column('calendar_settings', 'dec_31_is_half_day')
    op.drop_column('calendar_settings', 'dec_24_is_half_day')
    op.drop_column('calendar_settings', 'employer_federal_state')
