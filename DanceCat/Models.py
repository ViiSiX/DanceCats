"""
Docstring for DanceCat.Models module.

This module contains the Models which is extended from
SQLAlchemy's Base Model.
"""

from __future__ import unicode_literals
import datetime
from dateutil.relativedelta import relativedelta
from flask_login import UserMixin
from sqlalchemy import and_, not_
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.associationproxy import association_proxy
from DanceCat import db, config
from . import Helpers
from . import Constants


# pylint: disable=R0902

class ProxiedDictMixin(object):
    """Adds obj[key] access to a mapped class.

    This class basically proxies dictionary access to an attribute
    called ``_proxied``.  The class which inherits this class
    should have an attribute called ``_proxied`` which points to a dictionary.

    """

    def __len__(self):
        return len(self._proxied)

    def __iter__(self):
        return iter(self._proxied)

    def __getitem__(self, key):
        return self._proxied[key]

    def __contains__(self, key):
        return key in self._proxied

    def __setitem__(self, key, value):
        self._proxied[key] = value

    def __delitem__(self, key):
        del self._proxied[key]


class AllowedEmail(db.Model):
    """
    Docstring for AllowedEmail class.

    AllowedEmail Model indicate which email
    will be allowed to register new user.
    """

    allowed_email_id = db.Column('id', db.Integer,
                                 primary_key=True, autoincrement=True
                                 )
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

    user_id = db.Column('id', db.Integer,
                        primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), index=True, unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    is_active = db.Column('isActive', db.Boolean,
                          nullable=False, default=True)
    created_on = db.Column('createdOn', db.DateTime,
                           default=datetime.datetime.now)
    last_login = db.Column('lastLogin', db.DateTime, nullable=True)
    last_updated = db.Column('lastUpdated',
                             db.DateTime,
                             onupdate=datetime.datetime.now,
                             default=datetime.datetime.now)
    version = db.Column(db.Integer, index=False, nullable=False)

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
    def is_anonymous(self):
        """Return True if user is anonymous - Flask-Login method."""
        return False

    def get_id(self):
        """Get the user id in unicode string."""
        try:
            return unicode(self.user_id)
        except NameError:
            return str(self.user_id)

    def __repr__(self):
        """Print the User instance."""
        return '<User {email} - Id {id}>'.format(
            email=self.email,
            id=self.user_id
        )


class Connection(db.Model):
    """
    Docstring for Connection Model class.

    Connection Model class represent for the connection table
    which is used to store the connections to the Databases.
    """

    connection_id = db.Column('id', db.Integer,
                              primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.SmallInteger, nullable=False)
    host = db.Column(db.String(100), nullable=False)
    port = db.Column(db.Integer, nullable=True)
    user_name = db.Column('userName', db.String(100), nullable=False)
    password = db.Column(db.TEXT, nullable=True)
    database = db.Column(db.String(100), nullable=False)
    user_id = db.Column('userId', db.Integer,
                        db.ForeignKey('user.id'), nullable=False)
    last_updated = db.Column('lastUpdated',
                             db.DateTime,
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
        self.user_name = kwargs.get('user_name')
        self.encrypt_password(kwargs.get('password'))
        self.user_id = creator_user_id
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
            'user': self.user_name,
            'host': self.host,
            'database': self.database,
            'port':
                self.port if self.port
                else Constants.
                CONNECTION_TYPES_DICT[self.type]['default_port']
        }

        # If no password leave it alone
        if self.password is not None:
            db_config['password'] = Helpers.db_credential_decrypt(
                self.password, config['DB_ENCRYPT_KEY']
            )

        return db_config

    def __repr__(self):
        """Print the Connection instance."""
        return '<Connection "{name}" - Id {id}>'.format(
            name=self.name, id=self.connection_id
        )


