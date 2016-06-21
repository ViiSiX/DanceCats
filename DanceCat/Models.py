from flask_login import UserMixin
from DanceCat import db, config, Helpers, Constants
import datetime


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), index=True, unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    isActive = db.Column(db.Boolean, nullable=False, default=True)
    createdOn = db.Column(db.DateTime, default=datetime.datetime.now)
    lastLogin = db.Column(db.DateTime, nullable=True)
    lastUpdated = db.Column(db.DateTime, onupdate=datetime.datetime.now, default=datetime.datetime.now)
    version = db.Column(db.Integer, index=True, nullable=False)

    def __init__(self, user_email, user_password):
        self.email = user_email
        self.password = Helpers.encrypt_password(user_password)
        self.version = 1

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
    version = db.Column(db.Integer, index=True, nullable=False)

    def __init__(self, name, db_type, host, database, user_name,
                 creator_user_id,
                 port=None, password=None):
        self.name = name
        self.type = db_type
        self.host = host
        self.port = port
        self.userName = user_name
        self.encrypt_password(password)
        self.database = database
        self.userId = creator_user_id
        self.version = 1

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


class AllowedEmail(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), index=True, unique=True, nullable=False)
    version = db.Column(db.String(255), index=True, nullable=False)

    def __init__(self, allowed_email):
        self.email = allowed_email
        self.version = 1

    def __repr__(self):
        return '<{email}>'.format(email=self.email)
