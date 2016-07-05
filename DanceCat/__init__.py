from flask import Flask
from flask_compress import Compress
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_socketio import SocketIO
from flask_redislite import FlaskRedis
from FrequencyTaskChecker import frequency_checker
from multiprocessing import Process


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

socket_io = SocketIO(app)

# frequency_task_checker(5)
try:
    worker_pid_file = open(app.config.get('WORKER_PID'))
    worker_pid = int(worker_pid_file.read())
    worker_pid_file.close()
except IOError:
    def worker_wrapper(worker_instance, pid_path):
        import atexit
        import signal
        from os import remove

        def exit_handler():
            remove(pid_path)

        def signal_handler(signum, frame):
            remove(pid_path)

        atexit.register(exit_handler)
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        worker_instance.work()

        remove(pid_path)


    with app.app_context():
        worker = rdb.get_worker()
        p = Process(target=worker_wrapper, kwargs={
            'worker_instance': worker,
            'pid_path': app.config.get('WORKER_PID')
        })
        p.start()
        worker_pid_file = open(app.config.get('WORKER_PID'), 'w')
        worker_pid_file.write("%d" % p.pid)
        worker_pid_file.close()

from DanceCat import Models, Views, ErrorViews, Socket
