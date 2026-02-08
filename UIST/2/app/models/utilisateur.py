"""
Modèle Utilisateur et AuditUsage
"""
from app.db import executer_requete, executer_requete_unique
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class Utilisateur:
    """Classe représentant un utilisateur du système"""
    
    # Hiérarchie des rôles (du plus élevé au plus bas)
    HIERARCHIE_ROLES = {
        'SUPER_ADMIN': 5,
        'DIRECTEUR': 4,
        'GESTION_1': 3,
        'GESTION_2': 3,
        'GESTION_3': 3,
        'ENSEIGNANT': 2,
        'ETUDIANT': 1,
        'PARENT': 1
    }
    
    @staticmethod
    def creer(matricule, nom, prenom, email, mot_de_passe, role):
        """Crée un nouvel utilisateur"""
        mot_de_passe_hash = generate_password_hash(mot_de_passe)
        
        query = """
            INSERT INTO utilisateurs (matricule, nom, prenom, email, mot_de_passe, role)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        
        return executer_requete(query, (matricule, nom, prenom, email, mot_de_passe_hash, role))
    
    @staticmethod
    def obtenir_par_id(id_user):
        """Récupère un utilisateur par son ID"""
        query = "SELECT * FROM utilisateurs WHERE id_user = ?"
        return executer_requete_unique(query, (id_user,))
    
    @staticmethod
    def obtenir_par_matricule(matricule):
        """Récupère un utilisateur par son matricule"""
        query = "SELECT * FROM utilisateurs WHERE matricule = ?"
        return executer_requete_unique(query, (matricule,))
    
    @staticmethod
    def obtenir_par_email(email):
        """Récupère un utilisateur par son email"""
        query = "SELECT * FROM utilisateurs WHERE email = ?"
        return executer_requete_unique(query, (email,))
    
    @staticmethod
    def obtenir_tous(role=None):
        """Récupère tous les utilisateurs, optionnellement filtrés par rôle"""
        if role:
            query = "SELECT * FROM utilisateurs WHERE role = ? ORDER BY nom, prenom"
            return executer_requete(query, (role,), obtenir_resultats=True)
        else:
            query = "SELECT * FROM utilisateurs ORDER BY role, nom, prenom"
            return executer_requete(query, obtenir_resultats=True)
    
    @staticmethod
    def verifier_mot_de_passe(utilisateur, mot_de_passe):
        """Vérifie le mot de passe d'un utilisateur"""
        if not utilisateur:
            return False
        return check_password_hash(utilisateur['mot_de_passe'], mot_de_passe)
    
    @staticmethod
    def mettre_a_jour_derniere_connexion(id_user):
        """Met à jour la date de dernière connexion"""
        query = "UPDATE utilisateurs SET derniere_connexion = ? WHERE id_user = ?"
        executer_requete(query, (datetime.now(), id_user))
    
    @staticmethod
    def modifier(id_user, nom=None, prenom=None, email=None, role=None):
        """Modifie un utilisateur"""
        updates = []
        params = []
        
        if nom:
            updates.append("nom = ?")
            params.append(nom)
        if prenom:
            updates.append("prenom = ?")
            params.append(prenom)
        if email:
            updates.append("email = ?")
            params.append(email)
        if role:
            updates.append("role = ?")
            params.append(role)
        
        if not updates:
            return False
        
        params.append(id_user)
        query = f"UPDATE utilisateurs SET {', '.join(updates)} WHERE id_user = ?"
        
        return executer_requete(query, tuple(params)) > 0
    
    @staticmethod
    def changer_mot_de_passe(id_user, nouveau_mot_de_passe):
        """Change le mot de passe d'un utilisateur"""
        mot_de_passe_hash = generate_password_hash(nouveau_mot_de_passe)
        query = "UPDATE utilisateurs SET mot_de_passe = ? WHERE id_user = ?"
        return executer_requete(query, (mot_de_passe_hash, id_user)) > 0
    
    @staticmethod
    def desactiver(id_user):
        """Désactive un utilisateur"""
        query = "UPDATE utilisateurs SET est_actif = 0 WHERE id_user = ?"
        return executer_requete(query, (id_user,)) > 0
    
    @staticmethod
    def activer(id_user):
        """Active un utilisateur"""
        query = "UPDATE utilisateurs SET est_actif = 1 WHERE id_user = ?"
        return executer_requete(query, (id_user,)) > 0
    
    @staticmethod
    def supprimer(id_user):
        """Supprime un utilisateur"""
        query = "DELETE FROM utilisateurs WHERE id_user = ?"
        return executer_requete(query, (id_user,)) > 0
    
    @staticmethod
    def peut_gerer_role(role_gestionnaire, role_cible):
        """
        Vérifie si un rôle peut gérer un autre rôle selon la hiérarchie
        RG04 - Hiérarchie des Rôles
        """
        niveau_gestionnaire = Utilisateur.HIERARCHIE_ROLES.get(role_gestionnaire, 0)
        niveau_cible = Utilisateur.HIERARCHIE_ROLES.get(role_cible, 0)
        
        return niveau_gestionnaire > niveau_cible
    
    @staticmethod
    def compter_par_role():
        """Compte le nombre d'utilisateurs par rôle"""
        query = """
            SELECT role, COUNT(*) as nombre
            FROM utilisateurs
            GROUP BY role
            ORDER BY role
        """
        return executer_requete(query, obtenir_resultats=True)


