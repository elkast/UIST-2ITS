-- ============================================================================
-- SCRIPT DE CRÉATION COMPLÈTE DE LA BASE DE DONNÉES UIST_2ITS - UNICAMPUS
-- Version: 2.0 (Complète avec anciennes et nouvelles tables)
-- Date: Janvier 2025
-- Description: Création complète de toutes les tables pour le système UniCampus
-- ============================================================================

-- Suppression de la base si elle existe (ATTENTION: cela supprime toutes les données!)
-- Commentez cette ligne si vous voulez conserver les données existantes
DROP DATABASE IF EXISTS UIST_2ITS;

-- Création de la base de données
CREATE DATABASE UIST_2ITS CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE UIST_2ITS;

-- ============================================================================
-- TABLE UTILISATEURS (Table principale pour l'authentification)
-- ============================================================================

CREATE TABLE Utilisateurs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    prenom VARCHAR(100) NOT NULL,
    matricule VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(150) UNIQUE,
    password_hash VARCHAR(255),
    role ENUM(
        'SUPER_ADMIN',           -- Niveau 1: Gestion des admins, rapports d'audit
        'ADMIN',                 -- Niveau 2: Gestion de tous les utilisateurs
        'DIRECTEUR',             -- Niveau 3: Validation des notes, signalements
        'GESTIONNAIRE_PV',       -- Niveau 3: Bulletins et PV
        'GESTIONNAIRE_EXAMENS',  -- Niveau 3: Structuration examens, import notes
        'GESTIONNAIRE_EDT',      -- Niveau 3: Gestion emploi du temps
        'ENSEIGNANT',            -- Niveau 4: Saisie notes, consultation EDT
        'ETUDIANT',              -- Niveau 5: Consultation notes/EDT, signalements
        'PARENT',                -- Niveau 5: Consultation notes/EDT enfants
        -- Anciens rôles pour compatibilité
        'etudiant',
        'enseignant', 
        'administration',
        'sous_admin'
    ) NOT NULL,
    created_by_id INT,
    last_login DATETIME,
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by_id) REFERENCES Utilisateurs(id) ON DELETE SET NULL,
    INDEX idx_matricule (matricule),
    INDEX idx_email (email),
    INDEX idx_role (role)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- TABLE FILIERES (Promotions/Classes)
-- ============================================================================

