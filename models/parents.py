"""
Modèle Parents - Profil parent lié aux utilisateurs et étudiants
"""
from database import db
from datetime import datetime

class Parent(db.Model):
    """Table parents - Profils parents"""
    __tablename__ = 'parents'
    
    id_parent = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_user = db.Column(db.Integer, db.ForeignKey('utilisateurs.id_user'), unique=True, nullable=False, index=True)
    telephone = db.Column(db.String(20), nullable=True)
    profession = db.Column(db.String(100), nullable=True)
    
    def __repr__(self):
        return f'<Parent {self.id_parent}>'

class ParenteLiaison(db.Model):
    """Table parente_liaison - Relation N:N entre parents et étudiants"""
    __tablename__ = 'parente_liaison'
    
    id_liaison = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_parent = db.Column(db.Integer, db.ForeignKey('parents.id_parent'), nullable=False, index=True)
    id_etudiant = db.Column(db.Integer, db.ForeignKey('etudiants.id_etudiant'), nullable=False, index=True)
    lien_parente = db.Column(db.String(20), nullable=False)  # Père, Mère, Tuteur
    date_liaison = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Liaison Parent {self.id_parent} - Etudiant {self.id_etudiant}>'

# ============================================================================
# FONCTIONS PROCÉDURALES - GESTION DES PARENTS
# ============================================================================

def creer_parent(id_user, telephone=None, profession=None):
    """
    Crée un profil parent
    
    Args:
        id_user: ID de l'utilisateur
        telephone: Numéro de téléphone
        profession: Profession
    
    Returns:
        dict: {'success': bool, 'parent_id': int, 'message': str}
    """
    try:
        from models.utilisateurs import obtenir_utilisateur_par_id
        user = obtenir_utilisateur_par_id(id_user)
        if not user or user.role != 'PARENT':
            return {'success': False, 'message': 'Utilisateur invalide ou non parent'}
        
        if obtenir_parent_par_user_id(id_user):
            return {'success': False, 'message': 'Profil parent déjà existant'}
        
        parent = Parent(
            id_user=id_user,
            telephone=telephone,
            profession=profession
        )
        
        db.session.add(parent)
        db.session.commit()
        
        return {
            'success': True,
            'parent_id': parent.id_parent,
            'message': 'Parent créé avec succès'
        }
    
    except Exception as e:
        db.session.rollback()
        return {'success': False, 'message': f'Erreur: {str(e)}'}

def obtenir_parent_par_id(parent_id):
    """Récupère un parent par son ID"""
    return db.session.get(Parent, parent_id)

def obtenir_parent_par_user_id(user_id):
    """Récupère un parent par l'ID utilisateur"""
    return db.session.query(Parent).filter_by(id_user=user_id).first()

# ============================================================================
# FONCTIONS - LIAISONS PARENT-ÉTUDIANT
# ============================================================================

def creer_liaison_parent_etudiant(id_parent, id_etudiant, lien_parente):
    """
    Crée une liaison entre un parent et un étudiant
    
    Args:
        id_parent: ID du parent
        id_etudiant: ID de l'étudiant
        lien_parente: Type de lien (Père, Mère, Tuteur)
    
    Returns:
        dict: {'success': bool, 'message': str}
    """
    try:
        # Vérifier existence parent et étudiant
        if not obtenir_parent_par_id(id_parent):
            return {'success': False, 'message': 'Parent introuvable'}
        
        from models.etudiants import obtenir_etudiant_par_id
        if not obtenir_etudiant_par_id(id_etudiant):
            return {'success': False, 'message': 'Étudiant introuvable'}
        
        # Vérifier doublon
        existing = db.session.query(ParenteLiaison).filter_by(
            id_parent=id_parent,
            id_etudiant=id_etudiant,
            lien_parente=lien_parente
        ).first()
        
        if existing:
            return {'success': False, 'message': 'Liaison déjà existante'}
        
        liaison = ParenteLiaison(
            id_parent=id_parent,
            id_etudiant=id_etudiant,
            lien_parente=lien_parente
        )
        
        db.session.add(liaison)
        db.session.commit()
        
        return {'success': True, 'message': 'Liaison créée avec succès'}
    
    except Exception as e:
        db.session.rollback()
        return {'success': False, 'message': f'Erreur: {str(e)}'}

def obtenir_enfants_parent(id_parent):
    """
    Liste tous les étudiants liés à un parent
    
    Returns:
        Liste de dict avec etudiant, user, filiere, lien
    """
    from models.etudiants import Etudiant
    from models.utilisateurs import Utilisateur
    from models.filieres import Filiere
    
    results = db.session.query(
        Etudiant, Utilisateur, Filiere, ParenteLiaison
    ).join(
        Utilisateur, Etudiant.id_user == Utilisateur.id_user
    ).join(
        Filiere, Etudiant.id_filiere == Filiere.id_filiere
    ).join(
        ParenteLiaison, Etudiant.id_etudiant == ParenteLiaison.id_etudiant
    ).filter(
        ParenteLiaison.id_parent == id_parent
    ).all()
    
    enfants = []
    for etudiant, user, filiere, liaison in results:
        enfants.append({
            'etudiant': etudiant,
            'user': user,
            'filiere': filiere,
            'lien': liaison.lien_parente
        })
    
    return enfants

def verifier_lien_parent_etudiant(id_parent, id_etudiant):
    """
    Vérifie si un lien existe entre un parent et un étudiant
    
    Returns:
        bool
    """
    liaison = db.session.query(ParenteLiaison).filter_by(
        id_parent=id_parent,
        id_etudiant=id_etudiant
    ).first()
    
    return liaison is not None

def supprimer_liaison(id_liaison):
    """Supprime une liaison parent-étudiant"""
    try:
        liaison = db.session.get(ParenteLiaison, id_liaison)
        if liaison:
            db.session.delete(liaison)
            db.session.commit()
            return {'success': True, 'message': 'Liaison supprimée'}
        return {'success': False, 'message': 'Liaison introuvable'}
    
    except Exception as e:
        db.session.rollback()
        return {'success': False, 'message': f'Erreur: {str(e)}'}

LIENS_PARENTE_VALIDES = ['Père', 'Mère', 'Tuteur', 'Tutrice']
