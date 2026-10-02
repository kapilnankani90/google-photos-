# Database Migrations

**Implementation Status: Active (Step 2 — Supabase Foundation)**

This directory contains version-controlled database migrations:
- `001_initial_schema.sql`: Initial schema defining the 9 approved core tables, PostgreSQL extensions (`uuid-ossp`, `vector`), 384-dimensional vector column with HNSW index, English tsvector FTS column with GIN index, and referential constraints.
