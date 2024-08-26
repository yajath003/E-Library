from application import db


class books(db.Model):
    __tablename__ = 'books'
    book_id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True)
    book_name = db.Column(db.String(80), nullable=False, unique=True)
    book_description = db.Column(db.String(900), nullable=False)
    book_author = db.Column(db.String(80), nullable=False)
    data = db.Column(db.String(255))
    section_id = db.Column(db.Integer, db.ForeignKey('sections.sec_id'), nullable=False)
    section = db.relationship('sections', backref=db.backref('books', lazy=True))
    doa = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return '<Book {}>'.format(self.book_name)