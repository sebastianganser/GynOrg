"""refactor absence types

Revision ID: g7h8i9j0k1l2
Revises: f6g7h8i9j0k1
Create Date: 2026-03-31 16:45:00.000000

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision = 'g7h8i9j0k1l2'
down_revision = 'f6g7h8i9j0k1'
branch_labels = None
depends_on = None


def upgrade():
    # First, truncate/delete existing data so we don't violate foreign keys 
    # and because the user requested a clean slate
    op.execute('DELETE FROM absences')
    op.execute('DELETE FROM absence_types')

    # Add new column
    op.add_column('absence_types', sa.Column('is_vacation', sa.Boolean(), server_default=sa.text('false'), nullable=False))
    
    # Remove old columns
    op.drop_column('absence_types', 'category')
    op.drop_column('absence_types', 'description')


def downgrade():
    op.add_column('absence_types', sa.Column('description', sa.VARCHAR(length=500), autoincrement=False, nullable=True))
    op.add_column('absence_types', sa.Column('category', sa.VARCHAR(length=50), autoincrement=False, nullable=True))
    op.drop_column('absence_types', 'is_vacation')
