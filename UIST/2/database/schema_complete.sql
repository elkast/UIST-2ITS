-- ==========================================================
-- UIST-2ITS : SCHÉMA COMPLET SQLite3
-- ==========================================================

PRAGMA foreign_keys = ON;

-- ==========================================================
-- COUCHE GOUVERNANCE
-- ==========================================================

CREATE TABLE IF NOT EXISTS utilisateurs (
    id_user INTEGER PRIMARY KEY AUTOINCREMENT,
    matricule TEXT UNIQUE NOT NULL,
    nom TEXT NOT NULL,
    prenom TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    mot_de_passe TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('SUPER_ADMIN', 'DIRECTEUR', 'GESTION_1', 'GESTION_2', 'GESTION_3', 'ENSEIGNANT', 'ETUDIANT', 'PARENT')),
    est_actif INTEGER DEFAULT 1,
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    derniere_connexion TIMESTAMP NULL
);

CREATE INDEX IF NOT EXISTS idx_utilisateurs_role ON utilisateurs(role);
CREATE INDEX IF NOT EXISTS idx_utilisateurs_email ON utilisateurs(email);

CREATE TABLE IF NOT EXISTS audit_usage (
    id_audit INTEGER PRIMARY KEY AUTOINCREMENT,
    id_user INTEGER,
    action TEXT NOT NULL,
    table_affectee TEXT,
    id_enregistrement INTEGER,
    details TEXT,
    ip_address TEXT,
    date_action TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_user) REFERENCES utilisateurs(id_user) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_audit_user_date ON audit_usage(id_user, date_action);

-- ==========================================================
-- POLE GESTION 1 : Infrastructure
-- ==========================================================

CREATE TABLE IF NOT EXISTS salles (
    id_salle INTEGER PRIMARY KEY AUTOINCREMENT,
    nom_salle TEXT NOT NULL,
    capacite INTEGER NOT NULL CHECK(capacite > 0),
    equipements TEXT,
    batiment TEXT,
    est_active INTEGER DEFAULT 1,
    UNIQUE(nom_salle, batiment)
);

