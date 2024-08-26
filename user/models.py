#External Modules
import os
import base64
from werkzeug.security import check_password_hash, generate_password_hash

#Internal Modules
from application import db
from settings import SECRET_KEY

class user_login(db.Model):
    __tablename__ = 'user_login'
    user_id = db.Column(db.Integer, primary_key = True, nullable = False, unique = True)
    username = db.Column(db.String(80), nullable = False, unique = True)
    password = db.Column(db.String(128), nullable = False)
    email = db.Column(db.String(120), nullable = False)


class requests(db.Model):
    __tablename__ = 'requests'
    req_no = db.Column(db.Integer, primary_key = True, nullable = False, unique = True)
    book_id =  db.Column(db.Integer, db.ForeignKey('books.book_id'), nullable=False)
    username = db.Column(db.String(80), db.ForeignKey('user_login.username'), nullable = False)
    book_name = db.Column(db.String(80), nullable = False)