"""
Initialisation de l'application Flask UIST-2ITS
Configure l'application et enregistre les blueprints
"""
from flask import Flask
from dotenv import load_dotenv
from config import obtenir_config
import os

# Charger les variables d'environnement
load_dotenv()

def creer_application(config_name=None):
    """
    Fonction factory pour créer et configurer l'application Flask
    
    Args:
        config_name (str): Nom de la configuration à utiliser
    
    Returns:
        Flask: Instance de l'application configurée
    """
    app = Flask(__name__, 
                template_folder='../templates',
                static_folder='../static')
    
    # Configuration de l'application
    config_class = obtenir_config(config_name)
    app.config.from_object(config_class)
    
    # Créer les dossiers nécessaires
    os.makedirs('database', exist_ok=True)
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('static/bulletins', exist_ok=True)
    os.makedirs('static/pv', exist_ok=True)
    
    # Filtre Jinja2 personnalisé pour formater les timedelta
    @app.template_filter('format_time')
    def format_time_filter(value):
        """
        Formate un objet timedelta ou string en format HH:MM
        
        Args:
            value: timedelta, datetime.time ou string
            
        Returns:
            str: Heure formatée en HH:MM
        """
        from datetime import timedelta, time
        
        if value is None:
            return ''
        
        # Si c'est déjà une string, la retourner telle quelle
        if isinstance(value, str):
            return value
        
        # Si c'est un timedelta, convertir en HH:MM
        if isinstance(value, timedelta):
            total_seconds = int(value.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            return f"{hours:02d}:{minutes:02d}"
        
        # Si c'est un datetime.time, utiliser strftime
        if isinstance(value, time):
            return value.strftime('%H:%M')
        
        # Si c'est un datetime, utiliser strftime
        if hasattr(value, 'strftime'):
            return value.strftime('%H:%M')
        
        # Par défaut, retourner la représentation string
        return str(value)
    
    # Initialiser la base de données SQLite3
    from app import db
    db.init_app(app)
    
    # Message si la base n'existe pas
    if not os.path.exists(app.config['DB_PATH']):
        print("\n" + "="*70)
        print("⚠️  BASE DE DONNÉES NON INITIALISÉE")
        print("="*70)
        print("Exécutez: python scripts/init_complet_db.py")
        print("="*70 + "\n")
    
    # Enregistrement des blueprints - Routes simplifiées
    from app.blueprints.auth.routes import auth_bp
    from app.blueprints.super_admin.routes import super_admin_bp
    
    # Enregistrer auth en premier
    app.register_blueprint(auth_bp)
    app.register_blueprint(super_admin_bp, url_prefix='/super-admin')
    
    # Enregistrer les autres blueprints s'ils existent
    try:
        from app.blueprints.directeur.routes import directeur_bp
        app.register_blueprint(directeur_bp, url_prefix='/directeur')
    except ImportError:
        print("⚠️ Blueprint directeur non trouvé")
    
    try:
        from app.blueprints.gestion1.routes import gestion1_bp
        app.register_blueprint(gestion1_bp, url_prefix='/gestion1')
    except ImportError:
        print("⚠️ Blueprint gestion1 non trouvé")
    
    try:
        from app.blueprints.gestion2.routes import gestion2_bp
        app.register_blueprint(gestion2_bp, url_prefix='/gestion2')
    except ImportError:
        print("⚠️ Blueprint gestion2 non trouvé")
    
    try:
        from app.blueprints.gestion3.routes import gestion3_bp
        app.register_blueprint(gestion3_bp, url_prefix='/gestion3')
    except ImportError:
        print("⚠️ Blueprint gestion3 non trouvé")
    
    try:
        from app.blueprints.enseignant.routes import enseignant_bp
        app.register_blueprint(enseignant_bp, url_prefix='/enseignant')
    except ImportError:
        print("⚠️ Blueprint enseignant non trouvé")
    
    try:
        from app.blueprints.etudiant.routes import etudiant_bp
        app.register_blueprint(etudiant_bp, url_prefix='/etudiant')
    except ImportError:
        print("⚠️ Blueprint etudiant non trouvé")
    
    try:
        from app.blueprints.parent.routes import parent_bp
        app.register_blueprint(parent_bp, url_prefix='/parent')
    except ImportError:
        print("⚠️ Blueprint parent non trouvé")
    
    # Initialiser les middlewares si nécessaire
    try:
        from app.middleware import initialize_middleware
        initialize_middleware(app)
    except ImportError:
        pass  # Middleware optionnel
    
    # Route racine - redirection selon le rôle
    @app.route('/')
    def index():
        from flask import redirect, url_for, session
        if 'utilisateur_id' in session:
            role = session.get('role')
            role_redirects = {
                'SUPER_ADMIN': 'super_admin.dashboard',
                'DIRECTEUR': 'directeur.dashboard',
                'GESTION_1': 'gestion1.dashboard',
                'GESTION_2': 'gestion2.dashboard',
                'GESTION_3': 'gestion3.dashboard',
                'ENSEIGNANT': 'enseignant.dashboard',
                'ETUDIANT': 'etudiant.dashboard',
                'PARENT': 'parent.dashboard'
            }
            return redirect(url_for(role_redirects.get(role, 'auth.connexion')))
        return redirect(url_for('auth.landing'))
    
    # Route de diagnostic
    @app.route('/diagnostic')
    def diagnostic():
        from flask import render_template
        return render_template('diagnostic.html')

    # Pages d'erreurs customisées avec logging
    from flask import render_template as rt, session, request
    
    @app.errorhandler(401)
    def error_401(e):
        try:
            from app.services.audit_service import log_security_event
            log_security_event('unauthorized_access', 
                              session.get('user_id', 'anonymous'),
                              session.get('role', 'unknown'),
                              request.remote_addr,
                              {'url': request.url, 'error': str(e)})
        except:
            pass
        return rt('errors/401.html'), 401

    @app.errorhandler(403)
    def error_403(e):
        try:
            from app.services.audit_service import log_security_event
            log_security_event('forbidden_access',
                              session.get('user_id', 'anonymous'),
                              session.get('role', 'unknown'),
                              request.remote_addr,
                              {'url': request.url, 'error': str(e)})
        except:
            pass
        return rt('errors/403.html'), 403

    @app.errorhandler(404)
    def error_404(e):
        return rt('errors/404.html'), 404

    @app.errorhandler(500)
    def error_500(e):
        print(f"Erreur 500: {e}")
        return rt('errors/500.html'), 500
    
    return app