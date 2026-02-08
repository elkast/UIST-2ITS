# 🗄️ Guide de la Base de Données - UIST-2ITS

## 📌 Vue d'ensemble

Ce guide documente la structure de la base de données SQLite3 du système UIST-2ITS, la migration depuis MySQL, et les bonnes pratiques d'utilisation.

---

## 🔄 Migration MySQL → SQLite3

### Pourquoi SQLite3 ?

**Avantages:**
- ✅ **Simplicité:** Un seul fichier, pas de serveur
- ✅ **Portable:** Facile à déplacer, sauvegarder
- ✅ **Performance:** Excellent pour <100k utilisateurs
- ✅ **Fiabilité:** Très stable, bien testé
- ✅ **Développement:** Parfait pour dev local

**Limitations connues:**
- ⚠️ Pas de procédures stockées (remplacées par Python)
- ⚠️ Types limités (TEXT, INTEGER, REAL, BLOB)
- ⚠️ Concurrence limitée (mais suffisante pour notre cas)

### Script de Migration

Fichier: `scripts/migrer_mysql_vers_sqlite.py`

```python
"""
Script de migration MySQL vers SQLite3
"""
import sqlite3
import mysql.connector
from datetime import datetime

def migrer_mysql_vers_sqlite():
    """Migre les données de MySQL vers SQLite3"""
    
    # Connexion MySQL
    mysql_conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='uist_2its'
    )
    
    # Connexion SQLite3
    sqlite_conn = sqlite3.connect('database/uist_2its.db')
    sqlite_conn.execute('PRAGMA foreign_keys = ON')
    
    # Tables à migrer dans l'ordre (respects contraintes FK)
    tables = [
        'Utilisateurs',
        'Enseignants',
        'Etudiants',
        'Parents',
        'Filieres',
        'Salles',
        'Cours',
        'EmploiDuTemps',
        'Notes',
        'Presences',
        'Bulletins',
        'Conflits',
        'ImportNotes',
        'StatutsEnseignants',
        'Messages',
        'UsageAudit',
        'ActiviteUtilisateurs',
        'NotificationsWorkflow',
        'BlocagesWorkflow',
        'UtilisateursActifs'
    ]
    
    for table in tables:
        print(f"Migration de {table}...")
        migrer_table(mysql_conn, sqlite_conn, table)
    
    mysql_conn.close()
    sqlite_conn.commit()
    sqlite_conn.close()
    
    print("✅ Migration terminée avec succès!")

def migrer_table(mysql_conn, sqlite_conn, table_name):
    """Migre une table spécifique"""
    mysql_cursor = mysql_conn.cursor(dictionary=True)
    sqlite_cursor = sqlite_conn.cursor()
    
    # Lire les données de MySQL
    mysql_cursor.execute(f"SELECT * FROM {table_name}")
    rows = mysql_cursor.fetchall()
    
    if not rows:
        print(f"  ⚠️ {table_name} vide")
        return
    
    # Préparer l'insertion SQLite
    columns = rows[0].keys()
    placeholders = ', '.join(['?' for _ in columns])
    insert_sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
    
    # Insérer les données
    for row in rows:
        values = tuple(row.values())
        try:
            sqlite_cursor.execute(insert_sql, values)
        except sqlite3.IntegrityError as e:
            print(f"  ⚠️ Erreur insertion {table_name}: {e}")
    
    print(f"  ✅ {len(rows)} lignes migrées")
    mysql_cursor.close()

if __name__ == '__main__':
    migrer_mysql_vers_sqlite()
```

---

## 📊 Structure de la Base de Données

### Schéma Complet SQLite3

Fichier: `database/schema_sqlite.sql`

### Tables Principales

#### 1. Utilisateurs (Table Centrale)

```sql
CREATE TABLE Utilisateurs (
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

CREATE INDEX idx_utilisateurs_matricule ON Utilisateurs(matricule);
CREATE INDEX idx_utilisateurs_role ON Utilisateurs(role);
CREATE INDEX idx_utilisateurs_email ON Utilisateurs(email);
```

