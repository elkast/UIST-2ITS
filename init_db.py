"""
Script d'initialisation de la base de données
Crée toutes les tables et les données de base
"""
from app import create_app
from database import db
from helpers.init_data import initialiser_donnees_base

if __name__ == '__main__':
    print("🚀 Initialisation de la base de données UIST-2ITS...")
    
    app = create_app()
    
    with app.app_context():
        # Créer toutes les tables
        print("📊 Création des tables...")
        db.create_all()
        print("✅ Tables créées!")
        
        # Initialiser les données de base
        print("\n💾 Initialisation des données de base...")
        initialiser_donnees_base()
        print("✅ Données de base créées!")
        
    print("\n🎉 Base de données initialisée avec succès!")
    print("\n📝 Vous pouvez maintenant lancer l'application avec:")
    print("   python app.py")
