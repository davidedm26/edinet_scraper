# EDINET Scraper ETL

## Background
EDINET is the Japanese Financial Services Agency’s electronic disclosure system where all publicly listed Japanese companies publish regulated filings and disclosures. Reliable access to, and processing of, this data is crucial for analytical, compliance, and research applications.

End-to-end scraper to download public EDINET filings (PDFs and CSVs), persist file metadata to MongoDB, and organize outputs in a portable `data/` layout.

This guide walks you through prerequisites, setup, running, retrying failed companies, and where to find results.

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
- Populate/update the `companies` collection 
- Process pending companies, downloading PDFs and CSVs, and saving metadata

## Running Locally (without Docker)
> **Note:** MongoDB runs via Docker Compose by default; you must start your own MongoDB instance and override `MONGO_URI`.


1) Create and activate a Python 3.11 environment

```bash
python -m venv .venv
.venv\Scripts\activate
```

2) Install dependencies

```bash
pip install -r requirements.txt
```

3) Start your MongoDB instance and set `MONGO_URI` 

```bash
set MONGO_URI=mongodb://localhost:27017
```

4) Run the pipeline

```bash
python src/pipeline.py
```

## Data & Metadata

- Files are stored under `data/<EDINET_CODE>/<pdf|csv>/<DOCUMENT_TYPE>/...`
- File metadata is stored in MongoDB `files` collection with a unique index on `(document_name, file_type, edinet_code)`
- Companies and their processing status live in the `companies` collection


## Troubleshooting

- “Connection refused” to MongoDB: ensure `mongodb` service is up: `docker-compose ps`
- Empty folders on failed downloads: worker logic creates directories lazily only when writing files
- Cursor timeouts or long runs: processing works in snapshots and uses simple retries

## Notes

- Downloaded files will be available in the `data/` folder.


