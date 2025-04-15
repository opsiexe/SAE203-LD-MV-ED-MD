from flask import Blueprint

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return "Bienvenue sur le backend de gestion de support 🎫"