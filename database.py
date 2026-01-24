"""
Configuration et initialisation de la base de données
Architecture compatible SQLite/PostgreSQL/MySQL
"""
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData

# Convention de nommage pour les contraintes
naming_convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=naming_convention)
db = SQLAlchemy(metadata=metadata)

def init_db(app):
    """
    Initialise la connexion à la base de données
    
    Args:
        app: Instance Flask
    """
    db.init_app(app)
    
    with app.app_context():
        # Importer tous les modèles
        import models.utilisateurs
        import models.etudiants
        import models.enseignants
        import models.parents
        import models.filieres
        import models.cours
        import models.salles
        import models.emploi_temps
        import models.notes
        import models.presences
        import models.bulletins
        import models.audit
        
        # Créer toutes les tables
        db.create_all()
        
        # Initialiser les données de base si nécessaire
        from helpers.init_data import initialiser_donnees_base
        initialiser_donnees_base()

def get_db():
    """Retourne l'instance de la base de données"""
    return db
