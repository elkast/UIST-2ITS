"""
Script pour récupérer les identifiants de connexion
Affiche les comptes créés avec leurs mots de passe
"""
from app import create_app
from models.utilisateurs import Utilisateur
from database import db

def afficher_identifiants():
    """Affiche les identifiants de tous les utilisateurs"""
    
    print("\n" + "="*80)
    print("🔑 IDENTIFIANTS DE CONNEXION - UIST-2ITS")
    print("="*80)
    
    # Récupérer tous les utilisateurs
    utilisateurs = db.session.query(Utilisateur).order_by(Utilisateur.role, Utilisateur.nom).all()
    
    if not utilisateurs:
        print("\n❌ Aucun utilisateur trouvé dans la base de données")
        print("💡 Exécutez d'abord: python init_db.py")
        print("💡 Puis pour créer les comptes de test: python creer_utilisateurs_demo.py")
        return
    
    # Grouper par rôle
    roles_dict = {}
    for user in utilisateurs:
        if user.role not in roles_dict:
            roles_dict[user.role] = []
        roles_dict[user.role].append(user)
    
    # Afficher par rôle
    for role, users in sorted(roles_dict.items()):
        print(f"\n📋 {role}")
        print("-"*80)
        for user in users:
            print(f"   Matricule: {user.matricule}")
            print(f"   Nom: {user.prenom} {user.nom}")
            print(f"   Email: {user.email}")
            print(f"   Statut: {'✅ Actif' if user.est_actif else '❌ Inactif'}")
            print("-"*80)
    
    print("\n⚠️  MOTS DE PASSE PAR DÉFAUT:")
    print("-"*80)
    print("   SUPER_ADMIN    : Admin@2025")
    print("   DIRECTEUR      : Directeur@2025")
    print("   GESTION_1      : Gestion1@2025")
    print("   GESTION_2      : Gestion2@2025")
    print("   GESTION_3      : Gestion3@2025")
    print("   ENSEIGNANT     : Enseignant@2025")
    print("   ETUDIANT       : Etudiant@2025")
    print("   PARENT         : Parent@2025")
    print("="*80)
    
    print("\n💡 INSTRUCTIONS:")
    print("   1. Copiez le matricule de l'utilisateur souhaité")
    print("   2. Utilisez le mot de passe correspondant au rôle")
    print("   3. Connectez-vous sur http://localhost:5000")
    print("\n⚠️  IMPORTANT: Changez ces mots de passe en production!")
    print("="*80 + "\n")

if __name__ == '__main__':
    app = create_app()
    
    with app.app_context():
        afficher_identifiants()
