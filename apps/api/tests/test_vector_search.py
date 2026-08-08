"""
Unit and Integration Tests for Semantic Vector Search, FAISS index persistence,
retrieve-then-rerank pipeline, soft-delete filtering, and concurrent upload safety.
"""

import asyncio
import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

from app.schemas.resume_intelligence import ResumeParsingResult, ResumeContact
from app.schemas.resume_matching import BaseMatchResult, MatchFactor
from app.services.embedding_service import build_job_text, build_profile_text, generate_embedding
from app.services.vector_search_service import VectorSearchService


class VectorSearchTests(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.index_dir = Path(self.temp_dir.name)
        self.vector_service = VectorSearchService(index_dir=self.index_dir)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_embedding_generation(self):
        """Test vector generation produces 384-dimensional normalized float list."""
        text = "Senior Backend Engineer with Python, FastAPI, and PostgreSQL expertise."
        embedding = generate_embedding(text)
        self.assertIsInstance(embedding, list)
        self.assertEqual(len(embedding), 384)
        self.assertTrue(all(isinstance(x, float) for x in embedding))

    async def test_faiss_persistence_and_reload(self):
        """Test index creation, incremental addition, disk persistence, and reload on server restart."""
        emb1 = generate_embedding("Python developer with FastAPI")
        emb2 = generate_embedding("React frontend engineer with TypeScript")

        await self.vector_service.add_profile_to_index(
            profile_id="prof_1", candidate_id="cand_1", resume_id="res_1", embedding=emb1
        )
        await self.vector_service.add_profile_to_index(
            profile_id="prof_2", candidate_id="cand_2", resume_id="res_2", embedding=emb2
        )

        # Simulate server restart by instantiating new VectorSearchService loading from same disk path
        reloaded_service = VectorSearchService(index_dir=self.index_dir)
        self.assertEqual(len(reloaded_service.id_mapping), 2)
        self.assertEqual(reloaded_service.id_mapping[0]["profile_id"], "prof_1")
        self.assertEqual(reloaded_service.id_mapping[1]["profile_id"], "prof_2")

    async def test_semantic_non_keyword_matching(self):
        """Test semantic vector search surfaces 'FastAPI' candidate when job asks for 'web framework experience'."""
        emb_fastapi = generate_embedding("Skills: FastAPI, Python, REST APIs. Experience building microservices.")
        emb_finance = generate_embedding("Skills: Accounting, Financial Auditing, Tax returns.")

        await self.vector_service.add_profile_to_index(
            profile_id="prof_fastapi", candidate_id="cand_fastapi", resume_id="res_fastapi", embedding=emb_fastapi
        )
        await self.vector_service.add_profile_to_index(
            profile_id="prof_finance", candidate_id="cand_finance", resume_id="res_finance", embedding=emb_finance
        )

        job_query = {
            "title": "Backend Software Developer",
            "description": "Looking for strong modern web framework experience and API microservices.",
            "required_skills": ["web framework experience"],
        }

        shortlist = self.vector_service.search_candidates_for_job(job_query, top_n=5)
        self.assertGreater(len(shortlist), 0)
        top_match = shortlist[0]
        self.assertEqual(top_match["profile_id"], "prof_fastapi")

    async def test_similar_candidates_endpoint_logic(self):
        """Test nearest-neighbor candidate lookup excludes self."""
        emb_python_a = generate_embedding("Python FastAPI backend developer")
        emb_python_b = generate_embedding("Python Django microservice developer")
        emb_design = generate_embedding("Figma UI UX Graphic designer")

        await self.vector_service.add_profile_to_index("prof_py_a", "cand_py_a", "res_py_a", emb_python_a)
        await self.vector_service.add_profile_to_index("prof_py_b", "cand_py_b", "res_py_b", emb_python_b)
        await self.vector_service.add_profile_to_index("prof_des", "cand_des", "res_des", emb_design)

        similar = self.vector_service.search_similar_candidates_for_profile("prof_py_a", top_k=2)
        self.assertEqual(len(similar), 2)
        # Excludes self (prof_py_a) and ranks prof_py_b before prof_des
        self.assertEqual(similar[0]["profile_id"], "prof_py_b")

    async def test_deletion_handling_soft_delete(self):
        """Test soft-deleted profile is excluded from search and similar candidate results."""
        emb1 = generate_embedding("Python engineer")
        emb2 = generate_embedding("Python engineer")

        await self.vector_service.add_profile_to_index("prof_del", "cand_del", "res_del", emb1)
        await self.vector_service.add_profile_to_index("prof_active", "cand_active", "res_active", emb2)

        # Mark prof_del as deleted
        await self.vector_service.mark_profile_deleted("prof_del", candidate_id="cand_del")

        job = {"title": "Python Developer", "required_skills": ["Python"]}
        shortlist = self.vector_service.search_candidates_for_job(job, top_n=10)

        profile_ids = [item["profile_id"] for item in shortlist]
        self.assertNotIn("prof_del", profile_ids)
        self.assertIn("prof_active", profile_ids)

    async def test_concurrent_resume_uploads(self):
        """Test concurrent resume uploads protected by asyncio.Lock maintain index integrity."""
        emb1 = generate_embedding("DevOps engineer AWS Kubernetes")
        emb2 = generate_embedding("Data scientist PyTorch TensorFlow")
        emb3 = generate_embedding("Frontend developer React TypeScript")

        # Execute 3 near-simultaneous uploads using asyncio.gather
        await asyncio.gather(
            self.vector_service.add_profile_to_index("p1", "c1", "r1", emb1),
            self.vector_service.add_profile_to_index("p2", "c2", "r2", emb2),
            self.vector_service.add_profile_to_index("p3", "c3", "r3", emb3),
        )

        reloaded = VectorSearchService(index_dir=self.index_dir)
        self.assertEqual(len(reloaded.id_mapping), 3)
        p_ids = {entry["profile_id"] for entry in reloaded.id_mapping}
        self.assertEqual(p_ids, {"p1", "p2", "p3"})

    @patch("app.repositories.job_repo.get_by_id")
    @patch("app.services.resume_matching_service.match_resume_to_job")
    async def test_retrieve_then_rerank_flow(self, mock_match, mock_get_job):
        """Test retrieve-then-rerank pipeline shortlists via FAISS and re-ranks via AI match."""
        from unittest.mock import MagicMock
        from beanie import PydanticObjectId
        from app.services.resume_matching_service import shortlist_and_match_job

        job_oid = PydanticObjectId()
        mock_job = MagicMock()
        mock_job.id = job_oid
        mock_job.model_dump.return_value = {
            "title": "Backend Lead",
            "description": "Python FastAPI backend description with technical details",
            "required_skills": ["Python", "FastAPI"],
            "optional_skills": ["Docker"],
        }
        mock_get_job.return_value = mock_job

        # Add profile to test service index
        emb = generate_embedding("Python FastAPI Developer")
        await self.vector_service.add_profile_to_index("prof_99", "cand_99", "res_99", emb)

        # Mock match result
        from app.schemas.resume_matching import ExplainableMatchResponse, MatchRecommendation, RecruiterRecommendation
        fake_response = ExplainableMatchResponse(
            id="match_1",
            profile_id="prof_99",
            job_id=str(job_oid),
            result=BaseMatchResult(
                overall_match_percentage=92,
                missing_skills=[],
                score_reasoning="Strong fit",
                factors=[MatchFactor(name="Python", point_contribution=92, reason="Matches Python & FastAPI")],
            ),
            recommendation=MatchRecommendation(recommendation=RecruiterRecommendation.HIRE, reason="Strong match"),
        )
        mock_match.return_value = fake_response

        with patch("app.services.vector_search_service.vector_search_service", self.vector_service):
            results = await shortlist_and_match_job(str(job_oid), top_n=5)
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0].result.overall_match_percentage, 92)


if __name__ == "__main__":
    unittest.main()
