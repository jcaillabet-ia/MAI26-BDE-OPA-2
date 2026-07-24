# Projet CryptoBot

## Préparation du projet

Renommer le fichier .env.example en .env, et ajouter à l'intérieur la clé

```
COINGECKO_API_KEY=...
```

## Lancement du projet

```bash
docker compose up
```

### Préparation des données

Accéder à la doc de FastAPI avec l'URL

```
http://localhost:8000/docs
```

Et exécuter la route **/admin/postgres/fill**

## Lancement des tests

```bash
docker compose run --rm tests
```