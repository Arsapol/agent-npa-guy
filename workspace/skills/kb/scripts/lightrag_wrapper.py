"""LightRAG wrapper configured for Gemini (LLM + embeddings) with PostgreSQL storage."""

import asyncio
import os
from pathlib import Path
from typing import Optional

import numpy as np
from loguru import logger

# Graceful import
try:
    from lightrag import LightRAG, QueryParam
    from lightrag.llm.openai import openai_complete_if_cache, openai_embed
    from lightrag.utils import EmbeddingFunc

    LIGHTRAG_AVAILABLE = True
except ImportError:
    LIGHTRAG_AVAILABLE = False
    logger.warning("lightrag-hku not installed. Run: pip install lightrag-hku")

GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai"
GEMINI_LLM_MODEL = "gemini-3.1-flash-lite-preview"
GEMINI_EMBEDDING_MODEL = "gemini-embedding-001"
GEMINI_EMBEDDING_DIM = 3072
POSTGRES_DEFAULT_URI = "postgresql://arsapolm@localhost:5432/npa_kb"
VALID_MODES = ("local", "global", "hybrid", "mix", "naive")


async def gemini_llm_complete(
    prompt: str,
    system_prompt: str | None = None,
    history_messages: list[dict] | None = None,
    **kwargs: object,
) -> str:
    if history_messages is None:
        history_messages = []
    return await openai_complete_if_cache(
        model=GEMINI_LLM_MODEL,
        prompt=prompt,
        system_prompt=system_prompt,
        history_messages=history_messages,
        api_key=os.environ.get("GEMINI_API_KEY"),
        base_url=GEMINI_BASE_URL,
        **kwargs,
    )


async def gemini_embedding(texts: list[str]) -> np.ndarray:
    return await openai_embed.func(
        texts,
        model=GEMINI_EMBEDDING_MODEL,
        api_key=os.environ.get("GEMINI_API_KEY"),
        base_url=GEMINI_BASE_URL,
    )


