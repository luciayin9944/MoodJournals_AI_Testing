## journals.py

from flask import Flask, request, jsonify, make_response
from flask_restful import Api, Resource
from config import db, bcrypt, jwt, Config
from models import *  
from flask_jwt_extended import get_jwt_identity, jwt_required


class WeeklyJournal(Resource):
    @jwt_required()
    def get(self, year, week_number):
        curr_user_id = get_jwt_identity()

        week_journal = Journal.query.filter_by(user_id=curr_user_id, year=year, week_number=week_number).first()

        if not week_journal:
            return {"message": "No journal found for this week."}, 404
        
        entries = JournalEntry.query.filter_by(journal_id=week_journal.id).order_by(JournalEntry.entry_date.asc()).all()
        return jsonify(JournalEntrySchema(many=True).dump(entries))
    

    
class JournalList(Resource):
    @jwt_required()
    def get(self):
        curr_user_id = get_jwt_identity()
        page = request.args.get("page", 1, type=int)
        per_page = 6

        pagination = (
            db.session.query(Journal)
            .filter_by(user_id=curr_user_id)
            .order_by(Journal.year.desc(), Journal.week_number.desc())
            .paginate(page=page, per_page=per_page, error_out=False)
        )

        result = JournalSchema(many=True).dump(pagination.items)

        return jsonify({
            "journals": result,
            "total": pagination.total,
            "page": pagination.page,
            "pages": pagination.pages
        })
    


class WeeklyAnalysis(Resource):
    @jwt_required()
    def get(self, year, week_number):
        curr_user_id = get_jwt_identity()

        week_journal = Journal.query.filter_by(user_id=curr_user_id, year=year, week_number=week_number).first()

        if not week_journal:
            return {"message": "No journal found for this week."}, 404
        
        entries = JournalEntry.query.filter_by(journal_id=week_journal.id).order_by(JournalEntry.entry_date.asc()).all()
    
        data = [
            {
                "entry_date": entry.entry_date.isoformat(),
                "mood_score": entry.mood_score,
                "mood_tag": entry.mood_tag,
                "notes": entry.notes
            }
            for entry in entries
        ]
        return {"entries": data}, 200
        

class HasJournalEntries(Resource):
    @jwt_required()
    def get(self, year, week_number):
        curr_user_id = get_jwt_identity()

        week_journal = Journal.query.filter_by(user_id=curr_user_id, year=year, week_number=week_number).first()
        if not week_journal:
            return {"has_entries": False}, 200
        
        entry = db.session.query(JournalEntry.id).filter_by(journal_id=week_journal.id).first()
        if entry:
            return {"has_entries": True}, 200
        else:
            return {"has_entries": False}, 200