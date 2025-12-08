"""
Configuration de l'application UIST-Planify
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuration de base"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'cle_secrete_developpement_a_changer')
    
    # Base de données
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_NAME = os.getenv('DB_NAME', 'UIST_2ITS')
    
    # Session 
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 3600  # 1 heure

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
    DB_NAME = 'uist_planify_test'

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