CREATE TABLE Filieres (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom_filiere VARCHAR(100) NOT NULL,
    niveau VARCHAR(10) NOT NULL,
    nombre_etudiants INT DEFAULT 0,
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_niveau (niveau)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- TABLE ENSEIGNANTS
-- ============================================================================

CREATE TABLE Enseignants (
    utilisateur_id INT PRIMARY KEY,
    specialite VARCHAR(100),
    total_heures_prevues DECIMAL(10,2) DEFAULT 0,
    total_heures_effectuees DECIMAL(10,2) DEFAULT 0,
    FOREIGN KEY (utilisateur_id) REFERENCES Utilisateurs(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- TABLE ETUDIANTS
-- ============================================================================

CREATE TABLE Etudiants (
    utilisateur_id INT PRIMARY KEY,
    filiere_id INT NOT NULL,
    FOREIGN KEY (utilisateur_id) REFERENCES Utilisateurs(id) ON DELETE CASCADE,
    FOREIGN KEY (filiere_id) REFERENCES Filieres(id) ON DELETE RESTRICT,
    INDEX idx_filiere (filiere_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- TABLE SALLES
-- ============================================================================

CREATE TABLE Salles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom_salle VARCHAR(50) NOT NULL UNIQUE,
    capacite INT NOT NULL,
    equipements TEXT,
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_nom_salle (nom_salle)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- TABLE COURS
-- ============================================================================

CREATE TABLE Cours (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom_cours VARCHAR(150) NOT NULL,
    filiere_id INT NOT NULL,
    type_cours ENUM('CM', 'TD', 'TP') NOT NULL,
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (filiere_id) REFERENCES Filieres(id) ON DELETE CASCADE,
    INDEX idx_filiere (filiere_id),
    INDEX idx_type (type_cours)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- TABLE EMPLOIDUTEMPS (Créneaux)
-- ============================================================================

CREATE TABLE EmploiDuTemps (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cours_id INT NOT NULL,
    enseignant_id INT NOT NULL,
    salle_id INT NOT NULL,
    jour ENUM('Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi') NOT NULL,
    heure_debut TIME NOT NULL,
    heure_fin TIME NOT NULL,
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cours_id) REFERENCES Cours(id) ON DELETE CASCADE,
    FOREIGN KEY (enseignant_id) REFERENCES Enseignants(utilisateur_id) ON DELETE CASCADE,
    FOREIGN KEY (salle_id) REFERENCES Salles(id) ON DELETE CASCADE,
    INDEX idx_jour (jour),
    INDEX idx_enseignant (enseignant_id),
    INDEX idx_salle (salle_id),
    INDEX idx_cours (cours_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- TABLE PRESENCES (Suivi de présence des enseignants)
-- ============================================================================

CREATE TABLE Presences (
    id INT AUTO_INCREMENT PRIMARY KEY,
    creneau_id INT NOT NULL,
    enseignant_id INT NOT NULL,
    statut ENUM('present', 'absent', 'retard', 'non_marque') DEFAULT 'non_marque',
    date_cours DATE NOT NULL,
    remarques TEXT,
    marque_par INT,
    date_marquage TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (creneau_id) REFERENCES EmploiDuTemps(id) ON DELETE CASCADE,
    FOREIGN KEY (enseignant_id) REFERENCES Enseignants(utilisateur_id) ON DELETE CASCADE,
    FOREIGN KEY (marque_par) REFERENCES Utilisateurs(id) ON DELETE SET NULL,
    INDEX idx_creneau (creneau_id),
    INDEX idx_enseignant (enseignant_id),
    INDEX idx_date (date_cours),
    INDEX idx_statut (statut)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- TABLE NOTES (Avec workflow de validation UniCampus)
-- ============================================================================

CREATE TABLE Notes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    etudiant_id INT NOT NULL,
    cours_id INT NOT NULL,
    type_evaluation ENUM('DS', 'Examen', 'TP', 'Projet', 'CC') NOT NULL,
    note DECIMAL(5,2) NOT NULL CHECK (note >= 0 AND note <= 20),
    coefficient DECIMAL(3,2) DEFAULT 1.00 CHECK (coefficient > 0),
    statut ENUM('EN_ATTENTE_DIRECTEUR', 'VALIDÉ', 'EN_REVISION') DEFAULT 'EN_ATTENTE_DIRECTEUR',
    date_evaluation DATE NOT NULL,
    commentaire TEXT,
    saisi_par INT NOT NULL,
    valide_par INT,
    date_validation DATETIME,
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (etudiant_id) REFERENCES Etudiants(utilisateur_id) ON DELETE CASCADE,
    FOREIGN KEY (cours_id) REFERENCES Cours(id) ON DELETE CASCADE,
    FOREIGN KEY (saisi_par) REFERENCES Utilisateurs(id) ON DELETE RESTRICT,
    FOREIGN KEY (valide_par) REFERENCES Utilisateurs(id) ON DELETE SET NULL,
    INDEX idx_statut (statut),
    INDEX idx_etudiant (etudiant_id),
    INDEX idx_cours (cours_id),
    INDEX idx_date_eval (date_evaluation)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- TABLE MESSAGES (Messagerie et signalements)
-- ============================================================================

CREATE TABLE Messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    expediteur_id INT NOT NULL,
    destinataire_id INT NOT NULL,
    type_message ENUM('SIGNALEMENT', 'NOTIFICATION', 'MESSAGE') DEFAULT 'MESSAGE',
    sujet VARCHAR(200) NOT NULL,
    contenu TEXT NOT NULL,
    note_id INT,
    lu BOOLEAN DEFAULT FALSE,
    date_lecture DATETIME,
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (expediteur_id) REFERENCES Utilisateurs(id) ON DELETE CASCADE,
    FOREIGN KEY (destinataire_id) REFERENCES Utilisateurs(id) ON DELETE CASCADE,
    FOREIGN KEY (note_id) REFERENCES Notes(id) ON DELETE SET NULL,
    INDEX idx_destinataire (destinataire_id),
    INDEX idx_expediteur (expediteur_id),
    INDEX idx_lu (lu),
    INDEX idx_type (type_message)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- TABLE BULLETINS (Génération de bulletins)
-- ============================================================================

CREATE TABLE Bulletins (
    id INT AUTO_INCREMENT PRIMARY KEY,
    etudiant_id INT NOT NULL,
    filiere_id INT NOT NULL,
    semestre VARCHAR(20) NOT NULL,
    annee_academique VARCHAR(20) NOT NULL,
    moyenne_generale DECIMAL(5,2),
    rang INT,
    appreciation TEXT,
    fichier_pdf VARCHAR(255),
    genere_par INT NOT NULL,
    date_generation DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (etudiant_id) REFERENCES Etudiants(utilisateur_id) ON DELETE CASCADE,
    FOREIGN KEY (filiere_id) REFERENCES Filieres(id) ON DELETE CASCADE,
    FOREIGN KEY (genere_par) REFERENCES Utilisateurs(id) ON DELETE RESTRICT,
    INDEX idx_etudiant (etudiant_id),
    INDEX idx_semestre (semestre, annee_academique),
    UNIQUE KEY unique_bulletin (etudiant_id, semestre, annee_academique)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- TABLE USAGEAUDIT (Traçabilité des actions)
-- ============================================================================

CREATE TABLE UsageAudit (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    action VARCHAR(100) NOT NULL,
    meta JSON,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Utilisateurs(id) ON DELETE CASCADE,
    INDEX idx_user (user_id),
    INDEX idx_action (action),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- TABLE PARENTSETUDIANTS (Liaison parents-étudiants)
-- ============================================================================

CREATE TABLE ParentsEtudiants (
    id INT AUTO_INCREMENT PRIMARY KEY,
    parent_id INT NOT NULL,
    etudiant_id INT NOT NULL,
    relation ENUM('pere', 'mere', 'tuteur', 'autre') DEFAULT 'autre',
    telephone VARCHAR(20),
    email VARCHAR(150),
    adresse TEXT,
    contact_prioritaire BOOLEAN DEFAULT FALSE,
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES Utilisateurs(id) ON DELETE CASCADE,
    FOREIGN KEY (etudiant_id) REFERENCES Etudiants(utilisateur_id) ON DELETE CASCADE,
    INDEX idx_parent (parent_id),
    INDEX idx_etudiant (etudiant_id),
    UNIQUE KEY unique_parent_etudiant (parent_id, etudiant_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- TABLE IMPORTNOTES (Historique des imports)
-- ============================================================================

CREATE TABLE ImportNotes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cours_id INT NOT NULL,
    filiere_id INT NOT NULL,
    enseignant_id INT NOT NULL,
    role_initiateur VARCHAR(50),
    fichier_nom VARCHAR(255) NOT NULL,
    nombre_notes INT DEFAULT 0,
    date_import TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cours_id) REFERENCES Cours(id) ON DELETE CASCADE,
    FOREIGN KEY (filiere_id) REFERENCES Filieres(id) ON DELETE CASCADE,
    FOREIGN KEY (enseignant_id) REFERENCES Utilisateurs(id) ON DELETE CASCADE,
    INDEX idx_cours (cours_id),
    INDEX idx_enseignant (enseignant_id),
    INDEX idx_date (date_import)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- TABLE STATUTSENSEIGNANTTEMPSREEL (Statuts temps réel des enseignants)
-- ============================================================================

CREATE TABLE StatutsEnseignantTempsReel (
    id INT AUTO_INCREMENT PRIMARY KEY,
    enseignant_id INT NOT NULL,
    creneau_id INT NOT NULL,
    date_cours DATE NOT NULL,
    statut ENUM('disponible', 'non_disponible', 'en_retard', 'present') DEFAULT 'disponible',
    heure_arrivee TIME,
    remarques TEXT,
    mis_a_jour_par INT,
    date_maj TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (enseignant_id) REFERENCES Enseignants(utilisateur_id) ON DELETE CASCADE,
    FOREIGN KEY (creneau_id) REFERENCES EmploiDuTemps(id) ON DELETE CASCADE,
    FOREIGN KEY (mis_a_jour_par) REFERENCES Utilisateurs(id) ON DELETE SET NULL,
    INDEX idx_enseignant (enseignant_id),
    INDEX idx_creneau (creneau_id),
    INDEX idx_date (date_cours),
    UNIQUE KEY unique_statut (enseignant_id, creneau_id, date_cours)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- TABLE CONFLITSPLANIFICATION (Gestion des conflits)
-- ============================================================================

CREATE TABLE ConflitsPlanification (
    id INT AUTO_INCREMENT PRIMARY KEY,
    creneau_id INT NOT NULL,
    type_conflit ENUM('enseignant', 'salle', 'filiere') NOT NULL,
    creneau_conflit_id INT,
    description TEXT NOT NULL,
    severite ENUM('faible', 'moyenne', 'critique') DEFAULT 'moyenne',
    statut ENUM('actif', 'resolu', 'ignore') DEFAULT 'actif',
    action_suggeree TEXT,
    date_detection TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolu_par INT,
    date_resolution DATETIME,
    FOREIGN KEY (creneau_id) REFERENCES EmploiDuTemps(id) ON DELETE CASCADE,
    FOREIGN KEY (creneau_conflit_id) REFERENCES EmploiDuTemps(id) ON DELETE CASCADE,
    FOREIGN KEY (resolu_par) REFERENCES Utilisateurs(id) ON DELETE SET NULL,
    INDEX idx_statut (statut),
    INDEX idx_severite (severite)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- VUES (Pour faciliter les requêtes)
-- ============================================================================

CREATE OR REPLACE VIEW vue_parents_etudiants AS
SELECT 
    pe.id,
    pe.parent_id,
    up.nom as parent_nom,
    up.prenom as parent_prenom,
    up.matricule as parent_matricule,
    pe.etudiant_id,
    ue.nom as etudiant_nom,
    ue.prenom as etudiant_prenom,
    ue.matricule as etudiant_matricule,
    pe.relation,
    pe.telephone,
    pe.email,
    pe.adresse,
    pe.contact_prioritaire,
    f.nom_filiere,
    f.niveau
FROM ParentsEtudiants pe
JOIN Utilisateurs up ON pe.parent_id = up.id
JOIN Etudiants e ON pe.etudiant_id = e.utilisateur_id
JOIN Utilisateurs ue ON e.utilisateur_id = ue.id
JOIN Filieres f ON e.filiere_id = f.id;

-- ============================================================================
-- INSERTION DES DONNÉES DE TEST
-- ============================================================================

-- Mot de passe par défaut: "password123"
-- Hash bcrypt: $2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5lE7NqNjseK5u

-- Comptes administratifs
INSERT INTO Utilisateurs (nom, prenom, matricule, email, password_hash, role, created_by_id) VALUES
('Super', 'Admin', 'SA2025001', 'superadmin@uist.edu', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5lE7NqNjseK5u', 'SUPER_ADMIN', NULL),
('Admin', 'Principal', 'A2025001', 'admin@uist.edu', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5lE7NqNjseK5u', 'ADMIN', 1);

-- Comptes gestionnaires
INSERT INTO Utilisateurs (nom, prenom, matricule, email, password_hash, role, created_by_id) VALUES
('Directeur', 'Académique', 'DIR2025001', 'directeur@uist.edu', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5lE7NqNjseK5u', 'DIRECTEUR', 2),
('Gestionnaire', 'PV', 'GPV2025001', 'gpv@uist.edu', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5lE7NqNjseK5u', 'GESTIONNAIRE_PV', 2),
('Gestionnaire', 'Examens', 'GEX2025001', 'gexamens@uist.edu', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5lE7NqNjseK5u', 'GESTIONNAIRE_EXAMENS', 2),
('Gestionnaire', 'EDT', 'GEDT2025001', 'gedt@uist.edu', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5lE7NqNjseK5u', 'GESTIONNAIRE_EDT', 2);

-- Filières de test
INSERT INTO Filieres (nom_filiere, niveau, nombre_etudiants) VALUES
('Informatique', 'L3', 45),
('Génie Logiciel', 'M1', 30),
('Réseaux et Télécommunications', 'L3', 40),
('Systèmes d\'Information', 'L2', 50);

-- Enseignant de test
INSERT INTO Utilisateurs (nom, prenom, matricule, email, password_hash, role, created_by_id) VALUES
('Enseignant', 'Test', 'P2025001', 'enseignant@uist.edu', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5lE7NqNjseK5u', 'ENSEIGNANT', 2);

INSERT INTO Enseignants (utilisateur_id, specialite) VALUES
(7, 'Informatique et Algorithmique');

-- Étudiant de test
INSERT INTO Utilisateurs (nom, prenom, matricule, email, password_hash, role, created_by_id) VALUES
('Étudiant', 'Test', 'E2025001', 'etudiant@uist.edu', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5lE7NqNjseK5u', 'ETUDIANT', 2);

INSERT INTO Etudiants (utilisateur_id, filiere_id) VALUES
(8, 1);

-- Parent de test
INSERT INTO Utilisateurs (nom, prenom, matricule, email, password_hash, role, created_by_id) VALUES
('Parent', 'Test', 'PAR2025001', 'parent@uist.edu', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5lE7NqNjseK5u', 'PARENT', 2);

INSERT INTO ParentsEtudiants (parent_id, etudiant_id, relation, telephone, email, contact_prioritaire) VALUES
(9, 8, 'pere', '+221 77 123 45 67', 'parent@uist.edu', TRUE);

-- Salles de test
INSERT INTO Salles (nom_salle, capacite, equipements) VALUES
('Amphi A', 100, 'Vidéo-projecteur, Micro, Climatisation'),
('Salle Info 1', 30, 'PC, Vidéo-projecteur'),
('Salle TD 1', 40, 'Tableau blanc, Vidéo-projecteur'),
('Labo TP', 25, 'PC, Équipements réseau');

-- Cours de test
INSERT INTO Cours (nom_cours, filiere_id, type_cours) VALUES
('Algorithmique Avancée', 1, 'CM'),
('Structures de Données', 1, 'TD'),
('Programmation C', 1, 'TP'),
('Base de Données', 1, 'CM');

-- Notes de test (en attente de validation)
INSERT INTO Notes (etudiant_id, cours_id, type_evaluation, note, coefficient, statut, date_evaluation, saisi_par) VALUES
(8, 1, 'DS', 15.50, 1.00, 'EN_ATTENTE_DIRECTEUR', CURDATE(), 7),
(8, 2, 'CC', 14.00, 0.50, 'EN_ATTENTE_DIRECTEUR', CURDATE(), 7),
(8, 3, 'TP', 16.50, 1.50, 'EN_ATTENTE_DIRECTEUR', CURDATE(), 7);

-- ============================================================================
-- CONFIRMATION
-- ============================================================================

SELECT '✓ Base de données UIST_2ITS créée avec succès!' AS Status;
SELECT '' AS '';
SELECT 'Tables créées:' AS Info;
SHOW TABLES;
SELECT '' AS '';
SELECT 'Comptes utilisateurs créés:' AS Info;
SELECT matricule, role, email FROM Utilisateurs ORDER BY FIELD(role, 'SUPER_ADMIN', 'ADMIN', 'DIRECTEUR', 'GESTIONNAIRE_PV', 'GESTIONNAIRE_EXAMENS', 'GESTIONNAIRE_EDT', 'ENSEIGNANT', 'ETUDIANT', 'PARENT');
SELECT '' AS '';
SELECT 'Mot de passe pour tous les comptes: password123' AS Important;
SELECT '' AS '';
SELECT '✓ Prêt à utiliser! Connectez-vous avec DIR2025001 / password123' AS Message;