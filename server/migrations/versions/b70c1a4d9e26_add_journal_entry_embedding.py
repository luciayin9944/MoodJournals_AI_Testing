"""Add nullable embeddings to journal entries.

Revision ID: b70c1a4d9e26
Revises: 7596ddc82698
"""

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import VECTOR


revision = 'b70c1a4d9e26'
down_revision = '7596ddc82698'
branch_labels = None
depends_on = None


def upgrade():
    # PostgreSQL must already have the pgvector extension files installed.
    # SQLite is used by the existing offline tests; it has no vector search.
    if op.get_bind().dialect.name == 'postgresql':
        op.execute('CREATE EXTENSION IF NOT EXISTS vector')

    op.add_column(
        'journal_entries',
        sa.Column('embedding', VECTOR(1536), nullable=True),
    )


def downgrade():
    # Retain the extension: other tables may also use its types/functions.
    op.drop_column('journal_entries', 'embedding')
