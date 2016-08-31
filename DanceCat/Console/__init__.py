"""This module include console commands for DanceCat."""

from __future__ import print_function
import datetime
import sqlalchemy.exc
from dateutil.relativedelta import relativedelta
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from DanceCat import app, db, Models, Constants


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


# Add Migrate commands.
manager.add_command('db', MigrateCommand)
