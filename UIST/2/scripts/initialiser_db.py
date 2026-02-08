"""
Script d'Initialisation de la Base de Données SQLite3 - UIST-2ITS
Crée le schéma et insère des données de test
"""
import sqlite3
import os
import sys
from datetime import datetime
from werkzeug.security import generate_password_hash

# Ajouter le chemin parent
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def creer_schema(conn):
    """Crée le schéma complet de la base de données"""
    cursor = conn.cursor()
    
    print("📋 Création du schéma...")
    
    # Lire le fichier schema si disponible
    schema_path = 'database/schema_sqlite.sql'
    if os.path.exists(schema_path):
        with open(schema_path, 'r', encoding='utf-8') as f:
            cursor.executescript(f.read())
        print("  ✅ Schéma créé depuis schema_sqlite.sql")
    else:
        # Créer manuellement les tables principales
        cursor.executescript("""
        -- Table Utilisateurs
        CREATE TABLE IF NOT EXISTS Utilisateurs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            matricule VARCHAR(20) UNIQUE NOT NULL,
            nom VARCHAR(100) NOT NULL,
            prenom VARCHAR(100) NOT NULL,
            email VARCHAR(150) UNIQUE NOT NULL,
            mot_de_passe VARCHAR(255) NOT NULL,
            role TEXT CHECK(role IN (
                'SUPER_ADMIN', 'ADMIN', 'DIRECTEUR',
                'GESTIONNAIRE_PV', 'GESTIONNAIRE_EXAMENS', 'GESTIONNAIRE_EDT', 'GESTIONNAIRE_PRESENCES',
                'ENSEIGNANT', 'ETUDIANT', 'PARENT'
            )) NOT NULL,
            telephone VARCHAR(20),
            adresse TEXT,
            actif INTEGER DEFAULT 1,
            date_creation DATETIME DEFAULT CURRENT_TIMESTAMP,
            derniere_connexion DATETIME
        );
        
        CREATE INDEX IF NOT EXISTS idx_utilisateurs_matricule ON Utilisateurs(matricule);
        CREATE INDEX IF NOT EXISTS idx_utilisateurs_role ON Utilisateurs(role);
        CREATE INDEX IF NOT EXISTS idx_utilisateurs_email ON Utilisateurs(email);
        
        -- Table Enseignants
        CREATE TABLE IF NOT EXISTS Enseignants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            utilisateur_id INTEGER NOT NULL UNIQUE,
            specialite VARCHAR(100),
            grade VARCHAR(50),
            departement VARCHAR(100),
            statut_emploi TEXT CHECK(statut_emploi IN ('PERMANENT', 'CONTRACTUEL', 'VACATAIRE')) DEFAULT 'CONTRACTUEL',
            date_embauche DATE,
            FOREIGN KEY (utilisateur_id) REFERENCES Utilisateurs(id) ON DELETE CASCADE
        );
        
        -- Table Filieres
        CREATE TABLE IF NOT EXISTS Filieres (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code VARCHAR(10) UNIQUE NOT NULL,
            nom VARCHAR(150) NOT NULL,
            description TEXT,
            chef_filiere_id INTEGER,
            credits_requis INTEGER DEFAULT 180,
            duree_annees INTEGER DEFAULT 3,
            actif INTEGER DEFAULT 1,
            FOREIGN KEY (chef_filiere_id) REFERENCES Enseignants(id) ON DELETE SET NULL
        );
        
        -- Table Etudiants
        CREATE TABLE IF NOT EXISTS Etudiants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            utilisateur_id INTEGER NOT NULL UNIQUE,
            filiere_id INTEGER NOT NULL,
            niveau TEXT CHECK(niveau IN ('L1', 'L2', 'L3', 'M1', 'M2')) NOT NULL,
            annee_academique VARCHAR(9) NOT NULL,
            numero_cni VARCHAR(50),
            date_naissance DATE,
            lieu_naissance VARCHAR(100),
            nationalite VARCHAR(50) DEFAULT 'CAMEROUNAISE',
            FOREIGN KEY (utilisateur_id) REFERENCES Utilisateurs(id) ON DELETE CASCADE,
            FOREIGN KEY (filiere_id) REFERENCES Filieres(id) ON DELETE RESTRICT
        );
        
        -- Table UsageAudit
        CREATE TABLE IF NOT EXISTS UsageAudit (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            utilisateur_id INTEGER,
            action_type VARCHAR(50) NOT NULL,
            action_description TEXT,
            ip_address VARCHAR(45),
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (utilisateur_id) REFERENCES Utilisateurs(id) ON DELETE SET NULL
        );
        """)
        print("  ✅ Schéma de base créé")
    
    conn.commit()

