"""
Modèles étendus pour UIST-2ITS
Nouvelles tables: Notifications, AuditUsage, Bulletins, ImportNotes, Signalements
"""
from app.db import executer_requete, executer_requete_unique
from datetime import datetime
import json


class Notification:
    """Modèle pour la table Notifications"""
    
    @staticmethod
    def creer(destinataire_id, type_notification, titre, message, priorite='normale', lien_action=None, metadata=None):
        """
        Crée une nouvelle notification
        
        Args:
            destinataire_id (int): ID de l'utilisateur destinataire
            type_notification (str): Type de notification
            titre (str): Titre de la notification
            message (str): Contenu du message
            priorite (str): Priorité (basse, normale, haute, critique)
            lien_action (str): URL d'action optionnelle
            metadata (dict): Métadonnées JSON optionnelles
            
        Returns:
            int: ID de la notification créée
        """
        metadata_json = json.dumps(metadata) if metadata else None
        
        requete = """
            INSERT INTO Notifications 
            (destinataire_id, type_notification, titre, message, priorite, lien_action, metadata)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        return executer_requete(requete, (
            destinataire_id, type_notification, titre, message, 
            priorite, lien_action, metadata_json
        ))
    
    @staticmethod
    def obtenir_non_lues(utilisateur_id, limit=50):
        """
        Récupère les notifications non lues d'un utilisateur
        
        Args:
            utilisateur_id (int): ID de l'utilisateur
            limit (int): Nombre maximum de notifications
            
        Returns:
            list: Liste des notifications non lues
        """
        requete = """
            SELECT * FROM Notifications
            WHERE destinataire_id = %s AND is_read = FALSE
            ORDER BY created_at DESC
            LIMIT %s
        """
        return executer_requete(requete, (utilisateur_id, limit), obtenir_resultats=True)
    
    @staticmethod
    def compter_non_lues(utilisateur_id):
        """
        Compte les notifications non lues
        
        Args:
            utilisateur_id (int): ID de l'utilisateur
            
        Returns:
            int: Nombre de notifications non lues
        """
        requete = """
            SELECT COUNT(*) as count 
            FROM Notifications
            WHERE destinataire_id = %s AND is_read = FALSE
        """
        result = executer_requete_unique(requete, (utilisateur_id,))
        return result['count'] if result else 0
    
    @staticmethod
    def marquer_comme_lue(notification_id, utilisateur_id):
        """
        Marque une notification comme lue
        
        Args:
            notification_id (int): ID de la notification
            utilisateur_id (int): ID de l'utilisateur (vérification)
            
        Returns:
            int: Nombre de lignes affectées
        """
        requete = """
            UPDATE Notifications 
            SET is_read = TRUE, read_at = NOW()
            WHERE id = %s AND destinataire_id = %s
        """
        return executer_requete(requete, (notification_id, utilisateur_id))
    
    @staticmethod
    def marquer_toutes_comme_lues(utilisateur_id):
        """
        Marque toutes les notifications d'un utilisateur comme lues
        
        Args:
            utilisateur_id (int): ID de l'utilisateur
            
        Returns:
            int: Nombre de lignes affectées
        """
        requete = """
            UPDATE Notifications 
            SET is_read = TRUE, read_at = NOW()
            WHERE destinataire_id = %s AND is_read = FALSE
        """
        return executer_requete(requete, (utilisateur_id,))
    
    @staticmethod
    def obtenir_recentes(utilisateur_id, limit=20):
        """
        Récupère les notifications récentes (lues et non lues)
        
        Args:
            utilisateur_id (int): ID de l'utilisateur
            limit (int): Nombre maximum de notifications
            
        Returns:
            list: Liste des notifications récentes
        """
        requete = """
            SELECT * FROM Notifications
            WHERE destinataire_id = %s
            ORDER BY created_at DESC
            LIMIT %s
        """
        return executer_requete(requete, (utilisateur_id, limit), obtenir_resultats=True)


class AuditUsage:
    """Modèle pour la table AuditUsage (logs d'audit)"""
    
    @staticmethod
    def creer(user_id, action, description=None, ip_address=None, meta=None):
        """
        Crée un log d'audit
        
        Args:
            user_id (int): ID de l'utilisateur
            action (str): Action effectuée
            description (str): Description de l'action
            ip_address (str): Adresse IP
            meta (dict): Métadonnées JSON
            
        Returns:
            int: ID du log créé
        """
        meta_json = json.dumps(meta) if meta else None
        
        requete = """
            INSERT INTO AuditUsage 
            (user_id, action, description, ip_address, meta)
            VALUES (%s, %s, %s, %s, %s)
        """
        return executer_requete(requete, (user_id, action, description, ip_address, meta_json))
    
    @staticmethod
    def obtenir_logs_utilisateur(user_id, limit=100):
        """
        Récupère les logs d'un utilisateur
        
        Args:
            user_id (int): ID de l'utilisateur
            limit (int): Nombre maximum de logs
            
        Returns:
            list: Liste des logs
        """
        requete = """
            SELECT * FROM AuditUsage
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT %s
        """
        return executer_requete(requete, (user_id, limit), obtenir_resultats=True)
    
    @staticmethod
    def obtenir_logs_recents(limit=100):
        """
        Récupère les logs récents du système
        
        Args:
            limit (int): Nombre maximum de logs
            
        Returns:
            list: Liste des logs récents
        """
        requete = """
            SELECT a.*, u.matricule, u.nom, u.prenom, u.role
            FROM AuditUsage a
            LEFT JOIN Utilisateurs u ON a.user_id = u.id
            ORDER BY a.created_at DESC
            LIMIT %s
        """
        return executer_requete(requete, (limit,), obtenir_resultats=True)
    
    @staticmethod
    def statistiques_actions(date_debut=None, date_fin=None):
        """
        Statistiques sur les actions effectuées
        
        Args:
            date_debut (str): Date de début (YYYY-MM-DD)
            date_fin (str): Date de fin (YYYY-MM-DD)
            
        Returns:
            list: Statistiques par action
        """
        requete = "SELECT action, COUNT(*) as count FROM AuditUsage"
        params = []
        
        if date_debut and date_fin:
            requete += " WHERE created_at BETWEEN %s AND %s"
            params = [date_debut, date_fin]
        elif date_debut:
            requete += " WHERE created_at >= %s"
            params = [date_debut]
        elif date_fin:
            requete += " WHERE created_at <= %s"
            params = [date_fin]
        
        requete += " GROUP BY action ORDER BY count DESC"
        
        return executer_requete(requete, tuple(params) if params else None, obtenir_resultats=True)
    
    @staticmethod
    def obtenir_utilisateurs_actifs_recents(minutes=30):
        """
        Récupère les utilisateurs actifs dans les X dernières minutes
        
        Args:
            minutes (int): Nombre de minutes
            
        Returns:
            list: Liste des utilisateurs actifs
        """
        requete = """
            SELECT DISTINCT
                u.id, u.matricule, u.nom, u.prenom, u.role,
                MAX(a.created_at) as derniere_activite
            FROM AuditUsage a
            JOIN Utilisateurs u ON a.user_id = u.id
            WHERE a.created_at >= DATE_SUB(NOW(), INTERVAL %s MINUTE)
            GROUP BY u.id, u.matricule, u.nom, u.prenom, u.role
            ORDER BY derniere_activite DESC
        """
        return executer_requete(requete, (minutes,), obtenir_resultats=True)


class Bulletin:
    """Modèle pour la table Bulletins"""
    
    @staticmethod
    def creer(etudiant_id, filiere_id, semestre, annee_academique, genere_par, 
              moyenne_generale, rang, total_etudiants, appreciation=None, fichier_pdf=None):
        """
        Crée un nouveau bulletin
        
        Args:
            etudiant_id (int): ID de l'étudiant
            filiere_id (int): ID de la filière
            semestre (str): Semestre (S1, S2, etc.)
            annee_academique (str): Année académique
            genere_par (int): ID de l'utilisateur qui génère
            moyenne_generale (float): Moyenne générale
            rang (int): Classement
            total_etudiants (int): Total d'étudiants
            appreciation (str): Appréciation
            fichier_pdf (str): Nom du fichier PDF
            
        Returns:
            int: ID du bulletin créé
        """
        requete = """
            INSERT INTO Bulletins 
            (etudiant_id, filiere_id, semestre, annee_academique, genere_par,
             moyenne_generale, rang, total_etudiants, appreciation, fichier_pdf, statut)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'TERMINE')
        """
        return executer_requete(requete, (
            etudiant_id, filiere_id, semestre, annee_academique, genere_par,
            moyenne_generale, rang, total_etudiants, appreciation, fichier_pdf
        ))
    
    @staticmethod
    def obtenir_tous(limit=100):
        """
        Récupère tous les bulletins
        
        Args:
            limit (int): Nombre maximum de bulletins
            
        Returns:
            list: Liste des bulletins
        """
        requete = """
            SELECT b.*, 
                   u.matricule as etudiant_matricule,
                   u.nom as etudiant_nom,
                   u.prenom as etudiant_prenom,
                   f.nom_filiere,
                   f.niveau
            FROM Bulletins b
            JOIN Utilisateurs u ON b.etudiant_id = u.id
            JOIN Filieres f ON b.filiere_id = f.id
            ORDER BY b.created_at DESC
            LIMIT %s
        """
        return executer_requete(requete, (limit,), obtenir_resultats=True)
    
    @staticmethod
    def obtenir_par_etudiant(etudiant_id):
        """
        Récupère les bulletins d'un étudiant
        
        Args:
            etudiant_id (int): ID de l'étudiant
            
        Returns:
            list: Liste des bulletins de l'étudiant
        """
        requete = """
            SELECT b.*, f.nom_filiere, f.niveau
            FROM Bulletins b
            JOIN Filieres f ON b.filiere_id = f.id
            WHERE b.etudiant_id = %s
            ORDER BY b.annee_academique DESC, b.semestre DESC
        """
        return executer_requete(requete, (etudiant_id,), obtenir_resultats=True)
    
    @staticmethod
    def obtenir_par_filiere(filiere_id, semestre=None, annee_academique=None):
        """
        Récupère les bulletins d'une filière
        
        Args:
            filiere_id (int): ID de la filière
            semestre (str): Semestre (optionnel)
            annee_academique (str): Année académique (optionnel)
            
        Returns:
            list: Liste des bulletins de la filière
        """
        requete = """
            SELECT b.*,
                   u.matricule as etudiant_matricule,
                   u.nom as etudiant_nom,
                   u.prenom as etudiant_prenom
            FROM Bulletins b
            JOIN Utilisateurs u ON b.etudiant_id = u.id
            WHERE b.filiere_id = %s
        """
        params = [filiere_id]
        
        if semestre:
            requete += " AND b.semestre = %s"
            params.append(semestre)
        
        if annee_academique:
            requete += " AND b.annee_academique = %s"
            params.append(annee_academique)
        
        requete += " ORDER BY b.rang ASC"
        
        return executer_requete(requete, tuple(params), obtenir_resultats=True)
    
    @staticmethod
    def statistiques_filiere(filiere_id, semestre, annee_academique):
        """
        Statistiques de bulletins pour une filière
        
        Args:
            filiere_id (int): ID de la filière
            semestre (str): Semestre
            annee_academique (str): Année académique
            
        Returns:
            dict: Statistiques
        """
        requete = """
            SELECT 
                COUNT(*) as nb_bulletins,
                ROUND(AVG(moyenne_generale), 2) as moyenne_filiere,
                MIN(moyenne_generale) as note_min,
                MAX(moyenne_generale) as note_max,
                COUNT(CASE WHEN moyenne_generale >= 10 THEN 1 END) as nb_reussis,
                ROUND(COUNT(CASE WHEN moyenne_generale >= 10 THEN 1 END) * 100.0 / COUNT(*), 2) as taux_reussite
            FROM Bulletins
            WHERE filiere_id = %s AND semestre = %s AND annee_academique = %s
        """
        return executer_requete_unique(requete, (filiere_id, semestre, annee_academique))


class ImportNote:
    """Modèle pour la table ImportNotes"""
    
    @staticmethod
    def creer(cours_id, filiere_id, importeur_id, fichier_nom, nombre_notes=0, role_initiateur=None):
        """
        Crée un enregistrement d'import
        
        Args:
            cours_id (int): ID du cours
            filiere_id (int): ID de la filière
            importeur_id (int): ID de l'importeur
            fichier_nom (str): Nom du fichier
            nombre_notes (int): Nombre de notes importées
            role_initiateur (str): Rôle de l'initiateur
            
        Returns:
            int: ID de l'import créé
        """
        requete = """
            INSERT INTO ImportNotes 
            (cours_id, filiere_id, importeur_id, fichier_nom, lignes_succes, role_initiateur, statut)
            VALUES (%s, %s, %s, %s, %s, %s, 'TERMINE')
        """
        return executer_requete(requete, (
            cours_id, filiere_id, importeur_id, fichier_nom, nombre_notes, role_initiateur
        ))
    
    @staticmethod
    def mettre_a_jour_statut(import_id, lignes_totales, lignes_succes, lignes_erreurs, details_erreurs=None):
        """
        Met à jour le statut d'un import
        
        Args:
            import_id (int): ID de l'import
            lignes_totales (int): Nombre total de lignes
            lignes_succes (int): Nombre de lignes réussies
            lignes_erreurs (int): Nombre de lignes en erreur
            details_erreurs (str): Détails des erreurs
            
        Returns:
            int: Nombre de lignes affectées
        """
        statut = 'TERMINE' if lignes_erreurs == 0 else 'ERREUR'
        
        requete = """
            UPDATE ImportNotes 
            SET lignes_totales = %s,
                lignes_succes = %s,
                lignes_erreurs = %s,
                details_erreurs = %s,
                statut = %s,
                completed_at = NOW()
            WHERE id = %s
        """
        return executer_requete(requete, (
            lignes_totales, lignes_succes, lignes_erreurs, details_erreurs, statut, import_id
        ))
    
    @staticmethod
    def obtenir_historique(limit=50):
        """
        Récupère l'historique des imports
        
        Args:
            limit (int): Nombre maximum d'imports
            
        Returns:
            list: Liste des imports
        """
        requete = """
            SELECT i.*,
                   c.nom_cours,
                   f.nom_filiere,
                   f.niveau,
                   u.nom as importeur_nom,
                   u.prenom as importeur_prenom,
                   u.matricule as importeur_matricule
            FROM ImportNotes i
            JOIN Cours c ON i.cours_id = c.id
            JOIN Filieres f ON i.filiere_id = f.id
            JOIN Utilisateurs u ON i.importeur_id = u.id
            ORDER BY i.created_at DESC
            LIMIT %s
        """
        return executer_requete(requete, (limit,), obtenir_resultats=True)
    
    @staticmethod
    def obtenir_par_cours(cours_id):
        """
        Récupère les imports d'un cours
        
        Args:
            cours_id (int): ID du cours
            
        Returns:
            list: Liste des imports du cours
        """
        requete = """
            SELECT i.*,
                   u.nom as importeur_nom,
                   u.prenom as importeur_prenom
            FROM ImportNotes i
            JOIN Utilisateurs u ON i.importeur_id = u.id
            WHERE i.cours_id = %s
            ORDER BY i.created_at DESC
        """
        return executer_requete(requete, (cours_id,), obtenir_resultats=True)
    
    @staticmethod
    def statistiques_imports(date_debut=None, date_fin=None):
        """
        Statistiques sur les imports
        
        Args:
            date_debut (str): Date de début
            date_fin (str): Date de fin
            
        Returns:
            dict: Statistiques
        """
        requete = """
            SELECT 
                COUNT(*) as nb_imports,
                SUM(lignes_totales) as total_lignes,
                SUM(lignes_succes) as total_succes,
                SUM(lignes_erreurs) as total_erreurs,
                ROUND(SUM(lignes_succes) * 100.0 / SUM(lignes_totales), 2) as taux_succes
            FROM ImportNotes
        """
        params = []
        
        if date_debut and date_fin:
            requete += " WHERE created_at BETWEEN %s AND %s"
            params = [date_debut, date_fin]
        
        return executer_requete_unique(requete, tuple(params) if params else None)


class Signalement:
    """Modèle pour la table Signalements"""
    
    @staticmethod
    def creer(etudiant_id, type_signalement, motif, note_id=None, cours_id=None):
        """
        Crée un nouveau signalement
        
        Args:
            etudiant_id (int): ID de l'étudiant
            type_signalement (str): Type de signalement
            motif (str): Motif du signalement
            note_id (int): ID de la note concernée (optionnel)
            cours_id (int): ID du cours concerné (optionnel)
            
        Returns:
            int: ID du signalement créé
        """
        requete = """
            INSERT INTO Signalements 
            (etudiant_id, note_id, cours_id, type_signalement, motif, statut)
            VALUES (%s, %s, %s, %s, %s, 'EN_ATTENTE')
        """
        return executer_requete(requete, (etudiant_id, note_id, cours_id, type_signalement, motif))
    
    @staticmethod
    def obtenir_tous(statut=None):
        """
        Récupère tous les signalements
        
        Args:
            statut (str): Filtrer par statut (optionnel)
            
        Returns:
            list: Liste des signalements
        """
        requete = """
            SELECT s.*,
                   u.matricule as etudiant_matricule,
                   u.nom as etudiant_nom,
                   u.prenom as etudiant_prenom,
                   n.note as note_valeur,
                   c.nom_cours
            FROM Signalements s
            JOIN Utilisateurs u ON s.etudiant_id = u.id
            LEFT JOIN Notes n ON s.note_id = n.id
            LEFT JOIN Cours c ON s.cours_id = c.id
        """
        
        if statut:
            requete += " WHERE s.statut = %s"
            params = (statut,)
        else:
            params = None
        
        requete += " ORDER BY s.created_at DESC"
        
        return executer_requete(requete, params, obtenir_resultats=True)
    
    @staticmethod
    def obtenir_par_etudiant(etudiant_id):
        """
        Récupère les signalements d'un étudiant
        
        Args:
            etudiant_id (int): ID de l'étudiant
            
        Returns:
            list: Liste des signalements de l'étudiant
        """
        requete = """
            SELECT s.*,
                   n.note as note_valeur,
                   c.nom_cours,
                   t.nom as traiteur_nom,
                   t.prenom as traiteur_prenom
            FROM Signalements s
            LEFT JOIN Notes n ON s.note_id = n.id
            LEFT JOIN Cours c ON s.cours_id = c.id
            LEFT JOIN Utilisateurs t ON s.traite_par = t.id
            WHERE s.etudiant_id = %s
            ORDER BY s.created_at DESC
        """
        return executer_requete(requete, (etudiant_id,), obtenir_resultats=True)
    
    @staticmethod
    def traiter_signalement(signalement_id, traite_par, reponse, nouveau_statut='RESOLU'):
        """
        Traite un signalement
        
        Args:
            signalement_id (int): ID du signalement
            traite_par (int): ID de l'utilisateur qui traite
            reponse (str): Réponse au signalement
            nouveau_statut (str): Nouveau statut
            
        Returns:
            int: Nombre de lignes affectées
        """
        requete = """
            UPDATE Signalements 
            SET statut = %s,
                traite_par = %s,
                reponse = %s,
                resolved_at = NOW()
            WHERE id = %s
        """
        return executer_requete(requete, (nouveau_statut, traite_par, reponse, signalement_id))
    
    @staticmethod
    def compter_en_attente():
        """
        Compte les signalements en attente
        
        Returns:
            int: Nombre de signalements en attente
        """
        requete = """
            SELECT COUNT(*) as count 
            FROM Signalements
            WHERE statut IN ('EN_ATTENTE', 'EN_TRAITEMENT')
        """
        result = executer_requete_unique(requete)
        return result['count'] if result else 0