"""
Point d'entrée de l'application UIST-2ITS
Lance le serveur Flask en mode développement
"""
from app import creer_application

app = creer_application()

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🎓 SYSTÈME UIST-2ITS - Gestion Universitaire")
    print("="*70)
    print("📊 Base de données: SQLite3")
    print("🌐 Serveur: http://localhost:5000")
    print("="*70 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)