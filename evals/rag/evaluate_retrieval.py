## evaluate_retrieval.py

import json
from app import create_app
from services.retrieval_service import retrieval_entries


def load_cases(path):
    with open(path, "r", encoding="utf-8") as file:
        cases = json.load(file)
        return cases
    

# Compare the retrieved IDs with the expected relevant IDs.
def calculate_metrics(retrieved_ids, expected_ids, top_k):
    expected = set(expected_ids)
    retrieved = set(retrieved_ids[:top_k])

    matched_count = len(retrieved & expected)

    return {
        "precision": matched_count / top_k,
        "recall": matched_count / len(expected),
        "hit_rate": int(matched_count > 0),
    }
    

# Run retrieval and calculate scores for one question.
def evaluate_case(case, top_k=10):
    entries = retrieval_entries(
        user_id=case["user_id"],
        question=case["question"],
        time_range=case["time_range"],
        top_k=top_k,
    )

    retrieved_ids = [entry.id for entry in entries]
    expected_ids = case["expected_entry_ids"]
    metrics = calculate_metrics(retrieved_ids, expected_ids, top_k)

    result = {
        "id": case["id"],
        "user_id": case["user_id"],
        "question": case["question"],
        "time_range": case["time_range"],
        "expected_entry_ids": expected_ids,
        "retrieved_entry_ids": retrieved_ids,
        "matched_entry_ids": sorted(
            set(retrieved_ids) & set(expected_ids)
        ),
        "metrics": metrics,
    }
    return result

    # {
    #     "id": "anxiety_01",
    #     "user_id": 1,
    #     "question": "What situations usually make me feel anxious?",
    #     "time_range": "all_time",
    #     "expected_entry_ids": [12, 18, 31, 44],
    #     "retrieved_entry_ids": [12, 99, 18],
    #     "matched_entry_ids": [12, 18],
    #     "metrics": {
    #         "hit_rate": 1,
    #         "precision": 2 / 3,
    #         "recall": 2 / 4,
    #     },
    # }


# Average each metric across all evaluated questions.
def summarize_results(results):
    summary = {}

    for name in {"hit_rate", "precision", "recall"}:
        total = 0

        for result in results:
            total += result["metrics"][name]

        #average:
        summary[name] = total/len(results) #ex: average_precision=(0.8+0.6+0.4)/3=0.6
    return summary


# Run the evaluation, print scores, and save a report.
def main():
    CASES_PATH = "evals/fixtures/retrieval_cases.json"
    RESULTS_PATH = "evals/reports/retrieval_results.json"
    top_k = 10
    cases = load_cases(CASES_PATH)
    results = []

    app = create_app()

    with app.app_context():
        for case in cases:
            result = evaluate_case(case, top_k)
            results.append(result)

            metrics = result["metrics"]

            print(f"\nEvaluating: {case['id']}", flush=True)
            print("Retrieved:", result["retrieved_entry_ids"])
            print("Matched:", result["matched_entry_ids"])
            print(f"Hit@{top_k}: {metrics['hit_rate']}")
            print(f"Precision@{top_k}: {metrics['precision']:.2%}")
            print(f"Recall@{top_k}: {metrics['recall']:.2%}")

    summary = summarize_results(results)

    print(f"\nAverage scores across {len(results)} questions:")
    print(f"Hit Rate@{top_k}: {summary['hit_rate']:.2%}")
    print(f"Precision@{top_k}: {summary['precision']:.2%}")
    print(f"Recall@{top_k}: {summary['recall']:.2%}")

    report = {
        "top_k": top_k,
        "case_count": len(results),
        "summary": summary,
        "results": results,
    }

    with open(RESULTS_PATH, "w", encoding="utf-8") as file:
        json.dump(report, file, indent=2, ensure_ascii=False)

    print(f"\nResults saved to: {RESULTS_PATH}")


if __name__ == "__main__":
    main()
