"""
Vector Search Service — FAISS Index Management with incremental addition,
disk persistence, soft-delete filtering, and asyncio concurrency safety.
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Any
import numpy as np

from app.core.config import settings
from app.services.embedding_service import build_job_text, generate_embedding

logger = logging.getLogger(__name__)

_FAISS_AVAILABLE = False
try:
    import faiss
    _FAISS_AVAILABLE = True
except ImportError:
    _FAISS_AVAILABLE = False


class VectorSearchService:
    """Centralized FAISS vector index engine with disk sync and soft-delete filtering."""

    def __init__(self, index_dir: Path | None = None) -> None:
        self.index_dir = index_dir or settings.VECTOR_INDEX_DIR
        self.index_path = self.index_dir / "faiss.index"
        self.mapping_path = self.index_dir / "id_mapping.json"
        self.deleted_path = self.index_dir / "deleted_ids.json"

        self.dimension = settings.EMBEDDING_DIMENSION
        self._lock = asyncio.Lock()

        # In-memory index data
        self.index: Any = None
        self.id_mapping: list[dict[str, str]] = []
        self.deleted_profile_ids: set[str] = set()
        self.deleted_candidate_ids: set[str] = set()

        # Fallback numpy matrix if FAISS package unavailable
        self._fallback_vectors: list[list[float]] = []

        self._load_index()

    def _init_empty_index() -> None:
        if _FAISS_AVAILABLE:
            self.index = faiss.IndexFlatIP(self.dimension)
        else:
            self.index = None
            self._fallback_vectors = []
        self.id_mapping = []
        self.deleted_profile_ids = set()
        self.deleted_candidate_ids = set()

    def _load_index(self) -> None:
        """Load FAISS index, mapping, and soft-deleted IDs from disk."""
        self.index_dir.mkdir(parents=True, exist_ok=True)

        # 1. Load Soft-Deleted IDs
        if self.deleted_path.exists():
            try:
                data = json.loads(self.deleted_path.read_text(encoding="utf-8"))
                self.deleted_profile_ids = set(data.get("deleted_profile_ids", []))
                self.deleted_candidate_ids = set(data.get("deleted_candidate_ids", []))
            except Exception as exc:
                logger.warning("Could not parse deleted_ids.json: %s", exc)
                self.deleted_profile_ids = set()
                self.deleted_candidate_ids = set()

        # 2. Load ID Mappings
        if self.mapping_path.exists():
            try:
                self.id_mapping = json.loads(self.mapping_path.read_text(encoding="utf-8"))
            except Exception as exc:
                logger.warning("Could not parse id_mapping.json: %s", exc)
                self.id_mapping = []

        # 3. Load FAISS Index File
        if _FAISS_AVAILABLE and self.index_path.exists():
            try:
                self.index = faiss.read_index(str(self.index_path))
                logger.info("Loaded FAISS index from disk with %d vectors", self.index.ntotal)
                return
            except Exception as exc:
                logger.warning("Could not load FAISS index file: %s. Creating new index.", exc)

        # Fallback / Initial empty index setup
        if _FAISS_AVAILABLE:
            self.index = faiss.IndexFlatIP(self.dimension)
        else:
            self.index = None

    def _save_index_unlocked(self) -> None:
        """Persist index, ID mappings, and soft-delete set to disk."""
        self.index_dir.mkdir(parents=True, exist_ok=True)

        # Save ID mapping
        self.mapping_path.write_text(json.dumps(self.id_mapping, indent=2), encoding="utf-8")

        # Save deleted IDs
        deleted_data = {
            "deleted_profile_ids": list(self.deleted_profile_ids),
            "deleted_candidate_ids": list(self.deleted_candidate_ids),
        }
        self.deleted_path.write_text(json.dumps(deleted_data, indent=2), encoding="utf-8")

        # Save FAISS index
        if _FAISS_AVAILABLE and self.index is not None:
            try:
                faiss.write_index(self.index, str(self.index_path))
                logger.info("Saved FAISS index to disk (%d items)", self.index.ntotal)
            except Exception as exc:
                logger.error("Failed to write FAISS index to disk: %s", exc)

    async def add_profile_to_index(
        self,
        profile_id: str,
        candidate_id: str,
        resume_id: str | None,
        embedding: list[float],
    ) -> None:
        """
        Incrementally add a candidate profile's embedding to FAISS index with lock protection.
        """
        async with self._lock:
            # Ensure embedding matches dimension
            vec = np.array(embedding, dtype=np.float32)
            if vec.shape[0] != self.dimension:
                logger.warning("Embedding dimension mismatch: got %d, expected %d", vec.shape[0], self.dimension)
                return

            # Normalize vector for cosine similarity
            norm = np.linalg.norm(vec)
            if norm > 0:
                vec = vec / norm
            vec = np.expand_dims(vec, axis=0)

            if _FAISS_AVAILABLE and self.index is not None:
                self.index.add(vec)
            else:
                self._fallback_vectors.append(vec.flatten().tolist())

            mapping_entry = {
                "candidate_id": str(candidate_id),
                "profile_id": str(profile_id),
                "resume_id": str(resume_id) if resume_id else "",
            }
            self.id_mapping.append(mapping_entry)

            # If profile was previously soft-deleted, unmark it
            self.deleted_profile_ids.discard(str(profile_id))

            self._save_index_unlocked()
            logger.info("Incrementally added profile %s to FAISS index", profile_id)

    async def mark_profile_deleted(self, profile_id: str, candidate_id: str | None = None) -> None:
        """
        Mark a profile as soft-deleted so vector search filters it out immediately.
        """
        async with self._lock:
            self.deleted_profile_ids.add(str(profile_id))
            if candidate_id:
                self.deleted_candidate_ids.add(str(candidate_id))

            # Save deleted IDs file
            deleted_data = {
                "deleted_profile_ids": list(self.deleted_profile_ids),
                "deleted_candidate_ids": list(self.deleted_candidate_ids),
            }
            self.deleted_path.write_text(json.dumps(deleted_data, indent=2), encoding="utf-8")
            logger.info("Marked profile %s as soft-deleted in vector index", profile_id)

    def search_candidates_for_job(
        self, job_details: dict[str, Any], top_n: int = 20
    ) -> list[dict[str, Any]]:
        """
        Perform vector similarity search for a job description against the FAISS index.
        Filters out soft-deleted profiles.
        """
        total_index_count = self.index.ntotal if (_FAISS_AVAILABLE and self.index) else len(self._fallback_vectors)
        if total_index_count == 0 or len(self.id_mapping) == 0:
            logger.info("Vector index is empty. Returning empty shortlist.")
            return []

        job_text = build_job_text(job_details)
        query_vec = generate_embedding(job_text)
        q_np = np.array([query_vec], dtype=np.float32)

        # Retrieve extra items to account for potential soft-deleted entries
        fetch_k = min(total_index_count, top_n + len(self.deleted_profile_ids) + 5)

        if _FAISS_AVAILABLE and self.index is not None:
            scores, indices = self.index.search(q_np, fetch_k)
            indices_list = indices[0].tolist()
            scores_list = scores[0].tolist()
        else:
            # Fallback cosine similarity search using numpy
            matrix = np.array(self._fallback_vectors, dtype=np.float32)
            sims = np.dot(matrix, q_np.T).flatten()
            indices_list = np.argsort(-sims)[:fetch_k].tolist()
            scores_list = [float(sims[idx]) for idx in indices_list]

        results: list[dict[str, Any]] = []
        for idx, score in zip(indices_list, scores_list):
            if idx < 0 or idx >= len(self.id_mapping):
                continue
            entry = self.id_mapping[idx]
            pid = entry["profile_id"]
            cid = entry["candidate_id"]

            # Filter out soft-deleted entries
            if pid in self.deleted_profile_ids or cid in self.deleted_candidate_ids:
                continue

            results.append({
                "candidate_id": cid,
                "profile_id": pid,
                "resume_id": entry.get("resume_id"),
                "similarity_score": round(float(score), 4),
            })
            if len(results) >= top_n:
                break

        return results

    def search_similar_candidates_for_profile(
        self, target_profile_id: str, top_k: int = 5
    ) -> list[dict[str, Any]]:
        """
        Perform vector nearest-neighbor search for a candidate profile.
        Excludes the target profile itself and soft-deleted candidates.
        """
        total_index_count = self.index.ntotal if (_FAISS_AVAILABLE and self.index) else len(self._fallback_vectors)
        if total_index_count == 0 or len(self.id_mapping) == 0:
            return []

        # Locate query profile vector in mapping
        target_idx = -1
        for idx, entry in enumerate(self.id_mapping):
            if entry["profile_id"] == target_profile_id:
                target_idx = idx
                break

        if target_idx < 0:
            logger.warning("Target profile %s not found in vector index mapping", target_profile_id)
            return []

        # Retrieve query vector
        if _FAISS_AVAILABLE and self.index is not None:
            q_np = self.index.reconstruct(target_idx).reshape(1, -1)
        else:
            q_np = np.array([self._fallback_vectors[target_idx]], dtype=np.float32)

        fetch_k = min(total_index_count, top_k + len(self.deleted_profile_ids) + 5)

        if _FAISS_AVAILABLE and self.index is not None:
            scores, indices = self.index.search(q_np, fetch_k)
            indices_list = indices[0].tolist()
            scores_list = scores[0].tolist()
        else:
            matrix = np.array(self._fallback_vectors, dtype=np.float32)
            sims = np.dot(matrix, q_np.T).flatten()
            indices_list = np.argsort(-sims)[:fetch_k].tolist()
            scores_list = [float(sims[idx]) for idx in indices_list]

        results: list[dict[str, Any]] = []
        for idx, score in zip(indices_list, scores_list):
            if idx < 0 or idx >= len(self.id_mapping):
                continue
            entry = self.id_mapping[idx]
            pid = entry["profile_id"]
            cid = entry["candidate_id"]

            # Exclude self and soft-deleted candidates
            if pid == target_profile_id or pid in self.deleted_profile_ids or cid in self.deleted_candidate_ids:
                continue

            results.append({
                "candidate_id": cid,
                "profile_id": pid,
                "resume_id": entry.get("resume_id"),
                "similarity_score": round(float(score), 4),
            })
            if len(results) >= top_k:
                break

        return results

    async def rebuild_index_from_db(self) -> int:
        """
        Full rebuild helper: loads active ResumeProfile records from MongoDB,
        purges soft-deleted sets, and writes a clean index to disk under lock.
        """
        from app.models.resume_profile import ResumeProfile

        async with self._lock:
            profiles = await ResumeProfile.find_all().to_list()
            active_profiles = [p for p in profiles if str(p.id) not in self.deleted_profile_ids]

            if _FAISS_AVAILABLE:
                self.index = faiss.IndexFlatIP(self.dimension)
            else:
                self.index = None
                self._fallback_vectors = []

            self.id_mapping = []
            self.deleted_profile_ids = set()
            self.deleted_candidate_ids = set()

            for p in active_profiles:
                emb = p.embedding
                if not emb:
                    # Generate embedding if missing
                    txt = build_job_text(p.model_dump())
                    emb = generate_embedding(txt)
                    p.embedding = emb
                    await p.save()

                vec = np.array(emb, dtype=np.float32)
                norm = np.linalg.norm(vec)
                if norm > 0:
                    vec /= norm
                vec = np.expand_dims(vec, axis=0)

                if _FAISS_AVAILABLE and self.index is not None:
                    self.index.add(vec)
                else:
                    self._fallback_vectors.append(vec.flatten().tolist())

                self.id_mapping.append({
                    "candidate_id": str(p.candidate_id),
                    "profile_id": str(p.id),
                    "resume_id": str(p.resume_id),
                })

            self._save_index_unlocked()
            logger.info("Rebuilt FAISS vector index with %d active profiles", len(active_profiles))
            return len(active_profiles)


# Singleton vector search service instance
vector_search_service = VectorSearchService()
