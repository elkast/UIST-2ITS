"""
Service étendu de notifications avec support complet du workflow
"""
from app.models_extended import Notification, AuditUsage


class NotificationServiceExtended:
    """Service de gestion des notifications étendues"""
    
    @staticmethod
    def notifier_validation_note(etudiant_id, cours_nom, note_valeur):
        """
        Notifie un étudiant de la validation d'une note
        
        Args:
            etudiant_id (int): ID de l'étudiant
            cours_nom (str): Nom du cours
            note_valeur (float): Note obtenue
        """
        Notification.creer(
            destinataire_id=etudiant_id,
            type_notification='NOTE_VALIDATED',
            titre=f"Note validée - {cours_nom}",
            message=f"Votre note de {note_valeur}/20 pour le cours '{cours_nom}' a été validée et est maintenant consultable.",
            priorite='normale',
            lien_action='/etudiant/mes-notes'
        )
    
    @staticmethod
    def notifier_parents_validation_note(etudiant_id, cours_nom, note_valeur):
        """
        Notifie les parents de la validation d'une note
        
        Args:
            etudiant_id (int): ID de l'étudiant
            cours_nom (str): Nom du cours
            note_valeur (float): Note obtenue
        """
        from app.models import Parent, Utilisateur
        
        # Récupérer l'étudiant
        etudiant = Utilisateur.obtenir_par_id(etudiant_id)
        if not etudiant:
            return
        
        # Récupérer les parents
        parents = Parent.obtenir_parents(etudiant_id)
        if not parents:
            return
        
        # Notifier chaque parent
        for parent in parents:
            Notification.creer(
                destinataire_id=parent['parent_id'],
                type_notification='NOTE_VALIDATED',
                titre=f"Note validée - {etudiant['prenom']} {etudiant['nom']}",
                message=f"La note de {note_valeur}/20 de votre enfant {etudiant['prenom']} {etudiant['nom']} pour le cours '{cours_nom}' a été validée.",
                priorite='normale',
                lien_action=f'/parent/enfant/{etudiant_id}'
            )
    
    @staticmethod
    def notifier_bulletin_pret(etudiant_id, semestre, annee_academique, bulletin_id):
        """
        Notifie un étudiant que son bulletin est prêt
        
        Args:
            etudiant_id (int): ID de l'étudiant
            semestre (str): Semestre
            annee_academique (str): Année académique
            bulletin_id (int): ID du bulletin
        """
        Notification.creer(
            destinataire_id=etudiant_id,
            type_notification='BULLETIN_READY',
            titre=f"Bulletin disponible - {semestre} {annee_academique}",
            message=f"Votre bulletin pour le {semestre} de l'année {annee_academique} est maintenant disponible.",
            priorite='haute',
            lien_action=f'/etudiant/bulletins/{bulletin_id}'
        )
    
    @staticmethod
    def notifier_parents_bulletin_pret(etudiant_id, semestre, annee_academique, bulletin_id):
        """
        Notifie les parents qu'un bulletin est prêt
        
        Args:
            etudiant_id (int): ID de l'étudiant
            semestre (str): Semestre
            annee_academique (str): Année académique
            bulletin_id (int): ID du bulletin
        """
        from app.models import Parent, Utilisateur
        
        etudiant = Utilisateur.obtenir_par_id(etudiant_id)
        if not etudiant:
            return
        
        parents = Parent.obtenir_parents(etudiant_id)
        if not parents:
            return
        
        for parent in parents:
            Notification.creer(
                destinataire_id=parent['parent_id'],
                type_notification='BULLETIN_READY',
                titre=f"Bulletin disponible - {etudiant['prenom']} {etudiant['nom']}",
                message=f"Le bulletin de {etudiant['prenom']} {etudiant['nom']} pour le {semestre} {annee_academique} est disponible.",
                priorite='haute',
                lien_action=f'/parent/enfant/{etudiant_id}/bulletins/{bulletin_id}'
            )
    
    @staticmethod
    def notifier_notes_manquantes(enseignant_id, cours_nom, filiere_nom):
        """
        Notifie un enseignant qu'il manque des notes
        
        Args:
            enseignant_id (int): ID de l'enseignant
            cours_nom (str): Nom du cours
            filiere_nom (str): Nom de la filière
        """
        Notification.creer(
            destinataire_id=enseignant_id,
            type_notification='NOTES_MISSING',
            titre=f"Notes manquantes - {cours_nom}",
            message=f"Des notes sont manquantes pour le cours '{cours_nom}' ({filiere_nom}). Veuillez les saisir pour permettre la génération des bulletins.",
            priorite='haute',
            lien_action='/enseignant/saisie-notes'
        )
    
    @staticmethod
    def notifier_bulletin_bloque(gestionnaire_pv_id, filiere_nom, nb_notes_manquantes):
        """
        Notifie le gestionnaire PV que des bulletins sont bloqués
        
        Args:
            gestionnaire_pv_id (int): ID du gestionnaire PV
            filiere_nom (str): Nom de la filière
            nb_notes_manquantes (int): Nombre de notes manquantes
        """
        Notification.creer(
            destinataire_id=gestionnaire_pv_id,
            type_notification='BULLETIN_BLOCKED',
            titre=f"Bulletin bloqué - {filiere_nom}",
            message=f"Impossible de générer les bulletins pour {filiere_nom}. {nb_notes_manquantes} note(s) en attente de validation.",
            priorite='critique',
            lien_action='/gestionnaire-pv/dashboard'
        )
    
    @staticmethod
    def notifier_conflit_edt(gestionnaire_edt_id, type_conflit, details):
        """
        Notifie le gestionnaire EDT d'un conflit
        
        Args:
            gestionnaire_edt_id (int): ID du gestionnaire EDT
            type_conflit (str): Type de conflit
            details (str): Détails du conflit
        """
        Notification.creer(
            destinataire_id=gestionnaire_edt_id,
            type_notification='CONFLICT_DETECTED',
            titre=f"Conflit détecté - {type_conflit}",
            message=details,
            priorite='critique',
            lien_action='/gestionnaire-edt/conflits'
        )
    
    @staticmethod
    def notifier_signalement_recu(directeur_id, etudiant_nom, cours_nom):
        """
        Notifie le directeur qu'un signalement a été reçu
        
        Args:
            directeur_id (int): ID du directeur
            etudiant_nom (str): Nom de l'étudiant
            cours_nom (str): Nom du cours
        """
        Notification.creer(
            destinataire_id=directeur_id,
            type_notification='SIGNALEMENT_RECEIVED',
            titre=f"Nouveau signalement - {etudiant_nom}",
            message=f"L'étudiant {etudiant_nom} a signalé une erreur pour le cours '{cours_nom}'.",
            priorite='haute',
            lien_action='/directeur/signalements'
        )
    
    @staticmethod
    def notifier_import_termine(importeur_id, cours_nom, nb_succes, nb_erreurs):
        """
        Notifie l'importeur que l'import est terminé
        
        Args:
            importeur_id (int): ID de l'importeur
            cours_nom (str): Nom du cours
            nb_succes (int): Nombre de notes importées avec succès
            nb_erreurs (int): Nombre d'erreurs
        """
        type_notif = 'IMPORT_COMPLETED' if nb_erreurs == 0 else 'IMPORT_FAILED'
        priorite = 'normale' if nb_erreurs == 0 else 'haute'
        
        message = f"Import terminé pour '{cours_nom}': {nb_succes} note(s) importée(s)"
        if nb_erreurs > 0:
            message += f", {nb_erreurs} erreur(s)."
        else:
            message += "."
        
        Notification.creer(
            destinataire_id=importeur_id,
            type_notification=type_notif,
            titre=f"Import terminé - {cours_nom}",
            message=message,
            priorite=priorite,
            lien_action='/gestionnaire-examens/imports'
        )
    
    @staticmethod
    def notifier_signalement_traite(etudiant_id, cours_nom, reponse):
        """
        Notifie l'étudiant que son signalement a été traité
        
        Args:
            etudiant_id (int): ID de l'étudiant
            cours_nom (str): Nom du cours
            reponse (str): Réponse au signalement
        """
        Notification.creer(
            destinataire_id=etudiant_id,
            type_notification='GENERAL',
            titre=f"Signalement traité - {cours_nom}",
            message=f"Votre signalement concernant '{cours_nom}' a été traité. Réponse: {reponse}",
            priorite='normale',
            lien_action='/etudiant/signalements'
        )


