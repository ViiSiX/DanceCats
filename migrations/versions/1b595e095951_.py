"""Add is job and schedule isDeleted fields.

Revision ID: 1b595e095951
Revises: b85f81a9f3cf
Create Date: 2016-08-04 20:25:24.702258

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1b595e095951'
down_revision = 'b85f81a9f3cf'


def upgrade():
    """Add is job and schedule isDeleted fields."""
    op.add_column('job', sa.Column('isDeleted', sa.Boolean(), nullable=False))
    op.add_column('schedule', sa.Column('isDeleted', sa.Boolean(), nullable=False))


def downgrade():
    """Remove is job and schedule isDeleted fields."""
    op.drop_column('schedule', 'isDeleted')
    op.drop_column('job', 'isDeleted')
