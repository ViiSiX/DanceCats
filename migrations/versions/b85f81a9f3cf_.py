"""empty message

Revision ID: b85f81a9f3cf
Revises: None
Create Date: 2016-08-01 22:40:16.978187

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b85f81a9f3cf'
down_revision = None


def upgrade():
    """Add lastUpdatedColumn to Schedule."""
    op.add_column('schedule', sa.Column('lastUpdated', sa.DateTime(), nullable=True))


def downgrade():
    """Remove lastUpdatedColumn from Schedule."""
    op.drop_column('schedule', 'lastUpdated')
