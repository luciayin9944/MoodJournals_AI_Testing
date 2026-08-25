# # seed.py

from app import create_app
from config import db
from models import User, Journal, JournalEntry, Suggestion
from datetime import date
import json


def reset_database():
    db.drop_all()
    db.create_all()

def seed_data():
    # user
    user = User(
        username="testuser",
        email="test@example.com",
    )
    user.password_hash = "password123"  
    db.session.add(user)
    db.session.commit()

    ## === Week 25 ===
    journal_25 = Journal(
        week_number=25,
        year=2026,
        user_id=user.id
    )
    db.session.add(journal_25)
    db.session.commit()

    entries_25 = [
        JournalEntry(journal_id=journal_25.id, entry_date=date(2026, 6, 15), mood_tag="Happy", mood_score=7, notes="Great start to the week."),
        JournalEntry(journal_id=journal_25.id, entry_date=date(2026, 6, 16), mood_tag="Tired", mood_score=5, notes="Didn't sleep well last night."),
        JournalEntry(journal_id=journal_25.id, entry_date=date(2026, 6, 17), mood_tag="Productive", mood_score=8, notes="Knocked out all my to-dos."),
        JournalEntry(journal_id=journal_25.id, entry_date=date(2026, 6, 18), mood_tag="Relaxed", mood_score=6, notes="Took time to unwind."),
        JournalEntry(journal_id=journal_25.id, entry_date=date(2026, 6, 19), mood_tag="Lonely", mood_score=4, notes="Felt isolated today."),
        JournalEntry(journal_id=journal_25.id, entry_date=date(2026, 6, 20), mood_tag="Joyful", mood_score=9, notes="Hung out with friends."),
        JournalEntry(journal_id=journal_25.id, entry_date=date(2026, 6, 21), mood_tag="Calm", mood_score=7, notes="Peaceful Sunday.")
    ]
    db.session.add_all(entries_25)

    suggestion_25 = Suggestion(
        journal_id=journal_25.id,
        summary="Week started strong with happiness and productivity, dipped mid-week due to loneliness but ended joyfully and peacefully.",
        selfcare_tips=json.dumps([
            "1. Reach out to friends when feeling lonely, even for a short call.",
            "2. Maintain consistent sleep habits to stay energized during the week."
        ])
    )
    db.session.add(suggestion_25)

    ## === Week 26 ===
    journal_26 = Journal(
        week_number=26,
        year=2026,
        user_id=user.id
    )
    db.session.add(journal_26)
    db.session.commit()

    entries_26 = [
        JournalEntry(journal_id=journal_26.id, entry_date=date(2026, 6, 22), mood_tag="Hopeful", mood_score=7, notes="Started new goals."),
        JournalEntry(journal_id=journal_26.id, entry_date=date(2026, 6, 23), mood_tag="Bored", mood_score=4, notes="Day felt slow."),
        JournalEntry(journal_id=journal_26.id, entry_date=date(2026, 6, 24), mood_tag="Productive", mood_score=8, notes="Accomplished a lot."),
        JournalEntry(journal_id=journal_26.id, entry_date=date(2026, 6, 25), mood_tag="Anxious", mood_score=5, notes="Upcoming presentation."),
        JournalEntry(journal_id=journal_26.id, entry_date=date(2026, 6, 26), mood_tag="Stressed", mood_score=4, notes="Too many tasks."),
        JournalEntry(journal_id=journal_26.id, entry_date=date(2026, 6, 27), mood_tag="Relaxed", mood_score=7, notes="Took a break."),
        JournalEntry(journal_id=journal_26.id, entry_date=date(2026, 6, 28), mood_tag="Excited", mood_score=9, notes="Looking forward to next week.")
    ]
    db.session.add_all(entries_26)

    suggestion_26 = Suggestion(
        journal_id=journal_26.id,
        summary="Productivity was high but anxiety and stress spiked mid-week. Ending the week excited is a positive sign.",
        selfcare_tips=json.dumps([
            "1. Break large tasks into smaller ones to reduce stress.",
            "2. Allow time to recharge on weekends to prevent burnout."
        ])
    )
    db.session.add(suggestion_26)

    ## === Week 27 ===
    journal_27 = Journal(
        week_number=27,
        year=2026,
        user_id=user.id
    )
    db.session.add(journal_27)
    db.session.commit()

    entries_27 = [
        JournalEntry(journal_id=journal_27.id, entry_date=date(2026, 6, 29), mood_tag="Nervous", mood_score=5, notes="Big meeting today."),
        JournalEntry(journal_id=journal_27.id, entry_date=date(2026, 6, 30), mood_tag="Productive", mood_score=8, notes="Crushed all tasks."),
        JournalEntry(journal_id=journal_27.id, entry_date=date(2026, 7, 1), mood_tag="Angry", mood_score=3, notes="Conflict with coworker."),
        JournalEntry(journal_id=journal_27.id, entry_date=date(2026, 7, 2), mood_tag="Happy", mood_score=7, notes="Resolved issues. Felt better."),
        JournalEntry(journal_id=journal_27.id, entry_date=date(2026, 7, 3), mood_tag="Joyful", mood_score=8, notes="Celebrated the holiday."),
        JournalEntry(journal_id=journal_27.id, entry_date=date(2026, 7, 4), mood_tag="Tired", mood_score=5, notes="Stayed up too late."),
        JournalEntry(journal_id=journal_27.id, entry_date=date(2026, 7, 5), mood_tag="Relaxed", mood_score=6, notes="Catching up on sleep.")
    ]
    db.session.add_all(entries_27)

    suggestion_27 = Suggestion(
        journal_id=journal_27.id,
        summary="Despite emotional lows early in the week, things improved with resolution, joy, and rest.",
        selfcare_tips=json.dumps([
            "1. Try journaling after emotional conflict to gain perspective.",
            "2. Maintain healthy sleep routines to stay emotionally balanced."
        ])
    )
    db.session.add(suggestion_27)

    ## === Week 28 ===
    journal_28 = Journal(
        week_number=28,
        year=2026,
        user_id=user.id
    )
    db.session.add(journal_28)
    db.session.commit()

    entries_28 = [
        JournalEntry(journal_id=journal_28.id, entry_date=date(2026, 7, 6), mood_tag="Sad", mood_score=4, notes="Felt low in the morning."),
        JournalEntry(journal_id=journal_28.id, entry_date=date(2026, 7, 7), mood_tag="Calm", mood_score=6, notes="Walked in nature."),
        JournalEntry(journal_id=journal_28.id, entry_date=date(2026, 7, 8), mood_tag="Overwhelmed", mood_score=3, notes="Too much on my plate."),
        JournalEntry(journal_id=journal_28.id, entry_date=date(2026, 7, 9), mood_tag="Hopeful", mood_score=7, notes="Things might get better."),
        JournalEntry(journal_id=journal_28.id, entry_date=date(2026, 7, 10), mood_tag="Productive", mood_score=8, notes="Completed a major task."),
        JournalEntry(journal_id=journal_28.id, entry_date=date(2026, 7, 12), mood_tag="Stressed", mood_score=5, notes="Preparing for next week."),
        JournalEntry(journal_id=journal_28.id, entry_date=date(2026, 7, 12), mood_tag="Relaxed", mood_score=7, notes="Rested and recovered.")
    ]
    db.session.add_all(entries_28)

    suggestion_28 = Suggestion(
        journal_id=journal_28.id,
        summary="The week began with sadness and stress but ended with productivity and relaxation. A good recovery trend.",
        selfcare_tips=json.dumps([
            "1. Keep practicing gratitude and hopeful thinking.",
            "2. Use relaxation techniques like deep breathing or nature walks mid-week when feeling overwhelmed."
        ])
    )
    db.session.add(suggestion_28)

    ## === Week 29 ===
    journal_29 = Journal(
        week_number=29,
        year=2026,
        user_id=user.id
    )
    db.session.add(journal_29)
    db.session.commit()

    entries_29 = [
        JournalEntry(journal_id=journal_29.id, entry_date=date(2026, 7, 13), mood_tag="Tired", mood_score=4, notes="Felt very tired after work. Just wanted to sleep."),
        JournalEntry(journal_id=journal_29.id, entry_date=date(2026, 7, 14), mood_tag="Happy", mood_score=7, notes="Had a productive morning. Mood was better than yesterday."),
        JournalEntry(journal_id=journal_29.id, entry_date=date(2026, 7, 15), mood_tag="Overwhelmed", mood_score=5, notes="Too many meetings. Overwhelmed and drained."),
        JournalEntry(journal_id=journal_29.id, entry_date=date(2026, 7, 16), mood_tag="Joyful", mood_score=7, notes="Spent time with friends. Laughed a lot. Felt good."),
        JournalEntry(journal_id=journal_29.id, entry_date=date(2026, 7, 17), mood_tag="Tired", mood_score=5, notes="Low energy all day. Didn't feel like doing much."),
        JournalEntry(journal_id=journal_29.id, entry_date=date(2026, 7, 18), mood_tag="Joyful", mood_score=9, notes="Went hiking. It helped clear my mind."),
        JournalEntry(journal_id=journal_29.id, entry_date=date(2026, 7, 19), mood_tag="Anxious", mood_score=9, notes="Back to work stress again. Feeling anxious about deadlines.")
    ]
    db.session.add_all(entries_29)

    suggestion_29 = Suggestion(
        journal_id=journal_29.id,
        summary="The emotional trend seems to fluctuate throughout the week, with moments of tiredness, productivity, overwhelm, joy with friends, low energy, clarity after hiking, and anxiety about work deadlines.",
        selfcare_tips=json.dumps([
            "1. Practice mindfulness techniques to manage feelings of overwhelm and anxiety. Take a few minutes each day to focus on your breath and bring yourself back to the present moment.",
            "2. Prioritize self-care activities that bring you joy and energy, such as spending more time with friends, engaging in activities you love, or getting regular exercise to boost your mood and energy levels."
        ])
    )
    db.session.add(suggestion_29)

    ## === Week 30 ===
    journal_30 = Journal(
        week_number=30,
        year=2026,
        user_id=user.id
    )
    db.session.add(journal_30)
    db.session.commit()

    entries_30 = [
        JournalEntry(journal_id=journal_30.id, entry_date=date(2026, 7, 20), mood_tag="Calm", mood_score=6, notes="Started the week with meditation. Felt peaceful."),
        JournalEntry(journal_id=journal_30.id, entry_date=date(2026, 7, 21), mood_tag="Productive", mood_score=8, notes="Deep work session. Made good progress."),
        JournalEntry(journal_id=journal_30.id, entry_date=date(2026, 7, 22), mood_tag="Disappointed", mood_score=5, notes="Hard to stay focused today."),
        JournalEntry(journal_id=journal_30.id, entry_date=date(2026, 7, 23), mood_tag="Joyful", mood_score=7, notes="Talked to family. Reminded me of what's important."),
        JournalEntry(journal_id=journal_30.id, entry_date=date(2026, 7, 24), mood_tag="Productive", mood_score=8, notes="Great workout today."),
        JournalEntry(journal_id=journal_30.id, entry_date=date(2026, 7, 25), mood_tag="Relaxed", mood_score=7, notes="Relaxed weekend. Feeling balanced."),
        JournalEntry(journal_id=journal_30.id, entry_date=date(2026, 7, 26), mood_tag="Worried", mood_score=4, notes="Worried about upcoming deadlines.")
    ]
    db.session.add_all(entries_30)

    suggestion_30 = Suggestion(
        journal_id=journal_30.id,
        summary="The week started peacefully and productively but ended with some worry. Balancing mindfulness and productivity helped, but stress resurfaced.",
        selfcare_tips=json.dumps([
            "1. Maintain daily mindfulness practices, such as morning meditation or evening journaling, to help stabilize your mood and maintain calm through the week.",
            "2. When experiencing worry or mental overload, break your workload into small, manageable tasks, and use tools like time blocking or to-do lists to regain clarity and control.",
            "3. Make time for regular connection with loved ones, especially on stressful days. Talking to a supportive friend or family member can help reduce worry and remind you of your support system."
        ])
    )
    db.session.add(suggestion_30)

    ## === Week 31 ===
    journal_31 = Journal(
        week_number=31,
        year=2026,
        user_id=user.id
    )
    db.session.add(journal_31)
    db.session.commit()

    entries_31 = [
        JournalEntry(journal_id=journal_31.id, entry_date=date(2026, 7, 27), mood_tag="Productive", mood_score=7, notes="Set clear goals. Felt motivated."),
        JournalEntry(journal_id=journal_31.id, entry_date=date(2026, 7, 28), mood_tag="Overwhelmed", mood_score=4, notes="Technical issues blocked my progress."),
        JournalEntry(journal_id=journal_31.id, entry_date=date(2026, 7, 29), mood_tag="Hopeful", mood_score=6, notes="Found a workaround. Things are looking up."),
        JournalEntry(journal_id=journal_31.id, entry_date=date(2026, 7, 30), mood_tag="Productive", mood_score=8, notes="Big breakthrough! Finished major task."),
        JournalEntry(journal_id=journal_31.id, entry_date=date(2026, 8, 31), mood_tag="Calm", mood_score=7, notes="Smooth day. Kept a good pace."),
        JournalEntry(journal_id=journal_31.id, entry_date=date(2026, 8, 1), mood_tag="Relaxed", mood_score=5, notes="Didn't do much. Just rested."),
        JournalEntry(journal_id=journal_31.id, entry_date=date(2026, 8, 2), mood_tag="Calm", mood_score=8, notes="Reflected on the week. Felt proud.")
    ]
    db.session.add_all(entries_31)

    suggestion_31 = Suggestion(
        journal_id=journal_31.id,
        summary="This week was a rollercoaster: frustration mid-week, recovery, then solid wins and reflection. Good resilience shown.",
        selfcare_tips=json.dumps([
            "1. Recognize and celebrate your small and large accomplishments. Writing them down at the end of the day can build confidence and motivation.",
            "2. During periods of frustration or technical blockers, step away briefly to reset. A short walk or deep breathing session can improve focus and reduce stress.",
            "3. Balance your drive with rest. Incorporate intentional rest on weekends—unplug from work, limit screen time, and engage in relaxing hobbies that restore your energy."
        ])
    )
    db.session.add(suggestion_31)
    db.session.commit()

    ## === Week 32 ===
    journal_32 = Journal(
        week_number=32,
        year=2026,
        user_id=user.id
    )
    db.session.add(journal_32)
    db.session.commit()

    entries_32 = [
        JournalEntry(journal_id=journal_32.id, entry_date=date(2026, 8, 3), mood_tag="Focused", mood_score=7, notes="Got into deep work mode. Finished key part of the project."),
        JournalEntry(journal_id=journal_32.id, entry_date=date(2026, 8, 5), mood_tag="Tired", mood_score=5, notes="Didn't sleep well. Had to push through the day."),
        JournalEntry(journal_id=journal_32.id, entry_date=date(2026, 8, 6), mood_tag="Excited", mood_score=8, notes="Pushed through a long day of coding. The project is nearly done, feeling tired but excited to see it coming together.")
    ]
    db.session.add_all(entries_32)
    db.session.commit()


    ## === Week 33 ===
    journal_33 = Journal(
        week_number=33,
        year=2026,
        user_id=user.id
    )
    db.session.add(journal_33)
    db.session.commit()

    entries_33 = [
        JournalEntry(journal_id=journal_33.id, entry_date=date(2026, 8, 10), mood_tag="Focused", mood_score=7, notes="Worked through tasks steadily."),
        JournalEntry(journal_id=journal_33.id, entry_date=date(2026, 8, 11), mood_tag="Tired", mood_score=4, notes="Lacked energy, tough to concentrate."),
        JournalEntry(journal_id=journal_33.id, entry_date=date(2026, 8, 12), mood_tag="Other", mood_score=6, notes="Positive feedback boosted confidence."),
        JournalEntry(journal_id=journal_33.id, entry_date=date(2026, 8, 13), mood_tag="Productive", mood_score=8, notes="Good momentum. Finished key tasks."),
        JournalEntry(journal_id=journal_33.id, entry_date=date(2026, 8, 14), mood_tag="Calm", mood_score=7, notes="Smooth day, managed stress better."),
        JournalEntry(journal_id=journal_33.id, entry_date=date(2026, 8, 15), mood_tag="Relaxed", mood_score=6, notes="Took some downtime, recharged."),
        JournalEntry(journal_id=journal_33.id, entry_date=date(2026, 8, 16), mood_tag="Happy", mood_score=8, notes="Looked back at progress. Feeling steady.")
    ]
    db.session.add_all(entries_33)

    suggestion_33 = Suggestion(
        journal_id=journal_33.id,
        summary="The week showed ups and downs in energy, but consistent progress and feedback helped you maintain momentum.",
        selfcare_tips=json.dumps([
            "1. Build a short daily wind-down routine to improve sleep quality and energy levels.",
            "2. When tired, try shifting to lighter tasks instead of forcing focus—this keeps productivity flowing.",
            "3. Keep acknowledging positive feedback and progress; it reinforces confidence and motivation."
        ])
    )
    db.session.add(suggestion_33)
    db.session.commit()


    ## === Week 34 ===
    journal_34 = Journal(
        week_number=34,
        year=2026,
        user_id=user.id
    )
    db.session.add(journal_34)
    db.session.commit()

    entries_34 = [
        JournalEntry(journal_id=journal_34.id, entry_date=date(2026, 8, 17), mood_tag="Hopeful", mood_score=7, notes="Started week with new goals."),
        JournalEntry(journal_id=journal_34.id, entry_date=date(2026, 8, 18), mood_tag="Overwhelmed", mood_score=5, notes="Ran into unexpected issues."),
        JournalEntry(journal_id=journal_34.id, entry_date=date(2026, 8, 19), mood_tag="Excited", mood_score=6, notes="Pushed through difficulties."),
        JournalEntry(journal_id=journal_34.id, entry_date=date(2026, 8, 20), mood_tag="Productive", mood_score=8, notes="Breakthrough with problem-solving."),
        JournalEntry(journal_id=journal_34.id, entry_date=date(2026, 8, 21), mood_tag="Other", mood_score=7, notes="Wrapped up tasks successfully."),
        JournalEntry(journal_id=journal_34.id, entry_date=date(2026, 8, 22), mood_tag="Calm", mood_score=6, notes="Enjoyed a slow day."),
        JournalEntry(journal_id=journal_34.id, entry_date=date(2026, 8, 23), mood_tag="Calm", mood_score=8, notes="Weekend reflection, steady mood.")
    ]
    db.session.add_all(entries_34)

    suggestion_34 = Suggestion(
        journal_id=journal_34.id,
        summary="Challenges tested your patience, but persistence and breakthroughs made the week successful overall.",
        selfcare_tips=json.dumps([
            "1. When problems arise, pause to brainstorm multiple solutions instead of sticking to one path.",
            "2. Use quick stress-relief techniques (like stretching or box breathing) during frustrating moments.",
            "3. End your week with gratitude journaling to reinforce resilience and positive perspective."
        ])
    )
    db.session.add(suggestion_34)
    db.session.commit()


    # ## === Week 35 ===
    # journal_35 = Journal(
    #     week_number=35,
    #     year=2026,
    #     user_id=user.id
    # )
    # db.session.add(journal_35)
    # db.session.commit()

    # entries_35 = [
    #     JournalEntry(journal_id=journal_35.id, entry_date=date(2026, 8, 24), mood_tag="Focused", mood_score=8, notes="Strong start, clear priorities."),
    #     JournalEntry(journal_id=journal_35.id, entry_date=date(2026, 8, 25), mood_tag="Overwhelmed", mood_score=5, notes="Too many tasks piled up."),
    #     JournalEntry(journal_id=journal_35.id, entry_date=date(2026, 8, 26), mood_tag="Focused", mood_score=7, notes="Prioritized tasks, felt more in control."),
    #     JournalEntry(journal_id=journal_35.id, entry_date=date(2026, 8, 27), mood_tag="Excited", mood_score=8, notes="Finished major milestones."),
    #     JournalEntry(journal_id=journal_35.id, entry_date=date(2026, 8, 28), mood_tag="Calm", mood_score=7, notes="Handled tasks steadily."),
    #     JournalEntry(journal_id=journal_35.id, entry_date=date(2026, 8, 29), mood_tag="Joyful", mood_score=9, notes="Enjoyed long weekend, relaxed outdoors."),
    #     JournalEntry(journal_id=journal_35.id, entry_date=date(2026, 8, 30), mood_tag="Joyful", mood_score=9, notes="Went camping with family and friends, felt refreshed and happy.")
    # ]
    # db.session.add_all(entries_35)

    # suggestion_35 = Suggestion(
    #     journal_id=journal_35.id,
    #     summary="This week balanced motivation, pressure, and achievement. Despite midweek stress, you refocused and accomplished key milestones. Ending the week with a long weekend camping trip brought joy, connection, and renewal.",
    #     selfcare_tips=json.dumps([
    #         "1. Use nature breaks like camping or outdoor walks regularly to recharge and restore balance.",
    #         "2. When feeling overwhelmed, lean on social connections—sharing time with friends or family can ease stress and boost mood.",
    #         "3. Continue celebrating progress with gratitude and reflection, especially after combining hard work with meaningful rest."
    #     ])
    # )
    # db.session.add(suggestion_35)
    # db.session.commit()


    #     ## === Week 36 ===
    # journal_36 = Journal(
    #     week_number=36,
    #     year=2026,
    #     user_id=user.id
    # )
    # db.session.add(journal_36)
    # db.session.commit()

    # entries_36 = [
    #     JournalEntry(journal_id=journal_36.id, entry_date=date(2026, 8, 31), mood_tag="Excited", mood_score=8, notes="Kicked off a new project. Energy was high, felt motivated."),
    #     JournalEntry(journal_id=journal_36.id, entry_date=date(2026, 9, 1), mood_tag="Focused", mood_score=7, notes="Spent hours planning project tasks. Clear roadmap, but workload looks heavy."),
    #     JournalEntry(journal_id=journal_36.id, entry_date=date(2026, 9, 2), mood_tag="Productive", mood_score=8, notes="Good progress on initial setup. Momentum is strong."),
    #     JournalEntry(journal_id=journal_36.id, entry_date=date(2026, 9, 3), mood_tag="Anxious", mood_score=5, notes="Started looking at job postings. The market seems very competitive."),
    #     JournalEntry(journal_id=journal_36.id, entry_date=date(2026, 9, 4), mood_tag="Stressed", mood_score=4, notes="Applied to a few positions but didn’t get responses. Felt pressure mounting."),
    #     JournalEntry(journal_id=journal_36.id, entry_date=date(2026, 9, 5), mood_tag="Tired", mood_score=5, notes="Worked late on both project and job search. Felt drained."),
    #     JournalEntry(journal_id=journal_36.id, entry_date=date(2026, 9, 6), mood_tag="Hopeful", mood_score=6, notes="Took a break, tried to reset mindset. Still hopeful things will work out.")
    # ]
    # db.session.add_all(entries_36)

    # ## === Week 37 ===
    # journal_37 = Journal(
    #     week_number=37,
    #     year=2026,
    #     user_id=user.id
    # )
    # db.session.add(journal_37)
    # db.session.commit()

    # entries_37 = [
    #     JournalEntry(journal_id=journal_37.id, entry_date=date(2026, 9, 7), mood_tag="Nervous", mood_score=5, notes="Prepared for interviews, but job rejections still in mind."),
    #     JournalEntry(journal_id=journal_37.id, entry_date=date(2026, 9, 8), mood_tag="Overwhelmed", mood_score=4, notes="Balancing project work and job search feels exhausting. Need better routine.")
    # ]
    # db.session.add_all(entries_37)

    
    print("✅ Database seeded successfully.")

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        reset_database()
        seed_data()





