"""Knowledge Base Toolkit for NPA-guy's property intelligence agent.

Wraps LightRAG with temporal metadata tracking via kb_metadata table.
Every ingestion records category, area, source, and auto-calculated expiry.
"""

import hashlib
import os
import subprocess
from datetime import datetime

from agno.tools import Toolkit
from loguru import logger
try:
    from .lightrag_wrapper import LightRAGManager, POSTGRES_DEFAULT_URI
except ImportError:
    from lightrag_wrapper import LightRAGManager, POSTGRES_DEFAULT_URI

# Category → TTL in days
CATEGORY_TTL = {
    "pricing": 90,         # 3 months
    "rental": 90,          # 3 months
    "flood": 365,          # 12 months (seasonal)
    "legal": 180,          # 6 months
    "area": 180,           # 6 months
    "project": 365,        # 12 months
    "infrastructure": 365, # 12 months
    "other": 180,          # 6 months default
}


def _make_doc_id(content: str) -> str:
    """Generate a deterministic doc ID from content hash."""
    return f"npa-{hashlib.sha256(content.encode()).hexdigest()[:16]}"


def _run_psql(pg_uri: str, sql: str, params: tuple = ()) -> subprocess.CompletedProcess:
    """Run a psql command. For parameterized queries, use %s placeholders."""
    # For simple queries without params, run directly
    if not params:
        return subprocess.run(
            ["psql", pg_uri, "-c", sql],
            capture_output=True, text=True, timeout=10,
        )
    # For parameterized, build the command with escaped values
    escaped_sql = sql
    for p in params:
        if p is None:
            escaped_sql = escaped_sql.replace("%s", "NULL", 1)
        else:
            escaped = str(p).replace("'", "''")
            escaped_sql = escaped_sql.replace("%s", f"'{escaped}'", 1)
    return subprocess.run(
        ["psql", pg_uri, "-c", escaped_sql],
        capture_output=True, text=True, timeout=10,
    )


