#External Moudules
from flask import Blueprint, render_template, redirect, session, request, url_for, flash
from werkzeug.utils import secure_filename
from sqlalchemy import exists
import os
from datetime import datetime
from collections import defaultdict
#Internal libraries
from application import db
from book.models import books
from book.forms import BookForm
from section.models import sections
from user.models import requests
from librarian.models import accept
from librarian.forms import LoginForm
from librarian.views import librarian_app
from user.views import user_app

book_app = Blueprint('book_app', __name__)

UPLOAD_FOLDER = 'static/files'
ALLOWED_EXTENSIONS = {'pdf', 'txt', 'doc', 'docx'}


@book_app.route('/editbook', methods=['GET', 'POST'])
def editbook():
    form = BookForm()
    date_of_addition = datetime.now()
    sections_query = sections.query.all()
    section_names = [(section.sec_id, section.section_name) for section in sections_query]

    if request.method == 'POST':
        print(request.form)
        if form.validate_on_submit():
            file_path = None
            if 'book_file' in request.files:
                file = request.files['book_file']
                if file.filename != '':
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(UPLOAD_FOLDER, filename)
                    file.save(file_path)

            selected_section_id = int(request.form.get('section_name'))
            selected_section = sections.query.get(selected_section_id)

            book = books(
                book_name=form.book_name.data,
                book_description=form.book_description.data,
                book_author=form.book_author.data,
                data=file_path,
                section=selected_section,
                doa=date_of_addition
            )
            db.session.add(book)
            db.session.commit()
            flash('Book added successfully')
            return redirect(url_for('librarian_app.lmain'))
        else:
            print("Form errors:", form.errors)
    if 'librarian_name' in session:
        return render_template('book/editbook.html', form=form, section_names=section_names)
    else:
        return redirect(url_for('librarian_app.lsignin'))


@book_app.route('/book/<int:book_id>', methods=['GET', 'POST'])
def book(book_id):
    num = book_id
    form = BookForm()
    book_names = books.query.get_or_404(book_id)
    book = (book_names.book_id, book_names.book_name, book_names.book_author, book_names.book_description,
            book_names.section_id, book_names.doa)

    if request.method == 'POST':
        # Check if the book has already been requested by the current user
        username = session.get('uname')
        existing_request = requests.query.filter_by(book_id=num, username=username).first()
        if existing_request:
            flash('The book is already requested')
            return redirect(url_for('user_app.umain'))
        existing_accept = accept.query.filter_by(book_id = num, username = username).first()
        if existing_accept:
            flash("The book is already in your 'my books' ")
            return redirect(url_for('user_app.umain'))
        req_count = requests.query.filter_by(username = username).count()
        acc_count = accept.query.filter_by(username = username).count()
        print(req_count, acc_count)
        if req_count <= 5 and acc_count<= 5:
            req = requests(
                book_id=num,
                username=username,
                book_name=book_names.book_name
            )
            print(req)
            db.session.add(req)
            db.session.commit()
            flash('The book is requested')
            return redirect(url_for('user_app.umain'))
        else:
            flash("maximum request limit reached")
            return redirect(url_for('user_app.umain'))
    if 'uname' in session:
        return render_template('book/book.html', form=form, book=book)
    else:
        return redirect(url_for('user_app.usignin'))


@book_app.route('/dbook', methods=['GET', 'POST'])
def dbook():
    if request.method == 'POST':
        selected_books = request.form.getlist('selected_books[]')
        selected_sections = request.form.getlist('selected_sections[]')

        # Delete selected books
        for book_id in selected_books:
            book = books.query.get(book_id)
            db.session.delete(book)

        # Delete books within selected sections
        for section_name in selected_sections:
            section = sections.query.filter_by(section_name=section_name).first()
            books_to_delete = books.query.filter_by(section=section).all()
            for book in books_to_delete:
                db.session.delete(book)

            # Check if the section is empty after book deletion
            if not books.query.filter_by(section=section).first():
                db.session.delete(section)

        db.session.commit()
        flash('Selected books and sections deleted successfully', 'success')
        return redirect(url_for('librarian_app.lmain'))

    # If not a POST request, render the template with the form and book details
    form = BookForm()
    book_query = books.query.all()
    # Group books by section
    books_by_section = defaultdict(list)
    for book in book_query:
        section_name = book.section.section_name
        books_by_section[section_name].append(
            (book.book_id, book.book_name, book.book_author, book.book_description, book.section_id, book.doa)
        )
    books_by_section = dict(books_by_section)
    if 'librarian_name' in session:
        return render_template('book/dbook.html', form=form, books_by_section=books_by_section)
    else:
        return redirect(url_for('librarian_app.lsignin'))
