from flask import Flask, render_template, request, flash, redirect, url_for
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

if __name__ == '__main__':
    app.run(debug=True)
