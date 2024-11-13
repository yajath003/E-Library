# External Modules
from flask_wtf import FlaskForm
from wtforms import validators, StringField, PasswordField, ValidationError
from wtforms import EmailField, SubmitField
from werkzeug.security import check_password_hash

# Internal Modules
from librarian.models import lib_login

class RegisterForm(FlaskForm):
    librarian_name = StringField('User Name', [validators.InputRequired()])
    email = EmailField('Email address', [validators.InputRequired(), validators.Email()])
    password = PasswordField('Password', [
            validators.InputRequired(),
            validators.Length(min=4, max=80) ])
    confirm = PasswordField('Repeat Password', [
            validators.EqualTo('password', message='Passwords must match'), ])
    token = StringField('Secret Code')

    def validate_username(self, librarian_name):
        user = lib_login.query.filter_by(full_name=librarian_name.data).first()
        if user is not None:
            raise ValidationError('Please use a different username')

    def validate_email(self, email):
        author = lib_login.query.filter_by(email=email.data).first()
        if author is not None:
            raise ValidationError('Email already in use, please use a different one.')


class LoginForm(FlaskForm):
    librarian_name = StringField('Librarian Name', [validators.InputRequired()])
    password = PasswordField('Password', [
            validators.InputRequired(),
            validators.Length(min=4, max=80)
        ])
    submit = SubmitField('Login')

    def validate(self, extra_validators=None):
        rv = super().validate(extra_validators=extra_validators)  # Call the parent class validate method
        if not rv:
            return False

        user = lib_login.query.filter_by(librarian_name=self.librarian_name.data).first()

        if user:
            if not check_password_hash(user.password, self.password.data):
                self.password.errors.append('Incorrect email or password')
                return False
            return True
        else:
            self.password.errors.append('Incorrect email or password')
            return False

