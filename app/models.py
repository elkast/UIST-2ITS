"""
Modèles de données pour l'application UIST-Planify
Classes Python représentant les tables de la base de données
"""
from app.db import executer_requete, executer_requete_unique
from werkzeug.security import generate_password_hash

class Utilisateur:
    """Modèle pour la table Utilisateurs"""
    
    @staticmethod
    def creer(nom, prenom, matricule, role):
        """
        Crée un nouvel utilisateur
        
        Args:
            nom (str): Nom de famille
            prenom (str): Prénom
            matricule (str): Matricule (unique)
            role (str): Role (etudiant, enseignant, administration, sous_admin)
        
        Returns:
            int: ID de l'utilisateur créé
        """
        requete = """
            INSERT INTO Utilisateurs (nom, prenom, matricule, role)
            VALUES (%s, %s, %s, %s)
        """
        return executer_requete(requete, (nom, prenom, matricule, role))
    
    @staticmethod
    def obtenir_par_matricule(matricule):
        """
        Récupère un utilisateur par son matricule
        
        Args:
            matricule (str): Matricule de l'utilisateur
        
        Returns:
            dict: Données de l'utilisateur ou None
        """
        requete = "SELECT * FROM Utilisateurs WHERE matricule = %s"
        return executer_requete_unique(requete, (matricule,))
    
    @staticmethod
    def obtenir_par_id(utilisateur_id):
        """
        Récupère un utilisateur par son ID
        
        Args:
            utilisateur_id (int): ID de l'utilisateur
        
        Returns:
            dict: Données de l'utilisateur ou None
        """
        requete = "SELECT * FROM Utilisateurs WHERE id = %s"
        return executer_requete_unique(requete, (utilisateur_id,))
    
    @staticmethod
    def obtenir_tous():
        """
        Récupère tous les utilisateurs
        
        Returns:
            list: Liste de tous les utilisateurs
        """
        requete = "SELECT * FROM Utilisateurs ORDER BY nom, prenom"
        return executer_requete(requete, obtenir_resultats=True)
    
    @staticmethod
    def modifier(utilisateur_id, nom, prenom, matricule, role):
        """
        Modifie un utilisateur
        
        Args:
            utilisateur_id (int): ID de l'utilisateur
            nom (str): Nouveau nom
            prenom (str): Nouveau prénom
            matricule (str): Nouveau matricule
            role (str): Nouveau rôle
        
        Returns:
            int: Nombre de lignes affectées
        """
        requete = """
            UPDATE Utilisateurs 
            SET nom = %s, prenom = %s, matricule = %s, role = %s
            WHERE id = %s
        """
        return executer_requete(requete, (nom, prenom, matricule, role, utilisateur_id))
    
    @staticmethod
    def supprimer(utilisateur_id):
        """
        Supprime un utilisateur
        
        Args:
            utilisateur_id (int): ID de l'utilisateur
        
        Returns:
            int: Nombre de lignes affectées
        """
        requete = "DELETE FROM Utilisateurs WHERE id = %s"
        return executer_requete(requete, (utilisateur_id,))
    
    @staticmethod
    def filtrer(role=None, filiere_id=None, recherche=None):
        """
        Filtre les utilisateurs selon différents critères
        
        Args:
            role (str): Filtrer par rôle
            filiere_id (int): Filtrer par filière (pour étudiants)
            recherche (str): Recherche par nom, prénom ou matricule
        
        Returns:
            list: Liste des utilisateurs filtrés
        """
        requete = """
            SELECT u.*, 
                   CASE 
                       WHEN u.role IN ('etudiant', 'ETUDIANT') THEN e.filiere_id
                       ELSE NULL
                   END as filiere_id,
                   CASE 
                       WHEN u.role IN ('etudiant', 'ETUDIANT') THEN f.nom_filiere
                       ELSE NULL
                   END as nom_filiere,
                   CASE 
                       WHEN u.role IN ('enseignant', 'ENSEIGNANT') THEN ens.specialite
                       ELSE NULL
                   END as specialite
            FROM Utilisateurs u
            LEFT JOIN Etudiants e ON u.id = e.utilisateur_id AND u.role IN ('etudiant', 'ETUDIANT')
            LEFT JOIN Filieres f ON e.filiere_id = f.id
            LEFT JOIN Enseignants ens ON u.id = ens.utilisateur_id AND u.role IN ('enseignant', 'ENSEIGNANT')
            WHERE 1=1
        """
        params = []
        
        if role:
            requete += " AND u.role = %s"
            params.append(role)
        
        if filiere_id:
            requete += " AND e.filiere_id = %s"
            params.append(filiere_id)
        
        if recherche:
            requete += " AND (u.nom LIKE %s OR u.prenom LIKE %s OR u.matricule LIKE %s)"
            search_term = f"%{recherche}%"
            params.extend([search_term, search_term, search_term])
        
        requete += " ORDER BY u.nom, u.prenom"
        
        return executer_requete(requete, tuple(params) if params else None, obtenir_resultats=True)

    @staticmethod
    def creer_complet(email, password_hash, role, nom, prenom, matricule=None, created_by_id=None, filiere_id=None, specialite=None):
        """
        Crée un utilisateur complet avec tous les champs
        
        Args:
            email (str): Email de l'utilisateur
            password_hash (str): Hash du mot de passe
            role (str): Rôle de l'utilisateur
            nom (str): Nom de famille
            prenom (str): Prénom
            matricule (str, optional): Matricule (généré si None)
            created_by_id (int, optional): ID du créateur
            filiere_id (int, optional): ID de la filière pour étudiants
            specialite (str, optional): Spécialité pour enseignants
        
        Returns:
            int: ID de l'utilisateur créé
        """
        from app.utils import generer_matricule
        if matricule is None:
            matricule = generer_matricule(role)
        
        requete = """
            INSERT INTO Utilisateurs (email, password_hash, nom, prenom, matricule, role, created_by_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        params = (email, password_hash, nom, prenom, matricule, role, created_by_id)
        user_id = executer_requete(requete, params)
        
        if user_id:
            # Créer profils spécifiques
            if role in ['ENSEIGNANT', 'enseignant']:
                from app.models import Enseignant
                Enseignant.creer(user_id, specialite or '')
            elif role in ['ETUDIANT', 'etudiant']:
                from app.models import Etudiant
                if filiere_id:
                    Etudiant.creer(user_id, filiere_id)
                else:
                    # Supprimer si pas de filière
                    Utilisateur.supprimer(user_id)
                    return None
        
        return user_id

    @staticmethod
    def mettre_a_jour_last_login(user_id):
        """
        Met à jour la dernière connexion de l'utilisateur
        
        Args:
            user_id (int): ID de l'utilisateur
        
        Returns:
            int: Nombre de lignes affectées
        """
        requete = "UPDATE Utilisateurs SET last_login = NOW() WHERE id = %s"
        return executer_requete(requete, (user_id,))

    @staticmethod
    def compter_par_role():
        """
        Compte le nombre d'utilisateurs par rôle
        
        Returns:
            list: Liste de dicts {role: str, count: int}
        """
        requete = "SELECT role, COUNT(*) as count FROM Utilisateurs GROUP BY role"
        return executer_requete(requete, obtenir_resultats=True)

    @staticmethod
    def obtenir_par_role(role):
        """
        Récupère les utilisateurs par rôle

        Args:
            role (str): Rôle des utilisateurs à récupérer

        Returns:
            list: Liste des utilisateurs avec ce rôle
        """
        requete = "SELECT * FROM Utilisateurs WHERE role = %s ORDER BY nom, prenom"
        return executer_requete(requete, (role,), obtenir_resultats=True)

    @staticmethod
    def lister_avec_last_login():
        """
        Liste tous les utilisateurs avec leur dernière connexion effective
        
        Returns:
            list: Liste des utilisateurs avec effective_last_login
        """
        requete = """
            SELECT u.*, 
                   COALESCE(u.last_login, 
                           (SELECT MAX(created_at) 
                            FROM UsageAudit 
                            WHERE user_id = u.id AND action = 'LOGIN')) as effective_last_login
            FROM Utilisateurs u 
            ORDER BY u.nom, u.prenom
        """
        return executer_requete(requete, obtenir_resultats=True)

    @staticmethod
    def creer(nom, prenom, matricule, role):
        """
        Crée un nouvel utilisateur (version legacy pour compatibilité)
        
        Args:
            nom (str): Nom de famille
            prenom (str): Prénom
            matricule (str): Matricule (unique)
            role (str): Role (etudiant, enseignant, administration, sous_admin)
        
        Returns:
            int: ID de l'utilisateur créé
        """
        requete = """
            INSERT INTO Utilisateurs (nom, prenom, matricule, role)
            VALUES (%s, %s, %s, %s)
        """
        return executer_requete(requete, (nom, prenom, matricule, role))

    @staticmethod
    def modifier(utilisateur_id, nom, prenom, matricule, role):
        """
        Modifie un utilisateur (version legacy pour compatibilité)
        
        Args:
            utilisateur_id (int): ID de l'utilisateur
            nom (str): Nouveau nom
            prenom (str): Nouveau prénom
            matricule (str): Nouveau matricule
            role (str): Nouveau rôle
        
        Returns:
            int: Nombre de lignes affectées
        """
        requete = """
            UPDATE Utilisateurs 
            SET nom = %s, prenom = %s, matricule = %s, role = %s
            WHERE id = %s
        """
        return executer_requete(requete, (nom, prenom, matricule, role, utilisateur_id))


class Enseignant:
    """Modèle pour la table Enseignants"""

    @staticmethod
    def creer(utilisateur_id, specialite):
        """
        Crée un profil enseignant

        Args:
            utilisateur_id (int): ID de l'utilisateur
            specialite (str): Spécialité de l'enseignant

        Returns:
            int: Nombre de lignes affectées
        """
        requete = "INSERT INTO Enseignants (utilisateur_id, specialite) VALUES (%s, %s)"
        return executer_requete(requete, (utilisateur_id, specialite))

    @staticmethod
    def obtenir_tous():
        """
        Récupère tous les enseignants avec leurs informations utilisateur

        Returns:
            list: Liste de tous les enseignants
        """
        requete = """
            SELECT u.*, e.specialite, e.total_heures_prevues, e.total_heures_effectuees
            FROM Enseignants e
            JOIN Utilisateurs u ON e.utilisateur_id = u.id
            ORDER BY u.nom, u.prenom
        """
        return executer_requete(requete, obtenir_resultats=True)

    @staticmethod
    def obtenir_par_id(utilisateur_id):
        """
        Récupère un enseignant par son ID utilisateur

        Args:
            utilisateur_id (int): ID de l'utilisateur

        Returns:
            dict: Données de l'enseignant ou None
        """
        requete = """
            SELECT u.*, e.specialite, e.total_heures_prevues, e.total_heures_effectuees
            FROM Enseignants e
            JOIN Utilisateurs u ON e.utilisateur_id = u.id
            WHERE e.utilisateur_id = %s
        """
        return executer_requete_unique(requete, (utilisateur_id,))

    @staticmethod
    def modifier(utilisateur_id, specialite):
        """
        Modifie les informations d'un enseignant

        Args:
            utilisateur_id (int): ID de l'utilisateur
            specialite (str): Nouvelle spécialité

        Returns:
            int: Nombre de lignes affectées
        """
        requete = "UPDATE Enseignants SET specialite = %s WHERE utilisateur_id = %s"
        return executer_requete(requete, (specialite, utilisateur_id))
    
    @staticmethod
    def mettre_a_jour_heures(utilisateur_id):
        """
        Met à jour les heures prévues et effectuées pour un enseignant
        
        Args:
            utilisateur_id (int): ID de l'enseignant
        
        Returns:
            int: Nombre de lignes affectées
        """
        # Calculer heures prévues
        requete_prevues = """
            UPDATE Enseignants 
            SET total_heures_prevues = (
                SELECT COALESCE(SUM(TIME_TO_SEC(TIMEDIFF(edt.heure_fin, edt.heure_debut)) / 3600), 0)
                FROM EmploiDuTemps edt
                WHERE edt.enseignant_id = %s
            )
            WHERE utilisateur_id = %s
        """
        executer_requete(requete_prevues, (utilisateur_id, utilisateur_id))
        
        # Calculer heures effectuées
        requete_effectuees = """
            UPDATE Enseignants 
            SET total_heures_effectuees = (
                SELECT COALESCE(SUM(TIME_TO_SEC(TIMEDIFF(edt.heure_fin, edt.heure_debut)) / 3600), 0)
                FROM EmploiDuTemps edt
                INNER JOIN Presences p ON p.creneau_id = edt.id
                WHERE edt.enseignant_id = %s AND p.statut = 'present'
            )
            WHERE utilisateur_id = %s
        """
        return executer_requete(requete_effectuees, (utilisateur_id, utilisateur_id))


class Etudiant:
    """Modèle pour la table Etudiants"""
    
    @staticmethod
    def creer(utilisateur_id, filiere_id):
        """
        Crée un profil étudiant
        
        Args:
            utilisateur_id (int): ID de l'utilisateur
            filiere_id (int): ID de la filière
        
        Returns:
            int: Nombre de lignes affectées
        """
        requete = "INSERT INTO Etudiants (utilisateur_id, filiere_id) VALUES (%s, %s)"
        return executer_requete(requete, (utilisateur_id, filiere_id))
    
    @staticmethod
    def obtenir_tous():
        """
        Récupère tous les étudiants avec leurs informations
        
        Returns:
            list: Liste de tous les étudiants
        """
        requete = """
            SELECT u.*, e.filiere_id, f.nom_filiere, f.niveau
            FROM Etudiants e
            JOIN Utilisateurs u ON e.utilisateur_id = u.id
            JOIN Filieres f ON e.filiere_id = f.id
            ORDER BY u.nom, u.prenom
        """
        return executer_requete(requete, obtenir_resultats=True)
    
    @staticmethod
    def obtenir_par_id(utilisateur_id):
        """
        Récupère un étudiant par son ID utilisateur

        Args:
            utilisateur_id (int): ID de l'utilisateur

        Returns:
            dict: Données de l'étudiant ou None
        """
        requete = """
            SELECT u.*, e.filiere_id, f.nom_filiere, f.niveau
            FROM Etudiants e
            JOIN Utilisateurs u ON e.utilisateur_id = u.id
            JOIN Filieres f ON e.filiere_id = f.id
            WHERE e.utilisateur_id = %s
        """
        return executer_requete_unique(requete, (utilisateur_id,))
    
    @staticmethod
    def modifier(utilisateur_id, filiere_id):
        """
        Modifie la filière d'un étudiant
        
        Args:
            utilisateur_id (int): ID de l'utilisateur
            filiere_id (int): Nouvelle filière
        
        Returns:
            int: Nombre de lignes affectées
        """
        requete = "UPDATE Etudiants SET filiere_id = %s WHERE utilisateur_id = %s"
        return executer_requete(requete, (filiere_id, utilisateur_id))


class Filiere:
    """Modèle pour la table Filieres"""
    
    @staticmethod
    def creer(nom_filiere, niveau, nombre_etudiants=0):
        """
        Crée une nouvelle filière
        
        Args:
            nom_filiere (str): Nom de la filière
            niveau (str): Niveau (L1, L2, L3, M1, M2)
            nombre_etudiants (int): Nombre d'étudiants
        
        Returns:
            int: ID de la filière créée
        """
        requete = "INSERT INTO Filieres (nom_filiere, niveau, nombre_etudiants) VALUES (%s, %s, %s)"
        return executer_requete(requete, (nom_filiere, niveau, nombre_etudiants))
    
    @staticmethod
    def obtenir_toutes():
        """
        Récupère toutes les filières
        
        Returns:
            list: Liste de toutes les filières
        """
        requete = "SELECT * FROM Filieres ORDER BY niveau, nom_filiere"
        return executer_requete(requete, obtenir_resultats=True)
    
    @staticmethod
    def obtenir_par_id(filiere_id):
        """
        Récupère une filière par son ID
        
        Args:
            filiere_id (int): ID de la filière
        
        Returns:
            dict: Données de la filière ou None
        """
        requete = "SELECT * FROM Filieres WHERE id = %s"
        return executer_requete_unique(requete, (filiere_id,))
    
    @staticmethod
    def modifier(filiere_id, nom_filiere, niveau, nombre_etudiants):
        """
        Modifie une filière
        
        Args:
            filiere_id (int): ID de la filière
            nom_filiere (str): Nouveau nom
            niveau (str): Nouveau niveau
            nombre_etudiants (int): Nouveau nombre d'étudiants
        
        Returns:
            int: Nombre de lignes affectées
        """
        requete = """
            UPDATE Filieres 
            SET nom_filiere = %s, niveau = %s, nombre_etudiants = %s 
            WHERE id = %s
        """
        return executer_requete(requete, (nom_filiere, niveau, nombre_etudiants, filiere_id))
    
    @staticmethod
    def supprimer(filiere_id):
        """
        Supprime une filière
        
        Args:
            filiere_id (int): ID de la filière
        
        Returns:
            int: Nombre de lignes affectées
        """
        requete = "DELETE FROM Filieres WHERE id = %s"
        return executer_requete(requete, (filiere_id,))


class Salle:
    """Modèle pour la table Salles"""
    
    @staticmethod
    def creer(nom_salle, capacite, equipements=''):
        """
        Crée une nouvelle salle
        
        Args:
            nom_salle (str): Nom de la salle
            capacite (int): Capacité de la salle
            equipements (str): Liste des équipements
        
        Returns:
            int: ID de la salle créée
        """
        requete = "INSERT INTO Salles (nom_salle, capacite, equipements) VALUES (%s, %s, %s)"
        return executer_requete(requete, (nom_salle, capacite, equipements))
    
    @staticmethod
    def obtenir_toutes():
        """
        Récupère toutes les salles
        
        Returns:
            list: Liste de toutes les salles
        """
        requete = "SELECT * FROM Salles ORDER BY nom_salle"
        return executer_requete(requete, obtenir_resultats=True)
    
    @staticmethod
    def obtenir_par_id(salle_id):
        """
        Récupère une salle par son ID
        
        Args:
            salle_id (int): ID de la salle
        
        Returns:
            dict: Données de la salle ou None
        """
        requete = "SELECT * FROM Salles WHERE id = %s"
        return executer_requete_unique(requete, (salle_id,))
    
    @staticmethod
    def modifier(salle_id, nom_salle, capacite, equipements):
        """
        Modifie une salle
        
        Args:
            salle_id (int): ID de la salle
            nom_salle (str): Nouveau nom
            capacite (int): Nouvelle capacité
            equipements (str): Nouveaux équipements
        
        Returns:
            int: Nombre de lignes affectées
        """
        requete = """
            UPDATE Salles 
            SET nom_salle = %s, capacite = %s, equipements = %s 
            WHERE id = %s
        """
        return executer_requete(requete, (nom_salle, capacite, equipements, salle_id))
    
    @staticmethod
    def supprimer(salle_id):
        """
        Supprime une salle
        
        Args:
            salle_id (int): ID de la salle
        
        Returns:
            int: Nombre de lignes affectées
        """
        requete = "DELETE FROM Salles WHERE id = %s"
        return executer_requete(requete, (salle_id,))


class Cours:
    """Modèle pour la table Cours"""
    
    @staticmethod
    def creer(nom_cours, filiere_id, type_cours):
        """
        Crée un nouveau cours
        
        Args:
            nom_cours (str): Nom du cours
            filiere_id (int): ID de la filière
            type_cours (str): Type (CM, TD, TP)
        
        Returns:
            int: ID du cours créé
        """
        requete = "INSERT INTO Cours (nom_cours, filiere_id, type_cours) VALUES (%s, %s, %s)"
        return executer_requete(requete, (nom_cours, filiere_id, type_cours))
    
    @staticmethod
    def obtenir_tous():
        """
        Récupère tous les cours avec leurs informations de filière
        
        Returns:
            list: Liste de tous les cours
        """
        requete = """
            SELECT c.*, f.nom_filiere, f.niveau
            FROM Cours c
            JOIN Filieres f ON c.filiere_id = f.id
            ORDER BY f.niveau, f.nom_filiere, c.nom_cours
        """
        return executer_requete(requete, obtenir_resultats=True)
    
    @staticmethod
    def obtenir_par_id(cours_id):
        """
        Récupère un cours par son ID
        
        Args:
            cours_id (int): ID du cours
        
        Returns:
            dict: Données du cours ou None
        """
        requete = """
            SELECT c.*, f.nom_filiere, f.niveau
            FROM Cours c
            JOIN Filieres f ON c.filiere_id = f.id
            WHERE c.id = %s
        """
        return executer_requete_unique(requete, (cours_id,))
    
    @staticmethod
    def obtenir_par_filiere(filiere_id):
        """
        Récupère tous les cours d'une filière
        
        Args:
            filiere_id (int): ID de la filière
        
        Returns:
            list: Liste des cours de la filière
        """
        requete = "SELECT * FROM Cours WHERE filiere_id = %s ORDER BY nom_cours"
        return executer_requete(requete, (filiere_id,), obtenir_resultats=True)
    
    @staticmethod
    def modifier(cours_id, nom_cours, filiere_id, type_cours):
        """
        Modifie un cours
        
        Args:
            cours_id (int): ID du cours
            nom_cours (str): Nouveau nom
            filiere_id (int): Nouvelle filière
            type_cours (str): Nouveau type
        
        Returns:
            int: Nombre de lignes affectées
        """
        requete = """
            UPDATE Cours 
            SET nom_cours = %s, filiere_id = %s, type_cours = %s 
            WHERE id = %s
        """
        return executer_requete(requete, (nom_cours, filiere_id, type_cours, cours_id))
    
    @staticmethod
    def supprimer(cours_id):
        """
        Supprime un cours
        
        Args:
            cours_id (int): ID du cours
        
        Returns:
            int: Nombre de lignes affectées
        """
        requete = "DELETE FROM Cours WHERE id = %s"
        return executer_requete(requete, (cours_id,))


class EmploiDuTemps:
    """Modèle pour la table EmploiDuTemps"""
    
    @staticmethod
    def creer(cours_id, enseignant_id, salle_id, jour, heure_debut, heure_fin):
        """
        Crée un nouveau créneau dans l'emploi du temps
        
        Args:
            cours_id (int): ID du cours
            enseignant_id (int): ID de l'enseignant
            salle_id (int): ID de la salle
            jour (str): Jour de la semaine
            heure_debut (str): Heure de début (format HH:MM)
            heure_fin (str): Heure de fin (format HH:MM)
        
        Returns:
            int: ID du créneau créé ou 0 en cas d'erreur
        """
        requete = """
            INSERT INTO EmploiDuTemps 
            (cours_id, enseignant_id, salle_id, jour, heure_debut, heure_fin)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        return executer_requete(requete, (cours_id, enseignant_id, salle_id, jour, heure_debut, heure_fin))
    
    @staticmethod
    def verifier_conflit(enseignant_id, salle_id, jour, heure_debut, heure_fin, cours_id, creneau_id=None):
        """
        Vérifie s'il y a un conflit de planning (RG01)
        
        Args:
            enseignant_id (int): ID de l'enseignant
            salle_id (int): ID de la salle
            jour (str): Jour de la semaine
            heure_debut (str): Heure de début
            heure_fin (str): Heure de fin
            cours_id (int): ID du cours
            creneau_id (int): ID du créneau à exclure (pour modification)
        
        Returns:
            dict: Informations sur le conflit ou None si pas de conflit
        """
        # Vérifier conflit enseignant
        requete_enseignant = """
            SELECT * FROM EmploiDuTemps
            WHERE enseignant_id = %s 
            AND jour = %s
            AND (
                (heure_debut < %s AND heure_fin > %s) OR
                (heure_debut < %s AND heure_fin > %s) OR
                (heure_debut >= %s AND heure_fin <= %s)
            )
        """
        params_enseignant = (enseignant_id, jour, heure_fin, heure_debut, heure_fin, heure_fin, heure_debut, heure_fin)
        
        if creneau_id:
            requete_enseignant += " AND id != %s"
            params_enseignant = params_enseignant + (creneau_id,)
        
        conflit_enseignant = executer_requete_unique(requete_enseignant, params_enseignant)
        if conflit_enseignant:
            return {'type': 'enseignant', 'details': conflit_enseignant}
        
        # Vérifier conflit salle
        requete_salle = """
            SELECT * FROM EmploiDuTemps
            WHERE salle_id = %s 
            AND jour = %s
            AND (
                (heure_debut < %s AND heure_fin > %s) OR
                (heure_debut < %s AND heure_fin > %s) OR
                (heure_debut >= %s AND heure_fin <= %s)
            )
        """
        params_salle = (salle_id, jour, heure_fin, heure_debut, heure_fin, heure_fin, heure_debut, heure_fin)
        
        if creneau_id:
            requete_salle += " AND id != %s"
            params_salle = params_salle + (creneau_id,)
        
        conflit_salle = executer_requete_unique(requete_salle, params_salle)
        if conflit_salle:
            return {'type': 'salle', 'details': conflit_salle}
        
        # Vérifier conflit filière (via cours)
        requete_filiere = """
            SELECT edt.* FROM EmploiDuTemps edt
            JOIN Cours c1 ON edt.cours_id = c1.id
            JOIN Cours c2 ON c2.id = %s
            WHERE c1.filiere_id = c2.filiere_id
            AND edt.jour = %s
            AND (
                (edt.heure_debut < %s AND edt.heure_fin > %s) OR
                (edt.heure_debut < %s AND edt.heure_fin > %s) OR
                (edt.heure_debut >= %s AND edt.heure_fin <= %s)
            )
        """
        params_filiere = (cours_id, jour, heure_fin, heure_debut, heure_fin, heure_fin, heure_debut, heure_fin)
        
        if creneau_id:
            requete_filiere += " AND edt.id != %s"
            params_filiere = params_filiere + (creneau_id,)
        
        conflit_filiere = executer_requete_unique(requete_filiere, params_filiere)
        if conflit_filiere:
            return {'type': 'filiere', 'details': conflit_filiere}
        
        return None
    
    @staticmethod
    def obtenir_tous():
        """
        Récupère tous les créneaux avec toutes les informations
        
        Returns:
            list: Liste de tous les créneaux
        """
        requete = """
            SELECT 
                edt.*,
                c.nom_cours, c.type_cours,
                u.nom as enseignant_nom, u.prenom as enseignant_prenom,
                s.nom_salle,
                f.nom_filiere, f.niveau
            FROM EmploiDuTemps edt
            JOIN Cours c ON edt.cours_id = c.id
            JOIN Enseignants e ON edt.enseignant_id = e.utilisateur_id
            JOIN Utilisateurs u ON e.utilisateur_id = u.id
            JOIN Salles s ON edt.salle_id = s.id
            JOIN Filieres f ON c.filiere_id = f.id
            ORDER BY 
                FIELD(edt.jour, 'Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi'),
                edt.heure_debut
        """
        return executer_requete(requete, obtenir_resultats=True)
    
    @staticmethod
    def obtenir_par_enseignant(enseignant_id):
        """
        Récupère l'emploi du temps d'un enseignant
        
        Args:
            enseignant_id (int): ID de l'enseignant
        
        Returns:
            list: Liste des créneaux de l'enseignant
        """
        requete = """
            SELECT 
                edt.*,
                c.nom_cours, c.type_cours,
                s.nom_salle,
                f.nom_filiere, f.niveau
            FROM EmploiDuTemps edt
            JOIN Cours c ON edt.cours_id = c.id
            JOIN Salles s ON edt.salle_id = s.id
            JOIN Filieres f ON c.filiere_id = f.id
            WHERE edt.enseignant_id = %s
            ORDER BY 
                FIELD(edt.jour, 'Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi'),
                edt.heure_debut
        """
        return executer_requete(requete, (enseignant_id,), obtenir_resultats=True)
    
    @staticmethod
    def obtenir_par_filiere(filiere_id):
        """
        Récupère l'emploi du temps d'une filière

        Args:
            filiere_id (int): ID de la filière

        Returns:
            list: Liste des créneaux de la filière
        """
        requete = """
            SELECT
                edt.*,
                c.nom_cours, c.type_cours,
                u.nom as enseignant_nom, u.prenom as enseignant_prenom,
                s.nom_salle
            FROM EmploiDuTemps edt
            JOIN Cours c ON edt.cours_id = c.id
            JOIN Enseignants e ON edt.enseignant_id = e.utilisateur_id
            JOIN Utilisateurs u ON e.utilisateur_id = u.id
            JOIN Salles s ON edt.salle_id = s.id
            WHERE c.filiere_id = %s
            ORDER BY
                FIELD(edt.jour, 'Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi'),
                edt.heure_debut
        """
        return executer_requete(requete, (filiere_id,), obtenir_resultats=True)

    @staticmethod
    def obtenir_par_etudiant(etudiant_id):
        """
        Récupère l'emploi du temps d'un étudiant (via sa filière)

        Args:
            etudiant_id (int): ID de l'étudiant

        Returns:
            list: Liste des créneaux de la filière de l'étudiant
        """
        etudiant = Etudiant.obtenir_par_id(etudiant_id)
        if not etudiant or not etudiant.get('filiere_id'):
            return []
        return EmploiDuTemps.obtenir_par_filiere(etudiant['filiere_id'])

    @staticmethod
    def obtenir_par_parent(parent_id):
        """
        Récupère l'emploi du temps des enfants d'un parent

        Args:
            parent_id (int): ID du parent

        Returns:
            list: Liste des créneaux des filières des enfants
        """
        enfants = Parent.obtenir_enfants(parent_id)
        if not enfants:
            return []

        # Collecter toutes les filières des enfants
        filieres_ids = list(set(enfant['filiere_id'] for enfant in enfants if enfant.get('filiere_id')))

        all_creneaux = []
        for filiere_id in filieres_ids:
            creneaux = EmploiDuTemps.obtenir_par_filiere(filiere_id)
            if creneaux:
                all_creneaux.extend(creneaux)

        # Supprimer les doublons si nécessaire
        seen = set()
        unique_creneaux = []
        for c in all_creneaux:
            key = (c['id'],)
            if key not in seen:
                seen.add(key)
                unique_creneaux.append(c)

        return unique_creneaux
    
    @staticmethod
    def obtenir_par_filiere_avec_statuts(filiere_id, date_cours=None):
        """
        Récupère l'emploi du temps d'une filière avec les statuts des enseignants
        
        Args:
            filiere_id (int): ID de la filière
            date_cours (str): Date du cours pour récupérer les statuts (YYYY-MM-DD)
        
        Returns:
            list: Liste des créneaux avec statuts
        """
        if date_cours:
            requete = """
                SELECT 
                    edt.*,
                    c.nom_cours, c.type_cours,
                    u.nom as enseignant_nom, u.prenom as enseignant_prenom,
                    s.nom_salle,
                    COALESCE(st.statut, 'disponible') as statut_enseignant,
                    st.heure_arrivee,
                    st.remarques as statut_remarques
                FROM EmploiDuTemps edt
                JOIN Cours c ON edt.cours_id = c.id
                JOIN Enseignants e ON edt.enseignant_id = e.utilisateur_id
                JOIN Utilisateurs u ON e.utilisateur_id = u.id
                JOIN Salles s ON edt.salle_id = s.id
                LEFT JOIN StatutsEnseignantTempsReel st ON st.creneau_id = edt.id 
                    AND st.enseignant_id = edt.enseignant_id 
                    AND st.date_cours = %s
                WHERE c.filiere_id = %s
                ORDER BY 
                    FIELD(edt.jour, 'Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi'),
                    edt.heure_debut
            """
            return executer_requete(requete, (date_cours, filiere_id), obtenir_resultats=True)
        else:
            return EmploiDuTemps.obtenir_par_filiere(filiere_id)
    
    @staticmethod
    def obtenir_par_id(creneau_id):
        """
        Récupère un créneau par son ID
        
        Args:
            creneau_id (int): ID du créneau
        
        Returns:
            dict: Données du créneau ou None
        """
        requete = """
            SELECT 
                edt.*,
                c.nom_cours, c.type_cours, c.filiere_id,
                u.nom as enseignant_nom, u.prenom as enseignant_prenom,
                s.nom_salle,
                f.nom_filiere, f.niveau
            FROM EmploiDuTemps edt
            JOIN Cours c ON edt.cours_id = c.id
            JOIN Enseignants e ON edt.enseignant_id = e.utilisateur_id
            JOIN Utilisateurs u ON e.utilisateur_id = u.id
            JOIN Salles s ON edt.salle_id = s.id
            JOIN Filieres f ON c.filiere_id = f.id
            WHERE edt.id = %s
        """
        return executer_requete_unique(requete, (creneau_id,))
    
    @staticmethod
    def modifier(creneau_id, cours_id, enseignant_id, salle_id, jour, heure_debut, heure_fin):
        """
        Modifie un créneau
        
        Args:
            creneau_id (int): ID du créneau
            cours_id (int): Nouveau cours
            enseignant_id (int): Nouvel enseignant
            salle_id (int): Nouvelle salle
            jour (str): Nouveau jour
            heure_debut (str): Nouvelle heure de début
            heure_fin (str): Nouvelle heure de fin
        
        Returns:
            int: Nombre de lignes affectées
        """
        requete = """
            UPDATE EmploiDuTemps 
            SET cours_id = %s, enseignant_id = %s, salle_id = %s, 
                jour = %s, heure_debut = %s, heure_fin = %s
            WHERE id = %s
        """
        return executer_requete(requete, (cours_id, enseignant_id, salle_id, jour, heure_debut, heure_fin, creneau_id))
    
    @staticmethod
    def supprimer(creneau_id):
        """
        Supprime un créneau
        
        Args:
            creneau_id (int): ID du créneau
        
        Returns:
            int: Nombre de lignes affectées
        """
        requete = "DELETE FROM EmploiDuTemps WHERE id = %s"
        return executer_requete(requete, (creneau_id,))


