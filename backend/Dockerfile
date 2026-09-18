FROM python:3.11-slim

WORKDIR /app/backend

# Install system dependencies required for building some python packages (like psycopg)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source and frontend assets used by the FastAPI app
COPY backend/ .
COPY frontend/ /app/frontend/

# Run database migrations before starting the API. Render provides the PORT
# environment variable at runtime.
CMD ["sh", "-c", "alembic -c alembic/alembic.ini upgrade head && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
