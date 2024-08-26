#External Modules
from datetime import datetime, timedelta
# Internal Modules
from application import db


class lib_login(db.Model):
    __tablename__ = 'lib_login'
    lib_id = db.Column(db.Integer, primary_key = True, nullable = False, unique = True)
    librarian_name = db.Column(db.String(80), nullable = False, unique = True)
    password = db.Column(db.String(128), nullable = False)
    email = db.Column(db.String(120), nullable = False)

class accept(db.Model):
    __tablename__ = 'accept'
    acc_no = db.Column(db.Integer, primary_key=True, nullable=False, unique=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.book_id'), nullable=False)
    book_name = db.Column(db.String(80), nullable=False)
    username = db.Column(db.String(80), db.ForeignKey('user_login.username'), nullable=False)
    librarian_name = db.Column(db.String(80), db.ForeignKey('lib_login.librarian_name'), nullable=False)
    issued_date = db.Column(db.Date, default=datetime.utcnow, nullable=False)
    _valid_date = db.Column(db.Date, nullable=False)  # Use a private attribute to store valid_date

    def __init__(self, **kwargs):
        super(accept, self).__init__(**kwargs)
        if self.issued_date is None:
            self.issued_date = datetime.utcnow().date()  # Set issued_date to current date if not provided
        if self._valid_date is None:
            self._valid_date = self.issued_date + timedelta(days=5)  # Calculate _valid_date

    @property
    def valid_date(self):
        return self._valid_date

    @valid_date.setter
    def valid_date(self, value):
        self._valid_date = value

    @staticmethod
    def update_valid_date(target, value, oldvalue, initiator):
        if value and not oldvalue:
            target._valid_date = value + timedelta(days=5)

db.event.listen(accept.issued_date, 'set', accept.update_valid_date)