# Google Photos Discovery Engine — Interactive Research & Evidence Console

> **Part 1 Engineering Foundation — Google Photos Graduation Project**  
> **Engineering Contract:** `part1_discovery_engine_implementation_spec.md`

---

## 1. Project Anchor & Purpose

$$\mathbf{PROJECT\ ANCHOR:}\ \text{Increase the percentage of users who successfully retrieve a photo they remember but cannot precisely describe when they start searching.}$$

This repository implements **Part 1: Build an AI-Powered Discovery Engine** as an interactive software system comprising two complementary subsystems:

1. **Subsystem A — The Algorithmic Discovery Engine Core (Photo Retrieval Engine):**  
   A 7-stage deterministic retrieval pipeline (Interpretation $\rightarrow$ Signal Generation $\rightarrow$ Multi-Path Discovery $\rightarrow$ Coverage Checking $\rightarrow$ Controlled Recovery $\rightarrow$ Compositional Matching $\rightarrow$ Result Organization) that operates over photo metadata to resolve real-world user retrieval failures.
2. **Subsystem B — The Qualitative Research Evidence RAG Console (Research Intelligence System):**  
   A server-side RAG engine and exploration console indexing the empirical research corpus of **308 master records** (245 Play Store reviews, 38 Reddit discussions, 25 1:1 user interview retrieval episodes) to analyze failure modes, cross-source contradictions, and quote-backed research insights.

---

## 2. Target Architecture

```
┌────────────────────────────────┐         ┌────────────────────────────────┐
│         VERCEL (EDGE)          │  HTTPS  │        RAILWAY (PAAS)          │
│ • Next.js 14 App Router        │ ──────► │ • Python 3.11+ / FastAPI       │
│ • Interactive Research Console │  REST   │ • Uvicorn ASGI Server          │
│ • React / Vanilla CSS System   │         │ • Local Transformer Embeddings │
└────────────────────────────────┘         └────────────────────────────────┘
                                                           │
                                                           │ Internal Network
                                                           ▼
                                           ┌────────────────────────────────┐
                                           │       SUPABASE (MANAGED)       │
                                           │ • PostgreSQL 15+               │
                                           │ • pgvector (HNSW Cosine Index) │
                                           │ • Full-Text Search (tsvector)  │
                                           └────────────────────────────────┘
```

---

## 3. Repository Structure

```
d:/graduation project 3/
├── backend/                               # FastAPI / Python Application Foundation
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── endpoints/
│   │   │       │   └── health.py          # GET /api/v1/health status endpoint
│   │   │       └── router.py              # API v1 router assembly & mount points
│   │   ├── core/
│   │   │   ├── config.py                  # Pydantic Settings & environment config
│   │   │   └── logging.py                 # Structured request logger
│   │   ├── embedding/                     # Step 5: Local 384-dim embedding service (scaffold)
│   │   ├── evaluation/                    # Step 10: Parity & benchmark evaluators (scaffold)
│   │   ├── rag/                           # Step 7: Gemini RAG & quote validator (scaffold)
│   │   ├── representation/                # Step 4: Locked V2 schema & intent parser (scaffold)
│   │   ├── retrieval/                     # Step 6: 7-stage multi-path pipeline (scaffold)
│   │   ├── __init__.py
│   │   └── main.py                        # FastAPI entry point & CORS configuration
│   ├── tests/                             # Backend Test Suite
│   │   ├── fixtures/                      # Isolated benchmark handlers documentation
│   │   ├── conftest.py                    # Pytest fixtures & TestClient
│   │   └── test_health.py                 # Health check integration tests
│   ├── .env.example                       # Backend environment variable template
│   └── requirements.txt                   # Backend Python dependencies
│
├── frontend/                              # Next.js 14 App Router Development Foundation
│   ├── src/
│   │   ├── app/
│   │   │   ├── globals.css                # Pure CSS design system & tokens
│   │   │   ├── layout.tsx                 # Root layout with Google Photos styling
│   │   │   └── page.tsx                   # Local development & status dashboard
│   │   └── types/
│   │       └── discovery.ts               # Locked V2 schema & API TypeScript contracts
│   ├── .env.example                       # Frontend environment variable template
│   ├── .env.local                         # Local environment configuration
│   ├── package.json                       # Next.js & React dependencies
│   └── tsconfig.json                      # TypeScript configuration
│
├── database/                              # Supabase PostgreSQL Foundation (Step 2)
│   ├── migrations/                        # Directory for versioned SQL migrations (Step 2)
│   │   └── README.md
│   └── README.md                          # Database architecture documentation
│
├── config/                                # Declarative Configuration
│   └── ingestion_manifest.json            # 308-case corpus manifest thresholds
│
├── scripts/                               # Deployment & Ingestion Scaffolds
│   ├── ingest_evidence.py                 # Step 3: Master evidence ingestion CLI scaffold
│   └── benchmark_embeddings.py            # Step 5: Container embedding benchmark scaffold
│
├── .env.example                           # Master environment variable template
├── .gitignore                             # Git ignore rules for Python, Node, secrets
├── README.md                              # This document
│
└── [Locked Conceptual Specifications]     # Read-only reference engineering artifacts
    ├── part1_discovery_engine_implementation_spec.md
    ├── part1_memory_representation_schema_v2.md
    ├── part1_discovery_engine_architecture_final.md
    ├── part1_discovery_engine_operating_spec_final.md
    ├── part1_discovery_engine_experimental_spec.md
    ├── part1_experimental_benchmark.json
    └── part1_experiment_results.json
```

