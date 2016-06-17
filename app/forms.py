from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, BooleanField, TextAreaField, validators


class RegisterForm(Form):
    email = StringField('Email Address', validators=[
        validators.DataRequired(),
        validators.Email()
    ])
    password = PasswordField('Password', validators=[
        validators.DataRequired(),
        validators.Length(min=8)
    ])
