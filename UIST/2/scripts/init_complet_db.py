"""
Script d'Initialisation Complète - UIST-2ITS
Crée le schéma et insère toutes les données de test selon UIST-2ITS.txt
"""
import sqlite3
import os
import sys
from datetime import datetime, date
from werkzeug.security import generate_password_hash

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def creer_schema_complet(conn):
    """Crée le schéma complet"""
    print("\n📋 Création du schéma SQLite3...")
    
    schema_path = 'database/schema_sqlite.sql'
    if os.path.exists(schema_path):
        with open(schema_path, 'r', encoding='utf-8') as f:
            conn.executescript(f.read())
        print("  ✅ Schéma créé depuis schema_sqlite.sql")
    else:
        print("  ❌ Fichier schema_sqlite.sql introuvable!")
        return False
    
    conn.commit()
    return True

def inserer_donnees_test(conn):
    """Insère des données de test complètes"""
    cursor = conn.cursor()
    
    print("\n📝 Insertion des données de test...\n")
    
    # Mot de passe par défaut: "password123"
    password_hash = generate_password_hash('password123')
    
    # ========== UTILISATEURS ==========
    print("1. Création des utilisateurs...")
    
    utilisateurs = [
        # Super Admin
        ('ADMIN001', 'Admin', 'Super', 'admin@uist-2its.cm', password_hash, 'SUPER_ADMIN'),
        
        # Directeur
        ('DIR001', 'Kamga', 'Marcel', 'directeur@uist-2its.cm', password_hash, 'DIRECTEUR'),
        
        # Gestionnaires
        ('GEST101', 'Ngono', 'Paul', 'gestion1@uist-2its.cm', password_hash, 'GESTION_1'),
        ('GEST201', 'Mbarga', 'Christine', 'gestion2@uist-2its.cm', password_hash, 'GESTION_2'),
        ('GEST301', 'Fouda', 'Jean', 'gestion3@uist-2its.cm', password_hash, 'GESTION_3'),
        
        # Enseignants
        ('ENS001', 'Essomba', 'Roger', 'prof1@uist-2its.cm', password_hash, 'ENSEIGNANT'),
        ('ENS002', 'Nkolo', 'Marie', 'prof2@uist-2its.cm', password_hash, 'ENSEIGNANT'),
        ('ENS003', 'Tchoua', 'Alain', 'prof3@uist-2its.cm', password_hash, 'ENSEIGNANT'),
        ('ENS004', 'Ondoa', 'Brigitte', 'prof4@uist-2its.cm', password_hash, 'ENSEIGNANT'),
        ('ENS005', 'Mbassi', 'Eric', 'prof5@uist-2its.cm', password_hash, 'ENSEIGNANT'),
        
        # Étudiants
        ('ETU001', 'Atangana', 'Jean', 'etudiant1@uist-2its.cm', password_hash, 'ETUDIANT'),
        ('ETU002', 'Biyong', 'Alice', 'etudiant2@uist-2its.cm', password_hash, 'ETUDIANT'),
        ('ETU003', 'Eto', 'Patrick', 'etudiant3@uist-2its.cm', password_hash, 'ETUDIANT'),
        ('ETU004', 'Manga', 'Sophie', 'etudiant4@uist-2its.cm', password_hash, 'ETUDIANT'),
        ('ETU005', 'Owono', 'David', 'etudiant5@uist-2its.cm', password_hash, 'ETUDIANT'),
        ('ETU006', 'Bella', 'Grace', 'etudiant6@uist-2its.cm', password_hash, 'ETUDIANT'),
        ('ETU007', 'Ngo', 'Martin', 'etudiant7@uist-2its.cm', password_hash, 'ETUDIANT'),
        ('ETU008', 'Amougou', 'Claudine', 'etudiant8@uist-2its.cm', password_hash, 'ETUDIANT'),
        ('ETU009', 'Njoya', 'Boris', 'etudiant9@uist-2its.cm', password_hash, 'ETUDIANT'),
        ('ETU010', 'Feudjio', 'Annie', 'etudiant10@uist-2its.cm', password_hash, 'ETUDIANT'),
        
        # Parents
        ('PAR001', 'Atangana', 'Pierre', 'parent1@uist-2its.cm', password_hash, 'PARENT'),
        ('PAR002', 'Biyong', 'Marie', 'parent2@uist-2its.cm', password_hash, 'PARENT'),
        ('PAR003', 'Eto', 'Jacques', 'parent3@uist-2its.cm', password_hash, 'PARENT'),
    ]
    
    for matricule, nom, prenom, email, pwd, role in utilisateurs:
        cursor.execute("""
            INSERT OR IGNORE INTO utilisateurs (matricule, nom, prenom, email, mot_de_passe, role)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (matricule, nom, prenom, email, pwd, role))
    
    print(f"  ✅ {len(utilisateurs)} utilisateurs créés")
    
    # ========== FILIÈRES ==========
    print("2. Création des filières...")
    
    filieres = [
        ('INFO-L1', 'Informatique', 'L1', 40),
        ('INFO-L2', 'Informatique', 'L2', 35),
        ('INFO-L3', 'Informatique', 'L3', 30),
        ('RESEAU-L1', 'Réseaux et Télécommunications', 'L1', 30),
        ('RESEAU-L2', 'Réseaux et Télécommunications', 'L2', 25),
        ('MULTI-L1', 'Multimédia', 'L1', 25),
        ('MULTI-L2', 'Multimédia', 'L2', 20),
    ]
    
    for code, nom, niveau, effectif in filieres:
        cursor.execute("""
            INSERT OR IGNORE INTO filieres (code_filiere, nom_filiere, niveau, effectif_prevu)
            VALUES (?, ?, ?, ?)
        """, (code, nom, niveau, effectif))
    
    print(f"  ✅ {len(filieres)} filières créées")
    
    # ========== ENSEIGNANTS ==========
    print("3. Création des profils enseignants...")
    
    enseignants_data = [
        ('ENS001', 'Programmation Orientée Objet', '+237 690 12 34 56'),
        ('ENS002', 'Base de Données', '+237 691 23 45 67'),
        ('ENS003', 'Réseaux Informatiques', '+237 692 34 56 78'),
        ('ENS004', 'Conception Multimédia', '+237 693 45 67 89'),
        ('ENS005', 'Développement Web', '+237 694 56 78 90'),
    ]
    
    for matricule, specialite, tel in enseignants_data:
        cursor.execute("SELECT id_user FROM utilisateurs WHERE matricule = ?", (matricule,))
        result = cursor.fetchone()
        if result:
            user_id = result[0]
            cursor.execute("""
                INSERT OR IGNORE INTO enseignants (id_user, specialite, telephone)
                VALUES (?, ?, ?)
            """, (user_id, specialite, tel))
    
    print(f"  ✅ {len(enseignants_data)} enseignants créés")
    
    # ========== ÉTUDIANTS ==========
    print("4. Création des profils étudiants...")
    
    etudiants_data = [
        ('ETU001', 'INFO-L1', '1999-05-15', '107890AB', 'Yaoundé'),
        ('ETU002', 'INFO-L1', '1999-08-22', '108901BC', 'Douala'),
        ('ETU003', 'INFO-L2', '1998-03-10', '109012CD', 'Bafoussam'),
        ('ETU004', 'INFO-L2', '1998-11-30', '110123DE', 'Yaoundé'),
        ('ETU005', 'INFO-L3', '1997-07-18', '111234EF', 'Bertoua'),
        ('ETU006', 'RESEAU-L1', '1999-12-05', '112345FG', 'Garoua'),
        ('ETU007', 'RESEAU-L2', '1998-06-25', '113456GH', 'Yaoundé'),
        ('ETU008', 'MULTI-L1', '1999-09-14', '114567HI', 'Douala'),
        ('ETU009', 'MULTI-L2', '1998-04-20', '115678IJ', 'Maroua'),
        ('ETU010', 'INFO-L1', '1999-10-08', '116789JK', 'Yaoundé'),
    ]
    
    for matricule, filiere_code, naissance, cni, adresse in etudiants_data:
        cursor.execute("SELECT id_user FROM utilisateurs WHERE matricule = ?", (matricule,))
        user_result = cursor.fetchone()
        cursor.execute("SELECT id_filiere FROM filieres WHERE code_filiere = ?", (filiere_code,))
        filiere_result = cursor.fetchone()
        
        if user_result and filiere_result:
            cursor.execute("""
                INSERT OR IGNORE INTO etudiants (id_user, id_filiere, date_naissance, numero_cni, adresse)
                VALUES (?, ?, ?, ?, ?)
            """, (user_result[0], filiere_result[0], naissance, cni, adresse))
    
    print(f"  ✅ {len(etudiants_data)} étudiants créés")
    
    # ========== PARENTS ==========
    print("5. Création des profils parents...")
    
    parents_data = [
        ('PAR001', 'Ingénieur', '+237 680 11 22 33'),
        ('PAR002', 'Enseignante', '+237 681 22 33 44'),
        ('PAR003', 'Commerçant', '+237 682 33 44 55'),
    ]
    
    for matricule, profession, tel in parents_data:
        cursor.execute("SELECT id_user FROM utilisateurs WHERE matricule = ?", (matricule,))
        result = cursor.fetchone()
        if result:
            cursor.execute("""
                INSERT OR IGNORE INTO parents (id_user, profession, telephone)
                VALUES (?, ?, ?)
            """, (result[0], profession, tel))
    
    print(f"  ✅ {len(parents_data)} parents créés")
    
    # ========== LIAISON PARENT-ÉTUDIANT ==========
    print("6. Création des liaisons parent-étudiant...")
    
    cursor.execute("SELECT id_parent FROM parents ORDER BY id_parent LIMIT 3")
    parent_ids = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT id_etudiant FROM etudiants ORDER BY id_etudiant LIMIT 3")
    etudiant_ids = [row[0] for row in cursor.fetchall()]
    
    liaisons = []
    for i, (parent_id, etudiant_id) in enumerate(zip(parent_ids, etudiant_ids)):
        lien = ['Père', 'Mère', 'Tuteur'][i % 3]
        cursor.execute("""
            INSERT OR IGNORE INTO parente_liaison (id_parent, id_etudiant, lien_parente)
            VALUES (?, ?, ?)
        """, (parent_id, etudiant_id, lien))
        liaisons.append((parent_id, etudiant_id))
    
    print(f"  ✅ {len(liaisons)} liaisons créées")
    
    # ========== SALLES ==========
    print("7. Création des salles...")
    
    salles = [
        ('A101', 60, 'Vidéoprojecteur, Tableau blanc', 'Bâtiment A'),
        ('A102', 50, 'Ordinateurs (30 postes)', 'Bâtiment A'),
        ('B201', 40, 'Laboratoire réseau', 'Bâtiment B'),
        ('B202', 45, 'Vidéoprojecteur', 'Bâtiment B'),
        ('C301', 70, 'Amphithéâtre, Vidéoprojecteur', 'Bâtiment C'),
    ]
    
    for nom, capacite, equipements, batiment in salles:
        cursor.execute("""
            INSERT OR IGNORE INTO salles (nom_salle, capacite, equipements, batiment)
            VALUES (?, ?, ?, ?)
        """, (nom, capacite, equipements, batiment))
    
    print(f"  ✅ {len(salles)} salles créées")
    
    # ========== COURS ==========
    print("8. Création des cours...")
    
    cours_data = [
        ('INFO101', 'Introduction à l\'Informatique', 3, 'INFO-L1', 1.5),
        ('INFO102', 'Programmation C', 4, 'INFO-L1', 2.0),
        ('INFO201', 'Base de Données', 4, 'INFO-L2', 2.0),
        ('INFO202', 'Programmation Orientée Objet', 4, 'INFO-L2', 2.0),
        ('INFO301', 'Développement Web Avancé', 5, 'INFO-L3', 2.5),
        ('RESEAU101', 'Introduction aux Réseaux', 3, 'RESEAU-L1', 1.5),
        ('RESEAU201', 'Administration Réseaux', 4, 'RESEAU-L2', 2.0),
        ('MULTI101', 'Design Graphique', 3, 'MULTI-L1', 1.5),
        ('MULTI201', 'Animation 3D', 4, 'MULTI-L2', 2.0),
    ]
    
    for code, libelle, credit, filiere_code, coef in cours_data:
        cursor.execute("SELECT id_filiere FROM filieres WHERE code_filiere = ?", (filiere_code,))
        result = cursor.fetchone()
        if result:
            cursor.execute("""
                INSERT OR IGNORE INTO cours (code_cours, libelle, credit, id_filiere, coefficient)
                VALUES (?, ?, ?, ?, ?)
            """, (code, libelle, credit, result[0], coef))
    
    print(f"  ✅ {len(cours_data)} cours créés")
    
    # ========== EMPLOI DU TEMPS (exemples) ==========
    print("9. Création de l'emploi du temps...")
    
    cursor.execute("SELECT id_enseignant FROM enseignants LIMIT 5")
    ens_ids = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT id_salle FROM salles LIMIT 5")
    salle_ids = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT id_cours FROM cours LIMIT 5")
    cours_ids = [row[0] for row in cursor.fetchall()]
    
    edt_data = [
        (cours_ids[0], ens_ids[0], salle_ids[0], 'Lundi', '08:00', '10:00', 1, '2025-2026', 'Cours'),
        (cours_ids[1], ens_ids[1], salle_ids[1], 'Lundi', '10:15', '12:15', 1, '2025-2026', 'TD'),
        (cours_ids[2], ens_ids[2], salle_ids[2], 'Mardi', '08:00', '10:00', 1, '2025-2026', 'Cours'),
        (cours_ids[3], ens_ids[3], salle_ids[3], 'Mercredi', '14:00', '16:00', 1, '2025-2026', 'TP'),
        (cours_ids[4], ens_ids[4], salle_ids[4], 'Jeudi', '10:00', '12:00', 1, '2025-2026', 'Cours'),
    ]
    
    for edt in edt_data:
        cursor.execute("""
            INSERT OR IGNORE INTO emploi_du_temps 
            (id_cours, id_enseignant, id_salle, jour, heure_debut, heure_fin, semaine_numero, annee_academique, type_creneau)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, edt)
    
    print(f"  ✅ {len(edt_data)} créneaux EDT créés")
    
    # ========== NOTES (exemples) ==========
    print("10. Création des notes...")
    
    cursor.execute("SELECT id_etudiant FROM etudiants LIMIT 5")
    etud_ids = [row[0] for row in cursor.fetchall()]
    
    notes_data = []
    for etud_id in etud_ids:
        for cours_id in cours_ids[:3]:
            note = 12.5 + (etud_id % 5) + (cours_id % 3)
            notes_data.append((etud_id, cours_id, note, 'CC', 'En attente'))
    
    for note_data in notes_data:
        cursor.execute("""
            INSERT OR IGNORE INTO notes (id_etudiant, id_cours, valeur_note, type_evaluation, statut_validation)
            VALUES (?, ?, ?, ?, ?)
        """, note_data)
    
    print(f"  ✅ {len(notes_data)} notes créées")
    
    conn.commit()
    print("\n✅ Toutes les données de test ont été insérées avec succès!")

