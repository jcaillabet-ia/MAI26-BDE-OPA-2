FROM python:3.11-slim

WORKDIR /app

# Empêcher Python de générer des fichiers .pyc
ENV PYTHONDONTWRITEBYTECODE=1

# Afficher directement les logs dans Docker
ENV PYTHONUNBUFFERED=1

# Permettre à l'API d'importer api/ et api/src/
ENV PYTHONPATH=/app:/app/src

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
