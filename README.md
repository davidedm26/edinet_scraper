# EDINET Scraper ETL

End-to-end scraper to download public EDINET filings (PDFs and CSVs), persist file metadata to MongoDB, and organize outputs in a portable `data/` layout.

Inspired by documentation-style READMEs like “How to Scrape Amazon Prices”, this guide walks you through prerequisites, setup, running, retrying failed companies, and where to find results.

## Prerequisites

- Docker and Docker Compose installed
- Optionally, Python 3.11+ if running locally (without Docker)

## Quick Start (Docker)

1) Clone this repository

```bash
git clone https://github.com/davidedm26/edinet_scraper.git
cd edinet_scraper
```

2) Build and start services

```bash
docker-compose build etl
docker-compose up -d mongodb etl
```

3) Run the pipeline inside the ETL container

```bash
docker-compose exec etl python src/pipeline.py
```

This will:
- Generate/update the EDINET code list
- Populate the `companies` collection
- Process pending companies, downloading PDFs and CSVs, and saving metadata

## Running Locally (without Docker)

1) Create and activate a Python 3.11 environment

```bash
python -m venv .venv
.venv\Scripts\activate
```

2) Install dependencies

```bash
pip install -r requirements.txt
```

3) Start MongoDB (locally) or set `MONGO_URI`

```bash
set MONGO_URI=mongodb://localhost:27017
```

4) Run the pipeline

```bash
python src/pipeline.py
```

## Retrying Failed Companies (simple mode)

If some companies ended with status `error`, you can do a one-shot retry with a max attempts limit. Inside the container or locally:

```bash
python -c "from src.pipeline import retry_error_companies; retry_error_companies(max_attempts=3)"
```

Behavior:
- Companies in `error` get an `attempts` counter. On success (`done`), the `attempts` field is removed.
- Companies reaching the max attempts can be marked as `failed` (not retried further), depending on your settings.

## Data & Metadata

- Files are stored under `data/<EDINET_CODE>/<pdf|csv>/<DOCUMENT_TYPE>/...`
- File metadata is stored in MongoDB `files` collection with a unique index on `(document_name, file_type, edinet_code)`
- Companies and their processing status live in the `companies` collection

## Configuration

- `MONGO_URI` (env): MongoDB connection string
- Concurrency & limits are defined in `src/utils/scraper.py` and `src/pipeline.py`

## Troubleshooting

- “Connection refused” to MongoDB: ensure `mongodb` service is up: `docker-compose ps`
- Empty folders on failed downloads: worker logic creates directories lazily only when writing files
- Cursor timeouts or long runs: processing works in snapshots and uses simple retries

## Notes

- Downloaded files will be available in the `data/` folder.
- MongoDB runs via Docker Compose by default; override `MONGO_URI` if you run your own instance.

---

If you have questions or ideas, open an issue or PR in this repository.
