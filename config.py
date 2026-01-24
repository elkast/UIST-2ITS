"""
Configuration centrale de l'application UIST-2ITS
Gestion des environnements : développement, test, production
"""
import os
from datetime import timedelta
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

class Config:
    """Configuration de base partagée"""
    
    # Clés secrètes
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 3600)))
    
    # Base de données - Compatible SQLite/PostgreSQL/MySQL
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///uist_planify.db')
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False  # Mettre True pour debug SQL
    
    # Paramètres de session
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)
    
    # Upload de fichiers
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16MB
    ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'pdf'}
    
    # Paramètres académiques
    ANNEE_ACADEMIQUE = os.getenv('ANNEE_ACADEMIQUE', '2025-2026')
    
    # Pagination
    ITEMS_PER_PAGE = 20
    
    # Charte graphique
    COULEURS = {
        'primaire': '#1A365D',      # Bleu institutionnel
        'secondaire': '#D4AF37',    # Or académique
        'texte': '#4A5568',         # Gris ardoise
        'succes': '#2F855A',        # Vert
        'alerte': '#C53030',        # Rouge
        'info': '#2B6CB0'           # Bleu info
    }

class DevelopmentConfig(Config):
    """Configuration développement"""
    DEBUG = True
    SQLALCHEMY_ECHO = True

class ProductionConfig(Config):
    """Configuration production"""
    DEBUG = False
    SQLALCHEMY_ECHO = False
    
    # En production, ces clés DOIVENT être définies dans l'environnement
    @classmethod
    def init_app(cls, app):
        assert os.getenv('SECRET_KEY'), "SECRET_KEY doit être définie en production"
        assert os.getenv('JWT_SECRET_KEY'), "JWT_SECRET_KEY doit être définie en production"

class TestConfig(Config):
    """Configuration tests"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

# Dictionnaire des configurations
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestConfig,
    'default': DevelopmentConfig
}
