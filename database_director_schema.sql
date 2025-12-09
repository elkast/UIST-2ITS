-- Schema pour les fonctionnalités Directeur
-- À exécuter sur la base de données UIST_2ITS

-- Table pour les assignations enseignant-cours-filière
CREATE TABLE IF NOT EXISTS AssignationsEnseignants (
    id INT AUTO_INCREMENT PRIMARY KEY,
    enseignant_id INT NOT NULL,
    cours_id INT NOT NULL,
    filiere_id INT NOT NULL,
    niveau VARCHAR(10) NOT NULL,
    annee_academique VARCHAR(20) NOT NULL,
    assigne_par INT NOT NULL,
    date_assignation DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (enseignant_id) REFERENCES Utilisateurs(id) ON DELETE CASCADE,
    FOREIGN KEY (cours_id) REFERENCES Cours(id) ON DELETE CASCADE,
    FOREIGN KEY (filiere_id) REFERENCES Filieres(id) ON DELETE CASCADE,
    FOREIGN KEY (assigne_par) REFERENCES Utilisateurs(id),
    INDEX idx_enseignant (enseignant_id),
    INDEX idx_cours (cours_id),
    INDEX idx_filiere_niveau (filiere_id, niveau),
    INDEX idx_annee (annee_academique)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table pour les disponibilités des enseignants
CREATE TABLE IF NOT EXISTS DisponibilitesEnseignants (
    id INT AUTO_INCREMENT PRIMARY KEY,
    enseignant_id INT NOT NULL,
    date_debut DATE NOT NULL,
    date_fin DATE NOT NULL,
    type_indisponibilite ENUM('ABSENCE', 'RETARD', 'DISPONIBLE', 'CHANGEMENT_HORAIRE') NOT NULL,
    motif TEXT,
    visible_etudiants BOOLEAN DEFAULT TRUE,
    date_creation DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (enseignant_id) REFERENCES Utilisateurs(id) ON DELETE CASCADE,
    INDEX idx_enseignant (enseignant_id),
    INDEX idx_dates (date_debut, date_fin),
    INDEX idx_visible (visible_etudiants)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Ajout de colonnes manquantes dans la table Notes (vérifier d'abord si elles existent)
-- Exécuter ces commandes une par une
ALTER TABLE Notes ADD COLUMN commentaire_validation TEXT;
ALTER TABLE Notes ADD COLUMN date_validation DATETIME;

-- Index pour améliorer les performances
-- Créer seulement s'ils n'existent pas déjà
CREATE INDEX idx_notes_statut ON Notes(statut);
CREATE INDEX idx_notes_validation ON Notes(valide_par, date_validation);
CREATE INDEX idx_notes_filiere ON Notes(cours_id);

-- Vues pour faciliter les requêtes du directeur

-- Vue: Notes avec détails complets
CREATE OR REPLACE VIEW v_notes_details AS
SELECT 
    n.*,
    u_etud.matricule as etudiant_matricule,
    u_etud.nom as etudiant_nom,
    u_etud.prenom as etudiant_prenom,
    c.nom_cours,
    c.type_cours,
    f.id as filiere_id,
    f.nom_filiere,
    f.niveau,
    u_saisi.nom as saisi_par_nom,
    u_saisi.prenom as saisi_par_prenom,
    u_valid.nom as valide_par_nom,
    u_valid.prenom as valide_par_prenom
FROM Notes n
JOIN Etudiants e ON n.etudiant_id = e.utilisateur_id
JOIN Utilisateurs u_etud ON e.utilisateur_id = u_etud.id
JOIN Cours c ON n.cours_id = c.id
JOIN Filieres f ON c.filiere_id = f.id
JOIN Utilisateurs u_saisi ON n.saisi_par = u_saisi.id
LEFT JOIN Utilisateurs u_valid ON n.valide_par = u_valid.id;

-- Vue: Emplois du temps avec détails complets
CREATE OR REPLACE VIEW v_emploi_temps_complet AS
SELECT 
    edt.*,
    c.nom_cours,
    c.type_cours,
    f.id as filiere_id,
    f.nom_filiere,
    f.niveau,
    u.nom as enseignant_nom,
    u.prenom as enseignant_prenom,
    u.matricule as enseignant_matricule,
    s.nom_salle,
    s.capacite
FROM EmploiDuTemps edt
JOIN Cours c ON edt.cours_id = c.id
JOIN Filieres f ON c.filiere_id = f.id
JOIN Enseignants ens ON edt.enseignant_id = ens.utilisateur_id
JOIN Utilisateurs u ON ens.utilisateur_id = u.id
JOIN Salles s ON edt.salle_id = s.id;

-- Vue: Statistiques par filière
CREATE OR REPLACE VIEW v_stats_filieres AS
SELECT 
    f.id as filiere_id,
    f.nom_filiere,
    f.niveau,
    COUNT(DISTINCT e.utilisateur_id) as nb_etudiants,
    COUNT(DISTINCT c.id) as nb_cours,
    COUNT(DISTINCT edt.enseignant_id) as nb_enseignants,
    COUNT(DISTINCT n.id) as nb_notes_total,
    SUM(CASE WHEN n.statut = 'VALIDÉ' THEN 1 ELSE 0 END) as nb_notes_validees,
    SUM(CASE WHEN n.statut = 'EN_ATTENTE_DIRECTEUR' THEN 1 ELSE 0 END) as nb_notes_en_attente,
    ROUND(AVG(CASE WHEN n.statut = 'VALIDÉ' THEN n.note END), 2) as moyenne_generale
FROM Filieres f
LEFT JOIN Etudiants e ON f.id = e.filiere_id
LEFT JOIN Cours c ON f.id = c.filiere_id
LEFT JOIN EmploiDuTemps edt ON c.id = edt.cours_id
LEFT JOIN Notes n ON c.id = n.cours_id
GROUP BY f.id, f.nom_filiere, f.niveau;