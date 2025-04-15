from . import db
from datetime import datetime

class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    demandeur = db.Column(db.String(100))
    email = db.Column(db.String(100))
    sujet = db.Column(db.String(200))
    contenu = db.Column(db.Text)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    date_modification = db.Column(db.DateTime, onupdate=datetime.utcnow)
    date_resolution = db.Column(db.DateTime)
    statut = db.Column(db.String(50), default='Nouveau')
    priorite = db.Column(db.Integer)