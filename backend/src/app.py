# ==========================
# IMPORTS
# ==========================
import os
import re
import datetime
import email
import imaplib
import smtplib
import psycopg2
from email.mime.text import MIMEText
from flask import (
    Flask, render_template, request, flash, redirect, url_for,
    jsonify, make_response, send_from_directory, session,
    render_template_string
)
from flask_cors import CORS
from werkzeug.utils import secure_filename

# ==========================
# PARAMÈTRES CONFIGURABLES
# ==========================
DB_CONFIG = {
    "dbname": "supportdb",
    "user": "postgres",
    "password": "motdepasse123",  # À modifier !
    "host": "localhost",
    "port": "5433"
}

EMAIL_CONFIG = {
    "address": "sae203.md.ld.mv.ed@gmail.com",  # À modifier !
    "password": "eusm wqix ojss nxdy",          # À modifier !
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "imap_server": "imap.gmail.com"
}

UPLOAD_FOLDER = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'uploads'
)
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg'}

# ==========================
# INITIALISATION APP FLASK
# ==========================
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app = Flask(__name__)
app.secret_key = "dev"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
CORS(app, origins=["*"])

# ==========================
# FONCTIONS UTILITAIRES
# ==========================


def get_db_connection():
    """Connexion à la base de données PostgreSQL."""
    return psycopg2.connect(**DB_CONFIG)


def allowed_file(filename):
    """Vérifie si l'extension du fichier est autorisée."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def clean_email_body(body):
    """Nettoie le corps d'un email (supprime signatures/citations)."""
    lines = body.splitlines()
    cleaned = []
    for line in lines:
        if line.strip().startswith('--'):
            break
        if re.match(r'^(Le|On|From:|De :|>|\s*>).*', line):
            continue
        cleaned.append(line)
    return '\n'.join([l for l in cleaned]).strip()


def get_last_message_headers(ticket_email):
    """Récupère les en-têtes du dernier mail reçu d'un client."""
    try:
        mail = imaplib.IMAP4_SSL(EMAIL_CONFIG["imap_server"])
        mail.login(EMAIL_CONFIG["address"], EMAIL_CONFIG["password"])
        mail.select("inbox")
        status, data = mail.search(None, f'FROM "{ticket_email}"')
        mail_ids = data[0].split()
        if not mail_ids:
            return None, None, None
        latest_id = mail_ids[-1]
        status, msg_data = mail.fetch(latest_id, "(RFC822)")
        msg = email.message_from_bytes(msg_data[0][1])
        message_id = msg.get("Message-ID")
        references = msg.get("References") or message_id
        return message_id, references, msg.get("Subject")
    except Exception as e:
        print(f"Erreur IMAP (headers): {e}")
        return None, None, None


def sync_client_emails():
    """Synchronise les emails clients et les stocke dans la base."""
    try:
        mail = imaplib.IMAP4_SSL(EMAIL_CONFIG["imap_server"])
        mail.login(EMAIL_CONFIG["address"], EMAIL_CONFIG["password"])
        mail.select("inbox")
        status, data = mail.search(None, 'ALL')
        mail_ids = data[0].split()
        conn = get_db_connection()
        cur = conn.cursor()
        for mail_id in mail_ids:
            status, msg_data = mail.fetch(mail_id, "(RFC822)")
            msg = email.message_from_bytes(msg_data[0][1])
            from_email = email.utils.parseaddr(msg["From"])[1]
            mail_date = msg.get("Date")
            try:
                parsed_date = email.utils.parsedate_to_datetime(mail_date)
            except Exception:
                parsed_date = datetime.datetime.now()
            cur.execute(
                "SELECT id FROM tickets WHERE email = %s ORDER BY id DESC LIMIT 1", (from_email,))
            ticket = cur.fetchone()
            if not ticket:
                continue
            ticket_id = ticket[0]
            # Extraction du corps du mail
            if msg.is_multipart():
                body = ""
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        body = part.get_payload(decode=True).decode()
                        break
                    elif part.get_content_type() == "text/html" and not body:
                        body = part.get_payload(decode=True).decode()
            else:
                body = msg.get_payload(decode=True).decode()
            body = clean_email_body(body)
            # Vérifie si déjà stocké
            cur.execute("SELECT 1 FROM messages WHERE ticket_id = %s AND content = %s AND sender = %s",
                        (ticket_id, body, from_email))
            if not cur.fetchone():
                cur.execute(
                    "INSERT INTO messages (ticket_id, sender, content, date) VALUES (%s, %s, %s, %s)",
                    (ticket_id, from_email, body, parsed_date)
                )
                conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Erreur lors de la synchronisation des mails : {e}")

