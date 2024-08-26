from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_markdown import MarkdownExtension
from flaskext.markdown import Markdown

db = SQLAlchemy()
def create_app(**config_overrides):
    app = Flask(__name__)

    # Load config
    app.config.from_pyfile('settings.py')

    db.init_app(app)
    migrate = Migrate(app, db)


    from librarian.views import librarian_app
    from user.views import user_app
    from intro.views import intro_app
    from book.views import book_app
    from section.views import section_app


    #MarkdownExtension(app)
    app.register_blueprint(librarian_app)
    app.register_blueprint(user_app)
    app.register_blueprint(intro_app)
    app.register_blueprint(book_app)
    app.register_blueprint(section_app)
    return app
