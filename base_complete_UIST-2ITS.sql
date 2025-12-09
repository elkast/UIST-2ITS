-- ============================================================================
-- SCRIPT DE CRÉATION COMPLÈTE DE LA BASE DE DONNÉES UIST_2ITS
-- Version: 3.0 (Complète et corrigée)
-- Date: Janvier 2025
-- Description: Base de données complète pour le système de gestion universitaire
-- ============================================================================

-- Suppression de la base si elle existe
DROP DATABASE IF EXISTS UIST_2ITS;

-- Création de la base de données
CREATE DATABASE UIST_2ITS CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE UIST_2ITS;

-- ============================================================================
-- TABLE UTILISATEURS (Authentification et gestion des comptes)
-- ============================================================================

CREATE TABLE Utilisateurs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    prenom VARCHAR(100) NOT NULL,
    matricule VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(150) UNIQUE,
    password_hash VARCHAR(255),
    role ENUM(
        'SUPER_ADMIN',
        'ADMIN',
        'DIRECTEUR',
        'GESTIONNAIRE_PV',
        'GESTIONNAIRE_EXAMENS',
        'GESTIONNAIRE_EDT',
        'GESTIONNAIRE_PRESENCES',
        'ENSEIGNANT',
        'ETUDIANT',
        'PARENT',
        'etudiant',
        'enseignant',
        'administration',
        'sous_admin'
    ) NOT NULL,
    actif BOOLEAN DEFAULT TRUE,
    created_by_id INT,
    last_login DATETIME,
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by_id) REFERENCES Utilisateurs(id) ON DELETE SET NULL,
    INDEX idx_matricule (matricule),
    INDEX idx_email (email),
    INDEX idx_role (role)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- TABLE FILIERES
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
    id INT AUTO_INCREMENT PRIMARY KEY,
    utilisateur_id INT UNIQUE NOT NULL,
    specialite VARCHAR(100),
    total_heures_prevues DECIMAL(10,2) DEFAULT 0,
    total_heures_effectuees DECIMAL(10,2) DEFAULT 0,
    FOREIGN KEY (utilisateur_id) REFERENCES Utilisateurs(id) ON DELETE CASCADE,
    INDEX idx_utilisateur (utilisateur_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- TABLE ETUDIANTS
-- ============================================================================

CREATE TABLE Etudiants (
    id INT AUTO_INCREMENT PRIMARY KEY,
    utilisateur_id INT UNIQUE NOT NULL,
    filiere_id INT NOT NULL,
    FOREIGN KEY (utilisateur_id) REFERENCES Utilisateurs(id) ON DELETE CASCADE,
    FOREIGN KEY (filiere_id) REFERENCES Filieres(id) ON DELETE RESTRICT,
    INDEX idx_utilisateur (utilisateur_id),
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
    enseignant_id INT,
    type_cours ENUM('CM', 'TD', 'TP') NOT NULL,
    coefficient DECIMAL(3,2) DEFAULT 1.00,
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (filiere_id) REFERENCES Filieres(id) ON DELETE CASCADE,
    FOREIGN KEY (enseignant_id) REFERENCES Enseignants(id) ON DELETE SET NULL,
    INDEX idx_filiere (filiere_id),
    INDEX idx_enseignant (enseignant_id),
    INDEX idx_type (type_cours)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- TABLE EMPLOIDUTEMPS
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
    FOREIGN KEY (enseignant_id) REFERENCES Enseignants(id) ON DELETE CASCADE,
    FOREIGN KEY (salle_id) REFERENCES Salles(id) ON DELETE CASCADE,
    INDEX idx_jour (jour),
    INDEX idx_enseignant (enseignant_id),
    INDEX idx_salle (salle_id),
    INDEX idx_cours (cours_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- TABLE PRESENCES
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
    FOREIGN KEY (enseignant_id) REFERENCES Enseignants(id) ON DELETE CASCADE,
    FOREIGN KEY (marque_par) REFERENCES Utilisateurs(id) ON DELETE SET NULL,
    INDEX idx_creneau (creneau_id),
    INDEX idx_enseignant (enseignant_id),
    INDEX idx_date (date_cours),
    INDEX idx_statut (statut)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- TABLE NOTES
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
    FOREIGN KEY (etudiant_id) REFERENCES Etudiants(id) ON DELETE CASCADE,
    FOREIGN KEY (cours_id) REFERENCES Cours(id) ON DELETE CASCADE,
    FOREIGN KEY (saisi_par) REFERENCES Utilisateurs(id) ON DELETE RESTRICT,
    FOREIGN KEY (valide_par) REFERENCES Utilisateurs(id) ON DELETE SET NULL,
    INDEX idx_statut (statut),
    INDEX idx_etudiant (etudiant_id),
    INDEX idx_cours (cours_id),
    INDEX idx_date_eval (date_evaluation)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- TABLE MESSAGES
-- ============================================================================

CREATE TABLE Messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    expediteur_id INT NOT NULL,
    destinataire_id INT,
    type_message ENUM('SIGNALEMENT', 'NOTIFICATION', 'MESSAGE') DEFAULT 'MESSAGE',
    sujet VARCHAR(200) NOT NULL,
    contenu TEXT NOT NULL,
    lu BOOLEAN DEFAULT FALSE,
    date_envoi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (expediteur_id) REFERENCES Utilisateurs(id) ON DELETE CASCADE,
    FOREIGN KEY (destinataire_id) REFERENCES Utilisateurs(id) ON DELETE CASCADE,
    INDEX idx_destinataire (destinataire_id),
    INDEX idx_lu (lu),
    INDEX idx_type (type_message)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- TABLE BULLETINS
-- ============================================================================

CREATE TABLE Bulletins (
    id INT AUTO_INCREMENT PRIMARY KEY,
    etudiant_id INT NOT NULL,
    semestre ENUM('S1', 'S2') NOT NULL,
    annee_academique VARCHAR(9) NOT NULL,
    moyenne_generale DECIMAL(5,2),
    classement INT,
    total_etudiants INT,
    appreciation TEXT,
    fichier_pdf VARCHAR(255),
    genere_par INT,
    date_generation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (etudiant_id) REFERENCES Etudiants(id) ON DELETE CASCADE,
    FOREIGN KEY (genere_par) REFERENCES Utilisateurs(id) ON DELETE SET NULL,
    INDEX idx_etudiant (etudiant_id),
    INDEX idx_annee (annee_academique)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- TABLE PARENTS_ETUDIANTS (Relation parents-enfants)
-- ============================================================================

CREATE TABLE ParentsEtudiants (
    id INT AUTO_INCREMENT PRIMARY KEY,
    parent_id INT NOT NULL,
    etudiant_id INT NOT NULL,
    lien_parente ENUM('Pere', 'Mere', 'Tuteur', 'Autre') NOT NULL,
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES Utilisateurs(id) ON DELETE CASCADE,
    FOREIGN KEY (etudiant_id) REFERENCES Etudiants(id) ON DELETE CASCADE,
    UNIQUE KEY unique_parent_etudiant (parent_id, etudiant_id),
    INDEX idx_parent (parent_id),
    INDEX idx_etudiant (etudiant_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- TABLE IMPORT_NOTES (Historique des imports)
-- ============================================================================

CREATE TABLE ImportNotes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cours_id INT NOT NULL,
    fichier_nom VARCHAR(255) NOT NULL,
    nb_notes_importees INT DEFAULT 0,
    nb_erreurs INT DEFAULT 0,
    details_erreurs TEXT,
    importe_par INT NOT NULL,
    date_import TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cours_id) REFERENCES Cours(id) ON DELETE CASCADE,
    FOREIGN KEY (importe_par) REFERENCES Utilisateurs(id) ON DELETE RESTRICT,
    INDEX idx_cours (cours_id),
    INDEX idx_date (date_import)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- TABLE USAGE_AUDIT (Traçabilité des actions)
-- ============================================================================

CREATE TABLE UsageAudit (
    id INT AUTO_INCREMENT PRIMARY KEY,
    utilisateur_id INT,
    action VARCHAR(100) NOT NULL,
    table_affectee VARCHAR(50),
    enregistrement_id INT,
    details TEXT,
    ip_address VARCHAR(45),
    user_agent TEXT,
    date_action TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (utilisateur_id) REFERENCES Utilisateurs(id) ON DELETE SET NULL,
    INDEX idx_utilisateur (utilisateur_id),
    INDEX idx_date (date_action),
    INDEX idx_action (action)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- INSERTION DES DONNÉES DE TEST
-- ============================================================================

-- Insertion des filières
INSERT INTO Filieres (nom_filiere, niveau, nombre_etudiants) VALUES
('Informatique', 'L1', 0),
('Informatique', 'L2', 0),
('Informatique', 'L3', 0),
('Gestion', 'L1', 0),
('Gestion', 'L2', 0),
('Gestion', 'L3', 0);

-- Insertion des utilisateurs (mot de passe: password123)
-- Hash pour 'password123': $2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIbXJBlQXK

INSERT INTO Utilisateurs (nom, prenom, matricule, email, password_hash, role) VALUES
-- Super Admin
('SUPER', 'Admin', 'SA2025001', 'superadmin@uist.edu', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIbXJBlQXK', 'SUPER_ADMIN'),
-- Admin
('ADMIN', 'Principal', 'A2025001', 'admin@uist.edu', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIbXJBlQXK', 'ADMIN'),
-- Directeur
('DIRECTEUR', 'Académique', 'DIR2025001', 'directeur@uist.edu', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIbXJBlQXK', 'DIRECTEUR'),
-- Gestionnaires
('GESTIONNAIRE', 'PV', 'GPV2025001', 'gpv@uist.edu', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIbXJBlQXK', 'GESTIONNAIRE_PV'),
('GESTIONNAIRE', 'Examens', 'GEX2025001', 'gexamens@uist.edu', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIbXJBlQXK', 'GESTIONNAIRE_EXAMENS'),
('GESTIONNAIRE', 'EDT', 'GEDT2025001', 'gedt@uist.edu', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIbXJBlQXK', 'GESTIONNAIRE_EDT'),
('GESTIONNAIRE', 'Présences', 'GPRE2025001', 'gpresences@uist.edu', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIbXJBlQXK', 'GESTIONNAIRE_PRESENCES'),
-- Enseignants
('DIOP', 'Mamadou', 'P2025001', 'mdiop@uist.edu', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIbXJBlQXK', 'ENSEIGNANT'),
('NDIAYE', 'Aissatou', 'P2025002', 'andiaye@uist.edu', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIbXJBlQXK', 'ENSEIGNANT'),
-- Étudiants
('FALL', 'Ousmane', 'E2025001', 'ofall@uist.edu', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIbXJBlQXK', 'ETUDIANT'),
('SALL', 'Fatou', 'E2025002', 'fsall@uist.edu', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIbXJBlQXK', 'ETUDIANT'),
-- Parent
('PARENT', 'Test', 'PAR2025001', 'parent@uist.edu', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIbXJBlQXK', 'PARENT');

-- Insertion des enseignants
INSERT INTO Enseignants (utilisateur_id, specialite) VALUES
(8, 'Informatique'),
(9, 'Mathématiques');

-- Insertion des étudiants
INSERT INTO Etudiants (utilisateur_id, filiere_id) VALUES
(10, 1),  -- Ousmane FALL en Informatique L1
(11, 1);  -- Fatou SALL en Informatique L1

-- Mise à jour du nombre d'étudiants dans les filières
UPDATE Filieres SET nombre_etudiants = 2 WHERE id = 1;

-- Insertion des salles
INSERT INTO Salles (nom_salle, capacite, equipements) VALUES
('Amphi A', 200, 'Projecteur, Micro, Climatisation'),
('Amphi B', 150, 'Projecteur, Tableau interactif'),
('Salle TD1', 40, 'Tableau blanc, Projecteur'),
('Salle TD2', 40, 'Tableau blanc, Projecteur'),
('Labo Info 1', 30, '30 Ordinateurs, Projecteur'),
('Labo Info 2', 30, '30 Ordinateurs, Projecteur');

-- Insertion des cours
INSERT INTO Cours (nom_cours, filiere_id, enseignant_id, type_cours, coefficient) VALUES
('Algorithmique et Structures de Données', 1, 1, 'CM', 2.00),
('Programmation C', 1, 1, 'TP', 1.50),
('Mathématiques Discrètes', 1, 2, 'CM', 2.00),
('Base de Données', 1, 1, 'CM', 2.00),
('Systèmes d\'Exploitation', 1, 2, 'CM', 1.50);

-- Insertion d'un emploi du temps exemple
INSERT INTO EmploiDuTemps (cours_id, enseignant_id, salle_id, jour, heure_debut, heure_fin) VALUES
(1, 1, 1, 'Lundi', '08:00:00', '10:00:00'),
(2, 1, 5, 'Lundi', '10:00:00', '12:00:00'),
(3, 2, 1, 'Mardi', '08:00:00', '10:00:00'),
(4, 1, 1, 'Mercredi', '08:00:00', '10:00:00'),
(5, 2, 1, 'Jeudi', '08:00:00', '10:00:00');

-- Insertion de notes exemples
INSERT INTO Notes (etudiant_id, cours_id, type_evaluation, note, coefficient, statut, date_evaluation, saisi_par) VALUES
(1, 1, 'DS', 15.50, 1.00, 'VALIDÉ', '2025-01-10', 8),
(1, 1, 'Examen', 14.00, 2.00, 'VALIDÉ', '2025-01-20', 8),
(2, 1, 'DS', 16.00, 1.00, 'VALIDÉ', '2025-01-10', 8),
(2, 1, 'Examen', 15.50, 2.00, 'EN_ATTENTE_DIRECTEUR', '2025-01-20', 8);

-- Insertion relation parent-étudiant
INSERT INTO ParentsEtudiants (parent_id, etudiant_id, lien_parente) VALUES
(12, 1, 'Pere');

-- ============================================================================
-- FIN DU SCRIPT
-- ============================================================================

SELECT 'Base de données UIST_2ITS créée avec succès!' AS message;