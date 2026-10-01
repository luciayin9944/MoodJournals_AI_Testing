##RAG API
from flask import request, current_app
from flask_restful import Resource
from flask_jwt_extended import get_jwt_identity, jwt_required
from services import rag_service
from services.exceptions import ProviderError, ProviderTimeoutError
from ai_validation import AIResponseValidationError


class LongTermAnalysis(Resource):
    @jwt_required()
    def post(self):
        curr_user_id = get_jwt_identity()

        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return {"error": "Request body must be a JSON object."}, 400

        question = data.get("question")
        if not isinstance(question, str) or not question.strip():
            return {"error": "Please select a question."}, 400
        question = question.strip()

        time_range = data.get("time_range")
        if time_range is None:
            time_range = "3_months" #default

        if time_range not in ("3_months", "6_months", "1_year", "all_time"):
            return {"error": "Unsupported time_range."}, 400

        # Run the RAG pipeline and translate failures into HTTP responses.
        try:
            result = rag_service.analyze_mood(
                user_id=curr_user_id,
                question=question,
                time_range=time_range,
            )

        except ProviderTimeoutError:
            current_app.logger.exception("Long-term analysis timed out")
            return {"error": "AI service timed out. Please try again."}, 504

        except ProviderError:
            current_app.logger.exception("Long-term analysis provider failed")
            return {"error": "AI service could not complete the analysis."}, 502

        except AIResponseValidationError:
            current_app.logger.exception("Long-term analysis response was invalid")
            return {"error": "AI service returned an invalid response."}, 502

        except Exception:
            current_app.logger.exception("Unexpected long-term analysis failure")
            return {"error": "Could not complete the analysis."}, 500

        return result, 200


        