"""
evaluation/run_latency.py
Empirical latency benchmark runner.
Executes RAG pipeline over N test queries, instruments per-stage latency,
computes empirical P50 / P70 / P100 / Mean / Min / Max, and verifies against the <200ms target.
"""

import os
import sys
import json
import time
import argparse
import numpy as np

# Add project root and backend to path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, os.path.join(ROOT_DIR, "backend"))

from app.services.orchestrator import RAGOrchestrator
from evaluation.metrics import calculate_latency_percentiles

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

def run_latency_benchmark(
    test_queries_file="evaluation/test_queries.json",
    output_dir="evaluation/results",
    num_queries=100,
    target_ms=200.0
):
    print("=" * 70)
    print("  RAG PIPELINE LATENCY BENCHMARK (P50 / P70 / P100 MEASUREMENT)")
    print("=" * 70)
    print(f"Test Queries File: {test_queries_file}")
    print(f"Target Latency: < {target_ms} ms")

    if not os.path.exists(test_queries_file):
        print("[!] Test queries not found. Creating from dataset...")
        from scripts.create_eval_set import create_eval_set
        create_eval_set(output_test_queries=test_queries_file)

    with open(test_queries_file, "r", encoding="utf-8") as f:
        queries_data = json.load(f)

    benchmark_queries = queries_data[:num_queries]
    actual_count = len(benchmark_queries)
    print(f"Loaded {actual_count} benchmark queries for latency profiling.")

    orchestrator = RAGOrchestrator()
    os.makedirs(output_dir, exist_ok=True)

    # Latency metric collectors
    total_rag_latencies = []
    embedding_latencies = []
    retrieval_latencies = []
    generation_latencies = []
    grounding_latencies = []
    context_latencies = []
    query_runs = []

    # Warmup query
    print("\nWarming up pipeline caches...")
    _ = orchestrator.run_rag_pipeline(benchmark_queries[0]["query"])

    print(f"Running latency benchmark across {actual_count} queries...\n")
    t0_bench = time.time()

    for idx, item in enumerate(benchmark_queries, start=1):
        q = item["query"]
        q_id = item.get("query_id")

        # Run pipeline
        res = orchestrator.run_rag_pipeline(q)
        lat = res["latency"]

        total_ms = lat["total_rag_ms"]
        total_rag_latencies.append(total_ms)
        embedding_latencies.append(lat["embedding_ms"])
        retrieval_latencies.append(lat["retrieval_ms"])
        context_latencies.append(lat["context_building_ms"])
        generation_latencies.append(lat["generation_ms"])
        grounding_latencies.append(lat["grounding_ms"])

        query_runs.append({
            "query_index": idx,
            "query_id": q_id,
            "query": q,
            "grounded": res["grounded"],
            "confidence": res["confidence"],
            "sources_count": len(res["sources"]),
            "latency": lat
        })

        if idx % 20 == 0 or idx == actual_count:
            p50_cur = np.percentile(total_rag_latencies, 50)
            print(f"  Processed {idx}/{actual_count} queries | Running P50: {p50_cur:.2f} ms")

    total_bench_duration = time.time() - t0_bench

    # Calculate percentiles
    total_rag_stats = calculate_latency_percentiles(total_rag_latencies)
    embedding_stats = calculate_latency_percentiles(embedding_latencies)
    retrieval_stats = calculate_latency_percentiles(retrieval_latencies)
    generation_stats = calculate_latency_percentiles(generation_latencies)
    grounding_stats = calculate_latency_percentiles(grounding_latencies)
    context_stats = calculate_latency_percentiles(context_latencies)

    p50 = total_rag_stats["p50_ms"]
    p70 = total_rag_stats["p70_ms"]
    p100 = total_rag_stats["p100_ms"]
    mean_ms = total_rag_stats["mean_ms"]

    status = "PASS" if p70 < target_ms else "NEEDS OPTIMIZATION"

    detailed_latency_output = {
        "num_queries": actual_count,
        "target_ms": target_ms,
        "status": status,
        "total_rag": total_rag_stats,
        "stage_breakdowns": {
            "embedding": embedding_stats,
            "retrieval": retrieval_stats,
            "context_building": context_stats,
            "generation": generation_stats,
            "grounding": grounding_stats
        },
        "query_runs": query_runs
    }

    latency_path = os.path.join(output_dir, "latency_results.json")
    with open(latency_path, "w", encoding="utf-8") as f:
        json.dump(detailed_latency_output, f, indent=2, ensure_ascii=False)

    # Read retrieval metrics if available to assemble master summary
    retrieval_path = os.path.join(output_dir, "retrieval_results.json")
    retrieval_data = {}
    if os.path.exists(retrieval_path):
        with open(retrieval_path, "r", encoding="utf-8") as f:
            retrieval_data = json.load(f)

    # Check dataset manifest for counts
    manifest_path = "data/processed/manifest.json"
    manifest_data = {}
    if os.path.exists(manifest_path):
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest_data = json.load(f)

    summary = {
        "project": "VoiceRAG",
        "tagline": "Ask. Retrieve. Verify.",
        "dataset_name": "ai4bharat/MSMARCO-XI",
        "dataset_language": os.getenv("DATASET_LANGUAGE", "hi"),
        "dataset_split": os.getenv("DATASET_SPLIT", "validation"),
        "indexed_rows": manifest_data.get("processed_rows", 2000),
        "indexed_passages": manifest_data.get("total_passages", 19987),
        "num_queries": actual_count,
        "target_ms": target_ms,
        "status": status,
        "p50_ms": p50,
        "p70_ms": p70,
        "p100_ms": p100,
        "mean_ms": mean_ms,
        "min_ms": total_rag_stats["min_ms"],
        "max_ms": total_rag_stats["max_ms"],
        "recall_at_1": retrieval_data.get("recall_at_1", 0.0),
        "recall_at_5": retrieval_data.get("recall_at_5", 0.0),
        "mrr_at_5": retrieval_data.get("mrr_at_5", 0.0),
        "ndcg_at_5": retrieval_data.get("ndcg_at_5", 0.0),
        "stages_mean_ms": {
            "embedding_ms": embedding_stats["mean_ms"],
            "retrieval_ms": retrieval_stats["mean_ms"],
            "context_building_ms": context_stats["mean_ms"],
            "generation_ms": generation_stats["mean_ms"],
            "grounding_ms": grounding_stats["mean_ms"],
            "total_rag_ms": mean_ms
        }
    }

    summary_path = os.path.join(output_dir, "summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 70)
    print("  EMPIRICAL LATENCY BENCHMARK RESULTS (Across N = %d Queries):" % actual_count)
    print("  Target Latency : < %.1f ms" % target_ms)
    print("  Status         : %s" % status)
    print("-" * 70)
    print(f"  P50 Latency    : {p50:.2f} ms")
    print(f"  P70 Latency    : {p70:.2f} ms")
    print(f"  P100 Latency   : {p100:.2f} ms")
    print(f"  Mean Latency   : {mean_ms:.2f} ms")
    print("-" * 70)
    print("  STAGE LATENCIES (Mean):")
    print(f"    - Embedding        : {embedding_stats['mean_ms']:.2f} ms")
    print(f"    - Vector Retrieval : {retrieval_stats['mean_ms']:.2f} ms")
    print(f"    - Context Building : {context_stats['mean_ms']:.2f} ms")
    print(f"    - Generation       : {generation_stats['mean_ms']:.2f} ms")
    print(f"    - Grounding Check  : {grounding_stats['mean_ms']:.2f} ms")
    print(f"    - Total RAG        : {mean_ms:.2f} ms")
    print(f"\n  Saved Latency Results To : {latency_path}")
    print(f"  Saved Master Summary To  : {summary_path}")
    print("=" * 70)

    return summary

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run empirical latency benchmark over test queries.")
    parser.add_argument("--test_queries_file", default="evaluation/test_queries.json")
    parser.add_argument("--output_dir", default="evaluation/results")
    parser.add_argument("--num_queries", type=int, default=100)
    parser.add_argument("--target_ms", type=float, default=200.0)
    args = parser.parse_args()

    run_latency_benchmark(
        test_queries_file=args.test_queries_file,
        output_dir=args.output_dir,
        num_queries=args.num_queries,
        target_ms=args.target_ms
    )
