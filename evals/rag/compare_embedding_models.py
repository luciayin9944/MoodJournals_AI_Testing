## compare_embedding_models.py

import json
import os
from time import perf_counter

import numpy as np

from app import create_app
from config import db
from models import Journal, JournalEntry
from services.embedding_service import build_entry_embedding_text
from services.openai_client import call_openai
from services.retrieval_service import get_date_range
from evaluate_retrieval import (
    load_cases,
    calculate_metrics,
    summarize_results,
)


CASES_PATH = "evals/fixtures/retrieval_cases.json"
RESULTS_PATH = "evals/reports/embedding_models_comparison.json"
TOP_K = 10

# Standard API prices: USD per million input tokens.
# Review these prices before future experiments.
MODELS = {
    "text-embedding-3-small": {
        "dimensions": 1536,
        "price": 0.02,
    },
    "text-embedding-3-large": {
        "dimensions": 3072,
        "price": 0.13,
    },
}


# Read journal text once so both models use the same data.
def load_entries(user_ids, end_date):
    rows = (
        db.session.query(JournalEntry, Journal.user_id)
        .join(Journal)
        .filter(
            Journal.user_id.in_(user_ids),
            JournalEntry.entry_date <= end_date,
            JournalEntry.embedding.isnot(None),
        )
        .order_by(JournalEntry.id)
        .all()
    )

    return [
        {
            "id": entry.id,
            "user_id": user_id,
            "date": entry.entry_date,
            "text": build_entry_embedding_text(entry),
        }
        for entry, user_id in rows
    ]


# Generate temporary vectors and measure token usage and elapsed time.
def embed_texts(texts, model, dimensions):
    started = perf_counter()
    vectors = []
    tokens = 0

    # Send up to 32 texts per ordinary API request.
    for start in range(0, len(texts), 32):
        batch = texts[start:start + 32]

        response = call_openai(
            lambda client: client.embeddings.create(
                model=model,
                input=batch,
                dimensions=dimensions,
                encoding_format="float",
            )
        )

        # Preserve the original input order.
        data = sorted(response.data, key=lambda item: item.index)

        if len(data) != len(batch):
            raise ValueError(
                "The provider returned an unexpected vector count."
            )

        vectors.extend(item.embedding for item in data)
        tokens += response.usage.total_tokens

    vectors = np.asarray(vectors, dtype=float)

    if vectors.shape != (len(texts), dimensions):
        raise ValueError(
            "The provider returned unexpected vector dimensions."
        )

    # Normalize vectors so a dot product gives cosine similarity.
    lengths = np.linalg.norm(vectors, axis=1, keepdims=True)

    if not np.isfinite(vectors).all() or np.any(lengths == 0):
        raise ValueError("The provider returned an invalid vector.")

    vectors = vectors / lengths

    return vectors, tokens, perf_counter() - started


# Rank only entries allowed by this case's user and date filters.
def rank_entries(
    entries,
    vectors,
    question_vector,
    eligible_ids,
    top_k,
):
    scored = []

    for entry, vector in zip(entries, vectors):
        if entry["id"] in eligible_ids:
            score = float(np.dot(vector, question_vector))
            scored.append((entry["id"], score))

    # Highest similarity first; entry ID breaks ties.
    scored.sort(key=lambda item: (-item[1], item[0]))

    return [
        entry_id
        for entry_id, score in scored[:top_k]
    ]


def estimate_cost(tokens, price):
    return tokens / 1_000_000 * price


