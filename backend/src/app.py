from flask import Flask, render_template, request, flash, redirect, url_for, jsonify, make_response
from flask_cors import CORS
from email.mime.text import MIMEText
import psycopg2
import smtplib

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
CORS(app, origins=["*"])

@app.route('/')
def index():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM tickets;')
    tickets = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('index.html', tickets=tickets)

@app.route("/mark_finished/<int:ticket_id>", methods=["POST"])
def mark_finished(ticket_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE tickets SET statut = %s WHERE id = %s", ("fini", ticket_id))
    flash("Le statut a bien été changer")
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for("index"))

@app.route("/delete_ticket/<int:ticket_id>", methods=["POST"])
def delete_ticket(ticket_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM tickets WHERE id = %s", (ticket_id,))
    flash("Ticket supprimé avec succès.")
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for("index"))

@app.route("/send_email/<int:ticket_id>", methods=["POST"])
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

@app.route("/mark_open/<int:ticket_id>", methods=["POST"])
def mark_open(ticket_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE tickets SET statut = %s WHERE id = %s", ("ouvert", ticket_id))
    flash("Le statut a bien été changer")
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for("index"))

@app.route("/api/add_ticket", methods=["POST", "OPTIONS"])
def add_ticket():
    if request.method == 'OPTIONS':
        response = app.make_response('', 200)
        response.headers['Access-Control-Allow-Origin'] = 'http://localhost:5173'
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return
    
    object = request.form["objet"]
    description = request.form["description"]
    email = request.form["email"]
    attachment = request.form["piece_jointe"]
    status = "ouvert"
    creation_date = request.form["date_creation"]
    modification_date = request.form["date_modification"]
    resolution_date = request.form["date_resolution"]
    user_id = request.form["user_id"]

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO tickets (objet, description, email, piece_jointe, statut, date_creation, date_modification, date_resolution, user_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
        (object, description, email, attachment, status, creation_date, modification_date, resolution_date, user_id)
    )
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "Ticket ajouté avec succès."})


@app.route('/api/gettickets', methods=['GET', 'OPTIONS'])
def get_tickets():
    if request.method == 'OPTIONS':
        response = app.make_response('', 200)
        response.headers['Access-Control-Allow-Origin'] = 'http://localhost:5173'  # Remplacer par l'origine de ton frontend
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return
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

if __name__ == '__main__':
    app.run(debug=True)
