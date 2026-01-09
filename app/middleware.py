"""
Middleware pour UIST-2ITS
Intercepteurs de requêtes pour logging, sécurité et gestion d'erreurs
"""
from flask import request, session, g
from functools import wraps
import time
from app.exceptions import log_user_action, log_security_event, log_error


def setup_request_logging(app):
    """
    Configure le logging automatique des requêtes
    
    Args:
        app: Instance Flask
    """
    
    @app.before_request
    def log_request():
        """Log avant chaque requête"""
        g.start_time = time.time()
        g.request_id = f"{int(time.time() * 1000)}-{request.remote_addr}"
        
        # Logger les requêtes sensibles
        if request.method in ['POST', 'PUT', 'DELETE', 'PATCH']:
            log_user_action(
                f'request_{request.method.lower()}',
                f"{request.method} {request.path}",
                {
                    'request_id': g.request_id,
                    'endpoint': request.endpoint,
                    'ip': request.remote_addr
                }
            )
    
    @app.after_request
    def log_response(response):
        """Log après chaque requête"""
        if hasattr(g, 'start_time'):
            elapsed = time.time() - g.start_time
            
            # Logger les requêtes lentes (> 1 seconde)
            if elapsed > 1.0:
                log_user_action(
                    'slow_request',
                    f"Requête lente: {request.path}",
                    {
                        'request_id': g.request_id,
                        'duration': f"{elapsed:.2f}s",
                        'endpoint': request.endpoint
                    }
                )
        
        return response


def setup_security_middleware(app):
    """
    Configure le middleware de sécurité
    
    Args:
        app: Instance Flask
    """
    
    @app.before_request
    def check_security():
        """Vérifications de sécurité avant chaque requête"""
        
        # 1. Détecter les tentatives d'accès suspects
        if request.path.startswith('/admin') or request.path.startswith('/directeur'):
            if 'utilisateur_id' not in session:
                log_security_event(
                    'unauthorized_admin_attempt',
                    'anonymous',
                    'unknown',
                    request.remote_addr,
                    {'path': request.path}
                )
        
        # 2. Vérifier les sessions expirées
        if 'utilisateur_id' in session:
            # Implémenter une vérification de timeout de session si nécessaire
            pass
        
        # 3. Détecter les tentatives de force brute (à implémenter avec Redis/cache)
        # Compter les tentatives de connexion échouées par IP
        pass


def setup_error_middleware(app):
    """
    Configure le middleware de gestion d'erreurs
    
    Args:
        app: Instance Flask
    """
    
    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        """Gestion globale des erreurs non gérées"""
        log_error(error, {
            'request_id': getattr(g, 'request_id', 'unknown'),
            'endpoint': request.endpoint,
            'method': request.method,
            'path': request.path
        })
        
        # Retourner une erreur 500 générique
        from flask import render_template
        return render_template('errors/500.html'), 500


def rate_limit(max_requests=10, window=60):
    """
    Décorateur pour limiter le taux de requêtes
    
    Args:
        max_requests: Nombre maximum de requêtes
        window: Fenêtre de temps en secondes
    
    Usage:
        @rate_limit(max_requests=5, window=60)
        def ma_route():
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Implémenter avec Redis ou cache mémoire
            # Pour l'instant, juste passer
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def csrf_protect(f):
    """
    Protection CSRF pour les formulaires
    
    Usage:
        @csrf_protect
        def ma_route():
            ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method == 'POST':
            # Vérifier le token CSRF (déjà géré par Flask-WTF)
            pass
        return f(*args, **kwargs)
    return decorated_function


def initialize_middleware(app):
    """
    Initialise tous les middlewares
    
    Args:
        app: Instance Flask
    """
    setup_request_logging(app)
    setup_security_middleware(app)
    setup_error_middleware(app)