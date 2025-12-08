"""
Module de gestion de la connexion à la base de données MySQL
Fournit des fonctions utilitaires pour exécuter des requêtes
"""
import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

load_dotenv()

def obtenir_connexion():
    """
    Établit et retourne une connexion à la base de données MySQL
    
    Returns:
        mysql.connector.connection.MySQLConnection: Connexion à la DB ou None en cas d'erreur
    """
    try:
        connexion = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', ''),
            database=os.getenv('DB_NAME', 'UIST_2ITS'),
            charset='utf8mb4',
            collation='utf8mb4_unicode_ci'
        )
        return connexion
    except Error as e:
        print(f"Erreur de connexion à MySQL: {e}")
        return None

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
    connexion = obtenir_connexion()
    if not connexion:
        return None if obtenir_resultats else 0
    
    try:
        curseur = connexion.cursor(dictionary=True)
        curseur.execute(requete, parametres or ())
        
        if obtenir_resultats:
            resultats = curseur.fetchall()
            curseur.close()
            connexion.close()
            return resultats
        else:
            connexion.commit()
            dernier_id = curseur.lastrowid
            lignes_affectees = curseur.rowcount
            curseur.close()
            connexion.close()
            return dernier_id if dernier_id > 0 else lignes_affectees
            
    except Error as e:
        print(f"Erreur lors de l'exécution de la requête: {e}")
        if connexion:
            connexion.rollback()
            connexion.close()
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