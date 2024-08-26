from flask import Blueprint,render_template, session
intro_app = Blueprint('intro_app', __name__)


@intro_app.route('/')
def index():
    session.clear()
    return render_template('intro/login.html')

