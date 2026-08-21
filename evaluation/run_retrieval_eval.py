"""
evaluation/run_retrieval_eval.py
Evaluates retrieval accuracy against dataset is_selected gold annotations.
Measures Recall@1, Recall@5, MRR@5, NDCG@5.
Never hardcodes or fabricates values.
"""

import os
import sys
import json
import time
import argparse

# Add project root and backend to path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, os.path.join(ROOT_DIR, "backend"))

from app.services.retrieval import RetrievalPipeline
from evaluation.metrics import compute_recall_at_k, compute_mrr_at_k, compute_ndcg_at_k

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

def run_retrieval_evaluation(
    benchmark_file="data/evaluation/eval_benchmark.json",
    output_dir="evaluation/results",
    top_k=5
):
    print("=" * 70)
    print("  MSMARCO-XI DATASET-GROUNDED RETRIEVAL EVALUATION")
    print("=" * 70)
    print(f"Benchmark File: {benchmark_file}")
    print(f"Top-K: {top_k}")

    if not os.path.exists(benchmark_file):
        print("[!] Benchmark file not found. Generating from dataset...")
        from scripts.create_eval_set import create_eval_set
        create_eval_set(output_benchmark=benchmark_file)

    with open(benchmark_file, "r", encoding="utf-8") as f:
        benchmark = json.load(f)

    print(f"Loaded {len(benchmark):,} gold evaluation queries.")

    pipeline = RetrievalPipeline(top_k=top_k)
    os.makedirs(output_dir, exist_ok=True)

    recall_1_list = []
    recall_5_list = []
    mrr_5_list = []
    ndcg_5_list = []
    query_eval_records = []

    t0 = time.time()
    for idx, item in enumerate(benchmark, start=1):
        query = item["query"]
        gold_chunk_ids = set(item.get("gold_chunk_ids", []))
        query_id = item.get("query_id")

        # Run retrieval
        res = pipeline.retrieve(query, top_k=top_k, min_score=0.0)
        retrieved_chunks = [r.chunk_id for r in res["results"]]

        # Calculate metrics
        r1 = compute_recall_at_k(retrieved_chunks, gold_chunk_ids, k=1)
        r5 = compute_recall_at_k(retrieved_chunks, gold_chunk_ids, k=5)
        mrr5 = compute_mrr_at_k(retrieved_chunks, gold_chunk_ids, k=5)
        ndcg5 = compute_ndcg_at_k(retrieved_chunks, gold_chunk_ids, k=5)

        recall_1_list.append(r1)
        recall_5_list.append(r5)
        mrr_5_list.append(mrr5)
        ndcg_5_list.append(ndcg5)

        query_eval_records.append({
            "query_id": query_id,
            "query": query,
            "retrieved_chunk_ids": retrieved_chunks,
            "gold_chunk_ids": list(gold_chunk_ids),
            "recall_at_1": r1,
            "recall_at_5": r5,
            "mrr_at_5": mrr5,
            "top_score": res.get("top_score", 0.0),
            "latency_ms": res["latency"]["total_retrieval_ms"]
        })

        if idx % 25 == 0 or idx == len(benchmark):
            cur_r5 = sum(recall_5_list) / len(recall_5_list)
            cur_mrr = sum(mrr_5_list) / len(mrr_5_list)
            print(f"  Evaluated {idx}/{len(benchmark)} queries | Running Recall@5: {cur_r5:.4f} | MRR@5: {cur_mrr:.4f}")

    total_eval_time = time.time() - t0
    mean_recall_1 = sum(recall_1_list) / len(recall_1_list)
    mean_recall_5 = sum(recall_5_list) / len(recall_5_list)
    mean_mrr_5 = sum(mrr_5_list) / len(mrr_5_list)
    mean_ndcg_5 = sum(ndcg_5_list) / len(ndcg_5_list)

    eval_results = {
        "dataset_name": "ai4bharat/MSMARCO-XI",
        "num_queries_evaluated": len(benchmark),
        "recall_at_1": round(mean_recall_1, 4),
        "recall_at_5": round(mean_recall_5, 4),
        "mrr_at_5": round(mean_mrr_5, 4),
        "ndcg_at_5": round(mean_ndcg_5, 4),
        "total_eval_time_sec": round(total_eval_time, 2),
        "queries": query_eval_records
    }

    out_path = os.path.join(output_dir, "retrieval_results.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(eval_results, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 70)
    print("  DATASET RETRIEVAL EVALUATION RESULTS:")
    print(f"  Total Queries Evaluated : {len(benchmark)}")
    print(f"  Recall@1               : {mean_recall_1:.4f} ({mean_recall_1*100:.1f}%)")
    print(f"  Recall@5               : {mean_recall_5:.4f} ({mean_recall_5*100:.1f}%)")
    print(f"  MRR@5                  : {mean_mrr_5:.4f}")
    print(f"  NDCG@5                 : {mean_ndcg_5:.4f}")
    print(f"  Results saved to       : {out_path}")
    print("=" * 70)

    return eval_results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run dataset retrieval evaluation.")
    parser.add_argument("--benchmark_file", default="data/evaluation/eval_benchmark.json")
    parser.add_argument("--output_dir", default="evaluation/results")
    parser.add_argument("--top_k", type=int, default=5)
    args = parser.parse_args()

    run_retrieval_evaluation(
        benchmark_file=args.benchmark_file,
        output_dir=args.output_dir,
        top_k=args.top_k
    )
