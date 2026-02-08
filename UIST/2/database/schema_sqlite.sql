-- ==========================================================
-- UIST-2ITS : SCHÉMA SQLite3 COMPLET
-- Basé sur la documentation UIST-2ITS.txt
-- ==========================================================

-- ==========================================================
-- COUCHE GOUVERNANCE
-- ==========================================================

CREATE TABLE IF NOT EXISTS utilisateurs (
    id_user INTEGER PRIMARY KEY AUTOINCREMENT,
    matricule VARCHAR(20) UNIQUE NOT NULL,
    nom VARCHAR(100) NOT NULL,
    prenom VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    mot_de_passe VARCHAR(255) NOT NULL,
    role TEXT CHECK(role IN (
        'SUPER_ADMIN', 
        'DIRECTEUR', 
        'GESTION_1', 
        'GESTION_2', 
        'GESTION_3', 
        'ENSEIGNANT', 
        'ETUDIANT', 
        'PARENT'
    )) NOT NULL,
    est_actif INTEGER DEFAULT 1,
    date_creation DATETIME DEFAULT CURRENT_TIMESTAMP,
    derniere_connexion DATETIME NULL
);

CREATE INDEX IF NOT EXISTS idx_utilisateurs_role ON utilisateurs(role);
CREATE INDEX IF NOT EXISTS idx_utilisateurs_email ON utilisateurs(email);
CREATE INDEX IF NOT EXISTS idx_utilisateurs_matricule ON utilisateurs(matricule);

CREATE TABLE IF NOT EXISTS audit_usage (
    id_audit INTEGER PRIMARY KEY AUTOINCREMENT,
    id_user INTEGER,
    action VARCHAR(255) NOT NULL,
    table_affectee VARCHAR(50),
    id_enregistrement INTEGER,
    details TEXT,
    ip_address VARCHAR(45),
    date_action DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_user) REFERENCES utilisateurs(id_user) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_audit_user_date ON audit_usage(id_user, date_action);

-- ==========================================================
-- POLE GESTION 1 : Infrastructure
-- ==========================================================

CREATE TABLE IF NOT EXISTS salles (
    id_salle INTEGER PRIMARY KEY AUTOINCREMENT,
    nom_salle VARCHAR(50) NOT NULL,
    capacite INTEGER NOT NULL CHECK (capacite > 0),
    equipements TEXT,
    batiment VARCHAR(50),
    est_active INTEGER DEFAULT 1,
    UNIQUE(nom_salle, batiment)
);