CREATE TABLE IF NOT EXISTS filieres (
    id_filiere INTEGER PRIMARY KEY AUTOINCREMENT,
    code_filiere TEXT UNIQUE NOT NULL,
    nom_filiere TEXT NOT NULL,
    niveau TEXT NOT NULL,
    effectif_prevu INTEGER DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_filieres_niveau ON filieres(niveau);

CREATE TABLE IF NOT EXISTS enseignants (
    id_enseignant INTEGER PRIMARY KEY AUTOINCREMENT,
    id_user INTEGER UNIQUE NOT NULL,
    specialite TEXT,
    telephone TEXT,
    total_heures_prevues REAL DEFAULT 0,
    total_heures_effectuees REAL DEFAULT 0,
    FOREIGN KEY (id_user) REFERENCES utilisateurs(id_user) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS cours (
    id_cours INTEGER PRIMARY KEY AUTOINCREMENT,
    code_cours TEXT UNIQUE NOT NULL,
    libelle TEXT NOT NULL,
    credit INTEGER DEFAULT 1 CHECK(credit BETWEEN 1 AND 10),
    id_filiere INTEGER NOT NULL,
    coefficient REAL DEFAULT 1.00,
    FOREIGN KEY (id_filiere) REFERENCES filieres(id_filiere) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_cours_filiere ON cours(id_filiere);

CREATE TABLE IF NOT EXISTS disponibilites_enseignants (
    id_dispo INTEGER PRIMARY KEY AUTOINCREMENT,
    id_enseignant INTEGER NOT NULL,
    jour TEXT NOT NULL CHECK(jour IN ('Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi')),
    heure_debut TEXT NOT NULL,
    heure_fin TEXT NOT NULL,
    est_disponible INTEGER DEFAULT 1,
    type_contrainte TEXT DEFAULT 'Fixe' CHECK(type_contrainte IN ('Fixe', 'Prefere', 'Exceptionnel')),
    motif TEXT,
    FOREIGN KEY (id_enseignant) REFERENCES enseignants(id_enseignant) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_dispo_enseignant_jour ON disponibilites_enseignants(id_enseignant, jour);

-- ==========================================================
-- POLE GESTION 3 : Planification & Suivi
-- ==========================================================

CREATE TABLE IF NOT EXISTS emploi_du_temps (
    id_edt INTEGER PRIMARY KEY AUTOINCREMENT,
    id_cours INTEGER NOT NULL,
    id_enseignant INTEGER NOT NULL,
    id_salle INTEGER NOT NULL,
    jour TEXT NOT NULL CHECK(jour IN ('Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi')),
    heure_debut TEXT NOT NULL,
    heure_fin TEXT NOT NULL,
    semaine_numero INTEGER NOT NULL CHECK(semaine_numero BETWEEN 1 AND 52),
    annee_academique TEXT NOT NULL,
    type_creneau TEXT DEFAULT 'Cours' CHECK(type_creneau IN ('Cours', 'TD', 'TP', 'Examen')),
    FOREIGN KEY (id_cours) REFERENCES cours(id_cours) ON DELETE CASCADE,
    FOREIGN KEY (id_enseignant) REFERENCES enseignants(id_enseignant) ON DELETE RESTRICT,
    FOREIGN KEY (id_salle) REFERENCES salles(id_salle) ON DELETE RESTRICT
);

CREATE INDEX IF NOT EXISTS idx_edt_semaine_jour ON emploi_du_temps(semaine_numero, jour);
CREATE INDEX IF NOT EXISTS idx_edt_enseignant ON emploi_du_temps(id_enseignant);
CREATE INDEX IF NOT EXISTS idx_edt_salle ON emploi_du_temps(id_salle);

CREATE TABLE IF NOT EXISTS presences (
    id_presence INTEGER PRIMARY KEY AUTOINCREMENT,
    id_edt INTEGER NOT NULL,
    statut TEXT DEFAULT 'Present' CHECK(statut IN ('Present', 'Absent', 'Retard')),
    date_pointage DATE NOT NULL,
    heure_pointage TEXT,
    commentaire TEXT,
    marque_par INTEGER,
    FOREIGN KEY (id_edt) REFERENCES emploi_du_temps(id_edt) ON DELETE CASCADE,
    FOREIGN KEY (marque_par) REFERENCES utilisateurs(id_user) ON DELETE SET NULL,
    UNIQUE(id_edt, date_pointage)
);

CREATE INDEX IF NOT EXISTS idx_presences_date ON presences(date_pointage);

-- ==========================================================
-- POLE GESTION 2 : Scolarité
-- ==========================================================

CREATE TABLE IF NOT EXISTS etudiants (
    id_etudiant INTEGER PRIMARY KEY AUTOINCREMENT,
    id_user INTEGER UNIQUE NOT NULL,
    id_filiere INTEGER NOT NULL,
    date_naissance DATE,
    lieu_naissance TEXT,
    adresse TEXT,
    telephone TEXT,
    date_inscription DATE DEFAULT (DATE('now')),
    FOREIGN KEY (id_user) REFERENCES utilisateurs(id_user) ON DELETE CASCADE,
    FOREIGN KEY (id_filiere) REFERENCES filieres(id_filiere) ON DELETE RESTRICT
);

CREATE INDEX IF NOT EXISTS idx_etudiants_filiere ON etudiants(id_filiere);

CREATE TABLE IF NOT EXISTS parents (
    id_parent INTEGER PRIMARY KEY AUTOINCREMENT,
    id_user INTEGER UNIQUE NOT NULL,
    profession TEXT,
    telephone TEXT,
    adresse TEXT,
    FOREIGN KEY (id_user) REFERENCES utilisateurs(id_user) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS parente_liaison (
    id_liaison INTEGER PRIMARY KEY AUTOINCREMENT,
    id_parent INTEGER NOT NULL,
    id_etudiant INTEGER NOT NULL,
    lien_parente TEXT NOT NULL CHECK(lien_parente IN ('Père', 'Mère', 'Tuteur', 'Autre')),
    est_contact_principal INTEGER DEFAULT 0,
    FOREIGN KEY (id_parent) REFERENCES parents(id_parent) ON DELETE CASCADE,
    FOREIGN KEY (id_etudiant) REFERENCES etudiants(id_etudiant) ON DELETE CASCADE,
    UNIQUE(id_parent, id_etudiant)
);

CREATE TABLE IF NOT EXISTS notes (
    id_note INTEGER PRIMARY KEY AUTOINCREMENT,
    id_etudiant INTEGER NOT NULL,
    id_cours INTEGER NOT NULL,
    valeur_note REAL NOT NULL CHECK(valeur_note BETWEEN 0 AND 20),
    type_evaluation TEXT NOT NULL CHECK(type_evaluation IN ('Devoir', 'Controle', 'Examen', 'TP', 'Projet')),
    coefficient REAL DEFAULT 1.00,
    statut_validation TEXT DEFAULT 'En attente' CHECK(statut_validation IN ('En attente', 'Valide')),
    id_validateur INTEGER,
    date_saisie TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_validation TIMESTAMP NULL,
    commentaire TEXT,
    FOREIGN KEY (id_etudiant) REFERENCES etudiants(id_etudiant) ON DELETE CASCADE,
    FOREIGN KEY (id_cours) REFERENCES cours(id_cours) ON DELETE RESTRICT,
    FOREIGN KEY (id_validateur) REFERENCES utilisateurs(id_user) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_notes_etudiant_cours ON notes(id_etudiant, id_cours);
CREATE INDEX IF NOT EXISTS idx_notes_statut ON notes(statut_validation);

CREATE TABLE IF NOT EXISTS bulletins (
    id_bulletin INTEGER PRIMARY KEY AUTOINCREMENT,
    id_etudiant INTEGER NOT NULL,
    moyenne_generale REAL,
    rang INTEGER,
    semestre INTEGER CHECK(semestre IN (1, 2)),
    annee_academique TEXT NOT NULL,
    chemin_pdf TEXT,
    date_generation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    genere_par INTEGER,
    FOREIGN KEY (id_etudiant) REFERENCES etudiants(id_etudiant) ON DELETE CASCADE,
    FOREIGN KEY (genere_par) REFERENCES utilisateurs(id_user) ON DELETE SET NULL,
    UNIQUE(id_etudiant, semestre, annee_academique)
);

CREATE INDEX IF NOT EXISTS idx_bulletins_annee ON bulletins(annee_academique);

-- ==========================================================
-- MESSAGERIE & NOTIFICATIONS
-- ==========================================================

CREATE TABLE IF NOT EXISTS messages (
    id_message INTEGER PRIMARY KEY AUTOINCREMENT,
    id_expediteur INTEGER NOT NULL,
    id_destinataire INTEGER NOT NULL,
    objet TEXT,
    contenu TEXT NOT NULL,
    est_lu INTEGER DEFAULT 0,
    date_envoi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_lecture TIMESTAMP NULL,
    FOREIGN KEY (id_expediteur) REFERENCES utilisateurs(id_user) ON DELETE CASCADE,
    FOREIGN KEY (id_destinataire) REFERENCES utilisateurs(id_user) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_messages_destinataire ON messages(id_destinataire, est_lu);

-- ==========================================================
-- CONFIGURATION SYSTÈME
-- ==========================================================

CREATE TABLE IF NOT EXISTS configuration_systeme (
    id_config INTEGER PRIMARY KEY AUTOINCREMENT,
    cle TEXT UNIQUE NOT NULL,
    valeur TEXT,
    description TEXT,
    modifie_par INTEGER,
    date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (modifie_par) REFERENCES utilisateurs(id_user) ON DELETE SET NULL
);

-- Initialisation des configurations par défaut
INSERT OR IGNORE INTO configuration_systeme (cle, valeur, description) VALUES
('annee_academique_actuelle', '2025-2026', 'Année académique en cours'),
('semestre_actuel', '1', 'Semestre actuel (1 ou 2)'),
('taux_presence_minimum', '75', 'Taux de présence minimum requis (%)'),
('duree_session_minutes', '120', 'Durée de validité des sessions en minutes');