**Description:**
- **Rôles hiérarchiques:** SUPER_ADMIN > ADMIN > DIRECTEUR > GESTIONNAIRES > ENSEIGNANT/ETUDIANT/PARENT
- **Matricule:** Auto-généré (format: ENS001, ETU001, etc.)
- **Actif:** 1 = actif, 0 = désactivé

#### 2. Enseignants

```sql
CREATE TABLE Enseignants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    utilisateur_id INTEGER NOT NULL UNIQUE,
    specialite VARCHAR(100),
    grade VARCHAR(50),
    departement VARCHAR(100),
    statut_emploi TEXT CHECK(statut_emploi IN ('PERMANENT', 'CONTRACTUEL', 'VACATAIRE')) DEFAULT 'CONTRACTUEL',
    date_embauche DATE,
    FOREIGN KEY (utilisateur_id) REFERENCES Utilisateurs(id) ON DELETE CASCADE
);

CREATE INDEX idx_enseignants_utilisateur ON Enseignants(utilisateur_id);
CREATE INDEX idx_enseignants_statut ON Enseignants(statut_emploi);
```

#### 3. Étudiants

```sql
CREATE TABLE Etudiants (
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

CREATE INDEX idx_etudiants_utilisateur ON Etudiants(utilisateur_id);
CREATE INDEX idx_etudiants_filiere ON Etudiants(filiere_id);
CREATE INDEX idx_etudiants_niveau ON Etudiants(niveau);
```

#### 4. Parents

```sql
CREATE TABLE Parents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    utilisateur_id INTEGER NOT NULL,
    etudiant_id INTEGER NOT NULL,
    lien_parente TEXT CHECK(lien_parente IN ('PERE', 'MERE', 'TUTEUR', 'AUTRE')) DEFAULT 'TUTEUR',
    profession VARCHAR(100),
    PRIMARY KEY (utilisateur_id, etudiant_id),
    FOREIGN KEY (utilisateur_id) REFERENCES Utilisateurs(id) ON DELETE CASCADE,
    FOREIGN KEY (etudiant_id) REFERENCES Etudiants(id) ON DELETE CASCADE
);

CREATE INDEX idx_parents_etudiant ON Parents(etudiant_id);
```

#### 5. Filières

```sql
CREATE TABLE Filieres (
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

CREATE INDEX idx_filieres_code ON Filieres(code);
```

#### 6. Cours

```sql
CREATE TABLE Cours (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code VARCHAR(20) UNIQUE NOT NULL,
    nom VARCHAR(200) NOT NULL,
    description TEXT,
    credits INTEGER DEFAULT 3,
    heures_cm INTEGER DEFAULT 0,
    heures_td INTEGER DEFAULT 0,
    heures_tp INTEGER DEFAULT 0,
    filiere_id INTEGER NOT NULL,
    niveau TEXT CHECK(niveau IN ('L1', 'L2', 'L3', 'M1', 'M2')) NOT NULL,
    semestre INTEGER CHECK(semestre IN (1, 2)) NOT NULL,
    enseignant_id INTEGER,
    actif INTEGER DEFAULT 1,
    FOREIGN KEY (filiere_id) REFERENCES Filieres(id) ON DELETE CASCADE,
    FOREIGN KEY (enseignant_id) REFERENCES Enseignants(id) ON DELETE SET NULL
);

CREATE INDEX idx_cours_filiere ON Cours(filiere_id);
CREATE INDEX idx_cours_enseignant ON Cours(enseignant_id);
CREATE INDEX idx_cours_niveau_semestre ON Cours(niveau, semestre);
```

#### 7. Salles

