"""Test script for DanceCatConsole."""

from __future__ import print_function
import os
import pytest
import datetime
from dateutil.relativedelta import relativedelta
from os import remove
from sqlalchemy import inspect
from DanceCat import Console


@pytest.fixture
def app():
    """Test fixture to set app config and remove previous test files."""
    db_file_path = os.path.join(os.getcwd() + '/var/test.db')

    Console.app.config.update({
        'SQLALCHEMY_DATABASE_URI': ('sqlite:///' + db_file_path),
        'SQLALCHEMY_TRACK_MODIFICATIONS': False
    })

    try:
        remove(db_file_path)
    except OSError:
        pass

    return Console.app


@pytest.fixture
def user_email():
    """Return test email."""
    return 'test@test.test'


def test_list_commands():
    """Test for full coverage."""
    Console.list_all()


def test_db_create_all(app):
    """Test db_create_all command."""
    print(app)
    assert app.config.get('SQLALCHEMY_DATABASE_URI') is not None

    Console.db_create_all()

    tables_list = inspect(Console.db.engine).get_table_names()

    for table in Console.db.metadata.tables.items():
        assert table[0] in tables_list


def test_schedule_update(app, user_email):
    """Test schedule_update command."""
    assert app.config.get('SQLALCHEMY_DATABASE_URI') is not None

    Console.db_create_all()

    allowed_email = Console.Models.AllowedEmail(user_email)
    Console.db.session.add(allowed_email)
    Console.db.session.commit()
    assert allowed_email.email is not None

    user = Console.Models.User(user_email, '123456')
    Console.db.session.add(user)
    Console.db.session.commit()
    assert user.user_id is not None

    connection = Console.Models.Connection(
        Console.Constants.MYSQL,
        'localhost',
        'test_db',
        user.user_id,
        user_name='db_user'
    )
    Console.db.session.add(connection)
    Console.db.session.commit()
    assert connection.connection_id is not None

    job = Console.Models.Job(
        'test job',
        'select * from table_1',
        user.user_id
    )
    Console.db.session.add(job)
    Console.db.session.commit()
    assert job.job_id is not None

    outdated_schedule = Console.Models.Schedule(
        job_id=job.job_id,
        start_time=datetime.datetime.now(),
        user_id=user.user_id,
        is_active=True,
        schedule_type=Console.Constants.SCHEDULE_DAILY
    )
    Console.db.session.add(outdated_schedule)
    Console.db.session.commit()
    assert outdated_schedule.schedule_id is not None

    outdated_schedule.next_run -= relativedelta(hours=1)
    Console.db.session.commit()
    assert outdated_schedule.next_run < datetime.datetime.now()

    Console.schedule_update()

    updated_schedule = Console.Models.Schedule.query.get(
        outdated_schedule.schedule_id
    )
    assert updated_schedule.next_run >= datetime.datetime.now()
