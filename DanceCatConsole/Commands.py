"""This module include commands for DanceCat."""

from __future__ import print_function
import time
import datetime
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from __init__ import app, db, Models, Constants


migrate = Migrate(app, db)
manager = Manager(app)


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
            db.session.commit()

        time.sleep(1)

        schedules = Models.Schedule.query.filter(
            Models.Schedule.is_active,
            Models.Schedule.next_run <= datetime.datetime.now()
        ).all()

    print("Finished!")


# Add Migrate commands.
manager.add_command('db', MigrateCommand)
