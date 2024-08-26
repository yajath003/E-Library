# External Modules
from flask_wtf import FlaskForm
from wtforms import validators, StringField

class SectionForm(FlaskForm):
    section_name = StringField('Section Name', [validators.InputRequired()])
