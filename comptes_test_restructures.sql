-- Comptes de test restructurés pour UIST-2ITS
-- Mot de passe pour tous: password123
-- Hash: $2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzS0MYq7PS

-- Supprimer les anciens comptes de test si existants
DELETE FROM Utilisateurs WHERE matricule IN (
  'SA2025001', 'A2025001', 'DIR2025001', 'GPV2025001', 'GEX2025001', 
  'GEDT2025001', 'P2025001', 'E2025001', 'PAR2025001'
);

-- 1. SUPER ADMIN
INSERT INTO Utilisateurs (nom, prenom, matricule, email, password_hash, role, created_at) VALUES
('Super', 'Admin', 'SA2025001', 'superadmin@uist.edu', 
 '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzS0MYq7PS', 
 'SUPER_ADMIN', NOW());

-- 2. ADMIN
INSERT INTO Utilisateurs (nom, prenom, matricule, email, password_hash, role, created_at) VALUES
('Admin', 'Principal', 'A2025001', 'admin@uist.edu', 
 '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzS0MYq7PS', 
 'ADMIN', NOW());

-- 3. DIRECTEUR
INSERT INTO Utilisateurs (nom, prenom, matricule, email, password_hash, role, created_at) VALUES
('Directeur', 'Académique', 'DIR2025001', 'directeur@uist.edu', 
 '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzS0MYq7PS', 
 'DIRECTEUR', NOW());

-- 4. GESTIONNAIRE PV
INSERT INTO Utilisateurs (nom, prenom, matricule, email, password_hash, role, created_at) VALUES
('Gestionnaire', 'PV', 'GPV2025001', 'gpv@uist.edu', 
 '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzS0MYq7PS', 
 'GESTIONNAIRE_PV', NOW());

-- 5. GESTIONNAIRE EXAMENS
INSERT INTO Utilisateurs (nom, prenom, matricule, email, password_hash, role, created_at) VALUES
('Gestionnaire', 'Examens', 'GEX2025001', 'gexamens@uist.edu', 
 '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzS0MYq7PS', 
 'GESTIONNAIRE_EXAMENS', NOW());

-- 6. GESTIONNAIRE EDT
INSERT INTO Utilisateurs (nom, prenom, matricule, email, password_hash, role, created_at) VALUES
('Gestionnaire', 'EDT', 'GEDT2025001', 'gedt@uist.edu', 
 '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzS0MYq7PS', 
 'GESTIONNAIRE_EDT', NOW());

-- 7. ENSEIGNANT
INSERT INTO Utilisateurs (nom, prenom, matricule, email, password_hash, role, created_at) VALUES
('Professeur', 'Test', 'P2025001', 'enseignant@uist.edu', 
 '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzS0MYq7PS', 
 'ENSEIGNANT', NOW());

-- Créer profil enseignant
INSERT INTO Enseignants (utilisateur_id, specialite) 
SELECT id, 'Informatique' FROM Utilisateurs WHERE matricule = 'P2025001';

-- 8. ÉTUDIANT
INSERT INTO Utilisateurs (nom, prenom, matricule, email, password_hash, role, created_at) VALUES
('Étudiant', 'Test', 'E2025001', 'etudiant@uist.edu', 
 '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzS0MYq7PS', 
 'ETUDIANT', NOW());

-- Créer profil étudiant (filière 1 si existe)
INSERT INTO Etudiants (utilisateur_id, filiere_id) 
SELECT u.id, 1 FROM Utilisateurs u WHERE u.matricule = 'E2025001' AND EXISTS (SELECT 1 FROM Filieres WHERE id = 1);

-- 9. PARENT
INSERT INTO Utilisateurs (nom, prenom, matricule, email, password_hash, role, created_at) VALUES
('Parent', 'Test', 'PAR2025001', 'parent@uist.edu', 
 '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzS0MYq7PS', 
 'PARENT', NOW());

-- Afficher les comptes créés
SELECT 
    matricule as 'Matricule',
    CONCAT(nom, ' ', prenom) as 'Nom Complet',
    email as 'Email',
    role as 'Rôle',
    'password123' as 'Mot de passe'
FROM Utilisateurs 
WHERE matricule IN ('SA2025001', 'A2025001', 'DIR2025001', 'GPV2025001', 'GEX2025001', 'GEDT2025001', 'P2025001', 'E2025001', 'PAR2025001')
ORDER BY 
    CASE role
        WHEN 'SUPER_ADMIN' THEN 1
        WHEN 'ADMIN' THEN 2
        WHEN 'DIRECTEUR' THEN 3
        WHEN 'GESTIONNAIRE_PV' THEN 4
        WHEN 'GESTIONNAIRE_EXAMENS' THEN 5
        WHEN 'GESTIONNAIRE_EDT' THEN 6
        WHEN 'ENSEIGNANT' THEN 7
        WHEN 'ETUDIANT' THEN 8
        WHEN 'PARENT' THEN 9
    END;