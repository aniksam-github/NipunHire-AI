"""
Elasticsearch integration module for full-text candidate resume search,
fuzzy skill matching, and BM25 relevance scoring.
"""

import logging
from typing import Any, Dict, List, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

try:
    from elasticsearch import AsyncElasticsearch
    HAS_ELASTICSEARCH = True
except ImportError:
    AsyncElasticsearch = Any
    HAS_ELASTICSEARCH = False

es_client: Optional[Any] = None
INDEX_NAME = "nipunhire_candidate_resumes"


async def init_elasticsearch() -> Optional[Any]:
    """Initialize AsyncElasticsearch client connection and candidate resume index."""
    global es_client
    if not HAS_ELASTICSEARCH:
        logger.info("Elasticsearch package not available — full-text search fallback active.")
        es_client = None
        return None

    try:
        es_client = AsyncElasticsearch(
            settings.ELASTICSEARCH_URL,
            request_timeout=5,
            max_retries=2,
            retry_on_timeout=True
        )

        # Create candidate resumes index if it does not exist
        if not await es_client.indices.exists(index=INDEX_NAME):
            await es_client.indices.create(
                index=INDEX_NAME,
                mappings={
                    "properties": {
                        "candidate_id": {"type": "keyword"},
                        "candidate_name": {"type": "text"},
                        "headline": {"type": "text", "analyzer": "standard"},
                        "resume_text": {"type": "text", "analyzer": "standard"},
                        "skills": {"type": "keyword"},
                        "experience_years": {"type": "float"},
                        "created_at": {"type": "date"}
                    }
                }
            )
            logger.info(f"Created Elasticsearch index: {INDEX_NAME}")
        else:
            logger.info(f"Connected to existing Elasticsearch index: {INDEX_NAME}")

        return es_client
    except Exception as e:
        logger.warning(f"Elasticsearch unavailable (falling back to DB search): {e}")
        es_client = None
        return None


async def close_elasticsearch() -> None:
    """Close AsyncElasticsearch client connection on app shutdown."""
    global es_client
    if es_client is not None:
        await es_client.close()
        logger.info("Closed Elasticsearch connection.")
        es_client = None


async def index_candidate_resume(
    candidate_id: str,
    candidate_name: str,
    headline: str,
    resume_text: str,
    skills: List[str],
    experience_years: float = 0.0
) -> bool:
    """Index candidate resume text & metadata into Elasticsearch."""
    if not es_client:
        return False

    try:
        document = {
            "candidate_id": candidate_id,
            "candidate_name": candidate_name,
            "headline": headline,
            "resume_text": resume_text,
            "skills": skills,
            "experience_years": experience_years,
        }
        await es_client.index(index=INDEX_NAME, id=candidate_id, document=document)
        return True
    except Exception as e:
        logger.error(f"Failed to index candidate resume {candidate_id} in Elasticsearch: {e}")
        return False


async def search_candidates_es(query_text: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Full-text fuzzy candidate search using BM25 relevance scoring.
    Searches across headline, skills, and resume_text fields.
    """
    if not es_client:
        return []

    try:
        response = await es_client.search(
            index=INDEX_NAME,
            query={
                "multi_match": {
                    "query": query_text,
                    "fields": ["headline^3", "skills^2", "resume_text"],
                    "fuzziness": "AUTO",
                    "prefix_length": 2
                }
            },
            size=limit
        )

        results = []
        for hit in response["hits"]["hits"]:
            item = hit["_source"]
            item["_score"] = hit["_score"]
            results.append(item)

        return results
    except Exception as e:
        logger.error(f"Elasticsearch query failed for '{query_text}': {e}")
        return []
