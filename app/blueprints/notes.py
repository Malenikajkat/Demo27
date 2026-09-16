"""Blueprint для API заметок."""
from flask import Blueprint, request, jsonify
from sqlalchemy import select, func

from app.models import Note, User
from app.utils import build_note_response
from app.extensions import db

notes_bp = Blueprint("notes", __name__)


@notes_bp.route("/", methods=["GET"])
def get_notes():
    """Список заметок с трансформацией данных."""
    try:
        skip = request.args.get("skip", 0, type=int)
        limit = request.args.get("limit", 100, type=int)

        if skip < 0 or limit < 1:
            return jsonify({
                "error": "Bad Request",
                "message": "skip >= 0, limit >= 1",
            }), 400

        stmt = (
            select(Note, User.login)
            .join(User, Note.id_user == User.user_id)
            .offset(skip)
            .limit(limit)
        )
        results = db.session.execute(stmt).all()

        notes = [build_note_response(note, login) for note, login in results]
        total = db.session.execute(func.count(Note.note_id)).scalar()

        return jsonify({"notes": notes, "total": total}), 200

    except Exception:
        db.session.rollback()
        return jsonify({
            "error": "Internal Server Error",
            "message": "Ошибка базы данных",
        }), 500


@notes_bp.route("/<int:note_id>", methods=["GET"])
def get_note(note_id):
    """Получение одной заметки."""
    try:
        note = db.session.get(Note, note_id)
        if not note:
            return jsonify({"error": "Not Found", "message": "Заметка не найдена"}), 404

        user = db.session.get(User, note.id_user)
        login = user.login if user else "unknown"

        return jsonify(build_note_response(note, login)), 200

    except Exception:
        db.session.rollback()
        return jsonify({
            "error": "Internal Server Error",
            "message": "Ошибка базы данных",
        }), 500
