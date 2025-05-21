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
import uuid
import time
import socket
from email.mime.text import MIMEText
from flask import (
    Flask, render_template, request, flash, redirect, url_for,
    jsonify, make_response, send_from_directory, session,
    render_template_string
)
from flask_cors import CORS
from werkzeug.utils import secure_filename
from email.header import decode_header

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
        # Arrête à la première citation ou signature
        if line.strip().startswith('--'):
            break
        if re.match(r'^(Le|On|From:|De :|>|\s*>|.*écrit\s*:).*', line, re.IGNORECASE):
            break
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


def extract_ticket_code(subject):
    import re
    # Décodage du sujet si encodé MIME
    if subject:
        decoded_fragments = decode_header(subject)
        subject = ''.join(
            fragment.decode(
                encoding or 'utf-8') if isinstance(fragment, bytes) else fragment
            for fragment, encoding in decoded_fragments
        )
    m = re.search(r'\[Ticket #([A-Za-z0-9\-]+)\]', subject or "")
    return m.group(1) if m else None


def sync_client_emails():
    try:
        print("Début synchronisation IMAP")
        mail = imaplib.IMAP4_SSL(EMAIL_CONFIG["imap_server"])
        mail.login(EMAIL_CONFIG["address"], EMAIL_CONFIG["password"])
        mail.select("inbox")
        status, data = mail.search(None, 'ALL')
        mail_ids = data[0].split()
        print(f"Nombre de mails trouvés: {len(mail_ids)}")
        conn = get_db_connection()
        cur = conn.cursor()
        for mail_id in mail_ids:
            status, msg_data = mail.fetch(mail_id, "(RFC822)")
            msg = email.message_from_bytes(msg_data[0][1])
            subject = msg.get("Subject", "")
            ticket_code = extract_ticket_code(subject)
            print(f"Sujet: {subject} | Code extrait: {ticket_code}")
            if not ticket_code:
                print("Aucun code ticket trouvé, mail ignoré.")
                continue
            cur.execute(
                "SELECT id FROM tickets WHERE ticket_code = %s", (ticket_code,))
            ticket = cur.fetchone()
            if not ticket:
                print(
                    f"Aucun ticket trouvé pour code {ticket_code}, mail ignoré.")
                continue
            ticket_id = ticket[0]
            from_email = email.utils.parseaddr(msg["From"])[1]
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
            # Affiche le début du corps
            print(f"Corps extrait: {body[:50]}...")
            # Vérifie si déjà stocké
            cur.execute("SELECT 1 FROM messages WHERE ticket_id = %s AND content = %s AND sender = %s",
                        (ticket_id, body, from_email))
            if not cur.fetchone():
                print(f"Insertion message ticket {ticket_id} de {from_email}")
                cur.execute(
                    "INSERT INTO messages (ticket_id, sender, content) VALUES (%s, %s, %s)",
                    (ticket_id, from_email, body)
                )
                conn.commit()
            else:
                print("Message déjà présent en base, pas d'insertion.")
        cur.close()
        conn.close()
        print("Fin synchronisation IMAP")
    except Exception as e:
        print(f"Erreur lors de la synchronisation des mails : {e}")


LAST_EMAIL_SYNC = 0
EMAIL_SYNC_INTERVAL = 90  # secondes (1min30 recommandé pour Gmail)


def sync_client_emails_if_needed():
    global LAST_EMAIL_SYNC
    now = time.time()
    if now - LAST_EMAIL_SYNC > EMAIL_SYNC_INTERVAL:
        sync_client_emails()
        LAST_EMAIL_SYNC = now


# ==========================
# ROUTES FLASK
# ==========================


