#!/bin/bash

# Lancer PostgreSQL
docker start pg-sae203 || docker run --name pg-sae203 \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=motdepasse123 \
  -e POSTGRES_DB=supportdb \
  -p 5433:5432 \
  -d postgres

# Backend Flask
cd backend
pip install -r requirements.txt

# Lancer le serveur Flask (en arrière-plan)
nohup python ./src/app.py & 

# Frontend Vue
cd ../frontend
npm install
# Lancer le serveur Vue (en arrière-plan)
nohup npm run dev -- --host &

echo "✅ Environnement prêt sur Codespaces !"