CREATE TABLE IF NOT EXISTS filieres (
    id_filiere INTEGER PRIMARY KEY AUTOINCREMENT,
    code_filiere VARCHAR(20) UNIQUE NOT NULL,
    nom_filiere VARCHAR(100) NOT NULL,
    niveau VARCHAR(20) NOT NULL,
    effectif_prevu INTEGER DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_filieres_niveau ON filieres(niveau);

CREATE TABLE IF NOT EXISTS enseignants (
    id_enseignant INTEGER PRIMARY KEY AUTOINCREMENT,
    id_user INTEGER UNIQUE NOT NULL,
    specialite VARCHAR(150),
    telephone VARCHAR(20),
    total_heures_prevues DECIMAL(6,2) DEFAULT 0,
    total_heures_effectuees DECIMAL(6,2) DEFAULT 0,
    FOREIGN KEY (id_user) REFERENCES utilisateurs(id_user) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS cours (
    id_cours INTEGER PRIMARY KEY AUTOINCREMENT,
    code_cours VARCHAR(20) UNIQUE NOT NULL,
    libelle VARCHAR(150) NOT NULL,
    credit INTEGER DEFAULT 1 CHECK (credit BETWEEN 1 AND 10),
    id_filiere INTEGER NOT NULL,
    coefficient DECIMAL(3,2) DEFAULT 1.00,
    FOREIGN KEY (id_filiere) REFERENCES filieres(id_filiere) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_cours_filiere ON cours(id_filiere);

CREATE TABLE IF NOT EXISTS disponibilites_enseignants (
    id_dispo INTEGER PRIMARY KEY AUTOINCREMENT,
    id_enseignant INTEGER NOT NULL,
    jour TEXT CHECK(jour IN ('Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi')) NOT NULL,
    heure_debut TIME NOT NULL,
    heure_fin TIME NOT NULL,
    est_disponible INTEGER DEFAULT 1,
    type_contrainte TEXT CHECK(type_contrainte IN ('Fixe', 'Prefere', 'Exceptionnel')) DEFAULT 'Fixe',
    motif TEXT,
    FOREIGN KEY (id_enseignant) REFERENCES enseignants(id_enseignant) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_dispo_enseignant_jour ON disponibilites_enseignants(id_enseignant, jour);

-- ==========================================================
-- POLE GESTION 2 & 3 : Scolarité et Suivi
-- ==========================================================

CREATE TABLE IF NOT EXISTS etudiants (
    id_etudiant INTEGER PRIMARY KEY AUTOINCREMENT,
    id_user INTEGER UNIQUE NOT NULL,
    id_filiere INTEGER NOT NULL,
    date_naissance DATE,
    numero_cni VARCHAR(50),
    adresse TEXT,
    telephone VARCHAR(20),
    FOREIGN KEY (id_user) REFERENCES utilisateurs(id_user) ON DELETE CASCADE,
    FOREIGN KEY (id_filiere) REFERENCES filieres(id_filiere) ON DELETE RESTRICT
);

CREATE INDEX IF NOT EXISTS idx_etudiants_filiere ON etudiants(id_filiere);

CREATE TABLE IF NOT EXISTS parents (
    id_parent INTEGER PRIMARY KEY AUTOINCREMENT,
    id_user INTEGER UNIQUE NOT NULL,
    profession VARCHAR(100),
    telephone VARCHAR(20),
    FOREIGN KEY (id_user) REFERENCES utilisateurs(id_user) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS parente_liaison (
    id_liaison INTEGER PRIMARY KEY AUTOINCREMENT,
    id_parent INTEGER NOT NULL,
    id_etudiant INTEGER NOT NULL,
    lien_parente TEXT CHECK(lien_parente IN ('Père', 'Mère', 'Tuteur', 'Autre')) DEFAULT 'Tuteur',
    FOREIGN KEY (id_parent) REFERENCES parents(id_parent) ON DELETE CASCADE,
    FOREIGN KEY (id_etudiant) REFERENCES etudiants(id_etudiant) ON DELETE CASCADE,
    UNIQUE(id_parent, id_etudiant, lien_parente)
);

CREATE INDEX IF NOT EXISTS idx_parente_etudiant ON parente_liaison(id_etudiant);
CREATE INDEX IF NOT EXISTS idx_parente_parent ON parente_liaison(id_parent);

-- ==========================================================
-- EMPLOI DU TEMPS
-- ==========================================================

CREATE TABLE IF NOT EXISTS emploi_du_temps (
    id_edt INTEGER PRIMARY KEY AUTOINCREMENT,
    id_cours INTEGER NOT NULL,
    id_enseignant INTEGER NOT NULL,
    id_salle INTEGER NOT NULL,
    jour TEXT CHECK(jour IN ('Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi')) NOT NULL,
    heure_debut TIME NOT NULL,
    heure_fin TIME NOT NULL,
    semaine_numero INTEGER NOT NULL CHECK (semaine_numero BETWEEN 1 AND 52),
    annee_academique VARCHAR(9) NOT NULL,
    type_creneau TEXT CHECK(type_creneau IN ('Cours', 'TD', 'TP', 'Examen')) DEFAULT 'Cours',
    FOREIGN KEY (id_cours) REFERENCES cours(id_cours) ON DELETE CASCADE,
    FOREIGN KEY (id_enseignant) REFERENCES enseignants(id_enseignant) ON DELETE RESTRICT,
    FOREIGN KEY (id_salle) REFERENCES salles(id_salle) ON DELETE RESTRICT
);

CREATE INDEX IF NOT EXISTS idx_edt_semaine_jour ON emploi_du_temps(semaine_numero, jour);
CREATE INDEX IF NOT EXISTS idx_edt_enseignant ON emploi_du_temps(id_enseignant);
CREATE INDEX IF NOT EXISTS idx_edt_salle ON emploi_du_temps(id_salle);
CREATE INDEX IF NOT EXISTS idx_edt_cours ON emploi_du_temps(id_cours);

-- ==========================================================
-- PRESENCES
-- ==========================================================

CREATE TABLE IF NOT EXISTS presences (
    id_presence INTEGER PRIMARY KEY AUTOINCREMENT,
    id_edt INTEGER NOT NULL,
    id_etudiant INTEGER,
    id_enseignant INTEGER,
    statut TEXT CHECK(statut IN ('Present', 'Absent', 'Retard', 'Justifie')) DEFAULT 'Absent',
    date_pointage DATE NOT NULL,
    commentaire TEXT,
    FOREIGN KEY (id_edt) REFERENCES emploi_du_temps(id_edt) ON DELETE CASCADE,
    FOREIGN KEY (id_etudiant) REFERENCES etudiants(id_etudiant) ON DELETE CASCADE,
    FOREIGN KEY (id_enseignant) REFERENCES enseignants(id_enseignant) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_presences_edt ON presences(id_edt);
CREATE INDEX IF NOT EXISTS idx_presences_etudiant ON presences(id_etudiant);
CREATE INDEX IF NOT EXISTS idx_presences_date ON presences(date_pointage);

-- ==========================================================
-- NOTES ET EVALUATIONS
-- ==========================================================

CREATE TABLE IF NOT EXISTS notes (
    id_note INTEGER PRIMARY KEY AUTOINCREMENT,
    id_etudiant INTEGER NOT NULL,
    id_cours INTEGER NOT NULL,
    valeur_note DECIMAL(5,2) CHECK(valeur_note >= 0 AND valeur_note <= 20),
    type_evaluation TEXT CHECK(type_evaluation IN ('CC', 'TP', 'Examen', 'Projet')) DEFAULT 'CC',
    statut_validation TEXT CHECK(statut_validation IN ('En attente', 'Valide', 'Rejete')) DEFAULT 'En attente',
    id_validateur INTEGER,
    date_saisie DATETIME DEFAULT CURRENT_TIMESTAMP,
    date_validation DATETIME,
    commentaire TEXT,
    FOREIGN KEY (id_etudiant) REFERENCES etudiants(id_etudiant) ON DELETE CASCADE,
    FOREIGN KEY (id_cours) REFERENCES cours(id_cours) ON DELETE CASCADE,
    FOREIGN KEY (id_validateur) REFERENCES utilisateurs(id_user) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_notes_etudiant ON notes(id_etudiant);
CREATE INDEX IF NOT EXISTS idx_notes_cours ON notes(id_cours);
CREATE INDEX IF NOT EXISTS idx_notes_validation ON notes(statut_validation);

CREATE TABLE IF NOT EXISTS bulletins (
    id_bulletin INTEGER PRIMARY KEY AUTOINCREMENT,
    id_etudiant INTEGER NOT NULL,
    annee_academique VARCHAR(9) NOT NULL,
    semestre INTEGER CHECK(semestre IN (1, 2)) NOT NULL,
    moyenne_generale DECIMAL(5,2),
    rang INTEGER,
    total_etudiants INTEGER,
    chemin_pdf VARCHAR(255),
    date_generation DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_etudiant) REFERENCES etudiants(id_etudiant) ON DELETE CASCADE,
    UNIQUE(id_etudiant, annee_academique, semestre)
);

CREATE INDEX IF NOT EXISTS idx_bulletins_etudiant ON bulletins(id_etudiant);

-- ==========================================================
-- IMPORT ET CONFLITS
-- ==========================================================

CREATE TABLE IF NOT EXISTS import_notes (
    id_import INTEGER PRIMARY KEY AUTOINCREMENT,
    nom_fichier VARCHAR(255) NOT NULL,
    id_user INTEGER NOT NULL,
    date_import DATETIME DEFAULT CURRENT_TIMESTAMP,
    lignes_totales INTEGER DEFAULT 0,
    lignes_importees INTEGER DEFAULT 0,
    lignes_erreurs INTEGER DEFAULT 0,
    statut TEXT CHECK(statut IN ('En cours', 'Termine', 'Erreur')) DEFAULT 'En cours',
    rapport_erreurs TEXT,
    FOREIGN KEY (id_user) REFERENCES utilisateurs(id_user) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS conflits (
    id_conflit INTEGER PRIMARY KEY AUTOINCREMENT,
    type_conflit TEXT CHECK(type_conflit IN (
        'Enseignant_Double', 'Salle_Double', 'Filiere_Double'
    )) NOT NULL,
    id_edt_1 INTEGER NOT NULL,
    id_edt_2 INTEGER,
    description TEXT,
    severite TEXT CHECK(severite IN ('Faible', 'Moyenne', 'Haute')) DEFAULT 'Moyenne',
    statut TEXT CHECK(statut IN ('Actif', 'Resolu', 'Ignore')) DEFAULT 'Actif',
    date_detection DATETIME DEFAULT CURRENT_TIMESTAMP,
    date_resolution DATETIME,
    id_resolveur INTEGER,
    FOREIGN KEY (id_edt_1) REFERENCES emploi_du_temps(id_edt) ON DELETE CASCADE,
    FOREIGN KEY (id_edt_2) REFERENCES emploi_du_temps(id_edt) ON DELETE CASCADE,
    FOREIGN KEY (id_resolveur) REFERENCES utilisateurs(id_user) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_conflits_statut ON conflits(statut);
CREATE INDEX IF NOT EXISTS idx_conflits_type ON conflits(type_conflit);

-- ==========================================================
-- MESSAGERIE
-- ==========================================================

CREATE TABLE IF NOT EXISTS messages (
    id_message INTEGER PRIMARY KEY AUTOINCREMENT,
    id_expediteur INTEGER NOT NULL,
    id_destinataire INTEGER NOT NULL,
    sujet VARCHAR(200),
    contenu TEXT NOT NULL,
    lu INTEGER DEFAULT 0,
    date_envoi DATETIME DEFAULT CURRENT_TIMESTAMP,
    date_lecture DATETIME,
    FOREIGN KEY (id_expediteur) REFERENCES utilisateurs(id_user) ON DELETE CASCADE,
    FOREIGN KEY (id_destinataire) REFERENCES utilisateurs(id_user) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_messages_destinataire ON messages(id_destinataire);
CREATE INDEX IF NOT EXISTS idx_messages_lu ON messages(lu);