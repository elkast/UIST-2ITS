"""
Service de génération de matricules uniques
"""
from datetime import datetime
from app.db import executer_requete_unique

class MatriculeService:
    """Service pour générer des matricules uniques selon le rôle"""
    
    PREFIXES = {
        'SUPER_ADMIN': 'SA',
        'DIRECTEUR': 'DIR',
        'GESTION_1': 'G1',
        'GESTION_2': 'G2',
        'GESTION_3': 'G3',
        'ENSEIGNANT': 'ENS',
        'ETUDIANT': 'ETU',
        'PARENT': 'PAR'
    }
    
    @staticmethod
    def generer(role):
        """
        Génère un matricule unique selon le rôle
        
        Format: [PREFIX][ANNEE][NUMERO]
        Exemple: SA2025001, ETU2025042, ENS2025015
        
        Args:
            role (str): Le rôle de l'utilisateur
        
        Returns:
            str: Matricule unique
        """
        prefix = MatriculeService.PREFIXES.get(role, 'USR')
        annee = datetime.now().year
        
        # Trouver le dernier numéro pour ce rôle cette année
        query = """
            SELECT matricule
            FROM utilisateurs
            WHERE matricule LIKE ? AND role = ?
            ORDER BY matricule DESC
            LIMIT 1
        """
        
        pattern = f"{prefix}{annee}%"
        dernier = executer_requete_unique(query, (pattern, role))
        
        if dernier:
            # Extraire le numéro et incrémenter
            try:
                dernier_numero = int(dernier['matricule'][-3:])
                nouveau_numero = dernier_numero + 1
            except:
                nouveau_numero = 1
        else:
            nouveau_numero = 1
        
        # Formater avec padding de zéros
        matricule = f"{prefix}{annee}{nouveau_numero:03d}"
        
        return matricule
    
    @staticmethod
    def valider(matricule):
        """
        Valide le format d'un matricule
        
        Args:
            matricule (str): Matricule à valider
        
        Returns:
            bool: True si valide, False sinon
        """
        if not matricule or len(matricule) < 9:
            return False
        
        # Vérifier que le préfixe existe
        for prefix in MatriculeService.PREFIXES.values():
            if matricule.startswith(prefix):
                return True
        
        return False