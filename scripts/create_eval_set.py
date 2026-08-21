"""
scripts/create_eval_set.py
Extract gold evaluation queries with known is_selected relevance annotations from MSMARCO-XI.
Creates the evaluation benchmark used by retrieval evaluation and latency measurement.
"""

import os
import sys
import json
import argparse

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

def create_eval_set(
    input_records="data/processed/corpus_records.jsonl",
    output_benchmark="data/evaluation/eval_benchmark.json",
    output_test_queries="evaluation/test_queries.json",
    num_queries=150
):
    print("=" * 70)
    print("  CREATING DATASET-GROUNDED EVALUATION BENCHMARK")
    print("=" * 70)

    if not os.path.exists(input_records):
        raise FileNotFoundError(f"Input records {input_records} not found.")

    os.makedirs(os.path.dirname(output_benchmark), exist_ok=True)
    os.makedirs(os.path.dirname(output_test_queries), exist_ok=True)

    benchmark_queries = []
    
    with open(input_records, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            rec = json.loads(line)
            query_id = rec.get("query_id")
            query = rec.get("query")
            eng_query = rec.get("Eng_Query")
            answer = rec.get("Answer")
            passages = rec.get("passages", {})
            trans_passages = passages.get("Translated_passages", [])
            is_selected = passages.get("is_selected", [])

            # Check if there is at least one gold selected passage
            selected_indices = [idx for idx, val in enumerate(is_selected) if val == 1 and idx < len(trans_passages)]
            if not selected_indices or not query or not query.strip():
                continue

            gold_chunks = [f"q{query_id}_p{idx}_c0" for idx in selected_indices]
            gold_passages_text = [trans_passages[idx] for idx in selected_indices]

            benchmark_item = {
                "query_id": query_id,
                "query": query.strip(),
                "eng_query": eng_query.strip() if eng_query else "",
                "gold_answer": answer.strip() if answer else "",
                "gold_passage_indices": selected_indices,
                "gold_chunk_ids": gold_chunks,
                "gold_passages_snippet": [t[:200] for t in gold_passages_text]
            }
            benchmark_queries.append(benchmark_item)

            if len(benchmark_queries) >= num_queries:
                break

    # Save benchmark
    with open(output_benchmark, "w", encoding="utf-8") as f:
        json.dump(benchmark_queries, f, indent=2, ensure_ascii=False)

    # Save simplified test queries for latency runner
    simple_queries = [
        {
            "query_id": b["query_id"],
            "query": b["query"],
            "eng_query": b["eng_query"]
        }
        for b in benchmark_queries
    ]
    with open(output_test_queries, "w", encoding="utf-8") as f:
        json.dump(simple_queries, f, indent=2, ensure_ascii=False)

    print(f"\n[OK] Evaluation benchmark successfully created!")
    print(f"     Total Gold Benchmark Queries: {len(benchmark_queries):,}")
    print(f"     Saved Benchmark To: {output_benchmark}")
    print(f"     Saved Test Queries To: {output_test_queries}")
    print("=" * 70)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create ground-truth evaluation benchmark from MSMARCO-XI.")
    parser.add_argument("--input_records", default="data/processed/corpus_records.jsonl", help="Preprocessed records")
    parser.add_argument("--output_benchmark", default="data/evaluation/eval_benchmark.json", help="Full benchmark output")
    parser.add_argument("--output_test_queries", default="evaluation/test_queries.json", help="Test queries output")
    parser.add_argument("--num_queries", type=int, default=150, help="Number of benchmark queries")
    args = parser.parse_args()

    create_eval_set(
        input_records=args.input_records,
        output_benchmark=args.output_benchmark,
        output_test_queries=args.output_test_queries,
        num_queries=args.num_queries
    )