class KBToolkit(Toolkit):
    def __init__(self, **kwargs):
        self._kb = LightRAGManager()
        self._pg_uri = os.environ.get("POSTGRES_URI", POSTGRES_DEFAULT_URI)
        tools = [
            self.insert_document,
            self.query_knowledge,
            self.check_freshness,
            self.get_stale_entries,
            self.get_graph_stats,
            self.health_check,
        ]
        super().__init__(name="kb_toolkit", tools=tools, **kwargs)

    def insert_document(
        self,
        content: str,
        description: str = "",
        category: str = "other",
        area: str = "",
        source: str = "",
    ) -> str:
        """Insert a document into NPA-guy's knowledge base WITH temporal tracking.

        Every ingestion is tracked with category, area, source, and auto-calculated expiry.
        This allows checking data freshness and flagging stale entries.

        Categories and their TTL (time-to-live):
        - "pricing": 90 days (sale prices, price/sqm benchmarks)
        - "rental": 90 days (rental rates, yield data)
        - "flood": 365 days (flood reports, risk assessments)
        - "legal": 180 days (title issues, encumbrances, court info)
        - "area": 180 days (area intelligence, amenities, neighborhood info)
        - "project": 365 days (developer info, building reviews, juristic person)
        - "infrastructure": 365 days (BTS extensions, expressways, malls)
        - "other": 180 days (default)

        Args:
            content (str): The document text to ingest (recommended: under 2000 chars)
            description (str): Brief label (e.g. "Sukhumvit 77 rental rates April 2026")
            category (str): One of: pricing, rental, flood, legal, area, project, infrastructure, other
            area (str): Geographic area (e.g. "สุขุมวิท 77", "อ่อนนุช", "บางเขน")
            source (str): Data source (e.g. "DDProperty", "Hipflat", "Pantip", "web_search")

        Returns:
            str: Success/failure message with metadata info
        """
        logger.info(
            f"[TOOL CALLED] insert_document(len={len(content)}, "
            f"cat='{category}', area='{area}', src='{source}')"
        )

        # Validate category
        if category not in CATEGORY_TTL:
            category = "other"

        # Prepend temporal header to content for LightRAG entity extraction
        today = datetime.now().strftime("%Y-%m-%d")
        ttl_days = CATEGORY_TTL[category]
        temporal_header = (
            f"[Date: {today}] [Category: {category}] "
            f"[Area: {area or 'unspecified'}] [Source: {source or 'unspecified'}] "
            f"[Valid for: {ttl_days} days]\n\n"
        )
        enriched_content = temporal_header + content

        # Ingest to LightRAG
        result = self._kb.insert_document(enriched_content, description)
        logger.info(f"[TOOL RESULT] {result[:100]}")

        # Write metadata to kb_metadata table
        doc_id = _make_doc_id(content)
        try:
            meta_result = _run_psql(
                self._pg_uri,
                f"INSERT INTO kb_metadata "
                f"(doc_id, category, area, source, summary, valid_until) "
                f"VALUES (%s, %s, %s, %s, %s, "
                f"NOW() + INTERVAL '{ttl_days} days')",
                (doc_id, category, area or None, source or None, description[:500]),
            )
            if meta_result.returncode != 0:
                logger.warning(f"Metadata write failed: {meta_result.stderr[:200]}")
                result += f"\n⚠️ Metadata tracking failed (KB ingest still succeeded)"
            else:
                result += (
                    f"\n📋 Metadata: category={category}, area={area or '-'}, "
                    f"expires in {ttl_days} days"
                )
        except Exception as e:
            logger.warning(f"Metadata write error: {e}")

        return result

    def query_knowledge(self, query: str, mode: str = "hybrid") -> str:
        """Query NPA-guy's knowledge base for stored property insights.

        Results include temporal headers [Date: ...] so you can judge data freshness.
        If data looks old, use check_freshness() to verify, or re-search for updated info.

        Modes:
        - "hybrid" (default): Entity + thematic. Best for most queries.
        - "local": Entity-focused. Best for specific properties/projects.
        - "global": Theme-focused. Best for area trends, market patterns.
        - "mix": KG + vector. Best for finding connections.
        - "naive": Vector only. Fastest.

        Args:
            query (str): The search query
            mode (str): Query mode

        Returns:
            str: Retrieved knowledge (check [Date:] headers for freshness)
        """
        query_preview = f"{query[:50]}..." if len(query) > 50 else query
        logger.info(f"[TOOL CALLED] query_knowledge(query='{query_preview}', mode='{mode}')")
        result = self._kb.query_knowledge(query, mode)
        logger.info(f"[TOOL RESULT] len={len(result)}")
        return result

    def check_freshness(self, area: str = "", category: str = "") -> str:
        """Check freshness of KB data for a given area and/or category.

        Returns counts of fresh vs stale entries. Use before relying on KB data
        for pricing or rental recommendations.

        Args:
            area (str): Area to check (e.g. "อ่อนนุช", "สุขุมวิท"). Empty = all areas.
            category (str): Category to check (e.g. "pricing", "rental"). Empty = all.

        Returns:
            str: Freshness report with counts and oldest entry date
        """
        logger.info(f"[TOOL CALLED] check_freshness(area='{area}', category='{category}')")

        conditions = []
        if area:
            conditions.append(f"area ILIKE '%{area.replace(chr(39), '')}%'")
        if category:
            conditions.append(f"category = '{category.replace(chr(39), '')}'")

        where = " AND ".join(conditions) if conditions else "1=1"

        sql = f"""
            SELECT
                COUNT(*) FILTER (WHERE NOT stale AND valid_until > NOW()) as fresh,
                COUNT(*) FILTER (WHERE stale OR valid_until <= NOW()) as stale,
                COUNT(*) as total,
                MIN(ingested_at)::text as oldest,
                MAX(ingested_at)::text as newest
            FROM kb_metadata
            WHERE {where};
        """

        try:
            result = subprocess.run(
                ["psql", self._pg_uri, "-t", "-A", "-F", "\t", "-c", sql],
                capture_output=True, text=True, timeout=10,
            )
            if result.returncode != 0:
                return f"Error: {result.stderr.strip()[:200]}"

            parts = result.stdout.strip().split("\t")
            if len(parts) >= 5:
                fresh, stale, total, oldest, newest = parts
                report = f"KB Freshness Report"
                if area:
                    report += f" — Area: {area}"
                if category:
                    report += f" — Category: {category}"
                report += f"\n  Fresh: {fresh} | Stale: {stale} | Total: {total}"
                report += f"\n  Oldest: {oldest} | Newest: {newest}"
                if int(stale) > 0:
                    report += f"\n  ⚠️ {stale} entries are stale — consider re-searching for updated data"
                return report
            return "No metadata entries found for this filter."
        except Exception as e:
            return f"Error: {e}"

    def get_stale_entries(self, limit: int = 20) -> str:
        """Get all stale KB entries that need re-verification.

        Returns entries where valid_until has passed or stale flag is set.
        Use this to identify which areas/topics need fresh web searches.

        Args:
            limit (int): Max entries to return (default: 20)

        Returns:
            str: List of stale entries with category, area, and age
        """
        logger.info(f"[TOOL CALLED] get_stale_entries(limit={limit})")

        sql = f"""
            SELECT category, area, source, summary,
                   ingested_at::text, valid_until::text,
                   EXTRACT(DAY FROM NOW() - valid_until)::int as days_overdue
            FROM kb_metadata
            WHERE stale = true OR valid_until <= NOW()
            ORDER BY valid_until ASC
            LIMIT {int(limit)};
        """

        try:
            result = subprocess.run(
                ["psql", self._pg_uri, "-t", "-A", "-F", "\t", "-c", sql],
                capture_output=True, text=True, timeout=10,
            )
            if result.returncode != 0:
                return f"Error: {result.stderr.strip()[:200]}"

            lines = result.stdout.strip()
            if not lines:
                return "✅ No stale entries. All KB data is fresh!"

            output = "Stale KB Entries (need re-verification):\n\n"
            for line in lines.split("\n"):
                parts = line.split("\t")
                if len(parts) >= 7:
                    cat, area, src, summary, ingested, valid, overdue = parts
                    output += f"  [{cat}] {area or '-'} — {summary[:80]}\n"
                    output += f"    Source: {src or '-'} | Ingested: {ingested[:10]} | Expired: {overdue}d ago\n\n"

            return output
        except Exception as e:
            return f"Error: {e}"

    def get_graph_stats(self) -> str:
        """Get statistics about NPA-guy's knowledge graph.

        Returns node count, edge count, storage size, plus metadata summary.

        Returns:
            str: Formatted knowledge graph statistics
        """
        logger.info("[TOOL CALLED] get_graph_stats()")
        result = self._kb.get_graph_stats()

        # Append metadata stats
        try:
            meta_result = subprocess.run(
                ["psql", self._pg_uri, "-t", "-A", "-F", "\t", "-c",
                 "SELECT COUNT(*) as total, "
                 "COUNT(*) FILTER (WHERE NOT stale AND valid_until > NOW()) as fresh, "
                 "COUNT(*) FILTER (WHERE stale OR valid_until <= NOW()) as stale "
                 "FROM kb_metadata;"],
                capture_output=True, text=True, timeout=10,
            )
            if meta_result.returncode == 0:
                parts = meta_result.stdout.strip().split("\t")
                if len(parts) >= 3:
                    total, fresh, stale = parts
                    result += (
                        f"\n- Tracked documents: {total} "
                        f"(fresh: {fresh}, stale: {stale})"
                    )
        except Exception:
            pass

        logger.info(f"[TOOL RESULT] {result[:100]}")
        return result

    def health_check(self) -> str:
        """Check the health of NPA-guy's knowledge base system.

        Verifies: LightRAG installation, API key, storage, metadata table.

        Returns:
            str: Health status report
        """
        logger.info("[TOOL CALLED] health_check()")
        result = self._kb.health_check()

        # Check metadata table
        try:
            meta_result = subprocess.run(
                ["psql", self._pg_uri, "-t", "-A", "-c",
                 "SELECT COUNT(*) FROM kb_metadata;"],
                capture_output=True, text=True, timeout=10,
            )
            if meta_result.returncode == 0:
                result += f"\n- Metadata table: OK ({meta_result.stdout.strip()} entries)"
            else:
                result += f"\n- Metadata table: ERROR ({meta_result.stderr.strip()[:100]})"
        except Exception as e:
            result += f"\n- Metadata table: ERROR ({e})"

        return result
