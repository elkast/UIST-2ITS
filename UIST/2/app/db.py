"""
Module de gestion de la connexion à la base de données SQLite3
Fournit des fonctions utilitaires pour exécuter des requêtes
"""
import sqlite3
import os
from flask import g, current_app
from contextlib import contextmanager

def obtenir_connexion():
    """
    Établit et retourne une connexion à la base de données SQLite3
    
    Returns:
        sqlite3.Connection: Connexion à la DB
    """
    if 'db' not in g:
        db_path = current_app.config.get('DB_PATH', 'database/uist_2its.db')
        
        # Créer le dossier database s'il n'existe pas
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        g.db = sqlite3.connect(
            db_path,
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
        # Activer les contraintes de clés étrangères
        g.db.execute('PRAGMA foreign_keys = ON')
    
    return g.db

def fermer_connexion(e=None):
    """Ferme la connexion à la base de données"""
    db = g.pop('db', None)
    
    if db is not None:
        db.close()

def init_db():
    """Initialise la base de données avec le schéma"""
    db = obtenir_connexion()
    
    schema_path = os.path.join(os.path.dirname(__file__), '..', 'database', 'schema_complete.sql')
    with open(schema_path, 'r', encoding='utf-8') as f:
        db.executescript(f.read())
    
    db.commit()

def executer_requete(requete, parametres=None, obtenir_resultats=False):
    """
    Exécute une requête SQL (SELECT, INSERT, UPDATE, DELETE)
    
    Args:
        requete (str): La requête SQL à exécuter
        parametres (tuple): Les paramètres de la requête (optionnel)
        obtenir_resultats (bool): True pour SELECT, False pour INSERT/UPDATE/DELETE
    
    Returns:
        list ou int: Liste de résultats pour SELECT, ID inséré ou nombre de lignes affectées pour autres
    """
    try:
        db = obtenir_connexion()
        cur = db.execute(requete, parametres or ())
        
        if obtenir_resultats:
            resultats = [dict(row) for row in cur.fetchall()]
            return resultats
        else:
            db.commit()
            return cur.lastrowid if cur.lastrowid > 0 else cur.rowcount
            
    except sqlite3.Error as e:
        print(f"Erreur lors de l'exécution de la requête: {e}")
        db.rollback()
        return None if obtenir_resultats else 0

def executer_requete_unique(requete, parametres=None):
    """
    Exécute une requête SELECT et retourne un seul résultat
    
    Args:
        requete (str): La requête SQL à exécuter
        parametres (tuple): Les paramètres de la requête (optionnel)
    
    Returns:
        dict: Un seul résultat ou None
    """
    resultats = executer_requete(requete, parametres, obtenir_resultats=True)
    return resultats[0] if resultats and len(resultats) > 0 else None

def init_app(app):
    """Initialise la base de données avec l'application Flask"""
    app.teardown_appcontext(fermer_connexion)