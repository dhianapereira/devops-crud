# ===== STAGE 1: builder =====
FROM python:3.12-alpine AS builder

# Install system dependencies required for psycopg2
RUN apk add --no-cache gcc musl-dev linux-headers postgresql-dev

WORKDIR /app

COPY requirements.txt .

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install --upgrade pip && pip install -r requirements.txt

# ===== STAGE 2: runtime =====
FROM python:3.12-alpine

RUN apk add --no-cache postgresql-libs

# Copy Python environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app

COPY app ./app

# Default environment variables
ENV FLASK_APP=app/main.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5000

EXPOSE 5000

CMD ["python", "-m", "app.main"]