class Job(db.Model, ProxiedDictMixin):
    """
    Docstring for Job Model class.

    Job Model class represent for job table which is used to
    store the get data job's information.
    """

    __tablename__ = 'job'

    job_id = db.Column('id', db.Integer,
                       primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    annotation = db.Column(db.Text)
    connection_id = db.Column('connectionId', db.Integer,
                              db.ForeignKey('connection.id'), nullable=True)
    _commands = db.Column('commands', db.Text, nullable=False)
    user_id = db.Column('userId', db.Integer,
                        db.ForeignKey('user.id'), nullable=False)
    created_on = db.Column('createdOn', db.DateTime,
                           default=datetime.datetime.now)
    last_updated = db.Column('lastUpdated',
                             db.DateTime,
                             onupdate=datetime.datetime.now,
                             default=datetime.datetime.now)
    no_of_executed = db.Column('noOfExecuted', db.Integer,
                               default=0, nullable=False)
    job_type = db.Column('jobType', db.SmallInteger,
                         default=Constants.JOB_NONE,
                         nullable=False)
    is_deleted = db.Column('isDeleted', db.Boolean,
                           default=False, nullable=False)
    version = db.Column(db.Integer, index=True, nullable=False)

    emails = db.relationship('JobMailTo',
                             primaryjoin="and_(Job.job_id==JobMailTo.job_id, "
                                         "JobMailTo.enable==True)",
                             backref='Job',
                             lazy='joined')
    schedules = db.relationship('Schedule',
                                primaryjoin="and_("
                                            "Job.job_id==Schedule.job_id,"
                                            "Schedule.is_deleted==False"
                                            ")",
                                backref='Job',
                                lazy='joined')
    features = \
        db.relationship('JobFeature',
                        collection_class=attribute_mapped_collection(
                            'feature_name')
                        )
    _proxied = association_proxy("features",
                                 "feature_value",
                                 creator=lambda feature_name, feature_value:
                                 JobFeature(feature_name=feature_name,
                                            feature_value=feature_value)
                                 )

    __mapper_args__ = {
        'polymorphic_on': job_type,
        'polymorphic_identity': Constants.JOB_NONE
    }

    def __init__(self, name, commands, user_id, **kwargs):
        """
        Constructor for Job.

        :param name: Job's name.
        :param command: Job's command which will be executed.
        :param user_id: Job's creator's User Id.
        :param kwargs:
            annotation: Job's description and annotation.
        """
        self.name = name
        self.annotation = kwargs.get('annotation')
        if self.job_type == Constants.JOB_NONE:
            self.commands = "/* NO COMMAND */\n" + commands
        else:
            self.commands = commands
        self.user_id = user_id
        self.version = Constants.MODEL_JOB_VERSION

    @property
    def commands(self):
        """Return command field."""
        return self._commands

    @commands.setter
    def commands(self, commands):
        """Setter for commands property."""
        self._commands = commands

    def update_executed_times(self):
        """Update Job's total executed times."""
        self.no_of_executed += 1

    @property
    def recipients(self):
        """Return Job recipients list."""
        recipients_list = []
        for recipient in self.emails:
            recipients_list.append(str(recipient))
        return recipients_list

    @classmethod
    def with_feature(cls, feature_name, feature_value):
        """Used to query job having given attribute."""
        return cls.facts.any(feature_name=feature_name,
                             feature_value=feature_value)

    def __repr__(self):
        """Print the Job instance."""
        return '<Job "{name}" - Id {id}>'.format(
            name=self.name, id=self.job_id
        )


class QueryDataJob(Job):
    """Job for query Data from Database."""

    __mapper_args__ = {
        'polymorphic_identity': Constants.JOB_QUERY
    }

    def __init__(self, name, query_string, user_id, **kwargs):
        """
        Constructor for QueryDataJob class.

        :param name: Job's name.
        :param query_string:
            Query that will be used to get data from Database.
        :param user_id: Job's creator's User Id.
        :param kwargs:
            annotation: Job's description and annotation.
            connection_id: Connection's Id, reference to Connection Model.
        """
        self.connection_id = kwargs.get('connection_id')
        self.job_type = Constants.JOB_QUERY
        query_string = "/* QUERY STRING */\n" + query_string

        super(QueryDataJob, self).__init__(name=name, commands=query_string,
                                           user_id=user_id, kwargs=kwargs)

    @property
    def query_string(self):
        """Return command field."""
        return self._commands

    @query_string.setter
    def query_string(self, query_string):
        """Setter for commands property."""
        self._commands = query_string

    @hybrid_property
    def is_active(self):
        """Check if the job is active or not."""
        return not not self.connection_id


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

    schedule_id = db.Column('id', db.Integer,
                            primary_key=True, autoincrement=True)
    job_id = db.Column('jobId', db.Integer,
                       db.ForeignKey('job.id'), nullable=False)
    _is_active = db.Column('isActive', db.Boolean,
                           default=True, nullable=False)
    minute_of_hour = db.Column('minuteOfHour',
                               db.SmallInteger, default=0, nullable=False)
    hour_of_day = db.Column('hourOfDay', db.SmallInteger,
                            default=0, nullable=False)
    day_of_week = db.Column('dayOfWeek', db.SmallInteger,
                            default=0, nullable=False)
    day_of_month = db.Column('dayOfMonth', db.SmallInteger,
                             default=1, nullable=False)
    schedule_type = db.Column('scheduleType', db.SmallInteger,
                              default=Constants.SCHEDULE_ONCE,
                              nullable=False)
    next_run = db.Column('nextRun', db.DateTime, nullable=True)
    user_id = db.Column('userId', db.Integer,
                        db.ForeignKey('user.id'), nullable=False)
    created_on = db.Column('createdOn', db.DateTime,
                           default=datetime.datetime.now)
    last_updated = db.Column('lastUpdated',
                             db.DateTime,
                             onupdate=datetime.datetime.now,
                             default=datetime.datetime.now)
    is_deleted = db.Column('isDeleted', db.Boolean,
                           default=False, nullable=False)
    version = db.Column(db.Integer, index=True, nullable=False)

    def __init__(self, job_id, start_time, user_id,
                 **kwargs):
        """
        Input and validate schedule.

        :param job_id:
            Scheduled Job's Id.
        :param start_time:
            Time when the job will be trigger, datetime instance.
        :type start_time: datetime.datetime
        :param kwargs:
            schedule_type: Schedule type, see in the class's docstring.
            is_active: This schedule is active or not.
        """
        self.job_id = job_id
        self.schedule_type = \
            kwargs.get('schedule_type', Constants.SCHEDULE_ONCE)
        self._is_active = kwargs.get('is_active', False)
        self.update_start_time(start_time)
        self.user_id = user_id
        self.version = Constants.MODEL_SCHEDULE_VERSION

    @hybrid_property
    def is_active(self):
        """Get Schedule's active status."""
        return self._is_active and not self.is_deleted

    @is_active.setter
    def is_active(self, is_active):
        """Set Schedule's active status."""
        self._is_active = is_active

    @is_active.expression
    def is_active(self):
        """Get Schedule's active status expression."""
        return and_(self._is_active, not_(self.is_deleted))

    def validate(self):
        """
        Validate the schedule.

        :return: True if the schedule will be run on the feature else False.
        """
        if self.schedule_type == Constants.SCHEDULE_ONCE:
            return self.next_run > datetime.datetime.now()

        if self.schedule_type == Constants.SCHEDULE_HOURLY:
            return Helpers.validate_minute_of_hour(self.minute_of_hour)

        if self.schedule_type == Constants.SCHEDULE_DAILY:
            return Helpers.validate_minute_of_hour(self.minute_of_hour) and \
                Helpers.validate_hour_of_day(self.hour_of_day)

        if self.schedule_type == Constants.SCHEDULE_WEEKLY:
            return Helpers.validate_minute_of_hour(self.minute_of_hour) and \
                Helpers.validate_hour_of_day(self.hour_of_day) and \
                Helpers.validate_day_of_week(self.day_of_week)

        if self.schedule_type == Constants.SCHEDULE_MONTHLY:
            return Helpers.validate_minute_of_hour(self.minute_of_hour) and \
                Helpers.validate_hour_of_day(self.hour_of_day) and \
                Helpers.validate_day_of_week(self.day_of_month)

    def update_start_time(self, start_time):
        """Update next run time on schedule updating."""
        self.minute_of_hour = start_time.minute
        self.hour_of_day = start_time.hour
        self.day_of_week = start_time.weekday()
        self.day_of_month = start_time.day
        self.next_run = start_time

        if start_time < datetime.datetime.now() + relativedelta(minutes=1):
            self.update_next_run(False)

    def update_next_run(self, validated=False, frequency=60):
        """Update the next time this job will be run."""
        if not validated:
            validated = self.validate()

        if not validated:
            raise ValueError('Schedule is not valid!')

        if self.schedule_type == Constants.SCHEDULE_ONCE:
            return

        cur_time = datetime.datetime.now()
        next_run_time = datetime.datetime.now()

        if self.schedule_type == Constants.SCHEDULE_HOURLY:
            next_run_time += relativedelta(
                minute=self.minute_of_hour, seconds=-1
            )
            cur_time -= relativedelta(minutes=-1)

            if cur_time >= next_run_time:
                next_run_time += relativedelta(hours=1)

        elif self.schedule_type == Constants.SCHEDULE_DAILY:
            next_run_time += relativedelta(minute=self.minute_of_hour,
                                           hour=self.hour_of_day)

            if cur_time >= next_run_time:
                next_run_time += relativedelta(days=1)

        elif self.schedule_type == Constants.SCHEDULE_WEEKLY:
            next_run_time += relativedelta(minute=self.minute_of_hour,
                                           hour=self.hour_of_day,
                                           weekday=self.day_of_week)

            if cur_time >= next_run_time:
                next_run_time += relativedelta(weeks=1)

        elif self.schedule_type == Constants.SCHEDULE_MONTHLY:
            next_run_time += relativedelta(minute=self.minute_of_hour,
                                           hour=self.hour_of_day,
                                           day=self.day_of_month)

            if cur_time >= next_run_time:
                next_run_time += relativedelta(months=1)

        self.next_run = next_run_time.replace(second=0)
        # TODO: Better algorithm

    def __repr__(self):
        """Print the Schedule instance."""
        return '<Schedule Id {id} of Job Id {jobId}>'.format(
            id=self.schedule_id, jobId=self.job_id
        )


class TrackJobRun(db.Model):
    """Track status whenever a job is running."""

    track_job_run_id = db.Column('id', db.Integer,
                                 primary_key=True, autoincrement=True)
    job_id = db.Column('jobId', db.Integer,
                       db.ForeignKey('job.id'), nullable=False)
    schedule_id = db.Column('scheduleId', db.Integer,
                            db.ForeignKey('schedule.id'), nullable=True)
    scheduled_on = db.Column('scheduledOn', db.DateTime,
                             default=datetime.datetime.now, nullable=False)
    ran_on = db.Column('ranOn', db.DateTime, nullable=True)
    duration = db.Column(db.Integer, default=0, nullable=False)
    status = db.Column(db.SmallInteger,
                       default=Constants.JOB_QUEUED, nullable=False)
    error_string = db.Column('errorString', db.Text, nullable=True)
    version = db.Column(db.Integer, index=True, nullable=False)

    def __init__(self, job_id, schedule_id=None):
        """
        Call when enqueue a job.

        :param job_id:
            Running Job's Id.
        :param schedule_id:
            Running Schedule's Id.
        """
        self.job_id = job_id
        self.schedule_id = schedule_id
        self.version = Constants.MODEL_TRACK_JOB_RUN_VERSION

    def start(self):
        """Call to track when the Job begin to run."""
        self.ran_on = datetime.datetime.now()
        self.status = Constants.JOB_RUNNING

    def complete(self, is_success, run_duration, error_string=None):
        """
        Call whenever a job is completed.

        :param is_success: Is the job success.
        :param run_duration: Runtime in milliseconds.
        :param error_string: Error when the job is failed.
        """
        self.status = Constants.JOB_RAN_SUCCESS \
            if is_success else Constants.JOB_RAN_FAILED
        self.duration = run_duration
        self.error_string = error_string

    def check_expiration(self):
        """
        Check and update result expiration.

        :return: True if the result is expiring.
                 False if the result is still valid or expired.
        """
        if self.status != Constants.JOB_RAN_SUCCESS:
            return False

        time_delta = self.duration + ((
            datetime.datetime.now() - self.ran_on
        ).total_seconds() * 1000)

        if self.status == Constants.JOB_RAN_SUCCESS \
                and time_delta > \
                config.get('JOB_RESULT_VALID_SECONDS', 86400) * 1000:
            self.status = Constants.JOB_RESULT_EXPIRED
            return True

        return False

    def __repr__(self):
        """Print the Job Tracker instance."""
        return '<Tracker {id}: Job Id {jobId} {status}>'.format(
            id=self.track_job_run_id, jobId=self.job_id,
            status=Constants.JOB_TRACKING_STATUSES_DICT[self.status]['name']
        )


class JobMailTo(db.Model):
    """Emails which the result will be sent to."""

    job_mail_to_id = db.Column('id', db.Integer,
                               primary_key=True, autoincrement=True)
    job_id = db.Column('jobId', db.Integer,
                       db.ForeignKey('job.id'), nullable=False)
    email_address = db.Column('emailAddress', db.String(100), nullable=False)
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
        self.job_id = job_id
        self.email_address = email_address

    def __repr__(self):
        """Print the email."""
        return '{email_address}'.format(
            email_address=self.email_address
        )


class JobFeature(db.Model):
    """Used to extend Job's table."""

    job_id = db.Column('jobId', db.Integer,
                       db.ForeignKey('job.id'),
                       primary_key=True)
    feature_name = db.Column('featureName', db.String(255),
                             primary_key=True)
    _feature_value = db.Column('featureValue', db.String(255),
                               nullable=False)
    last_updated = db.Column('lastUpdated',
                             db.DateTime,
                             onupdate=datetime.datetime.now,
                             default=datetime.datetime.now)

    def __init__(self, feature_name, feature_value):
        """
        Docstring for JobFeature Model constructor.

        :param feature_name:
            Job's feature name, ref to Constants.
        :param feature_value:
            Job's feature value.
        """
        if feature_name in Constants.JOB_FEATURE_DICT:
            self.feature_name = feature_name
        else:
            raise ValueError('Do not know feature name of "{feature_name}"'.
                             format(feature_name=feature_name))
        self.feature_value = feature_value

    @hybrid_property
    def feature_value(self):
        """Convert feature value to it's type and return."""
        return Constants.JOB_FEATURE_DICT[self.feature_name]['py_type'](
            self._feature_value
        )

    @feature_value.setter
    def feature_value(self, feature_value):
        """Validate feature value and save to _feature_value."""
        if isinstance(feature_value,
                      Constants.JOB_FEATURE_DICT
                      [self.feature_name]['py_type']):
            self._feature_value = str(feature_value)
        else:
            raise ValueError('Invalid type of "{feature_name}"'.
                             format(feature_name=self.feature_name))

    def __repr__(self):
        """Print feature value."""
        return '<Job {job_id}\'s {feature_name}: {feature_value}>'.format(
            job_id=self.job_id,
            feature_name=self.feature_name,
            feature_value=self.feature_value
        )

# pylint: disable=R0902