class Presence:
    """Modèle pour la table Presences"""
    
    @staticmethod
    def creer(creneau_id, enseignant_id, statut, date_cours, remarques='', marque_par=None):
        """
        Crée un enregistrement de présence
        
        Args:
            creneau_id (int): ID du créneau
            enseignant_id (int): ID de l'enseignant
            statut (str): Statut (present, absent, retard, non_marque)
            date_cours (str): Date du cours (YYYY-MM-DD)
            remarques (str): Remarques optionnelles
            marque_par (int): ID de l'utilisateur qui marque
        
        Returns:
            int: ID de la présence créée
        """
        requete = """
            INSERT INTO Presences (creneau_id, enseignant_id, statut, date_cours, remarques, marque_par)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        return executer_requete(requete, (creneau_id, enseignant_id, statut, date_cours, remarques, marque_par))
    
    @staticmethod
    def marquer_presence(creneau_id, enseignant_id, statut, date_cours, remarques='', marque_par=None):
        """
        Marque ou met à jour la présence pour un créneau
        
        Args:
            creneau_id (int): ID du créneau
            enseignant_id (int): ID de l'enseignant
            statut (str): Statut (present, absent, retard)
            date_cours (str): Date du cours
            remarques (str): Remarques
            marque_par (int): ID de l'utilisateur qui marque
        
        Returns:
            int: ID de la présence
        """
        # Vérifier si une présence existe déjà
        presence_existante = Presence.obtenir_par_creneau_et_date(creneau_id, date_cours)
        
        if presence_existante:
            # Mettre à jour
            requete = """
                UPDATE Presences 
                SET statut = %s, remarques = %s, marque_par = %s, date_marquage = CURRENT_TIMESTAMP
                WHERE creneau_id = %s AND date_cours = %s
            """
            executer_requete(requete, (statut, remarques, marque_par, creneau_id, date_cours))
            return presence_existante['id']
        else:
            # Créer
            return Presence.creer(creneau_id, enseignant_id, statut, date_cours, remarques, marque_par)
    
    @staticmethod
    def obtenir_par_creneau_et_date(creneau_id, date_cours):
        """
        Récupère la présence pour un créneau et une date
        
        Args:
            creneau_id (int): ID du créneau
            date_cours (str): Date du cours
        
        Returns:
            dict: Données de présence ou None
        """
        requete = "SELECT * FROM Presences WHERE creneau_id = %s AND date_cours = %s"
        return executer_requete_unique(requete, (creneau_id, date_cours))
    
    @staticmethod
    def obtenir_par_enseignant(enseignant_id, date_debut=None, date_fin=None):
        """
        Récupère toutes les présences d'un enseignant
        
        Args:
            enseignant_id (int): ID de l'enseignant
            date_debut (str): Date de début (optionnel)
            date_fin (str): Date de fin (optionnel)
        
        Returns:
            list: Liste des présences
        """
        requete = """
            SELECT p.*, 
                   edt.jour, edt.heure_debut, edt.heure_fin,
                   c.nom_cours, c.type_cours,
                   s.nom_salle,
                   u.nom as marque_par_nom, u.prenom as marque_par_prenom
            FROM Presences p
            JOIN EmploiDuTemps edt ON p.creneau_id = edt.id
            JOIN Cours c ON edt.cours_id = c.id
            JOIN Salles s ON edt.salle_id = s.id
            LEFT JOIN Utilisateurs u ON p.marque_par = u.id
            WHERE p.enseignant_id = %s
        """
        params = [enseignant_id]
        
        if date_debut:
            requete += " AND p.date_cours >= %s"
            params.append(date_debut)
        
        if date_fin:
            requete += " AND p.date_cours <= %s"
            params.append(date_fin)
        
        requete += " ORDER BY p.date_cours DESC, edt.heure_debut"
        
        return executer_requete(requete, tuple(params), obtenir_resultats=True)
    
    @staticmethod
    def obtenir_statistiques_enseignant(enseignant_id):
        """
        Calcule les statistiques de présence pour un enseignant
        
        Args:
            enseignant_id (int): ID de l'enseignant
        
        Returns:
            dict: Statistiques de présence
        """
        requete = """
            SELECT 
                COUNT(*) as total_seances,
                SUM(CASE WHEN statut = 'present' THEN 1 ELSE 0 END) as presents,
                SUM(CASE WHEN statut = 'absent' THEN 1 ELSE 0 END) as absents,
                SUM(CASE WHEN statut = 'retard' THEN 1 ELSE 0 END) as retards,
                SUM(CASE WHEN statut = 'non_marque' THEN 1 ELSE 0 END) as non_marques
            FROM Presences
            WHERE enseignant_id = %s
        """
        return executer_requete_unique(requete, (enseignant_id,))
    
    @staticmethod
    def obtenir_toutes_presences(date_debut=None, date_fin=None):
        """
        Récupère toutes les présences avec filtres optionnels
        
        Args:
            date_debut (str): Date de début
            date_fin (str): Date de fin
        
        Returns:
            list: Liste de toutes les présences
        """
        requete = """
            SELECT p.*,
                   edt.jour, edt.heure_debut, edt.heure_fin,
                   c.nom_cours, c.type_cours,
                   s.nom_salle,
                   u_ens.nom as enseignant_nom, u_ens.prenom as enseignant_prenom,
                   u_mark.nom as marque_par_nom, u_mark.prenom as marque_par_prenom
            FROM Presences p
            JOIN EmploiDuTemps edt ON p.creneau_id = edt.id
            JOIN Cours c ON edt.cours_id = c.id
            JOIN Salles s ON edt.salle_id = s.id
            JOIN Utilisateurs u_ens ON p.enseignant_id = u_ens.id
            LEFT JOIN Utilisateurs u_mark ON p.marque_par = u_mark.id
            WHERE 1=1
        """
        params = []
        
        if date_debut:
            requete += " AND p.date_cours >= %s"
            params.append(date_debut)
        
        if date_fin:
            requete += " AND p.date_cours <= %s"
            params.append(date_fin)
        
        requete += " ORDER BY p.date_cours DESC, edt.heure_debut"
        
        return executer_requete(requete, tuple(params) if params else None, obtenir_resultats=True)


class Note:
    """Modèle pour la table Notes avec workflow de validation UniCampus"""
    
    @staticmethod
    def creer(etudiant_id, cours_id, type_evaluation, note, coefficient, date_evaluation, commentaire, saisi_par, statut='EN_ATTENTE_DIRECTEUR'):
        """
        Crée une nouvelle note (statut par défaut: EN_ATTENTE_DIRECTEUR)
        
        Args:
            etudiant_id (int): ID de l'étudiant
            cours_id (int): ID du cours
            type_evaluation (str): Type d'évaluation (DS, Examen, TP, Projet, CC)
            note (float): Note sur 20
            coefficient (float): Coefficient de la note
            date_evaluation (str): Date de l'évaluation
            commentaire (str): Commentaire optionnel
            saisi_par (int): ID de l'utilisateur qui saisit
            statut (str): Statut initial (EN_ATTENTE_DIRECTEUR par défaut)
        
        Returns:
            int: ID de la note créée
        """
        requete = """
            INSERT INTO Notes 
            (etudiant_id, cours_id, type_evaluation, note, coefficient, date_evaluation, commentaire, saisi_par, statut)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        return executer_requete(requete, (etudiant_id, cours_id, type_evaluation, note, coefficient, date_evaluation, commentaire, saisi_par, statut))
    
    @staticmethod
    def obtenir_par_etudiant(etudiant_id, statut=None):
        """
        Récupère les notes d'un étudiant (filtrées par statut si spécifié)
        
        Args:
            etudiant_id (int): ID de l'étudiant
            statut (str, optional): Filtrer par statut (VALIDÉ, EN_ATTENTE_DIRECTEUR, etc.)
        
        Returns:
            list: Liste des notes de l'étudiant
        """
        requete = """
            SELECT n.*, 
                   c.nom_cours, c.type_cours,
                   f.nom_filiere, f.niveau,
                   u.nom as saisi_par_nom, u.prenom as saisi_par_prenom,
                   uv.nom as valide_par_nom, uv.prenom as valide_par_prenom
            FROM Notes n
            JOIN Cours c ON n.cours_id = c.id
            JOIN Filieres f ON c.filiere_id = f.id
            JOIN Utilisateurs u ON n.saisi_par = u.id
            LEFT JOIN Utilisateurs uv ON n.valide_par = uv.id
            WHERE n.etudiant_id = %s
        """
        params = [etudiant_id]
        
        if statut:
            requete += " AND n.statut = %s"
            params.append(statut)
        
        requete += " ORDER BY n.date_evaluation DESC, c.nom_cours"
        
        return executer_requete(requete, tuple(params), obtenir_resultats=True)
    
    @staticmethod
    def obtenir_notes_validees():
        """
        Récupère toutes les notes validées avec détails

        Returns:
            list: Liste des notes validées
        """
        requete = """
            SELECT n.*,
                   u_etud.nom as etudiant_nom, u_etud.prenom as etudiant_prenom,
                   u_ens.nom as enseignant_nom, u_ens.prenom as enseignant_prenom,
                   c.nom_cours
            FROM Notes n
            JOIN Utilisateurs u_etud ON n.etudiant_id = u_etud.id
            JOIN Utilisateurs u_ens ON n.enseignant_id = u_ens.id
            JOIN Cours c ON n.cours_id = c.id
            WHERE n.statut = 'VALIDÉ'
            ORDER BY n.date_creation DESC
        """
        return executer_requete(requete, obtenir_resultats=True)
    
    @staticmethod
    def obtenir_notes_validees_etudiant(etudiant_id):
        """
        Récupère uniquement les notes validées d'un étudiant
        
        Args:
            etudiant_id (int): ID de l'étudiant
        
        Returns:
            list: Liste des notes validées
        """
        return Note.obtenir_par_etudiant(etudiant_id, statut='VALIDÉ')
    
    @staticmethod
    def obtenir_notes_en_attente(filiere_id=None):
        """
        Récupère toutes les notes en attente de validation (pour le Directeur)

        Args:
            filiere_id (int, optional): Filtrer par filière

        Returns:
            list: Liste des notes en attente
        """
        requete = """
            SELECT n.*,
                   u_etud.matricule, u_etud.nom as etudiant_nom, u_etud.prenom as etudiant_prenom,
                   c.nom_cours, c.type_cours,
                   f.nom_filiere, f.niveau,
                   u_saisi.nom as saisi_par_nom, u_saisi.prenom as saisi_par_prenom
            FROM Notes n
            JOIN Etudiants e ON n.etudiant_id = e.utilisateur_id
            JOIN Utilisateurs u_etud ON e.utilisateur_id = u_etud.id
            JOIN Cours c ON n.cours_id = c.id
            JOIN Filieres f ON c.filiere_id = f.id
            JOIN Utilisateurs u_saisi ON n.saisi_par = u_saisi.id
            WHERE n.statut = 'EN_ATTENTE_DIRECTEUR'
        """
        params = []

        if filiere_id:
            requete += " AND c.filiere_id = %s"
            params.append(filiere_id)

        requete += " ORDER BY n.date_creation ASC, f.niveau, u_etud.nom"

        return executer_requete(requete, tuple(params) if params else None, obtenir_resultats=True)
    
    @staticmethod
    def valider_note(note_id, directeur_id):
        """
        Valide une note (change le statut à VALIDÉ)
        
        Args:
            note_id (int): ID de la note
            directeur_id (int): ID du directeur qui valide
        
        Returns:
            int: Nombre de lignes affectées
        """
        requete = """
            UPDATE Notes 
            SET statut = 'VALIDÉ', valide_par = %s, date_validation = NOW()
            WHERE id = %s AND statut = 'EN_ATTENTE_DIRECTEUR'
        """
        return executer_requete(requete, (directeur_id, note_id))
    
    @staticmethod
    def modifier_note_non_validee(note_id, nouvelle_note, nouveau_coefficient=None, nouveau_commentaire=None):
        """
        Modifie une note non validée (réservé au Directeur)
        
        Args:
            note_id (int): ID de la note
            nouvelle_note (float): Nouvelle valeur de la note
            nouveau_coefficient (float, optional): Nouveau coefficient
            nouveau_commentaire (str, optional): Nouveau commentaire
        
        Returns:
            int: Nombre de lignes affectées
        """
        # Construire la requête dynamiquement
        updates = ["note = %s"]
        params = [nouvelle_note]
        
        if nouveau_coefficient is not None:
            updates.append("coefficient = %s")
            params.append(nouveau_coefficient)
        
        if nouveau_commentaire is not None:
            updates.append("commentaire = %s")
            params.append(nouveau_commentaire)
        
        params.append(note_id)
        
        requete = f"""
            UPDATE Notes 
            SET {', '.join(updates)}
            WHERE id = %s AND statut IN ('EN_ATTENTE_DIRECTEUR', 'EN_REVISION')
        """
        return executer_requete(requete, tuple(params))
    
    @staticmethod
    def mettre_en_revision(note_id):
        """
        Met une note en révision
        
        Args:
            note_id (int): ID de la note
        
        Returns:
            int: Nombre de lignes affectées
        """
        requete = "UPDATE Notes SET statut = 'EN_REVISION' WHERE id = %s"
        return executer_requete(requete, (note_id,))
    
    @staticmethod
    def obtenir_par_cours(cours_id):
        """
        Récupère toutes les notes d'un cours
        
        Args:
            cours_id (int): ID du cours
        
        Returns:
            list: Liste des notes du cours
        """
        requete = """
            SELECT n.*,
                   u_etud.matricule, u_etud.nom as etudiant_nom, u_etud.prenom as etudiant_prenom,
                   u_saisi.nom as saisi_par_nom, u_saisi.prenom as saisi_par_prenom
            FROM Notes n
            JOIN Etudiants e ON n.etudiant_id = e.utilisateur_id
            JOIN Utilisateurs u_etud ON e.utilisateur_id = u_etud.id
            JOIN Utilisateurs u_saisi ON n.saisi_par = u_saisi.id
            WHERE n.cours_id = %s
            ORDER BY u_etud.nom, u_etud.prenom, n.type_evaluation
        """
        return executer_requete(requete, (cours_id,), obtenir_resultats=True)
    
    @staticmethod
    def obtenir_par_filiere(filiere_id):
        """
        Récupère toutes les notes d'une filière
        
        Args:
            filiere_id (int): ID de la filière
        
        Returns:
            list: Liste des notes de la filière
        """
        requete = """
            SELECT n.*,
                   u_etud.matricule, u_etud.nom as etudiant_nom, u_etud.prenom as etudiant_prenom,
                   c.nom_cours, c.type_cours,
                   u_saisi.nom as saisi_par_nom, u_saisi.prenom as saisi_par_prenom
            FROM Notes n
            JOIN Etudiants e ON n.etudiant_id = e.utilisateur_id
            JOIN Utilisateurs u_etud ON e.utilisateur_id = u_etud.id
            JOIN Cours c ON n.cours_id = c.id
            JOIN Utilisateurs u_saisi ON n.saisi_par = u_saisi.id
            WHERE c.filiere_id = %s
            ORDER BY u_etud.nom, u_etud.prenom, c.nom_cours
        """
        return executer_requete(requete, (filiere_id,), obtenir_resultats=True)
    
    @staticmethod
    def obtenir_par_id(note_id):
        """
        Récupère une note par son ID
        
        Args:
            note_id (int): ID de la note
        
        Returns:
            dict: Données de la note ou None
        """
        requete = "SELECT * FROM Notes WHERE id = %s"
        return executer_requete_unique(requete, (note_id,))
    
    @staticmethod
    def modifier(note_id, note, coefficient, commentaire):
        """
        Modifie une note existante (uniquement si non validée)
        
        Args:
            note_id (int): ID de la note
            note (float): Nouvelle note
            coefficient (float): Nouveau coefficient
            commentaire (str): Nouveau commentaire
        
        Returns:
            int: Nombre de lignes affectées
        """
        requete = """
            UPDATE Notes 
            SET note = %s, coefficient = %s, commentaire = %s
            WHERE id = %s AND statut != 'VALIDÉ'
        """
        return executer_requete(requete, (note, coefficient, commentaire, note_id))
    
    @staticmethod
    def supprimer(note_id):
        """
        Supprime une note
        
        Args:
            note_id (int): ID de la note
        
        Returns:
            int: Nombre de lignes affectées
        """
        requete = "DELETE FROM Notes WHERE id = %s"
        return executer_requete(requete, (note_id,))
    
    @staticmethod
    def calculer_moyenne_etudiant(etudiant_id, cours_id=None, seulement_validees=True):
        """
        Calcule la moyenne d'un étudiant (uniquement notes validées par défaut)
        
        Args:
            etudiant_id (int): ID de l'étudiant
            cours_id (int, optional): ID du cours
            seulement_validees (bool): Calculer uniquement avec les notes validées
        
        Returns:
            dict: Moyenne et statistiques
        """
        statut_filter = "AND statut = 'VALIDÉ'" if seulement_validees else ""
        
        if cours_id:
            requete = f"""
                SELECT 
                    ROUND(SUM(note * coefficient) / SUM(coefficient), 2) as moyenne,
                    COUNT(*) as nb_notes,
                    MIN(note) as note_min,
                    MAX(note) as note_max
                FROM Notes
                WHERE etudiant_id = %s AND cours_id = %s {statut_filter}
            """
            params = (etudiant_id, cours_id)
        else:
            requete = f"""
                SELECT 
                    ROUND(SUM(note * coefficient) / SUM(coefficient), 2) as moyenne,
                    COUNT(*) as nb_notes,
                    MIN(note) as note_min,
                    MAX(note) as note_max
                FROM Notes
                WHERE etudiant_id = %s {statut_filter}
            """
            params = (etudiant_id,)
        
        return executer_requete_unique(requete, params)
    
    @staticmethod
    def calculer_moyenne_cours(cours_id):
        """
        Calcule la moyenne générale d'un cours
        
        Args:
            cours_id (int): ID du cours
        
        Returns:
            dict: Statistiques du cours
        """
        requete = """
            SELECT 
                ROUND(AVG(note), 2) as moyenne,
                COUNT(DISTINCT etudiant_id) as nb_etudiants,
                MIN(note) as note_min,
                MAX(note) as note_max,
                COUNT(*) as nb_notes
            FROM Notes
            WHERE cours_id = %s
        """
        return executer_requete_unique(requete, (cours_id,))
    
    @staticmethod
    def obtenir_toutes():
        """
        Récupère toutes les notes avec informations complètes

        Returns:
            list: Liste de toutes les notes
        """
        requete = """
            SELECT n.*,
                   u_etud.matricule, u_etud.nom as etudiant_nom, u_etud.prenom as etudiant_prenom,
                   c.nom_cours, c.type_cours,
                   f.nom_filiere, f.niveau,
                   u_saisi.nom as saisi_par_nom, u_saisi.prenom as saisi_par_prenom,
                   uv.nom as valide_par_nom, uv.prenom as valide_par_prenom
            FROM Notes n
            JOIN Etudiants e ON n.etudiant_id = e.utilisateur_id
            JOIN Utilisateurs u_etud ON e.utilisateur_id = u_etud.id
            JOIN Cours c ON n.cours_id = c.id
            JOIN Filieres f ON c.filiere_id = f.id
            JOIN Utilisateurs u_saisi ON n.saisi_par = u_saisi.id
            LEFT JOIN Utilisateurs uv ON n.valide_par = uv.id
            ORDER BY n.date_creation DESC
        """
        return executer_requete(requete, obtenir_resultats=True)

    @staticmethod
    def obtenir_cours_enseignant(enseignant_id):
        """
        Récupère les cours enseignés par un enseignant

        Args:
            enseignant_id (int): ID de l'enseignant

        Returns:
            list: Liste des cours
        """
        requete = """
            SELECT DISTINCT c.*, f.nom_filiere, f.niveau
            FROM Cours c
            JOIN EmploiDuTemps edt ON c.id = edt.cours_id
            JOIN Filieres f ON c.filiere_id = f.id
            WHERE edt.enseignant_id = %s
            ORDER BY f.niveau, c.nom_cours
        """
        return executer_requete(requete, (enseignant_id,), obtenir_resultats=True)


