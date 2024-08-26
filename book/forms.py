# External Modules
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, RadioField
from wtforms import FileField
from wtforms.validators import DataRequired


# Internal Modules
from section.models import sections as sec

class BookForm(FlaskForm):
    book_name = StringField('Book Name', validators=[DataRequired()])
    book_description = TextAreaField('Book Description', validators=[DataRequired()])
    book_author = StringField('Book Author', validators=[DataRequired()])
    book_file = FileField('Book File', validators=[DataRequired()])
    section_name = RadioField('Section Name', validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        sections = sec.query.all()
        self.section_name.choices = [(str(section.sec_id), section.section_name) for section in sections]