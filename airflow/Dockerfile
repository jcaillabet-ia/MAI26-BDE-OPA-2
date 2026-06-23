FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

ENV AIRFLOW_HOME=/app

RUN airflow config list --defaults > "${AIRFLOW_HOME}/airflow.cfg"