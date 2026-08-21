"""
scripts/download_dataset.py
Configurable downloader for the official ai4bharat/MSMARCO-XI dataset.
Supports downloading any of the 14 Indic languages from Hugging Face.
"""

import os
import sys
import argparse
from huggingface_hub import hf_hub_download

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# Supported languages in ai4bharat/MSMARCO-XI
LANGUAGE_MAP = {
    "as": "asm",
    "bn": "ben",
    "gu": "guj",
    "hi": "hin",
    "kn": "kan",
    "ml": "mal",
    "mr": "mar",
    "ne": "nep",
    "or": "ori",
    "pa": "pan",
    "sa": "san",
    "ta": "tam",
    "te": "tel",
    "ur": "urd"
}

def download_dataset(language="hi", split="validation", output_dir=None):
    if language not in LANGUAGE_MAP:
        raise ValueError(f"Unsupported language '{language}'. Available: {list(LANGUAGE_MAP.keys())}")
    
    lang_code = LANGUAGE_MAP[language]
    filename = f"{split}/{lang_code}{'val' if split == 'validation' else 'train'}.parquet"
    
    print(f"Downloading MSMARCO-XI file: {filename} for language: {language}...")
    
    downloaded_path = hf_hub_download(
        repo_id="ai4bharat/MSMARCO-XI",
        filename=filename,
        repo_type="dataset"
    )
    print(f"Downloaded snapshot file to HF cache: {downloaded_path}")

    # Copy / link to data/raw if output_dir provided
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        dest = os.path.join(output_dir, f"{lang_code}_{split}.parquet")
        import shutil
        shutil.copyfile(downloaded_path, dest)
        print(f"Copied dataset to: {dest}")
        return dest
        
    return downloaded_path

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download MSMARCO-XI dataset from Hugging Face.")
    parser.add_argument("--language", default=os.getenv("DATASET_LANGUAGE", "hi"), help="Language code (e.g. hi, bn, ta, te)")
    parser.add_argument("--split", default=os.getenv("DATASET_SPLIT", "validation"), help="Split (validation or train)")
    parser.add_argument("--output_dir", default="data/raw", help="Target output directory")
    args = parser.parse_args()

    download_dataset(language=args.language, split=args.split, output_dir=args.output_dir)
