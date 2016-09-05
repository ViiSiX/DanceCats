"""This module include console commands for DanceCat."""

from __future__ import print_function
import datetime
import sqlalchemy.exc
from dateutil.relativedelta import relativedelta
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from .. import app, db, config, \
    Models, Constants, Helpers


# pylint: disable=C0103
migrate = Migrate(app, db)
manager = Manager(app)
# pylint: enable=C0103


@manager.command
def list_all():
    """List all commands."""
    print('Init database:')
    print('- db_create_all')

    print('Migrate Database')
    print('- db init')
    print('- db migrate')
    print('- db upgrade')
    print('- db downgrade')

    print('Connection')
    print('- connection_update_encryption')

    print('Scheduling')
    print('- schedule_update')

    return True


@manager.command
def db_create_all():
    """DanceCat database initial."""
    db.create_all()


@manager.command
def schedule_update():
    """Update outdated schedules on offline time."""
    schedules = Models.Schedule.query.filter(
        Models.Schedule.is_active,
        Models.Schedule.schedule_type != Constants.SCHEDULE_ONCE,
        Models.Schedule.next_run <= datetime.datetime.now()
    ).all()

    while len(schedules) > 0:
        for schedule in schedules:
            print(
                "Update next run time for schedule with id {id}.".format(
                    id=schedule.schedule_id
                )
            )
            schedule.update_next_run(True)
            schedule.next_run += relativedelta(minutes=1)
            db.session.commit()

        schedules = Models.Schedule.query.filter(
            Models.Schedule.is_active,
            Models.Schedule.next_run < datetime.datetime.now()
        ).all()

    print("Finished!")


@manager.command
def add_allowed_user(email):
    """
    Add given email to allowed_email table.

    :param email: Given email that will be allowed to create new user.
    :return: None.
    """
    try:
        allowed_email = Models.AllowedEmail(email)
        db.session.add(allowed_email)
        db.session.commit()

        print("Added \"{email}\" to allowed users list.".format(
            email=email
        ))
    except sqlalchemy.exc.IntegrityError:
        print("\"{email}\" was already in the allowed users list.".format(
            email=email
        ))

    db.session.close()


@manager.command
def connection_upgrade():
    """Upgrade connections to new version."""
    old_connections = Models.Connection.query.filter(
        Models.Connection.version < Constants.MODEL_CONNECTION_VERSION
    ).all()

    for old_connection in old_connections:
        # Upgrade to version 2: Switch password encryption from
        # RC4 to AES.
        if old_connection.version < 2:
            print('Update connection {connection} to version 2.'.format(
                connection=old_connection
            ))

            old_connection.password = Helpers.aes_encrypt(
                Helpers.rc4_decrypt(
                    old_connection.password,
                    config['DB_ENCRYPT_KEY']
                ),
                config['DB_ENCRYPT_KEY']
            )
            old_connection.version = 2
            db.session.commit()

    print('Finished!')


# Add Migrate commands.
manager.add_command('db', MigrateCommand)
