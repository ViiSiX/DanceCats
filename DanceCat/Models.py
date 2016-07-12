"""
Docstring for DanceCat.Models module.

This module contains the Models which is extended from
SQLAlchemy's Base Model.
"""

import datetime
from dateutil.relativedelta import relativedelta
from flask_login import UserMixin
from DanceCat import db, config
from . import Helpers
from . import Constants


# pylint: disable=C0103,R0902

class AllowedEmail(db.Model):
    """
    Docstring for AllowedEmail class.

    AllowedEmail Model indicate which email
    will be allowed to register new user.
    """

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), index=True, unique=True, nullable=False)
    version = db.Column(db.String(255), index=True, nullable=False)

    def __init__(self, allowed_email):
        """
        Constructor for AllowedEmail class.

        :param allowed_email:
            The email that will be allow to
            register a new user.
        """
        self.email = allowed_email
        self.version = Constants.MODEL_ALLOWED_EMAIL_VERSION

    def __repr__(self):
        """Print allowed email address."""
        return '{email}'.format(email=self.email)


class User(UserMixin, db.Model):
    """
    Docstring for User Model class.

    The User class represent for the User table
    contain a user's information.
    """

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), index=True, unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    isActive = db.Column(db.Boolean, nullable=False, default=True)
    createdOn = db.Column(db.DateTime, default=datetime.datetime.now)
    lastLogin = db.Column(db.DateTime, nullable=True)
    lastUpdated = db.Column(db.DateTime,
                            onupdate=datetime.datetime.now,
                            default=datetime.datetime.now)
    version = db.Column(db.Integer, index=True, nullable=False)

    connections = db.relationship('Connection', backref='User', lazy='joined')
    jobs = db.relationship('Job', backref='User', lazy='joined')

    def __init__(self, user_email, user_password):
        """
        Constructor for User class.

        :param user_email: User's email.
        :param user_password: User's password in clear text.
        """
        self.email = user_email
        self.password = Helpers.encrypt_password(user_password)
        self.version = Constants.MODEL_USER_VERSION

    @property
    def is_active(self):
        """Check if the user is active or not - Flask-Login method."""
        return self.isActive

    @property
    def is_anonymous(self):
        """Return True if user is anonymous - Flask-Login method."""
        return False

    def get_id(self):
        """Get the user id in unicode string."""
        try:
            return unicode(self.id)
        except NameError:
            return str(self.id)

    def __repr__(self):
        """Print the User instance."""
        return '<User %r - Id %r>' % (self.email, self.id)


class Connection(db.Model):
    """
    Docstring for Connection Model class.

    Connection Model class represent for the connection table
    which is used to store the connections to the Databases.
    """

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.SmallInteger, nullable=False)
    host = db.Column(db.String(100), nullable=False)
    port = db.Column(db.Integer, nullable=True)
    userName = db.Column(db.String(100), nullable=False)
    password = db.Column(db.TEXT, nullable=True)
    database = db.Column(db.String(100), nullable=False)
    userId = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    lastUpdated = db.Column(db.DateTime,
                            onupdate=datetime.datetime.now,
                            default=datetime.datetime.now)
    version = db.Column(db.Integer, index=True, nullable=False)

    jobs = db.relationship('Job', backref='Connection', lazy='joined')

    def __init__(self, db_type, host, database, creator_user_id, **kwargs):
        """
        Constructor for Connection class.

        :param db_type:
            Database Type which is defined in Constant module.
        :param host:
            Database host.
        :param database:
            Database name.
        :param creator_user_id:
            Id of user which create this connection.
        :param kwargs:
            name: Name of the connection.
            port: Port of the database if different to the default port.
            user_name: User which is used to connect to the database.
            password: Password which is used to connect to the database.
        """
        self.name = kwargs.get(
            'name',
            "{host} - {db}".format(host=host, db=database)
        )
        self.type = db_type
        self.host = host
        self.database = database
        self.port = kwargs.get('port')
        self.userName = kwargs.get('user_name')
        self.encrypt_password(kwargs.get('password'))
        self.userId = creator_user_id
        self.version = Constants.MODEL_CONNECTION_VERSION

    def encrypt_password(self, password):
        """Encrypt the clear text password."""
        self.password = Helpers.db_credential_encrypt(
            password, config['DB_ENCRYPT_KEY']
        ) if password else None

    def db_config_generator(self):
        """
        Generate database config.

        Generate the database configuration which will
        be passed to DatabaseConnector class's constructor.
        """
        db_config = {
            'user': self.userName,
            'host': self.host,
            'database': self.database,
            'port':
                self.port if self.port
                else Constants.CONNECTION_TYPES_DICT[self.type]['default_port']
        }

        # If no password leave it alone
        if self.password is not None:
            db_config['password'] = \
                Helpers.db_credential_decrypt(
                    self.password, config['DB_ENCRYPT_KEY']
                )

        return db_config

    def __repr__(self):
        """Print the Connection instance."""
        return '<Connection "{name}" - Id {id}>'.format(
            name=self.name, id=self.id
        )


