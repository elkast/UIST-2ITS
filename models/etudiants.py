"""
Modèle Étudiants - Profil étudiant lié aux utilisateurs
"""
from database import db
from datetime import datetime

class Etudiant(db.Model):
    """Table etudiants - Profils étudiants"""
    __tablename__ = 'etudiants'
    
    id_etudiant = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_user = db.Column(db.Integer, db.ForeignKey('utilisateurs.id_user'), unique=True, nullable=False, index=True)
    id_filiere = db.Column(db.Integer, db.ForeignKey('filieres.id_filiere'), nullable=False, index=True)
    date_naissance = db.Column(db.Date, nullable=True)
    adresse = db.Column(db.Text, nullable=True)
    date_inscription = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Etudiant {self.id_etudiant}>'

# ============================================================================
# FONCTIONS PROCÉDURALES - GESTION DES ÉTUDIANTS
# ============================================================================

def creer_etudiant(id_user, id_filiere, date_naissance=None, adresse=None):
    """
    Crée un profil étudiant
    
    Args:
        id_user: ID de l'utilisateur
        id_filiere: ID de la filière
        date_naissance: Date de naissance (optionnel)
        adresse: Adresse (optionnel)
    
    Returns:
        dict: {'success': bool, 'etudiant_id': int, 'message': str}
    """
    try:
        # Vérifier que l'utilisateur existe et est un étudiant
        from models.utilisateurs import obtenir_utilisateur_par_id
        user = obtenir_utilisateur_par_id(id_user)
        if not user or user.role != 'ETUDIANT':
            return {'success': False, 'message': 'Utilisateur invalide ou non étudiant'}
        
        # Vérifier unicité (un utilisateur = un étudiant)
        if obtenir_etudiant_par_user_id(id_user):
            return {'success': False, 'message': 'Profil étudiant déjà existant'}
        
        # Vérifier existence filière
        from models.filieres import obtenir_filiere_par_id
        if not obtenir_filiere_par_id(id_filiere):
            return {'success': False, 'message': 'Filière inexistante'}
        
        etudiant = Etudiant(
            id_user=id_user,
            id_filiere=id_filiere,
            date_naissance=date_naissance,
            adresse=adresse
        )
        
        db.session.add(etudiant)
        db.session.commit()
        
        return {
            'success': True,
            'etudiant_id': etudiant.id_etudiant,
            'message': 'Étudiant créé avec succès'
        }
    
    except Exception as e:
        db.session.rollback()
        return {'success': False, 'message': f'Erreur: {str(e)}'}

def obtenir_etudiant_par_id(etudiant_id):
    """Récupère un étudiant par son ID"""
    return db.session.get(Etudiant, etudiant_id)

def obtenir_etudiant_par_user_id(user_id):
    """Récupère un étudiant par l'ID utilisateur"""
    return db.session.query(Etudiant).filter_by(id_user=user_id).first()

def obtenir_etudiant_par_matricule(matricule):
    """
    Récupère un étudiant par le matricule utilisateur
    
    Returns:
        Etudiant ou None
    """
    from models.utilisateurs import Utilisateur
    
    result = db.session.query(Etudiant).join(
        Utilisateur, Etudiant.id_user == Utilisateur.id_user
    ).filter(Utilisateur.matricule == matricule).first()
    
    return result

def lister_etudiants_par_filiere(id_filiere):
    """Liste tous les étudiants d'une filière"""
    return db.session.query(Etudiant).filter_by(id_filiere=id_filiere).all()

def obtenir_infos_completes_etudiant(etudiant_id):
    """
    Récupère toutes les infos d'un étudiant (user + filière)
    
    Returns:
        dict avec etudiant, user, filiere ou None
    """
    from models.utilisateurs import Utilisateur
    from models.filieres import Filiere
    
    result = db.session.query(Etudiant, Utilisateur, Filiere).join(
        Utilisateur, Etudiant.id_user == Utilisateur.id_user
    ).join(
        Filiere, Etudiant.id_filiere == Filiere.id_filiere
    ).filter(Etudiant.id_etudiant == etudiant_id).first()
    
    if result:
        etudiant, user, filiere = result
        return {
            'etudiant': etudiant,
            'user': user,
            'filiere': filiere
        }
    return None

def compter_etudiants_filiere(id_filiere):
    """Compte le nombre d'étudiants dans une filière"""
    return db.session.query(Etudiant).filter_by(id_filiere=id_filiere).count()

def modifier_etudiant(etudiant_id, **kwargs):
    """
    Modifie un étudiant existant
    
    Args:
        etudiant_id: ID de l'étudiant
        **kwargs: Champs à modifier
    
    Returns:
        dict: {'success': bool, 'message': str}
    """
    try:
        etudiant = obtenir_etudiant_par_id(etudiant_id)
        if not etudiant:
            return {'success': False, 'message': 'Étudiant introuvable'}
        
        for key, value in kwargs.items():
            if hasattr(etudiant, key):
                setattr(etudiant, key, value)
        
        db.session.commit()
        return {'success': True, 'message': 'Étudiant modifié avec succès'}
    
    except Exception as e:
        db.session.rollback()
        return {'success': False, 'message': f'Erreur: {str(e)}'}
