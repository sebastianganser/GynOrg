"""add_job_positions

Revision ID: b2c3d4e5f6g7
Revises: a1b2c3d4e5f6
Create Date: 2026-02-27 13:50:00.000000

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel

# revision identifiers, used by Alembic.
revision = 'b2c3d4e5f6g7'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # 1. Create the new job_positions table
    op.create_table('job_positions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False),
    sa.Column('description', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
    sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_job_positions_name'), 'job_positions', ['name'], unique=False)

    # 2. Migrate existing position strings into the new table
    # This prevents users from losing their previously entered positions
    connection = op.get_bind()
    
    # Get all distinct positions from employees
    # Handle both cases: null and empty string by coalesce and nullif
    result = connection.execute(sa.text("SELECT DISTINCT position FROM employees WHERE position IS NOT NULL AND position != ''"))
    existing_positions = [row[0] for row in result]
    
    for pos_name in existing_positions:
        # Insert them into the new table
        connection.execute(
            sa.text("INSERT INTO job_positions (name) VALUES (:name) ON CONFLICT DO NOTHING"),
            {"name": pos_name}
        )

def downgrade() -> None:
    # Drop the table
    op.drop_index(op.f('ix_job_positions_name'), table_name='job_positions')
    op.drop_table('job_positions')
