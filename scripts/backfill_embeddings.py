"""Fill missing journal embeddings using the configured database and provider."""

import sys
from pathlib import Path

from sqlalchemy.exc import SQLAlchemyError


SERVER_DIR = Path(__file__).resolve().parents[1] / "server"
if str(SERVER_DIR) not in sys.path:
    sys.path.insert(0, str(SERVER_DIR))

from app import create_app
from config import db
from models import JournalEntry
from services import embedding_service
from services.exceptions import ProviderError


def backfill_embeddings():
    entries = (
        JournalEntry.query
        .filter(JournalEntry.embedding.is_(None))
        .order_by(JournalEntry.id)
        .all()
    )
    updated = 0
    failed = 0

    for entry in entries:
        entry_id = entry.id
        try:
            entry.embedding = embedding_service.generate_entry_embedding(entry)
            db.session.commit()
            updated += 1
        except (ProviderError, SQLAlchemyError, ValueError) as error:
            db.session.rollback()
            failed += 1
            print(f"Entry {entry_id}: failed ({type(error).__name__}).")

    return updated, failed


def main():
    app = create_app()
    with app.app_context():
        updated, failed = backfill_embeddings()
        print(f"Updated: {updated}, failed: {failed}")


if __name__ == "__main__":
    main()
