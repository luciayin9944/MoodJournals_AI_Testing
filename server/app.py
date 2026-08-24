# app.py

from flask import Flask, request, jsonify, make_response
from flask_restful import Api
from config import db, bcrypt, jwt, Config
from flask_cors import CORS

from resources.word_cloud import MonthlyWordCloud
from resources.ai_suggestion import AiSuggestion
from resources.auth import Signup, WhoAmI, Login
from resources.entries import NewEntry, Entry, TodayEntry, MonthlyEntries, MonthlyEntriesAnalysis
from resources.journals import JournalList, WeeklyJournal, WeeklyAnalysis, HasJournalEntries



def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    CORS(app)
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    api = Api(app)

    # API resources
    # Auth
    api.add_resource(Signup, '/signup')
    api.add_resource(Login, '/login')
    api.add_resource(WhoAmI, '/me')

    # Journal (weekly)
    api.add_resource(JournalList, '/journals')  # GET list paginated
    api.add_resource(WeeklyJournal, '/journals/<int:year>/<int:week_number>')  # GET entries in week
    api.add_resource(HasJournalEntries, '/journals/<int:year>/<int:week_number>/has_entries')
    api.add_resource(WeeklyAnalysis, '/journals/<int:year>/<int:week_number>/analysis')
    api.add_resource(AiSuggestion, '/journals/<int:year>/<int:week_number>/suggestion')

    # Entry (daily)
    api.add_resource(NewEntry, '/entries')  # POST new, GET by entry_id
    api.add_resource(Entry, '/entries/<int:entry_id>')  # PATCH, DELETE
    api.add_resource(TodayEntry, '/entries/today')  # GET today's entry
    api.add_resource(MonthlyEntries, '/entries/<int:year>/<int:month>')
    api.add_resource(MonthlyEntriesAnalysis, '/entries/<int:year>/<int:month>/analysis')
    api.add_resource(MonthlyWordCloud, '/entries/<int:year>/<int:month>/word_cloud')
      

    return app





        


        