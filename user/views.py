#External Libraries
from flask import Blueprint, render_template, redirect, session, request, url_for, flash, abort
from werkzeug.security import generate_password_hash
from collections import defaultdict
from datetime import datetime
#Internal Libraries
from application import db
from user.models import user_login, requests
from librarian.models import accept
from user.forms import RegisterForm, LoginForm, SearchForm
from book.models import books

user_app = Blueprint('user_app', __name__)


@user_app.route('/user')
def user():
    form = RegisterForm()
    return render_template('user/user.html', form = form)

@user_app.route('/usignin', methods = ['GET', 'POST'])
def usignin():
    form = LoginForm()
    error = None
    if request.method == 'GET' and request.args.get('next'):
        session['next'] = request.args.get('next', None)
    if form.validate_on_submit():
        user = user_login.query.filter_by(username = form.username.data).first()
        session['user_id'] = user.user_id
        session['uname'] = user.username
        if 'next' in session:
            next = session.get('next')
            session.pop('next')
            return redirect(next)
        else:
            return redirect(url_for('user_app.umain'))
    return render_template('user/usignin.html', form = form)


@user_app.route('/uregister', methods = ['GET', 'POST'])
def uregister():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_pwd = generate_password_hash(form.password.data)
        user = user_login(
            username = form.username.data,
            email = form.email.data,
            password = hashed_pwd
        )
        db.session.add(user)
        db.session.commit()
        session['username'] = user.username
        flash('You are registered successfully')
        return redirect(url_for('.usignin'))
    return render_template('user/uregister.html', form = form)


@user_app.route('/umain', methods=['GET', 'POST'])
def umain():
    form = RegisterForm()
    # Fetch all books
    book_query = books.query.all()

    # Group books by section
    books_by_section = defaultdict(list)
    for book in book_query:
        section_name = book.section.section_name
        books_by_section[section_name].append(
            (book.book_id, book.book_name, book.book_author, book.book_description, book.section_id, book.doa)
        )
    books_by_section = dict(books_by_section)

    # Fetch the 10 most recently added books
    recent_books_query = books.query.order_by(books.doa.desc()).limit(10).all()
    recent_books = [{
        'id': book.book_id,
        'title': book.book_name,
        'author': book.book_author,
        'image_url': 'static/images/book1.jpg',
        'upload_date': book.doa
    } for book in recent_books_query]
    if 'uname' in session:
        return render_template('user/umain.html', form=form, books_by_section=books_by_section, recent_books=recent_books)
    else:
        return redirect(url_for('.usignin'))


@user_app.route('/mybooks', methods=['GET', 'POST'])
def mybooks():
    form = RegisterForm()
    form1 = LoginForm()
    username = session.get('uname')
    requested_book = requests.query.filter_by(username=username).all()
    requested_books = [(req.req_no, req.book_id, req.username, req.book_name) for req in requested_book]
    accepted_book = accept.query.filter_by(username=username).all()
    accepted_books = [
        (acc.acc_no, acc.book_id, acc.book_name, acc.username, acc.librarian_name, acc.issued_date, acc._valid_date) for
        acc in accepted_book]
    # Delete rows where _valid_date equals current date
    current_date = datetime.now().date()
    rows_to_delete = accept.query.filter(accept._valid_date == current_date).all()
    for row in rows_to_delete:
        db.session.delete(row)
    db.session.commit()
    if 'uname' in session:
        return render_template('user/mybooks.html', requested_books=requested_books, accepted_books=accepted_books, form=form)
    else:
        return redirect(url_for('.usignin'))


@user_app.route('/search_result', methods=('GET', 'POST'))
def search_result():
    # Fetch the query and results from the request or any other source
    query = request.form.get('query')  # Assuming the query is sent via POST
    results = []  # Placeholder for search results, replace it with your actual search results

    return render_template('user/search_result.html', query=query, results=results)


@user_app.route('/search', methods=('GET', 'POST'))
def search():
    form = SearchForm()
    posts = books.query
    if request.method == 'POST' and form.validate_on_submit():
        q = form.search.data
        posts = posts.filter(books.book_name.like('%' + q + '%'))
        posts = posts.order_by(books.book_id).all()
        return render_template('user/search_result.html', query=q, results=posts, title='Search Results', form=form)

    q = form.search.data if form.search.data else ''
    posts = posts.filter(books.book_name.like('%' + q + '%'))
    posts = posts.order_by(books.book_id).all()
    return render_template('user/umain.html', query=q, results=posts, title='Search Results', form=form)

@user_app.route('/profile', methods = ['GET', 'POST'])
def profile():
    form = RegisterForm()
    username = session['uname']
    user_info = user_login.query.filter_by(username=username)
    user_info = [
        [req.username, req.email, req.user_id] for
        req in user_info]
    acc_books = accept.query.filter_by(username=username).count()
    user_info.append(acc_books)
    req_books = requests.query.filter_by(username=username).count()
    user_info.append(req_books)
    return render_template('user/profile.html', form = form, info = user_info)
