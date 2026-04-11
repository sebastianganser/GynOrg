"""add goae extra fields

Revision ID: p6q7r8s9t0u1
Revises: o5p6q7r8s9t0
Create Date: 2026-04-02
"""
from alembic import op
import sqlalchemy as sa

revision = 'p6q7r8s9t0u1'
down_revision = 'o5p6q7r8s9t0'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('goae_ziffern', sa.Column('ausschlussziffern', sa.Text(), nullable=True))
    op.add_column('goae_ziffern', sa.Column('hinweistext', sa.Text(), nullable=True))
    op.add_column('goae_ziffern', sa.Column('detail_url', sa.Text(), nullable=True))
    # abschnitt max_length erweitern für 'ANALOG'
    op.alter_column('goae_ziffern', 'abschnitt',
                     type_=sa.String(length=10),
                     existing_type=sa.String(length=5))


def downgrade() -> None:
    op.drop_column('goae_ziffern', 'detail_url')
    op.drop_column('goae_ziffern', 'hinweistext')
    op.drop_column('goae_ziffern', 'ausschlussziffern')
    op.alter_column('goae_ziffern', 'abschnitt',
                     type_=sa.String(length=5),
                     existing_type=sa.String(length=10))
