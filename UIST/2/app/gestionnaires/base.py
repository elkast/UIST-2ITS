"""
Gestionnaire de Base
Classe mère pour tous les gestionnaires avec fonctionnalités communes
"""
from flask import session, flash, request
from app.db import executer_requete, executer_requete_unique


class GestionnaireBase:
    """
    Classe de base pour tous les gestionnaires
    Fournit des méthodes utilitaires communes
    """
    
    @staticmethod
    def obtenir_utilisateur_courant():
        """
        Récupère l'utilisateur actuellement connecté
        
        Returns:
            dict: Informations de l'utilisateur ou None
        """
        utilisateur_id = session.get('utilisateur_id')
        if not utilisateur_id:
            return None
            
        requete = "SELECT * FROM utilisateurs WHERE id_user = ?"
        return executer_requete_unique(requete, (utilisateur_id,))
    
    @staticmethod
    def obtenir_role_courant():
        """
        Récupère le rôle de l'utilisateur courant
        
        Returns:
            str: Rôle de l'utilisateur
        """
        return session.get('role', '')
    
    @staticmethod
    def verifier_permission(roles_autorises):
        """
        Vérifie si l'utilisateur a la permission requise
        
        Args:
            roles_autorises (list): Liste des rôles autorisés
            
        Returns:
            bool: True si autorisé, False sinon
        """
        role_courant = GestionnaireBase.obtenir_role_courant()
        return role_courant in roles_autorises
    
    @staticmethod
    def enregistrer_audit(action, table_affectee=None, id_enregistrement=None, details=None):
        """
        Enregistre une action dans l'audit
        
        Args:
            action (str): Description de l'action
            table_affectee (str): Table concernée
            id_enregistrement (int): ID de l'enregistrement
            details (str): Détails supplémentaires
        """
        try:
            utilisateur_id = session.get('utilisateur_id')
            ip_address = request.remote_addr
            
            requete = """
                INSERT INTO audit_usage 
                (id_user, action, table_affectee, id_enregistrement, details, ip_address)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            executer_requete(requete, (
                utilisateur_id, action, table_affectee, 
                id_enregistrement, details, ip_address
            ))
        except Exception as e:
            print(f"❌ Erreur audit: {e}")
    
    @staticmethod
    def afficher_message(message, categorie='info'):
        """
        Affiche un message flash à l'utilisateur
        
        Args:
            message (str): Message à afficher
            categorie (str): Type de message (success, danger, warning, info)
        """
        flash(message, categorie)
    
    @staticmethod
    def paginer_resultats(resultats, page=1, par_page=20):
        """
        Pagine une liste de résultats
        
        Args:
            resultats (list): Liste complète des résultats
            page (int): Numéro de page (commence à 1)
            par_page (int): Nombre d'éléments par page
            
        Returns:
            dict: Dictionnaire avec résultats paginés et métadonnées
        """
        total = len(resultats)
        total_pages = (total + par_page - 1) // par_page  # Division avec arrondi supérieur
        
        debut = (page - 1) * par_page
        fin = debut + par_page
        
        return {
            'elements': resultats[debut:fin],
            'page_courante': page,
            'total_pages': total_pages,
            'total_elements': total,
            'a_page_precedente': page > 1,
            'a_page_suivante': page < total_pages
        }