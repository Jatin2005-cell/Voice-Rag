"""
scripts/prepare_dataset.py
Extract and prepare a clean, configurable subset of MSMARCO-XI data.
Splits data cleanly into corpus knowledge base and evaluation subsets.
Preserves query_id, query_type, language, queries, answers, passages, and is_selected relevance labels.
"""

import os
import sys
import json
import argparse
import pyarrow.parquet as pq

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

def prepare_dataset(
    input_parquet=None,
    output_dir="data/processed",
    max_rows=2000,
    language="hi"
):
    print("=" * 70)
    print("  PREPARING MSMARCO-XI DATASET SUBSET")
    print("=" * 70)

    # Locate source parquet
    if not input_parquet or not os.path.exists(input_parquet):
        cache_path = os.path.expanduser(
            r"~\.cache\huggingface\hub\datasets--ai4bharat--MSMARCO-XI\snapshots\bf5cdc1f26e581e519018e434db14edd1b77602b\validation\hinval.parquet"
        )
        local_path = "data/raw/hin_validation.parquet"
        if os.path.exists(local_path):
            input_parquet = local_path
        elif os.path.exists(cache_path):
            input_parquet = cache_path
        else:
            raise FileNotFoundError("Source dataset parquet not found. Run scripts/download_dataset.py first.")

    print(f"Reading from source: {input_parquet}")
    print(f"Max rows to process: {max_rows:,}")
    print(f"Target language: {language}")

    table = pq.read_table(input_parquet)
    total_source_rows = len(table)
    print(f"Total rows available in source table: {total_source_rows:,}")

    num_rows = min(max_rows, total_source_rows)
    sub_table = table.slice(0, num_rows)
    records = sub_table.to_pylist()

    os.makedirs(output_dir, exist_ok=True)
    out_file = os.path.join(output_dir, "corpus_records.jsonl")
    
    total_passages = 0
    total_selected_passages = 0

    with open(out_file, "w", encoding="utf-8") as f:
        for row in records:
            passages = row.get("passages", {})
            trans_passages = passages.get("Translated_passages", []) or []
            eng_passages = passages.get("English_passages", []) or []
            is_selected = passages.get("is_selected", []) or []
            
            total_passages += len(trans_passages)
            total_selected_passages += sum(is_selected)

            clean_record = {
                "query_id": row.get("query_id"),
                "query_type": row.get("query_type"),
                "target_lang": row.get("target_lang", language),
                "source_lang": row.get("source_lang", "en"),
                "query": row.get("query"),
                "Eng_Query": row.get("Eng_Query"),
                "Answer": row.get("Answer"),
                "Eng_Answer": row.get("Eng_Answer"),
                "passages": {
                    "Translated_passages": trans_passages,
                    "English_passages": eng_passages,
                    "is_selected": is_selected
                }
            }
            f.write(json.dumps(clean_record, ensure_ascii=False) + "\n")

    manifest = {
        "dataset_name": "ai4bharat/MSMARCO-XI",
        "language": language,
        "source_parquet": input_parquet,
        "processed_rows": num_rows,
        "total_passages": total_passages,
        "total_selected_passages": total_selected_passages,
        "output_file": out_file
    }
    manifest_path = os.path.join(output_dir, "manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(f"\n[OK] Prepared dataset saved to: {out_file}")
    print(f"     Rows Processed: {num_rows:,}")
    print(f"     Candidate Passages Extracted: {total_passages:,}")
    print(f"     Gold Relevant Passages: {total_selected_passages:,}")
    print(f"     Manifest saved to: {manifest_path}")
    print("=" * 70)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Prepare MSMARCO-XI subset for RAG ingestion.")
    parser.add_argument("--input_parquet", default=None, help="Path to input parquet file")
    parser.add_argument("--output_dir", default="data/processed", help="Output directory")
    parser.add_argument("--max_rows", type=int, default=int(os.getenv("MAX_ROWS", "2000")), help="Number of rows to process")
    parser.add_argument("--language", default=os.getenv("DATASET_LANGUAGE", "hi"), help="Language code")
    args = parser.parse_args()

    prepare_dataset(
        input_parquet=args.input_parquet,
        output_dir=args.output_dir,
        max_rows=args.max_rows,
        language=args.language
    )