```sql
CREATE TABLE Salles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code VARCHAR(20) UNIQUE NOT NULL,
    nom VARCHAR(100) NOT NULL,
    batiment VARCHAR(50),
    capacite INTEGER DEFAULT 0,
    type_salle TEXT CHECK(type_salle IN ('AMPHITHEATRE', 'TD', 'TP', 'AUTRE')) DEFAULT 'TD',
    equipements TEXT,
    disponible INTEGER DEFAULT 1
);

CREATE INDEX idx_salles_type ON Salles(type_salle);
CREATE INDEX idx_salles_disponible ON Salles(disponible);
```

#### 8. Emploi du Temps

```sql
CREATE TABLE EmploiDuTemps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cours_id INTEGER NOT NULL,
    salle_id INTEGER,
    enseignant_id INTEGER,
    jour_semaine TEXT CHECK(jour_semaine IN ('LUNDI', 'MARDI', 'MERCREDI', 'JEUDI', 'VENDREDI', 'SAMEDI')) NOT NULL,
    heure_debut TIME NOT NULL,
    heure_fin TIME NOT NULL,
    type_cours TEXT CHECK(type_cours IN ('CM', 'TD', 'TP')) NOT NULL,
    semestre INTEGER CHECK(semestre IN (1, 2)) NOT NULL,
    annee_academique VARCHAR(9) NOT NULL,
    recurrent INTEGER DEFAULT 1,
    actif INTEGER DEFAULT 1,
    FOREIGN KEY (cours_id) REFERENCES Cours(id) ON DELETE CASCADE,
    FOREIGN KEY (salle_id) REFERENCES Salles(id) ON DELETE SET NULL,
    FOREIGN KEY (enseignant_id) REFERENCES Enseignants(id) ON DELETE SET NULL
);

CREATE INDEX idx_edt_cours ON EmploiDuTemps(cours_id);
CREATE INDEX idx_edt_enseignant ON EmploiDuTemps(enseignant_id);
CREATE INDEX idx_edt_salle ON EmploiDuTemps(salle_id);
CREATE INDEX idx_edt_jour ON EmploiDuTemps(jour_semaine);
```

#### 9. Notes

```sql
CREATE TABLE Notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    etudiant_id INTEGER NOT NULL,
    cours_id INTEGER NOT NULL,
    type_evaluation TEXT CHECK(type_evaluation IN ('CC', 'TP', 'EXAMEN', 'PROJET')) NOT NULL,
    note DECIMAL(5,2) CHECK(note >= 0 AND note <= 20),
    coefficient INTEGER DEFAULT 1,
    semestre INTEGER CHECK(semestre IN (1, 2)) NOT NULL,
    annee_academique VARCHAR(9) NOT NULL,
    enseignant_id INTEGER,
    date_saisie DATETIME DEFAULT CURRENT_TIMESTAMP,
    validee INTEGER DEFAULT 0,
    date_validation DATETIME,
    validateur_id INTEGER,
    commentaire TEXT,
    FOREIGN KEY (etudiant_id) REFERENCES Etudiants(id) ON DELETE CASCADE,
    FOREIGN KEY (cours_id) REFERENCES Cours(id) ON DELETE CASCADE,
    FOREIGN KEY (enseignant_id) REFERENCES Enseignants(id) ON DELETE SET NULL,
    FOREIGN KEY (validateur_id) REFERENCES Utilisateurs(id) ON DELETE SET NULL
);

CREATE INDEX idx_notes_etudiant ON Notes(etudiant_id);
CREATE INDEX idx_notes_cours ON Notes(cours_id);
CREATE INDEX idx_notes_validee ON Notes(validee);
CREATE INDEX idx_notes_annee_semestre ON Notes(annee_academique, semestre);
```

#### 10. Présences

