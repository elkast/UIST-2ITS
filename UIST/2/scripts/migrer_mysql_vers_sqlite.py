"""
Script de Migration MySQL vers SQLite3 - UIST-2ITS
Migre toutes les données de MySQL vers SQLite3 avec conversion des types
"""
import sqlite3
import sys
import os
from datetime import datetime

# Ajouter le chemin parent pour importer les modules de l'app
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

try:
    import mysql.connector
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False
    print("⚠️  MySQL Connector non installé. Installation requise: pip install mysql-connector-python")

class MigrateurBaseDonnees:
    """Gère la migration de MySQL vers SQLite3"""
    
    def __init__(self):
        self.mysql_conn = None
        self.sqlite_conn = None
        self.statistiques = {
            'tables_migrees': 0,
            'lignes_totales': 0,
            'erreurs': 0
        }
    
    def connecter_mysql(self, host='localhost', user='root', password='', database='uist_2its'):
        """Connexion à MySQL"""
        if not MYSQL_AVAILABLE:
            raise Exception("MySQL Connector non disponible")
        
        try:
            self.mysql_conn = mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database
            )
            print(f"✅ Connecté à MySQL: {database}")
            return True
        except Exception as e:
            print(f"❌ Erreur connexion MySQL: {e}")
            return False
    
    def connecter_sqlite(self, db_path='database/uist_2its.db'):
        """Connexion à SQLite3"""
        try:
            # Créer le dossier database s'il n'existe pas
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            
            self.sqlite_conn = sqlite3.connect(db_path)
            self.sqlite_conn.execute('PRAGMA foreign_keys = ON')
            print(f"✅ Connecté à SQLite: {db_path}")
            return True
        except Exception as e:
            print(f"❌ Erreur connexion SQLite: {e}")
            return False
    
    def convertir_valeur(self, valeur, type_colonne):
        """Convertit les valeurs MySQL en format SQLite"""
        if valeur is None:
            return None
        
        # Conversions spécifiques
        if isinstance(valeur, datetime):
            return valeur.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(valeur, bool):
            return 1 if valeur else 0
        elif isinstance(valeur, bytes):
            return valeur.decode('utf-8', errors='ignore')
        else:
            return valeur
    
    def migrer_table(self, nom_table):
        """Migre une table spécifique de MySQL vers SQLite"""
        try:
            mysql_cursor = self.mysql_conn.cursor(dictionary=True)
            sqlite_cursor = self.sqlite_conn.cursor()
            
            # Lire les données de MySQL
            mysql_cursor.execute(f"SELECT * FROM {nom_table}")
            rows = mysql_cursor.fetchall()
            
            if not rows:
                print(f"  ⚠️  {nom_table}: table vide")
                mysql_cursor.close()
                return 0
            
            # Préparer l'insertion SQLite
            colonnes = list(rows[0].keys())
            placeholders = ', '.join(['?' for _ in colonnes])
            insert_sql = f"INSERT OR IGNORE INTO {nom_table} ({', '.join(colonnes)}) VALUES ({placeholders})"
            
            # Insérer les données
            lignes_inserees = 0
            for row in rows:
                values = tuple(self.convertir_valeur(row[col], None) for col in colonnes)
                try:
                    sqlite_cursor.execute(insert_sql, values)
                    lignes_inserees += 1
                except sqlite3.IntegrityError as e:
                    self.statistiques['erreurs'] += 1
                    print(f"  ⚠️  Erreur insertion {nom_table}: {e}")
            
            self.sqlite_conn.commit()
            mysql_cursor.close()
            
            print(f"  ✅ {nom_table}: {lignes_inserees} lignes migrées")
            return lignes_inserees
            
        except Exception as e:
            print(f"  ❌ Erreur migration {nom_table}: {e}")
            return 0
    
    def executer_migration(self):
        """Exécute la migration complète"""
        print("\n🔄 Début de la migration MySQL → SQLite3\n")
        
        # Tables dans l'ordre respectant les contraintes de clés étrangères
        tables = [
            # Tables de base (sans FK)
            'Utilisateurs',
            
            # Tables liées aux utilisateurs
            'Enseignants',
            'Etudiants',
            
            # Tables académiques
            'Filieres',
            'Salles',
            'Cours',
            
            # Relations et dépendances
            'Parents',
            'EmploiDuTemps',
            'Notes',
            'Presences',
            'Bulletins',
            
            # Gestion et workflows
            'Conflits',
            'ImportNotes',
            'StatutsEnseignants',
            'Messages',
            
            # Audit et monitoring
            'UsageAudit',
            'ActiviteUtilisateurs',
            'NotificationsWorkflow',
            'BlocagesWorkflow',
            'UtilisateursActifs'
        ]
        
        for table in tables:
            lignes = self.migrer_table(table)
            if lignes > 0:
                self.statistiques['tables_migrees'] += 1
                self.statistiques['lignes_totales'] += lignes
        
        self.afficher_rapport()
    
    def afficher_rapport(self):
        """Affiche le rapport de migration"""
        print("\n" + "="*60)
        print("📊 RAPPORT DE MIGRATION")
        print("="*60)
        print(f"Tables migrées:     {self.statistiques['tables_migrees']}")
        print(f"Lignes totales:     {self.statistiques['lignes_totales']}")
        print(f"Erreurs:            {self.statistiques['erreurs']}")
        print("="*60)
        
        if self.statistiques['erreurs'] == 0:
            print("✅ Migration terminée avec succès!")
        else:
            print(f"⚠️  Migration terminée avec {self.statistiques['erreurs']} erreur(s)")
        print("")
    
    def fermer_connexions(self):
        """Ferme les connexions"""
        if self.mysql_conn:
            self.mysql_conn.close()
            print("✅ Connexion MySQL fermée")
        
        if self.sqlite_conn:
            self.sqlite_conn.close()
            print("✅ Connexion SQLite fermée")


def main():
    """Fonction principale"""
    print("\n" + "="*60)
    print("🔄 MIGRATION BASE DE DONNÉES UIST-2ITS")
    print("   MySQL → SQLite3")
    print("="*60 + "\n")
    
    if not MYSQL_AVAILABLE:
        print("❌ MySQL Connector non installé.")
        print("   Installation: pip install mysql-connector-python")
        return
    
    # Configuration MySQL
    print("Configuration MySQL:")
    host = input("  Host (localhost): ").strip() or "localhost"
    user = input("  User (root): ").strip() or "root"
    password = input("  Password: ").strip()
    database = input("  Database (uist_2its): ").strip() or "uist_2its"
    
    # Configuration SQLite
    print("\nConfiguration SQLite:")
    sqlite_path = input("  Chemin DB (database/uist_2its.db): ").strip() or "database/uist_2its.db"
    
    # Confirmation
    print(f"\n⚠️  La base SQLite '{sqlite_path}' sera créée/mise à jour.")
    confirmer = input("Continuer? (oui/non): ").strip().lower()
    
    if confirmer not in ['oui', 'o', 'yes', 'y']:
        print("❌ Migration annulée")
        return
    
    # Créer le migrateur
    migrateur = MigrateurBaseDonnees()
    
    # Connecter aux bases
    if not migrateur.connecter_mysql(host, user, password, database):
        return
    
    if not migrateur.connecter_sqlite(sqlite_path):
        migrateur.fermer_connexions()
        return
    
    # Exécuter la migration
    try:
        migrateur.executer_migration()
    except Exception as e:
        print(f"\n❌ Erreur lors de la migration: {e}")
    finally:
        migrateur.fermer_connexions()


if __name__ == '__main__':
    main()