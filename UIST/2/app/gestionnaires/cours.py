"""
Gestionnaire des Cours
Gère toutes les opérations liées aux cours, filières et salles
"""
from .base import GestionnaireBase
from app.db import executer_requete, executer_requete_unique


class GestionnaireCours(GestionnaireBase):
    """
    Gestionnaire pour les cours, filières et salles
    """
    
    # ============ GESTION DES FILIÈRES ============
    
    @staticmethod
    def lister_filieres(niveau=None, page=1):
        """
        Liste toutes les filières
        
        Args:
            niveau (str): Filtrer par niveau (L1, L2, L3, M1, M2)
            page (int): Numéro de page
            
        Returns:
            dict: Résultats paginés
        """
        requete = """
            SELECT f.*,
                   COUNT(DISTINCT e.id_etudiant) as nombre_etudiants,
                   COUNT(DISTINCT c.id_cours) as nombre_cours
            FROM filieres f
            LEFT JOIN etudiants e ON f.id_filiere = e.id_filiere
            LEFT JOIN cours c ON f.id_filiere = c.id_filiere
            WHERE 1=1
        """
        parametres = []
        
        if niveau:
            requete += " AND f.niveau = ?"
            parametres.append(niveau)
        
        requete += " GROUP BY f.id_filiere ORDER BY f.niveau, f.nom_filiere"
        
        resultats = executer_requete(requete, tuple(parametres), obtenir_resultats=True)
        
        return GestionnaireBase.paginer_resultats(resultats or [], page, par_page=20)
    
    @staticmethod
    def obtenir_filiere(filiere_id):
        """
        Récupère une filière par son ID
        
        Args:
            filiere_id (int): ID de la filière
            
        Returns:
            dict: Informations de la filière
        """
        requete = """
            SELECT f.*,
                   COUNT(DISTINCT e.id_etudiant) as nombre_etudiants,
                   COUNT(DISTINCT c.id_cours) as nombre_cours
            FROM filieres f
            LEFT JOIN etudiants e ON f.id_filiere = e.id_filiere
            LEFT JOIN cours c ON f.id_filiere = c.id_filiere
            WHERE f.id_filiere = ?
            GROUP BY f.id_filiere
        """
        return executer_requete_unique(requete, (filiere_id,))
    
    @staticmethod
    def creer_filiere(donnees):
        """
        Crée une nouvelle filière
        
        Args:
            donnees (dict): Données de la filière
                - code_filiere (str)
                - nom_filiere (str)
                - niveau (str)
                - effectif_prevu (int)
                
        Returns:
            tuple: (success: bool, message: str, filiere_id: int)
        """
        try:
            requete = """
                INSERT INTO filieres (code_filiere, nom_filiere, niveau, effectif_prevu)
                VALUES (?, ?, ?, ?)
            """
            filiere_id = executer_requete(requete, (
                donnees['code_filiere'],
                donnees['nom_filiere'],
                donnees['niveau'],
                donnees.get('effectif_prevu', 0)
            ))
            
            if filiere_id:
                GestionnaireBase.enregistrer_audit(
                    'creation_filiere',
                    'filieres',
                    filiere_id,
                    f"Création filière: {donnees['nom_filiere']}"
                )
                return True, "Filière créée avec succès", filiere_id
            
            return False, "Erreur lors de la création", None
            
        except Exception as e:
            print(f"❌ Erreur création filière: {e}")
            return False, f"Erreur: {str(e)}", None
    
    # ============ GESTION DES COURS ============
    
    @staticmethod
    def lister_cours(filiere_id=None, page=1):
        """
        Liste tous les cours
        
        Args:
            filiere_id (int): Filtrer par filière
            page (int): Numéro de page
            
        Returns:
            dict: Résultats paginés
        """
        requete = """
            SELECT c.*, f.nom_filiere, f.niveau
            FROM cours c
            LEFT JOIN filieres f ON c.id_filiere = f.id_filiere
            WHERE 1=1
        """
        parametres = []
        
        if filiere_id:
            requete += " AND c.id_filiere = ?"
            parametres.append(filiere_id)
        
        requete += " ORDER BY f.niveau, c.libelle"
        
        resultats = executer_requete(requete, tuple(parametres), obtenir_resultats=True)
        
        return GestionnaireBase.paginer_resultats(resultats or [], page, par_page=20)
    
    @staticmethod
    def creer_cours(donnees):
        """
        Crée un nouveau cours
        
        Args:
            donnees (dict): Données du cours
                - code_cours (str)
                - libelle (str)
                - credit (int)
                - id_filiere (int)
                - coefficient (float)
                
        Returns:
            tuple: (success: bool, message: str, cours_id: int)
        """
        try:
            requete = """
                INSERT INTO cours (code_cours, libelle, credit, id_filiere, coefficient)
                VALUES (?, ?, ?, ?, ?)
            """
            cours_id = executer_requete(requete, (
                donnees['code_cours'],
                donnees['libelle'],
                donnees.get('credit', 1),
                donnees['id_filiere'],
                donnees.get('coefficient', 1.0)
            ))
            
            if cours_id:
                GestionnaireBase.enregistrer_audit(
                    'creation_cours',
                    'cours',
                    cours_id,
                    f"Création cours: {donnees['libelle']}"
                )
                return True, "Cours créé avec succès", cours_id
            
            return False, "Erreur lors de la création", None
            
        except Exception as e:
            print(f"❌ Erreur création cours: {e}")
            return False, f"Erreur: {str(e)}", None
    
    # ============ GESTION DES SALLES ============
    
    @staticmethod
    def lister_salles(batiment=None, page=1):
        """
        Liste toutes les salles
        
        Args:
            batiment (str): Filtrer par bâtiment
            page (int): Numéro de page
            
        Returns:
            dict: Résultats paginés
        """
        requete = "SELECT * FROM salles WHERE 1=1"
        parametres = []
        
        if batiment:
            requete += " AND batiment = ?"
            parametres.append(batiment)
        
        requete += " ORDER BY batiment, nom_salle"
        
        resultats = executer_requete(requete, tuple(parametres), obtenir_resultats=True)
        
        return GestionnaireBase.paginer_resultats(resultats or [], page, par_page=20)
    
    @staticmethod
    def creer_salle(donnees):
        """
        Crée une nouvelle salle
        
        Args:
            donnees (dict): Données de la salle
                - nom_salle (str)
                - capacite (int)
                - equipements (str)
                - batiment (str)
                
        Returns:
            tuple: (success: bool, message: str, salle_id: int)
        """
        try:
            requete = """
                INSERT INTO salles (nom_salle, capacite, equipements, batiment, est_active)
                VALUES (?, ?, ?, ?, 1)
            """
            salle_id = executer_requete(requete, (
                donnees['nom_salle'],
                donnees['capacite'],
                donnees.get('equipements', ''),
                donnees.get('batiment', '')
            ))
            
            if salle_id:
                GestionnaireBase.enregistrer_audit(
                    'creation_salle',
                    'salles',
                    salle_id,
                    f"Création salle: {donnees['nom_salle']}"
                )
                return True, "Salle créée avec succès", salle_id
            
            return False, "Erreur lors de la création", None
            
        except Exception as e:
            print(f"❌ Erreur création salle: {e}")
            return False, f"Erreur: {str(e)}", None