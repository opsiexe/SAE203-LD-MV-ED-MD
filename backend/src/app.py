from flask import Flask, render_template, request, flash, redirect, url_for, jsonify, make_response, send_from_directory, session
from flask_cors import CORS
from email.mime.text import MIMEText
import psycopg2
import smtplib
import os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'uploads')
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg',
                      'jpeg'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


def get_db_connection():
    conn = psycopg2.connect(
        dbname="supportdb",
        user="postgres",
        password="motdepasse123",
        host="localhost",
        port="5433"
    )
    return conn


app = Flask(__name__)
app.secret_key = "dev"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
CORS(app, origins=["*"])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM tickets;')
    tickets = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('index.html', tickets=tickets)


@app.route("/api/mark_finished/<int:ticket_id>", methods=["POST"])
def mark_finished(ticket_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE tickets SET statut = %s WHERE id = %s",
                ("fini", ticket_id))
    flash("Le statut a bien été changer")
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for("index"))


@app.route("/api/delete_ticket/<int:ticket_id>", methods=["POST"])
def delete_ticket(ticket_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT piece_jointe FROM tickets WHERE id = %s", (ticket_id,))
    result = cur.fetchone()
    piece_jointe = result[0] if result else None
    cur.execute("DELETE FROM tickets WHERE id = %s", (ticket_id,))
    conn.commit()
    cur.close()
    conn.close()
    if piece_jointe:
        file_path = os.path.join(UPLOAD_FOLDER, piece_jointe)
        if os.path.exists(file_path):
            os.remove(file_path)

    flash("Ticket supprimé avec succès.")
    return redirect(url_for("index"))


@app.route("/api/send_email/<int:ticket_id>", methods=["POST"])
def send_email(ticket_id):
    to_email = request.form["email"]
    message = request.form["message"]

    msg = MIMEText(message, "html")
    msg["Subject"] = "Réponse à votre ticket"
    msg["From"] = "sae203.md.ld.mv.ed@gmail.com"
    msg["To"] = to_email

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login("sae203.md.ld.mv.ed@gmail.com", "eusm wqix ojss nxdy")
            server.send_message(msg)
        flash(f"Email envoyé à {to_email}")
    except Exception as e:
        flash(f"Erreur lors de l'envoi du mail : {str(e)}")

    return redirect(url_for("index"))


@app.route("/api/mark_open/<int:ticket_id>", methods=["POST"])
def mark_open(ticket_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE tickets SET statut = %s WHERE id = %s",
                ("ouvert", ticket_id))
    flash("Le statut a bien été changer")
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for("index"))


@app.route("/api/add_ticket", methods=["POST", "OPTIONS"])
def add_ticket():
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response

    try:
        # Extraction des données du formulaire
        object = request.form.get("objet", "")
        description = request.form.get("description", "")
        email = request.form.get("email", "")
        status = request.form.get("statut", "ouvert")
        user_id = request.form.get("user_id", "1")

        # Gestion des dates
        creation_date = request.form.get("date_creation")
        modification_date = request.form.get(
            "date_modification") if request.form.get("date_modification") else None
        resolution_date = request.form.get(
            "date_resolution") if request.form.get("date_resolution") else None

        # Traitement de la pièce jointe
        attachment_path = ""
        if 'file' in request.files:
            file = request.files['file']
            if file and file.filename != '':
                if allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    import time
                    unique_filename = f"{int(time.time())}_{filename}"
                    file_path = os.path.join(
                        app.config['UPLOAD_FOLDER'], unique_filename)
                    file.save(file_path)
                    attachment_path = unique_filename
                    print(f"Fichier sauvegardé: {file_path}")
                else:
                    return jsonify({"message": f"Type de fichier non autorisé. Extensions autorisées: {', '.join(ALLOWED_EXTENSIONS)}"}), 400
        else:
            attachment_path = request.form.get("piece_jointe", "")

        print(f"Données reçues: {request.form}")
        print(f"Fichier joint: {attachment_path}")

        # Exécution de la requête SQL
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO tickets (objet, description, email, piece_jointe, statut, date_creation, date_modification, date_resolution, user_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (object, description, email, attachment_path, status,
             creation_date, modification_date, resolution_date, user_id)
        )
        conn.commit()
        cur.close()
        conn.close()

        return jsonify({
            "message": "Ticket ajouté avec succès.",
            "piece_jointe": attachment_path
        })
    except Exception as e:
        print(f"Erreur lors de l'ajout du ticket: {str(e)}")
        return jsonify({"message": f"Erreur: {str(e)}"}), 500


@app.route('/api/uploads/<filename>', methods=["GET"])
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/api/gettickets', methods=['GET', 'OPTIONS'])
def get_tickets():
    if request.method == 'OPTIONS':
        response = make_response('', 200)
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM tickets')
    rows = cur.fetchall()
    cur.close()
    conn.close()

    # Convertir les lignes en dictionnaires
    tickets = []
    for row in rows:
        ticket = {
            "id": row[0],
            "objet": row[1],
            "description": row[2],
            "email": row[3],
            "piece_jointe": row[4],
            "statut": row[5],
            "date_creation": row[6],
            "date_modification": row[7],
            "date_resolution": row[8],
            "user_id": row[9]
        }
        tickets.append(ticket)

    return jsonify(tickets)


@app.route('/api/search', methods=['GET'])
def rechercher_tickets():
    keyword = request.args.get('keyword', '').strip()
    filter_by = request.args.get('filter_by', 'objet')
    statut = request.args.get('statut', '')
    order_by = request.args.get('order_by', 'date_creation')

    # Construction dynamique de la requête SQL
    query = "SELECT * FROM tickets WHERE 1=1"
    params = []

    # Filtre par mot-clé et champ sélectionné
    if keyword:
        if filter_by == 'objet':
            query += " AND objet ILIKE %s"
        elif filter_by == 'description':
            query += " AND description ILIKE %s"
        elif filter_by == 'email':
            query += " AND email ILIKE %s"
        params.append(f"%{keyword}%")

    # Filtre par statut
    if statut:
        query += " AND statut = %s"
        params.append(statut)

    # Tri
    if order_by in ['date_creation', 'date_modification', 'date_resolution']:
        query += f" ORDER BY {order_by} DESC"
    else:
        query += " ORDER BY date_creation DESC"

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(query, params)
    tickets = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('index.html', tickets=tickets)


if __name__ == '__main__':
    app.run(debug=True)
