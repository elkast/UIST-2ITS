"""
Script d'initialisation de la base de données
Crée la base de données et un super administrateur par défaut
"""
import os
import sys

# Ajouter le répertoire racine au path
sys.path.insert(0, os.path.dirname(__file__))

from app import creer_application
from app.models.utilisateur import Utilisateur
from app.services.matricule_service import MatriculeService

def init_database():
    """Initialise la base de données avec le schéma"""
    app = creer_application()
    
    with app.app_context():
        from app.db import init_db, executer_requete
        
        print("\n" + "="*70)
        print("🔧 INITIALISATION DE LA BASE DE DONNÉES")
        print("="*70)
        
        # Vérifier si la base existe déjà
        db_path = app.config['DB_PATH']
        if os.path.exists(db_path):
            response = input(f"\n⚠️  La base de données existe déjà ({db_path}).\nVoulez-vous la réinitialiser? (oui/non): ")
            if response.lower() not in ['oui', 'o', 'yes', 'y']:
                print("❌ Initialisation annulée.")
                return
            
            # Supprimer l'ancienne base
            os.remove(db_path)
            print(f"🗑️  Ancienne base de données supprimée")
        
        # Créer la nouvelle base
        init_db()
        print("✅ Schéma de base de données créé avec succès!")
        
        # Créer un super administrateur par défaut
        print("\n" + "-"*70)
        print("👤 CRÉATION DU SUPER ADMINISTRATEUR")
        print("-"*70)
        
        matricule = MatriculeService.generer('SUPER_ADMIN')
        
        id_user = Utilisateur.creer(
            matricule=matricule,
            nom="Administrateur",
            prenom="Système",
            email="admin@uist-2its.edu",
            mot_de_passe="Admin@2025",
            role="SUPER_ADMIN"
        )
        
        if id_user:
            print(f"\n✅ Super Administrateur créé avec succès!")
            print(f"   📋 Matricule: {matricule}")
            print(f"   📧 Email: admin@uist-2its.edu")
            print(f"   🔑 Mot de passe: Admin@2025")
            print(f"\n⚠️  IMPORTANT: Changez ce mot de passe après la première connexion!")
        else:
            print("❌ Erreur lors de la création du super administrateur")
        
        # Créer quelques données de test
        print("\n" + "-"*70)
        print("📝 CRÉATION DE DONNÉES DE TEST")
        print("-"*70)
        
        # Créer des filières
        filieres_data = [
            ('INFO-L3', 'Informatique Licence 3', 'L3', 45),
            ('MATH-L2', 'Mathématiques Licence 2', 'L2', 50),
            ('PHYS-M1', 'Physique Master 1', 'M1', 30)
        ]
        
        for code, nom, niveau, effectif in filieres_data:
            executer_requete(
                "INSERT INTO filieres (code_filiere, nom_filiere, niveau, effectif_prevu) VALUES (?, ?, ?, ?)",
                (code, nom, niveau, effectif)
            )
        print("✅ 3 filières créées")
        
        # Créer des salles
        salles_data = [
            ('Amphi A', 200, 'Projecteur, Micro, Tableau interactif', 'Bâtiment A'),
            ('Salle TP1', 30, 'Ordinateurs, Projecteur', 'Bâtiment B'),
            ('Salle TD1', 40, 'Tableau, Projecteur', 'Bâtiment C')
        ]
        
        for nom, capacite, equipements, batiment in salles_data:
            executer_requete(
                "INSERT INTO salles (nom_salle, capacite, equipements, batiment) VALUES (?, ?, ?, ?)",
                (nom, capacite, equipements, batiment)
            )
        print("✅ 3 salles créées")
        
        print("\n" + "="*70)
        print("🎉 INITIALISATION TERMINÉE AVEC SUCCÈS!")
        print("="*70)
        print("\n💡 Vous pouvez maintenant lancer l'application avec: python run.py")
        print(f"🌐 Puis vous connecter sur: http://localhost:5000\n")

if __name__ == '__main__':
    init_database()