```sql
CREATE TABLE Presences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    etudiant_id INTEGER NOT NULL,
    creneau_id INTEGER NOT NULL,
    date_cours DATE NOT NULL,
    present INTEGER DEFAULT 0,
    justifie INTEGER DEFAULT 0,
    motif_absence TEXT,
    date_marquage DATETIME DEFAULT CURRENT_TIMESTAMP,
    marquee_par INTEGER,
    FOREIGN KEY (etudiant_id) REFERENCES Etudiants(id) ON DELETE CASCADE,
    FOREIGN KEY (creneau_id) REFERENCES EmploiDuTemps(id) ON DELETE CASCADE,
    FOREIGN KEY (marquee_par) REFERENCES Utilisateurs(id) ON DELETE SET NULL
);

CREATE INDEX idx_presences_etudiant ON Presences(etudiant_id);
CREATE INDEX idx_presences_creneau ON Presences(creneau_id);
CREATE INDEX idx_presences_date ON Presences(date_cours);
```

#### 11. Bulletins

```sql
CREATE TABLE Bulletins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    etudiant_id INTEGER NOT NULL,
    semestre INTEGER CHECK(semestre IN (1, 2)) NOT NULL,
    annee_academique VARCHAR(9) NOT NULL,
    moyenne_generale DECIMAL(5,2),
    credits_obtenus INTEGER DEFAULT 0,
    rang_filiere INTEGER,
    total_etudiants INTEGER,
    decision TEXT CHECK(decision IN ('ADMIS', 'REDOUBLE', 'EXCLU')) DEFAULT 'ADMIS',
    chemin_pdf VARCHAR(255),
    date_generation DATETIME DEFAULT CURRENT_TIMESTAMP,
    genere_par INTEGER,
    UNIQUE(etudiant_id, semestre, annee_academique),
    FOREIGN KEY (etudiant_id) REFERENCES Etudiants(id) ON DELETE CASCADE,
    FOREIGN KEY (genere_par) REFERENCES Utilisateurs(id) ON DELETE SET NULL
);

CREATE INDEX idx_bulletins_etudiant ON Bulletins(etudiant_id);
CREATE INDEX idx_bulletins_annee_semestre ON Bulletins(annee_academique, semestre);
```

### Tables de Gestion

#### 12. Conflits EDT

```sql
CREATE TABLE Conflits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type_conflit TEXT CHECK(type_conflit IN (
        'ENSEIGNANT_DOUBLE', 'SALLE_DOUBLE', 'ETUDIANT_DOUBLE'
    )) NOT NULL,
    creneau1_id INTEGER NOT NULL,
    creneau2_id INTEGER,
    description TEXT,
    severite TEXT CHECK(severite IN ('FAIBLE', 'MOYENNE', 'HAUTE')) DEFAULT 'MOYENNE',
    statut TEXT CHECK(statut IN ('ACTIF', 'RESOLU', 'IGNORE')) DEFAULT 'ACTIF',
    date_detection DATETIME DEFAULT CURRENT_TIMESTAMP,
    date_resolution DATETIME,
    resolu_par INTEGER,
    FOREIGN KEY (creneau1_id) REFERENCES EmploiDuTemps(id) ON DELETE CASCADE,
    FOREIGN KEY (creneau2_id) REFERENCES EmploiDuTemps(id) ON DELETE CASCADE,
    FOREIGN KEY (resolu_par) REFERENCES Utilisateurs(id) ON DELETE SET NULL
);

CREATE INDEX idx_conflits_statut ON Conflits(statut);
CREATE INDEX idx_conflits_type ON Conflits(type_conflit);
```

#### 13. Import Notes

```sql
CREATE TABLE ImportNotes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fichier_nom VARCHAR(255) NOT NULL,
    cours_id INTEGER,
    type_evaluation TEXT CHECK(type_evaluation IN ('CC', 'TP', 'EXAMEN', 'PROJET')),
    importe_par INTEGER NOT NULL,
    date_import DATETIME DEFAULT CURRENT_TIMESTAMP,
    statut TEXT CHECK(statut IN ('EN_COURS', 'TERMINE', 'ERREUR')) DEFAULT 'EN_COURS',
    lignes_total INTEGER DEFAULT 0,
    lignes_importees INTEGER DEFAULT 0,
    lignes_erreur INTEGER DEFAULT 0,
    rapport_erreurs TEXT,
    FOREIGN KEY (cours_id) REFERENCES Cours(id) ON DELETE SET NULL,
    FOREIGN KEY (importe_par) REFERENCES Utilisateurs(id) ON DELETE CASCADE
);

CREATE INDEX idx_import_notes_statut ON ImportNotes(statut);
CREATE INDEX idx_import_notes_date ON ImportNotes(date_import);
```

