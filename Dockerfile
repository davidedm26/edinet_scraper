# Base Python
FROM python:3.11-slim

# Install dependencies di sistema per Chromium
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Cartella di lavoro
WORKDIR /app

# Copia requirements e installa dipendenze Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia il codice
COPY src/ ./src/

# Imposta variabili ambiente per Selenium/Chromium headless
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROME_DRIVER=/usr/bin/chromedriver

# Comando di default
CMD ["python", "src/pipeline.py"]