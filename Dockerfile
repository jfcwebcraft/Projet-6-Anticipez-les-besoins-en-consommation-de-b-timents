FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Copier le code de l'application
COPY . /app

# Installer dépendances (utilise requirements-notebook.txt pour simplifier)
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements-notebook.txt && \
    pip install --no-cache-dir bentoml

EXPOSE 3000

# Lancer le service BentoML
CMD ["bentoml", "serve", "service:EnergyPredictionService", "--production", "--port", "3000"]
