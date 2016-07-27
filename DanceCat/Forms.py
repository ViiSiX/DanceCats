"""
Docstring for DanceCat.Forms module.

Contains the forms classes which is extended from
WTForms. Used for template's forms rendering.
"""

from flask_wtf import Form
from wtforms import StringField, PasswordField, TextAreaField, \
    SelectField, IntegerField, \
    FormField, FieldList, \
    validators
from wtforms.compat import iteritems
from . import Constants


class RegisterForm(Form):
    """Form which is used for register new member and also Log In function."""

    email = StringField('Email Address', validators=[
        validators.DataRequired(),
        validators.Email()
    ])
    password = PasswordField('Password', validators=[
        validators.DataRequired(),
        validators.Length(min=8)
    ])


class ConnectionForm(Form):
    """Form which is used to create/edit Database connection."""

    type = SelectField('Connection Type',
                       coerce=int,
                       choices=Constants.CONNECTION_TYPES_LIST)
    name = StringField('Name', validators=[
        validators.DataRequired()
    ])
    host = StringField('DB Host', validators=[
        validators.DataRequired()
    ])
    port = IntegerField('DB Port', validators=[
        validators.optional()
    ])
    userName = StringField('Username', validators=[
        validators.DataRequired()
    ])
    password = PasswordField('Password')
    database = StringField('Database', validators=[
        validators.DataRequired()
    ])


class ScheduleForm(Form):
    """Used to create/edit job's schedule."""

    scheduleType = SelectField('Schedule Type',
                               coerce=int,
                               choices=Constants)
    startTime = StringField('Start On',
                            validators=[
                                validators.DataRequired()
                            ])


class QueryJobForm(Form):
    """Used to create/edit data getting jobs."""

    name = StringField('Name',
                       render_kw={
                           'placeholder': 'Your job name'
                       },
                       validators=[
                           validators.DataRequired()
                       ])
    annotation = TextAreaField('Annotation',
                               render_kw={
                                   'placeholder': 'Job\'s annotation'
                               })
    connectionId = SelectField('Connection',
                               coerce=int)
    queryString = TextAreaField('Query', validators=[validators.DataRequired()])
    emails = FieldList(StringField('Email',
                                   render_kw={
                                       'placeholder': 'report_to@dancecat.com'
                                   },
                                   validators=[
                                       validators.Optional(),
                                       validators.Email()
                                   ]),
                       'Send Result To',
                       min_entries=1)

    def populate_obj(self, obj):
        """
        Populate form to object.

        Since Form's default `populate_obj` function populate all
        the fields in this class, this function will do the same
        function except `emails` field.

        :param obj: Job Model object.
        """
        for name, field in iteritems(self._fields):
            if name != 'emails':
                field.populate_obj(obj, name)
