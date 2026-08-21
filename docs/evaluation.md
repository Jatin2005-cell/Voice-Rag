# VoiceRAG: Evaluation Benchmark & Results

## 1. Ground Truth Methodology

Unlike traditional RAG demos that evaluate on arbitrary or synthetic QA pairs, VoiceRAG derives its ground truth directly from the official **ai4bharat/MSMARCO-XI** validation set.

### Relevance Indicators
In MS MARCO, each query is paired with candidate passages where:
$$\text{is\_selected} = \begin{cases} 1, & \text{Passage is gold human-annotated answer source} \\ 0, & \text{Negative/distractor passage} \end{cases}$$

## 2. Benchmark Metrics

| Metric | Measured Value | Interpretation |
|---|---|---|
| **Recall@1** | **15.0%** (0.1500) | Probability of gold passage ranking at #1 position. |
| **Recall@5** | **53.0%** (0.5300) | Probability of gold passage retrieved in top-5 candidates. |
| **MRR@5** | **0.2987** | Mean Reciprocal Rank across Top-5 retrieved items. |
| **NDCG@5** | **0.3650** | Normalized Discounted Cumulative Gain accounting for position. |
| **Evaluation Set Size** | **100 Queries** | Filtered validation queries with verified relevance labels. |

---

## 3. Empirical Latency Performance

Measured across N = 100 queries dynamically executed via `evaluation/run_latency.py`:

| Percentile / Metric | Latency (ms) | Target (&lt; 200 ms) | Status |
|---|---|---|---|
| **P50 (Median)** | **38.85 ms** | &lt; 200.0 ms | **PASS ✓** |
| **P70 (70th %ile)** | **44.00 ms** | &lt; 200.0 ms | **PASS ✓** |
| **P100 (Max Observed)** | **64.97 ms** | &lt; 200.0 ms | **PASS ✓** |
| **Mean Latency** | **40.60 ms** | &lt; 200.0 ms | **PASS ✓** |
| **Minimum Observed** | **1.30 ms** (Cached) | &lt; 200.0 ms | **PASS ✓** |
