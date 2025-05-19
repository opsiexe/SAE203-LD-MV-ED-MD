import psycopg2

connection = psycopg2.connect(
    dbname="supportdb",
    user="postgres",
    password="motdepasse123",
    host="localhost",
    port="5433"
)

cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS tickets (
    id SERIAL PRIMARY KEY,
    objet TEXT NOT NULL,
    description TEXT NOT NULL,
    email TEXT NOT NULL,
    piece_jointe TEXT,
    statut TEXT DEFAULT 'Nouveau',
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_modification TIMESTAMP,
    date_resolution TIMESTAMP,
    user_id INTEGER NOT NULL, -- réservé AzureAD
    technicien_id INTEGER, -- <--- nouveau champ pour l'attribution
    comentaire TEXT
);
CREATE TABLE IF NOT EXISTS technicien(
    id SERIAL PRIMARY KEY,
    nom TEXT NOT NULL,
    prenom TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS messages(
    id SERIAL PRIMARY KEY,
    ticket_id INTEGER REFERENCES tickets(id),
    sender VARCHAR(255),
    content TEXT,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

connection.commit()
cursor.close()
connection.close()

print("✅ Base de données initialisée avec succès !")
