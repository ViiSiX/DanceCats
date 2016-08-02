"""Use to generate migration scripts."""
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from DanceCat import app, db


# pylint: disable=C0103,W0611
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

from DanceCat import Models

# pylint: enable=C0103,W0611

if __name__ == '__main__':
    manager.run()
