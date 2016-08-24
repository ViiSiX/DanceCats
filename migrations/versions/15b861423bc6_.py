"""Database Initialization.

Revision ID: 15b861423bc6
Revises: None
Create Date: 2016-08-24 17:58:08.367413

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '15b861423bc6'
down_revision = None


def upgrade():
    """Database Initialization."""
    op.create_table('allowed_email',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('email', sa.String(length=255), nullable=False),
                    sa.Column('version', sa.String(length=255), nullable=False),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index(op.f('ix_allowed_email_email'), 'allowed_email', ['email'], unique=True)
    op.create_index(op.f('ix_allowed_email_version'), 'allowed_email', ['version'], unique=False)

    op.create_table('user',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('email', sa.String(length=255), nullable=False),
                    sa.Column('password', sa.String(length=255), nullable=False),
                    sa.Column('isActive', sa.Boolean(), nullable=False),
                    sa.Column('createdOn', sa.DateTime(), nullable=True),
                    sa.Column('lastLogin', sa.DateTime(), nullable=True),
                    sa.Column('lastUpdated', sa.DateTime(), nullable=True),
                    sa.Column('version', sa.Integer(), nullable=False),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)
    op.create_index(op.f('ix_user_version'), 'user', ['version'], unique=False)

    op.create_table('connection',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('name', sa.String(length=100), nullable=False),
                    sa.Column('type', sa.SmallInteger(), nullable=False),
                    sa.Column('host', sa.String(length=100), nullable=False),
                    sa.Column('port', sa.Integer(), nullable=True),
                    sa.Column('userName', sa.String(length=100), nullable=False),
                    sa.Column('password', sa.TEXT(), nullable=True),
                    sa.Column('database', sa.String(length=100), nullable=False),
                    sa.Column('userId', sa.Integer(), nullable=False),
                    sa.Column('lastUpdated', sa.DateTime(), nullable=True),
                    sa.Column('version', sa.Integer(), nullable=False),
                    sa.ForeignKeyConstraint(['userId'], ['user.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index(op.f('ix_connection_version'), 'connection', ['version'], unique=False)

    op.create_table('job',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('name', sa.String(length=100), nullable=False),
                    sa.Column('annotation', sa.Text(), nullable=True),
                    sa.Column('connectionId', sa.Integer(), nullable=True),
                    sa.Column('commands', sa.Text(), nullable=False),
                    sa.Column('userId', sa.Integer(), nullable=False),
                    sa.Column('createdOn', sa.DateTime(), nullable=True),
                    sa.Column('lastUpdated', sa.DateTime(), nullable=True),
                    sa.Column('noOfExecuted', sa.Integer(), nullable=False),
                    sa.Column('jobType', sa.SmallInteger(), nullable=False),
                    sa.Column('version', sa.Integer(), nullable=False),
                    sa.ForeignKeyConstraint(['connectionId'], ['connection.id'], ),
                    sa.ForeignKeyConstraint(['userId'], ['user.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index(op.f('ix_job_version'), 'job', ['version'], unique=False)

    op.create_table('job_mail_to',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('jobId', sa.Integer(), nullable=False),
                    sa.Column('emailAddress', sa.String(length=100), nullable=False),
                    sa.Column('enable', sa.Boolean(), nullable=False),
                    sa.ForeignKeyConstraint(['jobId'], ['job.id'], ),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('jobId', 'emailAddress', name='job_email_unq')
                    )

    op.create_table('schedule',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('jobId', sa.Integer(), nullable=False),
                    sa.Column('isActive', sa.Boolean(), nullable=False),
                    sa.Column('minuteOfHour', sa.SmallInteger(), nullable=False),
                    sa.Column('hourOfDay', sa.SmallInteger(), nullable=False),
                    sa.Column('dayOfWeek', sa.SmallInteger(), nullable=False),
                    sa.Column('dayOfMonth', sa.SmallInteger(), nullable=False),
                    sa.Column('scheduleType', sa.SmallInteger(), nullable=False),
                    sa.Column('nextRun', sa.DateTime(), nullable=True),
                    sa.Column('userId', sa.Integer(), nullable=False),
                    sa.Column('createdOn', sa.DateTime(), nullable=True),
                    sa.Column('version', sa.Integer(), nullable=False),
                    sa.ForeignKeyConstraint(['jobId'], ['job.id'], ),
                    sa.ForeignKeyConstraint(['userId'], ['user.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index(op.f('ix_schedule_version'), 'schedule', ['version'], unique=False)

    op.create_table('track_job_run',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('jobId', sa.Integer(), nullable=False),
                    sa.Column('scheduleId', sa.Integer(), nullable=True),
                    sa.Column('scheduledOn', sa.DateTime(), nullable=False),
                    sa.Column('ranOn', sa.DateTime(), nullable=True),
                    sa.Column('duration', sa.Integer(), nullable=False),
                    sa.Column('status', sa.SmallInteger(), nullable=False),
                    sa.Column('errorString', sa.Text(), nullable=True),
                    sa.Column('version', sa.Integer(), nullable=False),
                    sa.ForeignKeyConstraint(['jobId'], ['job.id'], ),
                    sa.ForeignKeyConstraint(['scheduleId'], ['schedule.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index(op.f('ix_track_job_run_version'), 'track_job_run', ['version'], unique=False)


def downgrade():
    """Drop everything."""
    op.drop_index(op.f('ix_track_job_run_version'), table_name='track_job_run')
    op.drop_table('track_job_run')
    op.drop_index(op.f('ix_schedule_version'), table_name='schedule')
    op.drop_table('schedule')
    op.drop_table('job_mail_to')
    op.drop_index(op.f('ix_job_version'), table_name='job')
    op.drop_table('job')
    op.drop_index(op.f('ix_connection_version'), table_name='connection')
    op.drop_table('connection')
    op.drop_index(op.f('ix_user_version'), table_name='user')
    op.drop_index(op.f('ix_user_email'), table_name='user')
    op.drop_table('user')
    op.drop_index(op.f('ix_allowed_email_version'), table_name='allowed_email')
    op.drop_index(op.f('ix_allowed_email_email'), table_name='allowed_email')
    op.drop_table('allowed_email')
