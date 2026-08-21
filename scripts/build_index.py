"""
scripts/build_index.py
Build precomputed vector index from generated chunks.
Encodes chunk texts using the configured multilingual embedding provider and saves vector index & metadata to data/index/.
"""

import os
import sys
import json
import time
import argparse
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))
from app.services.embeddings import get_embedding_provider
from app.services.vector_store import FastDenseVectorStore

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

def build_index(
    chunks_file="data/chunks/chunks.jsonl",
    output_dir="data/index",
    batch_size=128,
    limit=None
):
    print("=" * 70)
    print("  BUILDING PRECOMPUTED MULTILINGUAL VECTOR INDEX")
    print("=" * 70)
    print(f"Loading chunks from: {chunks_file}")

    if not os.path.exists(chunks_file):
        raise FileNotFoundError(f"Chunks file {chunks_file} not found. Run scripts/build_chunks.py first.")

    records = []
    texts = []
    with open(chunks_file, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            rec = json.loads(line)
            records.append(rec)
            texts.append(rec["text"])
            if limit and len(records) >= limit:
                break

    total_chunks = len(records)
    print(f"Total chunks to index: {total_chunks:,}")

    embedder = get_embedding_provider()
    print(f"Embedding Provider: {embedder.model_name} (Dimension: {embedder.dimension})")
    print(f"Batch Size: {batch_size}")

    t0 = time.time()
    embeddings = []
    for i in range(0, total_chunks, batch_size):
        batch_texts = texts[i:i + batch_size]
        batch_embs = embedder.embed_batch(batch_texts, batch_size=batch_size)
        embeddings.extend(batch_embs)
        elapsed = time.time() - t0
        pct = min(100.0, (i + len(batch_texts)) / total_chunks * 100.0)
        print(f"  Indexed {i + len(batch_texts):,}/{total_chunks:,} chunks ({pct:.1f}%) | Elapsed: {elapsed:.1f}s", end="\r")

    print("\nEncoding complete. Building vector store...")
    emb_matrix = np.array(embeddings, dtype=np.float32)

    store = FastDenseVectorStore(dimension=embedder.dimension)
    store.upsert(records, emb_matrix)
    store.save(output_dir)

    total_time = time.time() - t0
    print(f"\n[OK] Vector index successfully built and saved to: {output_dir}")
    print(f"     Total Vectors: {total_chunks:,}")
    print(f"     Embedding Dimension: {embedder.dimension}")
    print(f"     Total Indexing Time: {total_time:.2f}s ({total_chunks / max(1, total_time):.1f} chunks/sec)")
    print("=" * 70)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Precompute vector index for MSMARCO-XI chunks.")
    parser.add_argument("--chunks_file", default="data/chunks/chunks.jsonl", help="Input chunks file")
    parser.add_argument("--output_dir", default="data/index", help="Output directory for index")
    parser.add_argument("--batch_size", type=int, default=128, help="Embedding batch size")
    parser.add_argument("--limit", type=int, default=None, help="Optional limit on number of chunks to index")
    args = parser.parse_args()

    build_index(
        chunks_file=args.chunks_file,
        output_dir=args.output_dir,
        batch_size=args.batch_size,
        limit=args.limit
    )