class AuditUsage:
    """Classe pour la traçabilité des actions"""
    
    @staticmethod
    def creer(id_user, action, table_affectee=None, id_enregistrement=None, details=None, ip_address=None):
        """Enregistre une action dans l'audit"""
        query = """
            INSERT INTO audit_usage (id_user, action, table_affectee, id_enregistrement, details, ip_address)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        
        return executer_requete(query, (id_user, action, table_affectee, id_enregistrement, details, ip_address))
    
    @staticmethod
    def obtenir_tous(limit=100, offset=0):
        """Récupère les dernières actions d'audit"""
        query = """
            SELECT a.*, u.matricule, u.nom, u.prenom, u.role
            FROM audit_usage a
            LEFT JOIN utilisateurs u ON a.id_user = u.id_user
            ORDER BY a.date_action DESC
            LIMIT ? OFFSET ?
        """
        return executer_requete(query, (limit, offset), obtenir_resultats=True)
    
    @staticmethod
    def obtenir_par_utilisateur(id_user, limit=50):
        """Récupère les actions d'un utilisateur spécifique"""
        query = """
            SELECT * FROM audit_usage
            WHERE id_user = ?
            ORDER BY date_action DESC
            LIMIT ?
        """
        return executer_requete(query, (id_user, limit), obtenir_resultats=True)
    
    @staticmethod
    def obtenir_par_table(table_affectee, limit=50):
        """Récupère les actions sur une table spécifique"""
        query = """
            SELECT a.*, u.matricule, u.nom, u.prenom
            FROM audit_usage a
            LEFT JOIN utilisateurs u ON a.id_user = u.id_user
            WHERE a.table_affectee = ?
            ORDER BY a.date_action DESC
            LIMIT ?
        """
        return executer_requete(query, (table_affectee, limit), obtenir_resultats=True)
    
    @staticmethod
    def rechercher(date_debut=None, date_fin=None, action=None, id_user=None):
        """Recherche des actions d'audit avec filtres"""
        conditions = []
        params = []
        
        if date_debut:
            conditions.append("date_action >= ?")
            params.append(date_debut)
        
        if date_fin:
            conditions.append("date_action <= ?")
            params.append(date_fin)
        
        if action:
            conditions.append("action LIKE ?")
            params.append(f"%{action}%")
        
        if id_user:
            conditions.append("id_user = ?")
            params.append(id_user)
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        query = f"""
            SELECT a.*, u.matricule, u.nom, u.prenom, u.role
            FROM audit_usage a
            LEFT JOIN utilisateurs u ON a.id_user = u.id_user
            WHERE {where_clause}
            ORDER BY a.date_action DESC
            LIMIT 1000
        """
        
        return executer_requete(query, tuple(params), obtenir_resultats=True)