class LightRAGManager:
    def __init__(self, working_dir: Optional[str] = None):
        if working_dir:
            self.working_dir = Path(working_dir)
        else:
            self.working_dir = Path(__file__).resolve().parents[3] / "data" / "lightrag"
        self.working_dir.mkdir(parents=True, exist_ok=True)
        logger.debug(f"LightRAG working dir: {self.working_dir}")

    def _make_rag(self) -> "LightRAG":
        """Create a fresh LightRAG instance (needed per asyncio.run call)."""
        if not LIGHTRAG_AVAILABLE:
            raise RuntimeError(
                "lightrag-hku not installed. Run: pip install lightrag-hku"
            )
        gemini_key = os.environ.get("GEMINI_API_KEY")
        if not gemini_key:
            raise RuntimeError("GEMINI_API_KEY environment variable not set")
        pg_uri = os.environ.get("POSTGRES_URI", POSTGRES_DEFAULT_URI)
        if not pg_uri:
            raise RuntimeError("POSTGRES_URI environment variable not set")
        # Set PG connection env vars for LightRAG's PG implementation
        os.environ.setdefault("POSTGRES_HOST", "localhost")
        os.environ.setdefault("POSTGRES_PORT", "5432")
        os.environ.setdefault("POSTGRES_USER", "arsapolm")
        os.environ.setdefault("POSTGRES_PASSWORD", "")
        os.environ.setdefault("POSTGRES_DATABASE", "npa_kb")
        # Use HNSW_HALFVEC for 3072-dim vectors (HNSW limit is 2000 dims)
        os.environ.setdefault("POSTGRES_VECTOR_INDEX_TYPE", "HNSW_HALFVEC")
        return LightRAG(
            working_dir=str(self.working_dir),
            llm_model_func=gemini_llm_complete,
            embedding_func=EmbeddingFunc(
                embedding_dim=GEMINI_EMBEDDING_DIM,
                max_token_size=8192,
                func=gemini_embedding,
                model_name=GEMINI_EMBEDDING_MODEL,
            ),
            # PostgreSQL for concurrent-safe storage (no more JSON corruption)
            kv_storage="PGKVStorage",
            vector_storage="PGVectorStorage",
            doc_status_storage="PGDocStatusStorage",
            # PostgreSQL graph via Apache AGE (concurrent-safe, replaces NetworkX)
            graph_storage="PGGraphStorage",
        )

    async def _async_insert(self, content: str) -> str:
        rag = self._make_rag()
        try:
            await rag.initialize_storages()
            await rag.ainsert(content)
            return "ok"
        finally:
            await rag.finalize_storages()

    async def _async_query(self, query: str, mode: str) -> str:
        rag = self._make_rag()
        try:
            await rag.initialize_storages()
            result = await rag.aquery(query, param=QueryParam(mode=mode))
            return result
        finally:
            await rag.finalize_storages()

    def insert_document(self, content: str, description: str = "") -> str:
        if not LIGHTRAG_AVAILABLE:
            return "Error: lightrag-hku not installed. Run: pip install lightrag-hku"
        if not content or not content.strip():
            return "Error: content is empty"
        try:
            text = f"[Document: {description}]\n\n{content}" if description else content
            asyncio.run(self._async_insert(text))
            return f"Document ingested successfully ({len(content)} chars). Entities and relationships extracted."
        except Exception as e:
            logger.error(f"Insert failed: {e}")
            return f"Error during ingestion: {e}"

    def query_knowledge(self, query: str, mode: str = "hybrid") -> str:
        if not LIGHTRAG_AVAILABLE:
            return "Error: lightrag-hku not installed. Run: pip install lightrag-hku"
        if mode not in VALID_MODES:
            return (
                f"Error: invalid mode '{mode}'. Valid modes: {', '.join(VALID_MODES)}"
            )
        try:
            result = asyncio.run(self._async_query(query, mode))
            return result if result else "No relevant knowledge found."
        except Exception as e:
            logger.error(f"Query failed: {e}")
            return f"Error during query: {e}"

    def get_graph_stats(self) -> str:
        try:
            import subprocess

            pg_uri = os.environ.get("POSTGRES_URI", POSTGRES_DEFAULT_URI)

            # Query LightRAG's own entity/relation tables (authoritative)
            result = subprocess.run(
                ["psql", pg_uri, "-t", "-A", "-c",
                 "SELECT count(*) FROM lightrag_full_entities;"],
                capture_output=True, text=True, timeout=10,
            )
            entity_count = result.stdout.strip() if result.returncode == 0 else "?"

            result_r = subprocess.run(
                ["psql", pg_uri, "-t", "-A", "-c",
                 "SELECT count(*) FROM lightrag_full_relations;"],
                capture_output=True, text=True, timeout=10,
            )
            relation_count = result_r.stdout.strip() if result_r.returncode == 0 else "?"

            result_d = subprocess.run(
                ["psql", pg_uri, "-t", "-A", "-c",
                 "SELECT count(*) FROM lightrag_doc_status;"],
                capture_output=True, text=True, timeout=10,
            )
            doc_count = result_d.stdout.strip() if result_d.returncode == 0 else "?"

            result_c = subprocess.run(
                ["psql", pg_uri, "-t", "-A", "-c",
                 "SELECT count(*) FROM lightrag_doc_chunks;"],
                capture_output=True, text=True, timeout=10,
            )
            chunk_count = result_c.stdout.strip() if result_c.returncode == 0 else "?"

            # Also try AGE graph via LOAD (required since AGE 1.7.0)
            age_nodes = "?"
            age_edges = "?"
            try:
                result_an = subprocess.run(
                    ["psql", pg_uri, "-t", "-A", "-q", "-c",
                     "LOAD 'age'; SET search_path = ag_catalog, public; "
                     "SELECT * FROM cypher('chunk_entity_relation', $$ MATCH (v) RETURN count(v) $$) AS (cnt agtype);"],
                    capture_output=True, text=True, timeout=10,
                )
                if result_an.returncode == 0 and result_an.stdout.strip():
                    age_nodes = result_an.stdout.strip()

                result_ae = subprocess.run(
                    ["psql", pg_uri, "-t", "-A", "-q", "-c",
                     "LOAD 'age'; SET search_path = ag_catalog, public; "
                     "SELECT * FROM cypher('chunk_entity_relation', $$ MATCH ()-[e]->() RETURN count(e) $$) AS (cnt agtype);"],
                    capture_output=True, text=True, timeout=10,
                )
                if result_ae.returncode == 0 and result_ae.stdout.strip():
                    age_edges = result_ae.stdout.strip()
            except Exception:
                pass

            return (
                f"Knowledge Base Statistics:\n"
                f"- Documents: {doc_count}\n"
                f"- Chunks: {chunk_count}\n"
                f"- Entities: {entity_count}\n"
                f"- Relations: {relation_count}\n"
                f"- AGE graph nodes: {age_nodes}\n"
                f"- AGE graph edges: {age_edges}\n"
                f"- Storage: PostgreSQL (KV/vectors via pgvector/graph via AGE)\n"
                f"- Database: ada_kb\n"
                f"- Working directory: {self.working_dir}"
            )
        except Exception as e:
            logger.error(f"Graph stats failed: {e}")
            return f"Error reading graph stats: {e}"

    def health_check(self) -> str:
        checks = []
        # 1. LightRAG installed
        checks.append(
            f"LightRAG installed: {'yes' if LIGHTRAG_AVAILABLE else 'NO - run: pip install lightrag-hku'}"
        )
        # 2. API key
        gemini_key = os.environ.get("GEMINI_API_KEY")
        checks.append(
            f"GEMINI_API_KEY set: {'yes' if gemini_key else 'NO - set GEMINI_API_KEY env var'}"
        )
        # 3. PostgreSQL connection
        pg_status = self._check_postgres()
        checks.append(f"PostgreSQL: {pg_status}")
        # 4. Working directory
        checks.append(
            f"Working directory: {self.working_dir} ({'exists' if self.working_dir.exists() else 'MISSING'})"
        )
        # 5. AGE extension
        age_status = self._check_age_extension()
        checks.append(f"Apache AGE: {age_status}")
        # Overall status
        healthy = (
            LIGHTRAG_AVAILABLE
            and bool(gemini_key)
            and "connected" in pg_status.lower()
            and self.working_dir.exists()
            and "installed" in age_status.lower()
        )
        status = "HEALTHY" if healthy else "UNHEALTHY"
        return f"Knowledge Base Status: {status}\n" + "\n".join(
            f"  - {c}" for c in checks
        )

    def _check_age_extension(self) -> str:
        """Check if Apache AGE extension is installed."""
        try:
            import subprocess

            result = subprocess.run(
                [
                    "psql",
                    os.environ.get("POSTGRES_URI", POSTGRES_DEFAULT_URI),
                    "-t", "-A", "-c",
                    "SELECT extversion FROM pg_extension WHERE extname = 'age';",
                ],
                capture_output=True, text=True, timeout=5,
            )
            version = result.stdout.strip()
            if version:
                return f"installed (v{version})"
            return "NOT installed — run: CREATE EXTENSION age;"
        except Exception as e:
            return f"error checking: {e}"

    def _check_postgres(self) -> str:
        """Check PostgreSQL connection and pgvector extension."""
        try:
            import subprocess
            result = subprocess.run(
                ["psql", os.environ.get("POSTGRES_URI", POSTGRES_DEFAULT_URI), "-c", "SELECT 1"],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                return "connected (ada_kb)"
            return f"connection failed: {result.stderr.strip()[:100]}"
        except FileNotFoundError:
            return "psql not found — PostgreSQL not installed?"
        except Exception as e:
            return f"error: {e}"
