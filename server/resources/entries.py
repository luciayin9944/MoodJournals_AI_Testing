## entries.py

from flask import Flask, request, jsonify, make_response
from flask_restful import Resource
from config import db
from models import *  
from flask_jwt_extended import get_jwt_identity, jwt_required
from datetime import date
from sqlalchemy import extract


## '/entries'
class NewEntry(Resource):
    @jwt_required()
    def post(self):
        curr_user_id = get_jwt_identity()
        data = request.get_json()
        curr_date = data.get("entry_date")

        try:
            entry_date = datetime.strptime(curr_date, "%Y-%m-%d").date()
        except Exception:
            return {"error": "Invalid date format. Use YYYY-MM-DD"}, 400
        
        existing_entry = (
            db.session.query(JournalEntry)
            .join(Journal)
            .filter(Journal.user_id==curr_user_id)
            .filter(JournalEntry.entry_date==entry_date)
            .first()
        )
        if existing_entry:
            return {"error": "Entry for this date already exists."}, 400
        
        iso_year, iso_week, _ = entry_date.isocalendar()

        week_journal = Journal.query.filter_by(user_id=curr_user_id, year=iso_year, week_number=iso_week).first()
        if not week_journal:
            ## add new week_journal record to Journal table
            week_journal = Journal(user_id=curr_user_id, year=iso_year,week_number=iso_week)
            db.session.add(week_journal)
            db.session.commit()
        
        ## add new entry to JournalEntry table
        new_entry = JournalEntry(
            journal_id = week_journal.id, 
            entry_date = entry_date,
            notes = data.get("notes"),
            mood_score = data.get("mood_score"),
            mood_tag = data.get("mood_tag")
        )

        try:
            db.session.add(new_entry)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500
        
        result = JournalEntrySchema().dump(new_entry)
        return result, 201


## '/entries/<int:entry_id>'
class Entry(Resource):
    @jwt_required()
    def get(self, entry_id):
        curr_user_id = get_jwt_identity()

        entry = (
            db.session.query(JournalEntry)
            .join(Journal)
            .filter(JournalEntry.id == entry_id)
            .filter(Journal.user_id == curr_user_id) 
            .first()
        )
        if not entry:
            return {"error": "Today Journal not found"}, 404 
     
        result = JournalEntrySchema().dump(entry)
        return jsonify(result)
    

    @jwt_required()
    def delete(self, entry_id):
        curr_user_id = get_jwt_identity()
        entry = (
            db.session.query(JournalEntry)
            .join(Journal)
            .filter(JournalEntry.id == entry_id)
            .filter(Journal.user_id == curr_user_id) 
            .first()
        )

        if not entry:
            return {"error": "Journal not found"}, 404
        try:
            db.session.delete(entry)
            db.session.commit()
            return {"message": "Journal deleted successfully"}, 200
        except Exception as e:
            return {"error": str(e)}, 500
        
    
    @jwt_required()
    def patch(self, entry_id):
        curr_user_id = get_jwt_identity()
        entry = (
            db.session.query(JournalEntry)
            .join(Journal)
            .filter(JournalEntry.id == entry_id)
            .filter(Journal.user_id == curr_user_id) 
            .first()
        )

        if not entry:
            return {"error": "Journal not found"}, 404
        
        data = request.get_json()
        entry.entry_date = datetime.strptime(data["entry_date"], "%Y-%m-%d").date() if "entry_date" in data else entry.entry_date
        entry.notes = data.get("notes", entry.notes)
        entry.mood_score = data.get("mood_score", entry.mood_score)
        entry.mood_tag = data.get("mood_tag", entry.mood_tag)

        try:   
            db.session.commit()  
            return JournalEntrySchema().dump(entry), 200 
        except ValueError as e:
            return {"errors": [str(e)]}, 400
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500


## '/entries/today'
class TodayEntry(Resource):
    @jwt_required()
    def get(self):
        curr_user_id = get_jwt_identity()
        today_str = date.today().isoformat()

        today_entry = (
            db.session.query(JournalEntry)
            .join(Journal)
            .filter(Journal.user_id==curr_user_id)
            .filter(JournalEntry.entry_date==today_str)
            .first()
        )

        if not today_entry:
            return {"message": "No journal found for today."}, 404

        return JournalEntrySchema().dump(today_entry), 200



class MonthlyEntries(Resource):
    @jwt_required()
    def get(self, year, month):
        curr_user_id = get_jwt_identity()

        month_entries = (
            JournalEntry.query
            .join(Journal)
            .filter(
                Journal.user_id==curr_user_id,
                extract('year', JournalEntry.entry_date)==year,
                extract('month', JournalEntry.entry_date)==month
            )
            .all()
        )
        return jsonify(JournalEntrySchema(many=True).dump(month_entries))



class MonthlyEntriesAnalysis(Resource):
    @jwt_required()
    def get(self, year, month):
        curr_user_id = get_jwt_identity()

        month_entries = (
            JournalEntry.query
            .join(Journal)
            .filter(
                Journal.user_id==curr_user_id,
                extract('year', JournalEntry.entry_date)==year,
                extract('month', JournalEntry.entry_date)==month
            )
            .all()
        )
        data = [
            {
                "entry_date": entry.entry_date.isoformat(),
                "mood_score": entry.mood_score,
                "mood_tag": entry.mood_tag,
                "notes": entry.notes
            }
            for entry in month_entries
        ]
        return {"entries": data}, 200