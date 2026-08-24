### OpenAi API

from flask_restful import Resource
from flask_jwt_extended import get_jwt_identity, jwt_required
from models import * 
import os
from dotenv import load_dotenv
from openai import OpenAI
import json

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class AiSuggestion(Resource):
    @jwt_required()
    def post(self, year, week_number):
        curr_user_id = get_jwt_identity()

        week_journal = Journal.query.filter_by(user_id=curr_user_id, year=year, week_number=week_number).first()
        if not week_journal:
            return {"message": "No journal found for this week."}, 404
        
        # if suggestion exist, return result. Don't generate new suggestions!
        suggestion = Suggestion.query.filter_by(journal_id=week_journal.id).first()
        if suggestion:
            result = SuggestionSchema().dump(suggestion)
            return result, 200
        
        entries = JournalEntry.query.filter_by(journal_id=week_journal.id).order_by(JournalEntry.entry_date.asc()).all()

        if len(entries) < 4:
            return {"message": "Not enough journal entries to generate summary (minimum 4 required)."}, 400

        ##WRONG; entries_dicts = jsonify(JournalEntrySchema(many=True).dump(entries))
        entry_dicts = JournalEntrySchema(many=True).dump(entries)
        combined_text = "\n".join(
            [f"{entry['entry_date']}: {entry['notes']}" for entry in entry_dicts if entry.get("notes")]
        )

        prompt = f"""
        You are a mental health assistant. Please analyze the following weekly journal logs and return your response in valid JSON with two fields: "summary" and "self_care_tips" (an array of 3 tips).
        For the entire week:
        1. Summarize the emotional trend over the week in 2-3 sentences.
        2. Provide 3 personalized, practical self-care suggestions based on the emotional needs.

        Weekly Journal Entries:
        {combined_text}

        Return format:
        {{
            "summary": "<your summary here>",
            "self_care_tips": [
                "<tip 1>",
                "<tip 2>",
                "<tip 3>"
            ]
        }}
        """

        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a supportive and insightful AI assistant focused on emotional well-being."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            ai_result = response.choices[0].message.content.strip()

            parsed = json.loads(ai_result)
            summary = parsed.get("summary", "")
            tips = parsed.get("self_care_tips", [])
            # tips_text = "\n".join(tips)
            tips_text = json.dumps(tips)
        except json.JSONDecodeError:
            return {"error": "Failed to parse AI response as JSON."}, 500
        except Exception as e:
            return {"error": f"OpenAI API error: {str(e)}"}, 500

        ## add new suggestion to Suggestion table
        new_suggestion = Suggestion(
            journal_id = week_journal.id, 
            summary = summary,
            selfcare_tips = tips_text
        )

        try:
            db.session.add(new_suggestion)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500
        
        result = SuggestionSchema().dump(new_suggestion)
        return result, 201
    


    @jwt_required()
    def get(self, year, week_number):
        curr_user_id = get_jwt_identity()

        suggestion = (
            Suggestion.query
            .join(Journal)
            .filter(
                Journal.user_id==curr_user_id,
                Journal.year==year,
                Journal.week_number==week_number
            ).first()
        )

        if suggestion:
            return {
                "summary": suggestion.summary,
                "selfcare_tips": suggestion.selfcare_tips
            }, 200
        else:
            return {"error": "No suggestion found for this week."}, 404

