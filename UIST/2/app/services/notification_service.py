"""
Service de notifications
Gère l'envoi de notifications aux utilisateurs
"""


class NotificationService:
    """Service de gestion des notifications"""
    
    @staticmethod
    def notifier_validation_note(etudiant_id, nom_cours, note):
        """
        Notifie un étudiant de la validation d'une note
        
        Args:
            etudiant_id (int): ID de l'étudiant
            nom_cours (str): Nom du cours
            note (float): Note obtenue
        """
        from app.models import Message
        
        # Créer un message de notification
        Message.creer(
            expediteur_id=1,  # Système
            destinataire_id=etudiant_id,
            sujet=f"Note validée - {nom_cours}",
            contenu=f"Votre note de {note}/20 pour le cours '{nom_cours}' a été validée et est maintenant consultable.",
            type_message='NOTIFICATION'
        )
    
    @staticmethod
    def notifier_nouveau_bulletin(etudiant_id, semestre, annee):
        """
        Notifie un étudiant de la génération d'un bulletin
        
        Args:
            etudiant_id (int): ID de l'étudiant
            semestre (str): Semestre
            annee (str): Année académique
        """
        from app.models import Message
        
        Message.creer(
            expediteur_id=1,  # Système
            destinataire_id=etudiant_id,
            sujet=f"Bulletin disponible - {semestre} {annee}",
            contenu=f"Votre bulletin pour le {semestre} de l'année {annee} est maintenant disponible en téléchargement.",
            type_message='NOTIFICATION'
        )
    
    @staticmethod
    def notifier_signalement_traite(utilisateur_id, sujet):
        """
        Notifie un utilisateur que son signalement a été traité
        
        Args:
            utilisateur_id (int): ID de l'utilisateur
            sujet (str): Sujet du signalement
        """
        from app.models import Message
        
        Message.creer(
            expediteur_id=1,  # Système
            destinataire_id=utilisateur_id,
            sujet=f"Signalement traité - {sujet}",
            contenu=f"Votre signalement concernant '{sujet}' a été traité par l'administration.",
            type_message='NOTIFICATION'
        )