#### 14. Statuts Enseignants

```sql
CREATE TABLE StatutsEnseignants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    enseignant_id INTEGER NOT NULL,
    disponible INTEGER DEFAULT 1,
    jours_indisponibles TEXT,
    heures_indisponibles TEXT,
    charge_horaire_max INTEGER DEFAULT 40,
    charge_horaire_actuelle INTEGER DEFAULT 0,
    date_maj DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (enseignant_id) REFERENCES Enseignants(id) ON DELETE CASCADE
);

CREATE INDEX idx_statuts_enseignant ON StatutsEnseignants(enseignant_id);
```

#### 15. Messages

```sql
CREATE TABLE Messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    expediteur_id INTEGER NOT NULL,
    destinataire_id INTEGER NOT NULL,
    sujet VARCHAR(200) NOT NULL,
    contenu TEXT NOT NULL,
    lu INTEGER DEFAULT 0,
    date_envoi DATETIME DEFAULT CURRENT_TIMESTAMP,
    date_lecture DATETIME,
    archive INTEGER DEFAULT 0,
    FOREIGN KEY (expediteur_id) REFERENCES Utilisateurs(id) ON DELETE CASCADE,
    FOREIGN KEY (destinataire_id) REFERENCES Utilisateurs(id) ON DELETE CASCADE
);

CREATE INDEX idx_messages_destinataire ON Messages(destinataire_id);
CREATE INDEX idx_messages_lu ON Messages(lu);
```

### Tables d'Audit et Monitoring

#### 16. Audit Usage

```sql
CREATE TABLE UsageAudit (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    utilisateur_id INTEGER,
    action_type VARCHAR(50) NOT NULL,
    action_description TEXT,
    ip_address VARCHAR(45),
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (utilisateur_id) REFERENCES Utilisateurs(id) ON DELETE SET NULL
);

CREATE INDEX idx_audit_utilisateur ON UsageAudit(utilisateur_id);
CREATE INDEX idx_audit_action ON UsageAudit(action_type);
CREATE INDEX idx_audit_timestamp ON UsageAudit(timestamp);
```

#### 17. Activité Utilisateurs

```sql
CREATE TABLE ActiviteUtilisateurs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    utilisateur_id INTEGER NOT NULL,
    type_activite TEXT CHECK(type_activite IN ('CONNEXION', 'DECONNEXION', 'ACTION', 'CONSULTATION')) NOT NULL,
    action_detail VARCHAR(255),
    ip_address VARCHAR(45),
    user_agent TEXT,
    duree_session INTEGER,
    timestamp_debut DATETIME DEFAULT CURRENT_TIMESTAMP,
    timestamp_fin DATETIME,
    FOREIGN KEY (utilisateur_id) REFERENCES Utilisateurs(id) ON DELETE CASCADE
);

CREATE INDEX idx_activite_utilisateur ON ActiviteUtilisateurs(utilisateur_id);
CREATE INDEX idx_activite_type ON ActiviteUtilisateurs(type_activite);
```

#### 18. Notifications Workflow

