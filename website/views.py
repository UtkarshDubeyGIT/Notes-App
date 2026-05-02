from flask import Blueprint, render_template,request , flash,jsonify
from flask_login import login_required, current_user
from . import db
import json
from .models import Note
views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        note = request.form.get('note')
        if len(note)<1:
            flash('Note is too short!', category='error')
        else: 
            new_note = Note(data=note, user_id=current_user.id)
            db.session.add(new_note)
            db.session.commit()
    return render_template("home.html", user= current_user)

@views.route('/delete-note', methods=['POST'])
@login_required
def delete_note():
    note = json.loads(request.data)
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if not note:
        return jsonify({'error': 'Note not found'}), 404
    if note.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized to delete this note'}), 403
    db.session.delete(note)
    db.session.commit()
    return jsonify({'success': True}), 200