"""Initial for the application, import and setup the necessary extensions."""

from flask import Flask
from flask_compress import Compress
from flask_mail import Mail
from flask_login import LoginManager
from flask_redislite import FlaskRedis
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from . import FrequencyTaskChecker


# pylint: disable=C0103
app = Flask(__name__)

Compress(app)

config = app.config
app.config.from_envvar('CONFIG_FILE')

db = SQLAlchemy(app)
rdb = FlaskRedis(app, collections=True, rq=True)

lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'
lm.session_protection = "strong"
lm.login_message = "Please log in to continue!"
lm.login_message_category = "alert-danger"

mail = Mail(app)

socket_io = SocketIO(app)

with app.app_context():
    rdb.start_worker()

FrequencyTaskChecker.start(60, app.config.get('FREQUENCY_PID', 'frequency.pid'))

from DanceCat import Views, ErrorViews, Socket

# pylint: enable=C0103
