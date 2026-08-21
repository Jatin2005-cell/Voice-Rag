# VoiceRAG: Retrieval & Chunking Strategy

## 1. Multi-Strategy Chunking

MSMARCO-XI is structured at the natural passage level. We implement 4 distinct chunking strategies in `backend/app/services/chunking.py`:

| Strategy | Logic | Primary Use Case |
|---|---|---|
| **Passage-Aware (Default)** | Preserves MS MARCO natural passage boundaries without fragmentation. Sub-chunks only when `words > 250`. | High semantic coherence; avoids breaking sentences across chunks. |
| **Fixed-Size** | Strict windowing of 150 words per chunk. | Benchmark baseline comparison. |
| **Overlapping** | Sliding window of 150 words with 50 words stride overlap. | Ensures boundary terms are not lost in long documents. |
| **Metadata-Aware** | Prepends query taxonomy markers (e.g. `[DESCRIPTION]`) to each passage. | Categorical contextualization during vector similarity search. |

Every chunk record retains complete provenance:
```json
{
  "chunk_id": "q1102432_p5_c0",
  "query_id": 1102432,
  "passage_idx": 5,
  "chunk_idx": 0,
  "text": "...",
  "english_text": "...",
  "language": "hi",
  "is_selected": 1,
  "strategy": "passage_aware"
}
```

---

## 2. Vector Indexing & In-Memory Dot Product

To achieve sub-5ms dense retrieval:
- Embeddings are precomputed in batch using `SentenceTransformerEmbeddingProvider` (384-dimensional dense vectors).
- Vectors are stored in a normalized NumPy float32 matrix (`(N, 384)`).
- Cosine similarity is computed via optimized BLAS matrix-vector dot product:
  $$\text{Score} = \mathbf{V} \cdot \mathbf{q}$$
- O(N) top-K partition (`np.argpartition`) extracts the top candidate indices in ~1.5 - 3.0 ms over tens of thousands of chunks.
