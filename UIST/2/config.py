"""
Configuration de l'application UIST-2ITS
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuration de base"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production-2025')
    
    # Base de données SQLite3
    DB_PATH = os.getenv('DB_PATH', 'database/uist_2its.db')
    
    # Session 
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 7200  # 2 heures
    
    # Upload
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max
    ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'csv', 'pdf'}
    
    # PDF Generation
    BULLETINS_FOLDER = 'static/bulletins'
    PV_FOLDER = 'static/pv'

class DeveloppementConfig(Config):
    """Configuration pour le développement"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Configuration pour la production"""
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True  # HTTPS uniquement

class TestConfig(Config):
    """Configuration pour les tests"""
    TESTING = True
    DB_PATH = 'database/test_uist_2its.db'

# Dictionnaire des configurations
configurations = {
    'developpement': DeveloppementConfig,
    'production': ProductionConfig,
    'test': TestConfig,
    'default': DeveloppementConfig
}

def obtenir_config(nom_environnement=None):
    """
    Obtient la configuration selon l'environnement
    
    Args:
        nom_environnement (str): Nom de l'environnement
    
    Returns:
        Config: Classe de configuration
    """
    if nom_environnement is None:
        nom_environnement = os.getenv('FLASK_ENV', 'developpement')
    
    return configurations.get(nom_environnement, DeveloppementConfig)