"""
Fonctions utilitaires pour l'application UIST-Planify
Gestion des rôles et génération de matricules
"""
from functools import wraps
from flask import session, redirect, url_for, flash, abort
from flask_login import current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta

# Hiérarchie des rôles UniCampus (niveau décroissant)
ROLES_HIERARCHY = {
    # Niveau 1: Root
    'SUPER_ADMIN': 10,
    'sous_admin': 10,  # Compatibilité

    # Niveau 2: Administration
    'ADMIN': 8,
    'administration': 8,  # Compatibilité

    # Niveau 3: Gestionnaires
    'DIRECTEUR': 6,
    'GESTIONNAIRE_PV': 5,
    'GESTIONNAIRE_EXAMENS': 5,
    'GESTIONNAIRE_EDT': 5,
    'GESTIONNAIRE_PRESENCES': 5,

    # Niveau 4: Enseignants
    'ENSEIGNANT': 3,
    'enseignant': 3,  # Compatibilité

    # Niveau 5: Étudiants et Parents
    'ETUDIANT': 1,
    'PARENT': 1,
    'etudiant': 1,  # Compatibilité
    'parent': 1  # Compatibilité
}

def generer_matricule(role):
    """
    Génère un matricule unique selon le rôle (support nouveaux rôles UniCampus)
    
    Args:
        role (str): Role de l'utilisateur (nouveaux ou anciens)
    
    Returns:
        str: Matricule généré (ex: E2025001, P2025001, DIR2025001)
    """
    from app.db import executer_requete_unique
    
    # Préfixes selon le rôle (support anciens et nouveaux)
    prefixes = {
        # Nouveaux rôles UniCampus
        'SUPER_ADMIN': 'SA',
        'ADMIN': 'A',
        'DIRECTEUR': 'DIR',
        'GESTIONNAIRE_PV': 'GPV',
        'GESTIONNAIRE_EXAMENS': 'GEX',
        'GESTIONNAIRE_EDT': 'GEDT',
        'GESTIONNAIRE_PRESENCES': 'GPRE',
        'ENSEIGNANT': 'P',
        'ETUDIANT': 'E',
        'PARENT': 'PAR',
        # Anciens pour compatibilité
        'etudiant': 'E',
        'enseignant': 'P',
        'administration': 'A',
        'sous_admin': 'SA',
        'parent': 'PAR'
    }
    
    prefix = prefixes.get(role, 'U')
    annee = datetime.now().year
    
    # Trouver le dernier matricule pour ce préfixe
    requete = """
        SELECT matricule FROM Utilisateurs 
        WHERE matricule LIKE %s 
        ORDER BY matricule DESC 
        LIMIT 1
    """
    pattern = f"{prefix}{annee}%"
    dernier = executer_requete_unique(requete, (pattern,))
    
    if dernier:
        # Extraire le numéro et incrémenter
        try:
            dernier_num = int(dernier['matricule'].replace(prefix + str(annee), ''))
            nouveau_num = dernier_num + 1
        except ValueError:
            nouveau_num = 1
    else:
        nouveau_num = 1
    
    return f"{prefix}{annee}{nouveau_num:04d}"


