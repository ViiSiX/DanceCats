"""Utils for DanceCat's unit tests ."""

import os
import pytest
from DanceCat import app as dancecat_app
from DanceCat import db


db_dir_path = os.path.dirname(os.path.realpath(__file__)) + '/.unittest'
if not os.path.exists(db_dir_path):
    os.mkdir(db_dir_path)
db_file_path = db_dir_path + '/test_db.db'


@pytest.fixture
def app():
    """Test fixture to set app config and remove previous test files."""
    if db.session:
        db.session.remove()

    dancecat_app.config.update({
        'SQLALCHEMY_DATABASE_URI': ('sqlite:///' + db_file_path),
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'DB_ENCRYPT_KEY': 'easy to guess!\\'
    })

    try:
        os.remove(db_file_path)
    except OSError:
        pass

    db.create_all()
    return dancecat_app


@pytest.fixture
def user_email():
    """Return test email."""
    return 'test@test.test'
