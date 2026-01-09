-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Hôte : 127.0.0.1:3306
-- Généré le : ven. 09 jan. 2026 à 01:34
-- Version du serveur : 9.1.0
-- Version de PHP : 8.3.14

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de données : `uist_2its`
--

DELIMITER $$
--
-- Procédures
--
DROP PROCEDURE IF EXISTS `get_dashboard_monitoring`$$
CREATE DEFINER=`root`@`localhost` PROCEDURE `get_dashboard_monitoring` ()   BEGIN
    -- Utilisateurs actifs maintenant
    SELECT 
        COUNT(*) as utilisateurs_actifs,
        COUNT(DISTINCT role) as roles_actifs
    FROM UtilisateursActifs;
    
    -- Blocages actifs
    SELECT 
        type_blocage,
        COUNT(*) as nombre
    FROM BlocagesWorkflow
    WHERE statut = 'ACTIF'
    GROUP BY type_blocage;
    
    -- Notifications non lues par priorité
    SELECT 
        priorite,
        COUNT(*) as nombre
    FROM NotificationsWorkflow
    WHERE lu = FALSE AND archivee = FALSE
    GROUP BY priorite;
END$$

DROP PROCEDURE IF EXISTS `resoudre_blocage`$$
CREATE DEFINER=`root`@`localhost` PROCEDURE `resoudre_blocage` (IN `p_blocage_id` INT, IN `p_validateur_id` INT)   BEGIN
    UPDATE BlocagesWorkflow
    SET statut = 'RESOLU',
        date_resolution = NOW()
    WHERE id = p_blocage_id;
    
    -- Logger l'action
    INSERT INTO UsageAudit (
        utilisateur_id, action_type, action_description
    ) VALUES (
        p_validateur_id, 'blocage_resolu',
        CONCAT('Résolution blocage ID:', p_blocage_id)
    );
END$$

DELIMITER ;

-- --------------------------------------------------------

--
-- Structure de la table `activiteutilisateurs`
--

