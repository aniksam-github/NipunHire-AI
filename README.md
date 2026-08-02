<div align="center">

# 🚀 NipunHire AI
### *Autonomous Explainable AI Hiring, Candidate Evaluation & Research Platform*

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg?style=for-the-badge&logo=apache)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.14-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev)
[![MongoDB](https://img.shields.io/badge/MongoDB-8.3-47A248?style=for-the-badge&logo=mongodb&logoColor=white)](https://mongodb.com)

---

[✨ Overview](#-overview) •
[🏗️ Architecture](#️-architecture) •
[⚡ Platform Modules](#-platform-modules) •
[🚀 Quick Start](#-quick-start) •
[📊 API Modules](#-api-modules) •
[🔬 Research & Ethics](#-research--ethics) •
[⚠️ Known Limitations](#️-known-limitations) •
[🗺️ Roadmap](#️-roadmap)

---

</div>

## 📌 Overview

**NipunHire AI** is an enterprise-grade, full-stack recruitment and candidate intelligence platform powered by transparent, audit-ready AI models. It bridges candidate career acceleration with recruiter decision support by replacing opaque black-box AI scores with **auditable factor contributions, mathematical reconciliation, and ethical human-in-the-loop disclaimers**.

```
📄 PDF Resume Processing  ──▶  🎯 Factor Match & Screening  ──▶  🎙️ Adaptive AI Interview
                                                                       │
🔬 Process Bias & Fraud Audit  ◀──  📊 Recruiter Ranking & Decision ◀──  💻 Static Code Review
```

> [!IMPORTANT]
> **Human-in-the-Loop AI Directive**: All AI outputs across NipunHire AI—from match percentages to interview cheat risk flags—are decision-support signals designed for human evaluation. Automated systems never issue final employment decisions or candidate rejections independently.

---

## 🏗️ Architecture

```mermaid
flowchart TD
    subgraph Client ["Client Presentation Layer (React 19 + TypeScript + Tailwind)"]
        UI[Single Page Web Application]
        State[TanStack Query + Zustand]
    end

    subgraph API ["API & Dependency Layer (FastAPI + Async Python 3.14)"]
        Router[REST API Routers /api/v1]
        Auth[JWT OAuth2 Security & RBAC]
        GlobalExc[Global Exception Handlers]
    end

    subgraph Service ["Domain Logic & AI Core"]
        Services[Service Layer]
        AIService[Centralized AIService + Retries]
        AuditService[Audit Log Append-Only Engine]
        Prompts[Prompt Template Loader]
    end

    subgraph Data ["Persistence & Extraction"]
        Motor[Async Motor Client + Beanie ODM]
        PyMuPDF[PyMuPDF PDF Text Extractor]
        DB[(MongoDB 8.3 Document Database)]
    end

    UI -->|REST + JWT Bearer| Router
    Router --> Auth
    Auth --> GlobalExc
    GlobalExc --> Services
    Services --> AIService
    Services --> AuditService
    AIService --> Prompts
    AIService -->|Structured JSON Responses| OpenAI[OpenAI GPT API]
    Services --> PyMuPDF
    Services --> Motor
    AuditService --> Motor
    Motor --> DB
```

---

## ⚡ Platform Modules

<details open>
<summary><b>📄 Phase 1–3: Resume Intelligence & ATS Compatibility</b></summary>
<br>

* 📥 **PDF Resume Ingestion**: Validated 5 MB PDF uploads with local storage and PyMuPDF text extraction.
* 🧠 **OpenAI Schema-Validated Parsing**: Converts unformatted resume text into structured candidate profile entities.
* 🔍 **AI Screening & ATS Feedback**: Evaluates strengths, weaknesses, category skills, and actionable improvement recommendations.
* 📜 **Resume History & Management**: Full retrieval, profile update, and soft/hard deletion workflows.

</details>

<details open>
<summary><b>🎯 Phase 4–5: Explainable Job Matching & Candidate Intelligence</b></summary>
<br>

* ⚖️ **Explainable Factor Matching**: Reconciles individual named point contributions strictly to sum to the overall match score percentage.
* 🤖 **Deterministic Recommendations**: Generates `Hire`, `Maybe`, or `Reject` candidate signals based on reconciled factor arithmetic.
* 📈 **AI Career Plans & Guidance**: Tailored career growth blueprints grounded in existing candidate profile data.
* 📝 **Review-Only ATS & Resume Rewrites**: Review-only optimization suggestions retaining original submitted text for side-by-side comparison.

</details>

<details open>
<summary><b>🎙️ Phase 6: Adaptive AI Interview Simulation</b></summary>
<br>

* 🔄 **Stateful Multi-Turn Sessions**: Tracks question history, difficulty levels, candidate turns, and session lifecycle (`in_progress`, `ready_to_complete`, `completed`, `abandoned`).
* 📊 **5-Dimension Turn Evaluation**: Scores technical correctness, communication clarity, problem-solving depth, behavioral alignment, and experience relevance per turn.
* 🔐 **Ownership Authorization**: Enforces candidate ownership checks (unauthorized access returns `404 Not Found` to prevent resource probing).
* 🎯 **Benchmark Comparisons**: Aggregates final reports with ideal answer comparisons and overall performance scores.

</details>

<details open>
<summary><b>💻 Phase 7: Coding AI & Static Code Review</b></summary>
<br>

* 🧩 **AI Question Generation**: Generates problem statements, input/output constraints, test cases, and starter code tailored to job technologies and difficulty levels.
* 🛡️ **Static Code Review (No Sandbox Execution)**: Analyzes submitted plain-text code for correctness, edge cases, Big-O time complexity, space complexity, and code quality.
* ⚠️ **Syntax Validity Checks**: Detects incomplete snippets or syntax defects, flagging `is_incomplete_or_invalid: true` rather than guessing execution outcomes.
* 📋 **Consolidated Feedback View**: Unifies question specification, candidate source code, and AI review analysis in a single endpoint.

</details>

<details open>
<summary><b>📊 Phase 8: Recruiter AI & Decision Support</b></summary>
<br>

* 📝 **Candidate Summary Reports**: Synthesizes multi-phase evaluations (resume match, interview report, coding review) into recruiter-facing executive summaries.
* 🔀 **Side-by-Side Candidate Comparison**: Generates side-by-side matrices ranking relative strengths and dimension leaders across candidate pools.
* 🔢 **Deterministic Candidate Ranking**: Ranks candidates using configurable sub-score weights (`match_weight`, `interview_weight`, `coding_weight`) with dynamic weight normalization for missing evaluations.
* ✍️ **AI Rank Justifications**: Generates concise natural language justifications per rank position based on computed scores.
* 💡 **Aggregate Hiring Recommendations**: Formulates final `Hire`, `Maybe`, or `Reject` decisions with grounded reasoning.
* 📑 **Job Description Generator**: Auto-generates structured job descriptions (summary, responsibilities, required and preferred qualifications) from role titles and skills.

</details>

<details open>
<summary><b>🔬 Phase 9: Research Features & Ethics Auditing</b></summary>
<br>

* 🔍 **Unified Explanation Traces**: Consolidates match factor breakdowns, interview dimensions, and coding reviews into a single trace with deterministic cross-phase consistency metrics.
* 🛡️ **Statistical Process Bias Auditing**: Calculates score distributions (mean, median, std dev, min/max), high variance flags, and single-factor rejection dominance across applicant pools. **Contains ZERO protected demographic attribute collection or profiling.**
* ⚠️ **Resume Internal Consistency Audit**: Checks stated resume text for timeline overlaps, unsupported skill claims, and date contradictions.
* 🕵️ **Interview Stylometric Cheat Risk Detection**: Analyzes Q&A history for phrasing shifts and unnatural polish. Informational-only; never auto-disqualifies candidates.
* ⚖️ **Mandatory Ethical Disclaimers**: Every research response includes a non-empty `human_review_disclaimer` field framing outputs as decision-support signals.

</details>

<details open>
<summary><b>🔒 Production Readiness & Audit Trail</b></summary>
<br>

* 🛡️ **RateLimiterMiddleware**: Sliding-window rate limiter tracking requests per IP to protect auth & expensive AI routes.
* 📜 **Immutable Append-Only Audit Trail**: Automatically records recruiter hiring recommendations, candidate status changes, and process bias audit queries.

</details>

---

## 🛠️ Tech Stack

| Domain | Tooling & Frameworks | Description |
| :--- | :--- | :--- |
| **Backend Core** | ![Python](https://img.shields.io/badge/Python-3.14-3776AB?style=flat-square&logo=python&logoColor=white) ![FastAPI](https://img.shields.io/badge/FastAPI-Latest-009688?style=flat-square&logo=fastapi&logoColor=white) ![Pydantic](https://img.shields.io/badge/Pydantic-v2-E92063?style=flat-square) | High-performance asynchronous REST API and strict schema validation |
| **Database** | ![MongoDB](https://img.shields.io/badge/MongoDB-8.3-47A248?style=flat-square&logo=mongodb&logoColor=white) ![Beanie](https://img.shields.io/badge/Beanie-ODM-blue?style=flat-square) | Async Motor MongoDB client with Beanie ODM document models |
| **AI Foundation** | ![OpenAI](https://img.shields.io/badge/OpenAI-API-412991?style=flat-square&logo=openai&logoColor=white) PyMuPDF | Structured JSON response parsing, prompt loader, and PDF text extraction |
| **Frontend UI** | ![React](https://img.shields.io/badge/React-19-61DAFB?style=flat-square&logo=react&logoColor=black) ![TypeScript](https://img.shields.io/badge/TypeScript-5.0-3178C6?style=flat-square&logo=typescript&logoColor=white) ![Vite](https://img.shields.io/badge/Vite-6.0-646CFF?style=flat-square&logo=vite&logoColor=white) | Modern SPA frontend with TanStack React Query & Zustand state management |
| **Styling & UI** | ![Tailwind](https://img.shields.io/badge/Tailwind_CSS-v3-06B6D4?style=flat-square&logo=tailwindcss&logoColor=white) Lucide React Sonner | Glassmorphism UI components, dynamic icons, and toast notifications |

---

## 🚀 Quick Start

### Prerequisites

* **Python 3.14+**
* **Node.js 20+** and `npm`
* **MongoDB** (Local instance or MongoDB Atlas)
* **OpenAI API Key**

### Step 1: Clone Repository

```bash
git clone https://github.com/aniksam-github/NipunHire-AI.git
cd NipunHire-AI
```

### Step 2: Backend Setup

```bash
# Create and activate virtual environment
python -m venv .venv

# Windows PowerShell
.venv\Scripts\Activate.ps1
# Linux/macOS
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp backend/.env.example backend/.env
```

Configure `backend/.env`:
```env
MONGODB_URI=mongodb://localhost:27017
DATABASE_NAME=nipunhire_db
JWT_SECRET=your-super-secret-jwt-key
OPENAI_API_KEY=sk-proj-your-openai-api-key
OPENAI_MODEL=gpt-4o-mini
```

Start Backend Server:
```bash
cd backend
uvicorn app.main:app --reload
```
Backend API will run live at `http://localhost:8000`.

### Step 3: Frontend Setup

```bash
cd ../frontend
npm install
cp .env.example .env
npm run dev
```
Frontend development server will run live at `http://localhost:5173`.

---

## 📊 API Modules

FastAPI automatically generates interactive API documentation:
* **Swagger UI**: [`http://localhost:8000/docs`](http://localhost:8000/docs)
* **ReDoc**: [`http://localhost:8000/redoc`](http://localhost:8000/redoc)

| Module | Base Path | Key Features | Auth Guard |
| :--- | :--- | :--- | :---: |
| **Auth** | `/api/v1/auth` | Login, registration, JWT token refresh | Public |
| **Jobs** | `/api/v1/jobs` | Job post creation, listing, updates, deletion | Authenticated |
| **Resumes** | `/api/v1/resumes` | PDF upload, PyMuPDF text extraction, AI screening | Authenticated |
| **Matching** | `/api/v1/matching` | Explainable factor matching & point contribution audit | Authenticated |
| **Interviews** | `/api/v1/interviews` | Multi-turn adaptive interviews, difficulty shifts, reports | Authenticated |
| **Coding** | `/api/v1/coding` | Challenge generation, plain-text code submission, static AI review | Authenticated |
| **Recruiter AI** | `/api/v1/recruiter` | Candidate summary, side-by-side comparison, candidate ranking | Recruiter / Admin |
| **Research** | `/api/v1/research` | Explanation traces, statistical process bias audits, cheat risk checks | Recruiter / Admin |
| **Audit Logs** | `/api/v1/audit-logs` | Read-only append-only audit trail for candidate/job decisions | Recruiter / Admin |

---

## 🔬 Research & Ethics

The `research data/` directory contains foundational literature and design specifications driving NipunHire AI's algorithmic transparency.

### **Core Academic Contributions**:
1. **Explainable Point Reconciliation**: Point contributions of individual match factors are mathematically constrained to sum exactly to overall match percentages.
2. **Process Audit vs Demographic Profiling**: Evaluates score variance ($\sigma^2$) and single-factor dominance across candidate pools **without collecting, inferring, or storing protected demographic attributes (race, gender, age, etc.)**.
3. **Internal Consistency Audits**: Evaluates timeline logic and stated claim internal consistency without claiming external background check verification.
4. **Human-in-the-Loop Disclaimers**: Every response schema in Phase 9 includes explicit non-empty `human_review_disclaimer` fields confirming that AI outputs are advisory signals.

---

## ⚠️ Known Limitations

1. **Rate Limiter Storage**: The default `RateLimiterMiddleware` uses process-local in-memory state (`self._history`). In multi-worker deployments (e.g. `uvicorn main:app --workers 4`) or multi-container Kubernetes replicas, rate limits are enforced per-worker rather than globally. A Redis-backed rate limiter (e.g., using `redis-py` or `limits`) is the recommended production upgrade for horizontally scaled environments.
2. **Audit Log Immutability Enforcement**: Audit log immutability is enforced at the **application layer** (the system exposes zero update, patch, or delete HTTP endpoints or repository methods). However, this is not enforced at the database storage engine layer—direct database access or administrative MongoDB commands could still alter or delete records.

---

## 📜 License

Distributed under the **Apache License 2.0**. See [`LICENSE`](LICENSE) for details.
