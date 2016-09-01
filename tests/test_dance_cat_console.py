"""Test script for DanceCatConsole."""

from __future__ import print_function
import os
import pytest
import datetime
from dateutil.relativedelta import relativedelta
from os import remove
from sqlalchemy import inspect
from DanceCat import Console


db_test_path = os.getcwd() + '/.test_console'
if not os.path.exists(db_test_path):
    os.mkdir(db_test_path)


@pytest.fixture
def app():
    """Test fixture to set app config and remove previous test files."""
    db_file_path = db_test_path + '/test_console.db'

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
    assert app.config.get('SQLALCHEMY_DATABASE_URI')

    Console.db_create_all()

    tables_list = inspect(Console.db.engine).get_table_names()

    for table in Console.db.metadata.tables.items():
        assert table[0] in tables_list


def test_add_allowed_user(app, user_email, capfd):
    """Test add_allowed_user command."""
    assert app.config.get('SQLALCHEMY_DATABASE_URI')

    Console.db_create_all()

    Console.add_allowed_user(user_email)
    out, err = capfd.readouterr()
    assert out == 'Added "{email}" to allowed users list.\n'.format(
        email=user_email
    )

    Console.add_allowed_user(user_email)
    out, err = capfd.readouterr()
    assert out == '"{email}" was already in the allowed users list.\n'.\
        format(
            email=user_email
        )


def test_schedule_update(app, user_email):
    """Test schedule_update command."""
    assert app.config.get('SQLALCHEMY_DATABASE_URI')

    Console.db_create_all()

    allowed_email = Console.Models.AllowedEmail(user_email)
    Console.db.session.add(allowed_email)
    Console.db.session.commit()
    assert allowed_email.email

    user = Console.Models.User(user_email, '123456')
    Console.db.session.add(user)
    Console.db.session.commit()
    assert user.user_id

    connection = Console.Models.Connection(
        Console.Constants.DB_MYSQL,
        'localhost',
        'test_db',
        user.user_id,
        user_name='db_user'
    )
    Console.db.session.add(connection)
    Console.db.session.commit()
    assert connection.connection_id

    job = Console.Models.Job(
        'test job',
        'select * from table_1',
        user.user_id
    )
    Console.db.session.add(job)
    Console.db.session.commit()
    assert job.job_id

    outdated_schedule = Console.Models.Schedule(
        job_id=job.job_id,
        start_time=datetime.datetime.now(),
        user_id=user.user_id,
        is_active=True,
        schedule_type=Console.Constants.SCHEDULE_DAILY
    )
    Console.db.session.add(outdated_schedule)
    Console.db.session.commit()
    assert outdated_schedule.schedule_id

    outdated_schedule.next_run -= relativedelta(hours=1)
    Console.db.session.commit()
    assert outdated_schedule.next_run < datetime.datetime.now()

    Console.schedule_update()

    updated_schedule = Console.Models.Schedule.query.get(
        outdated_schedule.schedule_id
    )
    assert updated_schedule.next_run >= datetime.datetime.now()