# ==========================
# ROUTES FLASK
# ==========================


@app.route('/')
def index():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM tickets;')
    tickets = cur.fetchall()
    cur.execute('SELECT * FROM technicien;')
    techniciens = cur.fetchall()
    cur.close()
    conn.close()
    statut_labels = {
        'new': 'Nouveau',
        'pending': 'En attente',
        'assigned': 'Assigné',
        'resolved': 'Résolu',
        'closed': 'Clôturé'
    }
    return render_template('index.html', tickets=tickets, statut_labels=statut_labels, techniciens=techniciens)


@app.route("/api/mark_finished/<int:ticket_id>", methods=["POST"])
def mark_finished(ticket_id):
    """Marque un ticket comme terminé."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE tickets SET statut = %s WHERE id = %s",
                ("fini", ticket_id))
    flash("Le statut a bien été changé")
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for("index"))


@app.route("/api/mark_open/<int:ticket_id>", methods=["POST"])
def mark_open(ticket_id):
    """Change le statut d'un ticket selon le formulaire."""
    new_status = request.form.get("statut", "new")
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE tickets SET statut = %s WHERE id = %s",
                (new_status, ticket_id))
    flash("Le statut a bien été changé")
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for("index"))


@app.route("/api/delete_ticket/<int:ticket_id>", methods=["POST"])
def delete_ticket(ticket_id):
    """Supprime un ticket et sa pièce jointe si présente."""
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
    """Envoie un email au client et l'enregistre dans la base."""
    to_email = request.form["email"]
    message = request.form["message"]
    message_id, references, subject = get_last_message_headers(to_email)
    msg = MIMEText(message, "html")
    msg["Subject"] = subject if subject else "Réponse à votre ticket"
    msg["From"] = EMAIL_CONFIG["address"]
    msg["To"] = to_email
    if message_id:
        msg["In-Reply-To"] = message_id
    if references:
        msg["References"] = references
    try:
        with smtplib.SMTP(EMAIL_CONFIG["smtp_server"], EMAIL_CONFIG["smtp_port"]) as server:
            server.starttls()
            server.login(EMAIL_CONFIG["address"], EMAIL_CONFIG["password"])
            server.send_message(msg)
        flash(f"Email envoyé à {to_email}")
    except Exception as e:
        flash(f"Erreur lors de l'envoi du mail : {str(e)}")
    # Enregistrement du message dans la base
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO messages (ticket_id, sender, content) VALUES (%s, %s, %s)",
                (ticket_id, "support", message))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for("index"))


@app.route("/api/add_ticket", methods=["POST", "OPTIONS"])
def add_ticket():
    """Ajoute un nouveau ticket (avec gestion de pièce jointe)."""
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response
    try:
        object = request.form.get("objet", "")
        description = request.form.get("description", "")
        email_addr = request.form.get("email", "")
        status = request.form.get("statut", "ouvert")
        user_id = request.form.get("user_id")
        if not user_id or user_id in ("", "None", "null"):
            user_id = None
        creation_date = request.form.get("date_creation")
        modification_date = request.form.get("date_modification") or None
        resolution_date = request.form.get("date_resolution") or None
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
                else:
                    return jsonify({"message": f"Type de fichier non autorisé. Extensions autorisées: {', '.join(ALLOWED_EXTENSIONS)}"}), 400
        else:
            attachment_path = request.form.get("piece_jointe", "")
        conn = get_db_connection()
        cur = conn.cursor()
        # On ne gère plus l'attribution à un technicien ici
        technicien_id = None
        cur.execute(
            "INSERT INTO tickets (objet, description, email, piece_jointe, statut, date_creation, date_modification, date_resolution, user_id, technicien_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (object, description, email_addr, attachment_path, status,
             creation_date, modification_date, resolution_date, user_id, technicien_id)
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
    """Télécharge une pièce jointe."""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/api/gettickets', methods=['GET', 'OPTIONS'])