```sql
CREATE TABLE NotificationsWorkflow (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    utilisateur_id INTEGER NOT NULL,
    titre VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    type_notification TEXT CHECK(type_notification IN (
        'INFO', 'ALERTE', 'BLOCAGE', 'VALIDATION', 'RAPPEL'
    )) DEFAULT 'INFO',
    priorite TEXT CHECK(priorite IN ('BASSE', 'NORMALE', 'HAUTE', 'URGENTE')) DEFAULT 'NORMALE',
    lu INTEGER DEFAULT 0,
    archivee INTEGER DEFAULT 0,
    date_creation DATETIME DEFAULT CURRENT_TIMESTAMP,
    date_lecture DATETIME,
    lien_action VARCHAR(255),
    FOREIGN KEY (utilisateur_id) REFERENCES Utilisateurs(id) ON DELETE CASCADE
);

CREATE INDEX idx_notif_utilisateur ON NotificationsWorkflow(utilisateur_id);
CREATE INDEX idx_notif_lu ON NotificationsWorkflow(lu);
CREATE INDEX idx_notif_priorite ON NotificationsWorkflow(priorite);
```

#### 19. Blocages Workflow

```sql
CREATE TABLE BlocagesWorkflow (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type_blocage TEXT CHECK(type_blocage IN (
        'NOTES_NON_VALIDEES', 'CONFLIT_EDT', 'SALLE_INDISPONIBLE',
        'ENSEIGNANT_INDISPONIBLE', 'CREDITS_INSUFFISANTS'
    )) NOT NULL,
    description TEXT NOT NULL,
    reference_id INTEGER,
    reference_table VARCHAR(50),
    severite TEXT CHECK(severite IN ('FAIBLE', 'MOYENNE', 'HAUTE', 'CRITIQUE')) DEFAULT 'MOYENNE',
    statut TEXT CHECK(statut IN ('ACTIF', 'RESOLU', 'IGNORE')) DEFAULT 'ACTIF',
    createur_id INTEGER,
    date_creation DATETIME DEFAULT CURRENT_TIMESTAMP,
    date_resolution DATETIME,
    resolu_par INTEGER,
    commentaire_resolution TEXT,
    FOREIGN KEY (createur_id) REFERENCES Utilisateurs(id) ON DELETE SET NULL,
    FOREIGN KEY (resolu_par) REFERENCES Utilisateurs(id) ON DELETE SET NULL
);

CREATE INDEX idx_blocages_statut ON BlocagesWorkflow(statut);
CREATE INDEX idx_blocages_type ON BlocagesWorkflow(type_blocage);
```

#### 20. Utilisateurs Actifs (Vue temps réel)

```sql
CREATE TABLE UtilisateursActifs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    utilisateur_id INTEGER NOT NULL UNIQUE,
    role VARCHAR(50),
    derniere_activite DATETIME DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45),
    session_id VARCHAR(255),
    FOREIGN KEY (utilisateur_id) REFERENCES Utilisateurs(id) ON DELETE CASCADE
);

CREATE INDEX idx_actifs_utilisateur ON UtilisateursActifs(utilisateur_id);
CREATE INDEX idx_actifs_activite ON UtilisateursActifs(derniere_activite);
```

---

## 🔧 Utilisation avec Python

### Connexion à la Base

```python
# app/db.py
import sqlite3
from flask import g, current_app

def obtenir_connexion():
    """Obtient la connexion SQLite3"""
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DB_PATH'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
        g.db.execute('PRAGMA foreign_keys = ON')
    return g.db

def executer_requete(requete, parametres=None, obtenir_resultats=False):
    """Exécute une requête SQL"""
    try:
        db = obtenir_connexion()
        cur = db.execute(requete, parametres or ())
        
        if obtenir_resultats:
            return [dict(row) for row in cur.fetchall()]
        else:
            db.commit()
            return cur.lastrowid if cur.lastrowid > 0 else cur.rowcount
    except sqlite3.Error as e:
        print(f"Erreur SQL: {e}")
        db.rollback()
        return None if obtenir_resultats else 0
```

### Exemples de Requêtes