class Job(db.Model):
    """
    Docstring for Job Model class.

    Job Model class represent for job table which is used to
    store the get data job's information.
    """

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    annotation = db.Column(db.Text)
    connectionId = db.Column(db.Integer, db.ForeignKey('connection.id'), nullable=False)
    queryString = db.Column(db.Text, nullable=False)
    userId = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    createdOn = db.Column(db.DateTime, default=datetime.datetime.now)
    lastUpdated = db.Column(db.DateTime,
                            onupdate=datetime.datetime.now,
                            default=datetime.datetime.now)
    noOfExecuted = db.Column(db.Integer, default=0, nullable=False)
    version = db.Column(db.Integer, index=True, nullable=False)

    emails = db.relationship('JobMailTo',
                             primaryjoin="and_(Job.id==JobMailTo.jobId, "
                                         "JobMailTo.enable==True)",
                             backref='Job',
                             lazy='joined')

    def __init__(self, name, connection_id, query_string, **kwargs):
        """
        Constructor for Job.

        :param name:
            Job's name.
        :param connection_id:
            Connection's Id, reference to Connection Model.
        :param query_string:
            Job's query which will be executed again the database.
        :param kwargs:
            user_id: Job's creator's User Id.
            annotation: Job's description and annotation.
        """
        self.name = name
        self.annotation = kwargs.get('annotation')
        self.connectionId = connection_id
        self.queryString = query_string
        self.userId = kwargs['user_id']
        self.version = Constants.MODEL_JOB_VERSION

    def update_executed_times(self):
        """Update Job's total executed times."""
        self.noOfExecuted += 1

    def __repr__(self):
        """Print the Job instance."""
        return '<Job "{name}" - Id {id}>'.format(
            name=self.name, id=self.id
        )


class Schedule(db.Model):
    """
    Schedule Model class represent for the schedule table.

    Schedule type:
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
        """
        Input and validate schedule.

        :param job_id:
            Scheduled Job's Id.
        :param schedule_type:
            Schedule type, see in the class's docstring.
        :param kwargs:
            is_active: this schedule is active or not.
            minute_of_hour: example 59.
            hour_of_day: example 23.
            day_of_week: example 5.
            day_of_month: example 28.
            next_run: datetime instance.
        """
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
        Validate the schedule.

        :return: True if the schedule will be run on the feature else False.
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
        """Update the next time this job will be run."""
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

    def __repr__(self):
        """Print the Schedule instance."""
        return '<Schedule Id {id} of Job Id {jobId}>'.format(
            id=self.id, jobId=self.jobId
        )


class TrackJobRun(db.Model):
    """Track status whenever a job is running."""

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    jobId = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)
    scheduleId = db.Column(db.Integer, db.ForeignKey('schedule.id'), nullable=True)
    scheduledOn = db.Column(db.DateTime, default=datetime.datetime.now, nullable=False)
    ranOn = db.Column(db.DateTime, nullable=True)
    duration = db.Column(db.Integer, default=0, nullable=False)
    status = db.Column(db.SmallInteger, default=Constants.JOB_QUEUED, nullable=False)
    errorString = db.Column(db.Text, nullable=True)
    version = db.Column(db.Integer, index=True, nullable=False)

    def __init__(self, job_id, schedule_id=None):
        """
        Call when enqueue a job.

        :param job_id:
            Running Job's Id.
        :param schedule_id:
            Running Schedule's Id.
        """
        self.jobId = job_id
        self.scheduleId = schedule_id
        self.version = Constants.MODEL_TRACK_JOB_RUN_VERSION

    def start(self):
        """Call to track when the Job begin to run."""
        self.ranOn = datetime.datetime.now()
        self.status = Constants.JOB_RUNNING

    def complete(self, is_success, run_duration, error_string=None):
        """
        Call whenever a job is completed.

        :param is_success: Is the job success.
        :param run_duration: Runtime in milliseconds.
        :param error_string: Error when the job is failed.
        """
        self.status = Constants.JOB_RAN_SUCCESS if is_success else Constants.JOB_RAN_FAILED
        self.duration = run_duration
        self.errorString = error_string

    def check_expiration(self):
        """
        Check and update result expiration.

        :return: True if the result is expiring.
                 False if the result is still valid or expired.
        """
        if self.status != Constants.JOB_RAN_SUCCESS:
            return False

        time_delta = self.duration + ((
            datetime.datetime.now() - self.ranOn
        ).total_seconds() * 1000)

        if self.status == Constants.JOB_RAN_SUCCESS\
                and time_delta > config.get('JOB_RESULT_VALID_SECONDS', 86400) * 1000:
            self.status = Constants.JOB_RESULT_EXPIRED
            return True

        return False

    def __repr__(self):
        """Print the Job Tracker instance."""
        return '<Tracker {id}: Job Id {jobId} {status}>'.format(
            id=self.id, jobId=self.jobId,
            status=Constants.JOB_TRACKING_STATUS_DICT[self.status]['name']
        )


class JobMailTo(db.Model):
    """Emails which the result will be sent to."""

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    jobId = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)
    emailAddress = db.Column(db.String(100), nullable=False)
    enable = db.Column(db.Boolean, default=True, nullable=False)

    __table_args__ = (
        db.UniqueConstraint('jobId', 'emailAddress', name='job_email_unq'),
    )

    def __init__(self, job_id, email_address):
        """
        Docstring for JobMailTo Model constructor.

        :param job_id:
            Job's Id.
        :param email_address:
            Email which will receive the results.
        """
        self.jobId = job_id
        self.emailAddress = email_address

    def __repr__(self):
        """Print the email."""
        return '{email_address}'.format(
            email_address=self.emailAddress
        )

# pylint: enable=C0103,R0902
