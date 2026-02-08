"""
Gestionnaire des Utilisateurs
Gère toutes les opérations liées aux utilisateurs
"""
from .base import GestionnaireBase
from app.db import executer_requete, executer_requete_unique
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


class GestionnaireUtilisateurs(GestionnaireBase):
    """
    Gestionnaire pour les opérations sur les utilisateurs
    """
    
    @staticmethod
    def lister_utilisateurs(role=None, recherche=None, page=1):
        """
        Liste les utilisateurs avec filtres optionnels
        
        Args:
            role (str): Filtrer par rôle
            recherche (str): Rechercher par nom/prénom/matricule
            page (int): Numéro de page
            
        Returns:
            dict: Résultats paginés
        """
        requete = """
            SELECT u.*,
                   e.id_etudiant, e.id_filiere,
                   f.nom_filiere,
                   ens.id_enseignant, ens.specialite,
                   p.id_parent
            FROM utilisateurs u
            LEFT JOIN etudiants e ON u.id_user = e.id_user
            LEFT JOIN filieres f ON e.id_filiere = f.id_filiere
            LEFT JOIN enseignants ens ON u.id_user = ens.id_user
            LEFT JOIN parents p ON u.id_user = p.id_user
            WHERE 1=1
        """
        parametres = []
        
        # Filtre par rôle
        if role:
            requete += " AND u.role = ?"
            parametres.append(role)
        
        # Filtre par recherche
        if recherche:
            requete += """ AND (
                u.nom LIKE ? OR 
                u.prenom LIKE ? OR 
                u.matricule LIKE ? OR
                u.email LIKE ?
            )"""
            terme = f"%{recherche}%"
            parametres.extend([terme, terme, terme, terme])
        
        requete += " ORDER BY u.nom, u.prenom"
        
        resultats = executer_requete(requete, tuple(parametres), obtenir_resultats=True)
        
        # Pagination
        return GestionnaireBase.paginer_resultats(resultats or [], page, par_page=20)
    
    @staticmethod
    def obtenir_utilisateur(utilisateur_id):
        """
        Récupère les détails d'un utilisateur
        
        Args:
            utilisateur_id (int): ID de l'utilisateur
            
        Returns:
            dict: Informations de l'utilisateur
        """
        requete = """
            SELECT u.*,
                   e.id_etudiant, e.id_filiere, e.date_naissance as etudiant_date_naissance,
                   f.nom_filiere, f.niveau,
                   ens.id_enseignant, ens.specialite, ens.telephone as enseignant_telephone,
                   p.id_parent
            FROM utilisateurs u
            LEFT JOIN etudiants e ON u.id_user = e.id_user
            LEFT JOIN filieres f ON e.id_filiere = f.id_filiere
            LEFT JOIN enseignants ens ON u.id_user = ens.id_user
            LEFT JOIN parents p ON u.id_user = p.id_user
            WHERE u.id_user = ?
        """
        return executer_requete_unique(requete, (utilisateur_id,))
    
    @staticmethod
    def creer_utilisateur(donnees):
        """
        Crée un nouvel utilisateur
        
        Args:
            donnees (dict): Données de l'utilisateur
                - nom (str)
                - prenom (str)
                - email (str)
                - role (str)
                - mot_de_passe (str)
                - matricule (str, optionnel)
                - filiere_id (int, optionnel pour étudiant)
                - specialite (str, optionnel pour enseignant)
                
        Returns:
            tuple: (success: bool, message: str, utilisateur_id: int)
        """
        try:
            # Génération du matricule si non fourni
            matricule = donnees.get('matricule')
            if not matricule:
                matricule = GestionnaireUtilisateurs._generer_matricule(donnees['role'])
            
            # Hash du mot de passe
            hash_mdp = generate_password_hash(donnees['mot_de_passe'])
            
            # Insertion dans la table utilisateurs
            requete_user = """
                INSERT INTO utilisateurs 
                (matricule, nom, prenom, email, mot_de_passe, role, est_actif)
                VALUES (?, ?, ?, ?, ?, ?, 1)
            """
            utilisateur_id = executer_requete(requete_user, (
                matricule,
                donnees['nom'],
                donnees['prenom'],
                donnees['email'],
                hash_mdp,
                donnees['role']
            ))
            
            if not utilisateur_id:
                return False, "Erreur lors de la création de l'utilisateur", None
            
            # Créer les profils spécifiques selon le rôle
            role = donnees['role'].upper()
            
            if role == 'ETUDIANT':
                if 'filiere_id' not in donnees:
                    return False, "La filière est obligatoire pour un étudiant", None
                
                requete_etudiant = """
                    INSERT INTO etudiants (id_user, id_filiere, date_naissance, adresse)
                    VALUES (?, ?, ?, ?)
                """
                executer_requete(requete_etudiant, (
                    utilisateur_id,
                    donnees['filiere_id'],
                    donnees.get('date_naissance'),
                    donnees.get('adresse', '')
                ))
            
            elif role == 'ENSEIGNANT':
                requete_enseignant = """
                    INSERT INTO enseignants (id_user, specialite, telephone)
                    VALUES (?, ?, ?)
                """
                executer_requete(requete_enseignant, (
                    utilisateur_id,
                    donnees.get('specialite', ''),
                    donnees.get('telephone', '')
                ))
            
            elif role == 'PARENT':
                requete_parent = """
                    INSERT INTO parents (id_user, telephone, adresse)
                    VALUES (?, ?, ?)
                """
                executer_requete(requete_parent, (
                    utilisateur_id,
                    donnees.get('telephone', ''),
                    donnees.get('adresse', '')
                ))
            
            # Audit
            GestionnaireBase.enregistrer_audit(
                'creation_utilisateur',
                'utilisateurs',
                utilisateur_id,
                f"Création utilisateur: {matricule} - {donnees['nom']} {donnees['prenom']}"
            )
            
            return True, f"Utilisateur créé avec succès (Matricule: {matricule})", utilisateur_id
            
        except Exception as e:
            print(f"❌ Erreur création utilisateur: {e}")
            return False, f"Erreur: {str(e)}", None
    
    @staticmethod
    def modifier_utilisateur(utilisateur_id, donnees):
        """
        Modifie un utilisateur existant
        
        Args:
            utilisateur_id (int): ID de l'utilisateur
            donnees (dict): Nouvelles données
            
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            # Mise à jour utilisateur
            requete_user = """
                UPDATE utilisateurs
                SET nom = ?, prenom = ?, email = ?
                WHERE id_user = ?
            """
            executer_requete(requete_user, (
                donnees['nom'],
                donnees['prenom'],
                donnees['email'],
                utilisateur_id
            ))
            
            # Mise à jour du mot de passe si fourni
            if donnees.get('mot_de_passe'):
                hash_mdp = generate_password_hash(donnees['mot_de_passe'])
                requete_mdp = "UPDATE utilisateurs SET mot_de_passe = ? WHERE id_user = ?"
                executer_requete(requete_mdp, (hash_mdp, utilisateur_id))
            
            # Mise à jour profils spécifiques
            utilisateur = GestionnaireUtilisateurs.obtenir_utilisateur(utilisateur_id)
            role = utilisateur['role'].upper()
            
            if role == 'ETUDIANT' and 'filiere_id' in donnees:
                requete_etudiant = """
                    UPDATE etudiants
                    SET id_filiere = ?, date_naissance = ?, adresse = ?
                    WHERE id_user = ?
                """
                executer_requete(requete_etudiant, (
                    donnees['filiere_id'],
                    donnees.get('date_naissance'),
                    donnees.get('adresse', ''),
                    utilisateur_id
                ))
            
            elif role == 'ENSEIGNANT':
                requete_enseignant = """
                    UPDATE enseignants
                    SET specialite = ?, telephone = ?
                    WHERE id_user = ?
                """
                executer_requete(requete_enseignant, (
                    donnees.get('specialite', ''),
                    donnees.get('telephone', ''),
                    utilisateur_id
                ))
            
            # Audit
            GestionnaireBase.enregistrer_audit(
                'modification_utilisateur',
                'utilisateurs',
                utilisateur_id,
                f"Modification: {donnees['nom']} {donnees['prenom']}"
            )
            
            return True, "Utilisateur modifié avec succès"
            
        except Exception as e:
            print(f"❌ Erreur modification: {e}")
            return False, f"Erreur: {str(e)}"
    
    @staticmethod
    def activer_desactiver(utilisateur_id, actif=True):
        """
        Active ou désactive un utilisateur
        
        Args:
            utilisateur_id (int): ID de l'utilisateur
            actif (bool): True pour activer, False pour désactiver
            
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            requete = "UPDATE utilisateurs SET est_actif = ? WHERE id_user = ?"
            executer_requete(requete, (1 if actif else 0, utilisateur_id))
            
            action = 'activation' if actif else 'desactivation'
            GestionnaireBase.enregistrer_audit(
                f'{action}_utilisateur',
                'utilisateurs',
                utilisateur_id
            )
            
            message = "Utilisateur activé" if actif else "Utilisateur désactivé"
            return True, message
            
        except Exception as e:
            return False, f"Erreur: {str(e)}"
    
    @staticmethod
    def _generer_matricule(role):
        """
        Génère un matricule unique au format UIST-YYYY-XXXXX
        
        Args:
            role (str): Rôle de l'utilisateur
            
        Returns:
            str: Matricule généré
        """
        annee = datetime.now().year
        
        # Compter les utilisateurs de ce rôle cette année
        requete = """
            SELECT COUNT(*) as count 
            FROM utilisateurs 
            WHERE matricule LIKE ? AND role = ?
        """
        resultat = executer_requete_unique(requete, (f"UIST-{annee}-%", role))
        count = resultat['count'] if resultat else 0
        
        # Format: UIST-2025-00001
        numero = str(count + 1).zfill(5)
        return f"UIST-{annee}-{numero}"
    
    @staticmethod
    def obtenir_statistiques():
        """
        Récupère les statistiques des utilisateurs
        
        Returns:
            dict: Statistiques par rôle
        """
        requete = """
            SELECT 
                role,
                COUNT(*) as total,
                SUM(CASE WHEN est_actif = 1 THEN 1 ELSE 0 END) as actifs,
                SUM(CASE WHEN est_actif = 0 THEN 1 ELSE 0 END) as inactifs
            FROM utilisateurs
            GROUP BY role
        """
        resultats = executer_requete(requete, obtenir_resultats=True)
        
        stats = {}
        for row in resultats or []:
            stats[row['role']] = {
                'total': row['total'],
                'actifs': row['actifs'],
                'inactifs': row['inactifs']
            }
        
        return stats