#External Moudules
from flask import Blueprint, render_template, redirect, request, url_for, flash, session
from flask import session as sec
#Internal Modules
from application import db
from section.models import sections
from section.forms import SectionForm


section_app = Blueprint('section_app', __name__)

@section_app.route('/editsection', methods=['POST', 'GET'])
def editsection():
    form = SectionForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            section = sections(
                section_name=form.section_name.data,
                librarian_name = sec.get('librarian_name')
            )
            db.session.add(section)
            db.session.commit()
            flash('The new section is added')
            return redirect(url_for('book_app.editbook'))
    if 'librarian_name' in session:
        return render_template('section/editsection.html', form=form)
    else:
        return redirect(url_for('librarian_app.lsignin'))
