"""update station is_internal

Revision ID: d4e5f6g7h8i9
Revises: c3d4e5f6g7h8
Create Date: 2026-03-18 22:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel

# revision identifiers, used by Alembic.
revision: str = 'd4e5f6g7h8i9'
down_revision: Union[str, None] = 'c3d4e5f6g7h8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('stations', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_internal', sa.Boolean(), server_default=sa.text('true'), nullable=False))
        batch_op.drop_column('color')


def downgrade() -> None:
    with op.batch_alter_table('stations', schema=None) as batch_op:
        batch_op.add_column(sa.Column('color', sa.String(length=7), nullable=True))
        batch_op.drop_column('is_internal')