```python
# SELECT
utilisateurs = executer_requete(
    "SELECT * FROM Utilisateurs WHERE role = ? AND actif = 1",
    ('ETUDIANT',),
    obtenir_resultats=True
)

# INSERT
user_id = executer_requete(
    """INSERT INTO Utilisateurs (matricule, nom, prenom, email, mot_de_passe, role)
       VALUES (?, ?, ?, ?, ?, ?)""",
    ('ETU001', 'Dupont', 'Jean', 'jean@email.com', 'hash...', 'ETUDIANT')
)

# UPDATE
lignes = executer_requete(
    "UPDATE Utilisateurs SET actif = 0 WHERE id = ?",
    (user_id,)
)

# DELETE
executer_requete("DELETE FROM Notes WHERE id = ?", (note_id,))
```

---

## 📈 Optimisations et Bonnes Pratiques

### Indexes

✅ **Créés automatiquement:**
- Index sur toutes les clés primaires
- Index sur toutes les clés étrangères
- Index sur colonnes fréquemment filtrées (role, actif, validee, etc.)

### Transactions

```python
# Toujours utiliser des transactions pour plusieurs opérations
db = obtenir_connexion()
try:
    db.execute("INSERT INTO Utilisateurs ...")
    db.execute("INSERT INTO Etudiants ...")
    db.commit()
except:
    db.rollback()
    raise
```

### Requêtes Préparées

✅ **Toujours utiliser des paramètres:**
```python
# BON
executer_requete("SELECT * FROM Users WHERE id = ?", (user_id,))

# MAUVAIS (injection SQL!)
executer_requete(f"SELECT * FROM Users WHERE id = {user_id}")
```

### Pagination

```python
def lister_avec_pagination(page=1, par_page=20):
    """Liste avec pagination"""
    offset = (page - 1) * par_page
    return executer_requete(
        "SELECT * FROM Utilisateurs LIMIT ? OFFSET ?",
        (par_page, offset),
        obtenir_resultats=True
    )
```

---

## 🛠️ Maintenance

### Backup Automatique

```python
# scripts/backup_db.py
import shutil
from datetime import datetime

def backup_database():
    """Crée un backup de la base"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    source = 'database/uist_2its.db'
    destination = f'backups/uist_2its_{timestamp}.db'
    shutil.copy2(source, destination)
    print(f"✅ Backup créé: {destination}")
```

### Optimisation

```python
# Exécuter périodiquement
def optimiser_database():
    """Optimise la base de données"""
    db = obtenir_connexion()
    db.execute('VACUUM')  # Récupère espace
    db.execute('ANALYZE')  # Met à jour statistiques
    db.commit()
```

### Vérification Intégrité

```python
def verifier_integrite():
    """Vérifie l'intégrité de la base"""
    db = obtenir_connexion()
    result = db.execute('PRAGMA integrity_check').fetchone()
    return result[0] == 'ok'
```

---

## 📊 Statistiques et Requêtes Utiles

### Nombre d'utilisateurs par rôle

```sql
SELECT role, COUNT(*) as nombre
FROM Utilisateurs
WHERE actif = 1
GROUP BY role
ORDER BY nombre DESC;
```

### Moyenne générale par filière

```sql
SELECT f.nom, AVG(b.moyenne_generale) as moyenne
FROM Bulletins b
JOIN Etudiants e ON b.etudiant_id = e.id
JOIN Filieres f ON e.filiere_id = f.id
WHERE b.annee_academique = '2025-2026'
GROUP BY f.id
ORDER BY moyenne DESC;
```

### Taux de présence par cours

```sql
SELECT c.nom,
       COUNT(*) as total,
       SUM(p.present) as presents,
       ROUND(SUM(p.present) * 100.0 / COUNT(*), 2) as taux_presence
FROM Presences p
JOIN EmploiDuTemps edt ON p.creneau_id = edt.id
JOIN Cours c ON edt.cours_id = c.id
GROUP BY c.id
ORDER BY taux_presence DESC;
```

---

**Version:** 1.0  
**Date:** Janvier 2026  
**Dernière mise à jour:** Janvier 2026