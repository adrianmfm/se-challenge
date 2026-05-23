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

# Run migrations then start the server
CMD alembic upgrade head && \
    uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}
