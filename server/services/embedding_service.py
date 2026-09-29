"""Build semantic journal text and generate embedding vectors."""

from flask import current_app

from config import Config
from .exceptions import ProviderConfigurationError, ProviderResponseError
from .openai_client import call_openai


def build_entry_embedding_text(entry) -> str:
    notes = entry.notes
    if notes is not None and not isinstance(notes, str):
        raise ValueError("Entry notes must be a string or None.")

    parts = [
        f"Mood tag: {entry.mood_tag or 'Other'}",
        f"Mood score: {entry.mood_score}/10",
    ]
    if notes and notes.strip():
        parts.append(f"Notes: {notes.strip()}")
    return "\n".join(parts)


def generate_embedding(text: str) -> list[float]:
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Embedding text must be a non-empty string.")

    model = current_app.config.get("EMBEDDING_MODEL")
    dimensions = current_app.config.get("EMBEDDING_DIMENSIONS")
    # V1 has one vector column and no per-row model/version metadata.
    if (
        model != Config.EMBEDDING_MODEL
        or type(dimensions) is not int
        or dimensions != Config.EMBEDDING_DIMENSIONS
    ):
        raise ProviderConfigurationError(
            "Embedding settings must match the fixed V1 model and dimensions."
        )

    text = text.strip()
    response = call_openai(
        lambda client: client.embeddings.create(
            model=model,
            dimensions=dimensions,
            input=text,
            encoding_format="float",
        )
    )
    data = getattr(response, "data", None)
    if not isinstance(data, list) or len(data) != 1:
        raise ProviderResponseError("AI provider must return exactly one embedding.")

    embedding = getattr(data[0], "embedding", None)
    if not isinstance(embedding, list) or len(embedding) != dimensions:
        raise ProviderResponseError("AI provider returned an invalid embedding size.")
    return embedding


def generate_entry_embedding(entry) -> list[float]:
    text = build_entry_embedding_text(entry)
    return generate_embedding(text)
