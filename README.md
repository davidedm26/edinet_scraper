# edinet_scraper

PDF and CSV files scraper for the EDINET JPN website.

## Environment Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/davidedm26/edinet_scraper.git
   cd edinet_scraper
   ```

2. **Build the Docker image**
   ```bash
   docker-compose build etl
   ```

3. **Start the ETL service**
   ```bash
   docker-compose up -d etl
   ```

4. **Run the pipeline from the container**
    ```bash
    docker-compose exec etl python src/pipeline.py
    ```

## Notes

- Make sure Docker and Docker Compose are installed.
- Downloaded files will be available in the `data/` folder.
- MongoDB is managed automatically via Docker Compose.

For usage details and configuration, see
