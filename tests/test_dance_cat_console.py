"""Unit tests for DanceCatConsole."""

from __future__ import print_function
import datetime
from dateutil.relativedelta import relativedelta
from sqlalchemy import inspect
from DanceCat import db
from DanceCat import Models
from DanceCat import Console
from DanceCat import Constants
from DanceCat import Helpers


def test_list_commands():
    """Test for full coverage."""
    Console.list_all()


def test_db_create_all(app):
    """Test db_create_all command."""
    assert app.config.get('SQLALCHEMY_DATABASE_URI')

    db.drop_all()
    Console.db_create_all()

    tables_list = inspect(db.engine).get_table_names()

    for table in db.metadata.tables.items():
        assert table[0] in tables_list


def test_add_allowed_user(app, user_email, capfd):
    """Test add_allowed_user command."""
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
    allowed_email = Models.AllowedEmail(user_email)
    db.session.add(allowed_email)
    db.session.commit()
    assert allowed_email.email

    user = Models.User(user_email, '123456')
    db.session.add(user)
    db.session.commit()
    assert user.user_id

    connection = Models.Connection(
        Constants.DB_MYSQL,
        'localhost',
        'test_db',
        user.user_id,
        user_name='db_user'
    )
    db.session.add(connection)
    db.session.commit()
    assert connection.connection_id

    job = Models.QueryDataJob(
        'test job',
        'select * from table_1',
        user.user_id
    )
    db.session.add(job)
    db.session.commit()
    assert job.job_id

    outdated_schedule = Models.Schedule(
        job_id=job.job_id,
        start_time=datetime.datetime.now(),
        user_id=user.user_id,
        is_active=True,
        schedule_type=Constants.SCHEDULE_DAILY
    )
    db.session.add(outdated_schedule)
    db.session.commit()
    assert outdated_schedule.schedule_id

    outdated_schedule.next_run -= relativedelta(hours=1)
    db.session.commit()
    assert outdated_schedule.next_run < datetime.datetime.now()

    Console.schedule_update()

    updated_schedule = Models.Schedule.query.get(
        outdated_schedule.schedule_id
    )
    assert updated_schedule.next_run >= datetime.datetime.now()


def test_connection_upgrade(app, user_email):
    """Test upgrading connections to new versions."""
    allowed_email = Models.AllowedEmail(user_email)
    db.session.add(allowed_email)
    db.session.commit()

    user = Models.User(user_email, '123456')
    db.session.add(user)
    db.session.commit()

    connection = Models.Connection(
        Constants.DB_MYSQL,
        'localhost',
        'test_db',
        user.user_id,
        user_name='db_user'
    )
    db.session.add(connection)
    db.session.commit()

    # Provide test data.
    connection_password = 'solar st0rm'
    connection.version = 1
    connection.password = Helpers.rc4_encrypt(
        connection_password,
        app.config.get('DB_ENCRYPT_KEY')
    )
    db.session.commit()

    Console.connection_upgrade()

    # Version 2
    updated_connection = Models.Connection.query.get(
        connection.connection_id
    )
    assert updated_connection.version >= 2
    assert Helpers.aes_decrypt(
        updated_connection.password,
        app.config.get('DB_ENCRYPT_KEY')
    ) == connection_password
