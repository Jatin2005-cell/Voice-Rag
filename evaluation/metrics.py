"""
evaluation/metrics.py
Standardized evaluation metrics for RAG retrieval and latency benchmarking.
Computes:
  - Recall@K
  - Mean Reciprocal Rank (MRR@K)
  - Normalized Discounted Cumulative Gain (NDCG@K)
  - P50, P70, P100 latency percentiles
"""

from typing import List, Dict, Any, Set, Union
import numpy as np
import math

def compute_recall_at_k(retrieved_ids: List[str], gold_ids: Union[List[str], Set[str]], k: int = 5) -> float:
    """Computes Recall@K: fraction of relevant items retrieved in top-K."""
    if not gold_ids:
        return 0.0
    gold_set = set(gold_ids)
    top_k_retrieved = retrieved_ids[:k]
    hits = len(gold_set.intersection(set(top_k_retrieved)))
    return 1.0 if hits > 0 else 0.0


def compute_mrr_at_k(retrieved_ids: List[str], gold_ids: Union[List[str], Set[str]], k: int = 5) -> float:
    """Computes Mean Reciprocal Rank (MRR@K): reciprocal rank of the first relevant retrieved item."""
    if not gold_ids:
        return 0.0
    gold_set = set(gold_ids)
    for rank, item_id in enumerate(retrieved_ids[:k], start=1):
        if item_id in gold_set:
            return 1.0 / rank
    return 0.0


def compute_ndcg_at_k(retrieved_ids: List[str], gold_ids: Union[List[str], Set[str]], k: int = 5) -> float:
    """Computes NDCG@K."""
    if not gold_ids:
        return 0.0
    gold_set = set(gold_ids)
    dcg = 0.0
    for i, item in enumerate(retrieved_ids[:k]):
        if item in gold_set:
            dcg += 1.0 / math.log2(i + 2)
    idcg = 1.0 / math.log2(2)  # For single relevant target
    return dcg / idcg if idcg > 0 else 0.0


def calculate_latency_percentiles(latencies: List[float]) -> Dict[str, float]:
    """Calculates empirical P50, P70, P100, Mean, Min, Max from actual measurements."""
    if not latencies:
        return {
            "p50_ms": 0.0,
            "p70_ms": 0.0,
            "p100_ms": 0.0,
            "mean_ms": 0.0,
            "min_ms": 0.0,
            "max_ms": 0.0,
            "count": 0
        }

    arr = np.array(latencies, dtype=np.float64)
    return {
        "p50_ms": round(float(np.percentile(arr, 50)), 2),
        "p70_ms": round(float(np.percentile(arr, 70)), 2),
        "p100_ms": round(float(np.max(arr)), 2),
        "mean_ms": round(float(np.mean(arr)), 2),
        "min_ms": round(float(np.min(arr)), 2),
        "max_ms": round(float(np.max(arr)), 2),
        "count": len(latencies)
    }
