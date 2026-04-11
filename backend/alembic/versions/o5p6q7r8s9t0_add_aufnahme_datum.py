"""add aufnahme_datum to patienten

Revision ID: o5p6q7r8s9t0
Revises: i9j0k1l2m3n4
Create Date: 2026-04-02
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'o5p6q7r8s9t0'
down_revision = 'i9j0k1l2m3n4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('patienten', sa.Column('aufnahme_datum', sa.Date(), nullable=True))


def downgrade() -> None:
    op.drop_column('patienten', 'aufnahme_datum')
