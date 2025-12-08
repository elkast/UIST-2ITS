"""
Initialisation de l'application Flask UIST-Planify
Configure l'application et enregistre les blueprints
"""
from flask import Flask
from dotenv import load_dotenv
import os

# Charger les variables d'environnement
load_dotenv()

def creer_application():
    """
    Fonction factory pour créer et configurer l'application Flask
    
    Returns:
        Flask: Instance de l'application configurée
    """
    app = Flask(__name__, 
                template_folder='../templates',
                static_folder='../static')
    
    # Configuration de l'application
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'cle_secrete_par_defaut')
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    
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
    
    # Enregistrement des blueprints
    from app.blueprints.auth.routes import auth_bp
    from app.blueprints.admin.routes import admin_bp
    from app.blueprints.edt.routes import edt_bp
    from app.blueprints.enseignant.routes import enseignant_bp
    from app.blueprints.etudiant.routes import etudiant_bp
    from app.blueprints.parent.routes import parent_bp
    from app.blueprints.api.routes import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(edt_bp, url_prefix='/edt')
    app.register_blueprint(enseignant_bp, url_prefix='/enseignant')
    app.register_blueprint(etudiant_bp, url_prefix='/etudiant')
    app.register_blueprint(parent_bp, url_prefix='/parent')
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Route d'accueil
    @app.route('/')
    def index():
        from flask import redirect, url_for
        return redirect(url_for('auth.connexion'))
    
    # Route de diagnostic
    @app.route('/diagnostic')
    def diagnostic():
        from flask import render_template
        return render_template('diagnostic.html')

    # Pages d'erreurs customisées
    from flask import render_template as rt

    @app.errorhandler(401)
    def error_401(e):
        return rt('errors/401.html'), 401

    @app.errorhandler(403)
    def error_403(e):
        return rt('errors/403.html'), 403

    @app.errorhandler(404)
    def error_404(e):
        return rt('errors/404.html'), 404

    @app.errorhandler(500)
    def error_500(e):
        return rt('errors/500.html'), 500
    
    return app