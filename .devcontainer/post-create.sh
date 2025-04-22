npm install --prefix frontend
docker start pg-sae203 || docker run --name pg-sae203 \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=motdepasse123 \
  -e POSTGRES_DB=supportdb \
  -p 5433:5432 \
  -d postgres
echo "⌛ Attente de PostgreSQL..."
sleep 5
pip install -r backend/requirements.txt
python backend/init_db.py
nohup flask --app backend/src/app run --host=0.0.0.0 --port=5000 &
cd frontend
npm install
cd ..
nohup npm run dev --prefix frontend &
echo "✅ Environnement prêt sur Codespaces !"