---

## 4. Prerequisites

- **Node.js:** v18.x or v20.x LTS (`node -v`, `npm -v`)
- **Python:** 3.10+ (tested with 3.14.5)
- **Git**

---

## 5. Local Setup & Installation

### Backend Setup

```bash
# 1. Install backend Python dependencies
pip install -r backend/requirements.txt

# 2. Configure environment (optional, defaults work out-of-the-box for foundation)
cp backend/.env.example backend/.env
```

### Frontend Setup

```bash
# 1. Install frontend dependencies
cd frontend
npm install

# 2. Verify local environment file
# frontend/.env.local defaults to NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

---

## 6. Running Locally

### Starting the Backend (FastAPI)

From the project root:

```bash
python -m uvicorn app.main:app --app-dir backend --reload --port 8000
```

- **API Base:** `http://localhost:8000`
- **Swagger Docs:** `http://localhost:8000/docs`
- **Health Check:** `http://localhost:8000/api/v1/health`

### Starting the Frontend (Next.js)

From the `frontend` directory:

```bash
cd frontend
npm run dev
```

- **Local Status Dashboard:** `http://localhost:3000`

---

## 7. Running Tests & Verifications

```bash
# Run backend pytest suite
python -m pytest backend/tests

# Run frontend build check (verifies TypeScript types and Next.js compilation)
npm --prefix frontend run build
```

---

## 8. Environment Variables Reference

| Variable | Target | Description | Example (Placeholders Only) |
| :--- | :--- | :--- | :--- |
| `DATABASE_URL` | Backend | Supabase connection string (Step 2) | `postgresql://postgres:[PASSWORD]@[REF].supabase.co:5432/postgres` |
| `GEMINI_API_KEY` | Backend | Google Gemini API key (Step 7) | `AIzaSy...[REDACTED]` |
| `EMBEDDING_MODEL_NAME` | Backend | Local embedding model (Pending Step 5 benchmark) | *(Empty in Step 1)* |
| `CORS_ORIGINS` | Backend | Whitelisted frontend origins | `http://localhost:3000,http://127.0.0.1:3000` |
| `NEXT_PUBLIC_API_BASE_URL` | Frontend | Backend REST API endpoint | `http://localhost:8000` |

---

## 9. Implementation Sequence

The implementation proceeds strictly across 13 sequential steps:

1. **Step 1 — Repository & Local Development Foundation** *(Active / Completed)*
2. **Step 2 — Supabase Foundation** *(Pending)*
3. **Step 3 — Evidence Ingestion (308 cases)** *(Pending)*
4. **Step 4 — V2 Representation Pipeline** *(Pending)*
5. **Step 5 — Embedding Benchmark & Model Selection** *(Pending)*
6. **Step 6 — Multi-Path Retrieval & Compositional Scoring** *(Pending)*
7. **Step 7 — Grounded RAG & Quote Validator** *(Pending)*
8. **Step 8 — Complete FastAPI Backend** *(Pending)*
9. **Step 9 — Research & Evidence Console Frontend** *(Pending)*
10. **Step 10 — Local End-to-End Validation** *(Pending)*
11. **Step 11 — Railway Deployment** *(Pending)*
12. **Step 12 — Vercel Deployment** *(Pending)*
13. **Step 13 — Production End-to-End Acceptance Test** *(Pending)*
