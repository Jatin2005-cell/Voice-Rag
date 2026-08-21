"""
scripts/inspect_dataset.py
Inspect the official ai4bharat/MSMARCO-XI Hugging Face dataset.
Outputs available languages, splits, column schema, row counts, passage structure, and relevance labels.
"""

import sys
import os
import json

# Ensure UTF-8 output encoding across platforms
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

def inspect_dataset():
    print("=" * 70)
    print("  MSMARCO-XI DATASET INSPECTOR (ai4bharat/MSMARCO-XI)")
    print("=" * 70)

    # Available Indic Languages supported by MSMARCO-XI
    languages = {
        "as": "Assamese",
        "bn": "Bengali",
        "gu": "Gujarati",
        "hi": "Hindi (Default Configuration)",
        "kn": "Kannada",
        "ml": "Malayalam",
        "mr": "Marathi",
        "ne": "Nepali",
        "or": "Odia",
        "pa": "Punjabi",
        "sa": "Sanskrit",
        "ta": "Tamil",
        "te": "Telugu",
        "ur": "Urdu"
    }

    print("\n[1] AVAILABLE INDIC LANGUAGE CONFIGURATIONS:")
    for code, name in languages.items():
        prefix = "-> [ACTIVE]" if code == "hi" else "  "
        print(f"  {prefix} {code:<4} : {name}")

    print("\n[2] DATASET SPLITS:")
    print("  - train       : Large corpus split (~3.7 GB per language)")
    print("  - validation  : Gold validation split (~461 MB, 97,941 rows for Hindi)")

    # Check for local cached file or load
    cache_path = os.path.expanduser(r"~\.cache\huggingface\hub\datasets--ai4bharat--MSMARCO-XI\snapshots\bf5cdc1f26e581e519018e434db14edd1b77602b\validation\hinval.parquet")
    raw_local = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "raw", "hinval.parquet")
    
    source_file = None
    if os.path.exists(raw_local):
        source_file = raw_local
    elif os.path.exists(cache_path):
        source_file = cache_path

    if source_file:
        import pyarrow.parquet as pq
        table = pq.read_table(source_file)
        num_rows = len(table)
        print(f"\n[3] LOCAL DATASET METRICS (File: {os.path.basename(source_file)}):")
        print(f"  Total Rows: {num_rows:,}")
        
        print("\n[4] SCHEMA & COLUMN DEFINITION:")
        for field in table.schema:
            print(f"  - {field.name:<20} : {field.type}")

        # Sample row inspection
        sample = table.slice(0, 1).to_pylist()[0]
        passages = sample.get("passages", {})
        trans_passages = passages.get("Translated_passages", [])
        eng_passages = passages.get("English_passages", [])
        is_selected = passages.get("is_selected", [])

        print("\n[5] SAMPLE ROW INSPECTION:")
        print(f"  Query ID         : {sample.get('query_id')}")
        print(f"  Query Type       : {sample.get('query_type')}")
        print(f"  Target Language  : {sample.get('target_lang', 'hi')}")
        print(f"  Source Language  : {sample.get('source_lang', 'en')}")
        print(f"  Translated Query : {sample.get('query')}")
        print(f"  Original Query   : {sample.get('Eng_Query')}")
        print(f"  Translated Answer: {sample.get('Answer')}")
        print(f"  Original Answer  : {sample.get('Eng_Answer')}")
        
        print("\n[6] PASSAGE & RELEVANCE STRUCTURE:")
        print(f"  Candidate Passages Count: {len(trans_passages)}")
        print(f"  Relevance Indicators (is_selected): {is_selected}")
        selected_indices = [idx for idx, val in enumerate(is_selected) if val == 1]
        print(f"  Gold Relevant Indices: {selected_indices}")
        
        for idx in range(min(2, len(trans_passages))):
            relevance_flag = "[GOLD RELEVANT]" if is_selected[idx] == 1 else "[NEGATIVE]"
            print(f"\n  Passage #{idx+1} {relevance_flag}:")
            print(f"    Translated (hi): {trans_passages[idx][:180]}...")
            print(f"    Original (en)  : {eng_passages[idx][:180]}...")

    else:
        print("\n[!] Dataset file not yet downloaded to local disk. Run scripts/download_dataset.py.")

    print("\n" + "=" * 70)

if __name__ == "__main__":
    inspect_dataset()
