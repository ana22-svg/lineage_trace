FROM python:3.11-slim

WORKDIR /app/backend

# Install system dependencies required for building some python packages (like psycopg)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

ENV MALLOC_ARENA_MAX=2 \
    OMP_NUM_THREADS=1 \
    TOKENIZERS_PARALLELISM=false \
    HF_HUB_DISABLE_SYMLINKS_WARNING=1 \
    PYTHONUNBUFFERED=1

# Install Python requirements
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download and cache embedding model during build so no RAM spikes occur at runtime
RUN python -c "from fastembed import TextEmbedding; list(TextEmbedding(model_name='sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2').embed(['init']))"

# Copy backend source and frontend assets used by the FastAPI app
COPY backend/ .
COPY frontend/ /app/frontend/

# Run database migrations before starting the API.
CMD ["sh", "-c", "alembic -c alembic/alembic.ini upgrade head && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