def role_required(allowed_roles):
    """
    Décorateur pour restreindre l'accès aux routes selon le rôle avec support de hiérarchie.
    Utilise Flask-Login si disponible, sinon retombe sur la session existante.
    
    SUPER_ADMIN et ADMIN ont accès à tout.
    Les autres rôles doivent être explicitement dans allowed_roles.

    Usage :
        @role_required(['SUPER_ADMIN', 'DIRECTEUR'])
        def ma_vue():
            ...
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 1) Vérification authentification
            is_auth = getattr(current_user, "is_authenticated", False)
            if is_auth:
                user_role = getattr(current_user, "role", None)
                user_id = getattr(current_user, "matricule", None)
            else:
                user_role = session.get("role")
                user_id = session.get("matricule")

            if not user_role:
                return abort(401)  # Non connecté / rôle absent

            # 2) Vérification du rôle avec hiérarchie
            # SUPER_ADMIN et ADMIN ont accès à tout
            if user_role in ['SUPER_ADMIN', 'sous_admin', 'ADMIN', 'administration']:
                return f(*args, **kwargs)
            
            # Pour les autres rôles, vérifier s'ils sont dans allowed_roles
            # Support des variantes de noms (majuscules/minuscules)
            role_variants = [user_role, user_role.upper(), user_role.lower()]
            
            if allowed_roles:
                has_access = any(variant in allowed_roles for variant in role_variants)
                if not has_access:
                    # Log minimal côté serveur pour audit
                    print(
                        f"ACCÈS REFUSÉ: {user_id or 'inconnu'} (rôle: {user_role}) a tenté d'accéder "
                        f"à une route protégée (rôles autorisés: {allowed_roles})."
                    )
                    return abort(403)

            return f(*args, **kwargs)

        return decorated_function

    return decorator

def calculer_duree_creneau(heure_debut, heure_fin):
    """
    Calcule la durée d'un créneau en heures
    
    Args:
        heure_debut (str ou time): Heure de début
        heure_fin (str ou time): Heure de fin
    
    Returns:
        float: Durée en heures
    """
    if isinstance(heure_debut, str):
        h_debut = datetime.strptime(heure_debut, '%H:%M')
        h_fin = datetime.strptime(heure_fin, '%H:%M')
    else:
        h_debut = datetime.combine(datetime.today(), heure_debut)
        h_fin = datetime.combine(datetime.today(), heure_fin)
    
    duree = h_fin - h_debut
    return duree.total_seconds() / 3600

def formater_taux_presence(heures_effectuees, heures_prevues):
    """
    Formate le taux de présence en pourcentage
    
    Args:
        heures_effectuees (float): Heures effectuées
        heures_prevues (float): Heures prévues
    
    Returns:
        str: Taux formaté (ex: "85.5%")
    """
    if heures_prevues == 0:
        return "0%"
    
    taux = (heures_effectuees / heures_prevues) * 100
    return f"{taux:.1f}%"

def connexion_requise(f):
    """
    Décorateur pour protéger les routes nécessitant une connexion
    
    Args:
        f: Fonction à décorer
    
    Returns:
        function: Fonction décorée
    """
    @wraps(f)
    def fonction_decoree(*args, **kwargs):
        if 'utilisateur_id' not in session:
            flash('Vous devez être connecté pour accéder à cette page.', 'warning')
            return redirect(url_for('auth.connexion'))
        return f(*args, **kwargs)
    return fonction_decoree

def role_requis(*roles_autorises):
    """
    Compatibilité ascendante : redirige vers le nouveau décorateur role_required.
    """
    return role_required(list(roles_autorises))


def obtenir_role_dashboard(role):
    """
    Retourne l'URL du dashboard approprié selon le rôle
    
    Args:
        role (str): Rôle de l'utilisateur
    
    Returns:
        str: Nom de la route du dashboard
    """
    dashboards = {
        'SUPER_ADMIN': 'admin.tableau_bord',
        'ADMIN': 'admin.tableau_bord',
        'DIRECTEUR': 'admin.directeur_dashboard',
        'GESTIONNAIRE_PV': 'admin.gestionnaire_pv_dashboard',
        'GESTIONNAIRE_EXAMENS': 'admin.gestionnaire_examens_dashboard',
        'GESTIONNAIRE_EDT': 'edt.gestionnaire_edt_dashboard',
        'GESTIONNAIRE_PRESENCES': 'admin.gestion_presences',
        'ENSEIGNANT': 'enseignant.tableau_bord',
        'ETUDIANT': 'etudiant.tableau_bord',
        'PARENT': 'parent.tableau_bord'
    }
    
    return dashboards.get(role, 'auth.connexion')

def get_role_display_name(role):
    """
    Retourne le nom d'affichage du rôle
    
    Args:
        role (str): Code du rôle
    
    Returns:
        str: Nom d'affichage
    """
    display_names = {
        'SUPER_ADMIN': 'Super Administrateur',
        'ADMIN': 'Administrateur',
        'DIRECTEUR': 'Directeur Académique',
        'GESTIONNAIRE_PV': 'Gestionnaire PV',
        'GESTIONNAIRE_EXAMENS': 'Gestionnaire Examens',
        'GESTIONNAIRE_EDT': 'Gestionnaire EDT',
        'GESTIONNAIRE_PRESENCES': 'Gestionnaire Présences',
        'ENSEIGNANT': 'Enseignant',
        'ETUDIANT': 'Étudiant',
        'PARENT': 'Parent'
    }
    return display_names.get(role, role)
