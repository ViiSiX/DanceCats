from flask_login import UserMixin
from DanceCat import db, config, Helpers, Constants
from dateutil.relativedelta import relativedelta
import datetime


class AllowedEmail(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), index=True, unique=True, nullable=False)
    version = db.Column(db.String(255), index=True, nullable=False)

    def __init__(self, allowed_email):
        self.email = allowed_email
        self.version = Constants.MODEL_ALLOWED_EMAIL_VERSION

    def __repr__(self):
        return '<{email}>'.format(email=self.email)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), index=True, unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    isActive = db.Column(db.Boolean, nullable=False, default=True)
    createdOn = db.Column(db.DateTime, default=datetime.datetime.now)
    lastLogin = db.Column(db.DateTime, nullable=True)
    lastUpdated = db.Column(db.DateTime, onupdate=datetime.datetime.now, default=datetime.datetime.now)
    version = db.Column(db.Integer, index=True, nullable=False)

    connections = db.relationship('Connection', backref='User', lazy='joined')
    jobs = db.relationship('Job', backref='User', lazy='joined')

    def __init__(self, user_email, user_password):
        self.email = user_email
        self.password = Helpers.encrypt_password(user_password)
        self.version = Constants.MODEL_USER_VERSION

    @property
    def is_active(self):
        return self.isActive

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        try:
            return unicode(self.id)
        except NameError:
            return str(self.id)

    def __repr__(self):
        return '<User %r - Id %r>' % (self.email, self.id)


class Connection(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.SmallInteger, nullable=False)
    host = db.Column(db.String(100), nullable=False)
    port = db.Column(db.Integer, nullable=True)
    userName = db.Column(db.String(100), nullable=False)
    password = db.Column(db.TEXT, nullable=True)
    database = db.Column(db.String(100), nullable=False)
    userId = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    lastUpdated = db.Column(db.DateTime, onupdate=datetime.datetime.now, default=datetime.datetime.now)
    version = db.Column(db.Integer, index=True, nullable=False)

    jobs = db.relationship('Job', backref='Connection', lazy='joined')

    def __init__(self, name, db_type, host, database, user_name,
                 creator_user_id, port=None, password=None):
        self.name = name
        self.type = db_type
        self.host = host
        self.port = port
        self.userName = user_name
        self.encrypt_password(password)
        self.database = database
        self.userId = creator_user_id
        self.version = Constants.MODEL_CONNECTION_VERSION

    def encrypt_password(self, password):
        self.password = Helpers.db_credential_encrypt(password, config['DB_ENCRYPT_KEY']) if password else None

    def db_config_generator(self):
        db_config = {
            'user': self.userName,
            'host': self.host,
            'database': self.database,
            'port': self.port if self.port else Constants.CONNECTION_TYPES_DICT[self.type]['default_port']
        }

        # If no password leave it alone
        if self.password is not None:
            db_config['password'] = Helpers.db_credential_decrypt(self.password, config['DB_ENCRYPT_KEY'])

        return db_config

    def __repr__(self):
        return '<Connection "{name}" - Id {id}>'.format(
            name=self.name, id=self.id
        )


class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    annotation = db.Column(db.Text)
    connectionId = db.Column(db.Integer, db.ForeignKey('connection.id'), nullable=False)
    queryString = db.Column(db.Text, nullable=False)
    userId = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    createdOn = db.Column(db.DateTime, default=datetime.datetime.now)
    lastUpdated = db.Column(db.DateTime, onupdate=datetime.datetime.now, default=datetime.datetime.now)
    noOfExecuted = db.Column(db.Integer, default=0, nullable=False)
    version = db.Column(db.Integer, index=True, nullable=False)

    def __init__(self, name, connection_id, query_string, user_id, annotation):
        self.name = name
        self.annotation = annotation
        self.connectionId = connection_id
        self.queryString = query_string
        self.userId = user_id
        self.version = Constants.MODEL_JOB_VERSION

    def update_executed_times(self):
        self.noOfExecuted += 1

    def __repr__(self):
        return '<Job "{name}" - Id {id}>'.format(
            name=self.name, id=self.id
        )


