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

    ## === Week 1: January 1–4 ===
    journal_1 = Journal(
        week_number=1,
        year=2026,
        user_id=user.id
    )
    db.session.add(journal_1)
    db.session.commit()

    entries_1 = [
        JournalEntry(journal_id=journal_1.id, entry_date=date(2026, 1, 1), mood_tag="Hopeful", mood_score=8, notes="Started the year with a quiet breakfast and a few realistic goals. Felt hopeful about making more time for myself."),
        JournalEntry(journal_id=journal_1.id, entry_date=date(2026, 1, 2), mood_tag="Stressed", mood_score=4, notes="Opened my work inbox and found several unfinished tasks waiting. Thinking about the backlog made it difficult to relax."),
        JournalEntry(journal_id=journal_1.id, entry_date=date(2026, 1, 3), mood_tag="Happy", mood_score=8, notes="Had dinner with family and shared stories from the holidays. Their company helped me stop worrying about work."),
        JournalEntry(journal_id=journal_1.id, entry_date=date(2026, 1, 4), mood_tag="Relaxed", mood_score=7, notes="Slept well and took a gentle walk in the afternoon. Felt calmer and more rested than earlier in the week.")
    ]
    db.session.add_all(entries_1)

    suggestion_1 = Suggestion(
        journal_id=journal_1.id,
        summary="The year began with hope, followed by stress about unfinished work. Family connection, restful sleep, and a quiet walk helped the week end more calmly.",
        selfcare_tips=json.dumps([
            "1. Choose one manageable task to start clearing the work backlog.",
            "2. Keep making time for supportive family conversations.",
            "3. Protect the sleep and quiet breaks that helped you feel rested."
        ])
    )
    db.session.add(suggestion_1)
    db.session.commit()

    ## === Week 2: January 5–11 ===
    journal_2 = Journal(
        week_number=2,
        year=2026,
        user_id=user.id
    )
    db.session.add(journal_2)
    db.session.commit()

    entries_2 = [
        JournalEntry(journal_id=journal_2.id, entry_date=date(2026, 1, 5), mood_tag="Anxious", mood_score=4, notes="A project presentation is coming up tomorrow. I kept rehearsing the opening because I was afraid of forgetting what to say."),
        JournalEntry(journal_id=journal_2.id, entry_date=date(2026, 1, 6), mood_tag="Relieved", mood_score=7, notes="Finished the presentation and answered the questions. The tension eased once I no longer had to imagine everything going wrong."),
        JournalEntry(journal_id=journal_2.id, entry_date=date(2026, 1, 7), mood_tag="Tired", mood_score=4, notes="Stayed up too late watching videos. With only five hours of sleep, even simple work felt slow."),
        JournalEntry(journal_id=journal_2.id, entry_date=date(2026, 1, 8), mood_tag="Stressed", mood_score=3, notes="Two deadlines landed on the same afternoon. I kept switching between tasks and felt behind on both."),
        JournalEntry(journal_id=journal_2.id, entry_date=date(2026, 1, 9), mood_tag="Joyful", mood_score=8, notes="Met friends for noodles after work. Laughing about old memories lifted the heavy mood I had carried all afternoon."),
        JournalEntry(journal_id=journal_2.id, entry_date=date(2026, 1, 10), mood_tag="Happy", mood_score=8, notes="Helped my family cook a long lunch. Enjoyed being together without having to rush anywhere."),
        JournalEntry(journal_id=journal_2.id, entry_date=date(2026, 1, 11), mood_tag="Relaxed", mood_score=7, notes="Took a short hike on a quiet trail. My work worries felt less intense after spending time outside.")
    ]
    db.session.add_all(entries_2)

    suggestion_2 = Suggestion(
        journal_id=journal_2.id,
        summary="Presentation anxiety eased after the event, but short sleep and overlapping deadlines brought tiredness and stress. Time with friends and family, followed by a hike, improved the end of the week.",
        selfcare_tips=json.dumps([
            "1. Use a brief rehearsal plan before presentations, with a clear stopping point.",
            "2. Break overlapping deadlines into smaller priorities.",
            "3. Preserve time for sleep, social connection, and outdoor breaks."
        ])
    )
    db.session.add(suggestion_2)
    db.session.commit()

    ## === Week 3: January 12–18 ===
    journal_3 = Journal(
        week_number=3,
        year=2026,
        user_id=user.id
    )
    db.session.add(journal_3)
    db.session.commit()

    entries_3 = [
        JournalEntry(journal_id=journal_3.id, entry_date=date(2026, 1, 12), mood_tag="Productive", mood_score=7, notes="Had a quiet morning to finish one task at a time. Seeing the list get shorter felt satisfying."),
        JournalEntry(journal_id=journal_3.id, entry_date=date(2026, 1, 13), mood_tag="Nervous", mood_score=4, notes="A recruiter scheduled an interview. I kept wondering whether I would freeze when asked to explain my experience."),
        JournalEntry(journal_id=journal_3.id, entry_date=date(2026, 1, 14), mood_tag="Hopeful", mood_score=6, notes="Practiced interview questions with a friend. Their patient feedback made the upcoming conversation feel more manageable."),
        JournalEntry(journal_id=journal_3.id, entry_date=date(2026, 1, 15), mood_tag="Normal", mood_score=6, notes="An ordinary day of email, errands, and cooking. My mood stayed fairly steady."),
        JournalEntry(journal_id=journal_3.id, entry_date=date(2026, 1, 16), mood_tag="Happy", mood_score=8, notes="Spent the evening painting a small landscape. Mixing colors gave me something enjoyable to focus on."),
        JournalEntry(journal_id=journal_3.id, entry_date=date(2026, 1, 17), mood_tag="Relaxed", mood_score=7, notes="Felt restless in the morning, then went swimming. I came home calmer and stopped replaying interview questions."),
        JournalEntry(journal_id=journal_3.id, entry_date=date(2026, 1, 18), mood_tag="Calm", mood_score=7, notes="After a full night's sleep, I had more patience for chores. The day felt easier than when I was running on little rest.")
    ]
    db.session.add_all(entries_3)

    suggestion_3 = Suggestion(
        journal_id=journal_3.id,
        summary="An upcoming interview brought nervousness, while practice with a friend helped restore confidence. Painting, swimming, and a restful night supported a calmer weekend.",
        selfcare_tips=json.dumps([
            "1. Prepare a few concrete interview examples instead of repeatedly reviewing everything.",
            "2. Keep a small block of time for painting or another enjoyable hobby.",
            "3. Notice how movement and sufficient sleep affect your mood."
        ])
    )
    db.session.add(suggestion_3)
    db.session.commit()

    ## === Week 4: January 19–25 ===
    journal_4 = Journal(
        week_number=4,
        year=2026,
        user_id=user.id
    )
    db.session.add(journal_4)
    db.session.commit()

    entries_4 = [
        JournalEntry(journal_id=journal_4.id, entry_date=date(2026, 1, 19), mood_tag="Focused", mood_score=7, notes="Worked through a clear plan without many interruptions. Felt comfortable with the pace of the day."),
        JournalEntry(journal_id=journal_4.id, entry_date=date(2026, 1, 20), mood_tag="Stressed", mood_score=4, notes="Meetings filled most of the calendar. I worried about the project work that still needed to happen afterward."),
        JournalEntry(journal_id=journal_4.id, entry_date=date(2026, 1, 21), mood_tag="Overwhelmed", mood_score=3, notes="Yesterday's unfinished work was joined by several urgent requests. I could not decide where to start."),
        JournalEntry(journal_id=journal_4.id, entry_date=date(2026, 1, 22), mood_tag="Relaxed", mood_score=7, notes="Went for a jog after feeling tense all afternoon. The movement helped me unwind before dinner."),
        JournalEntry(journal_id=journal_4.id, entry_date=date(2026, 1, 23), mood_tag="Tired", mood_score=4, notes="Woke up several times during the night. I struggled to concentrate and wanted frequent breaks."),
        JournalEntry(journal_id=journal_4.id, entry_date=date(2026, 1, 24), mood_tag="Happy", mood_score=8, notes="Visited family and looked through old photos. The familiar stories made me feel connected and cheerful."),
        JournalEntry(journal_id=journal_4.id, entry_date=date(2026, 1, 25), mood_tag="Calm", mood_score=8, notes="Walked a wooded trail without checking work messages. My thoughts were quieter by the time I returned.")
    ]
    db.session.add_all(entries_4)

    suggestion_4 = Suggestion(
        journal_id=journal_4.id,
        summary="A focused start gave way to stress and overwhelm as meetings and requests accumulated. Exercise and family time helped, while interrupted sleep contributed to tiredness.",
        selfcare_tips=json.dumps([
            "1. Reserve an uninterrupted work block after meeting-heavy periods.",
            "2. Use a short run or walk when tension builds.",
            "3. Leave room for rest after a night of interrupted sleep."
        ])
    )
    db.session.add(suggestion_4)
    db.session.commit()

    ## === Week 5: January 26–February 1 ===
    journal_5 = Journal(
        week_number=5,
        year=2026,
        user_id=user.id
    )
    db.session.add(journal_5)
    db.session.commit()

    entries_5 = [
        JournalEntry(journal_id=journal_5.id, entry_date=date(2026, 1, 26), mood_tag="Anxious", mood_score=4, notes="Tomorrow's budget review includes senior managers. I worried that I would be unable to answer their questions."),
        JournalEntry(journal_id=journal_5.id, entry_date=date(2026, 1, 27), mood_tag="Relieved", mood_score=7, notes="The budget discussion was more constructive than I expected. My shoulders relaxed after it finished."),
        JournalEntry(journal_id=journal_5.id, entry_date=date(2026, 1, 28), mood_tag="Stressed", mood_score=4, notes="A teammate was away, so I picked up extra tasks. The heavier workload made it difficult to switch off."),
        JournalEntry(journal_id=journal_5.id, entry_date=date(2026, 1, 29), mood_tag="Tired", mood_score=3, notes="Worked late to finish the additional tasks. I had little energy left for cooking or conversation."),
        JournalEntry(journal_id=journal_5.id, entry_date=date(2026, 1, 30), mood_tag="Excited", mood_score=8, notes="Left for a short trip to a coastal town. Looking forward to exploring gave me a welcome lift."),
        JournalEntry(journal_id=journal_5.id, entry_date=date(2026, 1, 31), mood_tag="Joyful", mood_score=9, notes="Explored the waterfront with a friend and tried a small cafe. The new surroundings and easy company made the day enjoyable."),
        JournalEntry(journal_id=journal_5.id, entry_date=date(2026, 2, 1), mood_tag="Relaxed", mood_score=7, notes="Had a slow morning before heading home. Felt refreshed after spending time away from the usual routine.")
    ]
    db.session.add_all(entries_5)

    suggestion_5 = Suggestion(
        journal_id=journal_5.id,
        summary="An important review caused anticipatory anxiety that eased afterward. Extra work and overtime reduced energy, while a short trip with a friend brought enjoyment and relief.",
        selfcare_tips=json.dumps([
            "1. Bring a short list of key points to important meetings.",
            "2. Discuss priorities when taking on another person's workload.",
            "3. Make room for enjoyable breaks after demanding work periods."
        ])
    )
    db.session.add(suggestion_5)
    db.session.commit()

    ## === Week 6: February 2–8 ===
    journal_6 = Journal(
        week_number=6,
        year=2026,
        user_id=user.id
    )
    db.session.add(journal_6)
    db.session.commit()

    entries_6 = [
        JournalEntry(journal_id=journal_6.id, entry_date=date(2026, 2, 2), mood_tag="Tired", mood_score=5, notes="Stayed up unpacking and slept less than usual. The morning felt slow even though work was manageable."),
        JournalEntry(journal_id=journal_6.id, entry_date=date(2026, 2, 3), mood_tag="Normal", mood_score=6, notes="Caught up on routine tasks and made dinner at home. Nothing especially good or difficult stood out."),
        JournalEntry(journal_id=journal_6.id, entry_date=date(2026, 2, 4), mood_tag="Anxious", mood_score=3, notes="I volunteered to introduce a speaker at a community event. Thinking about holding the microphone made my stomach flutter."),
        JournalEntry(journal_id=journal_6.id, entry_date=date(2026, 2, 5), mood_tag="Relieved", mood_score=7, notes="The introduction was brief and the audience was friendly. I felt much more relaxed once I finished speaking."),
        JournalEntry(journal_id=journal_6.id, entry_date=date(2026, 2, 6), mood_tag="Happy", mood_score=8, notes="Practiced a new song on guitar after dinner. Enjoyed making progress on something just for fun."),
        JournalEntry(journal_id=journal_6.id, entry_date=date(2026, 2, 7), mood_tag="Joyful", mood_score=8, notes="Spent the afternoon cooking with family. The conversation and shared meal made me feel happy."),
        JournalEntry(journal_id=journal_6.id, entry_date=date(2026, 2, 8), mood_tag="Calm", mood_score=7, notes="Got a full night's sleep and woke up without rushing. Felt more patient and steady throughout the day.")
    ]
    db.session.add_all(entries_6)

    suggestion_6 = Suggestion(
        journal_id=journal_6.id,
        summary="Public speaking brought a sharp increase in anxiety, followed by relief once the event ended. Music, family time, and better sleep supported a positive weekend.",
        selfcare_tips=json.dumps([
            "1. Keep speaking notes short and easy to follow.",
            "2. Continue using music as an enjoyable evening activity.",
            "3. Allow time to recover sleep after travel or late nights."
        ])
    )
    db.session.add(suggestion_6)
    db.session.commit()

    ## === Week 7: February 9–15 ===
    journal_7 = Journal(
        week_number=7,
        year=2026,
        user_id=user.id
    )
    db.session.add(journal_7)
    db.session.commit()

    entries_7 = [
        JournalEntry(journal_id=journal_7.id, entry_date=date(2026, 2, 9), mood_tag="Stressed", mood_score=4, notes="The release deadline moved forward. I felt pressure to finish more work in less time."),
        JournalEntry(journal_id=journal_7.id, entry_date=date(2026, 2, 10), mood_tag="Productive", mood_score=7, notes="Completed an important part of the release during a quiet morning. Finishing something concrete helped restore confidence."),
        JournalEntry(journal_id=journal_7.id, entry_date=date(2026, 2, 11), mood_tag="Overwhelmed", mood_score=3, notes="Three new requests interrupted the plan. The growing task list made it hard to see a clear stopping point."),
        JournalEntry(journal_id=journal_7.id, entry_date=date(2026, 2, 12), mood_tag="Tired", mood_score=4, notes="Stayed at work late trying to catch up. I felt mentally drained by the time I got home."),
        JournalEntry(journal_id=journal_7.id, entry_date=date(2026, 2, 13), mood_tag="Relaxed", mood_score=7, notes="Went for an easy run after a tense afternoon. I still had work to do, but it felt less consuming afterward."),
        JournalEntry(journal_id=journal_7.id, entry_date=date(2026, 2, 14), mood_tag="Happy", mood_score=8, notes="Played board games with friends. Their company helped me stop thinking about deadlines for a while."),
        JournalEntry(journal_id=journal_7.id, entry_date=date(2026, 2, 15), mood_tag="Calm", mood_score=7, notes="Kept the day quiet and went to bed early. Felt ready for a more measured start tomorrow.")
    ]
    db.session.add_all(entries_7)

    suggestion_7 = Suggestion(
        journal_id=journal_7.id,
        summary="A shortened deadline and new requests brought pressure, overwhelm, and fatigue. Completing one task, exercising, and seeing friends helped create some relief.",
        selfcare_tips=json.dumps([
            "1. Revisit priorities when deadlines or requirements change.",
            "2. Set a realistic stopping point before overtime becomes the default.",
            "3. Keep short exercise and social breaks in demanding weeks."
        ])
    )
    db.session.add(suggestion_7)
    db.session.commit()

    ## === Week 8: February 16–22 ===
    journal_8 = Journal(
        week_number=8,
        year=2026,
        user_id=user.id
    )
    db.session.add(journal_8)
    db.session.commit()

    entries_8 = [
        JournalEntry(journal_id=journal_8.id, entry_date=date(2026, 2, 16), mood_tag="Nervous", mood_score=4, notes="Prepared for a technical interview. I worried about going blank while explaining my reasoning."),
        JournalEntry(journal_id=journal_8.id, entry_date=date(2026, 2, 17), mood_tag="Worried", mood_score=4, notes="Kept reviewing interview notes late into the evening. It was difficult to decide when preparation was enough."),
        JournalEntry(journal_id=journal_8.id, entry_date=date(2026, 2, 18), mood_tag="Tired", mood_score=3, notes="The late preparation cut into my sleep. I felt foggy and easily distracted in the morning."),
        JournalEntry(journal_id=journal_8.id, entry_date=date(2026, 2, 19), mood_tag="Relieved", mood_score=7, notes="Finished the interview. I do not know the outcome, but no longer having to prepare brought a sense of relief."),
        JournalEntry(journal_id=journal_8.id, entry_date=date(2026, 2, 20), mood_tag="Bored", mood_score=5, notes="Spent the evening scrolling without much interest. Nothing was wrong, but the time felt unsatisfying."),
        JournalEntry(journal_id=journal_8.id, entry_date=date(2026, 2, 21), mood_tag="Happy", mood_score=8, notes="Tried a pottery class and enjoyed working with clay. It felt good to focus on something playful."),
        JournalEntry(journal_id=journal_8.id, entry_date=date(2026, 2, 22), mood_tag="Joyful", mood_score=8, notes="Had lunch with family and stayed to talk. Felt supported without needing to discuss the interview outcome.")
    ]
    db.session.add_all(entries_8)

    suggestion_8 = Suggestion(
        journal_id=journal_8.id,
        summary="Interview preparation brought nervousness and worry, with late studying contributing to fatigue. Relief followed the interview, and creative activity and family connection improved the weekend.",
        selfcare_tips=json.dumps([
            "1. Set a preparation cutoff that leaves room for sleep.",
            "2. Plan a small enjoyable activity after demanding events.",
            "3. Stay connected with people who help you feel supported."
        ])
    )
    db.session.add(suggestion_8)
    db.session.commit()

    ## === Week 9: February 23–March 1 ===
    journal_9 = Journal(
        week_number=9,
        year=2026,
        user_id=user.id
    )
    db.session.add(journal_9)
    db.session.commit()

    entries_9 = [
        JournalEntry(journal_id=journal_9.id, entry_date=date(2026, 2, 23), mood_tag="Stressed", mood_score=4, notes="Returned to several unfinished tasks. The backlog felt larger each time another message arrived."),
        JournalEntry(journal_id=journal_9.id, entry_date=date(2026, 2, 24), mood_tag="Anxious", mood_score=4, notes="A client demonstration is scheduled tomorrow. I worried about making a mistake while everyone watched."),
        JournalEntry(journal_id=journal_9.id, entry_date=date(2026, 2, 25), mood_tag="Relieved", mood_score=7, notes="The demonstration worked, and I could answer the main questions. Felt less tense once the call ended."),
        JournalEntry(journal_id=journal_9.id, entry_date=date(2026, 2, 26), mood_tag="Relaxed", mood_score=7, notes="Went cycling after an irritating afternoon. Moving outside helped me return home in a better mood."),
        JournalEntry(journal_id=journal_9.id, entry_date=date(2026, 2, 27), mood_tag="Happy", mood_score=8, notes="Caught up with a friend over dinner. An honest conversation helped me feel less alone with the work pressure."),
        JournalEntry(journal_id=journal_9.id, entry_date=date(2026, 2, 28), mood_tag="Excited", mood_score=8, notes="Took a day trip to a nearby town. Exploring unfamiliar streets and a small museum was enjoyable."),
        JournalEntry(journal_id=journal_9.id, entry_date=date(2026, 3, 1), mood_tag="Tired", mood_score=5, notes="Stayed up late after the trip and woke feeling sluggish. Enjoyed the outing, but needed a slower day.")
    ]
    db.session.add_all(entries_9)

    suggestion_9 = Suggestion(
        journal_id=journal_9.id,
        summary="A backlog and upcoming client demonstration brought stress and anxiety. Exercise, conversation, and exploring a new place improved mood, although a late night reduced energy afterward.",
        selfcare_tips=json.dumps([
            "1. Prepare a short checklist for demonstrations.",
            "2. Use outdoor movement or conversation to decompress after work.",
            "3. Leave recovery time around travel and late evenings."
        ])
    )
    db.session.add(suggestion_9)
    db.session.commit()

    ## === Week 10: March 2–8 ===
    journal_10 = Journal(
        week_number=10,
        year=2026,
        user_id=user.id
    )
    db.session.add(journal_10)
    db.session.commit()

    entries_10 = [
        JournalEntry(journal_id=journal_10.id, entry_date=date(2026, 3, 2), mood_tag="Normal", mood_score=6, notes="Handled routine work and errands. My mood stayed fairly even without any major events."),
        JournalEntry(journal_id=journal_10.id, entry_date=date(2026, 3, 3), mood_tag="Calm", mood_score=7, notes="After two restful nights, small interruptions bothered me less. I had more patience throughout the day."),
        JournalEntry(journal_id=journal_10.id, entry_date=date(2026, 3, 4), mood_tag="Anxious", mood_score=3, notes="I agreed to share an experience at a group event. Thinking about speaking to a room of unfamiliar people made me uneasy."),
        JournalEntry(journal_id=journal_10.id, entry_date=date(2026, 3, 5), mood_tag="Relieved", mood_score=7, notes="Finished the group talk. People listened kindly, and the worry eased once I had said what I planned."),
        JournalEntry(journal_id=journal_10.id, entry_date=date(2026, 3, 6), mood_tag="Happy", mood_score=8, notes="Spent the evening learning a new guitar song. Enjoyed the small improvements as I practiced."),
        JournalEntry(journal_id=journal_10.id, entry_date=date(2026, 3, 7), mood_tag="Joyful", mood_score=9, notes="Cooked dinner with friends and stayed at the table talking. The unhurried company made the evening special."),
        JournalEntry(journal_id=journal_10.id, entry_date=date(2026, 3, 8), mood_tag="Calm", mood_score=7, notes="Had a quiet Sunday with reading and a short walk. Felt content without needing to accomplish much.")
    ]
    db.session.add_all(entries_10)

    suggestion_10 = Suggestion(
        journal_id=journal_10.id,
        summary="The week was generally steady apart from anxiety before public speaking. Restful sleep, music, and an enjoyable meal with friends supported a positive end to the week.",
        selfcare_tips=json.dumps([
            "1. Remember the supportive response when preparing for another talk.",
            "2. Keep a consistent sleep routine when possible.",
            "3. Make space for enjoyable activities that do not need to be productive."
        ])
    )
    db.session.add(suggestion_10)
    db.session.commit()

    ## === Week 11: March 9–15 ===
    journal_11 = Journal(
        week_number=11,
        year=2026,
        user_id=user.id
    )
    db.session.add(journal_11)
    db.session.commit()

    entries_11 = [
        JournalEntry(journal_id=journal_11.id, entry_date=date(2026, 3, 9), mood_tag="Stressed", mood_score=4, notes="Two projects need finishing this week. The competing deadlines made it difficult to focus on one thing."),
        JournalEntry(journal_id=journal_11.id, entry_date=date(2026, 3, 10), mood_tag="Overwhelmed", mood_score=3, notes="New tasks arrived before the old ones were finished. I felt buried under the number of loose ends."),
        JournalEntry(journal_id=journal_11.id, entry_date=date(2026, 3, 11), mood_tag="Tired", mood_score=3, notes="Worked overtime and skipped my usual evening break. By bedtime I felt mentally worn out."),
        JournalEntry(journal_id=journal_11.id, entry_date=date(2026, 3, 12), mood_tag="Hopeful", mood_score=6, notes="My manager helped identify which tasks could wait. A shorter priority list made the workload feel more manageable."),
        JournalEntry(journal_id=journal_11.id, entry_date=date(2026, 3, 13), mood_tag="Relaxed", mood_score=7, notes="A gym session helped release the tension from work. I could enjoy dinner without mentally checking my task list."),
        JournalEntry(journal_id=journal_11.id, entry_date=date(2026, 3, 14), mood_tag="Lonely", mood_score=4, notes="Friends were busy, so I spent most of the day alone. Missed having someone to talk with."),
        JournalEntry(journal_id=journal_11.id, entry_date=date(2026, 3, 15), mood_tag="Calm", mood_score=7, notes="Went hiking on a wooded trail. I started the morning feeling low, but the quiet surroundings helped lift my mood.")
    ]
    db.session.add_all(entries_11)

    suggestion_11 = Suggestion(
        journal_id=journal_11.id,
        summary="Competing deadlines and accumulating tasks led to overwhelm and fatigue. Clearer priorities and exercise helped, while a lonely Saturday was followed by a calmer day outdoors.",
        selfcare_tips=json.dumps([
            "1. Ask for priority clarification when several tasks compete.",
            "2. Keep a realistic evening stopping time during deadline weeks.",
            "3. Plan a small social connection or outdoor break when feeling isolated."
        ])
    )
    db.session.add(suggestion_11)
    db.session.commit()

    ## === Week 12: March 16–22 ===
    journal_12 = Journal(
        week_number=12,
        year=2026,
        user_id=user.id
    )
    db.session.add(journal_12)
    db.session.commit()

    entries_12 = [
        JournalEntry(journal_id=journal_12.id, entry_date=date(2026, 3, 16), mood_tag="Nervous", mood_score=4, notes="Another interview is coming up. I worried that my examples would not sound convincing enough."),
        JournalEntry(journal_id=journal_12.id, entry_date=date(2026, 3, 17), mood_tag="Hopeful", mood_score=6, notes="Practiced explaining one project clearly instead of reviewing every detail. Felt more prepared afterward."),
        JournalEntry(journal_id=journal_12.id, entry_date=date(2026, 3, 18), mood_tag="Normal", mood_score=6, notes="An uneventful day of ordinary work and household chores. My mood stayed in the middle."),
        JournalEntry(journal_id=journal_12.id, entry_date=date(2026, 3, 19), mood_tag="Calm", mood_score=7, notes="Went to bed early and woke up rested. The interview still mattered, but I felt less reactive to the worry."),
        JournalEntry(journal_id=journal_12.id, entry_date=date(2026, 3, 20), mood_tag="Relieved", mood_score=7, notes="Completed the interview and put away my notes. Felt relieved to have the preparation behind me."),
        JournalEntry(journal_id=journal_12.id, entry_date=date(2026, 3, 21), mood_tag="Happy", mood_score=8, notes="Worked on a small photography project around the neighborhood. Looking for interesting details made the afternoon fun."),
        JournalEntry(journal_id=journal_12.id, entry_date=date(2026, 3, 22), mood_tag="Joyful", mood_score=9, notes="Visited family for lunch. Shared stories and laughter left me feeling connected and happy.")
    ]
    db.session.add_all(entries_12)

    suggestion_12 = Suggestion(
        journal_id=journal_12.id,
        summary="Interview nerves became more manageable with focused preparation and better rest. Relief after the interview was followed by enjoyment from photography and family time.",
        selfcare_tips=json.dumps([
            "1. Use a few clear examples when preparing for interviews.",
            "2. Preserve sleep instead of extending preparation late into the night.",
            "3. Keep creative and social activities in the week after a demanding event."
        ])
    )
    db.session.add(suggestion_12)
    db.session.commit()

    ## === Week 13: March 23–29 ===
    journal_13 = Journal(
        week_number=13,
        year=2026,
        user_id=user.id
    )
    db.session.add(journal_13)
    db.session.commit()

    entries_13 = [
        JournalEntry(journal_id=journal_13.id, entry_date=date(2026, 3, 23), mood_tag="Anxious", mood_score=4, notes="A presentation to unfamiliar colleagues is approaching. I kept imagining losing my place while everyone watched."),
        JournalEntry(journal_id=journal_13.id, entry_date=date(2026, 3, 24), mood_tag="Stressed", mood_score=3, notes="Presentation preparation was competing with a report deadline. I felt rushed and unsure what to finish first."),
        JournalEntry(journal_id=journal_13.id, entry_date=date(2026, 3, 25), mood_tag="Productive", mood_score=7, notes="Finished the report during a protected work block. Completing it reduced some of the pressure."),
        JournalEntry(journal_id=journal_13.id, entry_date=date(2026, 3, 26), mood_tag="Relaxed", mood_score=7, notes="Went swimming after a tense afternoon. The exercise helped me settle down and stop rehearsing in my head."),
        JournalEntry(journal_id=journal_13.id, entry_date=date(2026, 3, 27), mood_tag="Tired", mood_score=4, notes="Stayed up late making small changes to the slides. I felt low on energy the next morning."),
        JournalEntry(journal_id=journal_13.id, entry_date=date(2026, 3, 28), mood_tag="Happy", mood_score=8, notes="Met friends for brunch. Their company helped me step away from work concerns and enjoy the morning."),
        JournalEntry(journal_id=journal_13.id, entry_date=date(2026, 3, 29), mood_tag="Calm", mood_score=7, notes="Had a restful night and a quiet day at home. Felt more balanced with some distance from the busy week.")
    ]
    db.session.add_all(entries_13)

    suggestion_13 = Suggestion(
        journal_id=journal_13.id,
        summary="Presentation anxiety and a competing report deadline created pressure early in the week. Completing the report, swimming, social time, and rest helped, while late slide editing reduced energy.",
        selfcare_tips=json.dumps([
            "1. Separate presentation preparation from other deadline work into clear blocks.",
            "2. Set a limit on late revisions so preparation does not replace sleep.",
            "3. Continue making room for exercise and time with friends."
        ])
    )
    db.session.add(suggestion_13)
    db.session.commit()

    ## === Week 14: March 30–April 5 ===
    journal_14 = Journal(
        week_number=14,
        year=2026,
        user_id=user.id
    )
    db.session.add(journal_14)
    db.session.commit()

    entries_14 = [
        JournalEntry(journal_id=journal_14.id, entry_date=date(2026, 3, 30), mood_tag="Relieved", mood_score=7, notes="Delivered the presentation I had been preparing. Once the questions ended, I felt able to stop worrying about it."),
        JournalEntry(journal_id=journal_14.id, entry_date=date(2026, 3, 31), mood_tag="Anxious", mood_score=4, notes="An important planning meeting will include a difficult decision. I worried about explaining my position to senior colleagues."),
        JournalEntry(journal_id=journal_14.id, entry_date=date(2026, 4, 1), mood_tag="Relieved", mood_score=7, notes="The planning discussion stayed respectful even when people disagreed. Felt less tense after saying what I thought."),
        JournalEntry(journal_id=journal_14.id, entry_date=date(2026, 4, 2), mood_tag="Normal", mood_score=6, notes="Handled routine messages and a few errands. The day felt ordinary and emotionally steady."),
        JournalEntry(journal_id=journal_14.id, entry_date=date(2026, 4, 3), mood_tag="Happy", mood_score=8, notes="Had dinner with a friend before a weekend trip. Enjoyed talking about things unrelated to work."),
        JournalEntry(journal_id=journal_14.id, entry_date=date(2026, 4, 4), mood_tag="Excited", mood_score=9, notes="Explored a new city and visited a small gallery. The change of scenery made me feel curious and cheerful."),
        JournalEntry(journal_id=journal_14.id, entry_date=date(2026, 4, 5), mood_tag="Tired", mood_score=5, notes="The hotel was noisy and I slept poorly. Enjoyed the trip, but felt sluggish on the way home.")
    ]
    db.session.add_all(entries_14)

    suggestion_14 = Suggestion(
        journal_id=journal_14.id,
        summary="Relief followed the presentation, while another important meeting briefly renewed anxiety. Friendship and travel brought enjoyment, with poor hotel sleep affecting energy at the end.",
        selfcare_tips=json.dumps([
            "1. Write down the main points before a difficult meeting.",
            "2. Keep enjoyable social plans around busy work periods.",
            "3. Allow a lighter day after travel that disrupts sleep."
        ])
    )
    db.session.add(suggestion_14)
    db.session.commit()

    ## === Week 15: April 6–12 ===
    journal_15 = Journal(
        week_number=15,
        year=2026,
        user_id=user.id
    )
    db.session.add(journal_15)
    db.session.commit()

    entries_15 = [
        JournalEntry(journal_id=journal_15.id, entry_date=date(2026, 4, 6), mood_tag="Calm", mood_score=7, notes="Gave a short update to my familiar team. Knowing the audience and having clear notes helped me feel comfortable presenting."),
        JournalEntry(journal_id=journal_15.id, entry_date=date(2026, 4, 7), mood_tag="Stressed", mood_score=4, notes="Picked up extra responsibilities while a colleague was away. The larger workload made the afternoon feel pressured."),
        JournalEntry(journal_id=journal_15.id, entry_date=date(2026, 4, 8), mood_tag="Overwhelmed", mood_score=3, notes="Several unfinished tasks needed attention at once. I kept moving between them without feeling that anything was complete."),
        JournalEntry(journal_id=journal_15.id, entry_date=date(2026, 4, 9), mood_tag="Calm", mood_score=7, notes="A full night's sleep helped me recover some patience. The workload was unchanged, but I felt more able to approach it."),
        JournalEntry(journal_id=journal_15.id, entry_date=date(2026, 4, 10), mood_tag="Happy", mood_score=8, notes="Spent the evening baking a new recipe. Enjoyed focusing on the process and sharing the result."),
        JournalEntry(journal_id=journal_15.id, entry_date=date(2026, 4, 11), mood_tag="Joyful", mood_score=9, notes="Family came over for lunch. The shared food and conversation made the apartment feel warm and lively."),
        JournalEntry(journal_id=journal_15.id, entry_date=date(2026, 4, 12), mood_tag="Relaxed", mood_score=8, notes="Hiked a quiet route outside the city. By the end, I was thinking less about the unfinished work.")
    ]
    db.session.add_all(entries_15)

    suggestion_15 = Suggestion(
        journal_id=journal_15.id,
        summary="A familiar presentation felt comfortable, showing that speaking situations did not always bring anxiety. Extra responsibilities led to stress and overwhelm, while sleep, baking, family time, and hiking helped mood recover.",
        selfcare_tips=json.dumps([
            "1. Notice which preparation and audience conditions make presentations comfortable.",
            "2. Clarify priorities before taking on extra responsibilities.",
            "3. Keep using restorative sleep and enjoyable weekend activities."
        ])
    )
    db.session.add(suggestion_15)
    db.session.commit()

    ## === Week 16: April 13–19 ===
    journal_16 = Journal(
        week_number=16,
        year=2026,
        user_id=user.id
    )
    db.session.add(journal_16)
    db.session.commit()

    entries_16 = [
        JournalEntry(journal_id=journal_16.id, entry_date=date(2026, 4, 13), mood_tag="Tired", mood_score=4, notes="Stayed up scrolling and slept too little. I struggled to focus on ordinary tasks in the morning."),
        JournalEntry(journal_id=journal_16.id, entry_date=date(2026, 4, 14), mood_tag="Anxious", mood_score=3, notes="A panel interview is coming up. Being evaluated by several unfamiliar people at once made me uneasy."),
        JournalEntry(journal_id=journal_16.id, entry_date=date(2026, 4, 15), mood_tag="Overwhelmed", mood_score=3, notes="Interview preparation, project work, and household tasks all needed attention. I felt pulled in too many directions."),
        JournalEntry(journal_id=journal_16.id, entry_date=date(2026, 4, 16), mood_tag="Relieved", mood_score=7, notes="Finished the interview. I cannot predict the result, but felt relieved that the preparation was over."),
        JournalEntry(journal_id=journal_16.id, entry_date=date(2026, 4, 17), mood_tag="Relaxed", mood_score=7, notes="Went swimming after work. The steady movement helped ease the tension left from the busy week."),
        JournalEntry(journal_id=journal_16.id, entry_date=date(2026, 4, 18), mood_tag="Happy", mood_score=8, notes="Met a friend for a long walk and conversation. Felt supported and less caught up in my worries afterward."),
        JournalEntry(journal_id=journal_16.id, entry_date=date(2026, 4, 19), mood_tag="Joyful", mood_score=8, notes="Spent the afternoon taking photographs in the park. Enjoyed experimenting without needing a perfect result.")
    ]
    db.session.add_all(entries_16)

    suggestion_16 = Suggestion(
        journal_id=journal_16.id,
        summary="Short sleep, interview anxiety, and competing responsibilities made the first half of the week difficult. Relief after the interview, swimming, friendship, and photography supported a better weekend.",
        selfcare_tips=json.dumps([
            "1. Keep interview preparation within a manageable time window.",
            "2. Reduce optional tasks when several responsibilities compete.",
            "3. Protect activities that help you feel supported and relaxed."
        ])
    )
    db.session.add(suggestion_16)
    db.session.commit()

    ## === Week 17: April 20–26 ===
    journal_17 = Journal(
        week_number=17,
        year=2026,
        user_id=user.id
    )
    db.session.add(journal_17)
    db.session.commit()

    entries_17 = [
        JournalEntry(journal_id=journal_17.id, entry_date=date(2026, 4, 20), mood_tag="Focused", mood_score=7, notes="The task had a deadline, but its scope was small and clear. I felt focused rather than pressured while working."),
        JournalEntry(journal_id=journal_17.id, entry_date=date(2026, 4, 21), mood_tag="Stressed", mood_score=4, notes="An urgent request changed the plan without moving the original deadline. Trying to fit in both tasks made me tense."),
        JournalEntry(journal_id=journal_17.id, entry_date=date(2026, 4, 22), mood_tag="Tired", mood_score=3, notes="Worked late to finish the extra request. I had little energy left and found it hard to stay engaged at home."),
        JournalEntry(journal_id=journal_17.id, entry_date=date(2026, 4, 23), mood_tag="Overwhelmed", mood_score=3, notes="Back-to-back meetings used up the day. The remaining work felt too large for the evening ahead."),
        JournalEntry(journal_id=journal_17.id, entry_date=date(2026, 4, 24), mood_tag="Happy", mood_score=8, notes="Called family after work and talked through the difficult week. Felt lighter after being listened to."),
        JournalEntry(journal_id=journal_17.id, entry_date=date(2026, 4, 25), mood_tag="Calm", mood_score=7, notes="Slept well and woke with more energy. Simple chores felt manageable instead of irritating."),
        JournalEntry(journal_id=journal_17.id, entry_date=date(2026, 4, 26), mood_tag="Relaxed", mood_score=7, notes="Spent a slow afternoon reading and taking a short walk. Appreciated having no urgent demands.")
    ]
    db.session.add_all(entries_17)

    suggestion_17 = Suggestion(
        journal_id=journal_17.id,
        summary="A clear, manageable deadline initially supported focus. Unexpected work and crowded meetings then brought stress and exhaustion, with family support and rest helping recovery.",
        selfcare_tips=json.dumps([
            "1. Revisit scope or timing when urgent work changes the original plan.",
            "2. Leave protected work time around meetings where possible.",
            "3. Keep time for supportive conversations and recovery sleep."
        ])
    )
    db.session.add(suggestion_17)
    db.session.commit()

    ## === Week 18: April 27–May 3 ===
    journal_18 = Journal(
        week_number=18,
        year=2026,
        user_id=user.id
    )
    db.session.add(journal_18)
    db.session.commit()

    entries_18 = [
        JournalEntry(journal_id=journal_18.id, entry_date=date(2026, 4, 27), mood_tag="Nervous", mood_score=4, notes="I agreed to speak at a community gathering. Thinking about standing in front of the room made me restless."),
        JournalEntry(journal_id=journal_18.id, entry_date=date(2026, 4, 28), mood_tag="Anxious", mood_score=3, notes="Kept imagining forgetting my words during the talk. Rehearsing helped a little, but I still felt tense."),
        JournalEntry(journal_id=journal_18.id, entry_date=date(2026, 4, 29), mood_tag="Relieved", mood_score=7, notes="The talk finished and people asked friendly questions. I felt more comfortable once the speaking part was over."),
        JournalEntry(journal_id=journal_18.id, entry_date=date(2026, 4, 30), mood_tag="Happy", mood_score=8, notes="Painted after dinner and lost track of time in a pleasant way. Enjoyed making something without being evaluated."),
        JournalEntry(journal_id=journal_18.id, entry_date=date(2026, 5, 1), mood_tag="Joyful", mood_score=8, notes="Spent the evening playing games with friends. Laughter helped me let go of the tension from earlier in the week."),
        JournalEntry(journal_id=journal_18.id, entry_date=date(2026, 5, 2), mood_tag="Normal", mood_score=6, notes="Did grocery shopping and cleaned the apartment. A routine day with a fairly steady mood."),
        JournalEntry(journal_id=journal_18.id, entry_date=date(2026, 5, 3), mood_tag="Relaxed", mood_score=8, notes="Walked a long trail away from traffic. I returned feeling calmer and less mentally crowded.")
    ]
    db.session.add_all(entries_18)

    suggestion_18 = Suggestion(
        journal_id=journal_18.id,
        summary="Anticipating public speaking brought nervousness and anxiety, which eased after the talk. Painting, friends, and time outdoors provided enjoyable ways to unwind.",
        selfcare_tips=json.dumps([
            "1. Use a short outline and a limited rehearsal period before speaking.",
            "2. Plan an enjoyable activity after a demanding event.",
            "3. Keep outdoor time available when your thoughts feel crowded."
        ])
    )
    db.session.add(suggestion_18)
    db.session.commit()

    ## === Week 19: May 4–10 ===
    journal_19 = Journal(
        week_number=19,
        year=2026,
        user_id=user.id
    )
    db.session.add(journal_19)
    db.session.commit()

    entries_19 = [
        JournalEntry(journal_id=journal_19.id, entry_date=date(2026, 5, 4), mood_tag="Anxious", mood_score=4, notes="Tomorrow's client presentation includes a live demonstration. I worried about something failing while everyone watched."),
        JournalEntry(journal_id=journal_19.id, entry_date=date(2026, 5, 5), mood_tag="Relieved", mood_score=7, notes="The client presentation went smoothly. Felt able to breathe more easily once the demonstration ended."),
        JournalEntry(journal_id=journal_19.id, entry_date=date(2026, 5, 6), mood_tag="Stressed", mood_score=4, notes="A report deadline was approaching while other requests kept arriving. I felt pressured to work faster than was comfortable."),
        JournalEntry(journal_id=journal_19.id, entry_date=date(2026, 5, 7), mood_tag="Tired", mood_score=3, notes="Stayed online late finishing the report. My concentration faded, and I wanted to go straight to bed."),
        JournalEntry(journal_id=journal_19.id, entry_date=date(2026, 5, 8), mood_tag="Angry", mood_score=3, notes="A coworker dismissed an idea before I could explain it. I stayed irritated after the conversation ended."),
        JournalEntry(journal_id=journal_19.id, entry_date=date(2026, 5, 9), mood_tag="Happy", mood_score=8, notes="Played music with a friend. The shared activity helped take my attention away from yesterday's frustration."),
        JournalEntry(journal_id=journal_19.id, entry_date=date(2026, 5, 10), mood_tag="Calm", mood_score=7, notes="Had a restful night and a slow morning. Felt less reactive when I thought back over the week.")
    ]
    db.session.add_all(entries_19)

    suggestion_19 = Suggestion(
        journal_id=journal_19.id,
        summary="Presentation anxiety eased after the event, but deadline pressure, overtime, and a frustrating interaction affected the following days. Music with a friend and rest helped mood settle.",
        selfcare_tips=json.dumps([
            "1. Prepare a simple fallback plan for demonstrations.",
            "2. Make space to pause before revisiting a frustrating conversation.",
            "3. Keep recovery time after deadline-related overtime."
        ])
    )
    db.session.add(suggestion_19)
    db.session.commit()

    ## === Week 20: May 11–17 ===
    journal_20 = Journal(
        week_number=20,
        year=2026,
        user_id=user.id
    )
    db.session.add(journal_20)
    db.session.commit()

    entries_20 = [
        JournalEntry(journal_id=journal_20.id, entry_date=date(2026, 5, 11), mood_tag="Overwhelmed", mood_score=3, notes="Five meetings broke the day into tiny pieces. My unfinished project work kept accumulating between calls."),
        JournalEntry(journal_id=journal_20.id, entry_date=date(2026, 5, 12), mood_tag="Tired", mood_score=4, notes="Woke repeatedly during the night. Even straightforward decisions felt exhausting by lunchtime."),
        JournalEntry(journal_id=journal_20.id, entry_date=date(2026, 5, 13), mood_tag="Stressed", mood_score=4, notes="Several tasks were overdue after the meeting-heavy start. I worried about disappointing people waiting for them."),
        JournalEntry(journal_id=journal_20.id, entry_date=date(2026, 5, 14), mood_tag="Relaxed", mood_score=7, notes="Went to an exercise class after work. I left feeling less wound up and more able to enjoy the evening."),
        JournalEntry(journal_id=journal_20.id, entry_date=date(2026, 5, 15), mood_tag="Happy", mood_score=8, notes="Had dinner with friends after feeling discouraged earlier. Talking and laughing together noticeably improved my mood."),
        JournalEntry(journal_id=journal_20.id, entry_date=date(2026, 5, 16), mood_tag="Joyful", mood_score=8, notes="Spent a few hours making a ceramic bowl. Enjoyed working with my hands even though the shape was uneven."),
        JournalEntry(journal_id=journal_20.id, entry_date=date(2026, 5, 17), mood_tag="Normal", mood_score=6, notes="A quiet day of laundry, groceries, and reading. My mood was steady without any strong highs or lows.")
    ]
    db.session.add_all(entries_20)

    suggestion_20 = Suggestion(
        journal_id=journal_20.id,
        summary="Crowded meetings, interrupted sleep, and overdue work contributed to overwhelm and stress. Exercise, friendship, and a creative hobby improved the latter half of the week.",
        selfcare_tips=json.dumps([
            "1. Review whether meeting time leaves enough room for the work itself.",
            "2. Keep the next day's priorities manageable after poor sleep.",
            "3. Continue scheduling exercise and activities you enjoy."
        ])
    )
    db.session.add(suggestion_20)
    db.session.commit()

    ## === Week 21: May 18–24 ===
    journal_21 = Journal(
        week_number=21,
        year=2026,
        user_id=user.id
    )
    db.session.add(journal_21)
    db.session.commit()

    entries_21 = [
        JournalEntry(journal_id=journal_21.id, entry_date=date(2026, 5, 18), mood_tag="Anxious", mood_score=4, notes="An important review with leadership is tomorrow. I kept worrying about how they would judge my work."),
        JournalEntry(journal_id=journal_21.id, entry_date=date(2026, 5, 19), mood_tag="Relieved", mood_score=7, notes="The review turned into a useful discussion. Understanding the expectations helped reduce my worry."),
        JournalEntry(journal_id=journal_21.id, entry_date=date(2026, 5, 20), mood_tag="Stressed", mood_score=4, notes="The next project has a heavy workload and a tight deadline. Thinking about fitting everything in made me tense."),
        JournalEntry(journal_id=journal_21.id, entry_date=date(2026, 5, 21), mood_tag="Tired", mood_score=3, notes="Worked overtime to prepare the first handoff. Felt too drained to do much afterward."),
        JournalEntry(journal_id=journal_21.id, entry_date=date(2026, 5, 22), mood_tag="Happy", mood_score=8, notes="Called family before leaving for the weekend. Their interest and encouragement helped me feel supported."),
        JournalEntry(journal_id=journal_21.id, entry_date=date(2026, 5, 23), mood_tag="Excited", mood_score=9, notes="Took a short trip with friends and explored a different neighborhood. Enjoyed having something new to discover."),
        JournalEntry(journal_id=journal_21.id, entry_date=date(2026, 5, 24), mood_tag="Joyful", mood_score=9, notes="Visited a market and shared a long lunch with friends. The easy company made the trip feel refreshing.")
    ]
    db.session.add_all(entries_21)

    suggestion_21 = Suggestion(
        journal_id=journal_21.id,
        summary="A leadership review triggered anxiety, followed by relief when expectations became clearer. Workload pressure and overtime reduced energy, while family support and travel with friends brought enjoyment.",
        selfcare_tips=json.dumps([
            "1. Ask for clear expectations before high-pressure reviews.",
            "2. Break the new project into realistic milestones.",
            "3. Preserve social time and recovery after overtime."
        ])
    )
    db.session.add(suggestion_21)
    db.session.commit()

    ## === Week 22: May 25–31 ===
    journal_22 = Journal(
        week_number=22,
        year=2026,
        user_id=user.id
    )
    db.session.add(journal_22)
    db.session.commit()

    entries_22 = [
        JournalEntry(journal_id=journal_22.id, entry_date=date(2026, 5, 25), mood_tag="Normal", mood_score=6, notes="Returned to the usual routine after the trip. The day felt ordinary and fairly steady."),
        JournalEntry(journal_id=journal_22.id, entry_date=date(2026, 5, 26), mood_tag="Stressed", mood_score=4, notes="Several unfinished tasks were waiting alongside new deadlines. The backlog made it difficult to settle into work."),
        JournalEntry(journal_id=journal_22.id, entry_date=date(2026, 5, 27), mood_tag="Productive", mood_score=7, notes="Chose two priorities and finished them before opening new tasks. The clearer focus helped me feel more in control."),
        JournalEntry(journal_id=journal_22.id, entry_date=date(2026, 5, 28), mood_tag="Calm", mood_score=7, notes="Got a full night's sleep after several short ones. Felt more patient and less scattered in the morning."),
        JournalEntry(journal_id=journal_22.id, entry_date=date(2026, 5, 29), mood_tag="Happy", mood_score=8, notes="Spent the evening with friends at a small cafe. Their company helped me stop dwelling on the backlog."),
        JournalEntry(journal_id=journal_22.id, entry_date=date(2026, 5, 30), mood_tag="Disappointed", mood_score=5, notes="Went hiking hoping to feel better, but kept checking work messages. Came home still distracted and tense."),
        JournalEntry(journal_id=journal_22.id, entry_date=date(2026, 5, 31), mood_tag="Relaxed", mood_score=7, notes="Put my phone away while cooking and reading. Having a real break helped me feel calmer than yesterday.")
    ]
    db.session.add_all(entries_22)

    suggestion_22 = Suggestion(
        journal_id=journal_22.id,
        summary="A backlog brought stress, while focused priorities, sleep, and friends helped. Hiking did not provide the usual relief when work messages continued, but a more disconnected break felt restorative.",
        selfcare_tips=json.dumps([
            "1. Continue choosing a small set of priorities before starting new tasks.",
            "2. Try setting aside work messages during a planned break.",
            "3. Notice which conditions make rest genuinely useful for you."
        ])
    )
    db.session.add(suggestion_22)
    db.session.commit()

    ## === Week 23: June 1–7 ===
    journal_23 = Journal(
        week_number=23,
        year=2026,
        user_id=user.id
    )
    db.session.add(journal_23)
    db.session.commit()

    entries_23 = [
        JournalEntry(journal_id=journal_23.id, entry_date=date(2026, 6, 1), mood_tag="Nervous", mood_score=4, notes="An interview with a new team is scheduled this week. I felt uneasy about explaining my work to unfamiliar people."),
        JournalEntry(journal_id=journal_23.id, entry_date=date(2026, 6, 2), mood_tag="Tired", mood_score=4, notes="Stayed up late preparing examples. Too little sleep made it harder to concentrate the next morning."),
        JournalEntry(journal_id=journal_23.id, entry_date=date(2026, 6, 3), mood_tag="Overwhelmed", mood_score=3, notes="Interview preparation and project deadlines were competing for the same hours. I felt stretched across too many tasks."),
        JournalEntry(journal_id=journal_23.id, entry_date=date(2026, 6, 4), mood_tag="Calm", mood_score=7, notes="Stopped preparing earlier and got proper rest. Woke feeling steadier and more able to think clearly."),
        JournalEntry(journal_id=journal_23.id, entry_date=date(2026, 6, 5), mood_tag="Relieved", mood_score=7, notes="Finished the interview and talked with a supportive friend afterward. Felt lighter even though the outcome is still unknown."),
        JournalEntry(journal_id=journal_23.id, entry_date=date(2026, 6, 6), mood_tag="Happy", mood_score=8, notes="Worked on a photography project in the park. Enjoyed focusing on small details instead of evaluating my performance."),
        JournalEntry(journal_id=journal_23.id, entry_date=date(2026, 6, 7), mood_tag="Joyful", mood_score=9, notes="Shared lunch with family and stayed for conversation. Felt happy and connected by the end of the afternoon.")
    ]
    db.session.add_all(entries_23)

    suggestion_23 = Suggestion(
        journal_id=journal_23.id,
        summary="Interview nerves, late preparation, and competing deadlines contributed to tiredness and overwhelm. Better rest, a supportive conversation, photography, and family time helped mood improve.",
        selfcare_tips=json.dumps([
            "1. Set a preparation limit that protects sleep before interviews.",
            "2. Reduce optional commitments when deadlines overlap.",
            "3. Keep supportive conversations and enjoyable hobbies available afterward."
        ])
    )
    db.session.add(suggestion_23)
    db.session.commit()

    ## === Week 24: June 8–14 ===
    journal_24 = Journal(
        week_number=24,
        year=2026,
        user_id=user.id
    )
    db.session.add(journal_24)
    db.session.commit()

    entries_24 = [
        JournalEntry(journal_id=journal_24.id, entry_date=date(2026, 6, 8), mood_tag="Calm", mood_score=7, notes="Led a small planning meeting with a clear agenda. The familiar group and preparation helped me feel comfortable."),
        JournalEntry(journal_id=journal_24.id, entry_date=date(2026, 6, 9), mood_tag="Anxious", mood_score=4, notes="A larger presentation to unfamiliar colleagues is coming up. I worried about losing my train of thought in front of them."),
        JournalEntry(journal_id=journal_24.id, entry_date=date(2026, 6, 10), mood_tag="Stressed", mood_score=4, notes="Presentation preparation overlapped with a report deadline. I felt pressure to make progress on both at once."),
        JournalEntry(journal_id=journal_24.id, entry_date=date(2026, 6, 11), mood_tag="Tired", mood_score=3, notes="Worked overtime to finish the report. By evening, I had little energy and found it hard to concentrate."),
        JournalEntry(journal_id=journal_24.id, entry_date=date(2026, 6, 12), mood_tag="Relaxed", mood_score=7, notes="Took a gentle jog after work. The exercise helped ease the tension even though next week's presentation was still on my mind."),
        JournalEntry(journal_id=journal_24.id, entry_date=date(2026, 6, 13), mood_tag="Joyful", mood_score=8, notes="Joined friends for a relaxed evening of games. Laughing together helped me shake off the tiring week."),
        JournalEntry(journal_id=journal_24.id, entry_date=date(2026, 6, 14), mood_tag="Calm", mood_score=8, notes="Slept well and spent the morning on a quiet trail. Felt more rested and less caught up in work concerns.")
    ]
    db.session.add_all(entries_24)

    suggestion_24 = Suggestion(
        journal_id=journal_24.id,
        summary="A familiar meeting felt comfortable, while an upcoming larger presentation brought anxiety. Overlapping work and overtime increased stress and fatigue, followed by relief through exercise, friends, sleep, and time outdoors.",
        selfcare_tips=json.dumps([
            "1. Bring the clear agenda and preparation that helped in the smaller meeting to the larger presentation.",
            "2. Separate competing tasks into manageable work periods with a stopping time.",
            "3. Preserve exercise, social connection, and rest during busy weeks."
        ])
    )
    db.session.add(suggestion_24)
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
        JournalEntry(journal_id=journal_28.id, entry_date=date(2026, 7, 11), mood_tag="Stressed", mood_score=5, notes="Preparing for next week."),
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
        JournalEntry(journal_id=journal_31.id, entry_date=date(2026, 7, 31), mood_tag="Calm", mood_score=7, notes="Smooth day. Kept a good pace."),
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

    ## === Week 32: August 3–9 ===
    journal_32 = Journal(
        week_number=32,
        year=2026,
        user_id=user.id
    )
    db.session.add(journal_32)
    db.session.commit()

    entries_32 = [
        JournalEntry(journal_id=journal_32.id, entry_date=date(2026, 8, 3), mood_tag="Focused", mood_score=7, notes="Got into deep work mode. Finished key part of the project."),
        JournalEntry(journal_id=journal_32.id, entry_date=date(2026, 8, 4), mood_tag="Other", mood_score=4, notes="Practiced a project demo for a room of unfamiliar colleagues. My palms were damp and I kept imagining forgetting the opening."),
        JournalEntry(journal_id=journal_32.id, entry_date=date(2026, 8, 5), mood_tag="Tired", mood_score=5, notes="Didn't sleep well. Had to push through the day."),
        JournalEntry(journal_id=journal_32.id, entry_date=date(2026, 8, 6), mood_tag="Excited", mood_score=8, notes="Pushed through a long day of coding. The project is nearly done, feeling tired but excited to see it coming together."),
        JournalEntry(journal_id=journal_32.id, entry_date=date(2026, 8, 7), mood_tag="Relaxed", mood_score=7, notes="Went swimming after work. Project worries were still there, but the movement helped my shoulders loosen and my thoughts slow down."),
        JournalEntry(journal_id=journal_32.id, entry_date=date(2026, 8, 8), mood_tag="Normal", mood_score=6, notes="Bought groceries, replaced a kitchen light bulb, and sorted the mail. Nothing stood out emotionally."),
        JournalEntry(journal_id=journal_32.id, entry_date=date(2026, 8, 9), mood_tag="Happy", mood_score=8, notes="Cooked lunch with family and played guitar afterward. Enjoyed the company and having time for a hobby.")
    ]
    db.session.add_all(entries_32)

    suggestion_32 = Suggestion(
        journal_id=journal_32.id,
        summary="Project progress brought satisfaction alongside unease about presenting and tiredness after poor sleep. Swimming helped ease tension, and family time and guitar brought enjoyment after an ordinary Saturday.",
        selfcare_tips=json.dumps([
            "1. Use a short rehearsal plan for the demo, with a stopping time that protects sleep.",
            "2. Keep swimming or another enjoyable form of movement available after demanding workdays.",
            "3. Make room for family time and guitar alongside the project."
        ])
    )
    db.session.add(suggestion_32)
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


    ## === Week 35 ===
    journal_35 = Journal(
        week_number=35,
        year=2026,
        user_id=user.id
    )
    db.session.add(journal_35)
    db.session.commit()

    entries_35 = [
        JournalEntry(journal_id=journal_35.id, entry_date=date(2026, 8, 24), mood_tag="Focused", mood_score=8, notes="Strong start, clear priorities."),
        JournalEntry(journal_id=journal_35.id, entry_date=date(2026, 8, 25), mood_tag="Overwhelmed", mood_score=5, notes="Too many tasks piled up."),
        JournalEntry(journal_id=journal_35.id, entry_date=date(2026, 8, 26), mood_tag="Focused", mood_score=7, notes="Prioritized tasks, felt more in control."),
        JournalEntry(journal_id=journal_35.id, entry_date=date(2026, 8, 27), mood_tag="Excited", mood_score=8, notes="Finished major milestones."),
        JournalEntry(journal_id=journal_35.id, entry_date=date(2026, 8, 28), mood_tag="Calm", mood_score=7, notes="Handled tasks steadily."),
        JournalEntry(journal_id=journal_35.id, entry_date=date(2026, 8, 29), mood_tag="Joyful", mood_score=9, notes="Enjoyed long weekend, relaxed outdoors."),
        JournalEntry(journal_id=journal_35.id, entry_date=date(2026, 8, 30), mood_tag="Joyful", mood_score=9, notes="Went camping with family and friends, felt refreshed and happy.")
    ]
    db.session.add_all(entries_35)

    suggestion_35 = Suggestion(
        journal_id=journal_35.id,
        summary="This week balanced motivation, pressure, and achievement. Despite midweek stress, you refocused and accomplished key milestones. Ending the week with a long weekend camping trip brought joy, connection, and renewal.",
        selfcare_tips=json.dumps([
            "1. Use nature breaks like camping or outdoor walks regularly to recharge and restore balance.",
            "2. When feeling overwhelmed, lean on social connections—sharing time with friends or family can ease stress and boost mood.",
            "3. Continue celebrating progress with gratitude and reflection, especially after combining hard work with meaningful rest."
        ])
    )
    db.session.add(suggestion_35)
    db.session.commit()


    ## === Week 36: August 31–September 6 ===
    journal_36 = Journal(
        week_number=36,
        year=2026,
        user_id=user.id
    )
    db.session.add(journal_36)
    db.session.commit()

    entries_36 = [
        JournalEntry(journal_id=journal_36.id, entry_date=date(2026, 8, 31), mood_tag="Excited", mood_score=8, notes="Kicked off a new project. Energy was high, felt motivated."),
        JournalEntry(journal_id=journal_36.id, entry_date=date(2026, 9, 1), mood_tag="Focused", mood_score=7, notes="Spent hours planning project tasks. Clear roadmap, but workload looks heavy."),
        JournalEntry(journal_id=journal_36.id, entry_date=date(2026, 9, 2), mood_tag="Productive", mood_score=8, notes="Good progress on initial setup. Momentum is strong."),
        JournalEntry(journal_id=journal_36.id, entry_date=date(2026, 9, 3), mood_tag="Anxious", mood_score=5, notes="Started looking at job postings. The market seems very competitive."),
        JournalEntry(journal_id=journal_36.id, entry_date=date(2026, 9, 4), mood_tag="Stressed", mood_score=4, notes="Applied to a few positions but didn't get responses. Felt pressure mounting."),
        JournalEntry(journal_id=journal_36.id, entry_date=date(2026, 9, 5), mood_tag="Tired", mood_score=5, notes="Worked late on both project and job search. Felt drained."),
        JournalEntry(journal_id=journal_36.id, entry_date=date(2026, 9, 6), mood_tag="Hopeful", mood_score=6, notes="Took a break, tried to reset mindset. Still hopeful things will work out.")
    ]
    db.session.add_all(entries_36)

    suggestion_36 = Suggestion(
        journal_id=journal_36.id,
        summary="A new project began with motivation and progress. Job searching brought anxiety and pressure, while late work on both commitments left you tired. A break on Sunday helped you feel more hopeful.",
        selfcare_tips=json.dumps([
            "1. Set separate, manageable periods for project work and job applications.",
            "2. Choose an evening stopping time so both commitments leave room for rest.",
            "3. Keep taking breaks that help you regain perspective during the job search."
        ])
    )
    db.session.add(suggestion_36)
    db.session.commit()

    ## === Week 37: September 7–13 ===
    journal_37 = Journal(
        week_number=37,
        year=2026,
        user_id=user.id
    )
    db.session.add(journal_37)
    db.session.commit()

    entries_37 = [
        JournalEntry(journal_id=journal_37.id, entry_date=date(2026, 9, 7), mood_tag="Nervous", mood_score=5, notes="Prepared for interviews, but job rejections still in mind."),
        JournalEntry(journal_id=journal_37.id, entry_date=date(2026, 9, 8), mood_tag="Overwhelmed", mood_score=4, notes="Balancing project work and job search feels exhausting. Need better routine."),
        JournalEntry(journal_id=journal_37.id, entry_date=date(2026, 9, 9), mood_tag="Anxious", mood_score=4, notes="A technical interview is tomorrow. I kept rehearsing explanations because I was afraid of going blank when someone questioned my work."),
        JournalEntry(journal_id=journal_37.id, entry_date=date(2026, 9, 10), mood_tag="Relieved", mood_score=7, notes="Finished the interview. I still do not know the outcome, but my breathing settled once the conversation was over."),
        JournalEntry(journal_id=journal_37.id, entry_date=date(2026, 9, 11), mood_tag="Stressed", mood_score=4, notes="Back-to-back meetings left little time for a report due this afternoon. The unfinished work kept running through my mind after dinner."),
        JournalEntry(journal_id=journal_37.id, entry_date=date(2026, 9, 12), mood_tag="Joyful", mood_score=8, notes="Hiked with friends and stopped for a picnic. Laughing together on the trail lifted my mood after the demanding week."),
        JournalEntry(journal_id=journal_37.id, entry_date=date(2026, 9, 13), mood_tag="Normal", mood_score=6, notes="Did laundry, renewed a library book, and cooked dinner. My mood stayed fairly even throughout the day.")
    ]
    db.session.add_all(entries_37)

    suggestion_37 = Suggestion(
        journal_id=journal_37.id,
        summary="Interview preparation and competing commitments brought nervousness and overwhelm. Tension eased after the interview, although meetings and a report deadline added pressure. Hiking with friends lifted your mood before a neutral Sunday.",
        selfcare_tips=json.dumps([
            "1. Prepare a few interview examples, then allow yourself to stop rehearsing.",
            "2. Protect a work block for deadlines when the meeting calendar is full.",
            "3. Keep outdoor time with friends in your routine when it feels restorative."
        ])
    )
    db.session.add(suggestion_37)
    db.session.commit()

    ## === Week 38: September 14–20 ===
    journal_38 = Journal(
        week_number=38,
        year=2026,
        user_id=user.id
    )
    db.session.add(journal_38)
    db.session.commit()

    entries_38 = [
        JournalEntry(journal_id=journal_38.id, entry_date=date(2026, 9, 14), mood_tag="Other", mood_score=4, notes="An important project review with senior managers is coming up. My stomach tightened whenever I pictured their questions, and I reread my slides late into the night."),
        JournalEntry(journal_id=journal_38.id, entry_date=date(2026, 9, 15), mood_tag="Tired", mood_score=3, notes="Only slept five hours after working late on the review slides. I reread simple messages several times and had little energy for anything after work."),
        JournalEntry(journal_id=journal_38.id, entry_date=date(2026, 9, 16), mood_tag="Overwhelmed", mood_score=3, notes="Meetings took up most of the day while new requests arrived before yesterday's tasks were finished. I could not find a clear place to start."),
        JournalEntry(journal_id=journal_38.id, entry_date=date(2026, 9, 17), mood_tag="Relaxed", mood_score=7, notes="Went for a gentle run after work. The upcoming review still mattered to me, but I stopped replaying every possible question for a while."),
        JournalEntry(journal_id=journal_38.id, entry_date=date(2026, 9, 18), mood_tag="Happy", mood_score=8, notes="Had dinner with family and laughed over old stories. Felt connected and more cheerful on the way home."),
        JournalEntry(journal_id=journal_38.id, entry_date=date(2026, 9, 19), mood_tag="Excited", mood_score=7, notes="Put one of my paintings in a small community display. Felt proud to share a hobby, though I also wondered how visitors would respond."),
        JournalEntry(journal_id=journal_38.id, entry_date=date(2026, 9, 20), mood_tag="Calm", mood_score=7, notes="Spent the afternoon learning a song on guitar. Focusing on the melody gave me a satisfying break from thinking about work.")
    ]
    db.session.add_all(entries_38)

    suggestion_38 = Suggestion(
        journal_id=journal_38.id,
        summary="Anticipating an important review brought unease, and late preparation reduced sleep and energy. Meetings and unfinished tasks added overwhelm. Running, family connection, painting, and guitar brought relief and enjoyment, with some uncertainty about sharing your art.",
        selfcare_tips=json.dumps([
            "1. Set a preparation limit before important reviews to leave enough time for sleep.",
            "2. Identify one next task when meetings and new requests crowd the day.",
            "3. Preserve the movement, family time, and hobbies that offered welcome breaks."
        ])
    )
    db.session.add(suggestion_38)
    db.session.commit()

    ## === Week 39: September 21–24 (partial week) ===
    journal_39 = Journal(
        week_number=39,
        year=2026,
        user_id=user.id
    )
    db.session.add(journal_39)
    db.session.commit()

    entries_39 = [
        JournalEntry(journal_id=journal_39.id, entry_date=date(2026, 9, 21), mood_tag="Nervous", mood_score=4, notes="Agreed to introduce a panel at a community event tomorrow. Thinking about holding the microphone in front of the audience made my heart race."),
        JournalEntry(journal_id=journal_39.id, entry_date=date(2026, 9, 22), mood_tag="Relieved", mood_score=7, notes="Gave the short introduction with my notes nearby. After the first few sentences I felt more comfortable, and I enjoyed listening to the panel afterward."),
        JournalEntry(journal_id=journal_39.id, entry_date=date(2026, 9, 23), mood_tag="Other", mood_score=4, notes="A deadline moved forward while two overdue requests were still waiting. I kept switching between my inbox and the task list, unable to switch off in the evening."),
        JournalEntry(journal_id=journal_39.id, entry_date=date(2026, 9, 24), mood_tag="Happy", mood_score=8, notes="Took a walk with a friend after work and talked openly about the busy week. The unfinished tasks still bothered me, but I felt lighter and less alone.")
    ]
    db.session.add_all(entries_39)

    suggestion_39 = Suggestion(
        journal_id=journal_39.id,
        summary="Across these four days, anticipation of public speaking brought nerves that eased during the event. An earlier deadline and overdue requests made it difficult to switch off. A walk and conversation with a friend lifted your mood even though work concerns remained.",
        selfcare_tips=json.dumps([
            "1. Keep brief notes available for speaking engagements, since they helped during the introduction.",
            "2. Clarify priorities when deadlines move while other requests remain unfinished.",
            "3. Make time for walks and supportive conversations alongside ongoing work concerns."
        ])
    )
    db.session.add(suggestion_39)
    db.session.commit()

    print("✅ Database seeded successfully.")

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        reset_database()
        seed_data()