class Parent:
    """Modèle pour la gestion des parents d'étudiants"""

    @staticmethod
    def creer(nom, prenom, matricule):
        """
        Crée un utilisateur parent

        Args:
            nom (str): Nom du parent
            prenom (str): Prénom du parent
            matricule (str): Matricule unique

        Returns:
            int: ID de l'utilisateur créé
        """
        return Utilisateur.creer(nom, prenom, matricule, 'parent')

    @staticmethod
    def lier_etudiant(parent_id, etudiant_id, relation='autre', telephone='', email='', adresse='', contact_prioritaire=False):
        """
        Lie un parent à un étudiant

        Args:
            parent_id (int): ID du parent
            etudiant_id (int): ID de l'étudiant
            relation (str): Type de relation (pere, mere, tuteur, autre)
            telephone (str): Téléphone du parent
            email (str): Email du parent
            adresse (str): Adresse du parent
            contact_prioritaire (bool): Contact prioritaire

        Returns:
            int: ID de la liaison créée
        """
        requete = """
            INSERT INTO ParentsEtudiants
            (parent_id, etudiant_id, relation, telephone, email, adresse, contact_prioritaire)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        return executer_requete(requete, (parent_id, etudiant_id, relation, telephone, email, adresse, contact_prioritaire))

    @staticmethod
    def obtenir_enfants(parent_id):
        """
        Récupère tous les enfants d'un parent

        Args:
            parent_id (int): ID du parent

        Returns:
            list: Liste des enfants avec leurs informations
        """
        requete = """
            SELECT pe.*,
                   u_etud.nom as etudiant_nom, u_etud.prenom as etudiant_prenom, u_etud.matricule as etudiant_matricule,
                   e.filiere_id,
                   f.nom_filiere, f.niveau
            FROM ParentsEtudiants pe
            JOIN Utilisateurs u_etud ON pe.etudiant_id = u_etud.id
            LEFT JOIN Etudiants e ON pe.etudiant_id = e.utilisateur_id
            LEFT JOIN Filieres f ON e.filiere_id = f.id
            WHERE pe.parent_id = %s
            ORDER BY u_etud.nom, u_etud.prenom
        """
        return executer_requete(requete, (parent_id,), obtenir_resultats=True)

    @staticmethod
    def obtenir_parents_etudiant(etudiant_id):
        """
        Récupère tous les parents d'un étudiant

        Args:
            etudiant_id (int): ID de l'étudiant

        Returns:
            list: Liste des parents
        """
        requete = """
            SELECT * FROM vue_parents_etudiants
            WHERE etudiant_id = %s
            ORDER BY contact_prioritaire DESC, parent_nom
        """
        return executer_requete(requete, (etudiant_id,), obtenir_resultats=True)

    @staticmethod
    def modifier_liaison(liaison_id, relation, telephone, email, adresse, contact_prioritaire):
        """
        Modifie une liaison parent-étudiant

        Args:
            liaison_id (int): ID de la liaison
            relation (str): Type de relation
            telephone (str): Téléphone
            email (str): Email
            adresse (str): Adresse
            contact_prioritaire (bool): Contact prioritaire

        Returns:
            int: Nombre de lignes affectées
        """
        requete = """
            UPDATE ParentsEtudiants
            SET relation = %s, telephone = %s, email = %s, adresse = %s, contact_prioritaire = %s
            WHERE id = %s
        """
        return executer_requete(requete, (relation, telephone, email, adresse, contact_prioritaire, liaison_id))

    @staticmethod
    def supprimer_liaison(liaison_id):
        """
        Supprime une liaison parent-étudiant

        Args:
            liaison_id (int): ID de la liaison

        Returns:
            int: Nombre de lignes affectées
        """
        requete = "DELETE FROM ParentsEtudiants WHERE id = %s"
        return executer_requete(requete, (liaison_id,))


class Bulletin:
    """
    Gestion des bulletins de notes des étudiants
    """

    @staticmethod
    def obtenir_tous():
        """
        Récupère tous les bulletins générés

        Returns:
            list: Liste de tous les bulletins
        """
        requete = """
            SELECT b.*,
                   u.nom as etudiant_nom, u.prenom as etudiant_prenom,
                   f.nom_filiere
            FROM Bulletins b
            JOIN Utilisateurs u ON b.etudiant_id = u.id
            JOIN Etudiants e ON u.id = e.utilisateur_id
            JOIN Filieres f ON e.filiere_id = f.id
            ORDER BY b.date_generation DESC
        """
        return executer_requete(requete, obtenir_resultats=True)

    @staticmethod
    def creer(etudiant_id, periode, moyenne_generale, details_json, fichier_nom):
        """
        Crée un nouveau bulletin

        Args:
            etudiant_id (int): ID de l'étudiant
            periode (str): Période (S1, S2, etc.)
            moyenne_generale (float): Moyenne générale
            details_json (str): Détails en JSON
            fichier_nom (str): Nom du fichier PDF

        Returns:
            int: ID du bulletin créé
        """
        requete = """
            INSERT INTO Bulletins (etudiant_id, periode, moyenne_generale, details, fichier_nom, date_generation)
            VALUES (%s, %s, %s, %s, %s, NOW())
        """
        params = (etudiant_id, periode, moyenne_generale, details_json, fichier_nom)
        return executer_requete(requete, params, obtenir_id=True)

    @staticmethod
    def stats():
        """
        Statistiques sur les bulletins

        Returns:
            dict: Statistiques (total, par période, etc.)
        """
        requete = """
            SELECT
                COUNT(*) as total,
                periode,
                AVG(moyenne_generale) as moyenne_moyennes
            FROM Bulletins
            GROUP BY periode
        """
        resultats = executer_requete(requete, obtenir_resultats=True)

        stats = {'total': 0, 'par_periode': {}}
        for row in resultats or []:
            stats['total'] += row['total']
            stats['par_periode'][row['periode']] = {
                'count': row['total'],
                'avg': row['moyenne_moyennes']
            }

        return stats


class Conflit:
    """Modèle pour la gestion des conflits de planification"""
    
    @staticmethod
    def detecter_conflits(creneau_id=None):
        """
        Détecte les conflits de planification
        
        Args:
            creneau_id (int, optional): ID du créneau à vérifier, ou None pour tous
        
        Returns:
            list: Liste des conflits détectés
        """
        if creneau_id:
            # Vérifier un créneau spécifique
            creneau = EmploiDuTemps.obtenir_par_id(creneau_id)
            if not creneau:
                return []
            
            conflit = EmploiDuTemps.verifier_conflit(
                creneau['enseignant_id'],
                creneau['salle_id'],
                creneau['jour'],
                creneau['heure_debut'],
                creneau['heure_fin'],
                creneau['cours_id'],
                creneau_id
            )
            
            if conflit:
                return [conflit]
            return []
        else:
            # Vérifier tous les créneaux
            tous_creneaux = EmploiDuTemps.obtenir_tous()
            conflits = []
            
            for creneau in tous_creneaux:
                conflit = EmploiDuTemps.verifier_conflit(
                    creneau['enseignant_id'],
                    creneau['salle_id'],
                    creneau['jour'],
                    creneau['heure_debut'],
                    creneau['heure_fin'],
                    creneau['cours_id'],
                    creneau['id']
                )
                if conflit:
                    conflits.append({
                        'creneau_id': creneau['id'],
                        'conflit': conflit
                    })
            
            return conflits
    
    @staticmethod
    def enregistrer_conflit(creneau_id, type_conflit, creneau_conflit_id, description, severite='moyenne', action_suggeree=''):
        """
        Enregistre un conflit détecté
        
        Args:
            creneau_id (int): ID du créneau
            type_conflit (str): Type de conflit
            creneau_conflit_id (int): ID du créneau en conflit
            description (str): Description du conflit
            severite (str): Sévérité (faible, moyenne, critique)
            action_suggeree (str): Action suggérée
        
        Returns:
            int: ID du conflit créé
        """
        requete = """
            INSERT INTO ConflitsPlanification 
            (creneau_id, type_conflit, creneau_conflit_id, description, severite, action_suggeree)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        return executer_requete(requete, (creneau_id, type_conflit, creneau_conflit_id, description, severite, action_suggeree))
    
    @staticmethod
    def obtenir_conflits_actifs():
        """
        Récupère tous les conflits actifs
        
        Returns:
            list: Liste des conflits actifs
        """
        requete = """
            SELECT c.*,
                   edt1.jour, edt1.heure_debut, edt1.heure_fin,
                   cours1.nom_cours as cours_nom,
                   u1.nom as enseignant_nom, u1.prenom as enseignant_prenom,
                   s1.nom_salle,
                   f1.nom_filiere, f1.niveau
            FROM ConflitsPlanification c
            JOIN EmploiDuTemps edt1 ON c.creneau_id = edt1.id
            JOIN Cours cours1 ON edt1.cours_id = cours1.id
            JOIN Enseignants e1 ON edt1.enseignant_id = e1.utilisateur_id
            JOIN Utilisateurs u1 ON e1.utilisateur_id = u1.id
            JOIN Salles s1 ON edt1.salle_id = s1.id
            JOIN Filieres f1 ON cours1.filiere_id = f1.id
            WHERE c.statut = 'actif'
            ORDER BY c.severite DESC, c.date_detection DESC
        """
        return executer_requete(requete, obtenir_resultats=True)
    
    @staticmethod
    def resoudre_conflit(conflit_id, resolu_par):
        """
        Marque un conflit comme résolu
        
        Args:
            conflit_id (int): ID du conflit
            resolu_par (int): ID de l'utilisateur qui résout
        
        Returns:
            int: Nombre de lignes affectées
        """
        requete = """
            UPDATE ConflitsPlanification 
            SET statut = 'resolu', resolu_par = %s, date_resolution = CURRENT_TIMESTAMP
            WHERE id = %s
        """
        return executer_requete(requete, (resolu_par, conflit_id))
    
    @staticmethod
    def ignorer_conflit(conflit_id):
        """
        Marque un conflit comme ignoré
        
        Args:
            conflit_id (int): ID du conflit
        
        Returns:
            int: Nombre de lignes affectées
        """
        requete = "UPDATE ConflitsPlanification SET statut = 'ignore' WHERE id = %s"
        return executer_requete(requete, (conflit_id,))


