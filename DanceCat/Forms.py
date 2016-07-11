from flask_wtf import Form
from wtforms import StringField, PasswordField, TextAreaField, \
    SelectField, IntegerField, \
    FormField, FieldList, \
    validators
from wtforms.compat import iteritems
import Constants


class RegisterForm(Form):
    email = StringField('Email Address', validators=[
        validators.DataRequired(),
        validators.Email()
    ])
    password = PasswordField('Password', validators=[
        validators.DataRequired(),
        validators.Length(min=8)
    ])


class ConnectionForm(Form):
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


class JobMailToForm(Form):
    emailAddress = StringField(
        'Email',
        render_kw={
            'placeholder': 'report_to@dancecat.com'
        },
        validators=[
            validators.DataRequired(),
            validators.Email()
        ]
    )


class JobForm(Form):
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
                       'Send Result To')

    def populate_obj(self, obj):
        for name, field in iteritems(self._fields):
            if name != 'emails':
                field.populate_obj(obj, name)
