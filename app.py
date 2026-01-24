"""
Point d'entrée principal de l'application UIST-2ITS
Architecture MVT procédurale avec Flask Blueprints
"""
import os
from flask import Flask, render_template, redirect, url_for
from config import config
from database import init_db, db
from datetime import datetime
from scheduler import init_scheduler

def create_app(config_name=None):
    """
    Factory pour créer l'application Flask

    Args:
        config_name: Nom de la configuration (development, production, testing)

    Returns:
        Instance Flask configurée
    """
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialiser la base de données
    init_db(app)

    # Initialiser le planificateur de tâches automatiques
    init_scheduler(app)

    # Enregistrer les blueprints (modules)
    register_blueprints(app)

    # Enregistrer les filtres Jinja personnalisés
    register_template_filters(app)

    # Gestionnaires d'erreurs
    register_error_handlers(app)

    # Route d'accueil
    @app.route('/')
    def index():
        """Page d'accueil - Redirection vers login"""
        return redirect(url_for('auth.login'))

    return app

def register_blueprints(app):
    """Enregistre tous les blueprints de l'application"""
    from blueprints.auth import auth_bp
    from blueprints.super_admin import super_admin_bp
    from blueprints.directeur import directeur_bp
    from blueprints.gestion1 import gestion1_bp
    from blueprints.gestion2 import gestion2_bp
    from blueprints.gestion3 import gestion3_bp
    from blueprints.enseignant import enseignant_bp
    from blueprints.etudiant import etudiant_bp
    from blueprints.parent import parent_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(super_admin_bp, url_prefix='/super-admin')
    app.register_blueprint(directeur_bp, url_prefix='/directeur')
    app.register_blueprint(gestion1_bp, url_prefix='/gestion1')
    app.register_blueprint(gestion2_bp, url_prefix='/gestion2')
    app.register_blueprint(gestion3_bp, url_prefix='/gestion3')
    app.register_blueprint(enseignant_bp, url_prefix='/enseignant')
    app.register_blueprint(etudiant_bp, url_prefix='/etudiant')
    app.register_blueprint(parent_bp, url_prefix='/parent')

def register_template_filters(app):
    """Enregistre les filtres Jinja personnalisés"""

    @app.template_filter('format_date')
    def format_date(date, format='%d/%m/%Y'):
        """Formate une date"""
        if date is None:
            return ''
        if isinstance(date, str):
            return date
        return date.strftime(format)

    @app.template_filter('format_note')
    def format_note(note):
        """Formate une note sur 20"""
        if note is None:
            return '-'
        return f"{note:.2f}"

    @app.template_filter('statut_badge')
    def statut_badge(statut):
        """Retourne la classe CSS pour un badge de statut"""
        badges = {
            'Valide': 'success',
            'En attente': 'info',
            'Rejeté': 'danger',
            'Present': 'success',
            'Absent': 'danger',
            'Retard': 'warning'
        }
        return badges.get(statut, 'secondary')

def register_error_handlers(app):
    """Enregistre les gestionnaires d'erreurs HTTP"""

    @app.errorhandler(403)
    def forbidden(error):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def not_found(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000)