def afficher_statistiques(conn):
    """Affiche les statistiques de la base"""
    cursor = conn.cursor()
    
    print("\n" + "="*60)
    print("📊 STATISTIQUES DE LA BASE DE DONNÉES")
    print("="*60)
    
    tables = [
        ('utilisateurs', 'Utilisateurs'),
        ('enseignants', 'Enseignants'),
        ('etudiants', 'Étudiants'),
        ('parents', 'Parents'),
        ('filieres', 'Filières'),
        ('cours', 'Cours'),
        ('salles', 'Salles'),
        ('emploi_du_temps', 'Créneaux EDT'),
        ('notes', 'Notes'),
        ('parente_liaison', 'Liaisons Parent-Étudiant'),
    ]
    
    for table, label in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"  {label:.<40} {count:>5}")
    
    print("="*60)
    
    # Statistiques par rôle
    print("\n📋 UTILISATEURS PAR RÔLE:")
    cursor.execute("SELECT role, COUNT(*) FROM utilisateurs GROUP BY role ORDER BY role")
    for role, count in cursor.fetchall():
        print(f"  {role:.<40} {count:>5}")
    
    print("\n")

def main():
    """Fonction principale"""
    print("\n" + "="*60)
    print("🔧 INITIALISATION COMPLÈTE - UIST-2ITS")
    print("="*60)
    
    db_path = 'database/uist_2its.db'
    
    # Supprimer l'ancienne base si existe
    if os.path.exists(db_path):
        reponse = input(f"\n⚠️  La base '{db_path}' existe. Recréer? (oui/non): ").strip().lower()
        if reponse in ['oui', 'o', 'yes', 'y']:
            os.remove(db_path)
            print("  ✅ Ancienne base supprimée")
        else:
            print("  ℹ️  Conservation de la base existante")
            return
    
    # Créer le dossier
    os.makedirs('database', exist_ok=True)
    
    # Connexion
    conn = sqlite3.connect(db_path)
    conn.execute('PRAGMA foreign_keys = ON')
    print(f"\n✅ Connexion à '{db_path}'")
    
    try:
        # Créer le schéma
        if not creer_schema_complet(conn):
            return
        
        # Insérer les données
        inserer_donnees_test(conn)
        
        # Afficher les stats
        afficher_statistiques(conn)
        
        print("="*60)
        print("✅ INITIALISATION TERMINÉE AVEC SUCCÈS!")
        print("="*60)
        print("\n📝 COMPTES DE TEST CRÉÉS:")
        print("  👤 Admin:         admin@uist-2its.cm / password123")
        print("  👤 Directeur:     directeur@uist-2its.cm / password123")
        print("  👤 Gestion 1:     gestion1@uist-2its.cm / password123")
        print("  👤 Enseignant:    prof1@uist-2its.cm / password123")
        print("  👤 Étudiant:      etudiant1@uist-2its.cm / password123")
        print("  👤 Parent:        parent1@uist-2its.cm / password123")
        print("\n")
        
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()
        print("✅ Connexion fermée\n")

if __name__ == '__main__':
    main()