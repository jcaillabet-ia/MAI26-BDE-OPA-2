FROM python:3.11-slim

WORKDIR /app

# Empêcher Python de générer des fichiers .pyc
ENV PYTHONDONTWRITEBYTECODE=1
# Empêcher Python de mettre en mémoire tampon la sortie standard
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
