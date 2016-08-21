"""Add Jobs' Features

Revision ID: 821afc6cf29b
Revises: 1b595e095951
Create Date: 2016-08-21 11:16:50.263313

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '821afc6cf29b'
down_revision = '1b595e095951'


def upgrade():
    """Add JobFeature table."""
    op.create_table('job_feature',
                    sa.Column('jobId', sa.Integer(), nullable=False),
                    sa.Column('featureName', sa.String(length=255), nullable=False),
                    sa.Column('featureValue', sa.String(length=255), nullable=False),
                    sa.Column('lastUpdated', sa.DateTime(), nullable=True),
                    sa.ForeignKeyConstraint(['jobId'], ['job.id'], ),
                    sa.PrimaryKeyConstraint('jobId', 'featureName')
    )


def downgrade():
    """Remove JobFeature table."""
    op.drop_table('job_feature')