def get_tickets():
    """Renvoie tous les tickets (JSON)."""
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
    """Recherche de tickets avec filtres dynamiques."""
    keyword = request.args.get('keyword', '').strip()
    filter_by = request.args.get('filter_by', 'objet')
    statut = request.args.get('statut', '')
    order_by = request.args.get('order_by', 'date_creation')
    query = "SELECT * FROM tickets WHERE 1=1"
    params = []
    if keyword:
        if filter_by == 'objet':
            query += " AND objet ILIKE %s"
        elif filter_by == 'description':
            query += " AND description ILIKE %s"
        elif filter_by == 'email':
            query += " AND email ILIKE %s"
        params.append(f"%{keyword}%")
    if statut:
        query += " AND statut = %s"
        params.append(statut)
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
    statut_labels = {
        'new': 'Nouveau',
        'pending': 'En attente',
        'assigned': 'Assigné',
        'resolved': 'Résolu',
        'closed': 'Clôturé'
    }
    return render_template('index.html', tickets=tickets, statut_labels=statut_labels)


@app.route("/api/messages/<int:ticket_id>")
def get_messages(ticket_id):
    """Renvoie les messages associés à un ticket (JSON)."""
    sync_client_emails()
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT sender, content, date FROM messages WHERE ticket_id = %s ORDER BY date ASC", (ticket_id,))
    messages = [{"sender": row[0], "content": row[1], "date": row[2].strftime(
        '%d/%m/%Y %H:%M')} for row in cur.fetchall()]
    cur.close()
    conn.close()
    return jsonify(messages)


@app.route('/techniciens')
def techniciens():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM technicien")
    techniciens = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('techniciens.html', techniciens=techniciens)


@app.route('/techniciens/ajouter', methods=['GET', 'POST'])
def ajouter_technicien():
    if request.method == 'POST':
        nom = request.form['nom']
        prenom = request.form['prenom']
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO technicien (nom, prenom) VALUES (%s, %s)", (nom, prenom))
        conn.commit()
        cur.close()
        conn.close()
        flash("Technicien ajouté !")
        return redirect(url_for('techniciens'))
    return render_template('ajouter_technicien.html')


@app.route('/techniciens/supprimer/<int:technicien_id>', methods=['POST'])
def supprimer_technicien(technicien_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM technicien WHERE id = %s", (technicien_id,))
    conn.commit()
    cur.close()
    conn.close()
    flash("Technicien supprimé.")
    return redirect(url_for('techniciens'))


@app.route('/technicien/<int:technicien_id>')
def page_technicien(technicien_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT nom, prenom FROM technicien WHERE id = %s",
                (technicien_id,))
    tech = cur.fetchone()
    cur.execute("SELECT * FROM tickets WHERE technicien_id = %s",
                (technicien_id,))
    tickets = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('page_technicien.html', technicien=tech, tickets=tickets)


@app.route('/assigner_technicien/<int:ticket_id>', methods=['POST'])
def assigner_technicien(ticket_id):
    technicien_id = request.form['technicien_id']
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE tickets SET technicien_id = %s, statut = %s WHERE id = %s",
        (technicien_id, 'assigned', ticket_id)
    )
    conn.commit()
    cur.close()
    conn.close()
    flash("Ticket assigné au technicien.")
    return redirect(url_for('index'))


@app.route('/api/tickets_table')
def tickets_table():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM tickets;')
    tickets = cur.fetchall()
    cur.execute('SELECT * FROM technicien;')
    techniciens = cur.fetchall()
    cur.close()
    conn.close()
    statut_labels = {
        'new': 'Nouveau',
        'pending': 'En attente',
        'assigned': 'Assigné',
        'resolved': 'Résolu',
        'closed': 'Clôturé'
    }
    # On extrait juste le code du tableau de tickets
    return render_template('tickets_table.html', tickets=tickets, statut_labels=statut_labels, techniciens=techniciens)


# ==========================
# LANCEMENT DE L'APPLICATION
# ==========================
if __name__ == '__main__':
    app.run()