class ImportNote:
    """Modèle pour la table ImportNotes"""
    
    @staticmethod
    def creer(cours_id, filiere_id, enseignant_id, fichier_nom, nombre_notes, role_initiateur=None):
        """
        Enregistre un import de notes
        
        Args:
            cours_id (int): ID du cours
            filiere_id (int): ID de la filière
            enseignant_id (int): ID de l'enseignant
            fichier_nom (str): Nom du fichier importé
            nombre_notes (int): Nombre de notes importées
            role_initiateur (str, optional): Rôle de l'initiateur de l'import
        
        Returns:
            int: ID de l'import créé
        """
        requete = """
            INSERT INTO ImportNotes 
            (cours_id, filiere_id, enseignant_id, role_initiateur, fichier_nom, nombre_notes)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        return executer_requete(requete, (cours_id, filiere_id, enseignant_id, role_initiateur, fichier_nom, nombre_notes))
    
    @staticmethod
    def obtenir_historique(enseignant_id=None):
        """
        Récupère l'historique des imports
        
        Args:
            enseignant_id (int, optional): ID de l'enseignant
        
        Returns:
            list: Liste des imports
        """
        if enseignant_id:
            requete = """
                SELECT i.*,
                       c.nom_cours,
                       f.nom_filiere, f.niveau
                FROM ImportNotes i
                JOIN Cours c ON i.cours_id = c.id
                JOIN Filieres f ON i.filiere_id = f.id
                WHERE i.enseignant_id = %s
                ORDER BY i.date_import DESC
            """
            return executer_requete(requete, (enseignant_id,), obtenir_resultats=True)
        else:
            requete = """
                SELECT i.*,
                       c.nom_cours,
                       f.nom_filiere, f.niveau,
                       u.nom as enseignant_nom, u.prenom as enseignant_prenom
                FROM ImportNotes i
                JOIN Cours c ON i.cours_id = c.id
                JOIN Filieres f ON i.filiere_id = f.id
                JOIN Utilisateurs u ON i.enseignant_id = u.id
                ORDER BY i.date_import DESC
            """
            return executer_requete(requete, obtenir_resultats=True)


class StatutEnseignant:
    """Modèle pour la table StatutsEnseignantTempsReel"""
    
    @staticmethod
    def obtenir_statut(enseignant_id, creneau_id, date_cours):
        """
        Récupère le statut d'un enseignant pour un créneau et une date
        
        Args:
            enseignant_id (int): ID de l'enseignant
            creneau_id (int): ID du créneau
            date_cours (str): Date du cours (YYYY-MM-DD)
        
        Returns:
            dict: Données du statut ou None
        """
        requete = """
            SELECT * FROM StatutsEnseignantTempsReel
            WHERE enseignant_id = %s AND creneau_id = %s AND date_cours = %s
        """
        return executer_requete_unique(requete, (enseignant_id, creneau_id, date_cours))
    
    @staticmethod
    def marquer_statut(enseignant_id, creneau_id, date_cours, statut, heure_arrivee=None, remarques='', mis_a_jour_par=None):
        """
        Marque ou met à jour le statut d'un enseignant
        
        Args:
            enseignant_id (int): ID de l'enseignant
            creneau_id (int): ID du créneau
            date_cours (str): Date du cours
            statut (str): Statut (disponible, non_disponible, en_retard, present)
            heure_arrivee (str): Heure d'arrivée (format HH:MM)
            remarques (str): Remarques
            mis_a_jour_par (int): ID de l'utilisateur qui met à jour
        
        Returns:
            int: ID du statut
        """
        # Vérifier si un statut existe déjà
        statut_existant = StatutEnseignant.obtenir_statut(enseignant_id, creneau_id, date_cours)
        
        if statut_existant:
            # Mettre à jour
            requete = """
                UPDATE StatutsEnseignantTempsReel 
                SET statut = %s, heure_arrivee = %s, remarques = %s, mis_a_jour_par = %s
                WHERE enseignant_id = %s AND creneau_id = %s AND date_cours = %s
            """
            executer_requete(requete, (statut, heure_arrivee, remarques, mis_a_jour_par, enseignant_id, creneau_id, date_cours))
            return statut_existant['id']
        else:
            # Créer
            requete = """
                INSERT INTO StatutsEnseignantTempsReel 
                (enseignant_id, creneau_id, date_cours, statut, heure_arrivee, remarques, mis_a_jour_par)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            return executer_requete(requete, (enseignant_id, creneau_id, date_cours, statut, heure_arrivee, remarques, mis_a_jour_par))
    
    @staticmethod
    def obtenir_statuts_jour(date_cours):
        """
        Récupère tous les statuts pour une date donnée
        
        Args:
            date_cours (str): Date du cours (YYYY-MM-DD)
        
        Returns:
            list: Liste des statuts avec informations complètes
        """
        requete = """
            SELECT s.*,
                   u.nom as enseignant_nom, u.prenom as enseignant_prenom,
                   edt.jour, edt.heure_debut, edt.heure_fin,
                   c.nom_cours,
                   u_maj.nom as maj_par_nom, u_maj.prenom as maj_par_prenom
            FROM StatutsEnseignantTempsReel s
            JOIN Utilisateurs u ON s.enseignant_id = u.id
            JOIN EmploiDuTemps edt ON s.creneau_id = edt.id
            JOIN Cours c ON edt.cours_id = c.id
            LEFT JOIN Utilisateurs u_maj ON s.mis_a_jour_par = u_maj.id
            WHERE s.date_cours = %s
            ORDER BY edt.heure_debut
        """
        return executer_requete(requete, (date_cours,), obtenir_resultats=True)
    
    @staticmethod
    def obtenir_statuts_enseignant(enseignant_id, date_debut=None, date_fin=None):
        """
        Récupère tous les statuts d'un enseignant avec filtres optionnels
        
        Args:
            enseignant_id (int): ID de l'enseignant
            date_debut (str): Date de début (optionnel)
            date_fin (str): Date de fin (optionnel)
        
        Returns:
            list: Liste des statuts
        """
        requete = """
            SELECT s.*,
                   edt.jour, edt.heure_debut, edt.heure_fin,
                   c.nom_cours, c.type_cours,
                   sal.nom_salle
            FROM StatutsEnseignantTempsReel s
            JOIN EmploiDuTemps edt ON s.creneau_id = edt.id
            JOIN Cours c ON edt.cours_id = c.id
            JOIN Salles sal ON edt.salle_id = sal.id
            WHERE s.enseignant_id = %s
        """
        params = [enseignant_id]
        
        if date_debut:
            requete += " AND s.date_cours >= %s"
            params.append(date_debut)
        
        if date_fin:
            requete += " AND s.date_cours <= %s"
            params.append(date_fin)
        
        requete += " ORDER BY s.date_cours DESC, edt.heure_debut"
        
        return executer_requete(requete, tuple(params), obtenir_resultats=True)


