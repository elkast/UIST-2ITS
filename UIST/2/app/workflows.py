"""
Système de gestion des workflows pour UIST-2ITS
Orchestration des interactions et déclenchements d'actions en cascade
"""
from datetime import datetime
from app.exceptions import (
    WorkflowException, ValidationException, log_user_action, 
    check_note_workflow, validate_workflow_state
)
from app.db import executer_requete, executer_requete_unique


class WorkflowManager:
    """Gestionnaire central des workflows du système"""
    
    @staticmethod
    def process_note_submission(note_id, enseignant_id):
        """
        Traite la soumission d'une note par un enseignant
        Déclenche: notification au directeur, changement d'état
        
        Args:
            note_id: ID de la note
            enseignant_id: ID de l'enseignant
        
        Returns:
            dict: Résultat du workflow
        """
        # 1. Récupérer la note
        note = executer_requete_unique(
            "SELECT * FROM Notes WHERE id = %s",
            (note_id,)
        )
        
        if not note:
            raise ValidationException(f"Note {note_id} introuvable")
        
        # 2. Vérifier l'état actuel
        validate_workflow_state(
            note['statut'],
            ['BROUILLON', 'EN_CORRECTION'],
            'soumettre la note'
        )
        
        # 3. Changer l'état vers EN_ATTENTE_DIRECTEUR
        executer_requete(
            "UPDATE Notes SET statut = %s, date_soumission = NOW() WHERE id = %s",
            ('EN_ATTENTE_DIRECTEUR', note_id)
        )
        
        # 4. Logger l'action
        log_user_action(
            'note_submitted',
            f"Soumission de la note {note_id} pour validation",
            {'note_id': note_id, 'enseignant_id': enseignant_id}
        )
        
        # 5. Créer une notification pour le directeur
        WorkflowManager._create_notification(
            'DIRECTEUR',
            'note_validation_required',
            f"Nouvelle note en attente de validation",
            {'note_id': note_id, 'enseignant_id': enseignant_id}
        )
        
        # 6. Déclencher le workflow de notification
        WorkflowManager._trigger_notification_workflow('DIRECTEUR', 'new_note')
        
        return {
            'success': True,
            'note_id': note_id,
            'new_status': 'EN_ATTENTE_DIRECTEUR',
            'notifications_sent': True
        }
    
    @staticmethod
    def process_note_validation(note_id, directeur_id, action, commentaire=None):
        """
        Traite la validation/rejet d'une note par le directeur
        Déclenche: notification à l'enseignant, mise à jour bulletin, notification étudiant
        
        Args:
            note_id: ID de la note
            directeur_id: ID du directeur
            action: 'valider' ou 'rejeter'
            commentaire: Commentaire optionnel
        
        Returns:
            dict: Résultat du workflow
        """
        # 1. Récupérer la note avec informations étudiant
        note = executer_requete_unique("""
            SELECT n.*, e.utilisateur_id as etudiant_id, u.nom as enseignant_nom
            FROM Notes n
            JOIN Etudiants e ON n.etudiant_id = e.id
            JOIN Utilisateurs u ON n.enseignant_id = u.id
            WHERE n.id = %s
        """, (note_id,))
        
        if not note:
            raise ValidationException(f"Note {note_id} introuvable")
        
        # 2. Vérifier l'état actuel
        validate_workflow_state(
            note['statut'],
            ['EN_ATTENTE_DIRECTEUR'],
            action
        )
        
        # 3. Déterminer le nouvel état
        new_status = 'VALIDEE' if action == 'valider' else 'REJETEE'
        check_note_workflow(note['statut'], new_status)
        
        # 4. Mettre à jour la note
        executer_requete("""
            UPDATE Notes 
            SET statut = %s, 
                date_validation = NOW(),
                validateur_id = %s,
                commentaire_validation = %s
            WHERE id = %s
        """, (new_status, directeur_id, commentaire, note_id))
        
        # 5. Logger l'action
        log_user_action(
            f'note_{action}',
            f"Note {note_id} {action}ée par le directeur",
            {
                'note_id': note_id, 
                'directeur_id': directeur_id,
                'action': action,
                'commentaire': commentaire
            }
        )
        
        # 6. Notifications
        # 6a. Notifier l'enseignant
        WorkflowManager._create_notification(
            'ENSEIGNANT',
            f'note_{action}ed',
            f"Votre note a été {action}ée",
            {
                'note_id': note_id,
                'user_id': note['enseignant_id'],
                'commentaire': commentaire
            }
        )
        
        # 6b. Si validée, notifier l'étudiant
        if action == 'valider':
            WorkflowManager._create_notification(
                'ETUDIANT',
                'note_published',
                f"Nouvelle note disponible",
                {
                    'note_id': note_id,
                    'user_id': note['etudiant_id']
                }
            )
            
            # 6c. Mettre à jour les statistiques de l'étudiant
            WorkflowManager._update_student_stats(note['etudiant_id'])
            
            # 6d. Vérifier si le bulletin peut être généré
            WorkflowManager._check_bulletin_generation(note['etudiant_id'])
        
        return {
            'success': True,
            'note_id': note_id,
            'new_status': new_status,
            'notifications_sent': True
        }
    
    @staticmethod
    def process_edt_creation(creneau_data):
        """
        Traite la création d'un créneau EDT
        Déclenche: vérification conflits, notification enseignant/étudiants
        
        Args:
            creneau_data: Données du créneau
        
        Returns:
            dict: Résultat du workflow
        """
        from app.exceptions import check_edt_conflict
        
        # 1. Vérifier les conflits
        check_edt_conflict(
            creneau_data['jour'],
            creneau_data['heure_debut'],
            creneau_data['heure_fin'],
            salle_id=creneau_data.get('salle_id'),
            enseignant_id=creneau_data.get('enseignant_id'),
            filiere_id=creneau_data.get('filiere_id')
        )
        
        # 2. Créer le créneau
        creneau_id = executer_requete("""
            INSERT INTO EmploiDuTemps 
            (cours_id, enseignant_id, salle_id, filiere_id, jour, heure_debut, heure_fin, type_cours)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            creneau_data['cours_id'],
            creneau_data['enseignant_id'],
            creneau_data['salle_id'],
            creneau_data['filiere_id'],
            creneau_data['jour'],
            creneau_data['heure_debut'],
            creneau_data['heure_fin'],
            creneau_data.get('type_cours', 'CM')
        ))
        
        # 3. Logger l'action
        log_user_action(
            'edt_created',
            f"Création créneau EDT {creneau_id}",
            creneau_data
        )
        
        # 4. Notifier l'enseignant
        WorkflowManager._create_notification(
            'ENSEIGNANT',
            'edt_assigned',
            f"Nouveau cours assigné",
            {
                'creneau_id': creneau_id,
                'user_id': creneau_data['enseignant_id']
            }
        )
        
        # 5. Notifier les étudiants de la filière
        WorkflowManager._notify_filiere_students(
            creneau_data['filiere_id'],
            'edt_updated',
            'Votre emploi du temps a été mis à jour'
        )
        
        return {
            'success': True,
            'creneau_id': creneau_id,
            'notifications_sent': True
        }
    
    @staticmethod
    def process_student_enrollment(etudiant_id, filiere_id, niveau):
        """
        Traite l'inscription d'un étudiant
        Déclenche: création compte, assignation filière, notification parent
        
        Args:
            etudiant_id: ID de l'étudiant
            filiere_id: ID de la filière
            niveau: Niveau d'étude
        
        Returns:
            dict: Résultat du workflow
        """
        # 1. Créer l'entrée étudiant
        executer_requete("""
            INSERT INTO Etudiants (utilisateur_id, filiere_id, niveau, date_inscription)
            VALUES (%s, %s, %s, NOW())
            ON DUPLICATE KEY UPDATE filiere_id = %s, niveau = %s
        """, (etudiant_id, filiere_id, niveau, filiere_id, niveau))
        
        # 2. Logger l'action
        log_user_action(
            'student_enrolled',
            f"Inscription étudiant {etudiant_id} en filière {filiere_id}",
            {'etudiant_id': etudiant_id, 'filiere_id': filiere_id, 'niveau': niveau}
        )
        
        # 3. Vérifier si l'étudiant a un parent
        parent = executer_requete_unique("""
            SELECT parent_id FROM Eleves_Parents WHERE eleve_id = %s
        """, (etudiant_id,))
        
        if parent:
            # 4. Notifier le parent
            WorkflowManager._create_notification(
                'PARENT',
                'child_enrolled',
                f"Inscription confirmée",
                {
                    'user_id': parent['parent_id'],
                    'etudiant_id': etudiant_id,
                    'filiere_id': filiere_id
                }
            )
        
        return {
            'success': True,
            'etudiant_id': etudiant_id,
            'filiere_id': filiere_id,
            'parent_notified': parent is not None
        }
    
    @staticmethod
    def process_bulletin_generation(etudiant_id, semestre):
        """
        Traite la génération d'un bulletin
        Déclenche: calcul moyennes, classement, génération PDF, notification
        
        Args:
            etudiant_id: ID de l'étudiant
            semestre: Semestre concerné
        
        Returns:
            dict: Résultat du workflow
        """
        # 1. Vérifier que toutes les notes sont validées
        notes_non_validees = executer_requete("""
            SELECT COUNT(*) as count FROM Notes 
            WHERE etudiant_id = %s AND semestre = %s AND statut != 'VALIDEE'
        """, (etudiant_id, semestre), obtenir_resultats=True)
        
        if notes_non_validees[0]['count'] > 0:
            raise WorkflowException(
                "Impossible de générer le bulletin: certaines notes ne sont pas validées",
                current_state='incomplete',
                expected_state='all_validated'
            )
        
        # 2. Calculer la moyenne générale
        from app.services.bulletin_service import BulletinService
        moyenne = BulletinService.calculer_moyenne_generale(etudiant_id, semestre)
        
        # 3. Calculer le classement
        classement = BulletinService.calculer_classement(etudiant_id, semestre)
        
        # 4. Générer le PDF
        pdf_path = BulletinService.generer_pdf(etudiant_id, semestre)
        
        # 5. Enregistrer le bulletin
        bulletin_id = executer_requete("""
            INSERT INTO Bulletins 
            (etudiant_id, semestre, moyenne_generale, classement, fichier_pdf, date_generation)
            VALUES (%s, %s, %s, %s, %s, NOW())
        """, (etudiant_id, semestre, moyenne, classement, pdf_path))
        
        # 6. Logger l'action
        log_user_action(
            'bulletin_generated',
            f"Génération bulletin {bulletin_id}",
            {
                'bulletin_id': bulletin_id,
                'etudiant_id': etudiant_id,
                'semestre': semestre,
                'moyenne': moyenne,
                'classement': classement
            }
        )
        
        # 7. Notifier l'étudiant
        WorkflowManager._create_notification(
            'ETUDIANT',
            'bulletin_available',
            f"Votre bulletin est disponible",
            {
                'bulletin_id': bulletin_id,
                'user_id': etudiant_id
            }
        )
        
        # 8. Notifier le parent
        parent = executer_requete_unique("""
            SELECT parent_id FROM Eleves_Parents WHERE eleve_id = %s
        """, (etudiant_id,))
        
        if parent:
            WorkflowManager._create_notification(
                'PARENT',
                'child_bulletin_available',
                f"Bulletin disponible",
                {
                    'bulletin_id': bulletin_id,
                    'user_id': parent['parent_id'],
                    'etudiant_id': etudiant_id
                }
            )
        
        return {
            'success': True,
            'bulletin_id': bulletin_id,
            'pdf_path': pdf_path,
            'moyenne': moyenne,
            'classement': classement
        }
    
    @staticmethod
    def _create_notification(role, type_notification, message, details):
        """
        Crée une notification dans le système
        
        Args:
            role: Rôle destinataire
            type_notification: Type de notification
            message: Message de notification
            details: Détails supplémentaires
        """
        try:
            user_id = details.get('user_id')
            executer_requete("""
                INSERT INTO Notifications 
                (utilisateur_id, type_notification, message, details, lu, date_creation)
                VALUES (%s, %s, %s, %s, FALSE, NOW())
            """, (user_id, type_notification, message, str(details)))
        except Exception as e:
            # Ne pas bloquer le workflow si la notification échoue
            from app.exceptions import logger
            logger.warning(f"Échec création notification: {e}")
    
    @staticmethod
    def _trigger_notification_workflow(role, event_type):
        """
        Déclenche un workflow de notification (email, SMS, etc.)
        
        Args:
            role: Rôle concerné
            event_type: Type d'événement
        """
        # Placeholder pour système de notification externe
        # Peut être étendu avec email, SMS, push notifications
        pass
    
    @staticmethod
    def _update_student_stats(etudiant_id):
        """
        Met à jour les statistiques d'un étudiant
        
        Args:
            etudiant_id: ID de l'étudiant
        """
        # Calculer et mettre à jour la moyenne générale
        moyenne = executer_requete_unique("""
            SELECT AVG(valeur) as moyenne
            FROM Notes
            WHERE etudiant_id = %s AND statut = 'VALIDEE'
        """, (etudiant_id,))
        
        if moyenne and moyenne['moyenne']:
            executer_requete("""
                UPDATE Etudiants 
                SET moyenne_generale = %s, date_maj = NOW()
                WHERE utilisateur_id = %s
            """, (moyenne['moyenne'], etudiant_id))
    
    @staticmethod
    def _check_bulletin_generation(etudiant_id):
        """
        Vérifie si un bulletin peut être généré automatiquement
        
        Args:
            etudiant_id: ID de l'étudiant
        """
        # Logique pour vérifier si toutes les notes du semestre sont validées
        # et déclencher la génération automatique du bulletin
        pass
    
    @staticmethod
    def _notify_filiere_students(filiere_id, type_notification, message):
        """
        Notifie tous les étudiants d'une filière
        
        Args:
            filiere_id: ID de la filière
            type_notification: Type de notification
            message: Message
        """
        etudiants = executer_requete("""
            SELECT utilisateur_id FROM Etudiants WHERE filiere_id = %s
        """, (filiere_id,), obtenir_resultats=True)
        
        for etudiant in etudiants:
            WorkflowManager._create_notification(
                'ETUDIANT',
                type_notification,
                message,
                {'user_id': etudiant['utilisateur_id']}
            )