def inserer_donnees_test(conn):
    """Insère des données de test"""
    cursor = conn.cursor()
    
    print("\n📝 Insertion des données de test...")
    
    # Super Admin
    mot_de_passe_hash = generate_password_hash('admin123')
    cursor.execute("""
        INSERT OR IGNORE INTO Utilisateurs (matricule, nom, prenom, email, mot_de_passe, role)
        VALUES ('ADMIN001', 'Admin', 'Super', 'admin@uist-2its.cm', ?, 'SUPER_ADMIN')
    """, (mot_de_passe_hash,))
    
    # Directeur
    cursor.execute("""
        INSERT OR IGNORE INTO Utilisateurs (matricule, nom, prenom, email, mot_de_passe, role)
        VALUES ('DIR001', 'Directeur', 'Général', 'directeur@uist-2its.cm', ?, 'DIRECTEUR')
    """, (mot_de_passe_hash,))
    
    # Enseignants
    for i in range(1, 6):
        cursor.execute("""
            INSERT OR IGNORE INTO Utilisateurs (matricule, nom, prenom, email, mot_de_passe, role, telephone)
            VALUES (?, ?, ?, ?, ?, 'ENSEIGNANT', ?)
        """, (f'ENS{i:03d}', f'Enseignant{i}', f'Prof{i}', f'prof{i}@uist-2its.cm', 
              mot_de_passe_hash, f'+237 6XX XX XX {i:02d}'))
        
        # Profil enseignant
        cursor.execute("""
            INSERT OR IGNORE INTO Enseignants (utilisateur_id, specialite, grade, statut_emploi)
            SELECT id, ?, ?, 'PERMANENT' FROM Utilisateurs WHERE matricule = ?
        """, (f'Informatique', 'Docteur', f'ENS{i:03d}'))
    
    # Filières
    filieres = [
        ('INFO', 'Informatique', 'Formation en développement logiciel et systèmes d\'information'),
        ('RESEAU', 'Réseaux et Télécommunications', 'Formation en réseaux informatiques'),
        ('MULTI', 'Multimédia', 'Formation en design et développement multimédia')
    ]
    
    for code, nom, desc in filieres:
        cursor.execute("""
            INSERT OR IGNORE INTO Filieres (code, nom, description, credits_requis)
            VALUES (?, ?, ?, 180)
        """, (code, nom, desc))
    
    # Étudiants
    for i in range(1, 21):
        filiere = ['INFO', 'RESEAU', 'MULTI'][i % 3]
        niveau = ['L1', 'L2', 'L3', 'M1', 'M2'][i % 5]
        
        cursor.execute("""
            INSERT OR IGNORE INTO Utilisateurs (matricule, nom, prenom, email, mot_de_passe, role, telephone)
            VALUES (?, ?, ?, ?, ?, 'ETUDIANT', ?)
        """, (f'ETU{i:03d}', f'Etudiant{i}', f'Jean{i}', f'etudiant{i}@uist-2its.cm',
              mot_de_passe_hash, f'+237 6XX XX XX {i+20:02d}'))
        
        # Profil étudiant
        cursor.execute("""
            INSERT OR IGNORE INTO Etudiants (utilisateur_id, filiere_id, niveau, annee_academique)
            SELECT u.id, f.id, ?, '2025-2026'
            FROM Utilisateurs u, Filieres f
            WHERE u.matricule = ? AND f.code = ?
        """, (niveau, f'ETU{i:03d}', filiere))
    
    conn.commit()
    print("  ✅ Données de test insérées")
    
    # Afficher les statistiques
    cursor.execute("SELECT role, COUNT(*) FROM Utilisateurs GROUP BY role")
    print("\n📊 Statistiques:")
    for role, count in cursor.fetchall():
        print(f"  - {role}: {count}")

def main():
    """Fonction principale"""
    print("\n" + "="*60)
    print("🔧 INITIALISATION BASE DE DONNÉES UIST-2ITS")
    print("="*60 + "\n")
    
    db_path = 'database/uist_2its.db'
    
    # Vérifier si la base existe
    if os.path.exists(db_path):
        print(f"⚠️  La base '{db_path}' existe déjà.")
        reponse = input("  Voulez-vous la recréer? (oui/non): ").strip().lower()
        if reponse in ['oui', 'o', 'yes', 'y']:
            os.remove(db_path)
            print("  ✅ Ancienne base supprimée")
        else:
            print("  ℹ️  Conservation de la base existante")
    
    # Créer le dossier database
    os.makedirs('database', exist_ok=True)
    
    # Connexion SQLite
    conn = sqlite3.connect(db_path)
    conn.execute('PRAGMA foreign_keys = ON')
    print(f"✅ Connexion à '{db_path}'")
    
    try:
        # Créer le schéma
        creer_schema(conn)
        
        # Insérer données de test
        inserer_donnees_test(conn)
        
        print("\n✅ Initialisation terminée avec succès!")
        print(f"\n📝 Comptes de test créés:")
        print("  Admin:     admin@uist-2its.cm / admin123")
        print("  Directeur: directeur@uist-2its.cm / admin123")
        print("  Enseignant: prof1@uist-2its.cm / admin123")
        print("  Étudiant:  etudiant1@uist-2its.cm / admin123")
        print("")
        
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
    finally:
        conn.close()
        print("✅ Connexion fermée")

if __name__ == '__main__':
    main()