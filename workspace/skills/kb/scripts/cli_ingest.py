#!/usr/bin/env python3
"""Batch ingest documents into NPA-guy's LightRAG knowledge base WITH temporal metadata.

Usage:
    python cli_ingest.py --text "content..." --category pricing --area "ภาษีเจริญ" --source "DDProperty"
    python cli_ingest.py --file <path> --category rental --area "บางแค"
    python cli_ingest.py --news-db [--limit N]

Metadata flags (all optional):
    --category <cat>   Category: pricing, rental, flood, legal, area, project, infrastructure, other
    --area <area>      Geographic area (e.g. "ภาษีเจริญ", "สุขุมวิท 77")
    --source <src>     Data source (e.g. "DDProperty", "Hipflat", "web_search")
    --description <d>  Brief label for the document
"""

import argparse
import sqlite3
import sys
from pathlib import Path

# Ensure we can import from the same directory
sys.path.insert(0, str(Path(__file__).resolve().parent))

from kb_tools import KBToolkit


def ingest_text(kb: KBToolkit, text: str, **metadata) -> None:
    print(f"Ingesting text ({len(text)} chars)")
    result = kb.insert_document(
        content=text,
        description=metadata.get("description", ""),
        category=metadata.get("category", "other"),
        area=metadata.get("area", ""),
        source=metadata.get("source", ""),
    )
    print(result)
    if "Error:" in result:
        sys.exit(1)


def ingest_file(kb: KBToolkit, file_path: str, **metadata) -> None:
    path = Path(file_path)
    if not path.exists():
        print(f"Error: file not found: {file_path}")
        sys.exit(1)
    content = path.read_text(encoding="utf-8")
    print(f"Ingesting file: {path.name} ({len(content)} chars)")
    result = kb.insert_document(
        content=content,
        description=metadata.get("description") or path.name,
        category=metadata.get("category", "other"),
        area=metadata.get("area", ""),
        source=metadata.get("source", ""),
    )
    print(result)
    if "Error:" in result:
        sys.exit(1)


def ingest_news_db(kb: KBToolkit, limit: int = 50, **metadata) -> None:
    db_path = Path(__file__).resolve().parents[3] / "skills" / "alphaear-news" / "data" / "signal_flux.db"
    if not db_path.exists():
        print(f"Error: database not found: {db_path}")
        sys.exit(1)

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(
        "SELECT title, content, source, publish_time FROM daily_news "
        "WHERE content IS NOT NULL AND content != '' "
        "ORDER BY publish_time DESC LIMIT ?",
        (limit,),
    )
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print("No news articles found in database.")
        return

    print(f"Found {len(rows)} articles to ingest")
    for i, row in enumerate(rows, 1):
        title = row["title"] or "Untitled"
        content = row["content"] or ""
        source = row["source"] or "unknown"
        publish_time = row["publish_time"] or ""
        doc = f"[{source}] {title}\nPublished: {publish_time}\n\n{content}"
        print(f"  [{i}/{len(rows)}] {title[:60]}...")
        result = kb.insert_document(
            content=doc,
            description=f"{source}: {title[:50]}",
            category=metadata.get("category", "other"),
            area=metadata.get("area", ""),
            source=source,
        )
        print(f"    -> {result}")


def main():
    parser = argparse.ArgumentParser(description="Batch ingest into NPA-guy's knowledge base with temporal metadata")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--file", type=str, help="Path to text/markdown file to ingest")
    group.add_argument("--text", type=str, help="Inline text to ingest")
    group.add_argument("--news-db", action="store_true", help="Ingest from signal_flux.db")
    parser.add_argument("--limit", type=int, default=50, help="Max articles for --news-db (default: 50)")
    parser.add_argument("--category", type=str, default="other",
                        help="Category: pricing, rental, flood, legal, area, project, infrastructure, other")
    parser.add_argument("--area", type=str, default="", help="Geographic area (e.g. 'ภาษีเจริญ')")
    parser.add_argument("--source", type=str, default="", help="Data source (e.g. 'DDProperty')")
    parser.add_argument("--description", type=str, default="", help="Brief label for the document")

    args = parser.parse_args()
    kb = KBToolkit()

    metadata = {
        "category": args.category,
        "area": args.area,
        "source": args.source,
        "description": args.description,
    }

    if args.file:
        ingest_file(kb, args.file, **metadata)
    elif args.text:
        ingest_text(kb, args.text, **metadata)
    elif args.news_db:
        ingest_news_db(kb, args.limit, **metadata)


if __name__ == "__main__":
    main()
