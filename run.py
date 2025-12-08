"""
Point d'entrée de l'application UIST-Planify
Lance le serveur Flask en mode développement
"""
from app import creer_application

app = creer_application()

if __name__ == '__main__':
    app.run(debug=True)