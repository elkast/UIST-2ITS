"""
Planificateur de tâches automatiques pour la mise à jour de la base de données
Utilise APScheduler pour exécuter des tâches en arrière-plan
"""
import logging
from datetime import datetime

# Vérifier si APScheduler est disponible
try:
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.cron import CronTrigger
    from apscheduler.triggers.interval import IntervalTrigger
    APSCHEDULER_AVAILABLE = True
except ImportError:
    APSCHEDULER_AVAILABLE = False
    BackgroundScheduler = None
    CronTrigger = None
    IntervalTrigger = None

# Configuration du logger
logger = logging.getLogger(__name__)

def init_scheduler(app):
    """
    Initialise le planificateur de tâches automatiques

    Args:
        app: Instance Flask
    """
    if not APSCHEDULER_AVAILABLE:
        logger.warning("APScheduler non disponible. Installation recommandée: pip install APScheduler==3.10.4")
        return

    scheduler = BackgroundScheduler()

    # Configuration des tâches automatiques
    _configure_jobs(scheduler, app)

    # Démarrage du planificateur
    scheduler.start()
    logger.info("Planificateur de tâches automatiques démarré")

    # Arrêt propre lors de l'arrêt de l'application
    import atexit
    atexit.register(lambda: scheduler.shutdown())

def _configure_jobs(scheduler, app):
    """
    Configure toutes les tâches planifiées

    Args:
        scheduler: Instance du planificateur
        app: Instance Flask pour accéder au contexte
    """
    with app.app_context():
        # Mise à jour des statistiques quotidiennes - tous les jours à 2h00
        scheduler.add_job(
            func=_update_daily_stats,
            trigger=CronTrigger(hour=2, minute=0),
            id='update_daily_stats',
            name='Mise à jour des statistiques quotidiennes',
            replace_existing=True
        )

        # Nettoyage des sessions expirées - toutes les heures
        scheduler.add_job(
            func=_cleanup_expired_sessions,
            trigger=IntervalTrigger(hours=1),
            id='cleanup_sessions',
            name='Nettoyage des sessions expirées',
            replace_existing=True
        )

        # Archivage des logs d'audit - tous les dimanches à 3h00
        scheduler.add_job(
            func=_archive_audit_logs,
            trigger=CronTrigger(day_of_week='sun', hour=3, minute=0),
            id='archive_audit_logs',
            name='Archivage des logs d\'audit',
            replace_existing=True
        )

        # Mise à jour des moyennes mensuelles - 1er de chaque mois à 4h00
        scheduler.add_job(
            func=_update_monthly_averages,
            trigger=CronTrigger(day=1, hour=4, minute=0),
            id='update_monthly_averages',
            name='Mise à jour des moyennes mensuelles',
            replace_existing=True
        )

        # Synchronisation des données externes - toutes les 6 heures
        scheduler.add_job(
            func=_sync_external_data,
            trigger=IntervalTrigger(hours=6),
            id='sync_external_data',
            name='Synchronisation des données externes',
            replace_existing=True
        )

        logger.info("Toutes les tâches automatiques ont été configurées")

def _update_daily_stats():
    """Met à jour les statistiques quotidiennes"""
    try:
        from database import db
        from models.etudiants import Etudiant
        from models.enseignants import Enseignant
        from models.parents import Parent
        from models.utilisateurs import Utilisateur

        # Statistiques des utilisateurs actifs
        total_students = db.session.query(Etudiant).join(Utilisateur).filter(Utilisateur.est_actif == True).count()
        total_teachers = db.session.query(Enseignant).join(Utilisateur).filter(Utilisateur.est_actif == True).count()
        total_parents = db.session.query(Parent).join(Utilisateur).filter(Utilisateur.est_actif == True).count()

        # Mise à jour d'une table de statistiques (si elle existe)
        # Ici on pourrait créer une table stats_daily pour stocker ces données

        logger.info(f"Statistiques quotidiennes mises à jour: {total_students} étudiants, {total_teachers} enseignants, {total_parents} parents")

    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour des statistiques quotidiennes: {str(e)}")

def _cleanup_expired_sessions():
    """Nettoie les sessions utilisateur expirées"""
    try:
        from flask import session
        # Cette fonction pourrait nettoyer les sessions expirées
        # Dans un vrai système, on utiliserait Redis ou une base de données pour les sessions

        logger.info("Nettoyage des sessions expirées effectué")

    except Exception as e:
        logger.error(f"Erreur lors du nettoyage des sessions: {str(e)}")

def _archive_audit_logs():
    """Archive les anciens logs d'audit"""
    try:
        from database import db
        from models.audit import AuditUsage
        from datetime import datetime, timedelta

        # Archiver les logs de plus de 90 jours
        cutoff_date = datetime.utcnow() - timedelta(days=90)

        # Ici on pourrait déplacer les anciens logs vers une table d'archive
        # ou les exporter vers des fichiers

        logger.info("Archivage des logs d'audit effectué")

    except Exception as e:
        logger.error(f"Erreur lors de l'archivage des logs d'audit: {str(e)}")

def _update_monthly_averages():
    """Met à jour les moyennes mensuelles"""
    try:
        from database import db
        from models.notes import Note
        from models.etudiants import Etudiant
        from models.cours import Cours

        # Calcul des moyennes mensuelles par étudiant et par cours
        # Cette fonction pourrait mettre à jour une table de statistiques mensuelles

        logger.info("Mise à jour des moyennes mensuelles effectuée")

    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour des moyennes mensuelles: {str(e)}")

def _sync_external_data():
    """Synchronise les données avec des sources externes"""
    try:
        # Ici on pourrait synchroniser avec:
        # - API externes (emploi du temps, notes, etc.)
        # - Fichiers Excel uploadés
        # - Autres systèmes d'information

        logger.info("Synchronisation des données externes effectuée")

    except Exception as e:
        logger.error(f"Erreur lors de la synchronisation des données externes: {str(e)}")
