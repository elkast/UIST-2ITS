"""
Décorateurs pour la gestion des rôles et l'audit
"""
from functools import wraps
from flask import session, redirect, url_for, abort, request
from app.models.utilisateur import AuditUsage

def login_required(f):
    """Décorateur pour vérifier que l'utilisateur est connecté"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(roles_autorises):
    """
    Décorateur pour vérifier le rôle de l'utilisateur
    
    Args:
        roles_autorises (list): Liste des rôles autorisés à accéder à cette route
    
    Usage:
        @role_required(['SUPER_ADMIN', 'DIRECTEUR'])
        def ma_route():
            pass
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                return redirect(url_for('auth.login'))
            
            role = session.get('role')
            if role not in roles_autorises:
                abort(403)  # Forbidden
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def audit_action(action, table_affectee=None):
    """
    Décorateur pour enregistrer automatiquement les actions dans l'audit
    
    Args:
        action (str): Description de l'action
        table_affectee (str): Table affectée par l'action
    
    Usage:
        @audit_action('creation_utilisateur', 'utilisateurs')
        def creer_utilisateur():
            pass
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            result = f(*args, **kwargs)
            
            # Enregistrer l'action dans l'audit
            try:
                id_user = session.get('user_id')
                ip_address = request.remote_addr
                details = f"Route: {request.endpoint}"
                
                AuditUsage.creer(
                    id_user=id_user,
                    action=action,
                    table_affectee=table_affectee,
                    details=details,
                    ip_address=ip_address
                )
            except Exception as e:
                print(f"Erreur lors de l'audit: {e}")
            
            return result
        return decorated_function
    return decorator