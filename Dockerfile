# Dockerfile for FastAPI + async SQLAlchemy + Supabase + Google Cloud Storage (venv-based dev)
FROM python:3.11-slim

# Set workdir
WORKDIR /app

RUN useradd -m appuser
USER appuser

# Install system dependencies
RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

# Copy requirements (generate if not present)
COPY requirements.txt ./

RUN pip install --upgrade pip

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Expose FastAPI port
EXPOSE 8000

# Set environment variables (override in production)
ENV PYTHONUNBUFFERED=1

# Run the app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "${PORT}"]

