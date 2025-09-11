# EDINET Scraper – Development Journey

This document summarizes the evolution of the project from initial exploration to a stable, restartable ETL pipeline.

## 1. Reverse Engineering
Observed how the public portal behaved, identified the need to replicate search and file retrieval flows, and understood how to utilize hashing and session mechanisms for authenticated access and efficient data retrieval.

## 2. Prototype
Built a thin script: single company search, one document fetch (PDF / CSV) and basic file saving.

## 3. Core Extraction Engine
Generalized search over all documents for a company, added pagination aggregation and simple deduplication, introduced parallel downloads for I/O efficiency, and standardized metadata representation.

## 4. Persistence & State
Introduced MongoDB collections for companies (processing status) and files (metadata). Added unique constraints to guarantee idempotence, plus status transitions enabling safe resume after interruption.

## 5. Containerization (Docker)
Added Docker setup: `Dockerfile` for a reproducible image (deps + code) and `docker-compose.yml` to run scraper + MongoDB together. Defined env vars (e.g. `MONGO_URI`), bind‑mounted `data/` for persistence, internal network for stable communication. Goal: one‑command onboarding and environment isolation.

## 6. Operational Hardening
Added retries for failed companies search, lightweight attempt tracking, unified paths for portability and environment‑driven configuration.

## 7. Documentation & Statistics
Expanded README (background, setup paths, stats usage). Added aggregated statistics export (JSON) for monitoring throughput and error distribution. 

## 8. Outcomes
- From ad‑hoc scraping to a maintainable ETL core
- Stable directory + metadata layout
- Controlled retries vs silent failures
- Single command bootstrap (Docker or local) + JSON stats for reporting
