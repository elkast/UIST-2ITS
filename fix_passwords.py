#!/usr/bin/env python3
"""
Script pour corriger les mots de passe invalides dans la base de données
"""
from werkzeug.security import generate_password_hash
from app.db import executer_requete, executer_requete_unique

def corriger_mots_de_passe():
    """Corrige tous les mots de passe invalides"""

    # Mot de passe par défaut
    password_hash = generate_password_hash('password123')

    print("🔧 Correction des mots de passe invalides...")
    print("=" * 60)

    # Récupérer tous les utilisateurs
    utilisateurs = executer_requete("SELECT id, matricule, nom, prenom, password_hash FROM Utilisateurs", obtenir_resultats=True)

    if not utilisateurs:
        print("❌ Aucun utilisateur trouvé dans la base de données")
        return

    corrections = 0

    for user in utilisateurs:
        user_id = user['id']
        matricule = user['matricule']
        nom = user['nom']
        prenom = user['prenom']
        current_hash = user['password_hash']

        # Vérifier si le hash est valide (doit commencer par $2b$ ou $2a$ pour bcrypt)
        if not current_hash or not current_hash.startswith(('$2b$', '$2a$')):
            print(f"🔄 Correction du mot de passe pour {matricule} - {prenom} {nom}")
            print(f"   Ancien hash: {current_hash[:50]}..." if current_hash else "   Ancien hash: NULL")

            # Mettre à jour avec un hash valide
            executer_requete(
                "UPDATE Utilisateurs SET password_hash = %s WHERE id = %s",
                (password_hash, user_id)
            )

            corrections += 1
            print("   ✅ Corrigé")
        else:
            print(f"✅ {matricule} - {prenom} {nom}: Hash valide")

    print("=" * 60)
    print(f"✅ Corrections terminées: {corrections} mot(s) de passe corrigé(s)")
    print("\n📋 Informations de connexion:")
    print("   Matricule: [voir ci-dessus]")
    print("   Mot de passe: password123")
    print("\n⚠️  Note: Tous les utilisateurs ont maintenant le même mot de passe temporaire.")

if __name__ == '__main__':
    corriger_mots_de_passe()
