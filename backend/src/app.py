from flask import Flask, render_template, request, flash

app = Flask(__name__)
app.secret_key = "dev"

# Données fictives
tickets = [
    {
        'id': 1,
        'objet': 'Connexion impossible',
        'description': 'Je ne peux pas me connecter',
        'email': 'exemple1@mail.com',
        'piece_jointe': '',
    },
    {
        'id': 2,
        'objet': 'Erreur de facturation',
        'description': 'Facture incorrecte',
        'email': 'exemple2@mail.com',
        'piece_jointe': 'https://via.placeholder.com/100',
    },
]

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        flash("Formulaire soumis ! (fonctionnalité non active)")
    return render_template('index.html', tickets=tickets)

if __name__ == '__main__':
    app.run(debug=True)
