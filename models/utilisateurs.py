"""
Modèle Utilisateurs - Table centrale pour l'authentification
Gère les 8 rôles du système avec hiérarchie de privilèges
"""
from database import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class Utilisateur(db.Model):
    """
    Table utilisateurs - Authentification et rôles
    """
    __tablename__ = 'utilisateurs'
    
    id_user = db.Column(db.Integer, primary_key=True, autoincrement=True)
    matricule = db.Column(db.String(20), unique=True, nullable=False, index=True)
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    mot_de_passe = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, index=True)
    est_actif = db.Column(db.Boolean, default=True)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    derniere_connexion = db.Column(db.DateTime, nullable=True)
    
    def __repr__(self):
        return f'<Utilisateur {self.matricule} - {self.nom} {self.prenom}>'

# ============================================================================
# FONCTIONS PROCÉDURALES - GESTION DES UTILISATEURS
# ============================================================================

def creer_utilisateur(matricule, nom, prenom, email, mot_de_passe, role):
    """
    Crée un nouvel utilisateur avec hashage du mot de passe
    
    Args:
        matricule: Matricule unique (format UIST-YYYY-XXXXX)
        nom: Nom de famille
        prenom: Prénom
        email: Email unique
        mot_de_passe: Mot de passe en clair (sera hashé)
        role: Rôle parmi ROLES_VALIDES
    
    Returns:
        dict: {'success': bool, 'user_id': int, 'message': str}
    """
    try:
        # Vérifier unicité email
        if obtenir_utilisateur_par_email(email):
            return {'success': False, 'message': 'Email déjà utilisé'}
        
        # Vérifier unicité matricule
        if obtenir_utilisateur_par_matricule(matricule):
            return {'success': False, 'message': 'Matricule déjà utilisé'}
        
        # Créer utilisateur
        user = Utilisateur(
            matricule=matricule,
            nom=nom,
            prenom=prenom,
            email=email,
            mot_de_passe=generate_password_hash(mot_de_passe),
            role=role
        )
        
        db.session.add(user)
        db.session.commit()
        
        return {
            'success': True,
            'user_id': user.id_user,
            'message': 'Utilisateur créé avec succès'
        }
    
    except Exception as e:
        db.session.rollback()
        return {'success': False, 'message': f'Erreur: {str(e)}'}

def obtenir_utilisateur_par_id(user_id):
    """
    Récupère un utilisateur par son ID
    
    Args:
        user_id: ID de l'utilisateur
    
    Returns:
        Utilisateur ou None
    """
    return db.session.get(Utilisateur, user_id)

def obtenir_utilisateur_par_email(email):
    """
    Récupère un utilisateur par son email
    
    Args:
        email: Email de l'utilisateur
    
    Returns:
        Utilisateur ou None
    """
    return db.session.query(Utilisateur).filter_by(email=email).first()

def obtenir_utilisateur_par_matricule(matricule):
    """
    Récupère un utilisateur par son matricule
    
    Args:
        matricule: Matricule de l'utilisateur
    
    Returns:
        Utilisateur ou None
    """
    return db.session.query(Utilisateur).filter_by(matricule=matricule).first()

def verifier_mot_de_passe(user, mot_de_passe):
    """
    Vérifie si le mot de passe correspond au hash stocké
    
    Args:
        user: Instance Utilisateur
        mot_de_passe: Mot de passe à vérifier
    
    Returns:
        bool
    """
    return check_password_hash(user.mot_de_passe, mot_de_passe)

def mettre_a_jour_derniere_connexion(user_id):
    """
    Met à jour la date de dernière connexion
    
    Args:
        user_id: ID de l'utilisateur
    """
    user = obtenir_utilisateur_par_id(user_id)
    if user:
        user.derniere_connexion = datetime.utcnow()
        db.session.commit()

def lister_utilisateurs_par_role(role):
    """
    Liste tous les utilisateurs d'un rôle donné
    
    Args:
        role: Rôle à filtrer
    
    Returns:
        Liste d'utilisateurs
    """
    return db.session.query(Utilisateur).filter_by(role=role, est_actif=True).all()

def desactiver_utilisateur(user_id):
    """
    Désactive un utilisateur (soft delete)
    
    Args:
        user_id: ID de l'utilisateur
    
    Returns:
        dict: {'success': bool, 'message': str}
    """
    try:
        user = obtenir_utilisateur_par_id(user_id)
        if not user:
            return {'success': False, 'message': 'Utilisateur introuvable'}
        
        user.est_actif = False
        db.session.commit()
        return {'success': True, 'message': 'Utilisateur désactivé'}
    
    except Exception as e:
        db.session.rollback()
        return {'success': False, 'message': f'Erreur: {str(e)}'}

def reactiver_utilisateur(user_id):
    """
    Réactive un utilisateur désactivé
    
    Args:
        user_id: ID de l'utilisateur
    
    Returns:
        dict: {'success': bool, 'message': str}
    """
    try:
        user = obtenir_utilisateur_par_id(user_id)
        if not user:
            return {'success': False, 'message': 'Utilisateur introuvable'}
        
        user.est_actif = True
        db.session.commit()
        return {'success': True, 'message': 'Utilisateur réactivé'}
    
    except Exception as e:
        db.session.rollback()
        return {'success': False, 'message': f'Erreur: {str(e)}'}

def generer_matricule(role, annee=None):
    """
    Génère un matricule unique au format UIST-YYYY-XXXXX
    
    Args:
        role: Rôle de l'utilisateur
        annee: Année (par défaut année courante)
    
    Returns:
        str: Matricule généré
    """
    if annee is None:
        annee = datetime.now().year
    
    # Compter le nombre d'utilisateurs de ce rôle cette année
    prefix = f"UIST-{annee}-"
    count = db.session.query(Utilisateur).filter(
        Utilisateur.matricule.like(f"{prefix}%")
    ).count()
    
    return f"{prefix}{count + 1:05d}"

# Constantes pour les rôles et niveaux hiérarchiques
ROLES_VALIDES = [
    'SUPER_ADMIN',   # Niveau 5
    'DIRECTEUR',     # Niveau 4
    'GESTION_1',     # Niveau 3
    'GESTION_2',     # Niveau 3
    'GESTION_3',     # Niveau 3
    'ENSEIGNANT',    # Niveau 2
    'ETUDIANT',      # Niveau 1
    'PARENT'         # Niveau 1
]

HIERARCHIE_ROLES = {
    'SUPER_ADMIN': 5,
    'DIRECTEUR': 4,
    'GESTION_1': 3,
    'GESTION_2': 3,
    'GESTION_3': 3,
    'ENSEIGNANT': 2,
    'ETUDIANT': 1,
    'PARENT': 1
}

def obtenir_niveau_role(role):
    """Retourne le niveau hiérarchique d'un rôle"""
    return HIERARCHIE_ROLES.get(role, 0)

def peut_gerer_role(role_acteur, role_cible):
    """
    Vérifie si un acteur peut gérer un rôle cible
    
    Args:
        role_acteur: Rôle de l'acteur effectuant l'action
        role_cible: Rôle de l'utilisateur cible
    
    Returns:
        bool
    """
    return obtenir_niveau_role(role_acteur) > obtenir_niveau_role(role_cible)
