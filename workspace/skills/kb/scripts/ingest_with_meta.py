#!/usr/bin/env python3
"""Ingest a document into LightRAG + kb_metadata table.

Usage:
    python ingest_with_meta.py \
        --text "content" \
        --summary "brief description" \
        --category pricing \
        --area "ดินแดง" \
        --source "DDProperty"
"""

import argparse
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add scripts dir to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

# Load .env
from dotenv import load_dotenv
env_path = Path(__file__).resolve().parents[3] / ".env"
load_dotenv(env_path)

from lightrag_wrapper import LightRAGManager

# Category TTL in days
CATEGORY_TTL = {
    "pricing": 90,
    "rental": 90,
    "flood": 365,
    "legal": 180,
    "area": 180,
    "project": 365,
    "infrastructure": 365,
    "other": 180,
}

VALID_CATEGORIES = list(CATEGORY_TTL.keys())


def get_next_doc_id() -> str:
    """Generate a doc ID based on timestamp."""
    return f"doc_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"


def insert_metadata(doc_id: str, summary: str, category: str, area: str, source: str) -> None:
    """Insert into kb_metadata table."""
    import subprocess
    
    ttl_days = CATEGORY_TTL.get(category, 180)
    valid_until = datetime.now() + timedelta(days=ttl_days)
    ingested_at = datetime.now().isoformat()
    valid_until_str = valid_until.isoformat()
    
    # Escape single quotes
    summary_escaped = summary.replace("'", "''")
    area_escaped = area.replace("'", "''") if area else ""
    source_escaped = source.replace("'", "''") if source else ""
    
    pg_uri = os.environ.get("POSTGRES_URI", "postgresql://arsapolm@localhost:5432/npa_kb")
    
    sql = f"""
    INSERT INTO kb_metadata (doc_id, category, area, source, summary, ingested_at, valid_until, stale)
    VALUES ('{doc_id}', '{category}', '{area_escaped}', '{source_escaped}', '{summary_escaped}', '{ingested_at}', '{valid_until_str}', false);
    """
    
    result = subprocess.run(
        ["psql", pg_uri, "-c", sql],
        capture_output=True, text=True, timeout=10,
    )
    if result.returncode != 0:
        print(f"  WARNING: metadata insert failed: {result.stderr.strip()}")
    else:
        print(f"  Metadata saved: category={category}, area={area}, source={source}, TTL={ttl_days}d")


def main():
    parser = argparse.ArgumentParser(description="Ingest document with metadata")
    parser.add_argument("--text", type=str, required=True, help="Content to ingest")
    parser.add_argument("--summary", type=str, required=True, help="Brief description for metadata")
    parser.add_argument("--category", type=str, required=True, choices=VALID_CATEGORIES, help="Category")
    parser.add_argument("--area", type=str, required=True, help="Geographic area")
    parser.add_argument("--source", type=str, required=True, help="Data source")
    
    args = parser.parse_args()
    
    # Generate doc ID
    doc_id = get_next_doc_id()
    
    # Prepend metadata context to content for LightRAG extraction
    content_with_meta = (
        f"[Date: {datetime.now().strftime('%Y-%m-%d')} | Category: {args.category} | "
        f"Area: {args.area} | Source: {args.source}]\n\n{args.text}"
    )
    
    # Ingest into LightRAG
    print(f"Ingesting: {args.summary[:60]}...")
    kb = LightRAGManager()
    result = kb.insert_document(content_with_meta, description=args.summary)
    print(f"  LightRAG: {result}")
    
    # Insert metadata
    insert_metadata(doc_id, args.summary, args.category, args.area, args.source)
    print(f"  Done! doc_id={doc_id}")


if __name__ == "__main__":
    main()