class AuditService:
    """Service de gestion des logs d'audit"""
    
    @staticmethod
    def log_action(user_id, action, description=None, ip_address=None, meta=None):
        """
        Enregistre une action dans l'audit
        
        Args:
            user_id (int): ID de l'utilisateur
            action (str): Action effectuée
            description (str): Description
            ip_address (str): Adresse IP
            meta (dict): Métadonnées
        """
        return AuditUsage.creer(user_id, action, description, ip_address, meta)
    
    @staticmethod
    def log_connexion(user_id, ip_address):
        """Log une connexion"""
        return AuditService.log_action(
            user_id, 
            'LOGIN', 
            'Connexion utilisateur',
            ip_address
        )
    
    @staticmethod
    def log_deconnexion(user_id, ip_address):
        """Log une déconnexion"""
        return AuditService.log_action(
            user_id,
            'LOGOUT',
            'Déconnexion utilisateur',
            ip_address
        )
    
    @staticmethod
    def log_validation_note(user_id, note_id, etudiant_id):
        """Log une validation de note"""
        return AuditService.log_action(
            user_id,
            'VALIDATE_NOTE',
            f'Validation note #{note_id} pour étudiant #{etudiant_id}',
            meta={'note_id': note_id, 'etudiant_id': etudiant_id}
        )
    
    @staticmethod
    def log_generation_bulletin(user_id, bulletin_id, etudiant_id):
        """Log une génération de bulletin"""
        return AuditService.log_action(
            user_id,
            'GENERATE_BULLETIN',
            f'Génération bulletin #{bulletin_id} pour étudiant #{etudiant_id}',
            meta={'bulletin_id': bulletin_id, 'etudiant_id': etudiant_id}
        )
    
    @staticmethod
    def log_import_notes(user_id, import_id, nb_notes):
        """Log un import de notes"""
        return AuditService.log_action(
            user_id,
            'IMPORT_NOTES',
            f'Import #{import_id}: {nb_notes} notes',
            meta={'import_id': import_id, 'nb_notes': nb_notes}
        )
    
    @staticmethod
    def log_creation_creneau(user_id, creneau_id):
        """Log une création de créneau EDT"""
        return AuditService.log_action(
            user_id,
            'CREATE_CRENEAU',
            f'Création créneau #{creneau_id}',
            meta={'creneau_id': creneau_id}
        )
    
    @staticmethod
    def log_conflit_detecte(user_id, conflit_type, details):
        """Log une détection de conflit"""
        return AuditService.log_action(
            user_id,
            'CONFLICT_DETECTED',
            f'Conflit {conflit_type}',
            meta={'type': conflit_type, 'details': details}
        )