DROP TABLE IF EXISTS `activiteutilisateurs`;
CREATE TABLE IF NOT EXISTS `activiteutilisateurs` (
  `id` int NOT NULL AUTO_INCREMENT,
  `utilisateur_id` int NOT NULL,
  `type_activite` enum('CONNEXION','DECONNEXION','ACTION','CONSULTATION') COLLATE utf8mb4_unicode_ci NOT NULL,
  `action_detail` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `ip_address` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `user_agent` text COLLATE utf8mb4_unicode_ci,
  `duree_session` int DEFAULT NULL COMMENT 'Durée en secondes',
  `timestamp_debut` datetime DEFAULT CURRENT_TIMESTAMP,
  `timestamp_fin` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_utilisateur` (`utilisateur_id`),
  KEY `idx_type` (`type_activite`),
  KEY `idx_timestamp` (`timestamp_debut`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Structure de la table `assignationsenseignants`
--

DROP TABLE IF EXISTS `assignationsenseignants`;
CREATE TABLE IF NOT EXISTS `assignationsenseignants` (
  `id` int NOT NULL AUTO_INCREMENT,
  `enseignant_id` int NOT NULL,
  `cours_id` int NOT NULL,
  `filiere_id` int NOT NULL,
  `niveau` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  `annee_academique` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `assigne_par` int NOT NULL,
  `date_assignation` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `assigne_par` (`assigne_par`),
  KEY `idx_enseignant` (`enseignant_id`),
  KEY `idx_cours` (`cours_id`),
  KEY `idx_filiere_niveau` (`filiere_id`,`niveau`),
  KEY `idx_annee` (`annee_academique`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Structure de la table `auditusage`
--

DROP TABLE IF EXISTS `auditusage`;
CREATE TABLE IF NOT EXISTS `auditusage` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int DEFAULT NULL,
  `action` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` text COLLATE utf8mb4_unicode_ci,
  `ip_address` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `user_agent` text COLLATE utf8mb4_unicode_ci,
  `meta` json DEFAULT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_user_action` (`user_id`,`action`),
  KEY `idx_action` (`action`),
  KEY `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Doublure de structure pour la vue `blocagesactifs`
-- (Voir ci-dessous la vue réelle)
--
DROP VIEW IF EXISTS `blocagesactifs`;
CREATE TABLE IF NOT EXISTS `blocagesactifs` (
`id` int
,`type_blocage` enum('NOTES_MANQUANTES','VALIDATION_PENDING','CONFLIT_EDT','IMPORT_ERREUR')
,`entite_bloquee` varchar(100)
,`bloquant_matricule` varchar(50)
,`bloquant_nom` varchar(100)
,`bloquant_role` enum('SUPER_ADMIN','ADMIN','DIRECTEUR','GESTIONNAIRE_PV','GESTIONNAIRE_EXAMENS','GESTIONNAIRE_EDT','GESTIONNAIRE_PRESENCES','ENSEIGNANT','ETUDIANT','PARENT','etudiant','enseignant','administration','sous_admin')
,`bloque_matricule` varchar(50)
,`bloque_nom` varchar(100)
,`bloque_role` enum('SUPER_ADMIN','ADMIN','DIRECTEUR','GESTIONNAIRE_PV','GESTIONNAIRE_EXAMENS','GESTIONNAIRE_EDT','GESTIONNAIRE_PRESENCES','ENSEIGNANT','ETUDIANT','PARENT','etudiant','enseignant','administration','sous_admin')
,`description` text
,`date_creation` datetime
,`heures_blocage` bigint
);

-- --------------------------------------------------------

--
-- Structure de la table `blocagesworkflow`
--

DROP TABLE IF EXISTS `blocagesworkflow`;
CREATE TABLE IF NOT EXISTS `blocagesworkflow` (
  `id` int NOT NULL AUTO_INCREMENT,
  `type_blocage` enum('NOTES_MANQUANTES','VALIDATION_PENDING','CONFLIT_EDT','IMPORT_ERREUR') COLLATE utf8mb4_unicode_ci NOT NULL,
  `entite_bloquee` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Ex: bulletin_etudiant_123',
  `acteur_bloquant_id` int DEFAULT NULL COMMENT 'ID utilisateur qui doit agir',
  `acteur_bloque_id` int DEFAULT NULL COMMENT 'ID utilisateur bloqué',
  `description` text COLLATE utf8mb4_unicode_ci,
  `statut` enum('ACTIF','RESOLU','IGNORE') COLLATE utf8mb4_unicode_ci DEFAULT 'ACTIF',
  `date_creation` datetime DEFAULT CURRENT_TIMESTAMP,
  `date_resolution` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_type` (`type_blocage`),
  KEY `idx_statut` (`statut`),
  KEY `idx_acteur_bloquant` (`acteur_bloquant_id`),
  KEY `idx_acteur_bloque` (`acteur_bloque_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Structure de la table `bulletins`
--

DROP TABLE IF EXISTS `bulletins`;
CREATE TABLE IF NOT EXISTS `bulletins` (
  `id` int NOT NULL AUTO_INCREMENT,
  `etudiant_id` int NOT NULL,
  `semestre` enum('S1','S2') COLLATE utf8mb4_unicode_ci NOT NULL,
  `annee_academique` varchar(9) COLLATE utf8mb4_unicode_ci NOT NULL,
  `moyenne_generale` decimal(5,2) DEFAULT NULL,
  `classement` int DEFAULT NULL,
  `total_etudiants` int DEFAULT NULL,
  `appreciation` text COLLATE utf8mb4_unicode_ci,
  `fichier_pdf` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `genere_par` int DEFAULT NULL,
  `date_generation` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `genere_par` (`genere_par`),
  KEY `idx_etudiant` (`etudiant_id`),
  KEY `idx_annee` (`annee_academique`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Déclencheurs `bulletins`
--
DROP TRIGGER IF EXISTS `check_bulletin_blocage`;
DELIMITER $$
CREATE TRIGGER `check_bulletin_blocage` BEFORE INSERT ON `bulletins` FOR EACH ROW BEGIN
    DECLARE notes_non_validees INT;
    
    -- Compter les notes qui ne sont pas encore 'VALIDÉ'
    SELECT COUNT(*) INTO notes_non_validees
    FROM Notes
    WHERE etudiant_id = NEW.etudiant_id
    AND semestre = NEW.semestre
    AND statut != 'VALIDÉ'; -- Utilisation de l'accent comme dans votre DESCRIBE
    
    -- Si des notes manquent, on bloque et on crée un log de blocage
    IF notes_non_validees > 0 THEN
        INSERT INTO BlocagesWorkflow (
            type_blocage, 
            entite_bloquee, 
            description, 
            statut
        ) VALUES (
            'NOTES_MANQUANTES',
            CONCAT('bulletin_', NEW.etudiant_id, '_', NEW.semestre),
            CONCAT(notes_non_validees, ' note(s) non encore validée(s)'),
            'ACTIF'
        );
        
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Action annulée : Certaines notes ne sont pas encore validées pour ce semestre.';
    END IF;
END
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- Structure de la table `bulletinscache`
--

DROP TABLE IF EXISTS `bulletinscache`;
CREATE TABLE IF NOT EXISTS `bulletinscache` (
  `id` int NOT NULL AUTO_INCREMENT,
  `etudiant_id` int NOT NULL,
  `semestre` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `annee_academique` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `moyenne_cc` decimal(5,2) DEFAULT NULL,
  `moyenne_td` decimal(5,2) DEFAULT NULL,
  `moyenne_tp` decimal(5,2) DEFAULT NULL,
  `moyenne_ds` decimal(5,2) DEFAULT NULL,
  `moyenne_examen` decimal(5,2) DEFAULT NULL,
  `moyenne_generale` decimal(5,2) DEFAULT NULL,
  `classement_filiere` int DEFAULT NULL,
  `total_etudiants_filiere` int DEFAULT NULL,
  `statut_bulletin` enum('INCOMPLET','COMPLET','VALIDE') COLLATE utf8mb4_unicode_ci DEFAULT 'INCOMPLET',
  `derniere_maj` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_etudiant_semestre` (`etudiant_id`,`semestre`,`annee_academique`),
  KEY `idx_semestre` (`semestre`),
  KEY `idx_statut` (`statut_bulletin`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Structure de la table `cours`
--

DROP TABLE IF EXISTS `cours`;
CREATE TABLE IF NOT EXISTS `cours` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nom_cours` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `filiere_id` int NOT NULL,
  `enseignant_id` int DEFAULT NULL,
  `type_cours` enum('CM','TD','TP') COLLATE utf8mb4_unicode_ci NOT NULL,
  `coefficient` decimal(3,2) DEFAULT '1.00',
  `date_creation` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_filiere` (`filiere_id`),
  KEY `idx_enseignant` (`enseignant_id`),
  KEY `idx_type` (`type_cours`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Déchargement des données de la table `cours`
--

INSERT INTO `cours` (`id`, `nom_cours`, `filiere_id`, `enseignant_id`, `type_cours`, `coefficient`, `date_creation`) VALUES
(1, 'IA', 4, NULL, 'CM', 1.00, '2026-01-09 01:23:54'),
(2, 'stat-inf', 1, NULL, 'CM', 1.00, '2026-01-09 01:28:16');

-- --------------------------------------------------------

--
-- Structure de la table `disponibilitesenseignants`
--

DROP TABLE IF EXISTS `disponibilitesenseignants`;
CREATE TABLE IF NOT EXISTS `disponibilitesenseignants` (
  `id` int NOT NULL AUTO_INCREMENT,
  `enseignant_id` int NOT NULL,
  `date_debut` date NOT NULL,
  `date_fin` date NOT NULL,
  `type_indisponibilite` enum('ABSENCE','RETARD','DISPONIBLE','CHANGEMENT_HORAIRE') COLLATE utf8mb4_unicode_ci NOT NULL,
  `motif` text COLLATE utf8mb4_unicode_ci,
  `visible_etudiants` tinyint(1) DEFAULT '1',
  `date_creation` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_enseignant` (`enseignant_id`),
  KEY `idx_dates` (`date_debut`,`date_fin`),
  KEY `idx_visible` (`visible_etudiants`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Structure de la table `emploidutemps`
--

DROP TABLE IF EXISTS `emploidutemps`;
CREATE TABLE IF NOT EXISTS `emploidutemps` (
  `id` int NOT NULL AUTO_INCREMENT,
  `cours_id` int NOT NULL,
  `enseignant_id` int NOT NULL,
  `salle_id` int NOT NULL,
  `jour` enum('Lundi','Mardi','Mercredi','Jeudi','Vendredi','Samedi') COLLATE utf8mb4_unicode_ci NOT NULL,
  `heure_debut` time NOT NULL,
  `heure_fin` time NOT NULL,
  `date_creation` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `type_creneau` enum('cours','examen','controle','tp_note','td') COLLATE utf8mb4_unicode_ci DEFAULT 'cours',
  `duree_examen` int DEFAULT NULL COMMENT 'Durée en minutes',
  `coefficient_examen` decimal(5,2) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_jour` (`jour`),
  KEY `idx_enseignant` (`enseignant_id`),
  KEY `idx_salle` (`salle_id`),
  KEY `idx_cours` (`cours_id`),
  KEY `idx_jour_heure` (`jour`,`heure_debut`),
  KEY `idx_type_creneau` (`type_creneau`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Déchargement des données de la table `emploidutemps`
--

INSERT INTO `emploidutemps` (`id`, `cours_id`, `enseignant_id`, `salle_id`, `jour`, `heure_debut`, `heure_fin`, `date_creation`, `type_creneau`, `duree_examen`, `coefficient_examen`) VALUES
(14, 1, 6, 1, 'Mardi', '04:31:00', '06:33:00', '2026-01-09 01:28:39', 'cours', NULL, NULL);

-- --------------------------------------------------------

--
-- Structure de la table `enseignants`
--

DROP TABLE IF EXISTS `enseignants`;
CREATE TABLE IF NOT EXISTS `enseignants` (
  `id` int NOT NULL AUTO_INCREMENT,
  `utilisateur_id` int NOT NULL,
  `specialite` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `total_heures_prevues` decimal(10,2) DEFAULT '0.00',
  `total_heures_effectuees` decimal(10,2) DEFAULT '0.00',
  `statut_presence` enum('PRESENT','ABSENT') COLLATE utf8mb4_unicode_ci DEFAULT 'PRESENT',
  `derniere_maj_presence` datetime DEFAULT NULL,
  `disponibilite` text COLLATE utf8mb4_unicode_ci COMMENT 'Disponibilités de l enseignant',
  PRIMARY KEY (`id`),
  UNIQUE KEY `utilisateur_id` (`utilisateur_id`),
  KEY `idx_utilisateur` (`utilisateur_id`),
  KEY `idx_statut_presence` (`statut_presence`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Déchargement des données de la table `enseignants`
--

INSERT INTO `enseignants` (`id`, `utilisateur_id`, `specialite`, `total_heures_prevues`, `total_heures_effectuees`, `statut_presence`, `derniere_maj_presence`, `disponibilite`) VALUES
(6, 3, 'Mathématiques', 0.00, 0.00, 'PRESENT', NULL, NULL),
(7, 4, 'Physique', 0.00, 0.00, 'PRESENT', NULL, NULL),
(8, 5, 'Informatique', 0.00, 0.00, 'PRESENT', NULL, NULL),
(9, 6, 'Chimie', 0.00, 0.00, 'PRESENT', NULL, NULL),
(10, 7, 'Anglais', 0.00, 0.00, 'PRESENT', NULL, NULL),
(11, 34, 'Non spécifié', 0.00, 0.00, 'PRESENT', NULL, NULL);

-- --------------------------------------------------------

--
-- Structure de la table `errorlogs`
--

DROP TABLE IF EXISTS `errorlogs`;
CREATE TABLE IF NOT EXISTS `errorlogs` (
  `id` int NOT NULL AUTO_INCREMENT,
  `error_type` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `error_message` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `error_trace` text COLLATE utf8mb4_unicode_ci,
  `utilisateur_id` int DEFAULT NULL,
  `url` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `error_context` text COLLATE utf8mb4_unicode_ci,
  `timestamp_error` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_error_type` (`error_type`),
  KEY `idx_timestamp` (`timestamp_error`),
  KEY `utilisateur_id` (`utilisateur_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Structure de la table `etudiants`
--

DROP TABLE IF EXISTS `etudiants`;
CREATE TABLE IF NOT EXISTS `etudiants` (
  `id` int NOT NULL AUTO_INCREMENT,
  `utilisateur_id` int NOT NULL,
  `filiere_id` int NOT NULL,
  `moyenne_generale` decimal(5,2) DEFAULT NULL,
  `date_maj` datetime DEFAULT NULL,
  `niveau` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT 'L1',
  PRIMARY KEY (`id`),
  UNIQUE KEY `utilisateur_id` (`utilisateur_id`),
  KEY `idx_utilisateur` (`utilisateur_id`),
  KEY `idx_filiere` (`filiere_id`),
  KEY `idx_niveau` (`niveau`)
) ENGINE=InnoDB AUTO_INCREMENT=25 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Déchargement des données de la table `etudiants`
--

INSERT INTO `etudiants` (`id`, `utilisateur_id`, `filiere_id`, `moyenne_generale`, `date_maj`, `niveau`) VALUES
(5, 8, 1, NULL, NULL, 'L1'),
(6, 9, 1, NULL, NULL, 'L1'),
(7, 10, 1, NULL, NULL, 'L1'),
(8, 11, 1, NULL, NULL, 'L1'),
(9, 12, 1, NULL, NULL, 'L1'),
(10, 13, 4, NULL, NULL, 'L1'),
(11, 14, 4, NULL, NULL, 'L1'),
(12, 15, 4, NULL, NULL, 'L1'),
(13, 16, 4, NULL, NULL, 'L1'),
(14, 17, 4, NULL, NULL, 'L1'),
(15, 18, 2, NULL, NULL, 'L2'),
(16, 19, 2, NULL, NULL, 'L2'),
(17, 20, 2, NULL, NULL, 'L2'),
(18, 21, 2, NULL, NULL, 'L2'),
(19, 22, 2, NULL, NULL, 'L2'),
(20, 23, 3, NULL, NULL, 'L3'),
(21, 24, 3, NULL, NULL, 'L3'),
(22, 25, 3, NULL, NULL, 'L3'),
(23, 26, 3, NULL, NULL, 'L3'),
(24, 27, 3, NULL, NULL, 'L3');

-- --------------------------------------------------------

--
-- Structure de la table `filieres`
--

DROP TABLE IF EXISTS `filieres`;
CREATE TABLE IF NOT EXISTS `filieres` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nom_filiere` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `niveau` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  `nombre_etudiants` int DEFAULT '0',
  `date_creation` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_niveau` (`niveau`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Déchargement des données de la table `filieres`
--

INSERT INTO `filieres` (`id`, `nom_filiere`, `niveau`, `nombre_etudiants`, `date_creation`) VALUES
(1, 'Informatique', 'L1', 2, '2025-12-08 16:31:08'),
(2, 'Informatique', 'L2', 0, '2025-12-08 16:31:08'),
(3, 'Informatique', 'L3', 0, '2025-12-08 16:31:08'),
(4, 'Gestion', 'L1', 0, '2025-12-08 16:31:08'),
(5, 'Gestion', 'L2', 0, '2025-12-08 16:31:08'),
(6, 'Gestion', 'L3', 0, '2025-12-08 16:31:08');

-- --------------------------------------------------------

--
-- Structure de la table `importhistorique`
--

DROP TABLE IF EXISTS `importhistorique`;
CREATE TABLE IF NOT EXISTS `importhistorique` (
  `id` int NOT NULL AUTO_INCREMENT,
  `importeur_id` int NOT NULL,
  `type_import` enum('UTILISATEURS','NOTES','EDT') COLLATE utf8mb4_unicode_ci NOT NULL,
  `fichier_nom` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `lignes_totales` int DEFAULT NULL,
  `lignes_succes` int DEFAULT NULL,
  `lignes_erreurs` int DEFAULT NULL,
  `details_erreurs` text COLLATE utf8mb4_unicode_ci,
  `date_import` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_importeur` (`importeur_id`),
  KEY `idx_type` (`type_import`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Structure de la table `importnotes`
--

DROP TABLE IF EXISTS `importnotes`;
CREATE TABLE IF NOT EXISTS `importnotes` (
  `id` int NOT NULL AUTO_INCREMENT,
  `cours_id` int NOT NULL,
  `fichier_nom` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `nb_notes_importees` int DEFAULT '0',
  `nb_erreurs` int DEFAULT '0',
  `details_erreurs` text COLLATE utf8mb4_unicode_ci,
  `importe_par` int NOT NULL,
  `date_import` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `importe_par` (`importe_par`),
  KEY `idx_cours` (`cours_id`),
  KEY `idx_date` (`date_import`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Structure de la table `messages`
--

DROP TABLE IF EXISTS `messages`;
CREATE TABLE IF NOT EXISTS `messages` (
  `id` int NOT NULL AUTO_INCREMENT,
  `expediteur_id` int NOT NULL,
  `destinataire_id` int DEFAULT NULL,
  `type_message` enum('SIGNALEMENT','NOTIFICATION','MESSAGE') COLLATE utf8mb4_unicode_ci DEFAULT 'MESSAGE',
  `sujet` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `contenu` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `lu` tinyint(1) DEFAULT '0',
  `date_envoi` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `expediteur_id` (`expediteur_id`),
  KEY `idx_destinataire` (`destinataire_id`),
  KEY `idx_lu` (`lu`),
  KEY `idx_type` (`type_message`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Structure de la table `monitoringsysteme`
--

DROP TABLE IF EXISTS `monitoringsysteme`;
CREATE TABLE IF NOT EXISTS `monitoringsysteme` (
  `id` int NOT NULL AUTO_INCREMENT,
  `type_metric` enum('UTILISATEURS_ACTIFS','TEMPS_REPONSE','ERREURS_SERVEUR','TAUX_VALIDATION_NOTES','BULLETINS_GENERES','CONFLITS_EDT') COLLATE utf8mb4_unicode_ci NOT NULL,
  `valeur` decimal(10,2) DEFAULT NULL,
  `unite` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `periode_debut` datetime NOT NULL,
  `periode_fin` datetime NOT NULL,
  `details` json DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_type` (`type_metric`),
  KEY `idx_periode` (`periode_debut`,`periode_fin`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Structure de la table `notes`
--

DROP TABLE IF EXISTS `notes`;
CREATE TABLE IF NOT EXISTS `notes` (
  `id` int NOT NULL AUTO_INCREMENT,
  `etudiant_id` int NOT NULL,
  `cours_id` int NOT NULL,
  `type_evaluation` enum('DS','Examen','TP','Projet','CC') COLLATE utf8mb4_unicode_ci NOT NULL,
  `note` decimal(5,2) NOT NULL,
  `coefficient` decimal(3,2) DEFAULT '1.00',
  `statut` enum('EN_ATTENTE_DIRECTEUR','VALIDÉ','EN_REVISION') COLLATE utf8mb4_unicode_ci DEFAULT 'EN_ATTENTE_DIRECTEUR',
  `date_soumission` datetime DEFAULT NULL,
  `date_evaluation` date NOT NULL,
  `commentaire` text COLLATE utf8mb4_unicode_ci,
  `saisi_par` int NOT NULL,
  `valide_par` int DEFAULT NULL,
  `date_validation` datetime DEFAULT NULL,
  `date_creation` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `date_modification` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `commentaire_validation` text COLLATE utf8mb4_unicode_ci,
  `validateur_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `saisi_par` (`saisi_par`),
  KEY `idx_statut` (`statut`),
  KEY `idx_etudiant` (`etudiant_id`),
  KEY `idx_cours` (`cours_id`),
  KEY `idx_date_eval` (`date_evaluation`),
  KEY `idx_notes_statut` (`statut`),
  KEY `idx_notes_validation` (`valide_par`,`date_validation`),
  KEY `idx_notes_filiere` (`cours_id`),
  KEY `idx_date_soumission` (`date_soumission`),
  KEY `fk_notes_validateur` (`validateur_id`),
  KEY `idx_type_evaluation` (`type_evaluation`),
  KEY `idx_etudiant_statut` (`etudiant_id`,`statut`),
  KEY `idx_cours_statut` (`cours_id`,`statut`),
  KEY `idx_statut_etudiant` (`statut`,`etudiant_id`)
) ;

--
-- Déclencheurs `notes`
--
DROP TRIGGER IF EXISTS `after_note_soumise`;
DELIMITER $$
CREATE TRIGGER `after_note_soumise` AFTER UPDATE ON `notes` FOR EACH ROW BEGIN
    -- On vérifie si le statut passe à 'EN_ATTENTE_DIRECTEUR'
    IF NEW.statut = 'EN_ATTENTE_DIRECTEUR' AND (OLD.statut IS NULL OR OLD.statut != 'EN_ATTENTE_DIRECTEUR') THEN
        
        -- On insère la notification
        INSERT INTO NotificationsWorkflow (
            destinataire_id, 
            expediteur_id, 
            type_notification, 
            titre, 
            message, 
            priorite
        )
        SELECT 
            u.id, 
            c.enseignant_id, -- Récupéré depuis la table Cours
            'NOTE_VALIDEE',
            'Nouvelle note à valider',
            CONCAT('Une note pour le cours "', c.nom_cours, '" attend validation'),
            'NORMALE'
        FROM Utilisateurs u
        INNER JOIN Cours c ON c.id = NEW.cours_id
        WHERE u.role = 'DIRECTEUR'
        LIMIT 1;
        
    END IF;
END
$$
DELIMITER ;
DROP TRIGGER IF EXISTS `after_note_validation`;
DELIMITER $$
CREATE TRIGGER `after_note_validation` AFTER UPDATE ON `notes` FOR EACH ROW BEGIN
    -- On réagit si le statut devient 'VALIDÉ'
    IF OLD.statut = 'EN_ATTENTE_DIRECTEUR' AND NEW.statut = 'VALIDÉ' THEN
        INSERT INTO Notifications (destinataire_id, type_notification, titre, message, priorite)
        VALUES (NEW.etudiant_id, 'NOTE_VALIDATED', 'Note validée !', 
               CONCAT('Votre note pour le cours id:', NEW.cours_id, ' est validée.'), 'normale');
    END IF;
END
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- Structure de la table `notifications`
--

DROP TABLE IF EXISTS `notifications`;
CREATE TABLE IF NOT EXISTS `notifications` (
  `id` int NOT NULL AUTO_INCREMENT,
  `destinataire_id` int NOT NULL,
  `type_notification` enum('NOTE_VALIDATED','BULLETIN_READY','NOTES_MISSING','BULLETIN_BLOCKED','CONFLICT_DETECTED','SIGNALEMENT_RECEIVED','IMPORT_COMPLETED','IMPORT_FAILED','GENERAL') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'GENERAL',
  `titre` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `message` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_read` tinyint(1) DEFAULT '0',
  `priorite` enum('basse','normale','haute','critique') COLLATE utf8mb4_unicode_ci DEFAULT 'normale',
  `lien_action` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `metadata` json DEFAULT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `read_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `destinataire_id` (`destinataire_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Structure de la table `notificationsworkflow`
--

DROP TABLE IF EXISTS `notificationsworkflow`;
CREATE TABLE IF NOT EXISTS `notificationsworkflow` (
  `id` int NOT NULL AUTO_INCREMENT,
  `destinataire_id` int NOT NULL,
  `expediteur_id` int DEFAULT NULL,
  `type_notification` enum('NOTE_VALIDEE','NOTE_REJETEE','NOTES_MANQUANTES','BULLETIN_DISPONIBLE','EDT_MODIFIE','ENSEIGNANT_ABSENT','CONFLIT_EDT','BLOCAGE_WORKFLOW','IMPORT_TERMINE') COLLATE utf8mb4_unicode_ci NOT NULL,
  `titre` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `message` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `lien_action` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'URL pour action directe',
  `priorite` enum('BASSE','NORMALE','HAUTE','URGENTE') COLLATE utf8mb4_unicode_ci DEFAULT 'NORMALE',
  `lu` tinyint(1) DEFAULT '0',
  `date_creation` datetime DEFAULT CURRENT_TIMESTAMP,
  `date_lecture` datetime DEFAULT NULL,
  `archivee` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `idx_destinataire` (`destinataire_id`),
  KEY `idx_lu` (`lu`),
  KEY `idx_type` (`type_notification`),
  KEY `idx_priorite` (`priorite`),
  KEY `idx_date` (`date_creation`),
  KEY `expediteur_id` (`expediteur_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Structure de la table `parentsetudiants`
--

DROP TABLE IF EXISTS `parentsetudiants`;
CREATE TABLE IF NOT EXISTS `parentsetudiants` (
  `id` int NOT NULL AUTO_INCREMENT,
  `parent_id` int NOT NULL,
  `etudiant_id` int NOT NULL,
  `lien_parente` enum('Pere','Mere','Tuteur','Autre') COLLATE utf8mb4_unicode_ci NOT NULL,
  `date_creation` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_parent_etudiant` (`parent_id`,`etudiant_id`),
  KEY `idx_parent` (`parent_id`),
  KEY `idx_etudiant` (`etudiant_id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Structure de la table `presences`
--

DROP TABLE IF EXISTS `presences`;
CREATE TABLE IF NOT EXISTS `presences` (
  `id` int NOT NULL AUTO_INCREMENT,
  `creneau_id` int NOT NULL,
  `enseignant_id` int NOT NULL,
  `statut` enum('present','absent','retard','non_marque') COLLATE utf8mb4_unicode_ci DEFAULT 'non_marque',
  `date_cours` date NOT NULL,
  `remarques` text COLLATE utf8mb4_unicode_ci,
  `marque_par` int DEFAULT NULL,
  `date_marquage` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `marque_par` (`marque_par`),
  KEY `idx_creneau` (`creneau_id`),
  KEY `idx_enseignant` (`enseignant_id`),
  KEY `idx_date` (`date_cours`),
  KEY `idx_statut` (`statut`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Structure de la table `promotions`
--

DROP TABLE IF EXISTS `promotions`;
CREATE TABLE IF NOT EXISTS `promotions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `etudiant_id` int NOT NULL,
  `niveau_ancien` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  `niveau_nouveau` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  `annee_academique` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `moyenne_obtenue` decimal(5,2) DEFAULT NULL,
  `date_promotion` datetime DEFAULT CURRENT_TIMESTAMP,
  `validateur_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_etudiant` (`etudiant_id`),
  KEY `idx_annee` (`annee_academique`),
  KEY `validateur_id` (`validateur_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Structure de la table `salles`
--

DROP TABLE IF EXISTS `salles`;
CREATE TABLE IF NOT EXISTS `salles` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nom_salle` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `capacite` int NOT NULL,
  `equipements` text COLLATE utf8mb4_unicode_ci,
  `date_creation` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `nom_salle` (`nom_salle`),
  KEY `idx_nom_salle` (`nom_salle`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Déchargement des données de la table `salles`
--

INSERT INTO `salles` (`id`, `nom_salle`, `capacite`, `equipements`, `date_creation`) VALUES
(1, 'Amphi A', 200, 'Projecteur, Micro, Climatisation', '2025-12-08 16:31:11'),
(2, 'Amphi B', 150, 'Projecteur, Tableau interactif', '2025-12-08 16:31:11'),
(3, 'Salle TD1', 40, 'Tableau blanc, Projecteur', '2025-12-08 16:31:11'),
(4, 'Salle TD2', 40, 'Tableau blanc, Projecteur', '2025-12-08 16:31:11'),
(5, 'Labo Info 1', 30, '30 Ordinateurs, Projecteur', '2025-12-08 16:31:11'),
(6, 'Labo Info 2', 30, '30 Ordinateurs, Projecteur', '2025-12-08 16:31:11');

-- --------------------------------------------------------

--
-- Structure de la table `securitylogs`
--

DROP TABLE IF EXISTS `securitylogs`;
CREATE TABLE IF NOT EXISTS `securitylogs` (
  `id` int NOT NULL AUTO_INCREMENT,
  `event_type` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `utilisateur_id` int DEFAULT NULL,
  `role` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `ip_address` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `details` text COLLATE utf8mb4_unicode_ci,
  `timestamp_event` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_event_type` (`event_type`),
  KEY `idx_timestamp` (`timestamp_event`),
  KEY `utilisateur_id` (`utilisateur_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Structure de la table `signalements`
--

DROP TABLE IF EXISTS `signalements`;
CREATE TABLE IF NOT EXISTS `signalements` (
  `id` int NOT NULL AUTO_INCREMENT,
  `etudiant_id` int NOT NULL,
  `note_id` int DEFAULT NULL,
  `cours_id` int DEFAULT NULL,
  `type_signalement` enum('ERREUR_NOTE','NOTE_MANQUANTE','ERREUR_COEFFICIENT','AUTRE') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'AUTRE',
  `motif` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `statut` enum('EN_ATTENTE','EN_TRAITEMENT','RESOLU','REJETE') COLLATE utf8mb4_unicode_ci DEFAULT 'EN_ATTENTE',
  `traite_par` int DEFAULT NULL,
  `reponse` text COLLATE utf8mb4_unicode_ci,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `resolved_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_etudiant` (`etudiant_id`),
  KEY `idx_note` (`note_id`),
  KEY `idx_statut` (`statut`),
  KEY `idx_created_at` (`created_at`),
  KEY `cours_id` (`cours_id`),
  KEY `traite_par` (`traite_par`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Doublure de structure pour la vue `statsnotifications`
-- (Voir ci-dessous la vue réelle)
--
DROP VIEW IF EXISTS `statsnotifications`;
CREATE TABLE IF NOT EXISTS `statsnotifications` (
`type_notification` enum('NOTE_VALIDEE','NOTE_REJETEE','NOTES_MANQUANTES','BULLETIN_DISPONIBLE','EDT_MODIFIE','ENSEIGNANT_ABSENT','CONFLIT_EDT','BLOCAGE_WORKFLOW','IMPORT_TERMINE')
,`priorite` enum('BASSE','NORMALE','HAUTE','URGENTE')
,`total` bigint
,`lues` decimal(23,0)
,`non_lues` decimal(23,0)
,`temps_moyen_lecture_minutes` decimal(24,4)
);

-- --------------------------------------------------------

--
-- Structure de la table `temp_backup_utilisateurs`
--

DROP TABLE IF EXISTS `temp_backup_utilisateurs`;
CREATE TABLE IF NOT EXISTS `temp_backup_utilisateurs` (
  `id` int NOT NULL DEFAULT '0',
  `nom` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `prenom` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `matricule` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(150) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `password_hash` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `role` enum('SUPER_ADMIN','ADMIN','DIRECTEUR','GESTIONNAIRE_PV','GESTIONNAIRE_EXAMENS','GESTIONNAIRE_EDT','GESTIONNAIRE_PRESENCES','ENSEIGNANT','ETUDIANT','PARENT','etudiant','enseignant','administration','sous_admin') COLLATE utf8mb4_unicode_ci NOT NULL,
  `actif` tinyint(1) DEFAULT '1',
  `created_by_id` int DEFAULT NULL,
  `last_login` datetime DEFAULT NULL,
  `date_creation` timestamp NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Déchargement des données de la table `temp_backup_utilisateurs`
--

INSERT INTO `temp_backup_utilisateurs` (`id`, `nom`, `prenom`, `matricule`, `email`, `password_hash`, `role`, `actif`, `created_by_id`, `last_login`, `date_creation`) VALUES
(1, 'SUPER', 'Admin', 'SA2025001', 'superadmin@uist.edu', 'scrypt:32768:8:1$ehxtSNJRSxN6iPKA$3cb19cbd48e53471c22b99d0d1d3dd44fbc8a803b13a178ec04d77e8f5bc2e87c9053a97e8f80bb81bd1b7e44f4183ca3abea9e45848223ac3a27374c1e3219a', 'SUPER_ADMIN', 1, NULL, '2026-01-09 00:41:57', '2025-12-08 16:31:10'),
(2, 'ADMIN', 'Principal', 'A2025001', 'admin@uist.edu', 'scrypt:32768:8:1$ehxtSNJRSxN6iPKA$3cb19cbd48e53471c22b99d0d1d3dd44fbc8a803b13a178ec04d77e8f5bc2e87c9053a97e8f80bb81bd1b7e44f4183ca3abea9e45848223ac3a27374c1e3219a', 'ADMIN', 1, NULL, '2026-01-08 23:58:06', '2025-12-08 16:31:10'),
(3, 'DIRECTEUR', 'Académique', 'DIR2025001', 'directeur@uist.edu', 'scrypt:32768:8:1$ehxtSNJRSxN6iPKA$3cb19cbd48e53471c22b99d0d1d3dd44fbc8a803b13a178ec04d77e8f5bc2e87c9053a97e8f80bb81bd1b7e44f4183ca3abea9e45848223ac3a27374c1e3219a', 'DIRECTEUR', 1, NULL, '2026-01-09 00:39:28', '2025-12-08 16:31:10'),
(8, 'DIOP', 'Mamadou', 'P2025001', 'mdiop@uist.edu', 'scrypt:32768:8:1$ehxtSNJRSxN6iPKA$3cb19cbd48e53471c22b99d0d1d3dd44fbc8a803b13a178ec04d77e8f5bc2e87c9053a97e8f80bb81bd1b7e44f4183ca3abea9e45848223ac3a27374c1e3219a', 'ENSEIGNANT', 1, NULL, '2026-01-08 23:57:06', '2025-12-08 16:31:10'),
(9, 'NDIAYE', 'Aissatou', 'P2025002', 'andiaye@uist.edu', 'scrypt:32768:8:1$ehxtSNJRSxN6iPKA$3cb19cbd48e53471c22b99d0d1d3dd44fbc8a803b13a178ec04d77e8f5bc2e87c9053a97e8f80bb81bd1b7e44f4183ca3abea9e45848223ac3a27374c1e3219a', 'ENSEIGNANT', 1, NULL, '2026-01-08 23:34:49', '2025-12-08 16:31:10'),
(10, 'FALL', 'Ousmane', 'E2025001', 'ofall@uist.edu', 'scrypt:32768:8:1$ehxtSNJRSxN6iPKA$3cb19cbd48e53471c22b99d0d1d3dd44fbc8a803b13a178ec04d77e8f5bc2e87c9053a97e8f80bb81bd1b7e44f4183ca3abea9e45848223ac3a27374c1e3219a', 'ETUDIANT', 1, NULL, '2026-01-09 01:04:14', '2025-12-08 16:31:10'),
(11, 'SALL', 'Fatou', 'E2025002', 'fsall@uist.edu', 'scrypt:32768:8:1$ehxtSNJRSxN6iPKA$3cb19cbd48e53471c22b99d0d1d3dd44fbc8a803b13a178ec04d77e8f5bc2e87c9053a97e8f80bb81bd1b7e44f4183ca3abea9e45848223ac3a27374c1e3219a', 'ETUDIANT', 1, NULL, '2026-01-08 23:34:38', '2025-12-08 16:31:10'),
(12, 'PARENT', 'Test', 'PAR2025001', 'parent@uist.edu', 'scrypt:32768:8:1$ehxtSNJRSxN6iPKA$3cb19cbd48e53471c22b99d0d1d3dd44fbc8a803b13a178ec04d77e8f5bc2e87c9053a97e8f80bb81bd1b7e44f4183ca3abea9e45848223ac3a27374c1e3219a', 'PARENT', 1, NULL, '2026-01-09 00:39:05', '2025-12-08 16:31:10'),
(13, 'bv', 'vc', 'P20250003', 'vc@gmail.com', 'scrypt:32768:8:1$gmLblSQHFzdBPF94$33b5fdae6b52396bea8a02c41850d00cc03b35b1b49ff513c0a126e15eb7ec97332676d08e644ee35f13339fd35759f053f17abc01c8a71487f809814e23a19f', 'ENSEIGNANT', 1, 3, NULL, '2025-12-09 00:40:43');

-- --------------------------------------------------------

--
-- Structure de la table `usageaudit`
--

DROP TABLE IF EXISTS `usageaudit`;
CREATE TABLE IF NOT EXISTS `usageaudit` (
  `id` int NOT NULL AUTO_INCREMENT,
  `utilisateur_id` int DEFAULT NULL,
  `action` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `table_affectee` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `enregistrement_id` int DEFAULT NULL,
  `details` text COLLATE utf8mb4_unicode_ci,
  `ip_address` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `user_agent` text COLLATE utf8mb4_unicode_ci,
  `date_action` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_utilisateur` (`utilisateur_id`),
  KEY `idx_date` (`date_action`),
  KEY `idx_action` (`action`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Structure de la table `utilisateurs`
--

DROP TABLE IF EXISTS `utilisateurs`;
CREATE TABLE IF NOT EXISTS `utilisateurs` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nom` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `prenom` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `matricule` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(150) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `password_hash` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `role` enum('SUPER_ADMIN','ADMIN','DIRECTEUR','GESTIONNAIRE_PV','GESTIONNAIRE_EXAMENS','GESTIONNAIRE_EDT','GESTIONNAIRE_PRESENCES','ENSEIGNANT','ETUDIANT','PARENT','etudiant','enseignant','administration','sous_admin') COLLATE utf8mb4_unicode_ci NOT NULL,
  `actif` tinyint(1) DEFAULT '1',
  `created_by_id` int DEFAULT NULL,
  `last_login` datetime DEFAULT NULL,
  `date_creation` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `matricule` (`matricule`),
  UNIQUE KEY `email` (`email`),
  KEY `created_by_id` (`created_by_id`),
  KEY `idx_matricule` (`matricule`),
  KEY `idx_email` (`email`),
  KEY `idx_role` (`role`)
) ENGINE=InnoDB AUTO_INCREMENT=35 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Déchargement des données de la table `utilisateurs`
--

INSERT INTO `utilisateurs` (`id`, `nom`, `prenom`, `matricule`, `email`, `password_hash`, `role`, `actif`, `created_by_id`, `last_login`, `date_creation`) VALUES
(1, 'System', 'Administrator', 'SA2025001', 'admin@uist-2its.edu', 'scrypt:32768:8:1$YtduItNNIQyCbHpq$b16bf5c2c22c7cadd128dc6130a97dfcb2473b2f2750d6bab1bed80f0505aec943a37bc46b40014b511f030b60c09403531a04863b6c54c49a79301c14dd089c', 'SUPER_ADMIN', 1, NULL, '2026-01-09 01:20:45', '2026-01-09 01:16:33'),
(2, 'Diallo', 'Mohamed', 'DIR2025001', 'directeur@uist-2its.edu', 'scrypt:32768:8:1$YtduItNNIQyCbHpq$b16bf5c2c22c7cadd128dc6130a97dfcb2473b2f2750d6bab1bed80f0505aec943a37bc46b40014b511f030b60c09403531a04863b6c54c49a79301c14dd089c', 'DIRECTEUR', 1, NULL, '2026-01-09 01:30:01', '2026-01-09 01:16:33'),
(3, 'Traoré', 'Amadou', 'P2025001', 'a.traore@uist-2its.edu', 'scrypt:32768:8:1$YtduItNNIQyCbHpq$b16bf5c2c22c7cadd128dc6130a97dfcb2473b2f2750d6bab1bed80f0505aec943a37bc46b40014b511f030b60c09403531a04863b6c54c49a79301c14dd089c', 'ENSEIGNANT', 1, NULL, '2026-01-09 01:17:40', '2026-01-09 01:16:33'),
(4, 'Koné', 'Fatoumata', 'P2025002', 'f.kone@uist-2its.edu', 'scrypt:32768:8:1$YtduItNNIQyCbHpq$b16bf5c2c22c7cadd128dc6130a97dfcb2473b2f2750d6bab1bed80f0505aec943a37bc46b40014b511f030b60c09403531a04863b6c54c49a79301c14dd089c', 'ENSEIGNANT', 1, NULL, '2026-01-09 01:16:33', '2026-01-09 01:16:33'),
(5, 'Touré', 'Ibrahim', 'P2025003', 'i.toure@uist-2its.edu', 'scrypt:32768:8:1$YtduItNNIQyCbHpq$b16bf5c2c22c7cadd128dc6130a97dfcb2473b2f2750d6bab1bed80f0505aec943a37bc46b40014b511f030b60c09403531a04863b6c54c49a79301c14dd089c', 'ENSEIGNANT', 1, NULL, '2026-01-09 01:16:33', '2026-01-09 01:16:33'),
(6, 'Camara', 'Aissata', 'P2025004', 'a.camara@uist-2its.edu', 'scrypt:32768:8:1$YtduItNNIQyCbHpq$b16bf5c2c22c7cadd128dc6130a97dfcb2473b2f2750d6bab1bed80f0505aec943a37bc46b40014b511f030b60c09403531a04863b6c54c49a79301c14dd089c', 'ENSEIGNANT', 1, NULL, '2026-01-09 01:16:34', '2026-01-09 01:16:33'),
(7, 'Keita', 'Sekou', 'P2025005', 's.keita@uist-2its.edu', 'scrypt:32768:8:1$YtduItNNIQyCbHpq$b16bf5c2c22c7cadd128dc6130a97dfcb2473b2f2750d6bab1bed80f0505aec943a37bc46b40014b511f030b60c09403531a04863b6c54c49a79301c14dd089c', 'ENSEIGNANT', 1, NULL, '2026-01-09 01:16:34', '2026-01-09 01:16:33'),
(8, 'Sanogo', 'Ousmane', 'E2025001', 'o.sanogo@student.uist-2its.edu', 'scrypt:32768:8:1$YtduItNNIQyCbHpq$b16bf5c2c22c7cadd128dc6130a97dfcb2473b2f2750d6bab1bed80f0505aec943a37bc46b40014b511f030b60c09403531a04863b6c54c49a79301c14dd089c', 'ETUDIANT', 1, NULL, '2026-01-09 01:28:59', '2026-01-09 01:16:33'),
(9, 'Coulibaly', 'Mariam', 'E2025002', 'm.coulibaly@student.uist-2its.edu', 'scrypt:32768:8:1$YtduItNNIQyCbHpq$b16bf5c2c22c7cadd128dc6130a97dfcb2473b2f2750d6bab1bed80f0505aec943a37bc46b40014b511f030b60c09403531a04863b6c54c49a79301c14dd089c', 'ETUDIANT', 1, NULL, '2026-01-09 01:29:16', '2026-01-09 01:16:33'),
(10, 'Bamba', 'Bakary', 'E2025003', 'b.bamba@student.uist-2its.edu', 'scrypt:32768:8:1$YtduItNNIQyCbHpq$b16bf5c2c22c7cadd128dc6130a97dfcb2473b2f2750d6bab1bed80f0505aec943a37bc46b40014b511f030b60c09403531a04863b6c54c49a79301c14dd089c', 'ETUDIANT', 1, NULL, '2026-01-09 01:16:34', '2026-01-09 01:16:33'),
(11, 'Sissoko', 'Aminata', 'E2025004', 'a.sissoko@student.uist-2its.edu', 'scrypt:32768:8:1$YtduItNNIQyCbHpq$b16bf5c2c22c7cadd128dc6130a97dfcb2473b2f2750d6bab1bed80f0505aec943a37bc46b40014b511f030b60c09403531a04863b6c54c49a79301c14dd089c', 'ETUDIANT', 1, NULL, '2026-01-09 01:16:34', '2026-01-09 01:16:33'),
(12, 'Diarra', 'Seydou', 'E2025005', 's.diarra@student.uist-2its.edu', 'scrypt:32768:8:1$YtduItNNIQyCbHpq$b16bf5c2c22c7cadd128dc6130a97dfcb2473b2f2750d6bab1bed80f0505aec943a37bc46b40014b511f030b60c09403531a04863b6c54c49a79301c14dd089c', 'ETUDIANT', 1, NULL, '2026-01-09 01:16:34', '2026-01-09 01:16:33'),
(13, 'Sidibé', 'Kadiatou', 'E2025006', 'k.sidibe@student.uist-2its.edu', 'scrypt:32768:8:1$YtduItNNIQyCbHpq$b16bf5c2c22c7cadd128dc6130a97dfcb2473b2f2750d6bab1bed80f0505aec943a37bc46b40014b511f030b60c09403531a04863b6c54c49a79301c14dd089c', 'ETUDIANT', 1, NULL, '2026-01-09 01:16:34', '2026-01-09 01:16:33'),
(14, 'Maiga', 'Mamadou', 'E2025007', 'm.maiga@student.uist-2its.edu', 'scrypt:32768:8:1$YtduItNNIQyCbHpq$b16bf5c2c22c7cadd128dc6130a97dfcb2473b2f2750d6bab1bed80f0505aec943a37bc46b40014b511f030b60c09403531a04863b6c54c49a79301c14dd089c', 'ETUDIANT', 1, NULL, '2026-01-09 01:16:34', '2026-01-09 01:16:33'),
(15, 'Cissé', 'Salimata', 'E2025008', 's.cisse@student.uist-2its.edu', 'scrypt:32768:8:1$YtduItNNIQyCbHpq$b16bf5c2c22c7cadd128dc6130a97dfcb2473b2f2750d6bab1bed80f0505aec943a37bc46b40014b511f030b60c09403531a04863b6c54c49a79301c14dd089c', 'ETUDIANT', 1, NULL, '2026-01-09 01:16:34', '2026-01-09 01:16:33'),
(16, 'Bagayoko', 'Adama', 'E2025009', 'a.bagayoko@student.uist-2its.edu', 'scrypt:32768:8:1$YtduItNNIQyCbHpq$b16bf5c2c22c7cadd128dc6130a97dfcb2473b2f2750d6bab1bed80f0505aec943a37bc46b40014b511f030b60c09403531a04863b6c54c49a79301c14dd089c', 'ETUDIANT', 1, NULL, '2026-01-09 01:16:34', '2026-01-09 01:16:33'),
(17, 'Konaté', 'Assitan', 'E2025010', 'a.konate@student.uist-2its.edu', 'scrypt:32768:8:1$YtduItNNIQyCbHpq$b16bf5c2c22c7cadd128dc6130a97dfcb2473b2f2750d6bab1bed80f0505aec943a37bc46b40014b511f030b60c09403531a04863b6c54c49a79301c14dd089c', 'ETUDIANT', 1, NULL, '2026-01-09 01:16:34', '2026-01-09 01:16:33'),
(18, 'Dembélé', 'Lassana', 'E2025011', 'l.dembele@student.uist-2its.edu', 'scrypt:32768:8:1$YtduItNNIQyCbHpq$b16bf5c2c22c7cadd128dc6130a97dfcb2473b2f2750d6bab1bed80f0505aec943a37bc46b40014b511f030b60c09403531a04863b6c54c49a79301c14dd089c', 'ETUDIANT', 1, NULL, '2026-01-09 01:29:37', '2026-01-09 01:16:33'),
(19, 'Fofana', 'Aminata', 'E2025012', 'a.fofana@student.uist-2its.edu', 'scrypt:32768:8:1$YtduItNNIQyCbHpq$b16bf5c2c22c7cadd128dc6130a97dfcb2473b2f2750d6bab1bed80f0505aec943a37bc46b40014b511f030b60c09403531a04863b6c54c49a79301c14dd089c', 'ETUDIANT', 1, NULL, '2026-01-09 01:16:34', '2026-01-09 01:16:33'),
(20, 'Sylla', 'Moussa', 'E2025013', 'm.sylla@student.uist-2its.edu', 'scrypt:32768:8:1$YtduItNNIQyCbHpq$b16bf5c2c22c7cadd128dc6130a97dfcb2473b2f2750d6bab1bed80f0505aec943a37bc46b40014b511f030b60c09403531a04863b6c54c49a79301c14dd089c', 'ETUDIANT', 1, NULL, '2026-01-09 01:16:34', '2026-01-09 01:16:33'),
(21, 'Berthe', 'Fatoumata', 'E2025014', 'f.berthe@student.uist-2its.edu', 'scrypt:32768:8:1$YtduItNNIQyCbHpq$b16bf5c2c22c7cadd128dc6130a97dfcb2473b2f2750d6bab1bed80f0505aec943a37bc46b40014b511f030b60c09403531a04863b6c54c49a79301c14dd089c', 'ETUDIANT', 1, NULL, '2026-01-09 01:16:34', '2026-01-09 01:16:33'),
(22, 'Kante', 'Boubacar', 'E2025015', 'b.kante@student.uist-2its.edu', 'scrypt:32768:8:1$YtduItNNIQyCbHpq$b16bf5c2c22c7cadd128dc6130a97dfcb2473b2f2750d6bab1bed80f0505aec943a37bc46b40014b511f030b60c09403531a04863b6c54c49a79301c14dd089c', 'ETUDIANT', 1, NULL, '2026-01-09 01:16:34', '2026-01-09 01:16:33'),
(23, 'Samaké', 'Rokia', 'E2025016', 'r.samake@student.uist-2its.edu', 'scrypt:32768:8:1$YtduItNNIQyCbHpq$b16bf5c2c22c7cadd128dc6130a97dfcb2473b2f2750d6bab1bed80f0505aec943a37bc46b40014b511f030b60c09403531a04863b6c54c49a79301c14dd089c', 'ETUDIANT', 1, NULL, '2026-01-09 01:16:34', '2026-01-09 01:16:33'),
(24, 'Guindo', 'Abdoulaye', 'E2025017', 'a.guindo@student.uist-2its.edu', 'scrypt:32768:8:1$YtduItNNIQyCbHpq$b16bf5c2c22c7cadd128dc6130a97dfcb2473b2f2750d6bab1bed80f0505aec943a37bc46b40014b511f030b60c09403531a04863b6c54c49a79301c14dd089c', 'ETUDIANT', 1, NULL, '2026-01-09 01:16:34', '2026-01-09 01:16:33'),
(25, 'Dicko', 'Awa', 'E2025018', 'a.dicko@student.uist-2its.edu', 'scrypt:32768:8:1$YtduItNNIQyCbHpq$b16bf5c2c22c7cadd128dc6130a97dfcb2473b2f2750d6bab1bed80f0505aec943a37bc46b40014b511f030b60c09403531a04863b6c54c49a79301c14dd089c', 'ETUDIANT', 1, NULL, '2026-01-09 01:16:34', '2026-01-09 01:16:33'),
(26, 'Barry', 'Alpha', 'E2025019', 'a.barry@student.uist-2its.edu', 'scrypt:32768:8:1$YtduItNNIQyCbHpq$b16bf5c2c22c7cadd128dc6130a97dfcb2473b2f2750d6bab1bed80f0505aec943a37bc46b40014b511f030b60c09403531a04863b6c54c49a79301c14dd089c', 'ETUDIANT', 1, NULL, '2026-01-09 01:16:34', '2026-01-09 01:16:33'),
(27, 'Tall', 'Hawa', 'E2025020', 'h.tall@student.uist-2its.edu', 'scrypt:32768:8:1$YtduItNNIQyCbHpq$b16bf5c2c22c7cadd128dc6130a97dfcb2473b2f2750d6bab1bed80f0505aec943a37bc46b40014b511f030b60c09403531a04863b6c54c49a79301c14dd089c', 'ETUDIANT', 1, NULL, '2026-01-09 01:16:34', '2026-01-09 01:16:33'),
(28, 'Sanogo', 'Mamadou', 'PAR2025001', 'm.sanogo@parent.uist-2its.edu', 'scrypt:32768:8:1$YtduItNNIQyCbHpq$b16bf5c2c22c7cadd128dc6130a97dfcb2473b2f2750d6bab1bed80f0505aec943a37bc46b40014b511f030b60c09403531a04863b6c54c49a79301c14dd089c', 'PARENT', 1, NULL, '2026-01-09 01:16:34', '2026-01-09 01:16:33'),
(29, 'Coulibaly', 'Salif', 'PAR2025002', 's.coulibaly@parent.uist-2its.edu', 'scrypt:32768:8:1$YtduItNNIQyCbHpq$b16bf5c2c22c7cadd128dc6130a97dfcb2473b2f2750d6bab1bed80f0505aec943a37bc46b40014b511f030b60c09403531a04863b6c54c49a79301c14dd089c', 'PARENT', 1, NULL, '2026-01-09 01:16:34', '2026-01-09 01:16:33'),
(30, 'Sidibé', 'Moussa', 'PAR2025003', 'm.sidibe@parent.uist-2its.edu', 'scrypt:32768:8:1$YtduItNNIQyCbHpq$b16bf5c2c22c7cadd128dc6130a97dfcb2473b2f2750d6bab1bed80f0505aec943a37bc46b40014b511f030b60c09403531a04863b6c54c49a79301c14dd089c', 'PARENT', 1, NULL, '2026-01-09 01:16:34', '2026-01-09 01:16:33'),
(31, 'Dembélé', 'Bakary', 'PAR2025004', 'b.dembele@parent.uist-2its.edu', 'scrypt:32768:8:1$YtduItNNIQyCbHpq$b16bf5c2c22c7cadd128dc6130a97dfcb2473b2f2750d6bab1bed80f0505aec943a37bc46b40014b511f030b60c09403531a04863b6c54c49a79301c14dd089c', 'PARENT', 1, NULL, '2026-01-09 01:16:34', '2026-01-09 01:16:33'),
(32, 'Samaké', 'Ibrahim', 'PAR2025005', 'i.samake@parent.uist-2its.edu', 'scrypt:32768:8:1$YtduItNNIQyCbHpq$b16bf5c2c22c7cadd128dc6130a97dfcb2473b2f2750d6bab1bed80f0505aec943a37bc46b40014b511f030b60c09403531a04863b6c54c49a79301c14dd089c', 'PARENT', 1, NULL, '2026-01-09 01:16:34', '2026-01-09 01:16:33'),
(33, 'orso', 'mechi', 'E20260001', '', 'scrypt:32768:8:1$qLE8Si2BIcmQhQrD$29cea9d2d08bc44374edc4a85058707ced0800fddf39ea3e5ca37f21bc5de07a994b0357b6a93c3338b762e0ddeed3304519adf410be92110f862166ad075214', 'ETUDIANT', 1, 2, NULL, '2026-01-09 01:22:11'),
(34, 'PLATAUX', 'CYBER', 'P20260001', 'admin@maivaprint.com', 'scrypt:32768:8:1$wsiZ1pjojMr5SMCc$80ad663b23d70f44a78fcd17b6ddef8025883e86c9a5af22f3d7fb0c0959106016713b5601da16d15761f3d9e361eb806c403f4555d0aee48e8b31dd8a518a2b', 'ENSEIGNANT', 1, 2, NULL, '2026-01-09 01:23:15');

-- --------------------------------------------------------

--
-- Doublure de structure pour la vue `utilisateursactifs`
-- (Voir ci-dessous la vue réelle)
--
DROP VIEW IF EXISTS `utilisateursactifs`;
CREATE TABLE IF NOT EXISTS `utilisateursactifs` (
`id` int
,`matricule` varchar(50)
,`nom` varchar(100)
,`prenom` varchar(100)
,`role` enum('SUPER_ADMIN','ADMIN','DIRECTEUR','GESTIONNAIRE_PV','GESTIONNAIRE_EXAMENS','GESTIONNAIRE_EDT','GESTIONNAIRE_PRESENCES','ENSEIGNANT','ETUDIANT','PARENT','etudiant','enseignant','administration','sous_admin')
,`heure_connexion` datetime
,`duree_minutes` bigint
);

-- --------------------------------------------------------

--
-- Doublure de structure pour la vue `vue_notifications_non_lues`
-- (Voir ci-dessous la vue réelle)
--
DROP VIEW IF EXISTS `vue_notifications_non_lues`;
CREATE TABLE IF NOT EXISTS `vue_notifications_non_lues` (
`utilisateur_id` int
,`nom` varchar(100)
,`prenom` varchar(100)
,`nb_notifications` bigint
);

-- --------------------------------------------------------

--
-- Doublure de structure pour la vue `vue_signalements_en_attente`
-- (Voir ci-dessous la vue réelle)
--
DROP VIEW IF EXISTS `vue_signalements_en_attente`;
CREATE TABLE IF NOT EXISTS `vue_signalements_en_attente` (
`id` int
,`motif` text
,`statut` enum('EN_ATTENTE','EN_TRAITEMENT','RESOLU','REJETE')
,`etudiant_nom` varchar(100)
,`nom_cours` varchar(150)
);

-- --------------------------------------------------------

--
-- Doublure de structure pour la vue `v_emploi_temps_complet`
-- (Voir ci-dessous la vue réelle)
--
DROP VIEW IF EXISTS `v_emploi_temps_complet`;
CREATE TABLE IF NOT EXISTS `v_emploi_temps_complet` (
`id` int
,`cours_id` int
,`enseignant_id` int
,`salle_id` int
,`jour` enum('Lundi','Mardi','Mercredi','Jeudi','Vendredi','Samedi')
,`heure_debut` time
,`heure_fin` time
,`date_creation` timestamp
,`nom_cours` varchar(150)
,`type_cours` enum('CM','TD','TP')
,`filiere_id` int
,`nom_filiere` varchar(100)
,`niveau` varchar(10)
,`enseignant_nom` varchar(100)
,`enseignant_prenom` varchar(100)
,`enseignant_matricule` varchar(50)
,`nom_salle` varchar(50)
,`capacite` int
);

-- --------------------------------------------------------

--
-- Doublure de structure pour la vue `v_notes_details`
-- (Voir ci-dessous la vue réelle)
--
DROP VIEW IF EXISTS `v_notes_details`;
CREATE TABLE IF NOT EXISTS `v_notes_details` (
`id` int
,`etudiant_id` int
,`cours_id` int
,`type_evaluation` enum('DS','Examen','TP','Projet','CC')
,`note` decimal(5,2)
,`coefficient` decimal(3,2)
,`statut` enum('EN_ATTENTE_DIRECTEUR','VALIDÉ','EN_REVISION')
,`date_evaluation` date
,`commentaire` text
,`saisi_par` int
,`valide_par` int
,`date_validation` datetime
,`date_creation` timestamp
,`date_modification` timestamp
,`commentaire_validation` text
,`etudiant_matricule` varchar(50)
,`etudiant_nom` varchar(100)
,`etudiant_prenom` varchar(100)
,`nom_cours` varchar(150)
,`type_cours` enum('CM','TD','TP')
,`filiere_id` int
,`nom_filiere` varchar(100)
,`niveau` varchar(10)
,`saisi_par_nom` varchar(100)
,`saisi_par_prenom` varchar(100)
,`valide_par_nom` varchar(100)
,`valide_par_prenom` varchar(100)
);

-- --------------------------------------------------------

--
-- Doublure de structure pour la vue `v_stats_filieres`
-- (Voir ci-dessous la vue réelle)
--
DROP VIEW IF EXISTS `v_stats_filieres`;
CREATE TABLE IF NOT EXISTS `v_stats_filieres` (
`filiere_id` int
,`nom_filiere` varchar(100)
,`niveau` varchar(10)
,`nb_etudiants` bigint
,`nb_cours` bigint
,`nb_enseignants` bigint
,`nb_notes_total` bigint
,`nb_notes_validees` decimal(23,0)
,`nb_notes_en_attente` decimal(23,0)
,`moyenne_generale` decimal(6,2)
);

-- --------------------------------------------------------

--
-- Structure de la vue `blocagesactifs`
--
DROP TABLE IF EXISTS `blocagesactifs`;

DROP VIEW IF EXISTS `blocagesactifs`;
CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `blocagesactifs`  AS SELECT `b`.`id` AS `id`, `b`.`type_blocage` AS `type_blocage`, `b`.`entite_bloquee` AS `entite_bloquee`, `u1`.`matricule` AS `bloquant_matricule`, `u1`.`nom` AS `bloquant_nom`, `u1`.`role` AS `bloquant_role`, `u2`.`matricule` AS `bloque_matricule`, `u2`.`nom` AS `bloque_nom`, `u2`.`role` AS `bloque_role`, `b`.`description` AS `description`, `b`.`date_creation` AS `date_creation`, timestampdiff(HOUR,`b`.`date_creation`,now()) AS `heures_blocage` FROM ((`blocagesworkflow` `b` left join `utilisateurs` `u1` on((`b`.`acteur_bloquant_id` = `u1`.`id`))) left join `utilisateurs` `u2` on((`b`.`acteur_bloque_id` = `u2`.`id`))) WHERE (`b`.`statut` = 'ACTIF') ORDER BY `b`.`date_creation` DESC ;

-- --------------------------------------------------------

--
-- Structure de la vue `statsnotifications`
--
DROP TABLE IF EXISTS `statsnotifications`;

DROP VIEW IF EXISTS `statsnotifications`;
CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `statsnotifications`  AS SELECT `notificationsworkflow`.`type_notification` AS `type_notification`, `notificationsworkflow`.`priorite` AS `priorite`, count(0) AS `total`, sum((case when (`notificationsworkflow`.`lu` = true) then 1 else 0 end)) AS `lues`, sum((case when (`notificationsworkflow`.`lu` = false) then 1 else 0 end)) AS `non_lues`, avg(timestampdiff(MINUTE,`notificationsworkflow`.`date_creation`,`notificationsworkflow`.`date_lecture`)) AS `temps_moyen_lecture_minutes` FROM `notificationsworkflow` WHERE (`notificationsworkflow`.`date_creation` >= (now() - interval 7 day)) GROUP BY `notificationsworkflow`.`type_notification`, `notificationsworkflow`.`priorite` ;

-- --------------------------------------------------------

--
-- Structure de la vue `utilisateursactifs`
--
DROP TABLE IF EXISTS `utilisateursactifs`;

DROP VIEW IF EXISTS `utilisateursactifs`;
CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `utilisateursactifs`  AS SELECT `u`.`id` AS `id`, `u`.`matricule` AS `matricule`, `u`.`nom` AS `nom`, `u`.`prenom` AS `prenom`, `u`.`role` AS `role`, `a`.`timestamp_debut` AS `heure_connexion`, timestampdiff(MINUTE,`a`.`timestamp_debut`,now()) AS `duree_minutes` FROM (`utilisateurs` `u` join `activiteutilisateurs` `a` on((`u`.`id` = `a`.`utilisateur_id`))) WHERE ((`a`.`type_activite` = 'CONNEXION') AND (`a`.`timestamp_fin` is null) AND (`a`.`timestamp_debut` >= (now() - interval 12 hour))) ;

-- --------------------------------------------------------

--
-- Structure de la vue `vue_notifications_non_lues`
--
DROP TABLE IF EXISTS `vue_notifications_non_lues`;

DROP VIEW IF EXISTS `vue_notifications_non_lues`;
CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `vue_notifications_non_lues`  AS SELECT `u`.`id` AS `utilisateur_id`, `u`.`nom` AS `nom`, `u`.`prenom` AS `prenom`, count(`n`.`id`) AS `nb_notifications` FROM (`utilisateurs` `u` left join `notifications` `n` on(((`u`.`id` = `n`.`destinataire_id`) and (`n`.`is_read` = false)))) GROUP BY `u`.`id`, `u`.`nom`, `u`.`prenom` ;

-- --------------------------------------------------------

--
-- Structure de la vue `vue_signalements_en_attente`
--
DROP TABLE IF EXISTS `vue_signalements_en_attente`;

DROP VIEW IF EXISTS `vue_signalements_en_attente`;
CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `vue_signalements_en_attente`  AS SELECT `s`.`id` AS `id`, `s`.`motif` AS `motif`, `s`.`statut` AS `statut`, `u`.`nom` AS `etudiant_nom`, `c`.`nom_cours` AS `nom_cours` FROM (((`signalements` `s` join `utilisateurs` `u` on((`s`.`etudiant_id` = `u`.`id`))) left join `notes` `n` on((`s`.`note_id` = `n`.`id`))) left join `cours` `c` on((`n`.`cours_id` = `c`.`id`))) WHERE (`s`.`statut` = 'EN_ATTENTE') ;

-- --------------------------------------------------------

--
-- Structure de la vue `v_emploi_temps_complet`
--
DROP TABLE IF EXISTS `v_emploi_temps_complet`;

DROP VIEW IF EXISTS `v_emploi_temps_complet`;
CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `v_emploi_temps_complet`  AS SELECT `edt`.`id` AS `id`, `edt`.`cours_id` AS `cours_id`, `edt`.`enseignant_id` AS `enseignant_id`, `edt`.`salle_id` AS `salle_id`, `edt`.`jour` AS `jour`, `edt`.`heure_debut` AS `heure_debut`, `edt`.`heure_fin` AS `heure_fin`, `edt`.`date_creation` AS `date_creation`, `c`.`nom_cours` AS `nom_cours`, `c`.`type_cours` AS `type_cours`, `f`.`id` AS `filiere_id`, `f`.`nom_filiere` AS `nom_filiere`, `f`.`niveau` AS `niveau`, `u`.`nom` AS `enseignant_nom`, `u`.`prenom` AS `enseignant_prenom`, `u`.`matricule` AS `enseignant_matricule`, `s`.`nom_salle` AS `nom_salle`, `s`.`capacite` AS `capacite` FROM (((((`emploidutemps` `edt` join `cours` `c` on((`edt`.`cours_id` = `c`.`id`))) join `filieres` `f` on((`c`.`filiere_id` = `f`.`id`))) join `enseignants` `ens` on((`edt`.`enseignant_id` = `ens`.`utilisateur_id`))) join `utilisateurs` `u` on((`ens`.`utilisateur_id` = `u`.`id`))) join `salles` `s` on((`edt`.`salle_id` = `s`.`id`))) ;

-- --------------------------------------------------------

--
-- Structure de la vue `v_notes_details`
--
DROP TABLE IF EXISTS `v_notes_details`;

DROP VIEW IF EXISTS `v_notes_details`;
CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `v_notes_details`  AS SELECT `n`.`id` AS `id`, `n`.`etudiant_id` AS `etudiant_id`, `n`.`cours_id` AS `cours_id`, `n`.`type_evaluation` AS `type_evaluation`, `n`.`note` AS `note`, `n`.`coefficient` AS `coefficient`, `n`.`statut` AS `statut`, `n`.`date_evaluation` AS `date_evaluation`, `n`.`commentaire` AS `commentaire`, `n`.`saisi_par` AS `saisi_par`, `n`.`valide_par` AS `valide_par`, `n`.`date_validation` AS `date_validation`, `n`.`date_creation` AS `date_creation`, `n`.`date_modification` AS `date_modification`, `n`.`commentaire_validation` AS `commentaire_validation`, `u_etud`.`matricule` AS `etudiant_matricule`, `u_etud`.`nom` AS `etudiant_nom`, `u_etud`.`prenom` AS `etudiant_prenom`, `c`.`nom_cours` AS `nom_cours`, `c`.`type_cours` AS `type_cours`, `f`.`id` AS `filiere_id`, `f`.`nom_filiere` AS `nom_filiere`, `f`.`niveau` AS `niveau`, `u_saisi`.`nom` AS `saisi_par_nom`, `u_saisi`.`prenom` AS `saisi_par_prenom`, `u_valid`.`nom` AS `valide_par_nom`, `u_valid`.`prenom` AS `valide_par_prenom` FROM ((((((`notes` `n` join `etudiants` `e` on((`n`.`etudiant_id` = `e`.`utilisateur_id`))) join `utilisateurs` `u_etud` on((`e`.`utilisateur_id` = `u_etud`.`id`))) join `cours` `c` on((`n`.`cours_id` = `c`.`id`))) join `filieres` `f` on((`c`.`filiere_id` = `f`.`id`))) join `utilisateurs` `u_saisi` on((`n`.`saisi_par` = `u_saisi`.`id`))) left join `utilisateurs` `u_valid` on((`n`.`valide_par` = `u_valid`.`id`))) ;

-- --------------------------------------------------------

--
-- Structure de la vue `v_stats_filieres`
--
DROP TABLE IF EXISTS `v_stats_filieres`;

DROP VIEW IF EXISTS `v_stats_filieres`;
CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `v_stats_filieres`  AS SELECT `f`.`id` AS `filiere_id`, `f`.`nom_filiere` AS `nom_filiere`, `f`.`niveau` AS `niveau`, count(distinct `e`.`utilisateur_id`) AS `nb_etudiants`, count(distinct `c`.`id`) AS `nb_cours`, count(distinct `edt`.`enseignant_id`) AS `nb_enseignants`, count(distinct `n`.`id`) AS `nb_notes_total`, sum((case when (`n`.`statut` = 'VALIDÉ') then 1 else 0 end)) AS `nb_notes_validees`, sum((case when (`n`.`statut` = 'EN_ATTENTE_DIRECTEUR') then 1 else 0 end)) AS `nb_notes_en_attente`, round(avg((case when (`n`.`statut` = 'VALIDÉ') then `n`.`note` end)),2) AS `moyenne_generale` FROM ((((`filieres` `f` left join `etudiants` `e` on((`f`.`id` = `e`.`filiere_id`))) left join `cours` `c` on((`f`.`id` = `c`.`filiere_id`))) left join `emploidutemps` `edt` on((`c`.`id` = `edt`.`cours_id`))) left join `notes` `n` on((`c`.`id` = `n`.`cours_id`))) GROUP BY `f`.`id`, `f`.`nom_filiere`, `f`.`niveau` ;

--
-- Contraintes pour les tables déchargées
--

--
-- Contraintes pour la table `activiteutilisateurs`
--
ALTER TABLE `activiteutilisateurs`
  ADD CONSTRAINT `activiteutilisateurs_ibfk_1` FOREIGN KEY (`utilisateur_id`) REFERENCES `utilisateurs` (`id`) ON DELETE CASCADE;

--
-- Contraintes pour la table `assignationsenseignants`
--
ALTER TABLE `assignationsenseignants`
  ADD CONSTRAINT `assignationsenseignants_ibfk_1` FOREIGN KEY (`enseignant_id`) REFERENCES `utilisateurs` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `assignationsenseignants_ibfk_2` FOREIGN KEY (`cours_id`) REFERENCES `cours` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `assignationsenseignants_ibfk_3` FOREIGN KEY (`filiere_id`) REFERENCES `filieres` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `assignationsenseignants_ibfk_4` FOREIGN KEY (`assigne_par`) REFERENCES `utilisateurs` (`id`);

--
-- Contraintes pour la table `auditusage`
--
ALTER TABLE `auditusage`
  ADD CONSTRAINT `auditusage_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `utilisateurs` (`id`) ON DELETE SET NULL;

--
-- Contraintes pour la table `blocagesworkflow`
--
ALTER TABLE `blocagesworkflow`
  ADD CONSTRAINT `blocagesworkflow_ibfk_1` FOREIGN KEY (`acteur_bloquant_id`) REFERENCES `utilisateurs` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `blocagesworkflow_ibfk_2` FOREIGN KEY (`acteur_bloque_id`) REFERENCES `utilisateurs` (`id`) ON DELETE CASCADE;

--
-- Contraintes pour la table `bulletins`
--
ALTER TABLE `bulletins`
  ADD CONSTRAINT `bulletins_ibfk_1` FOREIGN KEY (`etudiant_id`) REFERENCES `etudiants` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `bulletins_ibfk_2` FOREIGN KEY (`genere_par`) REFERENCES `utilisateurs` (`id`) ON DELETE SET NULL;

--
-- Contraintes pour la table `bulletinscache`
--
ALTER TABLE `bulletinscache`
  ADD CONSTRAINT `bulletinscache_ibfk_1` FOREIGN KEY (`etudiant_id`) REFERENCES `utilisateurs` (`id`) ON DELETE CASCADE;

--
-- Contraintes pour la table `cours`
--
ALTER TABLE `cours`
  ADD CONSTRAINT `cours_ibfk_1` FOREIGN KEY (`filiere_id`) REFERENCES `filieres` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `cours_ibfk_2` FOREIGN KEY (`enseignant_id`) REFERENCES `enseignants` (`id`) ON DELETE SET NULL;

--
-- Contraintes pour la table `disponibilitesenseignants`
--
ALTER TABLE `disponibilitesenseignants`
  ADD CONSTRAINT `disponibilitesenseignants_ibfk_1` FOREIGN KEY (`enseignant_id`) REFERENCES `utilisateurs` (`id`) ON DELETE CASCADE;

--
-- Contraintes pour la table `emploidutemps`
--
ALTER TABLE `emploidutemps`
  ADD CONSTRAINT `emploidutemps_ibfk_1` FOREIGN KEY (`cours_id`) REFERENCES `cours` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `emploidutemps_ibfk_2` FOREIGN KEY (`enseignant_id`) REFERENCES `enseignants` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `emploidutemps_ibfk_3` FOREIGN KEY (`salle_id`) REFERENCES `salles` (`id`) ON DELETE CASCADE;

--
-- Contraintes pour la table `enseignants`
--
ALTER TABLE `enseignants`
  ADD CONSTRAINT `enseignants_ibfk_1` FOREIGN KEY (`utilisateur_id`) REFERENCES `utilisateurs` (`id`) ON DELETE CASCADE;

--
-- Contraintes pour la table `errorlogs`
--
ALTER TABLE `errorlogs`
  ADD CONSTRAINT `errorlogs_ibfk_1` FOREIGN KEY (`utilisateur_id`) REFERENCES `utilisateurs` (`id`) ON DELETE SET NULL;

--
-- Contraintes pour la table `etudiants`
--
ALTER TABLE `etudiants`
  ADD CONSTRAINT `etudiants_ibfk_1` FOREIGN KEY (`utilisateur_id`) REFERENCES `utilisateurs` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `etudiants_ibfk_2` FOREIGN KEY (`filiere_id`) REFERENCES `filieres` (`id`) ON DELETE RESTRICT;

--
-- Contraintes pour la table `importhistorique`
--
ALTER TABLE `importhistorique`
  ADD CONSTRAINT `importhistorique_ibfk_1` FOREIGN KEY (`importeur_id`) REFERENCES `utilisateurs` (`id`) ON DELETE CASCADE;

--
-- Contraintes pour la table `importnotes`
--
ALTER TABLE `importnotes`
  ADD CONSTRAINT `importnotes_ibfk_1` FOREIGN KEY (`cours_id`) REFERENCES `cours` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `importnotes_ibfk_2` FOREIGN KEY (`importe_par`) REFERENCES `utilisateurs` (`id`) ON DELETE RESTRICT;

--
-- Contraintes pour la table `messages`
--
ALTER TABLE `messages`
  ADD CONSTRAINT `messages_ibfk_1` FOREIGN KEY (`expediteur_id`) REFERENCES `utilisateurs` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `messages_ibfk_2` FOREIGN KEY (`destinataire_id`) REFERENCES `utilisateurs` (`id`) ON DELETE CASCADE;

--
-- Contraintes pour la table `notes`
--
ALTER TABLE `notes`
  ADD CONSTRAINT `fk_notes_validateur` FOREIGN KEY (`validateur_id`) REFERENCES `utilisateurs` (`id`) ON DELETE SET NULL,
  ADD CONSTRAINT `notes_ibfk_1` FOREIGN KEY (`etudiant_id`) REFERENCES `etudiants` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `notes_ibfk_2` FOREIGN KEY (`cours_id`) REFERENCES `cours` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `notes_ibfk_3` FOREIGN KEY (`saisi_par`) REFERENCES `utilisateurs` (`id`) ON DELETE RESTRICT,
  ADD CONSTRAINT `notes_ibfk_4` FOREIGN KEY (`valide_par`) REFERENCES `utilisateurs` (`id`) ON DELETE SET NULL;

--
-- Contraintes pour la table `notifications`
--
ALTER TABLE `notifications`
  ADD CONSTRAINT `notifications_ibfk_1` FOREIGN KEY (`destinataire_id`) REFERENCES `utilisateurs` (`id`) ON DELETE CASCADE;

--
-- Contraintes pour la table `notificationsworkflow`
--
ALTER TABLE `notificationsworkflow`
  ADD CONSTRAINT `notificationsworkflow_ibfk_1` FOREIGN KEY (`destinataire_id`) REFERENCES `utilisateurs` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `notificationsworkflow_ibfk_2` FOREIGN KEY (`expediteur_id`) REFERENCES `utilisateurs` (`id`) ON DELETE SET NULL;

--
-- Contraintes pour la table `parentsetudiants`
--
ALTER TABLE `parentsetudiants`
  ADD CONSTRAINT `parentsetudiants_ibfk_1` FOREIGN KEY (`parent_id`) REFERENCES `utilisateurs` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `parentsetudiants_ibfk_2` FOREIGN KEY (`etudiant_id`) REFERENCES `etudiants` (`id`) ON DELETE CASCADE;

--
-- Contraintes pour la table `presences`
--
ALTER TABLE `presences`
  ADD CONSTRAINT `presences_ibfk_1` FOREIGN KEY (`creneau_id`) REFERENCES `emploidutemps` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `presences_ibfk_2` FOREIGN KEY (`enseignant_id`) REFERENCES `enseignants` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `presences_ibfk_3` FOREIGN KEY (`marque_par`) REFERENCES `utilisateurs` (`id`) ON DELETE SET NULL;

--
-- Contraintes pour la table `promotions`
--
ALTER TABLE `promotions`
  ADD CONSTRAINT `promotions_ibfk_1` FOREIGN KEY (`etudiant_id`) REFERENCES `utilisateurs` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `promotions_ibfk_2` FOREIGN KEY (`validateur_id`) REFERENCES `utilisateurs` (`id`) ON DELETE SET NULL;

--
-- Contraintes pour la table `securitylogs`
--
ALTER TABLE `securitylogs`
  ADD CONSTRAINT `securitylogs_ibfk_1` FOREIGN KEY (`utilisateur_id`) REFERENCES `utilisateurs` (`id`) ON DELETE SET NULL;

--
-- Contraintes pour la table `signalements`
--
ALTER TABLE `signalements`
  ADD CONSTRAINT `signalements_ibfk_1` FOREIGN KEY (`etudiant_id`) REFERENCES `utilisateurs` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `signalements_ibfk_2` FOREIGN KEY (`note_id`) REFERENCES `notes` (`id`) ON DELETE SET NULL,
  ADD CONSTRAINT `signalements_ibfk_3` FOREIGN KEY (`cours_id`) REFERENCES `cours` (`id`) ON DELETE SET NULL,
  ADD CONSTRAINT `signalements_ibfk_4` FOREIGN KEY (`traite_par`) REFERENCES `utilisateurs` (`id`) ON DELETE SET NULL;

--
-- Contraintes pour la table `usageaudit`
--
ALTER TABLE `usageaudit`
  ADD CONSTRAINT `usageaudit_ibfk_1` FOREIGN KEY (`utilisateur_id`) REFERENCES `utilisateurs` (`id`) ON DELETE SET NULL;

--
-- Contraintes pour la table `utilisateurs`
--
ALTER TABLE `utilisateurs`
  ADD CONSTRAINT `utilisateurs_ibfk_1` FOREIGN KEY (`created_by_id`) REFERENCES `utilisateurs` (`id`) ON DELETE SET NULL;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
