"""
Modèles spécifiques pour le rôle Directeur
"""
from app.db import executer_requete, executer_requete_unique
from datetime import datetime

class Permission:
    """Gestion des permissions granulaires"""
    
    @staticmethod
    def obtenir_permissions_role(role):
        """Obtient les permissions pour un rôle"""
        permissions_map = {
            'SUPER_ADMIN': ['*'],
            'ADMIN': ['*'],
            'DIRECTEUR': [
                'create_user', 'edit_user', 'delete_user', 'view_users', 'manage_roles',
                'view_all_schedules', 'create_schedule', 'edit_schedule', 
                'delete_schedule', 'assign_teacher', 'manage_conflicts',
                'view_all_grades', 'validate_grades', 'edit_grades', 'export_grades',
                'schedule_exams', 'manage_exam_calendar',
                'send_announcements', 'manage_availability', 'view_all_messages'
            ],
            'GESTIONNAIRE_EXAMENS': [
                'view_all_grades', 'import_grades', 'export_grades', 
                'schedule_exams', 'manage_exam_calendar'
            ],
            'GESTIONNAIRE_PV': [
                'view_all_grades', 'generate_bulletins', 'validate_bulletins', 
                'publish_bulletins', 'export_grades'
            ],
        }
        return permissions_map.get(role, [])
    
    @staticmethod
    def verifier_permission(role, permission):
        """Vérifie si un rôle a une permission"""
        permissions = Permission.obtenir_permissions_role(role)
        return '*' in permissions or permission in permissions


class AssignationEnseignant:
    """Assignations enseignant-cours-filière"""
    
    @staticmethod
    def creer(enseignant_id, cours_id, filiere_id, niveau, annee_academique, assigne_par):
        """Crée une assignation"""
        requete = """
            INSERT INTO AssignationsEnseignants 
            (enseignant_id, cours_id, filiere_id, niveau, annee_academique, assigne_par, date_assignation)
            VALUES (%s, %s, %s, %s, %s, %s, NOW())
        """
        return executer_requete(requete, (enseignant_id, cours_id, filiere_id, niveau, annee_academique, assigne_par))
    
    @staticmethod
    def obtenir_toutes(filiere_id=None, niveau=None):
        """Récupère toutes les assignations"""
        requete = """
            SELECT a.*,
                   u_ens.nom as enseignant_nom, u_ens.prenom as enseignant_prenom,
                   c.nom_cours, f.nom_filiere
            FROM AssignationsEnseignants a
            JOIN Utilisateurs u_ens ON a.enseignant_id = u_ens.id
            JOIN Cours c ON a.cours_id = c.id
            JOIN Filieres f ON a.filiere_id = f.id
            WHERE 1=1
        """
        params = []
        
        if filiere_id:
            requete += " AND a.filiere_id = %s"
            params.append(filiere_id)
        
        if niveau:
            requete += " AND a.niveau = %s"
            params.append(niveau)
        
        return executer_requete(requete, tuple(params) if params else None, obtenir_resultats=True)


class DisponibiliteEnseignant:
    """Gestion des disponibilités enseignants"""
    
    @staticmethod
    def creer(enseignant_id, date_debut, date_fin, type_indisponibilite, motif, visible_etudiants=True):
        """Crée une disponibilité"""
        requete = """
            INSERT INTO DisponibilitesEnseignants 
            (enseignant_id, date_debut, date_fin, type_indisponibilite, motif, visible_etudiants, date_creation)
            VALUES (%s, %s, %s, %s, %s, %s, NOW())
        """
        return executer_requete(requete, (enseignant_id, date_debut, date_fin, type_indisponibilite, motif, visible_etudiants))
    
    @staticmethod
    def obtenir_visibles_etudiants(filiere_id=None):
        """Récupère les disponibilités visibles par étudiants"""
        requete = """
            SELECT d.*, u.nom as enseignant_nom, u.prenom as enseignant_prenom
            FROM DisponibilitesEnseignants d
            JOIN Utilisateurs u ON d.enseignant_id = u.id
            WHERE d.visible_etudiants = TRUE AND d.date_fin >= CURDATE()
            ORDER BY d.date_debut DESC
        """
        return executer_requete(requete, obtenir_resultats=True)


class ValidationNote:
    """Workflow de validation des notes"""
    
    @staticmethod
    def valider_note(note_id, valide_par, commentaire=''):
        """Valide une note"""
        requete = """
            UPDATE Notes 
            SET statut = 'VALIDÉ', valide_par = %s, date_validation = NOW(),
                commentaire_validation = %s
            WHERE id = %s AND statut = 'EN_ATTENTE_DIRECTEUR'
        """
        return executer_requete(requete, (valide_par, commentaire, note_id))
    
    @staticmethod
    def valider_lot(note_ids, valide_par):
        """Valide plusieurs notes"""
        if not note_ids:
            return 0
        placeholders = ','.join(['%s'] * len(note_ids))
        requete = f"""
            UPDATE Notes 
            SET statut = 'VALIDÉ', valide_par = %s, date_validation = NOW()
            WHERE id IN ({placeholders}) AND statut = 'EN_ATTENTE_DIRECTEUR'
        """
        return executer_requete(requete, tuple([valide_par] + note_ids))