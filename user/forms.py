# External Modules
from flask_wtf import FlaskForm
from wtforms import validators, StringField, PasswordField, ValidationError
from wtforms import EmailField, SubmitField, FileField,  BooleanField
from werkzeug.security import check_password_hash
from flask_wtf.file import FileAllowed
from flask import session

# Internal Modules
from user.models import user_login

class RegisterForm(FlaskForm):
    username = StringField('username', [validators.InputRequired()])
    email = EmailField('Email address', [validators.InputRequired(), validators.Email()])
    password = PasswordField('Password', [
            validators.InputRequired(),
            validators.Length(min=4, max=80) ])
    confirm = PasswordField('Repeat Password', [
            validators.EqualTo('password', message='Passwords must match'), ])
    token = StringField('Secret Code')

    def validate_username(self, username):
        user = user_login.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username')

    def validate_email(self, email):
        author = user_login.query.filter_by(email=email.data).first()
        if author is not None:
            raise ValidationError('Email already in use, please use a different one.')


class LoginForm(FlaskForm):
    username = StringField('User Name', [validators.InputRequired()])
    password = PasswordField('Password', [
            validators.InputRequired(),
            validators.Length(min=4, max=80)
        ])
    submit = SubmitField('Login')

    def validate(self):
        rv = FlaskForm.validate(self)
        if not rv:
            return False

        user = user_login.query.filter_by(
            username = self.username.data,
            ).first()

        if user:
            if not check_password_hash(user.password, self.password.data):
                self.password.errors.append('Incorrect email or password')
                return False
            return True
        else:
            self.password.errors.append('Incorrect email or password')
            return False

class SearchForm(FlaskForm):
    search = StringField('search', [validators.InputRequired()])
    submit = SubmitField('Search')