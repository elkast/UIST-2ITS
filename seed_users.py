"""
Script de création des utilisateurs de test
Crée tous les utilisateurs avec leurs profils respectifs
"""
from werkzeug.security import generate_password_hash
from app.db import executer_requete, executer_requete_unique


def creer_utilisateurs_test():
    """Crée les utilisateurs de test avec mots de passe hashés"""
    
    # Mot de passe par défaut
    password_hash = generate_password_hash('password123')
    
    utilisateurs = [
        # Super Admin
        {
            'nom': 'Super',
            'prenom': 'Admin',
            'matricule': 'SA2025001',
            'email': 'superadmin@uist.edu',
            'role': 'SUPER_ADMIN',
            'password_hash': password_hash
        },
        # Admin
        {
            'nom': 'Admin',
            'prenom': 'Principal',
            'matricule': 'A2025001',
            'email': 'admin@uist.edu',
            'role': 'ADMIN',
            'password_hash': password_hash
        },
        # Directeur
        {
            'nom': 'Directeur',
            'prenom': 'Académique',
            'matricule': 'DIR2025001',
            'email': 'directeur@uist.edu',
            'role': 'DIRECTEUR',
            'password_hash': password_hash
        },
        # Gestionnaire PV
        {
            'nom': 'Gestionnaire',
            'prenom': 'PV',
            'matricule': 'GPV2025001',
            'email': 'gpv@uist.edu',
            'role': 'GESTIONNAIRE_PV',
            'password_hash': password_hash
        },
        # Gestionnaire Examens
        {
            'nom': 'Gestionnaire',
            'prenom': 'Examens',
            'matricule': 'GEX2025001',
            'email': 'gexamens@uist.edu',
            'role': 'GESTIONNAIRE_EXAMENS',
            'password_hash': password_hash
        },
        # Gestionnaire EDT
        {
            'nom': 'Gestionnaire',
            'prenom': 'EDT',
            'matricule': 'GEDT2025001',
            'email': 'gedt@uist.edu',
            'role': 'GESTIONNAIRE_EDT',
            'password_hash': password_hash
        },
        # Gestionnaire Présences
        {
            'nom': 'Gestionnaire',
            'prenom': 'Présences',
            'matricule': 'GPRE2025001',
            'email': 'gpresences@uist.edu',
            'role': 'GESTIONNAIRE_PRESENCES',
            'password_hash': password_hash
        },
        # Enseignants
        {
            'nom': 'Diop',
            'prenom': 'Amadou',
            'matricule': 'P2025001',
            'email': 'enseignant1@uist.edu',
            'role': 'ENSEIGNANT',
            'password_hash': password_hash
        },
        {
            'nom': 'Ndiaye',
            'prenom': 'Fatou',
            'matricule': 'P2025002',
            'email': 'enseignant2@uist.edu',
            'role': 'ENSEIGNANT',
            'password_hash': password_hash
        },
        # Étudiants
        {
            'nom': 'Sow',
            'prenom': 'Moussa',
            'matricule': 'E2025001',
            'email': 'etudiant1@uist.edu',
            'role': 'ETUDIANT',
            'password_hash': password_hash
        },
        {
            'nom': 'Fall',
            'prenom': 'Aissatou',
            'matricule': 'E2025002',
            'email': 'etudiant2@uist.edu',
            'role': 'ETUDIANT',
            'password_hash': password_hash
        },
        # Parents
        {
            'nom': 'Sow',
            'prenom': 'Mamadou',
            'matricule': 'PAR2025001',
            'email': 'parent1@uist.edu',
            'role': 'PARENT',
            'password_hash': password_hash
        }
    ]
    
    print("🚀 Création des utilisateurs de test...")
    print("=" * 70)
    
    for user in utilisateurs:
        # Vérifier si l'utilisateur existe déjà
        existing = executer_requete_unique(
            "SELECT id FROM Utilisateurs WHERE matricule = %s",
            (user['matricule'],)
        )
        
        if existing:
            print(f"⚠️  {user['matricule']} existe déjà - Mise à jour du mot de passe")
            executer_requete(
                "UPDATE Utilisateurs SET password_hash = %s WHERE matricule = %s",
                (user['password_hash'], user['matricule'])
            )
        else:
            # Créer l'utilisateur
            user_id = executer_requete(
                """INSERT INTO Utilisateurs (nom, prenom, matricule, email, password_hash, role)
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (user['nom'], user['prenom'], user['matricule'], 
                 user['email'], user['password_hash'], user['role'])
            )
            
            if user_id:
                print(f"✅ {user['role']:20} | {user['matricule']:15} | {user['prenom']} {user['nom']}")
                
                # Créer les profils spécifiques
                if user['role'] == 'ENSEIGNANT':
                    executer_requete(
                        "INSERT INTO Enseignants (utilisateur_id, specialite) VALUES (%s, %s)",
                        (user_id, 'Informatique')
                    )
                elif user['role'] == 'ETUDIANT':
                    # Affecter à la filière Informatique L3 (ID 1)
                    executer_requete(
                        "INSERT INTO Etudiants (utilisateur_id, filiere_id) VALUES (%s, %s)",
                        (user_id, 1)
                    )
            else:
                print(f"❌ Erreur création {user['matricule']}")
    
    print("=" * 70)
    print("✅ Utilisateurs créés avec succès!")
    print("\n📋 Informations de connexion:")
    print("   Matricule: [voir tableau ci-dessus]")
    print("   Mot de passe: password123")
    print("\n⚠️  Note: Utilisez la page de connexion standard pour vous connecter.")


if __name__ == '__main__':
    creer_utilisateurs_test()