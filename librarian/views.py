#External libraries
from flask import Blueprint,render_template, redirect, session, request, url_for, flash
from werkzeug.security import generate_password_hash
from datetime import date

#Internal Libraries
from application import db
from librarian.forms import RegisterForm, LoginForm
from librarian.models import lib_login, accept
from user.models import requests
librarian_app = Blueprint('librarian_app', __name__)


@librarian_app.route('/librarian')
def librarian():
    form = RegisterForm()
    return render_template('librarian/librarian.html', form = form)

@librarian_app.route('/lsignin', methods = ['GET', 'POST'])
def lsignin():
    form = LoginForm()
    error = None
    if request.method == 'GET' and request.args.get('next'):
        session['next'] = request.args.get('next', None)
    if form.validate_on_submit():
        user = lib_login.query.filter_by(librarian_name=form.librarian_name.data).first()
        session['lib_id'] = user.lib_id
        session['librarian_name'] = user.librarian_name
        if 'next' in session:
            next = session.get('next')
            session.pop('next')
            return redirect(next)
        else:
            flash("Welcome librarian")
            return redirect(url_for('librarian_app.lmain'))
    return render_template('librarian/lsignin.html', form = form)


@librarian_app.route('/lregister', methods = ['GET', 'POST'])
def lregister():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_pwd = generate_password_hash(form.password.data)
        librarian = lib_login(
            librarian_name = form.librarian_name.data,
            email = form.email.data,
            password = hashed_pwd
        )
        db.session.add(librarian)
        db.session.commit()
        session['librarian_name'] = librarian.librarian_name
        flash('Your registration has been completed successfully')
        return redirect(url_for('.lsignin'))
    return render_template('librarian/lregister.html', form = form)

@librarian_app.route('/lmain')
def lmain():
    form = RegisterForm()
    all_requests = accept.query.all()
    count = requests.query.count()
    req = [(reqe.book_id, reqe.book_name, reqe.username, reqe.librarian_name) for reqe in all_requests]
    if 'librarian_name' in session:
        return render_template('librarian/lmain.html', form = form, all_requests = req, count = count)
    else:
        return redirect(url_for('librarian_app.lsignin'))


@librarian_app.route('/accbook', methods=['GET', 'POST'])
def accbook():
    form = RegisterForm()
    all_requests = requests.query.all()
    req = [(reqe.req_no, reqe.book_id, reqe.username, reqe.book_name) for reqe in all_requests]

    if request.method == 'POST':
        selected_book_ids = request.form.getlist('book_id')  # Retrieve multiple selected book IDs

        if selected_book_ids:
            for book_id in selected_book_ids:
                selected_request = requests.query.filter_by(book_id=book_id).first()  # Retrieve each selected request
                if selected_request:
                    new_accept = accept(
                        book_id=selected_request.book_id,
                        book_name=selected_request.book_name,
                        username=selected_request.username,
                        librarian_name=session.get('librarian_name')
                    )
                    db.session.add(new_accept)

                    db.session.delete(selected_request)

                else:
                    flash('Selected book request not found')
                    return redirect(url_for('librarian_app.lmain'))

            db.session.commit()
            flash('Books accepted successfully')
            return redirect(url_for('librarian_app.lmain'))

        else:
            flash('No books selected')
            return redirect(url_for('librarian_app.accbook'))
    if 'librarian_name' in session:
        return render_template('librarian/accbook.html', form=form, req=req)
    else:
        return redirect(url_for('librarian_app.lsignin'))
