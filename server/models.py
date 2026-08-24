## models.py

from sqlalchemy.orm import validates
from sqlalchemy.ext.hybrid import hybrid_property
from marshmallow import Schema, fields, validate
from config import db, bcrypt
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    _password_hash = db.Column(db.String)

    journals = db.relationship('Journal', back_populates='user', cascade='all, delete-orphan')

    @hybrid_property
    def password_hash(self):
        raise AttributeError("Password hashes may not be viewed.")
    
    @password_hash.setter
    def password_hash(self, password):
        self._password_hash = bcrypt.generate_password_hash(password).decode('utf-8')


    def authenticate(self, password):
        return bcrypt.check_password_hash(self._password_hash, password.encode('utf-8'))
    
    @validates('email')
    def validate_email(self, key, address):
        if '@' not in address:
            raise ValueError("Failed email validation")
        return address
    
    def __repr__(self):
        return f'User {self.username}, ID {self.id}'
    

class Journal(db.Model):
    __tablename__ = 'journals'

    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer)
    week_number = db.Column(db.Integer)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User', back_populates='journals')

    journal_entries = db.relationship('JournalEntry', back_populates='journal',cascade='all, delete-orphan')
    suggestion = db.relationship('Suggestion', back_populates='journal', uselist=False)

    @validates("year")
    def validate_year(self, key, value):
        current_year = datetime.now().year
        if value < current_year:
            raise ValueError("Year must be the current year or later.")
        return value


class JournalEntry(db.Model):
    __tablename__ = 'journal_entries'

    id = db.Column(db.Integer, primary_key=True)
    entry_date = db.Column(db.Date, nullable=False)
    notes = db.Column(db.Text)
    mood_score = db.Column(db.Integer, nullable=False)
    mood_tag = db.Column(db.String, nullable=False, server_default='Other')

    journal_id = db.Column(db.Integer, db.ForeignKey('journals.id'))
    journal = db.relationship('Journal', back_populates='journal_entries')

    @validates("mood_tag")
    def validate_mood_tag(self, key, value):
        allowed = {
            'Happy', 'Joyful', 'Excited', 'Hopeful', 'Relaxed', 'Calm', 'Normal', 'Sad', 'Angry', 'Anxious', 'Stressed', 'Lonely',
            'Focused', 'Productive', 'Relieved', 'Worried', 'Tired', 'Overwhelmed', 'Bored', 'Disappointed', 'Nervous', 'Other'
        }
        if value not in allowed:
            raise ValueError(f"Invalid mood tag: {value}")
        return value
    
    @validates("mood_score")
    def validate_mood_score(self, key, value):
        if not isinstance(value, int):
            raise ValueError("Mood score must be an integer.")
        if value < 1 or value > 10:
            raise ValueError("Mood score must be between 1 and 10.")
        return value


class Suggestion(db.Model):
    __tablename__ = 'suggestions'

    id = db.Column(db.Integer, primary_key=True)
    summary = db.Column(db.Text, nullable=False)
    selfcare_tips = db.Column(db.Text, nullable=False)

    journal_id = db.Column(db.Integer, db.ForeignKey('journals.id'))
    journal = db.relationship('Journal', back_populates='suggestion')



class UserSchema(Schema):
    id = fields.Int()
    username = fields.Str()
    email = fields.Email()
    journals = fields.List(fields.Nested(lambda:JournalSchema(exclude=("user",))))


class JournalSchema(Schema):
    id = fields.Int()
    year = fields.Int()
    week_number = fields.Int()
    user = fields.Nested(lambda: UserSchema(exclude=("journals", )))

    journal_entries = fields.List(fields.Nested(lambda: JournalEntrySchema(exclude=("journal", ))))
    suggestion = fields.Nested(lambda:SuggestionSchema(exclude=("journal", )))


class JournalEntrySchema(Schema):
    id = fields.Int()
    entry_date = fields.Date()
    notes = fields.Str(validate=validate.Length(max=1000))
    mood_score = fields.Int()
    mood_tag = fields.Str()
    journal = fields.Nested(lambda:JournalSchema(exclude=("journal_entries", )))


class SuggestionSchema(Schema):
    id = fields.Int()
    summary = fields.Str(validate=validate.Length(max=1000))
    selfcare_tips = fields.Str(validate=validate.Length(max=2000))

    journal = fields.Nested(lambda:JournalSchema(exclude=("suggestion", )))





        

