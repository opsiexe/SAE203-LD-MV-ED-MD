#!/bin/bash

# installer NPM
npm install --prefix frontend

# Lancer PostgreSQL
docker start pg-sae203 || docker run --name pg-sae203 \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=motdepasse123 \
  -e POSTGRES_DB=supportdb \
  -p 5433:5432 \
  -d postgres

# Attendre que le serveur PostgreSQL soit prêt
echo "⌛ Attente de PostgreSQL..."
sleep 5

# Backend Flask
pip install -r backend/requirements.txt

# Initialise la Tables
python backend/init_db.py

# Lancer le serveur Flask (en arrière-plan)
nohup flask --app backend/src/app run --host=0.0.0.0 --port=5000 &

# Frontend Vue
cd ../frontend
npm install

# Lancer le serveur Vue (en arrière-plan)
nohup npm run dev -- --host &

echo "✅ Environnement prêt sur Codespaces !"