class Schedule(db.Model):
    """
    Hourly: use minuteOfHour
    Daily: use minuteOfHour, hourOfDay
    Weekly: use minuteOfHour, hourOfDay and dayOfWeek;
        dayOfWeek: 0 - 6 as Monday to Sunday
    Monthly: use minuteOfHour, hourOfDay and dayOfMonth;
        dayOfMonth: 1-31
    Run once: nextRun in the future
    """
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    jobId = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)
    isActive = db.Column(db.Boolean, default=True, nullable=False)
    minuteOfHour = db.Column(db.SmallInteger, default=0, nullable=False)
    hourOfDay = db.Column(db.SmallInteger, default=0, nullable=False)
    dayOfWeek = db.Column(db.SmallInteger, default=0, nullable=False)
    dayOfMonth = db.Column(db.SmallInteger, default=1, nullable=False)
    scheduleType = db.Column(db.SmallInteger, default=Constants.SCHEDULE_ONCE, nullable=False)
    nextRun = db.Column(db.DateTime, nullable=True)
    userId = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    createdOn = db.Column(db.DateTime, default=datetime.datetime.now)
    version = db.Column(db.Integer, index=True, nullable=False)

    def __init__(self, job_id, schedule_type=0, **kwargs):
        self.jobId = job_id
        self.scheduleType = schedule_type
        self.isActive = kwargs.get('is_active', False)

        minute_of_hour = kwargs.get('minute_of_hour', 0)
        self.minuteOfHour = minute_of_hour if Helpers.validate_minute_of_hour(minute_of_hour) else 0

        hour_of_day = kwargs.get('hour_of_day', 0)
        self.hourOfDay = hour_of_day if Helpers.validate_hour_of_day(hour_of_day) else 0

        day_of_week = kwargs.get('day_of_week', 0)
        self.dayOfWeek = day_of_week if Helpers.validate_day_of_week(day_of_week) else 0

        day_of_month = kwargs.get('day_of_month', 0)
        self.dayOfMonth = day_of_month if Helpers.validate_day_of_month(day_of_month) else 0

        next_run = kwargs.get('next_run', None)
        if self.scheduleType == Constants.SCHEDULE_ONCE:
            if next_run is None:
                raise ValueError('Run once schedule require next run time!')
            else:
                self.nextRun = next_run
        else:
            self.update_next_run(True)

        self.version = Constants.MODEL_SCHEDULE_VERSION

    def validate(self):
        """
        :return: True if the schedule will be run on the feature else False
        """
        if self.scheduleType == Constants.SCHEDULE_ONCE:
            return self.nextRun > datetime.datetime.now()

        if self.scheduleType == Constants.SCHEDULE_HOURLY:
            return Helpers.validate_minute_of_hour(self.minuteOfHour)

        if self.scheduleType == Constants.SCHEDULE_DAILY:
            return Helpers.validate_minute_of_hour(self.minuteOfHour) \
                   and Helpers.validate_hour_of_day(self.hourOfDay)

        if self.scheduleType == Constants.SCHEDULE_WEEKLY:
            return Helpers.validate_minute_of_hour(self.minuteOfHour) \
                   and Helpers.validate_hour_of_day(self.hourOfDay) \
                   and Helpers.validate_day_of_week(self.dayOfWeek)

        if self.scheduleType == Constants.SCHEDULE_MONTHLY:
            return Helpers.validate_minute_of_hour(self.minuteOfHour) \
                   and Helpers.validate_hour_of_day(self.hourOfDay) \
                   and Helpers.validate_day_of_week(self.dayOfMonth)

    def update_next_run(self, validated=False):
        # TODO: Better algorithm
        if not validated:
            validated = self.validate()

        if not validated:
            raise ValueError('Schedule is not valid!')

        cur_time = datetime.datetime.now()
        next_run_time = datetime.datetime.now()

        if self.scheduleType == Constants.SCHEDULE_HOURLY:
            next_run_time += relativedelta(minute=self.minuteOfHour)

            if cur_time >= next_run_time:
                next_run_time += relativedelta(hours=1)

        elif self.scheduleType == Constants.SCHEDULE_DAILY:
            next_run_time += relativedelta(minute=self.minuteOfHour,
                                           hour=self.hourOfDay)

            if cur_time >= next_run_time:
                next_run_time += relativedelta(days=1)

        elif self.scheduleType == Constants.SCHEDULE_WEEKLY:
            next_run_time += relativedelta(minute=self.minuteOfHour,
                                           hour=self.hourOfDay,
                                           weekday=self.dayOfWeek)

            if cur_time >= next_run_time:
                next_run_time += relativedelta(weeks=1)

        elif self.scheduleType == Constants.SCHEDULE_MONTHLY:
            next_run_time += relativedelta(minute=self.minuteOfHour,
                                           hour=self.hourOfDay,
                                           day=self.dayOfMonth)

            if cur_time >= next_run_time:
                next_run_time += relativedelta(months=1)

        self.nextRun = next_run_time


class TrackJobRun(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    jobId = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)
    scheduleId = db.Column(db.Integer, db.ForeignKey('schedule.id'), nullable=True)
    runOn = db.Column(db.DateTime, default=datetime.datetime.now, nullable=False)
    duration = db.Column(db.Integer, default=0, nullable=False)
    status = db.Column(db.SmallInteger, default=0, nullable=False)
    version = db.Column(db.Integer, index=True, nullable=False)

    def __init__(self, job_id, schedule_id=None):
        self.jobId = job_id
        self.scheduleId = schedule_id
        self.version = Constants.MODEL_TRACK_JOB_RUN_VERSION

    def update_run_duration(self, run_duration):
        self.duration = run_duration

    def update_run_status(self, run_status):
        self.status = run_status
