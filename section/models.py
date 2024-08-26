# Internal Modules
from application import db


class sections(db.Model):
    __tablename__ = 'sections'
    sec_id = db.Column(db.Integer, primary_key = True, nullable = False, unique = True)
    section_name = db.Column(db.String(80), nullable = False, unique = True)
    librarian_name = db.Column(db.String(80), db.ForeignKey('lib_login.librarian_name'), nullable = False,)