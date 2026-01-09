"""
Système de gestion des exceptions et logs pour UIST-2ITS
Gestion centralisée des erreurs, logs d'audit et événements de sécurité
"""
import logging
from datetime import datetime
from functools import wraps
from flask import session, request, flash, redirect, url_for
from werkzeug.exceptions import HTTPException
import traceback

# Configuration des logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log', encoding='utf-8'),
        logging.FileHandler('logs/error.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('UIST-2ITS')
security_logger = logging.getLogger('UIST-2ITS.Security')
audit_logger = logging.getLogger('UIST-2ITS.Audit')


class UistException(Exception):
    """Exception de base pour UIST-2ITS"""
    def __init__(self, message, code=None, details=None):
        self.message = message
        self.code = code or 'UIST_ERROR'
        self.details = details or {}
        super().__init__(self.message)


class ValidationException(UistException):
    """Exception pour les erreurs de validation"""
    def __init__(self, message, field=None, details=None):
        details = details or {}
        if field:
            details['field'] = field
        super().__init__(message, 'VALIDATION_ERROR', details)


class DatabaseException(UistException):
    """Exception pour les erreurs de base de données"""
    def __init__(self, message, query=None, details=None):
        details = details or {}
        if query:
            details['query'] = query
        super().__init__(message, 'DATABASE_ERROR', details)


class AuthenticationException(UistException):
    """Exception pour les erreurs d'authentification"""
    def __init__(self, message, matricule=None, details=None):
        details = details or {}
        if matricule:
            details['matricule'] = matricule
        super().__init__(message, 'AUTH_ERROR', details)


class AuthorizationException(UistException):
    """Exception pour les erreurs d'autorisation"""
    def __init__(self, message, required_role=None, user_role=None, details=None):
        details = details or {}
        if required_role:
            details['required_role'] = required_role
        if user_role:
            details['user_role'] = user_role
        super().__init__(message, 'AUTHORIZATION_ERROR', details)


class ConflictException(UistException):
    """Exception pour les conflits (EDT, salles, etc.)"""
    def __init__(self, message, conflict_type=None, details=None):
        details = details or {}
        if conflict_type:
            details['conflict_type'] = conflict_type
        super().__init__(message, 'CONFLICT_ERROR', details)


class WorkflowException(UistException):
    """Exception pour les erreurs de workflow"""
    def __init__(self, message, current_state=None, expected_state=None, details=None):
        details = details or {}
        if current_state:
            details['current_state'] = current_state
        if expected_state:
            details['expected_state'] = expected_state
        super().__init__(message, 'WORKFLOW_ERROR', details)


def log_user_action(action_type, action_description, details=None):
    """
    Enregistre une action utilisateur dans les logs d'audit
    
    Args:
        action_type: Type d'action (login, logout, create, update, delete, etc.)
        action_description: Description de l'action
        details: Détails supplémentaires (dict)
    """
    user_id = session.get('utilisateur_id', 'anonymous')
    role = session.get('role', 'unknown')
    matricule = session.get('matricule', 'unknown')
    
    log_data = {
        'timestamp': datetime.now().isoformat(),
        'user_id': user_id,
        'matricule': matricule,
        'role': role,
        'action_type': action_type,
        'action': action_description,
        'ip': request.remote_addr if request else 'N/A',
        'user_agent': request.headers.get('User-Agent', 'N/A') if request else 'N/A',
        'details': details or {}
    }
    
    audit_logger.info(f"USER_ACTION: {log_data}")
    
    # Enregistrer dans la base de données si nécessaire
    try:
        from app.db import executer_requete
        executer_requete("""
            INSERT INTO UsageAudit 
            (utilisateur_id, action_type, action_description, ip_address, details, timestamp)
            VALUES (%s, %s, %s, %s, %s, NOW())
        """, (user_id, action_type, action_description, request.remote_addr if request else None, str(details)))
    except Exception as e:
        logger.error(f"Erreur lors de l'enregistrement de l'audit: {e}")


def log_security_event(event_type, user_id, role, ip_address, details=None):
    """
    Enregistre un événement de sécurité
    
    Args:
        event_type: Type d'événement (unauthorized_access, failed_login, etc.)
        user_id: ID de l'utilisateur
        role: Rôle de l'utilisateur
        ip_address: Adresse IP
        details: Détails supplémentaires
    """
    log_data = {
        'timestamp': datetime.now().isoformat(),
        'event_type': event_type,
        'user_id': user_id,
        'role': role,
        'ip': ip_address,
        'details': details or {}
    }
    
    security_logger.warning(f"SECURITY_EVENT: {log_data}")


def log_error(error, context=None):
    """
    Enregistre une erreur avec son contexte
    
    Args:
        error: Exception ou message d'erreur
        context: Contexte de l'erreur (dict)
    """
    error_data = {
        'timestamp': datetime.now().isoformat(),
        'error': str(error),
        'type': type(error).__name__,
        'traceback': traceback.format_exc() if isinstance(error, Exception) else None,
        'context': context or {},
        'user_id': session.get('utilisateur_id', 'anonymous'),
        'url': request.url if request else 'N/A'
    }
    
    logger.error(f"ERROR: {error_data}")


def handle_exception(f):
    """
    Décorateur pour gérer les exceptions dans les routes
    
    Usage:
        @handle_exception
        def ma_route():
            ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValidationException as e:
            log_error(e, {'type': 'validation', 'details': e.details})
            flash(f"Erreur de validation: {e.message}", 'danger')
            return redirect(request.referrer or url_for('auth.connexion'))
        except AuthenticationException as e:
            log_error(e, {'type': 'authentication', 'details': e.details})
            log_security_event('authentication_failed', e.details.get('matricule', 'unknown'), 
                             'unknown', request.remote_addr, e.details)
            flash(f"Erreur d'authentification: {e.message}", 'danger')
            return redirect(url_for('auth.connexion'))
        except AuthorizationException as e:
            log_error(e, {'type': 'authorization', 'details': e.details})
            log_security_event('authorization_failed', session.get('utilisateur_id'), 
                             session.get('role'), request.remote_addr, e.details)
            flash(f"Accès refusé: {e.message}", 'danger')
            return redirect(url_for('auth.connexion'))
        except ConflictException as e:
            log_error(e, {'type': 'conflict', 'details': e.details})
            flash(f"Conflit détecté: {e.message}", 'warning')
            return redirect(request.referrer or url_for('auth.connexion'))
        except DatabaseException as e:
            log_error(e, {'type': 'database', 'details': e.details})
            flash("Erreur de base de données. Veuillez réessayer plus tard.", 'danger')
            return redirect(request.referrer or url_for('auth.connexion'))
        except WorkflowException as e:
            log_error(e, {'type': 'workflow', 'details': e.details})
            flash(f"Erreur de workflow: {e.message}", 'warning')
            return redirect(request.referrer or url_for('auth.connexion'))
        except HTTPException as e:
            # Laisser Flask gérer les exceptions HTTP
            raise
        except Exception as e:
            log_error(e, {'type': 'unexpected', 'function': f.__name__})
            flash("Une erreur inattendue s'est produite. Veuillez réessayer.", 'danger')
            return redirect(url_for('auth.connexion'))
    
    return decorated_function


def validate_note_range(note, min_val=0, max_val=20):
    """
    Valide qu'une note est dans la plage autorisée
    
    Args:
        note: Note à valider
        min_val: Valeur minimale
        max_val: Valeur maximale
    
    Raises:
        ValidationException: Si la note est hors limites
    """
    try:
        note_float = float(note)
        if note_float < min_val or note_float > max_val:
            raise ValidationException(
                f"La note doit être entre {min_val} et {max_val}",
                field='note',
                details={'value': note, 'min': min_val, 'max': max_val}
            )
        return note_float
    except ValueError:
        raise ValidationException(
            "La note doit être un nombre valide",
            field='note',
            details={'value': note}
        )


def validate_matricule_unique(matricule, exclude_id=None):
    """
    Valide l'unicité d'un matricule
    
    Args:
        matricule: Matricule à vérifier
        exclude_id: ID à exclure de la vérification (pour les mises à jour)
    
    Raises:
        ValidationException: Si le matricule existe déjà
    """
    from app.db import executer_requete_unique
    
    query = "SELECT id FROM Utilisateurs WHERE matricule = %s"
    params = [matricule]
    
    if exclude_id:
        query += " AND id != %s"
        params.append(exclude_id)
    
    existing = executer_requete_unique(query, tuple(params))
    if existing:
        raise ValidationException(
            f"Le matricule {matricule} existe déjà",
            field='matricule',
            details={'matricule': matricule}
        )


def check_edt_conflict(jour, heure_debut, heure_fin, salle_id=None, enseignant_id=None, 
                       filiere_id=None, exclude_id=None):
    """
    Vérifie les conflits d'emploi du temps
    
    Args:
        jour: Jour de la semaine
        heure_debut: Heure de début
        heure_fin: Heure de fin
        salle_id: ID de la salle
        enseignant_id: ID de l'enseignant
        filiere_id: ID de la filière
        exclude_id: ID du créneau à exclure (pour les mises à jour)
    
    Raises:
        ConflictException: Si un conflit est détecté
    """
    from app.db import executer_requete
    
    conflicts = []
    
    base_query = """
        SELECT edt.id, edt.jour, edt.heure_debut, edt.heure_fin,
               c.nom_cours, s.nom_salle, u.nom as enseignant_nom, f.nom_filiere
        FROM EmploiDuTemps edt
        LEFT JOIN Cours c ON edt.cours_id = c.id
        LEFT JOIN Salles s ON edt.salle_id = s.id
        LEFT JOIN Utilisateurs u ON edt.enseignant_id = u.id
        LEFT JOIN Filieres f ON edt.filiere_id = f.id
        WHERE edt.jour = %s
        AND (
            (edt.heure_debut <= %s AND edt.heure_fin > %s)
            OR (edt.heure_debut < %s AND edt.heure_fin >= %s)
            OR (edt.heure_debut >= %s AND edt.heure_fin <= %s)
        )
    """
    
    params = [jour, heure_debut, heure_debut, heure_fin, heure_fin, heure_debut, heure_fin]
    
    if exclude_id:
        base_query += " AND edt.id != %s"
        params.append(exclude_id)
    
    # Vérifier conflit de salle
    if salle_id:
        query = base_query + " AND edt.salle_id = %s"
        result = executer_requete(query, tuple(params + [salle_id]), obtenir_resultats=True)
        if result:
            conflicts.append({
                'type': 'salle',
                'message': f"La salle {result[0]['nom_salle']} est déjà occupée",
                'details': result[0]
            })
    
    # Vérifier conflit d'enseignant
    if enseignant_id:
        query = base_query + " AND edt.enseignant_id = %s"
        result = executer_requete(query, tuple(params + [enseignant_id]), obtenir_resultats=True)
        if result:
            conflicts.append({
                'type': 'enseignant',
                'message': f"L'enseignant {result[0]['enseignant_nom']} a déjà un cours",
                'details': result[0]
            })
    
    # Vérifier conflit de filière
    if filiere_id:
        query = base_query + " AND edt.filiere_id = %s"
        result = executer_requete(query, tuple(params + [filiere_id]), obtenir_resultats=True)
        if result:
            conflicts.append({
                'type': 'filiere',
                'message': f"La filière {result[0]['nom_filiere']} a déjà un cours",
                'details': result[0]
            })
    
    if conflicts:
        conflict_messages = [c['message'] for c in conflicts]
        raise ConflictException(
            ". ".join(conflict_messages),
            conflict_type='edt',
            details={'conflicts': conflicts}
        )


def validate_workflow_state(current_state, expected_states, action):
    """
    Valide l'état actuel dans un workflow
    
    Args:
        current_state: État actuel
        expected_states: Liste des états attendus
        action: Action tentée
    
    Raises:
        WorkflowException: Si l'état n'est pas valide
    """
    if current_state not in expected_states:
        raise WorkflowException(
            f"Impossible de {action}: état actuel '{current_state}' invalide",
            current_state=current_state,
            expected_state=expected_states,
            details={'action': action}
        )


# États de workflow pour les notes
NOTE_WORKFLOW_STATES = {
    'BROUILLON': ['EN_ATTENTE_VALIDATION', 'SUPPRIME'],
    'EN_ATTENTE_VALIDATION': ['VALIDEE', 'REJETEE', 'EN_ATTENTE_DIRECTEUR'],
    'EN_ATTENTE_DIRECTEUR': ['VALIDEE', 'REJETEE', 'EN_CORRECTION'],
    'EN_CORRECTION': ['EN_ATTENTE_DIRECTEUR', 'SUPPRIME'],
    'VALIDEE': ['EN_CORRECTION'],
    'REJETEE': ['EN_CORRECTION', 'SUPPRIME'],
    'SUPPRIME': []
}


def check_note_workflow(current_state, target_state):
    """
    Vérifie si une transition d'état de note est valide
    
    Args:
        current_state: État actuel de la note
        target_state: État cible
    
    Raises:
        WorkflowException: Si la transition n'est pas valide
    """
    allowed_transitions = NOTE_WORKFLOW_STATES.get(current_state, [])
    
    if target_state not in allowed_transitions:
        raise WorkflowException(
            f"Transition invalide de '{current_state}' vers '{target_state}'",
            current_state=current_state,
            expected_state=allowed_transitions,
            details={'target_state': target_state}
        )