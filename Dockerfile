FROM python:3.12-slim

WORKDIR /app

# Install system dependencies for psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first (better layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY alembic/ alembic/
COPY alembic.ini .
COPY app/ app/
COPY tests/ tests/
COPY pytest.ini .
COPY start.sh .
RUN chmod +x start.sh

CMD ["./start.sh"]