class Message:
    """Modèle pour la table Messages (système de messagerie et signalements)"""
    
    @staticmethod
    def creer(expediteur_id, destinataire_id, sujet, contenu, type_message='MESSAGE', note_id=None):
        """
        Crée un nouveau message
        
        Args:
            expediteur_id (int): ID de l'expéditeur
            destinataire_id (int): ID du destinataire
            sujet (str): Sujet du message
            contenu (str): Contenu du message
            type_message (str): Type (MESSAGE, SIGNALEMENT, NOTIFICATION)
            note_id (int, optional): ID de la note concernée (pour signalements)
        
        Returns:
            int: ID du message créé
        """
        requete = """
            INSERT INTO Messages 
            (expediteur_id, destinataire_id, type_message, sujet, contenu, note_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        return executer_requete(requete, (expediteur_id, destinataire_id, type_message, sujet, contenu, note_id))
    
    @staticmethod
    def creer_signalement(etudiant_id, note_id, contenu):
        """
        Crée un signalement de note (envoyé au Directeur)
        
        Args:
            etudiant_id (int): ID de l'étudiant qui signale
            note_id (int): ID de la note concernée
            contenu (str): Contenu du signalement
        
        Returns:
            int: ID du message créé
        """
        # Récupérer la note pour le sujet
        note = Note.obtenir_par_id(note_id)
        if not note:
            return None
        
        # Trouver le directeur (premier utilisateur avec rôle DIRECTEUR)
        from app.db import executer_requete_unique
        directeur = executer_requete_unique(
            "SELECT id FROM Utilisateurs WHERE role = 'DIRECTEUR' LIMIT 1"
        )
        
        if not directeur:
            return None
        
        sujet = f"Signalement de note - {note.get('type_evaluation', 'Évaluation')}"
        
        return Message.creer(
            etudiant_id, 
            directeur['id'], 
            sujet, 
            contenu, 
            'SIGNALEMENT', 
            note_id
        )
    
    @staticmethod
    def obtenir_messages_non_lus(user_id):
        """
        Récupère les messages non lus d'un utilisateur
        
        Args:
            user_id (int): ID de l'utilisateur
        
        Returns:
            list: Liste des messages non lus
        """
        requete = """
            SELECT m.*,
                   u_exp.nom as expediteur_nom, u_exp.prenom as expediteur_prenom,
                   u_exp.role as expediteur_role
            FROM Messages m
            JOIN Utilisateurs u_exp ON m.expediteur_id = u_exp.id
            WHERE m.destinataire_id = %s AND m.lu = FALSE
            ORDER BY m.date_creation DESC
        """
        return executer_requete(requete, (user_id,), obtenir_resultats=True)
    
    @staticmethod
    def obtenir_tous_messages(user_id, type_message=None):
        """
        Récupère tous les messages d'un utilisateur
        
        Args:
            user_id (int): ID de l'utilisateur
            type_message (str, optional): Filtrer par type
        
        Returns:
            list: Liste des messages
        """
        requete = """
            SELECT m.*,
                   u_exp.nom as expediteur_nom, u_exp.prenom as expediteur_prenom,
                   u_exp.role as expediteur_role
            FROM Messages m
            JOIN Utilisateurs u_exp ON m.expediteur_id = u_exp.id
            WHERE m.destinataire_id = %s
        """
        params = [user_id]
        
        if type_message:
            requete += " AND m.type_message = %s"
            params.append(type_message)
        
        requete += " ORDER BY m.lu ASC, m.date_creation DESC"
        
        return executer_requete(requete, tuple(params), obtenir_resultats=True)
    
    @staticmethod
    def marquer_comme_lu(message_id):
        """
        Marque un message comme lu
        
        Args:
            message_id (int): ID du message
        
        Returns:
            int: Nombre de lignes affectées
        """
        requete = "UPDATE Messages SET lu = TRUE, date_lecture = NOW() WHERE id = %s"
        return executer_requete(requete, (message_id,))
    
    @staticmethod
    def compter_non_lus(user_id):
        """
        Compte le nombre de messages non lus
        
        Args:
            user_id (int): ID de l'utilisateur
        
        Returns:
            int: Nombre de messages non lus
        """
        requete = "SELECT COUNT(*) as count FROM Messages WHERE destinataire_id = %s AND lu = FALSE"
        result = executer_requete_unique(requete, (user_id,))
        return result['count'] if result else 0


class Bulletin:
    """Modèle pour la table Bulletins"""
    
    @staticmethod
    def creer(etudiant_id, filiere_id, semestre, annee_academique, genere_par, moyenne_generale=None, rang=None, appreciation=''):
        """
        Crée un nouveau bulletin
        
        Args:
            etudiant_id (int): ID de l'étudiant
            filiere_id (int): ID de la filière
            semestre (str): Semestre (S1, S2, etc.)
            annee_academique (str): Année académique (2024-2025)
            genere_par (int): ID de l'utilisateur qui génère
            moyenne_generale (float, optional): Moyenne générale
            rang (int, optional): Rang de l'étudiant
            appreciation (str): Appréciation
        
        Returns:
            int: ID du bulletin créé
        """
        requete = """
            INSERT INTO Bulletins 
            (etudiant_id, filiere_id, semestre, annee_academique, moyenne_generale, rang, appreciation, genere_par)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        return executer_requete(requete, (etudiant_id, filiere_id, semestre, annee_academique, moyenne_generale, rang, appreciation, genere_par))
    
    @staticmethod
    def obtenir_bulletins_etudiant(etudiant_id):
        """
        Récupère tous les bulletins d'un étudiant
        
        Args:
            etudiant_id (int): ID de l'étudiant
        
        Returns:
            list: Liste des bulletins
        """
        requete = """
            SELECT b.*,
                   f.nom_filiere, f.niveau,
                   u.nom as genere_par_nom, u.prenom as genere_par_prenom
            FROM Bulletins b
            JOIN Filieres f ON b.filiere_id = f.id
            JOIN Utilisateurs u ON b.genere_par = u.id
            WHERE b.etudiant_id = %s
            ORDER BY b.annee_academique DESC, b.semestre DESC
        """
        return executer_requete(requete, (etudiant_id,), obtenir_resultats=True)
    
    @staticmethod
    def obtenir_par_id(bulletin_id):
        """
        Récupère un bulletin par son ID
        
        Args:
            bulletin_id (int): ID du bulletin
        
        Returns:
            dict: Données du bulletin ou None
        """
        requete = """
            SELECT b.*,
                   u_etud.nom as etudiant_nom, u_etud.prenom as etudiant_prenom,
                   u_etud.matricule as etudiant_matricule,
                   f.nom_filiere, f.niveau
            FROM Bulletins b
            JOIN Etudiants e ON b.etudiant_id = e.utilisateur_id
            JOIN Utilisateurs u_etud ON e.utilisateur_id = u_etud.id
            JOIN Filieres f ON b.filiere_id = f.id
            WHERE b.id = %s
        """
        return executer_requete_unique(requete, (bulletin_id,))
    
    @staticmethod
    def mettre_a_jour_fichier_pdf(bulletin_id, fichier_pdf):
        """
        Met à jour le chemin du fichier PDF
        
        Args:
            bulletin_id (int): ID du bulletin
            fichier_pdf (str): Chemin du fichier PDF
        
        Returns:
            int: Nombre de lignes affectées
        """
        requete = "UPDATE Bulletins SET fichier_pdf = %s WHERE id = %s"
        return executer_requete(requete, (fichier_pdf, bulletin_id))
    
    @staticmethod
    def generer_bulletin(etudiant_id, semestre, annee_academique, genere_par):
        """
        Génère un bulletin avec calcul automatique de la moyenne
        
        Args:
            etudiant_id (int): ID de l'étudiant
            semestre (str): Semestre
            annee_academique (str): Année académique
            genere_par (int): ID de l'utilisateur qui génère
        
        Returns:
            int: ID du bulletin créé
        """
        # Calculer la moyenne générale (seulement notes validées)
        moyenne_data = Note.calculer_moyenne_etudiant(etudiant_id, seulement_validees=True)
        moyenne_generale = moyenne_data['moyenne'] if moyenne_data and moyenne_data['moyenne'] else 0
        
        # Récupérer la filière de l'étudiant
        etudiant = Etudiant.obtenir_par_id(etudiant_id)
        if not etudiant:
            return None
        
        filiere_id = etudiant['filiere_id']
        
        # Créer le bulletin
        return Bulletin.creer(
            etudiant_id, 
            filiere_id, 
            semestre, 
            annee_academique, 
            genere_par, 
            moyenne_generale
        )

    @staticmethod
    def obtenir_tous():
        """
        Récupère tous les bulletins avec informations complètes

        Returns:
            list: Liste de tous les bulletins
        """
        requete = """
            SELECT b.*,
                   u_etud.matricule as etudiant_matricule, u_etud.nom as etudiant_nom, u_etud.prenom as etudiant_prenom,
                   f.nom_filiere, f.niveau,
                   u_gen.nom as genere_par_nom, u_gen.prenom as genere_par_prenom
            FROM Bulletins b
            JOIN Etudiants e ON b.etudiant_id = e.utilisateur_id
            JOIN Utilisateurs u_etud ON e.utilisateur_id = u_etud.id
            JOIN Filieres f ON b.filiere_id = f.id
            JOIN Utilisateurs u_gen ON b.genere_par = u_gen.id
            ORDER BY b.annee_academique DESC, b.semestre DESC, u_etud.nom
        """
        return executer_requete(requete, obtenir_resultats=True)


