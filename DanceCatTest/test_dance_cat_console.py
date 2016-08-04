"""Test script for DanceCatConsole."""

from __future__ import print_function
import os
import pytest
import datetime
from dateutil.relativedelta import relativedelta
from os import remove
from sqlalchemy import inspect
from DanceCatConsole import app as app_console, db, \
    Constants, Models, Commands


@pytest.fixture
def app():
    """Test fixture to set app config and remove previous test files."""
    db_file_path = os.path.join(os.getcwd() + '/var/test.db')

    app_console.config.update({
        'SQLALCHEMY_DATABASE_URI': ('sqlite:///' + db_file_path),
        'SQLALCHEMY_TRACK_MODIFICATIONS': False
    })

    try:
        remove(db_file_path)
    except OSError:
        pass

    return app_console


@pytest.fixture
def user_email():
    """Return test email."""
    return 'test@test.test'


def test_db_create_all(app):
    """Test db_create_all command."""
    assert app.config.get('SQLALCHEMY_DATABASE_URI') is not None

    Commands.db_create_all()

    tables_list = inspect(db.engine).get_table_names()

    for table in db.metadata.tables.items():
        assert table[0] in tables_list


def test_schedule_update(app, user_email):
    """Test schedule_update command."""
    assert app.config.get('SQLALCHEMY_DATABASE_URI') is not None

    Commands.db_create_all()

    allowed_email = Models.AllowedEmail(user_email)
    db.session.add(allowed_email)
    db.session.commit()
    assert allowed_email.email is not None

    user = Models.User(user_email, '123456')
    db.session.add(user)
    db.session.commit()
    assert user.user_id is not None

    connection = Models.Connection(
        Constants.MYSQL,
        'localhost',
        'test_db',
        user.user_id,
        user_name='db_user'
    )
    db.session.add(connection)
    db.session.commit()
    assert connection.connection_id is not None

    job = Models.Job(
        'test job',
        'select * from table_1',
        user.user_id
    )
    db.session.add(job)
    db.session.commit()
    assert job.job_id is not None

    outdated_schedule = Models.Schedule(
        job_id=job.job_id,
        start_time=datetime.datetime.now(),
        user_id=user.user_id,
        is_active=True,
        schedule_type=Constants.SCHEDULE_DAILY
    )
    db.session.add(outdated_schedule)
    db.session.commit()
    assert outdated_schedule.schedule_id is not None

    outdated_schedule.next_run -= relativedelta(hours=1)
    db.session.commit()
    assert outdated_schedule.next_run < datetime.datetime.now()

    Commands.schedule_update()

    updated_schedule = Models.Schedule.query.get(outdated_schedule.schedule_id)
    assert updated_schedule.next_run >= datetime.datetime.now()
