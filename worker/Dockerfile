# ─────────────────────────────────────────────────────────────
#  Jino Café — Background Worker Dockerfile (Azure Container Apps)
# ─────────────────────────────────────────────────────────────
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy worker application
COPY . .

# Run worker loop
CMD ["python", "app/main.py"]