class ImportNote:
    """Modèle pour la table ImportNotes (historique des imports de notes)"""

    @staticmethod
    def creer(cours_id, filiere_id, utilisateur_id, fichier_nom, nb_lignes_importees, role_initiateur):
        """
        Crée un nouvel enregistrement d'import de notes

        Args:
            cours_id (int): ID du cours
            filiere_id (int): ID de la filière
            utilisateur_id (int): ID de l'utilisateur qui importe
            fichier_nom (str): Nom du fichier importé
            nb_lignes_importees (int): Nombre de lignes importées
            role_initiateur (str): Rôle de l'utilisateur

        Returns:
            int: ID de l'import créé
        """
        requete = """
            INSERT INTO ImportNotes (cours_id, filiere_id, utilisateur_id, fichier_nom, nb_lignes_importees, role_initiateur, date_import)
            VALUES (%s, %s, %s, %s, %s, %s, NOW())
            RETURNING id
        """
        params = (cours_id, filiere_id, utilisateur_id, fichier_nom, nb_lignes_importees, role_initiateur)
        result = executer_requete(requete, params, obtenir_resultats=True)
        return result[0]['id'] if result else None

    @staticmethod
    def obtenir_historique():
        """
        Récupère l'historique des imports de notes

        Returns:
            list: Liste des imports avec détails
        """
        requete = """
            SELECT i.*,
                   c.nom_cours,
                   f.nom_filiere,
                   u.nom as utilisateur_nom, u.prenom as utilisateur_prenom
            FROM ImportNotes i
            JOIN Cours c ON i.cours_id = c.id
            JOIN Filieres f ON i.filiere_id = f.id
            JOIN Utilisateurs u ON i.utilisateur_id = u.id
            ORDER BY i.date_import DESC
        """
        return executer_requete(requete, obtenir_resultats=True)




