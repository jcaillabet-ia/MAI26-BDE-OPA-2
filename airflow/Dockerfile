FROM python:3.11-slim

WORKDIR /app

# Empêcher Python de générer des fichiers .pyc
ENV PYTHONDONTWRITEBYTECODE=1
# Empêcher Python de mettre en mémoire tampon la sortie standard
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Par défaut, maintenir le conteneur en vie pour pouvoir y lancer des scripts
CMD ["tail", "-f", "/dev/null"]