@app.route('/')
def index():
    conn = get_db_connection()
    cur = conn.cursor()
    # Ne sélectionne pas les tickets clôturés par défaut
    cur.execute("SELECT * FROM tickets WHERE statut != 'closed';")
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
    # Supprimer d'abord les messages liés à ce ticket
    cur.execute("DELETE FROM messages WHERE ticket_id = %s", (ticket_id,))
    # Récupérer la pièce jointe avant de supprimer le ticket
    cur.execute("SELECT piece_jointe FROM tickets WHERE id = %s", (ticket_id,))
    result = cur.fetchone()
    piece_jointe = result[0] if result else None
    # Supprimer le ticket
    cur.execute("DELETE FROM tickets WHERE id = %s", (ticket_id,))
    conn.commit()
    cur.close()
    conn.close()
    if piece_jointe:
        file_path = os.path.join(UPLOAD_FOLDER, piece_jointe)
        if os.path.exists(file_path):
            os.remove(file_path)
    # Si la requête vient d'AJAX (frontend)
    if request.accept_mimetypes['application/json'] >= request.accept_mimetypes['text/html']:
        return jsonify({"message": "Ticket supprimé avec succès."}), 200
    # Sinon, redirection classique (interface admin)
    flash("Ticket supprimé avec succès.")
    return redirect(url_for("index"))


def get_last_message_headers_for_ticket(ticket_id):
    """Récupère les en-têtes du dernier mail pour CE ticket."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT sender, content, date FROM messages WHERE ticket_id = %s ORDER BY date DESC LIMIT 1",
            (ticket_id,)
        )
        last_msg = cur.fetchone()
        cur.close()
        conn.close()
        if not last_msg:
            return None, None, None
        # Si tu stockes Message-ID et References dans la table messages, récupère-les ici
        # Sinon, retourne juste None pour forcer un nouveau thread
        return None, None, None
    except Exception as e:
        print(f"Erreur lors de la récupération des headers du ticket: {e}")
        return None, None, None


@app.route("/api/send_email/<int:ticket_id>", methods=["POST"])
def send_email(ticket_id):
    to_email = request.form["email"]
    message = request.form["message"]
    message_id, references, subject = get_last_message_headers_for_ticket(
        ticket_id)
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT ticket_code FROM tickets WHERE id = %s", (ticket_id,))
    result = cur.fetchone()
    ticket_code = result[0] if result else "UNKNOWN"
    cur.close()
    conn.close()
    msg = MIMEText(message, "html")
    msg["Subject"] = f"[Ticket #{ticket_code}] " + \
        (subject if subject else "Réponse à votre ticket")
    msg["From"] = EMAIL_CONFIG["address"]
    msg["To"] = to_email

    # Premier message du ticket : génère un Message-ID unique
    if not message_id:
        msg_id = generate_message_id(ticket_code)
        msg["Message-ID"] = msg_id
    else:
        msg["In-Reply-To"] = message_id
        msg["References"] = references if references else message_id

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


def generate_ticket_code():
    return str(uuid.uuid4())[:8]  # ou une autre logique


def generate_message_id(ticket_code):
    hostname = socket.getfqdn()
    return f"<ticket-{ticket_code}-{uuid.uuid4()}@{hostname}>"


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
        ticket_code = generate_ticket_code()
        cur.execute(
            "INSERT INTO tickets (objet, description, email, piece_jointe, statut, date_creation, date_modification, date_resolution, user_id, technicien_id, ticket_code) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (object, description, email_addr, attachment_path, status,
             creation_date, modification_date, resolution_date, user_id, technicien_id, ticket_code)
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
    filter_by = request.args.get('filter_by', '')
    statut = request.args.get('statut', '')
    order_by = request.args.get('order_by', '')
    query = "SELECT * FROM tickets WHERE 1=1"
    params = []
    if keyword and filter_by:
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
    cur.execute('SELECT * FROM technicien;')
    techniciens = cur.fetchall()
    cur.close()
    conn.close()
    statut_labels = {
        'new': 'Nouveau',
        'pending': 'En attente',
        'assigned': 'Résolu',
        'closed': 'Clôturé'
    }
    return render_template('index.html', tickets=tickets, statut_labels=statut_labels, techniciens=techniciens)


@app.route("/api/messages/<int:ticket_id>")
def get_messages(ticket_id):
    """Renvoie les messages associés à un ticket (JSON)."""
    sync_client_emails()  # Synchronise IMAP à chaque ouverture de la popup
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
        'assigned': 'Résolu',
        'closed': 'Clôturé'
    }
    # On extrait juste le code du tableau de tickets
    return render_template('tickets_table.html', tickets=tickets, statut_labels=statut_labels, techniciens=techniciens)


# ==========================
# LANCEMENT DE L'APPLICATION
# ==========================
if __name__ == '__main__':
    app.run()
