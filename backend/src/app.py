from flask import Flask, render_template, request, flash, redirect, url_for
import psycopg2

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

if __name__ == '__main__':
    app.run(debug=True)
