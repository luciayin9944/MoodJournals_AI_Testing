from models import *  
from .embedding_service import generate_embedding
from datetime import date
from dateutil.relativedelta import relativedelta

def get_date_range(time_range):
    end_date  = date.today()

    if time_range == "all_time":
        return None, end_date
    
    months = {
        "3_months": 3,
        "6_months": 6,
        "1_year": 12,
    }

    if time_range not in months:
        raise ValueError("Unsupported time_range.")

    start_date = end_date - relativedelta(months=months[time_range])
    return start_date, end_date


def retrieval_entries(user_id, question, time_range, top_k=10):
    start_date, end_date = get_date_range(time_range)
    question_embedding = generate_embedding(question)

    query = (
        JournalEntry.query
        .join(Journal)
        .filter(
            Journal.user_id==user_id,
            JournalEntry.embedding.isnot(None),
            JournalEntry.entry_date <= end_date,
        )
    )

    if start_date is not None:
        query = query.filter(
            JournalEntry.entry_date >= start_date
        )

    entries = (
        query.order_by(
            JournalEntry.embedding.cosine_distance(question_embedding),
            JournalEntry.id,
        )
        .limit(top_k)
        .all()
    )

    return entries

    

    
# ## for testing 
# def main():
#     from app import create_app

#     app = create_app()

#     with app.app_context():
#         entries = retrieval_entries(
#             user_id=1,
#             question="What situations usually make me feel anxious?",
#             time_range="all_time",
#             top_k=5,
#         )

#         print(f"Found {len(entries)} entries.\n")

#         for entry in entries:
#             print(f"ID: {entry.id} | Date: {entry.entry_date}")
#             print(f"Mood: {entry.mood_tag} | Score: {entry.mood_score}")
#             print(entry.notes)
#             print()


# if __name__ == "__main__":
#     main()