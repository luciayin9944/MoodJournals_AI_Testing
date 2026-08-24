## word_cloud.py

from flask_restful import Resource
from flask_jwt_extended import get_jwt_identity, jwt_required
from models import *  
import re
from collections import Counter
from wordcloud import STOPWORDS
from sqlalchemy import extract

class MonthlyWordCloud(Resource):
    @jwt_required()
    def get(self, year, month):
        curr_user_id = get_jwt_identity()

        entries = (
            JournalEntry.query
            .join(Journal)
            .filter(
                Journal.user_id==curr_user_id,
                extract('year', JournalEntry.entry_date)==year,
                extract('month', JournalEntry.entry_date)==month
            ).all()
        )

        note_text = []
        for entry in entries:
            if entry.notes:
                note_text.append(entry.notes)
            else:
                note_text.append("")

        text = " ".join(note_text)
        ## remove punction
        text = re.sub(r'[^A-Za-z\s]', '', text)
        text = text.lower().split()
        stopwords = set(STOPWORDS)
        # Add custom stopwords
        stopwords.update(['feeling', 'felt', 'today', 'yesterday', 'didnt', 'time', 'day', 'went',
                   'much', 'wanted', 'lot', 'made']) 
        filtered_words = [word for word in text if word not in stopwords]

        word_freq = Counter(filtered_words)
        top_words = word_freq.most_common(50)

        word_cloud = []
        for word, freq in top_words:
            word_cloud.append({"text": word, "value": freq})
        
        return {"word_cloud": word_cloud}, 200