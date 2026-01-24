"""
Helper Authentification - JWT et gestion des sessions
"""
import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, session, redirect, url_for, flash
from config import Config

def generer_token_jwt(user_id, role):
    """
    Génère un token JWT pour un utilisateur
    
    Args:
        user_id: ID de l'utilisateur
        role: Rôle de l'utilisateur
    
    Returns:
        str: Token JWT
    """
    payload = {
        'user_id': user_id,
        'role': role,
        'exp': datetime.utcnow() + Config.JWT_ACCESS_TOKEN_EXPIRES,
        'iat': datetime.utcnow()
    }
    
    token = jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm='HS256')
    return token

def decoder_token_jwt(token):
    """
    Décode un token JWT
    
    Args:
        token: Token à décoder
    
    Returns:
        dict avec user_id et role ou None si invalide
    """
    try:
        payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=['HS256'])
        return {
            'user_id': payload['user_id'],
            'role': payload['role']
        }
    except jwt.ExpiredSignatureError:
        return None  # Token expiré
    except jwt.InvalidTokenError:
        return None  # Token invalide

def connexion_utilisateur(matricule, mot_de_passe=None, ip_address=None):
    """
    Connecte un utilisateur et génère un token

    Args:
        matricule: Matricule de l'utilisateur
        mot_de_passe: Mot de passe (ignoré pour connexion sans mot de passe)
        ip_address: Adresse IP (optionnel)

    Returns:
        dict: {'success': bool, 'token': str, 'user': dict, 'message': str}
    """
    from models.utilisateurs import obtenir_utilisateur_par_matricule, mettre_a_jour_derniere_connexion
    from models.audit import creer_log_audit, ACTIONS_AUDIT

    user = obtenir_utilisateur_par_matricule(matricule)

    if not user:
        return {'success': False, 'message': 'Matricule invalide'}

    if not user.est_actif:
        return {'success': False, 'message': 'Compte désactivé'}

    # Générer token
    token = generer_token_jwt(user.id_user, user.role)

    # Mettre à jour dernière connexion
    mettre_a_jour_derniere_connexion(user.id_user)

    # Log connexion réussie
    creer_log_audit(
        user.id_user,
        ACTIONS_AUDIT['CONNEXION'],
        details='Connexion réussie',
        ip_address=ip_address
    )

    return {
        'success': True,
        'token': token,
        'user': {
            'id_user': user.id_user,
            'matricule': user.matricule,
            'nom': user.nom,
            'prenom': user.prenom,
            'email': user.email,
            'role': user.role
        },
        'message': 'Connexion réussie'
    }

def obtenir_utilisateur_session():
    """
    Récupère l'utilisateur de la session courante
    
    Returns:
        dict avec user_id et role ou None
    """
    if 'user_id' in session and 'role' in session:
        return {
            'user_id': session['user_id'],
            'role': session['role']
        }
    return None

def verifier_role_autorise(roles_autorises):
    """
    Décorateur pour vérifier les rôles autorisés
    
    Args:
        roles_autorises: Liste des rôles autorisés
    
    Usage:
        @verifier_role_autorise(['DIRECTEUR', 'SUPER_ADMIN'])
        def ma_fonction():
            ...
    """
    def decorateur(fonction):
        @wraps(fonction)
        def wrapper(*args, **kwargs):
            user_session = obtenir_utilisateur_session()
            
            if not user_session:
                flash('Veuillez vous connecter', 'warning')
                return redirect(url_for('auth.login'))
            
            if user_session['role'] not in roles_autorises:
                from models.audit import creer_log_audit, ACTIONS_AUDIT
                creer_log_audit(
                    user_session['user_id'],
                    ACTIONS_AUDIT['ACCES_NON_AUTORISE'],
                    details=f"Tentative accès à {request.endpoint}",
                    ip_address=request.remote_addr
                )
                flash('Accès non autorisé', 'danger')
                return redirect(url_for('auth.login'))
            
            return fonction(*args, **kwargs)
        
        return wrapper
    return decorateur

def connexion_requise(fonction):
    """
    Décorateur simple pour exiger une connexion
    
    Usage:
        @connexion_requise
        def ma_fonction():
            ...
    """
    @wraps(fonction)
    def wrapper(*args, **kwargs):
        user_session = obtenir_utilisateur_session()
        
        if not user_session:
            flash('Veuillez vous connecter', 'warning')
            return redirect(url_for('auth.login'))
        
        return fonction(*args, **kwargs)
    
    return wrapper

def obtenir_ip_utilisateur():
    """Récupère l'adresse IP de l'utilisateur"""
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        return request.environ['REMOTE_ADDR']
    else:
        return request.environ['HTTP_X_FORWARDED_FOR']
