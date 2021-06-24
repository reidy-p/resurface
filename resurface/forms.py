from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, TimeField, IntegerField
from wtforms.validators import DataRequired
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, NumberRange
from resurface.models import User
from flask_wtf.html5 import URLField
from wtforms.validators import url


class LoginForm(FlaskForm):
    email = StringField('Email Address', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


class ReminderForm(FlaskForm):
    reminder_day = SelectField(
        u'Reminder Day',
        choices=[
            ('mon', 'Monday'),
            ('tue', 'Tuesday'),
            ('wed', 'Wednesday'),
            ('thu', 'Thursday'),
            ('fri', 'Friday'),
            ('sat', 'Saturday'),
            ('sun', 'Sunday')
        ]
    )
    reminder_time = TimeField(
        'Reminder Time'
    )
    num_items = IntegerField(
        'Number of Items',
        validators=[NumberRange(min=1, max=10, message='Please enter a value between 1 and 10')]
    )
    submit = SubmitField('Submit')


class ManualItemForm(FlaskForm):
    url = URLField(validators=[url()])
    title = StringField('Title')
    submit = SubmitField('Submit')


class AccessTokenForm(FlaskForm):
    access_token = StringField('Readwise Access Token')
    submit = SubmitField('Submit')
