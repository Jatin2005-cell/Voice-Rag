# VoiceRAG: Dataset Documentation (ai4bharat/MSMARCO-XI)

## 1. Overview
VoiceRAG strictly uses the official Indic MS MARCO benchmark:
- **Repository:** `https://huggingface.co/datasets/ai4bharat/MSMARCO-XI`
- **Supported Languages (14 Indic languages):**
  Assamese (`as`), Bengali (`bn`), Gujarati (`gu`), Hindi (`hi`), Kannada (`kn`), Malayalam (`ml`), Marathi (`mr`), Nepali (`ne`), Odia (`or`), Punjabi (`pa`), Sanskrit (`sa`), Tamil (`ta`), Telugu (`te`), Urdu (`ur`).

## 2. Active Language Configuration
- **Active Language:** Hindi (`hi` / `hin_Deva`)
- **Active Split:** `validation` (97,941 rows, 461 MB)
- **Extracted Subset:** 2,000 representative rows yielding **20,263 candidate passages** and **1,293 gold selected passages**.

## 3. Schema Definition
The dataset provides the following fields per record:
- `query_id` (int64): Unique query identifier
- `query_type` (string): Query taxonomy (e.g. DESCRIPTION, ENTITY, NUMERIC)
- `source_lang` (string): Original query language (`eng_Latn`)
- `target_lang` (string): Translated target language (`hin_Deva`)
- `query` (string): Translated query in target Indic language
- `Eng_Query` (string): Original English query
- `Answer` (string): Translated human-comprehension answer
- `Eng_Answer` (string): Original English answer
- `passages` (struct):
  - `is_selected` (list of int64, 0 or 1): **Gold ground truth relevance indicator**
  - `Translated_passages` (list of string): Candidate passage text translated to Indic language
  - `English_passages` (list of string): Candidate passage text in original English

## 4. Ingestion & Preprocessing
The ingestion pipeline is managed via:
1. `scripts/inspect_dataset.py`: Inspects remote/local schema, column definitions, and sample rows.
2. `scripts/download_dataset.py`: Downloads configurable parquet slices from Hugging Face.
3. `scripts/prepare_dataset.py`: Cleans and normalizes JSONL records in `data/processed/`.
4. `scripts/build_chunks.py`: Applies passage-aware semantic chunking in `data/chunks/`.
5. `scripts/build_index.py`: Precomputes multilingual embeddings into `data/index/`.
6. `scripts/create_eval_set.py`: Generates ground-truth evaluation pairs in `data/evaluation/`.
