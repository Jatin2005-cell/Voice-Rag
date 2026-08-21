"""
scripts/build_chunks.py
Chunking CLI script.
Loads preprocessed MSMARCO-XI records and applies the chosen chunking strategy.
Outputs chunks.jsonl and chunk_stats.json.
"""

import os
import sys
import json
import argparse

# Add backend to sys.path so we can import chunking service
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))
from app.services.chunking import get_chunker, ChunkRecord

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

def build_chunks(
    input_file="data/processed/corpus_records.jsonl",
    output_dir="data/chunks",
    strategy="passage"
):
    print("=" * 70)
    print("  BUILDING RAG CHUNKS (MULTI-STRATEGY CHUNKING)")
    print("=" * 70)
    print(f"Input records: {input_file}")
    print(f"Chunking Strategy: {strategy}")

    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Input records not found at {input_file}. Run scripts/prepare_dataset.py first.")

    chunker = get_chunker(strategy)
    os.makedirs(output_dir, exist_ok=True)
    out_file = os.path.join(output_dir, "chunks.jsonl")

    total_records = 0
    total_chunks = 0
    total_words = 0
    selected_chunks = 0

    with open(input_file, "r", encoding="utf-8") as fin, open(out_file, "w", encoding="utf-8") as fout:
        for line in fin:
            if not line.strip():
                continue
            record = json.loads(line)
            chunks = chunker.chunk_record(record)
            total_records += 1
            total_chunks += len(chunks)
            for c in chunks:
                total_words += c.word_count
                if c.is_selected == 1:
                    selected_chunks += 1
                fout.write(json.dumps(c.to_dict(), ensure_ascii=False) + "\n")

    avg_words = (total_words / total_chunks) if total_chunks > 0 else 0
    stats = {
        "strategy": strategy,
        "input_records": total_records,
        "total_chunks": total_chunks,
        "selected_chunks": selected_chunks,
        "average_words_per_chunk": round(avg_words, 2),
        "output_file": out_file
    }
    stats_path = os.path.join(output_dir, "chunk_stats.json")
    with open(stats_path, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)

    print(f"\n[OK] Chunks generated successfully!")
    print(f"     Strategy: {strategy}")
    print(f"     Source Records: {total_records:,}")
    print(f"     Total Chunks Produced: {total_chunks:,}")
    print(f"     Gold Selected Chunks: {selected_chunks:,}")
    print(f"     Average Words / Chunk: {avg_words:.1f}")
    print(f"     Output Saved To: {out_file}")
    print("=" * 70)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build chunks from MSMARCO-XI dataset records.")
    parser.add_argument("--input_file", default="data/processed/corpus_records.jsonl", help="Input JSONL file")
    parser.add_argument("--output_dir", default="data/chunks", help="Output directory")
    parser.add_argument("--strategy", default=os.getenv("CHUNKING_STRATEGY", "passage"), help="Strategy: passage, fixed, overlap, metadata")
    args = parser.parse_args()

    build_chunks(
        input_file=args.input_file,
        output_dir=args.output_dir,
        strategy=args.strategy
    )