# Embed the journal dataset once, then evaluate every question.
def evaluate_model(model, settings, cases, entries, top_k):
    dimensions = settings["dimensions"]
    price = settings["price"]

    print(f"\nEmbedding journals with {model}...", flush=True)

    texts = [entry["text"] for entry in entries]

    vectors, corpus_tokens, corpus_seconds = embed_texts(
        texts,
        model,
        dimensions,
    )

    results = []
    query_tokens = 0

    for case in cases:
        print(f"Evaluating: {case['id']}", flush=True)

        question_vectors, tokens, embedding_seconds = embed_texts(
            [case["question"].strip()],
            model,
            dimensions,
        )
        query_tokens += tokens

        started = perf_counter()

        retrieved_ids = rank_entries(
            entries,
            vectors,
            question_vectors[0],
            case["eligible_ids"],
            top_k,
        )

        search_seconds = perf_counter() - started
        expected_ids = case["expected_entry_ids"]

        results.append({
            "id": case["id"],
            "user_id": case["user_id"],
            "question": case["question"],
            "time_range": case["time_range"],
            "start_date": (
                case["start_date"].isoformat()
                if case["start_date"] else None
            ),
            "end_date": case["end_date"].isoformat(),
            "expected_entry_ids": expected_ids,
            "retrieved_entry_ids": retrieved_ids,
            "matched_entry_ids": sorted(
                set(retrieved_ids) & set(expected_ids)
            ),
            "metrics": calculate_metrics(
                retrieved_ids,
                expected_ids,
                top_k,
            ),
            "embedding_seconds": embedding_seconds,
            "search_seconds": search_seconds,
            "query_seconds": embedding_seconds + search_seconds,
            "query_tokens": tokens,
        })

    summary = summarize_results(results)

    corpus_cost = estimate_cost(corpus_tokens, price)
    query_cost = estimate_cost(query_tokens, price)

    mean_query_seconds = (
        sum(result["query_seconds"] for result in results)
        / len(results)
    )

    return {
        "model": model,
        "dimensions": dimensions,
        "price_per_million_tokens": price,
        "summary": summary,
        "corpus_seconds": corpus_seconds,
        "mean_query_seconds": mean_query_seconds,
        "corpus_tokens": corpus_tokens,
        "query_tokens": query_tokens,
        "corpus_cost_usd": corpus_cost,
        "query_cost_usd": query_cost,
        "total_estimated_cost_usd": corpus_cost + query_cost,
        "results": results,
    }


def main():
    cases = load_cases(CASES_PATH)

    if not cases or TOP_K <= 0:
        raise ValueError(
            "Provide evaluation cases and a positive TOP_K."
        )

    # Resolve date boundaries once and reuse them for both models.
    for case in cases:
        case["start_date"], case["end_date"] = get_date_range(
            case["time_range"]
        )

    user_ids = {case["user_id"] for case in cases}
    end_date = max(case["end_date"] for case in cases)

    app = create_app()

    with app.app_context():
        entries = load_entries(user_ids, end_date)

        if not entries:
            raise ValueError("No eligible journal entries were found.")

        # Check labels before making paid API requests.
        for case in cases:
            case["eligible_ids"] = {
                entry["id"]
                for entry in entries
                if entry["user_id"] == case["user_id"]
                and entry["date"] <= case["end_date"]
                and (
                    case["start_date"] is None
                    or entry["date"] >= case["start_date"]
                )
            }

            expected = set(case["expected_entry_ids"])

            if not expected or not expected.issubset(
                case["eligible_ids"]
            ):
                raise ValueError(
                    f"{case['id']}: check expected IDs, ownership, "
                    "dates, and missing embeddings."
                )

        comparisons = []

        for model, settings in MODELS.items():
            result = evaluate_model(
                model,
                settings,
                cases,
                entries,
                TOP_K,
            )
            comparisons.append(result)

            print(f"\n{model}")

            for name, score in result["summary"].items():
                print(f"{name}@{TOP_K}: {score:.2%}")

            print(
                f"Mean query time: "
                f"{result['mean_query_seconds']:.3f}s"
            )
            print(
                f"Estimated total cost: "
                f"${result['total_estimated_cost_usd']:.6f}"
            )

    report = {
        "evaluation_date": end_date.isoformat(),
        "top_k": TOP_K,
        "case_count": len(cases),
        "entry_count": len(entries),
        "entry_ids": [entry["id"] for entry in entries],
        "models": comparisons,
    }

    os.makedirs(
        os.path.dirname(RESULTS_PATH),
        exist_ok=True,
    )

    with open(RESULTS_PATH, "w", encoding="utf-8") as file:
        json.dump(report, file, indent=2, ensure_ascii=False)

    print(f"\nReport saved to: {RESULTS_PATH}")


if __name__ == "__main__":
    main()