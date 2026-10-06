### OpenAi API

from flask import request
from flask_restful import Resource
from flask_jwt_extended import get_jwt_identity, jwt_required
from models import * 
import os
from datetime import date
from dotenv import load_dotenv
from openai import OpenAI
import json
from ai_validation import AIResponseValidationError, parse_and_validate_ai_response
from ai_safety import (
    AIContentSafetyError,
    AIGroundednessError,
    validate_ai_content_safety,
    validate_basic_groundedness,
)

load_dotenv()


def get_ai_client():
    return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class AiSuggestion(Resource):
    @jwt_required()
    def post(self, year, week_number):
        curr_user_id = get_jwt_identity()

        week_journal = Journal.query.filter_by(user_id=curr_user_id, year=year, week_number=week_number).first()
        if not week_journal:
            return {"message": "No journal found for this week."}, 404
        
        entries = JournalEntry.query.filter_by(journal_id=week_journal.id).order_by(JournalEntry.entry_date.asc()).all()

        if len(entries) < 4:
            return {"message": "Not enough journal entries to generate summary (minimum 4 required)."}, 400


        # Regeneration 
        data = request.get_json(silent=True) or {}
        if not isinstance(data, dict):
            return {"error": "Request body must be a JSON object."}, 400

        regenerate = data.get("regenerate") is True  #data = {"regenerate": True}
        current_year, current_week, _ = date.today().isocalendar()
        is_current_week = (
                year == current_year and week_number == current_week
        )

        if regenerate and not is_current_week:
            return {
                "error": "Only the current week's summary can be regenerated."
            }, 403

        suggestion = Suggestion.query.filter_by(journal_id=week_journal.id).first()

        ## Ordinary requests can reuse the saved summary.
        ## Regeneration requests continue to the existing AI generation code.
        if suggestion and not regenerate:
            result = SuggestionSchema().dump(suggestion)
            return result, 200

        #no regeneration:
        # if suggestion:
        #     result = SuggestionSchema().dump(suggestion)
        #     return result, 200

        ##WRONG: entries_dicts = jsonify(JournalEntrySchema(many=True).dump(entries))
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
            response = get_ai_client().chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a supportive and insightful AI assistant focused on emotional well-being."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )

            ai_result = response.choices[0].message.content.strip()

            # parsed = json.loads(ai_result)
            # summary = parsed.get("summary", "")
            # tips = parsed.get("self_care_tips", [])

            validated = parse_and_validate_ai_response(ai_result)
            validate_ai_content_safety(validated)
            validate_basic_groundedness(validated, entry_dicts)
            summary = validated["summary"]
            tips = validated["self_care_tips"]
            tips_text = json.dumps(tips)

        
        except AIResponseValidationError:
            return {"error": "AI response did not match the required format."}, 500
        except (AIContentSafetyError, AIGroundednessError):
            return {"error": "AI response did not pass deterministic content checks."}, 500
        except Exception:
            return {"error": "OpenAI API request failed."}, 500

        status_code = 200 if suggestion else 201

        try:
            if suggestion:
                # Regeneration: update the existing record.
                suggestion.summary = summary
                suggestion.selfcare_tips = tips_text
            else:
                # First generation: create a record.
                suggestion = Suggestion(
                    journal_id=week_journal.id,
                    summary=summary,
                    selfcare_tips=tips_text,
                )
                db.session.add(suggestion)

            db.session.commit()
        except Exception:
            db.session.rollback()
            return {"error": "Could not save the summary."}, 500

        result = SuggestionSchema().dump(suggestion)
        return result, status_code
                
        ##no Regeneration
        # try:
        #     new_suggestion = Suggestion(
        #         journal_id = week_journal.id, 
        #         summary = summary,
        #         selfcare_tips = tips_text
        #     )
        #     db.session.add(new_suggestion)
        #     db.session.commit()
        # except Exception as e:
        #     db.session.rollback()
        #     return {"error": str(e)}, 500
        
        # result = SuggestionSchema().dump(new_suggestion)
        # return result, 201
    


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

        # Do not display a summary left behind by the old deletion logic.
        if suggestion and JournalEntry.query.filter_by(journal_id=suggestion.journal_id).count() >= 4:
            return {
                "summary": suggestion.summary,
                "selfcare_tips": suggestion.selfcare_tips
            }, 200
        else:
            return {"error": "No suggestion found for this week."}, 404