class AuditUsage:
    """Modèle pour la table UsageAudit (traçabilité des actions)"""
    
    @staticmethod
    def creer(user_id, action, meta=None, ip_address=None, user_agent=None):
        """
        Crée un enregistrement d'audit
        
        Args:
            user_id (int): ID de l'utilisateur
            action (str): Action effectuée (LOGIN, LOGOUT, CREATE_NOTE, VALIDATE_NOTE, etc.)
            meta (dict, optional): Métadonnées JSON
            ip_address (str, optional): Adresse IP
            user_agent (str, optional): User agent
        
        Returns:
            int: ID de l'enregistrement créé
        """
        import json
        meta_json = json.dumps(meta) if meta else None
        
        requete = """
            INSERT INTO UsageAudit (user_id, action, meta, ip_address, user_agent)
            VALUES (%s, %s, %s, %s, %s)
        """
        return executer_requete(requete, (user_id, action, meta_json, ip_address, user_agent))
    
    @staticmethod
    def obtenir_rapport_usage(date_debut=None, date_fin=None, user_id=None, action=None):
        """
        Génère un rapport d'utilisation
        
        Args:
            date_debut (str, optional): Date de début (YYYY-MM-DD)
            date_fin (str, optional): Date de fin (YYYY-MM-DD)
            user_id (int, optional): Filtrer par utilisateur
            action (str, optional): Filtrer par action
        
        Returns:
            list: Liste des enregistrements d'audit
        """
        requete = """
            SELECT a.*,
                   u.nom, u.prenom, u.matricule, u.role
            FROM UsageAudit a
            JOIN Utilisateurs u ON a.user_id = u.id
            WHERE 1=1
        """
        params = []
        
        if date_debut:
            requete += " AND DATE(a.created_at) >= %s"
            params.append(date_debut)
        
        if date_fin:
            requete += " AND DATE(a.created_at) <= %s"
            params.append(date_fin)
        
        if user_id:
            requete += " AND a.user_id = %s"
            params.append(user_id)
        
        if action:
            requete += " AND a.action = %s"
            params.append(action)
        
        requete += " ORDER BY a.created_at DESC"
        
        return executer_requete(requete, tuple(params) if params else None, obtenir_resultats=True)
    
    @staticmethod
    def obtenir_statistiques_utilisateur(user_id):
        """
        Obtient les statistiques d'utilisation d'un utilisateur
        
        Args:
            user_id (int): ID de l'utilisateur
        
        Returns:
            dict: Statistiques
        """
        requete = """
            SELECT 
                COUNT(*) as total_actions,
                COUNT(DISTINCT DATE(created_at)) as jours_actifs,
                MAX(created_at) as derniere_action,
                MIN(created_at) as premiere_action
            FROM UsageAudit
            WHERE user_id = %s
        """
        return executer_requete_unique(requete, (user_id,))
    
    @staticmethod
    def obtenir_actions_par_type(date_debut=None, date_fin=None):
        """
        Compte les actions par type
        
        Args:
            date_debut (str, optional): Date de début
            date_fin (str, optional): Date de fin
        
        Returns:
            list: Liste des actions avec compteurs
        """
        requete = """
            SELECT action, COUNT(*) as count
            FROM UsageAudit
            WHERE 1=1
        """
        params = []
        
        if date_debut:
            requete += " AND DATE(created_at) >= %s"
            params.append(date_debut)
        
        if date_fin:
            requete += " AND DATE(created_at) <= %s"
            params.append(date_fin)
        
        requete += " GROUP BY action ORDER BY count DESC"
        
        return executer_requete(requete, tuple(params) if params else None, obtenir_resultats=True)
