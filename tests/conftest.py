"""Utils for DanceCats' unit tests ."""

import os
import datetime
import pytest
from DanceCats import app as dancecats_app
from DanceCats import db, Constants, Models


db_dir_path = os.path.dirname(os.path.realpath(__file__)) + '/.unittest'
if not os.path.exists(db_dir_path):
    os.mkdir(db_dir_path)
db_file_path = db_dir_path + '/test_db.db'


@pytest.fixture
def app():
    """Test fixture to set app config and remove previous test files."""
    if db.session:
        db.session.remove()

    dancecats_app.config.update({
        'SQLALCHEMY_DATABASE_URI': ('sqlite:///' + db_file_path),
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'DB_ENCRYPT_KEY': 'easy to guess!\\'
    })

    try:
        os.remove(db_file_path)
    except OSError:
        pass

    db.create_all()
    return dancecats_app


@pytest.fixture
def user_email():
    """Return test email."""
    return 'test@test.test'


@pytest.fixture
def freeze_datetime(monkeypatch):
    """Patch datetime.now function to return fixed timestamp."""
    original_datetime = datetime.datetime

    class FrozenDateTimeMeta(type):
        """Meta class for FrozenDateTime class."""
        def __instancecheck__(self, instance):
            return isinstance(instance, (original_datetime, FrozenDateTime))

    class FrozenDateTime(datetime.datetime):
        """Use freeze method to control result of datetime.datetime.now()."""
        __metaclass__ = FrozenDateTimeMeta

        @classmethod
        def freeze(cls, freezing_timestamp):
            """Freeze time at freezing_timestamp."""
            cls.frozen_time = freezing_timestamp

        @classmethod
        def now(cls, tz=None):
            """Return the frozen time."""
            return cls.frozen_time

    monkeypatch.setattr(datetime, 'datetime', FrozenDateTime)
    FrozenDateTime.freeze(original_datetime.now())
    return FrozenDateTime


@pytest.fixture
def app_setup_to_add_user(app, user_email):
    """Setup data to the point add new User."""
    allowed_email = Models.AllowedEmail(user_email)
    db.session.add(allowed_email)
    db.session.commit()

    user = Models.User(user_email, '123456')
    db.session.add(user)
    db.session.commit()

    return {
        'app': app,
        'user_id': user.user_id
    }


@pytest.fixture
def app_setup_to_add_job(app_setup_to_add_user):
    """Setup data so we can test Schedule Model."""
    connection = Models.Connection(
        Constants.DB_MYSQL,
        'localhost',
        'test_db',
        app_setup_to_add_user['user_id'],
        user_name='db_user'
    )
    db.session.add(connection)
    db.session.commit()

    job = Models.QueryDataJob(
        'test job',
        'select * from table_1',
        app_setup_to_add_user['user_id']
    )
    db.session.add(job)
    db.session.commit()

    ret = app_setup_to_add_user
    ret['job_id'] = job.job_id
    return ret
